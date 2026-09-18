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
        text = row[0] if not isinstance(row, dict) else row.get("v")
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
                     tx: str) -> dict[str, Any]:
        state = self._load()
        result = state.credit(holder, payment_id, int(units), tx)
        self._save(state)
        return result.to_json()

    async def reserve(self, holder: str, units: int = 1) -> dict[str, Any]:
        state = self._load()
        result = state.reserve(holder, int(units))
        self._save(state)
        return result.to_json()

    async def commit(self, holder: str, reservation_id: int) -> bool:
        state = self._load()
        ok = state.commit(holder, int(reservation_id))
        self._save(state)
        return ok

    async def release(self, holder: str, reservation_id: int) -> bool:
        state = self._load()
        ok = state.release(holder, int(reservation_id))
        self._save(state)
        return ok

    async def balance(self, holder: str) -> dict[str, Any]:
        return self._load().balance(holder).to_json()

    async def seen(self, payment_id: str) -> bool:
        return self._load().seen(payment_id)


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
