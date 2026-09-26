"""Offline guards for the MODEL-112 research harness."""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from scripts.research import eval_jev_recommendations as research


def test_confidence_bands_are_code_owned_and_include_no_match() -> None:
    assert research.confidence_band(0.90) == "act"
    assert research.confidence_band(0.60) == "flag"
    assert research.confidence_band(0.59) == "null"
    assert research.confidence_band(0.99, no_match=True) == "null"


def test_label_sets_are_fixed_and_each_choice_has_no_match() -> None:
    cases = research.all_cases()
    assert len([case for case in cases if case.candidate == "task_routing"]) == 60
    assert {case.candidate for case in cases} == {
        "task_routing",
        "task_routing_blind",
        "evidence_attribution",
        "second_key",
        "explanation_check",
    }
    for case in cases:
        for question in case.questions.values():
            if question["type"] == "choice":
                assert research.NO_MATCH in question["criteria"]


def test_vague_size_words_do_not_assert_a_200k_context_minimum() -> None:
    labels = yaml.safe_load(research.TASK_LABELS.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in labels["cases"]}
    for case_id in (
        "Q01a",
        "Q01b",
        "Q01c",
        "Q08b",
        "Q08c",
        "Q09a",
        "Q09b",
        "Q09c",
    ):
        assert "context_200k" not in by_id[case_id]["conditions"]


def test_blind_attribution_cases_exercise_exact_evidence_identity() -> None:
    cases = research.blind_attribution_cases()

    assert len(cases) == 61
    assert {case.expected["attribution"] for case in cases} == {
        "supported",
        research.NO_MATCH,
    }
    assert {case.state["cohort"] for case in cases} == {
        "verified",
        "mismatch",
        "hard_negative",
    }
    assert {case.state.get("mutation") for case in cases} >= {
        None,
        "sibling_variant",
        "benchmark_version",
        "effort",
        "harness",
        "unit",
    }
    for case in cases:
        row = case.state["evidence_row"]
        assert {
            "subject",
            "model_id_as_evaluated",
            "benchmark_id",
            "benchmark_version",
            "value",
            "unit",
            "effort",
            "harness",
        } <= row.keys()
        assert case.state["cited_regions"]
        assert case.source_url.startswith("https://")
        assert case.source_read_date


def test_blind_routing_labels_are_separate_and_do_not_infer_conditions() -> None:
    cases = research.blind_task_cases()

    assert len(cases) == 24
    assert all(case.candidate == "task_routing_blind" for case in cases)
    by_id = {case.id: case for case in cases}
    assert by_id["B06"].expected["condition_context_200k"] is True
    assert by_id["B07"].expected["condition_context_200k"] is False
    assert by_id["B19"].expected["condition_low_latency"] is True
    assert by_id["B20"].expected["condition_commercial_use"] is True
    assert by_id["B21"].expected["condition_open_weights"] is True


def test_attribution_uses_model_102_ingestion_outcomes() -> None:
    labels = yaml.safe_load(research.JUDGMENT_LABELS.read_text(encoding="utf-8"))
    attribution = labels["attribution"]
    assert set(attribution["cohorts"]) == {"verified", "quarantined"}
    assert attribution["cohorts"]["verified"]["source"].endswith(
        "cost_to_correct_2026-09-20.jsonl.gz"
    )
    assert attribution["cohorts"]["quarantined"]["source"].endswith(
        "cascade_guard_2026-09-20.jsonl.gz"
    )

    rows = research.published_attribution_rows(labels)
    assert {row["arm"] for row in rows} == {"jev", "gpt-5-mini", "cascade"}
    assert {row["cohort"] for row in rows} == {"verified", "quarantined"}
    assert len(rows) == 3 * (627 + 383)
    assert sum(row["misattribution"] for row in rows if row["arm"] == "cascade") == 6
    assert sum(row["misattribution"] for row in rows if row["arm"] == "gpt-5-mini") == 7


def test_blind_attribution_labels_match_verification_and_mutations_change_one_field() -> None:
    cases = research.blind_attribution_cases()
    verified = [case for case in cases if case.state["cohort"] == "verified"]
    mismatches = [case for case in cases if case.state["cohort"] == "mismatch"]
    hard_negatives = [case for case in cases if case.state["cohort"] == "hard_negative"]

    assert len(verified) == 27
    assert all(case.state["verification_outcome"] == "verified" for case in verified)
    assert all(case.expected == {"attribution": "supported"} for case in verified)
    assert len(mismatches) == 9
    assert all(case.state["verification_outcome"] == "mismatch" for case in mismatches)
    assert all(case.expected == {"attribution": research.NO_MATCH} for case in mismatches)
    assert len(hard_negatives) == 25
    assert all(case.state["verification_outcome"] == "verified" for case in hard_negatives)
    assert all(case.expected == {"attribution": research.NO_MATCH} for case in hard_negatives)
    base_rows = {case.state["source_target"]: case.state["evidence_row"] for case in verified}
    for case in hard_negatives:
        base = base_rows[case.state["source_target"]]
        changed = {key for key in base if base[key] != case.state["evidence_row"][key]}
        assert changed == {
            {
                "sibling_variant": "subject",
                "benchmark_version": "benchmark_version",
                "effort": "effort",
                "harness": "harness",
                "unit": "unit",
            }[case.state["mutation"]]
        }


def test_blind_attribution_scoring_accepts_exact_rows_and_rejects_hard_negatives() -> None:
    cases = research.blind_attribution_cases()
    exact = next(case for case in cases if case.state["cohort"] == "verified")
    sibling = next(case for case in cases if case.state["mutation"] == "sibling_variant")

    exact_result = {
        "answers": {
            "attribution": {
                "type": "choice",
                "choice": "supported",
                "probabilities": {"supported": 0.99, research.NO_MATCH: 0.01},
            }
        }
    }
    rejected_result = {
        "answers": {
            "attribution": {
                "type": "choice",
                "choice": research.NO_MATCH,
                "probabilities": {"supported": 0.01, research.NO_MATCH: 0.99},
            }
        }
    }

    assert research.score_answers(exact_result, exact.expected)[0]
    assert research.score_answers(rejected_result, sibling.expected)[0]


def test_concurrent_reservations_cannot_oversubscribe_the_cap() -> None:
    budget = research.SpendBudget(1.0)
    gate = threading.Barrier(8)

    def reserve() -> bool:
        gate.wait()
        return budget.reserve(0.6)

    with ThreadPoolExecutor(max_workers=8) as pool:
        admitted = list(pool.map(lambda _: reserve(), range(8)))

    assert admitted.count(True) == 1
    assert budget.reserved == 0.6
    budget.reconcile(0.6, 0.4)
    assert budget.spent == 0.4
    assert budget.reserved == 0.0


def test_task_parser_uses_the_system_temporary_directory(monkeypatch, tmp_path: Path) -> None:
    directories: list[Path | None] = []

    class TemporaryDirectory:
        def __init__(self, *, dir=None):
            directories.append(dir)

        def __enter__(self) -> str:
            return str(tmp_path)

        def __exit__(self, *_args) -> None:
            return None

    def run_parser(*_args, **kwargs) -> None:
        output = Path(kwargs["env"]["MODELSPEC_JEV_TASK_OUTPUT"])
        output.write_text(json.dumps([]), encoding="utf-8")

    monkeypatch.setattr(research.tempfile, "TemporaryDirectory", TemporaryDirectory)
    monkeypatch.setattr(research.subprocess, "run", run_parser)

    assert research.parse_real_task_baseline([]) == []
    assert directories == [None]


def test_scoring_requires_every_typed_answer() -> None:
    body = {
        "answers": {
            "pick": {
                "type": "choice",
                "choice": "supported",
                "probabilities": {"supported": 0.92, "no_match": 0.08},
                "confidence": 0.84,
            },
            "condition": {"type": "noul", "noul": 0.7},
        }
    }
    correct, confidence, no_match, values = research.score_answers(
        body, {"pick": "supported", "condition": True}
    )
    assert correct
    assert confidence == 0.7
    assert not no_match
    assert values == {"pick": "supported", "condition": True}
