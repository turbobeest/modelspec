"""File the owner's ruling on a cite-only fact whose rule-15 readers disagreed (MODEL-551).

``python -m scripts.file_owner_ruling --data-dir <data checkout> --subject <id> --facet <facet>
--value <JSON> --state known|not_disclosed --ruled-by <owner> --ruled-at <YYYY-MM-DD>
--ticket MODEL-<n> --source <source id> [--source ...] --basis <counts only>
[--epoch initial] [--resolve <attempt id> ...] [--write]``

Dry-run unless ``--write``. It refuses, with one named reason and nothing written, unless
every condition holds:

* a complete ``readers_disagree`` attempt is logged for exactly this subject, facet and
  epoch (``verification/cited-attempts.jsonl``), and the epoch is the fact's current one;
* ``--ruled-by`` is an owner (``decision.owner_ruling.OWNERS``) and a ticket is given;
* the fact is not quarantined. Lifting a quarantine is the owner's open question: refused;
* the value fits the facet's ``value_type`` (``known``), or there is none (``not_disclosed``);
* the fact's stored id is its location id, and no ruling is filed for that key yet.

On success it appends the ruling line to ``verification/owner-rulings.jsonl``, files the
matching claim in ``verification/queue/events.jsonl`` (``collected``, then ``checked`` with
outcome ``cited``, ordered after every earlier event for the fact) and rewrites the one
fact: the ruling's value and state, its sources at the copy each resolved attempt read
(``snapshot_ref``, ``retrieved_at``), and ``derivation.owner_ruling``. The fact and the
claim are written from one source reference, so the data checks hold: the sources equal
the latest claim's, ``snapshot_ref`` and ``retrieved_at`` agree, and the stored id is the
location id.

Each file is read once. The plan and the write use those bytes; each append goes only to a
file that still has the planned size and sha256, and the fact file is replaced whole only
if it is unchanged. A rerun after a write that stopped part way finishes it. Nothing is
written to the verification log or the attempt log. The output is the outcome, the reason
and counts; never page text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.cited_change import VERIFICATION_LOG, LookupFailed, _facet, held_verdicts, lookup
from decision.cited_reader import ATTEMPTS_FILE
from decision.model import DETERMINISTIC, SourceRef, TargetRef, VerificationActor
from decision.owner_ruling import (
    AGENT,
    FIELDS,
    RULE,
    RULINGS_FILE,
    admits,
    attempt_id,
    cited_change_logged,
    disagreed,
    fact_epoch,
    loads,
    ruling_problem,
    source_copies,
)
from decision.verify import Claim
from scripts.refile_mixed_citations import QUEUE, canonical, event_target, event_time, write_atomic

#: Every named refusal.
REFUSALS = (
    "registry_lookup_failed", "unknown_facet", "malformed", "not_owner", "no_ticket",
    "basis_invalid", "bad_ruling_date", "value_invalid", "no_disagreement", "source_mismatch",
    "quarantined", "epoch_not_current", "fact_id_mismatch", "not_cited", "duplicate_ruling",
    "queue_ahead", "changed_since_planning",
)


class Refused(Exception):  # noqa: N818  (a named refusal, as the gate's)
    def __init__(self, reason: str, detail: str = "") -> None:
        assert reason in REFUSALS, reason
        super().__init__(reason)
        self.reason, self.detail = reason, detail


@dataclass
class Snapshot:
    """A file's bytes as planning read them (``None``: absent)."""

    path: Path
    data: bytes | None

    @classmethod
    def read(cls, path: Path) -> Snapshot:
        return cls(path, path.read_bytes() if path.is_file() else None)

    def lines(self) -> list[dict[str, Any]]:
        """Each line as JSON; a repeated key, in any spelling, is a ``ValueError``."""
        text = (self.data or b"").decode("utf-8")
        return [loads(line) for line in text.splitlines() if line.strip()]


@dataclass
class Plan:
    ruling: dict[str, Any]
    fact_id: str
    rulings: Snapshot
    queue: Snapshot
    fact_file: Snapshot
    #: Read, never written: the plan's disagreement and quarantine came from these bytes,
    #: and the write goes ahead only while they are unchanged.
    attempts: Snapshot | None = None
    verifications: Snapshot | None = None
    ruling_line: bytes = b""
    queue_lines: bytes = b""
    new_text: bytes | None = None
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def done(self) -> bool:
        return not self.ruling_line and not self.queue_lines and self.new_text is None


# --- the YAML edit -------------------------------------------------------------------------------


class _NoAliases(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class _UniqueKeys(yaml.SafeLoader):
    """``yaml.safe_load`` keeps the last of two equal keys; this loader refuses them."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, "a YAML mapping repeats a key", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def load_yaml(text: str) -> Any:
    """YAML as ``yaml.safe_load`` reads it, refusing a mapping that repeats a key."""
    try:
        return yaml.load(text, Loader=_UniqueKeys)  # noqa: S506  (a SafeLoader subclass)
    except TypeError as error:  # an unhashable key
        raise yaml.YAMLError(str(error)) from None


def _front(text: str) -> tuple[str, int]:
    """The YAML body of a card's front matter and its offset in the text."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise Refused("registry_lookup_failed", "the card has no front matter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise Refused("registry_lookup_failed", "the card's front matter is not closed")
    return "".join(lines[1:end]), len(lines[0])


def _mapping(node: yaml.Node) -> dict[str, yaml.Node]:
    return {key.value: value for key, value in node.value}


def _plain(obj: Any) -> Any:
    return json.loads(json.dumps(obj, default=str))


def replace_fact(text: str, *, card: bool, row_id: str | None, facet: str,
                 fact: dict[str, Any], expect: dict[str, Any]) -> str:
    """``text`` with one fact's block replaced and every other byte kept. The fact is
    found by its location (the card, or the offering row whose own id is ``row_id``) and
    facet, and must still be ``expect``; the result is re-parsed and must differ from the
    old data in that fact only."""
    from decision.cited_change import _row_id

    body, offset = _front(text) if card else (text, 0)
    if any(isinstance(token, yaml.AliasToken) for token in yaml.scan(body)):
        raise Refused("registry_lookup_failed", "the file uses YAML aliases")
    data, node = load_yaml(body), yaml.compose(body)
    parents = [(data, node)] if card else [
        (row, n) for row, n in zip(data or [], node.value if node is not None else [])
        if _row_id(row) == row_id]
    hits = [(parent, i, item) for parent, pnode in parents
            for i, item in enumerate(_mapping(pnode).get("facts", yaml.SequenceNode("", [])).value)
            if (parent.get("facts") or [])[i].get("facet") == facet]
    if len(hits) != 1 or hits[0][2].flow_style:
        raise Refused("registry_lookup_failed", "the fact is not in the file once, in block style")
    parent, index, item = hits[0]
    if _plain(parent["facts"][index]) != _plain(expect):
        raise Refused("changed_since_planning", "the fact file changed since planning")
    start = offset + item.start_mark.index
    # The item's end mark sits at the next token; the block ends with its last content line.
    end = offset + item.end_mark.index
    while end > start and text[end - 1] in " \t\r\n":
        end -= 1
    newline = text.find("\n", end)
    end = len(text) if newline == -1 else newline + 1
    column = item.start_mark.column
    dumped = yaml.dump(fact, Dumper=_NoAliases, sort_keys=False, default_flow_style=False,
                       allow_unicode=True, width=10**9).splitlines()
    block = "\n".join([dumped[0], *(" " * column + line for line in dumped[1:])]) + "\n"
    new = text[:start] + block + text[end:]
    parent["facts"][index] = _plain(fact)
    after = load_yaml(_front(new)[0] if card else new)
    if _plain(after) != _plain(data):
        raise Refused("registry_lookup_failed", "the edit changed more than the one fact")
    return new


# --- the plan ------------------------------------------------------------------------------------


def _source_rows(root: Path) -> dict[str, dict[str, Any]]:
    rows = load_yaml((root / "registry" / "sources.yaml").read_text("utf-8"))["sources"]
    return {row["id"]: row for row in rows}


def plan(*, data_dir: Path, subject: str, facet: str, value: Any, state: str, ruled_by: str,
         ruled_at: str, ticket: str, source_ids: list[str], basis: str, epoch: str = "initial",
         resolves: list[str] | None = None, now: datetime | None = None) -> Plan:
    now = now or datetime.now(UTC)
    root = Path(data_dir)
    facet_def = _facet(facet)
    if facet_def is None:
        raise Refused("unknown_facet", "the facet is not registered")
    try:
        found = lookup(subject, facet, root)
        registry = _source_rows(root)
    except (LookupFailed, OSError, KeyError, TypeError, yaml.YAMLError) as error:
        raise Refused("registry_lookup_failed", type(error).__name__) from None
    if (found.kind == "offering") != (facet_def.subject == "offering") or found.path is None:
        raise Refused("registry_lookup_failed", "the facet is not a facet of this subject")
    location = f"{subject}#{facet}"
    if set(found.fact_ids) != {location}:
        raise Refused("fact_id_mismatch", "the fact's stored id or subject is not its location's")
    # One snapshot of every file the plan rests on; the write checks each is unchanged.
    attempts_snapshot = Snapshot.read(root / ATTEMPTS_FILE)
    verifications = Snapshot.read(root / VERIFICATION_LOG)
    rulings = Snapshot.read(root / RULINGS_FILE)
    queue = Snapshot.read(root / QUEUE)
    fact_file = Snapshot.read(found.path)
    try:
        attempts, filed, events = (attempts_snapshot.lines(), rulings.lines(), queue.lines())
        logged = verifications.lines()
    except ValueError:
        raise Refused("malformed", "an append-only log does not parse or repeats a key") from None
    try:
        text = (fact_file.data or b"").decode("utf-8")
        load_yaml(_front(text)[0] if found.kind == "model" else text)
    except yaml.YAMLError:
        raise Refused("malformed", "the fact file does not parse or repeats a key") from None
    from decision.snapshot import _Compiler

    try:
        verdicts = _Compiler._verification_log(logged)
        held = held_verdicts(verdicts, found.fact_ids, found.fact)
    except (KeyError, TypeError, AttributeError):
        raise Refused("registry_lookup_failed", "the verification log does not parse") from None
    if held:
        raise Refused("quarantined", f"{len(held)} value(s) of this fact hold an unresolved "
                      "mismatch or unreachable verdict; lifting a quarantine is the owner's "
                      "open question, not a ruling")
    key = (subject, facet, epoch)
    disagreeing = [attempt_id(a) for a in attempts
                   if (a.get("subject"), a.get("facet"), a.get("epoch")) == key
                   and disagreed(a, facet)]
    if not disagreeing:
        raise Refused("no_disagreement", "no complete readers_disagree attempt is logged for "
                      "this subject, facet and epoch")
    ruling = {"subject": subject, "facet": facet, "epoch": epoch, "value": value, "state": state,
              "ruled_by": ruled_by, "ruled_at": ruled_at, "ticket": ticket,
              "source_ids": list(source_ids), "resolves": list(resolves or disagreeing),
              "basis": basis}
    assert set(ruling) == set(FIELDS)
    urls = {sid: str(row.get("url")) for sid, row in registry.items()}
    problem = ruling_problem(ruling, attempts=attempts, sources=urls, today=now.date())
    if problem is not None:
        raise Refused(*problem)
    # One ruling per subject, facet and epoch. The same line filed already is a write that
    # stopped part way: the rerun finishes it and appends no second line.
    same_key = [r for r in filed if (r.get("subject"), r.get("facet"), r.get("epoch")) == key]
    resuming = bool(same_key)
    if same_key and (len(same_key) > 1 or canonical(same_key[0]) != canonical(ruling)):
        raise Refused("duplicate_ruling", f"{len(same_key)} ruling(s) are filed for this "
                      "subject, facet and epoch already")
    if not cited_change_logged(found.fact, subject, attempts):
        raise Refused("epoch_not_current", "the fact's cited-change block is not one the "
                      "attempt log shows the gate made, so it names no epoch")
    if fact_epoch(found.fact) != epoch:
        raise Refused("epoch_not_current", "the fact is in another epoch than the ruling's")
    from decision.retention import cite_only_status

    if any(cite_only_status(urls.get(str(r.get("source_id")), "")) is not True
           for r in found.fact.get("sources") or [] if isinstance(r, dict)):
        raise Refused("not_cited", "the fact cites a source that is not on a cite-only host")
    copies = source_copies(ruling, attempts, urls)
    refs = [SourceRef(source_id=sid, snapshot_ref=copies[sid][0], retrieved_at=copies[sid][1],
                      cited_regions=[r["id"] for r in registry[sid].get("cited_regions") or []]
                      or ["page"])
            for sid in source_ids]
    fact = new_fact(found.fact, ruling, refs)
    claim = Claim(target=TargetRef(kind="fact", id=location), subject=subject, names=found.names,
                  field=facet, value=value,
                  collector=VerificationActor(agent=AGENT, model_family=DETERMINISTIC, method=RULE),
                  sources=tuple(refs), unit=facet_def.unit, label=facet_def.label, state=state)
    result = Plan(ruling, location, rulings, queue, fact_file, attempts_snapshot, verifications,
                  counts={"resolves": len(ruling["resolves"]), "sources": len(refs)})
    if not resuming:
        line = json.dumps(ruling, sort_keys=True, ensure_ascii=False)
        result.ruling_line = (line + "\n").encode()
    latest = None
    last = None
    try:
        for event in sorted(events, key=event_time):  # stable: equal instants keep line order
            if event_target(event) == ("fact", location):
                last = event_time(event)
                if event["event"] == "collected":
                    latest = event["claim"]
    except (KeyError, TypeError, ValueError):
        raise Refused("registry_lookup_failed", "the queue does not parse") from None
    if latest is None or canonical(latest) != canonical(claim.to_dict()):
        if last is not None and last > now:
            raise Refused("queue_ahead", "a queue event for this fact is dated after now")
        base = now.replace(microsecond=0)
        at = (max(base, last) if last is not None else base).isoformat()
        result.queue_lines = "".join(
            json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n" for event in (
                {"event": "collected", "at": at, "claim": claim.to_dict()},
                {"event": "checked", "at": at, "target": claim.target.model_dump(),
                 "outcome": "cited", "diff": []})).encode()
    if _plain(found.fact) != _plain(fact):
        text = (fact_file.data or b"").decode("utf-8")
        result.new_text = replace_fact(
            text, card=found.kind == "model", row_id=None if found.kind == "model" else subject,
            facet=facet, fact=fact, expect=found.fact).encode("utf-8")
    if result.done:
        raise Refused("duplicate_ruling", "this ruling is filed and applied already")
    # After the write the fact's latest claim is the planned one (or, on a rerun, the one filed).
    filed_claim = claim.to_dict() if result.queue_lines else latest
    if not admits(_plain(fact), subject,
                  rulings=[*filed, ruling] if not resuming else filed, attempts=attempts,
                  sources=urls, verdicts=verdicts, claims={location: filed_claim},
                  today=now.date()):
        raise Refused("malformed", "the fact as planned would not stand on its ruling")
    return result


def new_fact(old: dict[str, Any], ruling: dict[str, Any], refs: list[SourceRef]) -> dict[str, Any]:
    """The fact as the ruling calls for: value, state and sources replaced in place, every
    other key kept in its order. A source it cited before and no longer cites moves to
    ``checked_sources``, so the rule-15 gate still counts it as registered. ``derivation``
    keeps what it held (a cited-change block names the re-read epoch the ruling is in) and
    gains ``owner_ruling``."""
    new = {"value": ruling["value"], "state": ruling["state"],
           "sources": [r.model_dump(mode="json") for r in refs]}
    dropped = [r.get("source_id") for r in old.get("sources") or []
               if isinstance(r, dict) and r.get("source_id") not in {r.source_id for r in refs}]
    checked = list(dict.fromkeys([*(old.get("checked_sources") or []), *dropped]))
    fact = {k: new.get(k, v) for k, v in old.items() if k != "derivation"}
    for k, v in new.items():
        fact.setdefault(k, v)
    if checked:
        fact["checked_sources"] = checked
    # A plain copy: shared objects would dump as YAML anchors and aliases.
    kept = {k: v for k, v in (old.get("derivation") or {}).items() if k != "owner_ruling"}
    fact["derivation"] = json.loads(json.dumps({**kept, "owner_ruling": ruling}, default=str))
    return fact


# --- the write -----------------------------------------------------------------------------------


def _same(path: Path, expected: bytes | None) -> bool:
    if expected is None:
        return not path.exists()
    if not path.is_file():
        return False
    data = path.read_bytes()
    return len(data) == len(expected) and \
        hashlib.sha256(data).digest() == hashlib.sha256(expected).digest()


def append_exact(snapshot: Snapshot, data: bytes) -> None:
    """Append ``data`` only to the exact bytes planning read."""
    if not data:
        return
    expected = snapshot.data or b""
    if expected and not expected.endswith(b"\n"):
        raise Refused("changed_since_planning", f"{snapshot.path.name} lacks a final newline")
    snapshot.path.parent.mkdir(parents=True, exist_ok=True)
    with snapshot.path.open("a+b") as handle:
        handle.seek(0)
        current = handle.read()
        if len(current) != len(expected) or \
                hashlib.sha256(current).digest() != hashlib.sha256(expected).digest():
            raise Refused("changed_since_planning", f"{snapshot.path.name} changed since planning")
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def apply(result: Plan) -> None:
    """Check every file still holds what planning read, then append the ruling, append the
    claim and replace the fact file."""
    for snapshot in (result.rulings, result.queue, result.fact_file, result.attempts,
                     result.verifications):
        if snapshot is None:
            continue
        if not _same(snapshot.path, snapshot.data):
            raise Refused("changed_since_planning", f"{snapshot.path.name} changed since planning")
    append_exact(result.rulings, result.ruling_line)
    append_exact(result.queue, result.queue_lines)
    if result.new_text is not None:
        if not _same(result.fact_file.path, result.fact_file.data):
            raise Refused("changed_since_planning", "the fact file changed since planning")
        write_atomic(result.fact_file.path, result.new_text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--facet", required=True)
    ap.add_argument("--epoch", default="initial")
    ap.add_argument("--value", required=True, help="the value as JSON (null for not_disclosed)")
    ap.add_argument("--state", required=True)
    ap.add_argument("--ruled-by", required=True)
    ap.add_argument("--ruled-at", required=True, help="the day of the ruling, YYYY-MM-DD")
    ap.add_argument("--ticket", required=True)
    ap.add_argument("--source", action="append", required=True, dest="sources")
    ap.add_argument("--resolve", action="append", default=None, dest="resolves",
                    help="an attempt id the ruling settles (default: every disagreeing attempt)")
    ap.add_argument("--basis", required=True, help="counts and field names only")
    ap.add_argument("--write", action="store_true", help="file the ruling (default: dry run)")
    args = ap.parse_args(argv)
    os.environ["MODELSPEC_DATA_DIR"] = str(args.data_dir)
    try:
        value = json.loads(args.value)
    except ValueError:
        value = args.value
    out: dict[str, Any] = {"subject": args.subject, "facet": args.facet, "epoch": args.epoch}
    try:
        result = plan(data_dir=args.data_dir, subject=args.subject, facet=args.facet, value=value,
                      state=args.state, ruled_by=args.ruled_by, ruled_at=args.ruled_at,
                      ticket=args.ticket, source_ids=args.sources, basis=args.basis,
                      epoch=args.epoch, resolves=args.resolves)
        if args.write:
            apply(result)
    except Refused as refusal:
        out.update(outcome="refused", reason=refusal.reason, detail=refusal.detail)
        print(json.dumps(out, sort_keys=True))
        return 1
    out.update(outcome="filed" if args.write else "planned", reason=None, state=args.state,
               **result.counts, ruling_line=bool(result.ruling_line),
               claim_events=result.queue_lines.count(b"\n"),
               fact_file=str(result.fact_file.path.relative_to(args.data_dir))
               if result.new_text is not None else None)
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
