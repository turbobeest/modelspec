"""Durable Object wrapping `credits.LedgerState` (MODEL-75).

Bound as `CREDITS`. One instance, id `ledger`. SQLite holds a single JSON
document so a mutation is one write, not a cross-key KV race. The class is
imported from `entry.py` so Wrangler can find it by `class_name`.

MODEL-441. A Durable Object cannot move between Cloudflare accounts, so the
ledger moves by export and import across a short write freeze. `export_state`
seals this ledger in the same write that reads its copy, and from then on it
refuses every call. The new account's ledger waits in standby until
`import_state` makes it live. Exactly one ledger is live at a time, and none
during the freeze. See api/worker/src/ledger_admin.py and
docs/ops/cloudflare-account-move.md.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
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
#: One JSON row, so every role change is a single write: the role, the digest
#: this ledger was sealed with and how many times it has been exported, and
#: the digest and export it was imported from.
_META_KEY = "move"

_LEASES_KEY = "leases"

#: How long a billing mutation's lease on a live ledger lasts. Export waits
#: for every lease to end or expire, and a write under an expired lease is
#: refused, so no billing write can land after the ledger is copied.
LEASE_SECONDS = 120

#: The clock, swapped in tests.
_clock = time.time

#: A ledger's part in a move. `live` serves calls. `standby` has never served
#: and waits for its import. `sealed` has been exported and serves nothing.
LIVE, STANDBY, SEALED = "live", "standby", "sealed"

#: The mark a ledger that is not live puts on its errors. Error text can echo
#: caller input, so callers treat it as a hint and read `move_status` first.
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

    def _meta(self) -> dict[str, str]:
        """The move record. With none, the deployment's starting role: only a
        Worker deployed to receive the ledger starts in standby
        (LEDGER_STANDBY), so the ledger that already serves is live with
        nothing stored."""
        text = self._get(_META_KEY)
        if text:
            return {str(k): str(v) for k, v in json.loads(text).items()}
        flag = str(getattr(self.env, "LEDGER_STANDBY", "") or "").strip().lower()
        return {"role": STANDBY if flag in ("1", "true", "yes", "on") else LIVE}

    def _write_meta(self, meta: dict[str, str]) -> None:
        self._put(_META_KEY, json.dumps(meta, sort_keys=True))

    def _load(self) -> LedgerState:
        role = self._meta().get("role", LIVE)
        if role != LIVE:
            raise LedgerSealed(f"{SEALED_MARK}: {role}")
        return self._stored()

    def _save(self, state: LedgerState) -> None:
        self._put(_STATE_KEY, json.dumps(state.to_json()))

    async def move_status(self) -> dict[str, Any]:
        meta = self._meta()
        state = self._stored()
        return {"role": meta.get("role", LIVE), "digest": state_digest(canonical(state)),
                "holders": len(state.accounts), "sealed": meta.get("sealed", ""),
                "generation": meta.get("exports", ""), "sealed_at": meta.get("sealed_at", ""),
                "imported": meta.get("imported", ""),
                "imported_generation": meta.get("imported_generation", ""),
                "open_leases": len(self._leases())}

    def _leases(self) -> dict[str, float]:
        text = self._get(_LEASES_KEY)
        now = _clock()
        held = {str(k): float(v) for k, v in (json.loads(text) if text else {}).items()}
        return {k: v for k, v in held.items() if v > now}

    async def admit(self) -> str:
        """A lease for one billing mutation on this live ledger (MODEL-441)."""
        self._load()
        leases = self._leases()
        lease = secrets.token_hex(8)
        leases[lease] = _clock() + LEASE_SECONDS
        self._put(_LEASES_KEY, json.dumps(leases))
        return lease

    async def lease_ok(self, lease: str) -> bool:
        return (self._meta().get("role", LIVE) == LIVE
                and self._leases().get(str(lease), 0.0) > _clock())

    async def release_lease(self, lease: str) -> None:
        leases = self._leases()
        if leases.pop(str(lease), None) is not None:
            self._put(_LEASES_KEY, json.dumps(leases))

    async def export_state(self) -> dict[str, Any]:
        """Seal this ledger and return its copy, in one synchronous write, so
        no call can land between the copy and the seal. Open reservations and
        taken reads are released first: their requests can no longer commit,
        so they fail with a 503 and are not charged, and no hold is stranded
        in the copy. Exporting again returns the same copy."""
        meta = self._meta()
        if meta.get("role") == STANDBY:
            raise ValueError("a standby ledger has nothing to export")
        if meta.get("role") == LIVE:
            open_leases = self._leases()
            if open_leases:
                wait = int(max(open_leases.values()) - _clock()) + 1
                raise ValueError(f"{len(open_leases)} billing write(s) in flight; "
                                 f"export again in at most {wait}s")
            state = self._stored()
            for holder, acc in state.accounts.items():
                for rid in list(acc.reservations):
                    state.release(holder, rid)
                for token in list(acc.taken_reads):
                    state.release_read(holder, token)
            self._save(state)
            self._write_meta({**meta, "role": SEALED,
                              "sealed": state_digest(canonical(state)),
                              "exports": str(int(meta.get("exports") or 0) + 1),
                              "sealed_at": str(int(_clock()))})
        text = canonical(self._stored())
        return {"state": text, "digest": state_digest(text), **await self.move_status()}

    async def import_state(self, text: str, digest: str, generation: str = "") -> dict[str, Any]:
        """Take the exported copy. Only a standby ledger accepts one; importing
        the same copy again is a no-op. The state is written before the record
        that makes it live, so a restart between the two leaves a standby
        ledger that simply imports again."""
        text, digest, generation = str(text), str(digest), str(generation)
        if state_digest(text) != digest:
            raise ValueError("the copy does not match its digest")
        if not generation.isdigit() or int(generation) < 1:
            raise ValueError("the copy carries no export generation")
        meta = self._meta()
        same_copy = (meta.get("imported") == digest
                     and meta.get("imported_generation", "") == generation)
        if same_copy and meta.get("role") == LIVE:
            return await self.move_status()
        # A rolled-back destination: imported, then sealed with no write in
        # between, so it holds only a stale copy and may take a fresh export:
        # one with a strictly newer generation. Any earlier export, including
        # the one it was rolled back from, predates the source's unseal, so
        # taking it would make a second live ledger.
        rolled_back = (meta.get("role") == SEALED and meta.get("imported")
                       and meta.get("imported") == meta.get("sealed")
                       and int(generation) > int(meta.get("imported_generation") or 0))
        if meta.get("role") != STANDBY and not rolled_back:
            raise ValueError(f"a {meta.get('role')} ledger does not accept a copy")
        held = canonical(self._stored())
        if not rolled_back and held not in (
                canonical(LedgerState()), canonical(LedgerState.from_json(json.loads(text)))):
            # Standby comes from the deployment when nothing is recorded, so a
            # ledger that already holds balances must refuse rather than lose them.
            raise ValueError("this standby ledger already holds other balances")
        self._save(LedgerState.from_json(json.loads(text)))
        self._write_meta({"role": LIVE, "imported": digest, "imported_generation": generation,
                          "exports": meta.get("exports", "")})
        return await self.move_status()

    async def unseal(self, digest: str) -> dict[str, Any]:
        """Undo an export before the zone moves. Takes the digest it was sealed
        with, so it cannot be done by accident; the runbook seals the new
        ledger first and checks it took no writes."""
        meta = self._meta()
        if meta.get("role") != SEALED or meta.get("sealed") != str(digest):
            raise ValueError("that is not the digest this ledger was sealed with")
        self._write_meta({**meta, "role": LIVE})
        return await self.move_status()

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> dict[str, Any]:
        state = self._load()
        result = state.credit(holder, payment_id, int(units), tx,
                              expires_at=str(expires_at or ""),
                              source=str(source or "x402"))
        self._save(state)
        return result.to_json()

    async def spend_paid(self, holder: str, payment_id: str, units: int,
                         tx: str, expires_at: str = "") -> dict[str, Any]:
        state = self._load()
        result = state.spend_paid(holder, payment_id, int(units), tx,
                                  expires_at=str(expires_at or ""))
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
