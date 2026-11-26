"""Fallback reads for the weekly price re-read, and the UTC-month Firecrawl ledger.

MODEL-570: the fallback reads every page through the class-checked Playwright path
(``decision.sources.RenderedFetcher``, MODEL-565). It makes no Firecrawl call and
reads no Firecrawl key. Every request and redirect hop is class-checked before it is
sent; a cite-only page keeps its URL, retrieval time and hash only; page bytes are
kept only when every hop is retaining-class; an unclassed host or a chain that cannot
be walked is skipped and listed. Without Playwright every page that needed the
fallback is a listed skip, and the run stays green.

The month ledger (``read_fallback`` on schema 1 and 2, ``monthly_budget``) still
accounts earlier Firecrawl runs, which the admission fallback shares. Pages in those
earlier artifacts are never replayed as evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path

from decision.excluded import excluded_sources
from decision.firecrawl import (
    DISABLED_STOP_REASON,
    FIRECRAWL_CREDITS_PER_CALL,
    FIRECRAWL_MAX_CREDITS_PER_MONTH,
    FIRECRAWL_MAX_CREDITS_PER_RUN,
    fallback_needed,
)
from decision.firecrawl import firecrawl_allowed as fallback_host_allowed
from decision.normalise import NORMALISERS, canonical_url
from decision.retention import (
    TermsRegisterUnreadable,
    canonical_host,
    citation_metadata,
    cite_only_origin_restrictive,
    classified_hosts,
    is_classified,
)
from decision.sources import (
    REDIRECT_UNCLASSIFIED,
    TERMS_REGISTER_UNREADABLE,
    Fetcher,
    FetchMode,
    FetchResult,
    fingerprint_bytes,
    load_sources,
    refusal_reason,
)
from decision.verify import Queue, VerificationLog
from scripts.price_reread import (
    MAX_RENDERED_MANIFEST_BYTES,
    RenderedReplayFetcher,
    _fetch_rendered,
    _in_scope,
    _read_rendered_file,
    _unique_json_object,
    tracked_facts,
)


@dataclass(frozen=True)
class MonthlyBudget:
    allowance: int
    known_spend: int
    unreadable_ledgers: int


#: The artifact schema the Playwright fallback writes (MODEL-570).
SCHEMA_VERSION = 3
READER = "playwright"
FAKE_REASON = "fallback was a fake run"
LEGACY_REASON = "Firecrawl fallback pages are not replayed (MODEL-570)"
PLAYWRIGHT_UNAVAILABLE = "Playwright unavailable"
#: Rendered-path refusals of a chain that cannot be walked or kept (decision/sources.py).
UNWALKABLE_ERRORS = (
    "ambiguous URL",
    "excluded source",
    "source redirect limit reached",
    "redirect after load not followed",
    "navigation during capture",
    "final URL is cite-only",
)
STOP_REASONS = {
    DISABLED_STOP_REASON,
    "FIRECRAWL_API_KEY is not configured",
    "Firecrawl credit allowance exhausted",
    "Firecrawl team balance below minimum of 100 credits",
    "Firecrawl team balance read timed out",
    "Firecrawl team balance request failed",
    "Firecrawl team balance response is invalid",
}


class FallbackReplayFetcher(RenderedReplayFetcher):
    def __init__(self, directory: Path, *, pages: dict, fake: bool, spend_line: str,
                 legacy: bool = False, skipped: dict | None = None) -> None:
        super().__init__(directory, manifest=pages)
        self.fake = fake
        self.spend_line = spend_line
        # A Firecrawl artifact (schema 1 or 2) still counts in the month ledger, but its
        # pages came through a path whose hops could not be checked: never evidence.
        self.legacy = legacy
        self.skipped = dict(skipped or {})

    def fetch(self, url: str) -> FetchResult:
        if self.fake:
            return FetchResult("unreachable", error=FAKE_REASON)
        if self.legacy:
            return FetchResult("unreachable", error=LEGACY_REASON)
        return super().fetch(url)


def _playwright_line(pages: dict, skipped: dict, fake: bool) -> str:
    ok = [entry for entry in pages.values() if entry["outcome"] == "ok"]
    cited = sum(1 for entry in ok if "citation" in entry)
    line = (
        f"Playwright fallback{' FAKE' if fake else ''}: no Firecrawl, credits used=0; "
        f"pages read={len(ok)}; bytes kept={len(ok) - cited}; cite-only hash only={cited}; "
        f"failed={len(pages) - len(ok)}; skipped={len(skipped)}."
    )
    if skipped:
        line += " Skipped: " + "; ".join(f"{url} ({why})" for url, why in sorted(skipped.items()))
        line += "."
    return line


def _read_playwright(directory: Path, manifest: dict) -> tuple[FallbackReplayFetcher, int]:
    fields = {"schema_version", "month", "credits_spent", "reader", "fake", "pages", "skipped"}
    if set(manifest) != fields:
        raise ValueError("invalid fallback manifest fields")
    pages, skipped, fake = manifest["pages"], manifest["skipped"], manifest["fake"]
    if (
        type(manifest["credits_spent"]) is not int
        or manifest["credits_spent"] != 0
        or manifest["reader"] != READER
        or type(fake) is not bool
        or not isinstance(pages, dict)
        or not isinstance(skipped, dict)
        or any(not fallback_host_allowed(url) for url in (*pages, *skipped))
        or any(canonical_url(url) != url for url in skipped)
        or any(not isinstance(why, str) or not why for why in skipped.values())
        or set(pages) & set(skipped)
    ):
        raise ValueError("invalid fallback pages, skips or spend")
    return FallbackReplayFetcher(directory, pages=pages, fake=fake, skipped=skipped,
                                 spend_line=_playwright_line(pages, skipped, fake)), 0


def read_fallback(
    directory: Path, *, month: str | None = None
) -> tuple[FallbackReplayFetcher, int]:
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
    if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int:
        raise ValueError("invalid fallback manifest fields")
    version = manifest["schema_version"]
    if version not in {1, 2, SCHEMA_VERSION}:
        raise ValueError("invalid fallback manifest version")
    recorded_month = manifest.get("month")
    if (
        not isinstance(recorded_month, str)
        or re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", recorded_month) is None
        or (month is not None and recorded_month != month)
    ):
        raise ValueError("invalid fallback ledger month")
    if version == SCHEMA_VERSION:
        return _read_playwright(directory, manifest)
    fields = {"schema_version", "month", "credits_spent", "pages"}
    if version == 2:
        fields |= {
            "fake",
            "credits_reserved",
            "allowance",
            "prior_month_spend_known",
            "unreadable_ledgers",
            "team_balance",
            "stop_reason",
        }
    if set(manifest) != fields:
        raise ValueError("invalid fallback manifest fields")
    spent = manifest["credits_spent"]
    pages = manifest["pages"]
    fake = manifest.get("fake", False)
    if (
        type(spent) is not int
        or not 0 <= spent <= FIRECRAWL_MAX_CREDITS_PER_RUN
        or not isinstance(pages, dict)
        or type(fake) is not bool
        or spent != (0 if fake else len(pages) * FIRECRAWL_CREDITS_PER_CALL)
        or any(not fallback_host_allowed(url) for url in pages)
    ):
        raise ValueError("invalid fallback ledger spend or hosts")
    if version == 2:
        allowance = manifest["allowance"]
        balance = manifest["team_balance"]
        reason = manifest["stop_reason"]
        if (
            type(manifest["credits_reserved"]) is not int
            or manifest["credits_reserved"] != spent
            or type(allowance) is not int
            or not spent <= allowance <= FIRECRAWL_MAX_CREDITS_PER_RUN
            or any(
                type(manifest[key]) is not int or manifest[key] < 0
                for key in ("prior_month_spend_known", "unreadable_ledgers")
            )
            or (
                balance is not None
                and (
                    type(balance) not in {int, float}
                    or balance < 0
                    or isinstance(balance, float)
                    and not math.isfinite(balance)
                )
            )
            or (
                reason is not None
                and (
                    not isinstance(reason, str)
                    or reason not in STOP_REASONS
                    and re.fullmatch(r"Firecrawl team balance HTTP [1-5]\d{2}", reason) is None
                )
            )
            or (fake and (allowance != 0 or balance is not None or reason is not None))
        ):
            raise ValueError("invalid fallback run accounting")
        spend_line = (
            f"Firecrawl fallback{' FAKE' if fake else ''}: credits reserved/used={spent}; "
            f"allowance={allowance}; "
            f"prior month spend known={manifest['prior_month_spend_known']}; "
            f"unreadable ledgers={manifest['unreadable_ledgers']}; "
            f"team balance={balance if balance is not None else 'unread'}."
        )
        if reason:
            spend_line += f" Stopped: {reason}."
    else:
        # Earlier artifacts remain valid month ledgers; their audit fields were
        # not recorded, so do not invent values when replaying them.
        spend_line = (
            f"Firecrawl fallback: credits reserved/used={spent}; allowance=unrecorded; "
            "prior month spend known=unrecorded; unreadable ledgers=unrecorded; "
            "team balance=unread."
        )
    return FallbackReplayFetcher(directory, pages=pages, fake=fake, spend_line=spend_line,
                                 legacy=True), spent


def monthly_budget(ledger: Path, month: str) -> MonthlyBudget:
    """The workflow enumerates every earlier main run in this UTC month.

    It creates a directory even when that run's artifact is missing, expired or
    cannot download. Charge each unreadable run the full 12-credit maximum.
    A failed enumeration stops the workflow before fetching. This is stricter
    than forgetting missing ledgers and allowing another 12 credits each run.
    Artifacts alone cannot attest to forged lower spend or unrecorded runs;
    the residual bound for unrecorded invocations is 12 credits per invocation.
    A Playwright fallback artifact (schema 3) spends nothing and counts zero.
    """
    if ledger.is_symlink() or not ledger.is_dir():
        return MonthlyBudget(0, 0, 1)
    spent = 0
    unreadable = 0
    for directory in sorted(ledger.iterdir()):
        try:
            _, credits = read_fallback(directory, month=month)
        except (OSError, ValueError):
            unreadable += 1
            continue
        spent += credits
    allowance = min(
        FIRECRAWL_MAX_CREDITS_PER_RUN,
        max(
            0, FIRECRAWL_MAX_CREDITS_PER_MONTH - spent - unreadable * FIRECRAWL_MAX_CREDITS_PER_RUN
        ),
    )
    return MonthlyBudget(allowance, spent, unreadable)


class FakeReader:
    """Deterministic demo HTML for ``--fallback-fake``: no browser, no request."""

    def fetch(self, url: str, *, prepare=None) -> FetchResult:
        html = (
            '<!doctype html><html><head><meta name="modelspec-fallback" content="fake">'
            "</head><body><h1>FAKE price fallback demo, not evidence</h1><p>"
            + escape(canonical_url(url))
            + "</p></body></html>"
        )
        return FetchResult("ok", 200, body=html.encode("utf-8"), content_type="text/html",
                           charset="utf-8", resolved_urls=(canonical_url(url),),
                           retrieved_at=datetime.now(UTC))


def _skip_reason(result: FetchResult) -> str | None:
    """Why a read was refused before or along its chain, or None for a plain failure."""
    if (reason := refusal_reason(result)) is not None:
        return reason
    error = result.error or ""
    if result.outcome != "ok" and any(error.startswith(e) for e in UNWALKABLE_ERRORS):
        return f"unwalkable chain: {error}"
    return None


def _unclassed_hop(url: str, resolved_urls) -> str | None:
    """Recheck every hop of a read against the terms register (the guard already has):
    a hop without a class, or an unreadable register, refuses the read."""
    try:
        classes = classified_hosts()
    except TermsRegisterUnreadable:
        return TERMS_REGISTER_UNREADABLE
    if classes is None:
        return TERMS_REGISTER_UNREADABLE
    for hop in (url, *resolved_urls):
        try:
            host = canonical_host(hop)
        except ValueError:
            host = None
        if not is_classified(host, classes):
            return f"{REDIRECT_UNCLASSIFIED}:{host or 'unparseable'}"
    return None


def fallback_to(
    *,
    root: Path,
    rendered: RenderedReplayFetcher,
    directory: Path,
    month: str,
    plain: Fetcher,
    reader=None,
    fake: bool = False,
    unavailable: str | None = None,
) -> None:
    """Read in-scope, allowed HTML URLs whose primary fetch failed, through ``reader``.

    ``reader`` is the class-checked Playwright fetcher (or ``FakeReader`` for the demo).
    With no reader, every page that needed the fallback is listed as skipped with
    ``unavailable`` as the reason: never a silent pass.
    """
    sources = load_sources(root / "registry" / "sources.yaml")
    filed = Queue(root / "verification").filed()
    latest = VerificationLog(root / "verification").latest()
    source_ids = set()
    for tracked in tracked_facts(root):
        claim = filed.get(("fact", tracked.fact["id"]))
        if _in_scope(tracked.fact, claim, latest, sources) is None:
            source_ids.update(s.source_id for s in claim.sources)
    excluded = excluded_sources()
    recipe_urls = {
        canonical_url(str(source.url))
        for source in sources.values()
        if source.rendered_interactions
    }
    candidates: dict[str, tuple[str, set[str]]] = {}
    for sid in sorted(source_ids):
        source = sources.get(sid)
        if source is None or NORMALISERS[source.normaliser].content != "html":
            continue
        url = canonical_url(str(source.url))
        if url in recipe_urls or not fallback_host_allowed(url) or excluded.url(url):
            continue
        if source.fetch == FetchMode.RENDERED.value:
            entry = rendered.manifest.get(url)
            if entry is None or not fallback_needed(FetchResult(entry["outcome"], entry["status"])):
                continue
        candidates.setdefault(url, (source.fetch, set()))[1].add(sid)
    directory.mkdir(parents=True, exist_ok=True)
    pages: dict[str, dict] = {}
    skipped: dict[str, str] = {}

    def checkpoint() -> None:
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "month": month,
            "credits_spent": 0,
            "reader": READER,
            "fake": fake,
            "pages": pages,
            "skipped": skipped,
        }
        temporary = directory / "manifest.tmp"
        temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
        temporary.replace(directory / "manifest.json")

    checkpoint()
    for url, (mode, sids) in sorted(candidates.items()):
        primary = rendered.fetch(url) if mode == FetchMode.RENDERED.value else plain.fetch(url)
        if not fallback_needed(primary):
            continue
        if reader is None:
            skipped[url] = unavailable or PLAYWRIGHT_UNAVAILABLE
            checkpoint()
            continue
        result = _fetch_rendered(reader, url, sids, sources)
        if (why := _skip_reason(result)) is not None:
            skipped[url] = why
            checkpoint()
            continue
        if result.outcome == "ok" and not fake and (
                why := _unclassed_hop(url, result.resolved_urls)) is not None:
            skipped[url] = why
            checkpoint()
            continue
        name = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html"
        restricted = cite_only_origin_restrictive(url, result.resolved_urls)
        if restricted:
            (directory / name).unlink(missing_ok=True)
        entry = {"file": name, "outcome": result.outcome, "status": result.status,
                 "error": result.error}
        if result.outcome == "ok" and not restricted:
            # Every hop is retaining-class: the bytes may be kept, with the chain.
            (directory / name).write_bytes(result.body)
            entry["resolved_urls"] = list(result.resolved_urls)
        elif result.outcome == "ok":
            # Cite-only: URL, time and hash only; the bytes never reach the disk.
            entry["error"] = None
            entry["citation"] = citation_metadata(
                url, fingerprint_bytes(result.body),
                retrieved_at=result.retrieved_at or datetime.now(UTC),
                resolved_urls=result.resolved_urls)
        pages[url] = entry
        checkpoint()
    checkpoint()


class FallbackFetcher:
    """A successful primary result always wins; replay is never a network call."""

    def __init__(self, primary, fallback: FallbackReplayFetcher) -> None:
        self.primary = primary
        self.fallback = fallback

    def fetch(self, url: str, *, prepare=None) -> FetchResult:
        result = (self.primary.fetch(url, prepare=prepare) if prepare is not None
                  else self.primary.fetch(url))
        if (
            fallback_needed(result)
            and fallback_host_allowed(url)
            and canonical_url(url) in self.fallback.manifest
        ):
            alternative = self.fallback.fetch(url)
            if alternative.outcome == "ok" or self.fallback.fake:
                return alternative
        return result
