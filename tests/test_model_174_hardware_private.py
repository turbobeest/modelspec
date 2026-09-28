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
from tests.snapshot_records import FactValue, loaded_index


ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def repo_snapshot():
    built = build_snapshot(
        collect_repo(ROOT),
        registry=registry.default(),
        premier=load_premier(ROOT / "premier/slice-1.yaml"),
        gate=False,
    )
    return load_snapshot_bytes(built.to_bytes(key=None), key=None)


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


def test_an_unknown_hardware_fit_may_qualify() -> None:
    snapshot = loaded_index({
        "lab/known": {"model.fits_hardware": ["nvidia_rtx_5090"]},
        "lab/unknown": {"model.fits_hardware": FactValue("unknown", None)},
    })

    result = filter_apply(hardware_spec("nvidia_rtx_5090"), snapshot)

    assert result.feasible == ("lab/known",)
    assert [row.candidate for row in result.may_qualify] == ["lab/unknown"]


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


def test_hardware_and_private_deployment_reach_the_vocabulary(repo_snapshot) -> None:
    facets = {row["id"]: row for row in build_vocabulary(repo_snapshot)["facets"]}

    assert any(
        value["value"] == "nvidia_rtx_5090"
        for value in facets["model.fits_hardware"]["values"]
    )
    assert {value["value"] for value in facets["offering.private_deployment"]["values"]} \
        == {False, True}
