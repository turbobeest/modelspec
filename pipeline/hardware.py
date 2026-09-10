"""Compute which models fit on which devices, and how fast they would decode.

Everything here is *computed*, never measured, and is labelled as such all the
way to the page. A predicted figure presented as a measurement is a lie a reader
will plan around.

Decode speed for a mixture-of-experts model depends on *active* parameters, not
total. With no active-parameter data the prediction uses total, which understates
MoE speed — sometimes by a large factor. Every prediction says so.

Max context is leftover memory after weights and the working allowance, divided
by the KV-cache bytes per token. That needs layer and head geometry
(`num_layers`, `num_kv_heads` or `num_attention_heads`, `hidden_size`). The
schema has no `head_dim`; it is derived as `hidden_size / num_attention_heads`.
When any of that is missing, `max_context_at_quant` is null — never zero, never
a guess — and `max_context_missing_geometry` is true so a consumer can tell
"we do not know" from "it does not fit".

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

#: Headroom for activations, the framework and the OS, as a fraction of device
#: memory. KV-cache size is computed from layer geometry when the card has it;
#: this allowance is the rest of the working set, not a stand-in for the cache.
WORKING_ALLOWANCE = 0.25

#: Bytes per KV-cache element. The cache is commonly kept at fp16 even when the
#: weights are quantised; using QUANT_BYTES for the weight quant would understate
#: the cache (and overstate how much context fits) at q4/int8.
KV_BYTES_PER_ELEMENT = 2.0

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


@dataclass(frozen=True)
class MaxContext:
    """Predicted context length at one (device, quant) pair.

    `tokens` is null only when geometry is missing. Zero means the weights fit
    but leftover memory cannot hold a single token of KV — that is not the
    same as "we do not know".
    """
    tokens: int | None
    bound_by: str | None
    missing_geometry: bool
    kv_heads_from_attention: bool


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
    """Roofline estimate: bandwidth divided by the bytes read per token.

    `params` must be the parameters actually *read* to emit a token, which for a
    mixture-of-experts model is its active count, not its total. The difference
    is not marginal: qwen3-coder-next holds 480B and activates 3.2B, a factor of
    148. Using total parameters there understates its speed by that factor and
    makes the architecture built for speed look like the worst local choice.
    """
    per_token_gb = weights_gb(params, quant)
    if per_token_gb <= 0:
        return 0.0
    return round(bandwidth_gb_s * BANDWIDTH_EFFICIENCY / per_token_gb, 1)


def _kv_geometry(card: Any) -> tuple[float, bool] | None:
    """(bytes_per_token, kv_heads_taken_from_attention) or None.

    Never infers missing layer counts or hidden size. Absent `num_kv_heads` is
    MHA, so it falls back to `num_attention_heads` and reports that it did.
    """
    arch = card.architecture
    layers = arch.num_layers
    attn = arch.num_attention_heads
    kv = arch.num_kv_heads
    hidden = arch.hidden_size

    if not layers or layers <= 0:
        return None

    from_attention = kv is None
    heads = attn if from_attention else kv
    if not heads or heads <= 0:
        return None

    # Schema has no head_dim. For MHA/GQA it is hidden_size / num_attention_heads.
    if not attn or attn <= 0 or not hidden or hidden <= 0:
        return None
    if hidden % attn != 0:
        return None
    head_dim = hidden // attn
    if head_dim <= 0:
        return None

    bytes_per_token = 2 * layers * heads * head_dim * KV_BYTES_PER_ELEMENT
    return float(bytes_per_token), from_attention


def kv_bytes_per_token(card: Any) -> float | None:
    """KV-cache bytes per token at KV_BYTES_PER_ELEMENT, or None if geometry is missing.

    Independent of weight quantisation: the cache stays at fp16 even when the
    weights are q4. GQA/MQA use `num_kv_heads`, not `num_attention_heads`.
    """
    geo = _kv_geometry(card)
    return None if geo is None else geo[0]


def predicted_max_context(card: Any, capacity_gb: float, quant: str) -> MaxContext:
    """How many tokens of context the leftover memory can hold at `quant`.

    `(device_memory - weights - working_allowance) / kv_bytes_per_token`, then
    clamped to the model's own `context_window`. The clamp, not the raw device
    figure, is what a reader can actually use.
    """
    geo = _kv_geometry(card)
    if geo is None:
        return MaxContext(
            tokens=None,
            bound_by=None,
            missing_geometry=True,
            kv_heads_from_attention=False,
        )
    kv_bpt, from_attn = geo
    params = card.architecture.total_parameters
    device_memory_bytes = capacity_gb * 1e9
    weight_bytes = weights_gb(params, quant) * 1e9
    working_allowance_bytes = device_memory_bytes * WORKING_ALLOWANCE
    available = device_memory_bytes - weight_bytes - working_allowance_bytes
    device_tokens = 0 if available <= 0 else int(available / kv_bpt)
    window = card.modalities.text.context_window
    if window and window > 0 and device_tokens >= window:
        return MaxContext(
            tokens=int(window),
            bound_by="model",
            missing_geometry=False,
            kv_heads_from_attention=from_attn,
        )
    return MaxContext(
        tokens=device_tokens,
        bound_by="device",
        missing_geometry=False,
        kv_heads_from_attention=from_attn,
    )


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
    edges = edges_with_max_context = 0

    used_active = 0
    for card in cards:
        params = card.architecture.total_parameters
        # Capacity and speed read different numbers. Every weight must be
        # resident, so `fits` uses the total; only the active experts are read
        # per token, so the decode prediction uses the active count.
        active = card.architecture.active_parameters or params
        if not card.licensing.open_weights:
            skipped_closed += 1
            continue
        if not params:
            skipped_no_params += 1
            continue
        considered += 1
        is_moe = bool(card.architecture.num_experts)
        has_active = bool(card.architecture.active_parameters)
        if has_active:
            used_active += 1
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
            ctx = predicted_max_context(card, capacity, best)
            if ctx.tokens is not None:
                edges_with_max_context += 1
            sink.edge("Model", card.identity.model_id, "FITS_ON", "Hardware", device.id, {
                "quantization": best,
                "weights_gb": round(weights_gb(params, best), 2),
                "device_memory_gb": capacity,
                "predicted_decode_tps": predicted_decode_tps(
                    device.bandwidth_gb_s, active, best),
                "decode_reads_params": active,
                "fastest_quantization": smallest,
                "fastest_weights_gb": round(weights_gb(params, smallest), 2),
                "fastest_predicted_decode_tps": predicted_decode_tps(
                    device.bandwidth_gb_s, active, smallest),
                "quantizations_that_fit": ",".join(quants),
                "max_context_at_quant": ctx.tokens,
                "max_context_bound_by": ctx.bound_by,
                "max_context_missing_geometry": ctx.missing_geometry,
                "kv_heads_from_attention_heads": ctx.kv_heads_from_attention,
                # Everything above is arithmetic, not observation. The page and
                # the export must never render it as a measurement.
                "basis": "computed",
                "assumes_working_allowance": WORKING_ALLOWANCE,
                "assumes_bandwidth_efficiency": BANDWIDTH_EFFICIENCY,
                # No card carries active_parameters, so an MoE prediction uses
                # total parameters and understates its real speed.
                # Only conservative where the active count is still unknown.
                "moe_prediction_is_conservative": is_moe and not has_active,
            })
        fitted += 1 if fitted_any else 0

    return {
        "devices": len(devices),
        "models_considered": considered,
        "models_fitting_somewhere": fitted,
        "skipped_closed_weights": skipped_closed,
        "skipped_no_parameter_count": skipped_no_params,
        "edges": edges,
        "edges_with_max_context": edges_with_max_context,
        "working_allowance": WORKING_ALLOWANCE,
        "bandwidth_efficiency": BANDWIDTH_EFFICIENCY,
        "used_active_parameters": used_active,
    }
