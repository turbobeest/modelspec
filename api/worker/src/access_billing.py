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

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Any

import access_keys as keys
from access_keys import storage_name, storage_name_from_fingerprint
import credits
from access_config import AccessPolicy, PolicyError, load_policy
from access_kv import CloudflareKV

_EVENT_PREFIX = "event:"
_SESSION_PREFIX = "session:"
_SUB_PREFIX = "sub:"
_KEYREF_PREFIX = "keyref:"

STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"


def _claim_secret(policy: AccessPolicy, nonce: str) -> str:
    """Derive the claim key from the nonce stored on the claim. The key is not stored."""
    digest = hmac.new(nonce.encode(), b"modelspec.claim", hashlib.sha256).hexdigest()
    return policy.live_prefix + digest


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
    refunded: bool = False


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
    pending_invoice_id: str = ""
    plan_name: str = ""
    plan_credits: int = 0
    subscription_status: str = ""
    subscription_updated_at: int = 0
    invoice_id: str = ""
    invoice_period_start: int = 0
    invoice_period_end: int = 0
    invoice_paid: bool = False
    canceled_at: int = 0

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
            "pending_invoice_id": self.pending_invoice_id,
            "plan_name": self.plan_name,
            "plan_credits": self.plan_credits,
            "subscription_status": self.subscription_status,
            "subscription_updated_at": self.subscription_updated_at,
            "invoice_id": self.invoice_id,
            "invoice_period_start": self.invoice_period_start,
            "invoice_period_end": self.invoice_period_end,
            "invoice_paid": self.invoice_paid,
            "canceled_at": self.canceled_at,
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
            pending_invoice_id=str(data.get("pending_invoice_id") or ""),
            plan_name=str(data.get("plan_name") or ""),
            plan_credits=int(data.get("plan_credits") or 0),
            subscription_status=str(data.get("subscription_status") or ""),
            subscription_updated_at=int(data.get("subscription_updated_at") or 0),
            invoice_id=str(data.get("invoice_id") or ""),
            invoice_period_start=int(data.get("invoice_period_start") or 0),
            invoice_period_end=int(data.get("invoice_period_end") or 0),
            invoice_paid=bool(data.get("invoice_paid", False)),
            canceled_at=int(data.get("canceled_at") or 0),
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


async def record_chronology(kv: Any, subscription_id: str, *, now: datetime,
                            policy: AccessPolicy, customer_id: str = "",
                            subscription_status: str = "", updated_at: int = 0,
                            invoice_id: str = "", period_start: int = 0,
                            period_end: int = 0, paid: bool = False,
                            canceled_at: int = 0) -> None:
    """Retain accepted subscription status and invoice periods on the billing row."""
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        stored = SubscriptionRecord(
            subscription_id=subscription_id, customer_id=customer_id, price_id="",
            tier=policy.billing.downgrade_tier, status=STATUS_INACTIVE,
            key_fingerprint="", key_id="", created_at=_iso(now))
    if subscription_status:
        stored = replace(
            stored, subscription_status=subscription_status,
            subscription_updated_at=max(updated_at, stored.subscription_updated_at))
        if subscription_status == "active":
            stored = replace(stored, canceled_at=0)
        elif canceled_at:
            stored = replace(stored, canceled_at=max(int(canceled_at), stored.canceled_at))
    if invoice_id:
        incoming = (period_start, period_end)
        stored_period = (stored.invoice_period_start, stored.invoice_period_end)
        # An older period must not replace a newer one when the two handlers overlap.
        if not any(stored_period) or (any(incoming) and incoming >= stored_period):
            stored = replace(
                stored, invoice_id=invoice_id, invoice_period_start=period_start,
                invoice_period_end=period_end, invoice_paid=paid)
    await _write_sub(kv, stored)


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


async def link_current_checkout(kv: Any, stored: SubscriptionRecord, *,
                                session_id: str, key_fingerprint: str,
                                policy: AccessPolicy, ledger: Any) -> None:
    """Link Checkout using the subscription's current entitlement."""
    if key_fingerprint and not stored.key_fingerprint:
        attached = await attach_existing_key(
            kv, fingerprint_hex=key_fingerprint,
            subscription_id=stored.subscription_id, tier=stored.tier, policy=policy)
        if attached is not None:
            stored = replace(stored, key_fingerprint=key_fingerprint,
                             key_id=attached.key_id)
            await _write_sub(kv, stored)
            await _grant_pending_monthly(
                ledger, stored, invoice_id=f"claim:{stored.subscription_id}")
            stored = replace(stored, pending_monthly=0)
            await _write_sub(kv, stored)
    await _link_session(
        kv, session_id, stored.subscription_id, price_id=stored.price_id,
        credits_amount=stored.plan_credits, customer_id=stored.customer_id,
        key_fingerprint=stored.key_fingerprint)


async def attach_existing_key(kv: Any, *, fingerprint_hex: str,
                              subscription_id: str, tier: str,
                              policy: AccessPolicy, set_tier: bool = True
                              ) -> keys.KeyRecord | None:
    """Point this subscription at an already-issued key. Does not mint.

    A previous keyref (a pack session, an earlier plan) is detached so
    cancellation of the old row cannot downgrade this key.
    """
    if not fingerprint_hex:
        return None
    record = await keys.lookup_fingerprint(kv, fingerprint_hex)
    if record is None:
        return None
    if set_tier and record.tier != tier:
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
                             pending_monthly: int = 0, pending_invoice_id: str = "",
                             plan_name: str = "",
                             plan_credits: int = 0, key_fingerprint: str = "",
                             promote: bool = True,
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
        bound = existing.key_fingerprint or key_fingerprint
        attached = None
        if bound and not existing.key_fingerprint:
            attached = await attach_existing_key(
                kv, fingerprint_hex=bound, subscription_id=subscription_id,
                tier=tier, policy=policy, set_tier=promote)
        if promote and (existing.tier != tier or existing.status != STATUS_ACTIVE):
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
                pending_invoice_id=pending_invoice_id or existing.pending_invoice_id,
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
                fields["pending_invoice_id"] = pending_invoice_id or existing.pending_invoice_id
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
        pending_invoice_id=pending_invoice_id,
        plan_name=plan_name, plan_credits=plan_credits,
    )
    if key_fingerprint:
        attached = await attach_existing_key(
            kv, fingerprint_hex=key_fingerprint, subscription_id=subscription_id,
            tier=tier, policy=policy, set_tier=promote)
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
                     ledger: Any, now: datetime, policy: AccessPolicy,
                     tx: str = "") -> str:
    """ADD pack credits to an already-issued key. Idempotent on session id.

    `tx` is the PaymentIntent id when Checkout named one (MODEL-106): the
    ledger keeps it on the payment claim so a refund or dispute can find it.
    """
    if not fingerprint_hex or units < 1 or ledger is None:
        return "skipped"
    record = await keys.lookup_fingerprint(kv, fingerprint_hex)
    if record is None:
        return "missing_key"
    try:
        result = await ledger.credit(
            credits.holder_from_fingerprint(fingerprint_hex),
            f"pack:{session_id}", units, tx or session_id,
            expires_at=_pack_expiry(now, policy), source="pack")
        return "granted" if result.credited else result.reason or "duplicate"
    except credits.StoreNotConfigured:
        return "store_unbound"


async def set_subscription_tier(kv: Any, subscription_id: str, tier: str, *,
                                policy: AccessPolicy, align_key: bool = False) -> str:
    """Downgrade or restore this subscription's entitlement, and its key if any."""
    existing = await load_subscription(kv, subscription_id)
    if existing is None:
        return "no_key"
    key_differs = False
    if align_key and existing.key_fingerprint:
        current = await keys.lookup_fingerprint(kv, existing.key_fingerprint)
        key_differs = current is not None and current.tier != tier
    if existing.tier == tier and not key_differs:
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
            holder, stored.pending_monthly, stored.pending_invoice_id or invoice_id,
            stored.plan_name, stored.customer_id)
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
    session = await load_session(kv, session_id)
    if session is None:
        return None
    if session.product_kind != "pack":
        if await load_subscription(kv, session.subscription_id) is None:
            return None
    return await ledger.claim_purchase(kv, session_id, now=now, policy=policy)


async def _consume_claim_serialized(kv: Any, session_id: str, *, now: datetime,
                                    policy: AccessPolicy, ledger: Any
                                    ) -> ClaimResult | None:
    """Select one purchase owner before issuance and complete funding last."""
    session = await load_session(kv, session_id)
    if session is None:
        return None
    pack = session.product_kind == "pack"
    subscription_id = f"pack:{session_id}" if pack else session.subscription_id
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        if not pack:
            return None
        stored = _bound_pack_record(session, now=now, policy=policy, key=None)
    payment_id = f"pack:{session_id}" if pack else f"claim:{subscription_id}"
    selected = await ledger.claim_state(payment_id)
    if selected is not None and selected["stage"] == "complete":
        nonce = str(selected.get("nonce") or "")
        if not nonce:
            return ClaimResult(record=stored, consumed=True)
        secret = _claim_secret(policy, nonce)
        if keys.fingerprint(secret) != (stored.key_fingerprint or ""):
            return ClaimResult(record=stored, consumed=True)
        shown = ClaimResult(record=replace(stored, pending_monthly=0), issued=secret,
                            minted=True)
        await ledger.drop_claim_nonce(payment_id)
        return shown
    if selected is None and (session.claimed or (
            not pack and stored.key_fingerprint and not session.key_fingerprint)):
        return ClaimResult(record=stored, consumed=True)
    payment = await ledger.payment(payment_id)
    if pack and credits.unclaimed_units(payment) == 0:
        return ClaimResult(record=stored, refunded=True)

    bound = bool(session.key_fingerprint)
    needs_attachment = bound and not pack and not stored.key_fingerprint
    nonce = ""
    if bound:
        fingerprint_hex = stored.key_fingerprint or session.key_fingerprint
        if pack and payment and payment.get("holder"):
            fingerprint_hex = str(payment["holder"]).removeprefix("key:")
        record = await keys.lookup_fingerprint(kv, fingerprint_hex)
        if record is None:
            return None
        secret = ""
    else:
        nonce = str(selected.get("nonce") or "") if selected is not None else ""
        if selected is not None and not nonce:
            previous_fp = selected["holder"].removeprefix("key:")
            previous = await keys.lookup_fingerprint(kv, previous_fp)
            if previous is not None:
                await kv.put(storage_name_from_fingerprint(previous_fp),
                             json.dumps(replace(previous, active=False).to_json()))
        if not nonce:
            nonce = secrets.token_hex(32)
        secret = _claim_secret(policy, nonce)
        fingerprint_hex = keys.fingerprint(secret)
        record = keys.KeyRecord(
            key_id=keys.key_id(secret), tier=stored.tier,
            owner=f"stripe:{stored.customer_id or subscription_id}",
            created_at=_iso(now), label=(subscription_id if pack else
                                       f"subscription:{subscription_id}"))
    amount = (stored.plan_credits if pack else stored.pending_monthly)
    if selected is not None and (pack or not stored.pending_monthly):
        amount = int(selected["units"])
    if not pack and stored.status == STATUS_INACTIVE:
        amount = 0
    invoice_id = (stored.pending_invoice_id or
                  (selected.get("invoice_id", "") if selected else "") or payment_id)
    holder = credits.holder_from_fingerprint(fingerprint_hex)
    stored = replace(stored, key_fingerprint=fingerprint_hex, key_id=record.key_id)
    claim_row = {
        "holder": holder, "units": amount, "invoice_id": invoice_id,
        "stage": "prepared",
    }
    if nonce:
        claim_row["nonce"] = nonce
    await ledger.save_claim(payment_id, claim_row,
                            kind="pack" if pack else "monthly", units=amount, tx=session_id)

    if not bound:
        await kv.put(storage_name(secret), json.dumps(record.to_json()))
    elif needs_attachment:
        await attach_existing_key(
            kv, fingerprint_hex=fingerprint_hex, subscription_id=subscription_id,
            tier=stored.tier, policy=policy)
    if bound and pack:
        mapping = _pack_mapping(session, policy)
        if mapping is not None:
            await keys.set_tier(kv, fingerprint_hex, mapping.tier, policy=policy)
    else:
        await _write_sub(kv, replace(stored, pending_monthly=0))
        await _write_keyref(kv, fingerprint_hex, subscription_id)
    await _write_session(kv, replace(session, claimed=True))

    if amount > 0:
        if pack:
            result = await ledger.credit(holder, payment_id, amount, session_id,
                                         expires_at=_pack_expiry(now, policy), source="pack")
        else:
            result = await ledger.fund_claim(holder, payment_id, invoice_id, amount,
                                             stored.plan_name, stored.customer_id)
        if isinstance(result, dict):
            result = credits.CreditResult.from_json(result)
        if not result.credited and result.reason not in {"replay", "refunded"}:
            raise RuntimeError("purchase claim could not fund its selected owner")
        if not result.credited:
            await ledger.finish_claim(payment_id)
    else:
        await ledger.finish_claim(payment_id)
    shown = ClaimResult(record=replace(stored, pending_monthly=0), issued=secret,
                        minted=not bound, attached=bound)
    if nonce:
        await ledger.drop_claim_nonce(payment_id)
    return shown


async def rotate(kv: Any, current_key: str, *, now: datetime,
                 policy: AccessPolicy, ledger: Any = None
                 ) -> tuple[str, keys.KeyRecord] | None:
    return await ledger.rotate_key(kv, current_key, now=now, policy=policy)


async def _rotate_serialized(kv: Any, current_key: str, *, now: datetime,
                             policy: AccessPolicy, ledger: Any
                             ) -> tuple[str, keys.KeyRecord] | None:
    """Resume a rotation inside the ledger's serialized billing operation."""
    fingerprint_hex = keys.fingerprint(current_key)
    holder = credits.holder_from_fingerprint(fingerprint_hex)
    transition = await ledger.rotation_state(holder)
    if transition is None:
        record = await keys.lookup(kv, current_key)
        if record is None or not record.active:
            return None
        ref_raw = await kv.get(keyref_name(fingerprint_hex))
        subscription_id = KeyRef.from_json(ref_raw).subscription_id if ref_raw else ""
        transition = {
            "nonce": secrets.token_hex(32), "stage": "prepared",
            "key_record": record.to_json(),
            "subscription_id": subscription_id, "created_at": _iso(now),
        }
        await ledger.save_rotation(holder, transition)
    if transition["stage"] == "complete":
        return None
    record = keys.KeyRecord.from_json(json.dumps(transition["key_record"]))
    secret = policy.live_prefix + hmac.new(
        current_key.encode(), ("modelspec.rotation:" + transition["nonce"]).encode(),
        hashlib.sha256).hexdigest()
    new_fp = keys.fingerprint(secret)
    issued = replace(record, key_id=keys.key_id(secret),
                     created_at=transition["created_at"], active=True)
    if transition["stage"] == "prepared":
        current = await keys.lookup(kv, current_key)
        if current is not None:
            record = current
            issued = replace(issued, tier=current.tier)
        sub = await load_subscription(kv, transition["subscription_id"])
        owns_subscription = sub is not None and sub.key_fingerprint in {fingerprint_hex, new_fp}
        if owns_subscription:
            issued = replace(issued, tier=sub.tier)
            if sub.status == STATUS_INACTIVE:
                await ledger.clear_monthly(holder)
        await kv.put(storage_name(secret), json.dumps(issued.to_json()))
        await _write_keyref(kv, new_fp, transition["subscription_id"])
        if owns_subscription:
            await _write_sub(kv, replace(sub, key_fingerprint=new_fp,
                                        key_id=issued.key_id))
        await ledger.transfer(holder, credits.holder_from_fingerprint(new_fp))
        transition = {**transition, "stage": "transferred"}
    await kv.put(storage_name(current_key),
                 json.dumps(replace(record, active=False).to_json()))
    try:
        await ledger.save_rotation(holder, {"stage": "complete"})
    except Exception:
        if (await ledger.rotation_state(holder) or {}).get("stage") != "complete":
            raise
    return secret, issued


async def grant_monthly(kv: Any, subscription_id: str, *, ledger: Any,
                        units: int, invoice_id: str, plan: str,
                        period_end: int = 0, period_start: int = 0) -> str:
    """SET monthly on the claimed key, or remember it for claim. Packs untouched."""
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        return "no_key"
    if stored.key_fingerprint and ledger is not None:
        try:
            selected = await ledger.claim_state(f"claim:{subscription_id}")
            if selected is not None and selected["stage"] == "prepared":
                await _write_sub(kv, replace(
                    stored, pending_monthly=units, pending_invoice_id=invoice_id,
                    plan_name=plan or stored.plan_name, plan_credits=units))
                return "pending"
            result = await ledger.set_monthly(
                credits.holder_from_fingerprint(stored.key_fingerprint),
                units, invoice_id, plan, stored.customer_id,
                period_end=int(period_end or 0),
                period_start=int(period_start or 0))
            if result.reason == "stale":
                return "stale"
            if result.credited and stored.pending_monthly:
                await _write_sub(kv, replace(stored, pending_monthly=0,
                                             plan_name=plan or stored.plan_name,
                                             plan_credits=units or stored.plan_credits))
            return "granted" if result.credited else result.reason or "duplicate"
        except credits.StoreNotConfigured:
            return "store_unbound"
    updated = replace(stored, pending_monthly=units, pending_invoice_id=invoice_id,
                      plan_name=plan or stored.plan_name,
                      plan_credits=units or stored.plan_credits)
    await _write_sub(kv, updated)
    return "pending"


async def clear_monthly(kv: Any, subscription_id: str, *, ledger: Any,
                        period_end: int = 0, watermark: int = 0) -> str:
    """Zero monthly remaining. Pack grants stay.

    `period_end` rejects a failed invoice that ended at or before the stored
    watermark. `watermark` is the cancellation time. A stale clear leaves the
    allowance and the subscription row alone.
    """
    stored = await load_subscription(kv, subscription_id)
    if stored is None:
        return "no_key"
    if stored.key_fingerprint and ledger is not None:
        try:
            result = await ledger.clear_monthly(
                credits.holder_from_fingerprint(stored.key_fingerprint),
                period_end=int(period_end or 0), watermark=int(watermark or 0))
        except credits.StoreNotConfigured:
            return "store_unbound"
        if result.reason == "stale":
            return "stale"
    await _write_sub(kv, replace(stored, pending_monthly=0))
    return "cleared"


async def claim_from_env(ledger: Any, env: Any, session_id: str, now: str) -> str:
    result = await _consume_claim_serialized(
        CloudflareKV(env.ACCESS), str(session_id),
        now=datetime.fromisoformat(str(now).replace("Z", "+00:00")),
        policy=load_policy(env), ledger=ledger)
    return json.dumps(asdict(result) if result is not None else None)


async def rotate_from_env(ledger: Any, env: Any, current_key: str, now: str) -> str:
    result = await _rotate_serialized(
        CloudflareKV(env.ACCESS), str(current_key),
        now=datetime.fromisoformat(str(now).replace("Z", "+00:00")),
        policy=load_policy(env), ledger=ledger)
    return json.dumps(None if result is None else [result[0], result[1].to_json()])
