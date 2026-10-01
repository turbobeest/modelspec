"""Keyless /decide admission. Tokens and addresses are never persisted."""
from __future__ import annotations

import re

from ipaddress import ip_address, ip_network
from urllib.parse import urlparse

import access
import visitor

TOKEN_HEADER = "x-modelspec-turnstile"
REMAINING_HEADER = "x-modelspec-decisions-remaining"
SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
INTENT_HEADER = "x-modelspec-intent"
INTENT_REQUEST_LIMIT = 32
INTENT_WINDOW_SECONDS = 60


def intent_for(request):
    value = str(request.headers.get(INTENT_HEADER) or "")
    # Canonical unpadded base64url encoding of exactly 16 random bytes.
    return value if re.fullmatch(r"[A-Za-z0-9_-]{21}[AQgw]", value) else None


DAY_LIMIT = 20
BURST_LIMIT = 3
WINDOW_SECONDS = 600
UNAVAILABLE = "Manual decisions are temporarily unavailable. Please try again later."


def enabled(env):
    return access.enforcement(getattr(env, "HUMAN_GATE_ENABLED", None))


# Access/transport refusals, outside the closed decision contract.
REFUSALS = {
    "human_origin_required": 401,
    "human_challenge_required": 403,
    "human_gate_unavailable": 503,
    "human_day_limit": 429,
    "human_burst_limit": 429,
    "human_sweep_limit": 429,
    "human_intent_limit": 429,
}
LIMIT_CODES = {"day": "human_day_limit", "burst": "human_burst_limit", "sweep": "human_sweep_limit", "intent": "human_intent_limit"}


def identity_for(request, env):
    ip = str(request.headers.get("CF-Connecting-IP") or "").strip()
    if not ip:
        return None
    address = ip_address(ip)
    if address.version == 6:
        ip = str(ip_network(f"{address}/64", strict=False))
    return visitor.visitor_id(ip, getattr(env, visitor.KEY_VAR, None))


def unconfigured_reason(request, env) -> str:
    """Which prerequisite of `stub_for` is missing: a name, never a value."""
    if not identity_for(request, env):
        return "no_visitor_identity"
    if getattr(env, "HUMAN_GATE", None) is None:
        return "no_human_gate_binding"
    return "no_turnstile_secret"


def log_unavailable(where: str, exc: BaseException) -> None:
    """Log why the gate failed closed: the exception type and a short message.

    Never logs a request, spec, token, key or address. Messages come from the
    runtime or `unconfigured_reason`, and are cut to 160 characters.
    """
    print(f"human_gate_unavailable where={where} type={type(exc).__name__} "
          f"detail={str(exc)[:160]}")


def stub_for(request, env):
    identity = identity_for(request, env)
    binding = getattr(env, "HUMAN_GATE", None)
    if not identity or binding is None or not getattr(env, "TURNSTILE_SECRET", None):
        return None
    return binding.get(binding.idFromName(identity))


def as_dict(value):
    to_py = getattr(value, "to_py", None)
    return dict(to_py() if callable(to_py) else value)


async def admit(request, env, origins, verify):
    """Return (status, error code, message, headers), or an admitted 200."""
    origin = str(request.headers.get("origin") or "")
    if origin not in origins:
        return 401, "human_origin_required", "Use the paid API or MCP for machine access.", {}
    try:
        stub = stub_for(request, env)
        if stub is None:
            return 503, "human_gate_unavailable", UNAVAILABLE, {}
        intent = intent_for(request)
        # Only a visitor's already verified admission can bypass Siteverify.
        # This also consumes the continuation atomically against its cap.
        continued = await stub.continue_intent(intent) if intent else None
        meter = as_dict(continued) if continued is not None else None
        if meter is None:
            token = str(request.headers.get(TOKEN_HEADER) or "")
            if not token or len(token) > 2048:
                return 403, "human_challenge_required", "Complete the human verification before each lookup.", {}
            result = await verify(str(env.TURNSTILE_SECRET), token)
            # Siteverify uses bot/headless signals internally, but exposes no separate
            # headless flag. A failed validation is refused, never inferred as human.
            if not isinstance(result, dict) or result.get("success") is not True \
                    or result.get("hostname") != urlparse(origin).hostname \
                    or result.get("action") != "decide":
                return 403, "human_challenge_required", "Human verification failed or expired. Please verify again.", {}
            identity = identity_for(request, env)
            if identity is None:
                return 503, "human_gate_unavailable", UNAVAILABLE, {}
            # Verification may have crossed UTC midnight. Resolve the daily object
            # again so admission uses the current visitor ID.
            stub = env.HUMAN_GATE.get(env.HUMAN_GATE.idFromName(identity))
            meter = as_dict(await stub.take(intent))
        headers = {REMAINING_HEADER: str(meter["remaining"])}
        reason = meter["reason"]
        if reason:
            headers["retry-after"] = str(meter["retry_after"])
            messages = {
                "intent": "This decision action has expired or used its request allowance. Start a new lookup and verify again.",
                "day": "You have used today's 20 manual decisions. Come back after midnight UTC or use the paid API or MCP.",
                "burst": "Three decisions per minute is the manual lookup limit. Wait a minute, then verify again.",
                "sweep": "This lookup pattern resembles an automated sweep. Wait ten minutes and verify again, or use the paid API or MCP.",
            }
            return 429, LIMIT_CODES[reason], messages[reason], headers
        return 200, "", "", headers
    except Exception as exc:
        # An unavailable verifier or counter must never grant a free decision.
        log_unavailable("admit", exc)
        return 503, "human_gate_unavailable", UNAVAILABLE, {}
