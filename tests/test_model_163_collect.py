"""The MODEL-163 collector keeps a reproducible committed source census."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from decision.model import SourceRef
from scripts.model_143_collect import known, undisclosed
from scripts.model_163_collect import SOURCE_URLS, additions, skip_page_licence_facts

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


def test_a_model_page_does_not_file_licence_facts() -> None:
    ref = SourceRef(
        source_id="page", snapshot_ref="sha256:" + "cd" * 32, cited_regions=["model-spec"],
    )
    page = [
        undisclosed("licence.commercial_use", ref),
        undisclosed("licence.user_cap", ref),
        known("model.context_window", 8192, ref),
    ]
    on_card = [known("licence.commercial_use", "permitted", ref)]
    writing, filing = skip_page_licence_facts(page, on_card)
    assert [fact.facet for fact in filing] == ["model.context_window"]
    kept = next(fact for fact in writing if fact.facet == "licence.commercial_use")
    assert kept.value == "permitted"
    assert "licence.user_cap" not in {fact.facet for fact in writing}
