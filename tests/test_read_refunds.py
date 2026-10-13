"""MODEL-371: a read block is refundable only when every read in it fails."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKER_SRC = Path(__file__).resolve().parents[1] / "api" / "worker" / "src"
sys.path.insert(0, str(WORKER_SRC))

import credits  # noqa: E402
import credits_do  # noqa: E402
from tests.test_credits_do import Ctx, JsObjectProxy  # noqa: E402

HOLDER = "key:read-refund"
CLOCK = "2026-10-10T12:00:00Z"


@pytest.fixture(params=("memory", "durable"))
def ledger(request):
    if request.param == "memory":
        return credits.MemoryLedger()
    obj = credits_do.CreditsObject(Ctx(lambda v: JsObjectProxy({"v": v})), env=None)
    return credits.DurableLedger(SimpleNamespace(
        idFromName=lambda name: name, get=lambda ident: obj))


async def _fund(ledger, funding):
    if funding == "pack":
        assert (await ledger.credit(HOLDER, "pack_read", 2, "pi_read", source="pack")).credited
    else:
        assert (await ledger.set_monthly(
            HOLDER, 0 if funding == "overage" else 2, "in_read", "Scale",
            "cus_read")).credited


async def _take(ledger, *, per=10):
    taken = await ledger.take_read(HOLDER, per, 1000, 100, now=CLOCK, overage_cap=2)
    assert taken.ok and taken.token is not None
    return taken


def _charged(balance, funding, *, unreported=0):
    assert balance.available == (0 if funding == "overage" else 1)
    assert balance.overage_used == (1 if funding == "overage" else 0)
    assert balance.overage_unreported == unreported


@pytest.mark.parametrize("funding", ("monthly", "pack", "overage"))
def test_read_refund_waits_for_pending_read_in_same_block(ledger, funding):
    async def scenario():
        await _fund(ledger, funding)
        first, second = await asyncio.gather(_take(ledger), _take(ledger))
        assert await ledger.release_read(HOLDER, first.token)
        _charged(await ledger.balance(HOLDER, now=CLOCK), funding)
        assert await ledger.keep_read(HOLDER, second.token)
        _charged(await ledger.balance(HOLDER, now=CLOCK), funding,
                 unreported=1 if funding == "overage" else 0)

    asyncio.run(scenario())


@pytest.mark.parametrize("prefill", (2, 10))
def test_failed_read_leaves_remaining_reads_in_paid_block(ledger, prefill):
    async def scenario():
        await _fund(ledger, "monthly")
        first, *others = await asyncio.gather(*(_take(ledger) for _ in range(prefill)))
        for taken in others:
            assert await ledger.keep_read(HOLDER, taken.token)
        assert await ledger.release_read(HOLDER, first.token)
        for _ in range(11 - prefill):
            taken = await _take(ledger)
            assert await ledger.keep_read(HOLDER, taken.token)
        _charged(await ledger.balance(HOLDER, now=CLOCK), "monthly")
        next_block = await _take(ledger)
        assert next_block.read_count == 11
        assert next_block.available == 0

    asyncio.run(scenario())


@pytest.mark.parametrize("funding", ("monthly", "pack", "overage"))
def test_read_refund_keeps_charge_after_another_read_succeeds(ledger, funding):
    async def scenario():
        await _fund(ledger, funding)
        first, second = await asyncio.gather(_take(ledger), _take(ledger))
        assert await ledger.keep_read(HOLDER, second.token)
        assert await ledger.release_read(HOLDER, first.token)
        assert not await ledger.release_read(HOLDER, first.token)
        assert not await ledger.keep_read(HOLDER, first.token)
        assert not await ledger.release_read(HOLDER, second.token)
        _charged(await ledger.balance(HOLDER, now=CLOCK), funding,
                 unreported=1 if funding == "overage" else 0)

    asyncio.run(scenario())


@pytest.mark.parametrize("funding", ("monthly", "pack", "overage"))
@pytest.mark.parametrize("width", (2, 10))
@pytest.mark.parametrize("reverse", (False, True))
def test_read_block_refunds_once_only_after_every_read_fails(ledger, funding, width, reverse):
    async def scenario():
        await _fund(ledger, funding)
        taken = await asyncio.gather(*(_take(ledger) for _ in range(width)))
        order = list(reversed(taken)) if reverse else taken
        for read in order[:-1]:
            assert await ledger.release_read(HOLDER, read.token)
            _charged(await ledger.balance(HOLDER, now=CLOCK), funding)
        assert await ledger.release_read(HOLDER, order[-1].token)
        assert not await ledger.release_read(HOLDER, order[-1].token)
        balance = await ledger.balance(HOLDER, now=CLOCK)
        assert balance.available == (0 if funding == "overage" else 2)
        assert balance.overage_used == 0
        assert balance.overage_unreported == 0
        retry = await _take(ledger)
        assert retry.read_count == 1 and retry.read_burst == 1
        _charged(await ledger.balance(HOLDER, now=CLOCK), funding)

    asyncio.run(scenario())


def test_success_in_another_block_does_not_prevent_a_failed_block_refund(ledger):
    async def scenario():
        await _fund(ledger, "monthly")
        first, second, third, fourth = await asyncio.gather(
            *(_take(ledger, per=2) for _ in range(4)))
        assert await ledger.keep_read(HOLDER, fourth.token)
        assert await ledger.release_read(HOLDER, first.token)
        assert (await ledger.balance(HOLDER, now=CLOCK)).available == 0
        assert await ledger.release_read(HOLDER, second.token)
        assert await ledger.release_read(HOLDER, third.token)
        _charged(await ledger.balance(HOLDER, now=CLOCK), "monthly")
        retry = await _take(ledger, per=2)
        assert retry.read_count == 2 and retry.available == 1
        assert await ledger.keep_read(HOLDER, retry.token)
        next_block = await _take(ledger, per=2)
        assert next_block.read_count == 3 and next_block.available == 0

    asyncio.run(scenario())


def test_legacy_read_ticket_without_success_history_retains_charge():
    state = credits.LedgerState.from_json({"accounts": {HOLDER: {
        "monthly": 1, "read_day": CLOCK[:10], "read_count": 2,
        "read_minute": CLOCK[:16], "read_burst": 2, "reads_in_block": 2,
        "next_read": 3, "taken_reads": {"1": {
            "day": CLOCK[:10], "minute": CLOCK[:16], "monthly": 1,
            "block_before": 0, "block_after": 1,
        }},
    }}})
    ledger = credits.MemoryLedger(state)
    assert asyncio.run(ledger.release_read(HOLDER, 1))
    assert asyncio.run(ledger.balance(HOLDER, now=CLOCK)).available == 1
