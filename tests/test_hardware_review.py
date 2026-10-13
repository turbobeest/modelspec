"""Literal regressions for the MODEL-348 review probes p2, p3 and p4."""

from __future__ import annotations

import json

import pytest
import yaml

from decision.contract import Decision, InventoryProfile, SpecError, parse_spec
from decision.engine import decide
from decision.excluded import ExcludedSources
from decision.registry import default as registry
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.test_architecture_facts import (
    ROOT, SOURCES_WITH_HARDWARE, SPARK, answer, estimates, facts, fixture_snapshot,
    generator, spark, spec,
)


def device(name):
    return yaml.safe_load((ROOT / "hardware" / f"{name}.yaml").read_text())


def registered_sources(devices):
    urls = sorted({url for row in devices for url in row["sources"]}
                  - set(SOURCES_WITH_HARDWARE.values()))
    return {**SOURCES_WITH_HARDWARE,
            **{f"fixture-hardware-{i}": url for i, url in enumerate(urls)}}


def test_p2_multi_device_estimates_preserve_the_known_unique_facts_contract():
    devices = [spark(), device("nvidia_rtx_4090"), device("apple_m3_max"), device("cerebras_wse3")]
    index = fixture_snapshot(hardware=devices, sources=registered_sources(devices))
    decision = answer(index, access="own_hardware", estate={"devices": [row["id"] for row in devices]})
    assert decision.status == "answered"
    for top in decision.top:
        assert len(top.facts) == len({fact.facet for fact in top.facts})
        assert all(fact.value is not None for fact in top.facts)
        assert all(fact.record_id or isinstance(fact.value, int | float) and fact.formula
                   for fact in top.facts)
        assert all(not fact.facet.startswith("hardware.") for fact in top.facts)
        # The MoE fixtures carry no expert counts; dense rows owe none.
        assert top.model_dump().get("unknown_facets", []) in (
            [], ["model.experts_per_token", "model.experts_total"])
    top = next(row for row in decision.top if row.offering.model == "lab/gemma")
    assert [(row.device, row.facet, row.value, row.quantisation) for row in top.hardware_estimates] == [
        ("apple_m3_max", "hardware.weights_gb", 51.6, "bf16"),
        ("cerebras_wse3", "hardware.weights_gb", None, None),
        (SPARK, "hardware.weights_gb", 51.6, "bf16"),
        ("nvidia_rtx_4090", "hardware.weights_gb", 16.1, "q5"),
        ("apple_m3_max", "hardware.decode_tps_estimate", 36.8, "bf16"),
        ("cerebras_wse3", "hardware.decode_tps_estimate", None, None),
        (SPARK, "hardware.decode_tps_estimate", 25.1, "bf16"),
        ("nvidia_rtx_4090", "hardware.decode_tps_estimate", 297.1, "q5"),
    ]
    assert top.hardware_estimates[1].unknown_reason == (
        "On-wafer SRAM is working memory, not a GPU-style frame buffer; Cerebras streams weights "
        "from external MemoryX. The single-device FITS_ON calculation is misleading for this part.")
    assert top.hardware_estimates[7].interval.model_dump() == {"low": 148.5, "high": 360.8}
    assert Decision.model_validate_json(decision.model_dump_json()) == decision


def test_p2_single_device_decode_objective_and_condition_keep_provenance():
    index = fixture_snapshot()
    ranked = answer(index, estate={"devices": [SPARK]}, optimize={"max": "hardware.decode_tps_estimate"})
    assert ranked.status == "partial"
    assert [row.model for row in ranked.results] == ["lab/gemma", "lab/dense"]
    assert [row.contributions[0].raw_value for row in ranked.results] == [25.1, 3.1]
    assert [(row.model, row.unknown) for row in ranked.may_qualify] == [
        ("lab/deepseek", ["hardware.decode_tps_estimate"])]
    filtered = answer(index, estate={"devices": [SPARK]},
                      where=["model.class = text-generator", "hardware.decode_tps_estimate >= 10"])
    assert filtered.status == "partial"
    assert [row.model for row in filtered.results] == ["lab/gemma"]
    assert [(row.model, row.unknown) for row in filtered.may_qualify] == [
        ("lab/deepseek", ["hardware.decode_tps_estimate"])]
    eliminated = filtered.eliminated.models[0]
    assert (eliminated.model, eliminated.value, eliminated.records) == (
        "lab/dense", 3.1, ["lab/dense#model.parameters_total", "lab/dense#model.weights_openness",
                           "hardware:nvidia_dgx_spark#memory", "lab/dense#model.parameters_active"])
    assert "parameters_active 3.1e+10" in eliminated.formula
    miss = filtered.near_misses[0]
    assert (miss.offering.model, miss.value, miss.distance) == ("lab/dense", 3.1, 6.9)
    assert miss.records == ["lab/dense#model.parameters_total", "lab/dense#model.weights_openness",
                            "hardware:nvidia_dgx_spark#memory", "lab/dense#model.parameters_active"]


@pytest.mark.parametrize("estate", [None, {}, {"devices": []}, {"devices": [SPARK, "nvidia_rtx_4090"]}])
@pytest.mark.parametrize("updates", [
    {"where": ["hardware.decode_tps_estimate >= 10"]},
    {"where": ["hardware.weights_gb <= 70"]},
    {"where": [{"not": {"all": ["hardware.weights_gb <= 70", "model.class = text-generator"]}}]},
    {"where": [{"any": [{"known": "hardware.decode_tps_estimate"}, "model.class = text-generator"]}]},
    {"where": [{"facet": "hardware.weights_gb", "op": "<=", "value": 70,
                "soft": {"penalty": 0.1}}]},
    {"profile": {"profile_version": 1, "rules": ["hardware.weights_gb <= 70"]}},
    {"optimize": {"max": "hardware.decode_tps_estimate"}},
    {"optimize": {"min": "hardware.weights_gb"}},
    {"optimize": {"weights": {"-hardware.weights_gb": 1}}},
    {"optimize": {"lexicographic": [{"max": "hardware.decode_tps_estimate"},
                                     {"max": "model.context_window"}]}},
    {"optimize": {"pareto": ["hardware.decode_tps_estimate", "-hardware.weights_gb"]}},
])
def test_p2_p3_unevaluable_hardware_conditions_and_objectives_are_refused(estate, updates):
    with pytest.raises(SpecError, match="exactly one device in estate.devices") as exc:
        spec(estate=estate, **updates)
    assert [(issue.path, issue.field) for issue in exc.value.issues] == [
        ("estate.devices", "estate.devices")]


def test_hardware_device_requirement_also_applies_without_a_registry_lookup():
    with pytest.raises(SpecError, match="exactly one device in estate.devices") as exc:
        parse_spec({"spec_version": 1, "optimize": {"max": "hardware.decode_tps_estimate"}}, facets=None)
    assert [issue.path for issue in exc.value.issues] == ["estate.devices"]


@pytest.mark.parametrize("estate", [None, {}, {"devices": []}, {"devices": [SPARK, "nvidia_rtx_4090"]}])
def test_a_loaded_profile_hardware_condition_needs_one_estate_device(estate):
    profiles = {"profile:hardware": InventoryProfile.model_validate({
        "profile_version": 1, "rules": ["hardware.decode_tps_estimate >= 10"]})}
    index = fixture_snapshot()
    with pytest.raises(SpecError, match="exactly one device in estate.devices") as exc:
        decide(spec(profile="profile:hardware", estate=estate), index, facets=registry().facet, profiles=profiles)
    assert [(issue.path, issue.field) for issue in exc.value.issues] == [
        ("estate.devices", "estate.devices")]
    decision = decide(spec(profile="profile:hardware", estate={"devices": [SPARK]}),
                      index, facets=registry().facet, profiles=profiles)
    assert [row.model for row in decision.results] == ["lab/gemma"]
    assert [(row.model, row.unknown) for row in decision.may_qualify] == [
        ("lab/deepseek", ["hardware.decode_tps_estimate"])]


def test_scalar_uses_the_estate_device_when_fit_conditions_name_another_device():
    devices = [spark(), device("nvidia_rtx_4090")]
    index = fixture_snapshot(hardware=devices, sources=registered_sources(devices))
    decision = answer(index, estate={"devices": [SPARK]}, where=[
        "model.class = text-generator", {"not": "model.fits_hardware = nvidia_rtx_4090"},
        "hardware.decode_tps_estimate >= 10"])
    assert [row.model for row in decision.results] == ["lab/gemma"]
    assert facts(decision, "lab/gemma")["model.parameters_active"].value == 3_800_000_000
    assert {row.device for row in decision.top[0].hardware_estimates} == {SPARK, "nvidia_rtx_4090"}


def test_p2_negated_hardware_fit_still_shows_estimates_and_both_reading_lines():
    devices = [spark(), device("nvidia_rtx_4090")]
    decision = answer(fixture_snapshot(hardware=devices, sources=registered_sources(devices)),
                      where=["model.class = text-generator", {"not": "model.fits_hardware = nvidia_rtx_4090"}])
    assert decision.status == "answered"
    assert [row.model for row in decision.results] == ["lab/deepseek", "lab/dense", "lab/gemma"]
    assert {row.device for top in decision.top for row in top.hardware_estimates} == {"nvidia_rtx_4090"}
    assert "Do not claim fit for a specific quantization or context workload." in decision.reading.do_not_claim
    assert "Quantisation is assumed; context fit and decode speed are unmeasured." in decision.reading.do_not_claim


@pytest.mark.parametrize("facet, condition", [
    ("model.architecture", "model.architecture = MoE"),
    ("model.parameters_active", "model.parameters_active <= 1"),
    ("model.context_window", "model.context_window >= 1"),
])
def test_p3_all_unknown_hard_conditions_match_the_existing_best_effort_reporting(facet, condition):
    row = generator("lab/unknown")
    row["facts"] = [fact for fact in row["facts"] if fact["facet"] != facet]
    decision = answer(fixture_snapshot(models=[row]), where=["model.class = text-generator", condition])
    assert decision.status == "no_feasible"
    assert decision.answer is None
    assert decision.results == []
    assert [(row.model, row.unknown) for row in decision.may_qualify] == [("lab/unknown", [facet])]
    assert decision.eliminated.models == []
    assert decision.relax == [condition]
    assert decision.warnings == []


def test_p3_a_known_active_parameter_failure_is_an_elimination():
    decision = answer(fixture_snapshot(), where=["model.class = text-generator", "model.parameters_active <= 1"])
    assert decision.status == "no_feasible"
    assert decision.may_qualify == []
    assert [row.model for row in decision.eliminated.models] == ["lab/deepseek", "lab/dense", "lab/gemma"]
    assert decision.relax == ["model.parameters_active <= 1"]


def test_unknown_architecture_facets_and_estimates_do_not_widen_facts():
    decision = answer(fixture_snapshot(models=[generator("lab/unknown", None, total=None, active=None)]),
                      estate={"devices": [SPARK]})
    top = decision.top[0]
    assert top.unknown_facets == [
        "model.architecture", "model.experts_per_token", "model.experts_total",
        "model.parameters_active", "model.parameters_total"]
    assert [fact.facet for fact in top.facts] == [
        "model.class", "model.context_window", "model.weights_openness"]
    assert [(row.facet, row.value, row.quantisation, row.unknown_reason) for row in top.hardware_estimates] == [
        ("hardware.weights_gb", None, None, "verified total parameter count is missing"),
        ("hardware.decode_tps_estimate", None, None, "verified total parameter count is missing"),
    ]
    assert "unknown_facets" not in answer(fixture_snapshot()).top[0].model_dump()
    assert "hardware_estimates" not in answer(fixture_snapshot()).top[0].model_dump()


def test_p4_weight_memory_does_not_include_a_device_scaled_allowance():
    devices = [device("apple_m3_ultra"), device("nvidia_rtx_4090")]
    index = fixture_snapshot(models=[generator("lab/small", total=8_000_000_000, active=8_000_000_000,
                                               fits=("apple_m3_ultra", "nvidia_rtx_4090"))],
                             hardware=devices, sources=registered_sources(devices))
    for sku, capacity, usable in [("apple_m3_ultra", "512", "384"), ("nvidia_rtx_4090", "24", "18")]:
        decision = answer(index, estate={"devices": [sku]},
                          where=["model.class = text-generator", "hardware.weights_gb <= 64"])
        assert decision.status == "answered"
        weights = estimates(decision, "lab/small")["hardware.weights_gb"]
        assert (weights.value, weights.quantisation) == (16.0, "bf16")
        assert f"device capacity {capacity} GB, largest listed memory configuration" in weights.formula
        assert f"usable memory {capacity} × (1 - 0.25) = {usable} GB" in weights.formula


def test_p4_old_snapshot_has_an_explicit_missing_device_reason():
    decision = answer(fixture_snapshot(hardware=[]), estate={"devices": [SPARK]})
    assert [(row.facet, row.value, row.quantisation, row.unknown_reason)
            for row in decision.top[0].hardware_estimates] == [
        ("hardware.weights_gb", None, None, "snapshot has no device memory specifications for this SKU"),
        ("hardware.decode_tps_estimate", None, None, "snapshot has no device memory specifications for this SKU"),
    ]


@pytest.mark.parametrize("missing", [("spark-spec",), ("spark-spec", "spark-manual")])
def test_unregistered_hardware_sources_produce_unknowns_without_invented_ids(missing, caplog):
    sources = {k: v for k, v in SOURCES_WITH_HARDWARE.items() if k not in missing}
    built = build_snapshot(SnapshotInputs(models=[generator("lab/a")], hardware=[spark()],
                                         sources=sources), gate=False)
    for sid in missing:
        url = SOURCES_WITH_HARDWARE[sid]
        assert url not in json.dumps(built.content)
        assert url in caplog.text
    index = load_built_snapshot(built, include_archive=False)
    reason = f"{len(missing)} hardware source URLs are not registered"
    assert index.hardware_device(SPARK) == {"unknown_reason": reason, "record_id": None, "source_ids": []}
    decision = answer(index, estate={"devices": [SPARK]})
    assert [(row.value, row.quantisation, row.unknown_reason) for row in decision.top[0].hardware_estimates] == [
        (None, None, reason), (None, None, reason)]
    assert [row.id for row in decision.sources] == ["src-lab-docs"]
    assert all(not sid.startswith("hardware-") for row in decision.top[0].hardware_estimates for sid in row.source_ids)
    for row in decision.top[0].hardware_estimates:
        assert "http" not in row.model_dump_json()
        assert reason not in row.formula
        assert row.model_dump_json().count(reason) == 1


def test_excluded_hardware_source_has_an_explicit_reason_and_retains_no_excluded_url():
    row = spark()
    row["sources"] = ["https://excluded.example/device"]
    built = build_snapshot(SnapshotInputs(models=[generator("lab/a")], hardware=[row],
                                         sources={**SOURCES_WITH_HARDWARE,
                                                  "excluded": "https://excluded.example/device"}),
                           guard=ExcludedSources(hosts=("excluded.example",)), gate=False)
    assert "excluded.example" not in str(built.content)
    decision = answer(load_built_snapshot(built, include_archive=False), estate={"devices": [SPARK]})
    assert [(row.value, row.unknown_reason) for row in decision.top[0].hardware_estimates] == [
        (None, "device memory source is excluded by the snapshot source policy"),
        (None, "device memory source is excluded by the snapshot source policy")]
    assert [row.id for row in decision.sources] == ["src-lab-docs"]


@pytest.mark.parametrize("parameters, expected", [(616_000, 0.00123), (25_800_000_000, 51.6),
                                                   (1, 2e-9)])
def test_weights_use_three_significant_figures_without_zeroing_tiny_models(parameters, expected):
    decision = answer(fixture_snapshot(models=[generator("lab/tiny", total=parameters, active=parameters)]),
                      estate={"devices": [SPARK]})
    assert estimates(decision, "lab/tiny")["hardware.weights_gb"].value == expected
