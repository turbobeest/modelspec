"""MODEL-195 build-rendered social cards."""

from __future__ import annotations

import html
import os
import re
import shutil
import struct
import subprocess
from dataclasses import replace
from datetime import date
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
        coverage=landing.coverage.from_repo(ROOT, date.today()),
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
    circles = details["plottedCircles"]
    assert all(item is not None for item in (plot, axis, axis_label, point, callout))
    assert circles
    assert not _boxes_intersect(axis, axis_label), (axis, axis_label)
    assert not any(_boxes_intersect(callout, circle) for circle in circles), (
        callout, circles
    )
    assert all(circle["visible"] for circle in circles if circle["tied"]), circles


def test_landing_card_html_uses_exactly_the_page_figures(card_data: landing.LandingData) -> None:
    page = landing.render(card_data, variant="live")
    card = social_cards.landing_card(card_data)
    card_html = social_cards.render_card_html(card)
    tie_line = social_cards.landing_tie_line(card_data)

    assert tie_line in page
    card_text = html.unescape(re.sub(r"<[^>]+>", "", card_html))
    assert tie_line in card_text
    assert "On coding, the evidence can't tell 2 models apart from the top one." in card_text
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


def test_decide_card_uses_the_first_view_question() -> None:
    card = social_cards.decide_card()
    assert card.alt == "ModelSpec Decide: Which AI model fits your job?"
    assert card.headline.replace("<br>", " ") == "Which AI model fits your job?"
    page = (ROOT / "web" / "decide.html").read_text(encoding="utf-8")
    assert f'content="{card.alt}"' in page
    assert "Watch the field narrow" not in card.headline


def test_renderer_writes_every_card_at_the_contract_size(
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
        social_cards.DETAILS_IMAGE,
        social_cards.PRICING_IMAGE,
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
        ("pricing", social_cards.card_for_page("/pricing/"), False),
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
    assert social_cards.card_for_page("/pricing/").filename == social_cards.PRICING_IMAGE
    assert social_cards.card_filenames() == tuple(
        registration.filename for registration in social_cards.CARD_REGISTRY
    )
    decide = (ROOT / "web" / "decide.html").read_text(encoding="utf-8")
    card = social_cards.card_for_page("/decide/")
    assert f'https://modelspec.dev/{card.filename}' in decide
    assert f'content="{card.alt}"' in decide
    for tag in social_cards.social_meta_for_page("/decide/").splitlines():
        assert tag in decide
    pricing_page = (ROOT / "pipeline" / "pricing.py").read_text(encoding="utf-8")
    assert 'social_meta_for_page("/pricing/")' in pricing_page


def _pricing_flags(monkeypatch: pytest.MonkeyPatch, **variables: str) -> None:
    from pipeline import worker_flags

    monkeypatch.setattr(worker_flags, "production_vars", lambda root: variables)


@pytest.mark.parametrize(
    ("variables", "agent_line", "other_line"),
    [
        ({}, "Machine access needs a key.", "Agents pay per answer."),
        ({"ACCESS_ENFORCED": "true"}, "Agents pay per answer.", "Machine access needs a key."),
    ],
)
def test_pricing_card_follows_the_access_flag(
    monkeypatch: pytest.MonkeyPatch, variables: dict[str, str],
    agent_line: str, other_line: str,
) -> None:
    _pricing_flags(monkeypatch, **variables)
    card = social_cards.pricing_card()
    assert card.headline == f"People decide free.<br>{agent_line}"
    assert other_line not in card.headline
    assert agent_line in card.alt


def test_pricing_card_uses_production_flags_and_computed_rates() -> None:
    from pipeline import pricing, worker_flags

    card = social_cards.pricing_card()
    variables = worker_flags.production_vars(ROOT)
    agent_line, rate_range = pricing.hero_summary(
        pricing.load_tiers(ROOT),
        access_enforced=worker_flags.enabled(variables, "ACCESS_ENFORCED"),
        x402_live=pricing.x402_is_live(
            worker_flags.enabled(variables, "X402_ENABLED"),
            worker_flags.enabled(variables, "X402_MAINNET"),
        ),
    )
    assert card.headline == f"People decide free.<br>{agent_line}"
    assert rate_range in card.content


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, False), ("", False), ("0", False), ("false", False),
     ("1", True), ("true", True), (" TRUE ", True)],
)
def test_render_flag_is_explicit(
    monkeypatch: pytest.MonkeyPatch, value: str | None, expected: bool,
) -> None:
    if value is None:
        monkeypatch.delenv(social_cards.RENDER_ENV, raising=False)
    else:
        monkeypatch.setenv(social_cards.RENDER_ENV, value)
    assert social_cards.render_enabled() is expected


def test_build_without_the_flag_needs_no_npm_or_chromium(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pipeline import build as builder

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("the build launched the card renderer without the flag")

    monkeypatch.delenv(social_cards.RENDER_ENV, raising=False)
    monkeypatch.setattr(social_cards, "_render_jobs", refuse)
    out = tmp_path / "dist"
    assert builder.main(["--out", str(out), "--root", str(ROOT)]) == 0
    assert not list((out / "modelspec").glob("og-card-*.png"))
    for page, name in (("index.html", social_cards.LANDING_IMAGE),
                       ("pricing/index.html", social_cards.PRICING_IMAGE)):
        html_text = (out / "modelspec" / page).read_text(encoding="utf-8")
        assert f'property="og:image" content="https://modelspec.dev/{name}"' in html_text


def test_build_with_the_flag_renders_and_fails_hard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pipeline import build as builder

    def broken(tree: Path, data: landing.LandingData) -> None:
        raise RuntimeError("chromium is missing")

    monkeypatch.setenv(social_cards.RENDER_ENV, "1")
    monkeypatch.setattr(social_cards, "render", broken)
    with pytest.raises(RuntimeError, match="chromium is missing"):
        builder.main(["--out", str(tmp_path / "dist"), "--root", str(ROOT)])


def test_ci_installs_chromium_on_the_shard_that_renders_cards() -> None:
    workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
    assert "grep -qxE 'tests/test_(landing|social_cards)\\.py' shard-files.txt" in workflow


def test_build_emits_every_template_preview_and_card(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from decision.templates import load_templates
    from pipeline import build as builder

    monkeypatch.setenv(social_cards.RENDER_ENV, "1")
    out = tmp_path / "dist"
    assert builder.main(["--out", str(out), "--root", str(ROOT)]) == 0
    tree = out / "modelspec"
    templates = load_templates()
    assert templates
    for template in templates:
        template_id = template["id"]
        page = tree / "decide" / "templates" / template_id / "index.html"
        assert page.is_file(), f"missing public preview for {template_id}"
        source = page.read_text(encoding="utf-8")
        image = f"og-card-template-{template_id}.png"
        assert f'property="og:image" content="https://modelspec.dev/{image}"' in source
        assert f'name="twitter:image" content="https://modelspec.dev/{image}"' in source
        assert f'property="og:url" content="https://modelspec.dev/decide/templates/{template_id}/"' in source
        assert f'href="https://modelspec.dev/decide/templates/{template_id}/"' in source
        assert html.escape(template["name"]) in source
        assert html.escape(template["tradeoff"]) in source
        assert f'href="/decide/details/?template={template_id}"' in source
        assert _png_size(tree / image) == (1200, 630)


def test_template_card_and_page_preserve_large_ties_and_escape_public_copy() -> None:
    preview = social_cards.TemplatePreview(
        id="budget-coding", name='Coding <tools> & "budget"',
        tradeoff='Cost <= $0.05 & enough context for "code".',
        as_of="2026-10-13", models=("One", "Two", "Three", "Four"),
        unavailable_reason=None,
    )
    page = social_cards.template_page(preview)
    card = social_cards.template_card(preview)
    text = html.unescape(re.sub(r"<[^>]+>", " ", social_cards.render_card_html(card)))
    assert "Best now: One · Two · Three +1 more (tied)" in page
    assert "+1 more · Tied on the evidence" in text
    assert "Four" not in text
    assert preview.name in text
    assert preview.tradeoff in text
    assert 'Coding &lt;tools&gt; &amp; &quot;budget&quot;' in page
    assert 'property="og:image:alt" content="ModelSpec. Coding &lt;tools&gt; &amp; &quot;budget&quot;' in page
    assert "Frozen public snapshot · 2026-10-13" in page


@pytest.mark.parametrize("reason", [None, "No offering has a known throughput yet"])
def test_template_card_does_not_invent_a_model_when_no_leader_is_known(reason) -> None:
    preview = social_cards.TemplatePreview(
        id="coding-fastest", name="Coding, fastest", tradeoff="Speed among strong coders.",
        as_of="2026-10-13", models=(), unavailable_reason=reason,
    )
    expected = reason or "Best now: none has enough evidence yet"
    assert expected in social_cards.template_page(preview)
    card = social_cards.template_card(preview)
    assert expected in card.content
    assert "template-models" not in card.content


def test_every_frozen_template_card_has_clean_chromium_layout(tmp_path: Path) -> None:
    previews = social_cards.build_template_previews(ROOT, date.today())
    for preview in previews:
        report = social_cards.render_card(social_cards.template_card(preview), tmp_path / preview.filename)
        _assert_clean_layout(report)


def test_template_preview_ignores_an_ambient_private_registry(tmp_path: Path) -> None:
    from decision import registry

    private = tmp_path / "private-registry"
    shutil.copytree(ROOT / "registry", private / "registry")
    for directory in ("benchmarks", "hardware"):
        (private / directory).symlink_to(ROOT / directory, target_is_directory=True)
    facets = private / "registry" / "facets.yaml"
    text = facets.read_text(encoding="utf-8")
    assert text.count("    label: Output throughput\n") == 1
    sentinel = "PRIVATE_REGISTRY_LABEL_306"
    facets.write_text(text.replace("    label: Output throughput\n", f"    label: {sentinel}\n"), encoding="utf-8")
    previous = registry.REPO_ROOT
    try:
        registry.use_root(private)
        previews = social_cards.build_template_previews(ROOT, date.today())
    finally:
        registry.use_root(previous)
    assert previews
    for preview in previews:
        assert sentinel not in social_cards.template_page(preview), preview.id
        assert sentinel not in social_cards.template_card(preview).alt, preview.id


def test_blog_fixture_is_readable_at_phone_and_desktop_with_a_social_card(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pipeline import blog
    from tests.test_blog import BUILD, FIXTURE, KEYS, SLUG, publish

    if not (ROOT / "web" / "node_modules" / "playwright").is_dir():
        if os.environ.get("CI"):
            pytest.fail("blog browser test requires npm ci in web/")
        pytest.skip("blog browser test requires npm ci in web/")
    root = tmp_path / "source"
    shutil.copytree(FIXTURE, root / "blog")
    standard = root / "docs" / "method" / "release-breakdown-standard.md"
    standard.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "docs" / "method" / standard.name, standard)
    publish(root)
    monkeypatch.setenv("BLOG_ENABLED", "true")
    monkeypatch.setenv(social_cards.RENDER_ENV, "1")
    tree = tmp_path / "site"
    blog.write(tree, root, BUILD, public_keys=KEYS)
    shutil.copytree(ROOT / "site" / "fonts", tree / "fonts")
    result = subprocess.run(
        ["node", str(ROOT / "web" / "scripts" / "blog-browser.mjs"),
         str(tree), SLUG, str(tmp_path / "screenshots")],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=90,
    )
    import json
    checks = json.loads(result.stdout)
    assert set(checks) == {"390", "1440"}
    for viewport, values in checks.items():
        assert all(values.values()), (viewport, values)
    assert _png_size(tree / "blog" / SLUG / "r1" / "og-card.png") == (1200, 630)
