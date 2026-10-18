"""Run the shared decision engine for ``POST /v1/decide`` (MODEL-151)."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import replace
from datetime import UTC, date, datetime
from typing import Any, NamedTuple, Protocol
from urllib.parse import urlencode

from pydantic import ValidationError

from decision import contract
from decision.bounded import project as project_decision
from decision.compare import compare as compare_decisions
from decision.coverage import for_spec as coverage_for_spec
from decision.engine import decide as run_decision
from decision.registry import facet
from decision.reading import for_refusal
from decision.recovery import recovery_hints
from decision.router_config import EmptyAllowListError
from decision.snapshot import (
    SnapshotError,
    SnapshotIntegrityError,
    load_snapshot_bytes,
    verify_hmac_signature,
)

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
#: Where an issue about a facet's value points the caller (MODEL-318).
VOCABULARY_LOOKUP = "https://api.modelspec.dev/v1/vocabulary"
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


class SnapshotValidityError(SnapshotRefusalError):
    """No held price period covers the current UTC date."""


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
                 sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep,
                 today: Callable[[], date] | None = None,
                 bundled_snapshot=None, bundled_successor=None,
                 load_successor: Callable[[bytes | str], Any] | None = None):
        self._fetch = fetch
        self._bundled_snapshot = bundled_snapshot
        self._bundled_successor = bundled_successor
        self._bundled = bundled_snapshot is not None
        self._load_successor = load_successor
        self._successor_loaded = False
        self._bundle_error: str | None = None
        self._bundle_verified = False
        self._clock = clock
        self._today = today or (lambda: datetime.now(UTC).date())
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

    def health(self) -> dict[str, Any]:
        """Public metadata after ``current()`` has selected and authenticated."""
        snapshot = self.snapshot
        if snapshot is not None:
            try:
                self._current_snapshot(snapshot)
            except SnapshotValidityError:
                snapshot = None
        successor = self._bundled_successor if self._bundle_verified else None
        return {
            "id": snapshot.snapshot_id if snapshot is not None else None,
            "valid_until": (snapshot.valid_until.isoformat()
                            if snapshot is not None and snapshot.valid_until is not None else None),
            "successor_held": successor is not None,
            "successor_valid_from": successor.get("valid_from") if successor is not None else None,
        }

    def _due(self, force: bool) -> bool:
        if self._checked_at is None:
            return True
        age = self._clock() - self._checked_at
        return age >= (self._forced_interval if force else self._interval)

    def _live(self, load: _Load | None) -> bool:
        return load is not None and self._clock() - load.started < LOAD_WAIT_SECONDS

    def _current_snapshot(self, snapshot):
        try:
            snapshot.require_current(self._today())
        except SnapshotError as exc:
            raise SnapshotValidityError(str(exc)) from None
        return snapshot

    async def current(self, key: bytes | str | None, *, force: bool = False,
                      timings: list[float] | None = None):
        """The snapshot to answer from, revalidating first when it is due."""
        if self._bundled:
            if not self._bundle_verified:
                if key is None or key == "" or key == b"":
                    raise SnapshotRefusalError(
                        "the decision snapshot verification key is not configured")
                try:
                    verify_hmac_signature(
                        self._bundled_snapshot.content_hash,
                        self._bundled_snapshot.publisher_signature,
                        key, source="bundled decision snapshot")
                    if self._bundled_successor is not None:
                        verify_hmac_signature(
                            self._bundled_successor["content_hash"],
                            self._bundled_successor["signature"],
                            key, source="bundled decision successor")
                except SnapshotIntegrityError as exc:
                    raise SnapshotRefusalError(str(exc)) from None
                self._bundled_snapshot.signature_verified = True
                self._bundled_snapshot.signature_status = "verified (hmac-sha256)"
                self._bundle_verified = True
            if self._bundle_error is not None:
                raise SnapshotRefusalError(self._bundle_error)
            today = self._today()
            try:
                self._bundled_snapshot.require_current(today)
            except SnapshotError as exc:
                unavailable = str(exc)
            else:
                self._held = _Held(self._bundled_snapshot, None, "")
                return self._bundled_snapshot
            self._held = None
            successor = self._bundled_successor
            if (successor is not None and not self._successor_loaded
                    and self._load_successor is not None
                    and successor.get("valid_from") is not None
                    and today >= date.fromisoformat(successor["valid_from"])):
                # The expired index must be collectible before parsing its replacement.
                self._bundled_snapshot = None
                try:
                    self._bundled_snapshot = self._load_successor(key)
                except Exception as exc:  # noqa: BLE001 - an immutable bundle cannot recover
                    self._bundle_error = str(exc)
                    raise SnapshotRefusalError(self._bundle_error) from None
                self._successor_loaded = True
                snapshot = self._current_snapshot(self._bundled_snapshot)
                self._held = _Held(snapshot, None, "")
                return snapshot
            raise SnapshotValidityError(unavailable)
        load = self._load
        if self._live(load):
            if self._held is not None and not force:
                return self._current_snapshot(self._held.snapshot)
            started = time.perf_counter()
            try:
                return self._current_snapshot(await self._wait(load, key, force))
            finally:
                if timings is not None:
                    timings.append((time.perf_counter() - started) * 1000)
        if not self._due(force):
            if self._held is not None:
                return self._current_snapshot(self._held.snapshot)
            if self._refusal is not None:
                raise self._refusal
        started = time.perf_counter()
        try:
            return self._current_snapshot(await self._revalidate(key))
        finally:
            if timings is not None:
                timings.append((time.perf_counter() - started) * 1000)

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


#: The vocabulary section that lists a member of a facet family.
_FAMILY_SECTIONS = {"benchmark": "benchmarks", "domain": "domains"}


def _vocabulary_section(facet_id: str) -> str:
    try:
        parameter = facet(facet_id).parameter
    except KeyError:  # a benchmark only the loaded snapshot names
        return "benchmarks"
    return "facets" if parameter is None else _FAMILY_SECTIONS.get(parameter.name, "facets")


def _issue(issue: contract.Issue) -> dict[str, Any]:
    row = issue.as_dict()
    if issue.value_type is not None:
        # A value outside the facet's vocabulary (MODEL-318) names the lookup that lists it.
        row["next"] = VOCABULARY_LOOKUP + "?" + urlencode(
            {"section": _vocabulary_section(issue.field), "id": issue.field})
    return row


def _issues(exc: contract.SpecError) -> list[dict[str, Any]]:
    return [_issue(issue) for issue in exc.issues]


def _facets(*snapshots):
    benchmark_ids = frozenset(
        benchmark_id for snapshot in snapshots for benchmark_id in snapshot.benchmark_ids()
    )

    def lookup(facet_id: str):
        if facet_id in benchmark_ids:
            return replace(facet("evidence.benchmark"), id=facet_id)
        return facet(facet_id)

    return lookup


def version_fields(endpoint: str) -> dict[str, str]:
    if endpoint == "compare-models":
        return {"comparison_version": contract.MODEL_COMPARISON_VERSION}
    return {"contract_version": contract.CONTRACT_VERSION}


def error_response(
    code: str,
    message: str,
    *,
    status: int,
    snapshot_id: str | None,
    issues: list[dict[str, Any]] | None = None,
    recovery: list[dict[str, Any]] | None = None,
    endpoint: str = "decide",
    reading: contract.Reading | None = None,
    coverage: contract.CoverageRefusal | None = None,
) -> tuple[int, dict[str, Any]]:
    error: dict[str, Any] = {"code": code, "message": message}
    if issues is not None:
        error["issues"] = issues
    if recovery is not None:
        error["recovery"] = recovery
        error["recovery_omitted"] = len(issues or []) - len(recovery)
    body = {
        **version_fields(endpoint),
        "endpoint": endpoint,
        "snapshot": snapshot_id,
        "error": error,
    }
    if reading is not None:
        body["reading"] = reading.model_dump(mode="json")
    if coverage is not None:
        body["coverage"] = coverage.model_dump(mode="json")
    return status, body


def bounded_unavailable(message: str, *, snapshot_id: str) -> tuple[int, dict[str, Any]]:
    """A refusal only a bounded drill-down can receive.

    It belongs to the bounded representation, not to the 2.x error enum: a
    caller that never sends ``evidence_for`` never sees it, so it carries the
    bounded identity instead of a 2.x ``contract_version``.
    """
    return HTTP_SERVICE_UNAVAILABLE, {
        "representation": "bounded",
        "bounded_version": contract.BOUNDED_VERSION,
        "projects_contract": contract.CONTRACT_VERSION,
        "endpoint": "decide",
        "snapshot": snapshot_id,
        "error": {"code": "explanation_unavailable", "message": message},
    }


def no_snapshot(message: str, *, endpoint: str = "decide") -> tuple[int, dict[str, Any]]:
    """Return the temporary state used until Pages publishes a signed snapshot."""
    return HTTP_SERVICE_UNAVAILABLE, {
        **version_fields(endpoint),
        "endpoint": endpoint,
        "snapshot": None,
        "error": "no_snapshot",
        "message": message,
    }


def snapshot_changed(
    requested: str, snapshot, *, endpoint: str = "decide"
) -> tuple[int, dict[str, Any]]:
    """The caller's vocabulary describes another snapshot: reload it and ask again."""
    status, body = error_response(
        "snapshot_changed",
        f"the request was built for {requested}, but the Worker answers from "
        f"{snapshot.snapshot_id}; reload the vocabulary and retry",
        status=HTTP_CONFLICT,
        snapshot_id=snapshot.snapshot_id,
        endpoint=endpoint,
    )
    body["error"]["requested"] = requested
    body["error"]["current"] = snapshot.snapshot_id
    return status, body


def decide(payload: Any, snapshot, *,
           expected_snapshot: str | None = None,
           profiles: Mapping[str, contract.InventoryProfile] | None = None,
           ) -> tuple[int, dict[str, Any]]:
    """Validate one decision spec and return the shared engine's Decision.

    ``expected_snapshot`` is the ``X-ModelSpec-Snapshot`` request header. It is
    checked before the spec, because a spec built from an older vocabulary may
    name a benchmark this snapshot does not know.

    ``profiles`` is the engine's map for a referenced profile id. It is not a
    request field. Without it, an unresolved profile is ``invalid_spec``.
    """
    if expected_snapshot and expected_snapshot != snapshot.snapshot_id:
        return snapshot_changed(expected_snapshot, snapshot)
    facets = _facets(snapshot)
    raw_spec = payload
    try:
        if isinstance(payload, dict):
            controls = {key: payload[key] for key in ("fields", "evidence_for", "router_config")
                        if key in payload}
            try:
                options = contract.ResponseOptions.model_validate(controls)
            except ValidationError as exc:
                raise contract.SpecError(contract._issues(exc)) from None
            raw_spec = {key: value for key, value in payload.items() if key not in controls}
        else:
            options = contract.ResponseOptions()
            raw_spec = payload
        spec = contract.parse_spec(raw_spec, facets=facets)
    except contract.SpecError as exc:
        # Structural validation can still identify a requested domain when its
        # ID is outside the registry. Keep the original invalid_spec refusal.
        try:
            coverage = coverage_for_spec(contract.parse_spec(raw_spec, facets=None), snapshot)
        except contract.SpecError:
            coverage = None
        return error_response(
            "invalid_spec",
            "the request body is not a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            issues=_issues(exc),
            recovery=recovery_hints(exc.issues, facets=facets,
                                    benchmark_ids=tuple(snapshot.benchmark_ids()), payload=payload),
            reading=for_refusal(exc.issues),
            coverage=coverage,
        )
    if spec.snapshot not in ("latest", snapshot.snapshot_id):
        return error_response(
            "snapshot_not_loaded",
            f"the Worker loaded {snapshot.snapshot_id}, not {spec.snapshot}",
            status=HTTP_CONFLICT,
            snapshot_id=snapshot.snapshot_id,
        )
    try:
        details = []
        if options.evidence_for is not None and not any(
            snapshot.model_of(cid) == options.evidence_for for cid in snapshot.candidates()
        ):
            raise contract.SpecError([contract.Issue(
                None, "evidence_for", "model is not in this snapshot's active lineup", "evidence_for")])
        if options.evidence_for is not None:
            # Drill-down cites records even at explain=none. A snapshot built
            # before provenance retention cannot; that is the server's state,
            # not a fault in the request.
            try:
                snapshot.require_explanation_records()
            except SnapshotError as exc:
                return bounded_unavailable(
                    f"evidence_for needs the snapshot's retained verification records: {exc}. "
                    "Retry without evidence_for, or later against a rebuilt snapshot",
                    snapshot_id=snapshot.snapshot_id,
                )
        # ``filtered.feasible`` is the candidate tuple ``run_optimise`` hands to
        # ``optimise``, after profile rules and ``where``. ``explain`` ``none``
        # leaves the funnel empty, so the summary cannot read the count there.
        surviving: list[int] = []

        def _trace(filtered) -> None:
            surviving.append(len(filtered.feasible))

        # Record counts for the estimate caveat on every bounded summary.
        # member_evidence itself is attached only for an explained answer.
        member_rows: list | None = None
        if options.fields is not None or options.router_config is not None:
            member_rows = []

            def _take_members(rows, sink=member_rows) -> None:
                sink.extend(rows)

        decision = run_decision(
            spec, snapshot, facets=facets, profiles=profiles,
            _filter_trace=_trace,
            _capture_evidence=None if options.evidence_for is None else (options.evidence_for, details.append),
            _capture_member_evidence=None if member_rows is None else _take_members,
        )
        if (options.fields is not None or options.evidence_for is not None
                or options.router_config is not None):
            return HTTP_OK, project_decision(
                decision, options, detail=details[0] if details else None,
                not_applied=sorted(set(spec.capabilities or {}) - set(snapshot.domain_ids())),
                spec=spec, profiles=profiles,
                feasible=surviving[-1] if surviving else None,
                member_evidence=member_rows,
            )
    except SnapshotError as exc:
        return no_snapshot(str(exc))
    except EmptyAllowListError as exc:
        return HTTP_BAD_REQUEST, {
            "representation": "bounded",
            "bounded_version": contract.BOUNDED_VERSION,
            "projects_contract": contract.CONTRACT_VERSION,
            "endpoint": "decide",
            "snapshot": snapshot.snapshot_id,
            "error": {"code": exc.code, "message": str(exc)},
        }
    except contract.SpecError as exc:
        return error_response(
            "invalid_spec",
            "the request body is not a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            issues=_issues(exc),
            recovery=recovery_hints(exc.issues, facets=facets,
                                    benchmark_ids=tuple(snapshot.benchmark_ids()), payload=payload),
            reading=for_refusal(exc.issues),
            coverage=coverage_for_spec(spec, snapshot),
        )
    return HTTP_OK, decision.model_dump(mode="json")


def compare(payload: Any, old_snapshot, new_snapshot, *,
            expected_snapshot: str | None = None) -> tuple[int, dict[str, Any]]:
    """Compare one spec against two verified snapshots for ``POST /v1/compare``."""
    if expected_snapshot and expected_snapshot != new_snapshot.snapshot_id:
        status, body = snapshot_changed(expected_snapshot, new_snapshot)
        body["endpoint"] = "compare"
        return status, body
    if not isinstance(payload, dict) or not isinstance(payload.get("spec"), dict):
        return error_response(
            "invalid_request",
            "the request body must contain a spec object and compare_to snapshot ID",
            status=HTTP_BAD_REQUEST,
            snapshot_id=new_snapshot.snapshot_id,
            endpoint="compare",
        )
    compare_to = payload.get("compare_to")
    if compare_to != old_snapshot.snapshot_id:
        return error_response(
            "comparison_snapshot_changed",
            f"the comparison snapshot is {old_snapshot.snapshot_id}, not {compare_to}",
            status=HTTP_CONFLICT,
            snapshot_id=new_snapshot.snapshot_id,
            endpoint="compare",
        )
    facets = _facets(old_snapshot, new_snapshot)
    try:
        spec = contract.parse_spec(payload["spec"], facets=facets)
    except contract.SpecError as exc:
        return error_response(
            "invalid_spec",
            "the request body does not contain a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=new_snapshot.snapshot_id,
            issues=_issues(exc),
            endpoint="compare",
        )
    comparison_spec = spec.model_copy(
        update={"snapshot": "latest", "explain": "full", "estate": None})
    try:
        old = run_decision(comparison_spec, old_snapshot, facets=facets, comparison=True,
                           _validate_current=False)
        new = run_decision(comparison_spec, new_snapshot, facets=facets, comparison=True)
    except contract.SpecError as exc:
        return error_response(
            "invalid_spec",
            "the request body does not contain a valid decision spec",
            status=HTTP_BAD_REQUEST,
            snapshot_id=new_snapshot.snapshot_id,
            issues=_issues(exc),
            endpoint="compare",
        )
    result = compare_decisions(
        old,
        new,
        old_as_of=old_snapshot.as_of.isoformat() if old_snapshot.as_of else None,
        new_as_of=new_snapshot.as_of.isoformat() if new_snapshot.as_of else None,
    )
    result["spec_snapshot_ignored"] = spec.snapshot != "latest"
    return HTTP_OK, {
        "contract_version": contract.CONTRACT_VERSION,
        "endpoint": "compare",
        "snapshot": new_snapshot.snapshot_id,
        "compare_to": old_snapshot.snapshot_id,
        "result": result,
    }


MODEL_COMPARISON_BYTES = 14_000


def compare_models(
    payload: Any, snapshot, *, expected_snapshot: str | None = None
) -> tuple[int, dict[str, Any]]:
    """Read named models from one verified snapshot, without an objective."""
    from decision.model_comparison import collect_models, update_sources

    if expected_snapshot and expected_snapshot != snapshot.snapshot_id:
        return snapshot_changed(expected_snapshot, snapshot, endpoint="compare-models")
    try:
        request = contract.ModelComparisonRequest.model_validate(payload)
    except ValidationError as exc:
        return error_response(
            "invalid_request",
            "models must contain two to four distinct lab/model IDs",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            endpoint="compare-models",
            issues=[
                {"path": issue.path[:128], "reason": issue.reason[:300]}
                for issue in contract._issues(exc)[:8]
            ],
        )
    candidates = tuple(snapshot.candidates())
    model_ids = {snapshot.model_of(cid) for cid in candidates}
    missing = [
        {"path": f"models[{index}]", "reason": "model is not in this snapshot's active lineup"}
        for index, mid in enumerate(request.models)
        if mid not in model_ids
    ]
    if missing:
        return error_response(
            "invalid_request",
            "unknown model ID in models",
            status=HTTP_BAD_REQUEST,
            snapshot_id=snapshot.snapshot_id,
            endpoint="compare-models",
            issues=missing,
        )
    try:
        body = collect_models(request.models, snapshot)
    except SnapshotError:
        return error_response(
            "snapshot_refused",
            "rebuild the snapshot to retain comparison provenance",
            status=HTTP_SERVICE_UNAVAILABLE,
            snapshot_id=snapshot.snapshot_id,
            endpoint="compare-models",
        )

    rows = body["models"]
    # Remove complete records, together with their citations, until the MCP reserve fits.
    while len(serialise(body)) > MODEL_COMPARISON_BYTES:
        for collection in ("evidence", "offerings", "facts"):
            row = max(rows, key=lambda model: len(model[collection]))
            if row[collection]:
                removed = row[collection].pop()
                body["omitted"][collection] += 1
                if collection == "offerings":
                    body["omitted"]["facts"] += len(removed["facts"])
                break
        else:
            return error_response(
                "snapshot_refused",
                "comparison metadata exceeds the response budget",
                status=HTTP_SERVICE_UNAVAILABLE,
                snapshot_id=snapshot.snapshot_id,
                endpoint="compare-models",
            )
        update_sources(body, snapshot)
    return HTTP_OK, body


def serialise(body: dict[str, Any]) -> bytes:
    """Byte for byte what ``modelspec decide --json`` prints: compact, UTF-8.

    Compact because a ``full`` decision runs to hundreds of kilobytes, a third
    of it indentation when pretty-printed (MODEL-163).
    """
    return (json.dumps(body, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
