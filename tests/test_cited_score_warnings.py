"""Warnings follow cited score operands that the recommendation uses."""

from dataclasses import replace

import pytest

from decision.contract import CITE_ONLY_WARNING, parse_spec
from decision.engine import decide
from decision.registry import facet
from tests.snapshot_records import evidence, fact, model
from tests.test_cited_scores import BENCHMARK, CITED_URL, load, score_inputs


def score_index(*, cited_score=90, refinement=False):
    inputs = score_inputs()
    inputs.evidence[0]["score"] = cited_score
    models = [model(mid, facts=[
        fact("model", mid, "model.context_window", context),
        fact("model", mid, "model.class", "text-generator"),
    ]) for mid, context in (("lab/cited", 8000), ("lab/plain", 200000))]
    return load(replace(
        inputs, models=models,
        benchmark_refinements={BENCHMARK: [("rust", "direct")]} if refinement else {},
    ))


def answer_for(index, *, where=(), objective=None, level="none", **extra):
    spec = parse_spec({
        "spec_version": 1, "where": list(where),
        "optimize": objective or {"max": "model.context_window"},
        "explain": level, **extra,
    }, facets=facet)
    return decide(spec, index, facets=facet)


@pytest.mark.parametrize("level", ["none", "summary", "full"])
@pytest.mark.parametrize("dimension", [BENCHMARK, "software_engineering"])
def test_cited_score_filter_warns_for_recommended_model(level, dimension):
    answer = answer_for(score_index(), where=[f"{dimension} >= -100"],
                        objective={"min": "model.context_window"}, level=level)
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING in answer.warnings
    assert CITE_ONLY_WARNING in answer.results[0].warnings
    assert CITE_ONLY_WARNING in answer.bands.best[0].warnings


@pytest.mark.parametrize("level", ["none", "summary", "full"])
@pytest.mark.parametrize("dimension", [BENCHMARK, "software_engineering"])
def test_cited_score_reference_warns_after_reference_model_eliminated(level, dimension):
    answer = answer_for(score_index(cited_score=60), where=[
        "model.context_window >= 100000", f"{dimension} >= model(lab/cited)",
    ], level=level)
    assert answer.answer.members == ["lab/plain"]
    assert CITE_ONLY_WARNING in answer.warnings
    assert CITE_ONLY_WARNING not in answer.results[0].warnings


@pytest.mark.parametrize("cited_score, warned", [(90, True), (60, False)])
@pytest.mark.parametrize("dimension, margin", [(BENCHMARK, 25), ("software_engineering", 100)])
def test_best_reference_warns_only_for_cited_winning_anchor(cited_score, warned, dimension, margin):
    answer = answer_for(score_index(cited_score=cited_score),
                        where=[f"{dimension} >= best({margin})"])
    assert answer.answer.members == ["lab/plain"]
    assert (CITE_ONLY_WARNING in answer.warnings) is warned


def test_cited_best_reference_warns_after_another_best_filter_eliminates_anchor():
    answer = answer_for(score_index(), where=[
        f"{BENCHMARK} >= best(25)", "model.context_window >= best(0)",
    ])
    assert answer.answer.members == ["lab/plain"]
    assert all(row.model != "lab/cited" for row in answer.results)
    assert CITE_ONLY_WARNING in answer.warnings


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_capability_objective_warns_for_cited_driver(level):
    answer = answer_for(score_index(), objective={"max": "software_engineering"}, level=level)
    assert "lab/cited" in answer.answer.members
    assert CITE_ONLY_WARNING in answer.warnings


def test_refinement_objective_warns_for_cited_driver():
    answer = answer_for(score_index(refinement=True),
                        objective={"weights": {"software_engineering/rust": 1}})
    assert any(row.model == "lab/cited" for row in answer.results)
    assert CITE_ONLY_WARNING in answer.warnings


def test_unrelated_score_on_recommended_model_has_only_row_warning():
    answer = answer_for(score_index(), objective={"min": "model.context_window"})
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING not in answer.warnings
    assert CITE_ONLY_WARNING in answer.results[0].warnings
    assert CITE_ONLY_WARNING in answer.bands.best[0].warnings


def test_cited_score_used_by_independent_measurement_tie_breaker_warns():
    inputs = score_inputs()
    inputs.evidence.append(evidence("lab/cited", "gpqa_diamond", 85,
                                    source="src-cited", source_url=CITED_URL, outcome=None))
    inputs = replace(inputs, benchmark_domains={
        **inputs.benchmark_domains, "gpqa_diamond": [("reasoning", "direct")],
    })
    answer = answer_for(load(inputs))
    assert answer.answer.kind == "tied"
    assert answer.answer.tie_breakers.most_independently_measured == "lab/cited"
    assert CITE_ONLY_WARNING in answer.warnings


@pytest.mark.parametrize("level", ["summary", "full"])
def test_shown_capability_citation_warns_with_a_fact_objective(level):
    answer = answer_for(
        score_index(), objective={"min": "model.context_window"}, level=level,
        capabilities={"software_engineering": "required"},
    )
    assert answer.answer.members == ["lab/cited"]
    assert any(item.model_dump().get("citation") is not None
               for shown in answer.results if shown.model == "lab/cited"
               for group in shown.evidence for item in group.items)
    assert CITE_ONLY_WARNING in answer.warnings


@pytest.mark.parametrize("objective", [False, True])
def test_qualifier_excludes_cited_score_from_warning(objective):
    inputs = score_inputs()
    inputs.evidence[0]["measured_by"] = "provider_self_report"
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 95))
    inputs = replace(inputs, models=[model("lab/cited", context=200000), model("lab/plain")])
    index = load(inputs)
    answer = answer_for(
        index, where=[] if objective else [f"{BENCHMARK} >= 0 @independent"],
        objective={"max": f"{BENCHMARK} @independent"} if objective else None,
    )
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING not in answer.warnings


def test_short_circuit_skips_unused_cited_score_filter():
    answer = answer_for(score_index(), where=[{"any": [
        "model.context_window >= 1000", f"{BENCHMARK} >= 0",
    ]}], objective={"min": "model.context_window"})
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING not in answer.warnings


@pytest.mark.parametrize("dimension", ["software_engineering", "software_engineering/rust"])
def test_cited_driver_after_eight_shown_drivers_still_warns(dimension):
    inputs = score_inputs()
    inputs.evidence[0]["id"] = "zz-cited-driver"
    inputs.evidence.extend(evidence("lab/cited", "swe_bench_verified", 90, eid=f"aa-driver-{index}")
                           for index in range(8))
    inputs.evidence.append(evidence("lab/plain", "swe_bench_verified", 70))
    inputs = replace(
        inputs, models=[model(mid, facts=[fact("model", mid, "model.class", "text-generator")])
                        for mid in ("lab/cited", "lab/plain")],
        benchmark_domains={**inputs.benchmark_domains,
                           "swe_bench_verified": [("software_engineering", "direct")]},
        benchmark_metadata={**inputs.benchmark_metadata,
                            "swe_bench_verified": {"random_baseline": 0, "sample_size": 100}},
        benchmark_refinements={key: [("rust", "direct")]
                               for key in (BENCHMARK, "swe_bench_verified")},
    )
    index = load(inputs)
    drivers = (index.refinement_drivers("lab/cited", dimension) if "/" in dimension
               else index.capability_drivers("lab/cited", dimension))
    assert len(drivers) == 8
    assert all(row.record_id != "zz-cited-driver" for row in drivers)
    answer = answer_for(index, objective={"weights": {dimension: 1}})
    assert "lab/cited" in answer.answer.members
    assert CITE_ONLY_WARNING in answer.warnings


def test_excluded_cited_score_does_not_warn_for_capability_objective():
    inputs = score_inputs()
    inputs.evidence.extend([
        evidence("lab/cited", "code_verified", 90),
        evidence("lab/plain", "code_verified", 70),
    ])
    inputs = replace(inputs, benchmark_domains={
        **inputs.benchmark_domains, "code_verified": [("software_engineering", "direct")],
    })
    answer = answer_for(load(inputs), objective={"max": "software_engineering"},
                        exclude_benchmarks=[BENCHMARK])
    assert "lab/cited" in answer.answer.members
    assert CITE_ONLY_WARNING not in answer.warnings


def mixed_score_index(*, cited_score=80, verified_score=50):
    inputs = score_inputs()
    inputs.evidence[0]["score"] = cited_score
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, verified_score, day="2026-07-01"))
    return load(replace(inputs, models=[model("lab/cited", context=200000), model("lab/plain")]))


@pytest.mark.parametrize("condition", [
    f"{BENCHMARK} <= 70",
    f"{BENCHMARK} = 50",
    {"facet": BENCHMARK, "between": [40, 70]},
    {"not": {"not": f"{BENCHMARK} <= 70"}},
    f"{BENCHMARK} <= model(lab/plain)",
])
@pytest.mark.parametrize("cited_score, verified_score, qualifies", [(80, 50, True), (50, 80, False)])
def test_score_predicate_uses_verified_value(condition, cited_score, verified_score, qualifies):
    answer = answer_for(mixed_score_index(cited_score=cited_score, verified_score=verified_score),
                        where=["model.context_window >= 150000", condition])
    if qualifies:
        assert answer.answer is not None
        assert answer.answer.members == ["lab/cited"]
    else:
        assert answer.answer is None
    assert answer.status == ("answered" if qualifies else "no_feasible")
    assert CITE_ONLY_WARNING not in answer.warnings


@pytest.mark.parametrize("condition", [
    {"not": f"{BENCHMARK} = 90"},
    f"{BENCHMARK} = 90 soft(0.2)",
])
def test_failed_score_predicate_keeps_cited_provenance(condition):
    answer = answer_for(score_index(cited_score=80), where=[condition],
                        objective={"min": "model.context_window"})
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING in answer.warnings


@pytest.mark.parametrize("verified_first", [False, True])
def test_verified_score_remains_the_benchmark_objective_winner(verified_first):
    inputs = score_inputs()
    inputs.evidence[0]["score"] = 40
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 95))
    if verified_first:
        inputs.evidence.reverse()
    answer = answer_for(load(inputs), objective={"max": BENCHMARK}, level="full")
    assert answer.status == "answered"
    assert answer.answer.members == ["lab/cited"]
    assert answer.results[0].contributions[0].raw_value == 95
    assert CITE_ONLY_WARNING not in answer.warnings
    assert CITE_ONLY_WARNING not in answer.results[0].warnings


@pytest.mark.parametrize("condition, qualifies", [
    (f"{BENCHMARK} >= 80", True),
    (f"{BENCHMARK} <= 70", False),
    (f"{BENCHMARK} = 40", False),
    ({"facet": BENCHMARK, "between": [30, 50]}, False),
])
def test_cited_score_neither_admits_nor_vetoes_verified_candidate(condition, qualifies):
    answer = answer_for(mixed_score_index(cited_score=40, verified_score=95),
                        where=["model.context_window >= 150000", condition])
    assert answer.status == ("answered" if qualifies else "no_feasible")
    if qualifies:
        assert answer.answer is not None
        assert answer.answer.members == ["lab/cited"]
    else:
        assert answer.answer is None
    assert CITE_ONLY_WARNING not in answer.warnings


@pytest.mark.parametrize("verified_first", [False, True])
def test_cited_sibling_does_not_change_capability_estimate(verified_first):
    inputs = score_inputs()
    cited = inputs.evidence.pop(0)
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 40, day="2026-07-01"))
    baseline = answer_for(load(inputs), objective={"max": "software_engineering"}, level="full")
    expected = next(row for row in baseline.results if row.model == "lab/cited").estimates
    assert len(expected) == 1
    assert expected[0].value == pytest.approx(-0.574, abs=0.001)
    inputs.evidence.append(cited)
    if not verified_first:
        inputs.evidence.reverse()
    answer = answer_for(load(inputs), objective={"max": "software_engineering"}, level="full")
    actual = next(row for row in answer.results if row.model == "lab/cited")
    assert actual.estimates == expected
    assert answer.answer.members == baseline.answer.members
    assert CITE_ONLY_WARNING not in actual.warnings
    assert all(item.record_id != cited["id"]
               for row in answer.results for contribution in row.contributions
               for item in contribution.evidence)


@pytest.mark.parametrize("cited_score, verified_score, penalty", [(80, 50, 0), (50, 80, 0.2)])
def test_soft_score_predicate_penalty_uses_verified_value(cited_score, verified_score, penalty):
    answer = answer_for(mixed_score_index(cited_score=cited_score, verified_score=verified_score),
                        where=[f"{BENCHMARK} = 50 soft(0.2)"])
    assert answer.answer.members == ["lab/cited"]
    assert answer.results[0].soft_penalty == penalty
    assert CITE_ONLY_WARNING not in answer.warnings
