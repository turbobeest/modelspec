"""The Worker's Cloudflare entry point (MODEL-68, MODEL-80).

Deliberately thin. Everything that decides what the answer is lives in
`rank_service.py` and `policy_service.py`, which import nothing from the
Workers runtime and are therefore exercised directly by
`tests/test_rank_worker.py` and `tests/test_policy_check.py` under CPython.
What is left here is transport: route, read the body, fetch the published
export, read the determination store, serialise, and report the deployed
version.

The decision endpoints differ in one way that matters. `POST /v1/rank`,
`POST /v1/decide`, and `POST /v1/compare` hold no private data at all.
`POST /v1/policy-check` (MODEL-80) answers from the
public export *plus*, for an entitled caller, the policy determinations — which
are the paid product, are never in this repository, and reach the Worker only
through Workers KV, staged by `api/worker/load_determinations.py`. See
`docs/policy-check-api.md` for the trust boundary. `_entitlement()` below is the
one place a request is granted the private store, and it grants it by the tier
MODEL-69's access gate resolved from a presented key.

`POST /v1/signals` (MODEL-113) is a separate intake path. It authenticates the
exact body with a Grok Bot HMAC secret and writes a pending record to the
existing `ACCESS` KV namespace. Its read and acknowledgement routes require a
different secret held only by the repository workflow. The feature ships off.

`POST /v1/feedback` (MODEL-221) takes a rating of an answer from a person or an
agent, with no key. Storage ships off (`FEEDBACK_ENABLED`); when on, a record
goes to its own KV namespace, `FEEDBACK`, and holds no address, key or user
agent. `feedback_service.py` owns the rules; `docs/design/feedback-privacy.md`
says why.

All decision POST endpoints pass through that gate (`access.gate`, `docs/api-access.md`)
after the body is read and before any export is fetched. It ships with
enforcement OFF (`ACCESS_ENFORCED`): an unkeyed request is answered exactly as
before, a presented key is checked, metered and served per its tier, and a bad
key is refused rather than downgraded to anonymous.

The export is the same static JSON the sites and the CLI read
(`https://modelspec.dev/api/rank/...`). There is no database and no private
store on this path: the endpoint computes a fresh answer from current public
data on every request, which is the whole reason it exists.

`BUILD_COMMIT` is the deployed version. CI injects it per deploy
(`wrangler deploy --var`), `/v1/health` and every response echo it back as
`service_commit`, and the deploy's smoke test refuses to pass until the value it
reads is the sha it just pushed. MODEL-9 shipped three changes that were never
exercised because a smoke test could not tell a new deployment from an old
instance still answering; this is the cheap version of that lesson for a Worker.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import replace
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

# Load the private bundle before request schemas.
try:
    import bundled_data
except ModuleNotFoundError as exc:
    if exc.name != "bundled_data":
        raise

import access
import agent_guide
import access_config
import access_keys
import access_kv
import access_sandbox
import billing
import billing_page
import credits
import decide_service
import display_vocabulary
import feedback_service
import human_gate
import kv_value
import policy_service
import rank_service as service
import signals_service
import visitor
import visit_token
import x402
from credits_do import CreditsObject  # noqa: F401 — Wrangler class_name
from human_gate_do import HumanGateObject  # noqa: F401 — Wrangler class_name
from js import fetch
from workers import Response, WorkerEntrypoint

from decision.registry import default as _decision_registry

#: Files the endpoint reads. `candidates.json` is the catalogue; `hardware.json`
#: is the device vocabulary, added by MODEL-68 and absent from older exports —
#: its loss degrades `environment.hardware` to "refused", never to a wrong
#: answer.
CANDIDATES_PATH = "/api/rank/candidates.json"
HARDWARE_PATH = "/api/rank/hardware.json"
#: The public half of the compliance answer (MODEL-80): licence, origin,
#: commercial-use grant and per-platform availability for every card.
POLICY_PATH = "/api/policy/catalogue.json"
DECISION_SNAPSHOT_PATH = "/api/decision/snapshot.json.gz"
#: Reserved URL shape for the separate retained-snapshot hosting work. Unlike
#: ``DECISION_SNAPSHOT_PATH``, this is not a currently published static path;
#: comparison requests report ``comparison_snapshot_unavailable`` on its 404.
DECISION_HISTORY_TEMPLATE = "/api/decision/snapshots/{snapshot_id}.json.gz"
SNAPSHOT_KEY_VAR = "MODELSPEC_SNAPSHOT_KEY"
SIGNALS_ENABLED_VAR = "SIGNALS_ENABLED"
SIGNALS_HMAC_SECRET_VAR = "SIGNALS_HMAC_SECRET"
SIGNALS_READ_KEY_VAR = "SIGNALS_READ_KEY"
#: MODEL-221. Feedback storage: the switch (ships off), its own KV namespace,
#: and the secret that keys the abuse-limit counters so no address is stored.
FEEDBACK_ENABLED_VAR = "FEEDBACK_ENABLED"
FEEDBACK_BINDING = "FEEDBACK"
FEEDBACK_PEPPER_VAR = "FEEDBACK_LIMIT_PEPPER"
#: Comma-separated extra browser origins for local development only
#: (`--var FEEDBACK_DEV_ORIGINS:http://localhost:8000`). Empty in wrangler.jsonc.
FEEDBACK_DEV_ORIGINS_VAR = "FEEDBACK_DEV_ORIGINS"

#: KV keys holding the private determinations, staged by
#: `api/worker/load_determinations.py`. The manifest is read first and verified
#: against the blobs, so a half-finished load is never served.
KV_MANIFEST = "determinations/manifest"
KV_COMMERCIAL_USE = "determinations/commercial_use"
KV_RESIDENCY = "determinations/residency"

#: MODEL-69. The KV binding that holds key records and their counters — not
#: `DETERMINATIONS`, which holds our research and is only ever read. Bound in
#: `wrangler.jsonc` since 2026-09-18; a Worker deployed without it refuses a
#: presented live key `access_store_not_configured`.
ACCESS_BINDING = "ACCESS"
#: The enforcement switch. Off: an unkeyed request is served as the free tier,
#: exactly as before MODEL-69, and a presented key is checked. On: an unkeyed
#: request is a 401. Flipped in `wrangler.jsonc` once keys can be obtained.
ACCESS_ENFORCED_VAR = "ACCESS_ENFORCED"
#: MODEL-73. Hosted Checkout and the webhook that records the entitlement. Ships off.
BILLING_ENABLED_VAR = "BILLING_ENABLED"
STRIPE_WEBHOOK_SECRET_VAR = "STRIPE_WEBHOOK_SECRET"
STRIPE_SECRET_KEY_VAR = "STRIPE_SECRET_KEY"

#: Everything this Worker serves. Named back to the caller by every 404, so an
#: unrouted path — the bare root included — is a usable answer rather than a
#: dead end. `.github/scripts/check_rank_response.py` asserts every one of them
#: is named. `/v1/policy-check` (MODEL-80) is on this list for the same reason
#: `/v1/rank` is: a caller who mistypes it must be told it exists.
ACCEPTED_ENDPOINTS = (
    "POST /v1/rank", "POST /v1/decide", "POST /v1/compare",
    "POST /v1/policy-check", "POST /v1/feedback", "DELETE /v1/feedback", "GET /v1/health",
    "POST /v1/signals", "POST /v1/signals/discovered",
    "GET /v1/signals/pending", "POST /v1/signals/ack",
    "GET /v1/credits", "GET /v1/human-status",
    "POST /v1/billing/checkout", "POST /v1/billing/stripe-webhook",
    "GET /v1/billing/claim", "POST /v1/billing/claim", "POST /v1/billing/rotate",
)



def _accepted_endpoints(env) -> list[str]:
    """ACCEPTED_ENDPOINTS plus the routes this deployment switches on."""
    return [*ACCEPTED_ENDPOINTS,
            *(["POST /v1/visit-token"] if visit_token.enabled(env) else []),
            *(["GET /v1/vocabulary"] if globals().get("bundled_data") is not None else [])]


#: The subset that takes a body. All refuse a wrong verb through the one
#: `_method_not_allowed` below, and a path outside this tuple is a 404 before
#: anything is read or fetched.
POST_ENDPOINTS = ("/v1/rank", "/v1/decide", "/v1/compare", "/v1/policy-check")

# The browser clients: the production site (what SITE_MODE=live serves on the
# apex and www) and the private Pages preview branch deployed by
# `.github/workflows/deploy-sites.yml`, which is what gets tested before a flip.
CORS_ORIGINS = frozenset({
    "https://modelspec.dev",
    "https://www.modelspec.dev",
    "https://internal.modelspec-7np.pages.dev",
})

#: How long a fetched export is reused inside one isolate. Short enough that a
#: site deploy reaches callers quickly, long enough that a burst of requests
#: does not re-fetch 2 MB each time.
EXPORT_TTL_SECONDS = 300

#: Module-scope, so it survives across requests within an isolate and is
#: rebuilt by the memory snapshot on a cold start.
_cache: dict[str, object] = {"at": 0.0, "candidates": None, "hardware": None,
                            "prepared": None, "error": None}

#: The policy export and the determination store, cached on the same terms. The
#: determinations change when someone runs the loader, which is rare; the TTL
#: is the same one so that a deploy and a load both reach callers in five
#: minutes rather than by two different rules.
_policy_cache: dict[str, object] = {"at": 0.0, "catalogue": None, "error": None}
#: One `decide_service.SnapshotHolder` per export origin (MODEL-159): the
#: verified snapshot, revalidated against the origin at most once a minute.
_decision_holders: dict[str, object] = {}
#: `state` is one of the `STORE_*` values below; `error` is set only when it is
#: `broken`; `message` is the operator-facing sentence for whichever it is.
_store_cache: dict[str, object] = {"at": 0.0, "store": None, "error": None,
                                   "state": None, "message": None}


# Cloudflare captures top-level Python work in its deployment memory snapshot.
# No network or deployment secret is needed to parse/index the bundled bytes.
# The first request still authenticates their checked hash with the runtime key.
_decision_registry()
_bundled_decision_snapshot = None
_bundled_vocabulary = None
_bundled_vocabulary_text = None
if globals().get("bundled_data") is not None:
    _snapshot_bytes = bundled_data.read(DECISION_SNAPSHOT_PATH)
    if _snapshot_bytes is not None:
        _bundled_decision_snapshot = decide_service.load_snapshot_bytes(
            _snapshot_bytes, key=None, public_keys={}, include_archive=True,
            source="bundled decision snapshot",
        )
    del _snapshot_bytes
    _vocabulary_bytes = bundled_data.read("/api/decision/vocabulary.json")
    if _vocabulary_bytes is not None:
        # A malformed required vocabulary must fail deployment snapshot creation,
        # rather than publish an isolate that cannot serve its bundled data.
        _bundled_vocabulary_text = _vocabulary_bytes.decode("utf-8")
        _bundled_vocabulary = json.loads(_bundled_vocabulary_text)
    del _vocabulary_bytes

# Captured as False at deployment, then claimed before the first request awaits.
# Never retain a request, environment, or timer from deployment in the snapshot.
_isolate_served = False


def _decide_service():
    return decide_service


def _bundled_read(url: str):
    try:
        import bundled_data
    except ModuleNotFoundError as exc:
        if exc.name != "bundled_data":
            raise
        return False, None
    # A bundled deployment never falls back to public data, including history.
    return True, bundled_data.read(urlparse(url).path)


async def _get_json(url: str):
    bundled, raw = _bundled_read(url)
    if bundled:
        if raw is None:
            raise RuntimeError("private bundle is missing a required export")
        return json.loads(raw)
    response = await fetch(url)
    if not response.ok:
        raise RuntimeError(f"{url} returned HTTP {response.status}")
    return json.loads(await response.text())


# Bundled exports cannot change within this deployment. Prepare them in the
# deployment memory snapshot, as we already do for the decision snapshot.
if globals().get("bundled_data") is not None:
    _rank_bytes = bundled_data.read(CANDIDATES_PATH)
    if _rank_bytes is not None:
        # Malformed required candidates must fail deployment snapshot creation.
        _rank_export = json.loads(_rank_bytes)
        _hardware_bytes = None
        try:
            _hardware_bytes = bundled_data.read(HARDWARE_PATH)
            _hardware = json.loads(_hardware_bytes) if _hardware_bytes else None
        except Exception:  # noqa: BLE001 - optional, just as in _load_export
            _hardware = None
        _cache.update(candidates=_rank_export,
                      hardware=_hardware,
                      prepared=service.candidates_from_export(_rank_export))
        del _rank_export, _hardware_bytes, _hardware
    del _rank_bytes


class _Fetched:
    def __init__(self, status: int, etag: str | None, body: bytes | None):
        self.status, self.etag, self.body = status, etag, body


def _snapshot_fetcher(url: str):
    """A conditional GET of the snapshot, for `decide_service.SnapshotHolder`."""

    async def fetch_snapshot(etag: str | None) -> _Fetched:
        bundled, raw = _bundled_read(url)
        if bundled:
            if raw is None:
                return _Fetched(404, None, None)
            import hashlib
            tag = hashlib.sha256(raw).hexdigest()
            return _Fetched(304, tag, None) if etag == tag else _Fetched(200, tag, raw)
        headers = {"If-None-Match": etag} if etag else {}
        try:  # pragma: no cover - isolate only
            from js import Object  # type: ignore[import-not-found]
            from pyodide.ffi import to_js  # type: ignore[import-not-found]
            # no-store: the site serves the snapshot with max-age=14400, and a
            # cached copy would hide a new snapshot for hours. The conditional
            # header still makes an unchanged snapshot a cheap 304.
            options = to_js({"headers": headers, "cache": "no-store"},
                            dict_converter=Object.fromEntries)
        except ImportError:
            options = {"headers": headers, "cache": "no-store"}
        response = await fetch(url, options)
        status = int(response.status)
        # A missing header is JS null, which Pyodide does not turn into None.
        raw_tag = response.headers.get("etag")
        tag = None if kv_value.absent(raw_tag) else str(raw_tag)
        if status != 200:
            return _Fetched(status, tag, None)
        from js import Uint8Array

        view = Uint8Array.new(await response.arrayBuffer())
        return _Fetched(status, tag, bytes(view.to_py()))

    return fetch_snapshot


def _decision_holder(origin: str):
    holder = _decision_holders.get(origin)
    if holder is None:
        holder = _decide_service().SnapshotHolder(
            _snapshot_fetcher(origin + DECISION_SNAPSHOT_PATH),
            bundled_snapshot=_bundled_decision_snapshot)
        _decision_holders[origin] = holder
    return holder


async def _load_export(origin: str, *, force: bool = False):
    """Fetch the export, or reuse the copy this isolate already has.

    A failed refresh does not discard a good copy: an export that still answers
    beats an error, which is the same call the CLI makes about a stale snapshot.
    """
    fresh = (time.time() - float(_cache["at"])) < EXPORT_TTL_SECONDS
    if not force and (fresh or globals().get("bundled_data") is not None) and _cache["candidates"] is not None:
        return _cache["candidates"], _cache["hardware"]

    try:
        candidates = await _get_json(origin + CANDIDATES_PATH)
    except Exception as exc:  # noqa: BLE001 - surfaced on /v1/health, never swallowed
        _cache["error"] = f"{type(exc).__name__}: {exc}"
        if _cache["candidates"] is not None:
            return _cache["candidates"], _cache["hardware"]
        raise

    try:
        hardware = await _get_json(origin + HARDWARE_PATH)
    except Exception:  # noqa: BLE001 - optional; `environment.hardware` reports its absence
        hardware = None

    _cache.update({"at": time.time(), "candidates": candidates,
                   "prepared": service.candidates_from_export(candidates),
                   "hardware": hardware, "error": None})
    return candidates, hardware


async def _load_policy_catalogue(origin: str):
    """Fetch `/api/policy/catalogue.json`, or reuse this isolate's copy.

    Same posture as `_load_export`: a failed refresh keeps a good copy rather
    than turning a working endpoint into an error.
    """
    fresh = (time.time() - float(_policy_cache["at"])) < EXPORT_TTL_SECONDS
    if fresh and _policy_cache["catalogue"] is not None:
        return _policy_cache["catalogue"]
    try:
        catalogue = await _get_json(origin + POLICY_PATH)
    except Exception as exc:  # noqa: BLE001 - surfaced on /v1/health, never swallowed
        _policy_cache["error"] = f"{type(exc).__name__}: {exc}"
        if _policy_cache["catalogue"] is not None:
            return _policy_cache["catalogue"]
        raise
    _policy_cache.update({"at": time.time(), "catalogue": catalogue, "error": None})
    return catalogue


#: The four states of the determination store, as `/v1/health` names them.
#: `unbound` and `empty` are normal and carry no error; `broken` is the only
#: one that does, and it stays loud. Every state but `loaded` makes
#: `_load_determinations` return `None`, so an entitled request is refused
#: with 503 in all three — an empty store is not an empty answer.
STORE_UNBOUND = "unbound"
STORE_EMPTY = "empty"
STORE_LOADED = "loaded"
STORE_BROKEN = "broken"

#: What each non-error state means, in the words an operator reads.
STORE_MESSAGES = {
    STORE_UNBOUND: "no DETERMINATIONS KV binding on this deployment",
    STORE_EMPTY: (f"no determinations loaded yet: {KV_MANIFEST} is not in the "
                  "namespace; run api/worker/load_determinations.py"),
}

#: "No such key", whichever way KV and Pyodide spell it. Shared with the access
#: store's adapter so the two cannot disagree (`kv_value.py`, #104).
_absent = kv_value.absent


def _store_state(state: str, *, error: str | None = None) -> None:
    _store_cache.update({"state": state, "error": error,
                         "message": error or STORE_MESSAGES.get(state)})


async def _load_determinations(env):
    """Read the determination store out of KV, or return `None`.

    `None` means "not available", and every caller of this treats that as a
    refusal rather than as an empty store: an empty store would answer
    `undetermined` for everything, which is exactly the free answer, which is
    the one thing a paid caller must never receive by accident.

    The reason is recorded in `_store_cache["state"]`, one of the four
    `STORE_*` values. Only `broken` sets `_store_cache["error"]`: no binding
    and no manifest yet are states, not faults.

    The manifest is read first and each blob is verified against the SHA-256 it
    records. That is what makes the loader's write order meaningful — a load
    that died between the two blobs leaves a manifest describing the previous
    pair, and a mismatch here is a hard failure rather than a half-snapshot.
    """
    kv = getattr(env, "DETERMINATIONS", None)
    if kv is None:
        _store_state(STORE_UNBOUND)
        return None
    fresh = (time.time() - float(_store_cache["at"])) < EXPORT_TTL_SECONDS
    if fresh and _store_cache["store"] is not None:
        return _store_cache["store"]

    try:
        manifest_text = await kv.get(KV_MANIFEST)
        if _absent(manifest_text):
            # Nothing loaded yet. A missing manifest is the empty store, and the
            # blobs are not read: without a manifest there is nothing to verify
            # them against, and a stray blob is not a bundle.
            _store_state(STORE_EMPTY)
            return None
        manifest = json.loads(str(manifest_text))
        if not isinstance(manifest, dict):
            raise RuntimeError(f"{KV_MANIFEST} is not a JSON object")
        blobs = {}
        for key in (KV_COMMERCIAL_USE, KV_RESIDENCY):
            text = await kv.get(key)
            if _absent(text):
                raise RuntimeError(f"{key} is named by the manifest and is not in "
                                   "the namespace")
            text = str(text)
            expected = (manifest.get("blobs") or {}).get(key, {}).get("sha256")
            actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if expected != actual:
                raise RuntimeError(
                    f"{key} does not match the manifest (sha256 {actual[:12]} vs "
                    f"{expected}). The bundle is mid-load or was written by hand.")
            blobs[key] = json.loads(text)
        store = {
            "bundle_version": manifest.get("bundle_version"),
            "generated_on": manifest.get("generated_on"),
            "commercial_use": blobs[KV_COMMERCIAL_USE].get("commercial_use") or {},
            "residency": blobs[KV_RESIDENCY].get("residency") or {},
        }
    except Exception as exc:  # noqa: BLE001 - reported; never degraded into a free answer
        _store_state(STORE_BROKEN, error=f"{type(exc).__name__}: {exc}")
        return None

    _store_cache.update({"at": time.time(), "store": store})
    _store_state(STORE_LOADED)
    return store


def _entitlement(tier, *, funded: bool = False) -> str:
    """Which store this request may read. The one place the private store is granted.

    A funded key (credits remaining for this call) gets the determinations.
    An unlimited paid tier (null daily and burst — the exempt row) still does,
    because that row is data, not a name we branch on. Everything else,
    anonymous included, is the free tier: a complete and labelled answer
    (`determinations.included: false`), not a degraded one.
    """
    if funded:
        return policy_service.ENTITLEMENT_DETERMINATIONS
    if tier is not None and tier.paid and tier.live_data and tier.unlimited:
        return policy_service.ENTITLEMENT_DETERMINATIONS
    return policy_service.ENTITLEMENT_PUBLIC


def _access_store(env):
    """The key store, or a stand-in that refuses every read when none is bound."""
    binding = getattr(env, ACCESS_BINDING, None)
    if binding is None:
        return access_kv.UnboundKV(ACCESS_BINDING)
    return access_kv.CloudflareKV(binding)


def _billing_unconfigured(service_commit: str):
    """The tier table is missing, so Checkout/webhook cannot map a price."""
    outcome = billing._refusal(
        billing.BILLING_NOT_CONFIGURED,
        "the access/billing layer is not configured on this deployment",
        service_commit=service_commit, endpoint="billing")
    return outcome.status, outcome.body


async def _stripe_http(url: str, *, method: str, headers: dict, body: str,
                       timeout_ms: int | None = None):
    """Workers HTTP adapter, injected into billing and Turnstile tests."""
    try:  # pragma: no cover - isolate only
        from js import Object  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]
        native = {"method": method, "headers": headers, "body": body}
        if timeout_ms is not None:
            from js import AbortSignal
            native["signal"] = AbortSignal.timeout(timeout_ms)
        options = to_js(native, dict_converter=Object.fromEntries)
    except ImportError:
        options = {"method": method, "headers": headers, "body": body}
    return await fetch(url, options)


def _known_hardware_for_sandbox(payload) -> set[str]:
    """The sandbox reads no hardware vocabulary, so it cannot refuse a device id.

    It accepts whichever id was sent, filters nothing by it, and says so by
    echoing it with `applied.hardware_id: null`. Every other field is validated
    by the live parser, so an integrator's error handling meets the same
    refusals it will meet with a live key.
    """
    environment = payload.get("environment") if isinstance(payload, dict) else None
    hardware = environment.get("hardware") if isinstance(environment, dict) else None
    return {hardware} if isinstance(hardware, str) else set()


async def _verify_turnstile(secret: str, token: str) -> dict:
    response = await _stripe_http(
        human_gate.SITEVERIFY, method="POST",
        headers={"content-type": "application/json"},
        body=json.dumps({"secret": secret, "response": token}), timeout_ms=10_000)
    return json.loads(await response.text()) if int(response.status) == 200 else {"success": False}


def _json_response(status: int, body: dict, extra_headers: dict | None = None) -> Response:
    return Response(
        json.dumps(body, indent=2, default=str),
        status=status,
        headers={
            # The access gate's headers first, so none of them can replace the
            # three below: rate-limit state, the tier and the key's fingerprint
            # (never the key).
            **(extra_headers or {}),
            "content-type": "application/json; charset=utf-8",
            # A ranking is computed per request from data that changes on every
            # site deploy. Caching it at the edge would hand callers an answer
            # whose `build.commit` no longer describes the catalogue.
            "cache-control": "no-store",
            "x-modelspec-service-commit": str(body.get("service_commit") or ""),
        },
    )


class _DecisionTransport:
    def __init__(self):
        self.body: dict | None = None
        self.serialised: bytes | None = None
        self.headers: dict[str, str] = {}


def _decision_response(status: int, body: dict,
                       extra_headers: dict | None = None,
                       transport: _DecisionTransport | None = None) -> Response:
    decider = _decide_service()
    if status != decider.HTTP_OK:
        transport = None
    # The timed bytes are reused only for the very body they encode: x402's
    # unfunded fallback answers with a copy that adds credits.exhausted.
    serialised = transport.serialised if transport is not None and transport.body is body else None
    return Response(
        (serialised if serialised is not None else decider.serialise(body)).decode("utf-8"),
        status=status,
        headers={
            **(extra_headers or {}),
            **(transport.headers if transport is not None else {}),
            "content-type": "application/json; charset=utf-8",
            "cache-control": "no-store",
        },
    )


def _cors_headers(request, env=None) -> dict[str, str]:
    origin = str(request.headers.get("origin") or request.headers.get("Origin") or "")
    if origin not in CORS_ORIGINS:
        return {}
    # MODEL-292: the visit credential headers exist only while its gate is on.
    visit = visit_token.enabled(env)
    return {
        "access-control-allow-origin": origin,
        "access-control-allow-methods": "POST, OPTIONS",
        "access-control-allow-headers":
            "authorization, content-type, x-api-key, x-payment, x-modelspec-snapshot, x-modelspec-turnstile, x-modelspec-intent"
            + (f", {visit_token.HEADER}" if visit else ""),
        "access-control-expose-headers": (
            "x-modelspec-snapshot, x-modelspec-snapshot-stale, "
            "x-modelspec-decisions-remaining, "
            + (f"{visit_token.HEADER}, {visit_token.EXPIRY_HEADER}, " if visit else "")
            + "retry-after, Server-Timing"
        ),
        "access-control-max-age": "86400",
        "vary": "Origin",
    }


def _site_free_visitor(request, api_key: str | None, enabled: bool, env=None) -> str | None:
    """Return the anonymous meter key for an admitted browser request.

    None when the keyed visitor id is unavailable (no VISITOR_HMAC_KEY): the
    request then takes the paid path rather than a bare-hash meter."""
    if api_key is not None or not enabled or visit_token.enabled(env):
        return None
    origin = str(request.headers.get("origin") or request.headers.get("Origin") or "")
    if origin not in CORS_ORIGINS:
        return None
    return visitor.visitor_id_for(request, env)


def _html_response(status: int, page: str, service_commit: str,
                   extra_headers: dict | None = None) -> Response:
    """A page for a person's browser (the claim page). Never cached: it holds a key."""
    return Response(
        page,
        status=status,
        headers={
            **(extra_headers or {}),
            **billing_page.HEADERS,
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-store",
            "x-modelspec-service-commit": service_commit,
        },
    )


def _response_encoding(accepted: str) -> str | None:
    qualities = {}
    for item in accepted.lower().split(","):
        parts = item.strip().split(";")
        quality = 1.0
        for parameter in parts[1:]:
            if parameter.strip().startswith("q="):
                try:
                    quality = float(parameter.strip()[2:])
                except ValueError:
                    quality = 0.0
        qualities[parts[0].strip()] = quality if 0 <= quality <= 1 else 0.0
    choices = [(qualities.get(coding, qualities.get("*", 0)), coding)
               for coding in ("gzip", "br")]
    quality, coding = max(choices, key=lambda choice: (choice[0], choice[1] == "br"))
    return coding if quality > 0 else None


def _compress_response(request, response):
    """Let workerd encode JSON/HTML streams on every route, including refusals.

    Response defaults to automatic encodeBody. Setting Content-Encoding selects
    its native compressor, without a Python Brotli dependency or a second JSON
    serialization. HEAD and bodyless responses must not acquire a body.
    """
    if str(request.method).upper() == "HEAD" or response.status in (204, 304) or response.body is None:
        return response
    headers = {key.lower(): value for key, value in response.headers.items()}
    if "content-encoding" in headers or "no-transform" in headers.get("cache-control", ""):
        return response
    coding = _response_encoding(str(request.headers.get("accept-encoding") or ""))
    if coding is None:
        return response
    headers["content-encoding"] = coding
    headers.pop("content-length", None)
    vary = [value.strip() for value in headers.get("vary", "").split(",") if value.strip()]
    if not any(value.lower() in ("accept-encoding", "*") for value in vary):
        vary.append("Accept-Encoding")
    headers["vary"] = ", ".join(vary)
    return Response(response.body, status=response.status, headers=headers)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        global _isolate_served
        cold = not _isolate_served
        _isolate_served = True
        response = await self._fetch(request)
        headers = dict(response.headers.items())
        previous = next((value for key, value in headers.items()
                         if key.lower() == "server-timing"), "")
        headers = {key: value for key, value in headers.items()
                   if key.lower() != "server-timing"}
        timing = 'isolate;desc="cold"' if cold else 'isolate;desc="warm"'
        if cold:
            # Python runs only after workerd has restored its memory. Its clock
            # also freezes between I/O in production. Do not invent a duration.
            timing += ', startup;desc="runtime restore unobservable from Python"'
        if urlparse(str(request.url)).path.startswith("/v1/"):
            headers["Link"] = f'<{agent_guide.GUIDE_URL}>; rel="describedby"'
            headers["x-modelspec-guide-version"] = agent_guide.GUIDE_VERSION
            exposed = headers.get("access-control-expose-headers", "")
            headers["access-control-expose-headers"] = ", ".join(
                filter(None, [exposed, "Link", "x-modelspec-guide-version"]))
        headers["Server-Timing"] = f"{previous}, {timing}" if previous else timing
        body = response.body
        if str(request.method).upper() == "HEAD" or response.status in (204, 304):
            body = None
        response = Response(body, status=response.status, headers=headers)
        return _compress_response(request, response)

    async def _fetch(self, request):
        service_commit = str(getattr(self.env, "BUILD_COMMIT", "") or "unknown")
        origin = str(getattr(self.env, "EXPORT_ORIGIN", "") or "https://modelspec.dev")
        path = urlparse(str(request.url)).path.rstrip("/") or "/"
        method = str(request.method).upper()

        decider = None
        decision_transport = _DecisionTransport()
        if path in ("/v1/decide", "/v1/compare"):
            decider = _decide_service()

        if decider is not None and method == "OPTIONS":
            headers = _cors_headers(request, self.env)
            if not headers:
                return _json_response(service.HTTP_NOT_FOUND, {
                    "contract_version": decider.contract.CONTRACT_VERSION,
                    "endpoint": path.rsplit("/", 1)[-1],
                    "snapshot": None,
                    "error": {"code": "origin_not_allowed",
                              "message": f"this origin may not call {path}"},
                })
            return Response("", status=204, headers=headers)

        # With its gate off, the route does not exist: the generic 404 below answers it.
        if path == "/v1/visit-token" and visit_token.enabled(self.env):
            cors = _cors_headers(request, self.env)
            if method == "OPTIONS":
                return Response("", status=204, headers=cors)
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            status, body = await visit_token.exchange(request, self.env, CORS_ORIGINS, _verify_turnstile)
            return _json_response(status, body, cors)

        if path == "/v1/vocabulary":
            if globals().get("bundled_data") is not None:
                text = _bundled_vocabulary_text
                cors = _cors_headers(request, self.env)
                if method == "OPTIONS":
                    return Response("", status=204, headers={**cors, "access-control-allow-methods": "GET, HEAD, OPTIONS"})
                if method not in ("GET", "HEAD"):
                    return self._method_not_allowed(service_commit, path, "GET", method)
                if visit_token.enabled(self.env):
                    api_key = access_keys.extract(lambda name: request.headers.get(name))
                    admitted = False
                    if api_key is None and request.headers.get(visit_token.HEADER):
                        status, code, message, headers = await visit_token.admit(request, self.env, CORS_ORIGINS, "vocabulary")
                        admitted = status == 200
                        if not admitted and not (code == "visit_token_invalid" and not access.enforcement(getattr(self.env, ACCESS_ENFORCED_VAR, None))):
                            return _json_response(status, {"error": {"code": code, "message": message}}, {**cors, **headers})
                        if admitted:
                            cors.update(headers)
                    if not admitted:
                        async def allowed(*args):
                            return 200, {}
                        outcome = await access.gate(
                            api_key=api_key,
                            enforced=access.enforcement(getattr(self.env, ACCESS_ENFORCED_VAR, None)),
                            kv=_access_store(self.env), load_policy=lambda: access_config.load_policy(self.env),
                            anonymous=allowed, live=allowed,
                            sandbox=lambda: access.refusal(access.SANDBOX_NOT_AVAILABLE, "Use a live key for vocabulary.", envelope={}),
                        )
                        if not outcome.served:
                            return _json_response(outcome.status, outcome.body, {**cors, **outcome.headers})
                        cors.update(outcome.headers)
                elif human_gate.enabled(self.env):
                    try:
                        stub = human_gate.stub_for(request, self.env)
                        if stub is None:
                            raise RuntimeError("visitor identity unavailable")
                        meter = human_gate.as_dict(await stub.take_vocabulary())
                    except Exception:
                        return _json_response(503, {"error": {"code": "human_gate_unavailable", "message": human_gate.UNAVAILABLE}}, cors)
                    if meter["reason"]:
                        return _json_response(429, {"error": {"code": human_gate.LIMIT_CODES[meter["reason"]], "message": "Vocabulary lookup limit reached."}},
                                              {**cors, "retry-after": str(meter["retry_after"])})
                if text is None:
                    return _json_response(service.HTTP_BAD_GATEWAY, {"error": {
                        "code": "export_unavailable", "message": "bundled vocabulary is missing",
                    }}, cors)
                query = parse_qs(urlparse(str(request.url)).query, keep_blank_values=True)
                if any(key in query for key in ("section", "search", "id", "ids", "detail", "offset", "limit")):
                    try:
                        selected = display_vocabulary.lookup(
                            _bundled_vocabulary, section=query.get("section", ["starter"])[0],
                            search=query.get("search", [""])[0],
                            ids=[*query.get("id", []), *(item for value in query.get("ids", []) for item in value.split(","))],
                            detail=query.get("detail", ["compact"])[0],
                            offset=int(query.get("offset", ["0"])[0]),
                            limit=int(query.get("limit", ["20"])[0]),
                        )
                    except ValueError as exc:
                        return _json_response(400, {"error": {"code": "invalid_request", "message": str(exc)}}, cors)
                    text = json.dumps({"facets": [], "domains": [], "templates": [], "models": {}, "estate": {},
                                       **selected}, ensure_ascii=False)
                return Response("" if method == "HEAD" else text, status=200,
                                headers={**cors, "content-type": "application/json; charset=utf-8",
                                         "cache-control": "no-store" if visit_token.enabled(self.env) else "private, max-age=3600", "vary": "Origin"})
        if path == "/v1/feedback":
            return await self._feedback(request, method, service_commit)
        if path == "/v1/human-status":
            return await self._human_status(request, method)
        if path == "/v1/health":
            if method not in ("GET", "HEAD"):
                return self._method_not_allowed(service_commit, path, "GET", method)
            return await self._health(service_commit, origin)
        if path == "/v1/signals" or path.startswith("/v1/signals/"):
            return await self._signals(request, path, method, service_commit)
        if path.startswith("/v1/billing/"):
            return await self._billing(request, path, method, service_commit)
        if path == "/v1/credits":
            if method not in ("GET", "HEAD"):
                return self._method_not_allowed(service_commit, path, "GET", method)
            return await self._credits(request, service_commit, origin)
        if path not in POST_ENDPOINTS:
            # Including the bare root: the route covers the whole host, so an
            # unknown path is answered here rather than left to Cloudflare's
            # 522, which reads like an outage. No export fetch — a crawler
            # asking for /favicon.ico must not cost a subrequest.
            return _json_response(service.HTTP_NOT_FOUND, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "not_found", "message": f"no endpoint at {path}",
                          "accepted": _accepted_endpoints(self.env)},
                "result": [],
            })
        if method != "POST":
            return self._method_not_allowed(service_commit, path, "POST", method)

        max_body = (
            policy_service.MAX_BODY_BYTES
            if path == "/v1/policy-check"
            else decider.MAX_BODY_BYTES
            if decider is not None
            else service.MAX_BODY_BYTES
        )
        raw = await request.text()
        if len(raw.encode("utf-8")) > max_body:
            response = {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "payload_too_large",
                          "message": f"the body must be at most {max_body} bytes"},
                "result": [],
            }
            if decider is not None:
                response = decider.error_response(
                    "payload_too_large",
                    f"the body must be at most {max_body} bytes",
                    status=service.HTTP_PAYLOAD_TOO_LARGE,
                    snapshot_id=None,
                    endpoint=path.rsplit("/", 1)[-1],
                )[1]
                return _decision_response(
                    service.HTTP_PAYLOAD_TOO_LARGE, response, _cors_headers(request, self.env)
                )
            return _json_response(service.HTTP_PAYLOAD_TOO_LARGE, response)

        try:
            payload = json.loads(raw) if raw.strip() else None
        except ValueError as exc:
            if path == "/v1/policy-check":
                status, body = policy_service.error_response(
                    policy_service.RequestError(
                        "invalid_request", f"the body is not valid JSON: {exc}"),
                    None, service_commit, origin)
            elif decider is not None:
                status, body = decider.error_response(
                    "invalid_request",
                    f"the body is not valid JSON: {exc}",
                    status=decider.HTTP_BAD_REQUEST,
                    snapshot_id=None,
                    endpoint=path.rsplit("/", 1)[-1],
                )
                return _decision_response(status, body, _cors_headers(request, self.env))
            else:
                status, body = service.error_response(
                    service.RequestError(
                        "invalid_request", f"the body is not valid JSON: {exc}"),
                    None, service_commit, origin)
            return _json_response(status, body)

        # MODEL-69. Everything above is transport and costs no data; from here
        # on the access gate decides. It runs before either export is fetched,
        # so the sandbox never reaches data and a refused key costs nothing.
        api_key = access_keys.extract(lambda name: request.headers.get(name))
        if path == "/v1/policy-check":
            envelope = policy_service._envelope({}, service_commit, origin)

            async def _anonymous():
                return await self._policy_answer(payload, service_commit, origin,
                                                 _entitlement(None))

            async def _live(record, tier):
                return await self._policy_answer(payload, service_commit, origin,
                                                 _entitlement(tier, funded=True))

            async def _live_unfunded(record, tier):
                return await self._policy_answer(payload, service_commit, origin,
                                                 _entitlement(tier, funded=False))

            def sandbox():
                return access.refusal(
                    access.SANDBOX_NOT_AVAILABLE,
                    "the sandbox answers POST /v1/rank only; it holds no synthetic "
                    "policy data. Call /v1/policy-check with a live key.",
                    envelope=envelope)
        elif decider is not None:
            endpoint = path.rsplit("/", 1)[-1]
            envelope = {
                "contract_version": decider.contract.CONTRACT_VERSION,
                "endpoint": endpoint,
                "snapshot": getattr(_decision_holder(origin).snapshot, "snapshot_id", None),
                "service_commit": service_commit,
                "export_origin": origin,
            }

            sent = request.headers.get(decider.SNAPSHOT_HEADER)
            expected = None if _absent(sent) else str(sent).strip()

            async def _answer():
                if path == "/v1/compare":
                    return await self._compare(payload, origin, expected)
                return await self._decide(payload, origin, expected, decision_transport)

            async def _anonymous():
                return await _answer()

            async def _live(record, tier):
                return await _answer()

            async def _live_unfunded(record, tier):
                if path == "/v1/decide" and human_gate.enabled(self.env):
                    return decider.error_response(
                        "payment_required", "Machine decisions require remaining paid credits. "
                        "Use a funded API key or the paid MCP service.",
                        status=402, snapshot_id=envelope["snapshot"])
                return await _answer()

            def sandbox():
                return access.refusal(
                    access.SANDBOX_NOT_AVAILABLE,
                    "the sandbox has no synthetic signed decision snapshot; use a live request",
                    envelope=envelope,
                )
        else:
            envelope = service._envelope({}, service_commit, origin)

            async def _anonymous():
                return await self._rank(payload, service_commit, origin)

            async def _live(record, tier):
                return await self._rank(payload, service_commit, origin)

            async def _live_unfunded(record, tier):
                return await self._rank(payload, service_commit, origin)

            def sandbox():
                try:
                    parsed = service.parse_request(payload,
                                                   _known_hardware_for_sandbox(payload))
                except service.RequestError as exc:
                    return service.error_response(exc, None, service_commit, origin)
                return access_sandbox.rank_response(parsed, envelope=envelope)

        if path == "/v1/decide" and api_key is None and visit_token.enabled(self.env) and request.headers.get(visit_token.HEADER):
            status, code, message, gate_headers = await visit_token.admit(
                request, self.env, CORS_ORIGINS, "decide", payload)
            if status == 200:
                status, body = await _anonymous()
                return _decision_response(status, body, {
                    **gate_headers, **_decision_holder(origin).headers(), **_cors_headers(request, self.env),
                }, decision_transport)
            if not (code == "visit_token_invalid" and not access.enforcement(getattr(self.env, ACCESS_ENFORCED_VAR, None))):
                return _json_response(status, {**envelope, "error": {"code": code, "message": message}},
                                      {**gate_headers, **_cors_headers(request, self.env)})

        if path == "/v1/decide" and api_key is None and human_gate.enabled(self.env) and not visit_token.enabled(self.env):
            site_origin = str(request.headers.get("origin") or "") in CORS_ORIGINS
            # Other callers can still pay per call through x402 when it is on.
            if site_origin or not x402.load_config(self.env).enabled:
                status, code, message, gate_headers = await human_gate.admit(
                    request, self.env, CORS_ORIGINS, _verify_turnstile, payload)
                if status == 200:
                    status, body = await _anonymous()
                else:
                    return _json_response(status, {
                        "contract_version": decider.contract.CONTRACT_VERSION,
                        "endpoint": "decide",
                        "snapshot": None,
                        "error": {"code": code, "message": message},
                    }, {**gate_headers, **_cors_headers(request, self.env)})
                return _decision_response(status, body, {
                    **gate_headers, **_decision_holder(origin).headers(),
                    **_cors_headers(request, self.env),
                }, decision_transport)

        # MODEL-75. One wrap around the live/anonymous producers: x402 verify
        # and settle run before either of them writes an answer. The sandbox
        # is not wrapped. X402_ENABLED default off is a no-op.
        x402_trace = x402.ChargeTrace()
        free_visitor = _site_free_visitor(
            request, api_key, x402.load_config(self.env).enabled, self.env)
        anonymous = (
            _anonymous
            if free_visitor is not None
            else self._x402_wrap(_anonymous, request, path, api_key, envelope,
                                 payload, x402_trace, keyed=False)
        )
        live = self._x402_wrap(_live, request, path, api_key, envelope,
                               payload,
                               x402_trace, keyed=True,
                               produce_unfunded=_live_unfunded)

        outcome = await access.gate(
            api_key=access_keys.extract(lambda name: request.headers.get(name)),
            enforced=access.enforcement(getattr(self.env, ACCESS_ENFORCED_VAR, None)),
            kv=_access_store(self.env),
            load_policy=lambda: access_config.load_policy(self.env),
            anonymous=anonymous, live=live, sandbox=sandbox, envelope=envelope,
            limits_for=self._limits_for(api_key),
            anonymous_id=free_visitor,
        )
        headers = {
            **(outcome.headers or {}),
            **x402.http_headers(
                outcome.status, outcome.body, settlement=x402_trace.settlement
            ),
        }
        if path in ("/v1/decide", "/v1/compare"):
            if outcome.status == decider.HTTP_SERVICE_UNAVAILABLE \
                    and outcome.body.get("error") == "no_snapshot":
                headers["retry-after"] = str(decider.RETRY_AFTER_SECONDS)
            return _decision_response(
                outcome.status, outcome.body,
                {**headers, **_decision_holder(origin).headers(), **_cors_headers(request, self.env)},
                decision_transport,
            )
        return _json_response(outcome.status, outcome.body, headers)

    def _credit_params(self, path: str, payload=None) -> tuple[int, int, str]:
        try:
            policy = access_config.load_policy(self.env)
            clean_path = path.rstrip("/")
            if clean_path.endswith("policy-check"):
                resource = "policy-check"
            elif clean_path.endswith("decide"):
                explain = (
                    payload.get("explain", "summary")
                    if isinstance(payload, dict) else "summary"
                )
                resource = f"decide.{explain}"
            elif clean_path.endswith("compare"):
                resource = "decide.full"
            else:
                resource = "rank"
            return (policy.credits.weight(resource), policy.credits.pack_expiry_days,
                    policy.url("get_a_key") or "https://modelspec.dev/pricing")
        except access_config.PolicyError:
            return 1, 365, "https://modelspec.dev/pricing"

    def _limits_for(self, api_key):
        """Funded keys drop the daily window; unfunded billed keys use free limits."""

        async def limits_for(record, tier):
            if tier.unlimited:
                return tier
            holder = x402.holder_from_key(api_key)
            if not holder:
                return tier
            try:
                bal = await credits.ledger_from_env(self.env).balance(holder)
            except credits.StoreNotConfigured:
                return tier
            try:
                policy = access_config.load_policy(self.env)
            except access_config.PolicyError:
                return tier
            if bal.available > 0:
                return replace(tier, daily_limit=None,
                               burst_limit=policy.credits.burst_limit)
            try:
                return policy.tier("free")
            except access_config.PolicyError:
                return tier

        return limits_for

    async def _signals(self, request, path: str, method: str, service_commit: str):
        """Release-signal intake and the repository-only pending queue."""
        flag = signals_service.enabled(getattr(self.env, SIGNALS_ENABLED_VAR, None))
        if not flag:
            outcome = signals_service._error(
                404, "not_found", "release-signal intake is disabled"
            )
        elif path == "/v1/signals":
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            raw = (await request.text()).encode("utf-8")
            outcome = await signals_service.intake(
                raw=raw,
                signature=request.headers.get("x-modelspec-signature"),
                secret=str(getattr(self.env, SIGNALS_HMAC_SECRET_VAR, "") or "").encode(),
                enabled=True,
                kv=_access_store(self.env),
            )
        elif path == "/v1/signals/discovered":
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            outcome = await signals_service.discovered(
                raw=(await request.text()).encode("utf-8"),
                authorization=request.headers.get("authorization"),
                read_key=str(getattr(self.env, SIGNALS_READ_KEY_VAR, "") or "") or None,
                kv=_access_store(self.env),
            )
        elif path == "/v1/signals/pending":
            if method != "GET":
                return self._method_not_allowed(service_commit, path, "GET", method)
            outcome = await signals_service.pending(
                authorization=request.headers.get("authorization"),
                read_key=str(getattr(self.env, SIGNALS_READ_KEY_VAR, "") or "") or None,
                kv=_access_store(self.env),
                today=datetime.now(UTC).date(),
            )
        elif path == "/v1/signals/ack":
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            try:
                payload = json.loads(await request.text())
            except ValueError as exc:
                outcome = signals_service._error(
                    400, "invalid_request", f"the body is not valid JSON: {exc}"
                )
            else:
                outcome = await signals_service.acknowledge(
                    authorization=request.headers.get("authorization"),
                    read_key=str(getattr(self.env, SIGNALS_READ_KEY_VAR, "") or "") or None,
                    kv=_access_store(self.env),
                    payload=payload,
                    today=datetime.now(UTC).date(),
                )
        else:
            outcome = signals_service._error(404, "not_found", f"no endpoint at {path}")
        outcome.body["service_commit"] = service_commit
        return _json_response(outcome.status, outcome.body)

    async def _human_status(self, request, method):
        cors = _cors_headers(request, self.env)
        if not cors:
            return _json_response(403, {"enabled": human_gate.enabled(self.env)})
        if method == "OPTIONS":
            return Response("", status=204, headers={**cors, "access-control-allow-methods": "GET, OPTIONS"})
        if method != "GET":
            return _json_response(405, {"error": "method_not_allowed"}, cors)
        if visit_token.enabled(self.env):
            try:
                day, burst = visit_token.limits(self.env, "decide")
                return _json_response(200, {"enabled": True, "mode": "visit", "day_limit": day, "burst_limit": burst}, cors)
            except Exception:
                return _json_response(503, {"enabled": True, "message": "Human verification is temporarily unavailable."}, cors)
        if not human_gate.enabled(self.env):
            return _json_response(200, {"enabled": False}, cors)
        try:
            stub = human_gate.stub_for(request, self.env)
            if stub is None:
                raise RuntimeError(human_gate.unconfigured_reason(request, self.env))
            remaining = int(await stub.remaining())
            return _json_response(200, {"enabled": True, "remaining": remaining}, cors)
        except Exception as exc:
            human_gate.log_unavailable("status", exc)
            return _json_response(503, {"enabled": True, "message": human_gate.UNAVAILABLE}, cors)

    async def _feedback(self, request, method: str, service_commit: str):
        """`POST` and `DELETE /v1/feedback` (MODEL-221). No key is read."""
        extra = str(getattr(self.env, FEEDBACK_DEV_ORIGINS_VAR, "") or "")
        # Local development only: a value naming any other host is ignored,
        # so a stray production setting cannot open the endpoint to a site.
        allowed = CORS_ORIGINS | frozenset(
            o.strip() for o in extra.split(",")
            if re.fullmatch(r"http://(localhost|127\.0\.0\.1)(:\d+)?", o.strip()))
        origin = str(request.headers.get("origin") or "") or None
        cors = {}
        if origin in allowed:
            cors = {
                "access-control-allow-origin": origin,
                "access-control-allow-methods": "POST, DELETE, OPTIONS",
                "access-control-allow-headers": "content-type",
                "access-control-max-age": "86400",
                "vary": "Origin",
            }
        if method == "OPTIONS":
            return Response("", status=204 if cors else 403, headers=cors)
        if method not in ("POST", "DELETE"):
            return self._method_not_allowed(service_commit, "/v1/feedback", "POST or DELETE",
                                            method)
        binding = getattr(self.env, FEEDBACK_BINDING, None)
        store = feedback_service.Store(
            enabled=feedback_service.enabled(getattr(self.env, FEEDBACK_ENABLED_VAR, None)),
            kv=None if binding is None else access_kv.CloudflareKV(binding),
            pepper=str(getattr(self.env, FEEDBACK_PEPPER_VAR, "") or "").encode("utf-8"),
        )
        # Cloudflare sets CF-Connecting-IP on every request that reaches this
        # route and overwrites any the client sent. A request with none came
        # through a service binding: the MCP Worker, which forwards its own
        # caller's address in x-modelspec-client-ip so its callers are limited
        # one by one rather than as a crowd. Either way the address is only an
        # HMAC input; it is never stored or logged.
        address = str(request.headers.get("CF-Connecting-IP")
                      or request.headers.get("x-modelspec-client-ip") or "")
        handler = feedback_service.submit if method == "POST" else feedback_service.withdraw
        outcome = await handler(
            raw=(await request.text()).encode("utf-8"),
            address=address,
            origin=origin,
            allowed_origins=allowed,
            store=store,
        )
        outcome.body["service_commit"] = service_commit
        return _json_response(outcome.status, outcome.body, {**outcome.headers, **cors})

    def _x402_wrap(self, produce, request, path, api_key, envelope, payload, trace, *,
                   keyed: bool, produce_unfunded=None):
        """MODEL-75/93 hook. `keyed` uses the presented API key as the credit holder."""
        units, expiry_days, buy = self._credit_params(path, payload)

        async def wrapped(*args, **kwargs):
            cfg = x402.load_config(self.env)
            holder = x402.holder_from_key(api_key) if keyed else None
            unfunded = None
            if produce_unfunded is not None:
                unfunded = lambda: produce_unfunded(*args, **kwargs)
            return await x402.charge(
                config=cfg,
                ledger=credits.ledger_from_env(self.env),
                facilitator=x402.facilitator_from_env(self.env, cfg),
                get_header=lambda name: request.headers.get(name),
                holder=holder,
                resource_url=x402.resource_url(str(request.url), path, envelope.get(
                    "export_origin") or "https://api.modelspec.dev"),
                envelope=envelope,
                produce=lambda: produce(*args, **kwargs),
                produce_unfunded=unfunded,
                units=units,
                pack_expiry_days=expiry_days,
                buy_url=buy,
                trace=trace,
            )

        return wrapped

    async def _credits(self, request, service_commit: str, origin: str):
        """`GET /v1/credits` — the holder's prepaid balance."""
        envelope = service._envelope({}, service_commit, origin)
        envelope["endpoint"] = "credits"
        status, body = await x402.balance_query(
            config=x402.load_config(self.env),
            ledger=credits.ledger_from_env(self.env),
            api_key=access_keys.extract(lambda name: request.headers.get(name)),
            envelope=envelope,
        )
        return _json_response(status, body)

    async def _billing(self, request, path: str, method: str, service_commit: str):
        """MODEL-73: Checkout, webhook, claim, rotate. Routing only.

        `BILLING_ENABLED` gates Checkout alone (no new purchase can start).
        The webhook, claim and rotate serve purchases already paid for, so
        they answer with the flag off too (2026-09-24, holding mode).
        """
        if path not in ("/v1/billing/stripe-webhook", "/v1/billing/checkout",
                        "/v1/billing/claim", "/v1/billing/rotate"):
            return _json_response(service.HTTP_NOT_FOUND, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "not_found", "message": f"no endpoint at {path}",
                          "accepted": _accepted_endpoints(self.env)},
                "result": [],
            })

        flag = billing.enabled(getattr(self.env, BILLING_ENABLED_VAR, None))
        kv = _access_store(self.env)
        origin = (f"{urlparse(str(request.url)).scheme}://"
                  f"{urlparse(str(request.url)).netloc}")
        now = datetime.now(UTC)
        header = request.headers.get
        try:
            policy = access_config.load_policy(self.env)
        except access_config.PolicyError:
            policy = None

        if path == "/v1/billing/stripe-webhook":
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            if policy is None:
                return _json_response(*_billing_unconfigured(service_commit))
            raw = await request.text()
            outcome = await billing.webhook(
                payload=raw,
                signature=header("stripe-signature") or header("Stripe-Signature"),
                secret=str(getattr(self.env, STRIPE_WEBHOOK_SECRET_VAR, "") or "") or None,
                kv=kv, policy=policy, now=now,
                service_commit=service_commit,
                ledger=credits.ledger_from_env(self.env))
            return _json_response(outcome.status, outcome.body, outcome.headers)

        if path == "/v1/billing/claim":
            if method not in ("GET", "POST"):
                return self._method_not_allowed(service_commit, path, "GET or POST", method)
            if policy is None:
                return _json_response(*_billing_unconfigured(service_commit))
            raw = await request.text() if method == "POST" else ""
            payload = None
            if raw.strip():
                try:
                    payload = json.loads(raw)
                except ValueError as exc:
                    bad = billing._refusal(
                        billing.INVALID_REQUEST, f"the body is not valid JSON: {exc}",
                        service_commit=service_commit, endpoint="billing.claim")
                    return _json_response(bad.status, bad.body, bad.headers)
            session_id = billing.session_id_from_request(
                query=billing.query_string(str(request.url)), payload=payload)
            outcome = await billing.claim(
                session_id=session_id, kv=kv, policy=policy, now=now,
                service_commit=service_commit,
                ledger=credits.ledger_from_env(self.env))
            if billing_page.prefers_html(header("accept")):
                # MODEL-105: Stripe's success redirect lands a person here.
                return _html_response(
                    outcome.status, billing_page.claim_page(outcome.status, outcome.body),
                    service_commit, outcome.headers)
            return _json_response(outcome.status, outcome.body, outcome.headers)

        if path == "/v1/billing/rotate":
            if method != "POST":
                return self._method_not_allowed(service_commit, path, "POST", method)
            if policy is None:
                return _json_response(*_billing_unconfigured(service_commit))
            outcome = await billing.rotate(
                api_key=access_keys.extract(lambda name: header(name)),
                kv=kv, policy=policy, now=now,
                service_commit=service_commit,
                ledger=credits.ledger_from_env(self.env))
            return _json_response(outcome.status, outcome.body, outcome.headers)

        if method != "POST":
            return self._method_not_allowed(service_commit, path, "POST", method)
        if policy is None:
            return _json_response(*_billing_unconfigured(service_commit))
        raw = await request.text()
        stripe_secret = str(getattr(self.env, STRIPE_SECRET_KEY_VAR, "") or "") or None
        if billing.is_form_post(header("content-type"), raw):
            # MODEL-105: the /pricing buy button. 303 to Stripe; anonymous.
            outcome = await billing.checkout_form(
                raw=raw, flag=flag, secret=stripe_secret, origin=origin, kv=kv,
                policy=policy, service_commit=service_commit, http=_stripe_http)
            return _json_response(outcome.status, outcome.body, outcome.headers)
        payload = None
        if raw.strip():
            try:
                payload = json.loads(raw)
            except ValueError as exc:
                bad = billing._refusal(
                    billing.INVALID_REQUEST, f"the body is not valid JSON: {exc}",
                    service_commit=service_commit, endpoint="billing.checkout")
                return _json_response(bad.status, bad.body, bad.headers)
        outcome = await billing.checkout(
            payload=payload, flag=flag,
            secret=str(getattr(self.env, STRIPE_SECRET_KEY_VAR, "") or "") or None,
            origin=origin, kv=kv, policy=policy, service_commit=service_commit,
            http=_stripe_http,
            api_key=access_keys.extract(lambda name: header(name)))
        return _json_response(outcome.status, outcome.body, outcome.headers)

    async def _rank(self, payload, service_commit: str, origin: str):
        """`POST /v1/rank` from the published export. `(status, body)`."""
        try:
            candidates, hardware = await _load_export(origin)
        except Exception as exc:  # noqa: BLE001 - reported, with the origin named
            return service.HTTP_BAD_GATEWAY, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "export_origin": origin,
                "error": {"code": "export_unavailable",
                          "message": f"could not read the published export: {exc}"},
                "result": [],
            }

        try:
            return service.rank(payload, candidates, hardware, service_commit, origin,
                                prepared_candidates=_cache["prepared"]
                                if _cache["candidates"] is candidates else None)
        except service.RequestError as exc:
            return service.error_response(exc, candidates, service_commit, origin)

    async def _decide(self, payload, origin: str, expected: str | None = None,
                      transport: _DecisionTransport | None = None):
        """``POST /v1/decide`` against the isolate's verified snapshot.

        ``expected`` is the snapshot the caller's vocabulary names. When this
        isolate holds another, it revalidates at once: the site may have just
        deployed it. Still different, the caller gets ``snapshot_changed``.
        """
        decider = _decide_service()
        key = str(getattr(self.env, SNAPSHOT_KEY_VAR, "") or "") or None
        if key is None:
            return decider.no_snapshot(
                "no signed decision snapshot is published because the verification key "
                "is not configured"
            )
        holder = _decision_holder(origin)
        snapshot_timings = []
        try:
            snapshot = await holder.current(key, timings=snapshot_timings)
            if expected and expected != snapshot.snapshot_id:
                snapshot = await holder.current(key, force=True, timings=snapshot_timings)
        except decider.SnapshotMissingError:
            return decider.no_snapshot("the published decision snapshot does not exist")
        except decider.SnapshotRefusalError as exc:
            return decider.error_response(
                "snapshot_refused",
                str(exc),
                status=decider.HTTP_SERVICE_UNAVAILABLE,
                snapshot_id=None,
            )
        except Exception as exc:  # noqa: BLE001 - the fetched path is named to the caller
            return decider.error_response(
                "snapshot_unavailable",
                f"could not read the published decision snapshot: {exc}",
                status=decider.HTTP_BAD_GATEWAY,
                snapshot_id=None,
            )
        status, body = decider.decide(payload, snapshot, expected_snapshot=expected)
        if status == decider.HTTP_OK and transport is not None:
            transport.body = body
            transport.serialised = decider.serialise(body)
            # Workers freeze the clock during synchronous work (it moves only at
            # I/O), so the decision itself always measured 0.0 ms in production.
            # Only snapshot work, which waits on a fetch, has a real duration.
            if snapshot_timings:
                transport.headers["Server-Timing"] = f"snapshot;dur={sum(snapshot_timings):.1f}"
        return status, body

    async def _compare(self, payload, origin: str, expected: str | None = None):
        """``POST /v1/compare`` against the current and one named snapshot."""
        decider = _decide_service()
        key = str(getattr(self.env, SNAPSHOT_KEY_VAR, "") or "") or None
        if key is None:
            return decider.no_snapshot(
                "no signed decision snapshot is published because the verification key "
                "is not configured",
                endpoint="compare",
            )
        if not isinstance(payload, dict) or not isinstance(payload.get("compare_to"), str):
            return decider.error_response(
                "invalid_request",
                "the request body must contain a spec object and compare_to snapshot ID",
                status=decider.HTTP_BAD_REQUEST,
                snapshot_id=None,
                endpoint="compare",
            )
        compare_to = payload["compare_to"]
        if re.fullmatch(decider.contract.SNAPSHOT_PATTERN, compare_to) is None:
            return decider.error_response(
                "invalid_request",
                "compare_to must be a snapshot ID",
                status=decider.HTTP_BAD_REQUEST,
                snapshot_id=None,
                endpoint="compare",
            )
        try:
            current = await _decision_holder(origin).current(key)
            if expected and expected != current.snapshot_id:
                current = await _decision_holder(origin).current(key, force=True)
            fetched = await _snapshot_fetcher(
                origin + DECISION_HISTORY_TEMPLATE.format(snapshot_id=compare_to)
            )(None)
            if fetched.status == 404:
                return decider.error_response(
                    "comparison_snapshot_unavailable",
                    f"the origin does not publish retained decision snapshot {compare_to}",
                    status=decider.HTTP_CONFLICT,
                    snapshot_id=current.snapshot_id,
                    endpoint="compare",
                )
            if fetched.status != 200 or fetched.body is None:
                raise RuntimeError(f"comparison snapshot returned HTTP {fetched.status}")
            previous = decider.load_snapshot(fetched.body, key=key)
        except decider.SnapshotMissingError:
            return decider.no_snapshot(
                "the published decision snapshot does not exist", endpoint="compare"
            )
        except decider.SnapshotRefusalError as exc:
            return decider.error_response(
                "snapshot_refused", str(exc), status=decider.HTTP_SERVICE_UNAVAILABLE,
                snapshot_id=None, endpoint="compare",
            )
        except Exception as exc:  # noqa: BLE001 - the failed origin read is returned
            return decider.error_response(
                "snapshot_unavailable",
                f"could not read the published decision snapshots: {exc}",
                status=decider.HTTP_BAD_GATEWAY,
                snapshot_id=None,
                endpoint="compare",
            )
        return decider.compare(
            payload, previous, current, expected_snapshot=expected
        )

    def _method_not_allowed(self, service_commit: str, path: str,
                            takes: str, method: str) -> Response:
        """One 405, so every endpoint refuses a verb the same way.

        `/v1/health` used to answer any method, including PUT and DELETE. It
        never mattered while the route stopped everything outside `/v1/*` at a
        522; with the whole host routed here it is the Worker's own answer.
        """
        return _json_response(service.HTTP_METHOD_NOT_ALLOWED, {
            "schema_version": service.SCHEMA_VERSION,
            "service_commit": service_commit,
            "error": {"code": "method_not_allowed",
                      "message": f"{path} takes {takes}, not {method}"},
            "result": [],
        })

    async def _policy_check(self, payload, service_commit: str, origin: str,
                            entitlement: str = policy_service.ENTITLEMENT_PUBLIC) -> Response:
        """`_policy_answer` as a response, for callers that hold an entitlement."""
        return _json_response(*await self._policy_answer(payload, service_commit, origin,
                                                         entitlement))

    async def _policy_answer(self, payload, service_commit: str, origin: str,
                             entitlement: str):
        """`POST /v1/policy-check` (MODEL-80). `(status, body)`.

        The entitlement arrives decided — by `_entitlement`, from the tier the
        access gate resolved — and the store is read only when the request is
        entitled to it, so the free path never touches KV. When an entitled
        request cannot read the store, `policy_service.check` refuses with 503
        rather than answering from the public export alone — a paid caller
        cannot tell that answer from a real one.
        """
        try:
            catalogue = await _load_policy_catalogue(origin)
        except Exception as exc:  # noqa: BLE001 - reported, with the origin named
            return service.HTTP_BAD_GATEWAY, {
                "schema_version": policy_service.SCHEMA_VERSION,
                "endpoint": "policy-check",
                "service_commit": service_commit,
                "export_origin": origin,
                "error": {"code": "export_unavailable",
                          "message": f"could not read the policy export: {exc}"},
                "result": [],
            }

        store = None
        if entitlement == policy_service.ENTITLEMENT_DETERMINATIONS:
            store = await _load_determinations(self.env)

        try:
            status, body = policy_service.check(payload, catalogue, store, entitlement,
                                                service_commit, origin)
        except policy_service.RequestError as exc:
            if exc.code == "determinations_unavailable":
                # Why, in the store's own terms: unbound, empty or broken.
                # `last_error` is null unless it is broken.
                exc.detail.setdefault("store_state", _store_cache.get("state"))
                exc.detail.setdefault("store_message", _store_cache.get("message"))
                exc.detail.setdefault("last_error", _store_cache.get("error"))
            status, body = policy_service.error_response(exc, catalogue, service_commit,
                                                         origin)
        return status, body

    async def _health(self, service_commit: str, origin: str) -> Response:
        """What version is running, and can it read the catalogue.

        `service_commit` is fixed for the deployed script, so a stale answer
        cannot masquerade as a fresh one. The deploy smoke test polls this until
        it matches the sha it pushed, and fails loudly if it never does.
        """
        loaded, build, model_count, error = False, {}, 0, None
        try:
            candidates, _ = await _load_export(origin)
            loaded = True
            build = candidates.get("build") or {}
            model_count = len(candidates.get("candidates") or [])
        except Exception as exc:  # noqa: BLE001 - the diagnosis is the point
            error = f"{type(exc).__name__}: {exc}"

        policy_loaded, policy_count = False, 0
        try:
            catalogue = await _load_policy_catalogue(origin)
            policy_loaded = True
            policy_count = len(catalogue.get("models") or [])
        except Exception as exc:  # noqa: BLE001 - reported, not hidden
            error = error or f"{type(exc).__name__}: {exc}"

        status = service.HTTP_OK if loaded and policy_loaded else service.HTTP_BAD_GATEWAY
        return _json_response(status, {
            "schema_version": service.SCHEMA_VERSION,
            "endpoint": "health",
            "service_commit": service_commit,
            "export_origin": origin,
            "export_loaded": loaded,
            "policy_export_loaded": policy_loaded,
            "build": {"commit": build.get("commit"),
                      "built_at": build.get("built_at"),
                      "export_schema_version": build.get("export_schema_version")},
            "model_count": model_count,
            "policy_model_count": policy_count,
            # Whether a determination bundle is loadable, and which one — the
            # version and the day it was staged, so a KV load can be verified
            # from outside. Deliberately no counts and no content: this is a
            # public endpoint and the determinations are the product.
            "determinations": await self._determinations_health(),
            "last_error": error or _cache.get("error") or _policy_cache.get("error"),
        })

    async def _determinations_health(self) -> dict:
        """Is a bundle staged, and which one. Metadata only, never content.

        `state` is one of `unbound`, `empty`, `loaded`, `broken`. Only
        `broken` carries a `last_error`: an unbound or empty store is a normal
        condition, and reporting it as an exception would send an operator
        looking for corruption that is not there.
        """
        store = await _load_determinations(self.env)
        state = _store_cache.get("state")
        if store is None:
            return {"bound": state != STORE_UNBOUND, "state": state, "loaded": False,
                    "bundle_version": None, "generated_on": None,
                    "message": _store_cache.get("message"),
                    "last_error": _store_cache.get("error")}
        return {"bound": True, "state": STORE_LOADED, "loaded": True,
                "bundle_version": store.get("bundle_version"),
                "generated_on": store.get("generated_on"),
                "message": None, "last_error": None}
