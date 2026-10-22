"""Cited benchmark provenance survives each public evidence representation."""

import httpx
import pytest
from typer.testing import CliRunner

from cli.modelspec import cli, client
from decision.contract import ComparisonEvidence, EvidenceItem
from decision.model_comparison import collect_models
from tests.snapshot_records import SOURCES, source_ref
from tests.test_cited_scores import BENCHMARK, CITED_URL, load, score_inputs


CITATION = {
    "status": "cited",
    "sources": [{
        "source_id": "src-cited", "url": CITED_URL,
        "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None,
    }],
}


@pytest.fixture(params=[False, True], ids=["cite-only", "mixed"])
def citation_case(request):
    inputs = score_inputs()
    citation = {**CITATION, "sources": list(CITATION["sources"])}
    if request.param:
        inputs.evidence[0]["sources"].append({
            **source_ref("src-board"),
            "snapshot_ref": "sha256:" + "1" * 64,
            "retrieved_at": "2026-10-20T12:00:00Z",
        })
        citation["sources"].append({
            "source_id": "src-board", "url": SOURCES["src-board"],
            "snapshot_ref": "sha256:" + "1" * 64,
            "retrieved_at": "2026-10-20T12:00:00Z",
        })
    return inputs, citation


@pytest.mark.parametrize("contract,fields", [
    (EvidenceItem, {"benchmark": BENCHMARK, "value": 90, "measured_by": "independent",
                    "date": "2026-10-21", "date_type": "observed", "source": CITED_URL,
                    "directness": "direct"}),
    (ComparisonEvidence, {"benchmark": BENCHMARK, "value": 90, "unit": "percent",
                          "record_id": "lab/cited#score", "source_ids": ["src-cited"]}),
])
def test_evidence_contract_preserves_citation_and_omits_it_when_uncited(
    contract, fields, citation_case,
):
    _, citation = citation_case
    assert "citation" not in contract.model_validate(fields).model_dump(mode="json")
    cited = contract.model_validate({**fields, "citation": citation}).model_dump(mode="json")
    assert cited["citation"] == citation
    assert "verification" not in cited


def test_named_comparison_preserves_cited_benchmark_provenance(citation_case):
    inputs, citation = citation_case
    body = collect_models(["lab/cited", "lab/plain"], load(inputs))
    cited = body["models"][0]["evidence"]
    assert len(cited) == 1
    assert cited[0]["value"] == 90
    assert cited[0]["citation"] == citation
    assert set(cited[0]["source_ids"]) == {source["source_id"] for source in citation["sources"]}
    by_id = {source["id"]: source for source in body["sources"]}
    assert all(by_id[source["source_id"]]["url"] == source["url"] for source in citation["sources"])
    assert "citation" not in body["models"][1]["evidence"][0]


def test_human_named_comparison_labels_cited_benchmark_score(monkeypatch, tmp_path, citation_case):
    inputs, citation = citation_case
    body = collect_models(["lab/cited", "lab/plain"], load(inputs))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(200, json=body),
    ))
    result = CliRunner().invoke(cli.app, ["compare", "lab/cited", "lab/plain"],
                                env={"MODELSPEC_API_KEY": "test_model437_key"})
    assert result.exit_code == 0, result.output
    row = next(line for line in result.stdout.splitlines()
               if line.startswith(f"| {BENCHMARK}"))
    cited, verified = row.split(" | ")[1:3]
    assert "90.0 percent" in cited
    assert "[Cited, not machine-verified]" in cited
    assert all(source["source_id"] in cited for source in citation["sources"])
    assert "70.0 percent" in verified
    assert "Cited, not machine-verified" not in verified
