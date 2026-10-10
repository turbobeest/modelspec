"""Durable Object wrapping `credits.LedgerState` (MODEL-75).

Bound as `CREDITS`. One instance, id `ledger`. SQLite holds a single JSON
document so a mutation is one write, not a cross-key KV race. The class is
imported from `entry.py` so Wrangler can find it by `class_name`.
"""

from __future__ import annotations

import json
from typing import Any

from credits import LedgerState

try:
    from workers import DurableObject
except Exception:  # CPython tests stub `workers` without this name
    class DurableObject:  # pragma: no cover
        def __init__(self, ctx=None, env=None):
            self.ctx = ctx
            self.env = env


_STATE_KEY = "state"


class CreditsObject(DurableObject):
    """Serial mailbox for every credit mutation on this Worker."""

    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        self.ctx = ctx
        self.env = env

    def _ensure(self) -> None:
        self.ctx.storage.sql.exec(
            "CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")

    def _load(self) -> LedgerState:
        self._ensure()
        cursor = self.ctx.storage.sql.exec(
            "SELECT v FROM kv WHERE k = ?", _STATE_KEY)
        row = _one_row(cursor)
        if row is None:
            return LedgerState()
        text = _cell(row, "v")
        if not text:
            return LedgerState()
        return LedgerState.from_json(json.loads(str(text)))

    def _save(self, state: LedgerState) -> None:
        self._ensure()
        self.ctx.storage.sql.exec(
            "INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)",
            _STATE_KEY, json.dumps(state.to_json()),
        )

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> dict[str, Any]:
        state = self._load()
        result = state.credit(holder, payment_id, int(units), tx,
                              expires_at=str(expires_at or ""),
                              source=str(source or "x402"))
        self._save(state)
        return result.to_json()

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          reset_overage: bool = True) -> dict[str, Any]:
        state = self._load()
        result = state.set_monthly(holder, int(units), str(invoice_id),
                                   str(plan or ""), str(customer_id or ""),
                                   bool(reset_overage))
        self._save(state)
        return result.to_json()

    async def clear_monthly(self, holder: str) -> dict[str, Any]:
        state = self._load()
        result = state.clear_monthly(holder)
        self._save(state)
        return result.to_json()

    async def transfer(self, src: str, dst: str) -> bool:
        state = self._load()
        ok = state.transfer(str(src), str(dst))
        self._save(state)
        return ok

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "", overage_cap: int = 0) -> dict[str, Any]:
        state = self._load()
        result = state.reserve(holder, int(units), now=str(now or ""),
                               overage_cap=int(overage_cap or 0))
        self._save(state)
        return result.to_json()

    async def commit(self, holder: str, reservation_id: int) -> dict[str, Any]:
        state = self._load()
        result = state.commit(holder, int(reservation_id))
        self._save(state)
        return result.to_json()

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> dict[str, Any]:
        state = self._load()
        result = state.take_read(
            holder, int(reads_per_credit), int(daily_cap), int(burst_limit),
            now=str(now or ""), overage_cap=int(overage_cap or 0))
        self._save(state)
        return result.to_json()

    async def release_read(self, holder: str, token: int) -> bool:
        state = self._load()
        ok = state.release_read(holder, int(token))
        self._save(state)
        return ok

    async def keep_read(self, holder: str, token: int) -> bool:
        state = self._load()
        ok = state.keep_read(holder, int(token))
        self._save(state)
        return ok

    async def meter_identifier(self, holder: str, kind: str, counter: str) -> str:
        state = self._load()
        ident = state.meter_identifier(str(holder), str(kind), counter)
        self._save(state)
        return ident

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool:
        state = self._load()
        ok = state.note_unreported(
            holder, int(units), str(identifier), str(customer_id or ""),
            str(event_name or ""))
        self._save(state)
        return ok

    async def open_backlog(self, holder: str) -> list:
        state = self._load()
        units, seq, ident = state.open_backlog(holder)
        self._save(state)
        return [units, seq, ident]

    async def ack_backlog(self, holder: str, units: int, n: int) -> bool:
        state = self._load()
        ok = state.ack_backlog(holder, int(units), int(n))
        self._save(state)
        return ok

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int = 0) -> bool:
        state = self._load()
        when = int(created_at) or None
        ok = state.note_uncertain(holder, int(units), str(identifier), when)
        self._save(state)
        return ok

    async def list_uncertain(self, holder: str) -> list:
        return [[ident, units, created_at]
                for ident, units, created_at in self._load().list_uncertain(holder)]

    async def ack_uncertain(self, holder: str, identifier: str) -> bool:
        state = self._load()
        ok = state.ack_uncertain(holder, str(identifier))
        self._save(state)
        return ok

    async def age_uncertain(self, holder: str, now: int = 0) -> list:
        state = self._load()
        rows = state.age_uncertain(holder, int(now or 0))
        self._save(state)
        return [[ident, units, created_at] for ident, units, created_at in rows]

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        state = self._load()
        ok = state.unreconcile_uncertain(holder, str(identifier))
        self._save(state)
        return ok

    async def release(self, holder: str, reservation_id: int) -> bool:
        state = self._load()
        ok = state.release(holder, int(reservation_id))
        self._save(state)
        return ok

    async def balance(self, holder: str, now: str = "") -> dict[str, Any]:
        return self._load().balance(holder, now=str(now or "")).to_json()

    async def seen(self, payment_id: str) -> bool:
        return self._load().seen(payment_id)

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> dict[str, Any]:
        state = self._load()
        result = state.expect(str(payment_id), int(units), str(tx),
                              str(source or "pack"))
        self._save(state)
        return result.to_json()

    async def payment(self, payment_id: str) -> dict[str, Any] | None:
        return self._load().payment(str(payment_id))

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> dict[str, Any]:
        state = self._load()
        result = state.refund(str(tx), int(amount), int(amount_refunded),
                              bool(full), now=str(now or ""))
        self._save(state)
        return result.to_json()

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> dict[str, Any]:
        state = self._load()
        result = state.hold(str(tx), str(dispute_id), now=str(now or ""))
        self._save(state)
        return result.to_json()

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> dict[str, Any]:
        state = self._load()
        result = state.end_hold(str(tx), str(dispute_id), bool(restore),
                                now=str(now or ""))
        self._save(state)
        return result.to_json()


def _cell(row: Any, column: str) -> Any:
    """One column of a SQL row. On Workers the row is a JsProxy of a JS object
    (attribute access, `to_py()`, no integer index); under CPython tests it
    may be a dict or a tuple."""
    to_py = getattr(row, "to_py", None)
    if callable(to_py):
        row = to_py()
    if isinstance(row, dict):
        return row.get(column)
    if isinstance(row, (list, tuple)):
        return row[0] if row else None
    return getattr(row, column, None)


def _one_row(cursor) -> Any:
    if cursor is None:
        return None
    one = getattr(cursor, "one", None)
    if callable(one):
        try:
            return one()
        except Exception:
            return None
    to_array = getattr(cursor, "toArray", None)
    if callable(to_array):
        rows = list(to_array())
        return rows[0] if rows else None
    try:
        rows = list(cursor)
    except TypeError:
        return None
    return rows[0] if rows else None
