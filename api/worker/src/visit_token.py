"""MODEL-292: a short-lived, visitor-and-origin-bound page credential."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from urllib.parse import urlparse

import access
import human_gate

HEADER = "x-modelspec-visit-token"
EXPIRY_HEADER = "x-modelspec-visit-expires"
SECRET_VAR = "VISIT_TOKEN_HMAC_KEY"
LIFETIME_SECONDS = 30 * 60
REFUSALS = {"visit_token_invalid": 401, "visit_token_expired": 401}


def enabled(env):
    return access.enforcement(getattr(env, "VISIT_GATE_ENABLED", None))


def limits(env, scope):
    """Allowances are configuration, with defaults in wrangler.jsonc."""
    day = int(getattr(env, f"VISIT_{scope.upper()}_DAY_LIMIT"))
    burst = int(getattr(env, f"VISIT_{scope.upper()}_BURST_LIMIT"))
    if day <= 0 or burst <= 0:
        raise ValueError("invalid visit allowance")
    return day, burst


def secret_for(env):
    secret = str(getattr(env, SECRET_VAR, "") or "")
    if len(secret) < 32:
        raise ValueError("visit signing secret unavailable")
    return secret.encode("utf-8")


def issue(identity, origin, secret, now=None):
    issued = int(time.time() if now is None else now)
    expires = issued + LIFETIME_SECONDS
    payload = json.dumps([identity, origin, issued, expires], separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return encoded + "." + signature, expires


def verify(token, identity, origin, secret, now=None):
    """Return an access error or None. Authenticate before examining expiry."""
    try:
        if not token or len(token) > 2048:
            return "visit_token_invalid"
        encoded, signature = token.split(".")
        expected = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return "visit_token_invalid"
        bound_id, bound_origin, issued, expires = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        moment = time.time() if now is None else now
        if bound_id != identity or bound_origin != origin or type(issued) is not int or type(expires) is not int \
                or expires - issued != LIFETIME_SECONDS or issued > moment:
            return "visit_token_invalid"
        return "visit_token_expired" if moment >= expires else None
    except (ValueError, TypeError, UnicodeError):
        return "visit_token_invalid"


def credential(request, env, origins):
    origin = str(request.headers.get("origin") or "")
    if origin not in origins:
        return None
    identity = human_gate.identity_for(request, env)
    if not identity:
        raise ValueError("visitor identity unavailable")
    return identity, origin, secret_for(env)


async def exchange(request, env, origins, siteverify):
    try:
        bound = credential(request, env, origins)
        if bound is None:
            return 401, {"error": {"code": "human_origin_required", "message": "Use an API key for machine access."}}
        # Do not issue an unusable credential when its meter is unconfigured.
        limits(env, "decide")
        limits(env, "vocabulary")
        if getattr(env, "HUMAN_GATE", None) is None or not getattr(env, "TURNSTILE_SECRET", None):
            raise ValueError("visit gate unavailable")
        token = str(request.headers.get(human_gate.TOKEN_HEADER) or "")
        result = await siteverify(str(env.TURNSTILE_SECRET), token) if token and len(token) <= 2048 else None
        if not isinstance(result, dict) or result.get("success") is not True \
                or result.get("hostname") != urlparse(bound[1]).hostname or result.get("action") != "decide":
            return 403, {"error": {"code": "human_challenge_required", "message": "Human verification failed or expired."}}
        # The daily identity may have rotated during Siteverify.
        bound = credential(request, env, origins)
        value, expires = issue(*bound)
        return 200, {"token": value, "expires_at": expires}
    except Exception:
        return 503, {"error": {"code": "human_gate_unavailable", "message": "Human verification is temporarily unavailable."}}


async def admit(request, env, origins, scope, payload=None):
    try:
        bound = credential(request, env, origins)
        code = verify(str(request.headers.get(HEADER) or ""), *bound) if bound else "visit_token_invalid"
        if code:
            return 401, code, "Refresh human verification for this visit.", {}
        limits(env, scope)
        binding = env.HUMAN_GATE
        stub = binding.get(binding.idFromName(bound[0]))
        if scope == "vocabulary":
            meter = human_gate.as_dict(await stub.take_visit_vocabulary())
        else:
            meter = human_gate.as_dict(await stub.take_visit(human_gate.intent_for(request), json.dumps(payload)))
        headers = {human_gate.REMAINING_HEADER: str(meter["remaining"])}
        if meter["reason"]:
            headers["retry-after"] = str(meter["retry_after"])
            return 429, human_gate.LIMIT_CODES[meter["reason"]], "Human lookup allowance reached. Wait or use the paid API or MCP.", headers
        value, expires = issue(*bound)
        return 200, "", "", {**headers, HEADER: value, EXPIRY_HEADER: str(expires)}
    except Exception:
        return 503, "human_gate_unavailable", "Human verification is temporarily unavailable.", {}
