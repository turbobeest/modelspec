"""An agreed, unchanged cited-fact read files its record and read date (MODEL-572).

A fact filed with no cited-change block (a person's citation, an owner's correction of value
and state) has no read date when every source it cites is cite-only, so the data-trust audit
cannot date it. A fresh rule-15 agreement on the filed value used to file nothing
(``value_unchanged``). The decision (orchestrator, 2026-11-26, J11): such an agreement files its
record, the way ``cited_reading(allow_unchanged=True)`` already does for a board row. The
served value and state do not change; the record adds the reading and its date.

``cited_change(allow_unchanged=True)`` asks for it. Every condition of the gate's normal path
holds unchanged, licence facts included: two readers of distinct known families, blind, on a
first-party cite-only page, no disagreement logged in the fact's epoch, no held verdict, and for
``not_disclosed`` the page must show silence (``_check_silence``). On top of that:

* the fact carries no cited-change block (the rolling re-read reads one again) and no owner's
  ruling, and no quarantine clearing is asked for;
* the agreed value and state are the filed ones; an agreed other value is refused
  (``value_differs``) and files nothing. A change goes through the normal path.

The record is the normal ``RULE`` block with ``reconfirmed: true``, ``previous_state``, the epoch
it was read in and the agreement by the hash of its exact line in the attempt log (as a MODEL-573
correction names its agreement). The gate asks ``reconfirmation_problem`` of the fact as a writer
files it (``filed``), and so do the build (``decision.snapshot``) and the site loader
(``pipeline.load``): one test. It checks the served value against the logged attempt line, never
against the fact's own fields, and holds the fact while any of its values has an unresolved
verdict (``cited_change.held_rows``, the build's hold). A fact whose block claims a
reconfirmation and fails it is kept out. The writer files every source the fact cited before in
``checked_sources``, so no source leaves its provenance. Nothing here writes.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from typing import Any

#: The block key that marks a reconfirmation.
MARK = "reconfirmed"
DECIDED_BY = "orchestrator 2026-11-26 (MODEL-572, J11)"
STATES = frozenset({"known", "not_disclosed"})
#: A fact with no cited-change block and no ruling is read in this epoch (``fact_epoch``).
EPOCH = "initial"


def _block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def is_reconfirmation(fact: Mapping[str, Any]) -> bool:
    """The fact's cited-change block claims a reconfirmation (it may still fail the test)."""
    block = _block(fact)
    return block is not None and MARK in block


def fact_sha256(fact: Mapping[str, Any]) -> str:
    """The fact as the gate read it, in one spelling: a writer refuses a record read against
    another (a stale reconfirmation never overwrites a newer value, state or block)."""
    text = json.dumps(fact, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def filed(old: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    """The fact as a writer files a reconfirmation: ``retained_correction.filed_fact`` (value,
    state, the one source read, the block), with every source the fact cited before kept in
    ``checked_sources``."""
    from decision.retained_correction import filed_fact

    fact = filed_fact(old, record)
    before = [s.get("source_id") for s in old.get("sources") or () if isinstance(s, Mapping)]
    fact["checked_sources"] = list(dict.fromkeys(
        i for i in (*(old.get("checked_sources") or ()), *before) if isinstance(i, str) and i))
    return fact


def _retrieved_day(value: Any) -> date | None:
    try:
        when = datetime.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None
    if when is None or when.tzinfo is None:
        return None
    return when.astimezone(UTC).date()


def reconfirmation_problem(fact: Mapping[str, Any], subject: str, *, log: Any,
                           verdicts: Mapping[tuple[str, str, str], Any],
                           sources: Mapping[str, str], cutoff: date,
                           ids: Sequence[str] = ()) -> str | None:
    """Why ``fact`` is not a reconfirmation this rule admits, or ``None``.

    ``log`` is the attempt log (``quarantine_clearing.AttemptLog``), ``verdicts`` the verification
    log ranked by the build's own rule, ``sources`` the source registry's URLs, ``cutoff`` the
    last day the caller may know, ``ids`` further identities the fact may carry in the
    verification log (its location id and stored id are always checked)."""
    from decision.cited_change import RULE, fact_epoch
    from decision.quarantine_clearing import (
        _at,
        _block_is,
        agreement_problem,
        epoch_problem,
        line_hash,
    )
    from decision.retention import cite_only_status

    block = _block(fact)
    if block is None or block.get(MARK) is not True:
        return "the block does not mark a reconfirmation"
    if block.get("rule") != RULE:
        return "a reconfirmation is made only by the cite-only rule"
    if set(fact["derivation"]) != {"cited_change"} or "clearing_epoch" in block:
        return "a reconfirmation carries no owner's ruling, clearing or other derivation"
    facet, state, value = fact.get("facet"), fact.get("state"), fact.get("value")
    if not isinstance(facet, str) or state not in STATES \
            or (state == "not_disclosed") != (value is None):
        return "a reconfirmation is of a known fact with a value or a not_disclosed one"
    from decision.retained_correction import unresolved_holds

    try:
        # The one hold check a correction, a confirmation and a reconfirmation share (MODEL-491).
        held = unresolved_holds(fact, subject, verdicts=verdicts, log=log, ids=ids)
    except (KeyError, TypeError, AttributeError, ValueError):
        return "the fact's verification record cannot be read"
    if held:
        return f"{len(held)} value(s) of the fact hold an unresolved verdict"
    epoch, agreement = block.get("epoch"), block.get("agreement")
    if epoch != EPOCH or not isinstance(agreement, str):
        return "the block names no agreement in the epoch a plain fact is read in"
    # The agreement by its exact bytes, at its first position (as a MODEL-573 correction).
    found = [n for n, raw in enumerate(log.lines) if line_hash(raw) == agreement]
    if not found:
        return "the agreement is not a line of the attempt log"
    index = found[0]
    attempt = log.entries[index]
    if (attempt.get("subject"), attempt.get("facet"), attempt.get("epoch")) \
            != (subject, facet, epoch):
        return "the agreement is not this fact's, in the epoch the block names"
    # The served value is the logged agreement's, never the block's own fields.
    problem = agreement_problem(attempt, value, facet)
    if problem is not None:
        return problem
    if cite_only_status(attempt.get("url")) is not True:
        return "the agreement did not read a cite-only page"
    if not _block_is(fact, block, attempt, sources=sources):
        return "the record is not the block that agreement made"
    if state == "not_disclosed" and any(r.get("finding") != "not_stated"
                                        for r in block.get("readers") or ()):
        return "a not_disclosed reconfirmation records each reader's finding"
    at = _at(attempt.get("at"))
    if at is None or at.astimezone(UTC).date() > cutoff:
        return "the agreement is after this build's cutoff"
    # The read date is the logged agreement's own UTC day, never the fact's or the citation's
    # say-so: both must name it.
    day = at.astimezone(UTC).date()
    refs = fact.get("sources")
    if not isinstance(refs, list) or len(refs) != 1 or not isinstance(refs[0], Mapping) \
            or _retrieved_day(refs[0].get("retrieved_at")) != day \
            or block.get("read_date") != day.isoformat():
        return "the fact cites the one page read, on the day the agreement was logged"
    problem = epoch_problem(log.keyed(subject, facet, epoch), value, facet)
    if problem is not None:
        return problem
    own = fact_epoch(fact)
    seen = {line_hash(raw) for raw in log.lines[:index + 1]}
    for raw, later in zip(log.lines[index + 1:], log.entries[index + 1:], strict=True):
        digest = line_hash(raw)
        if digest in seen:
            continue
        seen.add(digest)
        if (later.get("subject"), later.get("facet")) == (subject, facet) \
                and later.get("epoch") not in {epoch, own}:
            return "an attempt in a later epoch was logged after the agreement"
    return None
