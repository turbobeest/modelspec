"""The rank Worker's Cloudflare entry point (MODEL-68).

Deliberately thin. Everything that decides what the answer is lives in
`rank_service.py`, which imports nothing from the Workers runtime and is
therefore exercised directly by `tests/test_rank_worker.py` under CPython. What
is left here is transport: route, read the body, fetch the published export,
serialise, and report the deployed version.

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

import rank_service as service

#: Files the endpoint reads. `candidates.json` is the catalogue; `hardware.json`
#: is the device vocabulary, added by MODEL-68 and absent from older exports —
#: its loss degrades `environment.hardware` to "refused", never to a wrong
#: answer.
CANDIDATES_PATH = "/api/rank/candidates.json"
HARDWARE_PATH = "/api/rank/hardware.json"

#: How long a fetched export is reused inside one isolate. Short enough that a
#: site deploy reaches callers quickly, long enough that a burst of requests
#: does not re-fetch 2 MB each time.
EXPORT_TTL_SECONDS = 300

#: Module-scope, so it survives across requests within an isolate and is
#: rebuilt by the memory snapshot on a cold start.
_cache: dict[str, object] = {"at": 0.0, "candidates": None, "hardware": None, "error": None}


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
            return await self._health(service_commit, origin)
        if path != "/v1/rank":
            return _json_response(service.HTTP_NOT_FOUND, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "not_found", "message": f"no endpoint at {path}",
                          "accepted": ["POST /v1/rank", "GET /v1/health"]},
                "result": [],
            })
        if method != "POST":
            return _json_response(service.HTTP_METHOD_NOT_ALLOWED, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "method_not_allowed",
                          "message": f"/v1/rank takes POST, not {method}"},
                "result": [],
            })

        raw = await request.text()
        if len(raw.encode("utf-8")) > service.MAX_BODY_BYTES:
            return _json_response(service.HTTP_PAYLOAD_TOO_LARGE, {
                "schema_version": service.SCHEMA_VERSION,
                "service_commit": service_commit,
                "error": {"code": "payload_too_large",
                          "message": f"the body must be at most {service.MAX_BODY_BYTES} bytes"},
                "result": [],
            })

        try:
            payload = json.loads(raw) if raw.strip() else None
        except ValueError as exc:
            status, body = service.error_response(
                service.RequestError("invalid_request", f"the body is not valid JSON: {exc}"),
                None, service_commit, origin)
            return _json_response(status, body)

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

        status = service.HTTP_OK if loaded else service.HTTP_BAD_GATEWAY
        return _json_response(status, {
            "schema_version": service.SCHEMA_VERSION,
            "endpoint": "health",
            "service_commit": service_commit,
            "export_origin": origin,
            "export_loaded": loaded,
            "build": {"commit": build.get("commit"),
                      "built_at": build.get("built_at"),
                      "export_schema_version": build.get("export_schema_version")},
            "model_count": model_count,
            "last_error": error or _cache.get("error"),
        })
