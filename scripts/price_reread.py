#!/usr/bin/env python3
"""Weekly re-read of every sourced price and subscription-plan page (MODEL-217).

MODEL-201 and MODEL-205 filed plan and price facts whose values the verifier's
deterministic readers confirmed from a retained copy of each page. This job
fetches each of those pages again over plain HTTP and asks the same readers,
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
  replacement (several candidates, or a list or flag the job does not rewrite).
- ``unreadable``: the page fetched but the reader no longer understands it: the
  cited region is gone, no reader accepts the page, or the subject is not found.
- ``unreachable``: the page did not fetch.
- ``not_reread``: out of this job's reach. The page needs a rendered browser, or
  the value is still quarantined, or an LLM reader last verified it and the
  deterministic readers cannot read it, so their failure says nothing about the
  page. When they can, an LLM-verified value is reconfirmed like any other, and
  a value they read otherwise is ``needs_review``, never ``changed``
  (MODEL-235).

``needs_review``, ``unreadable`` and ``unreachable`` are alerts. The job never
guesses a value for them; a person re-collects.

Two keys: the old value's collector is whoever filed it. A new value is filed
by ``modelspec-price-reread`` and confirmed by the verifier's deterministic
readers. Both keys are code from one repository, so the pull request's human
reviewer is the check that the readers still read the page as intended.

Nothing here calls a model or a paid scraper.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
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
from decision.sources import CopyStore, Fetcher, FetchMode, load_sources
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
    outcome: str  # "ok", "rendered", "excluded", or the fetch error
    copy_ref: str | None = None


@dataclass
class Report:
    checked_on: date
    facts: list[FactResult] = field(default_factory=list)
    sources: dict[str, SourceFetch] = field(default_factory=dict)
    #: source_id -> unified diff lines of its cited regions, old copy to new.
    diffs: dict[str, list[str]] = field(default_factory=dict)
    overdue: list[str] = field(default_factory=list)

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
            "sources": {sid: {"url": s.url, "outcome": s.outcome, "copy": s.copy_ref}
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


def fetch_sources(source_ids: Iterable[str], sources: Mapping[str, Any], fetcher: Fetcher,
                  store: CopyStore) -> dict[str, SourceFetch]:
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
        elif source.fetch == FetchMode.RENDERED.value:
            fetched[sid] = SourceFetch(sid, url, "rendered")
        else:
            result = fetcher.fetch(url)
            if result.outcome == "ok":
                fetched[sid] = SourceFetch(sid, url, "ok", store.put(result.body))
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


def _readings(claim: Claim, regions: StoredRegions) -> list[Any]:
    """Every reading the deterministic readers take from the claim's cited regions."""
    found = []
    for source in claim.sources:
        for region_id in source.cited_regions:
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


def _propose(claim: Claim, regions: StoredRegions, today: date) -> tuple[list[Any], bool]:
    """New values that verify for the claim's subject, and whether the readers found
    any value at all for that subject."""
    own = _own_names(claim)
    readings = [r for r in _readings(claim, regions)
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
        if set(outcomes) <= {"rendered", "excluded"}:
            return replace(base, reason="the page needs a rendered fetch"
                           if "rendered" in outcomes else "excluded source")
        return replace(base, status=Status.UNREACHABLE, reason="; ".join(outcomes))

    copies = {sid: (next(s.snapshot_ref for s in old_sources if s.source_id == sid),
                    f.copy_ref) for sid, f in ok.items()}
    pinned = tuple(s.model_copy(update={"snapshot_ref": ok[s.source_id].copy_ref})
                   if s.source_id in ok else s for s in old_sources)
    claim = replace(claim, sources=pinned)
    base = replace(base, copies=copies)

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
        write: bool = False, at: datetime | None = None) -> Report:
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
        (s.source_id for _, claim, _ in scoped for s in claim.sources), sources, fetcher, store)
    results = [reread_fact(t, c, report.sources, regions, today, root, llm)
               for t, c, llm in scoped]

    # Some servers answer a plain fetch now and then with a script shell, a bot wall
    # or a 403. A page whose facts would alert is fetched once more first.
    retryable = {Status.UNREADABLE, Status.UNREACHABLE}
    retry = sorted({sid for r in results if r.status in retryable for sid in r.source_ids})
    if retry:
        again = fetch_sources(retry, sources, fetcher, store)
        fresh = {sid for sid, f in again.items()
                 if f.outcome == "ok" and f.copy_ref != report.sources[sid].copy_ref}
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
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    parser.add_argument("--retain-only-cited", action="store_true",
                        help="prune the copy store to cited and fetched copies (runners only)")
    parser.add_argument("--today", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)

    store = CopyStore()
    report = run(fetcher=Fetcher(user_agent=USER_AGENT), store=store,
                 today=args.today or datetime.now(UTC).date(), write=args.write)
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
