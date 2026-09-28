"""The learned capability estimate stage (MODEL-129)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import pytest

from decision.capability import (
    BenchmarkSpec,
    CapabilityObservation,
    backtest_capabilities,
    backtest_newest_capabilities,
    fit_capabilities,
)
from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.excluded import excluded_sources
from decision.registry import default as default_registry
from decision.snapshot import (
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
    load_premier,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 25)


def observation(
    model_id: str,
    benchmark_id: str,
    value: float,
    *,
    domain: str = "software_engineering",
    directness: str = "direct",
    measured_by: str = "independent_evaluator",
    age_days: int = 10,
) -> CapabilityObservation:
    return CapabilityObservation(
        model_id=model_id,
        benchmark_id=benchmark_id,
        value=value,
        unit="percent",
        measured_by=measured_by,
        date=AS_OF - timedelta(days=age_days),
        record_id=f"{model_id}#{benchmark_id}#{measured_by}",
        version="1.0",
        domains=((domain, directness),),
    )


def synthetic_observations() -> list[CapabilityObservation]:
    rows: list[CapabilityObservation] = []
    for index in range(10):
        model_id = f"lab/model-{index}"
        ability = index - 4.5 if index < 9 else 3.51
        rows.extend(
            [
                observation(model_id, "novel_repo_work", 50 + 8 * ability),
                observation(model_id, "novel_patch_work", 52 + 7 * ability),
                observation(
                    model_id,
                    "novel_preference_proxy",
                    50 + 4 * ability + (1 if index % 2 else -1),
                    directness="proxy",
                ),
            ]
        )
    return rows


SPECS = {
    name: BenchmarkSpec(random_baseline=25, sample_size=500, direction="higher_is_better")
    for name in ("novel_repo_work", "novel_patch_work", "novel_preference_proxy")
}


def test_fit_uses_registry_tags_without_a_benchmark_allowlist() -> None:
    fit = fit_capabilities(synthetic_observations(), SPECS, as_of=AS_OF)

    estimate = fit.estimate("lab/model-9", "software_engineering")
    assert estimate is not None
    assert estimate.low < estimate.value < estimate.high
    assert fit.estimate("lab/not-observed", "software_engineering") is None
    assert fit.estimate("lab/model-9", "medical") is None
    assert set(fit.items) == set(SPECS)
    assert all(item.discrimination > 0 for item in fit.items.values())


def test_two_model_benchmark_keeps_honest_wide_domain_estimates() -> None:
    """Sparse domains rank their measured frontier instead of becoming all-null."""
    rows = [
        observation("lab/first", "new_retrieval_measure", 60, domain="retrieval"),
        observation("lab/second", "new_retrieval_measure", 70, domain="retrieval"),
    ]

    fit = fit_capabilities(
        rows,
        {"new_retrieval_measure": BenchmarkSpec()},
        as_of=AS_OF,
    )

    first = fit.estimate("lab/first", "retrieval")
    second = fit.estimate("lab/second", "retrieval")
    assert first is not None and second is not None
    assert first.value < second.value
    assert first.low < first.value < first.high
    assert second.low < second.value < second.high


def test_fit_is_deterministic_and_saturation_reduces_frontier_information() -> None:
    first = fit_capabilities(synthetic_observations(), SPECS, as_of=AS_OF)
    second = fit_capabilities(reversed(synthetic_observations()), SPECS, as_of=AS_OF)

    assert first.to_payload() == second.to_payload()
    item = first.items["novel_repo_work"]
    assert item.information(4.0) < item.information(0.0)


def test_payload_ignores_cross_interpreter_float_noise() -> None:
    fit = fit_capabilities(synthetic_observations(), SPECS, as_of=AS_OF)
    item_id, item = next(iter(fit.items.items()))
    lower = replace(
        fit,
        items={**fit.items, item_id: replace(item, discrimination=0.453699382112)},
    )
    upper = replace(
        fit,
        items={**fit.items, item_id: replace(item, discrimination=0.453699382113)},
    )

    assert lower.to_payload()["items"][item_id] == upper.to_payload()["items"][item_id]


def test_fractional_random_baseline_is_not_divided_twice() -> None:
    fit = fit_capabilities(
        synthetic_observations(),
        {**SPECS, "novel_repo_work": BenchmarkSpec(random_baseline=0.25)},
        as_of=AS_OF,
    )

    assert fit.items["novel_repo_work"].random_baseline == 0.25


def test_source_offset_age_and_directness_are_part_of_the_fit() -> None:
    rows = synthetic_observations()
    for index in range(10):
        model_id = f"lab/model-{index}"
        rows.append(
            observation(
                model_id,
                "novel_repo_work",
                58 + 8 * (index - 4.5),
                measured_by="provider_self_report",
            )
        )
    for index in range(10):
        rows.append(observation(
            f"lab/model-{index}",
            "old_measurement",
            50 + 5 * (index - 4.5),
            age_days=730,
        ))
    specs = {**SPECS, "old_measurement": SPECS["novel_repo_work"]}

    fit = fit_capabilities(rows, specs, as_of=AS_OF)
    drivers = {row.benchmark_id: row for row in fit.explain(
        "lab/model-9", "software_engineering", limit=20
    )}

    assert fit.source_offsets["provider_self_report"] > 0
    assert fit.directness.proxy_loading < fit.directness.direct_loading
    assert drivers["old_measurement"].recency_weight < drivers["novel_repo_work"].recency_weight
    assert all(row.loading > 0 for row in drivers.values())


def proxy_only_observations() -> list[CapabilityObservation]:
    scores = {
        "medical": {"lab/model-0": 1509, "lab/model-1": 1488, "lab/model-2": 1496},
        "chat-0": {"lab/model-0": 1459, "lab/model-1": 1483, "lab/model-2": 1538},
        "chat-1": {"lab/model-0": 1471, "lab/model-1": 1467, "lab/model-2": 1490},
        "reasoning": {"lab/model-0": 1488, "lab/model-1": 1532, "lab/model-2": 1494},
    }
    rows = []
    for benchmark_id, by_model in scores.items():
        if benchmark_id == "medical":
            domains = (("chat_preference", "direct"), ("medical", "proxy"))
        elif benchmark_id.startswith("chat-"):
            domains = (("chat_preference", "direct"),)
        else:
            domains = (("reasoning", "direct"),)
        rows.extend(
            CapabilityObservation(
                model_id=model_id,
                benchmark_id=benchmark_id,
                value=value,
                unit="elo",
                measured_by="independent_evaluator",
                date=AS_OF,
                record_id=f"{model_id}#{benchmark_id}",
                version="1.0",
                domains=domains,
            )
            for model_id, value in by_model.items()
        )
    return rows


@pytest.mark.parametrize("increase", [1, 10, 50])
def test_raising_proxy_domain_evidence_cannot_lower_the_estimate_or_rank(
    increase: int,
) -> None:
    rows = proxy_only_observations()
    specs = {row.benchmark_id: BenchmarkSpec() for row in rows}
    before = fit_capabilities(rows, specs, as_of=AS_OF)
    target = "lab/model-0"
    raised = [
        replace(row, value=row.value + increase)
        if row.model_id == target and row.benchmark_id == "medical"
        else row
        for row in rows
    ]
    after = fit_capabilities(raised, specs, as_of=AS_OF)

    def rank(fit) -> int:
        ordered = sorted(
            (
                (fit.estimate(model_id, "medical").value, model_id)
                for model_id in {row.model_id for row in rows}
            ),
            reverse=True,
        )
        return next(index for index, (_, model_id) in enumerate(ordered) if model_id == target)

    assert after.estimate(target, "medical").value >= before.estimate(target, "medical").value
    assert rank(after) <= rank(before)


@pytest.fixture(scope="module")
def medical_case_snapshot():
    root = Path(__file__).resolve().parents[1]
    built = build_snapshot(
        collect_repo(root),
        registry=default_registry(),
        premier=load_premier(root / "premier" / "slice-1.yaml"),
        as_of=AS_OF,
        guard=excluded_sources(),
        gate=False,
    )
    return load_built_snapshot(built, source="capability test build")


def test_medical_proxy_regression_follows_its_only_domain_benchmark(
    medical_case_snapshot,
) -> None:
    opus = "anthropic/claude-opus-4-6"
    muse = "meta/muse-spark"
    opus_evidence = medical_case_snapshot.evidence(opus, "arena_sc_medicine")
    muse_evidence = medical_case_snapshot.evidence(muse, "arena_sc_medicine")

    assert max(row.value for row in opus_evidence) == pytest.approx(1519.76)
    assert max(row.value for row in muse_evidence) == pytest.approx(1503.55)
    assert medical_case_snapshot.capability_estimate(
        opus, "medical"
    ).value >= medical_case_snapshot.capability_estimate(muse, "medical").value


def test_proxy_only_domain_estimate_says_so_in_the_explanation(
    medical_case_snapshot,
) -> None:
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "medical"},
            "explain": "summary",
            "limit": 3,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, medical_case_snapshot, facets=default_registry().facet)

    assert decision.results
    assert all("proxy_evidence_only" in result.warnings for result in decision.results)
    assert all(
        contribution.formula == "proxy-only monotone domain evidence estimate"
        for result in decision.results
        for contribution in result.contributions
        if contribution.dimension == "medical"
    )


def test_holdout_prediction_beats_the_benchmark_mean() -> None:
    result = backtest_capabilities(
        synthetic_observations(), SPECS, as_of=AS_OF, seeds=(7, 19), holdout=0.2
    )

    assert result.cells > 0
    assert result.model_rmse < result.naive_rmse


def test_newest_score_holdout_beats_the_benchmark_mean() -> None:
    result = backtest_newest_capabilities(synthetic_observations(), SPECS, as_of=AS_OF)

    assert result.cells > 0
    assert result.model_rmse < result.naive_rmse


def snapshot() -> object:
    models = [
        model(f"lab/model-{index}", context=8_000 * (index + 1))
        for index in range(10)
    ]
    rows = []
    for row in synthetic_observations():
        stored = evidence(
            row.model_id,
            row.benchmark_id,
            row.value,
            eid=row.record_id,
            measured_by=row.measured_by,
            day=row.date.isoformat(),
        )
        rows.append(stored)
    built = build_snapshot(
        SnapshotInputs(
            models=models,
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={
                name: [("software_engineering", directness)]
                for name, directness in (
                    ("novel_repo_work", "direct"),
                    ("novel_patch_work", "direct"),
                    ("novel_preference_proxy", "proxy"),
                )
            },
            benchmark_metadata={
                name: {
                    "random_baseline": spec.random_baseline,
                    "sample_size": spec.sample_size,
                    "direction": spec.direction,
                }
                for name, spec in SPECS.items()
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    return load_built_snapshot(built, source="capability test build")


def direct_and_proxy_snapshot() -> object:
    rows = [
        row
        for row in synthetic_observations()
        if row.benchmark_id in {"novel_repo_work", "novel_preference_proxy"}
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model(f"lab/model-{index}") for index in range(10)],
            evidence=[
                evidence(
                    row.model_id,
                    row.benchmark_id,
                    row.value,
                    eid=row.record_id,
                    measured_by=row.measured_by,
                    day=row.date.isoformat(),
                )
                for row in rows
            ],
            sources=SOURCES,
            benchmark_domains={
                "novel_repo_work": [("software_engineering", "direct")],
                "novel_preference_proxy": [("software_engineering", "proxy")],
            },
            benchmark_metadata={
                name: {
                    "random_baseline": SPECS[name].random_baseline,
                    "sample_size": SPECS[name].sample_size,
                    "direction": SPECS[name].direction,
                }
                for name in ("novel_repo_work", "novel_preference_proxy")
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    return load_built_snapshot(built)


def test_excluding_the_only_direct_benchmark_refits_and_explains_the_change() -> None:
    index = direct_and_proxy_snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "exclude_benchmarks": ["novel_repo_work"],
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"},
            "explain": "summary",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert decision.benchmark_exclusions is not None
    assert decision.benchmark_exclusions.benchmarks == ["novel_repo_work"]
    impact = next(
        row
        for row in decision.benchmark_exclusions.estimate_changes
        if row.model == "lab/model-9" and row.domain == "software_engineering"
    )
    assert impact.before is not None and impact.after is not None
    assert impact.after.interval[1] - impact.after.interval[0] > (
        impact.before.interval[1] - impact.before.interval[0]
    )
    assert {driver.benchmark for driver in impact.removed_drivers} == {"novel_repo_work"}
    assert all(
        item.benchmark != "novel_repo_work"
        for result in decision.results
        for contribution in result.contributions
        for item in contribution.evidence
    )


def test_excluded_evidence_cannot_answer_a_benchmark_objective() -> None:
    index = direct_and_proxy_snapshot()

    def facets(facet_id: str):
        if facet_id in index.benchmark_ids():
            return replace(default_registry().facet("evidence.benchmark"), id=facet_id)
        return default_registry().facet(facet_id)

    spec = parse_spec(
        {
            "spec_version": 1,
            "exclude_benchmarks": ["novel_repo_work"],
            "optimize": {"max": "novel_repo_work"},
            "explain": "summary",
        },
        facets=facets,
    )

    decision = decide(spec, index, facets=facets)

    assert decision.status == "no_feasible"
    assert decision.results == []


def test_an_unknown_excluded_benchmark_names_the_bad_field() -> None:
    index = direct_and_proxy_snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "exclude_benchmarks": ["made_up_benchmark"],
            "optimize": {"max": "software_engineering"},
        },
        facets=default_registry().facet,
    )

    with pytest.raises(SpecError) as info:
        decide(spec, index, facets=default_registry().facet)

    [issue] = info.value.issues
    assert issue.path == "exclude_benchmarks[0]"
    assert issue.field == "made_up_benchmark"
    assert issue.reason == "unknown benchmark ID in this snapshot"


def test_an_empty_excluded_set_is_byte_identical_to_omission() -> None:
    index = direct_and_proxy_snapshot()
    base = {
        "spec_version": 1,
        "optimize": {"max": "software_engineering"},
        "explain": "summary",
    }
    omitted = parse_spec(base, facets=default_registry().facet)
    empty = parse_spec(base | {"exclude_benchmarks": []}, facets=default_registry().facet)

    assert decide(omitted, index, facets=default_registry().facet).model_dump_json() == (
        decide(empty, index, facets=default_registry().facet).model_dump_json()
    )


ARCHIVE_KEY = b"archive-visibility-test-key"


def archive_snapshot_bytes() -> bytes:
    rows = [
        row
        for row in synthetic_observations()
        if row.benchmark_id in {"novel_repo_work", "novel_patch_work"}
    ]
    retired = [f"lab/retired-{index}" for index in range(10)]
    retired_rows = [
        evidence(
            model_id,
            name,
            30 + 6 * index + (5 if name == "novel_repo_work" else -5) * (index % 3),
            eid=f"{model_id}#{name}",
            day=(AS_OF - timedelta(days=200)).isoformat(),
        )
        for index, model_id in enumerate(retired)
        for name in ("novel_repo_work", "novel_patch_work")
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model(f"lab/model-{index}") for index in range(10)]
            + [model(model_id, lifecycle="retired") for model_id in retired],
            evidence=[
                *[
                    evidence(
                        row.model_id,
                        row.benchmark_id,
                        row.value,
                        eid=row.record_id,
                        measured_by=row.measured_by,
                        day=row.date.isoformat(),
                    )
                    for row in rows
                ],
                *retired_rows,
            ],
            sources=SOURCES,
            benchmark_domains={
                name: [("software_engineering", "direct")]
                for name in ("novel_repo_work", "novel_patch_work")
            },
            benchmark_metadata={
                name: {
                    "random_baseline": SPECS[name].random_baseline,
                    "sample_size": SPECS[name].sample_size,
                    "direction": SPECS[name].direction,
                }
                for name in ("novel_repo_work", "novel_patch_work")
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    return built.to_bytes(key=ARCHIVE_KEY)


def test_exclusion_refit_does_not_depend_on_archive_visibility() -> None:
    from decision.capability import excluding_benchmarks

    data = archive_snapshot_bytes()
    without = load_snapshot_bytes(data, key=ARCHIVE_KEY)
    with_archive = load_snapshot_bytes(data, key=ARCHIVE_KEY, include_archive=True)
    assert without.snapshot_id == with_archive.snapshot_id

    first = excluding_benchmarks(without, ["novel_patch_work"])
    second = excluding_benchmarks(with_archive, ["novel_patch_work"])

    for index in range(10):
        one = first.capability_estimate(f"lab/model-{index}", "software_engineering")
        two = second.capability_estimate(f"lab/model-{index}", "software_engineering")
        assert one is not None and one == two


def singleton_snapshot() -> object:
    rows = [
        row for row in synthetic_observations() if row.benchmark_id == "novel_repo_work"
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model(f"lab/model-{index}") for index in range(10)],
            evidence=[
                *[
                    evidence(
                        row.model_id,
                        row.benchmark_id,
                        row.value,
                        eid=row.record_id,
                        measured_by=row.measured_by,
                        day=row.date.isoformat(),
                    )
                    for row in rows
                ],
                evidence(
                    "lab/model-9",
                    "singleton_bench",
                    80,
                    eid="lab/model-9#singleton_bench",
                    day=(AS_OF - timedelta(days=10)).isoformat(),
                ),
            ],
            sources=SOURCES,
            benchmark_domains={
                "novel_repo_work": [("software_engineering", "direct")],
                "singleton_bench": [("software_engineering", "direct")],
            },
            benchmark_metadata={
                name: {"random_baseline": 25, "sample_size": 500, "direction": "higher_is_better"}
                for name in ("novel_repo_work", "singleton_bench")
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    return load_built_snapshot(built)


def test_removed_drivers_name_only_evidence_that_was_a_baseline_driver() -> None:
    index = singleton_snapshot()
    baseline = {
        row.benchmark_id
        for row in index.capability_drivers("lab/model-9", "software_engineering")
    }
    assert baseline == {"novel_repo_work"}
    spec = parse_spec(
        {
            "spec_version": 1,
            "exclude_benchmarks": ["singleton_bench"],
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"},
            "explain": "summary",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert decision.benchmark_exclusions is not None
    assert all(
        change.removed_drivers == [] for change in decision.benchmark_exclusions.estimate_changes
    )


def test_snapshot_stores_estimates_and_domain_objectives_read_them() -> None:
    index = snapshot()
    stored = index.capability_estimate("lab/model-9", "software_engineering")
    assert stored is not None and stored.low < stored.value < stored.high
    # Parsing the learned lookup belongs to snapshot load, not every request.
    assert index.capability_estimate("lab/model-9", "software_engineering") is stored
    drivers = index.capability_drivers("lab/model-9", "software_engineering")
    assert index.capability_drivers("lab/model-9", "software_engineering") is drivers
    evidence_row = index.evidence_record("lab/model-9", drivers[0].record_id)
    assert evidence_row is not None and evidence_row.record_id == drivers[0].record_id

    spec = parse_spec(
        {
            "spec_version": 1,
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"},
            "explain": "full",
            "limit": 3,
        },
        facets=default_registry().facet,
    )
    decision = decide(spec, index, facets=default_registry().facet)

    assert decision.results[0].offering.model == "lab/model-9"
    assert decision.results[0].estimates[0].domain == "software_engineering"
    assert decision.results[0].p_best is not None
    assert decision.results[0].top3_stability is not None
    assert decision.results[0].contributions[0].evidence
    assert all(item.loading is not None for item in decision.results[0].contributions[0].evidence)


def test_html_with_estimates_says_they_carry_uncertainty_intervals() -> None:
    from decision.explain import render_html

    index = snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"},
            "explain": "full",
            "limit": 3,
        },
        facets=default_registry().facet,
    )
    decision = decide(spec, index, facets=default_registry().facet)
    assert any(result.estimates for result in decision.results)

    html = render_html(decision, index)
    assert "include uncertainty intervals" in html
    assert "are not available" not in html


def test_overlapping_intervals_are_reported_as_not_separable() -> None:
    index = snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "software_engineering"},
            "explain": "summary",
            "limit": 10,
        },
        facets=default_registry().facet,
    )
    decision = decide(spec, index, facets=default_registry().facet)

    assert any("not_separable" in result.warnings for result in decision.results)
    groups = [
        result
        for result in decision.results
        if "not_separable" in result.warnings
    ]
    assert len(groups) >= 2


def test_weight_one_answer_matches_the_single_capability_objective() -> None:
    index = snapshot()

    def answer_for(optimize):
        decision = decide(
            parse_spec(
                {
                    "spec_version": 1,
                    "optimize": optimize,
                    "explain": "none",
                    "limit": 10,
                },
                facets=default_registry().facet,
            ),
            index,
            facets=default_registry().facet,
        )
        not_separable = {
            result.offering.model
            for result in decision.results
            if "not_separable" in result.warnings
        }
        return decision.answer, not_separable

    single = answer_for({"max": "software_engineering"})
    weighted = answer_for({"weights": {"software_engineering": 1.0}})

    assert weighted == single


def test_weighted_capability_objective_reports_p_best() -> None:
    index = snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {
                "weights": {
                    "software_engineering": 0.75,
                    "model.context_window": 0.25,
                }
            },
            "explain": "none",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert all(result.p_best is not None for result in decision.results)
    by_model = {result.offering.model: result.p_best for result in decision.results}
    assert sum(value for value in by_model.values() if value is not None) == pytest.approx(1)


def test_exact_objective_answer_ignores_requested_capability_overlap() -> None:
    index = snapshot()
    spec = parse_spec(
        {
            "spec_version": 1,
            "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "model.context_window"},
            "explain": "summary",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert [result.contributions[0].value for result in decision.results[:2]] == pytest.approx(
        [1.0, 8 / 9]
    )
    assert decision.answer is not None
    assert decision.answer.kind == "separated"
    assert decision.answer.members == ["lab/model-9"]
    assert decision.answer.leader == "lab/model-9"


def test_tied_answer_compares_models_to_the_leader_without_following_chains() -> None:
    def sold(mid: str, provider: str, price: float, speed: float):
        oid = f"{provider}/{mid}/global/standard"
        return offering(mid, provider, facts=[
            fact("offering", oid, "offering.price.input", price, source="src-pricing"),
            fact("offering", oid, "offering.price.output", price, source="src-pricing"),
            fact("offering", oid, "offering.speed.throughput", speed),
        ])

    def catalogued(mid: str, openness: str):
        return model(mid, facts=[
            fact("model", mid, "model.weights_openness", openness),
            fact("model", mid, "model.context_window", 128_000),
            fact("model", mid, "model.input_modalities", ["text"]),
            fact("model", mid, "licence.user_cap", "unbounded"),
        ])

    rows = [
        evidence("lab/alpha", "quality", 100, interval=[95, 105]),
        evidence("lab/alpha", "aux-one", 70),
        evidence("lab/alpha", "aux-two", 80),
        evidence("lab/beta", "quality", 90, interval=[94, 96]),
        evidence("lab/gamma", "quality", 80, interval=[85, 94]),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[
                catalogued("lab/alpha", "closed_weights"),
                catalogued("lab/beta", "open_weights"),
                catalogued("lab/gamma", "closed_weights"),
            ],
            offerings=[
                sold("lab/alpha", "provider-a", 3, 100),
                sold("lab/alpha", "provider-b", 5, 120),
                sold("lab/beta", "provider-a", 1, 50),
                sold("lab/gamma", "provider-a", 0.5, 200),
            ],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={
                "quality": [("software_engineering", "direct")],
                "aux-one": [("software_engineering", "direct")],
                "aux-two": [("software_engineering", "direct")],
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "quality @independent"},
            "explain": "none",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert decision.answer is not None
    assert decision.answer.kind == "tied"
    assert decision.answer.members == ["lab/alpha", "lab/beta"]
    assert decision.answer.deterministic_order == ["lab/alpha", "lab/beta"]
    assert decision.answer.tie_breakers.model_dump() == {
        "cheapest": "lab/beta",
        "open_weights": "lab/beta",
        "most_independently_measured": "lab/alpha",
        "fastest": "lab/alpha",
    }
    assert "80%" in decision.answer.basis


def test_one_models_offerings_never_tie_with_each_other_in_the_answer() -> None:
    rows = [
        evidence("lab/alpha", "quality", 90, interval=[89, 91]),
        evidence("lab/beta", "quality", 50, interval=[49, 51]),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha"), model("lab/beta")],
            offerings=[
                offering("lab/alpha", "provider-a"),
                offering("lab/alpha", "provider-b"),
                offering("lab/beta", "provider-a"),
            ],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"quality": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "quality @independent"},
            "explain": "none",
            "limit": 10,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert decision.answer is not None
    assert decision.answer.kind == "separated"
    assert decision.answer.members == ["lab/alpha"]
    assert decision.answer.leader == "lab/alpha"
    assert decision.answer.deterministic_order == ["lab/alpha"]


def test_overlapping_raw_evidence_intervals_are_reported_as_not_separable() -> None:
    rows = [
        evidence("lab/alpha", "swe_bench_pro", 55.0, interval=[51.0, 59.0]),
        evidence("lab/beta", "swe_bench_pro", 54.0, interval=[50.0, 58.0]),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha"), model("lab/beta")],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_built_snapshot(built, source="capability test build")
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "swe_bench_pro @independent"},
            "limit": 2,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert [row.offering.model for row in decision.results] == ["lab/alpha", "lab/beta"]
    assert all("not_separable" in row.warnings for row in decision.results)


def test_one_models_offerings_do_not_make_its_evidence_not_separable() -> None:
    rows = [
        evidence("lab/alpha", "swe_bench_pro", 90.0, interval=[89.0, 91.0]),
        evidence("lab/beta", "swe_bench_pro", 50.0, interval=[49.0, 51.0]),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha"), model("lab/beta")],
            offerings=[
                offering("lab/alpha", "provider-a"),
                offering("lab/alpha", "provider-b"),
                offering("lab/beta", "provider-a"),
            ],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_built_snapshot(built, source="capability test build")
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "swe_bench_pro @independent"},
            "limit": 3,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert [row.offering.model for row in decision.results] == [
        "lab/alpha",
        "lab/alpha",
        "lab/beta",
    ]
    assert all("not_separable" not in row.warnings for row in decision.results)


def test_overlapping_raw_intervals_from_different_versions_are_not_compared() -> None:
    alpha = evidence("lab/alpha", "swe_bench_pro", 55.0, interval=[51.0, 59.0])
    beta = evidence("lab/beta", "swe_bench_pro", 54.0, interval=[50.0, 58.0])
    beta["benchmark_version"] = "2.0"
    rows = [alpha, beta]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha"), model("lab/beta")],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_built_snapshot(built, source="capability test build")
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "swe_bench_pro @independent"},
            "limit": 2,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert [row.offering.model for row in decision.results] == ["lab/alpha", "lab/beta"]
    assert all("not_separable" not in row.warnings for row in decision.results)


def test_overlapping_raw_interval_does_not_override_a_separating_weighted_objective() -> None:
    rows = [
        evidence("lab/alpha", "swe_bench_pro", 55.0, interval=[51.0, 59.0]),
        evidence("lab/beta", "swe_bench_pro", 54.0, interval=[50.0, 58.0]),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha", context=200_000), model("lab/beta", context=100_000)],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )
    index = load_built_snapshot(built, source="capability test build")
    spec = parse_spec(
        {
            "spec_version": 1,
            "optimize": {
                "weights": {
                    "swe_bench_pro": 0.1,
                    "model.context_window": 0.9,
                }
            },
            "limit": 2,
        },
        facets=default_registry().facet,
    )

    decision = decide(spec, index, facets=default_registry().facet)

    assert [row.offering.model for row in decision.results] == ["lab/alpha", "lab/beta"]
    assert all("not_separable" not in row.warnings for row in decision.results)


def test_identical_snapshot_inputs_remain_byte_identical_with_estimates() -> None:
    first = snapshot()
    second = snapshot()
    assert first.content_hash == second.content_hash


def test_capability_fit_uses_only_the_snapshot_lineup() -> None:
    rows = synthetic_observations()
    inputs = SnapshotInputs(
        models=[model(f"lab/model-{index}") for index in range(10)] + [model("lab/outlier")],
        evidence=[
            evidence(
                row.model_id,
                row.benchmark_id,
                row.value,
                eid=row.record_id,
                measured_by=row.measured_by,
                day=row.date.isoformat(),
            )
            for row in rows
        ],
        sources=SOURCES,
        benchmark_domains={name: [("software_engineering", "direct")] for name in SPECS},
        benchmark_metadata={
            name: {
                "random_baseline": spec.random_baseline,
                "sample_size": spec.sample_size,
                "direction": spec.direction,
            }
            for name, spec in SPECS.items()
        },
    )
    with_outlier = SnapshotInputs(
        **{
            **inputs.__dict__,
            "evidence": [
                *inputs.evidence,
                *[
                    evidence(
                        "lab/outlier",
                        name,
                        99,
                        eid=f"lab/outlier#{name}",
                        day=AS_OF.isoformat(),
                    )
                    for name in SPECS
                ],
            ],
        }
    )
    premier = [f"lab/model-{index}" for index in range(10)]
    first = build_snapshot(
        inputs, registry=default_registry(), premier=premier, as_of=AS_OF, gate=False
    )
    second = build_snapshot(
        with_outlier,
        registry=default_registry(),
        premier=premier,
        as_of=AS_OF,
        gate=False,
    )

    assert first.content["capability"] == second.content["capability"]


@pytest.mark.parametrize("field", ["p_best", "top3_stability"])
def test_estimate_probabilities_stay_in_the_contract_range(field: str) -> None:
    index = snapshot()
    spec = parse_spec(
        {"spec_version": 1, "optimize": {"max": "software_engineering"}},
        facets=default_registry().facet,
    )
    decision = decide(spec, index, facets=default_registry().facet)
    assert all(0 <= getattr(result, field) <= 1 for result in decision.results)
