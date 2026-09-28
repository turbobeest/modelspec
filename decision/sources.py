"""The source registry's re-check: deterministic change detection (MODEL-137).

Every fact and piece of evidence names the registered sources it was read from,
and the cited region of each source it depends on (design §5). A re-check
fetches each source with plain HTTP, normalises it (``decision.normalise``) and
compares the fingerprint of each cited region with the last snapshot:

- ``unchanged``: every fact citing the region is re-confirmed, at no agent cost;
- ``changed``: only the facts citing that region are re-queued for re-extraction
  and two-key verification, and a governance region raises an alert event;
- ``unreachable``: counted against a grace period, after which the source's facts
  are quarantined.

Nothing here calls a model or a paid scraper. The re-check is a pure function of
the sources, their last states and what the origin servers return; agents run
downstream, only on what ``RecheckReport.requeue`` lists.

Source records use the shared types in ``decision.model``.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
import yaml

from decision.model import CitedRegion as CitedRegion
from decision.model import Source, SourceSnapshot
from decision.normalise import (
    NORMALISERS,
    Locator,
    UnsupportedContentError,
    canonical_url,
    fingerprint,
    normalise_document,
    select_region,
)


class FetchMode(StrEnum):
    HTTP = "http"
    CONDITIONAL_HTTP = "conditional_http"
    #: Needs a rendered browser to show its content. Declared, not implemented: a
    #: re-check records the need and fetches nothing.
    RENDERED = "rendered"

    @property
    def relative_cost(self) -> int:
        """What one check costs relative to a plain fetch."""
        return 20 if self is FetchMode.RENDERED else 1


def load_sources(path: str | Path) -> dict[str, Source]:
    """Load the canonical ``registry/sources.yaml`` format.

    The file is ``{schema_version: 1, sources: [...]}``, and each source row is
    validated by :class:`decision.model.Source`. A missing file is an empty
    registry so a checkout with no registered sources still builds an empty
    snapshot.
    """
    path = Path(path)
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping) or data.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    rows = data.get("sources")
    if not isinstance(rows, list):
        raise ValueError(f"{path}: sources must be a list")
    registered: dict[str, Source] = {}
    for i, raw in enumerate(rows):
        try:
            source = Source.model_validate(raw)
        except ValueError as exc:
            raise ValueError(f"{path}: sources[{i}]: {exc}") from exc
        if source.id in registered:
            raise ValueError(f"{path}: duplicate source ID {source.id!r}")
        registered[source.id] = source
    return registered

# --- what cites a region, and how often it is re-checked -----------------------------------------


class FactKind(StrEnum):
    PRICE = "price"
    RATE_LIMIT = "rate_limit"
    GOVERNANCE = "governance"
    LIVE_LEADERBOARD = "live_leaderboard"
    STATIC_EVIDENCE = "static_evidence"
    MODEL_SPEC = "model_spec"


#: Design §5. Model specifications are also checked at release; that is an event,
#: not an interval.
DEFAULT_INTERVALS: Mapping[FactKind, timedelta] = {
    FactKind.PRICE: timedelta(days=7),
    FactKind.RATE_LIMIT: timedelta(days=7),
    FactKind.GOVERNANCE: timedelta(days=7),
    FactKind.LIVE_LEADERBOARD: timedelta(days=7),
    FactKind.STATIC_EVIDENCE: timedelta(days=91),
    FactKind.MODEL_SPEC: timedelta(days=30),
}

#: Consecutive unreachable checks before a source's facts are quarantined.
DEFAULT_GRACE = 3


@dataclass(frozen=True)
class Citation:
    """A fact or piece of evidence (``ref``) that depends on one cited region."""

    ref: str
    source_id: str
    region_id: str
    kind: FactKind


@dataclass(frozen=True)
class SourceState:
    source_id: str
    snapshot: SourceSnapshot | None = None
    consecutive_failures: int = 0
    quarantined: bool = False
    last_attempt_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "snapshot": self.snapshot.model_dump(mode="json") if self.snapshot else None,
            "consecutive_failures": self.consecutive_failures,
            "quarantined": self.quarantined,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SourceState:
        snapshot = data.get("snapshot")
        attempt = data.get("last_attempt_at")
        return cls(
            source_id=data["source_id"],
            snapshot=SourceSnapshot.model_validate(snapshot) if snapshot else None,
            consecutive_failures=data.get("consecutive_failures", 0),
            quarantined=data.get("quarantined", False),
            last_attempt_at=datetime.fromisoformat(attempt) if attempt else None,
        )


def due(
    source: Source,
    now: datetime,
    *,
    state: SourceState | None,
    citations: Iterable[Citation],
    intervals: Mapping[FactKind, timedelta] = DEFAULT_INTERVALS,
) -> bool:
    """Whether ``source`` is due: its interval is the shortest of the facts citing it.

    A source nothing cites is never due; one never checked always is.
    """
    kinds = {c.kind for c in citations if c.source_id == source.id}
    if not kinds:
        return False
    last = state and (state.last_attempt_at or (state.snapshot and state.snapshot.retrieved_at))
    if not last:
        return True
    return now - last >= min(intervals[k] for k in kinds)


# --- fetching ------------------------------------------------------------------------------------

USER_AGENT = "ModelSpec-SourceCheck/1.0 (+https://modelspec.dev)"


@dataclass(frozen=True)
class FetchResult:
    outcome: Literal["ok", "not_modified", "unreachable"]
    status: int | None = None
    body: bytes = b""
    content_type: str = ""
    charset: str | None = None
    etag: str | None = None
    last_modified: str | None = None
    error: str | None = None


class Fetcher:
    """Plain HTTP with conditional requests, timeouts, retries with exponential backoff
    (honouring a numeric ``Retry-After``) and a minimum interval between requests to
    one host. ``sleep`` and ``clock`` are injectable so tests never wait."""

    RETRY_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})

    def __init__(
        self,
        client: httpx.Client | None = None,
        *,
        timeout: float = 20.0,
        retries: int = 2,
        backoff: float = 1.0,
        max_backoff: float = 60.0,
        min_host_interval: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        user_agent: str = USER_AGENT,
    ) -> None:
        self.client = client or httpx.Client()
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.max_backoff = max_backoff
        self.min_host_interval = min_host_interval
        self.sleep = sleep
        self.clock = clock
        self.user_agent = user_agent
        self._last_request: dict[str, float] = {}

    def _wait_for_host(self, host: str) -> None:
        last = self._last_request.get(host)
        if last is not None:
            remaining = self.min_host_interval - (self.clock() - last)
            if remaining > 0:
                self.sleep(remaining)
        self._last_request[host] = self.clock()

    def fetch(
        self, url: str, *, etag: str | None = None, last_modified: str | None = None
    ) -> FetchResult:
        headers = {"user-agent": self.user_agent}
        if etag:
            headers["if-none-match"] = etag
        if last_modified:
            headers["if-modified-since"] = last_modified
        host = urlsplit(url).hostname or ""
        error = "no attempt"
        delay = 0.0
        for attempt in range(self.retries + 1):
            if attempt:
                self.sleep(delay)
            self._wait_for_host(host)
            delay = min(self.backoff * 2**attempt, self.max_backoff)
            try:
                response = self.client.get(
                    url, headers=headers, timeout=self.timeout, follow_redirects=True
                )
            except httpx.TimeoutException as exc:
                error = f"timeout: {exc}"
                continue
            except httpx.TransportError as exc:
                error = f"transport error: {type(exc).__name__}: {exc}"
                continue
            if response.status_code == 304:
                return FetchResult(
                    "not_modified",
                    304,
                    etag=response.headers.get("etag"),
                    last_modified=response.headers.get("last-modified"),
                )
            if response.status_code in self.RETRY_STATUSES:
                error = f"HTTP {response.status_code}"
                retry_after = response.headers.get("retry-after", "")
                if retry_after.strip().isdigit():
                    delay = min(float(retry_after), self.max_backoff)
                continue
            if not response.is_success:
                return FetchResult(
                    "unreachable", response.status_code, error=f"HTTP {response.status_code}"
                )
            return FetchResult(
                "ok",
                response.status_code,
                body=response.content,
                content_type=response.headers.get("content-type", ""),
                charset=response.charset_encoding,
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
            )
        return FetchResult("unreachable", error=error)


# --- retained copies -----------------------------------------------------------------------------

_REF = re.compile(r"^sha256:([0-9a-f]{64})$")


class CopyStore:
    """Content-addressed retained copies (``sha256:<hex>`` → file), outside git.

    The root is ``root``, else ``$MODELSPEC_SOURCE_CACHE``, else
    ``~/.cache/modelspec/sources``.
    """

    def __init__(self, root: Path | str | None = None) -> None:
        env = os.environ.get("MODELSPEC_SOURCE_CACHE")
        self.root = Path(root or env or Path.home() / ".cache" / "modelspec" / "sources")

    def path(self, ref: str) -> Path:
        m = _REF.match(ref)
        if not m:
            raise ValueError(f"not a copy ref: {ref!r}")
        digest = m.group(1)
        return self.root / digest[:2] / digest

    def put(self, body: bytes) -> str:
        ref = fingerprint_bytes(body)
        target = self.path(ref)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
            with os.fdopen(fd, "wb") as fh:
                fh.write(body)
            os.replace(tmp, target)
        return ref

    def get(self, ref: str) -> bytes:
        return self.path(ref).read_bytes()

    def has(self, ref: str) -> bool:
        return self.path(ref).exists()


def fingerprint_bytes(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


# --- the re-check --------------------------------------------------------------------------------


class RegionStatus(StrEnum):
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    UNREACHABLE = "unreachable"


@dataclass(frozen=True)
class RegionResult:
    source_id: str
    region_id: str
    status: RegionStatus
    previous: str | None
    current: str | None
    detail: str | None = None


@dataclass(frozen=True)
class GovernanceChange:
    """An alert event: a region cited by a governance fact changed. Consumers come later."""

    source_id: str
    region_id: str
    url: str
    refs: tuple[str, ...]
    detected_at: datetime
    previous_fingerprint: str | None
    current_fingerprint: str | None
    previous_copy_ref: str
    current_copy_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": "governance_source_changed",
            "source_id": self.source_id,
            "region_id": self.region_id,
            "url": self.url,
            "refs": list(self.refs),
            "detected_at": self.detected_at.isoformat(),
            "previous_fingerprint": self.previous_fingerprint,
            "current_fingerprint": self.current_fingerprint,
            "previous_copy_ref": self.previous_copy_ref,
            "current_copy_ref": self.current_copy_ref,
        }


@dataclass(frozen=True)
class Skipped:
    """A source the deterministic re-check could not assess, and why."""

    source_id: str
    reason: str


@dataclass
class RecheckReport:
    regions: list[RegionResult] = field(default_factory=list)
    #: Facts and evidence citing a changed region: re-extract and re-verify these.
    requeue: list[str] = field(default_factory=list)
    #: Facts and evidence whose every cited region is unchanged.
    reconfirmed: list[str] = field(default_factory=list)
    #: Facts and evidence on a source past its unreachable grace period.
    quarantine: list[str] = field(default_factory=list)
    alerts: list[GovernanceChange] = field(default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)
    #: Every source's state after this run; persist these for the next one.
    states: dict[str, SourceState] = field(default_factory=dict)


def recheck(
    sources: Iterable[Source],
    states: Mapping[str, SourceState],
    citations: Iterable[Citation],
    *,
    fetcher: Fetcher,
    store: CopyStore,
    now: datetime,
    grace: int = DEFAULT_GRACE,
) -> RecheckReport:
    """Re-check ``sources`` against their last states. See the module docstring."""
    sources = list(sources)
    citations = list(citations)
    regions_of = {s.id: {r.id for r in s.cited_regions} for s in sources}
    for c in citations:
        if c.source_id in regions_of and c.region_id not in regions_of[c.source_id]:
            raise ValueError(f"{c.ref} cites unknown region {c.source_id}#{c.region_id}")

    report = RecheckReport(states=dict(states))
    for source in sources:
        state = states.get(source.id) or SourceState(source.id)
        report.states[source.id] = _check_one(source, state, fetcher, store, now, grace, report)

    by_region: dict[tuple[str, str], list[Citation]] = {}
    for c in citations:
        by_region.setdefault((c.source_id, c.region_id), []).append(c)

    requeue: set[str] = set()
    unchanged: set[str] = set()
    for result in report.regions:
        cited = by_region.get((result.source_id, result.region_id), [])
        if result.status is RegionStatus.CHANGED:
            requeue.update(c.ref for c in cited)
            governance = tuple(sorted(c.ref for c in cited if c.kind is FactKind.GOVERNANCE))
            previous = states.get(result.source_id)
            if governance and previous and previous.snapshot:
                current = report.states[result.source_id].snapshot
                assert current is not None
                report.alerts.append(
                    GovernanceChange(
                        source_id=result.source_id,
                        region_id=result.region_id,
                        url=next(s.url for s in sources if s.id == result.source_id),
                        refs=governance,
                        detected_at=now,
                        previous_fingerprint=result.previous,
                        current_fingerprint=result.current,
                        previous_copy_ref=previous.snapshot.copy_ref,
                        current_copy_ref=current.copy_ref,
                    )
                )
        elif result.status is RegionStatus.UNCHANGED:
            unchanged.update(c.ref for c in cited)

    quarantined_sources = {sid for sid, st in report.states.items() if st.quarantined}
    quarantine = {c.ref for c in citations if c.source_id in quarantined_sources}
    report.requeue = sorted(requeue - quarantine)
    report.reconfirmed = sorted(unchanged - requeue - quarantine)
    report.quarantine = sorted(quarantine)
    return report


def _check_one(
    source: Source,
    state: SourceState,
    fetcher: Fetcher,
    store: CopyStore,
    now: datetime,
    grace: int,
    report: RecheckReport,
) -> SourceState:
    if source.fetch == FetchMode.RENDERED.value:
        report.skipped.append(Skipped(source.id, "rendered_fetch_required"))
        return state

    previous = state.snapshot
    conditional = source.fetch == FetchMode.CONDITIONAL_HTTP.value and previous is not None
    result = fetcher.fetch(
        canonical_url(str(source.url)),
        etag=previous.etag if conditional and previous else None,
        last_modified=previous.last_modified if conditional and previous else None,
    )
    old = previous.region_fingerprints if previous else {}

    if result.outcome == "not_modified" and previous is not None:
        snapshot = previous.model_copy(update={
            "retrieved_at": now,
            "etag": result.etag or previous.etag,
            "last_modified": result.last_modified or previous.last_modified,
        })
        for region in source.cited_regions:
            fp = old.get(region.id)
            status = RegionStatus.UNCHANGED if fp is not None else RegionStatus.CHANGED
            report.regions.append(RegionResult(source.id, region.id, status, fp, fp, "HTTP 304"))
        return SourceState(source.id, snapshot, 0, False, now)

    if result.outcome != "ok":
        failures = state.consecutive_failures + 1
        detail = result.error or "HTTP 304 without a baseline"
        for region in source.cited_regions:
            fp = old.get(region.id)
            report.regions.append(
                RegionResult(source.id, region.id, RegionStatus.UNREACHABLE, fp, None, detail)
            )
        return SourceState(source.id, previous, failures, failures >= grace, now)

    rules = NORMALISERS[source.normaliser]
    try:
        if "pdf" in result.content_type.lower():
            raise UnsupportedContentError("pdf")
        doc = normalise_document(result.body, rules, charset=result.charset)
    except UnsupportedContentError as exc:
        report.skipped.append(Skipped(source.id, f"unsupported_content:{exc.kind}"))
        return replace(state, last_attempt_at=now)

    current: dict[str, str | None] = {}
    for region in source.cited_regions:
        kind = "heading" if region.locator.kind == "heading_anchor" else region.locator.kind
        text = select_region(doc, Locator(kind, region.locator.value))
        fp = fingerprint(text) if text is not None else None
        current[region.id] = fp
        before = old.get(region.id)
        unchanged = fp is not None and fp == before
        status = RegionStatus.UNCHANGED if unchanged else RegionStatus.CHANGED
        note = None if fp is not None else "locator matched nothing"
        report.regions.append(RegionResult(source.id, region.id, status, before, fp, note))

    snapshot = SourceSnapshot(
        source_id=source.id,
        retrieved_at=now,
        page_fingerprint=fingerprint(doc.text),
        region_fingerprints=current,
        copy_ref=store.put(result.body),
        etag=result.etag,
        last_modified=result.last_modified,
    )
    return SourceState(source.id, snapshot, 0, False, now)
