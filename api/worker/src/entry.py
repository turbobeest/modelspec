"""The Worker's Cloudflare entry point (MODEL-68, MODEL-80).

Deliberately thin. Everything that decides what the answer is lives in
`rank_service.py` and `policy_service.py`, which import nothing from the
Workers runtime and are therefore exercised directly by
`tests/test_rank_worker.py` and `tests/test_policy_check.py` under CPython.
What is left here is transport: route, read the body, fetch the published
export, read the determination store, serialise, and report the deployed
version.

Two endpoints, and they differ in one way that matters. `POST /v1/rank` holds
no private data at all. `POST /v1/policy-check` (MODEL-80) answers from the
public export *plus*, for an entitled caller, the policy determinations — which
are the paid product, are never in this repository, and reach the Worker only
through Workers KV, staged by `api/worker/load_determinations.py`. See
`docs/policy-check-api.md` for the trust boundary. `_entitlement()` below is the
one place a request is granted the private store, and it is the seam MODEL-69
fills.

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

import json
import time
from urllib.parse import urlparse

from js import fetch
from workers import Response, WorkerEntrypoint

import hashlib

import policy_service
import rank_service as service

#: Files the endpoint reads. `candidates.json` is the catalogue; `hardware.json`
#: is the device vocabulary, added by MODEL-68 and absent from older exports —
#: its loss degrades `environment.hardware` to "refused", never to a wrong
#: answer.
CANDIDATES_PATH = "/api/rank/candidates.json"
HARDWARE_PATH = "/api/rank/hardware.json"
#: The public half of the compliance answer (MODEL-80): licence, origin,
#: commercial-use grant and per-platform availability for every card.
POLICY_PATH = "/api/policy/catalogue.json"

#: KV keys holding the private determinations, staged by
#: `api/worker/load_determinations.py`. The manifest is read first and verified
#: against the blobs, so a half-finished load is never served.
KV_MANIFEST = "determinations/manifest"
KV_COMMERCIAL_USE = "determinations/commercial_use"
KV_RESIDENCY = "determinations/residency"

#: Everything this Worker serves. Named back to the caller by every 404, so an
#: unrouted path — the bare root included — is a usable answer rather than a
#: dead end. `.github/scripts/check_rank_response.py` asserts every one of them
#: is named. `/v1/policy-check` (MODEL-80) is on this list for the same reason
#: `/v1/rank` is: a caller who mistypes it must be told it exists.
ACCEPTED_ENDPOINTS = ("POST /v1/rank", "POST /v1/policy-check", "GET /v1/health")

#: The subset that takes a body. Both refuse a wrong verb through the one
#: `_method_not_allowed` below, and a path outside this tuple is a 404 before
#: anything is read or fetched.
POST_ENDPOINTS = ("/v1/rank", "/v1/policy-check")

#: How long a fetched export is reused inside one isolate. Short enough that a
#: site deploy reaches callers quickly, long enough that a burst of requests
#: does not re-fetch 2 MB each time.
EXPORT_TTL_SECONDS = 300

#: Module-scope, so it survives across requests within an isolate and is
#: rebuilt by the memory snapshot on a cold start.
_cache: dict[str, object] = {"at": 0.0, "candidates": None, "hardware": None, "error": None}

#: The policy export and the determination store, cached on the same terms. The
#: determinations change when someone runs the loader, which is rare; the TTL
#: is the same one so that a deploy and a load both reach callers in five
#: minutes rather than by two different rules.
_policy_cache: dict[str, object] = {"at": 0.0, "catalogue": None, "error": None}
#: `state` is one of the `STORE_*` values below; `error` is set only when it is
#: `broken`; `message` is the operator-facing sentence for whichever it is.
_store_cache: dict[str, object] = {"at": 0.0, "store": None, "error": None,
                                   "state": None, "message": None}


async def _get_json(url: str):
    response = await fetch(url)
    if not response.ok:
        raise RuntimeError(f"{url} returned HTTP {response.status}")
    return json.loads(await response.text())


async def _load_export(origin: str, *, force: bool = False):
    """Fetch the export, or reuse the copy this isolate already has.

    A failed refresh does not discard a good copy: an export that still answers
    beats an error, which is the same call the CLI makes about a stale snapshot.
    """
    fresh = (time.time() - float(_cache["at"])) < EXPORT_TTL_SECONDS
    if not force and fresh and _cache["candidates"] is not None:
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

try:  # Pyodide's JS `null`. Absent under CPython, where tests stub KV.
    from pyodide.ffi import jsnull as _JSNULL  # type: ignore[import-not-found]
except Exception:  # noqa: BLE001 - optional import; `_absent` also checks the type name
    _JSNULL = None


def _absent(value) -> bool:
    """Whether a `kv.get()` result means "no such key".

    Workers KV resolves a missing key to JS `null`. Pyodide converts JS `null`
    to `pyodide.ffi.jsnull`, **not** to `None` (only `undefined` becomes
    `None`), so an `is None` test lets it through, and `str()` of it is not
    JSON. That is the bug this guards: an empty namespace was reported as
    `JSONDecodeError`, i.e. as corrupt data. An empty or blank string is
    treated as absent too — no loader writes one, and parsing it proves
    nothing but that it is empty.
    """
    if value is None:
        return True
    if _JSNULL is not None and value is _JSNULL:
        return True
    if type(value).__name__ in ("JsNull", "JsUndefined"):
        return True
    return isinstance(value, str) and not value.strip()


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


def _entitlement(request, env) -> str:
    """Which store this request may read. **The single seam MODEL-69 fills.**

    Nothing here authenticates anything, on purpose: keys, tiers and rate limits
    are MODEL-69's, and a second opinion about who a caller is would be a second
    place for them to disagree. Until that lands, every request is the free
    tier, which is a complete and honest answer — `determinations.included` says
    `false` on it and every check it could not settle says `available_in_tier:
    paid` — and not a degraded one.

    MODEL-69 replaces the body of this function with its own tier lookup and
    returns `policy_service.ENTITLEMENT_DETERMINATIONS` for a paid key. Nothing
    else in this file or in `policy_service.py` changes.
    """
    return policy_service.ENTITLEMENT_PUBLIC


def _json_response(status: int, body: dict) -> Response:
    return Response(
        json.dumps(body, indent=2, default=str),
        status=status,
        headers={
            "content-type": "application/json; charset=utf-8",
            # A ranking is computed per request from data that changes on every
            # site deploy. Caching it at the edge would hand callers an answer
            # whose `build.commit` no longer describes the catalogue.
            "cache-control": "no-store",
            "x-modelspec-service-commit": str(body.get("service_commit") or ""),
        },
    )


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        service_commit = str(getattr(self.env, "BUILD_COMMIT", "") or "unknown")
        origin = str(getattr(self.env, "EXPORT_ORIGIN", "") or "https://modelspec.dev")
        path = urlparse(str(request.url)).path.rstrip("/") or "/"
        method = str(request.method).upper()

        if path == "/v1/health":
            if method not in ("GET", "HEAD"):
                return self._method_not_allowed(service_commit, path, "GET", method)
            return await self._health(service_commit, origin)
        if path not in POST_ENDPOINTS:
            # Including the bare root: the route covers the whole host, so an
            # unknown path is answered here rather than left to Cloudflare's
            # 522, which reads like an outage. No export fetch — a crawler
            # asking for /favicon.ico must not cost a subrequest.
            return _json_response(service.HTTP_NOT_FOUND, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "not_found", "message": f"no endpoint at {path}",
                          "accepted": list(ACCEPTED_ENDPOINTS)},
                "result": [],
            })
        if method != "POST":
            return self._method_not_allowed(service_commit, path, "POST", method)

        max_body = (policy_service.MAX_BODY_BYTES if path == "/v1/policy-check"
                    else service.MAX_BODY_BYTES)
        raw = await request.text()
        if len(raw.encode("utf-8")) > max_body:
            return _json_response(service.HTTP_PAYLOAD_TOO_LARGE, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "payload_too_large",
                          "message": f"the body must be at most {max_body} bytes"},
                "result": [],
            })

        try:
            payload = json.loads(raw) if raw.strip() else None
        except ValueError as exc:
            if path == "/v1/policy-check":
                status, body = policy_service.error_response(
                    policy_service.RequestError(
                        "invalid_request", f"the body is not valid JSON: {exc}"),
                    None, service_commit, origin)
            else:
                status, body = service.error_response(
                    service.RequestError(
                        "invalid_request", f"the body is not valid JSON: {exc}"),
                    None, service_commit, origin)
            return _json_response(status, body)

        if path == "/v1/policy-check":
            return await self._policy_check(payload, service_commit, origin)

        try:
            candidates, hardware = await _load_export(origin)
        except Exception as exc:  # noqa: BLE001 - reported, with the origin named
            return _json_response(service.HTTP_BAD_GATEWAY, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "export_origin": origin,
                "error": {"code": "export_unavailable",
                          "message": f"could not read the published export: {exc}"},
                "result": [],
            })

        try:
            status, body = service.rank(payload, candidates, hardware, service_commit, origin)
        except service.RequestError as exc:
            status, body = service.error_response(exc, candidates, service_commit, origin)
        return _json_response(status, body)

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

    async def _policy_check(self, payload, service_commit: str, origin: str) -> Response:
        """`POST /v1/policy-check` (MODEL-80).

        The entitlement is decided first and the store is read only when the
        request is entitled to it, so the free path never touches KV. When an
        entitled request cannot read the store, `policy_service.check` refuses
        with 503 rather than answering from the public export alone — a paid
        caller cannot tell that answer from a real one.
        """
        try:
            catalogue = await _load_policy_catalogue(origin)
        except Exception as exc:  # noqa: BLE001 - reported, with the origin named
            return _json_response(service.HTTP_BAD_GATEWAY, {
                "schema_version": policy_service.SCHEMA_VERSION,
                "endpoint": "policy-check",
                "service_commit": service_commit,
                "export_origin": origin,
                "error": {"code": "export_unavailable",
                          "message": f"could not read the policy export: {exc}"},
                "result": [],
            })

        entitlement = _entitlement(None, self.env)
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
        return _json_response(status, body)

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
