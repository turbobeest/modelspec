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
        self._gate = asyncio.Lock()

    async def blockConcurrencyWhile(self, callback):
        async with self._gate:
            return await callback()


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


def test_rotation_transfer_progress_survives_restart():
    async def scenario():
        ctx = Ctx(lambda v: {"v": v})
        first = _ledger(credits_do.CreditsObject(ctx, env=None))
        await first.set_monthly("key:first", 100, "in_rotation", "Solo")
        await first.save_rotation("key:first", {
            "nonce": "fixture-nonce", "stage": "prepared"})
        assert await first.transfer("key:first", "key:second")

        restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
        assert await restarted.rotation_state("key:first") == {
            "nonce": "fixture-nonce", "stage": "transferred"}
        assert await restarted.rotation_state("key:second") is None
        assert (await restarted.balance("key:first")).available == 0
        assert (await restarted.balance("key:second")).available == 100
        assert not await restarted.transfer("key:first", "key:second")
        assert (await restarted.balance("key:second")).available == 100

    asyncio.run(scenario())


def test_independent_clients_rotate_one_key():
    import access_config
    import access_keys
    import billing
    from access_kv import MemoryKV
    from datetime import UTC, datetime

    class YieldingKV(MemoryKV):
        async def get(self, name):
            value = await super().get(name)
            await asyncio.sleep(0)
            return value

        async def put(self, name, value, **kwargs):
            await super().put(name, value, **kwargs)
            await asyncio.sleep(0)

    async def scenario():
        kv = YieldingKV()
        policy = access_config.load_policy()
        now = datetime(2026, 9, 17, tzinfo=UTC)
        key, _ = await access_keys.issue(
            kv, tier="paid", owner="fixture", now=now, policy=policy)
        holder = credits.holder_from_fingerprint(access_keys.fingerprint(key))
        ctx = Ctx(lambda v: {"v": v})
        obj = credits_do.CreditsObject(ctx, SimpleNamespace(ACCESS=kv))
        clients = [_ledger(obj), _ledger(obj)]
        await clients[0].set_monthly(holder, 100, "in_clients", "Solo")

        results = await asyncio.gather(*(
            billing.rotate(api_key=key, kv=kv, policy=policy, now=now,
                           service_commit="test", ledger=client)
            for client in clients))
        assert sorted(result.status for result in results) == [200, 403]
        successes = [result for result in results if result.status == 200]
        assert len(successes) == 1
        new_key = successes[0].body["key"]
        new_holder = credits.holder_from_fingerprint(access_keys.fingerprint(new_key))
        assert (await clients[0].balance(new_holder)).available == 100
        persisted = json.dumps(ctx.storage.sql.table)
        assert key not in persisted and new_key not in persisted

        restarted = _ledger(credits_do.CreditsObject(ctx, SimpleNamespace(ACCESS=kv)))
        replay = await billing.rotate(
            api_key=key, kv=kv, policy=policy, now=now,
            service_commit="test", ledger=restarted)
        assert replay.status == 403

    asyncio.run(scenario())


@pytest.mark.parametrize("after_write", [False, True])
def test_rotation_resumes_after_object_restart(after_write):
    import access_config
    import access_keys
    import billing
    from access_kv import MemoryKV
    from datetime import UTC, datetime

    class InterruptedKV(MemoryKV):
        failed_name = ""

        async def put(self, name, value, **kwargs):
            interrupted = name == self.failed_name
            if interrupted and not after_write:
                raise OSError("fixture write unavailable")
            await super().put(name, value, **kwargs)
            if interrupted:
                raise OSError("fixture write unavailable")

    async def scenario():
        kv = InterruptedKV()
        policy = access_config.load_policy()
        now = datetime(2026, 9, 17, tzinfo=UTC)
        key, _ = await access_keys.issue(
            kv, tier="paid", owner="fixture", now=now, policy=policy)
        holder = credits.holder_from_fingerprint(access_keys.fingerprint(key))
        ctx = Ctx(lambda v: {"v": v})
        env = SimpleNamespace(ACCESS=kv)
        ledger = _ledger(credits_do.CreditsObject(ctx, env))
        await ledger.set_monthly(holder, 100, "in_restart", "Solo")
        kv.failed_name = access_keys.storage_name(key)

        with pytest.raises(OSError, match="fixture write"):
            await billing.rotate(
                api_key=key, kv=kv, policy=policy, now=now,
                service_commit="test", ledger=ledger)

        kv.failed_name = ""
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        result = await billing.rotate(
            api_key=key, kv=kv, policy=policy, now=now,
            service_commit="test", ledger=restarted)
        assert result.status == 200
        new_holder = credits.holder_from_fingerprint(
            access_keys.fingerprint(result.body["key"]))
        assert (await restarted.balance(holder)).available == 0
        assert (await restarted.balance(new_holder)).available == 100
        assert not (await access_keys.lookup(kv, key)).active
        assert await restarted.rotation_state(holder) == {"stage": "complete"}

    asyncio.run(scenario())
