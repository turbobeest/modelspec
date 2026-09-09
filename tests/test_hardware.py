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
    BANDWIDTH_EFFICIENCY, QUANT_BYTES, WORKING_ALLOWANCE,
    best_quant, compute, fitting_quants, load_devices, predicted_decode_tps, weights_gb,
)
from schema.card import ModelCard  # noqa: E402
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
