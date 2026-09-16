"""The hardware layer's promises.

Everything this module produces is computed, not measured. The tests exist to
keep that distinction load-bearing, and to pin the physics: capacity decides
whether a model fits, bandwidth decides how fast it decodes, and the two are
independent.
"""

from __future__ import annotations

import functools
import glob
import json
import re
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.graph import CLOUDFLARE_PAGES_MAX_FILE_BYTES, write  # noqa: E402
from pipeline.hardware import (  # noqa: E402
    BANDWIDTH_EFFICIENCY, KV_BYTES_PER_ELEMENT, QUANT_BYTES, WORKING_ALLOWANCE,
    Device, best_quant, compute, device_classes, fitting_quants,
    kv_bytes_per_token, load_devices, predicted_decode_tps,
    predicted_max_context, weights_gb,
)
from pipeline.render import format_weight_size, hardware_section  # noqa: E402
from schema.card import (  # noqa: E402
    Architecture, Identity, Licensing, Modalities, ModelCard, TextDetail,
)
from schema.enums import DeviceClass, ModelType  # noqa: E402
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


def _yaml_devices() -> list[tuple[Path, dict]]:
    rows = []
    for path in sorted((REPO_ROOT / "hardware").glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows.append((path, raw))
    return rows


def test_every_device_has_sourced_dated_capacity_and_bandwidth() -> None:
    """MODEL-25: no published row without a URL, a check date, capacity and bandwidth."""
    rows = _yaml_devices()
    assert rows, "no hardware definitions found"
    missing = []
    for path, raw in rows:
        mem = raw.get("memory") or {}
        sources = raw.get("sources") or []
        urls = [s for s in sources if isinstance(s, str) and s.startswith("https://")]
        verified = raw.get("verified_at")
        problems = []
        if not urls:
            problems.append("no https source")
        if isinstance(verified, date):
            verified = verified.isoformat()
        if not isinstance(verified, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified):
            problems.append(f"verified_at={verified!r}")
        if mem.get("capacity_gb") is None and not mem.get("capacity_options_gb"):
            problems.append("no capacity")
        if not mem.get("bandwidth_gb_s"):
            problems.append("no bandwidth")
        if not mem.get("bandwidth_derivation"):
            problems.append("no bandwidth_derivation")
        if problems:
            missing.append(f"{path.name}: {', '.join(problems)}")
    assert missing == []


def test_every_device_has_the_fields_fit_reads() -> None:
    """load_devices needs id, display_name, vendor, device_class, bandwidth, capacity."""
    for path, raw in _yaml_devices():
        mem = raw.get("memory") or {}
        assert raw.get("id") == path.stem, path.name
        assert raw.get("display_name"), path.name
        assert raw.get("vendor"), path.name
        assert raw.get("device_class"), path.name
        assert mem.get("bandwidth_gb_s"), path.name
        assert mem.get("capacity_gb") is not None or mem.get("capacity_options_gb"), path.name


def test_capacity_options_are_the_chip_not_a_soldered_sku() -> None:
    """Apple-style option lists live on one chip id; capacity_gb is the published max."""
    for path, raw in _yaml_devices():
        mem = raw.get("memory") or {}
        options = mem.get("capacity_options_gb")
        if not options:
            continue
        assert raw["id"] == path.stem
        assert not path.stem.endswith(tuple(f"_{int(c)}gb" for c in options)), path.name
        assert mem["capacity_gb"] == max(options), path.name


# ── GiB stored in a GB field ─────────────────────────────────────────────────

#: 1 GiB = 1024³ bytes; 1 GB = 1000³ bytes.
GIB_TO_GB = 1024 ** 3 / 1000 ** 3
GIB_ROUND_DECIMALS = 1

_GIB_QTY = re.compile(
    r"(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>GiBps|GiB/s|GiB)\b",
    re.IGNORECASE,
)
#: Host DRAM / VM RAM on TPU pages is not chip HBM; do not treat it as capacity_gb.
_NOT_CHIP_HBM = re.compile(
    r"DRAM|per host|per VM|host RAM|RAM \(GB\)",
    re.IGNORECASE,
)


def _converted_gb(gib: float) -> float:
    return round(gib * GIB_TO_GB, GIB_ROUND_DECIMALS)


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= 0.05


_AMBIGUOUS_UNIT = re.compile(r"unit is ambiguous", re.IGNORECASE)


def _notes_and_derivation(raw: dict) -> list[str]:
    mem = raw.get("memory") or {}
    blobs: list[str] = []
    deriv = mem.get("bandwidth_derivation")
    if isinstance(deriv, str):
        blobs.append(deriv)
    notes = raw.get("notes")
    if isinstance(notes, str):
        blobs.append(notes)
    return blobs


def _unit_is_ambiguous(raw: dict) -> bool:
    return any(_AMBIGUOUS_UNIT.search(blob) for blob in _notes_and_derivation(raw))


def _stored_bandwidth_and_capacities(raw: dict) -> tuple[float | None, list[float]]:
    mem = raw.get("memory") or {}
    stored_bw = mem.get("bandwidth_gb_s")
    stored_caps: list[float] = []
    if mem.get("capacity_gb") is not None:
        stored_caps.append(float(mem["capacity_gb"]))
    stored_caps.extend(float(c) for c in (mem.get("capacity_options_gb") or []))
    return (None if stored_bw is None else float(stored_bw), stored_caps)


def unconverted_gib_fields(raw: dict) -> list[str]:
    """Problems in a parsed hardware record: GiB mentioned, GB field still holds the GiB number.

    Reads `notes` and `memory.bandwidth_derivation` from the YAML mapping. Does not
    grep the file as text. Records that say the unit is ambiguous are exempt —
    those must keep the unconverted figure (see `converted_despite_ambiguous_unit`).
    """
    if _unit_is_ambiguous(raw):
        return []

    stored_bw, stored_caps = _stored_bandwidth_and_capacities(raw)
    problems: list[str] = []
    for blob in _notes_and_derivation(raw):
        if re.search(r"without converting", blob, re.IGNORECASE) and _GIB_QTY.search(blob):
            problems.append("notes/derivation still say the GiB figure was stored without conversion")
        for match in _GIB_QTY.finditer(blob):
            n = float(match.group("num"))
            unit = match.group("unit").lower()
            converted = _converted_gb(n)
            window_start = max(0, match.start() - 80)
            window = blob[window_start:match.end()]
            if unit in ("gibps", "gib/s"):
                if stored_bw is None:
                    continue
                if _close(stored_bw, n) and not _close(stored_bw, converted):
                    problems.append(
                        f"bandwidth_gb_s={stored_bw} still holds {n:g} {match.group('unit')} "
                        f"(converted {converted})"
                    )
                continue
            if _NOT_CHIP_HBM.search(window):
                continue
            if any(_close(c, n) for c in stored_caps) and not any(
                _close(c, converted) for c in stored_caps
            ):
                problems.append(
                    f"capacity still holds {n:g} GiB unconverted (converted {converted})"
                )
    return problems


def converted_despite_ambiguous_unit(raw: dict) -> list[str]:
    """Problems: notes/derivation say the unit is ambiguous, but a GB field holds the converted number.

    An ambiguous source must store the unconverted (conservative) figure. Reads
    `notes` and `memory.bandwidth_derivation` from the YAML mapping, not the file as text.
    """
    if not _unit_is_ambiguous(raw):
        return []

    stored_bw, stored_caps = _stored_bandwidth_and_capacities(raw)
    problems: list[str] = []
    for blob in _notes_and_derivation(raw):
        for match in _GIB_QTY.finditer(blob):
            n = float(match.group("num"))
            unit = match.group("unit").lower()
            converted = _converted_gb(n)
            window_start = max(0, match.start() - 80)
            window = blob[window_start:match.end()]
            if unit in ("gibps", "gib/s"):
                if stored_bw is None:
                    continue
                if not _close(stored_bw, n):
                    problems.append(
                        f"unit is ambiguous but bandwidth_gb_s={stored_bw} is not the "
                        f"unconverted {n:g} {match.group('unit')} (converted would be {converted})"
                    )
                continue
            if _NOT_CHIP_HBM.search(window):
                continue
            if not any(_close(c, n) for c in stored_caps):
                problems.append(
                    f"unit is ambiguous but capacity is not the unconverted {n:g} GiB "
                    f"(converted would be {converted})"
                )
    return problems


def test_unconverted_gib_in_derivation_is_caught() -> None:
    raw = {
        "memory": {
            "capacity_gb": 16,
            "bandwidth_gb_s": 800,
            "bandwidth_derivation": "800 GiBps stored without conversion",
        },
        "notes": "HBM bandwidth per chip 800 GiBps",
    }
    assert unconverted_gib_fields(raw)


def test_converted_gib_in_derivation_passes() -> None:
    raw = {
        "memory": {
            "capacity_gb": 16,
            "bandwidth_gb_s": 859.0,
            "bandwidth_derivation": "800 GiBps × 1.073741824 = 859.0 GB/s",
        },
        "notes": "HBM bandwidth per chip 800 GiBps; DRAM per host 512 GiB",
    }
    assert unconverted_gib_fields(raw) == []


def test_hardware_yaml_converts_gib_figures_mentioned_in_notes() -> None:
    """MODEL-41: a GiB figure in notes/derivation must not sit unconverted in a GB field."""
    failures = []
    for path, raw in _yaml_devices():
        problems = unconverted_gib_fields(raw)
        if problems:
            failures.append(f"{path.name}: {'; '.join(problems)}")
    assert failures == []


def test_ambiguous_unit_stores_unconverted() -> None:
    raw = {
        "memory": {
            "capacity_gb": 192,
            "bandwidth_gb_s": 7380,
            "bandwidth_derivation": (
                "HBM capacity unit is ambiguous (192 GiB table vs 192 GB body); "
                "192 stored unconverted"
            ),
        },
        "notes": "The unit is ambiguous. Table header 192 GiB, body 192 GB.",
    }
    assert unconverted_gib_fields(raw) == []
    assert converted_despite_ambiguous_unit(raw) == []


def test_ambiguous_unit_fails_if_converted() -> None:
    raw = {
        "memory": {
            "capacity_gb": 206.2,
            "bandwidth_gb_s": 7380,
            "bandwidth_derivation": (
                "192 GiB × 1.073741824 = 206.2 GB; the unit is ambiguous"
            ),
        },
        "notes": "The unit is ambiguous (192 GiB table vs 192 GB body).",
    }
    assert converted_despite_ambiguous_unit(raw)


def test_hardware_yaml_ambiguous_units_store_unconverted() -> None:
    """MODEL-41: an ambiguous unit must keep the unconverted conservative figure."""
    failures = []
    for path, raw in _yaml_devices():
        problems = converted_despite_ambiguous_unit(raw)
        if problems:
            failures.append(f"{path.name}: {'; '.join(problems)}")
    assert failures == []


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
    # A token-generating type by default: most of this module's tests are
    # about the KV-cache/context arithmetic, not about MODEL-53's type gate,
    # and should keep getting a decode prediction unless a test asks for
    # something else.
    model_type: ModelType | None = ModelType.LLM_CHAT,
) -> ModelCard:
    return ModelCard(
        identity=Identity(model_id=model_id, display_name=model_id, provider="test",
                          model_type=model_type),
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


def test_published_hardware_view_fits_cloudflare_pages(tmp_path: Path) -> None:
    """Wave-3 SKUs made the fat FITS_ON dump larger than Pages will host."""
    sink, stats = _real()
    assert stats["edges"] > 0
    write(tmp_path, sink, {"commit": "test"})
    path = tmp_path / "views" / "hardware.json"
    size = path.stat().st_size
    assert size < CLOUDFLARE_PAGES_MAX_FILE_BYTES, (
        f"hardware.json is {size} bytes; Pages refuses files over "
        f"{CLOUDFLARE_PAGES_MAX_FILE_BYTES}"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["counts"]["edges"] == stats["edges"]
    assert payload["edge_properties"] is False
    hardware_nodes = [n for n in payload["nodes"] if n["label"] == "Hardware"]
    eligible = {d.id for d in _devices() if d.single_device_fit}
    assert {n["id"] for n in hardware_nodes} == eligible
    assert "cerebras_wse3" not in eligible


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


# ── single-device fit flag (MODEL-47) ────────────────────────────────────────

_TINY_PARAMS = 616_032  # granite-timeseries-patchtst; bf16 is 0.001232064 GB


def test_single_device_fit_false_without_reason_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware/wafer.yaml").write_text(
        "id: wafer\ndisplay_name: Wafer\nvendor: x\ndevice_class: datacentre\n"
        "single_device_fit: false\n"
        "memory:\n  capacity_gb: 44\n  bandwidth_gb_s: 21000000\n  type: SRAM\n",
        encoding="utf-8")
    with pytest.raises(ValueError, match="single_device_fit_reason"):
        load_devices(tmp_path)


def test_single_device_fit_false_loads_with_reason(tmp_path: Path) -> None:
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware/wafer.yaml").write_text(
        "id: wafer\ndisplay_name: Wafer\nvendor: x\ndevice_class: datacentre\n"
        "single_device_fit: false\n"
        "single_device_fit_reason: working SRAM, not a frame buffer\n"
        "memory:\n  capacity_gb: 44\n  bandwidth_gb_s: 21000000\n  type: SRAM\n",
        encoding="utf-8")
    devices = load_devices(tmp_path)
    assert len(devices) == 1
    assert devices[0].single_device_fit is False
    assert "working SRAM" in (devices[0].single_device_fit_reason or "")


def test_omitted_single_device_fit_defaults_to_true(tmp_path: Path) -> None:
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware/gpu.yaml").write_text(
        "id: gpu\ndisplay_name: GPU\nvendor: x\ndevice_class: consumer\n"
        "memory:\n  capacity_gb: 24\n  bandwidth_gb_s: 1000\n  type: GDDR6\n",
        encoding="utf-8")
    devices = load_devices(tmp_path)
    assert devices[0].single_device_fit is True
    assert devices[0].single_device_fit_reason is None


def test_single_device_fit_false_suppresses_edges_and_predictions() -> None:
    flagged = Device(
        id="wafer", display_name="Wafer", vendor="x", device_class="datacentre",
        bandwidth_gb_s=21_000_000, capacity_options_gb=(44.0,),
        precisions_native=("bf16",), unified=False,
        single_device_fit=False,
        single_device_fit_reason="working SRAM, not a frame buffer",
    )
    sink = CollectingSink()
    stats = compute(sink, [_card(params=_TINY_PARAMS)], [flagged, _gpu()])
    assert stats["skipped_single_device_fit"] == 1
    assert stats["edges"] == 1
    fits = [e for e in sink.edges if e["type"] == "FITS_ON"]
    assert {e["to"] for e in fits} == {"gpu24"}
    assert not any(e["to"] == "wafer" for e in fits)
    for edge in fits:
        assert "predicted_decode_tps" in edge["props"]
        assert edge["to"] != "wafer"
    assert ("Hardware", "wafer") in sink.nodes
    assert ("Hardware", "gpu24") in sink.nodes


def test_yaml_false_flag_always_carries_a_reason() -> None:
    for path, raw in _yaml_devices():
        if raw.get("single_device_fit") is False:
            reason = raw.get("single_device_fit_reason")
            assert isinstance(reason, str) and reason.strip(), path.name


def test_cerebras_wse3_is_flagged_and_emits_no_fits_on() -> None:
    wse = next(d for d in _devices() if d.id == "cerebras_wse3")
    assert wse.single_device_fit is False
    assert wse.single_device_fit_reason
    sink, stats = _real()
    assert stats["skipped_single_device_fit"] >= 1
    for edge in sink.edges:
        if edge["type"] == "FITS_ON":
            assert edge["to"] != "cerebras_wse3"
            assert "predicted_decode_tps" not in edge or edge["to"] != "cerebras_wse3"


def test_sub_10m_parameter_weights_stay_unrounded_on_the_edge() -> None:
    stored = weights_gb(_TINY_PARAMS, "bf16")
    assert stored < 0.01
    assert round(stored, 2) == 0.0
    sink = CollectingSink()
    compute(sink, [_card(params=_TINY_PARAMS)], [_gpu()])
    gb = sink.edges[0]["props"]["weights_gb"]
    assert gb == pytest.approx(stored)
    assert gb != 0.0
    # Decode still uses the unrounded size, not a rounded-to-zero GB figure.
    assert sink.edges[0]["props"]["predicted_decode_tps"] > 0


def test_sub_10m_parameter_card_never_renders_zero_point_zero_gb() -> None:
    from types import SimpleNamespace

    stored = weights_gb(_TINY_PARAMS, "bf16")
    html = hardware_section(SimpleNamespace(hardware=[{
        "name": "24GB",
        "device": {"memory_bandwidth_gb_s": 1000},
        "device_memory_gb": 24,
        "quantization": "bf16",
        "weights_gb": stored,
        "predicted_decode_tps": 1.0,
        "fastest_predicted_decode_tps": 1.0,
        "fastest_quantization": "q4",
    }]))
    assert "0.0 GB" not in html
    assert "0.00 GB" not in html
    assert "MB" in html
    assert format_weight_size(stored) == "1.23 MB"
    assert format_weight_size(4.0) == "4.00 GB"
    assert format_weight_size(round(stored, 2)) != "0.0 GB"


def test_ordinary_gb_weights_render_to_two_decimals() -> None:
    """Unrounded storage must not print 3.620866048 GB on an ordinary model page."""
    from types import SimpleNamespace

    raw = 3.620866048
    assert format_weight_size(raw) == "3.62 GB"
    assert format_weight_size(16.060522496) == "16.06 GB"
    html = hardware_section(SimpleNamespace(hardware=[{
        "name": "24GB",
        "device": {"memory_bandwidth_gb_s": 1000},
        "device_memory_gb": 24,
        "quantization": "bf16",
        "weights_gb": raw,
        "predicted_decode_tps": 1.0,
        "fastest_predicted_decode_tps": 1.0,
        "fastest_quantization": "q4",
    }]))
    assert "3.620866048 GB" not in html
    assert "3.62 GB" in html


# ── non-token model types get capacity, not decode speed (MODEL-53) ─────────

def test_non_token_type_fits_but_gets_no_decode_prediction() -> None:
    """A vision encoder's weights fit in memory; it does not decode tokens."""
    card = _card(model_type=ModelType.VISION_ENCODER)
    sink = CollectingSink()
    stats = compute(sink, [card], [_gpu()])
    assert stats["edges"] == 1
    assert stats["decode_predictions_omitted"] == 1
    props = sink.edges[0]["props"]
    assert props["quantization"]  # capacity fit still answered
    assert props["weights_gb"] > 0
    assert props["predicted_decode_tps"] is None
    assert props["fastest_predicted_decode_tps"] is None
    assert props["decode_reads_params"] is None
    assert props["moe_prediction_is_conservative"] is False


def test_no_model_type_is_treated_as_non_token() -> None:
    """Absence is not a guess that a card chats. No type -> no decode figure."""
    card = _card(model_type=None)
    sink = CollectingSink()
    stats = compute(sink, [card], [_gpu()])
    assert stats["decode_predictions_omitted"] == 1
    assert sink.edges[0]["props"]["predicted_decode_tps"] is None


def test_llm_types_are_unaffected_by_the_non_token_gate() -> None:
    card = _card(model_type=ModelType.LLM_CHAT)
    sink = CollectingSink()
    stats = compute(sink, [card], [_gpu()])
    assert stats["decode_predictions_omitted"] == 0
    props = sink.edges[0]["props"]
    assert props["predicted_decode_tps"] is not None
    assert props["predicted_decode_tps"] > 0


def test_real_corpus_omits_decode_only_for_non_token_types() -> None:
    """Every FITS_ON edge with a null decode prediction traces to a non-token type."""
    from pipeline.hardware import TOKEN_GENERATING_MODEL_TYPES
    sink, stats = _real()
    cards_by_id = {
        c.identity.model_id: c
        for c in (ModelCard.from_yaml_file(f)
                  for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
                  if not f.endswith("LICENSE.md"))
    }
    omitted = 0
    for edge in sink.edges:
        if edge["type"] != "FITS_ON":
            continue
        card = cards_by_id[edge["from"]]
        if edge["props"]["predicted_decode_tps"] is None:
            omitted += 1
            assert card.identity.model_type not in TOKEN_GENERATING_MODEL_TYPES
        else:
            assert card.identity.model_type in TOKEN_GENERATING_MODEL_TYPES
    assert omitted == stats["decode_predictions_omitted"]
    assert omitted > 0, "expected at least the retyped MODEL-53 cards to omit decode"


def test_null_decode_renders_as_na_not_blank_or_zero() -> None:
    """A non-token model's row must say n/a, never an empty cell or 0."""
    from types import SimpleNamespace

    html = hardware_section(SimpleNamespace(hardware=[{
        "name": "24GB",
        "device": {"memory_bandwidth_gb_s": 1000},
        "device_memory_gb": 24,
        "quantization": "bf16",
        "weights_gb": 1.0,
        "predicted_decode_tps": None,
        "fastest_predicted_decode_tps": None,
        "fastest_quantization": "q4",
    }]))
    assert "n/a" in html
    assert ">~None<" not in html
    assert "None" not in html
    assert ">0<" not in html


def test_sub_mb_weight_never_renders_as_zero_mb() -> None:
    """A non-zero stored size below 1 MB must still print a non-zero MB figure."""
    tiny = 4e-7  # 0.0004 MB
    text = format_weight_size(tiny)
    assert text != "0 MB"
    assert "MB" in text
    assert text == "0.000400 MB"
    assert format_weight_size(0) == "0 MB"
    assert format_weight_size(0.616032) == "616 MB"
    assert format_weight_size(0.009996) == "10.0 MB"
    assert format_weight_size(None) == ""


# ── device class (MODEL-76) ──────────────────────────────────────────────────

def test_a_device_class_outside_the_vocabulary_is_rejected(tmp_path: Path) -> None:
    """`datacenter` is not a near miss; it is a class no query would find."""
    (tmp_path / "hardware").mkdir()
    (tmp_path / "hardware/bad.yaml").write_text(
        "id: bad\ndisplay_name: Bad\nvendor: x\ndevice_class: datacenter\n"
        "memory:\n  capacity_gb: 80\n  bandwidth_gb_s: 3350\n", encoding="utf-8")
    with pytest.raises(ValueError, match="device_class"):
        load_devices(tmp_path)


def test_every_device_record_declares_a_known_class() -> None:
    assert _devices()
    known = {c.value for c in DeviceClass}
    for device in _devices():
        assert device.device_class in known, f"{device.id}: {device.device_class}"


def test_device_classes_maps_every_device() -> None:
    mapping = device_classes(_devices())
    assert mapping == {d.id: d.device_class for d in _devices()}
    assert set(mapping.values()) <= {c.value for c in DeviceClass}


def test_every_published_hardware_node_carries_a_known_class(tmp_path: Path) -> None:
    """The acceptance for MODEL-76, wired exactly as `pipeline.build` wires it.

    A Hardware node with no class is invisible to "which models fit datacentre
    hardware", so a card profile keyed on an id that names no device record
    must fail here and be given one, not shipped classless.
    """
    files = [f for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
             if not f.endswith("LICENSE.md")]
    cards = [ModelCard.from_yaml_file(f) for f in files]
    devices = _devices()
    sink = derive_graph(cards, device_classes(devices))
    compute(sink, cards, devices)

    write(tmp_path, sink, {"commit": "test"})
    nodes = json.loads((tmp_path / "nodes.json").read_text(encoding="utf-8"))["nodes"]
    hardware_nodes = [n for n in nodes if n["label"] == "Hardware"]
    assert len(hardware_nodes) == len(devices)
    known = {c.value for c in DeviceClass}
    unclassed = [n["id"] for n in hardware_nodes if n.get("device_class") not in known]
    assert unclassed == [], f"Hardware nodes with no device class: {unclassed}"
    # Every class in the vocabulary is represented, so a grouped view is not
    # quietly one bucket.
    assert {n["device_class"] for n in hardware_nodes} == known
