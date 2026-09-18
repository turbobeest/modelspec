"""Coinbase CDP x402 facilitator client (MODEL-75).

Talks to the v2 verify and settle endpoints documented at
https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/x402-facilitator
(read 2026-09-18):

* POST {origin}/v2/x402/verify
* POST {origin}/v2/x402/settle

The body is `{x402Version, paymentPayload, paymentRequirements}` as in that
spec. Tests inject `post` and never call the network. The Worker injects
`js.fetch`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

from cdp_auth import CdpAuthError

#: Production origin. Paths are appended. Overridable via X402_FACILITATOR_URL.
DEFAULT_ORIGIN = "https://api.cdp.coinbase.com/platform"
VERIFY_PATH = "/v2/x402/verify"
SETTLE_PATH = "/v2/x402/settle"
X402_VERSION = 2

PostFn = Callable[[str, dict[str, Any], dict[str, str]],
                  Awaitable[tuple[int, dict[str, Any]]]]
AuthFn = Callable[[str, str], Awaitable[dict[str, str]] | dict[str, str]]


class FacilitatorError(RuntimeError):
    """The facilitator refused the call or was unreachable. Ours or theirs, not the caller's payload."""


@dataclass(frozen=True)
class VerifyResult:
    is_valid: bool
    payer: str = ""
    invalid_reason: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SettleResult:
    success: bool
    transaction: str = ""
    payer: str = ""
    network: str = ""
    error_reason: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


class Facilitator(Protocol):
    async def verify(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> VerifyResult: ...

    async def settle(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> SettleResult: ...


@dataclass
class StubFacilitator:
    """In-process facilitator. The suite's only facilitator; it does not fetch."""

    valid: bool = True
    settle_ok: bool = True
    payer: str = "0x857b06519E91e3A54538791bDbb0E22373e36b66"
    transaction: str = "0x" + "ab" * 32
    network: str = "eip155:84532"
    invalid_reason: str = "invalid_payload"
    error_reason: str = "invalid_transaction_state"
    calls: list[tuple[str, dict[str, Any]]] = field(default_factory=list)

    async def verify(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> VerifyResult:
        self.calls.append(("verify", payment_payload))
        if not self.valid:
            return VerifyResult(False, self.payer, self.invalid_reason)
        return VerifyResult(True, self.payer)

    async def settle(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> SettleResult:
        self.calls.append(("settle", payment_payload))
        if not self.settle_ok:
            return SettleResult(False, "", self.payer, self.network, self.error_reason)
        return SettleResult(True, self.transaction, self.payer, self.network)


class CdpFacilitator:
    """POST /v2/x402/verify and /v2/x402/settle. `post` is injected so tests never fetch."""

    def __init__(self, origin: str = DEFAULT_ORIGIN, *,
                 post: PostFn,
                 auth: AuthFn | None = None) -> None:
        self.origin = origin.rstrip("/")
        self._post = post
        self._auth = auth

    async def verify(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> VerifyResult:
        body = await self._call(VERIFY_PATH, payment_payload, requirements)
        return VerifyResult(
            is_valid=bool(body.get("isValid")),
            payer=str(body.get("payer") or ""),
            invalid_reason=str(body.get("invalidReason") or ""),
            raw=body,
        )

    async def settle(self, payment_payload: dict[str, Any],
                     requirements: dict[str, Any]) -> SettleResult:
        body = await self._call(SETTLE_PATH, payment_payload, requirements)
        return SettleResult(
            success=bool(body.get("success")),
            transaction=str(body.get("transaction") or ""),
            payer=str(body.get("payer") or ""),
            network=str(body.get("network") or ""),
            error_reason=str(body.get("errorReason") or body.get("errorMessage") or ""),
            raw=body,
        )

    async def _call(self, path: str, payment_payload: dict[str, Any],
                    requirements: dict[str, Any]) -> dict[str, Any]:
        url = self.origin + path
        payload = {
            "x402Version": X402_VERSION,
            "paymentPayload": payment_payload,
            "paymentRequirements": requirements,
        }
        headers = {"content-type": "application/json"}
        if self._auth is not None:
            try:
                extra = self._auth("POST", url)
                if hasattr(extra, "__await__"):
                    extra = await extra  # type: ignore[misc]
            except CdpAuthError as exc:
                raise FacilitatorError(str(exc)) from None
            headers.update(extra or {})
        status, body = await self._post(url, payload, headers)
        if status >= 500:
            raise FacilitatorError(f"facilitator {path} returned HTTP {status}")
        if not isinstance(body, dict):
            raise FacilitatorError(f"facilitator {path} returned a non-object")
        return body


async def worker_post(url: str, payload: dict[str, Any],
                      headers: dict[str, str]) -> tuple[int, dict[str, Any]]:
    """`js.fetch` adapter. Imported only on the Worker path."""
    from js import Object, fetch
    from pyodide.ffi import to_js

    init = to_js({
        "method": "POST",
        "headers": headers,
        "body": json.dumps(payload),
    }, dict_converter=Object.fromEntries)
    response = await fetch(url, init)
    text = await response.text()
    try:
        body = json.loads(text) if text else {}
    except ValueError:
        body = {"errorMessage": text[:200]}
    return int(response.status), body if isinstance(body, dict) else {}
