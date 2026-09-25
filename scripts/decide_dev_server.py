"""Serve `/v1/decide` and the decision vocabulary locally, for the decide page (MODEL-153).

The Worker answers `POST /v1/decide` with `api/worker/src/decide_service.py`;
this runs that same module on a snapshot file, beside the vocabulary built from
it, so a page change can be tried against real data before the Worker deploys.
Point the Vite dev server at it (see web/README.md):

    python scripts/decide_dev_server.py --snapshot snapshot.json.gz
    curl -o snapshot.json.gz https://modelspec.dev/api/decision/snapshot.json.gz

The signature is checked only when `MODELSPEC_SNAPSHOT_KEY` is set. Local only:
it binds 127.0.0.1 and has no access control.
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "api" / "worker" / "src")]

import decide_service  # noqa: E402
from decision import snapshot as decision_snapshot  # noqa: E402
from decision.vocabulary import build_vocabulary  # noqa: E402
from pipeline.load import load_benchmarks  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--snapshot", required=True, type=Path, help="a decision snapshot .json.gz")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args(argv)

    snapshot = decision_snapshot.load_snapshot(
        args.snapshot, key=decision_snapshot.env_key(), include_archive=True)
    pages = {b.benchmark_id: b.front for b in load_benchmarks(REPO)}
    vocabulary = json.dumps(build_vocabulary(snapshot, pages=pages), ensure_ascii=False).encode()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - http.server's name
            if self.path.split("?", 1)[0] == "/api/decision/vocabulary.json":
                self._send(200, vocabulary)
            else:
                self._send(404, b'{"error": "not_found"}')

        def do_POST(self) -> None:  # noqa: N802 - http.server's name
            if self.path.split("?", 1)[0] != "/v1/decide":
                self._send(404, b'{"error": "not_found"}')
                return
            raw = self.rfile.read(int(self.headers.get("content-length") or 0))
            try:
                payload = json.loads(raw or b"null")
            except ValueError as exc:
                status, body = decide_service.error_response(
                    "invalid_request", f"the body is not valid JSON: {exc}",
                    status=decide_service.HTTP_BAD_REQUEST, snapshot_id=None)
            else:
                status, body = decide_service.decide(payload, snapshot)
            self._send(status, decide_service.serialise(body))

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"{snapshot.snapshot_id} on http://127.0.0.1:{args.port} "
          "(/v1/decide, /api/decision/vocabulary.json)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
