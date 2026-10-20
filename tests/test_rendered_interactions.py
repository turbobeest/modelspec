"""MODEL-433: registry recipes select public pricing controls before capture."""

from __future__ import annotations

import json
import time

import pytest

from decision.sources import RenderedFetcher, load_sources, rendered_preparation


RECIPE = [
    {"action": "click", "selector": "#provider"},
    {"action": "select_option", "selector": "#region", "value": "us-east"},
    {"action": "scroll", "selector": "#prices"},
    {"action": "wait_text", "selector": "#prices", "text": "$4.00"},
]


def registry(tmp_path, interactions=RECIPE, **overrides):
    row = {
        "id": "fixture-pricing", "url": "https://fixture.example/prices",
        "fetch": "rendered", "rendered_interactions": interactions,
        "cited_regions": [{"id": "prices", "locator": {"kind": "css", "value": "#prices"}}],
        **overrides,
    }
    path = tmp_path / "sources.yaml"
    path.write_text(json.dumps({"schema_version": 1, "sources": [row]}))
    return load_sources(path)


def test_registry_loads_a_bounded_data_only_recipe(tmp_path):
    sources = registry(tmp_path)
    assert sources["fixture-pricing"].model_dump()["rendered_interactions"] == RECIPE


@pytest.mark.parametrize("recipe, overrides", [
    ([{"action": "evaluate", "selector": "body", "code": "alert(1)"}], {}),
    ([{"action": "fill", "selector": "input", "value": "password"}], {}),
    ([{"action": "click", "selector": ""}], {}),
    ([{"action": "select_option", "selector": "select"}], {}),
    ([{"action": "wait_text", "selector": "#prices", "text": ""}], {}),
    (RECIPE * 5, {}),
    (RECIPE[:-1], {}),
    (RECIPE, {"fetch": "http"}),
    (RECIPE, {"normaliser": "text-default", "cited_regions": []}),
])
def test_registry_rejects_unsafe_or_incomplete_recipes(tmp_path, recipe, overrides):
    with pytest.raises(ValueError):
        registry(tmp_path, recipe, **overrides)


@pytest.fixture
def browser():
    pytest.importorskip("playwright.sync_api")
    with RenderedFetcher(timeout=1, idle_timeout=0.01) as renderer:
        yield renderer


HTML = """<!doctype html>
<button id="provider" type="button" onclick="document.querySelector('#region').hidden=false">
Provider</button>
<select id="region" hidden onchange="setTimeout(() => {
document.querySelector('#prices').textContent='Model A Input $4.00 Output $20.00';
}, 50)">
<option value="">Choose region</option><option value="us-east">US East</option></select>
<div id="prices"></div>
"""


def render_fixture(browser, sources, html=HTML):
    browser._context.route("https://fixture.example/**",
                           lambda route: route.fulfill(body=html, content_type="text/html"))
    return browser.fetch("https://fixture.example/prices",
                         prepare=rendered_preparation(sources, sources))


def test_recipe_captures_prices_after_click_selection_and_text_wait(tmp_path, browser):
    result = render_fixture(browser, registry(tmp_path))
    assert result.outcome == "ok", result.error
    assert b'<div id="prices">Model A Input $4.00 Output $20.00</div>' in result.body


@pytest.mark.parametrize("recipe", [
    [{"action": "click", "selector": "#missing"}, RECIPE[-1]],
    [{"action": "wait_text", "selector": "#prices", "text": "$999"}],
    [{"action": "click", "selector": "button"}, RECIPE[-1]],
])
def test_failed_recipe_never_captures_a_plausible_partial_page(tmp_path, browser, recipe):
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        '<button type="button">A</button><button type="button">B</button>'
        '<div id="prices">Model A Input $4.00 Output $20.00</div>')
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "interaction" in result.error


@pytest.mark.parametrize("control", [
    '<a id="unsafe" href="/login">Sign in</a>',
    '<form><button id="unsafe">Submit</button></form>',
    '<input id="unsafe" type="submit">',
    '<button id="unsafe" type="button">Accept all cookies</button>',
    '<button id="unsafe" type="button">Log in</button>',
])
def test_recipe_refuses_navigation_forms_login_and_cookie_acceptance(tmp_path, browser, control):
    recipe = [{"action": "click", "selector": "#unsafe"}, RECIPE[-1]]
    result = render_fixture(browser, registry(tmp_path, recipe),
                            control + '<div id="prices">$4.00</div>')
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "unsafe" in result.error


def test_recipe_can_reject_optional_cookies(tmp_path, browser):
    recipe = [{"action": "reject_consent", "selector": "#reject"}, RECIPE[-1]]
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        '<button id="reject" type="button" onclick="this.remove()">Reject all cookies</button>'
        '<div id="prices">$4.00</div>')
    assert result.outcome == "ok", result.error
    assert b'id="reject"' not in result.body


def test_recipe_cannot_accept_cookies_with_a_native_select(tmp_path, browser):
    recipe = [{"action": "select_option", "selector": "#consent", "value": "all"},
              RECIPE[-1]]
    result = render_fixture(browser, registry(tmp_path, recipe), """
        <div id="cookie-consent"><select id="consent">
        <option value="none">Reject all</option><option value="all">Accept all</option>
        </select></div><div id="prices">$4.00</div>""")
    assert result.outcome == "unreachable"
    assert result.body == b""


def test_conflicting_recipes_for_one_url_fail_closed(tmp_path, browser):
    sources = registry(tmp_path)
    sources.update(registry(tmp_path, [RECIPE[-1]], id="alias"))
    result = render_fixture(browser, sources)
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "conflicting" in result.error


def test_recipe_has_one_deadline_for_all_steps(tmp_path, browser):
    recipe = [
        {"action": "wait_text", "selector": "#first", "text": "ready"},
        {"action": "wait_text", "selector": "#second", "text": "ready"},
    ]
    started = time.monotonic()
    result = render_fixture(browser, registry(tmp_path, recipe), """
        <div id="first"></div><div id="second"></div><script>
        setTimeout(() => document.querySelector('#first').textContent='ready', 700);
        setTimeout(() => document.querySelector('#second').textContent='ready', 1400);
        </script>""")
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert time.monotonic() - started < 2.5


def test_registry_recipe_takes_precedence_over_legacy_source_preparation(tmp_path):
    sources = registry(tmp_path, id="aws-pricing")
    from decision.sources import RENDERED_PREPARATIONS

    assert rendered_preparation(sources, sources) is not RENDERED_PREPARATIONS["aws-pricing"]
