"""MODEL-437 round 2 private deploy exports and corpus comparison. Scratch use only.

The public report contains counts and public corpus case IDs, never private rows.
Each state runs in a fresh process so registry/citation caches cannot cross states.
"""

from __future__ import annotations

import argparse
import collections
from datetime import UTC, date, datetime
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

KEY = "model437-round2-private-proof-throwaway-key"
WARNING = "cite_only_not_machine_verified"


def source_files(root):
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=True,
        )
        return [Path(p.decode()) for p in result.stdout.split(b"\0") if p]
    ignored = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "graphify-out"}
    return [p.relative_to(root) for p in root.rglob("*")
            if p.is_file() and not ignored.intersection(p.relative_to(root).parts)]


def stage(source, target, policy):
    target.mkdir(parents=True, exist_ok=False)
    for relative in source_files(source):
        origin = source / relative
        if origin.is_file():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, destination)
    if policy:
        shutil.copy2(policy, target / "registry/source-retention.json")


def identity(body, status):
    answer = body.get("answer") or {}
    rows = body.get("results") or []
    return {
        "http": status,
        "status": body.get("status"),
        "contract": body.get("contract_version"),
        "first_result_model": rows[0]["model"] if rows else None,
        "answer_kind": answer.get("kind"),
        "answer_members": sorted(answer.get("members", [])),
        "answer_order": answer.get("deterministic_order", []),
        "answer_leader": answer.get("leader"),
        "tie_breakers": answer.get("tie_breakers"),
        "ordered_result_models": list(dict.fromkeys(row["model"] for row in rows)),
        "warning": WARNING in body.get("warnings", []),
    }


def run_state(args):
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))
    os.environ.pop("MODELSPEC_SOURCE_CACHE", None)
    os.environ.pop("MODELSPEC_SNAPSHOT_ED25519_KEY", None)
    os.environ.update(MODELSPEC_SNAPSHOT_KEY=KEY, MODELSPEC_REQUIRE_DATA_DIR="1", DATA_SPLIT_ENABLED="false")
    from api.worker.vendor import export_data
    from pipeline.data_source import overlay
    from decision import registry
    from decision import snapshot as snapshot_runtime
    from decision.contract import Decision
    from decision.snapshot import load_snapshot_bytes
    from tests.corpus import corpus

    export_root = output / "exports"
    if not args.reuse_exports:
        print("Building deploy exports", flush=True)
        export_data(export_root, args.data_dir.resolve())
        print("Deploy exports complete; evaluating in a fresh process", flush=True)
        # export_data temporarily points registry modules at its private overlay.
        # Imported functions can retain default paths into that deleted overlay.
        # Evaluate in a fresh process so no build-time registry defaults survive.
        return subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "state", "--root", str(root),
             "--data-dir", str(args.data_dir.resolve()), "--output", str(output),
             "--reuse-exports"], cwd=root, env=os.environ.copy(),
        ).returncode
    runtime = output / "runtime-root"
    if not runtime.exists():
        overlay(root, args.data_dir.resolve(), runtime)
    registry.use_root(runtime)
    service = corpus.worker_service()
    cases = corpus.load_cases()
    periods = {}
    for period, filename in (("current", "snapshot.json.gz"), ("successor", "snapshot-successor.json.gz")):
        path = export_root / "decision" / filename
        if not path.exists():
            continue
        raw = path.read_bytes()
        envelope = json.loads(gzip.decompress(raw))
        metadata = envelope["content"]
        probe_day = date.fromisoformat(metadata["as_of"])

        class PeriodClock(datetime):
            @classmethod
            def now(cls, tz=None):
                instant = datetime.combine(probe_day, datetime.min.time(), tzinfo=UTC)
                return instant.astimezone(tz) if tz is not None else instant.replace(tzinfo=None)

        # Match the memory probe: advance the snapshot validity clock to the
        # period being exercised, rather than refusing future successor prices.
        snapshot_runtime.datetime = PeriodClock
        snap = load_snapshot_bytes(raw, key=KEY, include_archive=True, source="MODEL-437 round 2 private scratch")
        snapshots = {"repo": snap}
        predictions, failures = {}, {}
        contract_validations = 0
        print(f"{period}: evaluating {len(cases)} corpus cases at {probe_day}", flush=True)
        for position, case in enumerate(cases, 1):
            if case.snapshot not in snapshots:
                snapshots[case.snapshot] = corpus.load(corpus.snapshot_bytes(case.snapshot))
            status, raw_body = corpus.run_worker(case, snapshots[case.snapshot], service)
            body = json.loads(raw_body)
            issues = corpus.problems(case, status, body)
            if status == 200:
                try:
                    Decision.model_validate(body)
                    contract_validations += 1
                except Exception as error:
                    issues.append("contract validation: " + str(error))
            if issues:
                failures[case.id] = issues
            predictions[case.id] = identity(body, status) | {"snapshot": case.snapshot}
            if position % 40 == 0 or position == len(cases):
                print(f"{period}: {position}/{len(cases)} cases, {len(failures)} failures", flush=True)
        evidence = {value.record_id: snap.record(value.record_id)
                    for _, value in snap.corpus_evidence()}
        cited = [record for record in evidence.values()
                 if (record.get("citation") or {}).get("status") == "cited"]
        bad_cited = sum(record.get("verification") is not None for record in cited)
        template_cases = [case.id for case in cases if case.id.startswith("template-")
                          and case.id.endswith("-summary")]
        periods[period] = {
            "as_of": metadata.get("as_of"),
            "valid_from": metadata.get("valid_from"),
            "valid_until": metadata.get("valid_until"),
            "snapshot_id": envelope["snapshot_id"],
            "corpus_cases": len(cases),
            "repo_cases": sum(case.snapshot == "repo" for case in cases),
            "repo_http_200_cases": sum(predictions[case.id]["http"] == 200
                                       for case in cases if case.snapshot == "repo"),
            "expectation_failures": len(failures),
            "contract_validated_http_200": contract_validations,
            "template_cases": len(template_cases),
            "template_warnings": sum(predictions[case_id]["warning"] for case_id in template_cases),
            "corpus_warnings": sum(row["warning"] for row in predictions.values()),
            "unique_benchmark_evidence_records": len(evidence),
            "cited_benchmark_evidence_records": len(cited),
            "cited_records_with_nonnull_verification": bad_cited,
            "predictions": predictions,
            "private_failures": failures,
        }
    (output / "state.private.json").write_text(json.dumps(periods, indent=2) + "\n")
    summary = {period: {key: value for key, value in state.items()
                        if key not in {"predictions", "private_failures"}}
               for period, state in periods.items()}
    (output / "state.public.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)
    return int(any(state["expectation_failures"] or state["cited_records_with_nonnull_verification"]
                   for state in periods.values()))


def compare(a, other):
    before, after = a["predictions"], other["predictions"]
    if set(before) != set(after):
        raise ValueError("corpus case sets differ")
    keys = [key for key in before if before[key]["snapshot"] == "repo"]
    answer = lambda row: (row["answer_kind"], row["answer_members"])
    tie = lambda row: row["answer_members"] if row["answer_kind"] == "tied" else []
    changed = lambda key: [case for case in keys if before[case][key] != after[case][key]]
    counts = {key + "_changes": len(changed(key)) for key in (
        "http", "status", "contract", "first_result_model", "answer_kind", "answer_leader",
        "answer_order", "tie_breakers", "ordered_result_models")}
    counts["answer_kind_or_member_set_changes"] = sum(answer(before[case]) != answer(after[case]) for case in keys)
    counts["tie_member_set_changes"] = sum(tie(before[case]) != tie(after[case]) for case in keys)
    counts["repo_cases"] = len(keys)
    counts["first_result_changed_cases"] = changed("first_result_model")
    counts["answer_changed_cases"] = [case for case in keys if answer(before[case]) != answer(after[case])]
    return counts


def compare_states(output, labels):
    if "a" not in labels or len(set(labels)) != len(labels) or any(label not in "abcd" for label in labels):
        raise ValueError("comparison states must be distinct a/b/c/d labels including baseline a")
    states = {label: json.loads((output / label / "state.private.json").read_text()) for label in labels}
    if len({tuple(state) for state in states.values()}) != 1:
        raise ValueError("snapshot periods differ")
    report = {
        "selected_states": list(labels),
        "unobserved_states": [label for label in "abcd" if label not in states],
        "definitions": {
            "first_result_model": "results[0].model, or null when no results; this is deterministic ordering, not a claim of a unique recommendation",
            "answer_kind_or_member_set": "answer.kind and sorted answer.members; null and [] when absent",
            "tie_member_set": "sorted answer.members when answer.kind is tied, otherwise []",
            "template_warnings": "40 template corpus cases at explain summary, counted once each",
        },
        "periods": {},
    }
    for period in states["a"]:
        periods = {label: state[period] for label, state in states.items()}
        if len({row["as_of"] for row in periods.values()}) != 1:
            raise ValueError("as_of dates differ")
        report["periods"][period] = {
            "states": {label: {key: value for key, value in row.items()
                               if key not in {"predictions", "private_failures"}}
                       for label, row in periods.items()},
            **{label + "_vs_a": (compare(periods["a"], periods[label])
                                  if label in periods else {"status": "unobserved", "state": label})
               for label in "bcd"},
        }
        if "c" in periods and "d" in periods:
            report["periods"][period]["c_vs_d"] = compare(periods["d"], periods["c"])
    checked = [measurements[label + "_vs_a"]
               for measurements in report["periods"].values()
               for label in "cd" if label in states]
    report["acceptance_passed"] = all(
        row["repo_cases"] == 302 and not any(row[key] for key in (
            "first_result_model_changes", "tie_member_set_changes", "answer_kind_changes"))
        for row in checked
    ) if checked else None
    (output / "comparison.public.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return int(report["acceptance_passed"] is False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--main-root", type=Path, required=True)
    run.add_argument("--candidate-root", type=Path, required=True)
    run.add_argument("--host-policy", type=Path, required=True)
    run.add_argument("--data-dir", type=Path, required=True)
    run.add_argument("--baseline-data-dir", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--states", default="abc",
                     help="a=main, b=main+hosts, c=candidate+hosts; optional d=candidate+main hosts")
    single = sub.add_parser("state")
    single.add_argument("--root", type=Path, required=True)
    single.add_argument("--data-dir", type=Path, required=True)
    single.add_argument("--output", type=Path, required=True)
    single.add_argument("--reuse-exports", action="store_true")
    comparison = sub.add_parser("compare")
    comparison.add_argument("--output", type=Path, required=True)
    comparison.add_argument("--states", default="abc",
                            help="states to compare with baseline a; use abd when c has no result")
    args = parser.parse_args()
    if args.command == "state":
        return run_state(args)
    if args.command == "compare":
        return compare_states(args.output, args.states)
    args.output.mkdir(parents=True, exist_ok=True)
    for label in args.states:
        if label not in "abcd":
            raise ValueError("state must be a, b, c, or d")
        code = args.output / label / "code"
        policy = args.host_policy if label in "bc" else args.main_root / "registry/source-retention.json"
        stage(args.candidate_root if label in "cd" else args.main_root, code, policy)
        data_dir = args.baseline_data_dir if label == "a" else args.data_dir
        log = args.output / label / "build.private.log"
        print(f"state {label}: starting; progress log {log}", flush=True)
        env = dict(os.environ, PYTHONPATH=str(code), MODELSPEC_SNAPSHOT_KEY=KEY,
                   DATA_SPLIT_ENABLED="false", MODELSPEC_REQUIRE_DATA_DIR="1")
        with log.open("w") as stream:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "state",
                                     "--root", str(code), "--data-dir", str(data_dir),
                                     "--output", str(args.output / label)],
                                    cwd=code, env=env, stdout=stream, stderr=stream)
        print(f"state {label}: exit {result.returncode}; log {log}", flush=True)
        if result.returncode:
            return result.returncode
    if "a" in args.states and all((args.output / label / "state.private.json").exists() for label in args.states):
        return compare_states(args.output, args.states)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
