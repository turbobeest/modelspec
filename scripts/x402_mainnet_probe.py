"""Read-only checks after the x402 mainnet flip (MODEL-333, docs/x402-mainnet-flip.md).

Makes no payment and signs nothing. Needs a zero-balance production key in
MODELSPEC_API_KEY. Exits non-zero on the first failed check.

    python scripts/x402_mainnet_probe.py --expect-commit <merge sha>
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys

import httpx

NETWORK = "eip155:8453"
ASSET = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
PAY_TO = "0x69429dbeeee7218084ab5b896788f5fce452419c"
PACK_AMOUNTS = {"5000000", "25000000", "50000000", "100000000"}


def _check(ok: bool, what: str) -> None:
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://api.modelspec.dev")
    parser.add_argument("--expect-commit", help="merge commit the Worker should report")
    args = parser.parse_args()
    api_key = os.environ.get("MODELSPEC_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("MODELSPEC_API_KEY is required (a zero-balance production key)")

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=30) as client:
        health = client.get("/v1/health").json()
        if args.expect_commit:
            _check(health.get("service_commit") == args.expect_commit,
                   f"service_commit {health.get('service_commit')}")

        keyless = client.post("/v1/decide", json={"spec_version": 1})
        _check(keyless.status_code == 401, f"keyless decide is 401 (got {keyless.status_code})")

        headers = {"authorization": f"Bearer {api_key}"}
        balance = client.get("/v1/credits", headers=headers).json()
        _check(int(balance.get("available", -1)) == 0,
               f"probe key holds no credits (available={balance.get('available')})")

        offered = client.post("/v1/decide", headers=headers, json={"spec_version": 1})
        _check(offered.status_code == 402, f"unfunded keyed decide is 402 (got {offered.status_code})")
        body = offered.json()
        accepts = body.get("accepts") or []
        header = offered.headers.get("PAYMENT-REQUIRED", "")
        _check(bool(header), "PAYMENT-REQUIRED header present")
        decoded = json.loads(base64.b64decode(header))
        _check(decoded.get("accepts") == accepts, "header accepts match the body")
        _check(len(accepts) == 4, f"four pack offers (got {len(accepts)})")
        for row in accepts:
            _check(row.get("network") == NETWORK, f"network {row.get('network')}")
            _check(str(row.get("asset", "")).lower() == ASSET, f"asset {row.get('asset')}")
            _check(str(row.get("payTo", "")).lower() == PAY_TO, f"payTo {row.get('payTo')}")
        amounts = {str(row.get("amount")) for row in accepts}
        _check(amounts == PACK_AMOUNTS, f"pack amounts {sorted(amounts, key=int)}")
        credits = sorted(int(row["credits"]) for row in body["error"]["packs"])
        _check(credits == [250, 1300, 2750, 6000], f"pack credits {credits}")
    print("x402 mainnet probe passed")


if __name__ == "__main__":
    sys.exit(main())
