"""Probability bands and the named blend (MODEL-206)."""

from __future__ import annotations

import random
from datetime import date

import pytest

from decision import bands
from decision.bands import Distribution, p_at_least
from decision.contract import parse_spec
from decision.engine import decide
from decision.optimise import DimensionContribution, Normalisation, OptimisedResult
from decision.registry import default as default_registry
from decision.snapshot import (
    CapabilityEstimateValue,
    SnapshotInputs,
    build_snapshot,
    load_built_snapshot,
)
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 29)


def test_the_pairwise_probability_is_the_limit_of_comparing_posterior_draws() -> None:
    challenger, leader = Distribution(0.62, 0.11), Distribution(0.78, 0.16)
    rng = random.Random(206)
    draws = 200_000
    ahead = sum(rng.gauss(challenger.value, challenger.sd) >= rng.gauss(leader.value, leader.sd)
                for _ in range(draws))

    assert p_at_least(challenger, leader) == pytest.approx(ahead / draws, abs=0.004)
    assert p_at_least(challenger, leader) == 0.205


def test_exact_scores_compare_exactly() -> None:
    assert p_at_least(Distribution(0.5, 0), Distribution(0.5, 0)) == 1.0
    assert p_at_least(Distribution(0.4, 0), Distribution(0.5, 0)) == 0.0


def _row(model_id: str, score: float, *, width: float | None = None,
         sd: float = 0.0) -> OptimisedResult:
    estimate = None if width is None else CapabilityEstimateValue(
        score, score - width / 2, score + width / 2, sd)
    contribution = DimensionContribution(
        "software_engineering", score, score, 1.0, Normalisation(0.0, 1.0, "max"),
        estimate=estimate)
    return OptimisedResult(model_id, (contribution,), score, 0.0, (), (),
                           (score - width / 2, score + width / 2) if width else (score, score))


def test_a_thin_model_never_leads_or_joins_the_band_even_with_the_top_point_score() -> None:
    rows = [_row("lab/unproven", 0.9, width=4.0, sd=1.56),
            _row("lab/steady", 0.8, width=2.0, sd=0.78),
            _row("lab/close", 0.75, width=2.0, sd=0.78),
            _row("lab/far", -2.0, width=2.0, sd=0.78)]
    spread = {row.candidate_id: Distribution(row.score, row.contributions[0].estimate.sd)
              for row in rows}

    banded = bands.band(rows, spread, lambda cid: cid, {})

    assert banded.leader.candidate_id == "lab/steady"
    assert [row.candidate_id for row in banded.best] == ["lab/steady", "lab/close"]
    assert [row.candidate_id for row in banded.rest] == ["lab/far"]
    assert [row.candidate_id for row in banded.thin] == ["lab/unproven"]
    assert banded.p_beats["lab/unproven"] > bands.BAND_PROBABILITY


def test_the_width_threshold_is_strict() -> None:
    assert not bands.thin(_row("lab/edge", 0.0, width=bands.THIN_INTERVAL_WIDTH, sd=1.0))
    assert bands.thin(_row("lab/over", 0.0, width=bands.THIN_INTERVAL_WIDTH + 1e-9, sd=1.0))



@pytest.mark.parametrize("leader_value, challenger_value, joins", [
    (1.0, 0.3254, False),
    (0.6744897601960818, 0.0, False),
    (0.6744897401960817, 0.0, True),
])
def test_best_band_membership_precedes_probability_rounding(leader_value, challenger_value, joins):
    rows = [_row("lab/a", leader_value), _row("lab/b", challenger_value)]
    result = bands.band(rows, {
        "lab/a": Distribution(leader_value, 0.0),
        "lab/b": Distribution(challenger_value, 1.0),
    }, lambda cid: cid, {})
    assert result.p_beats["lab/b"] == 0.25
    assert [row.candidate_id for row in result.best] == (["lab/a", "lab/b"] if joins else ["lab/a"])
    assert [row.candidate_id for row in result.rest] == ([] if joins else ["lab/b"])


def test_best_band_includes_probability_exactly_at_threshold(monkeypatch):
    # Pin the numerical boundary independently of platform libm rounding.
    monkeypatch.setattr(bands, "erfc", lambda _: 0.5)
    rows = [_row("lab/a", 1.0), _row("lab/b", 0.0)]
    result = bands.band(rows, {"lab/a": Distribution(1.0, 0.0),
                               "lab/b": Distribution(0.0, 1.0)}, lambda cid: cid, {})
    assert result.p_beats["lab/b"] == 0.25
    assert [row.candidate_id for row in result.best] == ["lab/a", "lab/b"]
    assert result.rest == ()


@pytest.mark.parametrize("low, high, is_thin", [
    (-0.1, 2.7, False), (0.2, 3.0, False), (-3.0, -0.2, False),
    (-0.1, 2.699999999, False), (-0.1, 2.700000001, True),
    (0.2, 3.000000001, True), (-3.0, -0.199999999, True),
])
def test_band_and_blend_width_boundaries_ignore_interval_offset(low, high, is_thin):
    value = (low + high) / 2
    estimate = CapabilityEstimateValue(value, low, high, 1.0)
    part = DimensionContribution("software_engineering", value, value, 1.0,
                                 Normalisation(0.0, 1.0, "max"), estimate=estimate)
    row = OptimisedResult("lab/a", (part,), value, 0.0, ())
    assert bands.thin(row) is is_thin
    banded = bands.band([row], {"lab/a": Distribution(value, 1.0)}, lambda cid: cid, {})
    assert [item.candidate_id for item in banded.thin] == (["lab/a"] if is_thin else [])
    (term,) = bands.blend([row], lambda cid: cid, lambda _: {"lab/a": 1.0})
    assert term.thin == (["lab/a"] if is_thin else [])
    assert term.order == ([] if is_thin else ["lab/a"])

def test_when_every_model_is_thin_there_is_no_leader() -> None:
    rows = [_row("lab/a", 0.9, width=4.0, sd=1.5), _row("lab/b", 0.5, width=4.0, sd=1.5)]

    banded = bands.band(rows, {row.candidate_id: Distribution(row.score, 1.5) for row in rows},
                        lambda cid: cid, {})

    assert banded.leader is None and banded.best == () and banded.rest == ()
    assert [row.candidate_id for row in banded.thin] == ["lab/a", "lab/b"]


def test_the_best_band_is_ordered_by_p_best() -> None:
    rows = [_row("lab/a", 0.8, width=2.0, sd=0.5), _row("lab/b", 0.79, width=2.0, sd=0.5)]

    banded = bands.band(rows, {row.candidate_id: Distribution(row.score, 0.5) for row in rows},
                        lambda cid: cid, {"lab/a": 0.3, "lab/b": 0.6})

    assert [row.candidate_id for row in banded.best] == ["lab/b", "lab/a"]
    assert banded.leader.candidate_id == "lab/a"


# ── end to end: a coding agent on a budget ───────────────────────────────

# model, repo_work, patch_work, preference proxy, price per 1M tokens
LINEUP = [
    ("lab/frontier", 74.0, 70.0, None, 12.0),
    ("lab/solid", 68.0, 64.0, None, 4.0),
    ("lab/budget", 55.0, 50.0, None, 0.4),
    ("lab/older", 40.0, 38.0, 35.0, 1.2),
    ("lab/mystery", None, None, 85.0, 0.3),
]


@pytest.fixture(scope="module")
def budget_snapshot():
    models, offerings, rows = [], [], []
    for mid, repo, patch, proxy, price in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.context_window", 200_000),
            fact("model", mid, "model.weights_openness", "closed_weights"),
            fact("model", mid, "licence.user_cap", "unbounded"),
        ]))
        oid = f"sambanova/{mid}/global/standard"
        offerings.append(offering(mid, "sambanova", facts=[
            fact("offering", oid, "offering.price.input", price, source="src-pricing"),
            fact("offering", oid, "offering.price.output", 4 * price, source="src-pricing"),
        ]))
        for benchmark, score in (("repo_work", repo), ("patch_work", patch),
                                 ("preference_proxy", proxy)):
            if score is not None:
                rows.append(evidence(mid, benchmark, score, day="2026-09-01"))
    tags = {"repo_work": [("software_engineering", "direct")],
            "patch_work": [("software_engineering", "direct")],
            "preference_proxy": [("software_engineering", "proxy")]}
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains=tags,
                       benchmark_metadata={name: {"direction": "higher_is_better"}
                                           for name in tags}),
        registry=default_registry(), as_of=AS_OF)
    return load_built_snapshot(built, source="bands test build")


def _decide(snapshot, optimize):
    spec = parse_spec({"spec_version": 1, "where": ["model.class = text-generator"],
                       "optimize": optimize, "explain": "none", "limit": 20},
                      facets=default_registry().facet)
    return decide(spec, snapshot, facets=default_registry().facet)


def test_every_ranked_model_is_in_exactly_one_band_and_the_answer_is_the_best_band(
    budget_snapshot,
) -> None:
    decision = _decide(budget_snapshot, {"weights": {
        "software_engineering": 0.6, "-offering.cost_per_task": 0.4}})
    banded = decision.bands

    placed = [entry.model for band in (banded.best, banded.rest, banded.thin) for entry in band]
    assert sorted(placed) == sorted({row.offering.model for row in decision.results})
    assert sorted(decision.answer.members) == sorted(entry.model for entry in banded.best)
    assert [entry.model for entry in banded.thin] == ["lab/mystery"]
    assert "lab/mystery" not in decision.answer.members
    mystery = banded.thin[0]
    assert mystery.estimates[0].benchmarks == 1
    assert mystery.estimates[0].interval[1] - mystery.estimates[0].interval[0] \
        > bands.THIN_INTERVAL_WIDTH
    for entry in banded.best:
        if entry.model != banded.leader:
            assert entry.p_beats_leader >= bands.BAND_PROBABILITY
    for entry in banded.rest:
        assert entry.p_beats_leader < bands.BAND_PROBABILITY


def test_the_blend_names_the_mix_and_each_dimensions_own_leader(budget_snapshot) -> None:
    decision = _decide(budget_snapshot, {"weights": {
        "software_engineering": 0.6, "-offering.cost_per_task": 0.4}})
    coding, cost = decision.blend

    assert (coding.dimension, coding.share, coding.estimated) == ("software_engineering", 0.6, True)
    assert (cost.dimension, cost.share, cost.estimated) == ("-offering.cost_per_task", 0.4, False)
    assert coding.leaders == ["lab/frontier"]
    assert coding.runner_up == "lab/solid"
    assert 0 < coding.p_runner_up < 0.5
    assert coding.thin == ["lab/mystery"]
    assert "lab/mystery" not in coding.order
    assert cost.leaders == ["lab/mystery"]
    assert cost.order[0] == "lab/mystery"


def test_on_coding_alone_the_leader_and_its_confidence_are_stated(budget_snapshot) -> None:
    decision = _decide(budget_snapshot, {"max": "software_engineering"})
    [coding] = decision.blend

    assert decision.bands.leader == "lab/frontier" == coding.leaders[0]
    assert coding.share == 1.0
    assert coding.p_best is not None and coding.p_runner_up is not None


def test_a_new_snapshot_id_alone_does_not_reorder_the_best_band(budget_snapshot) -> None:
    """MODEL-440: p_best was a sample seeded from the snapshot id, so near-ties swapped."""
    original = budget_snapshot.snapshot_id
    seen = []
    try:
        for snapshot_id in (original, "snap_0000000000000001", "snap_00000000000000ff"):
            budget_snapshot.snapshot_id = snapshot_id
            decision = _decide(budget_snapshot, {"weights": {
                "software_engineering": 0.6, "-offering.cost_per_task": 0.4}})
            seen.append([(entry.model, entry.p_best) for entry in decision.bands.best])
    finally:
        budget_snapshot.snapshot_id = original

    assert seen == [[("lab/solid", 0.2976), ("lab/budget", 0.1184), ("lab/frontier", 0.0935)]] * 3


def test_a_lexicographic_objective_has_no_bands(budget_snapshot) -> None:
    decision = _decide(budget_snapshot, {"lexicographic": [
        {"max": "software_engineering"}, {"min": "offering.cost_per_task"}]})

    assert decision.bands is None and decision.blend == []
    assert "bands" not in decision.model_dump(mode="json")
    assert "blend" not in decision.model_dump(mode="json")


def test_pairwise_probability_at_band_threshold_joins_best():
    from math import sqrt

    from decision.contract import Objective
    from decision.optimise import EvidenceSelector, optimise
    from tests.test_decision_optimise import evidence_index, evidence_value

    half_width = bands.PUBLISHED_INTERVAL_Z / 0.6744897501960817
    snapshot = evidence_index({
        "lab/leader": [evidence_value(value=11, interval=(11, 11))],
        "lab/challenger": [evidence_value(
            value=10, interval=(10 - half_width, 10 + half_width),
        )],
    })
    rows = optimise(
        snapshot, snapshot.candidates(), Objective(max="quality"),
        evidence_selectors={"quality": EvidenceSelector("bench")},
    ).results
    distributions = {
        row.candidate_id: bands.Distribution(row.score, sqrt(bands.published_variance(row)))
        for row in rows
    }
    banded = bands.band(rows, distributions, lambda cid: cid, {})
    assert banded.p_beats["lab/challenger"] == 0.25
    assert [row.candidate_id for row in banded.best] == ["lab/leader", "lab/challenger"]
    assert banded.rest == ()


def test_cost_blend_uses_cheapest_offering_per_model():
    from tests.test_decision_optimise import run

    rows = run(
        {"a-cheap": {"cost": 1}, "a-dear": {"cost": 10}, "b": {"cost": 5}},
        {"min": "cost"},
    ).results
    (term,) = bands.blend(
        rows,
        lambda cid: "lab/a" if cid.startswith("a-") else "lab/b",
        lambda _distributions: {},
    )
    assert term.leaders == ["lab/a"]
    assert term.value == 1
    assert term.order == ["lab/a", "lab/b"]

