"""Run the board-reading gate (rule 15, readings) over every reading of one benchmark.

``python -m scripts.cited_reading --data-dir <data checkout> --benchmark <id> --source <source id>
[--clear-quarantine]``

Each reading (an evidence row of the benchmark that cites the source) goes through
``decision.cited_change.cited_reading`` with two subscription or local readers. Only a
``cited_change`` or a ``not_published`` outcome writes a card, through the refresh writer; the
card is never edited by hand. With ``--clear-quarantine`` a fresh agreement may clear a reading's
one held mismatch (MODEL-552): the clearing line the gate returns is appended to
``verification/quarantine-clearings.jsonl`` after the card is written. The board is read in memory
and no page is kept. The output is counts by outcome and reason: no model names, no values.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.cited_change import READING_KEYS, CitedChange, cited_reading
from decision.cited_reader import Reader
from decision.verify import (
    APPROVED_OLLAMA_READERS, ClaudeCLICompletion, OllamaChatCompletion,
)
from scripts import refresh_leaderboards as refresh
from scripts.model_143_evidence import evidence_id, evidence_key

CLAUDE_VERSION = "claude-sonnet-5"
DEFAULT_LOCAL = "gemma4:31b"


def _marked(complete) -> "callable":
    """A reader asks for ``<<<JSON ... JSON>>>``; a JSON-mode reply is wrapped to match."""
    def ask(prompt: str) -> str:
        reply = complete(prompt)
        return reply if "<<<JSON" in reply else f"<<<JSON {reply.strip()} JSON>>>"
    return ask


def default_readers(local_model: str = DEFAULT_LOCAL) -> list[Reader]:
    """The Claude CLI (subscription) and one approved local ollama model. No vendor API."""
    family = APPROVED_OLLAMA_READERS[local_model.lower()]
    return [
        Reader("claude-cli", "anthropic", CLAUDE_VERSION, _marked(ClaudeCLICompletion(max_calls=100))),
        Reader(f"ollama:{local_model}", family, local_model,
               _marked(OllamaChatCompletion(model=local_model, max_calls=100))),
    ]


def card_paths(root: Path, benchmark: str, source_id: str) -> list[tuple[str, Path, dict]]:
    """Every (subject, card, row) whose evidence row of the benchmark cites the source."""
    out = []
    for path in sorted((root / "models").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        if f"benchmark_id: {benchmark}" not in text:
            continue
        front = yaml.safe_load(text.split("---", 2)[1])
        for row in (front.get("benchmarks") or {}).get("evidence") or []:
            if row.get("benchmark_id") == benchmark and any(
                    s.get("source_id") == source_id for s in row.get("sources") or []):
                out.append((f"{path.parent.name}/{path.stem}", path, row))
    return out


_COST = re.compile(r"(\$\d+(?:[.,]\d+)*(?: (?:a|per) task)?)")


def dated_cost(text: str, cost_day: str) -> str:
    """Date a cost figure in a configuration with the day it was read. The gate reads the score
    only, so a new read day must never stand for a cost it did not read. The figure is kept."""
    if "(cost as of" in text:
        return text
    return _COST.sub(lambda m: f"{m.group(1)} (cost as of {cost_day})", text)


def rewritten_row(subject: str, old: dict[str, Any], outcome: CitedChange,
                  cost_day: str | None = None) -> dict[str, Any]:
    """The row the gate's record calls for. A mark adds ``not_published_since`` only; a changed
    score is written like a refresh reading, dated by the observation, with the page's hash."""
    record = outcome.record or {}
    new = dict(old)
    if outcome.marked:
        new["not_published_since"] = record["not_published_since"]
        return new
    day = record["source"]["retrieved_at"][:10]
    new.pop("not_published_since", None)
    new["score"] = record["value"]
    # A plain copy: shared objects would dump as YAML anchors and aliases.
    new["derivation"] = json.loads(json.dumps({"cited_change": record["derivation"]["cited_change"]}))
    was = None
    if isinstance(old.get("configuration"), str):
        was = refresh._read_day_of(old["configuration"])
        new["configuration"] = refresh._retell_read_day(old["configuration"], day)
    new["evidence_date"] = new["observed_at"] = new["verified_at"] = day
    new = refresh.align_observation_dating(new)
    # After the alignment: it re-dates every ``read <date>``, and the cost was not read on ``day``.
    if isinstance(new.get("configuration"), str) and (cost_day or (was and was != day)):
        new["configuration"] = dated_cost(new["configuration"], cost_day or was)
    new["sources"] = [
        {"source_id": record["source"]["source_id"], "snapshot_ref": record["source"]["snapshot_ref"],
         "cited_regions": ["rows"], "retrieved_at": record["source"]["retrieved_at"]}
        if s.get("source_id") == record["source"]["source_id"] else s
        for s in old.get("sources") or []]
    new["id"] = evidence_id(subject, new)
    return new


def _needs_derivation(row: dict) -> bool:
    """A row written by the gate before the record kept its derivation."""
    return not row.get("derivation") and any(
        s.get("retrieved_at") for s in row.get("sources") or [])


def run(root: Path, benchmark: str, source_id: str, readers: list[Reader], *,
        apply: bool = True, request=None, reconfirm: bool = False,
        cost_day: str | None = None, subject_only: str | None = None,
        clear_quarantine: bool = False, private: bool = False) -> Counter:
    os.environ["MODELSPEC_DATA_DIR"] = str(root)
    counts: Counter = Counter()
    for subject, path, row in card_paths(root, benchmark, source_id):
        if subject_only is not None and subject != subject_only:
            continue
        if reconfirm and subject_only is None and not _needs_derivation(row):
            continue
        reading = {k: row.get(k) for k in READING_KEYS}
        outcome = cited_reading(subject=subject, benchmark_id=benchmark, reading=reading,
                                source_id=source_id, readers=readers, request=request,
                                allow_unchanged=reconfirm or subject_only is not None,
                                clear_quarantine=clear_quarantine, private=private)
        counts[outcome.outcome + (f":{outcome.reason}" if outcome.reason else "")] += 1
        if apply and (outcome.changed or outcome.marked):
            refresh._rewrite_card(path, [(evidence_key(row), rewritten_row(subject, row, outcome, cost_day))])
            from decision.quarantine_clearing import append

            append((outcome.record or {}).get("clearings") or (), root)
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--benchmark", required=True)
    ap.add_argument("--private-data", action="store_true",
                    help="--data-dir is the private data: apply MODEL-491's counting rule")
    ap.add_argument("--source", required=True)
    ap.add_argument("--local-model", default=DEFAULT_LOCAL)
    ap.add_argument("--reconfirm", action="store_true",
                    help="read again only the rows the gate changed before the record kept its "
                         "derivation, and write it (score unchanged or changed as read)")
    ap.add_argument("--cost-day", help="the day the configuration's cost figure was last read; "
                    "an undated cost is marked with it")
    ap.add_argument("--subject", help="run the gate for this one model's reading only; an agreed "
                    "score equal to the filed one is a record, not a refusal")
    ap.add_argument("--clear-quarantine", action="store_true",
                    help="let a fresh agreement clear a reading's one held mismatch, within the "
                         "MODEL-552 limits, and append the clearing line")
    ap.add_argument("--no-write", action="store_true",
                    help="run the gate (it still logs its attempts) but write no card")
    args = ap.parse_args(argv)
    counts = run(args.data_dir, args.benchmark, args.source, default_readers(args.local_model),
                 apply=not args.no_write, reconfirm=args.reconfirm,
                 cost_day=args.cost_day, subject_only=args.subject,
                 clear_quarantine=args.clear_quarantine, private=args.private_data)
    print(json.dumps({"at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                      "outcomes": dict(sorted(counts.items()))}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
