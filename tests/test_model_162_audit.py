"""Completeness checks for the MODEL-162 OLL migration spot-check."""

from pathlib import Path


AUDIT = Path(__file__).parents[1] / "docs/audits/2026-09-26-model-162-oll-spot-check.md"


def test_model_162_audit_records_the_reproducible_sample_and_verdict() -> None:
    text = AUDIT.read_text(encoding="utf-8")

    assert "Seed:" in text
    assert "| CSV row | Model | Benchmark | Source URL | Card value | Source value | Match |" in text
    checked_rows = [line for line in text.splitlines() if line.startswith("| ") and "✅" in line]
    assert len(checked_rows) == 30
    assert "## Verdict" in text
