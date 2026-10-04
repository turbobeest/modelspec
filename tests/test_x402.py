"""MODEL-75: x402 prepaid credits, settled before delivery, billed only on success."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
sys.path.insert(0, str(WORKER_SRC))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cdp_auth  # noqa: E402
import credits  # noqa: E402
import x402  # noqa: E402
from test_cdp_auth import (  # noqa: E402
    decode_unverified,
    generate_ed25519,
    openssl_sign_async,
)
from x402_facilitator import CdpFacilitator, FacilitatorError, StubFacilitator  # noqa: E402

PAY_TO = "0x209693bc6afc0c5328ba36faf03c514ef312287c"
PAYER = "0x857b06519e91e3a54538791bdbb0e22373e36b66"
ENVELOPE = {"schema_version": "1.0", "service_commit": "test"}
RESOURCE = "https://api.modelspec.dev/v1/rank"


def _cfg(**kwargs: Any) -> x402.Config:
    base = dict(
        enabled=True,
        mainnet=False,
        network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA),
        pay_to=PAY_TO,
        price_atomic=1000,
        facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
    )
    base.update(kwargs)
    return x402.Config(**base)  # type: ignore[arg-type]


def _payload(*, nonce: str = "0x" + "11" * 32, value: str = "1000",
             to: str = PAY_TO, sig: str = "0x" + "ab" * 65) -> dict[str, Any]:
    return {
        "x402Version": 2,
        "accepted": {
            "scheme": "exact",
            "network": x402.NETWORK_BASE_SEPOLIA,
            "amount": value,
            "asset": x402._norm_addr(x402.USDC_BASE_SEPOLIA),
            "payTo": to,
        },
        "payload": {
            "signature": sig,
            "authorization": {
                "from": PAYER,
                "to": to,
                "value": value,
                "validAfter": "0",
                "validBefore": "9999999999",
                "nonce": nonce,
            },
        },
    }


def _header(payload: dict[str, Any]) -> dict[str, str]:
    raw = json.dumps(payload).encode("utf-8")
    return {x402.PAYMENT_SIGNATURE: base64.b64encode(raw).decode("ascii")}


def _get_header(headers: dict[str, str]):
    lowered = {k.lower(): v for k, v in headers.items()}

    def get(name: str) -> str | None:
        return lowered.get(name.lower())

    return get


async def _ok() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "result": [{"model_id": "example/ok"}]}


async def _empty() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "result": []}


async def _no_match() -> tuple[int, dict[str, Any]]:
    return 422, {**ENVELOPE, "error": {"code": "no_match", "message": "none"}, "result": []}


async def _boom() -> tuple[int, dict[str, Any]]:
    return 500, {**ENVELOPE, "error": {"code": "export_unavailable", "message": "x"}, "result": []}


def _run(coro):
    return asyncio.run(coro)


def test_sepolia_smoke_runs_only_against_the_stub_in_the_suite():
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "x402_sepolia_smoke.py"), "--stub"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    )
    assert json.loads(completed.stdout) == {
        "stub": True,
        "statuses": [402, 400, 200, 200],
        "pack_credits": 1250,
        "remaining_credits": 1249,
    }


# ── 402 discovery ────────────────────────────────────────────────────────────

def test_unfunded_request_returns_well_formed_402_naming_price_and_how_to_pay():
    produced = []

    async def produce():
        produced.append(1)
        return await _ok()

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert produced == []
    error = body["error"]
    assert error["code"] == "payment_required"
    assert error["price"]["amount"] == "1000"
    assert error["price"]["credits"] == 1
    assert error["price"]["placeholder"] is False
    assert error["price"]["placeholder_note"] == (
        "Live price: keyed requests show the smallest offered pack; "
        "keyless requests show this call's weighted price."
    )
    assert error["payTo"] == PAY_TO
    assert error["resource"] == RESOURCE
    assert error["accepts"][0]["network"] == x402.NETWORK_BASE_SEPOLIA
    assert "PAYMENT-SIGNATURE" in error["how_to_pay"]
    headers = x402.http_headers(status, body)
    assert x402.PAYMENT_REQUIRED_HEADER in headers
    decoded = json.loads(base64.b64decode(headers[x402.PAYMENT_REQUIRED_HEADER]))
    assert decoded["x402Version"] == 2
    assert decoded["accepts"][0]["payTo"] == PAY_TO


def test_per_call_price_scales_with_the_endpoint_weight():
    cheap = x402.payment_required_body(_cfg(price_atomic=1000), ENVELOPE, RESOURCE)
    dear = x402.payment_required_body(
        _cfg(price_atomic=1000), ENVELOPE, RESOURCE, units=10)
    assert cheap["error"]["price"]["amount"] == "1000"
    assert dear["error"]["price"]["amount"] == "10000"
    assert dear["error"]["price"]["usd"] == 0.01


def test_keyed_402_offers_every_card_pack_with_atomic_usdc_fields():
    policy = __import__("access_config").load_policy()
    cfg = x402.load_config(type("Env", (), {
        "TIER_POLICY": (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(),
        "X402_ENABLED": "true",
        "X402_PAY_TO": PAY_TO,
    })())
    body = x402.payment_required_body(
        cfg, ENVELOPE, RESOURCE, offer_packs=True, units=1)
    offers = body["error"]["packs"]
    assert body["error"]["price"]["atomic"] == 5_000_000
    assert body["error"]["price"]["credits"] == 1250
    assert body["error"]["price"]["placeholder"] is False
    assert body["error"]["price"]["placeholder_note"] == (
        "Live price: keyed requests show the smallest offered pack; "
        "keyless requests show this call's weighted price."
    )
    assert [(offer["credits"], offer["price"]["atomic"]) for offer in offers] == [
        (1250, 5_000_000),
        (7500, 25_000_000),
        (20000, 50_000_000),
        (50000, 100_000_000),
    ]
    assert all(offer["price"]["asset"] == cfg.asset for offer in offers)
    assert all(offer["price"]["network"] == cfg.network for offer in offers)
    assert all(offer["payTo"] == PAY_TO for offer in offers)
    assert len(body["accepts"]) == 4
    assert len(policy.billing.prices) > len(offers)


def test_enabled_keyed_request_discovers_packs_before_the_free_answer():
    policy = __import__("access_config").load_policy()
    cfg = _cfg(price_atomic=4_000, packs=x402.packs_from_policy(policy))
    holder = "key:" + "7" * 64
    produced: list[str] = []

    async def unfunded():
        produced.append("free")
        return 400, {"error": {"code": "invalid_spec"}, "results": []}

    status, body = _run(x402.charge(
        config=cfg, ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, produce_unfunded=unfunded))

    assert status == 402
    assert produced == []
    assert [row["credits"] for row in body["error"]["packs"]] == [
        1250, 7500, 20000, 50000,
    ]


def test_billing_docs_distinguish_exhausted_behavior_by_x402_flag():
    text = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    billing = " ".join(text.split())
    assert "When `X402_ENABLED` is off" in billing
    assert "When `X402_ENABLED` is on" in billing
    assert "HTTP 402" in billing
    assert "all four card-pack offers" in billing


def test_keyless_per_call_price_uses_smallest_pack_rate_times_weight():
    cfg = x402.load_config(type("Env", (), {
        "TIER_POLICY": (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(),
        "X402_ENABLED": "true",
        "X402_PAY_TO": PAY_TO,
    })())
    body = x402.payment_required_body(
        cfg, ENVELOPE, RESOURCE, offer_packs=False, units=5)
    assert cfg.price_atomic == 4_000
    assert body["error"]["price"] == {
        "amount": "20000",
        "atomic": 20_000,
        "usd": 0.02,
        "asset": cfg.asset,
        "network": cfg.network,
        "currency": "USDC",
        "credits": 5,
        "placeholder": False,
        "placeholder_note": (
            "Live price: keyed requests show the smallest offered pack; "
            "keyless requests show this call's weighted price."
        ),
    }


def test_disabled_flag_is_a_no_op():
    status, body = _run(x402.charge(
        config=_cfg(enabled=False), ledger=credits.MemoryLedger(),
        facilitator=StubFacilitator(), get_header=_get_header({}), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert body["result"]


def test_all_flags_off_leave_the_answer_bytes_unchanged():
    expected = json.dumps((200, {**ENVELOPE, "result": [{"model_id": "example/ok"}]}),
                          separators=(",", ":"), sort_keys=True)
    actual = _run(x402.charge(
        config=_cfg(enabled=False), ledger=credits.MemoryLedger(),
        facilitator=StubFacilitator(), get_header=_get_header({}), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert json.dumps(actual, separators=(",", ":"), sort_keys=True) == expected


# ── settlement credits once; replay does not ─────────────────────────────────

def test_settled_payment_credits_the_balance_exactly_once():
    ledger = credits.MemoryLedger()
    spy = StubFacilitator()
    holder = "key:" + "a" * 64
    payload = _payload(value="3000")  # three units
    status, body = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=spy,
        get_header=_get_header(_header(payload)), holder=holder,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert [c[0] for c in spy.calls] == ["verify", "settle"]
    bal = _run(ledger.balance(holder))
    # 3 credited, 1 committed for this success
    assert bal.available == 2
    assert bal.reserved == 0

    spy.calls.clear()
    status, body = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=spy,
        get_header=_get_header(_header(payload)), holder=holder,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert spy.calls == []  # replay must not re-settle
    bal = _run(ledger.balance(holder))
    assert bal.available == 1


def test_keyed_pack_payment_adds_the_exact_pack_to_the_card_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "9" * 64
    policy = __import__("access_config").load_policy()
    cfg = _cfg(price_atomic=4_000, packs=x402.packs_from_policy(policy))
    status, _ = _run(x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(_header(_payload(value="5000000"))), holder=holder,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok,
        units=1, pack_expiry_days=policy.credits.pack_expiry_days,
        now=__import__("datetime").datetime(2026, 9, 26, tzinfo=__import__("datetime").UTC)))
    assert status == 200
    balance = _run(ledger.balance(holder))
    assert balance.available == 1249
    assert balance.packs == 1249
    assert balance.grants[0].source == "x402"
    assert balance.grants[0].expires_at == "2027-09-26T00:00:00Z"


def test_replayed_settlement_does_not_credit_twice():
    ledger = credits.MemoryLedger()
    pid = x402.payment_id(_payload())
    first = _run(ledger.credit("key:h", pid, 5, "0xabc"))
    second = _run(ledger.credit("key:h", pid, 5, "0xabc"))
    assert first.credited is True
    assert second.credited is False
    assert second.reason == "replay"
    assert _run(ledger.balance("key:h")).available == 5


# ── verify, settle, then produce ─────────────────────────────────────────────

def test_attack_verification_ordering_settle_before_produce():
    spy = StubFacilitator()
    trace = x402.ChargeTrace()

    async def produce():
        assert [c[0] for c in spy.calls] == ["verify", "settle"], (
            "produce ran before verify and settle; this test fails if the order "
            "in x402.charge is reversed")
        return await _ok()

    status, _ = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce, trace=trace))
    assert status == 200
    assert trace.events.index("verify") < trace.events.index("settle")
    assert trace.events.index("settle") < trace.events.index("produce")


def test_settlement_before_answer_fails_if_the_order_is_reversed():
    """The acceptance criterion: this assertion is false if produce is moved above settle."""
    spy = StubFacilitator()

    async def produce():
        names = [c[0] for c in spy.calls]
        assert "settle" in names and names.index("settle") == len(names) - 1
        return await _ok()

    _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder="key:" + "b" * 64,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce))


# ── 500 / no-match / empty do not decrement ──────────────────────────────────

def test_a_500_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "c" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_boom))
    assert status == 500
    assert _run(ledger.balance(holder)).available == 1
    assert _run(ledger.balance(holder)).reserved == 0


def test_a_no_match_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "d" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_no_match))
    assert status == 422
    assert _run(ledger.balance(holder)).available == 1


def test_an_empty_result_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "e" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_empty))
    assert status == 200
    assert _run(ledger.balance(holder)).available == 1


@pytest.mark.parametrize("status,body,billable", [
    (200, {"results": [{"model": "lab/model"}]}, True),
    (200, {"results": []}, False),
    (400, {"results": [{"model": "lab/model"}]}, False),
    (500, {"results": [{"model": "lab/model"}]}, False),
])
def test_decision_answers_commit_only_for_a_nonempty_success(status, body, billable):
    assert x402.is_billable_success(status, body) is billable


def test_full_decision_reserves_two_credits_and_releases_them_on_error():
    ledger = credits.MemoryLedger()
    holder = "key:" + "8" * 64
    _run(ledger.credit(holder, "seed", 2, "0x1"))

    async def refused():
        balance = await ledger.balance(holder)
        assert balance.reserved == 2
        return 400, {"error": {"code": "invalid_spec"}, "results": []}

    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=refused, units=2))
    assert status == 400
    balance = _run(ledger.balance(holder))
    assert balance.available == 2
    assert balance.reserved == 0


# ── concurrency ──────────────────────────────────────────────────────────────

def test_concurrent_requests_cannot_drive_the_balance_negative_or_double_spend():
    ledger = credits.MemoryLedger()
    holder = "key:" + "f" * 64
    _run(ledger.credit(holder, "seed", 1, "0x1"))

    async def once():
        return await x402.charge(
            config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
            get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
            envelope=ENVELOPE, produce=_ok)

    async def both():
        return await asyncio.gather(once(), once())

    results = _run(both())
    statuses = sorted(status for status, _ in results)
    assert statuses == [200, 402]
    bal = _run(ledger.balance(holder))
    assert bal.available == 0
    assert bal.reserved == 0
    assert bal.total == 0


# ── attack classes from docs/agent-commerce-assessment.md §5 ─────────────────

def test_attack_free_riding_unfunded_never_produces():
    async def produce():
        raise AssertionError("free-riding: produce ran with no payment and no balance")

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert body["error"]["code"] == "payment_required"


def test_attack_toctou_reserve_before_produce():
    ledger = credits.MemoryLedger()
    holder = "key:" + "g" * 64
    _run(ledger.credit(holder, "seed", 1, "0x1"))
    reserved_at_produce: list[int] = []

    async def produce():
        reserved_at_produce.append(_run(ledger.balance(holder)).reserved)
        return await _ok()

    # produce is async and we cannot call _run from inside the event loop.
    async def produce_async():
        reserved_at_produce.append((await ledger.balance(holder)).reserved)
        return await _ok()

    _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce_async))
    assert reserved_at_produce == [1], (
        "produce ran without a reservation; a TOCTOU check-then-act would look like this")
    assert _run(ledger.balance(holder)).available == 0


def test_attack_front_running_wrong_payto_never_settles():
    spy = StubFacilitator()
    other = "0x0000000000000000000000000000000000000001"
    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload(to=other))), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 400
    assert body["error"]["code"] == "invalid_payment"
    assert spy.calls == []


# ── per-call fallback; balance query ─────────────────────────────────────────

def test_per_call_402_fallback_works_with_no_stored_balance():
    spy = StubFacilitator()
    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert body["result"]
    assert [c[0] for c in spy.calls] == ["verify", "settle"]


def test_drive_by_replay_does_not_get_a_second_result():
    ledger = credits.MemoryLedger()
    headers = _header(_payload(nonce="0x" + "cd" * 32))
    first = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok))
    assert first[0] == 200
    second = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok))
    assert second[0] == 402


def test_weighted_keyless_verification_failure_requotes_the_full_call_price():
    cfg = _cfg(price_atomic=4_000)
    status, body = _run(x402.charge(
        config=cfg, ledger=credits.MemoryLedger(),
        facilitator=StubFacilitator(valid=False),
        get_header=_get_header(_header(_payload(value="8000"))), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok, units=2))

    assert status == 402
    assert body["error"]["code"] == "payment_failed"
    assert body["error"]["price"]["amount"] == "8000"
    assert body["error"]["price"]["credits"] == 2


def test_weighted_keyless_settlement_failure_requotes_the_full_call_price():
    cfg = _cfg(price_atomic=4_000)
    status, body = _run(x402.charge(
        config=cfg, ledger=credits.MemoryLedger(),
        facilitator=StubFacilitator(settle_ok=False),
        get_header=_get_header(_header(_payload(value="8000"))), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok, units=2))

    assert status == 402
    assert body["error"]["code"] == "payment_failed"
    assert body["error"]["price"]["amount"] == "8000"
    assert body["error"]["price"]["credits"] == 2


def test_weighted_keyless_replay_requotes_the_full_call_price():
    cfg = _cfg(price_atomic=4_000)
    ledger = credits.MemoryLedger()
    headers = _header(_payload(value="8000", nonce="0x" + "ef" * 32))
    first = _run(x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, units=2))
    second = _run(x402.charge(
        config=cfg, ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, units=2))

    assert first[0] == 200
    assert second[0] == 402
    assert second[1]["error"]["price"]["amount"] == "8000"
    assert second[1]["error"]["price"]["credits"] == 2


def test_balance_is_queryable_by_the_holder():
    ledger = credits.MemoryLedger()
    key = "live_secret_example"
    holder = x402.holder_from_key(key)
    _run(ledger.credit(holder, "p", 4, "0x"))
    status, body = _run(x402.balance_query(
        config=_cfg(), ledger=ledger, api_key=key, envelope=ENVELOPE))
    assert status == 200
    assert body["available"] == 4
    assert body["holder"] == holder
    assert body["endpoint"] == "credits"


def test_balance_query_without_a_key_is_401():
    status, body = _run(x402.balance_query(
        config=_cfg(), ledger=credits.MemoryLedger(), api_key=None, envelope=ENVELOPE))
    assert status == 401
    assert body["error"]["code"] == "missing_holder"


def test_failed_verify_never_produces():
    spy = StubFacilitator(valid=False)

    async def produce():
        raise AssertionError("produce after failed verify")

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert body["error"]["code"] == "payment_failed"
    assert [c[0] for c in spy.calls] == ["verify"]


def test_mainnet_is_off_by_default_and_refuses_a_mainnet_network_var():
    cfg = _cfg(mainnet=False, network=x402.NETWORK_BASE)
    assert cfg.mainnet is False
    status, body = _run(x402.charge(
        config=cfg, ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 400


# ── facilitator client; no network ───────────────────────────────────────────

def test_facilitator_client_posts_to_the_documented_paths():
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(url)
        if url.endswith("/verify"):
            return 200, {"isValid": True, "payer": PAYER}
        return 200, {"success": True, "transaction": "0x1", "payer": PAYER,
                     "network": x402.NETWORK_BASE_SEPOLIA}

    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post)
    _run(client.verify(_payload(), {}))
    _run(client.settle(_payload(), {}))
    assert seen == [
        "https://api.cdp.coinbase.com/platform/v2/x402/verify",
        "https://api.cdp.coinbase.com/platform/v2/x402/settle",
    ]


def _minting_env(*, mainnet: bool = False, static: str = "",
                 key_id: str = "", secret: str = "") -> Any:
    env = type("E", (), {})()
    env.CDP_API_KEY_ID = key_id
    env.CDP_API_KEY_SECRET = secret
    env.CDP_JWT = static
    env.CDP_SIGN = openssl_sign_async
    env.X402_MAINNET = "true" if mainnet else "false"
    return env


def _bearer(headers: dict[str, str]) -> str:
    value = headers.get("Authorization") or headers.get("authorization") or ""
    assert value.startswith("Bearer ")
    return value.split(" ", 1)[1]


def test_each_facilitator_request_carries_a_fresh_unexpired_jwt_for_that_path():
    secret, _der, _pub = generate_ed25519()
    key_id = str(uuid.uuid4())
    seen: list[tuple[str, str]] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append((url, _bearer(headers)))
        if url.endswith("/verify"):
            return 200, {"isValid": True, "payer": PAYER}
        return 200, {"success": True, "transaction": "0x1", "payer": PAYER,
                     "network": x402.NETWORK_BASE_SEPOLIA}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id=key_id, secret=secret),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    now = int(time.time())
    _run(client.verify(_payload(), {}))
    _run(client.settle(_payload(), {}))
    assert len(seen) == 2
    nonces = []
    for url, token in seen:
        header, claims, _sig = decode_unverified(token)
        path = url.split("coinbase.com", 1)[1]
        assert claims["uri"] == f"POST api.cdp.coinbase.com{path}"
        assert claims["nbf"] <= now + 1
        assert claims["exp"] > now
        assert claims["exp"] - claims["nbf"] == 120
        assert header["kid"] == key_id
        nonces.append(header["nonce"])
    assert seen[0][1] != seen[1][1]
    assert nonces[0] != nonces[1]
    assert seen[0][0].endswith("/v2/x402/verify")
    assert seen[1][0].endswith("/v2/x402/settle")


def test_static_cdp_jwt_is_refused_when_mainnet_is_on():
    auth = cdp_auth.auth_from_env(
        _minting_env(mainnet=True, static="header.payload.sig"),
        mainnet=True,
    )
    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        raise AssertionError("must not post")

    client = CdpFacilitator(
        "https://api.cdp.coinbase.com/platform", post=post, auth=auth,
    )
    with pytest.raises(FacilitatorError, match="local-testing override"):
        _run(client.verify(_payload(), {}))


def test_static_cdp_jwt_is_a_sepolia_testing_override_only():
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(static="static.local.test"),
        mainnet=False,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    assert seen == ["static.local.test"]


def test_api_key_minting_wins_over_static_jwt():
    secret, _der, _pub = generate_ed25519()
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id="kid", secret=secret, static="static.must.not.be.used"),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    assert seen[0] != "static.must.not.be.used"
    _header, claims, _sig = decode_unverified(seen[0])
    assert claims["uri"].endswith("/v2/x402/verify")


def test_secret_and_jwt_do_not_appear_in_facilitator_logs(caplog, capsys):
    secret, _der, _pub = generate_ed25519()
    tokens: list[str] = []
    caplog.set_level(logging.DEBUG)

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        tokens.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id="kid", secret=secret),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    captured = capsys.readouterr()
    haystack = "\n".join([caplog.text, captured.out, captured.err])
    assert secret not in haystack
    assert tokens[0] not in haystack
    assert "Bearer " not in haystack


def test_no_test_calls_the_network():
    """The production post adapter is worker_post (js.fetch). Tests inject `post`."""
    import inspect
    from x402_facilitator import worker_post
    source = inspect.getsource(test_facilitator_client_posts_to_the_documented_paths)
    assert "worker_post" not in source
    assert worker_post.__name__ == "worker_post"


def test_wrangler_ships_the_flag_off_and_sepolia():
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("//"))
    assert '"X402_ENABLED": "false"' in live
    assert '"X402_MAINNET": "false"' in live
    assert '"X402_NETWORK": "eip155:84532"' in live
    assert '"class_name": "CreditsObject"' in live
    assert '"X402_PAY_TO": ""' in live
    assert "CDP_API_KEY" not in live
    assert "CDP_JWT" not in live


def _wrangler_config() -> dict[str, Any]:
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//"))
    return json.loads(live)


def test_production_x402_config_stays_off_and_has_no_receiver():
    config = _wrangler_config()
    assert config["vars"]["HUMAN_GATE_ENABLED"] == "false"
    assert config["vars"]["ACCESS_ENFORCED"] == "true"
    assert config["vars"]["BILLING_ENABLED"] == "true"
    assert config["vars"]["X402_ENABLED"] == "false"
    assert config["vars"]["X402_MAINNET"] == "false"
    assert config["vars"]["X402_PAY_TO"] == ""
    assert config["workers_dev"] is False
    assert config["routes"] == [
        {"pattern": "api.modelspec.dev/*", "zone_name": "modelspec.dev"}
    ]


def test_staging_x402_config_is_isolated_on_base_sepolia():
    config = _wrangler_config()
    staging = config["env"]["staging"]

    assert f'{config["name"]}-staging' == "modelspec-rank-staging"
    assert staging["workers_dev"] is True
    assert staging["routes"] == []
    assert staging["vars"] == {
        "EXPORT_ORIGIN": "https://modelspec.dev",
        "BUILD_COMMIT": "dev",
        "ACCESS_ENFORCED": "false",
        "VISIT_GATE_ENABLED": "false",
        "VISIT_DECIDE_DAY_LIMIT": "300",
        "VISIT_DECIDE_BURST_LIMIT": "30",
        "VISIT_VOCABULARY_DAY_LIMIT": "60",
        "VISIT_VOCABULARY_BURST_LIMIT": "10",
        "HUMAN_GATE_ENABLED": "true",
        "BILLING_ENABLED": "false",
        "FEEDBACK_ENABLED": "false",
        "X402_ENABLED": "true",
        "X402_MAINNET": "false",
        "X402_NETWORK": "eip155:84532",
        "X402_ASSET": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "X402_PAY_TO": "0x1e62c42388271C68ce55e7E39d85912ACB918529",
        "X402_FACILITATOR_URL": "https://api.cdp.coinbase.com/platform",
    }

    production_kv = {row["binding"]: row for row in config["kv_namespaces"]}
    staging_kv = {row["binding"]: row for row in staging["kv_namespaces"]}
    assert staging_kv.keys() == production_kv.keys()
    assert all("id" in row for row in production_kv.values())
    assert all("id" not in row for row in staging_kv.values())
    assert staging["durable_objects"] == config["durable_objects"]


def test_credits_modules_do_not_use_workers_kv():
    for name in ("credits.py", "credits_do.py"):
        source = (WORKER_SRC / name).read_text(encoding="utf-8")
        assert "CloudflareKV" not in source
        assert "kv_namespaces" not in source


# ── Worker wiring ────────────────────────────────────────────────────────────

@pytest.fixture
def entry(monkeypatch):
    import importlib.util
    import types

    js = types.ModuleType("js")

    async def _no_fetch(url):
        raise AssertionError(f"unexpected fetch of {url}")

    js.fetch = _no_fetch
    workers = types.ModuleType("workers")

    class _Response:
        def __init__(self, body, status=200, headers=None):
            self.body, self.status, self.headers = body, status, headers or {}

        def json(self):
            return json.loads(self.body)

    workers.Response = _Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    class _DurableObject:
        # Same signature as the real base: entry.py imports credits_do, which
        # stays cached in sys.modules, and a later test that constructs
        # CreditsObject(ctx, env) must not inherit a no-argument __init__.
        def __init__(self, ctx=None, env=None):
            self.ctx, self.env = ctx, env

    workers.DurableObject = _DurableObject
    monkeypatch.setitem(sys.modules, "js", js)
    monkeypatch.setitem(sys.modules, "workers", workers)
    for path in (str(REPO_ROOT), str(WORKER_SRC)):
        if path not in sys.path:
            sys.path.insert(0, path)
    spec = importlib.util.spec_from_file_location(
        "modelspec_worker_entry_x402", WORKER_SRC / "entry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    async def load_export(origin, force=False):
        return {"build": {"commit": "deadbeef", "built_at": "t",
                          "export_schema_version": "2.0"},
                "candidates": [{"id": "example/ok", "name": "ok"}]}, None

    module._load_export = load_export
    return module


class _Req:
    def __init__(self, path, body=None, method="POST", headers=None):
        self.url = f"https://api.modelspec.test{path}"
        self.method = method
        self._body = json.dumps(body) if not isinstance(body, str) else body
        self._headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.headers = type("H", (), {"get": lambda _s, n: self._headers.get(n.lower())})()

    async def text(self):
        return self._body or ""


def _entry_env(**overrides):
    class KVBinding:
        def __init__(self):
            self.store = __import__("access_kv").MemoryKV()

        async def get(self, name):
            return await self.store.get(name)

        async def put(self, name, value, options=None, *, expiration_ttl=None):
            ttl = expiration_ttl
            if options is not None:
                ttl = options.get("expirationTtl")
            await self.store.put(name, value, expiration_ttl=ttl)

        async def delete(self, name):
            await self.store.delete(name)

    values = {
        "BUILD_COMMIT": "c0ffee",
        "EXPORT_ORIGIN": "https://modelspec.test",
        "ACCESS_ENFORCED": "false",
        "BILLING_ENABLED": "false",
        "TIER_POLICY": (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(
            encoding="utf-8"),
        "X402_ENABLED": "true",
        "X402_PAY_TO": PAY_TO,
        "X402_NETWORK": x402.NETWORK_BASE_SEPOLIA,
        "X402_ASSET": x402.USDC_BASE_SEPOLIA,
        "ACCESS": KVBinding(),
        "CREDITS": credits.MemoryLedger(),
        "X402_FACILITATOR": StubFacilitator(),
        "VISITOR_HMAC_KEY": "fixture-visitor-key-0123456789",
    }
    values.update(overrides)
    return type("E", (), values)()


def _decision_holder():
    snapshot = type("Snapshot", (), {"snapshot_id": "snapshot-test"})()
    return type("Holder", (), {"snapshot": snapshot, "headers": lambda _self: {}})()


def _decision_request(origin=None, *, ip="203.0.113.8", key=None):
    headers = {"CF-Connecting-IP": ip}
    if origin is not None:
        headers["Origin"] = origin
    if key is not None:
        headers["Authorization"] = f"Bearer {key}"
    return _Req("/v1/decide", {"task": "choose a model"}, headers=headers)


def _decision_worker(entry, env=None):
    worker = entry.Default()
    worker.env = env or _entry_env()
    entry._decision_holder = lambda _origin: _decision_holder()

    async def decide(_payload, _origin, _expected, _transport):
        return 200, {
            "contract_version": "1.0",
            "endpoint": "decide",
            "snapshot": "snapshot-test",
            "results": [{"model_id": "example/ok"}],
        }

    worker._decide = decide
    return worker


@pytest.mark.parametrize("origin", [
    "https://modelspec.dev",
    "https://www.modelspec.dev",
    "https://internal.modelspec-7np.pages.dev",
])
def test_entry_site_origins_receive_the_free_tier_when_x402_is_on(entry, origin):
    response = asyncio.run(_decision_worker(entry).fetch(_decision_request(origin)))

    assert response.status == 200
    assert response.json()["results"] == [{"model_id": "example/ok"}]
    assert x402.PAYMENT_REQUIRED_HEADER not in response.headers
    assert response.headers["x-modelspec-tier"] == "free"


def test_enforcement_refuses_a_spoofed_site_origin_when_x402_is_on(entry):
    env = _entry_env(
        ACCESS_ENFORCED="true",
        VISIT_GATE_ENABLED="false",
        HUMAN_GATE_ENABLED="false",
    )
    produced = []

    async def decide(*_args, **_kwargs):
        produced.append("decide")
        return 200, {"results": [{"model_id": "example/ok"}]}

    worker = _decision_worker(entry, env)
    worker._decide = decide
    response = asyncio.run(worker.fetch(_decision_request("https://modelspec.dev")))

    assert produced == []
    assert response.status == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_entry_site_origin_is_limited_per_visitor_when_x402_is_on(entry):
    worker = _decision_worker(entry)
    responses = [
        asyncio.run(worker.fetch(_decision_request("https://modelspec.dev")))
        for _ in range(6)
    ]

    assert [response.status for response in responses] == [200] * 5 + [429]
    assert responses[-1].json()["error"]["code"] == "rate_limited"
    assert x402.PAYMENT_REQUIRED_HEADER not in responses[-1].headers
    another_visitor = asyncio.run(worker.fetch(_decision_request(
        "https://modelspec.dev", ip="198.51.100.21",
    )))
    assert another_visitor.status == 200


def test_entry_meter_writes_neither_the_ip_nor_its_bare_hash(entry):
    import hashlib

    env = _entry_env()
    ip = "203.0.113.8"
    asyncio.run(_decision_worker(entry, env).fetch(_decision_request("https://modelspec.dev", ip=ip)))
    blob = " ".join(env.ACCESS.store.data) + " " + " ".join(env.ACCESS.store.data.values())
    assert env.ACCESS.store.data
    assert ip not in blob
    assert hashlib.sha256(ip.encode()).hexdigest() not in blob


def test_entry_site_origin_without_the_visitor_key_takes_the_paid_path(entry):
    env = _entry_env(VISITOR_HMAC_KEY=None)
    response = asyncio.run(_decision_worker(entry, env).fetch(
        _decision_request("https://modelspec.dev")))

    assert response.status == 402
    assert env.ACCESS.store.data == {}


@pytest.mark.parametrize("origin", [None, "https://agent.example"])
def test_entry_non_site_anonymous_callers_receive_per_call_402(entry, origin):
    response = asyncio.run(_decision_worker(entry).fetch(_decision_request(origin)))

    assert response.status == 402
    assert response.json()["error"]["code"] == "payment_required"
    assert "price" in response.json()["error"]
    assert "packs" not in response.json()["error"]


def test_entry_zero_balance_key_receives_pack_offer_even_from_site(entry):
    key = "live_zero_balance"
    env = _entry_env()
    policy = __import__("access_config").load_policy(env)
    asyncio.run(__import__("access_keys").issue(
        env.ACCESS, tier="free", owner="test", now=datetime.now(UTC),
        policy=policy, secret=key,
    ))

    response = asyncio.run(_decision_worker(entry, env).fetch(_decision_request(
        "https://modelspec.dev", key=key,
    )))

    assert response.status == 402
    assert response.json()["error"]["code"] == "payment_required"
    assert [pack["credits"] for pack in response.json()["error"]["packs"]] == [
        1250, 7500, 20000, 50000,
    ]


def test_entry_unfunded_with_flag_on_is_402_and_does_not_fetch(entry):
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.ACCESS_ENFORCED = "false"
    env.X402_ENABLED = "true"
    env.X402_PAY_TO = PAY_TO
    env.X402_NETWORK = x402.NETWORK_BASE_SEPOLIA
    env.X402_ASSET = x402.USDC_BASE_SEPOLIA
    env.CREDITS = credits.MemoryLedger()
    env.X402_FACILITATOR = StubFacilitator()
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req("/v1/rank", {"use_case": "coding"})))
    assert response.status == 402
    body = response.json()
    assert body["error"]["code"] == "payment_required"
    assert x402.PAYMENT_REQUIRED_HEADER in response.headers


@pytest.mark.parametrize("explain,expected", [(None, 1), ("none", 1),
                                                ("summary", 1), ("full", 2)])
def test_entry_decide_weight_follows_explanation_level(entry, explain, expected):
    env = type("E", (), {})()
    env.TIER_POLICY = (REPO_ROOT / "api" / "worker" / "tiers.json").read_text()
    worker = entry.Default()
    worker.env = env
    payload = {} if explain is None else {"explain": explain}
    assert worker._credit_params("/v1/decide", payload)[0] == expected


def test_entry_with_all_flags_off_preserves_the_producer_bytes(entry):
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.ACCESS_ENFORCED = "false"
    env.BILLING_ENABLED = "false"
    env.X402_ENABLED = "false"
    worker = entry.Default()
    worker.env = env
    expected = {
        "schema_version": "1.0",
        "service_commit": "c0ffee",
        "result": [{"model_id": "example/unchanged"}],
    }

    async def rank(payload, service_commit, origin):
        return 200, expected

    worker._rank = rank
    response = asyncio.run(worker.fetch(_Req(
        "/v1/rank", {"use_case": "coding"},
        headers={"Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.8"},
    )))
    assert response.status == 200
    assert response.body == json.dumps(expected, indent=2, default=str)


def test_entry_credits_query(entry):
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.X402_ENABLED = "false"
    ledger = credits.MemoryLedger()
    key = "live_abc"
    asyncio.run(ledger.credit(x402.holder_from_key(key), "p", 7, "0x"))
    env.CREDITS = ledger
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req(
        "/v1/credits", method="GET", headers={"authorization": f"Bearer {key}"}, body="")))
    assert response.status == 200
    assert response.json()["available"] == 7
    # MODEL-316: the balance reuses rank's envelope but not its deprecation notice.
    assert response.json()["endpoint"] == "credits"
    assert "deprecation" not in response.json()


def test_entry_billing_paths_are_not_x402_paid_resources(entry):
    """Stripe's /v1/billing/* endpoints are not prepaid resources.

    Even with X402_ENABLED on, checkout, webhook, claim and rotate must be
    answered by the billing handlers, never wrapped into a 402.
    """
    assert all(not path.startswith("/v1/billing") for path in entry.POST_ENDPOINTS)
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.ACCESS_ENFORCED = "false"
    env.BILLING_ENABLED = "false"
    env.TIER_POLICY = (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(
        encoding="utf-8")
    env.X402_ENABLED = "true"
    env.X402_PAY_TO = PAY_TO
    env.X402_NETWORK = x402.NETWORK_BASE_SEPOLIA
    env.X402_ASSET = x402.USDC_BASE_SEPOLIA
    env.CREDITS = credits.MemoryLedger()
    env.X402_FACILITATOR = StubFacilitator()
    worker = entry.Default()
    worker.env = env
    for path in (
        "/v1/billing/checkout",
        "/v1/billing/stripe-webhook",
        "/v1/billing/claim",
        "/v1/billing/rotate",
    ):
        response = asyncio.run(worker.fetch(_Req(path, body="{}")))
        body = response.json()
        code = (body.get("error") or {}).get("code")
        assert response.status != 402, path
        assert code != "payment_required", path
        assert code != "not_found", path
        assert x402.PAYMENT_REQUIRED_HEADER not in (response.headers or {})
        assert code in {
            "billing_not_enabled", "billing_not_configured",
            "invalid_webhook_signature", "invalid_request",
            "access_store_not_configured",
        }, (path, response.status, code)
