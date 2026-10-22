"""Build accepted deploy exports for the round-three a/c/d comparison.

All states use the same repaired private checkout. This reuses round two's
fresh-process exporter and corpus runner, but round three permits explained
policy changes in c and requires an unchanged main-policy control in d.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / "r2" / "compare_private.py"
loader = importlib.util.spec_from_file_location("model439_round_two", HELPER)
r2 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(r2)

CONTROL = (
    "first_result_model_changes",
    "tie_member_set_changes",
    "answer_kind_changes",
    "http_changes",
    "status_changes",
    "ordered_result_models_changes",
    "answer_leader_changes",
    "answer_order_changes",
    "tie_breakers_changes",
    "fact_assurance_changes",
)


def compare(output):
    states = {
        label: json.loads((output / label / "state.private.json").read_text()) for label in "acd"
    }
    if any(set(state) != {"current", "successor"} for state in states.values()):
        raise ValueError("all three accepted exports must contain both periods")
    report = {
        "definitions": {
            "a": "main code, main policy, repaired data",
            "c": "candidate code, policy 866, the same repaired data",
            "d": "candidate code, main policy, the same repaired data",
            "first_result": "results[0].model, or null when absent",
            "tie_set": "sorted answer.members for tied answers, otherwise []",
        },
        "deploy_export_accepted": True,
        "periods": {},
    }
    for period in ("current", "successor"):
        rows = {label: state[period] for label, state in states.items()}
        if len({row["as_of"] for row in rows.values()}) != 1:
            raise ValueError("export periods use different dates")
        if any(row.get("diagnostic_only") for row in rows.values()):
            raise ValueError("diagnostic exports cannot establish acceptance")
        candidate = r2.compare(rows["a"], rows["c"])
        control = r2.compare(rows["a"], rows["d"])
        report["periods"][period] = {
            "c_vs_a": candidate,
            "d_vs_a": control,
            "control_passed": control["repo_cases"] == 302
            and not any(control[key] for key in CONTROL),
            "corpus_passed": all(
                row["repo_cases"] == 302
                and not row["expectation_failures"]
                and not row["cited_records_with_nonnull_verification"]
                for row in rows.values()
            ),
        }
    report["comparison_passed"] = all(
        period["control_passed"] and period["corpus_passed"]
        for period in report["periods"].values()
    )
    report["policy_changes_require_explanation"] = True
    (output / "comparison.public.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    return int(not report["comparison_passed"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main-root", type=Path)
    parser.add_argument("--candidate-root", type=Path)
    parser.add_argument("--host-policy", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states", default="acd")
    parser.add_argument("--compare-only", action="store_true")
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.compare_only:
        return compare(args.output)
    if not all((args.main_root, args.candidate_root, args.host_policy, args.data_dir)):
        parser.error("building states requires both code roots, policy and data")
    if (
        not args.states
        or len(set(args.states)) != len(args.states)
        or set(args.states) - set("acd")
    ):
        parser.error("--states must contain distinct a/c/d labels")
    args.output.mkdir(parents=True, exist_ok=True)
    for label in args.states:
        code = args.output / label / "code"
        policy = (
            args.host_policy if label == "c" else args.main_root / "registry/source-retention.json"
        )
        r2.stage(args.main_root if label == "a" else args.candidate_root, code, policy)
        env = dict(os.environ, PYTHONPATH=str(code))
        log = args.output / label / "build.private.log"
        command = [
            sys.executable,
            str(HELPER),
            "state",
            "--root",
            str(code),
            "--data-dir",
            str(args.data_dir.resolve()),
            "--output",
            str(args.output / label),
        ]
        print(f"state {label}: deploy export and corpus; private log {log}", flush=True)
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=code, env=env, stdout=stream, stderr=stream)
        print(f"state {label}: exit {result.returncode}", flush=True)
        if result.returncode:
            return result.returncode
    if all((args.output / label / "state.private.json").exists() for label in "acd"):
        return compare(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
