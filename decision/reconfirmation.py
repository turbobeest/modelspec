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

The record is the normal ``RULE`` block with ``reconfirmed: true`` and ``previous_state``. The
gate asks ``reconfirmation_problem`` of the fact as a writer files it, and so do the build
(``decision.snapshot``) and the site loader (``pipeline.load``): one test. A fact whose block
claims a reconfirmation and fails it is kept out of the build. Nothing here writes.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, date, datetime
from types import SimpleNamespace
from typing import Any

#: The block key that marks a reconfirmation.
MARK = "reconfirmed"
DECIDED_BY = "orchestrator 2026-11-26 (MODEL-572, J11)"
STATES = frozenset({"known", "not_disclosed"})


def _block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def is_reconfirmation(fact: Mapping[str, Any]) -> bool:
    """The fact's cited-change block claims a reconfirmation (it may still fail the test)."""
    block = _block(fact)
    return block is not None and MARK in block


def _day(value: Any) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _retrieved_day(value: Any) -> date | None:
    try:
        when = datetime.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None
    if when is None or when.tzinfo is None:
        return None
    return when.astimezone(UTC).date()


def reconfirmation_problem(fact: Mapping[str, Any]) -> str | None:
    """Why ``fact`` is not a reconfirmation this rule admits, or ``None``. ``fact`` is the fact as
    filed: its value, state, sources and ``derivation.cited_change`` block."""
    from decision.cited_change import RULE, _check_identities
    from decision.cited_reader import canonical

    block = _block(fact)
    if block is None:
        return "the fact carries no cited-change block"
    if block.get(MARK) is not True:
        return "the block does not mark a reconfirmation"
    if block.get("rule") != RULE or block.get("decided_by") is None:
        return "a reconfirmation is made only by the cite-only rule"
    derivation = fact.get("derivation")
    if set(derivation) != {"cited_change"}:
        return "a reconfirmation carries no owner's ruling or other derivation"
    if any(key in block for key in ("clearing_epoch", "clearing", "epoch", "agreement")):
        return "a reconfirmation is no clearing and no correction"
    facet, state, value = fact.get("facet"), fact.get("state"), fact.get("value")
    if not isinstance(facet, str) or state not in STATES:
        return "a reconfirmation is of a known or not_disclosed fact"
    if block.get("previous_state") != state:
        return "the state is not the filed state"
    if (state == "not_disclosed") != (value is None):
        return "a not_disclosed fact has no value, and a known fact has one"
    if canonical(value, facet) != canonical(block.get("previous_value"), facet):
        return "the value is not the filed value"
    readers = block.get("readers")
    if not isinstance(readers, list) or len(readers) != 2 \
            or not all(isinstance(r, Mapping) for r in readers):
        return "a reconfirmation names two readers"
    # The gate's own identity check (``cited_change._check_identities``), on the recorded readers.
    if _check_identities([SimpleNamespace(**{n: r.get(n) for n in
                                             ("reader_id", "family", "version")})
                          for r in readers]) is not None:
        return "the readers are not of two distinct known families"
    if any(canonical(r.get("value"), facet) != canonical(value, facet) for r in readers):
        return "a reader's answer is not the filed value"
    if state == "not_disclosed" and any(r.get("finding") != "not_stated" for r in readers):
        return "a not_disclosed reconfirmation records each reader's finding"
    read = _day(block.get("read_date"))
    sources = fact.get("sources")
    if read is None or not isinstance(sources, list) or len(sources) != 1 \
            or not isinstance(sources[0], Mapping) \
            or _retrieved_day(sources[0].get("retrieved_at")) != read:
        return "the fact cites the one page read, at its read date"
    return None
