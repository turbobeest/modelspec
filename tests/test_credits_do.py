"""CreditsObject against the row shapes the Workers Python runtime returns.

Under Pyodide, `ctx.storage.sql.exec(...).one()` hands back a JsProxy of a
JavaScript object, not a Python dict or tuple: `row[0]` raises TypeError. The
first read after any write took the whole Worker down with a 1101 (found in
the MODEL-93 end-to-end test, 2026-09-19).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))

import credits  # noqa: E402
import credits_do  # noqa: E402
import x402  # noqa: E402
from tests.test_credits import _cfg, _ok, _boom, ENVELOPE, RESOURCE  # noqa: E402
from x402_facilitator import StubFacilitator  # noqa: E402


class JsObjectProxy:
    """What Pyodide returns for `{v: "..."}`: attribute access and to_py(),
    no integer indexing."""

    def __init__(self, fields: dict[str, str]):
        self._fields = fields

    def __getattr__(self, name: str):
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(name) from None

    def to_py(self) -> dict[str, str]:
        return dict(self._fields)


class Cursor:
    def __init__(self, row):
        self._row = row

    def one(self):
        if self._row is None:
            raise RuntimeError("Expected exactly one result from SQL query, but got no results.")
        return self._row


class Sql:
    def __init__(self, row_type):
        self.table: dict[str, str] = {}
        self.row_type = row_type

    def exec(self, query: str, *params):
        if query.startswith("INSERT"):
            self.table[params[0]] = params[1]
            return Cursor(None)
        if query.startswith("SELECT"):
            v = self.table.get(params[0])
            return Cursor(None if v is None else self.row_type(v))
        return Cursor(None)


class Ctx:
    def __init__(self, row_type):
        self.storage = type("Storage", (), {"sql": Sql(row_type)})()


def _round_trip(row_type) -> dict:
    obj = credits_do.CreditsObject(Ctx(row_type), env=None)
    asyncio.run(obj.set_monthly("key:abc", 4000, "in_1", "Solo"))
    return asyncio.run(obj.balance("key:abc", ""))


def test_ledger_reads_back_a_js_object_row():
    bal = _round_trip(lambda v: JsObjectProxy({"v": v}))
    assert bal["monthly"] == 4000


def test_ledger_reads_back_dict_and_tuple_rows():
    assert _round_trip(lambda v: {"v": v})["monthly"] == 4000
    assert _round_trip(lambda v: (v,))["monthly"] == 4000


def _ledger(obj):
    def id_from_name(name):
        assert name == "ledger"
        return name

    return credits.DurableLedger(SimpleNamespace(idFromName=id_from_name, get=lambda _id: obj))


def test_a_one_shot_payment_is_credited_and_spent_in_one_step():
    obj = credits_do.CreditsObject(Ctx(lambda v: {"v": v}), env=None)
    ledger = _ledger(obj)

    result = asyncio.run(ledger.spend_paid("payer:0xabc", "x402:n1", 1, "0xtx"))

    assert result.credited is True
    state = credits.LedgerState.from_json(json.loads(obj._get("state")))
    assert len(state.accounts) == 1
    assert state.balance("payer:0xabc").available == 0
    assert state.seen("x402:n1") is True


def test_a_live_ledger_rpc_error_reaches_the_caller():
    async def credit(*_args):
        raise RuntimeError("bad payment id ledger-sealed: live")

    ledger = _ledger(SimpleNamespace(credit=credit))
    with pytest.raises(RuntimeError, match="bad payment id"):
        asyncio.run(ledger.credit("key:a", "x402:ledger-sealed: live", 1, "tx"))


def test_existing_state_survives_with_unused_move_and_lease_rows():
    ctx = Ctx(lambda v: {"v": v})
    state = credits.LedgerState()
    state.credit("key:a", "pack:old", 10, "tx-old", source="pack")
    unused = {"move": '{"role":"live","imported":"old-digest"}',
              "leases": '{"old-lease":9999999999}'}
    ctx.storage.sql.table.update({"state": json.dumps(state.to_json()), **unused})
    original_exec = ctx.storage.sql.exec

    def state_only(query, *params):
        if query.startswith(("SELECT", "INSERT")):
            assert params[0] == "state"
        return original_exec(query, *params)

    ctx.storage.sql.exec = state_only
    ledger = _ledger(credits_do.CreditsObject(ctx, env=None))
    assert asyncio.run(ledger.balance("key:a")).available == 10
    assert not asyncio.run(ledger.credit("key:a", "pack:old", 10, "tx-old", source="pack")).credited
    held = asyncio.run(ledger.reserve("key:a", 3))
    assert held.ok
    assert asyncio.run(ledger.commit("key:a", held.reservation_id)).ok

    restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
    assert asyncio.run(restarted.balance("key:a")).available == 7
    assert {key: ctx.storage.sql.table[key] for key in unused} == unused
    assert set(ctx.storage.sql.table) == {"state", "move", "leases"}


def durable():
    return _ledger(credits_do.CreditsObject(Ctx(lambda v: JsObjectProxy({"v": v})), None))


@pytest.mark.parametrize('status', [200, 500])
def test_key_rotation_during_response_finishes_reservation(status):
    async def scenario():
        ledger = durable()
        src, dst = 'key:old', 'key:new'
        assert (await ledger.set_monthly(src, 10, 'in_rotation', 'Solo')).credited
        async def produce():
            assert await ledger.transfer(src, dst)
            return await (_ok() if status == 200 else _boom())
        result = await x402.charge(
            config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
            get_header=lambda _: None, holder=src, resource_url=RESOURCE,
            envelope=ENVELOPE, produce=produce, units=5,
        )
        assert result[0] == status
        actual = await ledger.balance(dst)
        assert actual.reserved == 0, actual.to_json()
        assert actual.available == (5 if status == 200 else 10)
        assert (await ledger.balance(src)).available == 0
    asyncio.run(scenario())

def test_rotated_failed_catalog_read_returns_its_credit():
    async def scenario():
        ledger, src, dst = durable(), 'key:old-read', 'key:new-read'
        assert (await ledger.set_monthly(src, 10, 'in_read_rotation', 'Solo')).credited
        taken = await ledger.take_read(src, 10, 100, 10)
        assert taken.ok and taken.token is not None
        assert await ledger.transfer(src, dst)
        released = await ledger.release_read(src, taken.token)
        actual = await ledger.balance(dst)
        assert actual.available == 10, (released, actual.to_json())
    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["decision", "catalog"])
@pytest.mark.parametrize("success", [True, False])
def test_transferred_tokens_complete_once_across_merges(kind, success):
    async def scenario():
        ledger = durable()
        holders = ["key:first", "key:second", "key:third"]
        pending = []
        for i, who in enumerate(holders):
            await ledger.set_monthly(who, 10, f"in_merge_{i}", "Solo")
            taken = (await ledger.reserve(who, 2) if kind == "decision"
                     else await ledger.take_read(who, 10, 100, 100))
            assert taken.ok
            token = taken.reservation_id if kind == "decision" else taken.token
            assert token is not None
            pending.append((who, token))
        assert await ledger.transfer(holders[0], holders[1])
        assert await ledger.transfer(holders[1], holders[2])
        for who in holders[:2]:
            assert (await ledger.balance(who)).available == 0
            assert not (await ledger.reserve(who, 1, overage_cap=100)).ok
            assert not (await ledger.take_read(who, 10, 100, 100, overage_cap=100)).ok
        complete = ((ledger.commit if success else ledger.release) if kind == "decision"
                    else (ledger.keep_read if success else ledger.release_read))
        for who, token in pending:
            assert await complete(who, token)
            assert not await complete(who, token)
        actual = await ledger.balance(holders[-1])
        assert actual.reserved == 0
        expected = (24 if kind == "decision" else 27) if success else 30
        assert actual.available == expected
    asyncio.run(scenario())


@pytest.mark.parametrize("enabled", [False, True])
def test_charge_requires_a_confirmed_commit(enabled):
    class UnconfirmedLedger(credits.MemoryLedger):
        async def commit(self, holder, reservation_id):
            return credits.CommitResult(False)

    async def scenario():
        ledger = UnconfirmedLedger()
        await ledger.set_monthly("key:confirmation", 5, "in_confirmation", "Solo")
        with pytest.raises(RuntimeError, match="credit reservation"):
            await x402.charge(
                config=_cfg(enabled=enabled), ledger=ledger, facilitator=StubFacilitator(),
                get_header=lambda _: None, holder="key:confirmation", resource_url=RESOURCE,
                envelope=ENVELOPE, produce=_ok)
        assert (await ledger.balance("key:confirmation")).available == 5
    asyncio.run(scenario())


def test_merged_pending_overage_uses_distinct_meter_identities():
    async def scenario():
        ledger = durable()
        pending = []
        for who in ['key:meter-src', 'key:meter-dst']:
            await ledger.set_monthly(who, 0, 'in_' + who, 'Scale', 'cus_test')
            reservation = await ledger.reserve(who, 1, overage_cap=10)
            assert reservation.ok and reservation.reservation_id is not None
            pending.append((who, reservation.reservation_id))
        assert await ledger.transfer('key:meter-src', 'key:meter-dst')
        for who, token in pending:
            assert await ledger.commit(who, token)
        events = await ledger.open_meter_events('key:meter-dst')
        assert len(events) == 2
        assert len({row[0] for row in events}) == 2
    asyncio.run(scenario())


@pytest.mark.parametrize("funding", ["pack", "monthly"])
def test_pending_completion_retains_routing_during_delayed_funding(funding):
    async def scenario():
        ledger = durable()
        src, dst = "key:pending-source", "key:pending-destination"
        await ledger.set_monthly(src, 0, "in_pending", "Scale", "cus_pending")
        taken = await ledger.reserve(src, 5, overage_cap=10)
        assert taken.ok and taken.reservation_id is not None
        identifier = await ledger.meter_identifier(src, "res", taken.reservation_id)
        assert await ledger.transfer(src, dst)
        if funding == "pack":
            await ledger.credit(src, "pack_delayed", 10, "pi_delayed")
        else:
            await ledger.set_monthly(src, 10, "in_delayed", "Solo")
        assert not (await ledger.reserve(src, 1)).ok
        assert not (await ledger.take_read(src, 10, 100, 10)).ok
        assert await ledger.commit(src, taken.reservation_id)
        assert not await ledger.commit(src, taken.reservation_id)
        events = await ledger.open_meter_events(dst)
        assert len(events) == 1 and events[0][:2] == (identifier, 5)
        actual = await ledger.balance(dst)
        if funding == "pack":
            assert actual.packs == 10
            assert actual.overage_used == 5
        else:
            assert actual.monthly == 10
            assert actual.overage_used == 0
    asyncio.run(scenario())


def _funding_ledger(kind):
    if kind == "memory":
        return credits.MemoryLedger(), None
    obj = credits_do.CreditsObject(Ctx(lambda v: JsObjectProxy({"v": v})), None)
    return _ledger(obj), obj


def _funding_accounts(ledger, obj):
    if obj is None:
        return ledger.state.accounts
    return credits.LedgerState.from_json(json.loads(obj._get("state"))).accounts


@pytest.mark.parametrize("kind", ["memory", "durable"])
@pytest.mark.parametrize("funding", ["pack", "monthly", "clear"])
def test_funding_after_transfer_reaches_the_live_account(kind, funding):
    async def scenario():
        ledger, obj = _funding_ledger(kind)
        src, dst = "key:fund-src", "key:fund-dst"
        if funding == "pack":
            assert (await ledger.set_monthly(src, 0, "in_old", "Scale", "cus_fund")).credited
            opened = await ledger.reserve(src, 5, overage_cap=10)
            assert opened.ok and opened.reservation_id is not None
            assert await ledger.transfer(src, dst)
            assert (await ledger.credit(src, "pack_delayed", 7, "pi_delayed")).credited
            live = await ledger.balance(dst)
            assert live.packs == 7
            assert live.monthly == 0
            assert (await ledger.credit(src, "pack_delayed", 7, "pi_delayed")).reason == "replay"
            assert (await ledger.credit(dst, "pack_delayed", 7, "pi_delayed")).reason == "replay"
            assert (await ledger.commit(src, opened.reservation_id)).ok
            live = await ledger.balance(dst)
            assert live.packs == 7
            assert live.overage_used == 5
            drawn = await ledger.reserve(dst, 7)
            assert drawn.ok
            assert (await ledger.balance(dst)).available == 0
        elif funding == "monthly":
            assert (await ledger.set_monthly(src, 0, "in_old", "Scale", "cus_fund")).credited
            opened = await ledger.reserve(src, 5, overage_cap=10)
            assert opened.ok and opened.reservation_id is not None
            identifier = await ledger.meter_identifier(src, "res", opened.reservation_id)
            assert await ledger.transfer(src, dst)
            assert (await ledger.set_monthly(src, 10, "in_delayed", "Solo")).credited
            assert (await ledger.balance(dst)).monthly == 10
            assert (await ledger.balance(dst)).overage_used == 0
            spent = await ledger.reserve(dst, 10)
            assert spent.ok
            extra = await ledger.reserve(dst, 1, overage_cap=10)
            assert extra.ok and extra.reservation_id is not None
            assert (await ledger.set_monthly(src, 10, "in_delayed", "Solo")).reason == "replay"
            assert (await ledger.set_monthly(dst, 10, "in_delayed", "Solo")).reason == "replay"
            assert (await ledger.commit(dst, extra.reservation_id)).ok
            assert (await ledger.commit(src, opened.reservation_id)).ok
            events = await ledger.open_meter_events(dst)
            assert (identifier, 5) in [row[:2] for row in events]
            live = await ledger.balance(dst)
            assert live.monthly == 0
            assert live.overage_used == 1
        else:
            assert (await ledger.set_monthly(src, 8, "in_old", "Solo")).credited
            held = await ledger.reserve(src, 5)
            assert held.ok and held.reservation_id is not None
            assert await ledger.transfer(src, dst)
            cleared = await ledger.clear_monthly(src)
            assert cleared.credited and cleared.reason == "cleared"
            assert (await ledger.balance(dst)).monthly == 0
            assert await ledger.release(src, held.reservation_id)
            live = await ledger.balance(dst)
            assert live.monthly == 0
            assert live.available == 0
            assert live.reserved == 0
        accounts = _funding_accounts(ledger, obj)
        assert src not in accounts
        assert dst in accounts
        assert (await ledger.balance(src)).available == 0
        assert not (await ledger.reserve(src, 1)).ok
        assert not (await ledger.take_read(src, 10, 100, 10)).ok
    asyncio.run(scenario())


def test_stored_alias_accepts_later_funding_on_the_live_account():
    state = credits.LedgerState()
    assert state.set_monthly("key:src", 8, "in_old", "Solo").credited
    assert state.transfer("key:src", "key:dst")
    restored = credits.LedgerState.from_json(json.loads(json.dumps(state.to_json())))
    assert restored.set_monthly("key:src", 4, "in_later", "Solo").credited
    assert restored.balance("key:dst").monthly == 4
    assert "key:src" not in restored.accounts
    assert restored.set_monthly("key:src", 4, "in_later", "Solo").reason == "replay"
    assert restored.set_monthly("key:dst", 4, "in_later", "Solo").reason == "replay"
    assert restored.balance("key:dst").monthly == 4
    assert restored.set_monthly("key:src", 8, "in_old", "Solo").reason == "replay"
