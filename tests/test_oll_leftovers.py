"""MODEL-154: card data must agree with the model's own frozen OLL results.

The fixture retains the cited raw metrics, dataset revision and read date. It
is an audit record, not independent verification for the decision engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
AUDIT = json.loads((ROOT / "tests/fixtures/oll_leftovers_audit.json").read_text())
ROWS = AUDIT["ifeval_audit"]


def _benchmarks(card: str) -> dict:
    text = (ROOT / card).read_text()
    return yaml.safe_load(text.split("---", 2)[1])["benchmarks"]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["card"])
def test_oll_values_belong_to_the_card_model(row: dict) -> None:
    """A mirror, quantization or base model cannot inherit another model's run."""
    scores = _benchmarks(row["card"])["scores"]
    for field, change in row["fields"].items():
        assert scores.get(field) == change["new"], (row["card"], field)
    if "metrics" not in row:
        assert all(change["new"] is None for change in row["fields"].values())
        return

    expected_repository = row["model_repository"].replace("zai-org/", "THUDM/")
    assert row["evaluated_model"].lower() == expected_repository.lower()
    assert f'/{row["evaluated_model"]}/results_' in row["source"]
    metrics = row["metrics"]
    strict = metrics["leaderboard_ifeval"]
    expected = round(100 * mean([
        strict["prompt_level_strict_acc,none"],
        strict["inst_level_strict_acc,none"],
    ]), 1)
    assert scores["ifeval"] == expected
    if row["leftover"]:
        for field in ("bbh", "musr"):
            subtasks = [values["acc_norm,none"] for task, values in metrics.items()
                        if task.startswith(f"leaderboard_{field}_")]
            assert subtasks
            assert scores[field] == round(100 * mean(subtasks), 1)
        assert scores["mmlu_pro"] == round(
            100 * metrics["leaderboard_mmlu_pro"]["acc,none"], 1,
        )


def test_audit_covers_all_leftovers_and_required_sample() -> None:
    assert len(ROWS) == 138
    assert sum(row["leftover"] for row in ROWS) == 25
    sample = [row for row in ROWS if row["sampled"]]
    assert len(sample) == 15
    assert len(sample) / len(ROWS) >= 0.1
    mismatch = lambda row: row["fields"]["ifeval"]["old"] != row["fields"]["ifeval"]["new"]
    assert sum(map(mismatch, sample)) == 3
    assert sum(map(mismatch, ROWS)) == 24


@pytest.mark.parametrize("row", [r for r in ROWS if r["leftover"]],
                         ids=lambda row: row["card"])
def test_corrected_cards_cite_the_run_and_read_date(row: dict) -> None:
    notes = _benchmarks(row["card"])["benchmark_notes"]
    assert "MODEL-154" in notes
    assert row["read_date"] in notes
    assert row["source"] in notes


@pytest.mark.parametrize("row", AUDIT["full_math"], ids=lambda row: row["card"])
def test_full_math_is_not_math_500(row: dict) -> None:
    benchmarks = _benchmarks(row["card"])
    assert benchmarks["scores"].get("math_500") is None
    assert benchmarks["scores"]["math"] == row["value"]
    assert row["source"] in benchmarks["benchmark_notes"]
    assert row["read_date"] in benchmarks["benchmark_notes"]
