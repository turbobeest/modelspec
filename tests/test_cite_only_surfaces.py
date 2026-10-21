"""Cited facts remain usable while every answer discloses their assurance."""

from datetime import date
from pathlib import Path

import pytest

from decision.bounded import project
from decision.contract import ResponseOptions, parse_spec
from decision.engine import decide
from decision.explain import ExplanationError, checked_record
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from pipeline.export import Build
from pipeline.load import Benchmark, Catalogue, Disposition, Model
from pipeline.render import benchmark_page, model_page
from tests.snapshot_records import SOURCES, fact, model, source_ref

WARNING = "cite_only_not_machine_verified"
NOTICE = "Cited, not machine-verified"


def cited_record(*, mixed=False):
    record = fact("model", "lab/cited", "model.context_window", 128000)
    record["sources"][0]["retrieved_at"] = "2026-10-19T12:00:00Z"
    if mixed:
        record["sources"].append(source_ref("src-board"))
    return record


def cited_index(state="known", *, mixed=False):
    record = cited_record(mixed=mixed)
    if state != "known":
        record["state"] = state
        record["value"] = None
    return load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/cited", facts=[record])],
        sources={**SOURCES, "src-lab-docs": "https://docs.x.ai/models"},
    ), as_of=date(2026, 10, 19)))


@pytest.mark.parametrize("level", ["none", "summary", "full"])
@pytest.mark.parametrize("mixed", [False, True])
def test_cited_fact_warns_in_complete_and_bounded_decisions(level, mixed):
    index = cited_index(mixed=mixed)
    spec = parse_spec({"spec_version": 1, "optimize": {"max": "model.context_window"},
                       "explain": level}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert answer.results
    assert WARNING in answer.warnings
    assert WARNING in answer.results[0].warnings
    bounded = project(answer, ResponseOptions(fields=["model_rank"]), not_applied=[], spec=spec)
    assert WARNING in bounded["warnings"]
    assert WARNING in bounded["results"][0]["warnings"]
    assert NOTICE in bounded["summary_for_user"]
    assert any(NOTICE in item for item in bounded["must_mention"])
    if level == "full":
        shown = next(item for item in answer.top[0].facts if item.facet == "model.context_window")
        citation = shown.model_dump(mode="json")["citation"]
        assert citation["status"] == "cited"
        expected_sources = [{
            "source_id": "src-lab-docs", "url": "https://docs.x.ai/models",
            "snapshot_ref": "sha256:" + "0" * 64,
            "retrieved_at": "2026-10-19T12:00:00Z",
        }]
        if mixed:
            expected_sources.append({
                "source_id": "src-board", "url": SOURCES["src-board"],
                "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None,
            })
        assert citation["sources"] == expected_sources
        for expected in expected_sources:
            source = next(item for item in answer.sources if item.id == expected["source_id"])
            assert source.date is None


def test_cited_record_never_passes_as_verified_evidence():
    record = cited_record()
    record.pop("facet")
    record["score"] = record.pop("value")
    record["verification"] = None
    record["citation"] = {"status": "cited", "sources": [{
        "source_id": "src-lab-docs", "url": "https://docs.x.ai/models",
        "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None,
    }]}

    class EvidenceSnapshot:
        def record(self, _rid):
            return record

        def source_url(self, _source_id):
            return "https://docs.x.ai/models"

    with pytest.raises(ExplanationError, match="not verified"):
        checked_record(EvidenceSnapshot(), "evidence")


@pytest.mark.parametrize("mixed", [False, True])
def test_model_page_names_cited_fact_and_source_without_claiming_verification(mixed):
    index = cited_index(mixed=mixed)
    fact_value = index.fact("lab/cited", "model.context_window")
    assert fact_value.record_id is not None
    record = index.record(fact_value.record_id)
    assert record["verification"] is None
    card = Model("lab/cited", Path("models/lab/cited.md"), {}, "", cited_facts=[record])
    html = model_page(card, Build(commit="test", built_at="2026-10-19T12:00:00Z",
                                 as_of=date(2026, 10, 19)), {}, Catalogue(as_of=date(2026, 10, 19)))
    assert NOTICE in html
    assert "model.context_window" in html
    assert 'href="https://docs.x.ai/models"' in html
    assert "2026-10-19T12:00:00Z" in html
    assert "sha256:" + "0" * 64 in html
    if mixed:
        assert f'href="{SOURCES["src-board"]}"' in html


@pytest.mark.parametrize("state", ["known", "not_disclosed", "requires_contract"])
@pytest.mark.parametrize("mixed", [False, True])
def test_named_comparison_preserves_citation_metadata(state, mixed):
    from decision.model_comparison import collect_models

    body = collect_models(["lab/cited"], cited_index(state, mixed=mixed))
    shown = next(row for row in body["models"][0]["facts"] if row["facet"] == "model.context_window")
    assert shown["citation"]["status"] == "cited"
    assert shown["citation"]["sources"][0]["url"] == "https://docs.x.ai/models"
    assert shown["state"] == state
    expected_ids = {"src-lab-docs", "src-board"} if mixed else {"src-lab-docs"}
    assert set(shown["source_ids"]) == expected_ids
    assert {source["source_id"] for source in shown["citation"]["sources"]} == expected_ids
    if mixed:
        assert shown["citation"]["sources"][1]["url"] == SOURCES["src-board"]
    if state != "known":
        assert shown["value"] is None


def test_cited_estate_gain_does_not_warn_for_current_answer():
    from tests.snapshot_records import subscription

    plan = subscription(facts=[
        fact("offering", "sambanova/subscription/pro", facet_id, value, source="src-pricing")
        for facet_id, value in (
            ("offering.subscription.price", 20),
            ("offering.subscription.billing_period", "monthly"),
            ("offering.subscription.models_covered", ["lab/alpha"]),
            ("offering.subscription.surfaces", ["chat_app"]),
        )
    ])
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/alpha")], subscriptions=[plan],
        sources={**SOURCES, "src-pricing": "https://perplexity.ai/pro"},
    ), as_of=date(2026, 10, 19)))
    spec = parse_spec({"spec_version": 1, "estate": {},
                       "optimize": {"max": "model.context_window"}, "explain": "none"}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert any(gain.add.id == "sambanova/subscription/pro" for gain in answer.with_estate.gain)
    assert WARNING in answer.with_estate.warnings
    assert WARNING not in answer.warnings


def test_cited_plan_warns_in_vocabulary_routes_and_estate():
    from decision.vocabulary import _estate_ids
    from decision.registry import default
    from tests.snapshot_records import subscription

    plan = subscription(facts=[
        fact("offering", "sambanova/subscription/pro", "offering.subscription.price", 20),
        fact("offering", "sambanova/subscription/pro", "offering.subscription.billing_period", "monthly"),
        fact("offering", "sambanova/subscription/pro", "offering.subscription.models_covered", ["lab/alpha"]),
        fact("offering", "sambanova/subscription/pro", "offering.subscription.surfaces", ["chat_app"]),
    ])
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/alpha")], subscriptions=[plan],
        sources={**SOURCES, "src-lab-docs": "https://perplexity.ai/pro"},
    ), as_of=date(2026, 10, 19)))
    published = _estate_ids(index, default())["plans"][0]
    assert WARNING in published["warnings"]
    assert published["citations"]["offering.subscription.price"]["status"] == "cited"
    spec = parse_spec({"spec_version": 1, "access": "chat_app",
                       "estate": {"plans": ["sambanova/subscription/pro"]},
                       "optimize": {"max": "model.context_window"}, "explain": "full"}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert NOTICE in answer.results[0].plans[0].basis
    assert WARNING in answer.with_estate.warnings
    assert WARNING in answer.with_estate.results[0].warnings


def test_ordinary_facts_keep_verified_provenance_without_citation_fields():
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/ordinary")], sources=SOURCES,
    ), as_of=date(2026, 10, 19)))
    spec = parse_spec({"spec_version": 1, "optimize": {"max": "model.context_window"},
                       "explain": "full"}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert WARNING not in answer.warnings
    assert all(WARNING not in row.warnings for row in answer.results)
    assert all("citation" not in shown.model_dump(mode="json") for shown in answer.top[0].facts)
    assert all(source.date is not None for source in answer.sources)


def test_cited_benchmark_card_never_labels_its_evidence_verified():
    evidence = {
        "benchmark_id": "demo", "score": 50, "unit": "percent",
        "source_url": "https://docs.x.ai/benchmarks", "evidence_date": "2026-10-19",
        "source_kind": "provider_self_report", "model_id_as_evaluated": "lab/cited",
    }
    card = Model("lab/cited", Path("models/lab/cited.md"), {
        "benchmarks": {"scores": {"demo": 50}, "evidence": [evidence]},
    }, "")
    html = model_page(card, Build(commit="test", built_at="2026-10-19T12:00:00Z",
                                 as_of=date(2026, 10, 19)), {}, Catalogue(as_of=date(2026, 10, 19)))
    assert NOTICE in html
    assert "Verified benchmark evidence" not in html
    assert 'basis-verified' not in html.split('<body', 1)[-1]


def test_cited_catalogue_result_is_not_presented_as_verified():
    bench = Benchmark("demo", Path("benchmarks/demo.md"), {}, "")
    result = {"model_id": "lab/cited", "score": 90, "unit": "percent",
              "source_url": "https://docs.x.ai/benchmarks", "evidence_date": "2026-10-19"}
    catalogue = Catalogue(date(2026, 10, 19), {
        "demo": Disposition("active", "demo", results=(result,)),
    })
    html = benchmark_page(bench, Build("test", "2026-10-19T12:00:00Z", catalogue.as_of), catalogue, [])
    assert NOTICE in html
    assert "Verified results" not in html
    assert 'href="https://docs.x.ai/benchmarks"' in html
