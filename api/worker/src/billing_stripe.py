"""Stripe bits that cannot use the Stripe SDK (MODEL-73).

The Worker ships with `disable_python_external_sdk`, so verification and
Checkout Session creation are HMAC and `fetch` against `api.stripe.com`. Card
data never reaches this process: hosted Checkout collects it on Stripe's origin.
"""

from __future__ import annotations

import hmac
import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

#: Stripe's current API version. Sent on Checkout Session creates only; the
#: webhook payload is whatever the Dashboard endpoint was created with.
STRIPE_API_VERSION = "2026-08-26.dahlia"
STRIPE_API_BASE = "https://api.stripe.com/v1"

#: Checkout Session create. Not a live call in this repository's tests.
CHECKOUT_SESSIONS_PATH = "/checkout/sessions"
METER_EVENTS_PATH = "/billing/meter_events"


class SignatureError(ValueError):
    """The Stripe-Signature header is missing, malformed, wrong, or too old."""


class MeterEventError(RuntimeError):
    """Stripe answered a meter-event create and did not accept it."""

    def __init__(self, status: int):
        self.status = int(status)
        super().__init__(f"Stripe meter event create returned HTTP {self.status}")


def meter_event_was_rejected(exc: BaseException) -> bool:
    """True only for an HTTP 4xx. A timeout, a network error, or a 5xx may have landed."""
    return isinstance(exc, MeterEventError) and 400 <= exc.status < 500


def sign_header(payload: str, secret: str, timestamp: int) -> str:
    """A `Stripe-Signature` header for tests and for checking the verifier."""
    return f"t={timestamp},v1={_digest(payload, secret, timestamp)}"


def _digest(payload: str, secret: str, timestamp: int) -> str:
    signed = f"{timestamp}.{payload}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()


def parse_signature_header(header: str | None) -> tuple[int, list[str]]:
    if not header or not str(header).strip():
        raise SignatureError("Stripe-Signature header is missing")
    timestamp = None
    signatures: list[str] = []
    for item in str(header).split(","):
        key, _, value = item.strip().partition("=")
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError as exc:
                raise SignatureError("Stripe-Signature timestamp is not an integer") from exc
        elif key == "v1" and value:
            signatures.append(value)
    if timestamp is None or not signatures:
        raise SignatureError("Stripe-Signature header is missing t or v1")
    return timestamp, signatures


def verify_signature(payload: str, header: str | None, secret: str, *,
                     now: datetime, tolerance_seconds: int) -> int:
    """HMAC-SHA256 over `t.payload`. Returns the timestamp on success.

    Any matching `v1` is accepted (Stripe sends two during secret rotation).
    A timestamp outside `tolerance_seconds` is refused even if the MAC is
    correct, so a captured payload cannot be replayed forever.
    """
    if not secret:
        raise SignatureError("webhook secret is not configured")
    timestamp, signatures = parse_signature_header(header)
    skew = abs(int(now.timestamp()) - timestamp)
    if tolerance_seconds and skew > tolerance_seconds:
        raise SignatureError("Stripe-Signature timestamp is outside tolerance")
    expected = _digest(payload, secret, timestamp)
    if not any(hmac.compare_digest(expected, candidate) for candidate in signatures
               if len(candidate) == len(expected)):
        raise SignatureError("Stripe-Signature does not match")
    return timestamp


def checkout_form(*, price_id: str, success_url: str, cancel_url: str,
                  terms_url: str, mode: str = "subscription",
                  key_fingerprint: str = "", overage_price_id: str = "") -> str:
    """`application/x-www-form-urlencoded` body for a Checkout Session.

    `mode` is `subscription` for a monthly plan or `payment` for a one-off pack.
    `payment_method_types` is deliberately omitted: Stripe picks methods from
    the Dashboard. Terms of service are required; the Dashboard must also name
    `terms_url` as Checkout's terms URL.

    `key_fingerprint` is the SHA-256 of an existing API key, never the key.
    Stripe echoes it on the paid session so the webhook can credit that key.
    """
    if mode not in {"subscription", "payment"}:
        raise ValueError(f"Checkout mode {mode!r} is not subscription or payment")
    fields = {
        "mode": mode,
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "consent_collection[terms_of_service]": "required",
        "custom_text[terms_of_service_acceptance][message]": (
            f"I agree to the ModelSpec terms of service at {terms_url}"
        ),
        "metadata[modelspec_price_id]": price_id,
        "allow_promotion_codes": "false",
        # Sparks & Sawdust LLC's tax rule, the same as dev-mux: Stripe Tax on
        # every Checkout, which needs a billing address for the jurisdiction.
        # With no active registration Stripe computes zero tax, silently.
        "automatic_tax[enabled]": "true",
        "billing_address_collection": "required",
    }
    if mode == "subscription":
        fields["subscription_data[metadata][modelspec_price_id]"] = price_id
    if overage_price_id:
        # Metered Price: Stripe rejects a quantity on a metered line.
        fields["line_items[1][price]"] = overage_price_id
    if key_fingerprint:
        fields["metadata[modelspec_key_fingerprint]"] = key_fingerprint
        if mode == "subscription":
            fields["subscription_data[metadata][modelspec_key_fingerprint]"] = (
                key_fingerprint)
    return urlencode(fields)


async def create_checkout_session(*, secret: str, price_id: str, success_url: str,
                                  cancel_url: str, terms_url: str,
                                  http: Any, mode: str = "subscription",
                                  key_fingerprint: str = "",
                                  overage_price_id: str = "") -> dict[str, Any]:
    """POST /v1/checkout/sessions. `http` is injected; tests never call Stripe."""
    if not secret:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    body = checkout_form(price_id=price_id, success_url=success_url,
                         cancel_url=cancel_url, terms_url=terms_url, mode=mode,
                         key_fingerprint=key_fingerprint,
                         overage_price_id=overage_price_id)
    response = await http(
        STRIPE_API_BASE + CHECKOUT_SESSIONS_PATH,
        method="POST",
        headers={
            "authorization": f"Bearer {secret}",
            "content-type": "application/x-www-form-urlencoded",
            "stripe-version": STRIPE_API_VERSION,
        },
        body=body,
    )
    text = await response.text()
    status = int(getattr(response, "status", 0) or 0)
    ok = bool(getattr(response, "ok", 200 <= status < 300))
    if not ok:
        raise RuntimeError(f"Stripe Checkout Session create returned HTTP {status}")
    import json
    data = json.loads(text)
    if not isinstance(data, dict) or not data.get("id") or not data.get("url"):
        raise RuntimeError("Stripe Checkout Session create returned no id/url")
    return data


def meter_event_form(*, event_name: str, customer_id: str, value: int,
                     identifier: str, timestamp: int | None = None) -> str:
    """One Billing Meter event. `value` is the overage credits just settled.

    `timestamp` is unix seconds for when the usage happened. Stripe bills the
    event in that period. Omit it and Stripe uses the time of the POST.
    """
    fields = {
        "event_name": event_name,
        "payload[stripe_customer_id]": customer_id,
        "payload[value]": str(int(value)),
        "identifier": identifier,
    }
    if timestamp is not None:
        fields["timestamp"] = str(int(timestamp))
    return urlencode(fields)


def meter_identifier_already_used(text: str, data: dict[str, Any] | None = None) -> bool:
    """Stripe already accepted this meter-event identifier."""
    body = data if isinstance(data, dict) else {}
    error = body.get("error")
    if not isinstance(error, dict):
        error = body
    code = str(error.get("code") or "")
    message = str(error.get("message") or text or "").lower()
    if code == "duplicate_meter_event":
        return True
    return "identifier" in message and ("already" in message or "duplicate" in message)


async def create_meter_event(*, secret: str, event_name: str, customer_id: str,
                             value: int, identifier: str, http: Any,
                             timestamp: int | None = None,
                             timeout_ms: int | None = 5_000) -> dict[str, Any]:
    """POST /v1/billing/meter_events. `http` is injected; tests never call Stripe.

    `timeout_ms` is forwarded to `http`. A response that says this identifier
    was already used is success: Stripe accepted that event on an earlier try.
    `timestamp`, when set, is the `timestamp` form field (unix seconds).
    """
    if not secret:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    if value < 1 or not customer_id or not event_name:
        return {}
    body = meter_event_form(event_name=event_name, customer_id=customer_id,
                            value=value, identifier=identifier, timestamp=timestamp)
    response = await http(
        STRIPE_API_BASE + METER_EVENTS_PATH,
        method="POST",
        headers={
            "authorization": f"Bearer {secret}",
            "content-type": "application/x-www-form-urlencoded",
            "stripe-version": STRIPE_API_VERSION,
        },
        body=body,
        timeout_ms=timeout_ms,
    )
    text = await response.text()
    status = int(getattr(response, "status", 0) or 0)
    ok = bool(getattr(response, "ok", 200 <= status < 300))
    import json
    if ok:
        data = json.loads(text) if text else {}
        return data if isinstance(data, dict) else {}
    try:
        parsed = json.loads(text) if text else {}
    except json.JSONDecodeError:
        parsed = {}
    data = parsed if isinstance(parsed, dict) else {}
    if meter_identifier_already_used(text, data):
        return data
    raise MeterEventError(status)
