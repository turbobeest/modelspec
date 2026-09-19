"""MODEL-93: credit weights, drawdown, exhausted free answer, concurrency."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access_config  # noqa: E402
import credits  # noqa: E402
import x402  # noqa: E402
from x402_facilitator import StubFacilitator  # noqa: E402

ENVELOPE = {"schema_version": "1.0", "service_commit": "test"}
RESOURCE = "https://api.modelspec.dev/v1/rank"
PAY_TO = "0x209693bc6afc0c5328ba36faf03c514ef312287c"


def _run(coro):
    return asyncio.run(coro)


def _cfg(**kwargs: Any) -> x402.Config:
    base = dict(
        enabled=True, mainnet=False, network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA), pay_to=PAY_TO,
        price_atomic=1000, facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
    )
    base.update(kwargs)
    return x402.Config(**base)  # type: ignore[arg-type]


async def _ok() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "result": [{"model_id": "example/ok"}]}


async def _boom() -> tuple[int, dict[str, Any]]:
    return 500, {**ENVELOPE, "error": {"code": "export_unavailable", "message": "x"},
                 "result": []}


async def _free() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "determinations": {"entitlement": "public_export"},
                 "result": [{"model_id": "example/ok"}]}


def test_shipped_weights_are_one_and_five():
    policy = access_config.load_policy()
    assert policy.credits.weight("rank") == 1
    assert policy.credits.weight("policy-check") == 5


def test_changing_a_weight_needs_no_code_change():
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["credits"]["weights"]["rank"] = 9
    mapped = access_config.policy_from_json(json.dumps(table))
    assert mapped.credits.weight("rank") == 9
    assert access_config.load_policy().credits.weight("rank") == 1


def test_failure_costs_nothing_at_weight_five():
    ledger = credits.MemoryLedger()
    holder = "key:" + "11" * 32
    _run(ledger.set_monthly(holder, 20, "in_1", "Solo"))
    status, _ = _run(x402.charge(
        config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_boom, produce_unfunded=_free, units=5))
    assert status == 500
    assert _run(ledger.balance(holder)).available == 20
    assert _run(ledger.balance(holder)).reserved == 0


def test_rank_draws_one_policy_check_draws_five():
    ledger = credits.MemoryLedger()
    holder = "key:" + "22" * 32
    _run(ledger.set_monthly(holder, 10, "in_2", "Solo"))
    status, _ = _run(x402.charge(
        config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, units=1))
    assert status == 200
    assert _run(ledger.balance(holder)).available == 9
    status, _ = _run(x402.charge(
        config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, units=5))
    assert status == 200
    assert _run(ledger.balance(holder)).available == 4


def test_zero_balance_is_the_free_answer_plus_exhausted_not_an_error():
    ledger = credits.MemoryLedger()
    holder = "key:" + "33" * 32
    status, body = _run(x402.charge(
        config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, produce_unfunded=_free, units=1,
        buy_url="https://modelspec.dev/pricing"))
    assert status == 200
    assert body["credits"]["exhausted"] is True
    assert body["credits"]["available"] == 0
    assert body["credits"]["needed"] == 1
    assert body["credits"]["unit"] == "credit"
    assert "token" not in json.dumps(body).lower()
    assert body["credits"]["buy"] == "https://modelspec.dev/pricing"
    assert body["determinations"]["entitlement"] == "public_export"
    assert _run(ledger.balance(holder)).available == 0


def test_short_balance_does_not_cover_policy_check_weight():
    ledger = credits.MemoryLedger()
    holder = "key:" + "44" * 32
    _run(ledger.set_monthly(holder, 3, "in_3", "Solo"))
    status, body = _run(x402.charge(
        config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
        get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok, produce_unfunded=_free, units=5))
    assert status == 200
    assert body["credits"]["exhausted"] is True
    assert body["credits"]["needed"] == 5
    assert _run(ledger.balance(holder)).available == 3


def test_concurrency_cannot_overspend():
    ledger = credits.MemoryLedger()
    holder = "key:" + "55" * 32
    _run(ledger.set_monthly(holder, 1, "in_4", "Solo"))

    async def once():
        return await x402.charge(
            config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
            get_header=lambda n: None, holder=holder, resource_url=RESOURCE,
            envelope=ENVELOPE, produce=_ok, produce_unfunded=_free, units=1)

    async def both():
        return await asyncio.gather(once(), once())

    results = _run(both())
    statuses = [status for status, _ in results]
    assert statuses == [200, 200]
    exhausted = sum(1 for _, body in results if body.get("credits", {}).get("exhausted"))
    funded = sum(1 for _, body in results if not body.get("credits", {}).get("exhausted"))
    assert exhausted == 1 and funded == 1
    bal = _run(ledger.balance(holder))
    assert bal.available == 0
    assert bal.reserved == 0
    assert bal.monthly == 0


def test_ledger_serialization_refuses_the_second_reserve():
    ledger = credits.MemoryLedger()
    holder = "key:" + "66" * 32
    _run(ledger.credit(holder, "seed", 1, "0x1"))

    async def both():
        return await asyncio.gather(ledger.reserve(holder, 1), ledger.reserve(holder, 1))

    first, second = _run(both())
    assert sorted([first.ok, second.ok]) == [False, True]
    assert _run(ledger.balance(holder)).available + _run(ledger.balance(holder)).reserved == 1
