"""Flat benchmark scores are a closed legacy set (MODEL-118)."""

from __future__ import annotations

import csv
import json
import re
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

from scripts.migrate_oll_evidence import extract_v1_scores, extract_v2_scores

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "audits" / "model-118-legacy-flat-score-baseline.csv"
MIGRATION = ROOT / "docs" / "audits" / "model-118-oll-migration.csv"


def _scores(path: Path) -> dict:
    match = re.search(
        r"(?m)^  scores:\n(?P<body>(?:    [^\n]*\n)*?)(?=^  [a-z_]+:|^---$)",
        path.read_text(encoding="utf-8"),
    )
    return (yaml.safe_load("scores:\n" + match.group("body")) or {}).get("scores") or {} \
        if match else {}


@lru_cache(maxsize=None)
def _benchmarks(card: str) -> dict:
    text = (ROOT / card).read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^benchmarks:\n(?P<body>.*?)(?=^[a-z][a-z0-9_]*:|^---$)", text
    )
    return (yaml.safe_load("benchmarks:\n" + match.group("body")) or {})["benchmarks"]


def test_catalogue_adds_no_flat_benchmark_score() -> None:
    """A current flat value must be the exact value recorded before MODEL-118."""
    with BASELINE.open(newline="", encoding="utf-8") as handle:
        legacy = {
            (row["card"], row["benchmark_id"], row["score_json"])
            for row in csv.DictReader(handle)
        }
    current = {
        (path.relative_to(ROOT).as_posix(), benchmark_id,
         json.dumps(score, separators=(",", ":")))
        for path in sorted((ROOT / "models").glob("*/*.md"))
        for benchmark_id, score in _scores(path).items()
    }

    added = sorted(current - legacy)
    assert added == [], "new benchmark values belong in benchmarks.evidence only:\n" + "\n".join(
        f"{card}: {benchmark_id}={score}" for card, benchmark_id, score in added[:50]
    )


@pytest.fixture
def v1_result() -> dict:
    return {
        "config_general": {"model_name": "example/Tiny-7B"},
        "results": {
            "harness|arc:challenge|25": {"acc_norm": 0.704778},
            "harness|gsm8k|5": {"acc": 0.7161},
            "harness|hellaswag|10": {"acc_norm": 0.859689},
            "harness|truthfulqa:mc|0": {"mc2": 0.6224},
            "harness|winogrande|5": {"acc": 0.8161},
            "harness|hendrycksTest-abstract_algebra|5": {"acc": 0.58},
        },
    }


@pytest.fixture
def v2_result() -> dict:
    return {
        "config": {"model_args": "pretrained=example/Tiny-7B,revision=abc,dtype=bfloat16"},
        "date": 1718558676.590114,
        "results": {
            "leaderboard_ifeval": {
                "prompt_level_strict_acc,none": 0.5526802,
                "inst_level_strict_acc,none": 0.6606715,
            },
            "leaderboard_bbh_alpha": {"acc_norm,none": 0.5},
            "leaderboard_bbh_beta": {"acc_norm,none": 0.7},
            "leaderboard_math_hard": {"exact_match,none": 0.2771903},
            "leaderboard_gpqa": {"acc_norm,none": 0.3649329},
            "leaderboard_musr_alpha": {"acc_norm,none": 0.3},
            "leaderboard_musr_beta": {"acc_norm,none": 0.5},
            "leaderboard_mmlu_pro": {"acc,none": 0.4520445},
        },
    }


def test_v1_result_file_maps_only_oll_v1_metrics(v1_result: dict) -> None:
    identity, evaluated, scores = extract_v1_scores(
        v1_result, "example/Tiny-7B/results_2024-05-15T03-44-20.662749.json"
    )

    assert identity == "example/Tiny-7B"
    assert evaluated.isoformat() == "2024-05-15"
    assert scores == {
        "arc_challenge": pytest.approx(70.4778),
        "gsm8k": pytest.approx(71.61),
        "hellaswag": pytest.approx(85.9689),
        "truthfulqa": pytest.approx(62.24),
        "winogrande": pytest.approx(81.61),
        "mmlu_abstract_algebra": pytest.approx(58.0),
    }


def test_v2_result_file_uses_evaluation_date_and_canonical_keys(v2_result: dict) -> None:
    identity, evaluated, scores = extract_v2_scores(
        v2_result, "example/Tiny-7B/results_2025-02-13T18-27-04.338360.json"
    )

    assert identity == "example/Tiny-7B"
    assert evaluated.isoformat() == "2024-06-16"
    assert scores == {
        "ifeval": pytest.approx(60.667585),
        "bbh": pytest.approx(60.0),
        "math_lvl5": pytest.approx(27.71903),
        "gpqa_pooled": pytest.approx(36.49329),
        "musr": pytest.approx(40.0),
        "mmlu_pro": pytest.approx(45.20445),
    }
    assert "math_500" not in scores
    assert "gpqa_diamond" not in scores


def test_oll_audit_accounts_for_every_migrated_and_legacy_value() -> None:
    with MIGRATION.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3820
    assert {row["status"] for row in rows} == {"migrated", "unverified-legacy"}

    for row in rows:
        benchmarks = _benchmarks(row["card"])
        if row["status"] == "migrated":
            evidence = {item.get("id"): item for item in benchmarks.get("evidence") or []}
            item = evidence[row["evidence_id"]]
            assert item["benchmark_id"] == row["benchmark_id"]
            assert item["source_url"] == row["source_url"]
            assert item["date_type"] == "evaluated"
            assert item["evidence_date"] == row["evidence_date"]
        else:
            assert (benchmarks.get("scores") or {}).get(row["benchmark_id"]) == float(
                row["legacy_value"]
            )
