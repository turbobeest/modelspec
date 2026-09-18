"""ACCESS records MODEL-73 adds: Stripe events, subscriptions, sessions, keyrefs.

The key itself is stored only as a SHA-256 lookup in `access_keys`. These
records are the billing index on top of that: which Stripe event we have
already applied, which subscription is entitled to which tier, which Checkout
session points at that subscription, and (after claim) which fingerprint the
subscription currently owns.

The webhook never mints a key. Claim calls `access_keys.issue`, returns the
plaintext once, and writes only the hash. Every `.put` below names a record
through one of the `*_name` functions so `tests/test_legal.py` can see what we
write. The privacy statement lists the same four kinds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

import access_keys as keys
from access_config import AccessPolicy

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
    """Checkout session → subscription. Claimed once. No key material."""

    session_id: str
    subscription_id: str
    claimed: bool = False

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": "session",
            "session_id": self.session_id,
            "subscription_id": self.subscription_id,
            "claimed": self.claimed,
        }

    @classmethod
    def from_json(cls, text: str) -> SessionRecord:
        data = json.loads(text)
        return cls(session_id=str(data.get("session_id") or ""),
                   subscription_id=str(data.get("subscription_id") or ""),
                   claimed=bool(data.get("claimed", False)))


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


async def _link_session(kv: Any, session_id: str, subscription_id: str) -> None:
    """Point this Checkout session at the subscription. Never un-claim."""
    existing = await load_session(kv, session_id)
    if existing is not None and existing.claimed:
        return
    if (existing is not None and existing.subscription_id == subscription_id
            and not existing.claimed):
        return
    await _write_session(kv, SessionRecord(
        session_id=session_id, subscription_id=subscription_id, claimed=False))


async def record_entitlement(kv: Any, *, subscription_id: str, customer_id: str,
                             price_id: str, tier: str, session_id: str,
                             now: datetime, policy: AccessPolicy
                             ) -> tuple[str, SubscriptionRecord]:
    """Record (or refresh) the paid entitlement. Does not mint a key.

    A replayed `checkout.session.completed` after `invoice.paid` (or the reverse)
    shares one subscription row. If a session id is present it is linked so
    claim can mint.
    """
    policy.tier(tier)
    existing = await load_subscription(kv, subscription_id)
    if existing is not None:
        action = "already_entitled"
        updated = existing
        if existing.tier != tier or existing.status != STATUS_ACTIVE:
            if existing.key_fingerprint:
                moved = await keys.set_tier(
                    kv, existing.key_fingerprint, tier, policy=policy)
                if moved is None:
                    return "missing_key", existing
            updated = replace(
                existing, tier=tier, status=STATUS_ACTIVE,
                customer_id=customer_id or existing.customer_id,
                price_id=price_id or existing.price_id)
            await _write_sub(kv, updated)
            action = "restored" if existing.tier != tier else "already_entitled"
        elif customer_id and customer_id != existing.customer_id:
            updated = replace(existing, customer_id=customer_id)
            await _write_sub(kv, updated)
        if session_id:
            await _link_session(kv, session_id, subscription_id)
        return action, updated

    stored = SubscriptionRecord(
        subscription_id=subscription_id, customer_id=customer_id, price_id=price_id,
        tier=tier, status=STATUS_ACTIVE, key_fingerprint="", key_id="",
        created_at=_iso(now),
    )
    await _write_sub(kv, stored)
    if session_id:
        await _link_session(kv, session_id, subscription_id)
    return "entitled", stored


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


async def consume_claim(kv: Any, session_id: str, *, now: datetime,
                        policy: AccessPolicy
                        ) -> tuple[str, SubscriptionRecord] | None:
    """Mint the key for this session once. `(secret, record)` or consumed `("", record)`.

    `None` means the webhook has not linked this session yet. A second call
    does not mint.
    """
    session = await load_session(kv, session_id)
    if session is None:
        return None
    stored = await load_subscription(kv, session.subscription_id)
    if stored is None:
        return None
    if session.claimed or stored.key_fingerprint:
        return "", stored
    owner = (f"stripe:{stored.customer_id}" if stored.customer_id
             else f"stripe:{stored.subscription_id}")
    secret, record = await keys.issue(
        kv, tier=stored.tier, owner=owner, now=now, policy=policy,
        label=f"subscription:{stored.subscription_id}")
    fingerprint_hex = keys.fingerprint(secret)
    stored = replace(stored, key_fingerprint=fingerprint_hex, key_id=record.key_id)
    await _write_sub(kv, stored)
    await _write_keyref(kv, fingerprint_hex, stored.subscription_id)
    await _write_session(kv, replace(session, claimed=True))
    return secret, stored


async def rotate(kv: Any, current_key: str, *, now: datetime,
                 policy: AccessPolicy) -> tuple[str, keys.KeyRecord] | None:
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
    return secret, issued
