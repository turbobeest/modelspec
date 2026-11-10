"""Finite decision numbers (MODEL-458).

Non-finite spec numbers are rejected. Finite weights whose products overflow
still decide, and the returned scores stay finite. Ordinary finite scores are
unchanged.
"""

from __future__ import annotations

import json

import pytest

from decision.contract import CONTRACT_VERSION, Decision, SpecError, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from tests.snapshot_records import loaded_index

HUGE = 1e308


def _parse(body: dict | str):
    raw = json.loads(body) if isinstance(body, str) else body
    return parse_spec(raw, facets=facets)


def _rejects(body: dict | str) -> None:
    with pytest.raises(SpecError):
        _parse(body)


def _base(**extra) -> dict:
    spec = {
        "spec_version": 1,
        "where": [],
        "optimize": {"max": "model.context_window"},
        "explain": "none",
    }
    spec.update(extra)
    return spec


def test_contract_version_stays_current() -> None:
    assert CONTRACT_VERSION == "2.19"


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "1e400", "-1e400"])
def test_nonfinite_condition_numbers_are_rejected(value) -> None:
    _rejects(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":'
        + value
        + '}],"optimize":{"max":"model.context_window"}}'
    )


@pytest.mark.parametrize("compact", [
    "model.context_window >= 1e400",
    "model.context_window >= NaN",
    "model.context_window >= Infinity",
    "model.context_window >= -Infinity",
])
def test_nonfinite_compact_numbers_are_rejected(compact) -> None:
    _rejects(_base(where=[compact]))


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "1e400"])
def test_nonfinite_weights_are_rejected(value) -> None:
    _rejects(
        '{"spec_version":1,"where":[],"optimize":{"weights":{"model.context_window":'
        + value
        + "}}}"
    )


def test_nonfinite_best_margin_tolerance_hardware_and_budget_are_rejected() -> None:
    _rejects(_base(where=["model.context_window >= best(1e400)"]))
    _rejects(_base(optimize={
        "lexicographic": [
            {"max": "model.context_window", "within": "Infinity"},
            {"max": "model.max_output_tokens"},
        ],
    }))
    _rejects(_base(profile={
        "profile_version": 1,
        "local": [{"model": "lab/a", "hardware": {"class": "gpu", "memory_gb": "Infinity"}}],
    }))
    _rejects(_base(profile={
        "profile_version": 1,
        "budget": {"max_cost_per_task_usd": "Infinity"},
    }))
    _rejects(_base(optimize={
        "weights": {"model.weights_openness": {"prefer": "open_weights", "weight": "Infinity"}},
    }))


def test_finite_extremes_and_ordinary_constraints_still_decide() -> None:
    index = loaded_index({"lab/a": {"model.context_window": 1}})
    for where in (
        ["model.context_window >= 1e308"],
        ["model.context_window >= 0"],
        ["model.context_window >= -1"],
        [{"facet": "model.context_window", "op": ">=", "value": 10**400}],
    ):
        decision = decide(_parse(_base(where=where)), index, facets=facets)
        assert isinstance(decision, Decision)
        json.dumps(decision.model_dump(mode="json"), allow_nan=False)


def test_finite_weight_overflow_still_returns_a_decision() -> None:
    index = loaded_index({
        "lab/a": {"model.context_window": 100, "model.max_output_tokens": 100},
        "lab/b": {"model.context_window": 200, "model.max_output_tokens": 200},
    })
    spec = _parse(_base(
        explain="full",
        optimize={"weights": {
            "model.context_window": HUGE,
            "model.max_output_tokens": HUGE,
        }},
    ))
    decision = decide(spec, index, facets=facets)
    assert decision.status == "answered"
    assert [row.offering.model for row in decision.results] == ["lab/b", "lab/a"]
    text = json.dumps(decision.model_dump(mode="json"), allow_nan=False)
    restored = Decision.model_validate_json(text)
    assert restored.status == "answered"
    assert [row.offering.model for row in restored.results] == ["lab/b", "lab/a"]


def test_ordinary_finite_weights_keep_a_unit_score() -> None:
    from decision.contract import Objective
    from decision.optimise import optimise

    index = loaded_index({
        "lab/low": {"model.context_window": 10},
        "lab/high": {"model.context_window": 20},
    })
    result = optimise(
        index, ["lab/low", "lab/high"], Objective(max="model.context_window"),
    )
    assert [(row.candidate_id, row.score) for row in result.results] == [
        ("lab/high", 1.0),
        ("lab/low", 0.0),
    ]
