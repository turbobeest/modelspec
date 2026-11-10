"""The frozen public image keeps a count for each new diagnostic.

The counts are the whole baseline. A rise fails. A fall fails and tells the
reader to lower the baseline. The assertion text has no page names and no values.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.data_trust.catalogue import load

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = Path(__file__).resolve().parent / "fixtures" / "public_diagnostic_counts.json"
RULES = ("duplicate_yaml_key", "retained_cite_only_copy", "unknown_benchmark_key")


def public_diagnostic_counts(root: Path) -> dict[str, int]:
    catalogue = load(root)
    counts = {rule: 0 for rule in RULES}
    for finding in catalogue.inventory_findings:
        if finding.rule in counts:
            counts[finding.rule] += 1
    return counts


def count_problems(found: dict[str, int], baseline: dict[str, int]) -> list[str]:
    problems = []
    for rule in RULES:
        if found[rule] > baseline[rule]:
            problems.append(f"{rule} count {found[rule]} is above the baseline {baseline[rule]}")
        elif found[rule] < baseline[rule]:
            problems.append(
                f"{rule} count fell from {baseline[rule]} to {found[rule]}; lower the baseline"
            )
    return problems


def test_a_higher_count_fails():
    found = {"duplicate_yaml_key": 11, "retained_cite_only_copy": 0, "unknown_benchmark_key": 41}
    baseline = {"duplicate_yaml_key": 10, "retained_cite_only_copy": 0, "unknown_benchmark_key": 41}
    assert count_problems(found, baseline) == [
        "duplicate_yaml_key count 11 is above the baseline 10"
    ]


def test_a_lower_count_tells_the_reader_to_lower_the_baseline():
    found = {"duplicate_yaml_key": 10, "retained_cite_only_copy": 0, "unknown_benchmark_key": 40}
    baseline = {"duplicate_yaml_key": 10, "retained_cite_only_copy": 0, "unknown_benchmark_key": 41}
    assert count_problems(found, baseline) == [
        "unknown_benchmark_key count fell from 41 to 40; lower the baseline"
    ]


def test_public_image_diagnostic_counts_match_the_baseline():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    assert set(baseline) == set(RULES)
    assert all(isinstance(baseline[rule], int) and not isinstance(baseline[rule], bool) for rule in RULES)
    found = public_diagnostic_counts(ROOT)
    assert count_problems(found, baseline) == []
