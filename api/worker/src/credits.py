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

The unit is a credit.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

LEGACY_EXPIRY = "9999-12-31T00:00:00Z"


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
        )


@dataclass
class _PackGrant:
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

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> _PackGrant:
        return cls(
            str(data.get("grant_id") or ""),
            int(data.get("remaining") or 0),
            str(data.get("expires_at") or LEGACY_EXPIRY),
            str(data.get("source") or "pack"),
        )


@dataclass
class _Reservation:
    units: int
    monthly: int = 0
    packs: list[tuple[str, int]] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "units": self.units,
            "monthly": self.monthly,
            "packs": [[grant_id, amount] for grant_id, amount in self.packs],
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
        )


@dataclass
class _Account:
    monthly: int = 0
    reserved: int = 0
    next_res: int = 1
    reservations: dict[int, _Reservation] = field(default_factory=dict)
    packs: list[_PackGrant] = field(default_factory=list)
    plan: str = ""

    def live_packs(self, now: str) -> list[_PackGrant]:
        return [g for g in self.packs if g.remaining > 0 and not _expired(g.expires_at, now)]

    def pack_remaining(self, now: str) -> int:
        return sum(g.remaining for g in self.live_packs(now))

    def available_at(self, now: str) -> int:
        return max(0, self.monthly) + self.pack_remaining(now)

    def drop_expired(self, now: str) -> None:
        self.packs = [g for g in self.packs if g.remaining > 0 and not _expired(g.expires_at, now)]

    def to_json(self) -> dict[str, Any]:
        return {
            "monthly": self.monthly,
            "available": self.monthly + sum(g.remaining for g in self.packs if g.remaining > 0),
            "reserved": self.reserved,
            "next_res": self.next_res,
            "reservations": {str(k): v.to_json() for k, v in self.reservations.items()},
            "packs": [g.to_json() for g in self.packs],
            "plan": self.plan,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> _Account:
        raw = data.get("reservations") or {}
        reservations = {int(k): _Reservation.from_json(v) for k, v in raw.items()}
        packs = [_PackGrant.from_json(row) for row in (data.get("packs") or [])
                 if isinstance(row, dict)]
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
        """ADD pack credits. Idempotent on payment_id. Same bucket as a card pack."""
        rec = self.payments.get(payment_id)
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

    def set_monthly(self, holder: str, units: int, invoice_id: str,
                    plan: str = "") -> CreditResult:
        """SET remaining monthly allowance. Reset, no rollover. Idempotent on invoice_id."""
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
        if plan:
            acc.plan = plan
        return CreditResult(True, "", int(units))

    def clear_monthly(self, holder: str) -> CreditResult:
        """Zero the monthly allowance. Pack grants are untouched."""
        acc = self._acc(holder)
        acc.monthly = 0
        return CreditResult(True, "cleared", 0)

    def transfer(self, src: str, dst: str) -> bool:
        """Move an account to a new holder (key rotation)."""
        if not src or src == dst:
            return False
        acc = self.accounts.pop(src, None)
        if acc is None:
            return False
        existing = self.accounts.get(dst)
        if existing is None:
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
        return True

    def reserve(self, holder: str, units: int = 1, now: str = "") -> ReserveResult:
        clock = now or _now_iso()
        acc = self._acc(holder)
        acc.drop_expired(clock)
        available = acc.available_at(clock)
        if units < 1 or available < units:
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
        if remaining:
            acc.monthly += from_monthly
            for grant_id, take in pack_draws:
                for grant in acc.packs:
                    if grant.grant_id == grant_id:
                        grant.remaining += take
                        break
            return ReserveResult(False, None, acc.available_at(clock), acc.reserved)
        acc.reserved += units
        rid = acc.next_res
        acc.next_res += 1
        acc.reservations[rid] = _Reservation(units, from_monthly, pack_draws)
        return ReserveResult(True, rid, acc.available_at(clock), acc.reserved)

    def commit(self, holder: str, reservation_id: int) -> bool:
        acc = self._acc(holder)
        reservation = acc.reservations.pop(int(reservation_id), None)
        if reservation is None:
            return False
        acc.reserved -= reservation.units
        if acc.reserved < 0:
            acc.reserved = 0
        return True

    def release(self, holder: str, reservation_id: int) -> bool:
        acc = self._acc(holder)
        reservation = acc.reservations.pop(int(reservation_id), None)
        if reservation is None:
            return False
        acc.reserved -= reservation.units
        acc.monthly += reservation.monthly
        by_id = {g.grant_id: g for g in acc.packs}
        for grant_id, amount in reservation.packs:
            grant = by_id.get(grant_id)
            if grant is None:
                acc.packs.append(_PackGrant(
                    grant_id=grant_id, remaining=amount,
                    expires_at=LEGACY_EXPIRY, source="pack"))
            else:
                grant.remaining += amount
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
        )

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
        accounts = {name: _Account.from_json(raw)
                    for name, raw in (data.get("accounts") or {}).items()}
        payments = dict(data.get("payments") or {})
        return cls(accounts, payments)


class Ledger(Protocol):
    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult: ...

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "") -> CreditResult: ...

    async def clear_monthly(self, holder: str) -> CreditResult: ...

    async def transfer(self, src: str, dst: str) -> bool: ...

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "") -> ReserveResult: ...

    async def commit(self, holder: str, reservation_id: int) -> bool: ...

    async def release(self, holder: str, reservation_id: int) -> bool: ...

    async def balance(self, holder: str, now: str = "") -> Balance: ...

    async def seen(self, payment_id: str) -> bool: ...


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
                          plan: str = "") -> CreditResult:
        async with self._lock:
            return self.state.set_monthly(holder, units, invoice_id, plan)

    async def clear_monthly(self, holder: str) -> CreditResult:
        async with self._lock:
            return self.state.clear_monthly(holder)

    async def transfer(self, src: str, dst: str) -> bool:
        async with self._lock:
            return self.state.transfer(src, dst)

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "") -> ReserveResult:
        async with self._lock:
            return self.state.reserve(holder, units, now=now)

    async def commit(self, holder: str, reservation_id: int) -> bool:
        async with self._lock:
            return self.state.commit(holder, reservation_id)

    async def release(self, holder: str, reservation_id: int) -> bool:
        async with self._lock:
            return self.state.release(holder, reservation_id)

    async def balance(self, holder: str, now: str = "") -> Balance:
        async with self._lock:
            return self.state.balance(holder, now=now)

    async def seen(self, payment_id: str) -> bool:
        async with self._lock:
            return self.state.seen(payment_id)


class UnboundLedger:
    """No Durable Object on this deployment. Reads as empty; writes refuse."""

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str, expires_at: str = "",
                     source: str = "x402") -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def set_monthly(self, holder: str, units: int, invoice_id: str,
                          plan: str = "") -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def clear_monthly(self, holder: str) -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def transfer(self, src: str, dst: str) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "") -> ReserveResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def commit(self, holder: str, reservation_id: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def release(self, holder: str, reservation_id: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def balance(self, holder: str, now: str = "") -> Balance:
        return Balance(holder, 0, 0)

    async def seen(self, payment_id: str) -> bool:
        return False


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
                          plan: str = "") -> CreditResult:
        data = await self._stub.set_monthly(holder, int(units), invoice_id, plan)
        return CreditResult.from_json(dict(data))

    async def clear_monthly(self, holder: str) -> CreditResult:
        data = await self._stub.clear_monthly(holder)
        return CreditResult.from_json(dict(data))

    async def transfer(self, src: str, dst: str) -> bool:
        return bool(await self._stub.transfer(src, dst))

    async def reserve(self, holder: str, units: int = 1,
                      now: str = "") -> ReserveResult:
        data = await self._stub.reserve(holder, int(units), now)
        return ReserveResult.from_json(dict(data))

    async def commit(self, holder: str, reservation_id: int) -> bool:
        return bool(await self._stub.commit(holder, int(reservation_id)))

    async def release(self, holder: str, reservation_id: int) -> bool:
        return bool(await self._stub.release(holder, int(reservation_id)))

    async def balance(self, holder: str, now: str = "") -> Balance:
        data = await self._stub.balance(holder, now)
        return Balance.from_json(dict(data))

    async def seen(self, payment_id: str) -> bool:
        return bool(await self._stub.seen(payment_id))


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
