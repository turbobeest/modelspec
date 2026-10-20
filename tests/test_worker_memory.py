"""The PR probe enforces headroom against a reproducible public workload."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def assess(steady_mib: float, *, baseline_mib: float | None = None) -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the Worker memory probe")
    program = """
const { assessMemory } = require('./api/worker/measure_memory.cjs');
const [steady, baseline] = JSON.parse(process.argv[1]);
console.log(JSON.stringify(assessMemory(
  {steady_bytes: steady * 1048576},
  {limitMiB: 115, baseline: baseline === null ? null : {steady_bytes: baseline * 1048576}}
)));
"""
    result = subprocess.run([node, "-e", program, json.dumps([steady_mib, baseline_mib])],
                            cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_memory_gate_accepts_exactly_115_mib_and_rejects_one_byte_above():
    assert assess(115)["passed"] is True
    assert assess(115 + 1 / 1048576)["passed"] is False


def test_memory_gate_warns_only_above_one_mib_increase_from_main():
    assert assess(111, baseline_mib=110)["warnings"] == []
    assert "1 MiB" in assess(111 + 1 / 1048576, baseline_mib=110)["warnings"][0]
    assert assess(110, baseline_mib=111)["warnings"] == []


def test_memory_gate_refuses_invalid_counts_and_limits():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the Worker memory probe")
    program = """
const assert = require('node:assert/strict');
const { assessMemory } = require('./api/worker/measure_memory.cjs');
for (const result of [{}, {steady_bytes: NaN}, {steady_bytes: Infinity}, {steady_bytes: -1}]) {
  assert.throws(() => assessMemory(result));
}
for (const baseline of [{}, {steady_bytes: NaN}]) {
  assert.throws(() => assessMemory({steady_bytes: 1}, {baseline}));
}
assert.throws(() => assessMemory({steady_bytes: 1}, {limitMiB: 121}));
"""
    result = subprocess.run([node, "-e", program], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_memory_gate_compares_only_matching_periods_and_accepts_legacy_current_results():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the Worker memory probe")
    program = """
const assert = require('node:assert/strict');
const { assessMemory } = require('./api/worker/measure_memory.cjs');
const current = {steady_bytes: 100, period: 'current'};
const successor = {steady_bytes: 100, period: 'successor'};
assert.throws(() => assessMemory(successor, {baseline: current}), /period/);
assert.throws(() => assessMemory(current, {baseline: successor}), /period/);
assert.throws(() => assessMemory(successor, {baseline: {steady_bytes: 100}}), /period/);
assert.equal(assessMemory(current, {baseline: {steady_bytes: 100}}).passed, true);
assert.equal(assessMemory(successor, {baseline: successor}).passed, true);
"""
    result = subprocess.run([node, "-e", program], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_public_fixture_builds_admitted_synthetic_hardware_records(tmp_path):
    from api.worker.memory_fixture import materialize
    from decision.snapshot import build_from_repo

    root = materialize(ROOT, tmp_path / "data", as_of=date(2026, 10, 18))
    compiled = build_from_repo(
        root, premier=root / "premier/slice-1.yaml", as_of=date(2026, 10, 18))
    assert compiled.content["valid_until"] == "2026-10-21"
    from decision.snapshot import load_built_snapshot
    snapshot = load_built_snapshot(compiled, include_archive=True, source="memory fixture")
    rows = snapshot.hardware_fit_records("google/gemma-4-31b-it", "nvidia_rtx_4090")
    synthetic = [row for row in rows if row["id"].startswith("hardware-fit:memory-fixture-")]
    assert len(synthetic) >= 15
    assert max(len(row["source_ids"]) for row in synthetic) >= 54
    assert all(snapshot.source_url(sid).startswith("https://memory-fixture.example/")
               for row in synthetic for sid in row["source_ids"])
    assert (root / "models").resolve() == ROOT / "models"
    assert not (root / "hardware").is_symlink()
    # MODEL-417: as in deployment, every device's sourced memory is a retained
    # record, so provenance rows are as wide as the deployed table's.
    devices = [path.stem for path in (root / "hardware").glob("*.yaml")
               if not path.name.startswith("_")]
    assert len(devices) > 50
    for device in devices:
        record_id = snapshot.hardware_device(device)["record_id"]
        assert snapshot.record(record_id)["memory"]


def test_public_memory_workflow_gates_and_compares_the_main_bundle():
    workflow = yaml.safe_load((ROOT / ".github/workflows/rank-api.yml").read_text())
    job = workflow["jobs"]["memory"]
    assert "pull_request" in job["if"]
    assert not job.get("continue-on-error")
    assert all(not step.get("continue-on-error") for step in job["steps"])
    text = yaml.safe_dump(job)
    assert "--limit-mib 115" in text
    assert "--baseline" in text
    assert "memory_fixture.py" in text
    assert "pyodide@0.28.3" in text
    assert "secrets." not in text
    commands = [line.strip() for step in job["steps"] for line in step.get("run", "").splitlines()
                if "node --expose-gc" in line]
    assert len(commands) == 4
    assert sum("--successor" in command for command in commands) == 2
    assert all("--measure-only" in command for command in commands[:2])
    assert all("--limit-mib 115" in command for command in commands[2:])
    assert "--baseline" in commands[2]


@pytest.mark.parametrize("main_has_successor", [False, True])
def test_public_memory_workflow_requires_both_candidate_periods_on_historical_main(
    tmp_path, main_has_successor,
):
    workflow = yaml.safe_load((ROOT / ".github/workflows/rank-api.yml").read_text())
    steps = workflow["jobs"]["memory"]["steps"]
    detection = next((step for step in steps if step.get("id") == "main_periods"), None)
    assert detection is not None, "detect the actual baseline bundle's successor before probing it"
    bundle = tmp_path / "memory-main-bundle"
    bundle.mkdir()
    blobs = ({"/api/decision/snapshot-successor.json.gz": "fixture",
              "/api/decision/vocabulary-successor.json": "fixture"} if main_has_successor else {})
    (bundle / "bundled_data.py").write_text(f"BLOBS = {blobs!r}\n")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    (binaries / "python").symlink_to(sys.executable)
    node = binaries / "node"
    node.write_text(
        f"#!{sys.executable}\nimport json, os, sys\n"
        "with open(os.environ['MEMORY_CALLS'], 'a') as log:\n"
        "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n")
    node.chmod(0o755)
    output = tmp_path / "outputs"
    calls = tmp_path / "calls"
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output),
           "MEMORY_CALLS": str(calls), "PATH": f"{binaries}{os.pathsep}{os.environ['PATH']}"}
    result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", detection["run"]],
                            cwd=ROOT, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    capability = str(main_has_successor).lower()
    assert f"successor={capability}" in output.read_text().splitlines()
    logs = result.stdout
    for step in steps:
        script = step.get("run", "")
        if "node --expose-gc" not in script:
            continue
        script = script.replace("${{ steps.main_periods.outputs.successor }}", capability)
        result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", script],
                                cwd=ROOT, env=env, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        logs += result.stdout
    commands = [json.loads(line) for line in calls.read_text().splitlines()]
    baseline = [args for args in commands if "--measure-only" in args]
    candidate = [args for args in commands if "--measure-only" not in args]
    assert len(baseline) == 1 + main_has_successor
    assert "--successor" not in baseline[0]
    assert len(candidate) == 2
    assert ["--successor" in args for args in candidate] == [False, True]
    assert all(args[args.index("--limit-mib") + 1] == "115" for args in candidate)
    assert candidate[0][candidate[0].index("--baseline") + 1] == str(tmp_path / "memory-main.json")
    if main_has_successor:
        assert candidate[1][candidate[1].index("--baseline") + 1] == str(
            tmp_path / "memory-main-successor.json")
    else:
        assert "--baseline" not in candidate[1]
        assert "::notice::" in logs and "successor" in logs


@pytest.mark.parametrize("only_member", ["snapshot-successor.json.gz", "vocabulary-successor.json"])
def test_public_memory_workflow_rejects_incomplete_main_successor(tmp_path, only_member):
    workflow = yaml.safe_load((ROOT / ".github/workflows/rank-api.yml").read_text())
    steps = workflow["jobs"]["memory"]["steps"]
    detection = next((step for step in steps if step.get("id") == "main_periods"), None)
    assert detection is not None, "detect successor capability without hiding malformed bundles"
    bundle = tmp_path / "memory-main-bundle"
    bundle.mkdir()
    (bundle / "bundled_data.py").write_text(
        f"BLOBS = {{'/api/decision/{only_member}': 'fixture'}}\n")
    output = tmp_path / "outputs"
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output)}
    script = detection["run"].replace("python -", f'"{sys.executable}" -')
    result = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", script],
                            cwd=ROOT, env=env, text=True, capture_output=True)
    assert result.returncode != 0
    assert "incomplete successor" in result.stderr
    assert not output.exists() or "successor=false" not in output.read_text()


def test_private_memory_workflow_patch_gates_and_compares_both_periods():
    patch = (ROOT / "docs/model-407-recall-private.patch").read_text()
    commands = [line[1:].strip() for line in patch.splitlines()
                if line.startswith("+") and "node --expose-gc" in line]
    assert len(commands) == 4
    assert sum("--successor" in command for command in commands) == 2
    assert all("--measure-only" in command for command in commands[:2])
    assert all("--limit-mib 115" in command and "--baseline" in command
               for command in commands[2:])
    assert "--baseline \"$RUNNER_TEMP/private-main-successor-memory.json\"" in commands[-1]
