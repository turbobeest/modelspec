"""Compute which models fit on which devices, and how fast they would decode.

Everything here is *computed*, never measured, and is labelled as such all the
way to the page. A predicted figure presented as a measurement is a lie a reader
will plan around.

What the corpus can actually support, measured 2026-09-09:

* 1,011 of 1,143 cards carry `total_parameters`; 931 of those are open-weights.
* **Zero** cards carry `active_parameters`, `num_layers`, `num_kv_heads` or
  `hidden_size`.

That second line constrains this module more than anything else:

* Decode speed for a mixture-of-experts model depends on *active* parameters,
  not total. With no active-parameter data the prediction uses total, which
  understates MoE speed — sometimes by a large factor. Every prediction says so.
* Exact KV-cache size needs layer and head geometry. Without it, a flat working
  allowance is used rather than a precise figure dressed up as one.

`FITS_ON` is only computed for open-weights models. Asking whether a
closed-weights model "fits" on your GPU is meaningless — you cannot obtain it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from schema.graph import CollectingSink

#: Bytes per parameter at each quantisation, best case. Real files carry
#: metadata and some layers stay at higher precision, which the working
#: allowance below absorbs.
QUANT_BYTES: dict[str, float] = {
    "fp16": 2.0, "bf16": 2.0, "fp8": 1.0, "int8": 1.0,
    "q6": 0.75, "q5": 0.625, "int4": 0.5, "q4": 0.5,
}

#: Preference order when choosing the best quantisation that fits. Higher
#: precision first: we want the best quality that fits, not the smallest.
QUANT_PREFERENCE = ("bf16", "fp16", "fp8", "int8", "q6", "q5", "q4")

#: Headroom for the KV cache, activations, the framework and the OS, as a
#: fraction of device memory. A blunt instrument, and deliberately so: the
#: corpus has no layer or head geometry, so a precise-looking KV figure would be
#: invented. 25% is conservative for a mid-length context on a device that is
#: also driving a display.
WORKING_ALLOWANCE = 0.25

#: Real bandwidth utilisation. No decoder achieves the theoretical roofline;
#: measured llama.cpp and vLLM figures typically land in the 60-80% band.
BANDWIDTH_EFFICIENCY = 0.70


@dataclass(frozen=True)
class Device:
    id: str
    display_name: str
    vendor: str
    device_class: str
    bandwidth_gb_s: float
    capacity_options_gb: tuple[float, ...]
    precisions_native: tuple[str, ...]
    unified: bool

    @property
    def max_capacity_gb(self) -> float:
        return max(self.capacity_options_gb)


def load_devices(root: Path) -> list[Device]:
    """Read hardware/*.yaml. A device without bandwidth is rejected, not defaulted."""
    out: list[Device] = []
    for path in sorted((root / "hardware").glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        memory = raw["memory"]
        bandwidth = memory.get("bandwidth_gb_s")
        if not bandwidth:
            raise ValueError(
                f"{path.name}: no memory.bandwidth_gb_s. A device without bandwidth "
                "cannot answer how fast a model will run, which is the question this "
                "layer exists to answer. Fix the definition or remove it."
            )
        options = memory.get("capacity_options_gb") or [memory["capacity_gb"]]
        out.append(Device(
            id=raw["id"], display_name=raw["display_name"], vendor=raw["vendor"],
            device_class=raw["device_class"], bandwidth_gb_s=float(bandwidth),
            capacity_options_gb=tuple(float(c) for c in options),
            precisions_native=tuple(raw.get("precisions_native") or []),
            unified=bool(memory.get("unified_with_host")),
        ))
    return out


def weights_gb(params: float, quant: str) -> float:
    return params * QUANT_BYTES[quant] / 1e9


def fitting_quants(params: float, capacity_gb: float) -> list[str]:
    """Every quantisation whose weights fit in the usable memory, best quality first.

    A quantisation the silicon does not accelerate natively is still allowed — it
    runs, just without the speed benefit — so this gates on memory, not on
    `precisions_native`. That field informs the prediction, not the fit.
    """
    usable = capacity_gb * (1.0 - WORKING_ALLOWANCE)
    return [q for q in QUANT_PREFERENCE if weights_gb(params, q) <= usable]


def best_quant(params: float, capacity_gb: float, native: tuple[str, ...] = ()) -> str | None:
    """The highest-quality quantisation that fits, or None."""
    quants = fitting_quants(params, capacity_gb)
    return quants[0] if quants else None


def predicted_decode_tps(bandwidth_gb_s: float, params: float, quant: str) -> float:
    """Roofline estimate: bandwidth divided by the bytes read per token."""
    per_token_gb = weights_gb(params, quant)
    if per_token_gb <= 0:
        return 0.0
    return round(bandwidth_gb_s * BANDWIDTH_EFFICIENCY / per_token_gb, 1)


def compute(sink: CollectingSink, cards: list[Any], devices: list[Device]) -> dict[str, Any]:
    """Add Hardware nodes and FITS_ON edges. Returns counts for the summary."""
    for device in devices:
        sink.node("Hardware", "id", device.id, {
            "id": device.id,
            "display_name": device.display_name,
            "vendor": device.vendor,
            "device_class": device.device_class,
            "memory_bandwidth_gb_s": device.bandwidth_gb_s,
            "memory_gb": device.max_capacity_gb,
            "memory_options_gb": ",".join(str(c) for c in device.capacity_options_gb),
            "unified_memory": device.unified,
        })

    considered = fitted = skipped_closed = skipped_no_params = 0
    edges = 0

    for card in cards:
        params = card.architecture.total_parameters
        if not card.licensing.open_weights:
            skipped_closed += 1
            continue
        if not params:
            skipped_no_params += 1
            continue
        considered += 1
        is_moe = bool(card.architecture.num_experts)
        fitted_any = False

        for device in devices:
            capacity = device.max_capacity_gb
            quants = fitting_quants(params, capacity)
            if not quants:
                continue
            fitted_any = True
            edges += 1
            # Report the range, not a single "best". Highest quality that fits and
            # smallest that fits answer different questions, and quoting only the
            # first makes a large slow machine look worse than a small fast one
            # purely because it chose a heavier quantisation.
            best, smallest = quants[0], quants[-1]
            sink.edge("Model", card.identity.model_id, "FITS_ON", "Hardware", device.id, {
                "quantization": best,
                "weights_gb": round(weights_gb(params, best), 2),
                "device_memory_gb": capacity,
                "predicted_decode_tps": predicted_decode_tps(
                    device.bandwidth_gb_s, params, best),
                "fastest_quantization": smallest,
                "fastest_weights_gb": round(weights_gb(params, smallest), 2),
                "fastest_predicted_decode_tps": predicted_decode_tps(
                    device.bandwidth_gb_s, params, smallest),
                "quantizations_that_fit": ",".join(quants),
                # Everything above is arithmetic, not observation. The page and
                # the export must never render it as a measurement.
                "basis": "computed",
                "assumes_working_allowance": WORKING_ALLOWANCE,
                "assumes_bandwidth_efficiency": BANDWIDTH_EFFICIENCY,
                # No card carries active_parameters, so an MoE prediction uses
                # total parameters and understates its real speed.
                "moe_prediction_is_conservative": is_moe,
            })
        fitted += 1 if fitted_any else 0

    return {
        "devices": len(devices),
        "models_considered": considered,
        "models_fitting_somewhere": fitted,
        "skipped_closed_weights": skipped_closed,
        "skipped_no_parameter_count": skipped_no_params,
        "edges": edges,
        "working_allowance": WORKING_ALLOWANCE,
        "bandwidth_efficiency": BANDWIDTH_EFFICIENCY,
    }
