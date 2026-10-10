"""Fallback artifacts and conservative UTC-month accounting for price re-reads."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from decision.excluded import excluded_sources
from decision.firecrawl import (
    FIRECRAWL_CREDITS_PER_CALL,
    FIRECRAWL_MAX_CREDITS_PER_MONTH,
    FIRECRAWL_MAX_CREDITS_PER_RUN,
    FakeFirecrawlFetcher,
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


@dataclass(frozen=True)
class MonthlyBudget:
    allowance: int
    known_spend: int
    unreadable_ledgers: int


FAKE_REASON = "fallback was a fake run"
STOP_REASONS = {
    "FIRECRAWL_API_KEY is not configured",
    "Firecrawl credit allowance exhausted",
    "Firecrawl team balance below minimum of 100 credits",
    "Firecrawl team balance read timed out",
    "Firecrawl team balance request failed",
    "Firecrawl team balance response is invalid",
}


class FallbackReplayFetcher(RenderedReplayFetcher):
    def __init__(self, directory: Path, *, pages: dict, fake: bool, spend_line: str) -> None:
        super().__init__(directory, manifest=pages)
        self.fake = fake
        self.spend_line = spend_line

    def fetch(self, url: str) -> FetchResult:
        if self.fake:
            return FetchResult("unreachable", error=FAKE_REASON)
        return super().fetch(url)


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
    if version not in {1, 2}:
        raise ValueError("invalid fallback manifest version")
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
    recorded_month = manifest["month"]
    if (
        not isinstance(recorded_month, str)
        or re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", recorded_month) is None
        or (month is not None and recorded_month != month)
    ):
        raise ValueError("invalid fallback ledger month")
    spent = manifest["credits_spent"]
    pages = manifest["pages"]
    fake = manifest.get("fake", False)
    if (
        type(spent) is not int
        or not 0 <= spent <= FIRECRAWL_MAX_CREDITS_PER_RUN
        or not isinstance(pages, dict)
        or type(fake) is not bool
        or spent != (0 if fake else len(pages) * FIRECRAWL_CREDITS_PER_CALL)
        or any(not firecrawl_allowed(url) for url in pages)
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
    return FallbackReplayFetcher(directory, pages=pages, fake=fake, spend_line=spend_line), spent


def monthly_budget(ledger: Path, month: str) -> MonthlyBudget:
    """The workflow enumerates every earlier main run in this UTC month.

    It creates a directory even when that run's artifact is missing, expired or
    cannot download. Charge each unreadable run the full 12-credit maximum.
    A failed enumeration stops the workflow before fetching. This is stricter
    than forgetting missing ledgers and allowing another 12 credits each run.
    Artifacts alone cannot attest to forged lower spend or unrecorded runs;
    the residual bound for unrecorded invocations is 12 credits per invocation.
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


def fallback_to(
    *,
    root: Path,
    rendered: RenderedReplayFetcher,
    directory: Path,
    month: str,
    plain: Fetcher,
    firecrawl: FirecrawlFetcher | FakeFirecrawlFetcher,
    budget: MonthlyBudget,
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
        manifest = {
            "schema_version": 2,
            "month": month,
            "credits_spent": spent,
            "credits_reserved": spent,
            "allowance": firecrawl.allowance,
            "prior_month_spend_known": budget.known_spend,
            "unreadable_ledgers": budget.unreadable_ledgers,
            "team_balance": firecrawl.team_balance,
            "stop_reason": firecrawl.stop_reason,
            "fake": firecrawl.fake,
            "pages": pages,
        }
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
        if not firecrawl.prepare():
            break
        name = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html"
        # Persist the reservation before making the call. A timeout or killed
        # process must not leave a readable artifact that understates spend.
        pages[url] = {
            "file": name,
            "outcome": "unreachable",
            "status": None,
            "error": "Firecrawl attempt interrupted",
        }
        checkpoint(firecrawl.credits_spent + firecrawl.credits_per_call)
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
    checkpoint(firecrawl.credits_spent)


class FallbackFetcher:
    """A successful primary result always wins; replay is never a paid call."""

    def __init__(self, primary, fallback: FallbackReplayFetcher) -> None:
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
            if alternative.outcome == "ok" or self.fallback.fake:
                return alternative
        return result
