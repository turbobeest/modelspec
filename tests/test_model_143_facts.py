from __future__ import annotations

from pathlib import Path

import pytest

from decision import registry
from decision.model import value_hash
from decision.snapshot import (
    CompletenessError,
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_premier,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def repo_inputs() -> SnapshotInputs:
    return collect_repo(ROOT)


def test_every_premier_model_has_verified_guaranteed_facts(
    repo_inputs: SnapshotInputs,
) -> None:
    """MODEL-143 owns model completeness; MODEL-144 owns offering completeness."""
    model_only = SnapshotInputs(
        models=repo_inputs.models,
        evidence=repo_inputs.evidence,
        sources=repo_inputs.sources,
        benchmark_domains=repo_inputs.benchmark_domains,
        verifications=repo_inputs.verifications,
    )

    try:
        built = build_snapshot(
            model_only,
            registry=registry.default(),
            premier=load_premier(ROOT / "premier" / "slice-1.yaml"),
        )
    except CompletenessError as exc:
        model_gaps = [gap for gap in exc.gaps if gap.subject == gap.model]
        if model_gaps:
            pytest.fail("\n".join(str(gap) for gap in model_gaps))
        raise

    guaranteed = {
        facet.id
        for facet in registry.default().facets()
        if facet.subject == "model"
        and facet.tier == "guaranteed"
        and facet.computed_by is None
    }
    filed = set(built.content["lineup"]["facets"])
    assert guaranteed <= filed


def test_every_filed_premier_model_fact_has_registered_sources_and_verification(
    repo_inputs: SnapshotInputs,
) -> None:
    inputs = repo_inputs
    premier = set(load_premier(ROOT / "premier" / "slice-1.yaml"))
    latest = {
        (row["target"]["kind"], row["target"]["id"], row["target"]["value_hash"]): row
        for row in inputs.verifications
    }

    for model in inputs.models:
        if model["id"] not in premier:
            continue
        for fact in model["facts"]:
            assert fact["sources"], fact["id"]
            assert all(ref["source_id"] in inputs.sources for ref in fact["sources"]), fact["id"]
            if fact["state"] == "not_disclosed":
                checked = fact.get("checked_sources")
                assert checked, f"{fact['id']}: not_disclosed without checked sources"
                assert set(checked) <= set(inputs.sources), fact["id"]
                assert set(checked) <= {
                    ref["source_id"] for ref in fact["sources"]
                }, fact["id"]
            verification = latest.get(("fact", fact["id"], value_hash(fact["value"])))
            assert verification and verification["outcome"] == "verified", fact["id"]

        for evidence in model.get("benchmarks", {}).get("evidence", []):
            if not evidence.get("id"):
                continue
            assert evidence["sources"], evidence["id"]
            assert all(
                ref["source_id"] in inputs.sources for ref in evidence["sources"]
            ), evidence["id"]
            verification = latest.get(
                ("evidence", evidence["id"], value_hash(evidence["score"]))
            )
            assert verification and verification["outcome"] == "verified", evidence["id"]
