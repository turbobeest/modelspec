"""Measure API transport without saving request bodies, responses, or credentials.

python qa/latency_probe.py --count 30 --output /tmp/latency.json
Optional --shapes is a JSON list of {name, path, method, body} objects. Keep
private manifests outside this repository. Names must be anonymous labels.
Requires curl and, when negotiating br, the Python brotli package.
Each call opens a connection; DNS/connect/TLS are reported separately. The
first sample is retained, but is not proof that the isolate was cold.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import tempfile
from urllib.parse import urlsplit


def default_shapes():
    base = {"spec_version": 1, "snapshot": "latest",
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"}, "limit": 5}
    return [
        {"name": f"decide-{level}", "path": "/v1/decide", "method": "POST",
         "body": {**base, "explain": level}} for level in ("none", "summary", "full")
    ] + [
        {"name": "decide-estate", "path": "/v1/decide", "method": "POST",
         "body": {**base, "explain": "summary", "access": {"kind": "own_software"},
                  "estate": {"providers": ["openai"]}}},
        {"name": "decide-evidence", "path": "/v1/decide", "method": "POST",
         "body": {**base, "explain": "summary", "optimize": {"max": "swe_bench_pro"}}},
        {"name": "rank", "path": "/v1/rank", "method": "POST",
         "body": {"use_case": "coding", "limit": 10}},
        {"name": "vocabulary", "path": "/v1/vocabulary", "method": "GET"},
    ]


def validate_shapes(shapes):
    if not isinstance(shapes, list) or not shapes:
        raise ValueError("shapes must be a nonempty list")
    names = set()
    for shape in shapes:
        name, path = shape.get("name", ""), shape.get("path", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name) or name in names:
            raise ValueError("shape names must be unique anonymous labels")
        names.add(name)
        if not path.startswith("/") or path.startswith("//") or urlsplit(path).query or urlsplit(path).fragment:
            raise ValueError("shape paths must be relative paths without queries")
        if shape.get("method", "GET") not in ("GET", "POST", "HEAD"):
            raise ValueError("unsupported method")
    return shapes


def response_headers(raw):
    """Use the final block, after proxy CONNECT or interim responses."""
    blocks = re.split(r"\r?\n\r?\n", raw.strip())
    result = {}
    for block in blocks:
        if block.startswith("HTTP/"):
            result = {}
            for line in block.splitlines()[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.lower()
                    result[key] = result.get(key, "") + (", " if key in result else "") + value.strip()
    return result


def server_durations(value):
    return {match[0]: float(match[1]) for match in re.findall(
        r"(?:^|,)\s*([\w-]+)\s*;\s*dur=([\d.]+)", value)}


def isolate_state(value):
    match = re.search(r'(?:^|,)\s*isolate\s*;\s*desc="(cold|warm)"', value)
    return match[1] if match else "unknown"


def measure(origin, shape, *, encoding="br, gzip", timeout=30):
    # Read only this named variable. Put credentials and bodies on stdin, never
    # argv. Do not print curl stderr, which can include remote response content.
    key = os.environ.get("MODELSPEC_API_KEY")
    if key and any(c in key for c in '\r\n\x00'):
        raise ValueError("invalid API key characters")
    with tempfile.TemporaryDirectory(prefix="modelspec-latency-") as directory:
        header_path, body_path = Path(directory) / "headers", Path(directory) / "body"
        quote = lambda value: '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
        config = ["header = " + quote("Accept-Encoding: " + encoding)]
        if key:
            config.append("header = " + quote("Authorization: Bearer " + key))
        if "body" in shape:
            config += ["header = \"Content-Type: application/json\"",
                       "data = " + quote(json.dumps(shape["body"]))]
        command = ["curl", "--disable", "--silent", "--config", "-",
                   "--max-time", str(timeout), "--request", shape.get("method", "GET"),
                   "--dump-header", str(header_path), "--output", str(body_path),
                   "--write-out", "%{json}", origin.rstrip("/") + shape["path"]]
        run = subprocess.run(command, input="\n".join(config) + "\n", text=True,
                             capture_output=True, timeout=timeout + 5)
        metrics = json.loads(run.stdout) if run.stdout.strip() else {}
        headers = response_headers(header_path.read_text() if header_path.exists() else "")
        wire = body_path.read_bytes() if body_path.exists() else b""
        content_encoding = headers.get("content-encoding", "identity")
        raw = None
        if run.returncode == 0:
            raw = wire
            for coding in reversed(content_encoding.split(",")):
                if coding.strip() == "gzip":
                    raw = gzip.decompress(raw)
                elif coding.strip() == "br":
                    import brotli
                    raw = brotli.decompress(raw)
                elif coding.strip() != "identity":
                    raise ValueError("unsupported response encoding")
        ms = lambda field: float(metrics.get(field, 0)) * 1000
        dns, connect, tls = ms("time_namelookup"), ms("time_connect"), ms("time_appconnect")
        ttfb, total = ms("time_starttransfer"), ms("time_total")
        return {
            "status": int(metrics.get("http_code", 0)), "curl_exit": run.returncode,
            "dns_ms": dns, "connect_ms": max(0, connect - dns),
            "tls_ms": max(0, tls - connect) if tls else 0,
            "ttfb_ms": ttfb, "total_ms": total,
            "post_tls_ttfb_ms": max(0, ttfb - max(tls, connect)),
            "download_ms": max(0, total - ttfb),
            "compressed_bytes": len(wire), "raw_bytes": len(raw) if raw is not None else None,
            "content_encoding": content_encoding,
            "server_timing": headers.get("server-timing", ""),
            "isolate_state": isolate_state(headers.get("server-timing", "")),
            "server_durations_ms": server_durations(headers.get("server-timing", "")),
            "colo": headers.get("cf-ray", "").rsplit("-", 1)[-1] or None,
            "service_commit": headers.get("x-modelspec-service-commit"),
        }


def percentiles(values):
    ordered = sorted(values)
    return {"p50": statistics.median(ordered),
            "p95": ordered[max(0, math.ceil(len(ordered) * .95) - 1)]}


def summarise(samples):
    valid = [row for row in samples if row["curl_exit"] == 0]
    return {
        "calls": len(samples), "completed": len(valid),
        "statuses": {str(status): sum(row["status"] == status for row in samples)
                     for status in sorted({row["status"] for row in samples})},
        "colos": sorted({row["colo"] for row in valid if row["colo"]}),
        "encodings": sorted({row["content_encoding"] for row in valid}),
        "isolate_states": {
            state: {"calls": len(group),
                    "ttfb_ms": percentiles([row["ttfb_ms"] for row in group])}
            for state in ("cold", "warm", "unknown")
            if (group := [row for row in valid if row.get("isolate_state", "unknown") == state])
        },
        "first_total_ms": samples[0]["total_ms"],
        "warm_total_ms": percentiles([row["total_ms"] for row in samples[1:] if row["curl_exit"] == 0])
        if any(row["curl_exit"] == 0 for row in samples[1:]) else None,
        **{key: percentiles([row[key] for row in valid if row[key] is not None])
           for key in ("dns_ms", "connect_ms", "tls_ms", "ttfb_ms", "total_ms",
                       "post_tls_ttfb_ms", "download_ms", "compressed_bytes", "raw_bytes")
           if any(row[key] is not None for row in valid)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="https://api.modelspec.dev")
    parser.add_argument("--shapes", type=Path)
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--encoding", choices=("br, gzip", "gzip", "identity"), default="br, gzip")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    url = urlsplit(args.origin)
    if url.scheme not in ("https", "http") or not url.netloc or url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
        parser.error("origin must be a bare HTTP(S) origin without credentials")
    if not 1 <= args.count <= 1000:
        parser.error("count must be between 1 and 1000")
    if not os.environ.get("MODELSPEC_API_KEY"):
        args.output.write_text(json.dumps({
            "origin": args.origin, "status": "skipped", "reason": "no key", "shapes": [],
        }, indent=2) + "\n")
        print("skipped: no key (set MODELSPEC_API_KEY to measure API decisions)")
        return 0
    if "br" in args.encoding:
        try:
            import brotli  # noqa: F401
        except ImportError:
            parser.error("install brotli or select --encoding gzip")
    shapes = validate_shapes(json.loads(args.shapes.read_text()) if args.shapes else default_shapes())
    report = {"origin": args.origin, "connection_mode": "new connection per call", "shapes": []}
    for shape in shapes:
        samples = [measure(args.origin, shape, encoding=args.encoding) for _ in range(args.count)]
        row = {"name": shape["name"], "samples": samples, "summary": summarise(samples)}
        report["shapes"].append(row)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        summary = row["summary"]
        print(json.dumps({"name": row["name"], "summary": summary}), flush=True)
    return int(any(row["summary"]["completed"] != args.count for row in report["shapes"]))


if __name__ == "__main__":
    raise SystemExit(main())
