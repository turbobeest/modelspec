#!/usr/bin/env python3
"""Buy exactly one $5 Base USDC pack for 250 ModelSpec credits.

Jamie runs this through ``op run`` with MODELSPEC_API_KEY and
X402_PAYER_PRIVATE_KEY in the environment. Without the explicit spending
flag, only inspect and print the live offer. Requires httpx and eth-account.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import sys
import time
from typing import Any

import httpx

BASE_URL = "https://api.modelspec.dev"
NETWORK = "eip155:8453"
ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PAY_TO = "0x69429dbEEEE7218084AB5B896788f5fCE452419C"
AMOUNT = "5000000"
PACK_CREDITS = 250
INVALID_SPEC = {"spec_version": 1}


class BuyError(Exception):
    """A refusal whose message contains no remote body or credential."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's default error echoes unknown arguments, including secrets.
        raise BuyError("unsupported command-line arguments; use --help")


def _print(record: dict[str, Any]) -> None:
    text = json.dumps(record, sort_keys=True)
    for name in ("MODELSPEC_API_KEY", "X402_PAYER_PRIVATE_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            text = text.replace(json.dumps(value)[1:-1], "[REDACTED]")
    print(text, flush=True)


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise BuyError(f"{name} is required in the environment via op run")
    return value


def _decode(header: str | None) -> dict[str, Any]:
    if not header:
        raise BuyError("missing x402 payment header")
    try:
        body = json.loads(base64.b64decode(header, validate=True))
    except (ValueError, UnicodeError):
        raise BuyError("malformed x402 payment header") from None
    if not isinstance(body, dict):
        raise BuyError("x402 payment header must contain an object")
    return body


def _address(value: Any, expected: str, name: str) -> None:
    from eth_utils import is_checksum_address, to_checksum_address

    if not isinstance(value, str) or value.lower() != expected.lower():
        raise BuyError(f"refusing unexpected {name}")
    if not is_checksum_address(expected) or to_checksum_address(value) != expected:
        raise BuyError(f"refusing {name} with invalid EIP-55 checksum")
    letters = value[2:]
    if not (letters.islower() or letters.isupper()) and not is_checksum_address(value):
        raise BuyError(f"refusing {name} with invalid EIP-55 checksum")


def _offer(response: httpx.Response) -> dict[str, Any]:
    if response.status_code != 402:
        raise BuyError(f"expected live 402 offer, got HTTP {response.status_code}")
    body = response.json()
    required = _decode(response.headers.get("PAYMENT-REQUIRED"))
    if not isinstance(body, dict) or body.get("x402Version") != 2:
        raise BuyError("offer must use x402Version 2")
    accepts = body.get("accepts")
    if (required.get("x402Version") != 2 or required.get("accepts") != accepts
            or not isinstance(accepts, list) or not accepts):
        raise BuyError("402 body and PAYMENT-REQUIRED offers must agree")
    matches = [row for row in accepts if isinstance(row, dict) and row.get("amount") == AMOUNT]
    if len(matches) != 1:
        raise BuyError("requires exactly one $5 offer with amount 5000000; "
                       "refuses any other amount")
    row = matches[0]
    if row.get("network") != NETWORK:
        raise BuyError("refusing network other than eip155:8453")
    _address(row.get("asset"), ASSET, "asset")
    _address(row.get("payTo"), PAY_TO, "payTo")
    if row.get("scheme") != "exact":
        raise BuyError("refusing scheme other than exact")
    extra = row.get("extra")
    if (not isinstance(extra, dict) or type(extra.get("credits")) is not int
            or extra["credits"] != PACK_CREDITS):
        raise BuyError("$5 offer must buy exactly 250 credits")
    if extra.get("name") != "USD Coin" or extra.get("version") != "2":
        raise BuyError("offer must use the USD Coin version 2 signing domain")
    error = body.get("error")
    packs = error.get("packs") if isinstance(error, dict) else None
    if not isinstance(packs, list):
        raise BuyError("402 must list the $5 pack")
    matching_packs = [pack for pack in packs if isinstance(pack, dict)
                      and isinstance(pack.get("price"), dict)
                      and pack["price"].get("amount") == AMOUNT]
    if len(matching_packs) != 1:
        raise BuyError("402 must list exactly one $5 pack")
    pack = matching_packs[0]
    if (type(pack.get("credits")) is not int or pack["credits"] != PACK_CREDITS
            or type(pack["price"].get("atomic")) is not int
            or pack["price"]["atomic"] != 5_000_000):
        raise BuyError("$5 pack listing must match 5000000 units and 250 credits")
    return row


def _balance(client: httpx.Client, headers: dict[str, str]) -> int:
    response = client.get("/v1/credits", headers=headers)
    if response.status_code != 200:
        raise BuyError(f"credits query failed with HTTP {response.status_code}")
    body = response.json()
    available = body.get("available") if isinstance(body, dict) else None
    if type(available) is not int or available < 0:
        raise BuyError("credits query has no valid available balance")
    return available


def _sign(requirement: dict[str, Any], private_key: str) -> dict[str, Any]:
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    account = Account.from_key(private_key)
    now = int(time.time())
    authorization = {
        "from": account.address, "to": requirement["payTo"], "value": 5_000_000,
        "validAfter": now - 60, "validBefore": now + 60,
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
        "domain": {"name": requirement["extra"]["name"],
                   "version": requirement["extra"]["version"], "chainId": 8453,
                   "verifyingContract": requirement["asset"]},
        "message": authorization,
    }
    signature = Account.sign_message(
        encode_typed_data(full_message=typed), private_key
    ).signature.hex()
    return {
        "x402Version": 2, "accepted": requirement,
        "payload": {
            "signature": "0x" + signature.removeprefix("0x"),
            "authorization": {**authorization, "value": str(authorization["value"]),
                              "validAfter": str(authorization["validAfter"]),
                              "validBefore": str(authorization["validBefore"])},
        },
    }


def _buy(client: httpx.Client, headers: dict[str, str], offer: dict[str, Any],
         before: int, private_key: str) -> int:
    try:
        payment = _sign(offer, private_key)
    except Exception:
        raise BuyError("could not sign payment; check signer dependency and payer key") from None
    signature = base64.b64encode(json.dumps(payment, separators=(",", ":")).encode()).decode()
    status = None
    settlement: dict[str, Any] = {}
    try:
        # One submission only. A timeout can mean the payment already settled.
        response = client.post("/v1/decide", json=INVALID_SPEC,
                               headers={**headers, "PAYMENT-SIGNATURE": signature})
        status = response.status_code
        settlement = _decode(response.headers.get("PAYMENT-RESPONSE"))
    except (httpx.HTTPError, BuyError, ValueError):
        pass
    transaction = settlement.get("transaction")
    if not isinstance(transaction, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", transaction):
        transaction = None
    after = None
    try:
        after = _balance(client, headers)
    except (httpx.HTTPError, BuyError, ValueError):
        pass
    _print({"before": before, "transaction": transaction, "after": after,
            "payment_http_status": status})
    if (status != 400 or settlement.get("success") is not True
            or settlement.get("network") != NETWORK or transaction is None
            or after is None or after - before != PACK_CREDITS):
        raise BuyError("payment or 250-credit increase unconfirmed; exiting without retry; "
                       "inspect the transaction and credits before any new run")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        parser = Parser(description=__doc__, allow_abbrev=False)
        parser.add_argument("--i-understand-this-spends-real-usdc", action="store_true",
                            help="authorize exactly one $5 USDC payment on Base mainnet")
        args = parser.parse_args(argv)
        headers = {"authorization": f"Bearer {_required_env('MODELSPEC_API_KEY')}"}
        with httpx.Client(base_url=BASE_URL, timeout=30, follow_redirects=False,
                          trust_env=False) as client:
            before = _balance(client, headers)
            _print({"before": before})
            if before != 0:
                raise BuyError("requires an unfunded API key for the live 402 pack offer")
            offered = _offer(client.post("/v1/decide", headers=headers, json=INVALID_SPEC))
            _print({"dry_run": not args.i_understand_this_spends_real_usdc,
                    "offer": offered, "pack_credits": PACK_CREDITS})
            if not args.i_understand_this_spends_real_usdc:
                return 0
            return _buy(client, headers, offered, before,
                        _required_env("X402_PAYER_PRIVATE_KEY"))
    except BuyError as exc:
        _print({"error": str(exc)})
    except ImportError:
        _print({"error": "install eth-account with this Python interpreter"})
    except (httpx.HTTPError, ValueError, TypeError):
        _print({"error": "request failed or response malformed; payment was not retried"})
    return 1


if __name__ == "__main__":
    sys.exit(main())
