#!/usr/bin/env python3
"""Weekly re-read of every sourced price and subscription-plan page (MODEL-217).

MODEL-201 and MODEL-205 filed plan and price facts whose values the verifier's
deterministic readers confirmed from a retained copy of each page. This job
fetches each of those pages again over plain HTTP, or local Chromium with
``--rendered``, or replays a ``--render-to`` artifact with ``--rendered-from``.
It asks the same readers,
under the same two-key rules, whether the page still says what the fact says.
Each fact ends in one status:

- ``unchanged``: the recorded value verifies against the new copy. With
  ``--write`` that verification is logged with today's date, so the value's age
  restarts; the offering file is not touched.
- ``needs_review``: the value no longer verifies. The reason carries what the
  readers propose instead, if anything: one new value, several, a list or flag,
  or free text read only from a whole-page region. The job never writes a
  changed value (MODEL-423): a reader can take a price from the wrong row, so a
  person reviews every proposal and files it as a data change. ``changed`` is
  kept in the report's counts and is always zero.
- ``unreadable``: the page fetched but the reader no longer understands it: the
  cited region is gone, no reader accepts the page, or the subject is not found.
- ``unreachable``: the page did not fetch.
- ``not_reread``: out of this job's reach. A rendered browser was not enabled,
  the retained copy is a text projection that needs re-registering before an
  HTML re-read, the value is still quarantined, or an LLM reader last verified it
  and the deterministic readers cannot read it, so their failure says nothing
  about the page. When they can, an LLM-verified value is reconfirmed like any other, and
  a value they read otherwise is ``needs_review``, never ``changed``
  (MODEL-235).

``needs_review``, ``unreadable`` and ``unreachable`` are alerts. The job never
guesses a value for them; a person re-collects.

With ``--write`` the job records only reconfirmations of unchanged values, and
the dated citations of cite-only sources; it never edits a value.

The optional, read-only Firecrawl fallback has its own credit limits. Replays
and ordinary re-reads never call a model or a paid scraper.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from contextlib import ExitStack
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from decision.excluded import excluded_sources
from decision.model import (
    DETERMINISTIC,
    Verification,
    VerificationActor,
    fact_verification_value,
    value_hash,
)
from decision.normalise import (
    NORMALISERS,
    UnsupportedContentError,
    canonical_url,
    normalise_document,
)
from decision.sources import (
    RENDERED_PREPARATIONS,
    CopyStore,
    Fetcher,
    FetchMode,
    FetchResult,
    RenderedFetcher,
    fingerprint_bytes,
    load_sources,
    rendered_preparation,
)
from decision.verify import (
    Claim,
    ExtractorError,
    Queue,
    Result,
    StoredRegions,
    SubscriptionPageExtractor,
    VerificationLog,
    claim_verification_value,
    dated_price_claim,
    deterministic_extractors,
    normalise_name,
    parse_quantity,
    split_model_cell,
    verify,
)

from decision.retention import (
    citation_metadata, cite_only_origin_restrictive, cite_only_origin_status, is_cite_only_restrictive,
    record_origin_status,
)

ROOT = Path(__file__).resolve().parents[1]
#: ``automerge.yml`` must never queue this branch (tests/test_price_reread.py).
BRANCH = "data/weekly-price-reread"
#: A week with no change: dated reconfirmations only, which may auto-merge.
RECONFIRM_BRANCH = "data/weekly-price-reconfirm"
USER_AGENT = "ModelSpec-Price-Reread/1.0 (+https://modelspec.dev)"
FACET_PREFIXES = ("offering.price.", "offering.subscription.")
MAX_READ_AGE_DAYS = 7
REREAD = VerificationActor(
    agent="modelspec-price-reread",
    model_family=DETERMINISTIC,
    method="weekly-price-reread@1",
)
#: Lines of source diff shown per page in the report.
DIFF_LINES = 80
MAX_RENDERED_BODY_BYTES = 20 * 1024 * 1024
MAX_RENDERED_MANIFEST_BYTES = 1024 * 1024
#: Candidate replacement values checked per fact; see ``_propose``.
MAX_PROPOSAL_CHECKS = 32


class Status(StrEnum):
    CITED = "cited"
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    NEEDS_REVIEW = "needs_review"
    UNREADABLE = "unreadable"
    UNREACHABLE = "unreachable"
    NOT_REREAD = "not_reread"


ALERTS = frozenset({Status.NEEDS_REVIEW, Status.UNREADABLE, Status.UNREACHABLE})


@dataclass(frozen=True)
class FactResult:
    fact_id: str
    facet: str
    file: str
    source_ids: tuple[str, ...]
    status: Status
    old_state: str
    old_value: Any
    new_value: Any = None
    reason: str | None = None
    #: source_id -> (old copy ref, new copy ref), for sources fetched this run.
    copies: Mapping[str, tuple[str, str]] = field(default_factory=dict)
    #: The claim as re-read, sources pinned to the new copies.
    claim: Claim | None = field(default=None, compare=False, repr=False)
    #: For an unchanged fact, the record that re-verified it against the new copy.
    verification: Verification | None = field(default=None, compare=False, repr=False)
    cited: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact": self.fact_id,
            "facet": self.facet,
            "file": self.file,
            "sources": list(self.source_ids),
            "status": self.status.value,
            "old_state": self.old_state,
            "old_value": None if self.cited or self.status is Status.CITED else self.old_value,
            "new_value": None if self.cited or self.status is Status.CITED else self.new_value,
            "reason": self.reason,
            "copies": {sid: {"old": old, "new": new} for sid, (old, new) in self.copies.items()},
            **({"citations": self.citations()} if self.status is Status.CITED else {}),
        }

    def citations(self) -> dict[str, dict[str, Any]]:
        """Source ID -> the dated citation ``--write`` records on that reference.

        These are the exact ``snapshot_ref``, ``retrieved_at`` and ``resolved_urls``
        that ``rewrite_fact`` writes, so the data repository's guard can require
        each written citation to be one this run recorded (MODEL-423).
        """
        if self.claim is None:
            return {}
        return {ref.source_id: {"snapshot_ref": ref.snapshot_ref,
                                "retrieved_at": ref.retrieved_at.isoformat(),
                                "resolved_urls": [str(url) for url in ref.resolved_urls]}
                for ref in self.claim.sources
                if ref.source_id in self.copies and ref.retrieved_at is not None}


@dataclass
class SourceFetch:
    source_id: str
    url: str
    outcome: str  # "ok", "rendered", "text_projection", "excluded", or the fetch error
    copy_ref: str | None = None
    error: str | None = None
    retrieved_at: datetime | None = None
    resolved_urls: tuple[str, ...] = ()


@dataclass
class Report:
    checked_on: date
    facts: list[FactResult] = field(default_factory=list)
    sources: dict[str, SourceFetch] = field(default_factory=dict)
    #: source_id -> unified diff lines of its cited regions, old copy to new.
    diffs: dict[str, list[str]] = field(default_factory=dict)
    overdue: list[str] = field(default_factory=list)
    fallback_spend: str | None = None

    @property
    def changes(self) -> list[FactResult]:
        return [f for f in self.facts if f.status is Status.CHANGED]

    @property
    def alerts(self) -> list[FactResult]:
        return [f for f in self.facts if f.status in ALERTS
                or f.status is Status.CITED and any(old != new for old, new in f.copies.values())
                or f.status is Status.NOT_REREAD and f.fact_id in self.overdue]

    def counts(self) -> dict[str, int]:
        counts = Counter(f.status.value for f in self.facts)
        return {s.value: counts.get(s.value, 0) for s in Status
                if s is not Status.CITED or counts.get(s.value, 0)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_on": self.checked_on.isoformat(),
            "max_read_age_days": MAX_READ_AGE_DAYS,
            "overdue": self.overdue,
            "counts": self.counts(),
            "changes": [f.to_dict() for f in self.changes],
            "reconfirmed": [f.fact_id for f in self.facts if f.status is Status.UNCHANGED],
            "cited": [f.to_dict() for f in self.facts if f.status is Status.CITED],
            "alerts": [f.to_dict() for f in self.alerts],
            "not_reread": dict(Counter(
                f.reason or "" for f in self.facts if f.status is Status.NOT_REREAD)),
            "sources": {sid: {"url": s.url, "outcome": s.outcome, "copy": s.copy_ref,
                              "error": s.error}
                        for sid, s in sorted(self.sources.items())},
        }


# --- which facts --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Tracked:
    path: Path
    fact: Mapping[str, Any]


def tracked_facts(root: Path) -> list[Tracked]:
    """Every price and plan fact with a filed value, in file order."""
    found = []
    for path in sorted((root / "offerings").glob("**/*.yaml")):
        for offering in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            for fact in offering.get("facts") or []:
                if fact["facet"].startswith(FACET_PREFIXES) and fact["state"] != "unknown" \
                        and fact.get("sources"):
                    found.append(Tracked(path, fact))
    return found


def _in_scope(fact: Mapping[str, Any], claim: Claim | None, log_latest: Mapping,
              sources: Mapping | None = None) -> str | None:
    """Why this fact is out of the re-read's reach, or ``None``."""
    if claim is None:
        return "no filed claim"
    if value_hash(claim_verification_value(claim)) != value_hash(fact_verification_value(fact)):
        return "the fact differs from its filed claim"
    latest = log_latest.get(("fact", fact["id"]))
    # Granting: a cite-only source puts the fact in scope without a verified
    # result, so a malformed URL refuses (MODEL-420).
    statuses = [] if sources is None else [
        cite_only_origin_status(sources[ref.source_id].url, getattr(ref, "resolved_urls", ()))
        for ref in claim.sources if ref.source_id in sources]
    if None in statuses:
        return "a source URL is malformed"
    if any(statuses):
        if latest is not None and latest.outcome in {"mismatch", "unreachable"}:
            return "quarantined: latest source check failed"
        return None
    if latest is None or latest.outcome != "verified":
        return "quarantined: its value was never verified"
    if latest.target.value_hash != value_hash(fact_verification_value(fact)):
        return "quarantined: its verification is for another value"
    return None


def _llm_baseline(fact: Mapping[str, Any], log_latest: Mapping) -> str | None:
    """The model family of the LLM reader that last verified this fact, if one did."""
    latest = log_latest.get(("fact", fact["id"]))
    if latest is None:
        return None
    family = latest.verifier.model_family
    return None if family == DETERMINISTIC else family


# --- fetching -----------------------------------------------------------------------------------


def render_to(*, root: Path, directory: Path, rendered: RenderedFetcher) -> None:
    """Render only the HTML sources an in-scope re-read would fetch, once per URL."""
    sources = load_sources(root / "registry" / "sources.yaml")
    filed = Queue(root / "verification").filed()
    latest = VerificationLog(root / "verification").latest()
    source_ids = set()
    for tracked in tracked_facts(root):
        claim = filed.get(("fact", tracked.fact["id"]))
        if _in_scope(tracked.fact, claim, latest, sources) is None:
            assert claim is not None
            source_ids.update(s.source_id for s in claim.sources)
    excluded = excluded_sources()
    urls: dict[str, set[str]] = {}
    for sid in source_ids:
        source = sources.get(sid)
        if (source is not None and source.fetch == FetchMode.RENDERED.value
                and NORMALISERS[source.normaliser].content == "html"
                and not excluded.url(source.url)):
            urls.setdefault(canonical_url(str(source.url)), set()).add(sid)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for url, ids in sorted(urls.items()):
        result = _fetch_rendered(rendered, url, ids, sources)
        name = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html"
        restricted = cite_only_origin_restrictive(url, result.resolved_urls)
        if restricted:
            (directory / name).unlink(missing_ok=True)
        if result.outcome == "ok" and not restricted:
            (directory / name).write_bytes(result.body)
        manifest[url] = {"file": name, "outcome": result.outcome,
                         "status": result.status, "error": result.error}
        if result.outcome == "ok" and restricted:
            manifest[url]["error"] = None
            manifest[url]["citation"] = citation_metadata(
                url, fingerprint_bytes(result.body), retrieved_at=result.retrieved_at or datetime.now(UTC),
                resolved_urls=result.resolved_urls)
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _rendered_file(path: Path, limit: int) -> None:
    """The artifact may name regular files only, with a bounded byte count."""
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"rendered artifact file must be regular, not a symlink: {path.name}")
    if info.st_size > limit:
        raise ValueError(f"rendered artifact file exceeds {limit} bytes: {path.name}")


def _read_rendered_file(path: Path, limit: int) -> bytes:
    _rendered_file(path, limit)
    with path.open("rb") as body:
        content = body.read(limit + 1)
    if len(content) > limit:
        raise ValueError(f"rendered artifact file exceeds {limit} bytes: {path.name}")
    return content


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate rendered manifest key: {key!r}")
        result[key] = value
    return result


class RenderedReplayFetcher:
    """Read untrusted rendering artifacts as bytes; HTML parsing stays in Python."""

    def __init__(self, directory: Path, *, manifest: dict | None = None) -> None:
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("rendered artifact directory must be a directory, not a symlink")
        self.directory = directory
        if manifest is None:
            manifest = json.loads(
                _read_rendered_file(directory / "manifest.json", MAX_RENDERED_MANIFEST_BYTES),
                object_pairs_hook=_unique_json_object)
        if not isinstance(manifest, dict):
            raise ValueError("rendered manifest must be a JSON object")
        for url, entry in manifest.items():
            if not url.startswith(("http://", "https://")) or canonical_url(url) != url:
                raise ValueError("rendered manifest keys must be canonical HTTP URLs")
            if not isinstance(entry, dict) or set(entry) not in (
                    {"file", "outcome", "status", "error"},
                    {"file", "outcome", "status", "error", "citation"}):
                raise ValueError(f"invalid rendered manifest entry for {url}")
            name = entry["file"]
            if (not isinstance(name, str) or not name or name == "." or ".." in name
                    or "/" in name or "\\" in name or "\x00" in name or name == "manifest.json"):
                raise ValueError("rendered file must be a plain name inside the artifact directory")
            if entry["outcome"] not in ("ok", "not_modified", "unreachable"):
                raise ValueError(f"invalid rendered outcome for {url}")
            if entry["status"] is not None and type(entry["status"]) is not int:
                raise ValueError(f"invalid rendered status for {url}")
            if entry["error"] is not None and not isinstance(entry["error"], str):
                raise ValueError(f"invalid rendered error for {url}")
            path = directory / name
            citation = entry.get("citation")
            if citation is not None:
                if (not isinstance(citation, dict) or citation.get("url") != url
                        or not isinstance(citation.get("snapshot_ref"), str)
                        or not re.fullmatch(r"sha256:[0-9a-f]{64}", citation["snapshot_ref"])
                        or cite_only_origin_status(url, citation.get("resolved_urls", ()))
                        is not True):
                    raise ValueError("invalid cite-only rendered citation")
                datetime.fromisoformat(citation["retrieved_at"])
                if path.exists() or path.is_symlink():
                    raise ValueError("cite-only rendered artifact must not contain page bytes")
            elif is_cite_only_restrictive(url) and entry["outcome"] == "ok":
                raise ValueError("cite-only rendered artifact requires hash-only citation")
            elif entry["outcome"] == "ok" or path.exists() or path.is_symlink():
                _rendered_file(path, MAX_RENDERED_BODY_BYTES)
        self.manifest = manifest

    def fetch(self, url: str) -> FetchResult:
        entry = self.manifest.get(canonical_url(url))
        if entry is None:
            return FetchResult("unreachable", error="not rendered: URL missing from manifest")
        if entry["outcome"] != "ok":
            return FetchResult("unreachable", entry["status"],
                               error=f"not rendered: {entry['error'] or entry['outcome']}")
        if citation := entry.get("citation"):
            return FetchResult("ok", entry["status"], snapshot_ref=citation["snapshot_ref"],
                               retrieved_at=datetime.fromisoformat(citation["retrieved_at"]),
                               resolved_urls=tuple(citation["resolved_urls"]))
        return FetchResult("ok", entry["status"],
                           body=_read_rendered_file(self.directory / entry["file"],
                                                    MAX_RENDERED_BODY_BYTES),
                           content_type="text/html", charset="utf-8", error=entry["error"])


def _fetch_rendered(rendered: RenderedFetcher | RenderedReplayFetcher, url: str,
                    source_ids: Iterable[str], sources: Mapping[str, Any] | None = None
                    ) -> FetchResult:
    # A replay, or a fallback wrapped around one, serves captured bytes: only a live
    # browser takes a preparation.
    if isinstance(getattr(rendered, "primary", rendered), RenderedReplayFetcher):
        return rendered.fetch(url)
    source_ids = sorted(set(source_ids))
    preparation = (rendered_preparation(source_ids, sources) if sources is not None else
                   next((RENDERED_PREPARATIONS[sid] for sid in source_ids
                         if sid in RENDERED_PREPARATIONS), None))
    return rendered.fetch(url, prepare=preparation) if preparation else rendered.fetch(url)


def _valid_citation_record(store: CopyStore, ref: str) -> bool:
    """Whether ``ref`` has a citation record; ValueError when that record is malformed.

    A record whose stored origins fail ``record_origin_status`` never grants
    the cited outcome (MODEL-420); the caller refuses the source instead.
    """
    record = store.citation(ref)
    if record is not None and record_origin_status(record) is None:
        raise ValueError("invalid citation record")
    return record is not None


def fetch_sources(source_ids: Iterable[str], sources: Mapping[str, Any], fetcher: Fetcher,
                  store: CopyStore, rendered: RenderedFetcher | RenderedReplayFetcher | None = None
                  ) -> dict[str, SourceFetch]:
    excluded = excluded_sources()
    fetched: dict[str, SourceFetch] = {}
    for sid in sorted(set(source_ids)):
        source = sources.get(sid)
        if source is None:
            fetched[sid] = SourceFetch(sid, "", "unregistered source")
            continue
        url = canonical_url(str(source.url))
        if excluded.url(url):
            fetched[sid] = SourceFetch(sid, url, "excluded")
            continue
        if source.fetch == FetchMode.RENDERED.value:
            if rendered is None:
                fetched[sid] = SourceFetch(sid, url, "rendered")
                continue
            if NORMALISERS[source.normaliser].content != "html":
                fetched[sid] = SourceFetch(sid, url, "text_projection")
                continue
            result = _fetch_rendered(rendered, url, (sid,), sources)
        else:
            result = fetcher.fetch(url)
        if result.outcome == "ok":
            retrieved_at = result.retrieved_at or datetime.now(UTC)
            try:
                if result.snapshot_ref is not None:
                    if cite_only_origin_status(url, result.resolved_urls) is not True:
                        raise ValueError("a byte-free replay requires a cite-only origin")
                    ref = result.snapshot_ref
                    _valid_citation_record(store, ref)  # never overwrite a damaged one
                    store.record_citation(ref, source_url=url, retrieved_at=retrieved_at,
                                          resolved_urls=result.resolved_urls)
                else:
                    ref = store.put(result.body, source_url=url, retrieved_at=retrieved_at,
                                    resolved_urls=result.resolved_urls)
                # Granting: "cited" skips verification, so an existing record for
                # this hash counts only once every origin it carries is valid.
                outcome = "cited" if _valid_citation_record(store, ref) else "ok"
            except ValueError:
                # Fail closed for this source only (MODEL-420): no bytes, no
                # citation, and the other sources still run.
                fetched[sid] = SourceFetch(sid, url, "invalid_citation_metadata")
                continue
            fetched[sid] = SourceFetch(sid, url, outcome, ref,
                                       error=None if outcome == "cited" else result.error,
                                       retrieved_at=retrieved_at, resolved_urls=result.resolved_urls)
        else:
            fetched[sid] = SourceFetch(sid, url, result.error or result.outcome)
    return fetched


# --- one fact -----------------------------------------------------------------------------------


def _own_names(claim: Claim) -> set[str]:
    return {identity for name in claim.names
            for identity in (normalise_name(name), split_model_cell(name)[0])}


def _candidate(old: Any, reading_value: Any, unit: str | None) -> Any:
    """A reading as a value of the old value's type, or ``None``. Lists and flags are
    never rewritten here, and a value that was not disclosed may become a number only."""
    if isinstance(old, bool) or isinstance(old, list):
        return None
    if old is None or isinstance(old, (int, float)):
        q = parse_quantity(str(reading_value), unit)
        if q is None:
            return None
        if isinstance(old, float):
            return float(q.number)
        return int(q.number) if float(q.number).is_integer() else float(q.number)
    if isinstance(old, str) and isinstance(reading_value, str) and reading_value.strip():
        return reading_value.strip()
    return None


def _readings(claim: Claim, regions: StoredRegions, *, narrow_only: bool = False) -> list[Any]:
    """Possible replacements from the claim's cited regions, verified by `_propose`."""
    found = []
    for source in claim.sources:
        for region_id in source.cited_regions:
            if narrow_only:
                registered = regions.sources.get(source.source_id)
                if registered is None or not any(
                    r.id == region_id and r.locator.kind != "page"
                    for r in registered.cited_regions
                ):
                    continue
            text = regions.text(source.source_id, source.snapshot_ref, region_id)
            if text is None:
                continue
            if dated_price_claim(claim):
                found += regions.dated_prices(claim, source, region_id)
                continue
            for extractor in deterministic_extractors():
                if not extractor.accepts(text):
                    continue
                try:
                    if isinstance(extractor, SubscriptionPageExtractor) \
                            and claim.field == "offering.subscription.coverage_quote":
                        found += extractor.quote_candidates(claim, text)
                    else:
                        found += extractor.extract(claim, text)
                except ExtractorError:
                    continue
    return found


@dataclass(frozen=True)
class Proposal:
    """What the readers propose in place of a value that no longer verifies."""

    #: Values that verify for the claim's subject: none, one, or the first two found.
    values: list[Any]
    #: Whether the readers found any value at all for that subject.
    read_any: bool
    #: How many distinct candidate values the readers offered.
    candidates: int

    @property
    def stopped_early(self) -> bool:
        """Whether the search hit ``MAX_PROPOSAL_CHECKS`` and left candidates unchecked."""
        return self.candidates > MAX_PROPOSAL_CHECKS

    @property
    def unique(self) -> bool:
        """One verified value, and every other candidate was checked and failed."""
        return len(self.values) == 1 and not self.stopped_early

    @property
    def cap_note(self) -> str:
        """Says so in a review reason when the search stopped at the cap."""
        return (f" (the search checked only the first {MAX_PROPOSAL_CHECKS} of "
                f"{self.candidates} candidate values)" if self.stopped_early else "")


def _propose(claim: Claim, regions: StoredRegions, today: date, *,
             narrow_only: bool = False) -> Proposal:
    """New values that verify for the claim's subject.

    Each check is a full verification that reads the cited regions again. A coverage
    quote offers every line, sentence and run of lines of its region as a candidate,
    so checking all of them was quadratic in the page: on a long page one fact ran
    past the job's 15-minute cap (MODEL-423). The callers only tell none, one and
    several apart, so the search stops at the second value that verifies, and it
    checks at most ``MAX_PROPOSAL_CHECKS`` candidates.
    """
    own = _own_names(claim)
    readings = [r for r in _readings(claim, regions, narrow_only=narrow_only)
                if r.subject and split_model_cell(r.subject)[0] in own and r.value is not None]
    candidates: list[Any] = []
    seen: set[str] = set()
    for reading in readings:
        value = _candidate(claim.value, reading.value, reading.unit)
        if value is not None and (digest := value_hash(value)) not in seen:
            seen.add(digest)
            candidates.append(value)
    confirmed: list[Any] = []
    for value in candidates[:MAX_PROPOSAL_CHECKS]:
        if verify(replace(claim, value=value, collector=REREAD), regions,
                  deterministic_extractors(), today=today).outcome == "verified":
            confirmed.append(value)
            if len(confirmed) == 2:
                break
    return Proposal(confirmed, bool(readings), len(candidates))


def reread_fact(tracked: Tracked, claim: Claim, fetched: Mapping[str, SourceFetch],
                regions: StoredRegions, today: date, root: Path,
                llm: str | None = None) -> FactResult:
    """Re-read one fact. ``llm`` names the LLM reader that last verified it, if one
    did (MODEL-235): the deterministic readers may confirm that value, but a value
    they read differently is only an alert, never a change, and a page they
    cannot read says nothing about it."""
    fact = tracked.fact
    # The filed claim's sources, not the fact's: its cited regions are the ones the
    # value was verified from.
    old_sources = claim.sources
    base = FactResult(
        fact_id=fact["id"], facet=fact["facet"],
        file=str(tracked.path.relative_to(root)),
        source_ids=tuple(s.source_id for s in old_sources),
        status=Status.NOT_REREAD, old_state=fact["state"], old_value=fact.get("value"),
        cited=any(ref.source_id in regions.sources and cite_only_origin_restrictive(
            regions.sources[ref.source_id].url, ref.resolved_urls) for ref in old_sources),
    )
    ok = {s.source_id: fetched[s.source_id] for s in old_sources
          if fetched[s.source_id].outcome in {"ok", "cited"}}
    if not ok:
        outcomes = sorted({fetched[s.source_id].outcome for s in old_sources})
        if "fallback was a fake run" in outcomes:
            return replace(base, reason="fallback was a fake run")
        if set(outcomes) <= {"rendered", "text_projection", "excluded"}:
            if "text_projection" in outcomes:
                return replace(base, reason="the retained copy is a text projection; "
                               "re-register the source to re-read it rendered")
            return replace(base, reason="the page needs a rendered fetch"
                           if "rendered" in outcomes else "excluded source")
        return replace(base, status=Status.UNREACHABLE, reason="; ".join(outcomes))

    copies = {sid: (next(s.snapshot_ref for s in old_sources if s.source_id == sid),
                    f.copy_ref) for sid, f in ok.items()}
    pinned = tuple(s.model_copy(update={"snapshot_ref": ok[s.source_id].copy_ref,
                                       "retrieved_at": ok[s.source_id].retrieved_at,
                                       "resolved_urls": list(ok[s.source_id].resolved_urls)})
                   if s.source_id in ok else s for s in old_sources)
    claim = replace(claim, sources=pinned)
    base = replace(base, copies=copies)
    if any(item.outcome == "cited" for item in ok.values()):
        changed = any(old != new for old, new in copies.values())
        return replace(base, status=Status.CITED, claim=claim,
                       reason="Cited, not machine-verified; " + (
                           "source hash changed and needs a citation assessment" if changed else
                           "source hash unchanged"))

    preparation_errors = [f"{sid}: {source.error}" for sid, source in ok.items() if source.error]
    if preparation_errors:
        return replace(base, status=Status.UNREADABLE, reason="; ".join(preparation_errors))

    # Each candidate verifies against the same copies and normaliser rules.
    # Release the parsed documents when this fact's re-read returns.
    regions = StoredRegions(regions.store, regions.sources, cache_documents=True)
    result = verify(claim, regions, deterministic_extractors(), today=today)
    if result.outcome == "verified":
        return replace(base, status=Status.UNCHANGED, verification=result.verification)
    if llm is not None:
        # Only a well-formed value that verifies in its place is evidence of a change;
        # a reader that cannot parse the page says nothing about it.
        # A verbatim string "verifies" as whatever a reader returns, so only a number
        # counts here.
        llm_proposal = _propose(claim, regions, today) if result.outcome == "mismatch" else None
        confirmed = [v for v in (llm_proposal.values if llm_proposal else [])
                     if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if confirmed:
            return replace(base, status=Status.NEEDS_REVIEW,
                           reason=f"last verified by an LLM reader ({llm}); a deterministic "
                           "reader now reads " + ", ".join(map(json.dumps, confirmed))
                           + llm_proposal.cap_note)
        if llm_proposal is not None and llm_proposal.stopped_early:
            # Unchecked candidates may hold the new value: fail closed to review
            # rather than report that the readers cannot read the page (MODEL-423).
            return replace(base, status=Status.NEEDS_REVIEW,
                           reason=f"last verified by an LLM reader ({llm}); no deterministic "
                           "reading confirms a value" + llm_proposal.cap_note)
        return replace(base, reason=f"last verified by an LLM reader ({llm}); "
                       "the deterministic readers cannot read it")
    if result.outcome == "unreachable":
        return replace(base, status=Status.UNREADABLE,
                       reason=f"cited region not found in the new copy: {result.reason}"
                       f"{_page_size(regions, claim)}")
    if result.outcome == "skipped":
        return replace(base, status=Status.UNREADABLE,
                       reason=f"no reader accepts the new copy: {result.reason}"
                       f"{_page_size(regions, claim)}")

    proposal = _propose(claim, regions, today)
    confirmed = proposal.values
    diff = _diff_text(result)
    if not proposal.read_any:
        return replace(base, status=Status.UNREADABLE,
                       reason=f"the readers find no value for {claim.names[0]!r}: {diff}")
    if any(isinstance(value, str) for value in confirmed):
        if not _propose(claim, regions, today, narrow_only=True).values:
            page_regions = [
                f"{source.source_id}#{region.id}"
                for source in claim.sources
                for region in regions.sources[source.source_id].cited_regions
                if region.id in source.cited_regions and region.locator.kind == "page"
            ]
            return replace(base, status=Status.NEEDS_REVIEW,
                           reason="a free-text value read from a whole-page region "
                           f"({', '.join(page_regions)}) is not proposed as a change; "
                           "cite a narrower region" + proposal.cap_note)
    if proposal.unique and fact["state"] == "known":
        # The job never writes a changed value: a person reviews the proposal and
        # files it (MODEL-423). Only a value that still verifies is recorded.
        return replace(base, status=Status.NEEDS_REVIEW, new_value=confirmed[0],
                       reason=f"a reader now reads {json.dumps(confirmed[0])} in place of "
                       f"{json.dumps(fact.get('value'))}; a person reviews and files every "
                       f"change: {diff}")
    if proposal.unique:
        # A value the page did not state is new, not changed: a person confirms the
        # page now states it, and it is not a label for something else (MODEL-235).
        return replace(base, status=Status.NEEDS_REVIEW,
                       reason=f"was {fact['state']}; a reader now reads "
                       f"{json.dumps(confirmed[0])}: {diff}")
    if len(confirmed) > 1:
        why = "several new values verify, among them " + ", ".join(map(json.dumps, confirmed))
    elif confirmed:
        why = f"a reader reads {json.dumps(confirmed[0])}, but it may not be the only value"
    else:
        why = "no single new value verifies"
    return replace(base, status=Status.NEEDS_REVIEW,
                   reason=f"{why}{proposal.cap_note}; {diff}")


def _page_size(regions: StoredRegions, claim: Claim) -> str:
    """How much text each new copy has: a few characters means a script shell or a
    bot wall, not a redesign."""
    sizes = []
    for source in claim.sources:
        found = regions.sources.get(source.source_id)
        if found is None or is_cite_only_restrictive(found.url) or not regions.store.has(source.snapshot_ref):
            continue
        rules = NORMALISERS[found.normaliser]
        try:
            text = normalise_document(regions.store.get(source.snapshot_ref), rules).text
        except (UnsupportedContentError, ValueError):
            continue
        sizes.append(f"{source.source_id} has {len(text)} characters of text")
    return f" ({'; '.join(sizes)})" if sizes else ""


def _diff_text(result: Result) -> str:
    return "; ".join(f"{d.field}: expected {d.expected!r}, found {d.found!r}"
                     for d in result.diffs) or (result.reason or "")


# --- the run ------------------------------------------------------------------------------------


def run(*, root: Path = ROOT, fetcher: Fetcher, store: CopyStore, today: date,
        write: bool = False, at: datetime | None = None,
        rendered: RenderedFetcher | RenderedReplayFetcher | None = None) -> Report:
    """Re-read every tracked fact. With ``write``, apply the changes to ``root``."""
    at = at or datetime.now(UTC)
    sources = load_sources(root / "registry" / "sources.yaml")
    queue = Queue(root / "verification")
    log = VerificationLog(root / "verification")
    filed = queue.filed()
    latest = log.latest()
    regions = StoredRegions(store, sources)
    report = Report(today)

    facts = tracked_facts(root)
    scoped: list[tuple[Tracked, Claim, str | None]] = []
    for tracked in facts:
        baseline = latest.get(("fact", tracked.fact["id"]))
        if (baseline is None or baseline.outcome != "verified"
                or baseline.target.value_hash != value_hash(fact_verification_value(tracked.fact))
                or (today - baseline.date).days > MAX_READ_AGE_DAYS):
            report.overdue.append(tracked.fact["id"])
        claim = filed.get(("fact", tracked.fact["id"]))
        reason = _in_scope(tracked.fact, claim, latest, sources)
        if reason is None:
            assert claim is not None
            scoped.append((tracked, claim, _llm_baseline(tracked.fact, latest)))
        else:
            report.facts.append(FactResult(
                tracked.fact["id"], tracked.fact["facet"], str(tracked.path.relative_to(root)),
                tuple(s["source_id"] for s in tracked.fact["sources"]), Status.NOT_REREAD,
                tracked.fact["state"], tracked.fact.get("value"), reason=reason,
                cited=any(ref["source_id"] in sources and cite_only_origin_restrictive(
                    sources[ref["source_id"]].url, ref.get("resolved_urls", ()))
                    for ref in tracked.fact["sources"])))

    report.sources = fetch_sources(
        (s.source_id for _, claim, _ in scoped for s in claim.sources), sources, fetcher, store,
        rendered=rendered)
    results = [reread_fact(t, c, report.sources, regions, today, root, llm)
               for t, c, llm in scoped]

    # Some servers answer a fetch now and then with a script shell, a bot wall
    # or a 403. A page whose facts would alert is fetched once more first.
    retryable = {Status.UNREADABLE, Status.UNREACHABLE}
    retry = sorted({sid for r in results if r.status in retryable for sid in r.source_ids})
    if retry:
        again = fetch_sources(retry, sources, fetcher, store, rendered=rendered)
        fresh = {sid for sid, f in again.items()
                 if f.outcome == "ok" and (f.copy_ref != report.sources[sid].copy_ref
                                          or f.error != report.sources[sid].error)}
        report.sources.update({sid: again[sid] for sid in fresh})
        results = [
            reread_fact(t, c, report.sources, regions, today, root, llm)
            if r.status in retryable and fresh & set(r.source_ids) else r
            for (t, c, llm), r in zip(scoped, results, strict=True)
        ]
    report.facts += results

    report.diffs = source_diffs(report, sources, store)
    if write:
        for fact in report.facts:
            if fact.status is Status.CITED and fact.claim is not None:
                path = root / fact.file
                before = path.read_text(encoding="utf-8")
                after = rewrite_fact(before, fact)
                check_value_only(before, after, [fact])
                path.write_text(after, encoding="utf-8")
                queue.file(fact.claim, at=at)
                queue.checked(Result(fact.claim.target, "cited", reason=fact.reason), at=at)
        # A value that still reads the same is verified again today, so its age
        # restarts (the 7-day price interval, decision.sources.DEFAULT_INTERVALS).
        for fact in report.facts:
            if fact.status is Status.UNCHANGED and fact.verification is not None:
                log.append(fact.verification)
    return report


def source_diffs(report: Report, sources: Mapping[str, Any], store: CopyStore
                 ) -> dict[str, list[str]]:
    """The cited regions' text, old copy to new, for each page with a change or alert."""
    regions = StoredRegions(store, sources)
    wanted: dict[str, set[tuple[str, str]]] = {}
    for fact in report.changes + report.alerts:
        for sid, pair in fact.copies.items():
            wanted.setdefault(sid, set()).add(pair)
    diffs: dict[str, list[str]] = {}
    for sid, pairs in sorted(wanted.items()):
        if is_cite_only_restrictive(sources[sid].url) or any(
                store.citation(ref) is not None for pair in pairs for ref in pair):
            continue
        lines: list[str] = []
        for old, new in sorted(pairs):
            if old == new:
                continue
            if not store.has(old):
                lines.append(f"# the previous copy {old} is not retained on this runner")
                continue
            for region in sources[sid].cited_regions:
                before = regions.text(sid, old, region.id) or ""
                after = regions.text(sid, new, region.id) or ""
                lines += difflib.unified_diff(
                    before.splitlines(), after.splitlines(),
                    f"{sid}#{region.id} {old[:15]}", f"{sid}#{region.id} {new[:15]}",
                    n=1, lineterm="")
        lines = [line if len(line) <= 240 else line[:239] + "…" for line in lines]
        if len(lines) > DIFF_LINES:
            lines = [*lines[:DIFF_LINES], f"# … {len(lines) - DIFF_LINES} more lines"]
        diffs[sid] = lines
    return diffs


# --- writing ------------------------------------------------------------------------------------


def _dump_value(value: Any) -> str:
    """``value: <value>`` on one line. A string with a line break is written as a
    double-quoted JSON string, which is also valid YAML, so no continuation line
    depends on the file's indentation."""
    if isinstance(value, str) and "\n" in value:
        return "value: " + json.dumps(value, ensure_ascii=False)
    return yaml.safe_dump({"value": value}, width=10**9, allow_unicode=True,
                          default_flow_style=False).strip()


def rewrite_fact(text: str, change: FactResult) -> str:
    """``text`` with one fact's value, state and re-fetched copy refs replaced, and
    every other line kept byte for byte."""
    lines = text.splitlines(keepends=True)
    head = re.compile(rf"^(\s*)- id: {re.escape(change.fact_id)}\s*$")
    start = next((i for i, line in enumerate(lines) if head.match(line)), None)
    if start is None:
        raise ValueError(f"{change.fact_id}: not found")
    indent = len(head.match(lines[start]).group(1))
    key = " " * (indent + 2)
    end = start + 1
    while end < len(lines):
        line = lines[end]
        stripped = line.lstrip(" ")
        if stripped.strip() and len(line) - len(stripped) <= indent:
            break
        end += 1

    block = lines[start:end]
    out: list[str] = []
    current_source: str | None = None
    cited = change.status is Status.CITED
    refs = {ref.source_id: ref for ref in change.claim.sources} if cited and change.claim else {}
    i = 0
    while i < len(block):
        line = block[i]
        if not cited and line.startswith(key + "value:"):
            out.append(key + _dump_value(change.new_value) + "\n")
            i += 1
            # The old value's continuation lines are indented deeper; a quoted
            # scalar's paragraph break is a blank line inside it.
            while i < len(block) and (not block[i].strip()
                                      or len(block[i]) - len(block[i].lstrip(" ")) > len(key)):
                i += 1
            while not block[i - 1].strip():
                i -= 1
            continue
        if not cited and line.startswith(key + "state:"):
            out.append(f"{key}state: known\n")
        elif m := re.match(r"^\s*- source_id: (\S+)\s*$", line):
            current_source = m.group(1)
            out.append(line)
        elif (m := re.match(r"^(\s*)snapshot_ref: sha256:[0-9a-f]{64}\s*$", line)) \
                and current_source in change.copies:
            out.append(f"{m.group(1)}snapshot_ref: {change.copies[current_source][1]}\n")
            if cited:
                ref = refs[current_source]
                out.append(f"{m.group(1)}retrieved_at: '{ref.retrieved_at.isoformat()}'\n")
                out.append(f"{m.group(1)}resolved_urls: {json.dumps([str(url) for url in ref.resolved_urls])}\n")
        elif cited and current_source in change.copies and re.match(
                r"^\s*(retrieved_at|resolved_urls):", line):
            depth = len(line) - len(line.lstrip())
            i += 1
            while i < len(block) and (len(block[i]) - len(block[i].lstrip()) > depth
                                      or re.match(r"^\s*- https?://", block[i])):
                i += 1
            continue
        else:
            out.append(line)
        i += 1
    return "".join(lines[:start] + out + lines[end:])


def _facts_by_id(text: str) -> tuple[list[Any], dict[str, dict[str, Any]]]:
    offerings = yaml.safe_load(text) or []
    facts = {f["id"]: f for o in offerings for f in o.get("facts") or []}
    shells = [{k: v for k, v in o.items() if k != "facts"} for o in offerings]
    return shells, facts


def check_value_only(before: str, after: str, changes: Sequence[FactResult]) -> None:
    """Refuse a rewrite that touches anything but the changed facts' value, state and
    re-fetched copy refs, or that does not land the intended value."""
    shells_before, before_facts = _facts_by_id(before)
    shells_after, after_facts = _facts_by_id(after)
    if shells_before != shells_after or before_facts.keys() != after_facts.keys():
        raise ValueError("the rewrite changed an offering, or added or removed a fact")
    changed = {c.fact_id: c for c in changes}
    for fid, old in before_facts.items():
        new = after_facts[fid]
        change = changed.get(fid)
        if change is None:
            if old != new:
                raise ValueError(f"{fid}: changed without a re-read change")
            continue
        cited = change.status is Status.CITED
        expected_value = old.get("value") if cited else change.new_value
        if new.get("value") != expected_value or type(new.get("value")) is not type(
                expected_value) or new["state"] != (old["state"] if cited else "known"):
            raise ValueError(f"{fid}: the rewrite did not land {change.new_value!r}")
        expected_sources = [
            {**s, "snapshot_ref": change.copies[s["source_id"]][1]}
            if s["source_id"] in change.copies else s for s in old["sources"]]
        if cited and change.claim is not None:
            refs = {ref.source_id: ref for ref in change.claim.sources}
            for source in expected_sources:
                if source["source_id"] in change.copies:
                    ref = refs[source["source_id"]]
                    source.update(retrieved_at=ref.retrieved_at.isoformat(),
                                  resolved_urls=[str(url) for url in ref.resolved_urls])
        if new["sources"] != expected_sources:
            raise ValueError(f"{fid}: the rewrite changed its sources")
        rest = {"value", "state", "sources"}
        if {k: v for k, v in old.items() if k not in rest} != \
                {k: v for k, v in new.items() if k not in rest}:
            raise ValueError(f"{fid}: the rewrite changed a field besides the value")


def retain_only(store: CopyStore, root: Path, report: Report) -> int:
    """Delete every copy in ``store`` that no tracked fact cites and this run did not
    fetch. For a runner's store only; returns how many were deleted."""
    keep = {s["snapshot_ref"] for t in tracked_facts(root) for s in t.fact["sources"]}
    keep |= {s.copy_ref for s in report.sources.values() if s.copy_ref}
    removed = 0
    for path in store.root.glob("??/*"):
        if path.is_file() and f"sha256:{path.name}" not in keep:
            path.unlink()
            removed += 1
    return removed


# --- the report ---------------------------------------------------------------------------------


def _show(value: Any, state: str | None = None) -> str:
    if state == "not_disclosed" and value is None:
        return "not disclosed"
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= 120 else text[:117] + "…"


def render_report(report: Report) -> str:
    counts = report.counts()
    out = [
        f"## Price and plan re-read, {report.checked_on.isoformat()}",
        "",
        "| " + " | ".join(counts) + " |",
        "|" + "---|" * len(counts),
        "| " + " | ".join(str(n) for n in counts.values()) + " |",
        "",
        f"Each unchanged value was verified again on {report.checked_on.isoformat()} against "
        "a fresh copy of its page.",
        "",
    ]
    if report.fallback_spend is not None:
        out += [report.fallback_spend, ""]
    if report.changes:
        out += ["### Changed values", "",
                "A person reviews every change here before it merges; none auto-merges.", "",
                "| Fact | Old | New | Source |", "|---|---|---|---|"]
        for f in report.changes:
            sources = ", ".join(f"{sid} (`{new[:15]}`)" for sid, (_, new) in f.copies.items())
            out.append(f"| `{f.fact_id}` | {_show(f.old_value, f.old_state)} | "
                       f"{_show(f.new_value)} | {sources} |")
        out.append("")
    if report.alerts:
        out += ["### Needs a person", "",
                "The readers could not re-read these, so nothing was written for them.", "",
                "| Fact | Status | Why |", "|---|---|---|"]
        for f in report.alerts:
            out.append(f"| `{f.fact_id}` | {f.status.value} | {_show(f.reason)} |")
        out.append("")
    if report.diffs:
        out += ["### Source diffs", ""]
        for sid, lines in report.diffs.items():
            url = report.sources[sid].url if sid in report.sources else ""
            # Page text must not close the fence: make it longer than any run of
            # backticks the page contains.
            longest = max((len(run) for line in lines for run in re.findall(r"`+", line)),
                          default=0)
            fence = "`" * max(3, longest + 1)
            out += [f"`{sid}` {url}", "", f"{fence}diff", *(lines or ["# no text change"]),
                    fence, ""]
    not_reread = Counter(f.reason for f in report.facts if f.status is Status.NOT_REREAD)
    if not_reread:
        out += ["### Not re-read", "", "| Why | Facts |", "|---|---|"]
        out += [f"| {why} | {n} |" for why, n in not_reread.most_common()]
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true",
                        help="apply changed values to offerings/ and verification/")
    rendering = parser.add_mutually_exclusive_group()
    rendering.add_argument("--rendered", action="store_true",
                           help="re-read rendered HTML sources with local headless Chromium")
    rendering.add_argument("--render-to", type=Path,
                           help="render eligible pages into an artifact without verification")
    rendering.add_argument("--rendered-from", type=Path,
                           help="re-read rendered HTML from a validated artifact, without a browser")
    rendering.add_argument("--fallback-from-render", type=Path,
                           help="fetch failed eligible pages with the capped Firecrawl fallback")
    parser.add_argument("--fallback-to", type=Path)
    parser.add_argument("--fallback-ledger", type=Path)
    parser.add_argument("--fallback-fake", action="store_true",
                        help="demo fallback artifacts with fake HTML, no key or network")
    parser.add_argument("--fallback-from", type=Path,
                        help="replay a validated fallback artifact, without a Firecrawl key")
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    parser.add_argument("--retain-only-cited", action="store_true",
                        help="prune the copy store to cited and fetched copies (runners only)")
    parser.add_argument("--today", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    if args.render_to is not None and args.write:
        parser.error("--render-to cannot be combined with --write")
    if args.fallback_from_render is not None:
        if (args.write or args.fallback_to is None or args.fallback_ledger is None
                or args.fallback_from):
            parser.error("--fallback-from-render requires --fallback-to and --fallback-ledger, "
                         "without --write or --fallback-from")
    elif args.fallback_to is not None or args.fallback_ledger is not None or args.fallback_fake:
        parser.error("--fallback-to, --fallback-ledger and --fallback-fake require "
                     "--fallback-from-render")
    if args.fallback_from is not None and args.rendered_from is None:
        parser.error("--fallback-from requires --rendered-from")

    with ExitStack() as stack:
        rendered = None
        fallback_spend = None
        if args.rendered or args.render_to is not None:
            try:
                rendered = stack.enter_context(RenderedFetcher())
            except ImportError:
                flag = "--render-to" if args.render_to is not None else "--rendered"
                parser.error(f"{flag} requires Playwright; install playwright and its "
                             "Chromium browser (python -m playwright install chromium)")
        if args.render_to is not None:
            render_to(root=ROOT, directory=args.render_to, rendered=rendered)
            return 0
        if args.rendered_from is not None:
            try:
                rendered = RenderedReplayFetcher(args.rendered_from)
            except (OSError, ValueError) as exc:
                parser.error(f"invalid rendered artifact: {exc}")
        if args.fallback_from_render is not None:
            from decision.firecrawl import FakeFirecrawlFetcher, FirecrawlFetcher
            from scripts.price_reread_fallback import fallback_to, monthly_budget, read_fallback

            try:
                rendered = RenderedReplayFetcher(args.fallback_from_render)
                month = datetime.now(UTC).strftime("%Y-%m")
                budget = monthly_budget(args.fallback_ledger, month)
                fallback_to(root=ROOT, rendered=rendered, directory=args.fallback_to, month=month,
                            # Missing plain entries are unavailable in a fake run.
                            # Demo eligibility never makes a primary HTTP request.
                            plain=(rendered if args.fallback_fake else
                                   Fetcher(user_agent=USER_AGENT)),
                            firecrawl=FakeFirecrawlFetcher() if args.fallback_fake else
                            FirecrawlFetcher(allowance=budget.allowance), budget=budget)
                replay, _ = read_fallback(args.fallback_to)
                print(replay.spend_line)
                if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
                    with Path(summary).open("a", encoding="utf-8") as output:
                        output.write(replay.spend_line + "\n")
            except (OSError, ValueError) as exc:
                parser.error(f"invalid fallback artifact or ledger: {exc}")
            return 0
        fetcher = Fetcher(user_agent=USER_AGENT)
        if args.fallback_from is not None:
            from scripts.price_reread_fallback import FallbackFetcher, read_fallback

            try:
                fallback, _ = read_fallback(args.fallback_from)
                fallback_spend = fallback.spend_line
            except (OSError, ValueError) as exc:
                parser.error(f"invalid fallback artifact: {exc}")
            fetcher = FallbackFetcher(fetcher, fallback)
            rendered = FallbackFetcher(rendered, fallback)
        store = CopyStore()
        report = run(root=ROOT, fetcher=fetcher, store=store,
                     today=args.today or datetime.now(UTC).date(), write=args.write,
                     rendered=rendered)
        report.fallback_spend = fallback_spend
    markdown = render_report(report)
    if args.report_md:
        args.report_md.write_text(markdown + "\n", encoding="utf-8")
    if args.report_json:
        args.report_json.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
                                    + "\n", encoding="utf-8")
    if args.retain_only_cited:
        retain_only(store, ROOT, report)
    print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
