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
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

#: Who may rule. A ruling by anyone else is refused, by the filer and by the build.
OWNERS = frozenset({"jamie"})
RULINGS_FILE = "verification/owner-rulings.jsonl"
RULE = "owner-ruling@1"
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


def disagreed(entry: Mapping[str, Any], facet_id: str) -> bool:
    """A complete attempt whose two readers returned different values (``readers_disagree``)."""
    readers = entry.get("readers")
    return (entry.get("complete") is True and entry.get("agreed") is False
            and isinstance(readers, list) and len(readers) == 2
            and all(isinstance(r, Mapping) and "value" in r for r in readers)
            and _canonical(readers[0]["value"], facet_id)
            != _canonical(readers[1]["value"], facet_id))


def read_lines(path: Path) -> list[dict[str, Any]]:
    """Every line of a JSON-lines file as an object; an absent file is empty. Raises
    ``ValueError`` on a line that is not a JSON object."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError("a line is not a JSON object")
        out.append(obj)
    return out


def ruling_block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The ``owner_ruling`` block of a fact (in its ``derivation``), or ``None``."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("owner_ruling") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def fact_epoch(fact: Mapping[str, Any]) -> str:
    """The attempt-log epoch a fact is in now: a ruling's own; after a cited change, the
    re-read epoch its recorded text hash names (as ``decision.cited_change.reread``);
    otherwise ``initial``."""
    from decision.cited_change import cited_change_block

    block = ruling_block(fact)
    if block is not None:
        return str(block.get("epoch"))
    changed = cited_change_block(fact)
    if changed is not None:
        return f"reread:{changed.get('text_sha256') or changed.get('sha256')}"
    return "initial"


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
           today: date | None = None) -> bool:
    """Whether a fact carrying ``derivation.owner_ruling`` stands on a valid ruling.

    ``subject`` is the fact's owner as the build places it (the card's model id, or the
    offering row's own id), never the fact's stored subject. Exactly one ruling line is
    for this subject, facet and the block's epoch; the block is that line; the ruling is
    valid; the fact's stored id (when any) is its location id; its value and state are the
    ruling's; and it cites exactly the ruling's sources, each at the copy its resolved
    attempt read. A ruling for another subject, facet or epoch admits nothing."""
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
    key = (subject, facet, block.get("epoch"))
    lines = [r for r in rulings if (r.get("subject"), r.get("facet"), r.get("epoch")) == key]
    if len(lines) != 1:
        return False
    ruling = lines[0]
    if json.dumps(dict(block), sort_keys=True) != json.dumps(dict(ruling), sort_keys=True):
        return False
    if ruling_problem(ruling, attempts=attempts, sources=sources, today=today) is not None:
        return False
    if fact.get("state") != ruling["state"] \
            or _canonical(fact.get("value"), facet) != _canonical(ruling["value"], facet):
        return False
    copies = source_copies(ruling, attempts, sources)
    refs = [r for r in fact.get("sources") or () if isinstance(r, Mapping)]
    if sorted(str(r.get("source_id")) for r in refs) != sorted(ruling["source_ids"]) \
            or set(copies) != set(ruling["source_ids"]):
        return False
    for ref in refs:
        snapshot, at = copies[str(ref["source_id"])]
        if ref.get("snapshot_ref") != snapshot or not _same_instant(ref.get("retrieved_at"), at):
            return False
    return True


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
