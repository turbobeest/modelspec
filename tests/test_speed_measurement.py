"""Measured speed through the snapshot, the vocabulary and the engine (MODEL-212).

The repository's own inputs are compiled with the dry run's fixture facts in
place of the unknown speed facts, as a live measurement would be promoted.
Fixture numbers never reach a published snapshot: the compiler refuses them
unless a test asks, and the repository holds none.
"""

from __future__ import annotations

import copy
import dataclasses
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from decision.contract import BestRef, Compare, parse_condition, parse_spec, render_condition
from decision.engine import decide
from decision.excluded import excluded_sources
from decision.filter import apply
from decision.model import MEASUREMENT_STALE_AFTER_DAYS, Fact
from decision.registry import default
from decision.resolve import resolve
from decision.snapshot import (
    SnapshotBuildError,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
    load_premier,
)
from decision.templates import load_catalogue
from decision.vocabulary import build_vocabulary
from scripts.speed.__main__ import dry_run
from scripts.speed.aggregate import SOURCE_ID
from scripts.speed.method import METHOD_URL, REPETITIONS_PER_SLOT, WARMUPS_PER_SLOT
from scripts.speed.plan import load_plan

ROOT = Path(__file__).resolve().parents[1]
OFFERINGS = len(load_plan().entries)
THROUGHPUT = "offering.speed.throughput"
FASTEST = "google-gemini-api/google/gemini-3-8-flash/global/standard"


@pytest.fixture(scope="module")
def dry(tmp_path_factory):
    plan = dataclasses.replace(load_plan(), name="baseline", repetitions=REPETITIONS_PER_SLOT,
                               warmups=WARMUPS_PER_SLOT)
    return dry_run(plan, 12, tmp_path_factory.mktemp("speed"))


@pytest.fixture(scope="module")
def window_end(dry):
    ends = [f["measurement"]["window"]["end"] for f in dry["measurement"]["facts"]]
    return date.fromisoformat(max(ends)[:10])


@pytest.fixture(scope="module")
def measured_inputs(dry):
    """The repository's inputs with the fixture speed facts promoted into them."""
    facts = {f["id"]: f for f in dry["measurement"]["facts"]}
    inputs = collect_repo(ROOT)
    offerings = []
    for offering in inputs.offerings:
        offering = dict(offering)
        offering["facts"] = [facts.get(f["id"], f) for f in offering["facts"]]
        offerings.append(offering)
    return dataclasses.replace(
        inputs,
        offerings=offerings,
        sources={**inputs.sources,
                 SOURCE_ID: "https://github.com/turbobeest/modelspec/tree/main/measurements"},
        verifications=[*inputs.verifications, *dry["verifications"]],
    )


def _build(inputs, as_of, **kwargs):
    return build_snapshot(inputs, registry=default(),
                          premier=load_premier(ROOT / "premier" / "slice-1.yaml"),
                          as_of=as_of, guard=excluded_sources(), gate=False, **kwargs)


@pytest.fixture(scope="module")
def snapshot(measured_inputs, window_end):
    return load_built_snapshot(
        _build(measured_inputs, window_end + timedelta(days=1), allow_fixture_measurements=True))


@pytest.fixture(scope="module")
def vocabulary(snapshot):
    return build_vocabulary(snapshot)


# ── the record ─────────────────────────────────────────────────────────────


def _fact(dry, facet=THROUGHPUT):
    return copy.deepcopy(next(f for f in dry["measurement"]["facts"]
                              if f["id"] == f"{FASTEST}#{facet}"))


def test_a_measured_fact_is_its_median(dry):
    fact = _fact(dry)
    Fact.model_validate(fact)
    fact["value"] += 1
    with pytest.raises(ValidationError, match="value is the median"):
        Fact.model_validate(fact)


def test_only_a_facet_that_admits_a_modelspec_measurement_can_carry_one(dry):
    fact = _fact(dry)
    fact["facet"] = "offering.price.input"
    fact["id"] = f"{FASTEST}#offering.price.input"
    with pytest.raises(ValidationError, match="does not admit a ModelSpec measurement"):
        Fact.model_validate(fact)


def test_a_median_outside_its_interval_is_refused(dry):
    fact = _fact(dry)
    fact["measurement"]["interval"] = [0.0, fact["value"] - 1]
    with pytest.raises(ValidationError, match="inside its interval"):
        Fact.model_validate(fact)


# ── the snapshot ───────────────────────────────────────────────────────────


def test_the_repository_holds_no_fixture_measurement():
    for path in (ROOT / "offerings").rglob("*.yaml"):
        for offering in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            for fact in offering.get("facts") or []:
                provenance = (fact.get("measurement") or {}).get("provenance")
                assert provenance != "fixture", f"{path}: {fact.get('facet')}"


def test_a_published_build_refuses_fixture_numbers(measured_inputs, window_end):
    with pytest.raises(SnapshotBuildError, match="fixture numbers never enter"):
        _build(measured_inputs, window_end + timedelta(days=1))


def test_an_unverified_fixture_number_is_refused_too(measured_inputs, dry, window_end):
    """The guard runs before verification: a fixture fact is an error, not a quarantine."""
    unverified = dataclasses.replace(measured_inputs, verifications=[
        v for v in measured_inputs.verifications if v not in dry["verifications"]])
    with pytest.raises(SnapshotBuildError, match="fixture numbers never enter"):
        _build(unverified, window_end + timedelta(days=1))


def test_a_stale_measurement_stops_deciding(measured_inputs, window_end):
    late = window_end + timedelta(days=MEASUREMENT_STALE_AFTER_DAYS + 1)
    stale = load_built_snapshot(_build(measured_inputs, late, allow_fixture_measurements=True))
    assert stale.fact(FASTEST, THROUGHPUT).state == "unknown"
    assert stale.excluded["stale_measurement"] == 2 * OFFERINGS


def test_the_snapshot_carries_each_measured_value_with_its_interval(snapshot, dry):
    fact = snapshot.fact(FASTEST, THROUGHPUT)
    block = _fact(dry)["measurement"]
    assert fact.state == "known" and fact.value == block["median"]
    assert fact.interval == tuple(block["interval"])
    assert fact.measurement["measured_by"] == "ModelSpec"
    assert fact.measurement["n"] == 24 and fact.measurement["workload"] == "short_chat"


# ── the vocabulary ─────────────────────────────────────────────────────────


def test_the_vocabulary_says_who_measured_speed_and_how(vocabulary):
    row = next(f for f in vocabulary["facets"] if f["id"] == THROUGHPUT)
    assert row["known"] == OFFERINGS
    assert {k: row["measurement"][k] for k in ("measured_by", "methods", "workloads",
                                                "measured", "min_n")} == {
        "measured_by": ["ModelSpec"],
        "methods": [{"id": "speed-v1", "url": METHOD_URL}],
        "workloads": ["short_chat"],
        "measured": OFFERINGS,
        "min_n": 24,
    }
    unmeasured = next(f for f in vocabulary["facets"] if f["id"] == "offering.price.input")
    assert "measurement" not in unmeasured


def test_every_generation_fastest_template_ranks_once_speed_is_measured(vocabulary):
    """speed-v1 streams generated tokens, so an embedder has no output speed to
    measure: retrieval's Fastest tier still waits, and says why."""
    fastest = {t["id"]: t for t in vocabulary["templates"] if t["tier"] == "fastest"}
    assert len(fastest) == 7
    assert [i for i, t in fastest.items() if not t["available"]] == ["retrieval-fastest"]
    assert "Output throughput" in fastest["retrieval-fastest"]["unavailable_reason"]


# ── the engine ─────────────────────────────────────────────────────────────


def _decide(snapshot, weights):
    spec = parse_spec({"spec_version": 1, "where": ["model.class = text-generator"],
                       "optimize": {"weights": weights}, "explain": "none"},
                      facets=default().facet)
    return decide(spec, snapshot, facets=default().facet)


def _id(ref) -> str:
    return f"{ref.provider}/{ref.model}/{ref.region}/{ref.tier}"


def test_a_speed_prefer_ranks_from_the_measured_medians(snapshot):
    decision = _decide(snapshot, {THROUGHPUT: 1})
    ranked = [_id(r.offering) for r in decision.results]
    speeds = [snapshot.fact(o, THROUGHPUT).value for o in ranked]
    assert ranked[0] == FASTEST
    assert speeds == sorted(speeds, reverse=True)
    assert len(ranked) == OFFERINGS


def test_a_measured_interval_widens_the_answer_band(snapshot):
    """Speed is never one number: its 95% interval reaches the score interval."""
    decision = _decide(snapshot, {THROUGHPUT: 1})
    leader = decision.bands.best[0]
    low, high = leader.score_interval
    assert low < high


def test_the_coding_fastest_template_ranks_from_measured_throughput(snapshot):
    template = next(t for t in load_catalogue()["templates"] if t["id"] == "coding-fastest")
    spec = parse_spec(template["spec"] | {"explain": "full"}, facets=default().facet)
    decision = decide(spec, snapshot, facets=default().facet)
    assert decision.results
    for result in decision.results:
        term = next(c for c in result.contributions if c.dimension == THROUGHPUT)
        assert term.raw_value == snapshot.fact(_id(result.offering), THROUGHPUT).value


def _floor(template, domain):
    """The template's hard ``<domain> >= best(m)`` condition, or ``None``."""
    for text in template["spec"]["where"]:
        cond = parse_condition(text)
        if (isinstance(cond, Compare) and cond.facet == domain and cond.op == ">="
                and isinstance(cond.value, BestRef) and cond.soft is None):
            return cond
    return None


def test_every_template_that_prefers_speed_floors_capability_relative_to_the_best():
    """Latency without quality ranks models backwards (the 2026-09 programme's
    finding). A weighting only bounds how far speed moves the order within the
    lineup's range; a floor is a condition, so speed cannot buy capability back.

    The margin is at most 1.0 on the capability scale. Between two well-measured
    models (80% intervals 1.4 to 2.0 wide) a gap of 1.0 leaves the leader ahead
    with probability about 0.82 to 0.90: a survivor may be measurably weaker, but
    not decisively. A margin of 0.5 sits inside the Best band (P about 0.26 to
    0.33), which the Best tier's `fastest` tie-breaker already answers.
    """
    speedy = [t for t in load_catalogue()["templates"]
              if any(k.lstrip("-").startswith("offering.speed.") for k in t["weights"])]
    assert len(speedy) == 7
    for template in speedy:
        for domain in template["needs"]["domains"]:
            floor = _floor(template, domain)
            assert floor is not None, (template["id"], domain)
            assert floor.value.best <= 1.0, template["id"]


def _without_floor(template, domain):
    floor = render_condition(_floor(template, domain))
    return parse_spec(template["spec"] | {"where": [w for w in template["spec"]["where"]
                                                    if w != floor]},
                      facets=default().facet)


def test_every_fastest_answer_is_within_1_of_the_strongest_eligible_model(snapshot, vocabulary):
    ranked = [t for t in vocabulary["templates"] if t["tier"] == "fastest" and t["available"]]
    assert len(ranked) == 6
    registry = default()
    for template in ranked:
        [domain] = template["needs"]["domains"]
        eligible = apply(resolve(_without_floor(template, domain), facets=registry.facet),
                         snapshot).feasible
        estimates = [e.value for cid in eligible
                     if (e := snapshot.capability_estimate(cid, domain)) is not None]
        bar = max(estimates) - 1.0
        spec = parse_spec(template["spec"], facets=registry.facet)
        decision = decide(spec, snapshot, facets=registry.facet)
        assert decision.results, template["id"]
        for result in decision.results:
            estimate = snapshot.capability_estimate(_id(result.offering), domain).value
            assert estimate >= bar, (template["id"], result.offering.model, estimate, bar)


def test_the_fastest_measured_offering_is_below_the_coding_floor(snapshot):
    """gemini-3-8-flash streams fastest of every measured offering, and Coding,
    fastest eliminates it by the floor rather than outweighing it. Its estimate
    and the bar move with the repository's evidence, so they are read, not pinned."""
    speeds = {cid: fact.value for cid in snapshot.candidates()
              if (fact := snapshot.fact(cid, THROUGHPUT)).state == "known"}
    assert max(speeds, key=speeds.get) == FASTEST
    template = next(t for t in load_catalogue()["templates"] if t["id"] == "coding-fastest")
    registry = default()
    domain = "software_engineering"
    eligible = apply(resolve(_without_floor(template, domain), facets=registry.facet),
                     snapshot).feasible
    strongest = max(e.value for cid in eligible
                    if (e := snapshot.capability_estimate(cid, domain)) is not None)
    result = apply(resolve(parse_spec(template["spec"], facets=registry.facet),
                           facets=registry.facet), snapshot)
    [out] = [row for row in result.eliminated if row.candidate == FASTEST]
    assert out.condition == "software_engineering >= best(1.0)"
    assert out.facet == domain
    assert out.threshold == strongest - 1.0
    assert out.value == snapshot.capability_estimate(FASTEST, domain).value
    assert out.value < out.threshold
    assert [step.condition for step in result.funnel][-1] == "software_engineering >= best(1.0)"
