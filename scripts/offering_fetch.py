"""Staged first-party price reads with opt-in, durably bounded paid fallback."""

from __future__ import annotations

import fcntl
import json
import os
import re
import stat
import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from decision.firecrawl import FirecrawlFetcher, firecrawl_allowed
from decision.normalise import canonical_url
from decision.retention import cite_only_origin_status, is_cite_only_restrictive, redirect_urls
from decision.sources import Fetcher, FetchResult, RenderedFetcher, fingerprint_bytes, rendered_preparation
from scripts.admission_drafter import SourceBlockedError, source_block, source_fetch_block

RUN_LIMIT = 5
MONTHLY_LIMIT = 100
MONTH = re.compile(r"\d{4}-(?:0[1-9]|1[0-2])\Z")


def _refuse(reason: str) -> FetchResult:
    return FetchResult("unreachable", error=reason)


def _safe_result(url: str, result: FetchResult, lab: str, terms: dict) -> FetchResult:
    try:
        origins = redirect_urls(result.resolved_urls)
    except ValueError:
        return _refuse("malformed source redirect metadata")
    for origin in (url, *origins):
        if reason := source_block(origin, lab, terms):
            return _refuse(reason)
    cited = cite_only_origin_status(url, origins)
    if cited is None:
        return _refuse("malformed source or redirect URL")
    if cited:
        return replace(
            result, body=b"", error=None,
            snapshot_ref=(fingerprint_bytes(result.body) if result.body else result.snapshot_ref),
            retrieved_at=result.retrieved_at or datetime.now(UTC),
        )
    return result


class OfferingHTTPFetcher(Fetcher):
    """Read cite-only hosts transiently and enforce ownership before every redirect."""

    def __init__(self, client, *, lab: str, terms: dict, **kwargs):
        super().__init__(client, **kwargs)
        self.lab, self.terms = lab, terms

        def guard(request):
            if reason := source_block(str(request.url), lab, terms):
                raise SourceBlockedError(reason)

        client.event_hooks["request"].append(guard)

    def fetch(self, url: str, **kwargs) -> FetchResult:
        try:
            result = super().fetch(url, **kwargs)
        except SourceBlockedError as error:
            return _refuse(str(error))
        return _safe_result(url, result, self.lab, self.terms)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate ledger field")
        result[key] = value
    return result


def _read_ledger(path: Path, month: str) -> dict:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "r", encoding="utf-8") as source:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 64 * 1024:
            raise ValueError("unsafe ledger file")
        ledger = json.load(source, object_pairs_hook=_unique_object)
    if (not isinstance(ledger, dict) or set(ledger) != {"schema_version", "months"}
            or type(ledger["schema_version"]) is not int or ledger["schema_version"] != 1
            or not isinstance(ledger["months"], dict) or month not in ledger["months"]
            or any(not MONTH.fullmatch(key) or type(value) is not int or value < 0
                   for key, value in ledger["months"].items())):
        raise ValueError("invalid or unrestored monthly ledger")
    return ledger


def _write_ledger(path: Path, ledger: dict) -> None:
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(ledger, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


class OfferingFetcher:
    """The caller verifies each stage before requesting the next one.

    ``ledger`` opts into paid reads. It must be a restored JSON file containing
    ``schema_version: 1`` and ``months: {YYYY-MM: credits_reserved}``, including
    the current UTC month. Missing or unreadable accounting refuses paid work.
    A reservation is durable before a request and is never refunded on failure.
    ``renderer=False`` disables Chromium for injected offline transports.
    """

    def __init__(self, primary, *, lab: str, terms: dict, sources=None,
                 ledger: Path | None = None, month: str | None = None,
                 renderer=None, firecrawl_factory=FirecrawlFetcher):
        if month is not None and (not isinstance(month, str) or not MONTH.fullmatch(month)):
            raise ValueError("offering fallback month must be YYYY-MM")
        self.primary, self.lab, self.terms = primary, lab, terms
        self.sources = sources or {}
        self.ledger = Path(ledger) if ledger is not None else None
        self.month = month
        self.renderer = renderer
        self.firecrawl_factory = firecrawl_factory
        self.credits_spent = 0
        self._owns_renderer = False
        self._direct_urls: set[str] = set()
        self._rendered_urls: set[str] = set()
        self._paid_urls: set[str] = set()
        self._restricted_urls: set[str] = set()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if self._owns_renderer:
            self._owns_renderer = False
            self.renderer.__exit__(None, None, None)
            self.renderer = None

    def _result(self, url: str, result: FetchResult) -> FetchResult:
        result = _safe_result(url, result, self.lab, self.terms)
        if cite_only_origin_status(url, result.resolved_urls):
            self._restricted_urls.add(url)
        return result

    def fetch(self, url: str) -> FetchResult:
        if reason := source_block(url, self.lab, self.terms):
            return _refuse(reason)
        self._direct_urls.add(url)
        try:
            return self._result(url, self.primary.fetch(url))
        except SourceBlockedError as error:
            return _refuse(str(error))

    def _fallback_block(self, url: str) -> str | None:
        if reason := source_fetch_block(url, self.lab, self.terms):
            return reason
        if url in self._restricted_urls or is_cite_only_restrictive(url):
            return "cite-only source: browser and paid fallback are disabled"
        return None

    def _browser_guard(self, route):
        request = route.request
        if (is_cite_only_restrictive(request.url)
                or source_fetch_block(request.url, self.lab, self.terms)
                or request.method not in {"GET", "HEAD"}):
            route.abort()
            return
        # Chromium follows redirected requests without calling the route again.
        # Never hand it a redirect to a host whose bytes may not be retained.
        response = None
        try:
            response = route.fetch(max_redirects=0, timeout=self.renderer.timeout * 1000)
            if 300 <= response.status < 400:
                route.abort()
            else:
                route.fulfill(response=response)
        except Exception:
            route.abort()
        finally:
            if response is not None:
                response.dispose()

    def render(self, url: str) -> FetchResult:
        if reason := self._fallback_block(url):
            return _refuse(reason)
        if url not in self._direct_urls:
            return _refuse("direct source read must precede Chromium")
        self._rendered_urls.add(url)
        if self.renderer is False:
            return _refuse("local Chromium is disabled")
        if self.renderer is None:
            try:
                self.renderer = RenderedFetcher().__enter__()
                self._owns_renderer = True
                self.renderer._context.route("**/*", self._browser_guard)
            except Exception:
                self.close()
                return _refuse("local Chromium is unavailable")
        sources = {sid: source for sid, source in self.sources.items()
                   if canonical_url(str(source.url)) == canonical_url(url)}
        prepare = rendered_preparation(sources, sources)
        try:
            result = self.renderer.fetch(url, prepare=prepare)
        except Exception:
            return _refuse("local Chromium read failed")
        if result.error:
            return _refuse("local Chromium recipe failed")
        return self._result(url, result)

    def fallback(self, url: str) -> FetchResult:
        if reason := self._fallback_block(url):
            return _refuse(reason)
        if self.ledger is None:
            return _refuse("paid fallback is disabled")
        if url not in self._rendered_urls:
            return _refuse("Chromium source read must precede paid fallback")
        if url in self._paid_urls:
            return _refuse("paid fallback already attempted for this URL")
        if not firecrawl_allowed(url):
            return _refuse("paid fallback host is not allowed")
        month = datetime.now(UTC).strftime("%Y-%m")
        if self.month is not None and self.month != month:
            return _refuse("paid fallback ledger month differs from the current UTC month")
        if self.ledger.is_symlink() or self.ledger.parent.is_symlink():
            return _refuse("paid fallback ledger is unsafe")
        lock_path = self.ledger.with_name(f".{self.ledger.name}.lock")
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            with os.fdopen(descriptor, "a") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                ledger = _read_ledger(self.ledger, month)
                if self.credits_spent >= RUN_LIMIT:
                    return _refuse("paid fallback five-credit run limit exhausted")
                if ledger["months"][month] >= MONTHLY_LIMIT:
                    return _refuse("paid fallback 100-credit calendar month limit exhausted")
                paid = self.firecrawl_factory(allowance=1)
                if not paid.prepare():
                    return _refuse(paid.stop_reason or "paid fallback preparation failed")
                ledger["months"][month] += 1
                _write_ledger(self.ledger, ledger)
                self.credits_spent += 1
                self._paid_urls.add(url)
        except (OSError, ValueError, UnicodeError):
            return _refuse("paid fallback ledger is missing, unreadable or unsafe")
        return self._result(url, paid.fetch(url))
