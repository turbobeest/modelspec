#!/usr/bin/env python3
"""Buy one x402 pack on Base Sepolia, then verify and spend its credits.

Run ``--stub`` in tests. A real run requires ``--live`` so an accidental
invocation cannot sign or submit a payment. The wallet private key is read
from ``X402_SMOKE_PRIVATE_KEY`` and is never printed.

Protocol and Base Sepolia values were checked against the CDP facilitator
reference and Base chain reference on 2026-09-26:
https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/verify-payment
https://docs.base.org/base-chain/api-reference/ethereum-json-rpc-api/eth_chainId
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
WORKER_SRC = REPO / "api" / "worker" / "src"
DECIDE_SPEC = {
    "spec_version": 1,
    "capabilities": {"software_engineering": "required"},
    "optimize": {"max": "software_engineering"},
    "explain": "summary",
    "limit": 1,
}


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stub", action="store_true", help="use the in-process facilitator")
    mode.add_argument("--live", action="store_true", help="authorize one Base Sepolia payment")
    parser.add_argument("--base-url", default="https://api.modelspec.dev")
    return parser.parse_args()


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required")
    return value


def _sign(requirement: dict[str, Any], private_key: str) -> dict[str, Any]:
    try:
        from eth_account import Account
        from eth_account.messages import encode_typed_data
    except ImportError:
        raise SystemExit("Install eth-account: python -m pip install 'eth-account>=0.13'") from None

    network = str(requirement["network"])
    if network != "eip155:84532":
        raise SystemExit(f"refusing to pay on {network}; this script is Base Sepolia only")
    account = Account.from_key(private_key)
    now = int(time.time())
    authorization = {
        "from": account.address,
        "to": requirement["payTo"],
        "value": int(requirement["amount"]),
        "validAfter": now - 60,
        "validBefore": now + 600,
        "nonce": "0x" + secrets.token_hex(32),
    }
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": requirement.get("extra", {}).get("name", "USDC"),
            "version": requirement.get("extra", {}).get("version", "2"),
            "chainId": 84532,
            "verifyingContract": requirement["asset"],
        },
        "message": authorization,
    }
    signature = Account.sign_message(
        encode_typed_data(full_message=typed), private_key
    ).signature.hex()
    wire_authorization = {
        **authorization,
        "value": str(authorization["value"]),
        "validAfter": str(authorization["validAfter"]),
        "validBefore": str(authorization["validBefore"]),
    }
    return {
        "x402Version": 2,
        "accepted": requirement,
        "payload": {"signature": "0x" + signature.removeprefix("0x"),
                    "authorization": wire_authorization},
    }


def _settlement(header: str | None) -> dict[str, Any]:
    """The decoded PAYMENT-RESPONSE header: the facilitator's settlement record."""
    if not header:
        return {}
    try:
        decoded = json.loads(base64.b64decode(header))
    except ValueError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _live(base_url: str) -> None:
    import httpx

    api_key = _required_env("MODELSPEC_API_KEY")
    private_key = _required_env("X402_SMOKE_PRIVATE_KEY")
    headers = {"authorization": f"Bearer {api_key}", "content-type": "application/json"}
    with httpx.Client(base_url=base_url.rstrip("/"), timeout=30) as client:
        offered = client.post("/v1/decide", headers=headers, json={"spec_version": 1})
        if offered.status_code != 402:
            raise SystemExit(f"expected 402, got {offered.status_code}: {offered.text[:300]}")
        body = offered.json()
        accepts = body.get("accepts") or []
        packs = body.get("error", {}).get("packs") or []
        if not packs:
            raise SystemExit("the 402 response offered no packs")
        pack = min(packs, key=lambda row: int(row["price"]["atomic"]))
        requirement = next(
            (row for row in accepts if row.get("amount") == pack["price"]["amount"]),
            None,
        )
        if requirement is None:
            raise SystemExit("the smallest pack has no matching x402 requirement")
        payment = _sign(requirement, private_key)
        paid_headers = {**headers, "PAYMENT-SIGNATURE": base64.b64encode(
            json.dumps(payment, separators=(",", ":")).encode()).decode()}
        credited = client.post("/v1/decide", headers=paid_headers, json={"spec_version": 1})
        if credited.status_code != 400:
            raise SystemExit(
                f"pack settlement failed: {credited.status_code} {credited.text[:300]}"
            )
        settlement = _settlement(credited.headers.get("PAYMENT-RESPONSE"))
        before = client.get("/v1/credits", headers=headers).json()
        if int(before.get("available", 0)) < int(pack["credits"]):
            raise SystemExit(f"pack was not credited: {before}")
        decision = client.post("/v1/decide", headers=headers, json=DECIDE_SPEC)
        if decision.status_code != 200 or not decision.json().get("results"):
            raise SystemExit(f"decision failed: {decision.status_code} {decision.text[:300]}")
        after = client.get("/v1/credits", headers=headers).json()
        print(json.dumps({
            "network": requirement["network"],
            "pack_credits": pack["credits"],
            "transaction": settlement.get("transaction"),
            "before": before["available"],
            "after": after["available"],
        }))


async def _stub() -> None:
    sys.path.insert(0, str(WORKER_SRC))
    import access_config
    import credits
    import x402
    from x402_facilitator import StubFacilitator

    policy = access_config.load_policy()
    pay_to = "0x209693bc6afc0c5328ba36faf03c514ef312287c"
    packs = x402.packs_from_policy(policy)
    per_credit = packs[0].atomic // packs[0].credits
    cfg = x402.Config(True, False, x402.NETWORK_BASE_SEPOLIA,
                      x402._norm_addr(x402.USDC_BASE_SEPOLIA), pay_to, per_credit,
                      "https://stub.invalid", "https://stub.invalid",
                      packs)
    ledger = credits.MemoryLedger()
    holder = x402.holder_from_key("live_stub")
    resource = "https://stub.invalid/v1/decide"

    async def invalid():
        return 400, {"error": {"code": "invalid_spec"}, "results": []}

    async def decision():
        return 200, {"results": [{"model_id": "example/ok"}]}

    discovery_status, offer = await x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda _name: None, holder=holder, resource_url=resource,
        envelope={}, produce=invalid, produce_unfunded=invalid, units=1)
    assert discovery_status == 402
    packs = offer.get("error", {}).get("packs") or []
    assert packs
    smallest = min(packs, key=lambda row: int(row["price"]["atomic"]))
    requirement = next(
        row for row in offer["accepts"]
        if row["amount"] == smallest["price"]["amount"]
    )
    payload = {
        "x402Version": 2,
        "accepted": requirement,
        "payload": {"signature": "0x" + "ab" * 65, "authorization": {
            "from": "0x857b06519e91e3a54538791bdbb0e22373e36b66", "to": pay_to,
            "value": requirement["amount"], "validAfter": "0",
            "validBefore": "9999999999", "nonce": "0x" + "11" * 32}},
    }
    header = base64.b64encode(json.dumps(payload).encode()).decode()
    settlement_status, _ = await x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda name: header if name.lower() == "payment-signature" else None,
        holder=holder, resource_url=resource, envelope={},
        produce=invalid, units=1)
    credits_status, before = await x402.balance_query(
        config=cfg, ledger=ledger, api_key="live_stub", envelope={})
    decision_status, _ = await x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda _name: None, holder=holder, resource_url=resource,
        envelope={}, produce=decision, units=1)
    after = await ledger.balance(holder)
    assert settlement_status == 400
    assert before["available"] == smallest["credits"]
    assert decision_status == 200
    print(json.dumps({
        "stub": True,
        "statuses": [discovery_status, settlement_status, credits_status, decision_status],
        "pack_credits": before["available"],
        "remaining_credits": after.available,
    }))


def main() -> None:
    args = _args()
    if args.stub:
        asyncio.run(_stub())
    else:
        _live(args.base_url)


if __name__ == "__main__":
    main()
