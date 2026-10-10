"""QA-only streamable HTTP MCP proxy. Never deploy this proxy.

Bind to 0.0.0.0 on Docker Desktop for Mac; containers connect through
http://host.docker.internal:<port>/mcp. Authorization and session headers are
forwarded in memory. Access logs and exception bodies are deliberately absent.
Only call identifiers, flags, field names, counters and byte sizes enter JSONL.

V1 fetches the complete Decision with a pinned snapshot and limit 500, the
contract maximum. Both snapshot and limit are part of canonical_json, so these
pins can change spec_hash and decision_id. Both identities are checked against
their respective canonical Specs, and the answer must match the bounded body.
Serialized Decisions omit runtime-only feasible models; V1 requires zero
truncated models to reconstruct the full candidate set. Otherwise the call
passes through, counts candidates_truncated, and invalidates exposure proof.

The upstream summary retains engine-only evidence captures that even a complete
Decision cannot reproduce. We reserve space for next_move.say and use the
engine's last-resort paragraph clipper when necessary. Its ending is exact;
under clipping the preceding list trimming can differ from a future server
summary. Every such call counts summary_trim_gap. Named profiles are refused
for V1 because the complete Decision does not contain their rules. Inline
profiles work. A failed complete fetch uses retained bounded fields and counts
bounded_fallback, which cannot recover omitted candidates or profile rules.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import threading
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx

from decision.bounded import AGENT_BYTES, mcp_default_request
from decision.contract import Decision, parse_spec, spec_hash
from decision.next_move import (
    build_next_move,
    next_move_input_from_bounded,
    next_move_input_from_decision,
)
from decision.summary import SUMMARY_BYTES, _clip_paragraph
from pipeline.agent_copy import DECIDE_WORKED_EXAMPLE, NULL_RULE, SUMMARY_RULE

UPSTREAM = "https://api.modelspec.dev/mcp"
HEADER = "X-ModelSpec-Ablation"
METADATA_PATH = "/ablation"
OLD_SUMMARY_RULE = (
    "Present `summary_for_user` to the user unchanged and keep every `must_mention` item."
)
LIMITATIONS = [
    "summary_trim_gap: the reserved ending is exact; "
    "clipped preceding lists can differ from the server",
    "bounded_fallback: a failed complete fetch leaves omitted selection inputs unavailable",
    "candidates_truncated: a complete fetch with omitted models passes through and invalidates exposure proof",
    "named profiles are refused for V1; use inline profiles",
    "pinning latest and limit 500 can change canonical spec_hash and decision_id; both identities and the answer are verified",
    "V1 and combined double keyed /v1/decide calls to fetch the complete candidate set",
]
HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


class RewriteError(AssertionError):
    """An upstream assumption failed. Messages contain no upstream data."""


class CompleteFetchError(Exception):
    """Only transport/HTTP/parse failures permit the bounded fallback."""


class CopyDriftError(RewriteError):
    """The published copy no longer matches the exact replacement anchors."""


def packed(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def text_bytes(result: dict) -> int:
    return sum(
        len(item["text"].encode("utf-8"))
        for item in result.get("content", [])
        if item.get("type") == "text"
    )


def proxy_port(url: str) -> int:
    if not re.fullmatch(r"http://host\.docker\.internal:[0-9]+/mcp", url):
        raise ValueError("--ablation-proxy must be http://host.docker.internal:<port>/mcp")
    port = urlsplit(url).port
    if port is None or not 1 <= port <= 65535:
        raise ValueError("--ablation-proxy needs a port between 1 and 65535")
    return port


def upstream_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path != "/mcp"
    ):
        raise ValueError("Upstream must be an HTTPS /mcp URL without credentials or query")
    return url


@dataclass(frozen=True)
class Variants:
    next_move: bool = False
    worked_example: bool = False
    annotations: bool = False
    plugin: bool = False

    def names(self) -> list[str]:
        return [
            name
            for name, enabled in (
                ("v1", self.next_move),
                ("v2", self.plugin),
                ("v3", self.worked_example),
                ("v4", self.annotations),
            )
            if enabled
        ]


def metadata(variants: Variants, url: str, upstream: str = UPSTREAM) -> dict:
    proxy_port(url)
    upstream_url(upstream)
    return {
        "variants": variants.names(),
        "proxy_url": url,
        "upstream": upstream,
        "proxy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def read_metadata(url: str, path: Path | None, *, dry_run: bool = False) -> dict:
    port = proxy_port(url)
    if path is not None:
        data = json.loads(path.read_text())
    elif dry_run:
        raise ValueError("Proxy dry runs need --ablation-metadata; no discovery request is made")
    else:
        with httpx.Client(trust_env=False, timeout=5) as client:
            reply = client.get(f"http://127.0.0.1:{port}{METADATA_PATH}")
            reply.raise_for_status()
            data = reply.json()["ablation"]
    variants = data.get("variants")
    if (
        not isinstance(variants, list)
        or any(v not in {"v1", "v2", "v3", "v4"} for v in variants)
        or len(set(variants)) != len(variants)
        or data.get("proxy_url") != url
        or not re.fullmatch(r"[a-f0-9]{64}", data.get("proxy_sha256", ""))
    ):
        raise ValueError("Invalid ablation metadata")
    upstream_url(data.get("upstream", ""))
    return {key: data[key] for key in ("variants", "proxy_url", "upstream", "proxy_sha256")}


def private_directory(path: Path) -> Path:
    # A lazy import keeps the shared metadata helpers independent of the harness.
    from qa.tui_harness import private_output

    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Proxy output must not use symlinks")
    path = private_output(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    return path


def write_private(path: Path, value: dict) -> None:
    if path.is_symlink():
        raise ValueError("Ablation files must not be symlinks")
    with path.open("w", encoding="utf-8") as handle:
        path.chmod(0o600)
        handle.write(json.dumps(value, indent=2) + "\n")


def request_spec(arguments: dict) -> dict:
    return {
        key: value
        for key, value in mcp_default_request(arguments).items()
        if key not in {"fields", "evidence_for"}
    }


def decision_identity(digest: str, snapshot: str) -> str:
    return "dec_" + hashlib.sha256((digest + snapshot).encode()).hexdigest()[:24]


def check_identity(complete: Decision, bounded: dict, original: dict, pinned: dict) -> str:
    if complete.snapshot != bounded["snapshot"]:
        raise RewriteError("Complete Decision snapshot drifted")
    if complete.status != bounded["status"]:
        raise RewriteError("Complete Decision status drifted")
    answer = None if complete.answer is None else complete.answer.model_dump(mode="json")
    if answer != bounded.get("answer"):
        raise RewriteError("Complete Decision answer drifted")
    if (
        pinned != original | {"snapshot": bounded["snapshot"], "limit": 500}
        or original.get("snapshot", "latest") not in {"latest", bounded["snapshot"]}
    ):
        raise RewriteError("Complete Decision identity drifted beyond snapshot and limit pinning")
    original_spec = parse_spec(original, facets=None)
    pinned_spec = parse_spec(pinned, facets=None)
    before = spec_hash(original_spec)
    after = spec_hash(pinned_spec)
    if (
        bounded["spec_hash"] != before
        or complete.spec_hash != after
        or bounded["decision_id"] != decision_identity(before, complete.snapshot)
        or complete.decision_id != decision_identity(after, complete.snapshot)
    ):
        raise RewriteError("Complete Decision identity drifted beyond snapshot and limit pinning")
    pins = [name for name in ("snapshot", "limit")
            if getattr(original_spec, name) != getattr(pinned_spec, name)]
    return "_".join(pins) + "_pin" if pins else "matched"


def replace_summary_rule(text: str) -> str:
    if not isinstance(text, str) or text.count(OLD_SUMMARY_RULE) != 1 or SUMMARY_RULE in text:
        raise CopyDriftError("Upstream SUMMARY_RULE drifted")
    return text.replace(OLD_SUMMARY_RULE, SUMMARY_RULE, 1)


@dataclass
class Rewrite:
    message: dict
    fields: list[str] = field(default_factory=list)
    counters: Counter = field(default_factory=Counter)
    before: int = 0
    after: int = 0


def rewrite(message: dict, call: dict, variants: Variants, fetch_complete) -> Rewrite:
    """Rewrite one JSON-RPC response. Inputs remain unchanged, including on overflow."""
    original = message
    changed = copy.deepcopy(message)
    outcome = Rewrite(changed)
    result = changed.get("result")
    if not isinstance(result, dict) or changed.get("id") != call.get("id"):
        return Rewrite(original)
    method = call.get("method")
    if method == "initialize" and variants.next_move:
        result["instructions"] = replace_summary_rule(result.get("instructions", ""))
        outcome.fields.append("instructions")
    if method == "tools/list" and (variants.next_move or variants.worked_example):
        listed = result.get("tools", [])
        if not isinstance(listed, list) or any(not isinstance(tool, dict) for tool in listed):
            raise CopyDriftError("Upstream decide tool list drifted")
        tools = [tool for tool in listed if tool.get("name") == "decide"]
        if len(tools) != 1:
            raise CopyDriftError("Upstream decide tool list drifted")
        text = tools[0].get("description", "")
        if variants.next_move:
            text = replace_summary_rule(text)
        if variants.worked_example:
            if (
                not isinstance(text, str)
                or not text.endswith(NULL_RULE)
                or DECIDE_WORKED_EXAMPLE in text
            ):
                raise CopyDriftError("Upstream worked example insertion point drifted")
            text += DECIDE_WORKED_EXAMPLE
        tools[0]["description"] = text
        outcome.fields.append("tools.decide.description")
    params = call.get("params") or {}
    if method != "tools/call" or params.get("name") != "decide" or result.get("isError"):
        return outcome if outcome.fields else Rewrite(original)
    outcome.before = text_bytes(result)
    outcome.after = outcome.before
    if not (variants.next_move or variants.annotations):
        return Rewrite(original, before=outcome.before, after=outcome.before)
    content = result.get("content", [])
    envelope = None
    for index, item in enumerate(content):
        if item.get("type") != "text":
            continue
        try:
            candidate = json.loads(item["text"])
        except (ValueError, TypeError):
            continue
        if isinstance(candidate, dict) and isinstance(candidate.get("body"), dict):
            envelope = candidate
            break
    if envelope is None:
        raise RewriteError("Upstream decide JSON envelope drifted")
    body = envelope["body"]
    if envelope.get("status", 0) >= 400 or "error" in body:
        return Rewrite(original, before=outcome.before, after=outcome.before)
    if not isinstance(body.get("summary_for_user"), str):
        outcome.counters["unbounded_passthrough"] += 1
        outcome.message = original
        return outcome
    if variants.next_move:
        original_spec = request_spec(params.get("arguments") or {})
        pinned = original_spec | {"snapshot": body["snapshot"], "limit": 500}
        spec = parse_spec(pinned, facets=None)
        if isinstance(spec.profile, str):
            raise RewriteError("V1 cannot reproduce named profile rules; use an inline profile")
        try:
            complete = fetch_complete(pinned)
        except CompleteFetchError:
            inp = next_move_input_from_bounded(original_spec, body)
            outcome.counters["bounded_fallback"] += 1
        else:
            identity = check_identity(complete, body, original_spec, pinned)
            outcome.counters["complete_fetch"] += 1
            outcome.counters["identity_" + identity] += 1
            if complete.truncated.models != 0:
                outcome.counters["candidates_truncated"] += 1
                outcome.message = original
                return outcome
            inp = next_move_input_from_decision(
                complete,
                spec,
                not_applied=body.get("explanation", {}).get("not_applied", ()),
            )
        move = build_next_move(inp)
        if move is not None:
            body["next_move"] = move
            ending = " " + move["say"]
            paragraph = body["summary_for_user"]
            if len((paragraph + ending).encode("utf-8")) > SUMMARY_BYTES:
                room = SUMMARY_BYTES - len(ending.encode("utf-8"))
                if room < len(paragraph.split(". ", 1)[0].encode("utf-8")) + 1:
                    raise RewriteError(
                        "Next move cannot fit the answer statement and summary budget"
                    )
                paragraph = _clip_paragraph(paragraph, max_bytes=room)
                outcome.counters["summary_trim_gap"] += 1
            body["summary_for_user"] = paragraph + ending
            outcome.fields += ["body.next_move", "body.summary_for_user"]
            content[index]["text"] = packed(envelope).decode("utf-8")
        else:
            outcome.counters["separated_no_move"] += 1
    if variants.annotations:
        annotated = {
            "type": "text",
            "text": body["summary_for_user"],
            "annotations": {"audience": ["user"]},
        }
        if len(content) > index + 1 and content[index + 1].get("type") == "text":
            content[index + 1] = annotated
        else:
            content.insert(index + 1, annotated)
        outcome.fields.append("content.user_summary")
    outcome.after = text_bytes(result)
    if outcome.after > AGENT_BYTES:
        outcome.message = original
        outcome.fields.clear()
        outcome.counters["budget_passthrough"] += 1
        outcome.after = outcome.before
    if not outcome.fields:
        outcome.message = original
    return outcome


class Audit:
    def __init__(self, directory: Path, info: dict):
        self.directory, self.info = private_directory(directory), info
        self.path = self.directory / "calls.jsonl"
        if self.path.exists() or self.path.is_symlink():
            raise ValueError("Proxy call log already exists; choose a fresh output directory")
        self.path.touch(mode=0o600)
        self.counts = Counter()
        self.failures = Counter()
        self.responses = 0
        self.lock = threading.Lock()
        write_private(self.directory / "ablation.json", info)

    def record(self, call: dict, outcome: Rewrite, *, before: int, after: int) -> dict:
        identifier = call.get("id")
        # Hash string IDs so a client cannot smuggle a prompt or key into the log.
        if isinstance(identifier, str):
            identifier = "sha256:" + hashlib.sha256(identifier.encode()).hexdigest()
        elif type(identifier) is not int:
            identifier = None
        method = call.get("method")
        method = (
            method
            if method in {"initialize", "tools/list", "tools/call", "notifications/initialized"}
            else "other"
        )
        with self.lock:
            self.responses += 1
            row = {
                "response": self.responses,
                "call_id": identifier,
                "method": method,
                "variant_flags": self.info["variants"],
                "rewritten_fields": outcome.fields,
                "bytes_before": before,
                "bytes_after": after,
                "text_bytes_before": outcome.before,
                "text_bytes_after": outcome.after,
                "counters": dict(outcome.counters),
            }
            self.counts.update(outcome.counters)
            self.counts.update(outcome.fields)
            self.counts["responses"] += 1
            if outcome.fields:
                self.counts["rewritten_calls"] += 1
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(packed(row).decode() + "\n")
            return row

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "ablation": self.info,
                "counters": dict(self.counts),
                "failures": dict(self.failures),
                "limitations": LIMITATIONS,
            }


def forwarded_headers(headers, *, response=False) -> dict:
    connection = {item.strip().lower() for item in headers.get("connection", "").split(",")}
    removed = HOP_HEADERS | connection | {"accept-encoding"}
    if response:
        removed |= {"content-encoding"}
    return {key: value for key, value in headers.items() if key.lower() not in removed}


class Proxy:
    def __init__(self, variants: Variants, audit: Audit, *, client: httpx.Client | None = None):
        self.variants, self.audit = variants, audit
        self.client = client or httpx.Client(timeout=httpx.Timeout(90, connect=15), trust_env=False)

    def complete(self, spec: dict, authorization: str | None) -> Decision:
        origin = urlsplit(self.audit.info["upstream"])
        url = urlunsplit((origin.scheme, origin.netloc, "/v1/decide", "", ""))
        headers = {"Authorization": authorization} if authorization else {}
        try:
            response = self.client.post(url, json=spec, headers=headers)
            response.raise_for_status()
            return Decision.model_validate(response.json())
        except (httpx.HTTPError, ValueError):
            raise CompleteFetchError() from None

    def transform(self, raw: bytes, call: dict, authorization: str | None) -> tuple[bytes, dict]:
        try:
            message = json.loads(raw)
            if not isinstance(message, dict):
                raise RewriteError("MCP batches are not supported")
            outcome = rewrite(
                message, call, self.variants, lambda spec: self.complete(spec, authorization)
            )
        except (ValueError, KeyError, TypeError):
            raise RewriteError("Upstream MCP response shape drifted") from None
        output = packed(outcome.message) if outcome.fields else raw
        row = self.audit.record(call, outcome, before=len(raw), after=len(output))
        return output, row


def sse_event(proxy: Proxy, event: bytes, call: dict, authorization: str | None) -> bytes:
    """Preserve event/id/retry/comment lines and the original bytes on passthrough."""
    lines = event.splitlines(keepends=True)
    data = b"\n".join(
        line[5:].lstrip(b" ").rstrip(b"\r\n") for line in lines if line.startswith(b"data:")
    )
    if not data or data == b"[DONE]":
        return event
    output, _row = proxy.transform(data, call, authorization)
    if output == data:
        return event
    newline = b"\r\n" if b"\r\n" in event else b"\n"
    rewritten, inserted = [], False
    for line in lines:
        if line.startswith(b"data:"):
            if not inserted:
                rewritten.append(b"data: " + output + newline)
                inserted = True
        else:
            rewritten.append(line)
    return b"".join(rewritten)


class ProxyServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # BaseServer's traceback can contain request values. Audit only a count.
        self.proxy.audit.record(
            {}, Rewrite({}, counters=Counter(handler_error=1)), before=0, after=0
        )


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self.reply(code, b"", {})

    def do_POST(self):
        self.forward()

    def do_GET(self):
        if self.path == METADATA_PATH:
            raw = packed(self.server.proxy.audit.snapshot())
            self.reply(200, raw, {"Content-Type": "application/json"})
        else:
            self.forward()

    def do_DELETE(self):
        self.forward()

    def reply(self, status: int, raw: bytes, headers: dict, marker: dict | None = None):
        if marker is None:
            marker = self.server.proxy.audit.record({}, Rewrite({}), before=0, after=len(raw))
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header(
            HEADER,
            packed(
                {
                    "response": marker["response"],
                    "variants": self.server.proxy.audit.info["variants"],
                    "rewritten_fields": marker["rewritten_fields"],
                }
            ).decode(),
        )
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def forward(self):
        proxy = self.server.proxy
        if self.path != "/mcp":
            self.reply(404, b"", {})
            return
        call = {}
        sent_headers = False
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 <= length <= 1024 * 1024 or self.headers.get("Transfer-Encoding"):
                self.reply(413, b"", {})
                return
            raw = self.rfile.read(length)
            if raw:
                call = json.loads(raw)
                if not isinstance(call, dict):
                    raise RewriteError("MCP batches are not supported")
            authorization = self.headers.get("Authorization")
            with proxy.client.stream(
                self.command,
                proxy.audit.info["upstream"],
                content=raw,
                headers=forwarded_headers(self.headers),
            ) as upstream:
                headers = forwarded_headers(upstream.headers, response=True)
                content_type = upstream.headers.get("content-type", "").lower()
                if "text/event-stream" in content_type:
                    marker = proxy.audit.record(call, Rewrite({}), before=0, after=0)
                    self.send_response(upstream.status_code)
                    for key, value in headers.items():
                        self.send_header(key, value)
                    self.send_header(
                        HEADER,
                        packed(
                            {
                                "response": marker["response"],
                                "variants": proxy.audit.info["variants"],
                            }
                        ).decode(),
                    )
                    self.send_header("Connection", "close")
                    self.end_headers()
                    sent_headers = True
                    self.close_connection = True
                    event = bytearray()
                    for chunk in upstream.iter_bytes():
                        event.extend(chunk)
                        while match := re.search(rb"\r?\n\r?\n", event):
                            boundary = match.end()
                            self.wfile.write(
                                sse_event(proxy, bytes(event[:boundary]), call, authorization)
                            )
                            self.wfile.flush()
                            del event[:boundary]
                        if len(event) > 16 * 1024 * 1024:
                            raise RewriteError("Upstream SSE event exceeded the proxy buffer limit")
                    if event:
                        self.wfile.write(sse_event(proxy, bytes(event), call, authorization))
                else:
                    body = upstream.read()
                    if body and "json" in content_type:
                        body, marker = proxy.transform(body, call, authorization)
                    else:
                        marker = proxy.audit.record(
                            call, Rewrite({}), before=len(body), after=len(body)
                        )
                    self.reply(upstream.status_code, body, headers, marker)
        except (httpx.HTTPError, RewriteError, ValueError, KeyError, TypeError) as exc:
            reason = (
                str(exc)
                if isinstance(exc, RewriteError)
                else "Upstream transport or request failed"
            )
            with proxy.audit.lock:
                proxy.audit.failures[reason] += 1
            marker = proxy.audit.record(
                call, Rewrite({}, counters=Counter(proxy_error=1)), before=0, after=0
            )
            if not sent_headers:
                self.reply(
                    502,
                    packed({"error": "ablation_proxy_failed", "response": marker["response"]}),
                    {"Content-Type": "application/json"},
                    marker,
                )
            else:
                self.close_connection = True
                error = {
                    "jsonrpc": "2.0",
                    "id": call.get("id"),
                    "error": {"code": -32603, "message": reason},
                }
                self.wfile.write(b"event: message\ndata: " + packed(error) + b"\n\n")
                self.wfile.flush()


@contextmanager
def running_proxy(
    variants: Variants,
    directory: Path,
    *,
    port: int = 8765,
    bind: str = "0.0.0.0",
    upstream: str = UPSTREAM,
    client=None,
):
    server = ProxyServer((bind, port), Handler)
    actual_port = server.server_address[1]
    try:
        audit = Audit(
            directory,
            metadata(variants, f"http://host.docker.internal:{actual_port}/mcp", upstream),
        )
        proxy = Proxy(variants, audit, client=client)
        server.proxy = proxy
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield proxy
        finally:
            server.shutdown()
            thread.join(timeout=5)
            proxy.client.close()
            write_private(audit.directory / "counters.json", audit.snapshot())
    finally:
        server.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--upstream", default=UPSTREAM)
    parser.add_argument("--next-move", action="store_true")
    parser.add_argument("--worked-example", action="store_true")
    parser.add_argument("--annotations", action="store_true")
    args = parser.parse_args(argv)
    try:
        variants = Variants(args.next_move, args.worked_example, args.annotations)
        with running_proxy(
            variants, args.out, port=args.port, bind=args.bind, upstream=args.upstream
        ):
            threading.Event().wait()
    except KeyboardInterrupt:
        return 0
    except (ValueError, OSError):
        print("Ablation proxy refused; check its private directory, bind address and port.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
