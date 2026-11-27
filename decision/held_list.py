"""The listed held facts of the private data (MODEL-491, orchestrator 2026-11-27).

Once ``retained-source-proof@1`` stops counting, a few facts stay held for an honest reason: two
readers disagreed (a split), both found the page silent where a retaining page files no absence,
or two verdicts hold the fact, which a clearing cannot clear. Each is listed in the append-only
log ``verification/held.jsonl``, one line per listing, with exactly ``FIELDS``:

    {"rule": "held-fact@1", "subject": "<card id>", "facet": "<facet>",
     "fact_id": "<card id>#<facet>", "value_hash": "<value hash of the fact as filed>",
     "reason": "split" | "silent" | "held_verdicts",
     "line": "sha256:<hash of the gate-written attempt line>" | null,
     "verdicts": ["sha256:<verdict hash>", ...], "recorded_at": "<ISO time with zone>"}

A listing stands only when it resolves (``entry_problem``):
- the fact is on its card at its location id, and ``value_hash`` binds its value as filed;
- ``split`` or ``silent``: ``line`` is the hash of exactly one attempt line for this subject and
  facet that the gate tagged with that reason (``kind``, written by ``read_page`` under the line's
  hash, never a flag a hand-appended line declares for itself). It must be a complete harness
  attempt with its prompt, page and text hashes. It must carry its two readers' answers, from
  two distinct known families, which differ for a split, and are both null, with
  ``agreed_value`` null, for a silent read. Its ``filed_value`` must be the held fact's value.
  ``verdicts`` is empty.
- ``held_verdicts``: ``line`` is null, and ``verdicts`` names two or more distinct verdicts
  (``quarantine_clearing.verdict_sha256``). Each holds the fact now
  (``cited_change.held_rows``) on its location id and its current value, and together they come
  from at least two readers (verifier agent and method). A refusal before any read writes no
  line, so these verdicts are its justification.

The latest listing of a fact decides. It no longer applies once a clearing cleared after it
releases the fact by the shared test the gate and the build use
(``quarantine_clearing.fact_released``), for that fact and its value. That is how a hold ends:
the log is never rewritten. The build serves a standing listing as held, never cited or
verified, and does not count it as a gap. A listing that does not resolve fails the build, and an
unlisted gap still fails it. The site loader withholds a standing listing too.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HELD_FILE = "verification/held.jsonl"
RULE = "held-fact@1"
FIELDS = ("rule", "subject", "facet", "fact_id", "value_hash", "reason", "line", "verdicts",
          "recorded_at")
REASONS = ("split", "silent", "held_verdicts")
_REF = re.compile(r"sha256:[0-9a-f]{64}")
_HEX64 = re.compile(r"[0-9a-f]{64}")


def read(path: Path) -> list[dict[str, Any]]:
    """The listing lines, parsed by the refusing reader (a repeated key refuses)."""
    from decision.owner_ruling import loads

    if not path.is_file():
        return []
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            entry = loads(raw)
            if not isinstance(entry, dict):
                raise ValueError("a held line is not a JSON object")
            out.append(entry)
    return out


def _at(value: Any) -> datetime | None:
    try:
        when = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return when if when.tzinfo is not None else None


def entry_problem(entry: Mapping[str, Any], *, fact: Mapping[str, Any] | None, log: Any,
                  verdicts: Mapping[tuple[str, str, str], Any]) -> str | None:
    """Why one listing does not resolve, or ``None``. ``fact`` is the card's fact at the
    listing's location (``None`` when there is none), ``log`` the attempt log
    (``quarantine_clearing.AttemptLog``) and ``verdicts`` the verification log ranked by the
    build's own rule."""
    from decision.cited_change import _check_identities, held_rows
    from decision.model import fact_verification_value, matching_value_hashes
    from decision.quarantine_clearing import _canonical, verdict_sha256
    from decision.retained_correction import _unordered

    if set(entry) != set(FIELDS) or entry.get("rule") != RULE:
        return "a held line has exactly its fields and rule"
    subject, facet = entry.get("subject"), entry.get("facet")
    if not isinstance(subject, str) or not isinstance(facet, str) \
            or entry.get("fact_id") != f"{subject}#{facet}":
        return "the held line names no location id"
    if _at(entry.get("recorded_at")) is None:
        return "the held line has no zoned time"
    if fact is None:
        return "the held line names a fact that is not on its card"
    if fact.get("id") not in (None, entry["fact_id"]):
        return "the fact's stored id is not its location id"
    value = fact_verification_value(fact)
    unordered = _unordered(facet)
    if not _REF.fullmatch(str(entry.get("value_hash") or "")) \
            or not matching_value_hashes(value, [entry["value_hash"]], unordered=unordered):
        return "the held line names another value of the fact"
    reason = entry.get("reason")
    if reason not in REASONS:
        return "the held line names no known reason"
    if reason == "held_verdicts":
        listed = entry.get("verdicts")
        if entry.get("line") is not None or not isinstance(listed, list) \
                or not all(isinstance(v, str) and _REF.fullmatch(v) for v in listed) \
                or len(set(listed)) != len(listed) or len(listed) < 2:
            return "a double hold names two or more distinct verdicts and no line"
        try:
            holding = {verdict_sha256(row): row for key, row in
                       held_rows(verdicts, (entry["fact_id"],), fact)
                       if key[1] == entry["fact_id"]
                       and matching_value_hashes(value, [key[2]], unordered=unordered)}
        except (KeyError, TypeError, AttributeError, ValueError):
            return "the fact's verification record cannot be read"
        if not set(listed) <= set(holding):
            return "a listed verdict does not hold this fact's id and value"
        readers = {(str((holding[v].get("verifier") or {}).get("agent") or ""),
                    str((holding[v].get("verifier") or {}).get("method") or ""))
                   for v in listed}
        if len(readers) < 2:
            return "a double hold's verdicts come from fewer than two readers"
        return None
    if entry.get("verdicts") != [] or not isinstance(entry.get("line"), str) \
            or not _REF.fullmatch(entry["line"]):
        return "a split or silent hold names one attempt line and no verdicts"
    found = log.by_hash.get(entry["line"], [])
    if len(found) != 1:
        return "the held line's attempt is not a line of the attempt log"
    attempt = found[0]
    if (attempt.get("subject"), attempt.get("facet")) != (subject, facet):
        return "the attempt line is for another fact"
    # Only what the gate wrote into the line, under its hash: never self-declared flags alone.
    if attempt.get("kind") != reason:
        return "the attempt line is not one the gate tagged with this reason"
    if attempt.get("complete") is not True or attempt.get("harness") is not True \
            or not all(_HEX64.fullmatch(str(attempt.get(k) or ""))
                       for k in ("prompt_sha256", "page_sha256", "text_sha256")):
        return "the attempt line is not a complete harness attempt with its hashes"
    readers = attempt.get("readers")
    if not isinstance(readers, list) or len(readers) != 2 \
            or not all(isinstance(r, Mapping) and "value" in r for r in readers):
        return "the attempt line does not carry its two readers' answers"
    from types import SimpleNamespace

    if _check_identities([SimpleNamespace(**{k: r.get(k) for k in ("reader_id", "family",
                                                                   "version")})
                          for r in readers]) is not None:
        return "the attempt's readers are not two distinct known families"
    answers = [_canonical(r["value"], facet) for r in readers]
    if reason == "split" and not (attempt.get("agreed") is False and answers[0] != answers[1]):
        return "a split hold names an attempt whose readers did not disagree"
    if reason == "silent" and not (attempt.get("agreed") is True
                                   and attempt.get("agreed_value") is None
                                   and all(r["value"] is None for r in readers)):
        return "a silent hold names an attempt whose readers did not both find nothing"
    if "filed_value" not in attempt \
            or _canonical(attempt["filed_value"], facet) != _canonical(fact.get("value"), facet):
        return "the attempt was not read against this fact's value"
    return None


def standing(entries: Sequence[Mapping[str, Any]], *, fact_at: Callable[[str, str], Any],
             log: Any, verdicts: Mapping[tuple[str, str, str], Any],
             clearings: Sequence[Mapping[str, Any]] = (), sources: Mapping[str, str] | None = None,
             history: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
             cutoff: Any = None) -> tuple[set[tuple[str, str]], list[str]]:
    """``(the (subject, facet) pairs a standing listing holds, problems)``. The latest listing
    of a fact decides. It no longer stands once a clearing releases the fact by the same shared
    test the gate and the build use (``quarantine_clearing.fact_released``), for this fact and
    its value, with a clearing line cleared after the listing. Every problem is a fixed phrase
    and a count, never an id or a value."""
    latest: dict[tuple[str, str], Mapping[str, Any]] = {}
    problems: list[str] = []
    for entry in entries:
        latest[(str(entry.get("subject")), str(entry.get("facet")))] = entry
    out: set[tuple[str, str]] = set()
    for key, entry in latest.items():
        fact = fact_at(*key)
        problem = entry_problem(entry, fact=fact, log=log, verdicts=verdicts)
        if problem is not None:
            problems.append(problem)
            continue
        if not _released(entry, fact, key, log=log, verdicts=verdicts, clearings=clearings,
                         sources=sources or {}, history=history or {}, cutoff=cutoff):
            out.add(key)
    return out, problems


def _released(entry: Mapping[str, Any], fact: Mapping[str, Any], key: tuple[str, str], *,
              log: Any, verdicts: Mapping[tuple[str, str, str], Any],
              clearings: Sequence[Mapping[str, Any]], sources: Mapping[str, str],
              history: Mapping[str, Sequence[Mapping[str, Any]]], cutoff: Any) -> bool:
    """Whether a clearing cleared after the listing releases the fact, by the gate's and the
    build's own test (``quarantine_clearing.fact_released``) for every verdict that holds it."""
    from decision.cited_change import held_rows
    from decision.quarantine_clearing import _canonical, fact_released, verdict_sha256

    if cutoff is None:
        return False
    listed_at = _at(entry["recorded_at"])
    subject, facet = key
    want = _canonical(fact.get("value"), facet)
    later = [c for c in clearings if (c.get("subject"), c.get("facet")) == key
             and _canonical(c.get("value"), facet) == want
             and (_at(c.get("cleared_at")) or listed_at) > listed_at]
    if not later:
        return False
    try:
        rows = [row for _key, row in held_rows(verdicts, (f"{subject}#{facet}",), fact)]
    except (KeyError, TypeError, AttributeError, ValueError):
        return False
    named = {c.get("verdict_sha256") for c in later}
    if not rows or not all(verdict_sha256(r) in named for r in rows):
        return False
    try:
        return all(fact_released(fact, subject, verdict=r, clearings=later, log=log,
                                 sources=sources, history=history, cutoff=cutoff, held=rows)
                   for r in rows)
    except (KeyError, TypeError, AttributeError, ValueError):
        return False


def summary(problems: Sequence[str]) -> str:
    """Counts by fixed phrase, for an error that names no fact."""
    from collections import Counter

    return "; ".join(f"{n} x {p}" for p, n in sorted(Counter(problems).items()))


def line(*, subject: str, facet: str, value_hash: str, reason: str, attempt_line: str | None,
         verdicts: Sequence[str] = (), at: datetime) -> dict[str, Any]:
    """A listing as a writer files it (the writer appends ``json.dumps(..., sort_keys=True)``)."""
    from decision.quarantine_clearing import line_hash

    return {"rule": RULE, "subject": subject, "facet": facet, "fact_id": f"{subject}#{facet}",
            "value_hash": value_hash, "reason": reason,
            "line": line_hash(attempt_line) if attempt_line is not None else None,
            "verdicts": list(verdicts), "recorded_at": at.astimezone(UTC).isoformat()}


def dumps(entry: Mapping[str, Any]) -> str:
    return json.dumps(dict(entry), sort_keys=True, ensure_ascii=False)
