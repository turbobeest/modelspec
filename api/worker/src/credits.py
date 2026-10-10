"""Prepaid credit ledger (MODEL-75, MODEL-93).

Workers KV is eventually consistent and has no compare-and-set, so it cannot
keep a balance non-negative under concurrent requests. This module does not
use it. Mutations go through `LedgerState`, which is serial: `MemoryLedger`
holds an asyncio lock for tests; production wraps the same state in one
Durable Object (`CreditsObject`, `docs/x402.md`).

Record kinds, both JSON inside the object:

* a balance per holder — monthly remaining, pack grants (remaining + expiry),
  and reserved units for in-flight requests
* a payment claim per payment id (holder, units, settlement tx / invoice id)

A payment id is credited at most once. Reserve-before-produce is what makes a
4xx/5xx/no-match cost nothing, and what stops two in-flight requests spending
the same last unit.

Draw order: monthly allowance first, then pack grants, oldest expiry first.
Monthly SET (a paid invoice) replaces remaining monthly; it does not add.
Pack credits ADD and expire. Cancellation zeros monthly and leaves packs.

Reversals (MODEL-106). A card pack's payment claim stores the Stripe
PaymentIntent id as its `tx`, which is how a refund or a dispute finds it: a
refund removes the refunded share of the pack's unspent credits, a dispute
holds them until it closes. Spent credits are never clawed back. An anonymous
pack is `pending` (no holder yet) from payment until claim, so a refund or
dispute that arrives first is applied when the claim grants it.

The unit is a credit.
"""

from __future__ import annotations

import asyncio
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

LEGACY_EXPIRY = "9999-12-31T00:00:00Z"
# Stripe may already have an uncertain meter event. Retry that identifier,
# and stop queueing once this many are still open. One report retries at most
# UNCERTAIN_RETRIES_PER_REQUEST of them. An identifier is unique for about a
# day, so an entry older than UNCERTAIN_MAX_AGE_SECONDS is not retried.
UNCERTAIN_METER_CAP = 20
UNCERTAIN_RETRIES_PER_REQUEST = 3
UNCERTAIN_MAX_AGE_SECONDS = 20 * 60 * 60


def _unix_now() -> int:
    return int(time.time())


def _uncertain_rows(raw: Any, *, now: int | None = None) -> tuple[list[tuple[str, int, int]], int]:
    """Keep at most `UNCERTAIN_METER_CAP` events. Further units are unreconciled.

    Each kept row is `(identifier, units, created_at)`. A stored row with no
    `created_at` loads as created at `now`.
    """
    clock = _unix_now() if now is None else int(now)
    kept: list[tuple[str, int, int]] = []
    overflow = 0
    if not isinstance(raw, list):
        return kept, overflow
    for row in raw:
        if not isinstance(row, dict):
            continue
        ident = str(row.get("identifier") or "").strip()
        units = int(row.get("units") or 0)
        if not ident or units < 1:
            continue
        if len(kept) >= UNCERTAIN_METER_CAP:
            overflow += units
            continue
        if "created_at" not in row or row.get("created_at") in (None, ""):
            created_at = clock
        else:
            created_at = int(row["created_at"])
        kept.append((ident, units, created_at))
    return kept, overflow


def _uncertain_wire(data: Any) -> list[tuple[str, int, int]]:
    """Rows from a Durable Object: identifier, units, created_at."""
    to_py = getattr(data, "to_py", None)
    rows = to_py() if callable(to_py) else data
    out: list[tuple[str, int, int]] = []
    for row in rows or []:
        ident, units, created_at = row
        out.append((str(ident), int(units), int(created_at)))
    return out


def _ensure_meter_id(acc: _Account) -> str:
    """Random `m_` plus 32 hex chars. Reuse a stored id. Never derive one."""
    current = str(acc.meter_id or "")
    if current.strip():
        return current
    acc.meter_id = "m_" + secrets.token_hex(16)
    return acc.meter_id


def _stamp_backlog_id(acc: _Account) -> None:
    if acc.overage_backlog_open > 0 and not str(acc.overage_backlog_id or "").strip():
        acc.overage_backlog_id = f"{_ensure_meter_id(acc)}:backlog:{acc.overage_backlog_n}"


def _append_uncertain(acc: _Account, identifier: str, units: int,
                      created_at: int | None = None) -> bool:
    """Park one uncertain event. A full list adds `units` to `overage_unreconciled`."""
    ident = str(identifier or "").strip()
    amount = int(units)
    if amount < 1 or not ident:
        return False
    if any(row[0] == ident for row in acc.overage_uncertain):
        return True
    if len(acc.overage_uncertain) >= UNCERTAIN_METER_CAP:
        acc.overage_unreconciled += amount
        return False
    when = _unix_now() if created_at is None else int(created_at)
    acc.overage_uncertain.append((ident, amount, when))
    return True


def _move_meter_tail(existing: _Account, acc: _Account) -> None:
    """Copy meter retry state without giving an in-flight event a new id.

    The destination keeps its own `meter_id` when it has one. Otherwise it
    inherits the source's. Identifiers already stored are copied as they are.
    """
    if not str(existing.meter_id or "").strip():
        existing.meter_id = str(acc.meter_id or "")
    _stamp_backlog_id(existing)
    _stamp_backlog_id(acc)
    existing.overage_unreported += acc.overage_unreported
    existing.overage_unreconciled += acc.overage_unreconciled
    for ident, units, created_at in acc.overage_uncertain:
        _append_uncertain(existing, ident, units, created_at)
    if acc.overage_backlog_open > 0 and existing.overage_backlog_open < 1:
        existing.overage_backlog_open = acc.overage_backlog_open
        existing.overage_backlog_id = acc.overage_backlog_id
    elif acc.overage_backlog_open > 0 and existing.overage_backlog_id != acc.overage_backlog_id:
        # Dest already has its own in-flight identifier. Keep that snapshot
        # and retry the source snapshot under the identifier Stripe saw.
        parked = acc.overage_backlog_open
        existing.overage_unreported = max(0, existing.overage_unreported - parked)
        _append_uncertain(existing, acc.overage_backlog_id, parked)
    # n only chooses the next new identifier. Never rewind it.
    existing.overage_backlog_n = max(existing.overage_backlog_n, acc.overage_backlog_n)


class StoreNotConfigured(RuntimeError):
    """No Durable Object binding. Parallel to access_kv.StoreNotConfigured."""


def _now_iso(moment: datetime | None = None) -> str:
    clock = moment or datetime.now(UTC)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=UTC)
    return clock.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _expired(expires_at: str, now: str) -> bool:
    return (expires_at or "") <= now


@dataclass(frozen=True)
class CreditResult:
    credited: bool
    reason: str = ""
    units: int = 0

    def to_json(self) -> dict[str, Any]:
        return {"credited": self.credited, "reason": self.reason, "units": self.units}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> CreditResult:
        return cls(bool(data.get("credited")), str(data.get("reason") or ""),
                   int(data.get("units") or 0))


@dataclass(frozen=True)
class ReserveResult:
    ok: bool
    reservation_id: int | None = None
    available: int = 0
    reserved: int = 0

    def to_json(self) -> dict[str, Any]:
        return {"ok": self.ok, "reservation_id": self.reservation_id,
                "available": self.available, "reserved": self.reserved}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ReserveResult:
        rid = data.get("reservation_id")
        return cls(bool(data.get("ok")), None if rid is None else int(rid),
                   int(data.get("available") or 0), int(data.get("reserved") or 0))


@dataclass(frozen=True)
class CommitResult:
    """A settled reservation. `overage` is units past the prepaid balance.

    Truthy when the reservation existed, so callers that only check success
    keep working. A release never produces one of these: uncommitted overage
    is capacity returned, not a charge.
    """

    ok: bool
    overage: int = 0

    def __bool__(self) -> bool:
        return self.ok

    def to_json(self) -> dict[str, Any]:
        return {"ok": self.ok, "overage": self.overage}

    @classmethod
    def from_json(cls, data: Any) -> CommitResult:
        if isinstance(data, bool):
            return cls(data, 0)
        if not isinstance(data, dict):
            return cls(bool(data), 0)
        return cls(bool(data.get("ok")), int(data.get("overage") or 0))


@dataclass(frozen=True)
class ReadResult:
    """One metadata-read attempt. A refusal is not counted and not charged."""

    ok: bool
    reason: str = ""
    token: int | None = None
    available: int = 0
    read_count: int = 0
    read_burst: int = 0
    daily_cap: int = 0
    burst_limit: int = 0
    overage: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "ok": self.ok, "reason": self.reason, "token": self.token,
            "available": self.available, "read_count": self.read_count,
            "read_burst": self.read_burst, "daily_cap": self.daily_cap,
            "burst_limit": self.burst_limit, "overage": self.overage,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ReadResult:
        token = data.get("token")
        return cls(
            bool(data.get("ok")), str(data.get("reason") or ""),
            None if token is None else int(token),
            int(data.get("available") or 0), int(data.get("read_count") or 0),
            int(data.get("read_burst") or 0), int(data.get("daily_cap") or 0),
            int(data.get("burst_limit") or 0), int(data.get("overage") or 0),
        )


@dataclass(frozen=True)
class ReversalResult:
    """What a refund or a dispute did to one pack's credits (MODEL-106).

    `found` is false when no pack payment claim carries that PaymentIntent id:
    a plan invoice, a purchase made before the id was recorded, or a charge
    that is not ours. `pending` means the pack had not been claimed yet.
    """

    found: bool
    payment_id: str = ""
    pending: bool = False
    purchased: int = 0
    refunded_share: int = 0
    removed: int = 0
    already_spent: int = 0
    expired: int = 0
    held: int = 0
    restored: int = 0
    forfeited: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "found": self.found, "payment_id": self.payment_id,
            "pending": self.pending, "purchased": self.purchased,
            "refunded_share": self.refunded_share, "removed": self.removed,
            "already_spent": self.already_spent, "expired": self.expired,
            "held": self.held, "restored": self.restored,
            "forfeited": self.forfeited,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ReversalResult:
        return cls(
            bool(data.get("found")), str(data.get("payment_id") or ""),
            bool(data.get("pending")), int(data.get("purchased") or 0),
            int(data.get("refunded_share") or 0), int(data.get("removed") or 0),
            int(data.get("already_spent") or 0), int(data.get("expired") or 0),
            int(data.get("held") or 0), int(data.get("restored") or 0),
            int(data.get("forfeited") or 0),
        )


def refunded_share(purchased: int, amount: int, amount_refunded: int,
                   full: bool) -> int:
    """Credits a refund of `amount_refunded` out of `amount` takes back.

    Proportional to the money returned, measured against the credits the pack
    was sold with, rounded up: refunding the value of the unused balance
    (terms §6.6) removes exactly the unused credits, and a fraction of a credit
    never stays with the refunded buyer. Both amounts are the Charge's, tax
    included, so a refund of the whole tax-inclusive price is a full refund.
    """
    if full or amount <= 0:
        return purchased
    share = -(-purchased * max(0, amount_refunded) // amount)
    return max(0, min(purchased, share))


def _grantable(rec: dict[str, Any]) -> int:
    """Credits a pending pack claim will still grant: bought, less refunded or forfeited."""
    return max(0, int(rec.get("units") or 0) - int(rec.get("refunded") or 0)
               - int(rec.get("forfeited") or 0))


def unclaimed_units(rec: dict[str, Any] | None) -> int | None:
    """For a pending pack payment claim, what claim would grant. None if not pending."""
    if not rec or not rec.get("pending"):
        return None
    return _grantable(rec)


@dataclass(frozen=True)
class PackGrantView:
    grant_id: str
    remaining: int
    expires_at: str
    source: str

    def to_json(self) -> dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "remaining": self.remaining,
            "expires_at": self.expires_at,
            "source": self.source,
        }


@dataclass(frozen=True)
class Balance:
    holder: str
    available: int
    reserved: int
    monthly: int = 0
    packs: int = 0
    grants: tuple[PackGrantView, ...] = ()
    plan: str = ""
    overage_used: int = 0
    stripe_customer_id: str = ""
    overage_unreported: int = 0

    @property
    def total(self) -> int:
        return self.available + self.reserved

    def to_json(self) -> dict[str, Any]:
        return {
            "holder": self.holder,
            "available": self.available,
            "reserved": self.reserved,
            "total": self.total,
            "monthly": self.monthly,
            "packs": self.packs,
            "grants": [g.to_json() for g in self.grants],
            "plan": self.plan,
            "overage_used": self.overage_used,
            "stripe_customer_id": self.stripe_customer_id,
            "overage_unreported": self.overage_unreported,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Balance:
        raw_grants = data.get("grants") or []
        grants = tuple(
            PackGrantView(
                str(row.get("grant_id") or ""),
                int(row.get("remaining") or 0),
                str(row.get("expires_at") or ""),
                str(row.get("source") or ""),
            )
            for row in raw_grants if isinstance(row, dict)
        )
        return cls(
            str(data.get("holder") or ""),
            int(data.get("available") or 0),
            int(data.get("reserved") or 0),
            int(data.get("monthly") or 0),
            int(data.get("packs") or 0),
            grants,
            str(data.get("plan") or ""),
            int(data.get("overage_used") or 0),
            str(data.get("stripe_customer_id") or ""),
            int(data.get("overage_unreported") or 0),
        )


@dataclass
class _PackGrant:
    """Pack credits from one payment. `held` is frozen by an open dispute."""

    grant_id: str
    remaining: int
    expires_at: str
    source: str
    held: int = 0
    hold_id: str = ""

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "grant_id": self.grant_id,
            "remaining": self.remaining,
            "expires_at": self.expires_at,
            "source": self.source,
        }
        if self.held or self.hold_id:
            data["held"] = self.held
            data["hold_id"] = self.hold_id
        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> _PackGrant:
        return cls(
            str(data.get("grant_id") or ""),
            int(data.get("remaining") or 0),
            str(data.get("expires_at") or LEGACY_EXPIRY),
            str(data.get("source") or "pack"),
            int(data.get("held") or 0),
            str(data.get("hold_id") or ""),
        )


@dataclass
class _Reservation:
    units: int
    monthly: int = 0
    packs: list[tuple[str, int]] = field(default_factory=list)
    overage: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "units": self.units,
            "monthly": self.monthly,
            "packs": [[grant_id, amount] for grant_id, amount in self.packs],
            "overage": self.overage,
        }

    @classmethod
    def from_json(cls, data: Any) -> _Reservation:
        if isinstance(data, int):
            return cls(units=int(data), monthly=0, packs=[("legacy", int(data))])
        if not isinstance(data, dict):
            return cls(units=0)
        packs = []
        for row in data.get("packs") or []:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                packs.append((str(row[0]), int(row[1])))
            elif isinstance(row, dict):
                packs.append((str(row.get("grant_id") or ""), int(row.get("units") or 0)))
        return cls(
            units=int(data.get("units") or 0),
            monthly=int(data.get("monthly") or 0),
            packs=packs,
            overage=int(data.get("overage") or 0),
        )


@dataclass
class _TakenRead:
    """One counted catalog read, so a failed response can give that read back."""

    day: str = ""
    minute: str = ""
    overage: int = 0
    monthly: int = 0
    packs: list[tuple[str, int]] = field(default_factory=list)
    block_before: int = 0
    block_after: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "day": self.day, "minute": self.minute, "overage": self.overage,
            "monthly": self.monthly,
            "packs": [[grant_id, amount] for grant_id, amount in self.packs],
            "block_before": self.block_before, "block_after": self.block_after,
        }

    @classmethod
    def from_json(cls, data: Any) -> _TakenRead:
        if not isinstance(data, dict):
            return cls()
        packs = []
        for row in data.get("packs") or []:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                packs.append((str(row[0]), int(row[1])))
        return cls(
            str(data.get("day") or ""), str(data.get("minute") or ""),
            int(data.get("overage") or 0), int(data.get("monthly") or 0), packs,
            int(data.get("block_before") or 0), int(data.get("block_after") or 0),
        )


@dataclass
class _Account:
    monthly: int = 0
    reserved: int = 0
    next_res: int = 1
    reservations: dict[int, _Reservation] = field(default_factory=dict)
    packs: list[_PackGrant] = field(default_factory=list)
    plan: str = ""
    overage_used: int = 0
    stripe_customer_id: str = ""
    meter_id: str = ""
    read_day: str = ""
    read_count: int = 0
    read_minute: str = ""
    read_burst: int = 0
    reads_in_block: int = 0
    next_read: int = 1
    taken_reads: dict[int, _TakenRead] = field(default_factory=dict)
    overage_unreported: int = 0
    overage_backlog_n: int = 0
    overage_backlog_open: int = 0
    overage_backlog_id: str = ""
    overage_uncertain: list[tuple[str, int, int]] = field(default_factory=list)
    overage_unreconciled: int = 0

    def overage_open(self) -> int:
        return sum(item.overage for item in self.reservations.values())

    def live_packs(self, now: str) -> list[_PackGrant]:
        return [g for g in self.packs if g.remaining > 0 and not _expired(g.expires_at, now)]

    def pack_remaining(self, now: str) -> int:
        return sum(g.remaining for g in self.live_packs(now))

    def available_at(self, now: str) -> int:
        return max(0, self.monthly) + self.pack_remaining(now)

    def drop_expired(self, now: str) -> None:
        self.packs = [g for g in self.packs
                      if (g.remaining > 0 or g.held > 0) and not _expired(g.expires_at, now)]

    def to_json(self) -> dict[str, Any]:
        return {
            "monthly": self.monthly,
            "available": self.monthly + sum(g.remaining for g in self.packs if g.remaining > 0),
            "reserved": self.reserved,
            "next_res": self.next_res,
            "reservations": {str(k): v.to_json() for k, v in self.reservations.items()},
            "packs": [g.to_json() for g in self.packs],
            "plan": self.plan,
            "overage_used": self.overage_used,
            "stripe_customer_id": self.stripe_customer_id,
            "meter_id": self.meter_id,
            "read_day": self.read_day,
            "read_count": self.read_count,
            "read_minute": self.read_minute,
            "read_burst": self.read_burst,
            "reads_in_block": self.reads_in_block,
            "next_read": self.next_read,
            "taken_reads": {str(k): v.to_json() for k, v in self.taken_reads.items()},
            "overage_unreported": self.overage_unreported,
            "overage_backlog_n": self.overage_backlog_n,
            "overage_backlog_open": self.overage_backlog_open,
            "overage_backlog_id": self.overage_backlog_id,
            "overage_uncertain": [
                {"identifier": ident, "units": units, "created_at": created_at}
                for ident, units, created_at in self.overage_uncertain
            ],
            "overage_unreconciled": self.overage_unreconciled,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> _Account:
        raw = data.get("reservations") or {}
        reservations = {int(k): _Reservation.from_json(v) for k, v in raw.items()}
        packs = [_PackGrant.from_json(row) for row in (data.get("packs") or [])
                 if isinstance(row, dict)]
        raw_reads = data.get("taken_reads") or {}
        taken = {int(k): _TakenRead.from_json(v) for k, v in raw_reads.items()
                 if isinstance(v, dict)}
        uncertain, uncertain_overflow = _uncertain_rows(data.get("overage_uncertain"))
        if "overage_unreported" in data:
            unreported = int(data.get("overage_unreported") or 0)
        else:
            unreported = sum(
                int(row.get("units") or 0)
                for row in (data.get("unreported_overage") or [])
                if isinstance(row, dict))
        monthly = int(data.get("monthly") or 0)
        if not packs and "available" in data and "monthly" not in data:
            leftover = int(data.get("available") or 0)
            if leftover > 0:
                packs = [_PackGrant(
                    grant_id="legacy", remaining=leftover,
                    expires_at=LEGACY_EXPIRY, source="legacy")]
        return cls(
            monthly=monthly,
            reserved=int(data.get("reserved") or 0),
            next_res=int(data.get("next_res") or 1),
            reservations=reservations,
            packs=packs,
            plan=str(data.get("plan") or ""),
            overage_used=int(data.get("overage_used") or 0),
            stripe_customer_id=str(data.get("stripe_customer_id") or ""),
            meter_id=str(data.get("meter_id") or ""),
            read_day=str(data.get("read_day") or ""),
            read_count=int(data.get("read_count") or 0),
            read_minute=str(data.get("read_minute") or ""),
            read_burst=int(data.get("read_burst") or 0),
            reads_in_block=int(data.get("reads_in_block") or 0),
            next_read=int(data.get("next_read") or 1),
            taken_reads=taken,
            overage_unreported=unreported,
            overage_backlog_n=int(data.get("overage_backlog_n") or 0),
            overage_backlog_open=int(data.get("overage_backlog_open") or 0),
            overage_backlog_id=str(data.get("overage_backlog_id") or ""),
            overage_uncertain=uncertain,
            overage_unreconciled=int(data.get("overage_unreconciled") or 0) + uncertain_overflow,
        )


@dataclass
class LedgerState:
    """The whole ledger. One object, so every mutation is ordered against every other."""

    accounts: dict[str, _Account] = field(default_factory=dict)
    payments: dict[str, dict[str, Any]] = field(default_factory=dict)

    def _acc(self, holder: str) -> _Account:
        acc = self.accounts.get(holder)
        if acc is None:
            acc = _Account()
            self.accounts[holder] = acc
        return acc

    def credit(self, holder: str, payment_id: str, units: int,
               tx: str, expires_at: str = "", source: str = "x402") -> CreditResult:
        """ADD pack credits. Idempotent on payment_id. Same bucket as a card pack.

        A `pending` claim (see `expect`) is granted here, to this holder, less
        anything a refund or a lost dispute took before claim, and held if a
        dispute is still open.
        """
        rec = self.payments.get(payment_id)
        if rec is not None and rec.get("pending"):
            return self._grant_pending(holder, payment_id, rec, expires_at, source)
        if rec is not None:
            reason = "replay" if rec.get("holder") == holder else "conflict"
            return CreditResult(False, reason, int(rec.get("units") or 0))
        if units < 1:
            return CreditResult(False, "zero", 0)
        expiry = expires_at or LEGACY_EXPIRY
        self.payments[payment_id] = {
            "holder": holder, "units": int(units), "tx": tx,
            "kind": "pack", "source": source, "expires_at": expiry,
        }
        self._acc(holder).packs.append(_PackGrant(
            grant_id=payment_id, remaining=int(units),
            expires_at=expiry, source=source or "pack"))
        return CreditResult(True, "", int(units))

    def _grant_pending(self, holder: str, payment_id: str, rec: dict[str, Any],
                       expires_at: str, source: str) -> CreditResult:
        units = _grantable(rec)
        expiry = expires_at or LEGACY_EXPIRY
        rec.pop("pending", None)
        rec.update({"holder": holder, "expires_at": expiry})
        if units < 1:
            return CreditResult(False, "refunded", 0)
        grant = _PackGrant(grant_id=payment_id, remaining=units, expires_at=expiry,
                           source=source or rec.get("source") or "pack")
        if rec.get("hold"):
            grant.remaining, grant.held, grant.hold_id = 0, units, str(rec["hold"])
            rec["held"] = units
        self._acc(holder).packs.append(grant)
        return CreditResult(True, "", units)

    def expect(self, payment_id: str, units: int, tx: str,
               source: str = "pack") -> CreditResult:
        """Record a paid pack that has no holder yet. `credit` grants it at claim.

        Idempotent on payment_id; a claim already credited is left alone. `tx`
        is the Stripe PaymentIntent id, so a refund or a dispute that arrives
        before claim can still find this purchase.
        """
        if payment_id in self.payments:
            return CreditResult(False, "replay", int(self.payments[payment_id].get("units") or 0))
        if units < 1:
            return CreditResult(False, "zero", 0)
        self.payments[payment_id] = {
            "holder": "", "units": int(units), "tx": tx, "kind": "pack",
            "source": source, "pending": True,
        }
        return CreditResult(True, "pending", int(units))

    def payment(self, payment_id: str) -> dict[str, Any] | None:
        rec = self.payments.get(payment_id)
        return dict(rec) if rec is not None else None

    def _pack_claim(self, tx: str) -> tuple[str, dict[str, Any]] | None:
        if not tx:
            return None
        for payment_id, rec in self.payments.items():
            if rec.get("kind") == "pack" and rec.get("tx") == tx:
                return payment_id, rec
        return None

    def _grant(self, grant_id: str) -> _PackGrant | None:
        """The grant wherever it now lives. Rotation moves accounts, not ids."""
        for acc in self.accounts.values():
            for grant in acc.packs:
                if grant.grant_id == grant_id:
                    return grant
        return None

    def refund(self, tx: str, amount: int, amount_refunded: int, full: bool,
               now: str = "") -> ReversalResult:
        """Take back the refunded share of this pack's unspent credits.

        `amount_refunded` is the Charge's running total, so the share is a
        target, not an increment: a replayed or re-sent event removes nothing
        more. Credits already spent (or reserved by a request in flight) are
        not clawed back; they are reported as `already_spent`, and a reserved
        request released afterwards returns its credits to the refund, not to
        the key.
        """
        clock = now or _now_iso()
        found = self._pack_claim(tx)
        if found is None:
            return ReversalResult(False)
        payment_id, rec = found
        purchased = int(rec.get("units") or 0)
        target = refunded_share(purchased, int(amount), int(amount_refunded), bool(full))
        before = int(rec.get("refunded") or 0)
        pending = bool(rec.get("pending"))
        delta = target - before
        if delta <= 0:
            return ReversalResult(True, payment_id, pending, purchased, before)
        rec["refunded"] = target
        if pending:
            removable = max(0, purchased - before - int(rec.get("forfeited") or 0))
            return ReversalResult(True, payment_id, True, purchased, target,
                                  removed=min(delta, removable))
        grant = self._grant(payment_id)
        expired = 0
        removed = 0
        if grant is not None and _expired(grant.expires_at, clock):
            expired = min(delta, grant.remaining + grant.held)
            grant.remaining = grant.held = 0
        elif grant is not None:
            removed = min(delta, grant.remaining)
            grant.remaining -= removed
            from_held = min(delta - removed, grant.held)
            grant.held -= from_held
            removed += from_held
        elif _expired(str(rec.get("expires_at") or LEGACY_EXPIRY), clock):
            expired = delta
        spent = delta - removed - expired
        if spent:
            rec["owed"] = int(rec.get("owed") or 0) + spent
        return ReversalResult(True, payment_id, False, purchased, target,
                              removed=removed, already_spent=spent, expired=expired)

    def hold(self, tx: str, dispute_id: str, now: str = "") -> ReversalResult:
        """Freeze this pack's unspent credits while `dispute_id` is open."""
        found = self._pack_claim(tx)
        if found is None:
            return ReversalResult(False)
        payment_id, rec = found
        purchased = int(rec.get("units") or 0)
        pending = bool(rec.get("pending"))
        if rec.get("hold") or dispute_id in (rec.get("closed_disputes") or []):
            return ReversalResult(True, payment_id, pending, purchased)
        rec["hold"] = dispute_id
        if pending:
            rec["held"] = _grantable(rec)
            return ReversalResult(True, payment_id, True, purchased, held=rec["held"])
        grant = self._grant(payment_id)
        if grant is None:
            return ReversalResult(True, payment_id, False, purchased)
        units = grant.remaining
        grant.held += units
        grant.remaining = 0
        grant.hold_id = dispute_id
        rec["held"] = grant.held
        return ReversalResult(True, payment_id, False, purchased, held=units)

    def end_hold(self, tx: str, dispute_id: str, restore: bool,
                 now: str = "") -> ReversalResult:
        """Close `dispute_id`: give the held credits back, or forfeit them."""
        clock = now or _now_iso()
        found = self._pack_claim(tx)
        if found is None:
            return ReversalResult(False)
        payment_id, rec = found
        purchased = int(rec.get("units") or 0)
        pending = bool(rec.get("pending"))
        closed = list(rec.get("closed_disputes") or [])
        if dispute_id not in closed:
            closed.append(dispute_id)
        rec["closed_disputes"] = closed
        if rec.get("hold") != dispute_id:
            return ReversalResult(True, payment_id, pending, purchased)
        rec.pop("hold", None)
        if pending:
            # A refund since the hold may have shrunk what claim would grant.
            units = min(int(rec.pop("held", 0) or 0), _grantable(rec))
            if restore:
                return ReversalResult(True, payment_id, True, purchased, restored=units)
            rec["forfeited"] = int(rec.get("forfeited") or 0) + units
            return ReversalResult(True, payment_id, True, purchased, forfeited=units)
        rec.pop("held", None)
        grant = self._grant(payment_id)
        if grant is None:
            return ReversalResult(True, payment_id, False, purchased)
        units = grant.held
        grant.held = 0
        grant.hold_id = ""
        if not restore:
            rec["forfeited"] = int(rec.get("forfeited") or 0) + units
            return ReversalResult(True, payment_id, False, purchased, forfeited=units)
        if _expired(grant.expires_at, clock):
            return ReversalResult(True, payment_id, False, purchased, expired=units)
        grant.remaining += units
        return ReversalResult(True, payment_id, False, purchased, restored=units)

    def set_monthly(self, holder: str, units: int, invoice_id: str,
                    plan: str = "", customer_id: str = "",
                    reset_overage: bool = True) -> CreditResult:
        """SET remaining monthly allowance. Reset, no rollover. Idempotent on invoice_id.

        A new invoice zeroes overage used this period unless `reset_overage` is
        false. A subscription update refills the allowance and leaves the cap.
        A replay does not, so a repeated webhook cannot hand the cap back.
        """
        rec = self.payments.get(invoice_id)
        if rec is not None:
            reason = "replay" if rec.get("holder") == holder else "conflict"
            return CreditResult(False, reason, int(rec.get("units") or 0))
        if units < 0:
            return CreditResult(False, "zero", 0)
        self.payments[invoice_id] = {
            "holder": holder, "units": int(units), "tx": invoice_id,
            "kind": "monthly", "plan": plan,
        }
        acc = self._acc(holder)
        acc.monthly = int(units)
        if reset_overage:
            acc.overage_used = 0
        if plan:
            acc.plan = plan
        if customer_id:
            acc.stripe_customer_id = customer_id
        return CreditResult(True, "", int(units))

    def clear_monthly(self, holder: str) -> CreditResult:
        """Zero the monthly allowance and stop overage. Pack grants are untouched."""
        acc = self._acc(holder)
        acc.monthly = 0
        acc.overage_used = 0
        acc.plan = ""
        return CreditResult(True, "cleared", 0)

    def transfer(self, src: str, dst: str) -> bool:
        """Move an account to a new holder (key rotation)."""
        if not src or src == dst:
            return False
        acc = self.accounts.pop(src, None)
        if acc is None:
            return False
        for rec in self.payments.values():
            if rec.get("holder") == src:
                rec["holder"] = dst
        existing = self.accounts.get(dst)
        if existing is None:
            _stamp_backlog_id(acc)
            self.accounts[dst] = acc
            return True
        existing.monthly += acc.monthly
        existing.reserved += acc.reserved
        existing.packs.extend(acc.packs)
        offset = existing.next_res
        for rid, reservation in acc.reservations.items():
            existing.reservations[offset + rid] = reservation
        existing.next_res = offset + acc.next_res
        if acc.plan and not existing.plan:
            existing.plan = acc.plan
        existing.overage_used += acc.overage_used
        if acc.stripe_customer_id and not existing.stripe_customer_id:
            existing.stripe_customer_id = acc.stripe_customer_id
        if not existing.read_day or (acc.read_day and acc.read_day > existing.read_day):
            existing.read_day = acc.read_day
            existing.read_count = acc.read_count
            existing.reads_in_block = acc.reads_in_block
        elif acc.read_day and acc.read_day == existing.read_day:
            existing.read_count += acc.read_count
            existing.reads_in_block = 0
        if not existing.read_minute or (acc.read_minute and acc.read_minute > existing.read_minute):
            existing.read_minute = acc.read_minute
            existing.read_burst = acc.read_burst
        elif acc.read_minute and acc.read_minute == existing.read_minute:
            existing.read_burst += acc.read_burst
        read_offset = existing.next_read
        for token, taken in acc.taken_reads.items():
            existing.taken_reads[read_offset + token] = taken
        existing.next_read = read_offset + max(acc.next_read, 1)
        _move_meter_tail(existing, acc)
        return True

    def reserve(self, holder: str, units: int = 1, now: str = "",
                overage_cap: int = 0) -> ReserveResult:
        clock = now or _now_iso()
        acc = self._acc(holder)
        acc.drop_expired(clock)
        available = acc.available_at(clock)
        room = 0
        cap = int(overage_cap)
        if cap > 0 and not str(acc.stripe_customer_id or "").strip():
            cap = 0
        if cap > 0:
            room = max(0, cap - acc.overage_used - acc.overage_open())
        if units < 1 or available + room < units:
            return ReserveResult(False, None, available, acc.reserved)
        from_monthly = min(acc.monthly, units)
        acc.monthly -= from_monthly
        remaining = units - from_monthly
        pack_draws: list[tuple[str, int]] = []
        if remaining:
            ordered = sorted(acc.live_packs(clock),
                             key=lambda g: (g.expires_at, g.grant_id))
            for grant in ordered:
                if remaining <= 0:
                    break
                take = min(grant.remaining, remaining)
                if take <= 0:
                    continue
                grant.remaining -= take
                pack_draws.append((grant.grant_id, take))
                remaining -= take
            acc.drop_expired(clock)
        if remaining > room:
            acc.monthly += from_monthly
            for grant_id, take in pack_draws:
                for grant in acc.packs:
                    if grant.grant_id == grant_id:
                        grant.remaining += take
                        break
            return ReserveResult(False, None, acc.available_at(clock), acc.reserved)
        overage = remaining
        prepaid = units - overage
        acc.reserved += prepaid
        rid = acc.next_res
        acc.next_res += 1
        acc.reservations[rid] = _Reservation(units, from_monthly, pack_draws, overage)
        return ReserveResult(True, rid, acc.available_at(clock), acc.reserved)

    def commit(self, holder: str, reservation_id: int) -> CommitResult:
        acc = self._acc(holder)
        reservation = acc.reservations.pop(int(reservation_id), None)
        if reservation is None:
            return CommitResult(False)
        acc.reserved -= reservation.units - reservation.overage
        if acc.reserved < 0:
            acc.reserved = 0
        acc.overage_used += reservation.overage
        return CommitResult(True, reservation.overage)

    def release(self, holder: str, reservation_id: int) -> bool:
        acc = self._acc(holder)
        reservation = acc.reservations.pop(int(reservation_id), None)
        if reservation is None:
            return False
        acc.reserved -= reservation.units - reservation.overage
        acc.monthly += reservation.monthly
        # A refund that found these credits reserved counted them as spent
        # (`owed`); released, they are the refund's, not the key's.
        self._return_packs(acc, list(reservation.packs))
        if acc.reserved < 0:
            acc.reserved = 0
        return True

    def balance(self, holder: str, now: str = "") -> Balance:
        clock = now or _now_iso()
        acc = self.accounts.get(holder) or _Account()
        acc.drop_expired(clock)
        live = acc.live_packs(clock)
        packs = sum(g.remaining for g in live)
        return Balance(
            holder,
            acc.available_at(clock),
            acc.reserved,
            acc.monthly,
            packs,
            tuple(PackGrantView(g.grant_id, g.remaining, g.expires_at, g.source)
                  for g in live),
            acc.plan,
            acc.overage_used,
            acc.stripe_customer_id,
            acc.overage_unreported,
        )

    def _return_packs(self, acc: _Account, packs: list[tuple[str, int]]) -> None:
        by_id = {g.grant_id: g for g in acc.packs}
        for grant_id, amount in packs:
            rec = self.payments.get(grant_id) or {}
            owed = int(rec.get("owed") or 0)
            if owed:
                absorbed = min(owed, amount)
                rec["owed"] = owed - absorbed
                amount -= absorbed
            if amount <= 0:
                continue
            grant = by_id.get(grant_id)
            if grant is None:
                grant = _PackGrant(
                    grant_id=grant_id, remaining=0,
                    expires_at=str(rec.get("expires_at") or LEGACY_EXPIRY),
                    source=str(rec.get("source") or "pack"),
                    hold_id=str(rec.get("hold") or ""))
                acc.packs.append(grant)
                by_id[grant_id] = grant
            if grant.hold_id:
                grant.held += amount
                rec["held"] = grant.held
            else:
                grant.remaining += amount

    def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                  burst_limit: int, now: str = "", overage_cap: int = 0) -> ReadResult:
        """Count a catalog read and charge its block credit in this one step.

        The 1st, 11th, 21st… successful read draws one credit. A refusal does
        not count and does not draw. `release_read` undoes this take if the
        response then fails. Undo tickets from a previous UTC day are dropped
        here, without refunding them. The isolate that took them is gone.
        """
        clock = now or _now_iso()
        acc = self._acc(holder)
        day = clock[:10]
        minute = clock[:16]
        for token in [token for token, taken in acc.taken_reads.items()
                      if taken.day < day]:
            acc.taken_reads.pop(token, None)
        if acc.read_day != day:
            acc.read_day = day
            acc.read_count = 0
        if acc.read_minute != minute:
            acc.read_minute = minute
            acc.read_burst = 0
        available = acc.available_at(clock)
        if acc.read_count >= daily_cap:
            return ReadResult(False, "daily", available=available,
                              read_count=acc.read_count, read_burst=acc.read_burst,
                              daily_cap=daily_cap, burst_limit=burst_limit)
        if acc.read_burst >= burst_limit:
            return ReadResult(False, "burst", available=available,
                              read_count=acc.read_count, read_burst=acc.read_burst,
                              daily_cap=daily_cap, burst_limit=burst_limit)
        block_before = acc.reads_in_block
        monthly_drawn = 0
        pack_draws: list[tuple[str, int]] = []
        overage = 0
        if acc.reads_in_block == 0:
            reserved = self.reserve(holder, 1, now=clock, overage_cap=overage_cap)
            if not reserved.ok or reserved.reservation_id is None:
                return ReadResult(False, "exhausted", available=reserved.available,
                                  read_count=acc.read_count, read_burst=acc.read_burst,
                                  daily_cap=daily_cap, burst_limit=burst_limit)
            reservation = acc.reservations[reserved.reservation_id]
            monthly_drawn = reservation.monthly
            pack_draws = list(reservation.packs)
            settled = self.commit(holder, reserved.reservation_id)
            if not settled.ok:
                return ReadResult(False, "exhausted", available=acc.available_at(clock),
                                  read_count=acc.read_count, read_burst=acc.read_burst,
                                  daily_cap=daily_cap, burst_limit=burst_limit)
            overage = settled.overage
            available = acc.available_at(clock)
        acc.read_count += 1
        acc.read_burst += 1
        acc.reads_in_block += 1
        if reads_per_credit > 0 and acc.reads_in_block >= reads_per_credit:
            acc.reads_in_block = 0
        token = acc.next_read
        acc.next_read += 1
        acc.taken_reads[token] = _TakenRead(
            day, minute, overage, monthly_drawn, pack_draws,
            block_before, acc.reads_in_block)
        return ReadResult(True, token=token, available=available, overage=overage,
                          read_count=acc.read_count, read_burst=acc.read_burst,
                          daily_cap=daily_cap, burst_limit=burst_limit)

    def release_read(self, holder: str, token: int) -> bool:
        """Undo one taken read: decrement its count and return a charged credit."""
        acc = self.accounts.get(holder)
        if acc is None:
            return False
        taken = acc.taken_reads.pop(int(token), None)
        if taken is None:
            return False
        if acc.read_day == taken.day and acc.read_count > 0:
            acc.read_count -= 1
        if acc.read_minute == taken.minute and acc.read_burst > 0:
            acc.read_burst -= 1
        if acc.reads_in_block == taken.block_after:
            acc.reads_in_block = taken.block_before
        acc.monthly += taken.monthly
        if taken.overage:
            acc.overage_used = max(0, acc.overage_used - taken.overage)
        self._return_packs(acc, list(taken.packs))
        return True

    def keep_read(self, holder: str, token: int) -> bool:
        """The response succeeded. Drop the undo ticket; the count stays."""
        acc = self.accounts.get(holder)
        if acc is None:
            return False
        return acc.taken_reads.pop(int(token), None) is not None

    def note_unreported(self, holder: str, units: int, identifier: str,
                        customer_id: str = "", event_name: str = "") -> bool:
        """Add `units` to the account's one unreported-overage total.

        The Stripe customer and the meter event name already live on the
        account and the tier table. `identifier` is the event that failed.
        A non-positive amount or a blank identifier adds nothing. The settled
        overage itself stays spent.
        """
        amount = int(units)
        if amount < 1 or not str(identifier or "").strip():
            return False
        acc = self._acc(holder)
        acc.overage_unreported += amount
        return True

    def meter_identifier(self, holder: str, kind: str, counter: str | int) -> str:
        """`{meter_id}:{kind}:{counter}`. Generate `meter_id` on first use and store it.

        The id is `m_` plus 32 hex characters from `secrets.token_hex`. It is
        not derived from the holder, the key, or the Stripe customer. A later
        call for the same account reuses the stored id. A blank kind or
        counter returns `""` and stores nothing.
        """
        label = str(kind or "").strip()
        token = str(counter).strip()
        if not label or token == "":
            return ""
        return f"{_ensure_meter_id(self._acc(holder))}:{label}:{token}"

    def open_backlog(self, holder: str) -> tuple[int, int, str]:
        """Units to send, the backlog `n`, and the stored identifier.

        The first call snapshots `overage_unreported` into
        `overage_backlog_open` and stores `{meter_id}:backlog:{n}`. Until
        `ack_backlog`, a later call repeats that snapshot, so a retry uses
        the same identifier and the same value after the holder is renamed.
        An identifier already stored is not rewritten.
        """
        acc = self.accounts.get(holder)
        if acc is None:
            return 0, 0, ""
        if acc.overage_backlog_open > 0:
            _stamp_backlog_id(acc)
            return acc.overage_backlog_open, acc.overage_backlog_n, acc.overage_backlog_id
        if acc.overage_unreported < 1:
            return 0, 0, ""
        acc.overage_backlog_open = acc.overage_unreported
        acc.overage_backlog_id = f"{_ensure_meter_id(acc)}:backlog:{acc.overage_backlog_n}"
        return acc.overage_backlog_open, acc.overage_backlog_n, acc.overage_backlog_id

    def ack_backlog(self, holder: str, units: int, n: int) -> bool:
        """Stripe accepted the open backlog event for this `n`. Subtract it and advance.

        A late ack whose `n` is no longer the open one does nothing, so it
        cannot clear a later snapshot.
        """
        acc = self.accounts.get(holder)
        if acc is None or acc.overage_backlog_open < 1:
            return False
        if int(n) != acc.overage_backlog_n:
            return False
        amount = min(int(units), acc.overage_backlog_open, acc.overage_unreported)
        if amount < 1:
            return False
        acc.overage_unreported -= amount
        acc.overage_backlog_open = 0
        acc.overage_backlog_n += 1
        acc.overage_backlog_id = ""
        return True

    def note_uncertain(self, holder: str, units: int, identifier: str,
                       created_at: int | None = None) -> bool:
        """Keep one meter event whose outcome Stripe may already have recorded.

        The list holds at most `UNCERTAIN_METER_CAP` entries. Past that, the
        units go to `overage_unreconciled` and nothing sends them.
        `created_at` is unix seconds. Omit it and the entry is created now.
        """
        amount = int(units)
        ident = str(identifier or "").strip()
        if amount < 1 or not ident:
            return False
        return _append_uncertain(self._acc(holder), ident, amount, created_at)

    def list_uncertain(self, holder: str) -> list[tuple[str, int, int]]:
        acc = self.accounts.get(holder)
        if acc is None:
            return []
        return list(acc.overage_uncertain)

    def ack_uncertain(self, holder: str, identifier: str) -> bool:
        """Stripe accepted this identifier (2xx or a duplicate). Drop that entry."""
        acc = self.accounts.get(holder)
        if acc is None:
            return False
        ident = str(identifier or "")
        kept = [row for row in acc.overage_uncertain if row[0] != ident]
        if len(kept) == len(acc.overage_uncertain):
            return False
        acc.overage_uncertain = kept
        return True

    def age_uncertain(self, holder: str, now: int = 0) -> list[tuple[str, int, int]]:
        """Move entries older than 20 hours to `overage_unreconciled`. Return the rest.

        `now` is unix seconds. Zero uses the clock. An entry created exactly
        20 hours ago is still young enough to retry.
        """
        acc = self.accounts.get(holder)
        if acc is None:
            return []
        clock = int(now) if int(now) else _unix_now()
        fresh: list[tuple[str, int, int]] = []
        for ident, units, created_at in acc.overage_uncertain:
            if clock - int(created_at) > UNCERTAIN_MAX_AGE_SECONDS:
                acc.overage_unreconciled += units
            else:
                fresh.append((ident, units, created_at))
        acc.overage_uncertain = fresh
        return list(fresh)

    def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        """A retry got a definite non-duplicate 4xx. Drop it for a person to check.

        Stripe rejected this retry. The original send might still have landed,
        so the units go to `overage_unreconciled` and nothing sends them again.
        """
        acc = self.accounts.get(holder)
        if acc is None:
            return False
        ident = str(identifier or "")
        kept: list[tuple[str, int, int]] = []
        moved = 0
        for row in acc.overage_uncertain:
            if row[0] == ident:
                moved += row[1]
            else:
                kept.append(row)
        if moved < 1:
            return False
        acc.overage_uncertain = kept
        acc.overage_unreconciled += moved
        return True

    def seen(self, payment_id: str) -> bool:
        return payment_id in self.payments

    def to_json(self) -> dict[str, Any]:
        return {
            "accounts": {name: acc.to_json() for name, acc in self.accounts.items()},
            "payments": self.payments,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any] | None) -> LedgerState:
        data = data or {}
        raw_accounts = data.get("accounts") or {}
        accounts = {name: _Account.from_json(raw)
                    for name, raw in raw_accounts.items() if isinstance(raw, dict)}
        payments = dict(data.get("payments") or {})
        state = cls(accounts, payments)
        for name, raw in raw_accounts.items():
            if not isinstance(raw, dict):
                continue
            pending = raw.get("pending_reads") or {}
            if not isinstance(pending, dict):
                continue
            for row in pending.values():
                if isinstance(row, dict) and row.get("reservation_id") is not None:
                    state.release(name, int(row["reservation_id"]))
        return state


class Ledger(Protocol):
    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult: ...

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          reset_overage: bool = True) -> CreditResult: ...

    async def clear_monthly(self, holder: str) -> CreditResult: ...

    async def transfer(self, src: str, dst: str) -> bool: ...

    async def reserve(self, holder: str, units: int = 1, now: str = "",
                      overage_cap: int = 0) -> ReserveResult: ...

    async def commit(self, holder: str, reservation_id: int) -> CommitResult: ...

    async def release(self, holder: str, reservation_id: int) -> bool: ...

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> ReadResult: ...

    async def release_read(self, holder: str, token: int) -> bool: ...

    async def keep_read(self, holder: str, token: int) -> bool: ...

    async def meter_identifier(self, holder: str, kind: str,
                               counter: str | int) -> str: ...

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool: ...

    async def open_backlog(self, holder: str) -> tuple[int, int, str]: ...

    async def ack_backlog(self, holder: str, units: int, n: int) -> bool: ...

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int | None = None) -> bool: ...

    async def list_uncertain(self, holder: str) -> list[tuple[str, int, int]]: ...

    async def ack_uncertain(self, holder: str, identifier: str) -> bool: ...

    async def age_uncertain(self, holder: str, now: int = 0) -> list[tuple[str, int, int]]: ...

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool: ...

    async def balance(self, holder: str, now: str = "") -> Balance: ...

    async def seen(self, payment_id: str) -> bool: ...

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> CreditResult: ...

    async def payment(self, payment_id: str) -> dict[str, Any] | None: ...

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> ReversalResult: ...

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> ReversalResult: ...

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> ReversalResult: ...


class MemoryLedger:
    """In-process stand-in. One lock, the same serial semantics as the Durable Object."""

    def __init__(self, state: LedgerState | None = None) -> None:
        self.state = state or LedgerState()
        self._lock = asyncio.Lock()

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult:
        async with self._lock:
            return self.state.credit(holder, payment_id, units, tx,
                                     expires_at=expires_at, source=source)

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          reset_overage: bool = True) -> CreditResult:
        async with self._lock:
            return self.state.set_monthly(
                holder, units, invoice_id, plan, customer_id, reset_overage)

    async def clear_monthly(self, holder: str) -> CreditResult:
        async with self._lock:
            return self.state.clear_monthly(holder)

    async def transfer(self, src: str, dst: str) -> bool:
        async with self._lock:
            return self.state.transfer(src, dst)

    async def reserve(self, holder: str, units: int = 1, now: str = "",
                      overage_cap: int = 0) -> ReserveResult:
        async with self._lock:
            return self.state.reserve(holder, units, now=now, overage_cap=overage_cap)

    async def commit(self, holder: str, reservation_id: int) -> CommitResult:
        async with self._lock:
            return self.state.commit(holder, reservation_id)

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> ReadResult:
        async with self._lock:
            return self.state.take_read(
                holder, reads_per_credit, daily_cap, burst_limit, now, overage_cap)

    async def release_read(self, holder: str, token: int) -> bool:
        async with self._lock:
            return self.state.release_read(holder, token)

    async def keep_read(self, holder: str, token: int) -> bool:
        async with self._lock:
            return self.state.keep_read(holder, token)

    async def meter_identifier(self, holder: str, kind: str,
                               counter: str | int) -> str:
        async with self._lock:
            return self.state.meter_identifier(holder, kind, counter)

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool:
        async with self._lock:
            return self.state.note_unreported(
                holder, units, identifier, customer_id, event_name)

    async def open_backlog(self, holder: str) -> tuple[int, int, str]:
        async with self._lock:
            return self.state.open_backlog(holder)

    async def ack_backlog(self, holder: str, units: int, n: int) -> bool:
        async with self._lock:
            return self.state.ack_backlog(holder, units, n)

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int | None = None) -> bool:
        async with self._lock:
            return self.state.note_uncertain(holder, units, identifier, created_at)

    async def list_uncertain(self, holder: str) -> list[tuple[str, int, int]]:
        async with self._lock:
            return self.state.list_uncertain(holder)

    async def ack_uncertain(self, holder: str, identifier: str) -> bool:
        async with self._lock:
            return self.state.ack_uncertain(holder, identifier)

    async def age_uncertain(self, holder: str, now: int = 0) -> list[tuple[str, int, int]]:
        async with self._lock:
            return self.state.age_uncertain(holder, now)

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        async with self._lock:
            return self.state.unreconcile_uncertain(holder, identifier)

    async def release(self, holder: str, reservation_id: int) -> bool:
        async with self._lock:
            return self.state.release(holder, reservation_id)

    async def balance(self, holder: str, now: str = "") -> Balance:
        async with self._lock:
            return self.state.balance(holder, now=now)

    async def seen(self, payment_id: str) -> bool:
        async with self._lock:
            return self.state.seen(payment_id)

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> CreditResult:
        async with self._lock:
            return self.state.expect(payment_id, units, tx, source)

    async def payment(self, payment_id: str) -> dict[str, Any] | None:
        async with self._lock:
            return self.state.payment(payment_id)

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> ReversalResult:
        async with self._lock:
            return self.state.refund(tx, amount, amount_refunded, full, now=now)

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> ReversalResult:
        async with self._lock:
            return self.state.hold(tx, dispute_id, now=now)

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> ReversalResult:
        async with self._lock:
            return self.state.end_hold(tx, dispute_id, restore, now=now)


class UnboundLedger:
    """No Durable Object on this deployment. Reads as empty; writes refuse."""

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          reset_overage: bool = True) -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def clear_monthly(self, holder: str) -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def transfer(self, src: str, dst: str) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def reserve(self, holder: str, units: int = 1, now: str = "",
                      overage_cap: int = 0) -> ReserveResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def commit(self, holder: str, reservation_id: int) -> CommitResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> ReadResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def release_read(self, holder: str, token: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def keep_read(self, holder: str, token: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def meter_identifier(self, holder: str, kind: str,
                               counter: str | int) -> str:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def open_backlog(self, holder: str) -> tuple[int, int, str]:
        return 0, 0, ""

    async def ack_backlog(self, holder: str, units: int, n: int) -> bool:
        return False

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int | None = None) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def list_uncertain(self, holder: str) -> list[tuple[str, int, int]]:
        return []

    async def ack_uncertain(self, holder: str, identifier: str) -> bool:
        return False

    async def age_uncertain(self, holder: str, now: int = 0) -> list[tuple[str, int, int]]:
        return []

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        return False

    async def release(self, holder: str, reservation_id: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def balance(self, holder: str, now: str = "") -> Balance:
        return Balance(holder, 0, 0)

    async def seen(self, payment_id: str) -> bool:
        return False

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def payment(self, payment_id: str) -> dict[str, Any] | None:
        return None

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> ReversalResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> ReversalResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> ReversalResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")


class DurableLedger:
    """RPC adapter over the `CREDITS` Durable Object binding.

    One instance, named `ledger`. The object is single-threaded, which is the
    concurrency guarantee: every credit, reserve, commit and release runs in
    order. See `credits_do.CreditsObject`.
    """

    def __init__(self, namespace: Any) -> None:
        self._stub = namespace.get(namespace.idFromName("ledger"))

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult:
        data = await self._stub.credit(
            holder, payment_id, int(units), tx, expires_at, source)
        return CreditResult.from_json(dict(data))

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "", customer_id: str = "",
                          reset_overage: bool = True) -> CreditResult:
        data = await self._stub.set_monthly(
            holder, int(units), invoice_id, plan, customer_id, bool(reset_overage))
        return CreditResult.from_json(dict(data))

    async def clear_monthly(self, holder: str) -> CreditResult:
        data = await self._stub.clear_monthly(holder)
        return CreditResult.from_json(dict(data))

    async def transfer(self, src: str, dst: str) -> bool:
        return bool(await self._stub.transfer(src, dst))

    async def reserve(self, holder: str, units: int = 1, now: str = "",
                      overage_cap: int = 0) -> ReserveResult:
        data = await self._stub.reserve(holder, int(units), now, int(overage_cap))
        return ReserveResult.from_json(dict(data))

    async def commit(self, holder: str, reservation_id: int) -> CommitResult:
        data = await self._stub.commit(holder, int(reservation_id))
        return CommitResult.from_json(data)

    async def take_read(self, holder: str, reads_per_credit: int, daily_cap: int,
                        burst_limit: int, now: str = "",
                        overage_cap: int = 0) -> ReadResult:
        data = await self._stub.take_read(
            holder, int(reads_per_credit), int(daily_cap), int(burst_limit),
            now, int(overage_cap))
        return ReadResult.from_json(dict(data))

    async def release_read(self, holder: str, token: int) -> bool:
        return bool(await self._stub.release_read(holder, int(token)))

    async def keep_read(self, holder: str, token: int) -> bool:
        return bool(await self._stub.keep_read(holder, int(token)))

    async def meter_identifier(self, holder: str, kind: str,
                               counter: str | int) -> str:
        return str(await self._stub.meter_identifier(
            holder, str(kind), str(counter)) or "")

    async def note_unreported(self, holder: str, units: int, identifier: str,
                              customer_id: str = "", event_name: str = "") -> bool:
        return bool(await self._stub.note_unreported(
            holder, int(units), identifier, customer_id, event_name))

    async def open_backlog(self, holder: str) -> tuple[int, int, str]:
        data = await self._stub.open_backlog(holder)
        to_py = getattr(data, "to_py", None)
        row = to_py() if callable(to_py) else data
        units, seq, ident = row
        return int(units), int(seq), str(ident or "")

    async def ack_backlog(self, holder: str, units: int, n: int) -> bool:
        return bool(await self._stub.ack_backlog(holder, int(units), int(n)))

    async def note_uncertain(self, holder: str, units: int, identifier: str,
                             created_at: int | None = None) -> bool:
        return bool(await self._stub.note_uncertain(
            holder, int(units), identifier, int(created_at or 0)))

    async def list_uncertain(self, holder: str) -> list[tuple[str, int, int]]:
        data = await self._stub.list_uncertain(holder)
        return _uncertain_wire(data)

    async def ack_uncertain(self, holder: str, identifier: str) -> bool:
        return bool(await self._stub.ack_uncertain(holder, identifier))

    async def age_uncertain(self, holder: str, now: int = 0) -> list[tuple[str, int, int]]:
        data = await self._stub.age_uncertain(holder, int(now or 0))
        return _uncertain_wire(data)

    async def unreconcile_uncertain(self, holder: str, identifier: str) -> bool:
        return bool(await self._stub.unreconcile_uncertain(holder, identifier))

    async def release(self, holder: str, reservation_id: int) -> bool:
        return bool(await self._stub.release(holder, int(reservation_id)))

    async def balance(self, holder: str, now: str = "") -> Balance:
        data = await self._stub.balance(holder, now)
        return Balance.from_json(dict(data))

    async def seen(self, payment_id: str) -> bool:
        return bool(await self._stub.seen(payment_id))

    async def expect(self, payment_id: str, units: int, tx: str,
                     source: str = "pack") -> CreditResult:
        data = await self._stub.expect(payment_id, int(units), tx, source)
        return CreditResult.from_json(dict(data))

    async def payment(self, payment_id: str) -> dict[str, Any] | None:
        data = await self._stub.payment(payment_id)
        if not data:
            return None
        to_py = getattr(data, "to_py", None)
        return dict(to_py() if callable(to_py) else data)

    async def refund(self, tx: str, amount: int, amount_refunded: int,
                     full: bool, now: str = "") -> ReversalResult:
        data = await self._stub.refund(tx, int(amount), int(amount_refunded),
                                       bool(full), now)
        return ReversalResult.from_json(dict(data))

    async def hold(self, tx: str, dispute_id: str, now: str = "") -> ReversalResult:
        data = await self._stub.hold(tx, dispute_id, now)
        return ReversalResult.from_json(dict(data))

    async def end_hold(self, tx: str, dispute_id: str, restore: bool,
                       now: str = "") -> ReversalResult:
        data = await self._stub.end_hold(tx, dispute_id, bool(restore), now)
        return ReversalResult.from_json(dict(data))


def ledger_from_env(env: Any) -> Ledger:
    binding = getattr(env, "CREDITS", None)
    if binding is None:
        return UnboundLedger()
    if isinstance(binding, MemoryLedger):
        return binding
    return DurableLedger(binding)


def holder_from_fingerprint(fingerprint_hex: str) -> str:
    """Same holder id MODEL-75 uses: `key:` plus the SHA-256 of the API key."""
    return "key:" + fingerprint_hex
