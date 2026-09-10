"""The hardware layer's promises.

Everything this module produces is computed, not measured. The tests exist to
keep that distinction load-bearing, and to pin the physics: capacity decides
whether a model fits, bandwidth decides how fast it decodes, and the two are
independent.
"""

from __future__ import annotations

import functools
import glob
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.hardware import (  # noqa: E402
    BANDWIDTH_EFFICIENCY, KV_BYTES_PER_ELEMENT, QUANT_BYTES, WORKING_ALLOWANCE,
    Device, best_quant, compute, fitting_quants, kv_bytes_per_token,
    load_devices, predicted_decode_tps, predicted_max_context, weights_gb,
)
from schema.card import (  # noqa: E402
    Architecture, Identity, Licensing, Modalities, ModelCard, TextDetail,
)
from schema.graph import CollectingSink, derive_graph  # noqa: E402


@functools.lru_cache(maxsize=1)
def _devices():
    return load_devices(REPO_ROOT)


# ── the definitions ──────────────────────────────────────────────────────────

def test_every_device_declares_bandwidth() -> None:
    """A device without bandwidth cannot answer how fast a model runs."""
    assert _devices(), "no hardware definitions found"
    for device in _devices():
        assert device.bandwidth_gb_s > 0, f"{device.id} has no bandwidth"


def test_a_device_without_bandwidth_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware/bad.yaml").write_text(
        "id: bad\ndisplay_name: Bad\nvendor: x\ndevice_class: consumer\n"
        "memory:\n  capacity_gb: 16\n  type: GDDR6\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bandwidth"):
        load_devices(tmp_path)


def test_device_ids_are_unique() -> None:
    ids = [d.id for d in _devices()]
    assert len(ids) == len(set(ids))


# ── the arithmetic ───────────────────────────────────────────────────────────

def test_weights_scale_with_quantisation() -> None:
    assert weights_gb(70e9, "bf16") == pytest.approx(140.0)
    assert weights_gb(70e9, "int8") == pytest.approx(70.0)
    assert weights_gb(70e9, "q4") == pytest.approx(35.0)


def test_quantisation_preference_runs_best_quality_first() -> None:
    """`best` must mean highest quality that fits, not smallest."""
    quants = fitting_quants(7e9, 80)
    assert quants[0] == "bf16"
    assert quants[-1] == "q4"


def test_a_model_too_large_does_not_fit() -> None:
    assert best_quant(700e9, 24) is None
    assert fitting_quants(700e9, 24) == []


def test_the_working_allowance_is_actually_applied() -> None:
    """A model that exactly fills raw memory must not be reported as fitting."""
    capacity = 24.0
    params = capacity * 1e9 / QUANT_BYTES["q4"]  # exactly 24 GB of weights
    assert best_quant(params, capacity) is None
    smaller = capacity * (1 - WORKING_ALLOWANCE) * 1e9 / QUANT_BYTES["q4"]
    assert best_quant(smaller, capacity) == "q4"


# ── the physics ──────────────────────────────────────────────────────────────

def test_decode_speed_tracks_bandwidth_not_capacity() -> None:
    """The central claim of this layer: capacity gates, bandwidth paces."""
    params, quant = 13e9, "q4"
    slow_big = predicted_decode_tps(273, params, quant)     # DGX-Spark-like
    fast_small = predicted_decode_tps(1792, params, quant)  # RTX-5090-like
    assert fast_small > slow_big * 6


def test_prediction_never_exceeds_the_roofline() -> None:
    tps = predicted_decode_tps(1000, 7e9, "q4")
    theoretical = 1000 / weights_gb(7e9, "q4")
    assert tps <= theoretical
    assert tps == pytest.approx(theoretical * BANDWIDTH_EFFICIENCY, rel=0.01)


def test_a_heavier_quantisation_decodes_slower_on_the_same_device() -> None:
    assert predicted_decode_tps(800, 30e9, "q4") > predicted_decode_tps(800, 30e9, "bf16")


# ── the KV cache ─────────────────────────────────────────────────────────────

def _card(
    *,
    params: int = 8_000_000_000,
    layers: int | None = 32,
    hidden: int | None = 4096,
    attn: int | None = 32,
    kv: int | None = 8,
    context: int | None = 131_072,
    open_weights: bool = True,
    model_id: str = "test/model",
) -> ModelCard:
    return ModelCard(
        identity=Identity(model_id=model_id, display_name=model_id, provider="test"),
        architecture=Architecture(
            total_parameters=params,
            num_layers=layers,
            hidden_size=hidden,
            num_attention_heads=attn,
            num_kv_heads=kv,
        ),
        licensing=Licensing(open_weights=open_weights),
        modalities=Modalities(text=TextDetail(context_window=context)),
    )


def _gpu(capacity_gb: float = 24.0) -> Device:
    return Device(
        id="gpu24", display_name="24GB", vendor="x", device_class="consumer",
        bandwidth_gb_s=1000, capacity_options_gb=(capacity_gb,),
        precisions_native=("fp16",), unified=False,
    )


def test_gqa_is_not_charged_the_mha_cache_size() -> None:
    """num_kv_heads is the cache; using attention heads would overstate GQA."""
    gqa = _card(attn=32, kv=8)
    mha = _card(attn=32, kv=32)
    gqa_bpt = kv_bytes_per_token(gqa)
    mha_bpt = kv_bytes_per_token(mha)
    assert gqa_bpt is not None and mha_bpt is not None
    assert gqa_bpt == 2 * 32 * 8 * 128 * KV_BYTES_PER_ELEMENT
    assert mha_bpt == 2 * 32 * 32 * 128 * KV_BYTES_PER_ELEMENT
    assert gqa_bpt == mha_bpt / 4
    assert gqa_bpt < mha_bpt


def test_missing_geometry_yields_none_not_zero() -> None:
    """Null means we do not know. Zero would say the device holds no context."""
    card = _card(layers=None, hidden=None, attn=None, kv=None)
    assert kv_bytes_per_token(card) is None
    ctx = predicted_max_context(card, 24, "q4")
    assert ctx.tokens is None
    assert ctx.missing_geometry is True
    assert ctx.bound_by is None

    sink = CollectingSink()
    stats = compute(sink, [card], [_gpu()])
    assert stats["edges"] == 1
    props = sink.edges[0]["props"]
    assert props["max_context_at_quant"] is None
    assert props["max_context_at_quant"] != 0
    assert props["max_context_missing_geometry"] is True
    assert props["max_context_bound_by"] is None


def test_model_context_window_clamps_the_device_figure() -> None:
    """A 24GB card can hold far more KV than a 131k window; reporting 900k is wrong."""
    # Tiny KV so leftover memory would allow tens of millions of tokens.
    card = _card(layers=2, hidden=64, attn=1, kv=1, context=131_072)
    kv_bpt = 2 * 2 * 1 * 64 * KV_BYTES_PER_ELEMENT
    assert kv_bytes_per_token(card) == kv_bpt
    leftover = 24e9 - weights_gb(8e9, "q4") * 1e9 - 24e9 * WORKING_ALLOWANCE
    device_tokens = int(leftover / kv_bpt)
    assert device_tokens > 131_072

    ctx = predicted_max_context(card, 24, "q4")
    assert ctx.tokens == 131_072
    assert ctx.bound_by == "model"
    assert ctx.missing_geometry is False

    unclamped = _card(layers=2, hidden=64, attn=1, kv=1, context=device_tokens + 1)
    device = predicted_max_context(unclamped, 24, "q4")
    assert device.bound_by == "device"
    assert device.tokens == device_tokens


def test_head_dim_is_derived_from_hidden_size_when_absent() -> None:
    """The schema has no head_dim; hidden_size / num_attention_heads is the width."""
    card = _card(layers=32, hidden=4096, attn=32, kv=8)
    assert "head_dim" not in type(card.architecture).model_fields
    assert kv_bytes_per_token(card) == 2 * 32 * 8 * (4096 // 32) * KV_BYTES_PER_ELEMENT


def test_absent_kv_heads_fall_back_to_attention_heads() -> None:
    """Missing num_kv_heads means MHA, and the edge records that we assumed so."""
    card = _card(attn=32, kv=None)
    assert kv_bytes_per_token(card) == 2 * 32 * 32 * 128 * KV_BYTES_PER_ELEMENT
    ctx = predicted_max_context(card, 24, "q4")
    assert ctx.kv_heads_from_attention is True
    sink = CollectingSink()
    compute(sink, [card], [_gpu()])
    assert sink.edges[0]["props"]["kv_heads_from_attention_heads"] is True


def test_fits_on_carries_max_context_at_the_edge_quant() -> None:
    card = _card()
    sink = CollectingSink()
    compute(sink, [card], [_gpu()])
    props = sink.edges[0]["props"]
    expected = predicted_max_context(card, 24, props["quantization"])
    assert props["max_context_at_quant"] == expected.tokens
    assert props["max_context_bound_by"] == expected.bound_by
    assert props["max_context_missing_geometry"] is False


# ── the corpus ───────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _real():
    files = [f for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
             if not f.endswith("LICENSE.md")]
    cards = [ModelCard.from_yaml_file(f) for f in files]
    sink = derive_graph(cards)
    stats = compute(sink, cards, _devices())
    return sink, stats


def test_the_hardware_view_is_no_longer_empty() -> None:
    _, stats = _real()
    assert stats["edges"] > 0


def test_closed_weights_models_get_no_fits_on_edge() -> None:
    """Asking whether a model you cannot download "fits" is meaningless."""
    sink, stats = _real()
    assert stats["skipped_closed_weights"] > 0
    closed = {c.identity.model_id
              for c in (ModelCard.from_yaml_file(f)
                        for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"),
                                                  recursive=True))
                        if not f.endswith("LICENSE.md"))
              if not c.licensing.open_weights}
    for edge in sink.edges:
        if edge["type"] == "FITS_ON":
            assert edge["from"] not in closed


def test_every_fit_is_labelled_computed_not_measured() -> None:
    sink, _ = _real()
    fits = [e for e in sink.edges if e["type"] == "FITS_ON"]
    assert fits
    for edge in fits:
        assert edge["props"]["basis"] == "computed"
        assert "assumes_working_allowance" in edge["props"]
        assert "assumes_bandwidth_efficiency" in edge["props"]


def test_no_measured_throughput_is_invented() -> None:
    """tokens_per_sec is a measurement. Nothing here may populate it."""
    sink, _ = _real()
    for edge in sink.edges:
        if edge["type"] == "FITS_ON":
            assert "tokens_per_sec" not in edge["props"]
            assert "ttft_ms" not in edge["props"]


def test_computed_fits_on_edges_carry_max_context_or_a_geometry_flag() -> None:
    """Null + missing_geometry, or a non-negative int. Never an invented zero."""
    sink, stats = _real()
    computed = [e for e in sink.edges
                if e["type"] == "FITS_ON" and (e.get("props") or {}).get("basis") == "computed"]
    assert computed
    with_context = 0
    for edge in computed:
        props = edge["props"]
        assert "max_context_at_quant" in props
        assert "max_context_missing_geometry" in props
        if props["max_context_missing_geometry"]:
            assert props["max_context_at_quant"] is None
            assert props["max_context_bound_by"] is None
        else:
            assert isinstance(props["max_context_at_quant"], int)
            assert props["max_context_at_quant"] >= 0
            assert props["max_context_bound_by"] in ("device", "model")
            with_context += 1
    assert stats["edges_with_max_context"] == with_context
