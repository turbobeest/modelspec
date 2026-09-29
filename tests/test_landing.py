"""MODEL-186 landing data, copy, and variant contracts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from decision.computed import COST_PER_TASK, with_computed
from decision.contract import DEFAULT_TASK_TOKENS, parse_spec
from decision.engine import decide
from decision.registry import default
from decision.snapshot import build_from_repo, load_built_snapshot
from decision.templates import load_templates
from pipeline import landing
from pipeline.load import load_models

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def data() -> landing.LandingData:
    return landing.build_data(str(ROOT), date.today())


def test_landing_figures_are_derived_from_the_snapshot(data: landing.LandingData) -> None:
    leader = data.leader
    # The tie is /decide's best band for coding alone (MODEL-206): the leader
    # is the top estimate with enough evidence, and a thin model never ties.
    assert not leader.thin
    assert leader.estimate == max(model.estimate for model in data.models if not model.thin)
    assert not any(model.thin for model in data.tie)
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
    assert f"tell {tied_others} models apart" in page
    assert f"costs {data.ratio:.1f}× less" in page
    assert f"${data.monthly_gap:,.0f} a month apart" in page
    assert data.leader.name in page
    assert data.cheapest.name in page
    assert f"${data.leader_monthly:,.0f}" in page
    assert f"${data.cheapest_monthly:,.0f}" in page


def test_every_published_template_route_is_an_engine_result(data: landing.LandingData) -> None:
    registry = default()
    snapshot = build_from_repo(ROOT, premier=None, as_of=date.today(), gate=False)
    loaded = load_built_snapshot(snapshot, source="landing test build")
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
        if os.environ.get("CI"):
            pytest.fail("landing browser tests need Playwright in web/node_modules in CI")
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
    method_page = directory / "method.html"
    live.write_text(landing.render(changed, variant="live"), encoding="utf-8")
    holding.write_text(landing.render(changed, variant="holding"), encoding="utf-8")
    from pipeline import method
    method_page.write_text(
        method.page(changed, method.SigningState(("ed25519-test",), "ed25519-test")),
        encoding="utf-8",
    )
    assembled = directory / "assembled"
    (assembled / "decide").mkdir(parents=True)
    shutil.copyfile(
        ROOT / "web" / "dist" / "decide.html",
        assembled / "decide" / "index.html",
    )
    shutil.copytree(ROOT / "web" / "dist" / "assets", assembled / "assets")
    try:
        completed = subprocess.run(
            ["node", str(browser_script), str(live), str(holding), str(method_page), str(assembled)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        cannot_launch = (isinstance(error, FileNotFoundError)
                         or "Executable doesn't exist" in detail
                         or "browserType.launch" in detail)
        # CI installs Chromium for this shard, so a launch failure there is a
        # failure, never a skip: the browser checks must not vanish silently.
        if cannot_launch and os.environ.get("CI"):
            pytest.fail(f"landing browser tests could not run in CI:\n{detail}")
        if cannot_launch:
            pytest.skip(f"Chromium cannot run landing browser tests: {detail.splitlines()[0]}")
        pytest.fail(f"landing browser assertions failed:\n{detail}")
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    "check",
    [
        "altered_data", "challenge", "motion", "responsive", "holding",
        "forwarding", "assembled_decide", "assembled_decide_mobile", "forwarded_state_ranks",
        "method_responsive",
    ],
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
    assert '<meta name="robots" content="noindex">' not in live
    assert '<link rel="canonical" href="https://modelspec.dev/">' in live
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
    assert 'href="/decide/">Open the board</a>' in live
    assert 'href="/decide/">Open the board</a>' not in holding
    assert live.count('href="/graph/">Explore the graph</a>') == 1
    assert live.index('href="/graph/">Explore the graph</a>') > live.index("<footer>")
    assert 'href="/graph/">Explore the graph</a>' not in holding
    for page in (live, holding):
        assert page.count('href="/pricing/">Pricing</a>') == 2
        assert page.rindex('href="/pricing/">Pricing</a>') > page.index("<footer>")
    footer = (f"{len(data.routes)} of {data.template_count} templates · "
              "the others' top result has no published price")
    assert footer in live and footer in holding


@pytest.mark.parametrize("key", landing.DECIDE_QUERY_KEYS)
def test_old_root_query_state_moves_to_decide(key: str) -> None:
    assert landing.has_decide_state(f"?{key}=value", "")


@pytest.mark.parametrize("key", landing.DECIDE_HASH_KEYS)
def test_old_root_hash_state_moves_to_decide(key: str) -> None:
    assert landing.has_decide_state("", f"#{key}=value")


@pytest.mark.parametrize("search", ["", "?utm_source=launch", "?utm_medium=email&utm_campaign=go"])
def test_plain_and_campaign_root_urls_stay_on_the_landing(search: str) -> None:
    assert not landing.has_decide_state(search, "")


def test_the_landing_head_carries_the_current_headline(data: landing.LandingData) -> None:
    for variant in ("live", "holding"):
        page = landing.render(data, variant=variant)
        assert f"<title>{landing.TITLE}</title>" in page
        assert f'<meta name="description" content="{landing.DESCRIPTION}">' in page
        assert f'<meta property="og:title" content="{landing.TITLE}">' in page
        assert "usually a tie" not in page


def test_the_headline_figures_come_from_the_engine(data: landing.LandingData) -> None:
    """Recompute the hero's tie from /decide's own answer and find it on the page."""
    registry = default()
    snapshot = build_from_repo(ROOT, premier=None, as_of=date.today(), gate=False)
    loaded = load_built_snapshot(snapshot, source="landing headline test")
    answer = decide(parse_spec(landing.TIE_SPEC, facets=registry.facet), loaded,
                    facets=registry.facet)
    bands = answer.bands
    assert bands is not None and bands.leader is not None
    best = {entry.model: entry for entry in bands.best}
    cheapest = min(bands.best, key=lambda entry: (entry.cost_per_task,
                                                   -entry.estimates[0].value, entry.model))
    leader = best[bands.leader]
    ratio = round(leader.cost_per_task / cheapest.cost_per_task, 1)

    assert {model.id for model in data.tie} == set(best)
    assert data.leader_id == bands.leader
    assert data.cheapest_id == cheapest.model
    assert data.ratio == ratio
    assert data.band_probability == bands.band_probability
    assert data.cheapest_p == cheapest.p_beats_leader

    page = landing.render(data, variant="live")
    assert f"<h1>{landing.HEADLINE}</h1>" in page
    assert f'<p class="eyebrow">{landing.EYEBROW}</p>' in page
    hero = page[page.index('<section class="hero">'):page.index('<section class="receipt"')]
    assert f"can't tell {len(best) - 1} models apart from the top one" in hero
    assert f"costs {ratio:.1f}× less" in hero
    if cheapest.p_beats_leader is not None:
        assert f"a {cheapest.p_beats_leader:.0%} chance of scoring at least as well" in page
        assert f"At {bands.band_probability:.0%} or more" in page


def test_the_positioning_copy_types_no_numbers(data: landing.LandingData) -> None:
    """Numbers on the landing come from the engine; the new sections carry none."""
    import html
    import re

    page = landing.render(data, variant="live")
    routers = page[page.index('<section class="routers"'):page.index('<section class="teams"')]
    teams = page[page.index('<section class="teams"'):page.index('<section class="agents"')]
    text = html.unescape(re.sub(r"<[^>]+>", " ", routers + teams))
    assert re.search(r"\d", text) is None, text
    assert re.search(r"\d", landing.HEADLINE + landing.EYEBROW) is None


def test_every_analysis_row_links_to_a_proof_that_exists(data: landing.LandingData) -> None:
    import re

    from pipeline import method

    method_page = method.page(data, method.SigningState((), None))
    method_ids = set(re.findall(r'id="([^"]+)"', method_page))

    def github_anchors(rel: str) -> set[str]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        headings = re.findall(r"^#+ (.+)$", text, flags=re.M)
        return {re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
                for heading in headings}

    assert len(landing.ANALYSIS) >= 9
    for element, _, proof in landing.ANALYSIS:
        path, _, anchor = proof.partition("#")
        if path.startswith(landing.GH):
            rel = path.removeprefix(landing.GH)
            assert (ROOT / rel).is_file(), proof
            assert anchor in github_anchors(rel), proof
        elif path == "/method/":
            assert anchor in method_ids, proof
        else:
            assert path == "/legal/neutrality/", proof
            assert (ROOT / "docs" / "legal" / "neutrality.md").is_file()
    page = landing.render(data, variant="live")
    for element, _, proof in landing.ANALYSIS:
        assert f'<b>{element}</b>' in page
        assert f'href="{proof}"' in page


def test_the_positioning_does_not_overclaim(data: landing.LandingData) -> None:
    from decision.excluded import REMOVED_TEXT
    from pipeline import method
    from pipeline.build import llms_txt
    from pipeline.export import Build

    llms = llms_txt(site="ModelSpec", base="https://modelspec.dev",
                    build=Build(commit="0" * 40, built_at="2026-09-29T00:00:00+00:00",
                                as_of=date(2026, 9, 29)))
    pages = (landing.render(data, variant="live"), landing.render(data, variant="holding"),
             method.page(data, method.SigningState((), None)), llms)
    for page in pages:
        lowered = page.lower()
        for phrase in ("dod", "-grade", "compliant with", "complies with", "certified"):
            assert phrase not in lowered, phrase
        assert REMOVED_TEXT.search(page) is None
    assert "an analysis of alternatives" in pages[0].lower()
    assert "an analysis of alternatives" in llms.lower()
