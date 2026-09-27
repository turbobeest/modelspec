"""The MODEL-163 collector keeps a reproducible committed source census."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.model_163_collect import SOURCE_URLS, additions

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "model_163_collect.py"


def test_committed_source_census_uses_the_pre_model_163_lineup() -> None:
    assert set(additions()) == set(SOURCE_URLS)


def test_help_does_not_run_the_source_census() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert "--base-ref" in proc.stdout
