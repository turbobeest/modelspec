"""Which non-finite spec numbers still decide (MODEL-458).

A weight that is not finite is rejected, and so are the compact NaN, Infinity
and -Infinity tokens. Every other class below returned a decision before and
still does. Each response is strict JSON and round-trips through Decision.
"""

from __future__ import annotations

import json
import math

import pytest

from decision.contract import CONTRACT_VERSION, Decision, SpecError, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from tests.snapshot_records import loaded_index

HUGE = 1e308
INDEX = loaded_index({
    "lab/a": {"model.context_window": 100, "model.max_output_tokens": 100},
    "lab/b": {"model.context_window": 200, "model.max_output_tokens": 200},
})
BOTH = ["lab/b", "lab/a"]


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


def _json(text: str) -> dict:
    return json.loads(text)


def _decide(body: dict | str, explain: str) -> Decision:
    raw = _json(body) if isinstance(body, str) else dict(body)
    raw["explain"] = explain
    decision = decide(_parse(raw), INDEX, facets=facets)
    text = json.dumps(decision.model_dump(mode="json"), allow_nan=False)
    restored = Decision.model_validate_json(text)
    assert restored.status == decision.status
    assert [row.offering.model for row in restored.results] == [
        row.offering.model for row in decision.results
    ]
    return restored


# status, ranked models. Measured on the tree that already returned these.
DECIDE = [
    ("compare_json_nan", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":NaN}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", BOTH),
    ("compare_json_neg_inf", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":-Infinity}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", BOTH),
    ("compare_json_neg_1e400", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":-1e400}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", BOTH),
    ("compare_json_pos_inf", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":Infinity}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("compare_json_1e400", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","op":">=","value":1e400}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("compact_1e400", _base(where=["model.context_window >= 1e400"]), "no_feasible", []),
    ("compact_neg_1e400", _base(where=["model.context_window >= -1e400"]), "answered", BOTH),
    ("best_1e400", _base(where=["model.context_window >= best(1e400)"]), "answered", BOTH),
    ("window_0_1e400", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","between":[0,1e400]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", BOTH),
    ("window_0_pos_inf", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","between":[0,Infinity]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", BOTH),
    ("window_nan_1", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","between":[NaN,1]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("window_neg_inf_1", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","between":[-Infinity,1]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("in_100_1e400", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","in":[100,1e400]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "answered", ["lab/a"]),
    ("in_nan", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","in":[NaN]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("in_pos_inf", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","in":[Infinity]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("in_neg_inf", _json(
        '{"spec_version":1,"where":[{"facet":"model.context_window","in":[-Infinity]}],'
        '"optimize":{"max":"model.context_window"}}'
    ), "no_feasible", []),
    ("lex_within_1e400", _json(
        '{"spec_version":1,"where":[],"optimize":{"lexicographic":['
        '{"max":"model.context_window","within":1e400},'
        '{"max":"model.max_output_tokens"}]}}'
    ), "answered", BOTH),
    ("lex_within_string_inf", _base(optimize={
        "lexicographic": [
            {"max": "model.context_window", "within": "Infinity"},
            {"max": "model.max_output_tokens"},
        ],
    }), "answered", BOTH),
    ("lex_within_token_inf", _json(
        '{"spec_version":1,"where":[],"optimize":{"lexicographic":['
        '{"max":"model.context_window","within":Infinity},'
        '{"max":"model.max_output_tokens"}]}}'
    ), "answered", BOTH),
    ("memory_string_inf", _base(profile={
        "profile_version": 1,
        "local": [{"model": "lab/a", "hardware": {"class": "gpu", "memory_gb": "Infinity"}}],
    }), "answered", BOTH),
    ("memory_token_inf", _json(
        '{"spec_version":1,"where":[],"optimize":{"max":"model.context_window"},'
        '"profile":{"profile_version":1,"local":[{"model":"lab/a","hardware":'
        '{"class":"gpu","memory_gb":Infinity}}]}}'
    ), "answered", BOTH),
    ("budget_string_inf", _base(profile={
        "profile_version": 1,
        "budget": {"max_cost_per_task_usd": "Infinity"},
    }), "answered", BOTH),
    ("budget_token_inf", _json(
        '{"spec_version":1,"where":[],"optimize":{"max":"model.context_window"},'
        '"profile":{"profile_version":1,"budget":{"max_cost_per_task_usd":Infinity}}}'
    ), "answered", BOTH),
]

REFUSE = [
    ("compact_nan", _base(where=["model.context_window >= NaN"])),
    ("compact_pos_inf", _base(where=["model.context_window >= Infinity"])),
    ("compact_neg_inf", _base(where=["model.context_window >= -Infinity"])),
    ("best_nan", _base(where=["model.context_window >= best(NaN)"])),
    ("best_pos_inf", _base(where=["model.context_window >= best(Infinity)"])),
    ("best_neg_inf", _base(where=["model.context_window >= best(-Infinity)"])),
    ("weight_pos_inf", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.context_window":Infinity}}}'
    )),
    ("weight_1e400", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.context_window":1e400}}}'
    )),
    ("weight_nan", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.context_window":NaN}}}'
    )),
    ("weight_neg_1e400", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.context_window":-1e400}}}'
    )),
    ("weight_neg_inf", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.context_window":-Infinity}}}'
    )),
    ("preference_weight_string_inf", _base(optimize={
        "weights": {"model.weights_openness": {"prefer": "open_weights", "weight": "Infinity"}},
    })),
    ("preference_weight_token_inf", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.weights_openness":'
        '{"prefer":"open_weights","weight":Infinity}}}}'
    )),
    ("preference_value_nan", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.weights_openness":'
        '{"prefer":NaN,"weight":1}}}}'
    )),
    ("preference_value_pos_inf", _json(
        '{"spec_version":1,"optimize":{"weights":{"model.weights_openness":'
        '{"prefer":Infinity,"weight":1}}}}'
    )),
]


def test_contract_version_stays_current() -> None:
    assert CONTRACT_VERSION == "2.19"


@pytest.mark.parametrize(("name", "body", "status", "models"), DECIDE, ids=[row[0] for row in DECIDE])
def test_input_class_still_decides(name, body, status, models) -> None:
    del name
    for explain in ("none", "full"):
        decision = _decide(body, explain)
        assert decision.status == status
        assert [row.offering.model for row in decision.results] == models
        assert all(
            row.distance is None or math.isfinite(row.distance) for row in decision.near_misses
        )


@pytest.mark.parametrize(("name", "body"), REFUSE, ids=[row[0] for row in REFUSE])
def test_input_class_stays_rejected(name, body) -> None:
    del name
    _rejects(body)


def test_response_scalars_accept_a_nonfinite_measurement() -> None:
    from decision.contract import ModelElimination, NearMiss, OfferingRef

    offering = OfferingRef(model="lab/a")
    row = ModelElimination(
        model="lab/a",
        offering=offering,
        condition="model.context_window >= 1",
        value=float("nan"),
    )
    assert isinstance(row.value, float) and math.isnan(row.value)
    omitted = NearMiss(
        offering=offering,
        condition="model.context_window >= 1",
        distance=float("inf"),
    )
    assert omitted.distance is None
    kept = NearMiss(offering=offering, condition="model.context_window >= 1", distance=3.5)
    assert kept.distance == 3.5


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
    spec = _parse(_base(
        explain="full",
        optimize={"weights": {
            "model.context_window": HUGE,
            "model.max_output_tokens": HUGE,
        }},
    ))
    decision = decide(spec, INDEX, facets=facets)
    assert decision.status == "answered"
    assert [row.offering.model for row in decision.results] == BOTH
    text = json.dumps(decision.model_dump(mode="json"), allow_nan=False)
    restored = Decision.model_validate_json(text)
    assert restored.status == "answered"
    assert [row.offering.model for row in restored.results] == BOTH


def test_overflow_reports_the_caller_weight_and_penalty() -> None:
    spec = _parse(_base(
        explain="full",
        where=[{
            "facet": "model.context_window",
            "op": ">=",
            "value": 1000,
            "soft": {"penalty": 0.5},
        }],
        optimize={"weights": {
            "model.context_window": HUGE,
            "model.max_output_tokens": HUGE,
        }},
    ))
    decision = decide(spec, INDEX, facets=facets)
    assert decision.status == "answered"
    assert [row.offering.model for row in decision.results] == BOTH
    for row in decision.results:
        assert row.soft_penalty == 0.5
        assert [part.weight for part in row.contributions] == [HUGE, HUGE]
    assert [term.weight for term in decision.blend] == [HUGE, HUGE]
    text = json.dumps(decision.model_dump(mode="json"), allow_nan=False)
    restored = Decision.model_validate_json(text)
    assert [row.soft_penalty for row in restored.results] == [0.5, 0.5]
    assert [part.weight for part in restored.results[0].contributions] == [HUGE, HUGE]


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
