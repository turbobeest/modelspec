"""MODEL-195 build-rendered social cards."""

from __future__ import annotations

import os
import struct
import html
import re
from dataclasses import replace
from pathlib import Path

import pytest

from pipeline import brand, landing, social_cards

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def card_data() -> landing.LandingData:
    models = (
        landing.PlotModel("leader", "Leader", .9, 9, 8, 10, True),
        landing.PlotModel("tie", "Tie", .3, 8.8, 8.1, 9.5, True),
        landing.PlotModel("cheap", "Cheap", .1, 8.5, 8, 9, True),
        landing.PlotModel("other", "Other", .5, 5, 4, 6, False),
    )
    return landing.LandingData(
        as_of="2026-09-28",
        benchmark_count=7,
        task_input_tokens=12_000,
        task_output_tokens=3_000,
        monthly_tasks=10_000,
        models=models,
        leader_id="leader",
        cheapest_id="cheap",
        ratio=9.0,
        leader_monthly=9_000,
        cheapest_monthly=1_000,
        monthly_gap=8_000,
        routes=(),
        template_count=0,
        axes=landing._plot_axes(list(models)),
    )


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def _assert_clean_layout(report: dict[str, object]) -> None:
    frame = report["frame"]
    blocks = report["blocks"]
    for block in blocks:
        assert block["left"] >= frame["left"], block
        assert block["top"] >= frame["top"], block
        assert block["right"] <= frame["right"], block
        assert block["bottom"] <= frame["bottom"], block
    for index, first in enumerate(blocks):
        for second in blocks[index + 1:]:
            horizontal = min(first["right"], second["right"]) - max(first["left"], second["left"])
            vertical = min(first["bottom"], second["bottom"]) - max(first["top"], second["top"])
            assert horizontal <= 0 or vertical <= 0, (first, second)
    for element in report["text"]:
        assert element["scrollWidth"] <= element["clientWidth"], element
        assert element["scrollHeight"] <= element["clientHeight"], element


def _boxes_intersect(first: dict[str, float], second: dict[str, float]) -> bool:
    return (
        min(first["right"], second["right"]) > max(first["left"], second["left"])
        and min(first["bottom"], second["bottom"]) > max(first["top"], second["top"])
    )


def _assert_landing_plot_geometry(report: dict[str, object]) -> None:
    details = report["details"]
    plot = details["plot"]
    axis = details["yAxis"]
    axis_label = details["yAxisLabel"]
    point = details["cheapestPoint"]
    callout = details["cheapestCallout"]
    assert all(item is not None for item in (plot, axis, axis_label, point, callout))
    assert not _boxes_intersect(axis, axis_label), (axis, axis_label)
    assert callout["left"] >= plot["left"], (callout, plot)
    assert callout["top"] >= plot["top"], (callout, plot)
    assert callout["right"] <= plot["right"], (callout, plot)
    assert callout["bottom"] <= plot["bottom"], (callout, plot)
    horizontal_gap = max(callout["left"] - point["right"], point["left"] - callout["right"], 0)
    vertical_gap = max(callout["top"] - point["bottom"], point["top"] - callout["bottom"], 0)
    assert (horizontal_gap ** 2 + vertical_gap ** 2) ** .5 <= 24, (point, callout)


def test_landing_card_html_uses_exactly_the_page_figures(card_data: landing.LandingData) -> None:
    page = landing.render(card_data, variant="live")
    card = social_cards.landing_card(card_data)
    card_html = social_cards.render_card_html(card)
    tie_line = social_cards.landing_tie_line(card_data)

    assert tie_line in page
    card_text = html.unescape(re.sub(r"<[^>]+>", "", card_html))
    assert tie_line in card_text
    assert "The evidence can't tell 2 models apart from the top one." in card_text
    assert "The cheapest costs 9.0× less." in card_text


def test_each_page_points_at_its_card_with_dimensions_and_alt(
    card_data: landing.LandingData,
) -> None:
    landing_page = landing.render(card_data, variant="live")
    landing_card = social_cards.landing_card(card_data)
    for expected in (
        f'https://modelspec.dev/{landing_card.filename}',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{landing_card.alt}">',
        f'<meta name="twitter:image" content="https://modelspec.dev/{landing_card.filename}">',
    ):
        assert expected in landing_page

    decide = (ROOT / "web" / "decide.html").read_text(encoding="utf-8")
    assert "https://modelspec.dev/og-card-decide.png" in decide
    assert 'property="og:image:width" content="1200"' in decide
    assert 'property="og:image:height" content="630"' in decide
    assert 'property="og:image:alt" content="ModelSpec Decide:' in decide
    assert 'name="twitter:image" content="https://modelspec.dev/og-card-decide.png"' in decide


def test_other_pages_keep_the_fallback_card() -> None:
    meta = brand.social_meta("Another page", path="/another/")
    assert 'content="https://modelspec.dev/og-card.png"' in meta
    assert 'content="https://modelspec.dev/another/"' in meta


def test_renderer_writes_both_cards_at_the_contract_size(
    tmp_path: Path, card_data: landing.LandingData,
) -> None:
    if not (ROOT / "web" / "node_modules" / "playwright").is_dir():
        if os.environ.get("CI"):
            pytest.fail("social card rendering requires npm ci in web/")
        pytest.skip("social card rendering requires npm ci in web/")
    try:
        cards = social_cards.render(tmp_path, card_data)
    except Exception as error:
        if os.environ.get("CI"):
            raise
        pytest.skip(f"Chromium is unavailable: {error}")
    assert {card.filename for card in cards} == {
        social_cards.LANDING_IMAGE,
        social_cards.DECIDE_IMAGE,
    }
    for card in cards:
        assert (tmp_path / card.filename).is_file()
        assert _png_size(tmp_path / card.filename) == (1200, 630)


def test_chromium_layout_keeps_every_card_block_separate_and_in_frame(
    tmp_path: Path, card_data: landing.LandingData,
) -> None:
    if not (ROOT / "web" / "node_modules" / "playwright").is_dir():
        if os.environ.get("CI"):
            pytest.fail("social card rendering requires npm ci in web/")
        pytest.skip("social card rendering requires npm ci in web/")

    long_name = "A very long model name with a regional deployment and extended reasoning profile"
    stress_models = tuple(
        replace(
            card_data.models[index % len(card_data.models)],
            id=f"stress-{index}",
            name=long_name if index == 1 else f"Stress model {index}",
            tied=True,
        )
        for index in range(102)
    )
    stress_data = replace(
        card_data,
        models=stress_models,
        leader_id="stress-0",
        cheapest_id="stress-1",
    )
    edge_axes = landing.PlotAxes(
        cost_min=.1,
        cost_max=.9,
        cost_ticks=(),
        capability_min=5,
        capability_max=9,
        capability_ticks=(),
    )
    edge_cases = (
        ("left-edge", replace(card_data, cheapest_id="cheap", axes=edge_axes)),
        ("top-edge", replace(card_data, cheapest_id="leader", axes=edge_axes)),
        ("right-edge", replace(card_data, cheapest_id="tie", models=(
            replace(card_data.models[0], cost=.9),
            replace(card_data.models[1], cost=.9),
            *card_data.models[2:],
        ), axes=edge_axes)),
    )
    cases = [
        ("landing", social_cards.card_for_page("/", card_data), True),
        ("decide", social_cards.card_for_page("/decide/"), False),
        ("stress", social_cards.card_for_page("/", stress_data), True),
        *((name, social_cards.card_for_page("/", data), True)
          for name, data in edge_cases),
    ]
    for name, card, is_landing in cases:
        try:
            report = social_cards.render_card(card, tmp_path / f"layout-{name}.png")
        except Exception as error:
            if os.environ.get("CI"):
                raise
            pytest.skip(f"Chromium is unavailable: {error}")
        _assert_clean_layout(report)
        if is_landing:
            _assert_landing_plot_geometry(report)


def test_registry_drives_page_metadata_and_deploy_filenames(
    card_data: landing.LandingData,
) -> None:
    assert social_cards.card_for_page("/", card_data).filename == social_cards.LANDING_IMAGE
    assert social_cards.card_for_page("/decide/").filename == social_cards.DECIDE_IMAGE
    assert social_cards.card_filenames() == tuple(
        registration.filename for registration in social_cards.CARD_REGISTRY
    )
    decide = (ROOT / "web" / "decide.html").read_text(encoding="utf-8")
    card = social_cards.card_for_page("/decide/")
    assert f'https://modelspec.dev/{card.filename}' in decide
    assert f'content="{card.alt}"' in decide
    for tag in social_cards.social_meta_for_page("/decide/").splitlines():
        assert tag in decide
