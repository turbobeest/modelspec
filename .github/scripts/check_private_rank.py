"""Probe an enabled deployment without printing response data or exception text."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def probe(host, path, payload=None):
    request = urllib.request.Request(
        f"https://{host}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"user-agent": "ModelSpec-private-deploy-probe", "content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    except Exception as error:
        print(f"probe path={path}; category={type(error).__name__}")
        return 0, None
    print(f"probe path={path}; status={status}; bytes={len(raw)}")
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    deadline = time.monotonic() + 300
    while True:
        status, body = probe(args.host, "/v1/health")
        if status == 200 and isinstance(body, dict) and body.get("service_commit") == args.commit and body.get("export_loaded") is True:
            break
        if time.monotonic() >= deadline:
            raise SystemExit("private Worker health check failed")
        time.sleep(10)
    checks = [
        ("/v1/rank", {"use_case": "coding", "environment": {"hosting": "managed_api"}, "limit": 3}, {200}),
        ("/v1/policy-check", {"policy": {"origin": {"permitted_countries": ["US"]}}, "limit": 3}, {200}),
        ("/v1/decide", {"spec_version": 1, "snapshot": "latest", "optimize": {"max": "gpqa_diamond"}, "explain": "none", "limit": 1}, {200, 401, 403, 429}),
        ("/v1/vocabulary", None, {200}),
    ]
    for path, payload, expected in checks:
        status, body = probe(args.host, path, payload)
        if status not in expected or not isinstance(body, dict):
            raise SystemExit(f"private Worker check failed: path={path}; status={status}")
        if path == "/v1/vocabulary" and not all(key in body for key in ("facets", "domains", "models", "templates", "estate")):
            raise SystemExit("private Worker vocabulary shape check failed")
    print("private Worker probes passed")


if __name__ == "__main__":
    main()
