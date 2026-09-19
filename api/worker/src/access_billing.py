"""ACCESS records MODEL-73 adds: Stripe events, subscriptions, sessions, keyrefs.

The key itself is stored only as a SHA-256 lookup in `access_keys`. These
records are the billing index on top of that: which Stripe event we have
already applied, which subscription is entitled to which tier, which Checkout
session points at that subscription, and (after claim) which fingerprint the
subscription currently owns.

The webhook never mints a key. Anonymous claim calls `access_keys.issue`,
returns the plaintext once, and writes only the hash. An authenticated Checkout
(the request carried a live key) stores that key's SHA-256 fingerprint on the
session — never the key — and payment credits that key; claim does not mint.
Every `.put` below names a record through one of the `*_name` functions so
`tests/test_legal.py` can see what we write. The privacy statement lists the
same four kinds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Any

import access_keys as keys
import credits
from access_config import AccessPolicy, PolicyError

_EVENT_PREFIX = "event:"
_SESSION_PREFIX = "session:"
_SUB_PREFIX = "sub:"
_KEYREF_PREFIX = "keyref:"

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"


def event_name(event_id: str) -> str:
    return _EVENT_PREFIX + event_id


def session_name(session_id: str) -> str:
    return _SESSION_PREFIX + session_id


def subscription_name(subscription_id: str) -> str:
    return _SUB_PREFIX + subscription_id


def keyref_name(fingerprint_hex: str) -> str:
    return _KEYREF_PREFIX + fingerprint_hex


def _iso(now: datetime) -> str:
    return now.isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    type: str
    action: str
    processed_at: str

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "event",
            "event_id": self.event_id,
            "type": self.type,
            "action": self.action,
            "processed_at": self.processed_at,
        }

    @classmethod
    def from_json(cls, text: str) -> EventRecord:
        data = json.loads(text)
        return cls(event_id=str(data.get("event_id") or ""),
                   type=str(data.get("type") or ""),
                   action=str(data.get("action") or ""),
                   processed_at=str(data.get("processed_at") or ""))


@dataclass(frozen=True)
class SessionRecord:
    """Checkout session → subscription or pack. Claimed once. No key material.

    `key_fingerprint` is the SHA-256 of an existing live key when Checkout was
    authenticated. Empty means the session is anonymous and claim may mint.
    """

    session_id: str
    subscription_id: str
    claimed: bool = False
    product_kind: str = "plan"
    price_id: str = ""
    credits: int = 0
    customer_id: str = ""
    key_fingerprint: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "session",
            "session_id": self.session_id,
            "subscription_id": self.subscription_id,
            "claimed": self.claimed,
            "product_kind": self.product_kind,
            "price_id": self.price_id,
            "credits": self.credits,
            "customer_id": self.customer_id,
            "key_fingerprint": self.key_fingerprint,
        }

    @classmethod
    def from_json(cls, text: str) -> SessionRecord:
        data = json.loads(text)
        return cls(session_id=str(data.get("session_id") or ""),
                   subscription_id=str(data.get("subscription_id") or ""),
                   claimed=bool(data.get("claimed", False)),
                   product_kind=str(data.get("product_kind") or "plan"),
                   price_id=str(data.get("price_id") or ""),
                   credits=int(data.get("credits") or 0),
                   customer_id=str(data.get("customer_id") or ""),
                   key_fingerprint=str(data.get("key_fingerprint") or ""))


@dataclass(frozen=True)
class ClaimResult:
    """What claim did. `issued` is the plaintext, only when a key was minted this call.

    This value is returned to the caller and is never written to ACCESS.
    """

    record: SubscriptionRecord
    issued: str = ""
    minted: bool = False
    consumed: bool = False
    attached: bool = False


@dataclass(frozen=True)
class KeyRef:
    """Fingerprint → subscription, so rotation can find the billing row."""

    fingerprint: str
    subscription_id: str

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "keyref",
            "fingerprint": self.fingerprint,
            "subscription_id": self.subscription_id,
        }

    @classmethod
    def from_json(cls, text: str) -> KeyRef:
        data = json.loads(text)
        return cls(fingerprint=str(data.get("fingerprint") or ""),
                   subscription_id=str(data.get("subscription_id") or ""))


@dataclass(frozen=True)
class SubscriptionRecord:
    """One Stripe subscription and the entitlement it currently carries.

    No key value. After claim, `key_fingerprint` / `key_id` name the issued
    key; until then they are empty and claim is what mints.
    """

    subscription_id: str
    customer_id: str
    price_id: str
    tier: str
    status: str
    key_fingerprint: str
    key_id: str
    created_at: str
    pending_monthly: int = 0
    plan_name: str = ""
    plan_credits: int = 0

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "subscription",
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "price_id": self.price_id,
            "tier": self.tier,
            "status": self.status,
            "key_fingerprint": self.key_fingerprint,
            "key_id": self.key_id,
            "created_at": self.created_at,
            "pending_monthly": self.pending_monthly,
            "plan_name": self.plan_name,
            "plan_credits": self.plan_credits,
        }

    @classmethod
    def from_json(cls, text: str) -> SubscriptionRecord:
        data = json.loads(text)
        return cls(
            subscription_id=str(data.get("subscription_id") or ""),
            customer_id=str(data.get("customer_id") or ""),
            price_id=str(data.get("price_id") or ""),
            tier=str(data.get("tier") or ""),
            status=str(data.get("status") or STATUS_ACTIVE),
            key_fingerprint=str(data.get("key_fingerprint") or ""),
            key_id=str(data.get("key_id") or ""),
            created_at=str(data.get("created_at") or ""),
            pending_monthly=int(data.get("pending_monthly") or 0),
            plan_name=str(data.get("plan_name") or ""),
            plan_credits=int(data.get("plan_credits") or 0),
        )


async def seen(kv: Any, event_id: str) -> bool:
    if not event_id:
        return False
    return await kv.get(event_name(event_id)) is not None


async def remember(kv: Any, event_id: str, type_: str, action: str, *,
                   now: datetime, policy: AccessPolicy) -> None:
    record = EventRecord(event_id=event_id, type=type_, action=action,
                         processed_at=_iso(now))
    ttl = policy.billing.event_ttl_seconds or None
    await kv.put(event_name(event_id), json.dumps(record.to_json()),
                 expiration_ttl=ttl)


async def load_subscription(kv: Any, subscription_id: str) -> SubscriptionRecord | None:
    stored = await kv.get(subscription_name(subscription_id))
    if stored is None:
        return None
    return SubscriptionRecord.from_json(stored)


async def load_session(kv: Any, session_id: str) -> SessionRecord | None:
    stored = await kv.get(session_name(session_id))
    if stored is None:
        return None
    return SessionRecord.from_json(stored)


async def _write_sub(kv: Any, record: SubscriptionRecord) -> None:
    await kv.put(subscription_name(record.subscription_id), json.dumps(record.to_json()))


async def _write_session(kv: Any, record: SessionRecord) -> None:
    await kv.put(session_name(record.session_id), json.dumps(record.to_json()))


async def _write_keyref(kv: Any, fingerprint_hex: str, subscription_id: str) -> None:
    record = KeyRef(fingerprint=fingerprint_hex, subscription_id=subscription_id)
    await kv.put(keyref_name(fingerprint_hex), json.dumps(record.to_json()))


async def _link_session(kv: Any, session_id: str, subscription_id: str, *,
                        price_id: str = "", credits_amount: int = 0,
                        customer_id: str = "", key_fingerprint: str = "") -> None:
    """Point this Checkout session at the subscription. Never un-claim."""
    existing = await load_session(kv, session_id)
    if existing is not None and existing.claimed:
        return
    bound = key_fingerprint or (existing.key_fingerprint if existing else "")
    if (existing is not None and existing.subscription_id == subscription_id
            and not existing.claimed and existing.product_kind != "pack"
            and existing.key_fingerprint == bound):
        return
    await _write_session(kv, SessionRecord(
        session_id=session_id, subscription_id=subscription_id, claimed=False,
        product_kind="plan", price_id=price_id, credits=credits_amount,
        customer_id=customer_id, key_fingerprint=bound))


async def attach_existing_key(kv: Any, *, fingerprint_hex: str,
                              subscription_id: str, tier: str,
                              policy: AccessPolicy) -> keys.KeyRecord | None:
    """Point this subscription at an already-issued key. Does not mint.

    A previous keyref (a pack session, an earlier plan) is detached so
    cancellation of the old row cannot downgrade this key.
    """
    if not fingerprint_hex:
        return None
    record = await keys.lookup_fingerprint(kv, fingerprint_hex)
    if record is None:
        return None
    if record.tier != tier:
        moved = await keys.set_tier(kv, fingerprint_hex, tier, policy=policy)
        if moved is not None:
            record = moved
    ref_raw = await kv.get(keyref_name(fingerprint_hex))
    if ref_raw is not None:
        old = KeyRef.from_json(ref_raw)
        if old.subscription_id and old.subscription_id != subscription_id:
            old_sub = await load_subscription(kv, old.subscription_id)
            if old_sub is not None:
                await _write_sub(kv, replace(old_sub, key_fingerprint="", key_id=""))
    await _write_keyref(kv, fingerprint_hex, subscription_id)
    return record


async def record_entitlement(kv: Any, *, subscription_id: str, customer_id: str,
                             price_id: str, tier: str, session_id: str,
                             now: datetime, policy: AccessPolicy,
                             pending_monthly: int = 0, plan_name: str = "",
                             plan_credits: int = 0, key_fingerprint: str = ""
                             ) -> tuple[str, SubscriptionRecord]:
    """Record (or refresh) the paid entitlement. Does not mint a key.

    A replayed `checkout.session.completed` after `invoice.paid` (or the reverse)
    shares one subscription row. If a session id is present it is linked so
    claim can mint. `pending_monthly` is applied to the ledger at claim if the
    key does not exist yet. `key_fingerprint` binds an already-issued key;
    monthly is then granted on that key rather than waiting for a mint.
    """
    policy.tier(tier)
    existing = await load_subscription(kv, subscription_id)
    if existing is not None:
        action = "already_entitled"
        updated = existing
        bound = key_fingerprint or existing.key_fingerprint
        attached = None
        if bound and not existing.key_fingerprint:
            attached = await attach_existing_key(
                kv, fingerprint_hex=bound, subscription_id=subscription_id,
                tier=tier, policy=policy)
        if existing.tier != tier or existing.status != STATUS_ACTIVE:
            target_fp = bound or existing.key_fingerprint
            if target_fp:
                moved = await keys.set_tier(kv, target_fp, tier, policy=policy)
                if moved is None and attached is None:
                    return "missing_key", existing
            updated = replace(
                existing, tier=tier, status=STATUS_ACTIVE,
                customer_id=customer_id or existing.customer_id,
                price_id=price_id or existing.price_id,
                pending_monthly=pending_monthly or existing.pending_monthly,
                plan_name=plan_name or existing.plan_name,
                plan_credits=plan_credits or existing.plan_credits,
                key_fingerprint=bound or existing.key_fingerprint,
                key_id=(attached.key_id if attached is not None
                        else existing.key_id))
            await _write_sub(kv, updated)
            action = "restored" if existing.tier != tier else "already_entitled"
        else:
            fields: dict[str, Any] = {}
            if customer_id and customer_id != existing.customer_id:
                fields["customer_id"] = customer_id
            if pending_monthly and not (bound or existing.key_fingerprint):
                fields["pending_monthly"] = pending_monthly
            if plan_name:
                fields["plan_name"] = plan_name
            if plan_credits:
                fields["plan_credits"] = plan_credits
            if price_id and price_id != existing.price_id:
                fields["price_id"] = price_id
            if bound and bound != existing.key_fingerprint:
                fields["key_fingerprint"] = bound
            if attached is not None:
                fields["key_id"] = attached.key_id
                fields["key_fingerprint"] = bound
            if fields:
                updated = replace(existing, **fields)
                await _write_sub(kv, updated)
        if session_id:
            await _link_session(
                kv, session_id, subscription_id, price_id=price_id,
                credits_amount=plan_credits, customer_id=customer_id,
                key_fingerprint=bound)
        return action, updated

    stored = SubscriptionRecord(
        subscription_id=subscription_id, customer_id=customer_id, price_id=price_id,
        tier=tier, status=STATUS_ACTIVE, key_fingerprint="", key_id="",
        created_at=_iso(now), pending_monthly=pending_monthly,
        plan_name=plan_name, plan_credits=plan_credits,
    )
    if key_fingerprint:
        attached = await attach_existing_key(
            kv, fingerprint_hex=key_fingerprint, subscription_id=subscription_id,
            tier=tier, policy=policy)
        if attached is not None:
            stored = replace(stored, key_fingerprint=key_fingerprint,
                             key_id=attached.key_id, pending_monthly=0)
    await _write_sub(kv, stored)
    if session_id:
        await _link_session(
            kv, session_id, subscription_id, price_id=price_id,
            credits_amount=plan_credits, customer_id=customer_id,
            key_fingerprint=key_fingerprint)
    return "entitled", stored


async def record_pack_session(kv: Any, *, session_id: str, customer_id: str,
                              price_id: str, credits_amount: int,
                              key_fingerprint: str = "") -> str:
    """Link a one-off Checkout session so claim can mint, or credit a bound key."""
    existing = await load_session(kv, session_id)
    if existing is not None and existing.claimed:
        return "already_claimed"
    if existing is not None and not existing.claimed:
        bound = key_fingerprint or existing.key_fingerprint
        if bound != existing.key_fingerprint or credits_amount != existing.credits:
            await _write_session(kv, replace(
                existing, key_fingerprint=bound, credits=credits_amount or existing.credits,
                price_id=price_id or existing.price_id,
                customer_id=customer_id or existing.customer_id))
        return "already_entitled"
    await _write_session(kv, SessionRecord(
        session_id=session_id, subscription_id="", claimed=False,
        product_kind="pack", price_id=price_id, credits=credits_amount,
        customer_id=customer_id, key_fingerprint=key_fingerprint))
    return "entitled"


async def grant_pack(kv: Any, *, fingerprint_hex: str, session_id: str, units: int,
                     ledger: Any, now: datetime, policy: AccessPolicy) -> str:
    """ADD pack credits to an already-issued key. Idempotent on session id."""
    if not fingerprint_hex or units < 1 or ledger is None:
        return "skipped"
    record = await keys.lookup_fingerprint(kv, fingerprint_hex)
    if record is None:
        return "missing_key"
    try:
        result = await ledger.credit(
            credits.holder_from_fingerprint(fingerprint_hex),
            f"pack:{session_id}", units, session_id,
            expires_at=_pack_expiry(now, policy), source="pack")
        return "granted" if result.credited else result.reason or "duplicate"
    except credits.StoreNotConfigured:
        return "store_unbound"


async def set_subscription_tier(kv: Any, subscription_id: str, tier: str, *,
                                policy: AccessPolicy) -> str:
    """Downgrade or restore this subscription's entitlement, and its key if any."""
    existing = await load_subscription(kv, subscription_id)
    if existing is None:
        return "no_key"
    if existing.tier == tier:
        return "unchanged"
    if existing.key_fingerprint:
        updated = await keys.set_tier(kv, existing.key_fingerprint, tier, policy=policy)
        if updated is None:
            return "missing_key"
    status = (STATUS_INACTIVE if tier == policy.billing.downgrade_tier
              else STATUS_ACTIVE)
    await _write_sub(kv, replace(existing, tier=tier, status=status))
    return "tier_set"


def _pack_expiry(now: datetime, policy: AccessPolicy) -> str:
    clock = now if now.tzinfo else now.replace(tzinfo=UTC)
    expiry = clock.astimezone(UTC) + timedelta(days=policy.credits.pack_expiry_days)
    return expiry.isoformat(timespec="seconds").replace("+00:00", "Z")


async def _grant_pending_monthly(ledger: Any, stored: SubscriptionRecord,
                                 invoice_id: str) -> None:
    if ledger is None or not stored.key_fingerprint or stored.pending_monthly < 1:
        return
    holder = credits.holder_from_fingerprint(stored.key_fingerprint)
    try:
        await ledger.set_monthly(
            holder, stored.pending_monthly, invoice_id,
            stored.plan_name)
    except credits.StoreNotConfigured:
        return


def _pack_mapping(session: SessionRecord, policy: AccessPolicy):
    if not session.price_id:
        return None
    try:
        return policy.price(session.price_id)
    except PolicyError:
        return None


def _bound_pack_record(session: SessionRecord, *, now: datetime,
                       policy: AccessPolicy, key: keys.KeyRecord | None
                       ) -> SubscriptionRecord:
    mapping = _pack_mapping(session, policy)
    amount = session.credits or (mapping.credits if mapping is not None else 0)
    tier = (key.tier if key is not None
            else (mapping.tier if mapping is not None else "paid"))
    return SubscriptionRecord(
        subscription_id=f"pack:{session.session_id}",
        customer_id=session.customer_id, price_id=session.price_id,
        tier=tier, status=STATUS_ACTIVE,
        key_fingerprint=session.key_fingerprint,
        key_id=key.key_id if key is not None else "",
        created_at=_iso(now),
        plan_name=mapping.name if mapping is not None else "",
        plan_credits=amount)


async def consume_claim(kv: Any, session_id: str, *, now: datetime,
                        policy: AccessPolicy, ledger: Any = None
                        ) -> ClaimResult | None:
    """Apply this session once: mint a key, or credit the bound existing key.

    `None` means the webhook has not linked this session yet. A second call
    is `consumed` and does not mint. Pack sessions have no subscription row;
    a synthetic one is returned so claim's response shape stays the same.
    """
    session = await load_session(kv, session_id)
    if session is None:
        return None
    if session.product_kind == "pack":
        return await _consume_pack_claim(
            kv, session, now=now, policy=policy, ledger=ledger)

    stored = await load_subscription(kv, session.subscription_id)
    if stored is None:
        return None
    if session.claimed:
        return ClaimResult(record=stored, consumed=True)
    if session.key_fingerprint:
        return await _consume_bound_plan_claim(
            kv, session, stored, now=now, policy=policy, ledger=ledger)
    if stored.key_fingerprint:
        return ClaimResult(record=stored, consumed=True)
    owner = (f"stripe:{stored.customer_id}" if stored.customer_id
             else f"stripe:{stored.subscription_id}")
    secret, record = await keys.issue(
        kv, tier=stored.tier, owner=owner, now=now, policy=policy,
        label=f"subscription:{stored.subscription_id}")
    fingerprint_hex = keys.fingerprint(secret)
    stored = replace(stored, key_fingerprint=fingerprint_hex, key_id=record.key_id)
    await _grant_pending_monthly(
        ledger, stored, invoice_id=f"claim:{stored.subscription_id}")
    stored = replace(stored, pending_monthly=0)
    await _write_sub(kv, stored)
    await _write_keyref(kv, fingerprint_hex, stored.subscription_id)
    await _write_session(kv, replace(session, claimed=True))
    return ClaimResult(record=stored, issued=secret, minted=True)


async def _consume_bound_plan_claim(kv: Any, session: SessionRecord,
                                    stored: SubscriptionRecord, *, now: datetime,
                                    policy: AccessPolicy, ledger: Any
                                    ) -> ClaimResult | None:
    fingerprint_hex = session.key_fingerprint
    if not stored.key_fingerprint:
        attached = await attach_existing_key(
            kv, fingerprint_hex=fingerprint_hex,
            subscription_id=stored.subscription_id, tier=stored.tier,
            policy=policy)
        if attached is None:
            return None
        stored = replace(stored, key_fingerprint=fingerprint_hex,
                         key_id=attached.key_id)
        await _write_sub(kv, stored)
    await _grant_pending_monthly(
        ledger, stored, invoice_id=f"claim:{stored.subscription_id}")
    stored = replace(stored, pending_monthly=0)
    await _write_sub(kv, stored)
    await _write_session(kv, replace(session, claimed=True))
    return ClaimResult(record=stored, attached=True)


async def _consume_pack_claim(kv: Any, session: SessionRecord, *, now: datetime,
                              policy: AccessPolicy, ledger: Any
                              ) -> ClaimResult | None:
    if session.key_fingerprint:
        key = await keys.lookup_fingerprint(kv, session.key_fingerprint)
        dummy = _bound_pack_record(session, now=now, policy=policy, key=key)
        if session.claimed:
            return ClaimResult(record=dummy, consumed=True)
        if key is None:
            return None
        amount = dummy.plan_credits
        if amount > 0:
            await grant_pack(
                kv, fingerprint_hex=session.key_fingerprint,
                session_id=session.session_id, units=amount, ledger=ledger,
                now=now, policy=policy)
        mapping = _pack_mapping(session, policy)
        if mapping is not None:
            await keys.set_tier(
                kv, session.key_fingerprint, mapping.tier, policy=policy)
        await _write_session(kv, replace(session, claimed=True))
        return ClaimResult(record=dummy, attached=True)

    pack_sub_id = f"pack:{session.session_id}"
    if session.claimed:
        stored = await load_subscription(kv, pack_sub_id)
        if stored is not None:
            return ClaimResult(record=stored, consumed=True)
        dummy = SubscriptionRecord(
            subscription_id=pack_sub_id, customer_id=session.customer_id,
            price_id=session.price_id, tier=policy.billing.downgrade_tier,
            status=STATUS_INACTIVE, key_fingerprint="", key_id="",
            created_at=_iso(now))
        return ClaimResult(record=dummy, consumed=True)
    owner = (f"stripe:{session.customer_id}" if session.customer_id
             else f"stripe:pack:{session.session_id}")
    mapping = _pack_mapping(session, policy)
    tier = mapping.tier if mapping is not None else "paid"
    policy.tier(tier)
    secret, record = await keys.issue(
        kv, tier=tier, owner=owner, now=now, policy=policy,
        label=f"pack:{session.session_id}")
    fingerprint_hex = keys.fingerprint(secret)
    amount = session.credits or (mapping.credits if mapping is not None else 0)
    if ledger is not None and amount > 0:
        try:
            await ledger.credit(
                credits.holder_from_fingerprint(fingerprint_hex),
                f"pack:{session.session_id}", amount, session.session_id,
                expires_at=_pack_expiry(now, policy), source="pack")
        except credits.StoreNotConfigured:
            pass
    stored = SubscriptionRecord(
        subscription_id=pack_sub_id,
        customer_id=session.customer_id, price_id=session.price_id,
        tier=tier, status=STATUS_ACTIVE, key_fingerprint=fingerprint_hex,
        key_id=record.key_id, created_at=_iso(now),
        plan_name=mapping.name if mapping is not None else "",
        plan_credits=amount)
    await _write_sub(kv, stored)
    await _write_keyref(kv, fingerprint_hex, stored.subscription_id)
    await _write_session(kv, replace(session, claimed=True))
    return ClaimResult(record=stored, issued=secret, minted=True)


async def rotate(kv: Any, current_key: str, *, now: datetime,
                 policy: AccessPolicy, ledger: Any = None
                 ) -> tuple[str, keys.KeyRecord] | None:
    """Issue a replacement, revoke the current key. `None` if the key is unknown."""
    record = await keys.lookup(kv, current_key)
    if record is None:
        return None
    fingerprint_hex = keys.fingerprint(current_key)
    ref_raw = await kv.get(keyref_name(fingerprint_hex))
    subscription_id = ""
    sub: SubscriptionRecord | None = None
    if ref_raw is not None:
        ref = KeyRef.from_json(ref_raw)
        subscription_id = ref.subscription_id
        sub = await load_subscription(kv, subscription_id)
    owner = record.owner
    label = record.label
    secret, issued = await keys.issue(
        kv, tier=record.tier, owner=owner, now=now, policy=policy, label=label)
    new_fp = keys.fingerprint(secret)
    await keys.revoke(kv, current_key)
    await _write_keyref(kv, new_fp, subscription_id)
    if sub is not None:
        await _write_sub(kv, replace(
            sub, key_fingerprint=new_fp, key_id=issued.key_id, tier=record.tier))
    if ledger is not None:
        try:
            await ledger.transfer(
                credits.holder_from_fingerprint(fingerprint_hex),
                credits.holder_from_fingerprint(new_fp))
        except credits.StoreNotConfigured:
            pass
    return secret, issued


async def grant_monthly(kv: Any, subscription_id: str, *, ledger: Any,
                        units: int, invoice_id: str, plan: str) -> str:
    """SET monthly on the claimed key, or remember it for claim. Packs untouched."""
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        return "no_key"
    if stored.key_fingerprint and ledger is not None:
        try:
            result = await ledger.set_monthly(
                credits.holder_from_fingerprint(stored.key_fingerprint),
                units, invoice_id, plan)
            if result.credited and stored.pending_monthly:
                await _write_sub(kv, replace(stored, pending_monthly=0,
                                             plan_name=plan or stored.plan_name,
                                             plan_credits=units or stored.plan_credits))
            return "granted" if result.credited else result.reason or "duplicate"
        except credits.StoreNotConfigured:
            return "store_unbound"
    updated = replace(stored, pending_monthly=units, plan_name=plan or stored.plan_name,
                      plan_credits=units or stored.plan_credits)
    await _write_sub(kv, updated)
    return "pending"


async def clear_monthly(kv: Any, subscription_id: str, *, ledger: Any) -> str:
    """Zero monthly remaining. Pack grants stay."""
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        return "no_key"
    if stored.key_fingerprint and ledger is not None:
        try:
            await ledger.clear_monthly(
                credits.holder_from_fingerprint(stored.key_fingerprint))
        except credits.StoreNotConfigured:
            return "store_unbound"
    await _write_sub(kv, replace(stored, pending_monthly=0))
    return "cleared"
