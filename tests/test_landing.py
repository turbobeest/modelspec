"""MODEL-186 landing data, copy, and variant contracts."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from decision.computed import COST_PER_TASK, with_computed
from decision.contract import DEFAULT_TASK_TOKENS, parse_spec
from decision.engine import decide
from decision.registry import default
from decision.snapshot import build_from_repo, load_snapshot_bytes
from decision.templates import load_templates
from pipeline import landing
from pipeline.load import load_models

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


def test_every_published_template_route_is_an_engine_result(data: landing.LandingData) -> None:
    registry = default()
    snapshot = build_from_repo(ROOT, premier=None, as_of=date.today(), gate=False)
    loaded = load_snapshot_bytes(snapshot.to_bytes(), key=None)
    cards = {model.model_id: model for model in load_models(ROOT)}
    expected: list[tuple[str, str, str, float]] = []
    unpriced_results: list[str] = []
    for template in load_templates(registry=registry):
        spec = parse_spec(template["spec"] | {"explain": "none", "limit": 1},
                          facets=registry.facet)
        answer = decide(spec, loaded, facets=registry.facet)
        if not answer.results:
            continue
        result = answer.results[0]
        candidate = landing._offering_id(result)
        task_view = with_computed(loaded, spec.task_tokens or DEFAULT_TASK_TOKENS)
        computed = task_view.computed(candidate, COST_PER_TASK) if candidate else None
        if computed is None:
            unpriced_results.append(template["id"])
            continue
        expected.append((template["id"], template["name"],
                         cards[result.offering.model].display_name, computed.value))

    assert [(route.id, route.name, route.model, route.cost) for route in data.routes] == expected
    assert data.template_count == len(expected) + len(unpriced_results)
    # Round 2 deliberately omitted a template whose top result has no computed cost.
    # Round 3 keeps that decision and requires the terminal to disclose the omission.
    assert "retrieval-embeddings" in unpriced_results
    assert "retrieval-embeddings" not in {route.id for route in data.routes}
    assert all(route.cost is not None for route in data.routes)
    page = landing.render(data, variant="live")
    assert (f"{len(data.routes)} of {data.template_count} templates · "
            "the others' top result has no published price") in page


@pytest.fixture(scope="module")
def landing_browser_results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, bool]:
    """Execute both landing variants once in Chromium and return named checks."""
    browser_script = ROOT / "web" / "scripts" / "landing-browser.mjs"
    playwright = ROOT / "web" / "node_modules" / "playwright"
    if not playwright.is_dir():
        pytest.skip("landing browser tests require `npm ci` in web/")

    models = (
        landing.PlotModel("synthetic-leader", "Synthetic Leader", .9, 9, 8, 10, True),
        landing.PlotModel("synthetic-tie", "Synthetic Tie", .2, 8.5, 8, 9.5, True),
        landing.PlotModel("synthetic-cheapest", "Synthetic Cheapest", .1, 8.2, 8, 9, True),
        landing.PlotModel("synthetic-outsider", "Synthetic Outsider", .5, 5, 4, 6, False),
    )
    monthly_tasks = 4_321
    changed = landing.LandingData(
        as_of="2026-09-28",
        benchmark_count=7,
        task_input_tokens=12_000,
        task_output_tokens=3_000,
        monthly_tasks=monthly_tasks,
        models=models,
        leader_id="synthetic-leader",
        cheapest_id="synthetic-cheapest",
        ratio=9,
        leader_monthly=models[0].cost * monthly_tasks,
        cheapest_monthly=models[2].cost * monthly_tasks,
        monthly_gap=(models[0].cost - models[2].cost) * monthly_tasks,
        routes=(),
        template_count=0,
        axes=landing._plot_axes(list(models)),
    )
    directory = tmp_path_factory.mktemp("landing-browser")
    live = directory / "live.html"
    holding = directory / "holding.html"
    live.write_text(landing.render(changed, variant="live"), encoding="utf-8")
    holding.write_text(landing.render(changed, variant="holding"), encoding="utf-8")
    try:
        completed = subprocess.run(
            ["node", str(browser_script), str(live), str(holding)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        if "Executable doesn't exist" in detail or "browserType.launch" in detail:
            pytest.skip(f"Chromium cannot run landing browser tests: {detail.splitlines()[0]}")
        pytest.fail(f"landing browser assertions failed:\n{detail}")
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    "check",
    ["altered_data", "challenge", "motion", "responsive", "holding"],
)
def test_landing_behaviour_in_browser(
    landing_browser_results: dict[str, bool], check: str,
) -> None:
    assert landing_browser_results[check]


def test_plot_domains_and_ticks_are_derived_from_the_models() -> None:
    models = [
        landing.PlotModel("low", "Low", 0.001, -1.0, -1.5, -0.5, False),
        landing.PlotModel("high", "High", 5.0, 2.0, 1.5, 2.5, True),
    ]
    axes = landing._plot_axes(models)
    assert axes.cost_min < 0.001 < axes.cost_max
    assert axes.cost_min < 5.0 < axes.cost_max
    assert axes.capability_min < -1.5
    assert axes.capability_max > 2.5
    assert all(axes.cost_min <= tick <= axes.cost_max for tick in axes.cost_ticks)
    assert all(axes.capability_min <= tick <= axes.capability_max
               for tick in axes.capability_ticks)
    for tick in axes.cost_ticks:
        exponent = 10 ** int(f"{tick:e}".split("e")[1])
        assert round(tick / exponent, 10) in {1, 2, 5}


def test_live_and_holding_variants_differ_only_where_the_contract_requires(
    data: landing.LandingData,
) -> None:
    live = landing.render(data, variant="live")
    holding = landing.render(data, variant="holding")
    assert '<meta name="robots" content="noindex">' in live
    assert 'rel="canonical"' not in live
    assert '<link rel="canonical" href="https://modelspec.dev/">' in holding
    assert 'content="noindex"' not in holding
    release = "CLI, API and MCP. Install instructions arrive with the public release."
    for page in (live, holding):
        # First run in order: vocab and decide need the snapshot first.
        steps = [page.index(f"<code>{line}</code>") for line in landing.FIRST_RUN]
        assert steps == sorted(steps)
        assert landing.FIRST_RUN[1] == "modelspec snapshot fetch"
        assert release not in page
    unpublished = landing.render(data, variant="holding", package_published=False)
    assert "pipx install" not in unpublished
    assert release in unpublished
    assert "Every number is one click from its source." in live
    assert "Every number has a source." not in live
    assert "Every number has a source." in holding
    assert "When the board opens, each one is a click away." in holding
    assert "Every number is one click from its source." not in holding
    footer = (f"{len(data.routes)} of {data.template_count} templates · "
              "the others' top result has no published price")
    assert footer in live and footer in holding
