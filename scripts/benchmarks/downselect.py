#!/usr/bin/env python3
"""Deterministically downselect benchmark evidence into eligibility statuses."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

# Support both ``python -m scripts.benchmarks.downselect`` and direct execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from schema.benchmark_eligibility import (
    BenchmarkEvidence,
    EligibilityReport,
    EligibilityRow,
    ModelReferenceSet,
    evaluate,
)


def _date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("noncanonical date")
        return parsed
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be YYYY-MM-DD") from exc


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc


def build_report(evidence_dir: Path, reference_path: Path, as_of: date) -> EligibilityReport:
    if not evidence_dir.is_dir():
        raise ValueError(f"evidence directory does not exist: {evidence_dir}")
    reference = ModelReferenceSet.model_validate(_read_json(reference_path))
    paths = sorted(path for path in evidence_dir.glob("*.json") if path.is_file())
    evidence = [BenchmarkEvidence.model_validate(_read_json(path)) for path in paths]
    ids = [item.candidate_id for item in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate candidate_id values")
    relationships = {item.candidate_id: item.canonical_id for item in evidence}
    for candidate, canonical in relationships.items():
        if (
            candidate != canonical
            and canonical in relationships
            and relationships[canonical] != canonical
        ):
            raise ValueError(f"contradictory canonical relationship for {candidate}")
    rows: list[EligibilityRow] = []
    for item in sorted(evidence, key=lambda row: (row.candidate_id, row.canonical_id)):
        row = evaluate(item, reference, as_of)
        rows.append(row)
    return EligibilityReport(
        as_of=as_of,
        active_ids=sorted(row.candidate_id for row in rows if row.status == "active"),
        rows=rows,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence",
        required=True,
        type=Path,
        help="directory containing one JSON evidence record per candidate",
    )
    parser.add_argument("--reference-set", required=True, type=Path)
    parser.add_argument("--as-of", required=True, type=_date)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output == args.reference_set.resolve() or output.parent == args.evidence.resolve():
        parser.error("output must be separate from evidence and reference inputs")
    try:
        report = build_report(args.evidence, args.reference_set, args.as_of)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(
            json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(args.output)
    except (OSError, ValueError, ValidationError) as exc:
        if args.output.exists():
            args.output.unlink()
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
