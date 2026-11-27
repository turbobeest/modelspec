"""Run the rule-15 gate for one offering fact and write what it returns (MODEL-544).

``python -m scripts.cited_offering --data-dir <data checkout> --subject <offering id>
--facet <facet> --source <source id> [--accept-not-disclosed] [--clear-quarantine] [--no-write]``

``decision.cited_change.cited_change`` fetches the page in memory, has two subscription-CLI
readers of different families read it and returns a record or a named refusal. Only a
``cited_change`` writes: the fact's block in its offering file is replaced (every other line
is kept byte for byte) and its claim is filed in ``verification/queue/events.jsonl``
(``collected``, then ``checked`` with outcome ``cited``). The offering reference and the claim
are written from one source reference, so they name the same copy (``snapshot_ref``,
``retrieved_at``), as the data repository's claim-copy check requires (MODEL-542). Nothing is
written to the verification log. With ``--clear-quarantine`` a fresh agreement may clear the
fact's one held mismatch (MODEL-552, ``decision.quarantine_clearing``): the clearing line the gate
returns is appended to ``verification/quarantine-clearings.jsonl`` after the claim, and the build
admits the value only through it. The output is the outcome, the reason and the readers' values;
never page text.

``--allow-unchanged`` (MODEL-572, ``decision.reconfirmation``): an agreement on the filed value
and state of a fact with no cited-change block files its record and read date; the value and
state stay as filed. Such a record may be written for a card fact too (``--subject`` a model
id): its one block in the card's front matter is replaced (``file_owner_ruling.replace_fact``,
every other byte kept) and its claim is filed under its location id, ``<model>#<facet>``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from decision.cited_change import RULE, CitedChange, Lookup, cited_change, lookup
from decision.cited_reader import Reader
from decision.reconfirmation import MARK
from decision.model import DETERMINISTIC, SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, ClaudeCLICompletion, Queue, Result

AGENT = "cited-change-gate"
CLAUDE_VERSION = "claude-sonnet-5"


class WriteRefused(Exception):
    """The rewrite would change more than the one fact, or not land the record."""


def _marked(complete):
    def ask(prompt: str) -> str:
        reply = complete(prompt)
        return reply if "<<<JSON" in reply else f"<<<JSON {reply.strip()} JSON>>>"
    return ask


def _codex_version() -> str:
    version = subprocess.run(["codex", "--version"], capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, timeout=60).stdout.strip().splitlines()
    config = Path.home() / ".codex" / "config.toml"
    model = tomllib.loads(config.read_text("utf-8")).get("model", "") if config.is_file() else ""
    return " ".join(part for part in (version[-1] if version else "codex-cli", model) if part)


def codex_ask(prompt: str) -> str:
    """One ``codex exec`` run: read-only, ephemeral (no session kept), in an empty folder."""
    with tempfile.TemporaryDirectory() as empty:
        done = subprocess.run(
            ["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral"],
            input=prompt, capture_output=True, text=True, timeout=900, cwd=empty)
    if done.returncode != 0:
        raise RuntimeError(f"codex exit {done.returncode}")
    return done.stdout


def default_readers() -> list[Reader]:
    """Two subscription CLIs of different families. No vendor API."""
    return [Reader("codex-cli", "openai", _codex_version(), codex_ask),
            Reader("claude-cli", "anthropic", CLAUDE_VERSION,
                   _marked(ClaudeCLICompletion(max_calls=4)))]


# --- what is written -----------------------------------------------------------------------------


def source_ref(record: dict[str, Any]) -> SourceRef:
    """The one source reference both the offering fact and its claim carry."""
    source = record["source"]
    resolved = record["derivation"]["cited_change"].get("resolved_urls") or []
    return SourceRef(source_id=source["source_id"], snapshot_ref=source["snapshot_ref"],
                     cited_regions=list(source["cited_regions"]),
                     retrieved_at=source["retrieved_at"], resolved_urls=list(resolved))


def new_fact(old: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """The fact as the record calls for: value, state, the one source and the derivation.
    Its id, subject, facet and every other key stay as they were."""
    ref = source_ref(record).model_dump(mode="json")
    fact = {key: value for key, value in old.items() if key != "derivation"}
    fact.update(value=record["value"], state=record["state"], sources=[ref])
    # A plain copy: shared objects would dump as YAML anchors and aliases.
    fact["derivation"] = json.loads(json.dumps(
        {"cited_change": record["derivation"]["cited_change"]}))
    return fact


def _fact_id(record: dict[str, Any], found: Lookup) -> str:
    """An offering fact's stored id; a card fact's location id (``<model>#<facet>``)."""
    if found.kind == "model":
        return f"{record['subject']}#{record['facet']}"
    return found.fact["id"]


def claim(record: dict[str, Any], found: Lookup) -> Claim:
    from decision.registry import default

    facet = default().facet(record["facet"])
    return Claim(
        target=TargetRef(kind="fact", id=_fact_id(record, found)), subject=record["subject"],
        names=found.names, field=record["facet"], value=record["value"],
        collector=VerificationActor(agent=AGENT, model_family=DETERMINISTIC, method=RULE),
        sources=(source_ref(record),), unit=facet.unit, label=facet.label,
        state=record["state"])


class _NoAliases(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def rewrite(text: str, fact_id: str, fact: dict[str, Any]) -> str:
    """``text`` with the block of one fact replaced and every other line kept."""
    lines = text.splitlines(keepends=True)
    head = re.compile(rf"^(\s*)- id: {re.escape(fact_id)}\s*$")
    starts = [i for i, line in enumerate(lines) if head.match(line)]
    if len(starts) != 1:
        raise WriteRefused("the fact is not in the file exactly once")
    start = starts[0]
    indent = len(head.match(lines[start]).group(1))
    end = start + 1
    while end < len(lines):
        stripped = lines[end].lstrip(" ")
        if stripped.strip() and len(lines[end]) - len(stripped) <= indent:
            break
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    dumped = yaml.dump([fact], Dumper=_NoAliases, sort_keys=False, default_flow_style=False,
                       allow_unicode=True, width=10**9)
    block = ["" if not line else " " * indent + line + "\n" for line in dumped.splitlines()]
    return "".join(lines[:start] + block + lines[end:])


def _facts(text: str) -> tuple[list[Any], dict[str, Any]]:
    rows = yaml.safe_load(text) or []
    return ([{k: v for k, v in row.items() if k != "facts"} for row in rows],
            {f["id"]: f for row in rows for f in row.get("facts") or []})


def check_rewrite(before: str, after: str, fact_id: str, fact: dict[str, Any]) -> None:
    """Refuse a rewrite that touches anything but the one fact, or does not land it."""
    shells_before, facts_before = _facts(before)
    shells_after, facts_after = _facts(after)
    if shells_before != shells_after or facts_before.keys() != facts_after.keys():
        raise WriteRefused("the rewrite changed an offering, or added or removed a fact")
    for key, old in facts_before.items():
        if key != fact_id and facts_after[key] != old:
            raise WriteRefused(f"{key}: changed by another fact's rewrite")
    if facts_after[fact_id] != json.loads(json.dumps(fact)):
        raise WriteRefused("the rewrite did not land the record")


def _reconfirmed_fact(record: dict[str, Any], found: Lookup, data_dir: Path) -> dict[str, Any]:
    """The fact a reconfirmation files (``reconfirmation.filed``), or a refusal: the fact on disk
    must still be the one the gate read (its value, state and block, by ``read_against``), and
    the filed fact must pass the build's own test against the logs on disk."""
    from decision.reconfirmation import fact_sha256, filed, reconfirmation_problem
    from pipeline.load import LoadError, _correction_inputs

    block = record["derivation"]["cited_change"]
    current = dict(found.fact)
    if record.get("read_against") != fact_sha256(current) or "derivation" in current \
            or current.get("state") != block.get("previous_state") \
            or json.dumps(current.get("value")) != json.dumps(block.get("previous_value")):
        raise WriteRefused("the fact changed since the gate read it; read it again")
    fact = filed(current, {k: v for k, v in record.items() if k != "read_against"})
    try:
        log, verdicts, cutoff = _correction_inputs(data_dir, None)
    except LoadError as error:
        raise WriteRefused(f"the logs cannot be read: {error}") from None
    urls = {str(k): str(v.get("url")) for k, v in found.sources.items()
            if isinstance(v, dict) and v.get("url")}
    problem = reconfirmation_problem(fact, record["subject"], log=log, verdicts=verdicts,
                                     sources=urls, cutoff=cutoff, ids=found.fact_ids)
    if problem is not None:
        raise WriteRefused(f"the reconfirmation would not stand in the build: {problem}")
    return fact


def apply(outcome: CitedChange, *, data_dir: str | Path) -> Path:
    """Write a ``cited_change`` outcome for an offering fact (or a reconfirmation of a card
    fact): the file, then the claim."""
    if not outcome.changed or outcome.record is None:
        raise WriteRefused("only a cited_change is written")
    record = {k: v for k, v in outcome.record.items() if k not in {"clearings", "read_against"}}
    found = lookup(record["subject"], record["facet"], data_dir)
    if found.path is None or found.kind not in {"offering", "model"}:
        raise WriteRefused("not an offering or card fact")
    reconfirming = MARK in (record["derivation"]["cited_change"])
    if reconfirming:
        fact = _reconfirmed_fact(outcome.record, found, Path(data_dir))
    else:
        fact = new_fact(dict(found.fact), record)
    before = found.path.read_text(encoding="utf-8")
    if found.kind == "model":
        if not reconfirming:
            raise WriteRefused("a card fact is written here only for a reconfirmation")
        from scripts.file_owner_ruling import Refused, replace_fact

        try:
            after = replace_fact(before, card=True, row_id=None, facet=record["facet"],
                                 fact=fact, expect=dict(found.fact))
        except Refused as error:
            raise WriteRefused(str(error)) from None
    else:
        after = rewrite(before, found.fact["id"], fact)
        check_rewrite(before, after, found.fact["id"], fact)
    filed = claim(record, found)
    found.path.write_text(after, encoding="utf-8")
    at = datetime.fromisoformat(record["source"]["retrieved_at"])
    queue = Queue(Path(data_dir) / "verification")
    queue.file(filed, at=at)
    queue.checked(Result(filed.target, "cited",
                         reason="cite-only; two readers of different families agree (cited_change)"),
                  at=at)
    from decision.quarantine_clearing import append

    append(outcome.record.get("clearings") or (), data_dir)
    return found.path


def _readers_seen(outcome: CitedChange, data_dir: Path, subject: str, facet: str) -> list:
    block = ((outcome.record or {}).get("derivation") or {}).get("cited_change") or {}
    if block:
        return [(r["reader_id"], r["value"]) for r in block["readers"]]
    from decision.cited_reader import attempts

    logged = attempts(subject, facet, data_dir=data_dir)
    return [(r.get("reader_id"), r.get("value")) for r in (logged[-1]["readers"] if logged else [])]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--subject", required=True,
                    help="the offering id (or a model id, with --allow-unchanged)")
    ap.add_argument("--facet", required=True)
    ap.add_argument("--source", required=True, help="the registered source id to read")
    ap.add_argument("--accept-not-disclosed", action="store_true",
                    help="two readers agreeing the page does not state the value file "
                         "not_disclosed (otherwise no_value)")
    ap.add_argument("--clear-quarantine", action="store_true",
                    help="let a fresh agreement clear the fact's one held mismatch, within the "
                         "MODEL-552 limits, and append the clearing line")
    ap.add_argument("--allow-unchanged", action="store_true",
                    help="file the record of an agreement on the filed value and state of a fact "
                         "with no cited-change block (MODEL-572); the value does not change")
    ap.add_argument("--no-write", action="store_true",
                    help="run the gate (it still logs its attempt) but write nothing")
    args = ap.parse_args(argv)
    os.environ["MODELSPEC_DATA_DIR"] = str(args.data_dir)
    outcome = cited_change(subject=args.subject, facet=args.facet, source_id=args.source,
                           readers=default_readers(),
                           accept_not_disclosed=args.accept_not_disclosed,
                           clear_quarantine=args.clear_quarantine,
                           allow_unchanged=args.allow_unchanged)
    written = None
    if outcome.changed and not args.no_write:
        written = str(apply(outcome, data_dir=args.data_dir).relative_to(args.data_dir))
    print(json.dumps({"outcome": outcome.outcome, "reason": outcome.reason, "detail": outcome.detail,
                      "readers": _readers_seen(outcome, args.data_dir, args.subject, args.facet),
                      "state": (outcome.record or {}).get("state"),
                      "clearings": len((outcome.record or {}).get("clearings") or ()),
                      "written": written}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
