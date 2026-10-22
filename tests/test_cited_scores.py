"""Cited scores count as evidence without claiming machine verification."""

from dataclasses import replace
from datetime import date
import gzip

import pytest

from decision.contract import CITE_ONLY_WARNING, parse_spec
from decision.engine import decide
from decision.excluded import ExcludedSources
from decision.model import evidence_verification_value
from decision.registry import facet
from decision.snapshot import (
    SnapshotInputs, build_snapshot, canonical_json, content_hash, load_built_snapshot,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, evidence, model, offering, source_ref, verification


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
    built = build_snapshot(score_inputs(outcome=outcome), as_of=TODAY)
    assert built.envelope(None)["format_version"] == 2
    index = load_built_snapshot(built)
    rows = index.evidence("lab/cited", BENCHMARK)
    assert len(rows) == 1
    assert rows[0].value == 90
    assert rows[0].verified is False
    corpus_row = next(row for _, row in index.corpus_evidence()
                      if row.record_id == rows[0].record_id)
    assert corpus_row.verified is False
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


def test_format_one_verified_snapshot_remains_readable():
    inputs = score_inputs(outcome="verified")
    inputs.sources["src-cited"] = SOURCES["src-board"]
    inputs.evidence[0]["source_url"] = SOURCES["src-board"]
    envelope = build_snapshot(inputs, as_of=TODAY).envelope(None)
    envelope["format_version"] = 1
    envelope["content"]["format_version"] = 1
    digest = content_hash(envelope["content"])
    envelope.update(content_hash=digest, snapshot_id="snap_" + digest.split(":")[1][:16])
    raw = gzip.compress(canonical_json(envelope))
    index = load_snapshot_bytes(raw, key=None, public_keys={})
    assert index.evidence("lab/cited", BENCHMARK)[0].verified is True


@pytest.mark.parametrize("verified_first", [False, True])
@pytest.mark.parametrize("mixed", [False, True])
def test_cited_offering_score_cannot_replace_its_models_verified_score(verified_first, mixed):
    inputs = score_inputs()
    oid = "sambanova/lab/cited/global/standard"
    inputs.evidence[0] = evidence(
        oid, BENCHMARK, 40, source="src-cited", source_url=CITED_URL,
        subject_kind="offering", outcome=None,
    )
    if mixed:
        inputs.evidence[0]["sources"].append(source_ref("src-board"))
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 95))
    if verified_first:
        inputs.evidence.reverse()
    index = load(replace(inputs, offerings=[offering("lab/cited")]))
    spec = parse_spec({
        "spec_version": 1, "where": [f"{BENCHMARK} >= 80"],
        "optimize": {"max": BENCHMARK}, "explain": "full",
    }, facets=facet)

    answer = decide(spec, index, facets=facet)

    assert answer.status == "answered"
    assert answer.answer.members == ["lab/cited"]
    assert answer.results[0].offering.provider == "sambanova"
    assert answer.results[0].contributions[0].raw_value == 95
    assert CITE_ONLY_WARNING not in answer.warnings
    assert CITE_ONLY_WARNING not in answer.results[0].warnings
    assert [(row.value, row.verified) for row in index.evidence(oid, BENCHMARK)] == [(95, True)]


@pytest.mark.parametrize("outcome", [None, "mismatch", "unreachable"])
def test_rejected_open_score_does_not_displace_cited_score(outcome):
    inputs = score_inputs()
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 40, outcome=outcome))
    index = load(inputs)
    spec = parse_spec({
        "spec_version": 1, "optimize": {"max": BENCHMARK}, "explain": "full",
    }, facets=facet)

    answer = decide(spec, index, facets=facet)

    assert answer.status == "answered"
    assert answer.answer.members == ["lab/cited"]
    assert answer.results[0].contributions[0].raw_value == 90
    assert CITE_ONLY_WARNING in answer.warnings


def test_cited_precedence_preserves_multiple_verified_measurements():
    inputs = score_inputs()
    inputs.evidence.extend([
        evidence("lab/cited", BENCHMARK, 95),
        evidence("lab/cited", BENCHMARK, 96),
    ])
    index = load(inputs)
    spec = parse_spec({
        "spec_version": 1, "optimize": {"max": BENCHMARK}, "explain": "full",
    }, facets=facet)

    answer = decide(spec, index, facets=facet)

    assert answer.status == "partial"
    assert answer.answer.members == ["lab/plain"]
    assert [row.value for row in index.evidence("lab/cited", BENCHMARK)] == [95, 96]
    assert CITE_ONLY_WARNING not in answer.warnings


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


@pytest.mark.parametrize("outcome", [None, "verified"])
def test_mixed_cited_and_open_score_sources_are_cited_with_every_ref(outcome):
    inputs = score_inputs(outcome=outcome)
    inputs.evidence[0]["sources"].append(source_ref("src-board"))
    index = load(inputs)
    rows = index.evidence("lab/cited", BENCHMARK)
    assert len(rows) == 1
    assert rows[0].value == 90 and rows[0].verified is False
    record = index.record(rows[0].record_id)
    assert record["verification"] is None
    assert record["sources"] == inputs.evidence[0]["sources"]
    assert record["citation"] == {
        "status": "cited", "sources": [
            {"source_id": source_id, "url": url,
             "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None}
            for source_id, url in [("src-cited", CITED_URL), ("src-board", SOURCES["src-board"])]
        ],
    }


@pytest.mark.parametrize("mixed_first", [False, True])
def test_mixed_cited_score_loses_to_verified_sibling(mixed_first):
    inputs = score_inputs(outcome="verified")
    inputs.evidence[0]["sources"].append(source_ref("src-board"))
    inputs.evidence.append(evidence("lab/cited", BENCHMARK, 60))
    if mixed_first:
        inputs.evidence.reverse()
    index = load(inputs)
    assert [(row.value, row.verified) for row in index.evidence("lab/cited", BENCHMARK)] == [
        (60, True)]
    spec = parse_spec({"spec_version": 1, "optimize": {"max": BENCHMARK},
                       "explain": "full"}, facets=facet)
    answer = decide(spec, index, facets=facet)
    assert answer.answer.members == ["lab/plain"]
    assert CITE_ONLY_WARNING not in answer.warnings


@pytest.mark.parametrize("damage", [{"snapshot_ref": "invalid"}, {"resolved_urls": None}])
def test_mixed_score_with_malformed_retained_ref_is_excluded(damage):
    inputs = score_inputs(outcome="verified")
    inputs.evidence[0]["sources"].append({**source_ref("src-board"), **damage})
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


def test_cited_score_redirect_to_excluded_source_stays_out():
    inputs = score_inputs()
    inputs.evidence[0]["sources"][0]["resolved_urls"] = ["https://blocked.example/results"]
    index = load(inputs, guard=ExcludedSources(hosts=("blocked.example",)))
    assert index.evidence("lab/cited", BENCHMARK) == ()


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
