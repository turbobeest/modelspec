"""Durable Object wrapping `credits.LedgerState` (MODEL-75).

Bound as `CREDITS`. One instance, id `ledger`. SQLite holds a single JSON
document so a mutation is one write, not a cross-key KV race. The class is
imported from `entry.py` so Wrangler can find it by `class_name`.

MODEL-441. A Durable Object cannot move between Cloudflare accounts, so the
ledger moves by handoff between two objects with explicit roles (live,
standby, moving, moved). `begin_handoff` seals the live ledger in one
synchronous write and returns its copy; the target, in standby, imports it;
`finish_handoff` marks the source moved, and `credits.DurableLedger` forwards
its calls to the target from then on. Exactly one ledger is live at a time.
See api/worker/src/ledger_bridge.py and docs/ops/cloudflare-account-move.md.
"""

from __future__ import annotations

import hashlib
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
_ROLE_KEY = "role"
_TARGET_KEY = "target"
_SEALED_KEY = "sealed_digest"
_IMPORTED_KEY = "imported_digest"

#: A ledger's part in a move. `live` serves calls. `standby` has never served
#: and waits for an import. `moving` is sealed and its copy is in flight to
#: `target`. `moved` is sealed for good and its calls go to `target`.
LIVE, STANDBY, MOVING, MOVED = "live", "standby", "moving", "moved"

#: The mark a sealed ledger's errors carry. Error text can echo caller input,
#: so callers treat it as a hint and read `handoff_status` before acting.
SEALED_MARK = "ledger-sealed"


class LedgerSealed(RuntimeError):
    """This ledger does not serve calls in its current role."""


def state_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(state: LedgerState) -> str:
    return json.dumps(state.to_json(), sort_keys=True, separators=(",", ":"))


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

    def _role(self) -> str:
        """The stored role, else the deployment's starting role. Only a new
        account's Worker starts in standby (LEDGER_STANDBY), so the ledger that
        already serves production is live without any stored role."""
        role = self._get(_ROLE_KEY)
        if role:
            return role
        flag = str(getattr(self.env, "LEDGER_STANDBY", "") or "").strip().lower()
        return STANDBY if flag in ("1", "true", "yes", "on") else LIVE

    def _set(self, role: str, target: str = "", sealed: str = "") -> None:
        self._put(_ROLE_KEY, role)
        self._put(_TARGET_KEY, target)
        self._put(_SEALED_KEY, sealed)

    def _load(self) -> LedgerState:
        role = self._role()
        if role != LIVE:
            raise LedgerSealed(f"{SEALED_MARK}: {role}")
        return self._stored()

    def _save(self, state: LedgerState) -> None:
        self._put(_STATE_KEY, json.dumps(state.to_json()))

    async def handoff_status(self) -> dict[str, Any]:
        return {"role": self._role(), "target": self._get(_TARGET_KEY),
                "digest": state_digest(canonical(self._stored())),
                "sealed_digest": self._get(_SEALED_KEY),
                "imported_digest": self._get(_IMPORTED_KEY)}

    async def begin_handoff(self, target: str) -> dict[str, Any]:
        """Seal this live ledger for `target` and return its copy. Re-running
        for the same target returns the same copy, so an interrupted handoff
        can be completed."""
        target = str(target)
        role = self._role()
        if role in (MOVING, MOVED) and self._get(_TARGET_KEY) != target:
            raise ValueError("ledger is sealed for another target")
        if role == STANDBY:
            raise ValueError("a standby ledger has nothing to hand off")
        text = canonical(self._stored())
        if role == LIVE:
            self._set(MOVING, target, state_digest(text))
        return {"state": text, "digest": state_digest(text)}

    async def finish_handoff(self, target: str, digest: str) -> dict[str, Any]:
        role = self._role()
        if role == MOVED and self._get(_TARGET_KEY) == str(target):
            return await self.handoff_status()
        if role != MOVING or self._get(_TARGET_KEY) != str(target):
            raise ValueError("no handoff to this target is in progress")
        if self._get(_SEALED_KEY) != str(digest):
            raise ValueError("digest does not match the sealed ledger")
        self._set(MOVED, str(target), str(digest))
        # It no longer holds the copy it took in earlier; a later copy with the
        # same digest must be imported, not mistaken for a re-run.
        self._put(_IMPORTED_KEY, "")
        return await self.handoff_status()

    async def abort_handoff(self) -> dict[str, Any]:
        """Unseal a ledger whose copy did not land. Only `moving`: a moved
        ledger's copy is live elsewhere and comes back only by a hand-back."""
        if self._role() != MOVING:
            raise ValueError("only a ledger that is moving can be unsealed")
        self._set(LIVE)
        return await self.handoff_status()

    async def import_state(self, text: str, digest: str) -> dict[str, Any]:
        """Take a handed-off copy. Idempotent on the copy's digest, so a re-run
        after a lost answer succeeds even once the copy has taken writes.
        Otherwise accepted only by a ledger that holds no live state: one in
        standby, or one that handed its ledger away earlier (a hand-back).
        Never by a live or moving ledger, whose state is still the real one."""
        text, digest = str(text), str(digest)
        if state_digest(text) != digest:
            raise ValueError("digest does not match the document")
        role = self._role()
        if role == LIVE and self._get(_IMPORTED_KEY) == digest:
            return await self.handoff_status()
        if role not in (STANDBY, MOVED):
            raise ValueError(f"a {role} ledger does not accept a copy")
        self._save(LedgerState.from_json(json.loads(text)))
        self._put(_IMPORTED_KEY, digest)
        self._set(LIVE)
        return await self.handoff_status()

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
                          plan: str = "", customer_id: str = "") -> dict[str, Any]:
        state = self._load()
        result = state.set_monthly(holder, int(units), str(invoice_id),
                                   str(plan or ""), str(customer_id or ""))
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
        """Save the debit and its pending meter record in the same SQL write."""
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

    async def ack_backlog(self, holder: str, units: int, n: int,
                          identifier: str = "") -> bool:
        state = self._load()
        ok = state.ack_backlog(holder, int(units), int(n), str(identifier or ""))
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

    async def open_meter_events(self, holder: str, now: int = 0) -> list:
        state = self._load()
        rows = state.open_meter_events(holder, int(now or 0))
        self._save(state)
        return [[ident, units, created_at, first_attempt]
                for ident, units, created_at, first_attempt in rows]

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

    async def has_read_funding(self, holder: str, now: str = "") -> bool:
        return self._load().has_read_funding(holder, now=str(now or ""))

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
