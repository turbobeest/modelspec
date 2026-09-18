"""x402 prepaid credits and per-call 402 (MODEL-75).

An unfunded request to a paid resource is HTTP 402 with x402 v2 payment
requirements (header + JSON). A PAYMENT-SIGNATURE is verified and settled
with Coinbase's CDP facilitator **before** `produce` runs. Successful
settlement credits the holder's ledger exactly once; a successful result
then draws down one unit. A 4xx, 5xx, empty or no-match result releases
the reservation.

Flag: `X402_ENABLED`, default off, independent of Stripe. Mainnet
(`X402_MAINNET`) is a second flag, also off. See `docs/x402.md`.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable
from urllib.parse import urlparse

import credits
from x402_facilitator import (
    DEFAULT_ORIGIN,
    CdpFacilitator,
    Facilitator,
    FacilitatorError,
    StubFacilitator,
    worker_post,
)

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_PAYMENT_REQUIRED = 402
HTTP_MISCONFIGURED = 500
HTTP_STORE_UNAVAILABLE = 503

PAYMENT_REQUIRED = "payment_required"
PAYMENT_FAILED = "payment_failed"
INVALID_PAYMENT = "invalid_payment"
X402_NOT_CONFIGURED = "x402_not_configured"
CREDITS_STORE_NOT_CONFIGURED = "credits_store_not_configured"
MISSING_HOLDER = "missing_holder"

PAYMENT_SIGNATURE = "PAYMENT-SIGNATURE"
PAYMENT_REQUIRED_HEADER = "PAYMENT-REQUIRED"
PAYMENT_RESPONSE = "PAYMENT-RESPONSE"
X_PAYMENT = "X-PAYMENT"

#: x402 v2 HTTP transport (coinbase/x402 specs/transports-v2/http.md, read 2026-09-18).
X402_VERSION = 2
SCHEME = "exact"

#: CAIP-2, CDP facilitator table (docs.cdp.coinbase.com/x402/seller/facilitator, 2026-09-18).
NETWORK_BASE_SEPOLIA = "eip155:84532"
NETWORK_BASE = "eip155:8453"
#: Circle native USDC, https://developers.circle.com/stablecoins/usdc-contract-addresses (2026-09-18).
USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_DECIMALS = 6
USDC_EXTRA = {"name": "USDC", "version": "2"}

#: PLACEHOLDER price range, $0.001–$0.01 at 6 decimals. The price itself is config.
PRICE_ATOMIC_MIN = 1000
PRICE_ATOMIC_MAX = 10000
DEFAULT_PRICE_ATOMIC = 1000  # PLACEHOLDER $0.001 USDC
MAX_TIMEOUT_SECONDS = 60

_SWITCH_OFF = frozenset({"", "0", "false", "no", "off"})
_ADDR = re.compile(r"^0x[0-9a-fA-F]{40}$")


def flag(raw: Any) -> bool:
    """On unless the value is a documented off spelling. Same rule as ACCESS_ENFORCED."""
    if raw is None or raw is False:
        return False
    if raw is True:
        return True
    return str(raw).strip().lower() not in _SWITCH_OFF


def _attr(env: Any, name: str, default: str = "") -> str:
    return str(getattr(env, name, default) or default).strip()


@dataclass(frozen=True)
class Config:
    enabled: bool
    mainnet: bool
    network: str
    asset: str
    pay_to: str
    price_atomic: int
    facilitator_url: str
    resource_origin: str

    @property
    def configured(self) -> bool:
        return bool(self.pay_to) and _ADDR.match(self.pay_to) is not None and (
            PRICE_ATOMIC_MIN <= self.price_atomic <= PRICE_ATOMIC_MAX)

    @property
    def asset_name(self) -> str:
        return "USDC"


def load_config(env: Any) -> Config:
    price_raw = _attr(env, "X402_PRICE_ATOMIC", str(DEFAULT_PRICE_ATOMIC))
    try:
        price = int(price_raw)
    except ValueError:
        price = -1
    mainnet = flag(getattr(env, "X402_MAINNET", None))
    default_network = NETWORK_BASE if mainnet else NETWORK_BASE_SEPOLIA
    default_asset = USDC_BASE if mainnet else USDC_BASE_SEPOLIA
    return Config(
        enabled=flag(getattr(env, "X402_ENABLED", None)),
        mainnet=mainnet,
        network=_attr(env, "X402_NETWORK", default_network) or default_network,
        asset=_norm_addr(_attr(env, "X402_ASSET", default_asset) or default_asset),
        pay_to=_norm_addr(_attr(env, "X402_PAY_TO", "")),
        price_atomic=price,
        facilitator_url=_attr(env, "X402_FACILITATOR_URL", DEFAULT_ORIGIN) or DEFAULT_ORIGIN,
        resource_origin=_attr(env, "EXPORT_ORIGIN", "https://api.modelspec.dev")
        or "https://api.modelspec.dev",
    )


def _norm_addr(value: str) -> str:
    value = (value or "").strip()
    if _ADDR.match(value):
        return "0x" + value[2:].lower()
    return value


def holder_from_key(api_key: str | None) -> str | None:
    """Credits are keyed to the SHA-256 of an API key, never the key."""
    if not api_key or not str(api_key).strip():
        return None
    digest = hashlib.sha256(str(api_key).strip().encode("utf-8")).hexdigest()
    return "key:" + digest


def payment_id(payload: dict[str, Any]) -> str:
    inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    auth = inner.get("authorization") if isinstance(inner.get("authorization"), dict) else {}
    nonce = str(auth.get("nonce") or "")
    signature = str(inner.get("signature") or "")
    return hashlib.sha256(f"{nonce}|{signature}".encode("utf-8")).hexdigest()


def _b64(obj: dict[str, Any]) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def _maybe_b64_json(value: str) -> dict[str, Any]:
    text = value.strip()
    if not text:
        raise ValueError("empty payment header")
    if text[0] != "{":
        try:
            text = base64.b64decode(text, validate=False).decode("utf-8")
        except Exception as exc:
            raise ValueError("payment header is not JSON or base64 JSON") from exc
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("payment payload is not an object")
    return data


def parse_payment(get_header: Callable[[str], Any]) -> dict[str, Any] | None:
    """PAYMENT-SIGNATURE (x402 v2), or X-PAYMENT (v1 alias). None if absent."""
    raw = None
    for name in (PAYMENT_SIGNATURE, "payment-signature", X_PAYMENT, "x-payment"):
        value = get_header(name)
        if value:
            raw = str(value)
            break
    if not raw:
        return None
    return _maybe_b64_json(raw)


def _inner_payload(payload: dict[str, Any]) -> dict[str, Any]:
    inner = payload.get("payload")
    return inner if isinstance(inner, dict) else {}


def _authorization(payload: dict[str, Any]) -> dict[str, Any]:
    auth = _inner_payload(payload).get("authorization")
    return auth if isinstance(auth, dict) else {}


def requirements_for(config: Config, resource_url: str, description: str) -> dict[str, Any]:
    return {
        "scheme": SCHEME,
        "network": config.network,
        "amount": str(config.price_atomic),
        "asset": config.asset,
        "payTo": config.pay_to,
        "maxTimeoutSeconds": MAX_TIMEOUT_SECONDS,
        "extra": dict(USDC_EXTRA),
        # v1 clients still look for these:
        "maxAmountRequired": str(config.price_atomic),
        "resource": resource_url,
        "description": description,
        "mimeType": "application/json",
    }


def payment_required_object(config: Config, resource_url: str, *,
                            message: str = "PAYMENT-SIGNATURE header is required",
                            description: str = "ModelSpec paid result") -> dict[str, Any]:
    """x402 v2 PaymentRequired, for the PAYMENT-REQUIRED header."""
    return {
        "x402Version": X402_VERSION,
        "error": message,
        "resource": {
            "url": resource_url,
            "description": description,
            "mimeType": "application/json",
        },
        "accepts": [requirements_for(config, resource_url, description)],
    }


def payment_required_body(config: Config, envelope: dict[str, Any], resource_url: str, *,
                          message: str = "this resource requires payment",
                          code: str = PAYMENT_REQUIRED) -> dict[str, Any]:
    required = payment_required_object(config, resource_url, message=message)
    accepts = required["accepts"]
    return {
        **envelope,
        "error": {
            "code": code,
            "message": message,
            "x402Version": X402_VERSION,
            "price": {
                "amount": str(config.price_atomic),
                "atomic": config.price_atomic,
                "usd": config.price_atomic / (10 ** USDC_DECIMALS),
                "asset": config.asset,
                "network": config.network,
                "currency": "USDC",
                "placeholder": True,
                "placeholder_note": (
                    "PLACEHOLDER price in the $0.001–$0.01 range; not a live rate."
                ),
            },
            "payTo": config.pay_to,
            "resource": resource_url,
            "accepts": accepts,
            "how_to_pay": (
                "Retry with a PAYMENT-SIGNATURE header as in x402 v2 "
                "(https://www.x402.org / specs/transports-v2/http.md). "
                f"Pay {config.price_atomic} atomic USDC ({config.network}) to {config.pay_to}."
            ),
        },
        "result": [],
        "x402Version": X402_VERSION,
        "accepts": accepts,
        "resource": required["resource"],
    }


def http_headers(status: int, body: dict[str, Any], *,
                 settlement: dict[str, Any] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if status == HTTP_PAYMENT_REQUIRED:
        resource = body.get("resource") if isinstance(body.get("resource"), dict) else {}
        accepts = body.get("accepts") if isinstance(body.get("accepts"), list) else []
        error = body.get("error") if isinstance(body.get("error"), dict) else {}
        message = str(error.get("message") or "PAYMENT-SIGNATURE header is required")
        headers[PAYMENT_REQUIRED_HEADER] = _b64({
            "x402Version": X402_VERSION,
            "error": message,
            "resource": resource or {"url": "", "description": "", "mimeType": "application/json"},
            "accepts": accepts,
        })
    if settlement:
        headers[PAYMENT_RESPONSE] = _b64(settlement)
    return headers


def _error(envelope: dict[str, Any], status: int, code: str, message: str,
           detail: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    return status, {**envelope, "error": {"code": code, "message": message, **(detail or {})},
                    "result": []}


def is_billable_success(status: int, body: dict[str, Any]) -> bool:
    """One unit is drawn down only for a delivered result: HTTP 200 with a non-empty result."""
    if status != HTTP_OK:
        return False
    if body.get("error"):
        return False
    result = body.get("result")
    return isinstance(result, list) and len(result) > 0


def _units_bought(payload: dict[str, Any], price: int) -> int:
    auth = _authorization(payload)
    try:
        value = int(str(auth.get("value") or "0"))
    except ValueError:
        value = 0
    if price < 1:
        return 0
    return value // price


def _check_payload(payload: dict[str, Any], config: Config) -> str | None:
    """Return a refusal message, or None if the payload is acceptable to settle."""
    if config.mainnet is False and config.network == NETWORK_BASE:
        return "mainnet is disabled (X402_MAINNET is off)"
    if config.mainnet and config.network != NETWORK_BASE:
        return "X402_MAINNET is on but X402_NETWORK is not Base mainnet (eip155:8453)"
    auth = _authorization(payload)
    if not auth:
        return "payment payload has no authorization"
    to = _norm_addr(str(auth.get("to") or ""))
    if to != config.pay_to:
        return "authorization.to is not this service's payTo"
    inner = _inner_payload(payload)
    if not inner.get("signature"):
        return "payment payload has no signature"
    if not auth.get("nonce"):
        return "payment payload has no nonce"
    accepted = payload.get("accepted") if isinstance(payload.get("accepted"), dict) else {}
    network = str(accepted.get("network") or payload.get("network") or "")
    if network and network != config.network:
        return f"payment network {network} is not {config.network}"
    asset = _norm_addr(str(accepted.get("asset") or payload.get("asset") or config.asset))
    if asset and asset != config.asset:
        return "payment asset is not the configured USDC"
    try:
        value = int(str(auth.get("value") or "0"))
    except ValueError:
        return "authorization.value is not an integer"
    if value < config.price_atomic:
        return "authorization.value is below the price of one result"
    return None


@dataclass
class ChargeTrace:
    """Recorded so a test that reverses verify/settle/produce fails."""

    events: list[str] = field(default_factory=list)
    settlement: dict[str, Any] | None = None

    def note(self, event: str) -> None:
        self.events.append(event)


async def charge(
    *,
    config: Config,
    ledger: credits.Ledger,
    facilitator: Facilitator,
    get_header: Callable[[str], Any],
    holder: str | None,
    resource_url: str,
    envelope: dict[str, Any],
    produce: Callable[[], Awaitable[tuple[int, dict[str, Any]]]],
    trace: ChargeTrace | None = None,
) -> tuple[int, dict[str, Any]]:
    """Verify and settle, then produce. Returns (status, body). Headers via http_headers."""
    log = trace or ChargeTrace()

    if not config.enabled:
        log.note("disabled")
        return await produce()

    if not config.configured:
        log.note("misconfigured")
        return _error(envelope, HTTP_MISCONFIGURED, X402_NOT_CONFIGURED,
                      "x402 is enabled but payTo/price/network are not configured")

    try:
        payload = parse_payment(get_header)
    except (ValueError, json.JSONDecodeError) as exc:
        log.note("invalid_payment")
        return _error(envelope, HTTP_BAD_REQUEST, INVALID_PAYMENT, str(exc))

    oneshot = False
    if payload is not None:
        status, body, oneshot = await _settle_and_credit(
            config, ledger, facilitator, payload, holder, resource_url, envelope, log)
        if status is not None:
            return status, body

    reservation_id: int | None = None
    reserved_holder: str | None = None
    try:
        if holder:
            try:
                reserved = await ledger.reserve(holder, 1)
            except credits.StoreNotConfigured:
                return _error(envelope, HTTP_STORE_UNAVAILABLE, CREDITS_STORE_NOT_CONFIGURED,
                              "x402 is enabled and the CREDITS Durable Object is not bound")
            if not reserved.ok:
                log.note("unfunded")
                return HTTP_PAYMENT_REQUIRED, payment_required_body(
                    config, envelope, resource_url,
                    message="no prepaid credit remains; PAYMENT-SIGNATURE is required")
            reservation_id = reserved.reservation_id
            reserved_holder = holder
            log.note("reserved")
        elif oneshot:
            log.note("oneshot")
        else:
            log.note("unfunded")
            return HTTP_PAYMENT_REQUIRED, payment_required_body(config, envelope, resource_url)

        log.note("produce")
        status, body = await produce()
        if reservation_id is not None and reserved_holder is not None:
            if is_billable_success(status, body):
                await ledger.commit(reserved_holder, reservation_id)
                log.note("commit")
                reservation_id = None
            else:
                await ledger.release(reserved_holder, reservation_id)
                log.note("release")
                reservation_id = None
        return status, body
    finally:
        if reservation_id is not None and reserved_holder is not None:
            try:
                await ledger.release(reserved_holder, reservation_id)
                log.note("release")
            except credits.StoreNotConfigured:
                pass


async def _settle_and_credit(
    config: Config,
    ledger: credits.Ledger,
    facilitator: Facilitator,
    payload: dict[str, Any],
    holder: str | None,
    resource_url: str,
    envelope: dict[str, Any],
    log: ChargeTrace,
) -> tuple[int | None, dict[str, Any], bool]:
    """Verify, settle, credit. Returns (status, body, oneshot). status set means stop."""
    problem = _check_payload(payload, config)
    if problem:
        log.note("front_run_rejected" if "payTo" in problem else "invalid_payment")
        return HTTP_BAD_REQUEST, _error(envelope, HTTP_BAD_REQUEST, INVALID_PAYMENT, problem)[1], False

    pid = payment_id(payload)
    if pid == hashlib.sha256(b"|").hexdigest():
        return HTTP_BAD_REQUEST, _error(
            envelope, HTTP_BAD_REQUEST, INVALID_PAYMENT,
            "payment payload has no nonce and signature")[1], False

    units = _units_bought(payload, config.price_atomic)
    if units < 1:
        return HTTP_BAD_REQUEST, _error(
            envelope, HTTP_BAD_REQUEST, INVALID_PAYMENT,
            "payment does not cover one result")[1], False

    try:
        if await ledger.seen(pid):
            log.note("replay")
            if holder is None:
                return HTTP_PAYMENT_REQUIRED, payment_required_body(
                    config, envelope, resource_url,
                    message="that payment has already been settled"), False
            return None, {}, False
    except credits.StoreNotConfigured:
        pass

    requirements = requirements_for(config, resource_url, "ModelSpec paid result")

    log.note("verify")
    try:
        verified = await facilitator.verify(payload, requirements)
    except FacilitatorError as exc:
        return HTTP_MISCONFIGURED, _error(
            envelope, HTTP_MISCONFIGURED, X402_NOT_CONFIGURED, str(exc))[1], False
    if not verified.is_valid:
        log.note("verify_failed")
        return HTTP_PAYMENT_REQUIRED, payment_required_body(
            config, envelope, resource_url,
            message=f"payment verification failed: {verified.invalid_reason or 'invalid'}",
            code=PAYMENT_FAILED), False

    log.note("settle")
    try:
        settled = await facilitator.settle(payload, requirements)
    except FacilitatorError as exc:
        return HTTP_MISCONFIGURED, _error(
            envelope, HTTP_MISCONFIGURED, X402_NOT_CONFIGURED, str(exc))[1], False
    if not settled.success:
        log.note("settle_failed")
        return HTTP_PAYMENT_REQUIRED, payment_required_body(
            config, envelope, resource_url,
            message=f"payment settlement failed: {settled.error_reason or 'failed'}",
            code=PAYMENT_FAILED), False

    log.settlement = {
        "success": True,
        "transaction": settled.transaction,
        "network": settled.network or config.network,
        "payer": settled.payer or str(_authorization(payload).get("from") or ""),
    }

    credit_holder = holder or (
        "payer:" + _norm_addr(str(_authorization(payload).get("from") or "unknown")))
    try:
        result = await ledger.credit(credit_holder, pid, units, settled.transaction)
    except credits.StoreNotConfigured:
        if holder is None:
            log.note("oneshot_unbound")
            return None, {}, True
        return HTTP_STORE_UNAVAILABLE, _error(
            envelope, HTTP_STORE_UNAVAILABLE, CREDITS_STORE_NOT_CONFIGURED,
            "settlement succeeded and the credit store is not bound")[1], False

    if not result.credited and result.reason == "conflict":
        log.note("replay")
        return HTTP_PAYMENT_REQUIRED, payment_required_body(
            config, envelope, resource_url,
            message="that payment has already been settled"), False

    if holder is None:
        burned = await ledger.reserve(credit_holder, units)
        if burned.ok and burned.reservation_id is not None:
            await ledger.commit(credit_holder, burned.reservation_id)
        log.note("oneshot")
        return None, {}, True

    log.note("credit" if result.credited else "replay")
    return None, {}, False


def balance_body(envelope: dict[str, Any], balance: credits.Balance, *,
                 enabled: bool) -> dict[str, Any]:
    return {
        **envelope,
        "endpoint": "credits",
        "x402_enabled": enabled,
        "holder": balance.holder,
        "available": balance.available,
        "reserved": balance.reserved,
        "total": balance.total,
        "unit": "successful result",
        "result": [],
    }


async def balance_query(*, config: Config, ledger: credits.Ledger,
                        api_key: str | None,
                        envelope: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    holder = holder_from_key(api_key)
    if holder is None:
        return _error(envelope, HTTP_UNAUTHORIZED, MISSING_HOLDER,
                      "GET /v1/credits takes the API key whose balance you are asking for, "
                      "as Authorization: Bearer <key> or X-API-Key: <key>")
    try:
        bal = await ledger.balance(holder)
    except credits.StoreNotConfigured:
        if not config.enabled:
            return HTTP_OK, balance_body(envelope, credits.Balance(holder, 0, 0),
                                         enabled=False)
        return _error(envelope, HTTP_STORE_UNAVAILABLE, CREDITS_STORE_NOT_CONFIGURED,
                      "the CREDITS Durable Object is not bound")
    return HTTP_OK, balance_body(envelope, bal, enabled=config.enabled)


def resource_url(request_url: str, path: str, origin: str) -> str:
    parsed = urlparse(str(request_url))
    host = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else origin.rstrip("/")
    return host + path


def facilitator_from_env(env: Any, config: Config) -> Facilitator:
    injected = getattr(env, "X402_FACILITATOR", None)
    if injected is not None:
        return injected
    if not config.enabled:
        return StubFacilitator()

    async def auth(_method: str, _url: str) -> dict[str, str]:
        token = str(getattr(env, "CDP_JWT", "") or getattr(env, "CDP_API_KEY_ID", "") or "")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    return CdpFacilitator(config.facilitator_url, post=worker_post, auth=auth)
