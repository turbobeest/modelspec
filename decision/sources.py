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
import json
import os
import re
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import urlsplit

import yaml

if TYPE_CHECKING:
    import httpx

from decision.model import CitedRegion as CitedRegion
from decision.model import RenderedInteraction, Source, SourceSnapshot
from decision.retention import citation_metadata, cite_only_origin, require_source_url
from decision.normalise import (
    NORMALISERS,
    Locator,
    UnsupportedContentError,
    canonical_url,
    fingerprint,
    normalise_document,
    select_region,
)
from decision.perplexity_faq import prepare_pro_faq


class FetchMode(StrEnum):
    HTTP = "http"
    CONDITIONAL_HTTP = "conditional_http"
    #: Needs a rendered browser to show its content. Opt-in callers use
    #: RenderedFetcher; the plain HTTP re-check records the need without fetching.
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
    from schema import private_data, redacted_error

    content = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:
        if private_data(path):
            raise ValueError(redacted_error(exc, path)) from None
        raise
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
            if private_data(path):
                raise ValueError(redacted_error(exc, path, content=content, field_prefix=("sources", i))) from None
            raise ValueError(f"{path}: sources[{i}]: {exc}") from exc
        if source.id in registered:
            if private_data(path):
                raise ValueError(f"{path}: duplicate source ID; values redacted") from None
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
    resolved_urls: tuple[str, ...] = ()
    snapshot_ref: str | None = None
    retrieved_at: datetime | None = None


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
        import httpx

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
        import httpx

        headers = {"user-agent": self.user_agent}
        if etag:
            headers["if-none-match"] = etag
        if last_modified:
            headers["if-modified-since"] = last_modified
        host = urlsplit(url).hostname or ""
        error = "no attempt"
        status: int | None = None
        delay = 0.0
        for attempt in range(self.retries + 1):
            if attempt:
                self.sleep(delay)
            self._wait_for_host(host)
            delay = min(self.backoff * 2**attempt, self.max_backoff)
            status = None
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
            status = response.status_code
            if response.status_code == 304:
                return FetchResult(
                    "not_modified",
                    304,
                    etag=response.headers.get("etag"),
                    last_modified=response.headers.get("last-modified"),
                    resolved_urls=tuple(str(item.url) for item in (*response.history, response)),
                    retrieved_at=datetime.now(UTC),
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
                resolved_urls=tuple(str(item.url) for item in (*response.history, response)),
                retrieved_at=datetime.now(UTC),
            )
        return FetchResult("unreachable", status, error=error)


RenderedPreparation = Callable[[Any, float], None]

AWS_GLOBAL_ANTHROPIC_COMPONENT = (
    'div.aws-table[data-pricing-markup^="<h2>Global Cross-region Inference</h2>"]'
    '[data-pricing-markup*="<th>Anthropic models</th>"]'
)


def _prepare_aws_pricing(page: Any, timeout: float) -> None:
    """AWS mounts its pricing cells after opening the provider and scrolling."""
    deadline = time.monotonic() + timeout

    def remaining_ms() -> float:
        return max(1.0, (deadline - time.monotonic()) * 1000)

    page.get_by_role("tab", name="Anthropic", exact=True).click(timeout=remaining_ms())
    page.locator(AWS_GLOBAL_ANTHROPIC_COMPONENT).scroll_into_view_if_needed(
        timeout=remaining_ms())
    page.wait_for_function(
        r"""selector => {
            const tables = document.querySelectorAll(selector);
            if (tables.length !== 1) return false;
            const rows = Array.from(tables[0].querySelectorAll('tr'));
            const header = rows.some(row => Array.from(row.querySelectorAll('th'))
                .some(cell => cell.textContent.trim() === 'Anthropic models'));
            const prices = rows.some(row => Array.from(row.querySelectorAll('td'))
                .filter(cell => /^\$\d+(?:\.\d+)?$/.test(cell.textContent.trim())).length >= 2);
            return header && prices;
        }""",
        arg=AWS_GLOBAL_ANTHROPIC_COMPONENT + " table", timeout=remaining_ms())


# Preparations are engine code, never executable instructions from the registry.
RENDERED_PREPARATIONS: Mapping[str, RenderedPreparation] = {
    "aws-pricing": _prepare_aws_pricing,
    "model-368-perplexity-pro-faq": prepare_pro_faq,
}

_REGION_HAS_TEXT = """selector => {
    const node = document.querySelector(selector);
    return node !== null && node.textContent.trim().length > 0;
}"""


@dataclass(frozen=True)
class CitedRegionWait:
    """Wait, best effort, until each cited CSS region holds text (MODEL-423).

    A client-side app can mount its content after the load event and after the
    network goes idle. z.ai's subscribe page was captured as an empty shell, so
    every plan fact citing its plan cards read "cited region not found". A region
    still empty at the deadline is left to the readers, which report it as not
    found. The selectors come from the registry, but only as data: the page runs
    one fixed query function with the selector as its argument.
    """

    selectors: tuple[str, ...]

    def __call__(self, page: Any, timeout: float) -> None:
        try:
            from playwright.sync_api import TimeoutError as WaitTimeout
        except ImportError:  # a fake page in tests raises the builtin
            WaitTimeout = TimeoutError  # noqa: N806
        deadline = time.monotonic() + timeout
        for selector in self.selectors:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            try:
                page.wait_for_function(_REGION_HAS_TEXT, arg=selector,
                                       timeout=remaining * 1000)
            except WaitTimeout:
                return


class RenderedInteractionError(Exception):
    """A recipe could not safely reach its required page state."""


@contextmanager
def _read_only_interactions(page: Any, prepare: RenderedInteractions):
    context = page.context
    other_pages = set(context.pages) - {page}
    blocked = False

    def endpoint(url: str) -> tuple[str, str, str]:
        parsed = urlsplit(url)
        return parsed.scheme, parsed.netloc, parsed.path

    telemetry = {
        endpoint(str(step.url))
        for recipe in prepare.recipes for step in recipe if step.action == "block_telemetry"
    }

    def read_only(route: Any) -> None:
        nonlocal blocked
        request = route.request
        navigation = request.is_navigation_request()
        known_telemetry = endpoint(request.url) in telemetry
        if navigation or request.method not in {"GET", "HEAD"} or known_telemetry:
            if navigation or not known_telemetry:
                blocked = True
            route.abort()
        else:
            route.fallback()

    # Context routes also intercept the first request of a new popup.
    context.route("**/*", read_only)
    try:
        yield
    finally:
        try:
            for opened_page in context.pages:
                if opened_page not in other_pages:
                    opened_page.close()
        finally:
            context.unroute("**/*", read_only)
    if blocked:
        raise RenderedInteractionError("blocked interaction request")


_SAFE_CONTROL = r"""(node, action) => {
    const tag = node.tagName.toLowerCase();
    const role = node.getAttribute('role');
    const labels = [node.getAttribute('aria-label'), node.textContent, node.value]
        .map(value => (value || '').trim()).filter(Boolean);
    if (node.closest('form') || node.hasAttribute('form')) return false;
    if (node.closest('a[href]') && !node.closest('a[href]').getAttribute('href').startsWith('#'))
        return false;
    const context = node.closest('[id*="cookie"],[id*="consent"],[class*="cookie"],[class*="consent"]');
    if (action !== 'reject_consent' &&
        (context || labels.some(label =>
            /\b(cookie|consent|accept|agree|allow all)\b/i.test(label)))) return false;
    if (labels.some(label =>
        /\b(log.?in|sign.?in|sign.?up|register|submit|buy|purchase|checkout|subscribe)\b/i.test(label)))
        return false;
    if (action === 'select_option') return tag === 'select';
    const control = tag === 'button' || ['tab', 'button', 'combobox', 'option'].includes(role);
    if (!control) return false;
    if (action === 'reject_consent') {
        const reject = /^(reject all( cookies)?|decline( all)?|deny all|only necessary cookies)$/i;
        return labels.length > 0 && labels.every(label => reject.test(label));
    }
    if (/^(submit|reset)$/i.test(node.getAttribute('type') || '')) return false;
    return true;
}"""

_REGION_CONTAINS_TEXT = r"""({selector, text}) => {
    const nodes = document.querySelectorAll(selector);
    if (nodes.length !== 1) return false;
    const node = nodes[0];
    const shown = node.tagName === 'SELECT'
        ? Array.from(node.selectedOptions, option => option.label).join('\n')
        : node.innerText;
    return shown.includes(text);
}"""


@dataclass(frozen=True)
class RenderedInteractions:
    """Execute validated UI data within one deadline; never capture a failed recipe."""

    recipes: tuple[tuple[RenderedInteraction, ...], ...]

    def __call__(self, page: Any, timeout: float) -> None:
        from playwright.sync_api import Error

        if any(recipe != self.recipes[0] for recipe in self.recipes[1:]):
            raise RenderedInteractionError("conflicting interaction recipes for one URL")
        deadline = time.monotonic() + timeout

        def remaining_ms() -> float:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RenderedInteractionError("interaction time budget exhausted")
            return remaining * 1000

        try:
            for step in self.recipes[0]:
                if step.action == "block_telemetry":
                    continue
                if step.action == "wait_text":
                    page.wait_for_function(
                        _REGION_CONTAINS_TEXT,
                        arg={"selector": step.selector, "text": step.text},
                        timeout=remaining_ms())
                    continue
                target = page.locator(step.selector)
                if step.action == "scroll":
                    target.scroll_into_view_if_needed(timeout=remaining_ms())
                    continue
                if not target.evaluate(_SAFE_CONTROL, step.action, timeout=remaining_ms()):
                    raise RenderedInteractionError("unsafe interaction control")
                if step.action == "select_option":
                    target.select_option(value=step.value, timeout=remaining_ms())
                else:
                    target.click(timeout=remaining_ms())
            remaining_ms()
        except Error as exc:
            raise RenderedInteractionError(f"interaction failed: {exc}") from exc


def rendered_preparation(source_ids: Iterable[str],
                         sources: Mapping[str, Source]) -> RenderedPreparation | None:
    """The preparation a live render of these sources' shared URL runs before capture.

    A source's own preparation wins: it already waits for what it opens. Otherwise
    the render waits for every cited CSS region of every source at the URL.
    """
    ids = sorted(set(source_ids))
    recipes = tuple(tuple(sources[sid].rendered_interactions)
                    for sid in ids if sid in sources and sources[sid].rendered_interactions)
    if recipes:
        return RenderedInteractions(recipes)
    named = next((RENDERED_PREPARATIONS[sid] for sid in ids if sid in RENDERED_PREPARATIONS),
                 None)
    if named is not None:
        return named
    from decision.normalise import _split_citation

    selectors = tuple(dict.fromkeys(
        _split_citation(region.locator.value)[0]
        for sid in ids if sid in sources
        for region in sources[sid].cited_regions if region.locator.kind == "css"))
    return CitedRegionWait(selectors) if selectors else None


class RenderedFetcher:
    """Opt-in local Chromium fetches, sharing one browser for a context-managed run.

    Playwright is imported only when entering the context. Network idle is best
    effort: pages with persistent connections still yield their rendered HTML.
    An optional preparation runs before capture, within one timeout budget.
    Registry recipe failures return no HTML. Legacy preparations retain their
    partial HTML with an error for the caller to report.
    """

    def __init__(self, *, timeout: float = 20.0, idle_timeout: float = 5.0) -> None:
        self.timeout = timeout
        self.idle_timeout = idle_timeout

    def __enter__(self) -> RenderedFetcher:
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        try:
            # Keep Playwright's sandbox default. CI isolation comes from the
            # separate read-only render job, which has no repository write token.
            self._browser = self._playwright.chromium.launch(headless=True)
            self._context = self._browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                service_workers="block",
            )
        except Exception:
            self._playwright.stop()
            raise
        return self

    def __exit__(self, *exc: object) -> None:
        try:
            self._browser.close()
        finally:
            self._playwright.stop()

    def fetch(self, url: str, *, prepare: RenderedPreparation | None = None) -> FetchResult:
        from playwright.sync_api import Error, TimeoutError

        page = None
        try:
            page = self._context.new_page()
            response = page.goto(url, wait_until="load", timeout=self.timeout * 1000)
            if response is None:
                return FetchResult("unreachable", error="no HTTP response")
            if not 200 <= response.status < 300:
                return FetchResult("unreachable", response.status,
                                   error=f"HTTP {response.status}")
            try:
                page.wait_for_load_state("networkidle", timeout=self.idle_timeout * 1000)
            except TimeoutError:
                pass
            guard = (_read_only_interactions(page, prepare) if isinstance(prepare, RenderedInteractions)
                     else nullcontext())
            with guard:
                preparation_error = None
                if prepare is not None:
                    try:
                        prepare(page, self.timeout)
                    except Error as exc:
                        preparation_error = f"rendered preparation failed: {exc}"
                redirects = []
                request = response.request
                while request is not None:
                    redirects.append(str(request.url))
                    request = request.redirected_from
                return FetchResult("ok", response.status, body=page.content().encode("utf-8"),
                                   content_type="text/html", charset="utf-8",
                                   error=preparation_error,
                                   resolved_urls=tuple(dict.fromkeys((*reversed(redirects),
                                                        str(response.url), str(page.url)))),
                                   retrieved_at=datetime.now(UTC))
        except RenderedInteractionError as exc:
            return FetchResult("unreachable", response.status, error=str(exc))
        except Error as exc:
            return FetchResult("unreachable", error=str(exc))
        finally:
            if page is not None:
                page.close()


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

    # The cache directory can be restored from another run's artifact, so a file is
    # trusted only when its bytes still hash to its name (MODEL-235).

    def put(self, body: bytes, *, source_url: str, retrieved_at: datetime | None = None,
            resolved_urls: Iterable[str] = ()) -> str:
        source_url = require_source_url(source_url)
        resolved_urls = tuple(resolved_urls)
        ref = fingerprint_bytes(body)
        if cite_only_origin(source_url, resolved_urls):
            self.record_citation(ref, source_url=source_url, retrieved_at=retrieved_at,
                                 resolved_urls=resolved_urls)
            return ref
        if self.citation(ref) is not None:
            return ref
        target = self.path(ref)
        if not self.has(ref):
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
            with os.fdopen(fd, "wb") as fh:
                fh.write(body)
            os.replace(tmp, target)
        return ref

    def record_citation(self, ref: str, *, source_url: str,
                        retrieved_at: datetime | None = None, resolved_urls=()) -> None:
        target = self.path(ref).with_suffix(".citation.json")
        metadata = citation_metadata(source_url, ref, retrieved_at=retrieved_at or datetime.now(UTC),
                                     resolved_urls=resolved_urls)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(metadata, output, sort_keys=True)
        os.replace(temporary, target)

    def citation(self, ref: str) -> dict | None:
        target = self.path(ref).with_suffix(".citation.json")
        if not target.is_file():
            return None
        metadata = json.loads(target.read_text(encoding="utf-8"))
        if metadata.get("snapshot_ref") != ref:
            raise ValueError("citation metadata does not match its hash")
        return metadata

    def get(self, ref: str, *, source_url: str | None = None) -> bytes:
        if self.citation(ref) is not None or source_url is not None and cite_only_origin(source_url):
            raise ValueError("cite-only source has no readable retained copy")
        body = self.path(ref).read_bytes()
        if fingerprint_bytes(body) != ref:
            raise ValueError(f"retained copy {ref} does not match its hash")
        return body

    def has(self, ref: str) -> bool:
        if self.citation(ref) is not None:
            return False
        target = self.path(ref)
        if not target.is_file() or target.is_symlink():
            return False
        return fingerprint_bytes(target.read_bytes()) == ref


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
    #: The final fetch attempt for each source, including HTTP status and errors.
    fetches: dict[str, FetchResult] = field(default_factory=dict)


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
        elif result.status is RegionStatus.UNCHANGED and result.detail != "cite-only":
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
    report.fetches[source.id] = result
    old = previous.region_fingerprints if previous else {}

    previous_citation = store.citation(previous.copy_ref) if previous else None
    resolved_urls = tuple(dict.fromkeys((*result.resolved_urls,
                          *((previous_citation or {}).get("resolved_urls", ())))))
    if (cite_only_origin(source.url, resolved_urls) or previous_citation is not None) \
            and result.outcome in {"ok", "not_modified"}:
        if result.outcome == "not_modified" and previous is None:
            return replace(state, last_attempt_at=now)
        ref = (previous.copy_ref if result.outcome == "not_modified" else
               store.put(result.body, source_url=str(source.url), retrieved_at=now,
                         resolved_urls=resolved_urls))
        store.record_citation(ref, source_url=str(source.url), retrieved_at=now,
                              resolved_urls=resolved_urls)
        for region in source.cited_regions:
            before = previous.copy_ref if previous else None
            status = RegionStatus.UNCHANGED if before == ref else RegionStatus.CHANGED
            report.regions.append(RegionResult(source.id, region.id, status, before, ref, "cite-only"))
        report.skipped.append(Skipped(source.id, "cite_only_not_machine_verified"))
        snapshot = SourceSnapshot(source_id=source.id, retrieved_at=now, copy_ref=ref,
                                  page_fingerprint=ref, region_fingerprints={},
                                  etag=result.etag, last_modified=result.last_modified)
        return SourceState(source.id, snapshot, 0, False, now)

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
        copy_ref=store.put(result.body, source_url=str(source.url), retrieved_at=now,
                           resolved_urls=result.resolved_urls),
        etag=result.etag,
        last_modified=result.last_modified,
    )
    return SourceState(source.id, snapshot, 0, False, now)
