"""Static pages share the named comparison's complete, sourced model facts."""

from dataclasses import replace
from datetime import date

import pytest

from decision.registry import facet
from decision.snapshot import SnapshotError, SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, evidence, model, offering
from tests.test_decide_worker import service, snapshot, snapshot_bytes  # noqa: F401


def test_collector_preserves_named_comparison_bytes_and_unknowns(service, snapshot):
    from decision.model_comparison import collect_models

    collected = collect_models(["lab/b", "lab/a"], snapshot)
    status, response = service.compare_models({"models": ["lab/b", "lab/a"]}, snapshot)

    assert status == 200
    assert service.serialise(collected) == service.serialise(response)
    assert [row["model"] for row in collected["models"]] == ["lab/b", "lab/a"]
    facts = {row["facet"]: row for row in collected["models"][0]["facts"]}
    assert facts["model.context_window"] == {
        "facet": "model.context_window",
        "state": "known",
        "value": 64000,
        "unit": "tokens",
        "record_id": "lab/b#model.context_window",
        "source_ids": ["src-lab-docs"],
    }
    assert facts["model.release_date"]["state"] == "unknown"
    assert facts["model.release_date"]["value"] is None
    assert collected["omitted"] == {"facts": 0, "offerings": 0, "evidence": 0}
    assert {row["id"]: row["url"] for row in collected["sources"]} == SOURCES


def test_collector_retains_evidence_beyond_the_worker_response_budget(service):
    from decision.model_comparison import collect_models

    ids = ["lab/a", "lab/b"]
    benchmarks = [f"bench_{number}" for number in range(100)]
    loaded = load_built_snapshot(build_snapshot(
        SnapshotInputs(
            models=[model(mid) for mid in ids],
            offerings=[offering(mid) for mid in ids],
            evidence=[
                evidence(mid, benchmark, index, eid=f"{mid}#{benchmark}")
                for mid in ids
                for index, benchmark in enumerate(benchmarks)
            ],
            sources=SOURCES,
            benchmark_domains={benchmark: [] for benchmark in benchmarks},
        ),
        gate=False,
        as_of=date(2026, 10, 13),
    ))

    complete = collect_models(ids, loaded)
    status, bounded = service.compare_models({"models": ids}, loaded)

    assert status == 200
    assert len(service.serialise(complete)) > service.MODEL_COMPARISON_BYTES
    assert len(service.serialise(bounded)) <= service.MODEL_COMPARISON_BYTES
    assert complete["omitted"] == {"facts": 0, "offerings": 0, "evidence": 0}
    assert bounded["omitted"]["evidence"] > 0
    for row in complete["models"]:
        assert {item["benchmark"] for item in row["evidence"]} == set(benchmarks)
        assert all(item["record_id"] and item["source_ids"] for item in row["evidence"])


def test_collector_uses_the_supplied_public_facet_registry(snapshot):
    from decision.model_comparison import collect_models

    def public_facet(name):
        definition = facet(name)
        if name == "model.context_window":
            return replace(definition, unit="public-context-unit")
        return definition

    collected = collect_models(["lab/a", "lab/b"], snapshot, facets=public_facet)

    for row in collected["models"]:
        facts = {item["facet"]: item for item in row["facts"]}
        assert facts["model.context_window"]["unit"] == "public-context-unit"


def test_collector_refuses_a_snapshot_without_retained_provenance(snapshot, monkeypatch):
    from decision.model_comparison import collect_models

    monkeypatch.setattr(snapshot, "explanation_rebuild_required", "missing explanation records")
    with pytest.raises(SnapshotError, match="missing explanation records"):
        collect_models(["lab/a", "lab/b"], snapshot)
