"""Optional admission fetches with a durable 50-credit monthly Firecrawl limit."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from decision.excluded import excluded_sources
from decision.firecrawl import (
    FIRECRAWL_MAX_CREDITS_PER_RUN,
    FirecrawlFetcher,
    fallback_needed,
    firecrawl_allowed,
)
from decision.normalise import canonical_url
from decision.retention import cite_only_origin_restrictive
from decision.sources import FetchResult, fingerprint_bytes
from scripts.price_reread_fallback import monthly_budget

MONTHLY_LIMIT = 50


def _without_restricted_bytes(url: str, result: FetchResult) -> FetchResult:
    origins = (url, *result.resolved_urls)
    if any(excluded_sources().url(origin) for origin in origins):
        return FetchResult("unreachable", error="Admission source is excluded")
    # Restrictive: withhold bytes; the drafter refuses to cite a malformed origin.
    if result.outcome == "ok" and cite_only_origin_restrictive(url, result.resolved_urls):
        return replace(
            result,
            body=b"",
            snapshot_ref=result.snapshot_ref or fingerprint_bytes(result.body),
            retrieved_at=result.retrieved_at or datetime.now(UTC),
        )
    return result


class AdmissionFallback:
    """Use one caller-restored UTC month's ledger, shared by every invocation.

    Each child directory is an existing price-reread ledger artifact. Missing
    artifacts count as twelve credits. The sibling lock serializes budget reads
    and reservations; the ledger must already exist to attest that restoration
    completed. Ledger artifacts retain accounting only, never response bodies.
    """

    def __init__(
        self,
        primary,
        ledger: Path,
        *,
        month: str,
        firecrawl_factory=FirecrawlFetcher,
    ) -> None:
        if not isinstance(month, str) or re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", month) is None:
            raise ValueError("admission fallback month must be YYYY-MM")
        self.primary = primary
        self.ledger = Path(ledger)
        self.month = month
        self.firecrawl_factory = firecrawl_factory

    def fetch(self, url: str) -> FetchResult:
        if excluded_sources().url(url):
            return FetchResult("unreachable", error="Admission source is excluded")
        result = self.primary.fetch(url)
        if any(excluded_sources().url(origin) for origin in result.resolved_urls):
            return FetchResult("unreachable", error="Admission source is excluded")
        result = _without_restricted_bytes(url, result)
        if not fallback_needed(result):
            return result
        if not firecrawl_allowed(url):
            return FetchResult("unreachable", error="Admission Firecrawl host is not allowed")
        if self.ledger.is_symlink() or not self.ledger.is_dir():
            return FetchResult(
                "unreachable", error="Admission Firecrawl ledger is missing or unsafe"
            )
        lock_path = self.ledger.parent / f".{self.ledger.name}.admission.lock"
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        except OSError:
            return FetchResult(
                "unreachable", error="Admission Firecrawl ledger lock is unavailable"
            )
        with os.fdopen(descriptor, "a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            if self.ledger.is_symlink() or not self.ledger.is_dir():
                return FetchResult(
                    "unreachable", error="Admission Firecrawl ledger is missing or unsafe"
                )
            budget = monthly_budget(self.ledger, self.month)
            allowance = min(
                budget.allowance,
                max(
                    0,
                    MONTHLY_LIMIT
                    - budget.known_spend
                    - budget.unreadable_ledgers * FIRECRAWL_MAX_CREDITS_PER_RUN,
                ),
            )
            if allowance == 0:
                return FetchResult(
                    "unreachable", error="Admission Firecrawl monthly 50-credit limit exhausted"
                )
            paid = self.firecrawl_factory(allowance=allowance)
            if not paid.prepare():
                return FetchResult("unreachable", error=paid.stop_reason)
            url = canonical_url(url)
            self._reserve(url, paid, budget)
            return _without_restricted_bytes(url, paid.fetch(url))

    def _reserve(self, url, paid, budget) -> None:
        directory = Path(tempfile.mkdtemp(prefix="admission-", dir=self.ledger))
        manifest = {
            "schema_version": 2,
            "month": self.month,
            "credits_spent": 1,
            "credits_reserved": 1,
            "allowance": paid.allowance,
            "prior_month_spend_known": budget.known_spend,
            "unreadable_ledgers": budget.unreadable_ledgers,
            "team_balance": paid.team_balance,
            "stop_reason": None,
            "fake": False,
            "pages": {
                url: {
                    "file": hashlib.sha256(url.encode()).hexdigest() + ".html",
                    "outcome": "unreachable",
                    "status": None,
                    "error": "Admission reservation; page content is not retained",
                },
            },
        }
        temporary = directory / "manifest.tmp"
        with temporary.open("x", encoding="utf-8") as output:
            json.dump(manifest, output, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(directory / "manifest.json")
        for path in (directory, self.ledger):
            descriptor = os.open(path, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
