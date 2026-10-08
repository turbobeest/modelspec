"""Inspect the built client wheel, including its package and metadata file list."""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def test_wheel_contains_only_the_thin_client_and_its_guidance(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(tmp_path), str(root)],
        cwd=tmp_path,
        env={**os.environ, "PIP_CACHE_DIR": str(tmp_path / "pip-cache")},
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    with zipfile.ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
    assert names == {
        "cli/__init__.py",
        "cli/modelspec/__init__.py",
        "cli/modelspec/cli.py",
        "cli/modelspec/auth.py",
        "cli/modelspec/client.py",
        "cli/modelspec/errors.py",
        "cli/modelspec/guidance.py",
        "cli/modelspec/setup.py",
        "cli/modelspec/spec.py",
        "cli/modelspec/agent-bundle.json",
        "cli/modelspec/spec.schema.json",
        "cli/modelspec/feedback.schema.json",
        "modelspec_dev-0.3.1.dist-info/METADATA",
        "modelspec_dev-0.3.1.dist-info/WHEEL",
        "modelspec_dev-0.3.1.dist-info/entry_points.txt",
        "modelspec_dev-0.3.1.dist-info/licenses/LICENSE",
        "modelspec_dev-0.3.1.dist-info/RECORD",
    }
    assert not any(name.endswith(("/offline.py", "/snapshot.py", "/legacy.py")) for name in names)
    assert not {"models", "benchmarks", "registry", "pipeline", "decision", "api"} & {
        name.split("/", 1)[0] for name in names
    }
