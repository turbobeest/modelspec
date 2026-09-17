"""One code path from a presented key to an answer (MODEL-69).

`serve` is the whole of it. A request arrives with a key or without one; it is
classified, metered and either answered or refused, and the Worker's entry point
supplies the two things this module deliberately does not know: how to build a
live answer, and how to build a sandbox one.

    outcome = await access.serve(
        api_key=keys.extract(request.headers.get),
        kv=access_kv.CloudflareKV(env.API_KEYS),
        policy=access_config.load_policy(env),
        envelope=service._envelope({}, service_commit, origin),
        live=lambda record: self._rank(request_payload),
        sandbox=lambda: access_sandbox.rank_response(parsed, envelope=envelope),
    )

Three properties this file exists to keep, each with a test that fails if it
stops being true:

1. **The sandbox never reaches data.** The `test_` branch returns before the key
   store is read and before `live` is called. Not "does not normally"; cannot.
2. **There is one live path.** An exempt key is a key whose tier has `null`
   limits. It is looked up, metered and served by the same statements as a
   paying key, and `tests/test_api_access.py` asserts that the sequence of steps
   recorded for the two is identical, and that no module in this package so much
   as mentions the exempt tier by name outside a comment.
3. **A key is never written down.** What is logged, returned, and stored is a
   fingerprint. The secret exists in this module as a local variable and leaves
   as nothing.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import access_keys as keys
import access_limits as limits
from access_config import AccessPolicy, PolicyError
from access_keys import KeyRecord

HTTP_OK = 200
#: No key, or a key that is not ours. 401 rather than 403: the caller may
#: retry with credentials, which is exactly what 401 means.
HTTP_UNAUTHORIZED = 401
#: A key we know and will not serve — revoked. The caller retrying with the
#: same key will not help, which is what separates this from 401.
HTTP_FORBIDDEN = 403
HTTP_RATE_LIMITED = 429
#: The key is fine and the configuration is not. Ours, not the caller's.
HTTP_MISCONFIGURED = 500

MISSING_KEY = "missing_api_key"
INVALID_KEY = "invalid_api_key"
REVOKED_KEY = "key_revoked"
RATE_LIMITED = "rate_limited"
TIER_NOT_CONFIGURED = "tier_not_configured"


@dataclass
class Outcome:
    """A status, a body, the headers that go with it, and how it was reached."""

    status: int
    body: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)
    trace: tuple[str, ...] = ()
    tier: str | None = None
    key_id: str | None = None
    meter: limits.MeterOutcome | None = None

    @property
    def served(self) -> bool:
        return self.status < 400


def _how_to_get_a_key(policy: AccessPolicy) -> dict[str, str]:
    """Said in every refusal. A 401 that does not say what to do is a dead end."""
    return {
        "how_to_get_a_key": policy.url("get_a_key"),
        "sandbox": (
            f"any key beginning {policy.sandbox_prefix!r} is answered from the "
            "sandbox: unlimited, no signup, fixed synthetic results"
        ),
        "docs": policy.url("docs"),
    }


def _refusal(status: int, code: str, message: str, *, envelope: dict[str, Any],
             detail: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = {**envelope, "error": {"code": code, "message": message, **(detail or {})},
            "result": []}
    return status, body


def _rate_limit_headers(meter: limits.MeterOutcome, now: datetime) -> dict[str, str]:
    window = meter.refused_by or meter.window(limits.DAY)
    if window is None or window.limit is None:
        return {}
    headers = {
        "ratelimit-limit": str(window.limit),
        "ratelimit-remaining": str(window.remaining or 0),
        "ratelimit-reset": str(window.retry_after(now)),
    }
    if not meter.allowed:
        headers["retry-after"] = str(window.retry_after(now))
    return headers


def rate_limited_body(meter: limits.MeterOutcome, record: KeyRecord,
                      policy: AccessPolicy, now: datetime,
                      envelope: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """The 429. States the limit, the window, and when it resets.

    Both windows are reported, not just the one that refused: a caller at 5 in a
    minute wants to know whether the day is nearly gone as well.
    """
    refused = meter.refused_by
    assert refused is not None  # only called on a refusal
    detail = {
        **refused.to_json(now),
        "tier": record.tier,
        "windows": [w.to_json(now) for w in meter.windows],
        **_how_to_get_a_key(policy),
        "upgrade": policy.url("get_a_key"),
    }
    message = (
        f"rate limit reached: {refused.limit} request(s) per "
        f"{refused.window}. This window resets at {refused.to_json(now)['resets_at']}"
        f" ({refused.retry_after(now)}s). The sandbox is unlimited."
    )
    return _refusal(HTTP_RATE_LIMITED, RATE_LIMITED, message,
                    envelope=envelope, detail=detail)


async def serve(
    *,
    api_key: str | None,
    kv: Any,
    policy: AccessPolicy,
    live: Callable[[KeyRecord], Awaitable[tuple[int, dict[str, Any]]]],
    sandbox: Callable[[], tuple[int, dict[str, Any]]],
    envelope: dict[str, Any] | None = None,
    now: datetime | None = None,
    log: Callable[[str, dict[str, Any]], None] | None = None,
) -> Outcome:
    """Classify, meter, answer. The only entry point this package offers."""
    moment = now or datetime.now(UTC)
    shell = dict(envelope or {})
    trace: list[str] = []

    def note(event: str, **fields: Any) -> None:
        trace.append(event)
        if log is not None:
            log(event, fields)

    key = keys.normalise(api_key)
    if key is None:
        note("key.absent")
        status, body = _refusal(
            HTTP_UNAUTHORIZED, MISSING_KEY,
            "this endpoint requires an API key. Send it as "
            "'Authorization: Bearer <key>' or 'X-API-Key: <key>'. "
            f"Get one at {policy.url('get_a_key')}.",
            envelope=shell, detail=_how_to_get_a_key(policy))
        return Outcome(status, body, {"www-authenticate": 'Bearer realm="modelspec"'},
                       tuple(trace))

    identifier = keys.key_id(key)

    # The sandbox short-circuit. Before the key store, before the export,
    # before anything that could be called a data path.
    if keys.is_sandbox(key, policy):
        tier = policy.tier(policy.sandbox_tier)
        if not tier.live_data:
            note("key.sandbox", key_id=identifier, tier=tier.name)
            status, body = sandbox()
            return Outcome(status, body,
                           {"x-modelspec-tier": tier.name, "x-modelspec-key-id": identifier},
                           tuple(trace), tier=tier.name, key_id=identifier)

    note("key.lookup", key_id=identifier)
    record = await keys.lookup(kv, key)
    if record is None:
        note("key.unknown", key_id=identifier)
        status, body = _refusal(
            HTTP_UNAUTHORIZED, INVALID_KEY,
            "that API key is not recognised. Check it was copied whole, or get "
            f"one at {policy.url('get_a_key')}.",
            envelope=shell, detail=_how_to_get_a_key(policy))
        return Outcome(status, body, {"www-authenticate": 'Bearer realm="modelspec"'},
                       tuple(trace), key_id=identifier)

    if not record.active:
        note("key.revoked", key_id=record.key_id, tier=record.tier)
        status, body = _refusal(
            HTTP_FORBIDDEN, REVOKED_KEY,
            f"that API key has been revoked. Get a new one at {policy.url('get_a_key')}.",
            envelope=shell, detail=_how_to_get_a_key(policy))
        return Outcome(status, body, {}, tuple(trace), tier=record.tier,
                       key_id=record.key_id)

    try:
        tier = policy.tier(record.tier)
    except PolicyError as exc:
        note("tier.missing", key_id=record.key_id, tier=record.tier)
        status, body = _refusal(
            HTTP_MISCONFIGURED, TIER_NOT_CONFIGURED,
            f"this key names a tier the service is not configured for: {exc}",
            envelope=shell)
        return Outcome(status, body, {}, tuple(trace), tier=record.tier,
                       key_id=record.key_id)

    # Every live call is metered, including the ones no limit will refuse.
    note("limits.consume", key_id=record.key_id, tier=tier.name)
    meter = await limits.consume(kv, record.key_id, tier, moment)
    headers = {"x-modelspec-tier": tier.name, "x-modelspec-key-id": record.key_id,
               **_rate_limit_headers(meter, moment)}
    if not meter.allowed:
        note("limits.refused", key_id=record.key_id, tier=tier.name,
             scope=(meter.refused_by.scope if meter.refused_by else None))
        status, body = rate_limited_body(meter, record, policy, moment, shell)
        return Outcome(status, body, headers, tuple(trace), tier=tier.name,
                       key_id=record.key_id, meter=meter)

    note("serve.live", key_id=record.key_id, tier=tier.name)
    status, body = await live(record)
    return Outcome(status, body, headers, tuple(trace), tier=tier.name,
                   key_id=record.key_id, meter=meter)
