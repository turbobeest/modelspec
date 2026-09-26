"""The learned capability estimate stage (MODEL-129)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import pytest

from decision.capability import (
    BenchmarkSpec,
    CapabilityObservation,
    _round,
    backtest_capabilities,
    backtest_newest_capabilities,
    fit_capabilities,
)
from decision.contract import parse_spec
from decision.engine import decide
from decision.excluded import excluded_sources
from decision.registry import default as default_registry
from decision.snapshot import (
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_premier,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, evidence, model

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


def test_fit_is_deterministic_and_saturation_reduces_frontier_information() -> None:
    first = fit_capabilities(synthetic_observations(), SPECS, as_of=AS_OF)
    second = fit_capabilities(reversed(synthetic_observations()), SPECS, as_of=AS_OF)

    assert first.to_payload() == second.to_payload()
    item = first.items["novel_repo_work"]
    assert item.information(4.0) < item.information(0.0)


def test_payload_precision_absorbs_runtime_float_noise() -> None:
    assert _round(1470.799444444444) == _round(1470.799444444445)
    assert _round(0.443113861508) == _round(0.443113861509)


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
    return load_snapshot_bytes(built.to_bytes(key=None), key=None)


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
    models = [model(f"lab/model-{index}") for index in range(10)]
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
    return load_snapshot_bytes(built.to_bytes(key=None), key=None)


def test_snapshot_stores_estimates_and_domain_objectives_read_them() -> None:
    index = snapshot()
    stored = index.capability_estimate("lab/model-9", "software_engineering")
    assert stored is not None and stored.low < stored.value < stored.high

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
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)
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
