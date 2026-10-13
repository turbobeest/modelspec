"""MODEL-348: sourced architecture and hardware estimates, with no default weight."""

from __future__ import annotations

import copy
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
import yaml

from api.ranking.engine import ModelData, RankingEngine, USE_CASE_PROFILES
from decision.contract import (
    BOUNDED_VERSION, Decision, FactInterval, ShownFact, SpecError, parse_spec, render_json_schema,
)
from decision.engine import decide
from decision.hardware import ARCHITECTURE_FACETS, HARDWARE_FACETS
from decision.registry import default as registry
from decision.snapshot import (
    SnapshotBuildError, SnapshotInputs, build_snapshot, collect_repo, load_built_snapshot,
    load_snapshot_bytes,
)
from decision.templates import load_templates
from decision.vocabulary import build_vocabulary
from tests.snapshot_records import SOURCES, fact, model, offering

ROOT = Path(__file__).resolve().parents[1]
SPARK = "nvidia_dgx_spark"
SOURCES_WITH_HARDWARE = {
    **SOURCES,
    "spark-spec": "https://www.nvidia.com/en-us/products/workstations/dgx-spark/",
    "spark-manual": "https://docs.nvidia.com/dgx/dgx-spark/hardware.html",
}


def spark():
    return yaml.safe_load((ROOT / "hardware" / f"{SPARK}.yaml").read_text())


def generator(mid, architecture="dense-transformer", total=31_000_000_000,
              active=31_000_000_000, fits=(SPARK,)):
    values = {
        "model.class": "text-generator", "model.context_window": 200_000,
        "model.weights_openness": "open_weights", "model.fits_hardware": list(fits),
        "model.architecture": architecture, "model.parameters_total": total,
        "model.parameters_active": active,
    }
    return model(mid, facts=[fact("model", mid, facet, value)
                             for facet, value in values.items() if value is not None])


def fixture_snapshot(*, models=None, hardware=None, offerings=(), sources=SOURCES_WITH_HARDWARE):
    built = build_snapshot(SnapshotInputs(
        models=models if models is not None else [
            generator("lab/dense"),
            generator("lab/gemma", "MoE", 25_800_000_000, 3_800_000_000),
            generator("lab/deepseek", "MoE", 671_000_000_000, 37_000_000_000,
                      fits=("apple_m3_ultra",)),
        ],
        hardware=[spark()] if hardware is None else hardware,
        offerings=offerings,
        sources=sources,
    ), gate=False, as_of=date(2026, 10, 10))
    return load_built_snapshot(built, include_archive=False, source="architecture fixture")


def spec(**updates):
    return parse_spec({
        "spec_version": 1, "where": ["model.class = text-generator"],
        "optimize": {"max": "model.context_window"}, "explain": "full", **updates,
    }, facets=registry().facet)


def answer(index, **updates):
    return decide(spec(**updates), index, facets=registry().facet)


def facts(decision, mid):
    return {row.facet: row for top in decision.top if top.offering.model == mid for row in top.facts}


def estimates(decision, mid):
    return {row.facet: row for top in decision.top if top.offering.model == mid
            for row in top.hardware_estimates}


def test_spark_memory_uses_total_and_decode_uses_active_at_the_same_quant():
    decision = answer(fixture_snapshot(), access="own_hardware", estate={"devices": [SPARK]})
    assert decision.contract_version == "2.16"
    assert decision.status == "answered"
    assert set(decision.with_estate.answer.members) == {"lab/dense", "lab/gemma"}
    for mid, weights, speed, interval, total, active in (
        ("lab/dense", 62.0, 3.1, {"low": 1.5, "high": 3.7},
         31_000_000_000, 31_000_000_000),
        ("lab/gemma", 51.6, 25.1, {"low": 12.6, "high": 30.5},
         25_800_000_000, 3_800_000_000),
    ):
        shown = facts(decision, mid)
        assert shown["model.parameters_total"].value == total
        assert shown["model.parameters_active"].value == active
        assert shown["model.architecture"].record_id == f"{mid}#model.architecture"
        assert shown["model.architecture"].source_ids == ["src-lab-docs"]
        shown = estimates(decision, mid)
        assert shown["hardware.weights_gb"].value == weights
        decode = shown["hardware.decode_tps_estimate"]
        assert decode.value == speed
        assert decode.interval.model_dump() == interval
        assert decode.quantisation == "bf16"
        assert "memory.bandwidth_gb_s 273" in decode.formula
        assert "parameters_active" in decode.formula
        assert shown["hardware.weights_gb"].records == [
            f"{mid}#model.parameters_total", f"{mid}#model.weights_openness",
            "hardware:nvidia_dgx_spark#memory",
        ]
        assert decode.records == [
            f"{mid}#model.parameters_total", f"{mid}#model.weights_openness",
            "hardware:nvidia_dgx_spark#memory", f"{mid}#model.parameters_active",
        ]
        for facet in HARDWARE_FACETS:
            row = shown[facet]
            assert row.device == SPARK
            assert "record_id" not in row.model_dump()
            assert "unknown_reason" not in row.model_dump()
            assert row.source_ids == ["spark-manual", "spark-spec", "src-lab-docs"]
            assert row.formula.startswith("Estimate for nvidia_dgx_spark")
        assert "KV cache is inside the allowance" in shown["hardware.weights_gb"].formula
        assert "device capacity 128 GB, largest listed memory configuration" in decode.formula
        assert "usable memory 128 × (1 - 0.25) = 96 GB" in decode.formula
    huge = estimates(decision, "lab/deepseek")
    assert huge["hardware.weights_gb"].value is None
    assert "even q4 needs 335.5 GB" in huge["hardware.weights_gb"].unknown_reason
    assert "above 96 GB usable" in huge["hardware.weights_gb"].unknown_reason
    assert huge["hardware.decode_tps_estimate"].value is None
    assert "interval" not in huge["hardware.decode_tps_estimate"].model_dump()
    assert set(HARDWARE_FACETS) <= set(decision.reading.estimates)
    assert "Do not present estimates as measurements." in decision.reading.do_not_claim
    assert "Do not claim fit for a specific quantization or context workload." in decision.reading.do_not_claim
    assert "Quantisation is assumed; context fit and decode speed are unmeasured." in decision.reading.do_not_claim
    cited = {source.id: str(source.url) for source in decision.sources}
    assert cited["spark-spec"] == SOURCES_WITH_HARDWARE["spark-spec"]
    assert cited["spark-manual"] == SOURCES_WITH_HARDWARE["spark-manual"]
    assert Decision.model_validate_json(decision.model_dump_json()) == decision


def test_spark_chooses_fp8_when_bf16_does_not_fit():
    index = fixture_snapshot(models=[generator("lab/large", "MoE", 80_000_000_000, 5_000_000_000)])
    shown = estimates(answer(index, estate={"devices": [SPARK]}), "lab/large")
    assert shown["hardware.weights_gb"].value == 80.0
    decode = shown["hardware.decode_tps_estimate"]
    assert decode.quantisation == "fp8"
    assert decode.value == 38.2
    assert decode.interval.model_dump() == {"low": 19.1, "high": 46.4}


@pytest.mark.parametrize("architecture, unknown_facets", [
    ("dense-transformer", ["model.parameters_active"]),
    ("MoE", ["model.experts_per_token", "model.experts_total", "model.parameters_active"]),
    (None, ["model.architecture", "model.experts_per_token", "model.experts_total",
            "model.parameters_active"]),
])
def test_missing_active_never_falls_back_to_total_even_for_dense(architecture, unknown_facets):
    index = fixture_snapshot(models=[generator("lab/a", architecture, active=None)])
    decision = answer(index, access="own_hardware", estate={"devices": [SPARK]})
    shown = estimates(decision, "lab/a")
    assert shown["hardware.weights_gb"].value == 62.0
    assert "model.parameters_active" not in facts(decision, "lab/a")
    assert decision.top[0].unknown_facets == unknown_facets
    decode = shown["hardware.decode_tps_estimate"]
    assert decode.value is None
    assert decode.unknown_reason == (
        "verified positive parameters_active is missing; no fallback to parameters_total")
    assert "interval" not in decode.model_dump()


@pytest.mark.parametrize("missing", ["total", "bandwidth", "device", "pool", "openness"])
def test_unknown_hardware_inputs_stay_unknown_with_a_reason(missing):
    device = spark()
    models = [generator("lab/a", total=None if missing == "total" else 31_000_000_000)]
    if missing == "openness":
        models[0]["facts"] = [row for row in models[0]["facts"]
                               if row["facet"] != "model.weights_openness"]
    if missing == "bandwidth":
        device["memory"].pop("bandwidth_gb_s")
    if missing == "pool":
        device.update(single_device_fit=False, single_device_fit_reason="aggregate memory is not one pool")
    index = fixture_snapshot(models=models, hardware=[] if missing == "device" else [device],
                             offerings=[offering("lab/a")] if missing == "openness" else ())
    shown = estimates(answer(index, estate={"devices": [SPARK]}), "lab/a")
    decode = shown["hardware.decode_tps_estimate"]
    assert decode.value is None
    assert "unknown" in decode.formula
    assert "interval" not in decode.model_dump()
    if missing == "bandwidth":
        assert shown["hardware.weights_gb"].value == 62.0
        assert "memory.bandwidth_gb_s is missing" in decode.unknown_reason
    elif missing == "device":
        assert decode.unknown_reason == "snapshot has no device memory specifications for this SKU"
    else:
        assert shown["hardware.weights_gb"].value is None


@pytest.mark.parametrize("updates", [
    {"access": "own_hardware"}, {"estate": {"devices": [SPARK]}},
    {"where": [{"facet": "model.fits_hardware", "in": [SPARK]}]},
    {"where": ["model.architecture != MoE"]},
    {"where": ["model.parameters_total <= 50000000000"]},
    {"optimize": {"min": "model.parameters_active"}},
])
def test_architecture_facts_are_conditional_and_sourced(updates):
    decision = answer(fixture_snapshot(), **updates)
    for top in decision.top:
        shown = {row.facet: row for row in top.facts}
        for facet in ARCHITECTURE_FACETS[:3]:
            assert shown[facet].record_id == f"{top.offering.model}#{facet}"
            assert shown[facet].source_ids == ["src-lab-docs"]


def test_unrequested_architecture_and_estimates_do_not_expand_normal_answers():
    decision = answer(fixture_snapshot())
    assert all(not set(ARCHITECTURE_FACETS + HARDWARE_FACETS) & {f.facet for f in top.facts}
               for top in decision.top)
    unregistered = set(ARCHITECTURE_FACETS) - {facet.id for facet in registry().facets()}
    assert not unregistered & {
        f.facet for top in answer(fixture_snapshot(), access="own_hardware").top for f in top.facts
    }


@pytest.mark.parametrize("architecture", ["MoE", "dense-transformer"])
def test_expert_facts_are_shown_when_the_registry_defines_them(monkeypatch, architecture):
    registered = registry()
    original = registered.facet
    experts = {
        facet: replace(original("model.parameters_total"), id=facet)
        for facet in ("model.experts_total", "model.experts_per_token")
    }
    monkeypatch.setattr(registered, "facet", lambda name: experts[name] if name in experts else original(name))
    row = generator("lab/moe", architecture, 25_800_000_000, 3_800_000_000)
    row["facts"].extend([fact("model", "lab/moe", "model.experts_total", 64),
                         fact("model", "lab/moe", "model.experts_per_token", 8)])
    decision = answer(fixture_snapshot(models=[row]), access="own_hardware")
    shown = facts(decision, "lab/moe")
    if architecture == "dense-transformer":
        assert "model.experts_total" not in shown
        assert "model.experts_per_token" not in shown
        assert decision.top[0].unknown_facets == []
        return
    assert shown["model.experts_total"].value == 64
    assert shown["model.experts_per_token"].value == 8
    assert shown["model.experts_total"].record_id == "lab/moe#model.experts_total"
    assert shown["model.experts_per_token"].source_ids == ["src-lab-docs"]


@pytest.mark.parametrize("condition, expected", [
    ("model.architecture = MoE", {"lab/moe"}),
    ("model.architecture != MoE", {"lab/dense"}),
    ({"facet": "model.architecture", "in": ["MoE", "SSM"]}, {"lab/moe"}),
    ("model.parameters_active <= 4000000000", {"lab/moe"}),
])
def test_must_filters_preserve_unknown_as_may_qualify(condition, expected):
    index = fixture_snapshot(models=[generator("lab/dense"),
        generator("lab/moe", "MoE", 25_800_000_000, 3_800_000_000),
        generator("lab/unknown", None, active=None)])
    decision = answer(index, where=[condition])
    assert {row.model for row in decision.results} == expected
    assert {row.model for row in decision.may_qualify} == {"lab/unknown"}
    assert decision.may_qualify[0].unknown == [
        "model.parameters_active" if isinstance(condition, str) and "parameters_active" in condition
        else "model.architecture"]


@pytest.mark.parametrize("condition", [
    {"facet": "model.architecture", "op": "=", "value": "MoE", "soft": {"penalty": 0.1}},
    {"facet": "model.architecture", "op": "!=", "value": "dense-transformer", "soft": {"penalty": 0.1}},
    {"facet": "model.architecture", "in": ["MoE", "SSM"], "soft": {"penalty": 0.1}},
    {"facet": "model.parameters_active", "op": "<=", "value": 4_000_000_000,
     "soft": {"penalty": 0.1}},
])
def test_explicit_prefer_can_choose_architecture_or_active_params(condition):
    index = fixture_snapshot(models=[generator("lab/a"),
        generator("lab/z", "MoE", 31_000_000_000, 3_800_000_000)])
    unchanged = answer(index, estate={"devices": [SPARK]})
    assert [row.model for row in unchanged.results] == ["lab/a", "lab/z"]
    assert [row.soft_penalty for row in unchanged.results] == [0.0, 0.0]
    assert [(c.dimension, c.weight, c.value) for c in unchanged.results[0].contributions] == [
        ("model.context_window", 1.0, 1.0)]
    assert [(c.dimension, c.weight, c.value) for c in unchanged.results[1].contributions] == [
        ("model.context_window", 1.0, 1.0)]
    changed = answer(index, where=[condition])
    assert [row.model for row in changed.results] == ["lab/z", "lab/a"]
    assert [row.soft_penalty for row in changed.results] == [0.0, 0.1]


def test_value_preference_works_through_the_normal_objective_path():
    index = fixture_snapshot(models=[generator("lab/a"), generator("lab/z", "MoE")])
    decision = answer(index, optimize={"weights": {
        "model.architecture": {"prefer": "MoE", "weight": 1}}})
    assert [row.model for row in decision.results] == ["lab/z", "lab/a"]


def test_unknown_preferences_remain_unknown_in_the_normal_preference_path():
    index = fixture_snapshot(models=[generator("lab/dense"), generator("lab/moe", "MoE"),
                                     generator("lab/unknown", None)])
    traces = []
    decide(spec(where=[{"facet": "model.architecture", "op": "=", "value": "MoE",
                        "soft": {"penalty": 0.1}}]), index, facets=registry().facet,
           _filter_trace=traces.append)
    assert traces[0].penalties[0].failing == ("lab/dense",)
    assert traces[0].penalties[0].unknown == ("lab/unknown",)
    decision = answer(index, optimize={"weights": {
        "model.architecture": {"prefer": "MoE", "weight": 1}}})
    unknown = next(row for row in decision.results if row.model == "lab/unknown")
    assert unknown.contributions[0].preference_status == "unknown"
    assert unknown.contributions[0].raw_value is None
    assert unknown.warnings == ["unknown_preference_value"]


@pytest.mark.parametrize("architecture, active", [
    ("MoE", 31_000_000_000), ("dense-transformer", 3_800_000_000),
])
def test_architecture_alone_and_active_params_alone_cannot_order_a_default_objective(architecture, active):
    index = fixture_snapshot(models=[generator("lab/a"),
                                     generator("lab/z", architecture, 31_000_000_000, active)])
    decision = answer(index, access="own_hardware", estate={"devices": [SPARK]})
    assert decision.answer.kind == "tied"
    assert decision.answer.members == ["lab/a", "lab/z"]
    assert [row.model for row in decision.results] == ["lab/a", "lab/z"]
    assert [row.soft_penalty for row in decision.results] == [0.0, 0.0]
    assert [[(c.dimension, c.value, c.weight) for c in row.contributions] for row in decision.results] == [
        [("model.context_window", 1.0, 1.0)], [("model.context_window", 1.0, 1.0)],
    ]


def test_every_default_rank_profile_and_template_excludes_architecture_and_estimates():
    engine = RankingEngine(None)
    for profile in USE_CASE_PROFILES.values():
        scores = {bench: 50.0 for bench in profile.get("benchmark_weights", {})}
        dense = ModelData(model_id="lab/a", display_name="A", model_type="llm-chat",
                          total_parameters=31_000_000_000, active_parameters=31_000_000_000,
                          benchmark_scores=scores, tags={"dense-transformer"},
                          hardware_fits={SPARK: {"hardware.decode_tps_estimate": 3.1}})
        moe = ModelData(model_id="lab/z", display_name="Z", model_type="llm-chat",
                        total_parameters=31_000_000_000, active_parameters=3_800_000_000,
                        benchmark_scores=scores, tags={"MoE"},
                        hardware_fits={SPARK: {"hardware.decode_tps_estimate": 25.1}})
        a, z = engine._score(dense, profile), engine._score(moe, profile)
        assert a.score == z.score
        assert a.score_lower_bound == z.score_lower_bound
        assert a.score_upper_bound == z.score_upper_bound
        assert a.speed_score == z.speed_score == 0.0
        assert not set(ARCHITECTURE_FACETS + HARDWARE_FACETS) & set(profile.get("benchmark_weights", {}))
    for template in load_templates():
        assert not set(ARCHITECTURE_FACETS + HARDWARE_FACETS) & {
            key.removeprefix("-") for key in template["weights"]}


def test_multi_device_facts_are_separate_and_have_no_implicit_scalar():
    other = copy.deepcopy(spark())
    other.update(id="nvidia_rtx_4090")
    other["memory"].update(capacity_gb=24, bandwidth_gb_s=1008)
    index = fixture_snapshot(models=[generator("lab/a", "MoE", 25_800_000_000, 3_800_000_000)],
                             hardware=[spark(), other])
    decision = answer(index, estate={"devices": [SPARK, "nvidia_rtx_4090"]})
    rows = [f for f in decision.top[0].hardware_estimates if f.facet == "hardware.weights_gb"]
    assert [(row.device, row.value) for row in rows] == [(SPARK, 51.6), ("nvidia_rtx_4090", 16.1)]
    assert rows[1].quantisation == "q5"
    assert "hardware:nvidia_rtx_4090#memory" in rows[1].records
    with pytest.raises(SpecError, match="exactly one device in estate.devices"):
        answer(index, estate={"devices": [SPARK, "nvidia_rtx_4090"]},
               where=["hardware.weights_gb <= 100"])


def test_single_device_estimate_is_available_to_explicit_conditions():
    index = fixture_snapshot()
    decision = answer(index, estate={"devices": [SPARK]}, where=["hardware.decode_tps_estimate >= 20"])
    assert [row.model for row in decision.results] == ["lab/gemma"]
    assert [row.model for row in decision.may_qualify] == ["lab/deepseek"]


def test_vocabulary_advertises_architecture_and_active_parameter_conditions():
    vocabulary = build_vocabulary(fixture_snapshot())
    facets = {row["id"]: row for row in vocabulary["facets"]}
    architecture = facets["model.architecture"]
    assert {"=", "!=", "in"} <= set(architecture["operators"])
    assert "MoE" in architecture["allowed_values"]
    assert architecture["known"] == 3
    assert architecture["preference"]["kind"] == "value"
    assert "<=" in facets["model.parameters_active"]["operators"]
    assert facets["model.parameters_active"]["known"] == 3
    for facet in HARDWARE_FACETS:
        assert facets[facet]["computed_by"] == "MODEL-348"
        assert registry().facet(facet).permitted_source_kinds == ("modelspec_estimate",)


def test_hardware_snapshot_round_trip_and_repository_collection(tmp_path):
    device = spark()
    built = build_snapshot(SnapshotInputs(hardware=[device], sources=SOURCES_WITH_HARDWARE), gate=False)
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None, public_keys={})
    assert index.hardware_device(SPARK) == {
        "memory_capacity_gb": 128.0, "memory_bandwidth_gb_s": 273.0,
        "single_device_fit": True, "refusal_reason": None,
        "record_id": "hardware:nvidia_dgx_spark#memory",
        "source_ids": ["spark-manual", "spark-spec"],
    }
    assert index.record("hardware:nvidia_dgx_spark#memory")["memory"] == device["memory"]
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware" / f"{SPARK}.yaml").write_text(yaml.safe_dump(device))
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "sources": [{"id": sid, "url": url, "fetch": "conditional_http",
                     "normaliser": "html-default", "cited_regions": [
                         {"id": "page", "locator": {"kind": "page", "value": ""}}]}
                    for sid, url in SOURCES_WITH_HARDWARE.items()],
    }))
    collected = collect_repo(tmp_path)
    assert collected.hardware == [device]
    rebuilt = load_built_snapshot(build_snapshot(collected, gate=False),
                                  include_archive=False, source="repository hardware")
    assert rebuilt.hardware_device(SPARK)["memory_bandwidth_gb_s"] == 273.0
    assert str(rebuilt.source_url(rebuilt.hardware_device(SPARK)["source_ids"][0])).startswith("https://")


@pytest.mark.parametrize("field, value", [("capacity_gb", 0), ("capacity_gb", True),
                                          ("bandwidth_gb_s", float("inf"))])
def test_hardware_snapshot_rejects_invalid_memory(field, value):
    device = spark()
    device["memory"][field] = value
    with pytest.raises(SnapshotBuildError, match="positive and finite"):
        build_snapshot(SnapshotInputs(hardware=[device]), gate=False)


def test_optional_interval_is_absent_unless_set_and_bounded_version_is_unchanged():
    bare = ShownFact(facet="model.parameters_total", value=31_000_000_000).model_dump()
    assert "interval" not in bare and "device" not in bare
    with pytest.raises(ValueError, match="at least low"):
        FactInterval(low=10, high=1)
    assert BOUNDED_VERSION == "1.2"  # MODEL-339 moved it; this slice does not
    assert '"x-contract-version": "2.16"' in render_json_schema()
