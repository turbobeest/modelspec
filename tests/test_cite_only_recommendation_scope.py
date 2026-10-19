"""Citation notices follow recommendations across offerings and answer shapes."""

from datetime import date

import pytest

from decision.bounded import project
from decision.contract import CITE_ONLY_WARNING, ResponseOptions, parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, fact, model, offering


@pytest.fixture(params=["none", "summary", "full"])
def level(request):
    return request.param


def _model(mid, context, output=4000, *, cited=False, unknown_output=False):
    return model(mid, facts=[
        fact("model", mid, "model.context_window", context,
             source="src-xai" if cited else "src-lab-docs"),
        fact("model", mid, "model.max_output_tokens", output,
             state="not_disclosed" if unknown_output else "known"),
    ])


def _answer(models, level, *, offers=(), where=(), objective=None):
    snapshot = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=models, offerings=list(offers),
        sources={**SOURCES, "src-xai": "https://docs.x.ai/models"},
    ), as_of=date(2026, 10, 19)))
    spec = parse_spec({
        "spec_version": 1, "where": list(where),
        "optimize": objective or {"max": "model.context_window"},
        "explain": level, "limit": 1,
    }, facets=facet)
    decision = decide(spec, snapshot, facets=facet)
    bounded = project(decision, ResponseOptions(fields=["model_rank"]),
                      not_applied=[], spec=spec)
    return decision, bounded


def _assert_warning(decision, bounded, expected):
    assert (CITE_ONLY_WARNING in decision.warnings) is expected
    assert (CITE_ONLY_WARNING in bounded["warnings"]) is expected


def test_eliminated_cited_sibling_offering_does_not_warn_for_recommended_model(level):
    mid = "lab/plain"
    offers = []
    for provider, price, source in (
        ("openai", 100, "src-xai"), ("sambanova", 1, "src-pricing"),
    ):
        oid = f"{provider}/{mid}/global/standard"
        offers.append(offering(mid, provider, facts=[
            fact("offering", oid, "offering.price.input", price, source=source),
            fact("offering", oid, "offering.price.output", 1, source="src-pricing"),
        ]))
    decision, bounded = _answer([_model(mid, 16000)], level, offers=offers,
                                 where=["offering.price.input <= 10"])
    assert decision.answer.members == [mid]
    assert [(row.model, row.offering.provider) for row in decision.results] == [
        (mid, "sambanova")]
    assert CITE_ONLY_WARNING not in decision.results[0].warnings
    _assert_warning(decision, bounded, False)


@pytest.mark.parametrize("cited_recommendation", [False, True])
def test_partial_answer_warns_only_for_its_ranked_recommendation(level, cited_recommendation):
    decision, bounded = _answer([
        _model("lab/recommended", 16000, cited=cited_recommendation),
        _model("lab/maybe", 32000, cited=not cited_recommendation, unknown_output=True),
    ], level, where=["model.max_output_tokens >= 1000"])
    assert decision.status == "partial"
    assert decision.answer.members == ["lab/recommended"]
    assert [row.model for row in decision.results] == ["lab/recommended"]
    assert [row.model for row in decision.may_qualify] == ["lab/maybe"]
    _assert_warning(decision, bounded, cited_recommendation)


def test_cited_tied_member_outside_returned_limit_still_warns(level):
    decision, bounded = _answer([
        _model("lab/a-plain", 8000), _model("lab/z-cited", 8000, cited=True),
    ], level)
    assert decision.answer.kind == "tied"
    assert decision.answer.members == ["lab/a-plain", "lab/z-cited"]
    assert [row.model for row in decision.results] == ["lab/a-plain"]
    assert CITE_ONLY_WARNING not in decision.results[0].warnings
    _assert_warning(decision, bounded, True)


@pytest.mark.parametrize("objective", [
    {"lexicographic": [{"max": "model.context_window"}, {"max": "model.max_output_tokens"}]},
    {"pareto": ["model.context_window", "model.max_output_tokens"]},
])
@pytest.mark.parametrize("cited_recommendation", [False, True])
def test_null_answer_warns_only_for_returned_ranked_recommendation(
        level, objective, cited_recommendation):
    decision, bounded = _answer([
        _model("lab/plain", 16000, 4000),
        _model("lab/cited", 32000 if cited_recommendation else 8000,
               8000 if cited_recommendation else 2000, cited=True),
    ], level, objective=objective)
    assert decision.status == "answered"
    assert decision.answer is None
    assert [row.model for row in decision.results] == [
        "lab/cited" if cited_recommendation else "lab/plain"]
    _assert_warning(decision, bounded, cited_recommendation)


@pytest.mark.parametrize("reference", ["model", "best"])
def test_cited_reference_admitting_recommendation_warns_after_reference_is_eliminated(
        level, reference):
    if reference == "model":
        where = ["model.max_output_tokens >= 4000",
                 "model.context_window >= model(lab/reference)"]
        reference_context = 8000
    else:
        where = ["model.context_window >= best(8000)",
                 "model.max_output_tokens >= best(0)"]
        reference_context = 24000
    decision, bounded = _answer([
        _model("lab/recommended", 16000, 4000),
        _model("lab/reference", reference_context, 1000, cited=True),
    ], level, where=where)
    assert decision.answer.members == ["lab/recommended"]
    assert [row.model for row in decision.results] == ["lab/recommended"]
    assert CITE_ONLY_WARNING not in decision.results[0].warnings
    _assert_warning(decision, bounded, True)


def test_citation_on_only_may_qualify_row_does_not_warn_without_recommendation(level):
    decision, bounded = _answer([
        _model("lab/maybe", 16000, cited=True, unknown_output=True),
    ], level, where=["model.max_output_tokens >= 1000"])
    assert decision.status == "no_feasible"
    assert decision.answer is None
    assert decision.results == []
    assert [row.model for row in decision.may_qualify] == ["lab/maybe"]
    _assert_warning(decision, bounded, False)
