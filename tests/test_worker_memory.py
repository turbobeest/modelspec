"""The PR probe enforces headroom against a reproducible public workload."""

from __future__ import annotations

import json
import shutil
import subprocess
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
