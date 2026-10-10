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
- ``changed``: it does not, and exactly one new value for the same subject
  verifies against the new copy. With ``--write`` the fact takes that value and
  the new copy, and the verification is logged. A price change is never merged
  by a machine: the workflow opens a pull request for a person to review, on a
  branch ``automerge.yml`` skips.
- ``needs_review``: the value no longer verifies and the readers find no single
  replacement (several candidates, a list or flag the job does not rewrite,
  or free text read only from a whole-page region).
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

Two keys: the old value's collector is whoever filed it. A new value is filed
by ``modelspec-price-reread`` and confirmed by the verifier's deterministic
readers. Both keys are code from one repository, so the pull request's human
reviewer is the check that the readers still read the page as intended.

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
from decision.model import DETERMINISTIC, Verification, VerificationActor, value_hash
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
    load_sources,
)
from decision.verify import (
    Claim,
    ExtractorError,
    Queue,
    Result,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    normalise_name,
    parse_quantity,
    split_model_cell,
    verify,
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


class Status(StrEnum):
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact": self.fact_id,
            "facet": self.facet,
            "file": self.file,
            "sources": list(self.source_ids),
            "status": self.status.value,
            "old_state": self.old_state,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "copies": {sid: {"old": old, "new": new} for sid, (old, new) in self.copies.items()},
        }


@dataclass
class SourceFetch:
    source_id: str
    url: str
    outcome: str  # "ok", "rendered", "text_projection", "excluded", or the fetch error
    copy_ref: str | None = None
    error: str | None = None


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
                or f.status is Status.NOT_REREAD and f.fact_id in self.overdue]

    def counts(self) -> dict[str, int]:
        counts = Counter(f.status.value for f in self.facts)
        return {s.value: counts.get(s.value, 0) for s in Status}

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_on": self.checked_on.isoformat(),
            "max_read_age_days": MAX_READ_AGE_DAYS,
            "overdue": self.overdue,
            "counts": self.counts(),
            "changes": [f.to_dict() for f in self.changes],
            "reconfirmed": [f.fact_id for f in self.facts if f.status is Status.UNCHANGED],
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


def _in_scope(fact: Mapping[str, Any], claim: Claim | None, log_latest: Mapping) -> str | None:
    """Why this fact is out of the re-read's reach, or ``None``."""
    if claim is None:
        return "no filed claim"
    if value_hash(claim.value) != value_hash(fact.get("value")):
        return "the fact differs from its filed claim"
    latest = log_latest.get(("fact", fact["id"]))
    if latest is None or latest.outcome != "verified":
        return "quarantined: its value was never verified"
    if latest.target.value_hash != value_hash(fact.get("value")):
        return "quarantined: its verification is for another value"
    return None


def _llm_baseline(fact: Mapping[str, Any], log_latest: Mapping) -> str | None:
    """The model family of the LLM reader that last verified this fact, if one did."""
    family = log_latest[("fact", fact["id"])].verifier.model_family
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
        if _in_scope(tracked.fact, claim, latest) is None:
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
        result = _fetch_rendered(rendered, url, ids)
        name = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".html"
        if result.outcome == "ok":
            (directory / name).write_bytes(result.body)
        manifest[url] = {"file": name, "outcome": result.outcome,
                         "status": result.status, "error": result.error}
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
            if not isinstance(entry, dict) or set(entry) != {"file", "outcome", "status", "error"}:
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
            if entry["outcome"] == "ok" or path.exists() or path.is_symlink():
                _rendered_file(path, MAX_RENDERED_BODY_BYTES)
        self.manifest = manifest

    def fetch(self, url: str) -> FetchResult:
        entry = self.manifest.get(canonical_url(url))
        if entry is None:
            return FetchResult("unreachable", error="not rendered: URL missing from manifest")
        if entry["outcome"] != "ok":
            return FetchResult("unreachable", entry["status"],
                               error=f"not rendered: {entry['error'] or entry['outcome']}")
        return FetchResult("ok", entry["status"],
                           body=_read_rendered_file(self.directory / entry["file"],
                                                    MAX_RENDERED_BODY_BYTES),
                           content_type="text/html", charset="utf-8", error=entry["error"])


def _fetch_rendered(rendered: RenderedFetcher | RenderedReplayFetcher, url: str,
                    source_ids: Iterable[str]) -> FetchResult:
    # A replay, or a fallback wrapped around one, serves captured bytes: only a live
    # browser takes a preparation.
    if isinstance(getattr(rendered, "primary", rendered), RenderedReplayFetcher):
        return rendered.fetch(url)
    preparation = next((RENDERED_PREPARATIONS[sid] for sid in sorted(source_ids)
                        if sid in RENDERED_PREPARATIONS), None)
    return rendered.fetch(url, prepare=preparation) if preparation else rendered.fetch(url)


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
            result = _fetch_rendered(rendered, url, (sid,))
        else:
            result = fetcher.fetch(url)
        if result.outcome == "ok":
            fetched[sid] = SourceFetch(sid, url, "ok", store.put(result.body), error=result.error)
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
    """Every reading the deterministic readers take from the claim's cited regions."""
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
            for extractor in deterministic_extractors():
                if not extractor.accepts(text):
                    continue
                try:
                    found += extractor.extract(claim, text)
                except ExtractorError:
                    continue
    return found


def _propose(claim: Claim, regions: StoredRegions, today: date, *,
             narrow_only: bool = False) -> tuple[list[Any], bool]:
    """New values that verify for the claim's subject, and whether the readers found
    any value at all for that subject."""
    own = _own_names(claim)
    readings = [r for r in _readings(claim, regions, narrow_only=narrow_only)
                if r.subject and split_model_cell(r.subject)[0] in own and r.value is not None]
    candidates: list[Any] = []
    for reading in readings:
        value = _candidate(claim.value, reading.value, reading.unit)
        if value is not None and value_hash(value) not in {value_hash(c) for c in candidates}:
            candidates.append(value)
    confirmed = [
        value for value in candidates
        if verify(replace(claim, value=value, collector=REREAD), regions,
                  deterministic_extractors(), today=today).outcome == "verified"
    ]
    return confirmed, bool(readings)


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
    )
    ok = {s.source_id: fetched[s.source_id] for s in old_sources
          if fetched[s.source_id].outcome == "ok"}
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
    pinned = tuple(s.model_copy(update={"snapshot_ref": ok[s.source_id].copy_ref})
                   if s.source_id in ok else s for s in old_sources)
    claim = replace(claim, sources=pinned)
    base = replace(base, copies=copies)

    preparation_errors = [f"{sid}: {source.error}" for sid, source in ok.items() if source.error]
    if preparation_errors:
        return replace(base, status=Status.UNREADABLE, reason="; ".join(preparation_errors))

    result = verify(claim, regions, deterministic_extractors(), today=today)
    if result.outcome == "verified":
        return replace(base, status=Status.UNCHANGED, verification=result.verification)
    if llm is not None:
        # Only a well-formed value that verifies in its place is evidence of a change;
        # a reader that cannot parse the page says nothing about it.
        # A verbatim string "verifies" as whatever a reader returns, so only a number
        # counts here.
        confirmed = [v for v in (_propose(claim, regions, today)[0]
                                 if result.outcome == "mismatch" else [])
                     if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if confirmed:
            return replace(base, status=Status.NEEDS_REVIEW,
                           reason=f"last verified by an LLM reader ({llm}); a deterministic "
                           "reader now reads " + ", ".join(map(json.dumps, confirmed)))
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

    confirmed, read_any = _propose(claim, regions, today)
    diff = _diff_text(result)
    if not read_any:
        return replace(base, status=Status.UNREADABLE,
                       reason=f"the readers find no value for {claim.names[0]!r}: {diff}")
    if any(isinstance(value, str) for value in confirmed):
        narrow, _ = _propose(claim, regions, today, narrow_only=True)
        if not narrow:
            page_regions = [
                f"{source.source_id}#{region.id}"
                for source in claim.sources
                for region in regions.sources[source.source_id].cited_regions
                if region.id in source.cited_regions and region.locator.kind == "page"
            ]
            return replace(base, status=Status.NEEDS_REVIEW,
                           reason="a free-text value read from a whole-page region "
                           f"({', '.join(page_regions)}) is not proposed as a change; "
                           "cite a narrower region")
    if len(confirmed) == 1 and fact["state"] == "known":
        return replace(base, status=Status.CHANGED, new_value=confirmed[0], claim=claim)
    if len(confirmed) == 1:
        # A value the page did not state is new, not changed: a person confirms the
        # page now states it, and it is not a label for something else (MODEL-235).
        return replace(base, status=Status.NEEDS_REVIEW,
                       reason=f"was {fact['state']}; a reader now reads "
                       f"{json.dumps(confirmed[0])}: {diff}")
    why = ("several new values verify: " + ", ".join(map(json.dumps, confirmed))
           if confirmed else "no single new value verifies")
    return replace(base, status=Status.NEEDS_REVIEW, reason=f"{why}; {diff}")


def _page_size(regions: StoredRegions, claim: Claim) -> str:
    """How much text each new copy has: a few characters means a script shell or a
    bot wall, not a redesign."""
    sizes = []
    for source in claim.sources:
        found = regions.sources.get(source.source_id)
        if found is None or not regions.store.has(source.snapshot_ref):
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
                or baseline.target.value_hash != value_hash(tracked.fact.get("value"))
                or (today - baseline.date).days > MAX_READ_AGE_DAYS):
            report.overdue.append(tracked.fact["id"])
        claim = filed.get(("fact", tracked.fact["id"]))
        reason = _in_scope(tracked.fact, claim, latest)
        if reason is None:
            assert claim is not None
            scoped.append((tracked, claim, _llm_baseline(tracked.fact, latest)))
        else:
            report.facts.append(FactResult(
                tracked.fact["id"], tracked.fact["facet"], str(tracked.path.relative_to(root)),
                tuple(s["source_id"] for s in tracked.fact["sources"]), Status.NOT_REREAD,
                tracked.fact["state"], tracked.fact.get("value"), reason=reason))

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
        # A value that still reads the same is verified again today, so its age
        # restarts (the 7-day price interval, decision.sources.DEFAULT_INTERVALS).
        for fact in report.facts:
            if fact.status is Status.UNCHANGED and fact.verification is not None:
                log.append(fact.verification)
    if write and report.changes:
        refused = apply_changes(root, report.changes, at=at, today=today, regions=regions)
        report.facts = [
            replace(f, status=Status.NEEDS_REVIEW,
                    reason=f"read {f.new_value!r}, but the rewrite guard refused it: "
                    f"{refused[f.fact_id]}")
            if f.fact_id in refused else f
            for f in report.facts
        ]
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


def apply_changes(root: Path, changes: Sequence[FactResult], *, at: datetime, today: date,
                  regions: StoredRegions) -> dict[str, str]:
    """Rewrite each changed fact in place, then file and verify its new value.

    Returns the changes the guard refused, fact ID -> why; nothing is written for
    those, and the caller reports them as alerts.
    """
    refused: dict[str, str] = {}
    applied: list[FactResult] = []
    by_file: dict[str, list[FactResult]] = {}
    for change in changes:
        by_file.setdefault(change.file, []).append(change)
    for rel, file_changes in by_file.items():
        path = root / rel
        text = path.read_text(encoding="utf-8")
        for change in file_changes:
            try:
                after = rewrite_fact(text, change)
                check_value_only(text, after, [change])
            except ValueError as exc:
                refused[change.fact_id] = str(exc)
                continue
            text = after
            applied.append(change)
        path.write_text(text, encoding="utf-8")

    queue = Queue(root / "verification")
    log = VerificationLog(root / "verification")
    for change in applied:
        assert change.claim is not None
        claim = replace(change.claim, value=change.new_value, collector=REREAD)
        queue.file(claim, at=at)
        result = verify(claim, regions, deterministic_extractors(), today=today)
        if result.outcome != "verified" or result.verification is None:
            raise RuntimeError(f"{change.fact_id}: the new value did not verify on write")
        log.append(result.verification)
        queue.checked(result, at=at)
    return refused


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
    i = 0
    while i < len(block):
        line = block[i]
        if line.startswith(key + "value:"):
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
        if line.startswith(key + "state:"):
            out.append(f"{key}state: known\n")
        elif m := re.match(r"^\s*- source_id: (\S+)\s*$", line):
            current_source = m.group(1)
            out.append(line)
        elif (m := re.match(r"^(\s*)snapshot_ref: sha256:[0-9a-f]{64}\s*$", line)) \
                and current_source in change.copies:
            out.append(f"{m.group(1)}snapshot_ref: {change.copies[current_source][1]}\n")
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
        if new.get("value") != change.new_value or type(new.get("value")) is not type(
                change.new_value) or new["state"] != "known":
            raise ValueError(f"{fid}: the rewrite did not land {change.new_value!r}")
        expected_sources = [
            {**s, "snapshot_ref": change.copies[s["source_id"]][1]}
            if s["source_id"] in change.copies else s for s in old["sources"]]
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
