"""MODEL-24: the Instrument redesign of the model page.

What these defend is the honesty of the page, not its pixels. A constant that
repeats down a column, a section that renders half a chain, a stat cell holding
a blank and four provenance pills restyled into one grey chip are all ways of
saying more than the data supports.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.export import Build  # noqa: E402
from pipeline.load import Catalogue, Model  # noqa: E402
from pipeline.render import (  # noqa: E402
    CSS, FONTS, competitors_section, hardware_section, lineage_section, model_page, stat_strip,
    unresearched_section,
)

BUILD = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))


def _row(name: str, device_class: str | None = None, **props: object) -> dict:
    device = {"memory_bandwidth_gb_s": 1000}
    if device_class is not None:
        device["device_class"] = device_class
    row = {"name": name, "device": device,
           "device_memory_gb": 24, "quantization": "q4", "weights_gb": 4.0,
           "predicted_decode_tps": 100.0, "fastest_predicted_decode_tps": 100.0,
           "fastest_quantization": None}
    row.update(props)
    return row


def _rel(**kwargs: object) -> SimpleNamespace:
    base = {"ancestors": [], "descendants": [], "platforms": [], "hardware": [],
            "capabilities": [], "competitors": []}
    base.update(kwargs)
    return SimpleNamespace(**base)


def _tbody(html: str) -> str:
    return html.split("<tbody>")[1].split("</tbody>")[0]


# ── hoisting constants out of the hardware table ─────────────────────────────

def test_a_quantisation_shared_by_every_row_is_stated_once_not_repeated() -> None:
    html = hardware_section(_rel(hardware=[
        _row("A", weights_gb=4.0), _row("B", weights_gb=5.0), _row("C", weights_gb=6.0)]))
    assert "q4" in html.split("<table>")[0], "the shared quantisation belongs in the lede"
    assert "q4" not in _tbody(html)
    assert "Best quality" not in html


def test_a_quantisation_that_differs_stays_a_column() -> None:
    html = hardware_section(_rel(hardware=[
        _row("A", quantization="q4"), _row("B", quantization="bf16")]))
    assert "Best quality" in html
    body = _tbody(html)
    assert "q4" in body and "bf16" in body


def test_an_all_null_constant_is_dropped_and_the_lede_stays_silent() -> None:
    html = hardware_section(_rel(hardware=[_row("A"), _row("B")]))
    assert "Fastest at" not in html
    assert "fastest quantisation that fits" not in html


# ── the lineage chain ────────────────────────────────────────────────────────

def test_the_chain_omits_the_side_with_nothing_on_it() -> None:
    ancestors_only = lineage_section(
        _rel(ancestors=[{"id": "base", "name": "Base", "relation": "finetune"}]),
        pages={"base"}, display_name="Child")
    assert "Descended from" in ancestors_only
    assert "Is the base of" not in ancestors_only
    assert "finetune of" in ancestors_only

    descendants_only = lineage_section(
        _rel(descendants=[{"id": "kid", "name": "Kid", "relation": "quantized"}]),
        pages={"kid"}, display_name="Parent")
    assert "Is the base of" in descendants_only
    assert "Descended from" not in descendants_only
    assert "quantized" in descendants_only


def test_a_model_with_no_lineage_renders_nothing() -> None:
    assert lineage_section(_rel(), display_name="Lonely") == ""


# ── the not-yet-researched footer ────────────────────────────────────────────

FULL_FRONT = {
    "architecture": {"total_parameters": 7_000_000_000},
    "release_date": "2026-01-01",
    "last_updated": "2026-02-01",
    "family": "tiny",
    "status": "active",
    "licensing": {"open_weights": False, "license_type": "proprietary"},
    "modalities": {"text": {"context_window": 128000}},
    "cost": {"input": 1.0},
    "lineage": {"training_data_cutoff": "2025-06"},
}
FULL_REL = SimpleNamespace(
    ancestors=[{"id": "base", "name": "Base"}], descendants=[], platforms=[{"id": "p"}],
    hardware=[{"id": "gpu"}], capabilities=[{"name": "tool use"}], competitors=[])


def test_the_footer_names_the_absent_facts_and_counts_the_present_ones() -> None:
    front = {"family": "tiny", "status": "active", "release_date": "2026-01-01"}
    html = unresearched_section(front, None, {"mmlu": 80.0})
    assert "4 of the 15 facts this page can show" in html
    for absent in ("Parameters", "Licence", "Context window", "Pricing",
                   "Training cutoff", "Lineage", "Capabilities",
                   "Platform availability", "Hardware fit", "Last updated"):
        assert f'<span class="gap">{absent}</span>' in html
    for present in ("Family", "Status", "Release date", "Benchmark scores"):
        assert f'<span class="gap">{present}</span>' not in html


def test_a_card_that_declares_closed_weights_has_researched_that_fact() -> None:
    """False is an answer. Only null means nobody looked."""
    html = unresearched_section(FULL_FRONT, FULL_REL, {"mmlu": 80.0})
    assert html == ""


def test_the_footer_vanishes_only_when_all_fifteen_are_present() -> None:
    thinner = {k: v for k, v in FULL_FRONT.items() if k != "cost"}
    html = unresearched_section(thinner, FULL_REL, {"mmlu": 80.0})
    assert "14 of the 15 facts this page can show" in html
    assert '<span class="gap">Pricing</span>' in html


def test_a_missing_intermediate_does_not_crash_the_footer() -> None:
    html = unresearched_section({"licensing": None, "architecture": "nonsense"}, None, {})
    assert "0 of the 15 facts this page can show" in html


# ── the stat strip ───────────────────────────────────────────────────────────

def test_the_strip_declares_as_many_columns_as_it_renders_cells() -> None:
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"),
                  {"model_type": "llm", "release_date": "2026-01-01"}, "")
    html = stat_strip(model)
    assert "grid-template-columns:repeat(2,minmax(0,1fr))" in html
    for missing in ("Parameters", "Open weights", "Evidence basis"):
        assert missing not in html


def test_a_card_with_no_scores_omits_the_evidence_cell_rather_than_saying_none() -> None:
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"), {"model_type": "llm"}, "")
    assert "Evidence basis" not in stat_strip(model)


def test_the_evidence_cell_uses_the_ranking_engine_vocabulary() -> None:
    front = {"model_type": "llm", "benchmarks": {
        "scores": {"mmlu": 80.0, "gsm8k": 70.0},
        "evidence": [{"benchmark_id": "mmlu", "score": 80.0}]}}
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"), front, "")
    assert "mixed" in stat_strip(model)


# ── grouping falls back rather than inventing a class ────────────────────────

def test_rows_group_by_device_class_when_every_row_carries_one() -> None:
    html = hardware_section(_rel(hardware=[
        _row("H100", "datacentre", id="h100"), _row("RTX", "consumer", id="rtx")]))
    body = _tbody(html)
    assert body.index("datacentre") < body.index("consumer")
    assert "1 device<" in body


def test_grouping_falls_back_when_any_row_lacks_a_class() -> None:
    for rows in ([_row("A", id="h100"), _row("B", id="mystery")],
                 [_row("A", "datacentre", id="h100"), _row("B", id="mystery")]):
        html = hardware_section(_rel(hardware=rows))
        assert "<table>" in html
        assert "grouphead" not in html


def test_rows_without_an_id_key_still_render() -> None:
    """The pipeline's own rows carry one; a caller's need not."""
    html = hardware_section(_rel(hardware=[_row("A")]))
    assert "<table>" in html and "grouphead" not in html


# ── the decode bar ───────────────────────────────────────────────────────────

def test_the_bar_is_scaled_against_the_fastest_row_in_the_whole_table() -> None:
    html = hardware_section(_rel(hardware=[
        _row("Fast", predicted_decode_tps=200.0),
        _row("Half", predicted_decode_tps=100.0)]))
    assert 'style="width:100.0%"' in html
    assert 'style="width:50.0%"' in html


def test_a_null_decode_reads_n_a_and_never_none() -> None:
    html = hardware_section(_rel(hardware=[
        _row("Fast", predicted_decode_tps=200.0, fastest_predicted_decode_tps=200.0),
        _row("Silent", predicted_decode_tps=None, fastest_predicted_decode_tps=None)]))
    assert "n/a" in html
    assert "None" not in html


def test_every_null_decode_does_not_divide_by_zero() -> None:
    html = hardware_section(_rel(hardware=[
        _row("A", predicted_decode_tps=None), _row("B", predicted_decode_tps=None)]))
    assert 'style="width:0.0%"' in html


# ── the disclosure ───────────────────────────────────────────────────────────

def test_the_tail_hides_behind_a_disclosure_without_duplicating_a_row() -> None:
    rows = [_row(f"D{i}", predicted_decode_tps=float(20 - i)) for i in range(12)]
    html = hardware_section(_rel(hardware=rows))
    assert "Show all 12 devices" in html
    assert html.index("<details") < html.index("<table>"), (
        "the general-sibling selector needs the control before the table")
    assert _tbody(html).count("D11") == 1
    assert _tbody(html).count('class="more"') == 4


def test_eight_rows_need_no_disclosure() -> None:
    rows = [_row(f"D{i}", predicted_decode_tps=float(20 - i)) for i in range(8)]
    html = hardware_section(_rel(hardware=rows))
    assert "<details" not in html
    assert 'class="more"' not in html


def test_a_group_starting_past_the_cutoff_hides_its_header_too() -> None:
    rows = [_row(f"D{i}", "datacentre" if i < 9 else "edge", id=f"d{i}",
                 predicted_decode_tps=float(20 - i))
            for i in range(11)]
    html = hardware_section(_rel(hardware=rows))
    edge_header = [line for line in _tbody(html).split("<tr") if "edge" in line][0]
    assert 'class="more"' in edge_header


# ── the four provenance pills ────────────────────────────────────────────────

PILL_MODIFIERS = ("active", "unverified", "alias", "unassessed")
_TOKENS = dict(re.findall(r"--([a-z]+):(#[0-9a-fA-F]{3,8})", CSS))


def _rule(selector: str) -> str:
    match = re.search(re.escape(selector) + r"\{([^}]*)\}", CSS)
    assert match, f"{selector} is not declared"
    return match.group(1)


def _resolve(value: str) -> str:
    var = re.fullmatch(r"var\(--([a-z]+)\)", value.strip())
    return _TOKENS[var.group(1)].lower() if var else value.strip().lower()


def test_each_provenance_pill_declares_its_own_colour() -> None:
    colours = []
    for modifier in PILL_MODIFIERS:
        declaration = re.search(r"(?:^|;)color:([^;]+)", _rule(f".pill.{modifier}"))
        assert declaration, f".pill.{modifier} declares no colour"
        colours.append(_resolve(declaration.group(1)))
    assert len(set(colours)) == 4, f"the four pills collapsed to {colours}"


def test_each_provenance_pill_is_told_apart_without_colour() -> None:
    """Hue alone fails in greyscale and for common colour-vision deficiencies."""
    glyphs = []
    for modifier in PILL_MODIFIERS:
        body = _rule(f".pill.{modifier}")
        style = re.search(r"border:[^;]*\b(solid|dashed|dotted|double)\b", body)
        glyph = re.search(r'content:"([^"]+)"', _rule(f".pill.{modifier}::before"))
        assert style or glyph, f".pill.{modifier} has no non-hue channel"
        assert glyph, f".pill.{modifier} declares no leading glyph"
        glyphs.append(glyph.group(1))
    assert len(set(glyphs)) == 4, f"the leading glyphs collapsed to {glyphs}"


def test_verified_is_green_and_unverified_legacy_is_amber() -> None:
    """The same page shows both labels, and they must never be confusable."""
    front = {"model_type": "llm", "benchmarks": {
        "scores": {"mmlu": 80.0}, "evidence": [{"benchmark_id": "mmlu"}]}}
    verified = Model("a/v", Path("/r/models/a/v.md"), front, "")
    assert '<div class="val basis-verified">verified</div>' in stat_strip(verified)
    legacy = Model("a/l", Path("/r/models/a/l.md"),
                   {"model_type": "llm", "benchmarks": {"scores": {"mmlu": 80.0}}}, "")
    assert ('<div class="val long basis-unverified-legacy">unverified-legacy</div>'
            in stat_strip(legacy))
    assert _resolve(_rule(".basis-verified").split(":", 1)[1]) == _TOKENS["good"].lower()
    assert _resolve(_rule(".basis-unverified-legacy").split(":", 1)[1]) == _TOKENS["warn"].lower()
    assert _TOKENS["good"].lower() != _TOKENS["warn"].lower()


def test_the_accent_is_one_token_and_benchgraph_reassigns_it() -> None:
    declarations = re.findall(r"--accent:(#[0-9a-fA-F]{6})", CSS)
    assert len(declarations) == 2, "accent is declared once per site, nowhere else"
    assert '[data-site="benchgraph"]' in CSS
    body = CSS.split("[data-site=", 1)[1]
    assert "#f5b342" not in body.split("}", 1)[1], "no literal amber outside the tokens"


def test_the_sheet_has_no_rounded_corners() -> None:
    assert "border-radius" not in CSS


# ── the page as a whole ──────────────────────────────────────────────────────

def test_a_model_page_keeps_the_gutter_outside_nav_and_footer() -> None:
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"),
                  {"model_type": "llm", "status": "active"}, "")
    html = model_page(model, BUILD, {}, Catalogue(as_of=date(2026, 9, 15)))
    assert '<html lang="en" data-site="modelspec">' in html
    nav, rest = html.split('<main class="page">')
    assert "<nav>" in nav
    assert "<footer>" in rest.split("</main>")[1]


def test_capabilities_render_as_header_chips_not_a_section() -> None:
    rel = _rel(capabilities=[{"name": "tool use", "tier": "T3"}])
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"), {"model_type": "llm"}, "")
    html = model_page(model, BUILD, {}, Catalogue(as_of=date(2026, 9, 15)), rel)
    assert "<h2>Capabilities</h2>" not in html
    assert '<span class="pill">tool use &middot; T3</span>' in html
    assert html.index('class="chips"') < html.index('class="stats"')


# ── Self-hosted Archivo (MODEL-24: "no runtime CDN dependency beyond the fonts
#    already loaded"; MODEL-19: "no runtime dependency on a third-party CDN") ──

def test_archivo_is_not_requested_from_a_cdn() -> None:
    assert "Archivo" not in FONTS
    assert "fonts.googleapis.com" in FONTS  # JetBrains Mono was already loaded


def test_archivo_faces_are_declared_against_repo_paths() -> None:
    assert "/fonts/archivo-latin.woff2" in CSS
    assert "/fonts/archivo-latin-ext.woff2" in CSS
    assert CSS.count("@font-face") == 2


def test_archivo_is_preloaded_so_the_heading_face_is_not_a_late_swap() -> None:
    assert 'rel="preload"' in FONTS
    assert '/fonts/archivo-latin.woff2' in FONTS


def test_the_font_files_and_their_licence_ship_in_the_repo() -> None:
    fonts = Path(__file__).resolve().parent.parent / "site" / "fonts"
    assert (fonts / "archivo-latin.woff2").is_file()
    assert (fonts / "archivo-latin-ext.woff2").is_file()
    # The OFL requires the licence to travel with the font.
    assert "SIL Open Font License" in (fonts / "Archivo-OFL.txt").read_text(encoding="utf-8")


# ── competitors on a thin card ───────────────────────────────────────────────

def _competitor(name: str, score: object) -> dict:
    return {"id": name.lower(), "name": name, "overlap_score": score}


def test_zero_overlap_draws_no_bar_and_drops_the_scoring_clause() -> None:
    html = competitors_section(_rel(competitors=[_competitor("A", 0.0), _competitor("B", None)]))
    assert 'class="bar' not in html
    assert "the score is the overlap" not in html
    assert ">A<" in html and ">B<" in html


def test_a_positive_score_gets_a_bar_and_a_zero_beside_it_does_not() -> None:
    html = competitors_section(_rel(competitors=[_competitor("A", 0.5), _competitor("B", 0)]))
    assert html.count('class="bar') == 1
    assert 'style="width:50.0%"' in html
    assert "the score is the overlap" in html
