"""Cited scores count as evidence without claiming machine verification."""

from dataclasses import replace
from datetime import date

import pytest

from decision.contract import CITE_ONLY_WARNING, parse_spec
from decision.engine import decide
from decision.model import evidence_verification_value
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, evidence, model, source_ref, verification


TODAY = date(2026, 10, 21)
CITED_URL = "https://docs.x.ai/results"
BENCHMARK = "swe_bench_pro"


def score_inputs(*, outcome=None, cited_id="lab/cited"):
    row = evidence(cited_id, BENCHMARK, 90, source="src-cited",
                   source_url=CITED_URL, outcome=outcome)
    return SnapshotInputs(
        models=[model(cited_id), model("lab/plain")],
        evidence=[row, evidence("lab/plain", BENCHMARK, 70)],
        sources={**SOURCES, "src-cited": CITED_URL},
        benchmark_domains={BENCHMARK: [("software_engineering", "direct")]},
        benchmark_metadata={BENCHMARK: {"random_baseline": 0, "sample_size": 100}},
    )


def load(inputs, **kwargs):
    return load_built_snapshot(build_snapshot(inputs, as_of=TODAY, **kwargs))


@pytest.mark.parametrize("outcome", [None, "verified"])
def test_cited_score_survives_snapshot_roundtrip_without_verification(outcome):
    index = load(score_inputs(outcome=outcome))
    rows = index.evidence("lab/cited", BENCHMARK)
    assert len(rows) == 1
    assert rows[0].value == 90
    assert rows[0].verified is False
    record = index.record(rows[0].record_id)
    assert record["verification"] is None
    assert record["citation"] == {
        "status": "cited", "sources": [{
            "source_id": "src-cited", "url": CITED_URL,
            "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None,
        }],
    }
    assert index.capability_estimate("lab/cited", "software_engineering") is not None
    assert index.evidence("lab/plain", BENCHMARK)[0].verified is True


@pytest.mark.parametrize("outcome", ["mismatch", "unreachable"])
@pytest.mark.parametrize("logged", [False, True])
def test_failed_cited_score_stays_out(outcome, logged):
    inputs = score_inputs(outcome="verified" if logged else outcome)
    if logged:
        row = inputs.evidence[0]
        inputs = replace(inputs, verifications=[verification(
            "evidence", row["id"], outcome, day="2026-10-21",
            value=evidence_verification_value(row),
        )])
    index = load(inputs)
    assert index.evidence("lab/cited", BENCHMARK) == ()


@pytest.mark.parametrize("outcome", [None, "verified"])
def test_card_redirect_cannot_grant_cited_score_admission(outcome):
    inputs = score_inputs(outcome=outcome)
    inputs.sources["src-cited"] = "https://board.example.org/results"
    inputs.evidence[0]["source_url"] = inputs.sources["src-cited"]
    inputs.evidence[0]["sources"][0]["resolved_urls"] = [CITED_URL]
    assert load(inputs).evidence("lab/cited", BENCHMARK) == ()


def test_mixed_cited_and_open_score_sources_stay_out():
    inputs = score_inputs(outcome="verified")
    inputs.evidence[0]["sources"].append(source_ref("src-board"))
    assert load(inputs).evidence("lab/cited", BENCHMARK) == ()


@pytest.mark.parametrize("url", ["https://x.ai:bad/", "https://reader@x.ai/", "http://["])
def test_invalid_cited_score_display_url_stays_out(url):
    inputs = score_inputs()
    inputs.evidence[0]["source_url"] = url
    assert load(inputs).evidence("lab/cited", BENCHMARK) == ()


@pytest.mark.parametrize("regions", [[""], [7], "not-a-list"])
def test_invalid_cited_score_region_stays_out(regions):
    inputs = score_inputs()
    inputs.evidence[0]["sources"][0]["cited_regions"] = regions
    assert load(inputs).evidence("lab/cited", BENCHMARK) == ()


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_cited_score_ranks_and_warns_on_the_recommendation(level):
    index = load(score_inputs())
    spec = parse_spec({"spec_version": 1, "optimize": {"max": BENCHMARK},
                       "explain": level}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert answer.results[0].model == "lab/cited"
    assert answer.answer.members == ["lab/cited"]
    assert CITE_ONLY_WARNING in answer.warnings
    assert CITE_ONLY_WARNING in answer.results[0].warnings
    if level != "none":
        items = [item for top in [*answer.top, *answer.results]
                 for contribution in top.contributions for item in contribution.evidence
                 if item.record_id == score_inputs().evidence[0]["id"]]
        assert items
        assert all(item.model_dump()["citation"]["status"] == "cited" for item in items)


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_tied_cited_score_outside_limit_still_warns(level):
    inputs = score_inputs(cited_id="lab/z-cited")
    inputs.evidence[0]["score"] = 70
    index = load(inputs)
    spec = parse_spec({"spec_version": 1, "optimize": {"max": BENCHMARK},
                       "explain": level, "limit": 1}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert answer.answer.kind == "tied"
    assert set(answer.answer.members) == {"lab/z-cited", "lab/plain"}
    assert [row.model for row in answer.results] == ["lab/plain"]
    assert CITE_ONLY_WARNING in answer.warnings


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_unused_cited_score_does_not_warn_for_plain_recommendation(level):
    index = load(score_inputs())
    spec = parse_spec({"spec_version": 1, "where": ["model.context_window >= 1000"],
                       "optimize": {"max": "model.context_window"},
                       "explain": level, "limit": 1}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert CITE_ONLY_WARNING not in answer.warnings
