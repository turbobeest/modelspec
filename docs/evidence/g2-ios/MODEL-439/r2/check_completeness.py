"""Run the production snapshot gate against scratch code and private data."""

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import date
import json
import logging
import os
from pathlib import Path
import sys
import traceback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare-gaps", type=Path,
                        help="private gaps JSON from a preceding gated build")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date(2026, 10, 21))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.output / "build.private.log", level=logging.WARNING,
                        force=True)
    sys.path.insert(0, str(args.code.resolve()))
    os.environ.pop("MODELSPEC_SOURCE_CACHE", None)
    from pipeline.data_source import overlay
    from decision import registry, snapshot

    root = args.output / "private-overlay"
    if not root.exists():
        overlay(args.code, args.data_dir, root)
    registry.use_root(root)
    print(f"Running production snapshot completeness gate for {args.as_of}", flush=True)
    try:
        result = snapshot.build_from_repo(
            root, premier=root / "premier/slice-1.yaml", as_of=args.as_of,
        )
    except snapshot.CompletenessError as error:
        private = {"gaps": [asdict(gap) for gap in error.gaps]}
        (args.output / "gaps.private.json").write_text(json.dumps(private, indent=2) + "\n")
        report = {
            "gate": "failed",
            "gate_enabled": True,
            "as_of": args.as_of.isoformat(),
            "source_cache_configured": False,
            "gap_count": len(error.gaps),
            "distinct_subjects": len({gap.subject for gap in error.gaps}),
            "distinct_models": len({gap.model for gap in error.gaps}),
            "reason_counts": dict(Counter(gap.reason for gap in error.gaps)),
            "facet_counts": dict(Counter(gap.facet for gap in error.gaps)),
        }
        if args.compare_gaps:
            other = json.loads(args.compare_gaps.read_text())["gaps"]
            previous = {(row["subject"], row["facet"]) for row in other}
            current = {(row.subject, row.facet) for row in error.gaps}
            report.update(
                same_subject_facet_keys=previous == current,
                current_only_gaps=len(current - previous),
                previous_only_gaps=len(previous - current),
                same_subject_facet_reasons={
                    (row["subject"], row["facet"], row["reason"]) for row in other
                } == {(row.subject, row.facet, row.reason) for row in error.gaps},
            )
        code = 1
    except Exception as error:
        (args.output / "error.private.log").write_text(traceback.format_exc())
        report = {"gate": "error", "category": type(error).__name__}
        code = 2
    else:
        report = {"gate": "passed", "gate_enabled": True,
                  "as_of": args.as_of.isoformat(), "source_cache_configured": False,
                  "gap_count": 0}
        code = 0
    (args.output / "gate.public.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
