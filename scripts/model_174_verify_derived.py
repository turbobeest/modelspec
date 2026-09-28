#!/usr/bin/env python3
"""Independently verify MODEL-174 facts from retained primary inputs."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from decision.hardware import DeviceInput
from decision.model import (
    DETERMINISTIC,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore
from decision.verify import Queue, Result, VerificationLog

ROOT = Path(__file__).resolve().parents[1]
TODAY = date(2026, 9, 28)
CHECKED_AT = datetime(2026, 9, 28, 23, 0, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="codex-model-174",
    model_family="openai",
    method="retained-primary-inputs@2",
)
VERIFIER = VerificationActor(
    agent="model-174-derived-verifier",
    model_family=DETERMINISTIC,
    method="independent-derived-recompute@1",
)

_QUANT_BYTES = (2.0, 2.0, 1.0, 1.0, 0.75, 0.625, 0.5)
_WORKING_ALLOWANCE = 0.25


def parameter_count_from_primary(body: bytes) -> int:
    """Read the tensor census from a retained Hugging Face API response."""
    raw = json.loads(body)
    parameters = raw.get("safetensors", {}).get("parameters")
    if not isinstance(parameters, dict) or not parameters:
        raise ValueError("primary source has no safetensors parameter census")
    return sum(int(value) for value in parameters.values())


def recompute_hardware(
    weights_openness: str | None,
    parameters_total: int | None,
    devices: Iterable[DeviceInput],
) -> tuple[tuple[str, ...] | None, tuple[str, ...]]:
    """Recompute membership without calling the collector's fit implementation."""
    device_rows = tuple(devices)
    if weights_openness == "closed_weights":
        return (), ()
    if weights_openness != "open_weights" or parameters_total is None:
        return None, tuple(sorted(device.id for device in device_rows))

    fits: list[str] = []
    indeterminate: list[str] = []
    for device in device_rows:
        if not device.single_device_fit:
            indeterminate.append(device.id)
            continue
        usable_bytes = device.memory_capacity_gb * (1 - _WORKING_ALLOWANCE) * 1e9
        if any(parameters_total * byte_width <= usable_bytes for byte_width in _QUANT_BYTES):
            fits.append(device.id)
    return tuple(sorted(fits)), tuple(sorted(indeterminate))


def verify_private_source(body: bytes, *, expected: bool, proof: str) -> None:
    """Check a positive statement or an exhaustive-table absence in retained content."""
    corpus = re.sub(r"[^a-z0-9]+", " ", body.decode("utf-8", errors="replace").casefold())
    needle = re.sub(r"[^a-z0-9]+", " ", proof.casefold()).strip()
    if expected and needle not in corpus:
        raise ValueError(f"retained source does not state {proof!r}")
    if not expected and needle in corpus:
        raise ValueError(f"retained source still names {proof!r}")


def hardware_registry_hash(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "hardware").glob("*.yaml")):
        if path.name == "_schema.yaml":
            continue
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _devices() -> tuple[DeviceInput, ...]:
    rows = []
    for path in sorted((ROOT / "hardware").glob("*.yaml")):
        if path.name == "_schema.yaml":
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        capacity = raw.get("memory", {}).get("capacity_gb")
        if capacity is None:
            continue
        rows.append(DeviceInput(
            raw["id"],
            float(capacity),
            raw.get("single_device_fit", True),
            raw.get("single_device_fit_reason"),
        ))
    return tuple(rows)


def _front(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def _record(
    log: VerificationLog,
    queue: Queue,
    fact: dict,
    *,
    collector: VerificationActor = COLLECTOR,
) -> None:
    target = TargetRef(kind="fact", id=fact["id"])
    verification = Verification(
        target=VerificationTarget(
            kind="fact", id=fact["id"], value_hash=value_hash(fact["value"])
        ),
        collector=collector,
        verifier=VERIFIER,
        method=VERIFIER.method,
        outcome="verified",
        date=TODAY,
    )
    log.append(verification)
    queue.checked(Result(target, "verified", verification), at=CHECKED_AT)


def verify_hardware(store: CopyStore, log: VerificationLog, queue: Queue) -> int:
    devices = _devices()
    manifest_hash = hardware_registry_hash()
    count = 0
    lineup = yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    for row in lineup:
        model_id = row["model_id"]
        data = _front(ROOT / "models" / f"{model_id}.md")
        facts = {fact["facet"]: fact for fact in data.get("facts", [])}
        openness = facts["model.weights_openness"]["value"]
        parameter_fact = facts.get("model.parameters_total")
        parameters = None if parameter_fact is None else int(parameter_fact["value"])
        fit_fact = facts["model.fits_hardware"]
        derivation = fit_fact.get("derivation") or {}
        inputs = derivation.get("inputs") or {}
        if inputs.get("hardware_registry_sha256") != manifest_hash:
            raise ValueError(f"{model_id}: hardware input snapshot is not bound")
        if inputs.get("hardware_device_count") != len(devices):
            raise ValueError(f"{model_id}: hardware input count differs")

        if openness == "open_weights":
            source_ref = parameter_fact["sources"][0]
            if inputs.get("model_snapshot_ref") != source_ref["snapshot_ref"]:
                raise ValueError(f"{model_id}: parameter input snapshot is not bound")
            retained_parameters = parameter_count_from_primary(
                store.get(source_ref["snapshot_ref"])
            )
            if retained_parameters != parameters:
                raise ValueError(
                    f"{model_id}: retained primary count {retained_parameters} != {parameters}"
                )
            _record(log, queue, parameter_fact)
            count += 1

        expected_fit, expected_indeterminate = recompute_hardware(
            openness, parameters, devices
        )
        actual_fit = None if fit_fact["value"] is None else tuple(fit_fact["value"])
        if actual_fit != expected_fit:
            raise ValueError(f"{model_id}: hardware fit differs from independent recomputation")
        if fit_fact["state"] == "known":
            _record(log, queue, fit_fact)
            count += 1

        indeterminate = facts.get("model.hardware_fit_indeterminate")
        if expected_fit is not None and expected_indeterminate:
            if indeterminate is None or tuple(indeterminate["value"]) != expected_indeterminate:
                raise ValueError(f"{model_id}: indeterminate device set differs")
            if indeterminate.get("derivation") != derivation:
                raise ValueError(f"{model_id}: indeterminate set has different inputs")
            _record(log, queue, indeterminate)
            count += 1
    return count


def verify_private(store: CopyStore, log: VerificationLog, queue: Queue) -> int:
    count = 0
    for path in sorted((ROOT / "offerings").glob("*/*/*.yaml")):
        for offering in yaml.safe_load(path.read_text(encoding="utf-8")):
            for fact in offering.get("facts", []):
                if fact["facet"] != "offering.private_deployment" or fact["state"] != "known":
                    continue
                ref = fact["sources"][0]
                body = store.get(ref["snapshot_ref"])
                provider = offering["provider"]
                if fact["value"]:
                    proof = {
                        "azure-ai-foundry": "provisioned throughput",
                        "openai": "scale tier" if offering["model"].endswith("gpt-5-4")
                        else "reserved tier",
                        "google-vertex-ai": "provisioned throughput",
                    }[provider]
                else:
                    proof = offering["model"].rsplit("/", 1)[-1]
                verify_private_source(body, expected=fact["value"], proof=proof)
                _record(log, queue, fact)
                count += 1
    return count


def main() -> None:
    store = CopyStore()
    log = VerificationLog(ROOT / "verification")
    queue = Queue(ROOT / "verification")
    hardware = verify_hardware(store, log, queue)
    private = verify_private(store, log, queue)
    print(f"verified {hardware} hardware facts and {private} private-deployment facts")


if __name__ == "__main__":
    main()
