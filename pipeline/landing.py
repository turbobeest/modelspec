"""Build the data-driven ModelSpec landing page (MODEL-186)."""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qsl

from decision.computed import COST_PER_TASK, with_computed
from decision.contract import DEFAULT_TASK_TOKENS, parse_spec
from decision.engine import decide
from decision.registry import default
from decision.snapshot import build_from_repo, load_built_snapshot
from decision.templates import load_templates
from pipeline import brand, landing_chrome
from pipeline import social_cards
from pipeline.load import load_models

SOFTWARE_ENGINEERING = "software_engineering"
MONTHLY_TASKS = 10_000
PACKAGE_PUBLISHED = True  # modelspec-dev 0.1.0 on PyPI, 2026-09-27
# First run, in order: `vocab` and `decide` need the cached snapshot.
FIRST_RUN = (
    "pipx install modelspec-dev",
    "modelspec snapshot fetch",
    "modelspec decide --template budget-coding",
)
TITLE = "ModelSpec — your model is a guess"
DESCRIPTION = ("See which AI models the evidence can't tell apart, what each one really "
               "costs, and hand the choice to your agents. Sourced evidence; nobody pays "
               "to rank higher.")
ASSET_DIR = "landing-assets"
DATA_ID = "landing-data"
DECIDE_PATH = "/decide/"
DECIDE_QUERY_KEYS = ("demo", "estate", "layout", "simulate", "theme")
DECIDE_HASH_KEYS = ("s",)


def has_decide_state(search: str, hash_value: str) -> bool:
    """Whether a former-root URL carries state read by the decide app."""
    query = {key for key, _ in parse_qsl(search.removeprefix("?"), keep_blank_values=True)}
    fragment = {key for key, _ in parse_qsl(hash_value.removeprefix("#"), keep_blank_values=True)}
    return bool(query.intersection(DECIDE_QUERY_KEYS) or fragment.intersection(DECIDE_HASH_KEYS))


@dataclass(frozen=True)
class PlotModel:
    id: str
    name: str
    cost: float
    estimate: float
    low: float
    high: float
    tied: bool


@dataclass(frozen=True)
class TemplateRoute:
    id: str
    name: str
    model: str
    cost: float


@dataclass(frozen=True)
class PlotAxes:
    cost_min: float
    cost_max: float
    cost_ticks: tuple[float, ...]
    capability_min: float
    capability_max: float
    capability_ticks: tuple[float, ...]


@dataclass(frozen=True)
class LandingData:
    as_of: str
    benchmark_count: int
    task_input_tokens: int
    task_output_tokens: int
    monthly_tasks: int
    models: tuple[PlotModel, ...]
    leader_id: str
    cheapest_id: str
    ratio: float
    leader_monthly: float
    cheapest_monthly: float
    monthly_gap: float
    routes: tuple[TemplateRoute, ...]
    template_count: int
    axes: PlotAxes

    @property
    def leader(self) -> PlotModel:
        return next(model for model in self.models if model.id == self.leader_id)

    @property
    def cheapest(self) -> PlotModel:
        return next(model for model in self.models if model.id == self.cheapest_id)

    @property
    def tie(self) -> tuple[PlotModel, ...]:
        return tuple(model for model in self.models if model.tied)


def _offering_id(result: Any) -> str | None:
    offering = result.offering
    if not offering.provider:
        return None
    return f"{offering.provider}/{offering.model}/{offering.region}/{offering.tier}"


def _from_dict(raw: dict[str, Any]) -> LandingData:
    return LandingData(
        **{key: value for key, value in raw.items() if key not in {"models", "routes", "axes"}},
        models=tuple(PlotModel(**row) for row in raw["models"]),
        routes=tuple(TemplateRoute(**row) for row in raw["routes"]),
        axes=PlotAxes(**(raw["axes"] | {
            "cost_ticks": tuple(raw["axes"]["cost_ticks"]),
            "capability_ticks": tuple(raw["axes"]["capability_ticks"]),
        })),
    )


def _nice_values(low: float, high: float) -> tuple[float, ...]:
    """Return 1-2-5 ticks inside a positive range."""
    values: list[float] = []
    for exponent in range(math.floor(math.log10(low)) - 1,
                          math.ceil(math.log10(high)) + 2):
        magnitude = 10 ** exponent
        values.extend(factor * magnitude for factor in (1, 2, 5))
    return tuple(value for value in values if low <= value <= high)


def _linear_ticks(low: float, high: float, target: int = 5) -> tuple[float, ...]:
    span = high - low
    rough_step = span / target
    magnitude = 10 ** math.floor(math.log10(rough_step))
    step = next(factor * magnitude for factor in (1, 2, 5, 10)
                if factor * magnitude >= rough_step)
    first = math.ceil(low / step) * step
    count = math.floor((high - first) / step) + 1
    return tuple(round(first + index * step, 12) for index in range(count))


def _plot_axes(models: list[PlotModel]) -> PlotAxes:
    costs = [model.cost for model in models]
    log_low, log_high = math.log(min(costs)), math.log(max(costs))
    log_span = log_high - log_low
    log_padding = log_span * 0.08 if log_span else math.log(1.5)
    cost_min = math.exp(log_low - log_padding)
    cost_max = math.exp(log_high + log_padding)

    capability_low = min(model.low for model in models)
    capability_high = max(model.high for model in models)
    capability_span = capability_high - capability_low
    capability_padding = capability_span * 0.08 if capability_span else 0.5
    capability_min = capability_low - capability_padding
    capability_max = capability_high + capability_padding
    return PlotAxes(
        cost_min=cost_min,
        cost_max=cost_max,
        cost_ticks=_nice_values(cost_min, cost_max),
        capability_min=capability_min,
        capability_max=capability_max,
        capability_ticks=_linear_ticks(capability_min, capability_max),
    )


def _input_digest(root: Path, as_of: date) -> str:
    digest = hashlib.sha256(as_of.isoformat().encode())
    for name in ("models", "offerings", "benchmarks", "verification", "registry", "decision"):
        base = (root / name).resolve()
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            digest.update(name.encode())
            digest.update(path.relative_to(base).as_posix().encode())
            digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


@lru_cache(maxsize=4)
def _build_data(root_value: str, as_of: date, _digest: str) -> LandingData:
    root = Path(root_value)
    snapshot = build_from_repo(root, premier=None, as_of=as_of, gate=False)
    # This snapshot never leaves the build process. Check its content hash, but
    # do not sign it or require a publisher signature meant for public clients.
    loaded = load_built_snapshot(snapshot, source="landing-page build")
    priced = with_computed(loaded, DEFAULT_TASK_TOKENS)
    cards = {model.model_id: model for model in load_models(root)}

    rows: list[PlotModel] = []
    candidates = tuple(priced.candidates())
    for model_id in candidates:
        if priced.kind(model_id) != "model":
            continue
        if priced.fact(model_id, "model.class").value != "text-generator":
            continue
        estimate = priced.capability_estimate(model_id, SOFTWARE_ENGINEERING)
        offerings = [
            (computed.value, candidate)
            for candidate in candidates
            if priced.kind(candidate) == "offering"
            and priced.model_of(candidate) == model_id
            and (computed := priced.computed(candidate, COST_PER_TASK)) is not None
        ]
        if estimate is None or not offerings:
            continue
        cost, _ = min(offerings)
        rows.append(PlotModel(
            id=model_id,
            name=cards[model_id].display_name,
            cost=cost,
            estimate=estimate.value,
            low=estimate.low,
            high=estimate.high,
            tied=False,
        ))
    if not rows:
        raise ValueError("the landing page has no priced text models with coding estimates")

    leader = max(rows, key=lambda model: (model.estimate, -model.cost, model.id))
    tie_ids = {model.id for model in rows if model.high >= leader.low}
    rows = [PlotModel(**(asdict(model) | {"tied": model.id in tie_ids})) for model in rows]
    tie = [model for model in rows if model.tied]
    cheapest = min(tie, key=lambda model: (model.cost, -model.estimate, model.id))

    registry = default()
    templates = load_templates(registry=registry)
    routes: list[TemplateRoute] = []
    template_count = 0
    for template in templates:
        spec = parse_spec(template["spec"] | {"explain": "none", "limit": 1},
                          facets=registry.facet)
        answer = decide(spec, loaded, facets=registry.facet)
        if not answer.results:
            continue
        template_count += 1
        result = answer.results[0]
        candidate = _offering_id(result)
        task_view = with_computed(loaded, spec.task_tokens or DEFAULT_TASK_TOKENS)
        computed = task_view.computed(candidate, COST_PER_TASK) if candidate else None
        if computed is None:
            continue
        routes.append(TemplateRoute(
            id=template["id"],
            name=template["name"],
            model=cards[result.offering.model].display_name,
            cost=computed.value,
        ))

    leader_monthly = leader.cost * MONTHLY_TASKS
    cheapest_monthly = cheapest.cost * MONTHLY_TASKS
    return LandingData(
        as_of=as_of.isoformat(),
        benchmark_count=len({
            str(item.get("benchmark"))
            for item in loaded.capability_items.values()
            if any(domain == SOFTWARE_ENGINEERING for domain, _ in item.get("domains", ()))
        }),
        task_input_tokens=DEFAULT_TASK_TOKENS.input,
        task_output_tokens=DEFAULT_TASK_TOKENS.output,
        monthly_tasks=MONTHLY_TASKS,
        models=tuple(sorted(rows, key=lambda model: model.id)),
        leader_id=leader.id,
        cheapest_id=cheapest.id,
        ratio=round(leader.cost / cheapest.cost, 1),
        leader_monthly=leader_monthly,
        cheapest_monthly=cheapest_monthly,
        monthly_gap=leader_monthly - cheapest_monthly,
        routes=tuple(routes),
        template_count=template_count,
        axes=_plot_axes(rows),
    )


def build_data(root_value: str, as_of: date) -> LandingData:
    """Compute landing facts once per repository input set, across build workers."""
    root = Path(root_value).resolve()
    digest = _input_digest(root, as_of)
    cache = Path(tempfile.gettempdir()) / f"modelspec-landing-{digest}.json"
    lock = cache.with_suffix(".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_EX)
        if cache.is_file():
            return _from_dict(json.loads(cache.read_text(encoding="utf-8")))
        data = _build_data(str(root), as_of, digest)
        temporary = cache.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(asdict(data), ensure_ascii=False), encoding="utf-8")
        temporary.replace(cache)
        return data
    finally:
        os.close(descriptor)


def _money(value: float, decimals: int = 0) -> str:
    return f"${value:,.{decimals}f}"


def _compact_count(value: int) -> str:
    if value >= 1_000 and value % 1_000 == 0:
        return f"{value // 1_000}K"
    return f"{value:,}"


def _logo() -> str:
    return landing_chrome.logo()


def render(data: LandingData, *, variant: Literal["live", "holding"],
           package_published: bool = PACKAGE_PUBLISHED) -> str:
    """Render one page. Only the board state and indexing metadata vary."""
    leader, cheapest = data.leader, data.cheapest
    tied_others = len(data.tie) - 1
    board = (f'<a class="button primary" href="{DECIDE_PATH}">Open the board</a>' if variant == "live"
             else '<span class="board-status">Board opening soon</span>')
    board_compact = (f'<a class="button primary" href="{DECIDE_PATH}">Open the board</a>'
                     if variant == "live" else '<span class="board-status">Board opening soon</span>')
    graph_link = '<a href="/graph/">Explore the graph</a>' if variant == "live" else ""
    install = ('<pre class="install" aria-label="First run">'
               + "\n".join(f'<code>{line}</code>' for line in FIRST_RUN) + '</pre>'
               if package_published else
               '<p class="release-note">CLI, API and MCP. Install instructions arrive with the public release.</p>')
    guide_href = "#agents"
    canonical = '<link rel="canonical" href="https://modelspec.dev/">\n'
    robots = ''
    forward = ""
    if variant == "live":
        query_keys = json.dumps(DECIDE_QUERY_KEYS, separators=(",", ":"))
        hash_keys = json.dumps(DECIDE_HASH_KEYS, separators=(",", ":"))
        forward = (
            "<script>(()=>{const u=new URL(location.href),"
            f"q={query_keys},h={hash_keys};"
            "if(q.some(k=>u.searchParams.has(k))||h.some(k=>"
            "new URLSearchParams(u.hash.slice(1)).has(k)))"
            f"location.replace('{DECIDE_PATH}'+u.search+u.hash)"
            "})()</script>\n"
        )
    routes = "".join(
        '<div class="route"><span class="ticket">T-{0:04d}</span><span class="template">{1}</span>'
        '<span>{2}</span><span class="route-cost">{3}</span></div>'.format(
            4812 + index, html.escape(route.id), html.escape(route.model),
            _money(route.cost, 3))
        for index, route in enumerate(data.routes)
    )
    options = "".join(
        f'<option value="{html.escape(model.id)}">{html.escape(model.name)}</option>'
        for model in sorted(data.models, key=lambda model: model.name)
    )
    payload = json.dumps(asdict(data), separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")
    date_label = date.fromisoformat(data.as_of).strftime("%-d %B %Y")
    task_label = (f"{_compact_count(data.task_input_tokens)} in / "
                  f"{_compact_count(data.task_output_tokens)} out")
    trust_source = (
        '<h3>Every number is one click from its source.</h3><p>Which benchmark, which date, '
        "who ran it. Independent results sit beside the lab's own claims, and each is labelled.</p>"
        if variant == "live" else
        '<h3>Every number has a source.</h3><p>Which benchmark, which date, who ran it. '
        'When the board opens, each one is a click away.</p>'
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">{forward}<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESCRIPTION}">
<meta property="og:description" content="{DESCRIPTION}">
{robots}{canonical}{brand.head_links()}{social_cards.social_meta_for_page("/", data)}<link rel="stylesheet" href="/{ASSET_DIR}/landing.css"></head>
<body><div class="axis" aria-hidden="true"></div>
<header>{_logo()}<span class="wordmark"><b>Model</b>Spec</span><nav><a href="#receipt">What it costs you</a><a href="#agents">For agents</a><a href="/pricing/">Pricing</a><a href="#pick-a-model">Test your pick</a>{board}</nav></header>
<main><section class="hero"><div class="hero-copy"><h1>Your model is a guess.</h1>
<p class="fud"><span class="desktop-only">{social_cards.landing_tie_line(data)} Benchmarks disagree, leaderboards reshuffle, and nothing in your stack will ever tell you that you chose wrong.</span><span class="mobile-only">{social_cards.landing_tie_line(data)} Nothing in your stack will tell you.</span></p>
<p class="close">ModelSpec shows you the model your job needs, from sourced evidence. Nobody pays to rank higher. When one model wins, we say so. When it's a tie, we hand you the cheapest.</p>
<div class="actions">{board}<a class="button secondary" href="#agents">Give it to your agents</a></div></div>
<figure class="plot"><div class="chips" aria-hidden="true"><span data-stage="1">The top estimate</span><span data-stage="2">Can't be told apart from it</span><span data-stage="3">The cheapest of those</span></div>
<svg id="plot" viewBox="0 0 680 560" role="img" aria-label="{html.escape(cheapest.name)} is in the tie at {_money(cheapest.cost, 3)} a task: {data.ratio:.1f}× less."></svg>
<figcaption id="plot-caption"></figcaption></figure></section>
<section class="receipt" id="receipt"><div><h2><span class="desktop-only">Same job. </span>Tied on the evidence. {_money(data.monthly_gap)} a month apart.</h2>
<p>{html.escape(leader.name)} and {html.escape(cheapest.name)} both qualify for a budget coding agent, and their coding estimates overlap. The evidence can't say one is better. At {data.monthly_tasks:,} tasks a month, one costs {_money(data.leader_monthly)}. The other costs {_money(data.cheapest_monthly)}.</p>
<p class="note">Published prices, {date_label} snapshot. Your token counts change the numbers, and the board does the arithmetic in the open.</p></div>
<div class="paper"><b>One month of coding tasks</b><span>{data.monthly_tasks:,} tasks · {task_label}</span><hr>
<div><span>{html.escape(leader.name)}</span><span>{_money(data.leader_monthly, 2)}</span></div><small>{_money(leader.cost, 3)} × {data.monthly_tasks:,}</small>
<div><span>{html.escape(cheapest.name)}</span><span>{_money(data.cheapest_monthly, 2)}</span></div><small>{_money(cheapest.cost, 3)} × {data.monthly_tasks:,}</small><hr>
<div><b>Difference</b><b>{_money(data.monthly_gap, 2)}</b></div><div class="green"><span>Evidence separates them?</span><span>No</span></div></div></section>
<section class="agents" id="agents"><div><h2>Your agents pick a model thousands of times a day.</h2>
<p><span class="desktop-only">Most pick the same expensive one every time, because someone hard-coded it last quarter. Give them the board as a command. One offline call per task picks the model that fits that task, explains why, and gives the same answer every time for the same facts.</span><span class="mobile-only">Give them the board as a command. One offline call per task, explained, and the same answer every time for the same facts.</span></p>
<div class="install-row">{install}<a href="{guide_href}">Read the agent guide</a></div><p class="note">Also as an API, and as an MCP server your agent platform can call.</p></div>
<div class="terminal"><div class="terminal-title">orchestrator — routing today's tickets</div><div class="routes">{routes}<div class="route-total"><span>same answer for the same spec and snapshot, every time</span><span>{len(data.routes)} of {data.template_count} templates · the others' top result has no published price</span></div></div></div></section>
<section class="challenge" id="pick-a-model"><h2>Think you know the best coding model?</h2><form id="pick-form"><label for="model-pick"><span class="desktop-only">Put your pick on the board. See exactly where it lands, and why.</span><span class="mobile-only">Put your pick on the board and see where it lands.</span></label><div><select id="model-pick">{options}</select><button type="submit">Check my pick</button></div><output id="pick-result" aria-live="polite">Choose a model to compare with the top estimate.</output></form></section>
<section class="trust"><div>{trust_source}<a href="/method/">How we decide</a></div><div><h3>Unknown means unknown.</h3><p>A model with no published answer to your question stays on the board as "may qualify". It never becomes a zero, and it never quietly disappears.</p></div><div><h3>Nobody pays to rank higher.</h3><p>No referral fees, no paid placement, no sponsored slots. It's a published commitment you can check.</p></div></section></main>
<footer><span>© Sparks and Sawdust LLC</span>{graph_link}<a href="/method/">How we decide</a><a href="/pricing/">Pricing</a><a href="/legal/terms/">Terms</a><a href="/legal/privacy/">Privacy</a><a href="/legal/neutrality/">Neutrality commitment</a><span class="snapshot">Snapshot of {date_label} · {len(data.models)} models · {data.benchmark_count} benchmarks</span></footer>
<div class="sticky">{board_compact}<a class="button secondary" href="#agents">Agents</a></div>
<script id="{DATA_ID}" type="application/json">{payload}</script><script src="/{ASSET_DIR}/landing.js" defer></script></body></html>\n'''


def extract_data(page: str) -> LandingData:
    start = page.index(f'<script id="{DATA_ID}" type="application/json">')
    start = page.index(">", start) + 1
    end = page.index("</script>", start)
    raw = json.loads(page[start:end])
    return _from_dict(raw)


def write(tree: Path, data: LandingData, *, variant: Literal["live", "holding"],
          package_published: bool = PACKAGE_PUBLISHED) -> None:
    target = tree
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(
        render(data, variant=variant, package_published=package_published), encoding="utf-8")
    assets = tree / ASSET_DIR
    assets.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent / "landing_assets"
    for name in ("landing.css", "landing.js"):
        (assets / name).write_bytes((source / name).read_bytes())
