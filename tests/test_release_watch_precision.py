"""Labelled filter regressions, not estimates of historical live accuracy."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from release_signals.watch import Seen, SourceRun, load_registry
from scripts.release_watch_filter import filter_releases

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures/release_watch/precision-recall.json").read_text()
)
SOURCES = {source.id: source for source in load_registry().sources}
NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)


def source_run(fixture: dict) -> SourceRun:
    source = SOURCES[fixture["source_id"]]
    seen = tuple(
        Seen(
            key=case["key"],
            model_name=case["name"],
            provider=fixture["provider"],
            url=case.get(
                "url",
                f"https://release-watch-fixture.example/{source.id}/{case['key']}",
            ),
        )
        for case in fixture["cases"]
    )
    return SourceRun(source=source, status="ok", listed=len(seen), new=seen)


@pytest.mark.parametrize(
    "fixture", FIXTURE["sources"], ids=lambda fixture: fixture["source_id"]
)
def test_each_source_precision_recall_and_release_identity(fixture: dict) -> None:
    result = filter_releases([source_run(fixture)], NOW)
    expected = {
        case["key"]: case["expected_signal_id"]
        for case in fixture["cases"]
        if case["expected_signal_id"] is not None
    }
    predictions: dict[str, str] = {}
    for group in result["groups"]:
        for evidence in group["evidence"]:
            key = evidence["source_key"]
            assert key not in predictions, f"An observation reached two releases: {key}"
            predictions[key] = group["signal_id"]

    true_positives = sum(
        expected.get(key) == identifier for key, identifier in predictions.items()
    )
    false_positives = len(predictions) - true_positives
    false_negatives = sum(
        predictions.get(key) != identifier for key, identifier in expected.items()
    )
    precision = true_positives / len(predictions) if predictions else 0.0
    recall = true_positives / len(expected)

    assert {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
    } == {
        "true_positives": len(expected),
        "false_positives": 0,
        "false_negatives": 0,
        "precision": 1.0,
        "recall": 1.0,
    }, {"expected": expected, "predicted": predictions}
    assert sorted(signal.signal_id for signal in result["signals"]) == sorted(
        set(expected.values())
    )
    assert {row["source_key"] for row in result["rejected"]} == {
        case["key"] for case in fixture["cases"] if case["expected_signal_id"] is None
    }


def test_combined_sources_keep_every_labelled_candidate_under_one_release() -> None:
    result = filter_releases(
        [source_run(fixture) for fixture in FIXTURE["sources"]], NOW
    )
    expected: dict[str, set[tuple[str, str]]] = {}
    for fixture in FIXTURE["sources"]:
        for case in fixture["cases"]:
            identifier = case["expected_signal_id"]
            if identifier is not None:
                expected.setdefault(identifier, set()).add(
                    (fixture["source_id"], case["key"])
                )
    actual = {
        group["signal_id"]: {
            (evidence["source_id"], evidence["source_key"])
            for evidence in group["evidence"]
        }
        for group in result["groups"]
    }

    assert actual == expected
    assert sorted(signal.signal_id for signal in result["signals"]) == sorted(expected)


def test_fixture_covers_every_source_with_positive_and_negative_labels() -> None:
    fixtures = FIXTURE["sources"]
    assert len({fixture["source_id"] for fixture in fixtures}) == len(fixtures)
    assert {fixture["source_id"] for fixture in fixtures} == set(SOURCES)
    for fixture in fixtures:
        assert fixture["fixture_kind"] in {
            "synthetic",
            "synthetic_and_public_issue_metadata",
        }
        assert any(case["expected_signal_id"] is not None for case in fixture["cases"])
        assert any(case["expected_signal_id"] is None for case in fixture["cases"])
        assert len({case["key"] for case in fixture["cases"]}) == len(fixture["cases"])
