"""Probe an enabled deployment without printing response data or exception text."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.worker_flags import enabled, production_vars
from qa.access_smoke import missing_key_problem


def probe(host, path, payload=None, *, api_key=None):
    headers = {"user-agent": "ModelSpec-private-deploy-probe", "content-type": "application/json"}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        f"https://{host}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--boundary-only", action="store_true")
    parser.add_argument("--without-vocabulary", action="store_true")
    args = parser.parse_args(argv)
    enforced = enabled(production_vars(ROOT), "ACCESS_ENFORCED")
    key = os.environ.get("MODELSPEC_SMOKE_API_KEY") or None
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
    if args.without_vocabulary:
        checks = [check for check in checks if check[0] != "/v1/vocabulary"]
    if enforced:
        boundary = [*checks, ("/v1/compare", {"spec_version": 1}, {401})]
        for path, payload, _ in boundary:
            status, body = probe(args.host, path, payload)
            problem = missing_key_problem(status, body)
            if problem:
                raise SystemExit(f"Worker access check failed: path={path}; {problem}")
        if args.boundary_only:
            print("Worker access boundary probes passed")
            return
        if not key:
            print("::notice::MODELSPEC_SMOKE_API_KEY is empty; keyed Worker checks skipped")
            return
    for path, payload, expected in checks:
        status, body = probe(args.host, path, payload, api_key=key if enforced else None)
        if enforced:
            expected = {200}
        if status not in expected or not isinstance(body, dict):
            raise SystemExit(f"private Worker check failed: path={path}; status={status}")
        if path == "/v1/vocabulary" and not all(key in body for key in ("facets", "domains", "models", "templates", "estate")):
            raise SystemExit("private Worker vocabulary shape check failed")
    print("private Worker probes passed")


if __name__ == "__main__":
    main()
