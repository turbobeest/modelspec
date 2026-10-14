"""Run the actual integration tests against two corrupted temporary data copies."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRATCH = ROOT / ".artifacts/model-395"
TESTS = [
    "tests/test_decision_model.py::test_repository_subscription_offerings_validate_against_the_real_registry",
    "tests/test_decision_snapshot.py::test_production_snapshot_admits_supported_subscription_facts",
]
verdicts = {}
SCRATCH.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="mutations-", dir=SCRATCH) as directory:
    source = Path(directory)
    for entry in ROOT.iterdir():
        if entry.name in {".artifacts", ".pytest_cache", ".ruff_cache"}:
            continue
        if entry.name in {"tests", "offerings"}:
            shutil.copytree(
                entry, source / entry.name, ignore=shutil.ignore_patterns("__pycache__")
            )
        else:
            (source / entry.name).symlink_to(entry)
    path = source / "offerings/subscriptions/mistral.yaml"
    original = path.read_bytes()
    for mutation, reason in (
        ("missing-file", "missing subscription files"),
        ("unsourced-fact", "unsourced known subscription fact"),
    ):
        path.write_bytes(original)
        if mutation == "missing-file":
            path.unlink()
        else:
            rows = yaml.safe_load(path.read_text())
            fact = next(fact for row in rows for fact in row["facts"] if fact["state"] == "known")
            fact["sources"] = []
            path.write_text(yaml.safe_dump(rows))
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", *TESTS],
            cwd=source,
            env={
                **os.environ,
                "PYTHONPATH": str(source),
                "MODELSPEC_DATA_DIR": str(source),
                "MODELSPEC_REQUIRE_DATA_DIR": "1",
            },
            text=True,
            capture_output=True,
            timeout=180,
        )
        output = result.stdout + result.stderr
        (SCRATCH / f"mutation-{mutation}.log").write_text(output)
        assert result.returncode == 1, output
        assert "2 failed" in output and reason in output, output
        for test in TESTS:
            assert f"FAILED {test}" in output, output
        verdicts[mutation] = {
            "exit_code": result.returncode,
            "failed_tests": TESTS,
            "reason": reason,
        }
print(json.dumps(verdicts, indent=2))
