"""Decision warnings describe cited facts used by this answer."""

from datetime import date

import pytest

from decision.bounded import project
from decision.contract import ResponseOptions, parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, fact, model, offering


WARNING = "cite_only_not_machine_verified"
NOTICE = "Cited, not machine-verified"


def index_with_citation(cited_facet="model.context_window", *, retired=False):
    models = []
    for mid, context, cls in (("lab/cited", 8000, "vectoriser"),
                              ("lab/plain", 200000, "text-generator")):
        records = [
            fact("model", mid, "model.context_window", context),
            fact("model", mid, "model.class", cls),
            fact("model", mid, "model.max_output_tokens", 4000),
        ]
        if mid == "lab/cited":
            next(row for row in records if row["facet"] == cited_facet)["sources"][0][
                "source_id"] = "src-xai"
        models.append(model(mid, facts=records,
                            lifecycle="retired" if retired and mid == "lab/cited" else "active"))
    return load_built_snapshot(build_snapshot(SnapshotInputs(
        models=models, sources={**SOURCES, "src-xai": "https://docs.x.ai/models"},
    ), as_of=date(2026, 10, 19)))


def answer_for(index, *, where=(), level="none", objective=None, limit=1):
    spec = parse_spec({"spec_version": 1, "where": list(where),
                       "optimize": objective or {"max": "model.context_window"},
                       "explain": level, "limit": limit}, facets=facet)
    answer = decide(spec, index, facets=facet)
    bounded = project(answer, ResponseOptions(fields=["model_rank"]), not_applied=[], spec=spec)
    return answer, bounded


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_unrelated_cited_candidate_excluded_by_class_does_not_warn(level):
    answer, bounded = answer_for(index_with_citation(), level=level, where=[
        "model.class = text-generator", "model.context_window >= 100000",
    ])
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert answer.results[0].warnings == []
    assert WARNING not in answer.warnings
    assert WARNING not in bounded["warnings"]
    assert NOTICE not in bounded["summary_for_user"]
    assert all(NOTICE not in item for item in bounded["must_mention"])


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_cited_filter_elimination_warns_even_when_only_plain_result_remains(level):
    answer, bounded = answer_for(index_with_citation(), level=level,
                                 where=["model.context_window >= 100000"])
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert answer.results[0].warnings == []
    assert WARNING in answer.warnings
    assert NOTICE in bounded["summary_for_user"]
    assert "This answer uses cited facts" in bounded["summary_for_user"]
    assert any("This answer uses cited facts" in item for item in bounded["must_mention"])


@pytest.mark.parametrize("condition", [
    {"all": ["model.class = text-generator", "model.context_window >= 100000"]},
    {"not": {"any": ["model.class = vectoriser", "model.context_window < 100000"]}},
])
def test_short_circuited_cited_predicate_does_not_warn(condition):
    answer, _ = answer_for(index_with_citation(), where=[condition])
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert WARNING not in answer.warnings


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_unused_hidden_citation_outside_limit_does_not_warn(level):
    answer, _ = answer_for(index_with_citation("model.max_output_tokens"), level=level)
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert WARNING not in answer.warnings


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_unused_hidden_citation_on_returned_row_keeps_only_row_warning(level):
    answer, bounded = answer_for(index_with_citation("model.max_output_tokens"),
                                 level=level, limit=2)
    assert {row.offering.model for row in answer.results} == {"lab/plain", "lab/cited"}
    cited = next(row for row in answer.results if row.offering.model == "lab/cited")
    assert WARNING in cited.warnings
    assert WARNING not in answer.warnings
    assert NOTICE not in bounded["summary_for_user"]
    assert all(NOTICE not in item for item in bounded["must_mention"])


def test_cited_ranking_input_outside_limit_warns():
    answer, _ = answer_for(index_with_citation())
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert WARNING in answer.warnings
    assert answer.results[0].warnings == []


def test_retired_candidate_citation_is_not_used():
    answer, _ = answer_for(index_with_citation(retired=True))
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert WARNING not in answer.warnings


def test_cited_reference_threshold_warns_after_reference_model_is_excluded():
    answer, _ = answer_for(index_with_citation(), where=[
        "model.class = text-generator", "model.context_window >= model(lab/cited)",
    ])
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert WARNING in answer.warnings


def test_shown_citation_outside_result_limit_warns():
    answer, _ = answer_for(index_with_citation("model.class"), level="full")
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert any(item.citation is not None for row in answer.top for item in row.facts)
    assert WARNING in answer.warnings


@pytest.mark.parametrize("where, warned", [
    (["model.max_output_tokens >= 5000 soft(0.2)"], True),
    (["model.max_output_tokens >= 5000 soft(0.2)", "model.class = text-generator"], False),
    (["model.class = text-generator", "model.max_output_tokens >= 5000 soft(0.2)"], False),
])
def test_cited_soft_penalty_only_warns_when_candidate_is_ranked(where, warned):
    answer, _ = answer_for(index_with_citation("model.max_output_tokens"), where=where)
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert (WARNING in answer.warnings) is warned


@pytest.mark.parametrize("limited", [False, True])
def test_computed_cost_tracks_cited_price_only_for_used_offering(limited):
    offers = []
    for mid, provider, price in (("lab/cited", "openai", 100),
                                  ("lab/plain", "sambanova", 1)):
        oid = f"{provider}/{mid}/global/standard"
        offers.append(offering(mid, provider, facts=[
            fact("offering", oid, "offering.price.input", price,
                 source="src-xai" if mid == "lab/cited" else "src-pricing"),
            fact("offering", oid, "offering.price.output", 1, source="src-pricing"),
        ]))
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/cited"), model("lab/plain")], offerings=offers,
        sources={**SOURCES, "src-xai": "https://docs.x.ai/models"},
    ), as_of=date(2026, 10, 19)))
    answer, _ = answer_for(index, objective={"min": "offering.cost_per_task"},
                           where=["offering.provider = sambanova"] if limited else [])
    assert [row.offering.model for row in answer.results] == ["lab/plain"]
    assert answer.results[0].warnings == []
    assert (WARNING in answer.warnings) is not limited
