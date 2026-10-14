"""One Pushover notice after a confirmed sale (MODEL-391).

`SALE_ALERTS_ENABLED` uses `access.enforcement`: the same off spellings as
`BILLING_ENABLED` and `X402_ENABLED`. Unset is off. A missing
`PUSHOVER_APP_TOKEN` or `PUSHOVER_USER_KEY` does nothing.

The POST goes through `ctx.waitUntil`. It does not decide the sale. A
failure logs `sale_alert_schedule` or `sale_alert_post` and nothing else:
not the token, the user key, or the payload.

Dedupe is the store that already accepted the sale. Stripe calls this
only after `access_billing.remember` records a new paid plan or pack, so a
retried event id is `duplicate` and does not call again. x402 calls this
only when `ledger.credit` returns credited (the ledger's payment-id
dedupe); `ref` is the settlement transaction. `_seen` drops a second call
with the same ref inside one isolate. This module does not write KV.
"""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from urllib.parse import urlencode

import access

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
TIMEOUT_MS = 5_000
_TTL_DEFAULT = 900
_TTL_MIN = 60
_TTL_MAX = 86_400
_seen: set[str] = set()


def notify_sale(env: Any, ctx: Any, *, channel: str, product: str,
                amount_usd: Any, ref: str) -> None:
    """Schedule one notice. Returns before the POST finishes."""
    try:
        _schedule(env, ctx, channel=channel, product=product,
                  amount_usd=amount_usd, ref=ref)
    except Exception:
        logging.error("sale_alert_schedule")


def _schedule(env: Any, ctx: Any, *, channel: str, product: str,
              amount_usd: Any, ref: str) -> None:
    if env is None or not access.enforcement(getattr(env, "SALE_ALERTS_ENABLED", None)):
        return
    token = str(getattr(env, "PUSHOVER_APP_TOKEN", "") or "").strip()
    user = str(getattr(env, "PUSHOVER_USER_KEY", "") or "").strip()
    if not token or not user:
        return
    key = str(ref or "").strip()
    if not key or key in _seen:
        return
    _seen.add(key)
    body = urlencode({
        "token": token,
        "user": user,
        "title": "ModelSpec sale",
        "message": _message(channel, product, amount_usd, key),
        "ttl": str(_ttl(getattr(env, "SALE_ALERT_TTL_SECONDS", None))),
        "priority": "0",
    })
    _handoff(ctx, _deliver(body))


def _message(channel: str, product: str, amount_usd: Any, ref: str) -> str:
    label = " ".join(str(product or "sale").split()) or "sale"
    amount = _money(amount_usd)
    if str(channel).strip().lower() == "x402":
        prefix = ref[:6]
        shown = f"{prefix}…" if len(ref) > 6 else prefix
        return f"{amount} · {label} · x402 · tx {shown}"
    return f"{amount} · {label} · card"


def _money(amount: Any) -> str:
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        value = Decimal(0)
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${quantized:.2f}"


def _ttl(raw: Any) -> int:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return _TTL_DEFAULT
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return _TTL_DEFAULT
    return min(_TTL_MAX, max(_TTL_MIN, value))


async def _deliver(body: str) -> None:
    try:
        response = await _fetch(PUSHOVER_URL, body)
        status = int(getattr(response, "status", 0) or 0)
        if status and not 200 <= status < 300:
            raise RuntimeError("sale_alert_http")
    except Exception:
        logging.error("sale_alert_post")


async def _fetch(url: str, body: str) -> Any:
    """Workers `fetch` with a five-second abort. Tests replace this."""
    from js import AbortSignal, Object, fetch
    from pyodide.ffi import to_js

    native = {
        "method": "POST",
        "headers": {"content-type": "application/x-www-form-urlencoded"},
        "body": body,
        "signal": AbortSignal.timeout(TIMEOUT_MS),
    }
    options = to_js(native, dict_converter=Object.fromEntries)
    return await fetch(url, options)


def _handoff(ctx: Any, work: Any) -> None:
    wait = getattr(ctx, "waitUntil", None)
    if not callable(wait):
        _close(work)
        logging.error("sale_alert_schedule")
        return
    promise = _promise(work)
    try:
        wait(work if promise is None else promise)
    except Exception:
        logging.error("sale_alert_schedule")
        _close(work)


def _promise(work: Any) -> Any:
    try:
        from js import Promise
        from pyodide.ffi import create_proxy
    except ImportError:
        return None

    def executor(resolve, _reject):
        task = asyncio.ensure_future(work)

        def finished(fut: asyncio.Future) -> None:
            fut.exception()
            resolve(None)

        task.add_done_callback(finished)

    return Promise.new(create_proxy(executor))


def _close(work: Any) -> None:
    close = getattr(work, "close", None)
    if not callable(close) or getattr(work, "cr_running", False):
        return
    if getattr(work, "cr_frame", None) is None:
        return
    try:
        close()
    except RuntimeError:
        return
