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

    def _get(self, key: str) -> str:
        self._ensure()
        row = _one_row(self.ctx.storage.sql.exec(
            "SELECT v FROM kv WHERE k = ?", key))
        return "" if row is None else str(_cell(row, "v") or "")

    def _put(self, key: str, value: str) -> None:
        self._ensure()
        self.ctx.storage.sql.exec(
            "INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)", key, value)

    def _stored(self) -> LedgerState:
        text = self._get(_STATE_KEY)
        if not text:
            return LedgerState()
        return LedgerState.from_json(json.loads(text))

    def _save(self, state: LedgerState) -> None:
        self._put(_STATE_KEY, json.dumps(state.to_json()))

    async def claim_state(self, payment_id: str, encoded: bool = False) -> Any:
        data = self._stored().claim_state(str(payment_id))
        return json.dumps(data) if encoded else data

    async def save_claim(self, payment_id: str, data: Any,
                         kind: str, units: int, tx: str) -> None:
        state = self._stored()
        state.save_claim(str(payment_id), json.loads(data) if isinstance(data, str) else data,
                         kind=str(kind), units=int(units), tx=str(tx))
        self._save(state)

    async def finish_claim(self, payment_id: str) -> None:
        state = self._stored()
        state.finish_claim(str(payment_id))
        self._save(state)

    async def drop_claim_nonce(self, payment_id: str) -> None:
        state = self._stored()
        state.drop_claim_nonce(str(payment_id))
        self._save(state)

    async def fund_claim(self, holder: str, claim_id: str, invoice_id: str,
                         units: int, plan: str = "", customer_id: str = "",
                         subscription_id: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.fund_claim(
            str(holder), str(claim_id), str(invoice_id),
            int(units), str(plan), str(customer_id),
            subscription_id=str(subscription_id or ""))
        self._save(state)
        return result.to_json()

    async def claim_purchase(self, session_id: str, now: str) -> str:
        from access_billing import claim_from_env

        async def claim():
            return await claim_from_env(self, self.env, str(session_id), str(now))

        return await self.ctx.blockConcurrencyWhile(claim)

    async def rotation_state(self, holder: str, encoded: bool = False) -> Any:
        data = self._stored().rotation_state(str(holder))
        return json.dumps(data) if encoded else data

    async def save_rotation(self, holder: str, data: Any) -> None:
        state = self._stored()
        state.save_rotation(str(holder), json.loads(data) if isinstance(data, str) else data)
        self._save(state)

    async def rotate_key(self, current_key: str, now: str) -> str:
        from access_billing import rotate_from_env

        async def rotate():
            return await rotate_from_env(self, self.env, str(current_key), str(now))

        return await self.ctx.blockConcurrencyWhile(rotate)

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> dict[str, Any]:
        state = self._stored()
        result = state.credit(holder, payment_id, int(units), tx,
                              expires_at=str(expires_at or ""),
                              source=str(source or "x402"))
        self._save(state)
        return result.to_json()

    async def spend_paid(self, holder: str, payment_id: str, units: int,
                         tx: str, expires_at: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.spend_paid(holder, payment_id, int(units), tx,
                                  expires_at=str(expires_at or ""))
        self._save(state)
        return result.to_json()

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          period_end: int = 0, period_start: int = 0,
                          subscription_id: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.set_monthly(holder, int(units), str(invoice_id),
                                   str(plan or ""), str(customer_id or ""),
                                   period_end=int(period_end or 0),
                                   period_start=int(period_start or 0),
                                   subscription_id=str(subscription_id or ""))
        self._save(state)
        return result.to_json()

    async def clear_monthly(self, holder: str, period_end: int = 0,
                            watermark: int = 0,
                            subscription_id: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.clear_monthly(str(holder), period_end=int(period_end or 0),
                                     watermark=int(watermark or 0),
                                     subscription_id=str(subscription_id or ""))
        self._save(state)
        return result.to_json()

    async def invoice_watermark(self, holder: str) -> int:
        return self._stored().invoice_watermark(str(holder))

    async def entitlement_view(self, holder: str) -> dict[str, Any]:
        return self._stored().entitlement_view(str(holder))

    async def transfer(self, src: str, dst: str) -> bool:
        state = self._stored()
        ok = state.transfer(str(src), str(dst))
        self._save(state)
        return ok

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "", overage_cap: int = 0) -> dict[str, Any]:
        state = self._stored()
        result = state.reserve(holder, int(units), now=str(now or ""),
                               overage_cap=int(overage_cap or 0))
        self._save(state)
        return result.to_json()

    async def commit(self, holder: str, reservation_id: int) -> dict[str, Any]:
        """Save the debit and its pending meter record in the same SQL write."""
        state = self._stored()
        result = state.commit(holder, int(reservation_id))
        self._save(state)
        return result.to_json()

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> dict[str, Any]:
        state = self._stored()
        result = state.take_read(
            holder, int(reads_per_credit), int(daily_cap), int(burst_limit),
            now=str(now or ""), overage_cap=int(overage_cap or 0))
        self._save(state)
        return result.to_json()

    async def release_read(self, holder: str, token: int) -> bool:
        state = self._stored()
        ok = state.release_read(holder, int(token))
        self._save(state)
        return ok

    async def keep_read(self, holder: str, token: int) -> bool:
        state = self._stored()
        ok = state.keep_read(holder, int(token))
        self._save(state)
        return ok

    async def meter_identifier(self, holder: str, kind: str, counter: str) -> str:
        state = self._stored()
        ident = state.meter_identifier(str(holder), str(kind), counter)
        self._save(state)
        return ident

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool:
        state = self._stored()
        ok = state.note_unreported(
            holder, int(units), str(identifier), str(customer_id or ""),
            str(event_name or ""))
        self._save(state)
        return ok

    async def open_backlog(self, holder: str) -> list:
        state = self._stored()
        units, seq, ident = state.open_backlog(holder)
        self._save(state)
        return [units, seq, ident]

    async def ack_backlog(self, holder: str, units: int, n: int,
                          identifier: str = "") -> bool:
        state = self._stored()
        ok = state.ack_backlog(holder, int(units), int(n), str(identifier or ""))
        self._save(state)
        return ok

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int = 0) -> bool:
        state = self._stored()
        when = int(created_at) or None
        ok = state.note_uncertain(holder, int(units), str(identifier), when)
        self._save(state)
        return ok

    async def list_uncertain(self, holder: str) -> list:
        return [[ident, units, created_at]
                for ident, units, created_at in self._stored().list_uncertain(holder)]

    async def ack_uncertain(self, holder: str, identifier: str) -> bool:
        state = self._stored()
        ok = state.ack_uncertain(holder, str(identifier))
        self._save(state)
        return ok

    async def age_uncertain(self, holder: str, now: int = 0) -> list:
        state = self._stored()
        rows = state.age_uncertain(holder, int(now or 0))
        self._save(state)
        return [[ident, units, created_at] for ident, units, created_at in rows]

    async def open_meter_events(self, holder: str, now: int = 0) -> list:
        state = self._stored()
        rows = state.open_meter_events(holder, int(now or 0))
        self._save(state)
        return [[ident, units, created_at, first_attempt]
                for ident, units, created_at, first_attempt in rows]

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        state = self._stored()
        ok = state.unreconcile_uncertain(holder, str(identifier))
        self._save(state)
        return ok

    async def release(self, holder: str, reservation_id: int) -> bool:
        state = self._stored()
        ok = state.release(holder, int(reservation_id))
        self._save(state)
        return ok

    async def has_read_funding(self, holder: str, now: str = "") -> bool:
        return self._stored().has_read_funding(holder, now=str(now or ""))

    async def balance(self, holder: str, now: str = "") -> dict[str, Any]:
        return self._stored().balance(holder, now=str(now or "")).to_json()

    async def seen(self, payment_id: str) -> bool:
        return self._stored().seen(payment_id)

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> dict[str, Any]:
        state = self._stored()
        result = state.expect(str(payment_id), int(units), str(tx),
                              str(source or "pack"))
        self._save(state)
        return result.to_json()

    async def payment(self, payment_id: str) -> dict[str, Any] | None:
        return self._stored().payment(str(payment_id))

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.refund(str(tx), int(amount), int(amount_refunded),
                              bool(full), now=str(now or ""))
        self._save(state)
        return result.to_json()

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> dict[str, Any]:
        state = self._stored()
        result = state.hold(str(tx), str(dispute_id), now=str(now or ""))
        self._save(state)
        return result.to_json()

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> dict[str, Any]:
        state = self._stored()
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
