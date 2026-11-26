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

from decision.azure_pricing import wait_for_selected_prices
from decision.excluded import excluded_sources
from decision.model import CitedRegion as CitedRegion
from decision.model import RenderedInteraction, Source, SourceSnapshot
from decision.retention import (
    TermsRegisterUnreadable, canonical_host, citation_metadata, classified_hosts,
    cite_only_origin_restrictive, is_cite_only_restrictive, is_classified,
    registered_source_hosts, cite_only_origin_status,
    record_origin_status, require_source_url,
)
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


class ExcludedSource(ValueError):
    """The requested source or a resolved origin is excluded."""


class UnclassifiedRedirectError(ValueError):
    """A request reached a host with no class in the private terms register, or the register
    could not be read (MODEL-509)."""

    def __init__(self, host: str, *, unreadable: bool = False) -> None:
        super().__init__("terms register unreadable" if unreadable
                         else f"redirect to unclassified host {host}")
        self.host = host
        self.unreadable = unreadable


REDIRECT_UNCLASSIFIED = "redirect_unclassified"
TERMS_REGISTER_UNREADABLE = "terms_register_unreadable"


def _refusal_error(stop: UnclassifiedRedirectError) -> str:
    return TERMS_REGISTER_UNREADABLE if stop.unreadable else f"{REDIRECT_UNCLASSIFIED}:{stop.host}"


def refusal_reason(result: Any) -> str | None:
    """Why a fetch was refused at the terms register (``redirect_unclassified:<host>`` or
    ``terms_register_unreadable``), or None when it was not refused for that."""
    error = (result if isinstance(result, str) else getattr(result, "error", None)) or ""
    if error == TERMS_REGISTER_UNREADABLE or error.startswith(REDIRECT_UNCLASSIFIED + ":"):
        return error
    return None


def unclassified_redirect_host(result: Any) -> str | None:
    """The host a fetch was refused at, or None (also None for an unreadable register)."""
    error = refusal_reason(result) or ""
    prefix = REDIRECT_UNCLASSIFIED + ":"
    return (error[len(prefix):] or None) if error.startswith(prefix) else None


def named_refusal(reason: str, source_id: str) -> str:
    """The reason with the source named: ``redirect_unclassified:<source_id>:<host>``."""
    if reason == TERMS_REGISTER_UNREADABLE:
        return reason
    return f"{REDIRECT_UNCLASSIFIED}:{source_id}:{reason.partition(':')[2]}"


def _require_classified_request(start: str | None, url: str, *, first: bool,
                                strict: bool = False) -> None:
    """Refuse, before the request, a host the terms register does not class.

    With no data directory nothing is refused. A redirect within the start host
    passes; every other host needs a class (the host or a parent domain), and so does
    the first request when its host is the host of a registered source. With an unreadable
    register (terms or sources) every other host is refused.

    ``strict`` (the rendered path, MODEL-565) drops both exemptions: every host, the first
    included and whether or not a registered source lives there, needs a class, and no
    data directory refuses every request.
    """
    try:
        classes = classified_hosts()
        unreadable = False
    except TermsRegisterUnreadable:
        classes, unreadable = frozenset(), True
    if classes is None:
        if not strict:
            return
        classes, unreadable = frozenset(), True
    try:
        host = canonical_host(url)
    except ValueError:
        host = None
    if strict:
        if not unreadable and is_classified(host, classes):
            return
        raise UnclassifiedRedirectError(host or "unparseable", unreadable=unreadable)
    if host is not None and not first and host == start:
        return
    if first:
        # Only a host a registered source lives on needs a class at the first request; any
        # other caller's first fetch (the release-signal feed, a drafter) is checked at its
        # hops only. The host decides, so a path, query or fragment cannot dodge it.
        try:
            registered = registered_source_hosts() or frozenset()
        except TermsRegisterUnreadable:
            registered, unreadable = None, True  # cannot tell: fail closed
        if registered is not None and not is_classified(host, registered):
            return
    if not unreadable and is_classified(host, classes):
        return
    raise UnclassifiedRedirectError(host or "unparseable", unreadable=unreadable)


def require_allowed_source_urls(url: str, resolved_urls: Iterable[str] = ()) -> None:
    rules = excluded_sources()
    if any(rules.url(origin) for origin in (url, *resolved_urls)):
        raise ExcludedSource("excluded source")


def get_source_response(
    client: httpx.Client, url: str, *,
    before_request: Callable[[str], None] | None = None, **kwargs: Any,
) -> httpx.Response:
    """Apply source admission before each HTTP request, including redirects."""
    import httpx

    history = []
    request = None
    try:
        start = canonical_host(url)
    except ValueError:
        start = None
    while True:
        require_allowed_source_urls(url)
        _require_classified_request(start, url, first=request is None)
        if before_request is not None:
            before_request(url)
        response = (client.get(url, follow_redirects=False, **kwargs) if request is None
                    else client.send(request, auth=None, follow_redirects=False))
        if not response.has_redirect_location:
            response.history = history
            return response
        if len(history) >= 20:
            raise httpx.TooManyRedirects("source redirect limit reached", request=response.request)
        history.append(response)
        request = response.next_request
        url = str(request.url)


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
        error = "no attempt"
        status: int | None = None
        delay = 0.0
        for attempt in range(self.retries + 1):
            if attempt:
                self.sleep(delay)
            delay = min(self.backoff * 2**attempt, self.max_backoff)
            status = None
            try:
                response = get_source_response(
                    self.client, url, headers=headers, timeout=self.timeout,
                    before_request=lambda target: self._wait_for_host(urlsplit(target).hostname or ""),
                )
            except ExcludedSource:
                return FetchResult("unreachable", error="excluded source")
            except UnclassifiedRedirectError as stop:
                return FetchResult("unreachable", error=_refusal_error(stop))
            except httpx.TooManyRedirects:
                return FetchResult("unreachable", error="source redirect limit reached")
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

RENDERED_POSTCONDITIONS: Mapping[str, RenderedPreparation] = {
    "azure-pricing": wait_for_selected_prices,
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
def _read_only_interactions(page: Any, prepare: RenderedInteractions, timeout: float):
    from playwright.sync_api import Error

    context = page.context
    other_pages = set(context.pages) - {page}
    opened_pages = {page}
    pending_navigations = []
    blocked = False

    def navigation_page(request: Any) -> Any:
        try:
            return request.frame.page
        except Error:
            return None

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
            # A popup's first request can arrive before Playwright creates its Page.
            if navigation and navigation_page(request) is None:
                pending_navigations.append(request)
            route.abort()
        else:
            route.fallback()

    def close_opened_page(opened_page: Any) -> None:
        opened_pages.add(opened_page)
        opened_page.close()

    # Context routes also intercept the first request of a new popup.
    context.route("**/*", read_only)
    context.on("page", close_opened_page)
    try:
        yield
    finally:
        try:
            deadline = time.monotonic() + timeout
            opened_pages.update(set(context.pages) - other_pages)
            while opened_pages or pending_navigations:
                while pending_navigations:
                    request = pending_navigations.pop()
                    target = navigation_page(request)
                    if target is None:
                        target = context.wait_for_event(
                            "page", predicate=lambda candidate: navigation_page(request) == candidate,
                            timeout=max(1.0, (deadline - time.monotonic()) * 1000))
                    if target not in other_pages:
                        opened_pages.add(target)
                if opened_pages:
                    opened_pages.pop().close()
        except Error:
            context.close()
            raise
        finally:
            try:
                context.unroute("**/*", read_only)
            finally:
                context.remove_listener("page", close_opened_page)
    if blocked:
        raise RenderedInteractionError("blocked interaction request")


_SAFE_CONTROL = r"""(node, action) => {
    const tag = node.tagName.toLowerCase();
    const role = node.getAttribute('role');
    const labels = [node.getAttribute('aria-label'), node.title,
                    node.innerText, node.textContent, node.value,
                    ...Array.from(node.querySelectorAll('img[alt]'), image => image.alt)]
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

_TRANSACTION_NAME = re.compile(
    r"\b(log.?in|sign.?in|sign.?up|register|submit|buy|purchase|checkout|subscribe)\b", re.I)
_CONSENT_NAME = re.compile(r"\b(cookie|consent|accept|agree|allow all)\b", re.I)
_REJECT_NAME = re.compile(
    r"^(reject all( cookies)?|decline( all)?|deny all|only necessary cookies)$", re.I)

_REGION_CONTAINS_TEXT = """({selector, text}) => {
    const nodes = document.querySelectorAll(selector);
    if (nodes.length !== 1) return false;
    const node = nodes[0];
    if (node.tagName === 'SELECT')
        return Array.from(node.selectedOptions).some(option => option.label === text);
    return node.innerText.includes(text);
}"""


@dataclass(frozen=True)
class RenderedInteractions:
    """Execute validated UI data within one deadline; never capture a failed recipe."""

    recipes: tuple[tuple[RenderedInteraction, ...], ...]
    postconditions: tuple[RenderedPreparation, ...] = ()

    def __call__(self, page: Any, timeout: float) -> None:
        from playwright.sync_api import Error, expect

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
                # Playwright includes external labels and image alt text in the computed name.
                expect(target).not_to_have_accessible_name(_TRANSACTION_NAME, timeout=remaining_ms())
                if step.action == "reject_consent":
                    expect(target).to_have_accessible_name(_REJECT_NAME, timeout=remaining_ms())
                else:
                    expect(target).not_to_have_accessible_name(_CONSENT_NAME, timeout=remaining_ms())
                if step.action == "select_option":
                    target.select_option(value=step.value, timeout=remaining_ms())
                else:
                    target.click(timeout=remaining_ms())
            for postcondition in self.postconditions:
                postcondition(page, remaining_ms() / 1000)
            remaining_ms()
        except AssertionError as exc:
            raise RenderedInteractionError("unsafe interaction control") from exc
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
        urls = {canonical_url(str(sources[sid].url)) for sid in ids if sid in sources}
        postconditions = tuple(check for sid, check in RENDERED_POSTCONDITIONS.items()
                               if sid in sources and canonical_url(str(sources[sid].url)) in urls)
        return RenderedInteractions(recipes, postconditions)
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


_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
MAX_RENDERED_REDIRECTS = 20


def _redirect_target(url: str, response: Any) -> str | None:
    """The absolute target of a redirect response, or None when it is not one."""
    from urllib.parse import urljoin

    location = response.headers.get("location") if response.status in _REDIRECT_STATUSES else None
    return urljoin(url, location) if location else None


def _ambiguous_url(url: str) -> str | None:
    """Why a URL could be read two ways, or None (MODEL-565).

    The class check must see the host the browser will ask, so a URL any parser could
    read differently is refused before its host is looked up: userinfo, a backslash, a
    control or whitespace character, a percent sign in the host, a host that is not
    already lower-case ASCII (IDNA or case would change it), a trailing dot or an
    empty label.
    """
    if any(char.isspace() or ord(char) < 0x21 or ord(char) == 0x7F or char == "\\"
           for char in url):
        return "ambiguous URL"
    try:
        parts = urlsplit(url)
        port_free = parts.netloc.rpartition(":")[0] if parts.port else parts.netloc
    except ValueError:
        return "ambiguous URL"
    host = port_free.removesuffix(":")
    if (parts.scheme not in {"http", "https"} or "@" in parts.netloc or not host
            or "%" in host or host != host.lower() or not host.isascii()
            or host.endswith(".") or ".." in host or host.startswith(".")):
        return "ambiguous URL"
    try:
        if host.encode("idna").decode("ascii") != host or canonical_host(url) != host:
            return "ambiguous URL"
    except (UnicodeError, ValueError):
        return "ambiguous URL"
    return None


def _stop_navigation(route: Any) -> None:
    """End a main-frame request with an empty document. Nothing is sent to its host, and the
    fetcher never reads the document: it refuses the fetch or navigates on. (Chromium can hang
    closing a page whose main frame was aborted twice, so it is not aborted.)"""
    route.fulfill(status=200, body="", content_type="text/html")


class _RenderedRequestGuard:
    """Admit each request a rendered page makes, and each redirect hop, before it is sent.

    Chromium follows a redirect without calling a route handler, so an admitted request is
    sent by Playwright with redirects off (MODEL-565). Each check reads the URL as the
    browser gives it (``route.request.url``). A main-frame redirect is stopped and its
    target handed back to ``RenderedFetcher.fetch``, which navigates to it as a new
    request, checked here like the first. Any other request (subresources, frames, popups)
    that answers with a redirect is aborted: no URL rebuilt here is ever sent. A request to an
    excluded host or one the terms register does not class is never sent: the rule is the
    plain path's (``_require_classified_request``). On the main frame that refuses the fetch.
    """

    def __init__(self, page: Any, start: str | None, timeout: float) -> None:
        self.page = page
        self.start = start
        self.timeout_ms = timeout * 1000
        self.hops: list[str] = []  # main-frame URLs requested, in order
        self.pending: str | None = None  # a main-frame redirect target, not yet requested
        self.refused: str | None = None  # why a main-frame request was not sent

    def refusal(self, url: str) -> str | None:
        if (ambiguous := _ambiguous_url(url)) is not None:
            return ambiguous
        try:
            require_allowed_source_urls(url)
            _require_classified_request(self.start, url, first=False, strict=True)
        except ExcludedSource:
            return "excluded source"
        except UnclassifiedRedirectError as stop:
            return _refusal_error(stop)
        return None

    def retaining(self) -> bool:
        """Whether the capture may be kept as bytes: no main-frame hop is cite-only. Before
        the first hop it counts as kept, the stricter reading."""
        return not self.hops or not cite_only_origin_restrictive(self.hops[0], self.hops[1:])

    def subresource_refusal(self, url: str) -> str | None:
        """A page whose bytes are kept takes nothing from a cite-only host, so no text from
        one can reach its capture (MODEL-565). A cite-only page keeps no bytes at all."""
        refused = self.refusal(url)
        if refused is None and self.retaining() and is_cite_only_restrictive(url):
            return "cite-only subresource of a retained page"
        return refused

    def _main_frame(self, request: Any) -> bool:
        from playwright.sync_api import Error

        try:
            frame = request.frame
            return (request.is_navigation_request() and frame.parent_frame is None
                    and frame.page == self.page)
        except Error:  # a popup's first request can come before its page exists
            return False

    def __call__(self, route: Any) -> None:
        from playwright.sync_api import Error

        request = route.request
        url = request.url
        if urlsplit(url).scheme not in {"http", "https"}:
            route.fallback()  # data:, blob: and the like reach no host
            return
        main = self._main_frame(request)
        check = self.refusal if main else self.subresource_refusal
        try:
            if (refused := check(url)) is not None:
                if main:
                    self.refused = self.refused or refused
                    _stop_navigation(route)
                else:
                    route.abort()
                return
            if main:
                self.hops.append(url)
            response = route.fetch(max_redirects=0, timeout=self.timeout_ms)
            target = _redirect_target(url, response)
            if target is None:
                route.fulfill(response=response)
            elif main and (refused := _ambiguous_url(target)) is None:
                # The browser asks for the target as a new navigation; this handler then
                # checks the URL as the browser parsed it.
                self.pending = target
                _stop_navigation(route)
            elif main:
                self.refused = self.refused or refused
                _stop_navigation(route)
            else:
                route.abort()
        except Error:
            try:
                route.abort()
            except Error:
                pass

    def web_socket(self, socket: Any) -> None:
        # A refused socket is never connected: Playwright then answers it itself and nothing
        # reaches the host. (Closing it from the handler can hang the dispatcher.)
        url = re.sub(r"^ws", "http", socket.url)
        if self.subresource_refusal(url) is None:
            socket.connect_to_server()


#: Runs in every frame before the page's own scripts: no peer connection can be made.
_NO_WEBRTC = """for (const name of ['RTCPeerConnection', 'webkitRTCPeerConnection',
                    'RTCDataChannel', 'RTCIceCandidate', 'RTCSessionDescription']) {
    try { Object.defineProperty(globalThis, name, {value: undefined, writable: false,
                                                   configurable: false}); } catch (e) {}
}"""


class RenderedFetcher:
    """Opt-in local Chromium fetches, sharing one browser for a context-managed run.

    Playwright is imported only when entering the context. Network idle is best
    effort: pages with persistent connections still yield their rendered HTML.
    An optional preparation runs before capture, within one timeout budget.
    Registry recipe failures return no HTML. Legacy preparations retain their
    partial HTML with an error for the caller to report. Every request and redirect hop,
    from any page of the context, is admitted before it is sent (``_RenderedRequestGuard``),
    and with no terms register named nothing is fetched (MODEL-565).
    """

    def __init__(self, *, timeout: float = 20.0, idle_timeout: float = 5.0) -> None:
        self.timeout = timeout
        self.idle_timeout = idle_timeout
        self._guard: _RenderedRequestGuard | None = None

    def _route(self, route: Any) -> None:
        # One route for the context's whole life, so popups are covered too. Outside a
        # fetch no page has a reason to ask anything: refuse.
        if self._guard is None:
            route.abort()
        else:
            self._guard(route)

    def _web_socket(self, socket: Any) -> None:
        if self._guard is not None:  # outside a fetch a socket is never connected
            self._guard.web_socket(socket)

    def __enter__(self) -> RenderedFetcher:
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        try:
            # Keep Playwright's sandbox default. CI isolation comes from the
            # separate read-only render job, which has no repository write token.
            # DNS prefetch and preconnect reach a host without a request, so no route sees
            # them (MODEL-565): switch both off. A host the guard refuses then gets neither a
            # request nor, as far as these switches reach, a lookup or a connection.
            # WebRTC can send STUN or TURN traffic that no route sees: UDP that is not
            # proxied is refused, and the page never gets RTCPeerConnection (init script).
            self._browser = self._playwright.chromium.launch(headless=True, args=[
                "--dns-prefetch-disable",
                "--disable-features=PreconnectToSearch,NetworkPrediction,"
                "LoadingPredictorUseLocalPredictions,SpeculationRulesPrefetchFuture",
                "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
                "--webrtc-ip-handling-policy=disable_non_proxied_udp",
            ])
            self._context = self._browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                service_workers="block",
            )
            self._context.add_init_script(_NO_WEBRTC)
            # Registered first, so a recipe's read-only route (added later) runs before it.
            self._context.route("**/*", self._route)
            self._context.route_web_socket("**/*", self._web_socket)
        except Exception:
            self._playwright.stop()
            raise
        return self

    def __exit__(self, *exc: object) -> None:
        try:
            self._browser.close()
        finally:
            self._playwright.stop()

    def _guarded_goto(self, page: Any, url: str, guard: _RenderedRequestGuard) -> Any:
        """Navigate, following main-frame redirects one checked request at a time."""
        from playwright.sync_api import Error

        deadline = None  # set at the first redirect: the hops share one timeout
        for _ in range(MAX_RENDERED_REDIRECTS + 1):
            guard.pending = None
            timeout = (self.timeout * 1000 if deadline is None
                       else max(1.0, (deadline - time.monotonic()) * 1000))
            try:
                response = page.goto(url, wait_until="load", timeout=timeout)
            except Error:
                if guard.refused is None and guard.pending is None:
                    raise
                response = None
            if guard.refused is not None or guard.pending is None:
                return response
            if deadline is None:
                deadline = time.monotonic() + self.timeout
            url = guard.pending
        raise Error("source redirect limit reached")

    def fetch(self, url: str, *, prepare: RenderedPreparation | None = None) -> FetchResult:
        from playwright.sync_api import Error, TimeoutError

        page = None
        try:
            require_allowed_source_urls(url)
        except ExcludedSource:
            return FetchResult("unreachable", error="excluded source")
        if _ambiguous_url(url) is not None:
            return FetchResult("unreachable", error="ambiguous URL")
        try:
            # Every host, the first included, needs a class; no register refuses (MODEL-565).
            _require_classified_request(None, url, first=True, strict=True)
        except UnclassifiedRedirectError as stop:
            return FetchResult("unreachable", error=_refusal_error(stop))
        context = self._context
        before = list(getattr(context, "pages", ()))
        try:
            page = context.new_page()
            guard = self._guard = _RenderedRequestGuard(page, canonical_host(url), self.timeout)
            response = self._guarded_goto(page, url, guard)
            if guard.refused is not None:
                return FetchResult("unreachable", error=guard.refused)
            if response is None:
                return FetchResult("unreachable", error="no HTTP response")
            if not 200 <= response.status < 300:
                return FetchResult("unreachable", response.status,
                                   error=f"HTTP {response.status}")
            try:
                page.wait_for_load_state("networkidle", timeout=self.idle_timeout * 1000)
            except TimeoutError:
                pass
            interactions = (_read_only_interactions(page, prepare, self.timeout)
                            if isinstance(prepare, RenderedInteractions) else nullcontext())
            with interactions:
                preparation_error = None
                if prepare is not None:
                    try:
                        prepare(page, self.timeout)
                    except Error as exc:
                        preparation_error = f"rendered preparation failed: {exc}"
                # Serialise first, then read where the page is: a navigation between the two
                # reads, or a final URL the register would not admit, refuses the capture.
                seen = (str(page.url), len(guard.hops))
                body = page.content().encode("utf-8")
                final = str(page.url)
                if (final, len(guard.hops)) != seen:
                    return FetchResult("unreachable", error="navigation during capture")
                if guard.refused is not None:
                    return FetchResult("unreachable", error=guard.refused)
                if guard.pending is not None:
                    return FetchResult("unreachable", error="redirect after load not followed")
                if (refused := guard.refusal(final)) is not None:
                    return FetchResult("unreachable", error=refused)
                if guard.retaining() and is_cite_only_restrictive(final):
                    return FetchResult("unreachable", error="final URL is cite-only")
                if guard.hops:
                    # Every main-frame request in order, repeats kept: each was admitted
                    # before it was sent.
                    resolved = tuple(guard.hops)
                else:  # a page that was not routed (a test double)
                    redirects = []
                    request = response.request
                    while request is not None:
                        redirects.append(str(request.url))
                        request = request.redirected_from
                    resolved = tuple(dict.fromkeys((*reversed(redirects), str(response.url),
                                                    str(page.url))))
                return FetchResult("ok", response.status, body=body,
                                   content_type="text/html", charset="utf-8",
                                   error=preparation_error, resolved_urls=resolved,
                                   retrieved_at=datetime.now(UTC))
        except RenderedInteractionError as exc:
            return FetchResult("unreachable", response.status, error=str(exc))
        except Error as exc:
            if self._guard is not None and self._guard.refused is not None:
                return FetchResult("unreachable", error=self._guard.refused)
            return FetchResult("unreachable", error=str(exc))
        finally:
            try:
                if page is not None:
                    page.close()
                # Then every page the fetch opened, until none is left: closing one popup
                # can open another. Only after that is the guard lifted; outside a fetch
                # the context's route refuses every request.
                for _ in range(100):
                    opened = [other for other in getattr(context, "pages", ())
                              if other not in before]
                    if not opened:
                        break
                    for other in opened:
                        other.close()
                else:
                    context.close()
            finally:
                self._guard = None


# --- shell pages ---------------------------------------------------------------------------------

SHELL_PAGE = "shell_page"
#: Fewest characters of normalised text an HTML page must have to be bound (MODEL-519). The
#: smallest recorded real HTML page has 7,547; a shell is empty or a few words ("Loading",
#: "Enable JavaScript"), so 40 catches only the empty. The same-bytes rule catches shells that
#: keep page chrome (the DeepSeek pair has 2,085 characters of text). Text and JSON files can
#: be short and legitimate, so only an empty body refuses them.
MIN_PAGE_TEXT_CHARS = 40


class ShellPageError(ValueError):
    """The fetched bytes are a shell, not the page: nothing is cited or verified from them."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class ShellCheck:
    """How ``CopyStore.put`` and ``record_citation`` check a fetched page (MODEL-519).

    ``normaliser`` names the source's recipe; ``alias_urls`` are the URLs the registry marks
    as an alias or redirect of this one (they may share its bytes); ``text`` is the
    already-normalised text, when the caller has it.
    """

    normaliser: str = "html-default"
    alias_urls: tuple[str, ...] = ()
    text: str | None = None


def shell_alias_urls(source: Source, sources: Iterable[Source]) -> tuple[str, ...]:
    """URLs of the sources ``source`` is an alias of, or that are aliases of it."""
    return tuple(canonical_url(str(other.url)) for other in sources
                 if other.id != source.id
                 and (source.alias_of == other.id or other.alias_of == source.id))


def shell_refusal(reason: str | None, source_id: str) -> str | None:
    """The reason with the source named: ``shell_page:<source id>:<detail>``."""
    if reason is None:
        return None
    return f"{SHELL_PAGE}:{source_id}:{reason.partition(':')[2]}"


def shell_page_reason(error: str | None) -> str | None:
    return error if error and error.startswith(SHELL_PAGE + ":") else None


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
            resolved_urls: Iterable[str] = (), shell_check: ShellCheck | None = None) -> str:
        source_url = require_source_url(source_url)
        resolved_urls = tuple(resolved_urls)
        cite_only = cite_only_origin_status(source_url, resolved_urls)
        if cite_only is None:
            # Neither bytes nor a citation record for a malformed origin (MODEL-420).
            raise ValueError("retaining source bytes requires well-formed HTTP URLs")
        ref = fingerprint_bytes(body)
        if shell_check is not None:
            # Refuse a shell before anything is kept (MODEL-519).
            self.check_shell(body, ref, source_url, resolved_urls, shell_check)
        if cite_only or cite_only_origin_restrictive(source_url, resolved_urls):
            # Restrictive reading too: a host the private register marks forbids
            # keeps the citation and hash, never the bytes (MODEL-510).
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

    def _seen_path(self, ref: str) -> Path:
        return self.path(ref).with_suffix(".urls.json")

    def _seen(self, ref: str) -> list[dict]:
        """Every URL this hash was recorded for: the URL list this check keeps, and the
        per-(hash, URL) citation records (MODEL-513)."""
        try:
            data = json.loads(self._seen_path(ref).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = []
        rows = [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []
        try:
            records = self.citations(ref)
        except ValueError:
            records = []
        known = {row.get("url") for row in rows}
        for record in records:
            if isinstance(record.get("url"), str) and record["url"] not in known:
                known.add(record["url"])
                rows.append({"url": canonical_url(record["url"]),
                             "resolved": [str(u) for u in record.get("resolved_urls", ())]})
        return rows

    def _flag_path(self, ref: str) -> Path:
        return self.path(ref).with_suffix(".shell.json")

    def _flagged(self, ref: str) -> dict[str, str]:
        try:
            data = json.loads(self._flag_path(ref).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return {k: v for k, v in data.items() if isinstance(v, str)} if isinstance(data, dict) else {}

    def _write_json(self, target: Path, value: Any) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(value, out, sort_keys=True)
        os.replace(tmp, target)

    def check_shell(self, body: bytes | None, ref: str, source_url: str,
                     resolved_urls: Iterable[str], check: ShellCheck) -> None:
        """Raise ShellPageError when the bytes are empty or thin, or already recorded for a
        different URL on the same host (HTML pages only; raw text and JSON files can
        legitimately repeat, as a licence file does). Records the URL on success."""
        url = canonical_url(source_url)
        resolved = {canonical_url(str(u)) for u in resolved_urls}
        rules = NORMALISERS.get(check.normaliser, NORMALISERS["html-default"])
        if body is not None:
            if not body.strip():
                raise ShellPageError(f"{SHELL_PAGE}:empty_body")
            if rules.content == "html":
                text = check.text
                if text is None:
                    try:
                        text = normalise_document(body, rules).text
                    except UnsupportedContentError:
                        text = None
                if text is not None and len(text.strip()) < MIN_PAGE_TEXT_CHARS:
                    raise ShellPageError(
                        f"{SHELL_PAGE}:text_below_{MIN_PAGE_TEXT_CHARS}_chars")
        if rules.content == "html":
            try:
                host = canonical_host(url)
            except ValueError:
                host = None
            exempt = {canonical_url(u) for u in check.alias_urls} | resolved
            # A URL already caught in a collision keeps refusing, whichever came first.
            partner = self._flagged(ref).get(url)
            if partner is not None and partner not in exempt:
                raise ShellPageError(f"{SHELL_PAGE}:same_bytes_as:{partner}")
            for row in self._seen(ref):
                other = row.get("url")
                if not isinstance(other, str) or other == url or other in exempt:
                    continue
                if url in {canonical_url(str(u)) for u in row.get("resolved", ())}:
                    continue
                try:
                    same_host = canonical_host(other) == host
                except ValueError:
                    same_host = False
                if same_host:
                    # Neither URL is the page: refuse both, now and on every later read.
                    flagged = self._flagged(ref)
                    flagged[url], flagged[other] = other, url
                    self._write_json(self._flag_path(ref), flagged)
                    raise ShellPageError(f"{SHELL_PAGE}:same_bytes_as:{other}")
        rows = [r for r in self._seen(ref)]
        if not any(r.get("url") == url for r in rows):
            rows.append({"url": url, "resolved": sorted(resolved)})
            self._write_json(self._seen_path(ref), rows)

    def _alias_path(self, ref: str, url: str) -> Path:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        base = self.path(ref)
        return base.with_name(f"{base.name}.citation.{key}.json")

    def record_citation(self, ref: str, *, source_url: str,
                        retrieved_at: datetime | None = None, resolved_urls=(),
                        shell_check: ShellCheck | None = None) -> None:
        """Record that ``ref`` was fetched from ``source_url`` (MODEL-513).

        One record per (hash, URL): the same bytes served under two registered
        URLs keep both. ``<digest>.citation.json`` still holds the latest write,
        so a reader that asks only by hash sees what it always saw.
        """
        if shell_check is not None:
            # No bytes here: only the same-bytes rule can apply (MODEL-519).
            self.check_shell(None, ref, require_source_url(source_url), resolved_urls,
                             shell_check)
        metadata = citation_metadata(source_url, ref, retrieved_at=retrieved_at or datetime.now(UTC),
                                     resolved_urls=resolved_urls)
        for target in (self._alias_path(ref, metadata["url"]),
                       self.path(ref).with_suffix(".citation.json")):
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(dir=target.parent, prefix=".tmp-")
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(metadata, output, sort_keys=True)
            os.replace(temporary, target)

    @staticmethod
    def _read_record(target: Path, ref: str) -> dict:
        if not target.is_file():
            raise ValueError("citation record is not a readable file")
        try:
            metadata = json.loads(target.read_text(encoding="utf-8"))
        except OSError:
            raise ValueError("citation record is not a readable file") from None
        if not isinstance(metadata, dict):
            raise ValueError("citation record is not a JSON object")
        if metadata.get("snapshot_ref") != ref:
            raise ValueError("citation metadata does not match its hash")
        return metadata

    def citation(self, ref: str, *, url: str | None = None) -> dict | None:
        """The citation record for ``ref``, or None when no entry exists at its path.

        An entry that exists but is not a readable regular file holding a JSON
        object (a directory, a dangling symlink, bad JSON) raises ValueError:
        an unreadable record is never read as "no citation" (MODEL-420).
        With ``url``, only the record for that (hash, URL) pair.
        """
        if url is not None:
            return next((r for r in self.citations(ref) if r.get("url") == url), None)
        target = self.path(ref).with_suffix(".citation.json")
        if not os.path.lexists(target):
            return None
        return self._read_record(target, ref)

    def citations(self, ref: str) -> list[dict]:
        """Every citation record for ``ref``: one per URL, the latest write first."""
        latest = self.citation(ref)
        records = [] if latest is None else [latest]
        base = self.path(ref)
        if base.parent.is_dir():
            for target in sorted(base.parent.glob(f"{base.name}.citation.*.json")):
                record = self._read_record(target, ref)
                if all(record.get("url") != seen.get("url") for seen in records):
                    records.append(record)
        return records

    def get(self, ref: str, *, source_url: str | None = None) -> bytes:
        if self.citation(ref) is not None or source_url is not None and cite_only_origin_restrictive(source_url):
            raise ValueError("cite-only source has no readable retained copy")
        body = self.path(ref).read_bytes()
        if fingerprint_bytes(body) != ref:
            raise ValueError(f"retained copy {ref} does not match its hash")
        return body

    def has(self, ref: str) -> bool:
        try:
            if self.citation(ref) is not None:
                return False
        except ValueError:
            return False  # an unreadable citation record still withholds the copy
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


@dataclass(frozen=True)
class RedirectRefused:
    """An alert event: a fetch was refused at the terms register (MODEL-509)."""

    source_id: str
    reason: str
    url: str
    detected_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {"event": "redirect_unclassified", "source_id": self.source_id,
                "reason": self.reason, "url": self.url,
                "detected_at": self.detected_at.isoformat()}


@dataclass(frozen=True)
class ShellPageRefused:
    """An alert event: fetched bytes were a shell page and were not cited (MODEL-519)."""

    source_id: str
    reason: str
    url: str
    detected_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {"event": SHELL_PAGE, "source_id": self.source_id,
                "reason": self.reason, "url": self.url,
                "detected_at": self.detected_at.isoformat()}


@dataclass
class RecheckReport:
    regions: list[RegionResult] = field(default_factory=list)
    #: Facts and evidence citing a changed region: re-extract and re-verify these.
    requeue: list[str] = field(default_factory=list)
    #: Facts and evidence whose every cited region is unchanged.
    reconfirmed: list[str] = field(default_factory=list)
    #: Facts and evidence on a source past its unreachable grace period.
    quarantine: list[str] = field(default_factory=list)
    alerts: list[GovernanceChange | RedirectRefused | ShellPageRefused] = field(
        default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)
    #: Every source's state after this run; persist these for the next one.
    states: dict[str, SourceState] = field(default_factory=dict)
    #: The final fetch attempt for each source, including HTTP status and errors.
    fetches: dict[str, FetchResult] = field(default_factory=dict)

    @property
    def redirect_unclassified(self) -> int:
        """Sources refused at the terms register this run; above 0 the job ends red."""
        return sum(isinstance(alert, RedirectRefused) for alert in self.alerts)

    @property
    def shell_page(self) -> int:
        """Sources whose bytes were a shell this run (MODEL-519); above 0 the job ends red."""
        return sum(isinstance(alert, ShellPageRefused) for alert in self.alerts)


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
        report.states[source.id] = _check_one(source, state, fetcher, store, now, grace, report,
                                              shell_alias_urls(source, sources))

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
                        current_copy_ref=(
                            fingerprint_bytes(report.fetches[result.source_id].body)
                            if report.fetches[result.source_id].outcome == "ok"
                            else current.copy_ref
                        ),
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
    alias_urls: tuple[str, ...] = (),
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
    if (refused := refusal_reason(result)) is not None:
        # Refused before the request (MODEL-509): no bytes, no failure counted. The
        # refusal is its own alert, not a quiet skip.
        named = named_refusal(refused, source.id)
        report.skipped.append(Skipped(source.id, named))
        report.alerts.append(RedirectRefused(source.id, named, str(source.url), now))
        return replace(state, last_attempt_at=now)
    old = previous.region_fingerprints if previous else {}
    shell = ShellCheck(source.normaliser, alias_urls)

    def refuse_shell(stop: ShellPageError) -> SourceState:
        # Nothing is bound to a shell (MODEL-519): no bytes, no region result, no failure
        # counted; its own alert.
        named = shell_refusal(stop.reason, source.id)
        report.skipped.append(Skipped(source.id, named))
        report.alerts.append(ShellPageRefused(source.id, named, str(source.url), now))
        return replace(state, last_attempt_at=now)

    try:
        previous_citation = None
        if previous:
            previous_citation = (store.citation(previous.copy_ref, url=str(source.url))
                                 or store.citation(previous.copy_ref))
        # Every origin of the previous record is validated before its presence
        # grants the cite-only path (MODEL-420).
        if previous_citation is not None and record_origin_status(previous_citation) is None:
            raise ValueError("invalid previous citation record")
        resolved_urls = tuple(dict.fromkeys((*result.resolved_urls,
                              *((previous_citation or {}).get("resolved_urls", ())))))
        cite_only = cite_only_origin_status(source.url, resolved_urls)
        if cite_only is None:
            raise ValueError("invalid redirect URL")
    except (TypeError, ValueError):
        # Fail closed for this source only (MODEL-420): keep nothing, change no
        # snapshot or record, and go on to the next source.
        report.skipped.append(Skipped(source.id, "invalid_citation_metadata"))
        return replace(state, last_attempt_at=now)
    if (cite_only or previous_citation is not None) \
            and result.outcome in {"ok", "not_modified"}:
        if result.outcome == "not_modified" and previous is None:
            return replace(state, last_attempt_at=now)
        try:
            ref = (previous.copy_ref if result.outcome == "not_modified" else
                   store.put(result.body, source_url=str(source.url), retrieved_at=now,
                             resolved_urls=resolved_urls, shell_check=shell))
            store.record_citation(ref, source_url=str(source.url), retrieved_at=now,
                                  resolved_urls=resolved_urls, shell_check=shell)
        except ShellPageError as stop:
            return refuse_shell(stop)
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
        try:
            # A 304 has no bytes, but a URL flagged as a shell stays flagged (MODEL-519).
            store.check_shell(None, previous.copy_ref, str(source.url), result.resolved_urls, shell)
        except ShellPageError as stop:
            return refuse_shell(stop)
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
    if rules.content == "pdf":
        from decision.pdf_templates import retention_approved

        if not retention_approved(str(source.url), fingerprint_bytes(result.body)):
            if previous is not None and previous.copy_ref != fingerprint_bytes(result.body):
                for region in source.cited_regions:
                    report.regions.append(RegionResult(
                        source.id, region.id, RegionStatus.CHANGED,
                        old.get(region.id), None, "pdf_unapproved_revision",
                    ))
            report.skipped.append(Skipped(source.id, "pdf_retention_not_approved"))
            return replace(state, last_attempt_at=now)
    try:
        if "pdf" in result.content_type.lower() and rules.content != "pdf":
            raise UnsupportedContentError("pdf")
        doc = normalise_document(result.body, rules, charset=result.charset)
    except UnsupportedContentError as exc:
        report.skipped.append(Skipped(source.id, f"unsupported_content:{exc.kind}"))
        return replace(state, last_attempt_at=now)

    try:
        copy_ref = store.put(result.body, source_url=str(source.url), retrieved_at=now,
                             resolved_urls=result.resolved_urls,
                             shell_check=replace(shell, text=doc.text))
    except ShellPageError as stop:
        return refuse_shell(stop)
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
        copy_ref=copy_ref,
        etag=result.etag,
        last_modified=result.last_modified,
    )
    return SourceState(source.id, snapshot, 0, False, now)


def configured_copy_store() -> CopyStore | None:
    """The fetcher's copy store when ``MODELSPEC_SOURCE_CACHE`` names it, else ``None``: the
    one configuration the snapshot build and the site loader share, so a build never depends
    on an unconfigured home-directory cache and both read citation records alike."""
    return CopyStore() if os.environ.get("MODELSPEC_SOURCE_CACHE") else None
