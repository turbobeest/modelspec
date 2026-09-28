"""MODEL-186 landing data, copy, and variant contracts."""

from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path

import pytest

from pipeline import landing

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def data() -> landing.LandingData:
    return landing.build_data(str(ROOT), date.today())


def test_landing_figures_are_derived_from_the_snapshot(data: landing.LandingData) -> None:
    leader = data.leader
    assert leader.estimate == max(model.estimate for model in data.models)
    assert all(model.high >= leader.low for model in data.tie)
    assert data.cheapest in data.tie
    assert data.cheapest == min(
        data.tie, key=lambda model: (model.cost, -model.estimate, model.id)
    )
    assert data.ratio == round(leader.cost / data.cheapest.cost, 1)
    assert data.leader_monthly == leader.cost * landing.MONTHLY_TASKS
    assert data.cheapest_monthly == data.cheapest.cost * landing.MONTHLY_TASKS
    assert data.monthly_gap == data.leader_monthly - data.cheapest_monthly


def test_landing_copy_uses_the_computed_figures(data: landing.LandingData) -> None:
    page = landing.render(data, variant="live")
    tied_others = len(data.tie) - 1
    assert f"tell {tied_others} of these models apart" in page
    assert f"costs {data.ratio:.1f}× less" in page
    assert f"${data.monthly_gap:,.0f} a month apart" in page
    assert data.leader.name in page
    assert data.cheapest.name in page
    assert f"${data.leader_monthly:,.0f}" in page
    assert f"${data.cheapest_monthly:,.0f}" in page


def test_renderer_contains_no_model_name_or_model_price(data: landing.LandingData) -> None:
    source = inspect.getsource(landing.render)
    for model in data.models:
        assert model.name not in source
        assert f"${model.cost:.3f}" not in source


def test_every_published_template_route_is_an_engine_result(data: landing.LandingData) -> None:
    assert data.routes
    assert len({route.id for route in data.routes}) == len(data.routes)
    assert all(route.model for route in data.routes)


def test_live_and_holding_variants_differ_only_where_the_contract_requires(
    data: landing.LandingData,
) -> None:
    live = landing.render(data, variant="live")
    holding = landing.render(data, variant="holding")
    assert '<meta name="robots" content="noindex">' in live
    assert 'rel="canonical"' not in live
    assert 'href="/">Open the board</a>' in live
    assert '<link rel="canonical" href="https://modelspec.dev/">' in holding
    assert 'content="noindex"' not in holding
    assert "Board opening soon" in holding
    assert 'href="/">Open the board</a>' not in holding
    assert "pipx install modelspec-dev" not in live
    assert "pipx install modelspec-dev" not in holding
    release = "CLI, API and MCP. Install instructions arrive with the public release."
    assert release in live and release in holding


def test_page_has_the_interaction_and_accessibility_contract(data: landing.LandingData) -> None:
    page = landing.render(data, variant="live")
    assert '<select id="model-pick">' in page
    assert '<button type="submit">Check my pick</button>' in page
    assert 'aria-live="polite"' in page
    assert 'role="img" aria-label=' in page
    assert 'href="/legal/terms/"' in page
    assert 'href="/legal/privacy/"' in page
    assert 'href="/legal/neutrality/"' in page
    script = (ROOT / "pipeline/landing_assets/landing.js").read_text(encoding="utf-8")
    css = (ROOT / "pipeline/landing_assets/landing.css").read_text(encoding="utf-8")
    assert "2600" in script
    assert 'prefers-reduced-motion: reduce' in script
    assert "@media (max-width: 899px)" in css
