"""The owner's ruling past a recorded rule-15 disagreement (MODEL-551).

Rule 15 (``decision.cited_change``) changes a value on a cite-only page only when two
readers of different families agree. A complete attempt whose readers disagreed blocks
that subject, facet and epoch for good (``prior_attempt_disagreed``): no retry can shop
for agreement. Such a fact needs the owner's ruling, and this module is the only place a
ruling is accepted.

A ruling is one line of the append-only ``verification/owner-rulings.jsonl`` in the data
directory, with exactly ``FIELDS``:

* ``subject``, ``facet``, ``epoch``: the attempt-log key it rules on;
* ``value``, ``state``: what the fact becomes (``known`` with a value of the facet's type,
  or ``not_disclosed`` with none);
* ``ruled_by`` (one of ``OWNERS``, a list in code), ``ruled_at`` (a day), ``ticket``;
* ``source_ids``: the registered cite-only sources the disagreeing readers read;
* ``resolves``: the ``attempt_id`` of each disagreeing attempt it settles;
* ``basis``: short, counts and field names only, never page text.

``ruling_problem`` checks a line against the attempt log and the source registry: an owner,
a ticket, a day no earlier than the attempts it resolves, a value of the facet's type, and
for each resolved id a complete attempt for exactly that subject, facet and epoch whose two
readers returned different values. Every source is registered on a cite-only host and was
read by a resolved attempt, and every resolved attempt read one of the sources.

A ruled fact carries the line as ``derivation.owner_ruling`` and cites each source at the
copy its resolved attempt read (``snapshot_ref``, ``retrieved_at``). ``admits`` is the
build's test (``decision.snapshot``): the fact's location, value, state and sources must
be the ruling's, and the ruling valid, or the fact is not admitted. Outwardly a ruled fact
is an admitted cited fact: ``verification`` null and the existing ``citation`` object; the
ruling block is internal and never served. Nothing here lifts a quarantine (that is the
owner's open question), and nothing here writes: ``scripts/file_owner_ruling.py`` does.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

#: Who may rule. A ruling by anyone else is refused, by the filer and by the build.
OWNERS = frozenset({"jamie"})
RULINGS_FILE = "verification/owner-rulings.jsonl"
RULE = "owner-ruling@1"
#: The collector that files a ruling's claim (``scripts/file_owner_ruling.py``).
AGENT = "owner-ruling"
#: Exactly the fields of a ruling line.
FIELDS = ("subject", "facet", "epoch", "value", "state", "ruled_by", "ruled_at", "ticket",
          "source_ids", "resolves", "basis")
STATES = frozenset({"known", "not_disclosed"})
MAX_BASIS = 400
_TICKET = re.compile(r"MODEL-[1-9][0-9]*")
_ATTEMPT = re.compile(r"sha256:[0-9a-f]{64}")
_HEX = re.compile(r"[0-9a-f]{64}")


def attempt_id(entry: Mapping[str, Any]) -> str:
    """A logged attempt's id: the sha256 of its canonical JSON. The attempt log has no ids,
    and a line is never rewritten, so its content names it."""
    text = json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value: Any, facet_id: str) -> str:
    from decision.cited_reader import canonical

    return canonical(value, facet_id)


def _exact(value: Any) -> str:
    """A value in one exact spelling: keys sorted, types kept (``30`` is not ``30.0``, ``1``
    is not ``true``), no rounding and no reordering."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def disagreed(entry: Mapping[str, Any], facet_id: str) -> bool:
    """A real rule-15 ``readers_disagree``: a complete attempt made through the harness (a
    prompt hash and a page hash recorded), whose two readers pass the gate's own identity
    check (``decision.cited_change._check_identities``: id, family and version, two distinct
    known lineages) and returned values the gate's comparison tells apart. A seeded attempt,
    a reader with no identity or two readers of one family is not one."""
    from types import SimpleNamespace

    from decision.cited_change import _check_identities

    readers = entry.get("readers")
    if not (entry.get("complete") is True and entry.get("agreed") is False
            and entry.get("harness") is True
            and _HEX.fullmatch(str(entry.get("prompt_sha256") or ""))
            and _HEX.fullmatch(str(entry.get("page_sha256") or ""))
            and isinstance(readers, list) and len(readers) == 2
            and all(isinstance(r, Mapping) and "value" in r for r in readers)):
        return False
    pair = [SimpleNamespace(**{k: r.get(k) for k in ("reader_id", "family", "version")})
            for r in readers]
    return _check_identities(pair) is None and _canonical(readers[0]["value"], facet_id) \
        != _canonical(readers[1]["value"], facet_id)


class RepeatedKeyError(ValueError):
    """A JSON object repeats a key once decoded. The message names a line, never a key."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """A JSON object whose keys are unique once decoded: ``"a"`` and its escaped spelling
    are one key."""
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise RepeatedKeyError("a JSON object repeats a key")
        out[key] = value
    return out


def loads(line: str) -> Any:
    """``json.loads`` that refuses a repeated key at any depth, in any spelling."""
    return json.loads(line, object_pairs_hook=_unique_keys)


def read_json_lines(path: Path) -> list[Any]:
    """Every non-blank line of a JSON-lines file, decoded by ``loads``; an absent file is
    empty. The build reads ``verification/log.jsonl`` through this (MODEL-554): a row that
    repeats ``outcome`` would otherwise read as its last spelling. Raises ``RepeatedKeyError``
    naming the file, the first line and how many lines repeat a key; other decoding errors as
    ``json.loads`` raises them."""
    if not path.is_file():
        return []
    out, repeated = [], []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(loads(line))
        except RepeatedKeyError:
            repeated.append(number)
    if repeated:
        raise RepeatedKeyError(f"{path}: line {repeated[0]}: a JSON object repeats a key "
                               f"({len(repeated)} line(s) repeat a key)")
    return out


def read_lines(path: Path) -> list[dict[str, Any]]:
    """Every line of a JSON-lines file as an object; an absent file is empty. Raises
    ``ValueError`` on a line that is not a JSON object or repeats a key."""
    out = read_json_lines(path)
    if not all(isinstance(obj, dict) for obj in out):
        raise ValueError("a line is not a JSON object")
    return out


def ruling_block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The ``owner_ruling`` block of a fact (in its ``derivation``), or ``None``."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("owner_ruling") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def fact_epoch(fact: Mapping[str, Any]) -> str:
    """The fact's epoch by rule 15's own function (``decision.cited_change.fact_epoch``),
    never by its ruling block: a block cannot choose the epoch it is checked in. A ruled fact
    keeps the cited-change block it had, so a ruling in a re-read epoch stays in it."""
    from decision.cited_change import fact_epoch as rule_15_epoch

    return rule_15_epoch(fact)


def cited_change_logged(fact: Mapping[str, Any], subject: str,
                        attempts: Sequence[Mapping[str, Any]]) -> bool:
    """Whether the fact's cited-change block (which names its re-read epoch) is one the gate
    made: a complete agreed harness attempt for this subject and facet read the page the block
    records (``page_sha256`` equals its ``sha256``, and the logged ``text_sha256``, the hash
    the epoch is named by, equals its ``text_sha256``) with the prompt each recorded reader
    was sent. Every field the epoch is made of is bound to the attempt log; an attempt logged
    before the log kept the text hash binds a block only when the block names its epoch by the
    page hash. A fact with no such block is in ``initial`` and passes. A fabricated block
    cannot choose the epoch a ruling is checked in."""
    from decision.cited_change import cited_change_block

    block = cited_change_block(fact)
    if block is None:
        return True
    readers = block.get("readers")
    if not isinstance(readers, list) or not readers \
            or not all(isinstance(r, Mapping) for r in readers):
        return False
    prompts = {r.get("prompt_sha256") for r in readers}
    return any(
        (a.get("subject"), a.get("facet")) == (subject, fact.get("facet"))
        and a.get("complete") is True and a.get("agreed") is True and a.get("harness") is True
        and _HEX.fullmatch(str(a.get("page_sha256") or ""))
        and a.get("page_sha256") == block.get("sha256") and prompts == {a.get("prompt_sha256")}
        and a.get("text_sha256") == block.get("text_sha256")
        for a in attempts)


def ruling_claim_events(events_path: Path) -> tuple[dict[str, dict[str, Any]],
                                                     dict[str, tuple[dict[str, Any], ...]]]:
    """``(claims, history)`` for each fact whose latest filed claim (the latest ``collected``
    event in the queue, ordered as ``decision.verify.Queue``: by time, no zone means UTC, a
    later line on a tie) was filed by the owner-ruling filer. ``claims`` maps the fact id to
    that claim; ``history`` to every ``collected`` and ``checked`` event for the fact, in queue
    order, so a build as of an earlier day can find the claim that stood then. Any later
    admitted change files a later claim, so a fact absent here has no standing ruling."""
    if not events_path.is_file():
        return {}, {}
    events: dict[str, list[tuple[datetime, int, dict[str, Any]]]] = {}
    with events_path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if '"collected"' not in line and '"checked"' not in line:
                continue
            event = json.loads(line)
            kind = event.get("event")
            target = ((event.get("claim") or {}).get("target") if kind == "collected"
                      else event.get("target") if kind == "checked" else None)
            if isinstance(target, dict) and target.get("kind") == "fact" and target.get("id"):
                events.setdefault(target["id"], []).append((_event_time(event), index, event))
    claims, history = {}, {}
    for fid, rows in events.items():
        ordered = [event for _, _, event in sorted(rows, key=lambda r: (r[0], r[1]))]
        collected = [e for e in ordered if e.get("event") == "collected"]
        if collected and (collected[-1]["claim"].get("collector") or {}).get("agent") == AGENT:
            claims[fid] = collected[-1]["claim"]
            history[fid] = tuple(ordered)
    return claims, history


def latest_ruling_claims(events_path: Path) -> dict[str, dict[str, Any]]:
    """The ``claims`` half of ``ruling_claim_events``."""
    return ruling_claim_events(events_path)[0]


def _event_time(event: Mapping[str, Any]) -> datetime:
    at = datetime.fromisoformat(str(event["at"]).replace("Z", "+00:00"))
    return at if at.tzinfo is not None else at.replace(tzinfo=UTC)


def is_latest_change(ruling: Mapping[str, Any], claim: Mapping[str, Any] | None,
                     copies: Mapping[str, tuple[str, str]]) -> bool:
    """Whether the fact's latest filed claim is this ruling's own: filed by the owner-ruling
    filer under its rule, with the ruling's value and state and the copies its resolved
    attempts read. Only an admitted change files a claim, so an agreed read that the gate
    then refused supersedes nothing, while an applied change, or a later ruling, does; a
    ruling copied back over it does not stand."""
    if not isinstance(claim, Mapping):
        return False
    collector = claim.get("collector") or {}
    refs = {(str(r.get("source_id")), str(r.get("snapshot_ref")))
            for r in claim.get("sources") or () if isinstance(r, Mapping)}
    return (collector.get("agent") == AGENT and collector.get("method") == RULE
            and _exact(claim.get("value")) == _exact(ruling["value"])
            and claim.get("state") == ruling["state"]
            and refs == {(sid, copy[0]) for sid, copy in copies.items()})


def resolved_attempts(ruling: Mapping[str, Any],
                      attempts: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    """The attempts a ruling names, by id. Unknown ids are absent."""
    resolves = ruling.get("resolves")
    wanted = set(resolves) if isinstance(resolves, list) else set()
    return {i: a for a in attempts if (i := attempt_id(a)) in wanted}


def source_copies(ruling: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]],
                  sources: Mapping[str, str]) -> dict[str, tuple[str, str]]:
    """``source_id -> (snapshot_ref, retrieved_at)``: the copy the latest resolved attempt on
    that source's URL read. A source no resolved attempt read is absent."""
    by_url: dict[str, Mapping[str, Any]] = {}
    found = resolved_attempts(ruling, attempts).values()
    for entry in sorted(found, key=lambda a: str(a.get("at"))):
        by_url[str(entry.get("url"))] = entry
    out = {}
    for source_id in ruling.get("source_ids") or ():
        entry = by_url.get(sources.get(source_id, ""))
        if entry is not None:
            out[source_id] = (f"sha256:{entry.get('page_sha256')}", str(entry.get("at")))
    return out


def _day(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        day = date.fromisoformat(value)
    except ValueError:
        return None
    return day if day.isoformat() == value else None


def _at(entry: Mapping[str, Any]) -> datetime | None:
    try:
        at = datetime.fromisoformat(str(entry.get("at")))
    except ValueError:
        return None
    return at if at.tzinfo is not None else None


def ruling_problem(ruling: Any, *, attempts: Sequence[Mapping[str, Any]],
                   sources: Mapping[str, str], today: date | None = None) -> tuple[str, str] | None:
    """``(reason, detail)`` when the line is not a valid ruling, else ``None``. ``sources``
    maps registered source ids to URLs. Details carry counts and field names only."""
    from decision.cited_change import _facet, _value_fits
    from decision.retention import cite_only_status

    if not isinstance(ruling, Mapping) or set(ruling) != set(FIELDS):
        return "malformed", f"a ruling has exactly {len(FIELDS)} fields"
    if not all(isinstance(ruling[k], str) and ruling[k] for k in ("subject", "facet", "epoch")):
        return "malformed", "subject, facet and epoch are text"
    if ruling["ruled_by"] not in OWNERS:
        return "not_owner", "ruled_by is not an owner"
    if not isinstance(ruling["ticket"], str) or not _TICKET.fullmatch(ruling["ticket"]):
        return "no_ticket", "the ticket is not a MODEL ticket"
    basis = ruling["basis"]
    if not isinstance(basis, str) or not basis.strip() or len(basis) > MAX_BASIS \
            or "\n" in basis or "://" in basis:
        return "basis_invalid", f"the basis is one line of at most {MAX_BASIS} characters, no URL"
    ruled = _day(ruling["ruled_at"])
    today = today or datetime.now(UTC).date()
    if ruled is None or ruled > today:
        return "bad_ruling_date", "ruled_at is not a day, or is in the future"
    facet = _facet(ruling["facet"])
    if facet is None:
        return "unknown_facet", "the facet is not registered"
    if ruling["state"] not in STATES:
        return "value_invalid", f"the state is not one of {len(STATES)} a ruling may set"
    if ruling["state"] == "not_disclosed":
        if ruling["value"] is not None:
            return "value_invalid", "a not_disclosed ruling has no value"
    elif ruling["value"] is None or _value_fits(ruling["value"], facet) is not None:
        return "value_invalid", "the value is not a value of the facet's type"
    resolves, source_ids = ruling["resolves"], ruling["source_ids"]
    if not isinstance(resolves, list) or not resolves \
            or not all(isinstance(i, str) and _ATTEMPT.fullmatch(i) for i in resolves) \
            or len(set(resolves)) != len(resolves):
        return "no_disagreement", "resolves names no attempt id, or repeats one"
    found = resolved_attempts(ruling, attempts)
    key = (ruling["subject"], ruling["facet"], ruling["epoch"])
    if len(found) != len(resolves):
        return "no_disagreement", \
            f"{len(resolves) - len(found)} resolved id(s) name no logged attempt"
    for entry in found.values():
        if (entry.get("subject"), entry.get("facet"), entry.get("epoch")) != key:
            return "no_disagreement", "a resolved attempt is for another subject, facet or epoch"
        if not disagreed(entry, ruling["facet"]):
            return "no_disagreement", "a resolved attempt is not a complete readers_disagree"
        at = _at(entry)
        if at is None or not _HEX.fullmatch(str(entry.get("page_sha256") or "")):
            return "no_disagreement", "a resolved attempt has no zoned time or page hash"
        if at.astimezone(UTC).date() > ruled:
            return "bad_ruling_date", "ruled_at is before an attempt it resolves"
    if not isinstance(source_ids, list) or not source_ids \
            or not all(isinstance(s, str) and s for s in source_ids) \
            or len(set(source_ids)) != len(source_ids):
        return "source_mismatch", "source_ids names no source, or repeats one"
    urls = []
    for source_id in source_ids:
        url = sources.get(source_id)
        if url is None:
            return "source_mismatch", "a source is not in the source registry"
        if cite_only_status(url) is not True:
            return "source_mismatch", "a source is not on a cite-only host"
        urls.append(url)
    read = {str(entry.get("url")) for entry in found.values()}
    if set(urls) != read:
        return "source_mismatch", "the sources are not the pages the resolved attempts read"
    return None


def admits(fact: Mapping[str, Any], subject: str, *, rulings: Sequence[Mapping[str, Any]],
           attempts: Sequence[Mapping[str, Any]], sources: Mapping[str, str],
           verdicts: Mapping[tuple[str, str, str], Any] | None = None,
           claims: Mapping[str, Mapping[str, Any]] | None = None,
           today: date | None = None) -> bool:
    """Whether a fact carrying ``derivation.owner_ruling`` stands on a valid ruling.

    ``subject`` is the fact's owner as the build places it (the card's model id, or the
    offering row's own id), never the fact's stored subject. Exactly one ruling line is
    for this subject, facet and the fact's epoch (rule 15's, never the block's, from a
    cited-change block the attempt log shows the gate made: ``cited_change_logged``); the
    block is that line; the ruling is valid and the latest admitted change (its claim is the
    fact's latest, ``is_latest_change``; ``claims`` is ``latest_ruling_claims``); the fact's
    stored id (when any) is its location id; its value and state are exactly the ruling's;
    it cites exactly the ruling's sources, each at the copy its resolved attempt read; and,
    as the filer refuses, no value of the fact holds an unresolved mismatch or unreachable
    verdict. ``verdicts`` is the ranked verification log
    (``decision.snapshot._Compiler._verification_log``, the build's own index). A ruling
    for another subject, facet or epoch admits nothing."""
    from decision.cited_change import held_verdicts

    block = ruling_block(fact)
    if block is None:
        return False
    facet = str(fact.get("facet"))
    stored = fact.get("id")
    stored_subject = (fact.get("subject") or {}).get("id") \
        if isinstance(fact.get("subject"), Mapping) else None
    if (stored is not None and stored != f"{subject}#{facet}") \
            or (stored_subject is not None and stored_subject != subject):
        return False
    if not cited_change_logged(fact, subject, attempts):
        return False
    key = (subject, facet, fact_epoch(fact))
    lines = [r for r in rulings if (r.get("subject"), r.get("facet"), r.get("epoch")) == key]
    if len(lines) != 1:
        return False
    ruling = lines[0]
    if _exact(dict(block)) != _exact(dict(ruling)):
        return False
    if ruling_problem(ruling, attempts=attempts, sources=sources, today=today) is not None:
        return False
    if fact.get("state") != ruling["state"] or _exact(fact.get("value")) != _exact(ruling["value"]):
        return False
    ids = [f"{subject}#{facet}", *([stored] if isinstance(stored, str) else [])]
    try:
        if held_verdicts(verdicts or {}, ids, fact):
            return False
    except (KeyError, TypeError, AttributeError):
        return False
    copies = source_copies(ruling, attempts, sources)
    if not is_latest_change(ruling, (claims or {}).get(f"{subject}#{facet}"), copies):
        return False
    refs = [r for r in fact.get("sources") or () if isinstance(r, Mapping)]
    if sorted(str(r.get("source_id")) for r in refs) != sorted(ruling["source_ids"]) \
            or set(copies) != set(ruling["source_ids"]):
        return False
    for ref in refs:
        snapshot, at = copies[str(ref["source_id"])]
        if ref.get("snapshot_ref") != snapshot or not _same_instant(ref.get("retrieved_at"), at):
            return False
    return True


# --- one admission and one served form, for the snapshot and the site ----------------------------


def ruling_cutoff(as_of: date | None = None) -> date:
    """The last day whose rulings a build may know: ``as_of``, never later than the UTC day."""
    today = datetime.now(UTC).date()
    return min(as_of, today) if as_of is not None else today


def stands_at(fact: Mapping[str, Any], subject: str, cutoff: date,
              inputs: RulingInputs) -> bool:
    """Whether a build that knows the record up to ``cutoff`` knows the fact's ruling: the
    ruling is dated on or before ``cutoff``, and so is its own claim line, both filed (the
    latest ``collected`` event for the fact) and checked (a ``verified`` or ``cited`` event
    after it). A backdated ruling is not known before its claim was filed. Nothing is
    restored: a ruled fact a build does not know yet is withheld."""
    from datetime import time

    block = ruling_block(fact)
    day = _day(block.get("ruled_at")) if block is not None else None
    if day is None or day > cutoff:
        return False
    fid = f"{subject}#{fact.get('facet')}"
    claim = inputs.claims.get(fid)
    end = datetime.combine(cutoff, time.max, tzinfo=UTC)
    filed = checked = None
    for event in inputs.history.get(fid, ()):
        if event.get("event") == "collected":
            filed = _event_time(event) if claim is not None \
                and _exact(event.get("claim")) == _exact(claim) else None
            checked = None
        elif filed is not None and checked is None \
                and event.get("outcome") in ("verified", "cited"):
            checked = _event_time(event)
    return filed is not None and checked is not None and filed <= end and checked <= end


def has_ruling(fact: Mapping[str, Any]) -> bool:
    """The fact claims an owner ruling (``derivation.owner_ruling`` present, well formed or not)."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    return isinstance(derivation, Mapping) and "owner_ruling" in derivation


def served_fact(fact: Mapping[str, Any]) -> dict[str, Any]:
    """The fact as it is published. A ruled fact is published as a cited fact filed without a
    derivation is: the ruling and the cited-change block it keeps for its epoch (previous
    values, reader outputs, prompt hashes, manifests) are internal. Others are unchanged."""
    if has_ruling(fact):
        return {k: v for k, v in fact.items() if k != "derivation"}
    return dict(fact)


@dataclass(frozen=True)
class RulingInputs:
    """What admission reads besides the fact: the ruling lines, the rule-15 attempt log, the
    facts whose latest claim is a ruling's, and the ranked verification log."""

    rulings: tuple[Mapping[str, Any], ...] = ()
    attempts: tuple[Mapping[str, Any], ...] = ()
    claims: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    verdicts: Mapping[tuple[str, str, str], Any] = field(default_factory=dict)
    #: Fact id -> its queue events, for the facts in ``claims`` (``ruling_claim_events``).
    history: Mapping[str, Sequence[Mapping[str, Any]]] = field(default_factory=dict)


def read_ruling_inputs(root: Path, *, verdicts: bool = True) -> RulingInputs:
    """``RulingInputs`` from a data checkout. With no ruling line, nothing else is read.
    Raises ``ValueError``, ``KeyError`` or ``TypeError`` on a malformed log."""
    from decision.cited_reader import ATTEMPTS_FILE

    root = Path(root)
    rulings = read_lines(root / RULINGS_FILE)
    if not rulings:
        return RulingInputs()
    ranked: Mapping[tuple[str, str, str], Any] = {}
    if verdicts:
        from decision.cited_change import VERIFICATION_LOG
        from decision.snapshot import _Compiler

        ranked = _Compiler._verification_log(read_json_lines(root / VERIFICATION_LOG))
    claims, history = ruling_claim_events(root / "verification/queue/events.jsonl")
    return RulingInputs(tuple(rulings), tuple(read_lines(root / ATTEMPTS_FILE)), claims, ranked,
                        history)


def ruling_refused(fact: Mapping[str, Any], subject: str, *, cited: bool, inputs: RulingInputs,
                   sources: Mapping[str, str], as_of: date | None = None) -> bool:
    """The one "ruling stands at cutoff" test for a fact that claims a ruling, for the snapshot
    and the site: refused (the fact is withheld) when it is not cited, its ruling does not
    stand as a live build checks it (``admits``: uniqueness, retrieval copies, quarantine,
    latest claim), or the build's cutoff (``ruling_cutoff(as_of)``) is before the ruling or its
    claim line (``stands_at``). A ruling dated after the UTC day is refused whatever the
    ``as_of``. A fact that claims no ruling is never refused here."""
    if not has_ruling(fact):
        return False
    return not cited or not stands_at(fact, subject, ruling_cutoff(as_of), inputs) \
        or not admits(fact, subject, rulings=inputs.rulings, attempts=inputs.attempts,
                      sources=sources, verdicts=inputs.verdicts, claims=inputs.claims)


def _same_instant(left: Any, right: Any) -> bool:
    def parse(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value if value.tzinfo is not None else None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo is not None else None

    a, b = parse(left), parse(right)
    return a is not None and b is not None and a == b
