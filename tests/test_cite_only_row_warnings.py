"""Citation assurance stays attached to every disclosed candidate row."""

from datetime import date
from types import SimpleNamespace

import pytest

from decision.bands import Banded, entries
from decision.by_model import build_by_model
from decision.contract import (
    BandEntry,
    MayQualify,
    ModelElimination,
    ModelOffering,
    OfferingElimination,
    OfferingRef,
    parse_spec,
)
from decision.engine import decide
from decision.optimise import OptimisedResult
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, fact, model, offering


WARNING = "cite_only_not_machine_verified"
REF = {"model": "lab/cited"}


@pytest.mark.parametrize("row_type, fields", [
    (MayQualify, {"model": "lab/cited", "unknown": ["model.context_window"]}),
    (ModelElimination, {"model": "lab/cited", "condition": "too small"}),
    (OfferingElimination, {"offering": REF, "condition": "too small"}),
    (ModelOffering, {"offering": REF, "status": "ranked"}),
    (BandEntry, {"model": "lab/cited", "offering": REF,
                 "score": 1, "score_interval": (1, 1)}),
])
def test_row_warning_is_additive_and_empty_warnings_are_omitted(row_type, fields):
    ordinary = row_type(**fields).model_dump(mode="json")
    assert "warnings" not in ordinary
    cited = row_type(**fields, warnings=[WARNING]).model_dump(mode="json")
    assert cited == {**ordinary, "warnings": [WARNING]}


def _answer(*, cited=True, hosted=False, unknown=False):
    models = []
    offerings = []
    for mid, context, price in (("lab/cited", 8000, 10), ("lab/plain", 200000, 1)):
        source = "src-cited" if cited and mid == "lab/cited" else "src-lab-docs"
        models.append(model(mid, facts=[
            fact("model", mid, "model.context_window", context,
                 state="unknown" if unknown and mid == "lab/cited" else "known",
                 source="src-lab-docs" if unknown else source),
            fact("model", mid, "model.max_output_tokens", 4000, source=source),
        ]))
        if hosted:
            oid = f"sambanova/{mid}/global/standard"
            offerings.append(offering(mid, facts=[
                fact("offering", oid, "offering.price.input", price, source=source),
            ]))
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=models, offerings=offerings,
        sources={**SOURCES, "src-cited": "https://docs.x.ai/models"},
    ), as_of=date(2026, 10, 19)))
    condition = "offering.price.input <= 2" if hosted else "model.context_window >= 100000"
    spec = parse_spec({"spec_version": 1, "where": [condition],
                       "optimize": {"max": "model.max_output_tokens"},
                       "explain": "full", "limit": 20}, facets=facet)
    return decide(spec, index, facets=facet)


@pytest.mark.parametrize("hosted", [False, True])
def test_cited_elimination_warns_in_flat_grouped_and_by_model_rows(hosted):
    answer = _answer(hosted=hosted)
    eliminated = [row for row in answer.eliminated.models if row.model == "lab/cited"]
    assert eliminated
    assert all(row.model_dump().get("warnings") == [WARNING] for row in eliminated)
    group = next(row for row in answer.eliminated.model_groups if row.model == "lab/cited")
    grouped = group.offerings if hosted else [group.model_elimination]
    assert grouped and all(row is not None for row in grouped)
    assert all(row.model_dump().get("warnings") == [WARNING] for row in grouped)
    by_model = next(row for row in answer.by_model if row.model == "lab/cited")
    assert all(row.model_dump().get("warnings") == [WARNING] for row in by_model.offerings)


def test_may_qualify_grouping_keeps_candidate_warning():
    answer = _answer(unknown=True)
    candidate = next(row for row in answer.may_qualify if row.model == "lab/cited")
    assert candidate.warnings == [WARNING]
    grouped = build_by_model(answer, lambda ref: None)
    row = next(row for row in grouped if row.model == "lab/cited")
    assert row.offerings[0].model_dump().get("warnings") == [WARNING]


def test_ranked_grouping_keeps_candidate_warning():
    answer = _answer()
    answer.results[0].warnings = [WARNING]
    grouped = build_by_model(answer, lambda ref: None)
    row = next(row for row in grouped if row.model == answer.results[0].model)
    assert row.offerings[0].model_dump().get("warnings") == [WARNING]


def test_ordinary_elimination_rows_keep_their_serialized_shape():
    answer = _answer(cited=False)
    assert all("warnings" not in row.model_dump() for row in answer.eliminated.models)
    assert all("warnings" not in row.model_dump()
               for model_row in answer.by_model for row in model_row.offerings)


def test_existing_non_citation_result_warning_does_not_expand_grouped_rows():
    answer = _answer(cited=False)
    answer.results[0].warnings = ["proxy_only"]
    grouped = build_by_model(answer, lambda ref: None)
    assert all("warnings" not in row.model_dump()
               for model_row in grouped for row in model_row.offerings)


@pytest.mark.parametrize("name", ["best", "rest", "thin"])
def test_each_band_keeps_citation_on_its_affected_row_only(name):
    rows = tuple(OptimisedResult(mid, (), 1.0, 0.0, (), (), (1.0, 1.0))
                 for mid in ("lab/cited", "lab/plain"))
    banded = Banded(rows[0] if name == "best" else None,
                    rows if name == "best" else (), rows if name == "rest" else (),
                    rows if name == "thin" else (), {})
    snapshot = SimpleNamespace(model_of=lambda cid: cid,
                               cited_facts=lambda cid: ("fact-id",) if cid == "lab/cited" else ())
    result = entries(banded, snapshot, lambda cid: OfferingRef(model=cid), lambda cid: None, {})
    cited, ordinary = getattr(result, name)
    assert cited.model_dump().get("warnings") == [WARNING]
    assert "warnings" not in ordinary.model_dump()


@pytest.mark.parametrize("host", ["x.ai", "docs.x.ai", "perplexity.ai"])
@pytest.mark.parametrize("position", ["rest", "eliminated", "recommended", "tied"])
def test_grok_warning_stays_on_its_row_unless_the_answer_recommends_it(host, position):
    cited_context = 8000 if position in {"rest", "eliminated"} else 200000
    plain_context = 200000 if position == "tied" else 100000
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[
            model("xai/grok-4-7", facts=[fact("model", "xai/grok-4-7", "model.context_window",
                                           cited_context, source="src-cited")]),
            model("lab/plain", context=plain_context),
        ],
        sources={**SOURCES, "src-cited": f"https://{host}/models"},
    ), as_of=date(2026, 10, 19)))
    spec = parse_spec({"spec_version": 1,
                       "where": ["model.context_window >= 100000"] if position == "eliminated" else [],
                       "optimize": {"max": "model.context_window"},
                       "explain": "full", "limit": 20}, facets=facet)
    answer = decide(spec, index, facets=facet)
    if position == "eliminated":
        row = next(row for row in answer.eliminated.models if row.model == "xai/grok-4-7")
    else:
        band = answer.bands.rest if position == "rest" else answer.bands.best
        row = next(row for row in band if row.model == "xai/grok-4-7")
    assert row.model_dump().get("warnings") == [WARNING]
    assert (WARNING in answer.warnings) is (position in {"recommended", "tied"})
    if position == "tied":
        assert answer.answer.kind == "tied"
        assert set(answer.answer.members) == {"xai/grok-4-7", "lab/plain"}
