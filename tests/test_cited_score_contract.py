"""Cited benchmark provenance survives each public evidence representation."""

import pytest

from decision.contract import ComparisonEvidence, EvidenceItem
from decision.model_comparison import collect_models
from tests.test_cited_scores import BENCHMARK, CITED_URL, load, score_inputs


CITATION = {
    "status": "cited",
    "sources": [{
        "source_id": "src-cited", "url": CITED_URL,
        "snapshot_ref": "sha256:" + "0" * 64, "retrieved_at": None,
    }],
}


@pytest.mark.parametrize("contract,fields", [
    (EvidenceItem, {"benchmark": BENCHMARK, "value": 90, "measured_by": "independent",
                    "date": "2026-10-21", "date_type": "observed", "source": CITED_URL,
                    "directness": "direct"}),
    (ComparisonEvidence, {"benchmark": BENCHMARK, "value": 90, "unit": "percent",
                          "record_id": "lab/cited#score", "source_ids": ["src-cited"]}),
])
def test_evidence_contract_preserves_citation_and_omits_it_when_uncited(contract, fields):
    assert "citation" not in contract.model_validate(fields).model_dump(mode="json")
    cited = contract.model_validate({**fields, "citation": CITATION}).model_dump(mode="json")
    assert cited["citation"] == CITATION
    assert "verification" not in cited


def test_named_comparison_preserves_cited_benchmark_provenance():
    body = collect_models(["lab/cited", "lab/plain"], load(score_inputs()))
    cited = body["models"][0]["evidence"]
    assert len(cited) == 1
    assert cited[0]["value"] == 90
    assert cited[0]["citation"] == CITATION
    assert "citation" not in body["models"][1]["evidence"][0]
