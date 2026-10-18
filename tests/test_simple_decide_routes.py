"""MODEL-404: the first visit and the full board have distinct public routes."""

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from pipeline import agent_copy, entity, landing_chrome, live, social_cards, structured_data, surface_lint

ROOT = Path(__file__).resolve().parents[1]
ROUTES = (("/decide/", "decide.html"), ("/decide/details/", "decide-details.html"))


@pytest.mark.parametrize("path,entry", ROUTES)
def test_both_decide_routes_are_composed_and_describe_their_own_page(tmp_path, path, entry):
    src, web, out = (tmp_path / name for name in ("source", "web", "live"))
    real = src / "modelspec"
    for directory in live.KEEP_DIRS:
        (real / directory).mkdir(parents=True, exist_ok=True)
    for name in live.KEEP_FILES:
        (real / name).write_text("<!doctype html><html><head></head><body></body></html>")
    (real / "api/build.json").write_text('{"built_at":"2026-10-17","export_schema_version":"3.0"}')
    (real / "_headers").write_text("/*\n")
    (src / "benchgraph").mkdir()
    (src / "benchgraph/_redirects").write_text("")
    (web / "assets").mkdir(parents=True)
    for _, name in ROUTES:
        source = ROOT / "web" / name
        # A missing production entry must fail the route assertion, not fixture setup.
        (web / name).write_text(source.read_text() if source.exists() else '<div id="root"></div>')
    (web / "decision.html").write_text('<div id="root"></div>')
    live.build(src, web, out)
    published = out / "modelspec" / path.lstrip("/") / "index.html"
    assert published.is_file(), f"{path} is absent from the live composition"
    page = published.read_text()
    assert f'href="https://modelspec.dev{path}"' in page
    assert live.visible_words(page) >= live.MIN_WORDS
    assert f'"url":"https://modelspec.dev{path}"' in page
    assert f'content="https://modelspec.dev{path}"' in page
    assert '<div id="root"></div>' not in page
    assert surface_lint.structured_data({str(published): page}) == []
    source = (ROOT / "web" / entry).read_text()
    for tag in social_cards.social_meta_for_page(path).splitlines():
        assert tag in source
        assert tag in page


def test_both_decide_urls_have_source_dated_sitemap_entries():
    entries = ET.fromstring(live.sitemap()).findall("{*}url")
    dates = {row.findtext("{*}loc"): row.findtext("{*}lastmod") for row in entries}
    for path, _ in ROUTES:
        assert f"https://modelspec.dev{path}" in dates
        assert dates[f"https://modelspec.dev{path}"] == live.lastmod(path)
        assert path in structured_data.CRUMBS


@pytest.mark.parametrize(
    "path,capsule", (("/decide/", live.decide_capsule), ("/decide/details/", live.details_capsule)),
)
def test_decide_jsonld_names_and_descriptions_are_visible(tmp_path, path, capsule):
    page = capsule() + structured_data.script(structured_data.graph(path, tmp_path))
    assert surface_lint.structured_data({f"{path.lstrip('/')}index.html": page}) == []


def test_first_visit_description_and_card_match_the_simple_choices():
    page = (ROOT / "web/decide.html").read_text()
    assert "Pick a job. See your options and what each task costs." in page
    assert "Facet Board" not in page
    card = social_cards.render_card_html(social_cards.card_for_page("/decide/"))
    assert "Pick a job" in card
    assert "Doesn't matter" not in card
    capsule = live.decide_capsule()
    assert "Example: Everyday help. Pick a job if this isn't yours." in capsule
    assert 'href="/decide/details/"' in capsule


def test_board_links_and_agent_copy_point_to_the_detailed_board():
    assert entity.BOARD == "https://modelspec.dev/decide/details/"
    assert 'href="/decide/details/" class="button primary">Open the board</a>' in landing_chrome.site_header()
    assert entity.BOARD in agent_copy.guide()[1]
    assert entity.BOARD in agent_copy.copy()["instructions"]
    assert entity.BOARD in agent_copy.cli_text()["human_message"]


def test_template_preview_opens_its_template_on_the_detailed_board():
    preview = social_cards.TemplatePreview(
        id="coding-balanced", name="Coding", tradeoff="Balanced", as_of="2026-10-17",
        models=("Example model",), unavailable_reason=None,
    )
    assert 'href="/decide/details/?template=coding-balanced"' in social_cards.template_page(preview)
