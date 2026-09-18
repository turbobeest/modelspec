"""Stripe Checkout, webhook, claim and rotation (MODEL-73).

Hosted Checkout collects the card on Stripe's origin. This module never sees
card data. It verifies webhook signatures in process (HMAC-SHA256 over
`t.payload`), records the paid entitlement, and mints a key at claim — the
plaintext is returned once and never stored. KV writes go through
`access_billing`; this file decides.
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
from access_config import AccessPolicy, PolicyError
from access_kv import StoreNotConfigured, UnboundKV
from billing_stripe import SignatureError

HTTP_OK = 200
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
    "live rank access at the mapped tier's configured limits. It does not "
    "include policy-check determinations."
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
             detail: dict[str, Any] | None = None) -> Outcome:
    body = _envelope(endpoint, service_commit, {
        "error": {"code": code, "message": message, **(detail or {})},
        "result": [],
    })
    return Outcome(REFUSALS[code], body)


def _id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    if value is None:
        return ""
    return str(value)


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
    meta = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    return str(meta.get("modelspec_price_id") or "")


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
    if not price_id:
        return None, _refusal(
            PRICE_NOT_MAPPED, "the Stripe event names no Price id we can map to a tier",
            service_commit=service_commit, endpoint=endpoint)
    try:
        return policy.tier_for_price(price_id), None
    except PolicyError as exc:
        return None, _refusal(
            PRICE_NOT_MAPPED, str(exc), service_commit=service_commit, endpoint=endpoint,
            detail={"price_id": price_id})


async def apply_event(event: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                      now: datetime, service_commit: str) -> Outcome:
    """Apply one verified Stripe event. Idempotent on `event.id`."""
    endpoint = "billing.stripe-webhook"
    event_id = str(event.get("id") or "")
    type_ = str(event.get("type") or "")
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
            subscription_id = _id(obj.get("subscription"))
            session_id = _id(obj.get("id"))
            if obj.get("mode") and obj.get("mode") != "subscription":
                action = "ignored"
            elif obj.get("payment_status") not in (None, "paid", "no_payment_required"):
                action = "ignored"
            elif not subscription_id:
                action = "ignored"
            else:
                price_id = _price_from_session(obj)
                tier, error = await _map_price(policy, price_id, service_commit=service_commit,
                                               endpoint=endpoint)
                if error is not None:
                    return error
                action, _ = await store.record_entitlement(
                    kv, subscription_id=subscription_id,
                    customer_id=_id(obj.get("customer")), price_id=price_id, tier=tier or "",
                    session_id=session_id, now=now, policy=policy)
        else:
            subscription_id = _subscription_from_invoice(obj)
            if not subscription_id:
                action = "ignored"
            else:
                price_id = _price_from_invoice(obj)
                tier, error = await _map_price(policy, price_id, service_commit=service_commit,
                                               endpoint=endpoint)
                if error is not None:
                    return error
                action, _ = await store.record_entitlement(
                    kv, subscription_id=subscription_id,
                    customer_id=_id(obj.get("customer")), price_id=price_id, tier=tier or "",
                    session_id="", now=now, policy=policy)
    elif type_ in DOWNGRADE_TYPES:
        subscription_id = (_id(obj.get("id")) if type_ == "customer.subscription.deleted"
                           else _subscription_from_invoice(obj) or _id(obj.get("subscription")))
        if not subscription_id:
            action = "ignored"
        else:
            action = await store.set_subscription_tier(
                kv, subscription_id, policy.billing.downgrade_tier, policy=policy)
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
            if action == "tier_set":
                action = "downgraded"
        elif status == "active":
            price_id = _price_from_subscription(obj)
            if price_id:
                tier, error = await _map_price(policy, price_id, service_commit=service_commit,
                                               endpoint=endpoint)
                if error is not None:
                    return error
                action = await store.set_subscription_tier(
                    kv, subscription_id, tier or "", policy=policy)
                if action == "tier_set":
                    action = "restored"

    await store.remember(kv, event_id, type_, action, now=now, policy=policy)
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "received": True, "duplicate": False, "event_id": event_id, "type": type_,
        "action": action,
    }))


async def webhook(*, payload: str, signature: str | None, secret: str | None,
                  flag: bool, kv: Any, policy: AccessPolicy, now: datetime,
                  service_commit: str) -> Outcome:
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
                                 service_commit=service_commit)
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
                now: datetime, service_commit: str) -> Outcome:
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
        result = await store.consume_claim(kv, session_id, now=now, policy=policy)
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
    secret, record = result
    if not secret:
        return _refusal(
            CLAIM_CONSUMED,
            "that key was already shown. Rotate with POST /v1/billing/rotate if you still hold it.",
            service_commit=service_commit, endpoint=endpoint,
            detail={"key_id": record.key_id, "tier": record.tier})
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "key": secret,
        "key_id": record.key_id,
        "tier": record.tier,
        "shown": "once",
        "what_you_bought": WHAT_YOU_BUY,
        "how": "Authorization: Bearer <key>",
        "result": [],
    }))


async def rotate(*, api_key: str | None, flag: bool, kv: Any, policy: AccessPolicy,
                 now: datetime, service_commit: str) -> Outcome:
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
    rotated = await store.rotate(kv, key, now=now, policy=policy)
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


async def checkout(*, payload: Any, flag: bool, secret: str | None, origin: str,
                   kv: Any, policy: AccessPolicy, service_commit: str,
                   http: Any) -> Outcome:
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
    price_id = payload.get("price_id")
    if price_id is None or price_id == "":
        try:
            price_id = policy.default_price_id()
        except PolicyError as exc:
            return _refusal(INVALID_REQUEST, str(exc),
                            service_commit=service_commit, endpoint=endpoint)
    if not isinstance(price_id, str):
        return _refusal(INVALID_REQUEST, "price_id must be a string",
                        service_commit=service_commit, endpoint=endpoint)
    try:
        tier = policy.tier_for_price(price_id)
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
            http=http)
    except RuntimeError as exc:
        return _refusal(STRIPE_UNAVAILABLE, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "url": session["url"],
        "session_id": session["id"],
        "tier": tier,
        "price_id": price_id,
        "placeholder": policy.billing.prices[price_id].placeholder,
        "what_you_buy": WHAT_YOU_BUY,
        "terms_url": policy.billing.terms_url,
        "result": [],
    }))


def now_utc() -> datetime:
    return datetime.now(UTC)


def query_string(url: str) -> str:
    return urlparse(url).query
