"""Count restored score records in an explicitly nondeployable diagnostic.

The production completeness gate must be measured separately. This command
disables that gate only to inspect score admission. It never writes a snapshot,
runs a decision corpus, or measures Worker memory. Public output is aggregate.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
import logging
import os
from pathlib import Path
import sys
import traceback


def evidence_rows(index):
    return {row.record_id: (model, row) for model, row in index.corpus_evidence()}


def score_readings(rows):
    return {record_id: (model, row.benchmark_id, row.value, row.unit,
                        row.measured_by, row.date, row.version, row.subcategory,
                        row.effort, row.harness, row.interval, row.n, row.quality_flags)
            for record_id, (model, row) in rows.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--baseline-export", type=Path, required=True)
    parser.add_argument("--host-only-export", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date(2026, 10, 21))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.output / "build.private.log", level=logging.WARNING,
                        force=True)
    sys.path.insert(0, str(args.code.resolve()))
    os.environ.pop("MODELSPEC_SOURCE_CACHE", None)
    if not os.environ.get("MODELSPEC_SNAPSHOT_KEY"):
        raise ValueError("set the throwaway signing key used for the comparison exports")
    from pipeline.data_source import overlay
    from decision import registry, snapshot

    root = args.output / "private-overlay"
    if not root.exists():
        overlay(args.code, args.data_dir, root)
    registry.use_root(root)
    print("NONDEPLOYABLE diagnostic: compiling score records with gate=False; no snapshot output", flush=True)
    try:
        built = snapshot.build_from_repo(
            root, premier=root / "premier/slice-1.yaml", as_of=args.as_of, gate=False,
        )
        diagnostic = snapshot.load_built_snapshot(built, include_archive=True)
        baseline = snapshot.load_snapshot_bytes(args.baseline_export.read_bytes(), include_archive=True,
                                                source="baseline scratch export")
        host_only = snapshot.load_snapshot_bytes(args.host_only_export.read_bytes(), include_archive=True,
                                                 source="host-only scratch export")
        candidate_rows = evidence_rows(diagnostic)
        baseline_rows = evidence_rows(baseline)
        host_rows = evidence_rows(host_only)
        cited = {record_id for record_id, (_, row) in candidate_rows.items()
                 if row.cited}
        lost = set(baseline_rows) - set(host_rows)
        restored = lost & set(candidate_rows)
        score_a, score_c = score_readings(baseline_rows), score_readings(candidate_rows)
        common = set(score_a) & set(score_c)
        report = {
            "purpose": "score admission diagnostic only",
            "deployable": False,
            "gate_enabled": False,
            "production_acceptance": "blocked by separately reproduced completeness gaps",
            "as_of": args.as_of.isoformat(),
            "snapshot_written": False,
            "corpus_run": False,
            "memory_run": False,
            "baseline_evidence_records": len(baseline_rows),
            "host_only_evidence_records": len(host_rows),
            "diagnostic_evidence_records": len(candidate_rows),
            "cited_evidence_records": len(cited),
            "cited_records_with_null_verification": sum(
                diagnostic.record(record_id).get("verification") is None for record_id in cited),
            "cited_records_with_cited_status": sum(
                (diagnostic.record(record_id).get("citation") or {}).get("status") == "cited"
                for record_id in cited),
            "cited_values_marked_verified": sum(candidate_rows[record_id][1].verified for record_id in cited),
            "host_policy_lost_records": len(lost),
            "lost_records_restored": len(restored),
            "restored_records_labelled_cited": len(restored & cited),
            "baseline_records_still_missing": len(set(baseline_rows) - set(candidate_rows)),
            "additional_records_vs_baseline": len(set(candidate_rows) - set(baseline_rows)),
            "common_score_readings_changed_vs_baseline": sum(score_a[rid] != score_c[rid] for rid in common),
        }
    except Exception as error:
        (args.output / "error.private.log").write_text(traceback.format_exc())
        print(json.dumps({"diagnostic_failed": True, "category": type(error).__name__}), flush=True)
        return 2
    (args.output / "evidence-diagnostic.public.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
