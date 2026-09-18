"""Prepaid credit ledger (MODEL-75).

Workers KV is eventually consistent and has no compare-and-set, so it cannot
keep a balance non-negative under concurrent requests. This module does not
use it. Mutations go through `LedgerState`, which is serial: `MemoryLedger`
holds an asyncio lock for tests; production wraps the same state in one
Durable Object (`CreditsObject`, `docs/x402.md`).

Two record kinds, both JSON inside the object:

* a balance per holder (`available`, `reserved`)
* a payment claim per payment id (holder, units, settlement tx)

A payment id is credited at most once. Reserve-before-produce is what makes a
4xx/5xx/no-match cost nothing, and what stops two in-flight requests spending
the same last unit.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol


class StoreNotConfigured(RuntimeError):
    """No Durable Object binding. Parallel to access_kv.StoreNotConfigured."""


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
class Balance:
    holder: str
    available: int
    reserved: int

    @property
    def total(self) -> int:
        return self.available + self.reserved

    def to_json(self) -> dict[str, Any]:
        return {"holder": self.holder, "available": self.available,
                "reserved": self.reserved, "total": self.total}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Balance:
        return cls(str(data.get("holder") or ""), int(data.get("available") or 0),
                   int(data.get("reserved") or 0))


@dataclass
class _Account:
    available: int = 0
    reserved: int = 0
    next_res: int = 1
    reservations: dict[int, int] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "reserved": self.reserved,
            "next_res": self.next_res,
            "reservations": {str(k): v for k, v in self.reservations.items()},
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> _Account:
        raw = data.get("reservations") or {}
        reservations = {int(k): int(v) for k, v in raw.items()}
        return cls(int(data.get("available") or 0), int(data.get("reserved") or 0),
                   int(data.get("next_res") or 1), reservations)


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
               tx: str) -> CreditResult:
        rec = self.payments.get(payment_id)
        if rec is not None:
            reason = "replay" if rec.get("holder") == holder else "conflict"
            return CreditResult(False, reason, int(rec.get("units") or 0))
        if units < 1:
            return CreditResult(False, "zero", 0)
        self.payments[payment_id] = {"holder": holder, "units": int(units), "tx": tx}
        self._acc(holder).available += int(units)
        return CreditResult(True, "", int(units))

    def reserve(self, holder: str, units: int = 1) -> ReserveResult:
        acc = self._acc(holder)
        if units < 1 or acc.available < units:
            return ReserveResult(False, None, acc.available, acc.reserved)
        acc.available -= units
        acc.reserved += units
        rid = acc.next_res
        acc.next_res += 1
        acc.reservations[rid] = units
        return ReserveResult(True, rid, acc.available, acc.reserved)

    def commit(self, holder: str, reservation_id: int) -> bool:
        acc = self._acc(holder)
        units = acc.reservations.pop(int(reservation_id), None)
        if units is None:
            return False
        acc.reserved -= units
        if acc.reserved < 0:
            acc.reserved = 0
        return True

    def release(self, holder: str, reservation_id: int) -> bool:
        acc = self._acc(holder)
        units = acc.reservations.pop(int(reservation_id), None)
        if units is None:
            return False
        acc.reserved -= units
        acc.available += units
        if acc.reserved < 0:
            acc.reserved = 0
        return True

    def balance(self, holder: str) -> Balance:
        acc = self.accounts.get(holder) or _Account()
        return Balance(holder, acc.available, acc.reserved)

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
                     tx: str) -> CreditResult: ...

    async def reserve(self, holder: str, units: int = 1) -> ReserveResult: ...

    async def commit(self, holder: str, reservation_id: int) -> bool: ...

    async def release(self, holder: str, reservation_id: int) -> bool: ...

    async def balance(self, holder: str) -> Balance: ...

    async def seen(self, payment_id: str) -> bool: ...


class MemoryLedger:
    """In-process stand-in. One lock, the same serial semantics as the Durable Object."""

    def __init__(self, state: LedgerState | None = None) -> None:
        self.state = state or LedgerState()
        self._lock = asyncio.Lock()

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str) -> CreditResult:
        async with self._lock:
            return self.state.credit(holder, payment_id, units, tx)

    async def reserve(self, holder: str, units: int = 1) -> ReserveResult:
        async with self._lock:
            return self.state.reserve(holder, units)

    async def commit(self, holder: str, reservation_id: int) -> bool:
        async with self._lock:
            return self.state.commit(holder, reservation_id)

    async def release(self, holder: str, reservation_id: int) -> bool:
        async with self._lock:
            return self.state.release(holder, reservation_id)

    async def balance(self, holder: str) -> Balance:
        async with self._lock:
            return self.state.balance(holder)

    async def seen(self, payment_id: str) -> bool:
        async with self._lock:
            return self.state.seen(payment_id)


class UnboundLedger:
    """No Durable Object on this deployment. Reads as empty; writes refuse."""

    async def credit(self, holder: str, payment_id: str, units: int,
                     tx: str) -> CreditResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def reserve(self, holder: str, units: int = 1) -> ReserveResult:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def commit(self, holder: str, reservation_id: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def release(self, holder: str, reservation_id: int) -> bool:
        raise StoreNotConfigured("CREDITS Durable Object is not bound")

    async def balance(self, holder: str) -> Balance:
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
                     tx: str) -> CreditResult:
        data = await self._stub.credit(holder, payment_id, int(units), tx)
        return CreditResult.from_json(dict(data))

    async def reserve(self, holder: str, units: int = 1) -> ReserveResult:
        data = await self._stub.reserve(holder, int(units))
        return ReserveResult.from_json(dict(data))

    async def commit(self, holder: str, reservation_id: int) -> bool:
        return bool(await self._stub.commit(holder, int(reservation_id)))

    async def release(self, holder: str, reservation_id: int) -> bool:
        return bool(await self._stub.release(holder, int(reservation_id)))

    async def balance(self, holder: str) -> Balance:
        data = await self._stub.balance(holder)
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
