"""Cite-only facts remain usable without becoming machine-verified."""

from datetime import UTC, date, datetime
from dataclasses import replace

import pytest

from decision import verify
from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from decision.sources import CopyStore
from tests.snapshot_records import SOURCES, evidence, fact, model, offering, subscription, verification
from tests.test_decision_snapshot import COMPLETENESS_REGISTRY

TODAY = date(2026, 10, 19)
FETCHED = datetime(2026, 10, 18, 16, tzinfo=UTC)
CITE_URL = "https://docs.x.ai/docs/models"


class CiteRegions:
    def source_url(self, source_id):
        return CITE_URL

    def text(self, *args):
        pytest.fail("cite-only source bytes must never be read")


def claim(field="model.context_window", value=128000):
    row = fact("model", "lab/alpha", field, value, outcome=None)
    return verify.Claim(
        target=TargetRef(kind="fact", id=row["id"]),
        subject="lab/alpha", names=("Alpha",), field=field, value=value,
        collector=VerificationActor(agent="collector", model_family="collector", method="read"),
        sources=(SourceRef.model_validate(row["sources"][0]),),
    )


def snapshot_input(*, outcome=None, url=CITE_URL, facets=None):
    rows = model("lab/alpha")["facts"] if facets is None else facets
    for row in rows:
        row["sources"][0]["retrieved_at"] = FETCHED.isoformat()
        if outcome is None:
            row.pop("verification", None)
        elif outcome != "verified":
            row["verification"]["outcome"] = outcome
            if outcome == "mismatch":
                row["verification"]["diff"] = "value differs"
    return SnapshotInputs(
        models=[model("lab/alpha", facts=rows)], sources={**SOURCES, "src-lab-docs": url},
    )


def loaded(inputs, *, premier=None, registry=None):
    return load_built_snapshot(build_snapshot(
        inputs, as_of=TODAY, premier=premier, registry=registry,
    ))


def test_cite_source_ref_preserves_fetch_timestamp_without_changing_old_refs():
    raw = fact("model", "lab/alpha", "model.context_window", 128000)["sources"][0]
    assert SourceRef.model_validate(raw).model_dump(mode="json") == raw
    cited = SourceRef.model_validate({**raw, "retrieved_at": FETCHED.isoformat()})
    assert cited.retrieved_at == FETCHED
    assert SourceRef.model_validate_json(cited.model_dump_json()) == cited


@pytest.mark.parametrize("field,value", [
    ("model.context_window", 128000),
    ("origin.lab_jurisdiction", ["US"]),
    ("offering.subscription.price", 20),
])
def test_cite_verifier_returns_cited_without_reading_or_verifying(field, value):
    result = verify.verify(claim(field, value), CiteRegions(), (), today=TODAY)
    assert result.outcome == "cited"
    assert result.verification is None
    assert "cite" in result.reason


def test_cite_run_checks_queue_without_verification_or_recrawl(tmp_path):
    queue, log = verify.Queue(tmp_path), verify.VerificationLog(tmp_path)
    queue.file(claim(), at=FETCHED)
    report = verify.run(queue, log, CiteRegions(), (), today=TODAY)
    assert report.counts["cited"] == 1
    assert report.counts["verified"] == 0
    assert not log.records()
    assert queue.pending() == ([], [])
    assert queue.recrawl_requests() == []


@pytest.mark.parametrize("outcome", [None, "verified"])
@pytest.mark.parametrize("url", [
    CITE_URL, "https://www.anthropic.com/models", "https://developers.openai.com/models",
    "https://help.openai.com/models", "https://chatgpt.com/models", "https://cursor.com/models",
])
def test_cite_facts_satisfy_premier_completeness_without_verification(outcome, url):
    index = loaded(snapshot_input(outcome=outcome, url=url), premier=["lab/alpha"],
                   registry=COMPLETENESS_REGISTRY)
    row = index.fact("lab/alpha", "model.context_window")
    assert row.state == "known" and row.value == 128000
    record = index.record(row.record_id)
    assert record["verification"] is None
    assert record["citation"] == {
        "status": "cited", "sources": [{
            "source_id": "src-lab-docs", "url": url,
            "snapshot_ref": "sha256:" + "0" * 64,
            "retrieved_at": "2026-10-18T16:00:00+00:00",
        }],
    }
    assert row.record_id in index.cited_facts("lab/alpha")


@pytest.mark.parametrize("outcome", ["mismatch", "unreachable"])
def test_cite_policy_does_not_override_failed_verification(outcome):
    index = loaded(snapshot_input(outcome=outcome))
    assert index.fact("lab/alpha", "model.context_window").state == "unknown"


def test_cite_policy_does_not_admit_normal_host_unverified_facts():
    index = loaded(snapshot_input(url="https://example.org/models"))
    assert index.fact("lab/alpha", "model.context_window").state == "unknown"


@pytest.mark.parametrize("facet", ["offering.api_model_id", "offering.router_slug"])
def test_cite_policy_does_not_promote_operational_identifiers(facet):
    oid = "sambanova/lab/alpha/global/standard"
    row = fact("offering", oid, facet, "lab-alpha", outcome=None)
    inputs = snapshot_input()
    inputs = replace(inputs, offerings=[offering("lab/alpha", facts=[row])])
    index = loaded(inputs)
    assert index.fact(oid, facet).state == "unknown"


def test_cite_snapshot_requires_valid_snapshot_hash():
    inputs = snapshot_input()
    inputs.models[0]["facts"][0]["sources"][0]["snapshot_ref"] = "not-a-hash"
    index = loaded(inputs)
    assert index.fact("lab/alpha", "model.context_window").state == "unknown"


def test_cite_admission_still_validates_facet_value():
    inputs = snapshot_input()
    inputs.models[0]["facts"][0]["value"] = "large"
    assert loaded(inputs).fact("lab/alpha", "model.context_window").state == "unknown"


def test_authored_citation_cannot_relabel_an_ordinary_verified_fact():
    inputs = snapshot_input(outcome="verified", url="https://example.org/models")
    inputs.models[0]["facts"][0]["citation"] = {"status": "cited", "sources": []}
    index = loaded(inputs)
    row = index.fact("lab/alpha", "model.context_window")
    assert "citation" not in index.record(row.record_id)


def test_cite_lookup_includes_model_inheritance_and_subscription_facts():
    inputs = snapshot_input()
    inputs = replace(inputs, offerings=[offering("lab/alpha")], subscriptions=[subscription()])
    inputs.sources["src-pricing"] = CITE_URL
    index = loaded(inputs)
    assert set(index.cited_facts("lab/alpha")) <= set(index.cited_facts(
        "sambanova/lab/alpha/global/standard"))
    assert index.cited_facts("sambanova/subscription/pro")


@pytest.mark.parametrize("url", [CITE_URL, "https://example.org/models"])
def test_cite_lookup_does_not_load_full_provenance(url, monkeypatch):
    index = loaded(snapshot_input(outcome="verified", url=url))

    def reject_provenance_load(_record_id):
        pytest.fail("citation warning lookup must not unpack full provenance")

    monkeypatch.setattr(index, "record", reject_provenance_load)
    assert bool(index.cited_facts("lab/alpha")) is (url == CITE_URL)


def test_cite_redirect_policy_survives_snapshot_build_without_local_copy_store():
    inputs = snapshot_input(url="https://example.org/redirect")
    for row in inputs.models[0]["facts"]:
        row["sources"][0]["resolved_urls"] = [CITE_URL]
    index = loaded(inputs)
    record = index.record(index.fact("lab/alpha", "model.context_window").record_id)
    assert record["verification"] is None
    assert record["citation"]["status"] == "cited"


def test_cite_redirect_evidence_cannot_enter_as_verified():
    row = evidence("lab/alpha", "swe_bench_pro", 55.0)
    row["sources"][0]["resolved_urls"] = [CITE_URL]
    index = loaded(replace(snapshot_input(), evidence=[row]))
    assert index.evidence("lab/alpha", "swe_bench_pro") == ()


def test_cite_copy_marker_blocks_verification_after_redirect(tmp_path):
    store = CopyStore(tmp_path / "copies")
    store.record_citation("sha256:" + "0" * 64, source_url=SOURCES["src-lab-docs"],
                          retrieved_at=FETCHED, resolved_urls=[CITE_URL])
    source = Source(id="src-lab-docs", url=SOURCES["src-lab-docs"], cited_regions=[
        {"id": "r1", "locator": {"kind": "page", "value": ""}},
    ])
    regions = verify.StoredRegions(store, {source.id: source})
    result = verify.verify(claim(), regions, (), today=TODAY)
    assert result.outcome == "cited"
    assert result.verification is None


def test_cite_latest_mismatch_in_log_still_quarantines():
    inputs = snapshot_input(outcome="verified")
    inputs = replace(inputs, verifications=[verification(
        "fact", "lab/alpha#model.context_window", "mismatch", day="2026-10-19",
    )])
    assert loaded(inputs).fact("lab/alpha", "model.context_window").state == "unknown"


@pytest.mark.parametrize("specialized", ["xai_matrix", "dated_price", "evidence"])
def test_cite_policy_precedes_specialized_verification(specialized):
    request = claim()
    if specialized == "xai_matrix":
        request = replace(request, subject="xai/subscription/supergrok-lite",
                          field="offering.subscription.models_covered")
    elif specialized == "dated_price":
        request = replace(request, conditions={"effective_from": "2026-10-01"})
    else:
        request = replace(request, value={"score": 55.0})
    assert verify.verify(request, CiteRegions(), (), today=TODAY).outcome == "cited"


def test_cite_stored_regions_refuses_historical_copy(tmp_path):
    store = CopyStore(tmp_path / "copies")
    ref = store.put(b"historical synthetic fixture", source_url="https://fixture.example/")
    source = Source(id="source", url=CITE_URL, cited_regions=[
        {"id": "page", "locator": {"kind": "page", "value": ""}},
    ])
    regions = verify.StoredRegions(store, {source.id: source}, cache_documents=True)
    assert regions.text(source.id, ref, "page") is None
    assert regions._documents == {}
