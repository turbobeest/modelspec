"""Fallback artifacts and conservative UTC-month accounting for price re-reads."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from decision.excluded import excluded_sources
from decision.firecrawl import (
    FIRECRAWL_CREDITS_PER_CALL,
    FIRECRAWL_MAX_CREDITS_PER_MONTH,
    FIRECRAWL_MAX_CREDITS_PER_RUN,
    FirecrawlFetcher,
    fallback_needed,
    firecrawl_allowed,
)
from decision.normalise import NORMALISERS, canonical_url
from decision.sources import Fetcher, FetchMode, FetchResult, load_sources
from decision.verify import Queue, VerificationLog
from scripts.price_reread import (
    MAX_RENDERED_MANIFEST_BYTES,
    RenderedReplayFetcher,
    _in_scope,
    _read_rendered_file,
    _unique_json_object,
    tracked_facts,
)


def read_fallback(
    directory: Path, *, month: str | None = None
) -> tuple[RenderedReplayFetcher, int]:
    """Validate both spend and page entries before either accounting or replay."""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("fallback artifact directory must be a directory, not a symlink")
    try:
        manifest = json.loads(
            _read_rendered_file(directory / "manifest.json", MAX_RENDERED_MANIFEST_BYTES),
            object_pairs_hook=_unique_json_object,
        )
    except RecursionError:
        raise ValueError("fallback manifest JSON nesting exceeds limit") from None
    fields = {"schema_version", "month", "credits_spent", "pages"}
    if not isinstance(manifest, dict) or set(manifest) != fields:
        raise ValueError("invalid fallback manifest fields")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("invalid fallback manifest version")
    recorded_month = manifest["month"]
    if (
        not isinstance(recorded_month, str)
        or re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", recorded_month) is None
        or (month is not None and recorded_month != month)
    ):
        raise ValueError("invalid fallback ledger month")
    spent = manifest["credits_spent"]
    pages = manifest["pages"]
    if (
        type(spent) is not int
        or not 0 <= spent <= FIRECRAWL_MAX_CREDITS_PER_RUN
        or not isinstance(pages, dict)
        or spent != len(pages) * FIRECRAWL_CREDITS_PER_CALL
        or any(not firecrawl_allowed(url) for url in pages)
    ):
        raise ValueError("invalid fallback ledger spend or hosts")
    return RenderedReplayFetcher(directory, manifest=pages), spent


def monthly_allowance(ledger: Path, month: str) -> int:
    """The workflow enumerates every earlier main run in this UTC month.

    It creates a directory even when that run's artifact is missing, expired or
    cannot download. Charge each unreadable run the full 12-credit maximum.
    A failed enumeration stops the workflow before fetching. This is stricter
    than forgetting missing ledgers and allowing another 12 credits each run.
    Artifacts alone cannot attest to forged lower spend or unrecorded runs;
    the residual bound for unrecorded invocations is 12 credits per invocation.
    """
    if ledger.is_symlink() or not ledger.is_dir():
        return 0
    spent = 0
    for directory in sorted(ledger.iterdir()):
        try:
            _, credits = read_fallback(directory, month=month)
        except (OSError, ValueError):
            credits = FIRECRAWL_MAX_CREDITS_PER_RUN
        spent += credits
    return min(FIRECRAWL_MAX_CREDITS_PER_RUN, max(0, FIRECRAWL_MAX_CREDITS_PER_MONTH - spent))


def fallback_to(
    *,
    root: Path,
    rendered: RenderedReplayFetcher,
    directory: Path,
    month: str,
    plain: Fetcher,
    firecrawl: FirecrawlFetcher,
) -> None:
    """Spend only on in-scope, allowed HTML URLs whose primary fetch failed."""
    sources = load_sources(root / "registry" / "sources.yaml")
    filed = Queue(root / "verification").filed()
    latest = VerificationLog(root / "verification").latest()
    source_ids = set()
    for tracked in tracked_facts(root):
        claim = filed.get(("fact", tracked.fact["id"]))
        if _in_scope(tracked.fact, claim, latest) is None:
            source_ids.update(s.source_id for s in claim.sources)
    excluded = excluded_sources()
    candidates = {}
    for sid in sorted(source_ids):
        source = sources.get(sid)
        if source is None or NORMALISERS[source.normaliser].content != "html":
            continue
        url = canonical_url(str(source.url))
        if not firecrawl_allowed(url) or excluded.url(url):
            continue
        if source.fetch == FetchMode.RENDERED.value:
            entry = rendered.manifest.get(url)
            if entry is None or not fallback_needed(FetchResult(entry["outcome"], entry["status"])):
                continue
        candidates[url] = source.fetch
    directory.mkdir(parents=True, exist_ok=True)
    pages = {}

    def checkpoint(spent: int) -> None:
        manifest = {"schema_version": 1, "month": month, "credits_spent": spent, "pages": pages}
        temporary = directory / "manifest.tmp"
        temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temporary.replace(directory / "manifest.json")

    checkpoint(0)
    for url, mode in sorted(candidates.items()):
        if not firecrawl.can_fetch:
            break
        primary = rendered.fetch(url) if mode == FetchMode.RENDERED.value else plain.fetch(url)
        if not fallback_needed(primary):
            continue
        name = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html"
        # Persist the reservation before making the call. A timeout or killed
        # process must not leave a readable artifact that understates spend.
        pages[url] = {
            "file": name,
            "outcome": "unreachable",
            "status": None,
            "error": "Firecrawl attempt interrupted",
        }
        checkpoint(firecrawl.credits_spent + FIRECRAWL_CREDITS_PER_CALL)
        result = firecrawl.fetch(url)
        if result.outcome == "ok":
            (directory / name).write_bytes(result.body)
        pages[url] = {
            "file": name,
            "outcome": result.outcome,
            "status": result.status,
            "error": result.error,
        }
        checkpoint(firecrawl.credits_spent)


class FallbackFetcher:
    """A successful primary result always wins; replay is never a paid call."""

    def __init__(self, primary, fallback: RenderedReplayFetcher) -> None:
        self.primary = primary
        self.fallback = fallback

    def fetch(self, url: str) -> FetchResult:
        result = self.primary.fetch(url)
        if (
            fallback_needed(result)
            and firecrawl_allowed(url)
            and canonical_url(url) in self.fallback.manifest
        ):
            alternative = self.fallback.fetch(url)
            if alternative.outcome == "ok":
                return alternative
        return result
