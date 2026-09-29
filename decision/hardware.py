"""Decision-layer hardware-fit estimates (MODEL-174).

The estimate consumes verified model parameter counts and sourced device-memory
facts.  It deliberately delegates quantisation arithmetic to the established
hardware layer so the v1 view and the decision snapshot cannot disagree.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from pipeline.hardware import QUANT_BYTES, WORKING_ALLOWANCE, fitting_quants, weights_gb

FORMULA = (
    "parameters_total * bytes_per_parameter <= "
    "memory_capacity_gb * (1 - working_allowance) * 1e9"
)


@dataclass(frozen=True)
class DeviceInput:
    id: str
    memory_capacity_gb: float
    single_device_fit: bool = True
    refusal_reason: str | None = None


@dataclass(frozen=True)
class DeviceFit:
    fits: bool | None
    best_quant: str | None
    quantisations: tuple[str, ...]
    weights_gb: float | None
    usable_memory_gb: float | None
    reason: str | None = None


@dataclass(frozen=True)
class HardwareFit:
    fits_hardware: tuple[str, ...] | None
    indeterminate_hardware: tuple[str, ...]
    devices: Mapping[str, DeviceFit]
    formula: str
    inputs: Mapping[str, float | int | None | str]


def compute_fit(
    *,
    weights_openness: str | None,
    parameters_total: int | float | None,
    devices: Sequence[DeviceInput],
) -> HardwareFit:
    """Compute every per-device leg, preserving unknown instead of guessing."""
    rows: dict[str, DeviceFit] = {}
    known_fits: list[str] = []

    for device in devices:
        if weights_openness == "closed_weights":
            rows[device.id] = DeviceFit(
                False, None, (), None, None, "closed weights are not self-hostable"
            )
            continue
        if weights_openness != "open_weights":
            rows[device.id] = DeviceFit(
                None, None, (), None, None, "verified weights openness is missing"
            )
            continue
        if parameters_total is None:
            rows[device.id] = DeviceFit(
                None, None, (), None, None, "verified total parameter count is missing"
            )
            continue
        if not device.single_device_fit:
            rows[device.id] = DeviceFit(
                None,
                None,
                (),
                None,
                None,
                device.refusal_reason or "device does not expose one usable memory pool",
            )
            continue

        quants = tuple(fitting_quants(float(parameters_total), device.memory_capacity_gb))
        best = quants[0] if quants else None
        if best is not None:
            known_fits.append(device.id)
        rows[device.id] = DeviceFit(
            fits=best is not None,
            best_quant=best,
            quantisations=quants,
            weights_gb=weights_gb(float(parameters_total), best) if best else None,
            usable_memory_gb=device.memory_capacity_gb * (1 - WORKING_ALLOWANCE),
            reason=None if best else "no supported quantisation fits usable memory",
        )

    has_unknown = any(row.fits is None for row in rows.values())
    all_unknown = bool(rows) and all(row.fits is None for row in rows.values())
    return HardwareFit(
        fits_hardware=None if all_unknown else tuple(sorted(known_fits)),
        indeterminate_hardware=tuple(sorted(
            device_id for device_id, row in rows.items() if row.fits is None
        )),
        devices=MappingProxyType(rows),
        formula=FORMULA,
        inputs=MappingProxyType({
            "weights_openness": weights_openness,
            "parameters_total": parameters_total,
            "working_allowance": WORKING_ALLOWANCE,
            "quant_bytes": str(dict(sorted(QUANT_BYTES.items()))),
            "has_device_unknowns": str(has_unknown).lower(),
        }),
    )


__all__ = ["DeviceFit", "DeviceInput", "FORMULA", "HardwareFit", "compute_fit"]
