"""MODEL-174 hardware-fit computation and private-deployment coverage."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from decision import registry
from decision.contract import parse_spec
from decision.filter import apply as filter_apply
from decision.hardware import DeviceInput, compute_fit
from decision.model import load_offerings
from decision.resolve import resolve
from decision.snapshot import build_snapshot, collect_repo, load_premier, load_snapshot_bytes
from decision.vocabulary import build_vocabulary
from pipeline.hardware import WORKING_ALLOWANCE, load_devices
from scripts.model_174_verify_derived import (
    parameter_count_from_primary,
    recompute_hardware,
    verify_private_source,
)
from tests.snapshot_records import FactValue, loaded_index

ROOT = Path(__file__).parents[1]


def test_independent_verifier_reads_primary_parameter_content() -> None:
    body = b'{"safetensors":{"parameters":{"BF16":120,"F32":3}}}'

    assert parameter_count_from_primary(body) == 123


def test_independent_verifier_recomputes_each_hardware_leg() -> None:
    fits, indeterminate = recompute_hardware(
        "open_weights",
        1_000_000_000,
        (
            DeviceInput("small", 0.5),
            DeviceInput("large", 32.0),
            DeviceInput("refused", 44.0, False, "not one memory pool"),
        ),
    )

    assert fits == ("large",)
    assert indeterminate == ("refused",)


def test_private_verifier_checks_retained_provider_content() -> None:
    verify_private_source(
        b"Provisioned Throughput is dedicated capacity in your deployment.",
        expected=True,
        proof="provisioned throughput",
    )
    verify_private_source(
        b"Supported models: Nova Pro, Titan Text.",
        expected=False,
        proof="claude-opus-5-5",
    )
    with pytest.raises(ValueError, match="still names"):
        verify_private_source(
            b"Supported models: Claude Opus 5.5.",
            expected=False,
            proof="claude-opus-5-5",
        )


@pytest.fixture(scope="module")
def repo_snapshot():
    built = build_snapshot(
        collect_repo(ROOT),
        registry=registry.default(),
        premier=load_premier(ROOT / "premier/slice-1.yaml"),
        gate=False,
    )
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, public_keys={})


def test_fit_computation_records_quantisation_formula_and_inputs() -> None:
    devices = (
        DeviceInput("nvidia_rtx_5090", 32.0),
        DeviceInput("nvidia_dgx_spark", 128.0),
    )

    result = compute_fit(
        weights_openness="open_weights",
        parameters_total=40_000_000_000,
        devices=devices,
    )

    assert result.fits_hardware == ("nvidia_dgx_spark", "nvidia_rtx_5090")
    assert result.devices["nvidia_rtx_5090"].best_quant == "q4"
    assert result.devices["nvidia_dgx_spark"].best_quant == "bf16"
    assert result.formula == (
        "parameters_total * bytes_per_parameter <= "
        "memory_capacity_gb * (1 - working_allowance) * 1e9"
    )
    assert result.inputs["parameters_total"] == 40_000_000_000
    assert result.inputs["working_allowance"] == WORKING_ALLOWANCE


def test_closed_weights_are_known_not_self_hostable() -> None:
    result = compute_fit(
        weights_openness="closed_weights",
        parameters_total=None,
        devices=(DeviceInput("nvidia_rtx_5090", 32.0),),
    )

    assert result.fits_hardware == ()
    assert result.devices["nvidia_rtx_5090"].fits is False
    assert result.devices["nvidia_rtx_5090"].reason == "closed weights are not self-hostable"


def test_missing_parameter_count_is_unknown_with_a_reason() -> None:
    result = compute_fit(
        weights_openness="open_weights",
        parameters_total=None,
        devices=(DeviceInput("nvidia_rtx_5090", 32.0),),
    )

    assert result.fits_hardware is None
    assert result.devices["nvidia_rtx_5090"].fits is None
    assert result.devices["nvidia_rtx_5090"].reason == "verified total parameter count is missing"


def test_fit_computation_covers_every_registered_device() -> None:
    devices = tuple(
        DeviceInput(
            device.id,
            device.max_capacity_gb,
            device.single_device_fit,
            device.single_device_fit_reason,
        )
        for device in load_devices(ROOT)
    )

    result = compute_fit(
        weights_openness="open_weights",
        parameters_total=1_000_000_000,
        devices=devices,
    )

    assert set(result.devices) == {device.id for device in devices}
    assert result.indeterminate_hardware == (
        "cerebras_wse3",
        "nvidia_vera_rubin_superchip",
    )
    for device in devices:
        fit = result.devices[device.id]
        if device.single_device_fit:
            assert fit.fits is True
            assert fit.best_quant == "bf16"
        else:
            assert fit.fits is None
            assert fit.reason == device.refusal_reason


def test_every_slice1_offering_files_private_deployment(repo_snapshot) -> None:
    premier = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    }
    offerings = [
        offering
        for path in sorted((ROOT / "offerings").glob("*/*/*.yaml"))
        for offering in load_offerings(path)
    ]

    assert offerings
    for offering in offerings:
        assert offering.model in premier
        facts = [f for f in offering.facts if f.facet == "offering.private_deployment"]
        assert len(facts) == 1, offering.id
        fact = facts[0]
        if fact.state == "unknown":
            assert fact.value is None
            assert fact.checked_sources
        else:
            assert fact.sources
        admitted = repo_snapshot.fact(offering.id, "offering.private_deployment")
        assert admitted.state == fact.state
        assert admitted.value == fact.value


def test_every_slice1_model_files_hardware_fit(repo_snapshot) -> None:
    premier = yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    for row in premier:
        path = ROOT / "models" / f"{row['model_id']}.md"
        front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        facts = [f for f in front.get("facts", []) if f["facet"] == "model.fits_hardware"]
        assert len(facts) == 1, row["model_id"]
        fact = facts[0]
        openness = next(
            f for f in front.get("facts", []) if f["facet"] == "model.weights_openness"
        )
        if openness["value"] == "open_weights":
            assert fact["state"] in {"known", "unknown"}
        elif openness["value"] == "closed_weights":
            assert fact["state"] == "known"
            assert fact["value"] == []
        else:
            assert fact["state"] == "unknown"
            assert fact["value"] is None
            assert fact["checked_sources"]
        admitted = repo_snapshot.fact(row["model_id"], "model.fits_hardware")
        assert admitted.state == fact["state"]
        assert admitted.value == fact["value"]


def hardware_spec(device: str):
    parsed = parse_spec({
        "spec_version": 1,
        "where": [f"model.fits_hardware in {{{device}}}"],
        "optimize": {"max": "model.context_window"},
    }, facets=registry.facet)
    return resolve(parsed, facets=registry.facet)


def test_a_device_must_filters_the_decision_snapshot(repo_snapshot) -> None:
    result = filter_apply(hardware_spec("nvidia_rtx_5090"), repo_snapshot)

    assert "kingsoft/qzhou-embedding" in result.feasible
    assert "openai/openai/gpt-5-6-sol/global/standard" in {
        row.candidate for row in result.eliminated
    }


@pytest.mark.parametrize("device", ["cerebras_wse3", "nvidia_vera_rubin_superchip"])
def test_a_refused_device_must_preserves_per_device_unknown(repo_snapshot, device) -> None:
    result = filter_apply(hardware_spec(device), repo_snapshot)

    assert "google/gemma-4-e2b-it" in {
        row.candidate for row in result.may_qualify
    }
    assert "kingsoft/qzhou-embedding" in {
        row.candidate for row in result.may_qualify
    }
    assert "google/gemma-4-e2b-it" not in {
        row.candidate for row in result.eliminated
    }
    assert "kingsoft/qzhou-embedding" not in {
        row.candidate for row in result.eliminated
    }


def test_an_unknown_hardware_fit_may_qualify() -> None:
    snapshot = loaded_index({
        "lab/known": {"model.fits_hardware": ["nvidia_rtx_5090"]},
        "lab/unknown": {"model.fits_hardware": FactValue("unknown", None)},
    })

    result = filter_apply(hardware_spec("nvidia_rtx_5090"), snapshot)

    assert result.feasible == ("lab/known",)
    assert [row.candidate for row in result.may_qualify] == ["lab/unknown"]


def _mixed_device_index():
    return loaded_index({
        "lab/fits-and-refused": {
            "model.fits_hardware": ["nvidia_rtx_5090"],
            "model.hardware_fit_indeterminate": ["cerebras_wse3"],
        },
        "lab/refused-only": {
            "model.fits_hardware": [],
            "model.hardware_fit_indeterminate": ["cerebras_wse3"],
        },
        "lab/fits-only": {
            "model.fits_hardware": ["nvidia_rtx_5090"],
            "model.hardware_fit_indeterminate": [],
        },
    })


def _candidates(snapshot, bits: int) -> set[str]:
    return {cid for row, cid in enumerate(snapshot.candidates()) if bits >> row & 1}


def test_a_must_naming_a_fitting_and_a_refused_device_keeps_them_disjoint() -> None:
    snapshot = _mixed_device_index()

    result = filter_apply(
        hardware_spec("nvidia_rtx_5090, cerebras_wse3"), snapshot
    )

    assert set(result.feasible) == {"lab/fits-and-refused", "lab/fits-only"}
    assert [row.candidate for row in result.may_qualify] == ["lab/refused-only"]
    assert result.eliminated == ()


def test_contains_all_counts_fitting_devices_as_passing_and_refused_as_unknown() -> None:
    snapshot = _mixed_device_index()

    both = snapshot.ids_where(
        "model.fits_hardware", "contains_all", ["nvidia_rtx_5090", "cerebras_wse3"]
    )
    assert _candidates(snapshot, both.passing) == set()
    assert _candidates(snapshot, both.unknown) == {"lab/fits-and-refused"}
    assert _candidates(snapshot, both.failing) == {"lab/refused-only", "lab/fits-only"}

    fitted = snapshot.ids_where(
        "model.fits_hardware", "contains_all", ["nvidia_rtx_5090"]
    )
    assert _candidates(snapshot, fitted.passing) == {
        "lab/fits-and-refused", "lab/fits-only",
    }
    assert _candidates(snapshot, fitted.failing) == {"lab/refused-only"}


def test_private_deployment_is_also_a_three_valued_must(repo_snapshot) -> None:
    parsed = parse_spec({
        "spec_version": 1,
        "where": ["offering.private_deployment = true"],
        "optimize": {"min": "offering.price.input"},
    }, facets=registry.facet)
    result = filter_apply(resolve(parsed, facets=registry.facet), repo_snapshot)

    assert "azure-ai-foundry/openai/gpt-5-6-sol/global-short-context/standard" \
        in result.feasible
    assert "anthropic/anthropic/claude-opus-5-5/global/standard" in {
        row.candidate for row in result.may_qualify
    }
    assert "aws-bedrock/anthropic/claude-opus-5-5/global-cross-region/standard" in {
        row.candidate for row in result.eliminated
    }
    assert "deepseek/deepseek/deepseek-v4-pro/global/standard" in {
        row.candidate for row in result.may_qualify
    }


def test_hardware_and_private_deployment_reach_the_vocabulary(repo_snapshot) -> None:
    facets = {row["id"]: row for row in build_vocabulary(repo_snapshot)["facets"]}

    assert any(
        value["value"] == "nvidia_rtx_5090"
        for value in facets["model.fits_hardware"]["values"]
    )
    assert {value["value"] for value in facets["offering.private_deployment"]["values"]} \
        == {False, True}
