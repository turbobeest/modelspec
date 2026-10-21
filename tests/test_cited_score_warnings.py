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
    inputs.evidence.extend(evidence("lab/cited", BENCHMARK, 90, eid=f"aa-driver-{index}")
                           for index in range(8))
    inputs = replace(
        inputs, models=[model(mid, facts=[fact("model", mid, "model.class", "text-generator")])
                        for mid in ("lab/cited", "lab/plain")],
        benchmark_refinements={BENCHMARK: [("rust", "direct")]},
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
    f"{BENCHMARK} = 50 soft(0.2)",
    f"{BENCHMARK} <= model(lab/plain)",
])
@pytest.mark.parametrize("cited_score, verified_score, warned", [(80, 50, False), (50, 80, True)])
def test_score_predicate_warning_uses_supporting_rows(condition, cited_score, verified_score, warned):
    answer = answer_for(mixed_score_index(cited_score=cited_score, verified_score=verified_score),
                        where=[condition])
    assert answer.answer.members == ["lab/cited"]
    assert (CITE_ONLY_WARNING in answer.warnings) is warned


@pytest.mark.parametrize("condition", [
    {"not": f"{BENCHMARK} = 90"},
    f"{BENCHMARK} = 90 soft(0.2)",
])
def test_failed_score_predicate_keeps_cited_provenance(condition):
    answer = answer_for(mixed_score_index(), where=[condition])
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING in answer.warnings
