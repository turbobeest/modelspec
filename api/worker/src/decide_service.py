"""Run the shared decision engine for ``POST /v1/decide`` (MODEL-151)."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import replace
from typing import Any, NamedTuple, Protocol

from decision import contract
from decision.engine import decide as run_decision
from decision.registry import facet
from decision.snapshot import SnapshotIntegrityError, load_snapshot_bytes

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
MAX_BODY_BYTES = 64 * 1024
RETRY_AFTER_SECONDS = 300
#: How often an isolate asks the static origin whether the snapshot changed
#: (MODEL-159). A site deploy reaches every warm isolate within this interval.
REVALIDATE_SECONDS = 60
#: A request naming a snapshot the isolate does not hold revalidates at once,
#: but not more often than this, so a wrong header cannot make every request
#: a subrequest.
FORCED_REVALIDATE_SECONDS = 5
#: The request header carrying the snapshot the caller's vocabulary describes,
#: and the response header naming the snapshot that answered.
SNAPSHOT_HEADER = "x-modelspec-snapshot"
#: Present only when the latest refresh failed and an older verified snapshot answered.
STALE_HEADER = "x-modelspec-snapshot-stale"
_STALE_HEADER_MAX = 200
#: A request that finds a load in progress waits for it rather than starting
#: its own (MODEL-153), but not past this: a load older than this is presumed
#: dead, and the next request starts another.
LOAD_WAIT_SECONDS = 20
#: How often a waiting request looks at the load it is waiting on.
LOAD_POLL_SECONDS = 0.025


class SnapshotRefusalError(ValueError):
    """The published snapshot cannot be trusted and must not answer a request."""


class SnapshotMissingError(RuntimeError):
    """The static site has not published a decision snapshot yet."""


def load_snapshot(data: bytes, *, key: bytes | str | None):
    """Load a signed snapshot and require signature verification."""
    if key is None or key == "" or key == b"":
        raise SnapshotRefusalError("the decision snapshot verification key is not configured")
    try:
        snapshot = load_snapshot_bytes(
            data,
            key=key,
            include_archive=True,
            source="published decision snapshot",
        )
    except SnapshotIntegrityError as exc:
        raise SnapshotRefusalError(str(exc)) from None
    if not snapshot.signature_verified:
        raise SnapshotRefusalError("the published decision snapshot signature was not verified")
    return snapshot


class Fetched(Protocol):
    """One conditional GET of the snapshot: ``body`` is ``None`` unless ``status`` is 200."""

    status: int
    etag: str | None
    body: bytes | None


#: Fetch the published snapshot, sending ``If-None-Match`` when given an ETag.
FetchSnapshot = Callable[[str | None], Awaitable[Fetched]]


class _Held(NamedTuple):
    snapshot: Any
    etag: str | None
    digest: str


def _header_value(message: str) -> str:
    flat = " ".join(message.split()).encode("ascii", "replace").decode("ascii")
    return flat[:_STALE_HEADER_MAX]


class _Load:
    """One fetch-and-verify in progress. Other requests read its outcome, never its I/O."""

    def __init__(self, started: float):
        self.started = started
        self.done = False
        self.snapshot: Any = None
        self.error: BaseException | None = None


class SnapshotHolder:
    """The isolate's verified snapshot, revalidated at most once per interval.

    A changed snapshot replaces the held one only after its signature verifies,
    in one assignment. A refresh that fails for any reason keeps the verified
    snapshot and records why, for ``headers()``. With nothing held, a failure
    is raised; a refusal is remembered for the interval so an unsigned build
    is not re-downloaded on every request.

    One load at a time (MODEL-153). While a load runs, a request that can
    answer from the held snapshot does; one that cannot (a cold isolate, or a
    caller whose vocabulary names another snapshot) waits for that load and
    shares its outcome, success or failure. The page's first burst used to
    make a cold isolate fetch, verify and parse one copy per request.

    Waiters poll rather than await a future the loading request resolves: on
    Workers, resuming one request from another request's I/O is not safe.
    """

    def __init__(self, fetch: FetchSnapshot, *, clock: Callable[[], float] = time.monotonic,
                 interval: float = REVALIDATE_SECONDS,
                 forced_interval: float = FORCED_REVALIDATE_SECONDS,
                 sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep):
        self._fetch = fetch
        self._clock = clock
        self._sleep = sleep
        self._interval = interval
        self._forced_interval = forced_interval
        self._held: _Held | None = None
        self._checked_at: float | None = None
        self._refusal: SnapshotRefusalError | None = None
        self._stale: str | None = None
        self._load: _Load | None = None

    @property
    def snapshot(self):
        return self._held.snapshot if self._held is not None else None

    def headers(self) -> dict[str, str]:
        if self._held is None:
            return {}
        headers = {SNAPSHOT_HEADER: self._held.snapshot.snapshot_id}
        if self._stale is not None:
            headers[STALE_HEADER] = self._stale
        return headers

    def _due(self, force: bool) -> bool:
        if self._checked_at is None:
            return True
        age = self._clock() - self._checked_at
        return age >= (self._forced_interval if force else self._interval)

    def _live(self, load: _Load | None) -> bool:
        return load is not None and self._clock() - load.started < LOAD_WAIT_SECONDS

    async def current(self, key: bytes | str | None, *, force: bool = False):
        """The snapshot to answer from, revalidating first when it is due."""
        load = self._load
        if self._live(load):
            if self._held is not None and not force:
                return self._held.snapshot
            return await self._wait(load, key, force)
        if not self._due(force):
            if self._held is not None:
                return self._held.snapshot
            if self._refusal is not None:
                raise self._refusal
        return await self._revalidate(key)

    async def _wait(self, load: _Load, key, force: bool):
        while not load.done:
            if not self._live(load):
                # Presumed dead: join whichever request replaces it, or replace it.
                return await self.current(key, force=force)
            await self._sleep(LOAD_POLL_SECONDS)
        if load.error is None:
            return load.snapshot
        if isinstance(load.error, Exception):
            raise load.error
        # The loading request was cancelled before it finished: load here instead.
        return await self.current(key, force=force)

    async def _revalidate(self, key):
        load = _Load(self._clock())
        self._load = load
        # Stamped before the await: concurrent requests in this isolate keep
        # serving the held snapshot, or wait on this load, instead of fetching.
        self._checked_at = load.started
        try:
            load.snapshot = await self._refresh(key)
        except BaseException as exc:  # noqa: BLE001 - recorded for waiters, then re-raised
            load.error = exc
            raise
        finally:
            load.done = True
            if self._load is load:
                self._load = None
        return load.snapshot

    async def _refresh(self, key):
        held = self._held
        try:
            fetched = await self._fetch(held.etag if held is not None else None)
            snapshot = self._accept(fetched, held, key)
        except Exception as exc:  # noqa: BLE001 - kept as the stale reason, or raised
            if held is None:
                if isinstance(exc, SnapshotRefusalError):
                    self._refusal = exc
                else:
                    self._checked_at = None
                raise
            self._stale = _header_value(f"refresh failed, serving the verified "
                                        f"{held.snapshot.snapshot_id}: {exc}")
            return held.snapshot
        self._refusal = None
        self._stale = None
        return snapshot

    def _accept(self, fetched: Fetched, held: _Held | None, key):
        if fetched.status == 304 and held is not None:
            return held.snapshot
        if fetched.status == 404:
            raise SnapshotMissingError("the published decision snapshot returned HTTP 404")
        if fetched.status != 200 or fetched.body is None:
            raise RuntimeError(f"the published decision snapshot returned HTTP {fetched.status}")
        digest = hashlib.sha256(fetched.body).hexdigest()
        if held is not None and digest == held.digest:
            self._held = _Held(held.snapshot, fetched.etag, digest)
            return held.snapshot
        snapshot = load_snapshot(fetched.body, key=key)
        self._held = _Held(snapshot, fetched.etag, digest)
        return snapshot


def _issues(exc: contract.SpecError) -> list[dict[str, Any]]:
    return [
        {
            "path": issue.path,
            "condition": issue.condition,
            "field": issue.field,
            "reason": issue.reason,
        }
        for issue in exc.issues
    ]


def _facets(snapshot):
    benchmark_ids = frozenset(snapshot.benchmark_ids())

    def lookup(facet_id: str):
        if facet_id in benchmark_ids:
            return replace(facet("evidence.benchmark"), id=facet_id)
        return facet(facet_id)

    return lookup


def error_response(
    code: str,
    message: str,
    *,
    status: int,
    snapshot_id: str | None,
    issues: list[dict[str, Any]] | None = None,
) -> tuple[int, dict[str, Any]]:
    error: dict[str, Any] = {"code": code, "message": message}
    if issues is not None:
        error["issues"] = issues
    return status, {
        "contract_version": contract.CONTRACT_VERSION,
        "endpoint": "decide",
        "snapshot": snapshot_id,
        "error": error,
    }


def no_snapshot(message: str) -> tuple[int, dict[str, Any]]:
    """Return the temporary state used until Pages publishes a signed snapshot."""
    return HTTP_SERVICE_UNAVAILABLE, {
        "contract_version": contract.CONTRACT_VERSION,
        "endpoint": "decide",
        "snapshot": None,
        "error": "no_snapshot",
        "message": message,
    }


def snapshot_changed(requested: str, snapshot) -> tuple[int, dict[str, Any]]:
    """The caller's vocabulary describes another snapshot: reload it and ask again."""
    status, body = error_response(
        "snapshot_changed",
        f"the request was built for {requested}, but the Worker answers from "
        f"{snapshot.snapshot_id}; reload the vocabulary and retry",
        status=HTTP_CONFLICT,
        snapshot_id=snapshot.snapshot_id,
    )
    body["error"]["requested"] = requested
    body["error"]["current"] = snapshot.snapshot_id
    return status, body


def decide(payload: Any, snapshot, *,
           expected_snapshot: str | None = None) -> tuple[int, dict[str, Any]]:
    """Validate one contract-v1 spec and return the shared engine's Decision.

    ``expected_snapshot`` is the ``X-ModelSpec-Snapshot`` request header. It is
    checked before the spec, because a spec built from an older vocabulary may
    name a benchmark this snapshot does not know.
    """
    if expected_snapshot and expected_snapshot != snapshot.snapshot_id:
        return snapshot_changed(expected_snapshot, snapshot)
    facets = _facets(snapshot)
    try:
        spec = contract.parse_spec(payload, facets=facets)
    except contract.SpecError as exc:
        return error_response(
            "invalid_spec",
            "the request body is not a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            issues=_issues(exc),
        )
    if spec.snapshot not in ("latest", snapshot.snapshot_id):
        return error_response(
            "snapshot_not_loaded",
            f"the Worker loaded {snapshot.snapshot_id}, not {spec.snapshot}",
            status=HTTP_CONFLICT,
            snapshot_id=snapshot.snapshot_id,
        )
    decision = run_decision(spec, snapshot, facets=facets)
    return HTTP_OK, decision.model_dump(mode="json")


def serialise(body: dict[str, Any]) -> bytes:
    """Byte for byte what ``modelspec decide --json`` prints: compact, UTF-8.

    Compact because a ``full`` decision runs to hundreds of kilobytes, a third
    of it indentation when pretty-printed (MODEL-163).
    """
    return (json.dumps(body, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
