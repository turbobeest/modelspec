"""MODEL-175 offering-speed data and snapshot guards."""

from __future__ import annotations

from pathlib import Path

import yaml

from decision import registry
from decision.model import load_offerings
from decision.snapshot import build_snapshot, collect_repo, load_premier
from decision.sources import load_sources


ROOT = Path(__file__).parents[1]
SPEED_FACETS = {
    "offering.speed.time_to_first_token",
    "offering.speed.throughput",
}


def _offerings():
    return [
        offering
        for path in sorted((ROOT / "offerings").glob("*/*/*.yaml"))
        for offering in load_offerings(path)
    ]


def test_every_slice1_offering_files_both_speed_facets() -> None:
    premier = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    }

    offerings = _offerings()
    assert offerings
    for offering in offerings:
        assert offering.model in premier
        speed = [fact for fact in offering.facts if fact.facet in SPEED_FACETS]
        assert {fact.facet for fact in speed} == SPEED_FACETS, offering.id
        assert len(speed) == len(SPEED_FACETS), offering.id


def test_unknown_speed_names_every_registered_source_that_was_checked() -> None:
    sources = load_sources(ROOT / "registry/sources.yaml")

    for offering in _offerings():
        for fact in offering.facts:
            if fact.facet not in SPEED_FACETS or fact.state != "unknown":
                continue
            assert fact.value is None, fact.id
            assert fact.checked_sources, fact.id
            assert set(fact.checked_sources) <= set(sources), fact.id


def test_any_published_speed_reading_uses_a_live_source() -> None:
    sources = load_sources(ROOT / "registry/sources.yaml")

    for offering in _offerings():
        for fact in offering.facts:
            if fact.facet not in SPEED_FACETS or fact.state != "known":
                continue
            assert fact.sources, fact.id
            for ref in fact.sources:
                assert sources[ref.source_id].volatility == "live", fact.id


def test_both_speed_facets_reach_the_decision_snapshot_schema() -> None:
    inputs = collect_repo(ROOT)
    snapshot = build_snapshot(
        inputs,
        registry=registry.default(),
        premier=load_premier(ROOT / "premier/slice-1.yaml"),
    )

    for facet in SPEED_FACETS:
        assert snapshot.content["facet_subjects"][facet] == "offering"


def test_speed_measurement_proposal_is_filed() -> None:
    proposal = ROOT / "docs/research/speed-measurement.md"
    text = proposal.read_text(encoding="utf-8")
    assert "## Published-source review" in text
    assert "## Proposed ModelSpec measurement" in text
    assert "## Cost" in text
