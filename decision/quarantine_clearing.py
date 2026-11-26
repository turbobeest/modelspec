"""A fresh two-reader agreement clears a mismatch quarantine (MODEL-552, Jamie 2026-11-25).

Rule 15 (``decision.cited_change``) refuses a fact or board reading whose verification log holds
an unresolved ``mismatch`` or ``unreachable`` verdict (``quarantined``). Jamie's decision: a fresh
two-reader agreement may clear a mismatch quarantine, only when all of these hold:

1. The agreement comes from a later reading than the quarantining verdict: a later day, and a
   later epoch. The verdict records no page text hash (``Verification`` has none), so a
   "different page text hash" can never be shown against it; the later epoch is the branch that
   can. The gate reads a quarantined subject in its clearing epoch,
   ``<epoch>:clear:<verdict hash>``: it is named by the verdict's own hash, so no attempt in it
   can come before the verdict, and it is the only epoch a clearing may come from.
2. Its two readers are of two distinct known families (``cited_change._check_identities``).
3. No disagreement is recorded in that epoch, nor in the epoch the subject is in: every complete
   attempt there agreed, and every answer recorded there, complete or not, is the cleared value.
   That base epoch is the one rule 15 derives for the quarantined record as filed when the
   verdict was made (``verdict_epoch``, from the claim the verdict checked in the queue); when
   that cannot be shown, nothing is cleared. The cleared record's block names it
   (``previous_epoch``) and its ``clearing_epoch``.
4. Each clearing is one line of the append-only ``CLEARINGS_FILE`` (exactly ``FIELDS``) naming the
   quarantining verdict (its target, ``verdict_sha256`` and day) and the agreement that cleared it
   (``agreement``: the hash of the attempt's exact line in the attempt log, ``line_hash``, with
   its subject, facet and epoch). A row rebuilt in another spelling, or never logged, is no match.

Only a ``mismatch`` is cleared. An ``unreachable`` verdict stays blocked: the agreement reads one
page, and does not show that the source the verdict could not reach is reachable. A subject with
more than one held verdict stays blocked, and so does a fact that carries an owner's ruling (a
ruling never lifts a quarantine, MODEL-551). The gate clears only when its caller asks
(``clear_quarantine``).

The build admits the cleared value only through such a line (``fact_cleared``,
``reading_cleared``): the line must name the winning verdict exactly, its agreement must be in the
attempt log and meet every limit above at build time, the fact or row must be at its location and
carry the cited-change block that agreement made, with that value, citing the copy under the
registered source whose URL the agreement read. A cleared fact is served exactly as a plain cited
fact: ``verification`` null, its ``citation``, and no ``derivation`` (``owner_ruling.served_fact``).
An agreement on the filed value clears too: it is the agreement, not a change, that clears.
Nothing here writes but ``append``; the gate's callers (``scripts/cited_offering.py``,
``scripts/cited_reading.py``) append the lines the gate returns.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

#: The append-only clearing log, under the data directory.
CLEARINGS_FILE = "verification/quarantine-clearings.jsonl"
RULE = "quarantine-clearing@1"
DECIDED_BY = "Jamie 2026-11-25 (MODEL-552)"
#: Exactly the fields of a clearing line.
FIELDS = ("rule", "decided_by", "target", "verdict_sha256", "verdict_date", "subject", "facet",
          "epoch", "agreement", "value", "cleared_at")
CLEAR_MARK = ":clear:"
_HEX = re.compile(r"[0-9a-f]{64}")
_REF = re.compile(r"sha256:[0-9a-f]{64}")

Key = tuple[str, str, str]


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      default=str)


def verdict_sha256(row: Mapping[str, Any]) -> str:
    """The quarantining verdict's id: the sha256 of its canonical JSON (a day is its ISO text)."""
    return "sha256:" + hashlib.sha256(_json(dict(row)).encode("utf-8")).hexdigest()


def clearing_epoch(base: str, verdict: str) -> str:
    """The epoch a clearing agreement is read in: the subject's epoch, marked with the verdict."""
    return f"{base}{CLEAR_MARK}{verdict.removeprefix('sha256:')}"


def base_epoch(epoch: Any, verdict: str) -> str | None:
    """The subject's epoch a clearing epoch was opened in, or ``None`` if it is not that
    verdict's clearing epoch."""
    suffix = CLEAR_MARK + verdict.removeprefix("sha256:")
    if not isinstance(epoch, str) or not epoch.endswith(suffix) or len(epoch) == len(suffix):
        return None
    return epoch[:-len(suffix)]


def clearable(held: Sequence[tuple[Key, Mapping[str, Any]]]) -> str | None:
    """Why the held verdicts cannot be cleared, or ``None``: exactly one, a mismatch."""
    if len(held) != 1:
        return f"{len(held)} held verdicts; a clearing clears exactly one"
    if held[0][1].get("outcome") != "mismatch":
        return "an unreachable verdict is not cleared by an agreement"
    return None


def _day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _at(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else None
    try:
        at = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return at if at.tzinfo is not None else None


def later_than(verdict: Mapping[str, Any], at: datetime) -> bool:
    """Whether ``at`` is on a later UTC day than the verdict's day."""
    day = _day(verdict.get("date"))
    return day is not None and at.astimezone(UTC).date() > day


def _canonical(value: Any, facet_id: str) -> str:
    from decision.cited_reader import canonical

    return canonical(value, facet_id)


def epoch_problem(entries: Sequence[Mapping[str, Any]], value: Any, facet_id: str) -> str | None:
    """A disagreement recorded among ``entries``: a complete attempt that did not agree, or any
    recorded answer (agreed, or inside an incomplete attempt) that is not ``value``."""
    want = _canonical(value, facet_id)
    for entry in entries:
        if entry.get("complete"):
            if entry.get("agreed") is not True:
                return "a complete attempt in the epoch did not agree"
            if _canonical(entry.get("agreed_value"), facet_id) != want:
                return "an agreement in the epoch is on another value"
        else:
            for reader in entry.get("readers") or ():
                if isinstance(reader, Mapping) and "value" in reader \
                        and _canonical(reader["value"], facet_id) != want:
                    return "an answer in an incomplete attempt in the epoch is another value"
    return None


def agreement_problem(attempt: Mapping[str, Any], value: Any, facet_id: str) -> str | None:
    """Why ``attempt`` is not a two-reader agreement on ``value`` made through the harness."""
    from types import SimpleNamespace

    from decision.cited_change import _check_identities

    readers = attempt.get("readers")
    if not (attempt.get("complete") is True and attempt.get("agreed") is True
            and attempt.get("harness") is True
            and all(_HEX.fullmatch(str(attempt.get(k) or ""))
                    for k in ("prompt_sha256", "page_sha256", "text_sha256"))
            and isinstance(readers, list) and len(readers) == 2
            and all(isinstance(r, Mapping) and "value" in r for r in readers)):
        return "the agreement is not a complete agreed harness attempt with its hashes"
    pair = [SimpleNamespace(**{k: r.get(k) for k in ("reader_id", "family", "version")})
            for r in readers]
    if _check_identities(pair) is not None:
        return "the agreement's readers are not two distinct known families"
    want = _canonical(value, facet_id)
    if any(_canonical(v, facet_id) != want
           for v in (readers[0]["value"], readers[1]["value"], attempt.get("agreed_value"))):
        return "the agreement is not on the cleared value"
    if _at(attempt.get("at")) is None:
        return "the agreement has no zoned time"
    return None


def line_hash(raw: str) -> str:
    """An attempt's id for a clearing: the sha256 of its line in the attempt log, byte for byte
    (without the newline). A row rebuilt with the same fields in another spelling is not it."""
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AttemptLog:
    """The rule-15 attempt log as its raw lines: each parsed once (a repeated key refuses), and
    each found by the hash of its exact bytes."""

    def __init__(self, lines: Sequence[str] = ()):
        from decision.owner_ruling import loads

        self.lines = tuple(raw for raw in lines if raw.strip())
        self.entries: tuple[dict[str, Any], ...] = tuple(loads(raw) for raw in self.lines)
        if not all(isinstance(e, dict) for e in self.entries):
            raise ValueError("an attempt line is not a JSON object")
        self.by_hash: dict[str, list[dict[str, Any]]] = {}
        for raw, entry in zip(self.lines, self.entries, strict=True):
            self.by_hash.setdefault(line_hash(raw), []).append(entry)

    @classmethod
    def read(cls, path: Path) -> AttemptLog:
        if not path.is_file():
            return cls()
        return cls(path.read_text(encoding="utf-8").split("\n"))

    def keyed(self, subject: str, facet: str, epoch: str) -> list[dict[str, Any]]:
        return [e for e in self.entries
                if (e.get("subject"), e.get("facet"), e.get("epoch")) == (subject, facet, epoch)]


def line(*, key: Key, verdict: Mapping[str, Any], subject: str, facet: str, epoch: str,
         attempt_line: str, value: Any, at: datetime) -> dict[str, Any]:
    """The clearing line for one verdict and the agreement that clears it (its exact log line)."""
    return {
        "rule": RULE,
        "decided_by": DECIDED_BY,
        "target": {"kind": key[0], "id": key[1], "value_hash": key[2]},
        "verdict_sha256": verdict_sha256(verdict),
        "verdict_date": str(verdict.get("date")),
        "subject": subject,
        "facet": facet,
        "epoch": epoch,
        "agreement": line_hash(attempt_line),
        "value": value,
        "cleared_at": at.astimezone(UTC).replace(microsecond=0).isoformat(),
    }


_RULE_15 = "two-readers-"
_OWNER_RULING = "owner-ruling@1"
#: The verification queue, under the data directory: every claim filed and every check made.
QUEUE_FILE = "verification/queue/events.jsonl"

Settings = Callable[[Mapping[str, Any]], bool]


def _event_at(event: Mapping[str, Any]) -> datetime | None:
    at = _at(event.get("at"))
    if at is None:
        try:
            naive = datetime.fromisoformat(str(event.get("at")))
        except ValueError:
            return None
        at = naive.replace(tzinfo=UTC)  # the queue's own rule: no zone means UTC
    return at


def _event_target(event: Mapping[str, Any]) -> str | None:
    target = (event.get("claim") or {}).get("target") if event.get("event") == "collected" \
        else event.get("target")
    return target.get("id") if isinstance(target, Mapping) else None


def queue_history(path: Path, ids: set[str]) -> dict[str, list[dict[str, Any]]]:
    """Target id -> its ``collected``, ``checked`` and ``retired`` events, in queue order (by
    time, a later line on a tie), for the ids asked for. An absent queue has none."""
    from decision.owner_ruling import loads

    rows: dict[str, list[tuple[datetime, int, dict[str, Any]]]] = {}
    if not ids or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        for index, raw in enumerate(handle):
            if ('"collected"' not in raw and '"checked"' not in raw
                    and '"retired"' not in raw) \
                    or not any(i in raw for i in ids):
                continue
            event = loads(raw)  # a repeated key refuses (MODEL-554)
            target = _event_target(event)
            at = _event_at(event)
            if target in ids and at is not None \
                    and event.get("event") in ("collected", "checked", "retired"):
                rows.setdefault(target, []).append((at, index, event))
    return {k: [e for _, _, e in sorted(v, key=lambda r: (r[0], r[1]))] for k, v in rows.items()}


def claim_binds(claim: Mapping[str, Any], verdict: Mapping[str, Any]) -> bool:
    """Whether the claim is for the value the verdict holds: its verification value, as
    ``decision.verify`` binds a claim (``claim_verification_value``; a set facet's members in any
    order), hashes to the verdict's ``value_hash``, under the verdict's own id and kind."""
    from decision.model import fact_verification_value, matching_value_hashes, unordered_facet

    target, wanted = claim.get("target") or {}, verdict.get("target") or {}
    if not isinstance(target, Mapping) or (target.get("kind"), target.get("id")) \
            != (wanted.get("kind"), wanted.get("id")) or "value" not in claim:
        return False
    conditions = claim.get("conditions") if isinstance(claim.get("conditions"), Mapping) else {}
    value = fact_verification_value({"value": claim["value"], **{
        k: conditions.get(k) for k in ("effective_from", "effective_until")}})
    unordered = False
    if wanted.get("kind") == "fact":
        from decision.registry import default

        try:
            unordered = unordered_facet(default().facet(str(claim.get("field"))))
        except KeyError:
            unordered = False
    recorded = str(wanted.get("value_hash") or "")
    try:
        return recorded in matching_value_hashes(value, [recorded], unordered=unordered)
    except (TypeError, ValueError):
        return False


def check_binds(check: Mapping[str, Any], verdict: Mapping[str, Any],
                field: Any) -> bool | None:
    """Whether a check is shown to cover the verdict's value: ``True`` when its own target value
    hash, or the ``expected`` value its diff records for ``value``, is the verdict's; ``False``
    when either names another value; ``None`` when the check does not say."""
    target = check.get("target") if isinstance(check.get("target"), Mapping) else {}
    recorded = target.get("value_hash")
    if recorded is not None:
        return str(recorded) == str((verdict.get("target") or {}).get("value_hash") or "")
    expected = [d["expected"] for d in check.get("diff") or ()
                if isinstance(d, Mapping) and d.get("field") == "value" and "expected" in d]
    if not expected:
        return None
    wanted = verdict.get("target") or {}
    return all(claim_binds({"target": {"kind": wanted.get("kind"), "id": wanted.get("id")},
                            "value": value, "field": field}, verdict) for value in expected)


def verdict_epoch(verdict: Mapping[str, Any], *, history: Sequence[Mapping[str, Any]],
                  log: AttemptLog, subject: str, facet: str, first: str,
                  settings: Settings | None = None) -> str | None:
    """The epoch rule 15 derives for the quarantined record as it was filed when ``verdict`` was
    made, or ``None`` when that cannot be shown. ``history`` is the verdict target's queue events
    (``queue_history``). The check the verdict records is its ``checked`` event (same target,
    outcome and UTC day; only the latest such that day), and the record as filed is the claim it
    checked, for the very value the verdict holds (``claim_binds``). The check must be shown to
    cover that claim: either the check itself names the verdict's value (``check_binds``: its
    target value hash, or its diff's ``expected`` value), and the claim is the latest for that
    value before it; or the check does not say, and the claim is the one it follows in queue
    order, with no filing for another value in between. A check that names another value, or a
    pairing that cannot be shown, supplies nothing.
    A claim the rule-15 gate filed (method ``two-readers-...``) put the record in the re-read
    epoch of the agreed harness attempt that read the copy it cites, logged at or before the
    claim was filed and before the check, in the queue's time order
    (``<first>:reread:<text hash>``; a fact's is ``reread:<text hash>``, as ``fact_epoch``); any
    other claim left it in its first epoch (``initial``, or a reading's settings epoch). A claim
    under an owner's ruling, a claim ``settings`` rejects (a reading's settings are not shown to
    be this row's), no matching check or no such claim before it cannot be shown."""
    target = (verdict.get("target") or {}).get("id")
    day = _day(verdict.get("date"))
    pair = None
    # Only the newest matching check of the day may supply the epoch: if it cannot be bound to
    # the verdict's value, nothing clears (an older same-day check is never a fallback).
    matching = [i for i, event in enumerate(history)
                if event.get("event") == "checked" and _event_target(event) == target
                and event.get("outcome") == verdict.get("outcome") and day is not None
                and (at := _event_at(event)) is not None and at.astimezone(UTC).date() == day]
    if matching:
        index = matching[-1]
        event = history[index]
        filed = [e for e in history[:index]
                 if e.get("event") == "collected" and _event_target(e) == target]
        covers = check_binds(event, verdict, (filed[-1].get("claim") or {}).get("field")) \
            if filed else False
        if covers is None:
            filed = filed[-1:]  # the claim it follows, nothing for another value in between
        binding = [e for e in filed if claim_binds(e.get("claim") or {}, verdict)] \
            if covers is not False else []
        # A claim retired before the check (``Queue.retire``, MODEL-557) was not what it covered.
        start = max((i for i, e in enumerate(history[:index]) if binding and e is binding[-1]),
                    default=index)
        if binding and not any(e.get("event") == "retired" and _event_target(e) == target
                               for e in history[start + 1:index]):
            pair = (binding[-1], event)
    if pair is None:
        return None
    filed_event, checked = pair
    claim = filed_event["claim"]
    if settings is not None and not settings(claim):
        return None
    method = str((claim.get("collector") or {}).get("method") or "")
    if method == _OWNER_RULING:
        return None
    if not method.startswith(_RULE_15):
        return first
    copies = {str(ref.get("snapshot_ref")) for ref in claim.get("sources") or ()
              if isinstance(ref, Mapping)}
    filed_at, checked_at = _event_at(filed_event), _event_at(checked)
    for entry in reversed(log.entries):
        at = _at(entry.get("at"))
        if (entry.get("subject"), entry.get("facet")) == (subject, facet) \
                and entry.get("complete") is True and entry.get("agreed") is True \
                and entry.get("harness") is True and at is not None and filed_at is not None \
                and checked_at is not None and at <= filed_at and at < checked_at \
                and f"sha256:{entry.get('page_sha256')}" in copies \
                and _HEX.fullmatch(str(entry.get("text_sha256") or "")):
            prefix = "" if first == "initial" else first + ":"
            return f"{prefix}reread:{entry['text_sha256']}"
    return None


def reading_settings(row: Mapping[str, Any]) -> Settings:
    """Whether a claim was filed for this reading's settings: its conditions carry the row's
    ``effort`` and ``harness``, and its names the row's ``model_id_as_evaluated``."""
    def same(claim: Mapping[str, Any]) -> bool:
        conditions = claim.get("conditions") or {}
        return isinstance(conditions, Mapping) \
            and "effort" in conditions and "harness" in conditions \
            and conditions.get("effort") == row.get("effort") \
            and conditions.get("harness") == row.get("harness") \
            and row.get("model_id_as_evaluated") in (claim.get("names") or ())
    return same


def line_problem(entry: Any, *, verdict: Mapping[str, Any], subject: str, facet: str,
                 ids: Callable[[str], bool], log: AttemptLog, first: str,
                 history: Sequence[Mapping[str, Any]], cutoff: date,
                 settings: Settings | None = None) -> tuple[str, Mapping[str, Any] | None]:
    """``(problem, attempt)``: why ``entry`` does not clear ``verdict`` for this subject and facet
    (empty when it does), and the agreement it names when its exact line is logged. ``ids`` says
    whether a target id is the subject's own; ``first`` is the subject's first epoch and
    ``history`` the verdict target's queue events (``verdict_epoch``); ``cutoff`` is the last day
    the build may know."""
    if not isinstance(entry, Mapping) or set(entry) != set(FIELDS):
        return f"a clearing has exactly {len(FIELDS)} fields", None
    if entry["rule"] != RULE or entry["decided_by"] != DECIDED_BY:
        return "the clearing names another rule", None
    target, wanted = entry["target"], verdict.get("target") or {}
    if not isinstance(target, Mapping) or set(target) != {"kind", "id", "value_hash"} \
            or any(target.get(k) != wanted.get(k) for k in ("kind", "id")) \
            or str(target.get("value_hash") or "") != str(wanted.get("value_hash") or ""):
        return "the clearing names another verdict's target", None
    if not isinstance(target["id"], str) or not ids(target["id"]):
        return "the clearing's target is not this subject's", None
    if verdict.get("outcome") != "mismatch":
        return "only a mismatch is cleared", None
    if entry["verdict_sha256"] != verdict_sha256(verdict) \
            or entry["verdict_date"] != str(verdict.get("date")):
        return "the clearing names another verdict", None
    if (entry["subject"], entry["facet"]) != (subject, facet):
        return "the clearing is for another subject or facet", None
    base = base_epoch(entry["epoch"], entry["verdict_sha256"])
    if base is None:
        return "the clearing's epoch is not the verdict's clearing epoch", None
    if not isinstance(entry["agreement"], str) or not _REF.fullmatch(entry["agreement"]):
        return "the clearing names no agreement", None
    found = log.by_hash.get(entry["agreement"], [])
    if len(found) != 1:
        return "the clearing's agreement is not a line of the attempt log", None
    attempt = found[0]
    if (attempt.get("subject"), attempt.get("facet"), attempt.get("epoch")) \
            != (subject, facet, entry["epoch"]):
        return "the agreement is for another subject, facet or epoch", None
    problem = agreement_problem(attempt, entry["value"], facet)
    if problem is not None:
        return problem, None
    at, cleared = _at(attempt["at"]), _at(entry["cleared_at"])
    if not later_than(verdict, at):
        return "the agreement is not on a later day than the verdict", None
    if cleared is None or cleared < at or cleared.astimezone(UTC).date() > cutoff:
        return "the clearing time is before its agreement or after the build's day", None
    derived = verdict_epoch(verdict, history=history, log=log, subject=subject, facet=facet,
                            first=first, settings=settings)
    if derived is None:
        return "the record's epoch at the verdict cannot be shown", None
    if base != derived and not _board_base(base, derived, first, settings, attempt):
        return "the clearing's base epoch is not the record's epoch at the verdict", None
    for epoch in (entry["epoch"], base):
        problem = epoch_problem(log.keyed(subject, facet, epoch), entry["value"], facet)
        if problem is not None:
            return problem, None
    return "", attempt


def _board_base(base: str, derived: str, first: str, settings: Settings | None,
                attempt: Mapping[str, Any]) -> bool:
    """A board reading filed in its settings epoch (``first``) may be cleared in a board epoch
    of it (MODEL-555): the epoch the gate read the row in once the board's cited region changed,
    ``<first>:board:<region hash>``. The agreement must have logged that very region hash. The
    disagreements counted are then the clearing epoch's and that board epoch's, as the gate
    counts them; a split under an older board region does not block."""
    from decision.cited_change import is_board_epoch

    region = is_board_epoch(base, first)
    return settings is not None and derived == first and region is not None \
        and attempt.get("board_region_sha256") == region


def _block(record: Mapping[str, Any]) -> Mapping[str, Any] | None:
    derivation = record.get("derivation") if isinstance(record, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def is_cleared(record: Mapping[str, Any]) -> bool:
    """The record carries a cited-change block a clearing made (it names its clearing epoch)."""
    block = _block(record)
    return block is not None and "clearing_epoch" in block


def made_by(record: Mapping[str, Any], attempt: Mapping[str, Any], *, epoch: str, base: str,
            sources: Mapping[str, str]) -> bool:
    """Whether the record carries the cited-change block ``attempt`` made in ``epoch`` from
    ``base``, and cites that copy under the registered source whose URL the agreement read: the
    page and text hashes and URL are the attempt's, both recorded readers are its readers (id,
    family, version, value) and were sent its prompt."""
    block = _block(record)
    if block is None or block.get("clearing_epoch") != epoch \
            or block.get("previous_epoch") != base:
        return False
    readers = block.get("readers")
    if not isinstance(readers, list) or len(readers) != 2 \
            or not all(isinstance(r, Mapping) for r in readers):
        return False
    fields = ("reader_id", "family", "version", "value")
    if sorted(_json({k: r.get(k) for k in fields}) for r in readers) \
            != sorted(_json({k: r.get(k) for k in fields}) for r in attempt["readers"]):
        return False
    copy = f"sha256:{attempt['page_sha256']}"
    return (block.get("sha256") == attempt["page_sha256"]
            and block.get("text_sha256") == attempt["text_sha256"]
            and block.get("url") == attempt.get("url")
            and all(r.get("prompt_sha256") == attempt["prompt_sha256"] for r in readers)
            and any(isinstance(ref, Mapping) and ref.get("snapshot_ref") == copy
                    and sources.get(str(ref.get("source_id"))) == attempt.get("url")
                    for ref in record.get("sources") or ()))


def _clears(record: Mapping[str, Any], *, verdict: Mapping[str, Any], subject: str, facet: str,
            ids: Callable[[str], bool], value: Any, clearings: Sequence[Mapping[str, Any]],
            log: AttemptLog, first: str, sources: Mapping[str, str],
            history: Mapping[str, Sequence[Mapping[str, Any]]], cutoff: date,
            settings: Settings | None = None) -> bool:
    events = history.get(str((verdict.get("target") or {}).get("id")), ())
    for entry in clearings:
        problem, attempt = line_problem(entry, verdict=verdict, subject=subject, facet=facet,
                                        ids=ids, log=log, first=first, history=events,
                                        cutoff=cutoff, settings=settings)
        if problem or attempt is None:
            continue
        base = base_epoch(entry["epoch"], entry["verdict_sha256"])
        if _canonical(value, facet) == _canonical(entry["value"], facet) \
                and made_by(record, attempt, epoch=entry["epoch"], base=base, sources=sources):
            return True
    return False


def fact_cleared(fact: Mapping[str, Any], subject: str, *, verdict: Mapping[str, Any],
                 clearings: Sequence[Mapping[str, Any]], log: AttemptLog,
                 sources: Mapping[str, str], history: Mapping[str, Sequence[Mapping[str, Any]]],
                 cutoff: date) -> bool:
    """Whether a cited fact whose winning verdict is ``verdict`` (a mismatch) is admitted on a
    clearing line. ``subject`` is the fact's owner as the build places it. The fact's stored id,
    when any, is its location id; it carries no owner's ruling; its value and state are the
    cleared value's; and it carries the block its clearing agreement made."""
    from decision.owner_ruling import has_ruling

    facet = str(fact.get("facet"))
    location = f"{subject}#{facet}"
    stored = fact.get("id")
    if has_ruling(fact) or (stored is not None and stored != location):
        return False
    value = fact.get("value")
    if fact.get("state") != ("not_disclosed" if value is None else "known"):
        return False
    return _clears(fact, verdict=verdict, subject=subject, facet=facet,
                   ids=lambda rid: rid == location, value=value, clearings=clearings,
                   log=log, first="initial", sources=sources, history=history, cutoff=cutoff)


def reading_cleared(row: Mapping[str, Any], subject: str, *, verdict: Mapping[str, Any],
                    owns: Callable[[str], bool], clearings: Sequence[Mapping[str, Any]],
                    log: AttemptLog, sources: Mapping[str, str],
                    history: Mapping[str, Sequence[Mapping[str, Any]]], cutoff: date) -> bool:
    """Whether a cited board reading's held ``verdict`` (a mismatch on one of its ids, ``owns``)
    is cleared for this row: the line's base epoch is the one rule 15 derives for the record the
    verdict checked, which must be shown to have this row's settings (``verdict_epoch``), and the
    row carries the block the agreement made, with its score."""
    from decision.cited_change import BENCHMARK_PREFIX, READING_KEYS, reading_epoch

    facet = BENCHMARK_PREFIX + str(row.get("benchmark_id"))
    first = reading_epoch({k: row.get(k) for k in READING_KEYS})
    return _clears(row, verdict=verdict, subject=subject, facet=facet, ids=owns,
                   value=row.get("score"), clearings=clearings, log=log, first=first,
                   sources=sources, history=history, cutoff=cutoff,
                   settings=reading_settings(row))


def read_clearings(path: Path) -> list[dict[str, Any]]:
    """Every line of the clearing log as an object; an absent file is empty. Raises
    ``ValueError`` on a line that is not a JSON object or repeats a key."""
    from decision.owner_ruling import read_lines

    return read_lines(path)


def append(lines: Sequence[Mapping[str, Any]], data_dir: str | Path) -> None:
    """Append clearing lines to the data directory's log. Append-only; nothing is rewritten."""
    if not lines:
        return
    path = Path(data_dir) / CLEARINGS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for entry in lines:
            if set(entry) != set(FIELDS):
                raise ValueError("a clearing line has exactly its fields")
            handle.write(json.dumps(dict(entry), sort_keys=True, ensure_ascii=False) + "\n")
