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
import billing_reversals
import billing_stripe
import credits
import sale_alerts
from access_config import AccessPolicy, PolicyError, PriceMapping, friends_price
from access_kv import MemoryKV, StoreNotConfigured, UnboundKV
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
PURCHASE_REFUNDED = "purchase_refunded"

REFUSALS: dict[str, int] = {
    INVALID_SIGNATURE: HTTP_BAD_REQUEST,
    INVALID_REQUEST: HTTP_BAD_REQUEST,
    MISSING_KEY: HTTP_UNAUTHORIZED,
    INVALID_KEY: HTTP_UNAUTHORIZED,
    REVOKED_KEY: HTTP_FORBIDDEN,
    CLAIM_NOT_READY: HTTP_CONFLICT,
    CLAIM_CONSUMED: HTTP_GONE,
    PURCHASE_REFUNDED: HTTP_GONE,
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
#: MODEL-106. A refund or a dispute acts on the purchase's credits.
REVERSAL_TYPES = billing_reversals.TYPES
#: Every event type the webhook acts on. The Stripe destinations (live and
#: sandbox) must subscribe to each; `docs/billing.md` names each.
HANDLED_TYPES = (PROVISION_TYPES | DOWNGRADE_TYPES | REVERSAL_TYPES
                 | frozenset({"customer.subscription.updated"}))

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
    if mapping.tier == "friends":
        return "Friends & Family: live API access subject to the friends tier's burst limit."
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


def _line_price_id(row: dict[str, Any]) -> str:
    price = row.get("price")
    if isinstance(price, dict) and price.get("id"):
        return str(price["id"])
    if isinstance(price, str) and price:
        return price
    # Since API 2025-03-31.basil a line names its Price here instead.
    pricing = row.get("pricing")
    details = pricing.get("price_details") if isinstance(pricing, dict) else None
    if isinstance(details, dict):
        return _id(details.get("price"))
    return ""


def _metadata_price(obj: dict[str, Any]) -> str:
    meta = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    found = str(meta.get("modelspec_price_id") or "")
    if found:
        return found
    # Checkout's subscription_data metadata reaches a basil+ invoice here.
    parent = obj.get("parent")
    sub_details = parent.get("subscription_details") if isinstance(parent, dict) else None
    if isinstance(sub_details, dict):
        return str(_meta(sub_details).get("modelspec_price_id") or "")
    return ""


def _line_is_proration(row: dict[str, Any]) -> bool:
    if row.get("proration"):
        return True
    # Since API 2025-03-31.basil the flag sits under the line's parent.
    parent = row.get("parent")
    if isinstance(parent, dict):
        for key in ("subscription_item_details", "invoice_item_details"):
            details = parent.get(key)
            if isinstance(details, dict) and details.get("proration"):
                return True
    return False


def _line_amount(row: dict[str, Any]) -> int:
    try:
        return int(row.get("amount") or 0)
    except (TypeError, ValueError):
        return 0


def _price_from_invoice(obj: dict[str, Any], metered: set[str]) -> str:
    """The plan Price this invoice bills, or "" when it names none.

    The Price billed wins over checkout metadata, so a plan changed in Stripe
    after checkout grants what was paid for. The metered overage line is
    skipped. A proration invoice credits the old plan (a negative line) and
    charges the new one: the charge wins, and a regular line wins over a
    proration line. A billed Price that is not mapped is returned as is, so
    the caller refuses it instead of falling back to stale metadata. Metadata
    is used only when no line names a plan Price.
    """
    lines = obj.get("lines")
    rows = lines.get("data") if isinstance(lines, dict) else []
    billed: list[tuple[str, dict[str, Any]]] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            price_id = _line_price_id(row)
            if price_id and price_id not in metered:
                billed.append((price_id, row))
    if not billed:
        return _metadata_price(obj)
    charges = [entry for entry in billed if _line_amount(entry[1]) >= 0]
    regular = [entry for entry in charges if not _line_is_proration(entry[1])]
    if regular:
        return regular[0][0]
    if charges:
        return charges[-1][0]
    return billed[-1][0]


def _price_from_subscription(obj: dict[str, Any], metered: set[str]) -> str:
    """The plan Price on a subscription's items, else its metadata.

    The metered overage item is skipped. An item Price that is not mapped is
    returned as is, so the caller refuses it rather than trusting metadata.
    """
    items = obj.get("items")
    rows = items.get("data") if isinstance(items, dict) else []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            price_id = _line_price_id(row)
            if price_id and price_id not in metered:
                return price_id
    return _metadata_price(obj)


def _metered_price_ids(policy: AccessPolicy) -> set[str]:
    """Overage Prices. Their lines bill usage, never name the plan."""
    return {row.overage.price_id for row in policy.billing.prices.values()
            if row.overage is not None and row.overage.price_id}


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
                         endpoint: str, obj: dict[str, Any] | None = None
                         ) -> tuple[PriceMapping | None, Outcome | None]:
    if not price_id:
        return None, _refusal(
            PRICE_NOT_MAPPED, "the Stripe event names no Price id we can map",
            service_commit=service_commit, endpoint=endpoint)
    try:
        mapping = policy.price(price_id)
        if (mapping.kind == "plan" and obj is not None
                and obj.get("mode") != "payment" and _friends_promotion(obj, policy)):
            return friends_price(price_id), None
        return mapping, None
    except PolicyError as exc:
        return None, _refusal(
            PRICE_NOT_MAPPED, str(exc), service_commit=service_commit, endpoint=endpoint,
            detail={"price_id": price_id})


def _promotion_coupon(promotion: dict[str, Any]) -> Any:
    source = promotion.get("promotion")
    return source.get("coupon") if isinstance(source, dict) else promotion.get("coupon")


def _friends_promotion(obj: dict[str, Any], policy: AccessPolicy) -> bool:
    prefix = policy.billing.friends_promotion_code_prefix
    if not prefix:
        return False
    discounts = obj.get("discounts")
    for discount in discounts if isinstance(discounts, list) else []:
        promo = discount.get("promotion_code") if isinstance(discount, dict) else None
        if not isinstance(promo, dict):
            continue
        coupon = _promotion_coupon(promo)
        if (str(promo.get("code") or "").casefold().startswith(prefix.casefold())
                and isinstance(coupon, dict) and coupon.get("percent_off") == 100
                and coupon.get("duration") == "forever"):
            return True
    return False


async def _resolve_friends_event(event: dict[str, Any], *, policy: AccessPolicy,
                                 secret: str | None, http: Any) -> dict[str, Any]:
    """Expand only signed entitlement events, and only with friends configured."""
    cfg = policy.billing
    if not (cfg.friends_price_ids or cfg.friends_promotion_code_prefix):
        return event
    kind = event.get("type")
    data = event.get("data")
    obj = data.get("object") if isinstance(data, dict) else None
    if not isinstance(obj, dict):
        return event
    if kind == "customer.subscription.updated" and obj.get("status") == "active":
        resource = "subscriptions"
    elif kind == "invoice.paid":
        resource = "invoices"
    elif kind in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        if obj.get("payment_status") not in (None, "paid", "no_payment_required"):
            return event
        resource = "checkout/sessions"
    else:
        return event
    if resource == "checkout/sessions" and not _price_from_session(obj):
        expanded = await billing_stripe.retrieve(
            resource=resource, identifier=_id(obj), expand=["line_items"], secret=secret, http=http)
        obj = {**obj, "line_items": expanded.get("line_items"),
               "discounts": expanded.get("discounts", obj.get("discounts"))}
    discounts = obj.get("discounts")
    if (obj.get("mode") != "payment" and cfg.friends_promotion_code_prefix
            and isinstance(discounts, list)):
        if any(isinstance(item, str) for item in discounts):
            expanded = await billing_stripe.retrieve(
                resource=resource, identifier=_id(obj), expand=["discounts.promotion_code"],
                secret=secret, http=http)
            discounts = expanded.get("discounts")
            if not isinstance(discounts, list) or any(not isinstance(d, dict) for d in discounts):
                raise RuntimeError("Stripe entitlement read did not expand discounts")
        resolved = []
        for discount in discounts:
            if not isinstance(discount, dict):
                continue
            promo = discount.get("promotion_code")
            if isinstance(promo, str) or (isinstance(promo, dict)
                                          and not isinstance(_promotion_coupon(promo), dict)):
                promo = await billing_stripe.retrieve(
                    resource="promotion_codes", identifier=_id(promo),
                    expand=["promotion.coupon"], secret=secret, http=http)
                if not isinstance(_promotion_coupon(promo), dict):
                    raise RuntimeError(
                        "Stripe entitlement read did not expand the promotion coupon")
            resolved.append({**discount, "promotion_code": promo})
        obj = {**obj, "discounts": resolved}
    return {**event, "data": {**event.get("data", {}), "object": obj}}


def _ledger(ledger: Any) -> Any:
    return ledger if ledger is not None else credits.UnboundLedger()


def _billing_ledger(ledger: Any, kv: Any) -> Any:
    if ledger is None and isinstance(kv, MemoryKV):
        if not hasattr(kv, "billing_ledger"):
            kv.billing_ledger = credits.MemoryLedger()
        return kv.billing_ledger
    return _ledger(ledger)


_SALE_ACTIONS = frozenset({"entitled", "credited"})
_TERMINAL_SUBSCRIPTION_STATUSES = frozenset({"canceled", "incomplete_expired"})


def _cancellation_time(stored: store.SubscriptionRecord) -> int:
    """Terminal time on the subscription row. Older rows use the stored event time."""
    return int(stored.canceled_at or stored.subscription_updated_at or 0)


def _timestamp(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _invoice_period(obj: dict[str, Any], policy: AccessPolicy) -> tuple[int, int]:
    price_id = _price_from_invoice(obj, _metered_price_ids(policy))
    lines = obj.get("lines")
    rows = lines.get("data") if isinstance(lines, dict) else []
    if isinstance(rows, list):
        matching = [row for row in rows if isinstance(row, dict)
                    and _line_price_id(row) == price_id and _line_amount(row) >= 0]
        regular = [row for row in matching if not _line_is_proration(row)]
        for row in regular or matching:
            period = row.get("period")
            if isinstance(period, dict):
                start, end = _timestamp(period.get("start")), _timestamp(period.get("end"))
                if start or end:
                    return start, end
    return _timestamp(obj.get("period_start")), _timestamp(obj.get("period_end"))


def _event_subscription(type_: str, obj: dict[str, Any]) -> str:
    if type_.startswith("customer.subscription."):
        return _id(obj.get("id"))
    if type_.startswith("invoice."):
        return _subscription_from_invoice(obj)
    return ""


def _stale_entitlement_event(type_: str, obj: dict[str, Any], *, created: int,
                              stored: store.SubscriptionRecord | None,
                              policy: AccessPolicy) -> bool:
    if stored is None:
        return False
    terminal = stored.subscription_status in _TERMINAL_SUBSCRIPTION_STATUSES
    if type_.startswith("customer.subscription."):
        return bool(created and stored.subscription_updated_at
                    and created < stored.subscription_updated_at)
    if type_ in {"invoice.paid", "invoice.payment_failed"}:
        period = _invoice_period(obj, policy)
        # Cancellation time is canceled_at, else the stored subscription time
        # on a row that has no canceled_at. Compare the period start to that
        # time. An invoice with no period end stays stale.
        cancelled = _cancellation_time(stored) if terminal else 0
        if cancelled and credits._period_predates_cancellation(period[0], period[1], cancelled):
            return True
        current_period = (stored.invoice_period_start, stored.invoice_period_end)
        # A failed invoice with no period at all is not a newer period. When a
        # paid period is already stored, leave that allowance alone. A clear
        # with no period (rotation of an inactive subscription) is not this path.
        if (type_ == "invoice.payment_failed" and not any(period)
                and stored.invoice_paid and any(current_period)):
            return True
        if any(period) and any(current_period):
            stored_end = current_period[1]
            if (type_ == "invoice.paid" and period[1] and stored_end
                    and period[1] < stored_end):
                return True
            if (type_ == "invoice.payment_failed" and period[1] and stored_end
                    and period[1] <= stored_end):
                return True
            if (_id(obj.get("id")) == stored.invoice_id and stored.invoice_paid
                    and type_ == "invoice.payment_failed"):
                return True
        return False
    return terminal


_ENTITLEMENT_PASSES = 4


class EntitlementUnsettled(RuntimeError):
    """The key tier was still changing after the bounded copies.

    The webhook fails, so Stripe retries the event.
    """


def _plan_tier(policy: AccessPolicy, stored: store.SubscriptionRecord) -> str:
    """Tier for an entitled key when the event carries no mapping.

    The row's tier stands when it is set and is not the downgrade tier. A
    promotion-code Friends row is stored on an ordinary paid Price, so the
    Price is used only when the row's tier is empty or the downgrade tier.
    """
    downgrade = policy.billing.downgrade_tier
    if stored.tier and stored.tier != downgrade:
        return stored.tier
    if stored.price_id:
        try:
            tier = policy.price(stored.price_id).tier
        except PolicyError:
            tier = ""
        if tier and tier != downgrade:
            return tier
    return "paid"


def _entitled_tier(policy: AccessPolicy, stored: store.SubscriptionRecord,
                   mapping_tier: str = "") -> str:
    """The event's mapping wins. Otherwise the row, then the Price."""
    downgrade = policy.billing.downgrade_tier
    if mapping_tier and mapping_tier != downgrade:
        return mapping_tier
    return _plan_tier(policy, stored)


async def _sync_entitlement_tier(kv: Any, subscription_id: str, *, ledger: Any,
                                 policy: AccessPolicy, mapping_tier: str = "") -> str:
    """Copy the ledger's entitlement onto the key, then read it again.

    Another handler may accept an allowance write between the read and the
    key write. A changed generation means write the new tier. Four passes,
    then raise.
    """
    paid_tier = ""
    for _ in range(_ENTITLEMENT_PASSES):
        stored = await store.load_subscription(kv, subscription_id)
        if stored is None or not stored.key_fingerprint or ledger is None:
            return "no_key"
        if not paid_tier:
            paid_tier = _entitled_tier(policy, stored, mapping_tier)
        holder = credits.holder_from_fingerprint(stored.key_fingerprint)
        try:
            view = await ledger.entitlement_view(holder)
        except credits.StoreNotConfigured:
            return "store_unbound"
        generation = int(view["generation"])
        tier = paid_tier if view["entitled"] else policy.billing.downgrade_tier
        await store.set_subscription_tier(
            kv, subscription_id, tier, policy=policy, align_key=True)
        try:
            again = await ledger.entitlement_view(holder)
        except credits.StoreNotConfigured:
            return "store_unbound"
        if int(again["generation"]) == generation:
            return "downgraded" if not view["entitled"] else "entitled"
    raise EntitlementUnsettled("the entitlement tier did not settle")


# A rejected grant, a grant for another holder, or a grant with nothing to
# copy leaves the key tier alone. Replay copies the ledger's current tier.
_GRANT_SKIPS_TIER = frozenset({
    "", "stale", "conflict", "zero", "pending", "no_key", "store_unbound", "skipped",
})


async def _copy_grant_tier(kv: Any, subscription_id: str, *, ledger: Any,
                           policy: AccessPolicy, grant: str,
                           mapping_tier: str = "") -> None:
    """Copy the ledger tier after a grant the row's key can hold."""
    if grant in _GRANT_SKIPS_TIER or isinstance(ledger, credits.UnboundLedger):
        return
    stored = await store.load_subscription(kv, subscription_id)
    if stored is not None and stored.key_fingerprint and ledger is not None:
        try:
            view = await ledger.entitlement_view(
                credits.holder_from_fingerprint(stored.key_fingerprint))
        except credits.StoreNotConfigured:
            view = None
        # Generation zero and no stored cancellation: the ledger has not
        # recorded an allowance for this key. A replay must not downgrade it.
        if (isinstance(view, dict) and not view.get("entitled")
                and int(view.get("generation") or 0) == 0
                and int(view.get("canceled_at") or 0) == 0):
            return
    await _sync_entitlement_tier(
        kv, subscription_id, ledger=ledger, policy=policy,
        mapping_tier=mapping_tier)


async def _settle_downgrade(kv: Any, subscription_id: str, *, ledger: Any,
                            policy: AccessPolicy, cleared: str) -> str:
    """Write a tier only after the ledger accepts the clear."""
    if cleared == "stale":
        return "ignored"
    if cleared != "cleared":
        if cleared == "store_unbound":
            wrote = await store.set_subscription_tier(
                kv, subscription_id, policy.billing.downgrade_tier, policy=policy)
            return "downgraded" if wrote == "tier_set" else wrote
        return cleared
    settled = await _sync_entitlement_tier(
        kv, subscription_id, ledger=ledger, policy=policy)
    if settled == "entitled":
        return "ignored"
    if settled == "downgraded":
        return "downgraded"
    if settled == "no_key":
        wrote = await store.set_subscription_tier(
            kv, subscription_id, policy.billing.downgrade_tier, policy=policy)
        if wrote in {"tier_set", "unchanged"}:
            return "downgraded"
        return wrote
    return settled


def _sale_notice(type_: str, obj: dict[str, Any], policy: AccessPolicy
                 ) -> tuple[str, int] | None:
    """Catalog name and USD for a provision event that recorded a sale."""
    if type_.startswith("checkout.session."):
        if obj.get("payment_status") not in (None, "paid", "no_payment_required"):
            return None
        price_id = _price_from_session(obj)
    else:
        price_id = _price_from_invoice(obj, _metered_price_ids(policy))
    if not price_id:
        return None
    try:
        mapping = policy.price(price_id)
    except PolicyError:
        return None
    name = mapping.name
    if (mapping.kind == "plan" and mapping.interval == "month"
            and "month" not in name.casefold()):
        name = f"{name} monthly"
    return name, mapping.usd


async def apply_event(event: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                      now: datetime, service_commit: str,
                      ledger: Any = None, env: Any = None,
                      alert_ctx: Any = None) -> Outcome:
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

    subscription_id = _event_subscription(type_, obj)
    stored = await store.load_subscription(kv, subscription_id) if subscription_id else None
    created = _timestamp(event.get("created"))
    stale = _stale_entitlement_event(
        type_, obj, created=created, stored=stored, policy=policy)
    action = "ignored"
    extra: dict[str, Any] = {}
    if stale:
        pass
    elif type_ in REVERSAL_TYPES:
        try:
            action, extra = await billing_reversals.apply(
                type_, obj, ledger=ledger, now=now)
        except credits.StoreNotConfigured as exc:
            # Not remembered: Stripe retries, and the retry applies once bound.
            return _refusal(STORE_NOT_CONFIGURED, str(exc),
                            service_commit=service_commit, endpoint=endpoint)
    elif type_ in PROVISION_TYPES:
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
        elif type_ == "invoice.payment_failed":
            _period_start, period_end = _invoice_period(obj, policy)
            cleared = await store.clear_monthly(
                kv, subscription_id, ledger=ledger, period_end=period_end)
            action = await _settle_downgrade(
                kv, subscription_id, ledger=ledger, policy=policy,
                cleared=cleared)
        else:
            canceled_at = _timestamp(obj.get("canceled_at")) or created
            cleared = await store.clear_monthly(
                kv, subscription_id, ledger=ledger, watermark=canceled_at)
            action = await _settle_downgrade(
                kv, subscription_id, ledger=ledger, policy=policy,
                cleared=cleared)
    elif type_ == "customer.subscription.updated":
        status = str(obj.get("status") or "")
        subscription_id = _id(obj.get("id"))
        if not subscription_id:
            action = "ignored"
        elif status in EXPIRED_STATUSES:
            watermark = (_timestamp(obj.get("canceled_at")) or created
                         if status in _TERMINAL_SUBSCRIPTION_STATUSES else 0)
            cleared = await store.clear_monthly(
                kv, subscription_id, ledger=ledger, watermark=watermark)
            action = await _settle_downgrade(
                kv, subscription_id, ledger=ledger, policy=policy,
                cleared=cleared)
        elif status == "active":
            price_id = _price_from_subscription(obj, _metered_price_ids(policy))
            if price_id:
                mapping, error = await _map_price_row(
                    policy, price_id, service_commit=service_commit, endpoint=endpoint, obj=obj)
                if error is not None:
                    return error
                # Restore access only. Credits come from a paid invoice or
                # Checkout: an update (a plan change, a coupon, a cancel
                # toggle) is not a payment, and an upgrade's prorated invoice
                # may still be unpaid.
                action = await store.set_subscription_tier(
                    kv, subscription_id, mapping.tier if mapping else "", policy=policy)
                if action == "tier_set":
                    action = "restored"

    if subscription_id and not stale and action != "ignored":
        if type_ in {"invoice.payment_failed", "invoice.paid"}:
            period_start, period_end = _invoice_period(obj, policy)
            await store.record_chronology(
                kv, subscription_id, now=now, policy=policy,
                customer_id=_id(obj.get("customer")),
                invoice_id=_id(obj.get("id")) or event_id,
                period_start=period_start, period_end=period_end,
                paid=type_ == "invoice.paid")
        elif type_ == "customer.subscription.deleted" or (
                type_ == "customer.subscription.updated"
                and obj.get("status") in EXPIRED_STATUSES | {"active"}):
            status = ("canceled" if type_ == "customer.subscription.deleted"
                      else str(obj.get("status")))
            terminal_at = (_timestamp(obj.get("canceled_at")) or created
                           if status in _TERMINAL_SUBSCRIPTION_STATUSES else 0)
            await store.record_chronology(
                kv, subscription_id, now=now, policy=policy,
                customer_id=_id(obj.get("customer")),
                subscription_status=status, updated_at=created,
                canceled_at=terminal_at)

    await store.remember(kv, event_id, type_, action, now=now, policy=policy)
    if action in _SALE_ACTIONS and type_ in PROVISION_TYPES:
        notice = _sale_notice(type_, obj, policy)
        if notice is not None:
            sale_alerts.notify_sale(
                env, alert_ctx, channel="card", product=notice[0],
                amount_usd=notice[1], ref=event_id)
    return Outcome(HTTP_OK, _envelope(endpoint, service_commit, {
        "received": True, "duplicate": False, "event_id": event_id, "type": type_,
        "action": action, **extra,
    }))


async def _apply_checkout(obj: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                          now: datetime, ledger: Any, service_commit: str,
                          endpoint: str) -> tuple[str, Outcome | None]:
    session_id = _id(obj.get("id"))
    if obj.get("payment_status") not in (None, "paid", "no_payment_required"):
        return "ignored", None
    price_id = _price_from_session(obj)
    mapping, error = await _map_price_row(
        policy, price_id, service_commit=service_commit, endpoint=endpoint, obj=obj)
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
        payment_intent = _id(obj.get("payment_intent"))
        await _expect_pack(ledger, session_id, mapping.credits, payment_intent)
        if fingerprint:
            grant = await store.grant_pack(
                kv, fingerprint_hex=fingerprint, session_id=session_id,
                units=mapping.credits, ledger=ledger, now=now, policy=policy,
                tx=payment_intent)
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
    existing = await store.load_subscription(kv, subscription_id)
    initial_invoice = _id(obj.get("invoice"))
    recovers_initial = (existing is not None and initial_invoice
                        and initial_invoice == existing.invoice_id
                        and not existing.invoice_paid)
    if existing is not None and (
            (existing.invoice_id and not recovers_initial) or
            existing.subscription_status in _TERMINAL_SUBSCRIPTION_STATUSES):
        linked = await store.link_current_checkout(
            kv, existing, session_id=session_id, key_fingerprint=fingerprint,
            policy=policy, ledger=ledger)
        if linked == "stale":
            return "ignored", None
        await _copy_grant_tier(
            kv, subscription_id, ledger=ledger, policy=policy, grant=linked,
            mapping_tier=mapping.tier)
        if linked == "granted":
            return "credited", None
        return ("already_entitled" if existing.status == store.STATUS_ACTIVE
                else "ignored"), None
    invoice_id = initial_invoice or f"checkout:{session_id}"
    # Ask the ledger before any row or key write. A stale no-period grant for
    # the cancelled subscription must leave both as they were.
    probed = None
    if (fingerprint and ledger is not None
            and not isinstance(ledger, credits.UnboundLedger)
            and await keys.lookup_fingerprint(kv, fingerprint) is not None):
        try:
            probed = await ledger.set_monthly(
                credits.holder_from_fingerprint(fingerprint),
                mapping.credits, invoice_id, mapping.name,
                _id(obj.get("customer")), subscription_id=subscription_id)
        except credits.StoreNotConfigured:
            probed = None
        if isinstance(probed, dict):
            probed = credits.CreditResult.from_json(probed)
        if probed is not None and probed.reason == "stale":
            return "ignored", None
    action, record = await store.record_entitlement(
        kv, subscription_id=subscription_id,
        customer_id=_id(obj.get("customer")), price_id=price_id, tier=mapping.tier,
        session_id=session_id, now=now, policy=policy,
        pending_monthly=mapping.credits,
        pending_invoice_id=invoice_id,
        plan_name=mapping.name, plan_credits=mapping.credits, key_fingerprint=fingerprint)
    grant = await store.grant_monthly(
        kv, subscription_id, ledger=ledger, units=mapping.credits,
        invoice_id=invoice_id, plan=mapping.name)
    if (probed is not None and probed.credited) or grant == "granted":
        action = "credited" if action in {"entitled", "already_entitled"} else action
    await _copy_grant_tier(
        kv, subscription_id, ledger=ledger, policy=policy,
        grant="granted" if probed is not None and probed.credited else grant,
        mapping_tier=mapping.tier)
    if recovers_initial:
        await store.record_chronology(
            kv, subscription_id, now=now, policy=policy,
            invoice_id=initial_invoice, period_start=existing.invoice_period_start,
            period_end=existing.invoice_period_end, paid=True)
    return action, None


async def _expect_pack(ledger: Any, session_id: str, units: int,
                       payment_intent: str) -> None:
    """Record the paid pack in the ledger under its PaymentIntent id (MODEL-106).

    This is the link a later `charge.refunded` or `charge.dispute.*` follows:
    those name the PaymentIntent, never the Checkout session. Until claim the
    claim is `pending` (no holder); claim, or the bound key's grant just after
    this, credits it. A session without a PaymentIntent id links nothing.
    """
    if not payment_intent or units < 1:
        return
    try:
        await ledger.expect(f"pack:{session_id}", units, payment_intent, "pack")
    except credits.StoreNotConfigured:
        return


async def _apply_invoice_paid(obj: dict[str, Any], *, kv: Any, policy: AccessPolicy,
                              now: datetime, ledger: Any, service_commit: str,
                              endpoint: str, event_id: str) -> tuple[str, Outcome | None]:
    subscription_id = _subscription_from_invoice(obj)
    if not subscription_id:
        return "ignored", None
    price_id = _price_from_invoice(obj, _metered_price_ids(policy))
    mapping, error = await _map_price_row(
        policy, price_id, service_commit=service_commit, endpoint=endpoint, obj=obj)
    if error is not None:
        return "ignored", error
    assert mapping is not None
    if mapping.kind != "plan":
        return "ignored", None
    invoice_id = _id(obj.get("id")) or event_id
    fingerprint = _fingerprint_from_obj(obj)
    period_start, period_end = _invoice_period(obj, policy)
    existing = await store.load_subscription(kv, subscription_id)
    bound = existing.key_fingerprint if existing is not None else ""
    # No row yet: decide from the key named on the event, before any write.
    holder_fp = bound
    if (not holder_fp and fingerprint and ledger is not None
            and not isinstance(ledger, credits.UnboundLedger)
            and await keys.lookup_fingerprint(kv, fingerprint) is not None):
        holder_fp = fingerprint
    # A rejected grant must not store its period or move the row. The watermark
    # read is that reject when the period ended early; it writes nothing.
    if holder_fp and period_end and ledger is not None:
        try:
            mark = await ledger.invoice_watermark(
                credits.holder_from_fingerprint(holder_fp))
        except credits.StoreNotConfigured:
            mark = 0
        if int(mark or 0) and period_end < int(mark or 0):
            return "ignored", None
    probed = None
    if (holder_fp and ledger is not None
            and not isinstance(ledger, credits.UnboundLedger)):
        try:
            probed = await ledger.set_monthly(
                credits.holder_from_fingerprint(holder_fp),
                mapping.credits, invoice_id, mapping.name,
                _id(obj.get("customer")),
                period_end=int(period_end or 0),
                period_start=int(period_start or 0),
                subscription_id=subscription_id)
        except credits.StoreNotConfigured:
            probed = None
        if isinstance(probed, dict):
            probed = credits.CreditResult.from_json(probed)
        if probed is not None and probed.reason == "stale":
            return "ignored", None
    action, _ = await store.record_entitlement(
        kv, subscription_id=subscription_id,
        customer_id=_id(obj.get("customer")), price_id=price_id, tier=mapping.tier,
        session_id="", now=now, policy=policy,
        pending_monthly=mapping.credits, pending_invoice_id=invoice_id,
        plan_name=mapping.name, plan_credits=mapping.credits,
        key_fingerprint=fingerprint,
        promote=(isinstance(ledger, credits.UnboundLedger)
                 or not (bound or fingerprint)))
    await store.record_chronology(
        kv, subscription_id, now=now, policy=policy,
        customer_id=_id(obj.get("customer")), invoice_id=invoice_id,
        period_start=period_start, period_end=period_end, paid=True)
    grant = await store.grant_monthly(
        kv, subscription_id, ledger=ledger, units=mapping.credits,
        invoice_id=invoice_id, plan=mapping.name, period_end=period_end,
        period_start=period_start)
    if grant == "stale":
        return "ignored", None
    accepted = (probed is not None and probed.credited) or grant == "granted"
    if accepted:
        action = "credited"
    elif grant == "pending" and action == "entitled":
        action = "entitled"
    await _copy_grant_tier(
        kv, subscription_id, ledger=ledger, policy=policy,
        grant="granted" if accepted else grant,
        mapping_tier=mapping.tier)
    return action, None


async def webhook(*, payload: str, signature: str | None, secret: str | None,
                  kv: Any, policy: AccessPolicy, now: datetime,
                  service_commit: str, ledger: Any = None,
                  stripe_secret: str | None = None, http: Any = None,
                  env: Any = None, alert_ctx: Any = None) -> Outcome:
    """Apply one signed Stripe event, whatever `BILLING_ENABLED` says.

    The flag closes the shop: it gates `checkout` and nothing after it. Every
    event Stripe sends is about money that has already moved (a purchase made
    before the flag went off, a renewal of an existing plan, a refund, a
    chargeback), so refusing one would keep a refunded pack's credits, or take
    a renewal's payment and grant nothing. Before 2026-09-24 this returned
    `503 billing_not_enabled` with the flag off, which was harmless before the
    first sale and wrong after it.
    """
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
        friends_configured = (policy.billing.friends_price_ids
                              or policy.billing.friends_promotion_code_prefix)
        if friends_configured and not await store.seen(kv, str(event.get("id") or "")):
            try:
                event = await _resolve_friends_event(
                    event, policy=policy, secret=stripe_secret, http=http)
            except (RuntimeError, OSError, ValueError) as exc:
                return _refusal(STRIPE_UNAVAILABLE, str(exc),
                                service_commit=service_commit, endpoint=endpoint)
        return await apply_event(event, kv=kv, policy=policy, now=now,
                                 service_commit=service_commit, ledger=ledger,
                                 env=env, alert_ctx=alert_ctx)
    except StoreNotConfigured as exc:
        # Not remembered: Stripe retries the event.
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


async def claim(*, session_id: str, kv: Any, policy: AccessPolicy,
                now: datetime, service_commit: str, ledger: Any = None) -> Outcome:
    """Not gated by `BILLING_ENABLED`: a claim only delivers a purchase already paid for."""
    endpoint = "billing.claim"
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
            kv, session_id, now=now, policy=policy, ledger=_billing_ledger(ledger, kv))
    except (StoreNotConfigured, credits.StoreNotConfigured) as exc:
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
    if result.refunded:
        return _refusal(
            PURCHASE_REFUNDED,
            "this purchase was refunded before it was claimed; no key was issued",
            service_commit=service_commit, endpoint=endpoint)
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
    if record.tier == "friends":
        mapping = friends_price(record.price_id)
    kind = mapping.kind if mapping is not None else (
        "pack" if record.subscription_id.startswith("pack:") else "plan")
    body: dict[str, Any] = {
        "key_id": record.key_id,
        "tier": record.tier,
        "plan": record.plan_name or (mapping.name if mapping is not None else ""),
        "credits": (0 if record.tier == "friends" else
                    record.plan_credits or (mapping.credits if mapping is not None else 0)),
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


async def rotate(*, api_key: str | None, kv: Any, policy: AccessPolicy,
                 now: datetime, service_commit: str, ledger: Any = None) -> Outcome:
    """Not gated by `BILLING_ENABLED`: an existing key holder must always be able to rotate."""
    endpoint = "billing.rotate"
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
    try:
        rotated = await store.rotate(
            kv, key, now=now, policy=policy, ledger=_billing_ledger(ledger, kv))
    except credits.StoreNotConfigured as exc:
        return _refusal(STORE_NOT_CONFIGURED, str(exc),
                        service_commit=service_commit, endpoint=endpoint)
    if rotated is None:
        return _refusal(REVOKED_KEY, "that API key has been revoked",
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


def not_for_sale(mapping: PriceMapping) -> str | None:
    """Why checkout must refuse this row, or None when it can be sold."""
    if mapping.tier == "friends":
        return "Friends & Family Prices require a Stripe invitation link"
    if mapping.placeholder:
        return f"{mapping.price_id} is a placeholder Price; not for sale"
    if mapping.legacy:
        return f"{mapping.price_id} is a legacy Price; not for sale"
    return None


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
    refused = not_for_sale(mapping)
    if refused:
        return _refusal(PRICE_NOT_MAPPED, refused,
                        service_commit=service_commit, endpoint=endpoint,
                        detail={"price_id": price_id})
    overage_price_id = ""
    if mapping.overage is not None and mapping.overage.active:
        overage_price_id = mapping.overage.price_id
    success_url = origin.rstrip("/") + policy.billing.success_path
    if "{CHECKOUT_SESSION_ID}" not in success_url:
        success_url += ("&" if "?" in success_url else "?") + "session_id={CHECKOUT_SESSION_ID}"
    try:
        session = await billing_stripe.create_checkout_session(
            secret=secret, price_id=price_id, success_url=success_url,
            cancel_url=policy.billing.cancel_url, terms_url=policy.billing.terms_url,
            http=http, mode=mapping.checkout_mode,
            key_fingerprint=fingerprint or "",
            overage_price_id=overage_price_id,
            allow_promotion_codes=(mapping.kind == "plan"
                                   and bool(policy.billing.friends_promotion_code_prefix)))
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
