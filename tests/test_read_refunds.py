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


@pytest.mark.parametrize('reset', ['renew', 'cancel'])
@pytest.mark.parametrize('kind', ['decision', 'catalog'])
def test_old_failed_request_does_not_restore_obsolete_monthly_credits(ledger, reset, kind):
    async def scenario():
        who = 'key:monthly-race'
        assert (await ledger.set_monthly(who, 10, 'in_old', 'Solo')).credited
        if kind == 'decision':
            taken = await ledger.reserve(who, 5)
            assert taken.ok and taken.reservation_id is not None
        else:
            taken = await ledger.take_read(who, 10, 100, 10)
            assert taken.ok and taken.token is not None
        if reset == 'renew':
            assert (await ledger.set_monthly(who, 10, 'in_new', 'Solo')).credited
            expected = 10
        else:
            assert (await ledger.clear_monthly(who)).credited
            expected = 0
        if kind == 'decision':
            assert await ledger.release(who, taken.reservation_id)
        else:
            assert await ledger.release_read(who, taken.token)
        actual = await ledger.balance(who)
        assert actual.monthly == expected, actual.to_json()
    asyncio.run(scenario())

def test_old_failed_catalog_read_does_not_erase_new_period_overage(ledger):
    async def scenario():
        who = 'key:overage-race'
        assert (await ledger.set_monthly(who, 0, 'in_old', 'Scale', 'cus_test')).credited
        old = await ledger.take_read(who, 1, 100, 10, overage_cap=10)
        assert old.ok and old.token is not None
        assert (await ledger.set_monthly(who, 0, 'in_new', 'Scale', 'cus_test')).credited
        new = await ledger.reserve(who, 1, overage_cap=10)
        assert new.ok and new.reservation_id is not None
        assert (await ledger.commit(who, new.reservation_id)).ok
        assert await ledger.release_read(who, old.token)
        actual = await ledger.balance(who)
        assert actual.overage_used == 1, actual.to_json()
    asyncio.run(scenario())


@pytest.mark.parametrize("finish", ["commit", "release"])
def test_overage_completion_preserves_current_period_cap(ledger, finish):
    async def scenario():
        await ledger.set_monthly(HOLDER, 0, "in_previous", "Scale", "cus_read")
        old = await ledger.reserve(HOLDER, 2, overage_cap=2)
        assert old.ok and old.reservation_id is not None
        await ledger.set_monthly(HOLDER, 0, "in_current", "Scale", "cus_read")
        current = await ledger.reserve(HOLDER, 2, overage_cap=2)
        assert current.ok and current.reservation_id is not None
        assert await ledger.commit(HOLDER, current.reservation_id)
        assert await getattr(ledger, finish)(HOLDER, old.reservation_id)
        assert not await getattr(ledger, finish)(HOLDER, old.reservation_id)
        assert (await ledger.balance(HOLDER)).overage_used == 2
        assert not (await ledger.reserve(HOLDER, 1, overage_cap=2)).ok
        events = await ledger.open_meter_events(HOLDER)
        assert len(events) == (2 if finish == "commit" else 1)
        assert sum(row[1] for row in events) == (4 if finish == "commit" else 2)
        assert len({row[0] for row in events}) == len(events)
    asyncio.run(scenario())


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("funding", ["monthly", "overage"])
def test_read_block_refund_keeps_the_draws_allowance_period(ledger, reverse, funding):
    async def scenario():
        await ledger.set_monthly(HOLDER, 2 if funding == "monthly" else 0,
                                 "in_block_previous", "Scale", "cus_read")
        first = await _take(ledger)
        await ledger.set_monthly(HOLDER, 2, "in_block_current", "Solo")
        second = await _take(ledger)
        for taken in ([second, first] if reverse else [first, second]):
            assert await ledger.release_read(HOLDER, taken.token)
        actual = await ledger.balance(HOLDER)
        assert actual.monthly == 2
        assert actual.overage_used == 0
    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["decision", "catalog"])
def test_period_change_preserves_pack_returns(ledger, kind):
    async def scenario():
        await ledger.set_monthly(HOLDER, 0, "in_pack_previous", "Solo")
        await ledger.credit(HOLDER, "pack_period", 5, "pi_period")
        taken = (await ledger.reserve(HOLDER, 2) if kind == "decision" else await _take(ledger))
        assert taken.ok
        await ledger.set_monthly(HOLDER, 3, "in_pack_current", "Solo")
        if kind == "decision":
            assert taken.reservation_id is not None
            assert await ledger.release(HOLDER, taken.reservation_id)
        else:
            assert await ledger.release_read(HOLDER, taken.token)
        actual = await ledger.balance(HOLDER)
        assert actual.monthly == 3
        assert actual.packs == 5
    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["decision", "catalog"])
def test_merged_allowances_keep_current_and_obsolete_draws_separate(ledger, kind):
    async def take(who):
        result = (await ledger.reserve(who, 1) if kind == "decision"
                  else await ledger.take_read(who, 1, 100, 100))
        assert result.ok
        token = result.reservation_id if kind == "decision" else result.token
        assert token is not None
        return token

    async def scenario():
        src, dst = "key:period-source", "key:period-destination"
        await ledger.set_monthly(src, 3, "in_source_old", "Solo")
        old = await take(src)
        await ledger.set_monthly(src, 3, "in_source_new", "Solo")
        current = await take(src)
        await ledger.set_monthly(dst, 4, "in_destination", "Solo")
        target = await take(dst)
        assert await ledger.transfer(src, dst)
        release = ledger.release if kind == "decision" else ledger.release_read
        for who, token in [(src, old), (src, current), (dst, target)]:
            assert await release(who, token)
        assert (await ledger.balance(dst)).monthly == 7
    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["decision", "catalog"])
@pytest.mark.parametrize("renew", [False, True])
def test_legacy_draws_load_with_their_original_allowance(kind, renew):
    state = credits.LedgerState()
    state.set_monthly(HOLDER, 5, "in_legacy", "Solo")
    taken = (state.reserve(HOLDER, 2) if kind == "decision"
             else state.take_read(HOLDER, 10, 100, 100))
    assert taken.ok
    raw = state.to_json()
    account = raw["accounts"][HOLDER]
    account.pop("allowance_generation")
    for collection in ("reservations", "taken_reads"):
        for record in account[collection].values():
            record.pop("allowance_generation")
    restored = credits.LedgerState.from_json(raw)
    if renew:
        restored.set_monthly(HOLDER, 5, "in_legacy_new", "Solo")
    if kind == "decision":
        assert restored.release(HOLDER, taken.reservation_id)
    else:
        assert restored.release_read(HOLDER, taken.token)
    assert restored.balance(HOLDER).monthly == 5
