"""python -m scripts.data_trust data|sample|run --data-dir PATH [--json]."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from decision.registry import load as load_registry
from pipeline.data_source import overlay
from scripts.data_trust import invariants, sample
from scripts.data_trust.catalogue import Finding, calibrate, load
from scripts.data_trust.report import append_defects, summary, write

ENGINE = Path(__file__).resolve().parents[2]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("data", "sample", "run"))
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--seed")
    p.add_argument("--date", type=date.fromisoformat, default=date.today())
    p.add_argument("--json", action="store_true")
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--output-dir", type=Path)
    p.add_argument("--defect-log", type=Path)
    args = p.parse_args(argv)
    if args.n < 1:
        p.error("--n must be positive")
    seed = args.seed or args.date.strftime("%G-W%V")
    with tempfile.TemporaryDirectory(prefix="modelspec-trust-overlay-") as tmp:
        root = overlay(ENGINE, args.data_dir, Path(tmp))
        c = load(root)
        registry = load_registry(root / "registry", repo_root=root)
        try:
            calibrate(c, root, registry, args.date)
        except (ValueError, KeyError, TypeError):
            c.legacy = c.facts
            c.facts = []
            c.findings.append(Finding("snapshot", "build", "snapshot_build"))
        inv = invariants.run(c, registry, args.date)
        sampled = (
            sample.run(c, registry, n=args.n, seed=seed, as_of=args.date)
            if args.command != "data"
            else {
                "requested": 0,
                "sampled": 0,
                "seed": seed,
                "counts": {"matched": 0, "mismatched": 0, "unreadable": 0},
                "error_rate": sample.wilson(0, 0),
                "strata": [],
                "results": [],
            }
        )
    commit = subprocess.run(
        ["git", "-C", str(ENGINE), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    report = {
        "format": "modelspec.data-trust",
        "format_version": 2,
        "served_accuracy_target": 0.99999,
        "as_of": args.date.isoformat(),
        "engine_commit": commit,
        "audit_code_sha256": hashlib.sha256(
            b"".join(
                file.name.encode() + file.read_bytes()
                for file in sorted(Path(__file__).parent.glob("*.py"))
            )
        ).hexdigest(),
        "invariants": inv,
        "sample": sampled,
    }
    if args.defect_log:
        report["new_defects"] = append_defects(args.defect_log, report)
    if args.output_dir:
        write(report, args.output_dir)
    print(
        summary(report)
        if args.summary_only or not args.json
        else json.dumps(report, sort_keys=True, allow_nan=False),
        end="\n",
    )
    return 1 if inv["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
