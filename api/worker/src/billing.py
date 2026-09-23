"""Stripe Checkout, webhook, claim and rotation (MODEL-73, MODEL-93).

Hosted Checkout collects the card on Stripe's origin. This module never sees
card data. It verifies webhook signatures in process (HMAC-SHA256 over
`t.payload`), records the paid entitlement, and either credits an existing
key (Checkout carried a live key; only its SHA-256 fingerprint is stored) or
mints a key at claim for an anonymous purchase — the plaintext is returned
once and never stored. KV writes go through `access_billing`; this file decides.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs, urlparse

import access
import access_billing as store
import access_keys as keys
import billing_stripe
import credits
from access_config import AccessPolicy, PolicyError, PriceMapping
from access_kv import StoreNotConfigured, UnboundKV
from billing_stripe import SignatureError

HTTP_OK = 200
HTTP_SEE_OTHER = 303
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_CONFLICT = 409
HTTP_GONE = 410
HTTP_MISCONFIGURED = 500
HTTP_UNAVAILABLE = 503

INVALID_SIGNATURE = "invalid_webhook_signature"
BILLING_NOT_ENABLED = "billing_not_enabled"
BILLING_NOT_CONFIGURED = "billing_not_configured"
INVALID_REQUEST = "invalid_request"
PRICE_NOT_MAPPED = "price_not_mapped"
CLAIM_NOT_READY = "claim_not_ready"
CLAIM_CONSUMED = "claim_consumed"
MISSING_KEY = "missing_api_key"
INVALID_KEY = "invalid_api_key"
REVOKED_KEY = "key_revoked"
STORE_NOT_CONFIGURED = "access_store_not_configured"
STRIPE_UNAVAILABLE = "stripe_unavailable"

REFUSALS: dict[str, int] = {
    INVALID_SIGNATURE: HTTP_BAD_REQUEST,
    INVALID_REQUEST: HTTP_BAD_REQUEST,
    MISSING_KEY: HTTP_UNAUTHORIZED,
    INVALID_KEY: HTTP_UNAUTHORIZED,
    REVOKED_KEY: HTTP_FORBIDDEN,
    CLAIM_NOT_READY: HTTP_CONFLICT,
    CLAIM_CONSUMED: HTTP_GONE,
    PRICE_NOT_MAPPED: HTTP_MISCONFIGURED,
    STRIPE_UNAVAILABLE: HTTP_UNAVAILABLE,
    BILLING_NOT_ENABLED: HTTP_UNAVAILABLE,
    BILLING_NOT_CONFIGURED: HTTP_UNAVAILABLE,
    STORE_NOT_CONFIGURED: HTTP_UNAVAILABLE,
}

SCHEMA_VERSION = "1.0"

#: What an HTML `<form method="post">` sends: the `/pricing` buy buttons.
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"

#: Subscription statuses that mean paid service has ended. `past_due` is not
#: here: `invoice.payment_failed` already downgraded, and a later `invoice.paid`
#: restores. We do not keep serving paid limits while Stripe retries.
EXPIRED_STATUSES = frozenset({"canceled", "unpaid", "incomplete_expired"})

PROVISION_TYPES = frozenset({
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "invoice.paid",
})
DOWNGRADE_TYPES = frozenset({
    "invoice.payment_failed",
    "customer.subscription.deleted",
})

WHAT_YOU_BUY = (
    "credits on this API key: a monthly allowance that resets each paid "
    "invoice (no rollover), and/or pack credits that expire 12 months after "
    "purchase. A funded key receives the paid answer, including cited "
    "commercial-use and data-residency determinations. Only successful "
    "results draw credits."
)

CREDITS_ADDED = "credits added to your key"
PLAN_ATTACHED = "plan attached to your key"
KEY_SHOWN_ONCE = (
    "API key shown once. Store it; claiming again will not reveal it."
)
APPLIED_EXISTING = "existing_key"
APPLIED_NEW = "new_key"


def what_you_buy(mapping: PriceMapping | None = None) -> str:
    if mapping is None:
        return WHAT_YOU_BUY
    if mapping.kind == "plan":
        return (
            f"{mapping.name}: {mapping.credits} credits each paid month, "
            "reset with no rollover. A funded key receives the paid answer, "
            "including cited commercial-use and data-residency determinations. "
            "Only successful results draw credits. Pack credits are unaffected "
            "by cancellation."
        )
    return (
        f"{mapping.name}: {mapping.credits} credits added to this key, "
        "expiring 12 months after purchase, oldest spent first. "
        "A funded key receives the paid answer, including cited "
        "commercial-use and data-residency determinations. "
        "Only successful results draw credits."
    )


@dataclass
class Outcome:
    status: int
    body: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)


def enabled(raw: Any) -> bool:
    """`BILLING_ENABLED`. Same spellings as `ACCESS_ENFORCED`; a typo reads as on."""
    return access.enforcement(raw)


def _envelope(endpoint: str, service_commit: str, extra: dict[str, Any] | None = None
              ) -> dict[str, Any]:
    body = {
        "schema_version": SCHEMA_VERSION,
        "endpoint": endpoint,
        "service_commit": service_commit,
    }
    if extra:
        body.update(extra)
    return body


def _refusal(code: str, message: str, *, service_commit: str, endpoint: str,
             detail: dict[str, Any] | None = None, status: int | None = None
             ) -> Outcome:
    body = _envelope(endpoint, service_commit, {
        "error": {"code": code, "message": message, **(detail or {})},
        "result": [],
    })
    return Outcome(status if status is not None else REFUSALS[code], body)


def _id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    if value is None:
        return ""
    return str(value)


def _meta(obj: Any) -> dict[str, Any]:
    meta = obj.get("metadata") if isinstance(obj, dict) else None
    return meta if isinstance(meta, dict) else {}


def _looks_like_fingerprint(value: str) -> bool:
    """SHA-256 hex only. Rejects a live key if one were ever written into metadata."""
    if len(value) != 64:
        return False
    return all(c in "0123456789abcdef" for c in value)


def _fingerprint_from_obj(obj: dict[str, Any]) -> str:
    """SHA-256 of the bound API key, from Checkout / invoice / subscription metadata.

    Never a key value. A string that is not 64 hex characters is ignored, so a
    live key cannot land in ACCESS even if it were stuffed into Stripe metadata.
    """
    candidates: list[Any] = [_meta(obj).get("modelspec_key_fingerprint")]
    sub = obj.get("subscription")
    if isinstance(sub, dict):
        candidates.append(_meta(sub).get("modelspec_key_fingerprint"))
    details = obj.get("subscription_details")
    if isinstance(details, dict):
        candidates.append(_meta(details).get("modelspec_key_fingerprint"))
    parent = obj.get("parent")
    if isinstance(parent, dict):
        nested = parent.get("subscription_details")
        if isinstance(nested, dict):
            candidates.append(_meta(nested).get("modelspec_key_fingerprint"))
            nested_sub = nested.get("subscription")
            if isinstance(nested_sub, dict):
                candidates.append(_meta(nested_sub).get("modelspec_key_fingerprint"))
    for raw in candidates:
        value = str(raw or "").strip().lower()
        if _looks_like_fingerprint(value):
            return value
    return ""


def _price_from_session(obj: dict[str, Any]) -> str:
    meta = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    if meta.get("modelspec_price_id"):
        return str(meta["modelspec_price_id"])
    items = obj.get("line_items")
    rows = items.get("data") if isinstance(items, dict) else items
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            price = row.get("price")
            if isinstance(price, dict) and price.get("id"):
                return str(price["id"])
            if isinstance(price, str) and price:
                return price
    return ""


def _price_from_invoice(obj: dict[str, Any]) -> str:
    lines = obj.get("lines")
    rows = lines.get("data") if isinstance(lines, dict) else []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            price = row.get("price")
            if isinstance(price, dict) and price.get("id"):
                return str(price["id"])
            if isinstance(price, str) and price:
                return price
            # Since API 2025-03-31.basil a line names its Price here instead.
            pricing = row.get("pricing")
            details = pricing.get("price_details") if isinstance(pricing, dict) else None
            if isinstance(details, dict) and _id(details.get("price")):
                return _id(details.get("price"))
    meta = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    if meta.get("modelspec_price_id"):
        return str(meta["modelspec_price_id"])
    # Checkout's subscription_data metadata reaches a basil+ invoice here.
    parent = obj.get("parent")
    sub_details = parent.get("subscription_details") if isinstance(parent, dict) else None
    if isinstance(sub_details, dict):
        return str(_meta(sub_details).get("modelspec_price_id") or "")
    return ""


def _price_from_subscription(obj: dict[str, Any]) -> str:
    items = obj.get("items")
    rows = items.get("data") if isinstance(items, dict) else []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            price = row.get("price")
            if isinstance(price, dict) and price.get("id"):
                return str(price["id"])
            if isinstance(price, str) and price:
                return price
    meta = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    return str(meta.get("modelspec_price_id") or "")


def _subscription_from_invoice(obj: dict[str, Any]) -> str:
    direct = _id(obj.get("subscription"))
    if direct:
        return direct
    parent = obj.get("parent")
    if isinstance(parent, dict):
        details = parent.get("subscription_details")
        if isinstance(details, dict):
            return _id(details.get("subscription"))
    return ""


async def _map_price(policy: AccessPolicy, price_id: str, *, service_commit: str,
                     endpoint: str) -> tuple[str | None, Outcome | None]:
    mapping, error = await _map_price_row(
        policy, price_id, service_commit=service_commit, endpoint=endpoint)
    if error is not None:
        return None, error
    return (mapping.tier if mapping is not None else None), None


async def _map_price_row(policy: AccessPolicy, price_id: str, *, service_commit: str,
                         endpoint: str) -> tuple[PriceMapping | None, Outcome | None]:
    if not price_id:
        return None, _refusal(
            PRICE_NOT_MAPPED, "the Stripe event names no Price id we can map",
            service_commit=service_commit, endpoint=endpoint)
    try:
        return policy.price(price_id), None
    except PolicyError as exc:
        return None, _refusal(
            PRICE_NOT_MAPPED, str(exc), service_commit=service_commit, endpoint=endpoint,
            detail={"price_id": price_id})


def _ledger(ledger: Any) -> Any:
    return ledger if ledger is not None else credits.UnboundLedger()


async def apply_event(event: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                      now: datetime, service_commit: str,
                      ledger: Any = None) -> Outcome:
    """Apply one verified Stripe event. Idempotent on `event.id`."""
    endpoint = "billing.stripe-webhook"
    event_id = str(event.get("id") or "")
    type_ = str(event.get("type") or "")
    ledger = _ledger(ledger)
    if not event_id:
        return _refusal(INVALID_REQUEST, "the Stripe event has no id",
                        service_commit=service_commit, endpoint=endpoint)
    if await store.seen(kv, event_id):
        return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
            "received": True, "duplicate": True, "event_id": event_id, "type": type_,
            "action": "duplicate",
        }))

    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    obj = data.get("object") if isinstance(data, dict) else {}
    if not isinstance(obj, dict):
        obj = {}

    action = "ignored"
    if type_ in PROVISION_TYPES:
        if type_.startswith("checkout.session."):
            action, error = await _apply_checkout(
                obj, kv=kv, policy=policy, now=now, ledger=ledger,
                service_commit=service_commit, endpoint=endpoint)
            if error is not None:
                return error
        else:
            action, error = await _apply_invoice_paid(
                obj, kv=kv, policy=policy, now=now, ledger=ledger,
                service_commit=service_commit, endpoint=endpoint, event_id=event_id)
            if error is not None:
                return error
    elif type_ in DOWNGRADE_TYPES:
        subscription_id = (_id(obj.get("id")) if type_ == "customer.subscription.deleted"
                           else _subscription_from_invoice(obj) or _id(obj.get("subscription")))
        if not subscription_id:
            action = "ignored"
        else:
            action = await store.set_subscription_tier(
                kv, subscription_id, policy.billing.downgrade_tier, policy=policy)
            await store.clear_monthly(kv, subscription_id, ledger=ledger)
            if action == "tier_set":
                action = "downgraded"
    elif type_ == "customer.subscription.updated":
        status = str(obj.get("status") or "")
        subscription_id = _id(obj.get("id"))
        if not subscription_id:
            action = "ignored"
        elif status in EXPIRED_STATUSES:
            action = await store.set_subscription_tier(
                kv, subscription_id, policy.billing.downgrade_tier, policy=policy)
            await store.clear_monthly(kv, subscription_id, ledger=ledger)
            if action == "tier_set":
                action = "downgraded"
        elif status == "active":
            price_id = _price_from_subscription(obj)
            if price_id:
                mapping, error = await _map_price_row(
                    policy, price_id, service_commit=service_commit, endpoint=endpoint)
                if error is not None:
                    return error
                action = await store.set_subscription_tier(
                    kv, subscription_id, mapping.tier if mapping else "", policy=policy)
                if mapping is not None and mapping.kind == "plan":
                    await store.grant_monthly(
                        kv, subscription_id, ledger=ledger, units=mapping.credits,
                        invoice_id=f"sub-active:{event_id}", plan=mapping.name)
                if action == "tier_set":
                    action = "restored"

    await store.remember(kv, event_id, type_, action, now=now, policy=policy)
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "received": True, "duplicate": False, "event_id": event_id, "type": type_,
        "action": action,
    }))


async def _apply_checkout(obj: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                          now: datetime, ledger: Any, service_commit: str,
                          endpoint: str) -> tuple[str, Outcome | None]:
    session_id = _id(obj.get("id"))
    if obj.get("payment_status") not in (None, "paid", "no_payment_required"):
        return "ignored", None
    price_id = _price_from_session(obj)
    mapping, error = await _map_price_row(
        policy, price_id, service_commit=service_commit, endpoint=endpoint)
    if error is not None:
        return "ignored", error
    assert mapping is not None
    fingerprint = _fingerprint_from_obj(obj)
    mode = str(obj.get("mode") or "")
    if mode == "payment" or mapping.kind == "pack":
        if mapping.kind != "pack":
            return "ignored", _refusal(
                PRICE_NOT_MAPPED,
                f"Stripe price {price_id!r} is not a pack; payment-mode Checkout cannot grant it",
                service_commit=service_commit, endpoint=endpoint,
                detail={"price_id": price_id})
        action = await store.record_pack_session(
            kv, session_id=session_id, customer_id=_id(obj.get("customer")),
            price_id=price_id, credits_amount=mapping.credits,
            key_fingerprint=fingerprint)
        if fingerprint:
            grant = await store.grant_pack(
                kv, fingerprint_hex=fingerprint, session_id=session_id,
                units=mapping.credits, ledger=ledger, now=now, policy=policy)
            await keys.set_tier(kv, fingerprint, mapping.tier, policy=policy)
            if grant == "granted":
                action = "credited"
        return action, None
    subscription_id = _id(obj.get("subscription"))
    if mode and mode != "subscription":
        return "ignored", None
    if not subscription_id:
        return "ignored", None
    if mapping.kind != "plan":
        return "ignored", _refusal(
            PRICE_NOT_MAPPED,
            f"Stripe price {price_id!r} is not a plan; subscription Checkout cannot grant it",
            service_commit=service_commit, endpoint=endpoint,
            detail={"price_id": price_id})
    action, record = await store.record_entitlement(
        kv, subscription_id=subscription_id,
        customer_id=_id(obj.get("customer")), price_id=price_id, tier=mapping.tier,
        session_id=session_id, now=now, policy=policy,
        pending_monthly=mapping.credits, plan_name=mapping.name,
        plan_credits=mapping.credits, key_fingerprint=fingerprint)
    grant = await store.grant_monthly(
        kv, subscription_id, ledger=ledger, units=mapping.credits,
        invoice_id=f"checkout:{session_id}", plan=mapping.name)
    if grant == "granted":
        action = "credited" if action in {"entitled", "already_entitled"} else action
    return action, None


async def _apply_invoice_paid(obj: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                              now: datetime, ledger: Any, service_commit: str,
                              endpoint: str, event_id: str) -> tuple[str, Outcome | None]:
    subscription_id = _subscription_from_invoice(obj)
    if not subscription_id:
        return "ignored", None
    price_id = _price_from_invoice(obj)
    mapping, error = await _map_price_row(
        policy, price_id, service_commit=service_commit, endpoint=endpoint)
    if error is not None:
        return "ignored", error
    assert mapping is not None
    if mapping.kind != "plan":
        return "ignored", None
    invoice_id = _id(obj.get("id")) or event_id
    fingerprint = _fingerprint_from_obj(obj)
    action, _ = await store.record_entitlement(
        kv, subscription_id=subscription_id,
        customer_id=_id(obj.get("customer")), price_id=price_id, tier=mapping.tier,
        session_id="", now=now, policy=policy,
        pending_monthly=mapping.credits, plan_name=mapping.name,
        plan_credits=mapping.credits, key_fingerprint=fingerprint)
    grant = await store.grant_monthly(
        kv, subscription_id, ledger=ledger, units=mapping.credits,
        invoice_id=invoice_id, plan=mapping.name)
    if grant == "granted":
        action = "credited"
    elif grant == "pending" and action == "entitled":
        action = "entitled"
    return action, None


async def webhook(*, payload: str, signature: str | None, secret: str | None,
                  flag: bool, kv: Any, policy: AccessPolicy, now: datetime,
                  service_commit: str, ledger: Any = None) -> Outcome:
    endpoint = "billing.stripe-webhook"
    if not secret:
        return _refusal(
            BILLING_NOT_CONFIGURED,
            "STRIPE_WEBHOOK_SECRET is not set on this deployment",
            service_commit=service_commit, endpoint=endpoint)
    try:
        billing_stripe.verify_signature(
            payload, signature, secret, now=now,
            tolerance_seconds=policy.billing.signature_tolerance_seconds)
    except SignatureError as exc:
        return _refusal(INVALID_SIGNATURE, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    if not flag:
        return _refusal(
            BILLING_NOT_ENABLED,
            "billing is wired and the signature is valid, but BILLING_ENABLED is off",
            service_commit=service_commit, endpoint=endpoint)
    if isinstance(kv, UnboundKV):
        return _refusal(
            STORE_NOT_CONFIGURED,
            "ACCESS KV is not bound; a signed event cannot be applied",
            service_commit=service_commit, endpoint=endpoint)
    try:
        event = json.loads(payload) if payload else None
    except ValueError as exc:
        return _refusal(INVALID_REQUEST, f"the body is not valid JSON: {exc}",
                        service_commit=service_commit, endpoint=endpoint)
    if not isinstance(event, dict):
        return _refusal(INVALID_REQUEST, "the Stripe event must be a JSON object",
                        service_commit=service_commit, endpoint=endpoint)
    try:
        return await apply_event(event, kv=kv, policy=policy, now=now,
                                 service_commit=service_commit, ledger=ledger)
    except StoreNotConfigured as exc:
        return _refusal(STORE_NOT_CONFIGURED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    except PolicyError as exc:
        return _refusal(PRICE_NOT_MAPPED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)


def session_id_from_request(*, query: str, payload: Any) -> str:
    parsed = parse_qs(query, keep_blank_values=False)
    for key in ("session_id", "token"):
        values = parsed.get(key) or []
        if values and values[0].strip():
            return values[0].strip()
    if isinstance(payload, dict):
        for key in ("session_id", "token"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


async def claim(*, session_id: str, flag: bool, kv: Any, policy: AccessPolicy,
                now: datetime, service_commit: str, ledger: Any = None) -> Outcome:
    endpoint = "billing.claim"
    if not flag:
        return _refusal(BILLING_NOT_ENABLED, "BILLING_ENABLED is off",
                        service_commit=service_commit, endpoint=endpoint)
    if isinstance(kv, UnboundKV):
        return _refusal(STORE_NOT_CONFIGURED, "ACCESS KV is not bound",
                        service_commit=service_commit, endpoint=endpoint)
    if not session_id:
        return _refusal(
            INVALID_REQUEST,
            "send the Checkout session id as session_id (query or JSON body)",
            service_commit=service_commit, endpoint=endpoint)
    try:
        result = await store.consume_claim(
            kv, session_id, now=now, policy=policy, ledger=_ledger(ledger))
    except StoreNotConfigured as exc:
        return _refusal(STORE_NOT_CONFIGURED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    except PolicyError as exc:
        return _refusal(PRICE_NOT_MAPPED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    if result is None:
        return _refusal(
            CLAIM_NOT_READY,
            "payment received, key not ready, retry in a few seconds",
            service_commit=service_commit, endpoint=endpoint)
    record = result.record
    if result.consumed:
        return _refusal(
            CLAIM_CONSUMED,
            "that key was already shown. Rotate with POST /v1/billing/rotate if you still hold it.",
            service_commit=service_commit, endpoint=endpoint,
            detail={"key_id": record.key_id, "tier": record.tier})
    mapping = None
    if record.price_id:
        try:
            mapping = policy.price(record.price_id)
        except PolicyError:
            mapping = None
    kind = mapping.kind if mapping is not None else (
        "pack" if record.subscription_id.startswith("pack:") else "plan")
    body: dict[str, Any] = {
        "key_id": record.key_id,
        "tier": record.tier,
        "plan": record.plan_name or (mapping.name if mapping is not None else ""),
        "credits": record.plan_credits or (mapping.credits if mapping is not None else 0),
        "kind": kind,
        "what_you_bought": what_you_buy(mapping),
        "how": "Authorization: Bearer <key>",
        "applied_to": APPLIED_NEW if result.minted else APPLIED_EXISTING,
        "result": [],
    }
    if result.minted:
        body["key"] = result.issued
        body["shown"] = "once"
        body["message"] = KEY_SHOWN_ONCE
    else:
        body["shown"] = "already-held"
        body["message"] = CREDITS_ADDED if kind == "pack" else PLAN_ATTACHED
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, body))


async def rotate(*, api_key: str | None, flag: bool, kv: Any, policy: AccessPolicy,
                 now: datetime, service_commit: str, ledger: Any = None) -> Outcome:
    endpoint = "billing.rotate"
    if not flag:
        return _refusal(BILLING_NOT_ENABLED, "BILLING_ENABLED is off",
                        service_commit=service_commit, endpoint=endpoint)
    if isinstance(kv, UnboundKV):
        return _refusal(STORE_NOT_CONFIGURED, "ACCESS KV is not bound",
                        service_commit=service_commit, endpoint=endpoint)
    key = keys.normalise(api_key)
    if key is None:
        return _refusal(
            MISSING_KEY,
            "send the current API key as Authorization: Bearer <key> to rotate it",
            service_commit=service_commit, endpoint=endpoint)
    if keys.is_sandbox(key, policy):
        return _refusal(
            INVALID_REQUEST, "sandbox keys are not stored and cannot be rotated",
            service_commit=service_commit, endpoint=endpoint)
    try:
        record = await keys.lookup(kv, key)
    except StoreNotConfigured as exc:
        return _refusal(STORE_NOT_CONFIGURED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    if record is None:
        return _refusal(INVALID_KEY, "that API key is not recognised",
                        service_commit=service_commit, endpoint=endpoint)
    if not record.active:
        return _refusal(REVOKED_KEY, "that API key has been revoked",
                        service_commit=service_commit, endpoint=endpoint)
    rotated = await store.rotate(
        kv, key, now=now, policy=policy, ledger=_ledger(ledger))
    if rotated is None:
        return _refusal(INVALID_KEY, "that API key is not recognised",
                        service_commit=service_commit, endpoint=endpoint)
    secret, issued = rotated
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "key": secret,
        "key_id": issued.key_id,
        "tier": issued.tier,
        "shown": "once",
        "revoked_key_id": record.key_id,
        "how": "Authorization: Bearer <key>",
        "result": [],
    }))


async def _bound_checkout_fingerprint(api_key: str | None, *, kv: Any,
                                      policy: AccessPolicy, service_commit: str,
                                      endpoint: str
                                      ) -> tuple[str | None, Outcome | None]:
    """Resolve a presented live key to its fingerprint, or 401. None, None = anonymous."""
    key = keys.normalise(api_key)
    if key is None:
        return None, None
    if keys.is_sandbox(key, policy):
        return None, _refusal(
            INVALID_KEY, "sandbox keys cannot buy credits",
            service_commit=service_commit, endpoint=endpoint)
    try:
        record = await keys.lookup(kv, key)
    except StoreNotConfigured as exc:
        return None, _refusal(STORE_NOT_CONFIGURED, str(exc),
                              service_commit=service_commit, endpoint=endpoint)
    if record is None:
        return None, _refusal(
            INVALID_KEY, "that API key is not recognised",
            service_commit=service_commit, endpoint=endpoint)
    if not record.active:
        return None, _refusal(
            REVOKED_KEY, "that API key has been revoked",
            service_commit=service_commit, endpoint=endpoint,
            status=HTTP_UNAUTHORIZED)
    return keys.fingerprint(key), None


def _omitted_price_refusal(*, policy: AccessPolicy, service_commit: str,
                           endpoint: str) -> Outcome:
    ids = policy.price_ids()
    if not ids:
        message = "send price_id; the tier table maps no Stripe prices"
    else:
        message = "send price_id; never guessed. valid ids: " + ", ".join(ids)
    return _refusal(
        INVALID_REQUEST, message, service_commit=service_commit, endpoint=endpoint,
        detail={"valid_price_ids": ids})


async def checkout(*, payload: Any, flag: bool, secret: str | None, origin: str,
                   kv: Any, policy: AccessPolicy, service_commit: str,
                   http: Any, api_key: str | None = None) -> Outcome:
    endpoint = "billing.checkout"
    if not flag:
        return _refusal(BILLING_NOT_ENABLED, "BILLING_ENABLED is off",
                        service_commit=service_commit, endpoint=endpoint)
    if not secret:
        return _refusal(
            BILLING_NOT_CONFIGURED,
            "STRIPE_SECRET_KEY is not set on this deployment",
            service_commit=service_commit, endpoint=endpoint)
    if isinstance(kv, UnboundKV):
        return _refusal(STORE_NOT_CONFIGURED, "ACCESS KV is not bound",
                        service_commit=service_commit, endpoint=endpoint)
    if payload in (None, ""):
        payload = {}
    if not isinstance(payload, dict):
        return _refusal(INVALID_REQUEST, "the body must be a JSON object or empty",
                        service_commit=service_commit, endpoint=endpoint)
    stray = sorted(set(payload) - {"price_id"})
    if stray:
        return _refusal(
            INVALID_REQUEST, f"unknown field(s): {', '.join(stray)}",
            service_commit=service_commit, endpoint=endpoint,
            detail={"fields": stray, "accepted": ["price_id"]})
    fingerprint, key_error = await _bound_checkout_fingerprint(
        api_key, kv=kv, policy=policy, service_commit=service_commit,
        endpoint=endpoint)
    if key_error is not None:
        return key_error
    price_id = payload.get("price_id")
    if price_id is None or price_id == "":
        return _omitted_price_refusal(
            policy=policy, service_commit=service_commit, endpoint=endpoint)
    if not isinstance(price_id, str):
        return _refusal(INVALID_REQUEST, "price_id must be a string",
                        service_commit=service_commit, endpoint=endpoint)
    try:
        mapping = policy.price(price_id)
        tier = mapping.tier
        policy.tier(tier)
    except PolicyError as exc:
        return _refusal(PRICE_NOT_MAPPED, str(exc),
                        service_commit=service_commit, endpoint=endpoint,
                        detail={"price_id": price_id})
    success_url = origin.rstrip("/") + policy.billing.success_path
    if "{CHECKOUT_SESSION_ID}" not in success_url:
        success_url += ("&" if "?" in success_url else "?") + "session_id={CHECKOUT_SESSION_ID}"
    try:
        session = await billing_stripe.create_checkout_session(
            secret=secret, price_id=price_id, success_url=success_url,
            cancel_url=policy.billing.cancel_url, terms_url=policy.billing.terms_url,
            http=http, mode=mapping.checkout_mode,
            key_fingerprint=fingerprint or "")
    except RuntimeError as exc:
        return _refusal(STRIPE_UNAVAILABLE, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    extra: dict[str, Any] = {
        "url": session["url"],
        "session_id": session["id"],
        "tier": tier,
        "kind": mapping.kind,
        "name": mapping.name,
        "credits": mapping.credits,
        "price_id": price_id,
        "placeholder": mapping.placeholder,
        "what_you_buy": what_you_buy(mapping),
        "terms_url": policy.billing.terms_url,
        "applied_to": APPLIED_EXISTING if fingerprint else APPLIED_NEW,
        "result": [],
    }
    if fingerprint:
        extra["key_id"] = fingerprint[:keys.KEY_ID_LENGTH]
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, extra))


def is_form_post(content_type: str | None, raw: str) -> bool:
    """True when a Checkout body is the `/pricing` HTML form, not JSON (MODEL-105).

    Both conditions, so no JSON caller moves: `curl -d '{…}'` sends a JSON body
    under the form content type, and an empty body keeps today's JSON answer.
    """
    media = (content_type or "").split(";", 1)[0].strip().lower()
    if media != FORM_CONTENT_TYPE or not raw.strip():
        return False
    try:
        json.loads(raw)
    except ValueError:
        return True
    return False


async def checkout_form(*, raw: str, flag: bool, secret: str | None, origin: str,
                        kv: Any, policy: AccessPolicy, service_commit: str,
                        http: Any) -> Outcome:
    """The `/pricing` buy button: a form post answered with 303 to Stripe (MODEL-105).

    Anonymous Checkout: no key is bound, so claim mints one. Buying onto an
    existing key stays the JSON call with the key presented. Every refusal is
    the JSON path's own, and none of them carries a `Location`.
    """
    endpoint = "billing.checkout"
    if not flag:
        return _refusal(BILLING_NOT_ENABLED, "BILLING_ENABLED is off",
                        service_commit=service_commit, endpoint=endpoint)
    fields = parse_qs(raw, keep_blank_values=True)
    repeated = sorted(name for name, values in fields.items() if len(values) > 1)
    if repeated:
        return _refusal(
            INVALID_REQUEST, f"repeated form field(s): {', '.join(repeated)}",
            service_commit=service_commit, endpoint=endpoint,
            detail={"fields": repeated, "accepted": ["price_id"]})
    payload = {name: values[0] for name, values in fields.items()}
    price_id = payload.get("price_id")
    if price_id and price_id in policy.billing.prices:
        if policy.billing.prices[price_id].placeholder:
            return _refusal(
                PRICE_NOT_MAPPED, f"{price_id} is a placeholder Price; not for sale",
                service_commit=service_commit, endpoint=endpoint,
                detail={"price_id": price_id})
    outcome = await checkout(
        payload=payload, flag=flag, secret=secret, origin=origin, kv=kv,
        policy=policy, service_commit=service_commit, http=http, api_key=None)
    if outcome.status != HTTP_OK:
        return outcome
    url = outcome.body.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        return _refusal(STRIPE_UNAVAILABLE, "Stripe returned no https Checkout URL",
                        service_commit=service_commit, endpoint=endpoint)
    return Outcome(HTTP_SEE_OTHER, outcome.body, {"location": url})


def now_utc() -> datetime:
    return datetime.now(UTC)


def query_string(url: str) -> str:
    return urlparse(url).query
