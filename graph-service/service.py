"""Read-only HTTP query service for the benchgraph graph (MODEL-9).

Runs inside the container next to FalkorDB. On start it loads the export named
by GRAPH_EXPORT_URL (a directory path, file:// or https:// base URL; R2 in
production) into the local FalkorDB, then serves:

    GET /graph/health                         liveness + loaded build commit
    GET /graph/manifest                       the export manifest
    GET /graph/<name>?<params>                one named query from QUERIES

It never executes Cypher taken from a request: the path picks a query from a
fixed allowlist, parameters are validated and passed as Cypher parameters, and
the query runs through GRAPH.RO_QUERY.
"""

from __future__ import annotations

import json
import re
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from pipeline import benchgraph_graph as bg

#: Routes that are not graph queries.
META_ROUTES = ("health", "manifest")
ALLOWED = frozenset(META_ROUTES) | frozenset(bg.QUERIES)

#: `error` is a stable, non-sensitive code; exception text never leaves the process.
STATE: dict[str, object] = {"manifest": None, "error": None, "graph": None, "status": "loading"}

_URLISH = re.compile(r"[a-z][a-z0-9+.-]*://\S+", re.I)
_QUERY = re.compile(r"\?\S*")


def redact_url(source: str) -> str:
    """Keep scheme, host and path; drop userinfo, query and fragment.

    A local path (no scheme) passes through unchanged.
    """
    parts = urlsplit(source)
    if not parts.scheme or len(parts.scheme) == 1:  # "C:\\" style paths too
        return source
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def redact_message(text: str, source: str = "") -> str:
    """Strip the source URL, anything URL-shaped and query strings from a message."""
    if source:
        text = text.replace(source, redact_url(source))
    text = _URLISH.sub(lambda m: redact_url(m.group(0)), text)
    return _QUERY.sub("", text)


def load(source: str) -> None:
    manifest, doc = bg.read_export(source)
    graph = bg.connect(host=os.environ.get("FALKORDB_HOST", "127.0.0.1"),
                       port=int(os.environ.get("FALKORDB_PORT", "6379")))
    bg.load_document(graph, doc)
    STATE.update(manifest=manifest, graph=graph, error=None, status="ok")


class Handler(BaseHTTPRequestHandler):
    server_version = "benchgraph-graph/1.0"

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=300" if status == 200 else "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _base(self) -> dict:
        m = STATE["manifest"] or {}
        return {"build_commit": (m.get("build") or {}).get("commit"),
                "format_version": m.get("format_version")}

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        parts = urlsplit(self.path)
        segs = parts.path.strip("/").split("/")
        if len(segs) != 2 or segs[0] != "graph" or segs[1] not in ALLOWED:
            return self._send(404, {"error": "unknown route", "allowed": sorted(ALLOWED)})
        name = segs[1]
        try:
            raw_pairs = parse_qsl(parts.query, keep_blank_values=True, strict_parsing=bool(parts.query))
        except ValueError:
            return self._send(400, {"error": "malformed query string"})
        raw = dict(raw_pairs)
        if len(raw) != len(raw_pairs):
            return self._send(400, {"error": "repeated parameter"})

        if name == "health":
            loaded = STATE["manifest"] is not None
            body = {**self._base(), "status": "ok" if loaded else STATE["status"]}
            if not loaded:
                body["error"] = "export_not_loaded"
            return self._send(200 if loaded else 503, body)
        if STATE["manifest"] is None:
            return self._send(503, {"error": "graph not loaded"})
        if name == "manifest":
            return self._send(200, {**self._base(), "manifest": STATE["manifest"]})
        try:
            params = bg.validate_params(name, raw)
        except ValueError as exc:
            return self._send(400, {**self._base(), "error": str(exc)})
        try:
            rows = bg.run_query(STATE["graph"], name, raw)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return self._send(500, {**self._base(), "error": "query failed"})
        return self._send(200, {**self._base(), "query": name, "params": params, "rows": rows})

    def do_POST(self) -> None:  # noqa: N802
        self._send(405, {"error": "read-only"})

    do_PUT = do_DELETE = do_PATCH = do_POST


def _loader(source: str, attempts: int = 30, sleep=time.sleep) -> None:
    last = ""
    for attempt in range(1, attempts + 1):
        try:
            load(source)
            print(f"loaded export {self_commit()} from {redact_url(source)}", flush=True)
            return
        except Exception as exc:  # noqa: BLE001 - FalkorDB may still be starting
            STATE["error"] = "export_not_loaded"
            last = f"{type(exc).__name__}: {redact_message(str(exc), source)}"
            if attempt < attempts:
                sleep(min(attempt, 5))
    STATE["status"] = "error"
    print(f"giving up loading export from {redact_url(source)}: {last}", file=sys.stderr, flush=True)


def self_commit() -> str | None:
    m = STATE["manifest"] or {}
    return (m.get("build") or {}).get("commit")


def main() -> None:
    source = os.environ.get("GRAPH_EXPORT_URL")
    if not source:
        sys.exit("GRAPH_EXPORT_URL is required")
    threading.Thread(target=_loader, args=(source,), daemon=True).start()
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
