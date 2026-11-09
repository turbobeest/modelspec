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
