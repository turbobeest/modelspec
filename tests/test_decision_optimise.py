"""Optimise through its public boundary with the real snapshot index."""
from __future__ import annotations

from datetime import date

from decision.contract import EvidenceQualifiers, Objective
from decision.optimise import EvidenceSelector, optimise
from decision.snapshot import EvidenceValue
from tests.snapshot_records import loaded_index


def evidence_value(**overrides) -> EvidenceValue:
    values = {
        "benchmark_id": "bench",
        "version": "1",
        "subcategory": None,
        "value": 50,
        "unit": "percent",
        "measured_by": "independent",
        "effort": "default",
        "harness": "test@1.0",
        "date": None,
        "source_ids": ("src-board",),
        "verified": True,
        "interval": None,
        "n": None,
        "quality_flags": (),
    }
    values.update(overrides)
    return EvidenceValue(**values)


def run(rows, objective, **kwargs):
    return optimise(loaded_index(rows), list(rows), Objective.model_validate(objective), **kwargs)


def ids(result):
    return [row.candidate_id for row in result.results]


def test_single_normalises_penalty_and_places_missing_after_known():
    result = run({"b": {"speed": 100}, "a": {"speed": 90}, "c": {}},
                 {"max": "speed"}, penalties={"b": {"preference": 1.1}})
    assert ids(result) == ["a", "b", "c"]
    assert result.results[1].soft_penalty == 1.1
    assert result.results[1].contributions[0].raw_value == 100
    assert result.results[1].contributions[0].value == 1
    assert result.results[2].warnings == ("missing_objective_value",)


def test_weights_normalise_only_feasible_set_and_record_contributions():
    snapshot = loaded_index({"a": {"x": 10, "cost": 20}, "b": {"x": 20, "cost": 40},
                             "outside": {"x": 10000}})
    result = optimise(snapshot, ["b", "a"], Objective(weights={"x": 2, "-cost": 1}))
    assert ids(result) == ["b", "a"]
    assert result.results[0].score == 2
    assert result.results[0].contributions[1].normalisation.maximum == 20


def test_lexicographic_tolerance_is_anchored_not_pairwise_chained():
    rows = {"a": {"speed": 100, "cost": 30}, "b": {"speed": 96, "cost": 20},
            "c": {"speed": 92, "cost": 10}, "missing": {"speed": 1000}}
    result = run(rows, {"lexicographic": [{"max": "speed", "within": "5%"},
                                         {"min": "cost"}]})
    assert ids(result) == ["b", "a", "c", "missing"]


def test_pareto_returns_front_and_explains_dominance():
    result = run({"a": {"x": 4, "cost": 4}, "b": {"x": 2, "cost": 2},
                  "c": {"x": 1, "cost": 5}, "d": {"x": 4, "cost": 4}, "e": {}},
                 {"pareto": ["x", "-cost"]})
    assert ids(result) == ["a", "b", "d"]
    assert result.dominance["c"] == ("a", "b", "d")
    assert result.missing == ("e",)


def test_tipping_point_is_nearest_single_weight_crossing():
    result = run({"a": {"x": 10, "y": 0}, "b": {"x": 0, "y": 10}},
                 {"weights": {"x": 0.6, "y": 0.4}})
    assert len(result.tipping_points) == 2
    by_dimension = {point.dimension: point for point in result.tipping_points}
    assert abs(by_dimension["x"].threshold - 0.4) < 1e-12
    assert by_dimension["x"].direction == "decrease"
    assert by_dimension["y"].direction == "increase"
    assert abs(by_dimension["y"].threshold - 0.6) < 1e-12


def test_tipping_points_match_brute_force_with_penalties():
    import random
    rng = random.Random(142)
    for _ in range(15):
        rows = {str(i): {"x": rng.randrange(100), "y": rng.randrange(100)} for i in range(5)}
        weights = {"x": 0.7, "-y": 0.3}
        penalties = {"0": {"preference": 0.15}}
        result = run(rows, {"weights": weights}, penalties=penalties)
        points = result.tipping_points
        for dimension, original in weights.items():
            for direction, sign in [("increase", 1), ("decrease", -1)]:
                point = next((p for p in points if p.dimension == dimension
                              and p.direction == direction), None)
                # Independent grid search through the actual public ranking operation.
                first = None
                for step in range(1, 151):
                    delta = step * 0.01
                    changed = original + sign * delta
                    if changed <= 0:
                        break
                    trial = run(rows, {"weights": {**weights, dimension: changed}},
                                penalties=penalties)
                    if ids(trial)[0] != ids(result)[0]:
                        first = delta
                        break
                if first is not None:
                    assert point is not None
                    assert first - 0.01000001 <= point.change <= first + 1e-10
                if point is not None:
                    changed = point.threshold + sign * 1e-7
                    trial = run(rows, {"weights": {**weights, dimension: changed}},
                                penalties=penalties)
                    assert ids(trial)[0] != ids(result)[0]




def evidence_index(values: dict[str, list[EvidenceValue]]):
    return loaded_index(
        {cid: {} for cid in values},
        evidence_rows={(cid, "bench"): tuple(rows) for cid, rows in values.items()},
    )


def test_objective_qualifiers_create_the_complete_evidence_selector():
    selector = EvidenceSelector.from_qualifiers(
        "bench",
        EvidenceQualifiers(
            measured_by="independent",
            effort="max",
            harness="test@1.0",
            measured_after=date(2026, 8, 1),
            direct=True,
        ),
    )
    assert selector.benchmark_id == "bench"
    assert selector.measured_by is not None
    assert "independent_evaluator" in selector.measured_by
    assert selector.effort == "max"
    assert selector.harness == "test@1.0"
    assert selector.after == date(2026, 8, 1)
    assert selector.direct is True


def test_evidence_qualifiers_and_provenance_without_picking_best_measurement():
    from datetime import date

    from decision.optimise import EvidenceSelector
    index = evidence_index({
        "a": [evidence_value(value=40, date=date(2026, 9, 1)),
              evidence_value(value=99, effort="max", date=date(2026, 9, 1))],
        "b": [evidence_value(value=90, verified=False, date=date(2026, 9, 1))],
        "c": [evidence_value(value=60, date=date(2026, 9, 1)),
              evidence_value(value=70, date=date(2026, 9, 2))]})
    result = optimise(index, index.candidates(), Objective(max="quality"),
                      evidence_selectors={"quality": EvidenceSelector(
                          "bench", version="1", measured_by=frozenset({"independent"}),
                          effort="default", harness="test@1.0", after=date(2026, 8, 1))})
    assert ids(result) == ["a", "b", "c"]
    assert [row.value for row in result.results[0].contributions[0].evidence] == [40]
    assert result.results[0].contributions[0].sources == ("src-board",)
    assert result.results[2].warnings == ("missing_objective_value",)


def test_deprecated_or_contaminated_evidence_is_not_a_direct_answer():
    index = evidence_index({
        "deprecated": [evidence_value(value=99, quality_flags=("deprecated",))],
        "contaminated": [evidence_value(
            value=98, quality_flags=("contamination_warning",)
        )],
        "clean": [evidence_value(value=80)],
    })

    result = optimise(
        index,
        index.candidates(),
        Objective(max="quality"),
        evidence_selectors={"quality": EvidenceSelector("bench")},
    )

    assert ids(result) == ["clean", "contaminated", "deprecated"]
    assert result.missing == ("contaminated", "deprecated")


def test_domain_objective_refuses_blending():
    result = run({"a": {"coding": 100}}, {"max": "coding"}, domains={"coding"})
    assert result.status == "no_feasible"
    assert result.reason == "specify a benchmark or wait for the capability model (MODEL-129)"


def test_min_negative_values_ties_and_non_numeric_missing():
    result = run({"z": {"x": -10}, "a": {"x": -10}, "b": {"x": -2},
                  "c": {"x": True}, "d": {"x": "not-a-number"}}, {"min": "x"})
    assert ids(result) == ["a", "z", "b", "c", "d"]
    assert [r.score for r in result.results] == [1, 1, 0, None, None]


def test_constant_facets_do_not_contribute_and_have_no_tipping_point():
    result = run({"b": {"x": 8}, "a": {"x": 8}}, {"weights": {"x": 5}})
    assert ids(result) == ["a", "b"]
    assert [r.score for r in result.results] == [0, 0]
    assert result.tipping_points == ()


def test_lexicographic_absolute_tolerance_and_penalty():
    rows = {"a": {"x": 10, "cost": 4}, "b": {"x": 9, "cost": 1},
            "c": {"x": 0, "cost": 2}}
    objective = {"lexicographic": [{"max": "x", "within": 1}, {"min": "cost"}]}
    assert ids(run(rows, objective)) == ["b", "a", "c"]
    assert ids(run(rows, objective, penalties={"b": {"rule": 0.3}})) == ["a", "b", "c"]


def test_pareto_penalty_applies_to_each_dimension():
    result = run({"a": {"x": 10, "y": 10}, "b": {"x": 0, "y": 0}},
                 {"pareto": ["x", "y"]}, penalties={"a": {"rule": 1.1}})
    assert ids(result) == ["b"]
    assert result.dominance == {"a": ("b",)}


def test_empty_and_all_missing_objectives_have_no_feasible_result():
    assert run({}, {"max": "x"}).status == "no_feasible"
    result = run({"a": {}, "b": {"y": 1}}, {"weights": {"x": 1, "y": 1}})
    assert result.status == "no_feasible"
    assert result.results == ()
    assert result.missing == ("a", "b")


def test_pareto_matches_independent_integer_fixture():
    rows = {f"{x}{y}": {"x": x, "y": y} for x in range(4) for y in range(4)
            if x + y <= 3}
    result = run(rows, {"pareto": ["x", "y"]})
    assert ids(result) == ["03", "12", "21", "30"]
    assert result.dominance["11"] == ("12", "21")


def test_candidate_and_weight_order_do_not_change_results():
    rows = {"b": {"x": 10, "y": 0}, "a": {"x": 0, "y": 10}, "c": {}}
    first = run(rows, {"weights": {"x": 1, "y": 1}})
    second = run(dict(reversed(list(rows.items()))), {"weights": {"y": 1, "x": 1}})
    assert first == second
    assert first.tipping_points[0].change == 0


def test_penalty_and_weight_nonfinite_inputs_are_rejected():
    import pytest
    for penalty in [-1, float("nan"), float("inf")]:
        with pytest.raises(ValueError, match="penalties"):
            run({"a": {"x": 1}}, {"max": "x"}, penalties={"a": {"rule": penalty}})
    with pytest.raises(ValueError, match="weights"):
        run({"a": {"x": 1}}, {"weights": {"x": float("inf")}})




def test_lexicographic_without_tolerance_preserves_small_differences():
    result = run({"a": {"x": 1 - 1e-13, "y": 10}, "b": {"x": 1, "y": 0},
                  "c": {"x": 0, "y": 1}},
                 {"lexicographic": [{"max": "x"}, {"max": "y"}]})
    assert ids(result) == ["b", "a", "c"]


def test_all_evidence_selectors_exclude_other_measurement_conditions():
    from dataclasses import replace

    from decision.optimise import EvidenceSelector

    measurement = evidence_value(value=40, date=date(2026, 9, 1))
    other_conditions = [replace(measurement, **change) for change in [
        {"measured_by": "provider_self_report"}, {"harness": "other@1.0"},
        {"date": date(2026, 8, 1)}, {"version": "2"}, {"subcategory": "part"},
        {"benchmark_id": "other"}, {"verified": False}]]
    index = evidence_index({"a": [measurement, *other_conditions],
                            "b": [replace(measurement, value=60)]})
    selector = EvidenceSelector("bench", version="1", effort="default", harness="test@1.0",
                                after=date(2026, 8, 1), measured_by=frozenset({"independent"}))
    result = optimise(index, index.candidates(), Objective(min="coding"),
                      domains={"coding"}, evidence_selectors={"coding": selector})
    assert ids(result) == ["a", "b"]
    assert result.results[0].contributions[0].raw_value == 40
