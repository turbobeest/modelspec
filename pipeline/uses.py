"""Use-case and comparison pages, rendered from live decisions (MODEL-219).

One page per decision template (`registry/templates.yaml`) at `/use/<id>/`: the
engine's answer to that template on this build's snapshot, in /decide's three
bands, with the named blend and a link that opens the board with the template
applied. A template the snapshot can't answer still gets its page, which says
so and gives the engine's reason.

Comparison pages at `/compare/<domain>/<a>-vs-<b>/` pair the strongest models
in each domain a template ranks on, and only models with enough evidence to
band there. Each page gives both estimates with their ranges, P(best) in the
domain, and P(one scores at least as well as the other), and says whether that
separates them under /decide's own band rule. A pair without that evidence gets
no page.

No figure on these pages is typed: each comes from the engine's decision or
from a constant the engine itself uses, and `tests/test_uses.py` fails if a
digit reaches a page from anywhere else.
"""

from __future__ import annotations

import html
import json
import math
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import date
from itertools import combinations
from pathlib import Path
from typing import Any

from decision.bands import BAND_PROBABILITY, THIN_INTERVAL_WIDTH, Distribution, p_at_least
from decision.capability import _INTERVAL_Z
from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import RegistryError, default
from decision.templates import load_catalogue
from decision.vocabulary import _template_rows
from pipeline import brand, landing, landing_chrome
from pipeline.load import load_models

GH = "https://github.com/turbobeest/modelspec/blob/main/"
USE_ROOT = "/use/"
COMPARE_ROOT = "/compare/"
DECIDE_PATH = "/decide/"
ASSET = "landing-assets/uses.css"
#: How many of a domain's strongest banded models are paired with each other.
COMPARE_TOP = 6
#: The share of a normal inside ±`_INTERVAL_Z` sd: the level of every range.
INTERVAL_LEVEL = math.erf(_INTERVAL_Z / math.sqrt(2))


@dataclass(frozen=True)
class Estimate:
    domain: str
    value: float
    low: float
    high: float
    benchmarks: int
    direct: int


@dataclass(frozen=True)
class Row:
    """One model in a band, through its best offering."""

    model: str
    name: str
    score: float
    score_low: float
    score_high: float
    p_best: float | None
    p_beats_leader: float | None
    cost: float | None
    estimates: tuple[Estimate, ...]


@dataclass(frozen=True)
class BlendTerm:
    label: str
    share: float
    estimated: bool
    leaders: tuple[str, ...]
    p_best: float | None


@dataclass(frozen=True)
class Condition:
    text: str
    reason: str


@dataclass(frozen=True)
class UseCase:
    id: str
    name: str
    category: str
    category_name: str
    tier: str
    tier_name: str
    purpose: str
    tradeoff: str
    teaches: str
    domains: tuple[str, ...]
    musts: tuple[Condition, ...]
    prefers: tuple[Condition, ...]
    available: bool
    #: The engine's reason a template has no answer; None when it has one.
    reason: str | None
    leader: str | None
    best: tuple[Row, ...]
    rest: tuple[Row, ...]
    thin: tuple[Row, ...]
    may_qualify: int
    blend: tuple[BlendTerm, ...]

    @property
    def path(self) -> str:
        return f"{USE_ROOT}{self.id}/"


@dataclass(frozen=True)
class Side:
    model: str
    name: str
    estimate: Estimate
    #: P(best) among every model ranked in the domain.
    p_best: float | None


@dataclass(frozen=True)
class Comparison:
    domain: str
    domain_name: str
    #: The higher estimate first.
    a: Side
    b: Side
    #: P(a's score >= b's), and the reverse.
    p_a: float
    p_b: float
    #: Models ranked in the domain, the field P(best) is read against.
    field: int

    @property
    def separated(self) -> bool:
        return min(self.p_a, self.p_b) < BAND_PROBABILITY

    @property
    def path(self) -> str:
        first, second = sorted((_slug(self.a.model), _slug(self.b.model)))
        return f"{COMPARE_ROOT}{_slug(self.domain)}/{first}-vs-{second}/"


@dataclass(frozen=True)
class Pages:
    as_of: str
    band_probability: float
    thin_width: float
    interval_level: float
    categories: tuple[tuple[str, str], ...]
    tiers: tuple[tuple[str, str], ...]
    uses: tuple[UseCase, ...]
    comparisons: tuple[Comparison, ...]


def _slug(value: str) -> str:
    return value.replace("/", "-").replace("_", "-").replace(".", "-")


def _label(dimension: str, registry: Any) -> str:
    key = dimension.removeprefix("-")
    try:
        name = registry.domain(key).name
    except RegistryError:
        try:
            facet = registry.facet(key)
            name = facet.label or key
        except RegistryError:
            name = key
    return f"{name} (lower is better)" if dimension.startswith("-") else name


def _row(entry: Any, names: dict[str, str]) -> Row:
    return Row(
        model=entry.model, name=names.get(entry.model, entry.model),
        score=entry.score, score_low=entry.score_interval[0], score_high=entry.score_interval[1],
        p_best=entry.p_best, p_beats_leader=entry.p_beats_leader, cost=entry.cost_per_task,
        estimates=tuple(Estimate(item.dimension, item.value, item.interval[0], item.interval[1],
                                 item.benchmarks, item.direct_benchmarks)
                        for item in entry.estimates),
    )


def _use_case(template: dict[str, Any], loaded: Any, registry: Any, names: dict[str, str],
              categories: dict[str, str], tiers: dict[str, str]) -> UseCase:
    spec = parse_spec(template["spec"] | {"explain": "none"}, facets=registry.facet)
    answer = decide(spec, loaded, facets=registry.facet)
    bands = answer.bands
    total = sum(item["weight"] for item in template["weights"].values())
    return UseCase(
        id=template["id"], name=template["name"],
        category=template["category"], category_name=categories[template["category"]],
        tier=template["tier"], tier_name=tiers[template["tier"]],
        purpose=template["purpose"], tradeoff=template["tradeoff"], teaches=template["teaches"],
        domains=tuple(template["needs"]["domains"]),
        musts=tuple(Condition(row["condition"], row["reason"]) for row in template["where"]),
        prefers=tuple(Condition(f"{_label(key, registry)}: {item['weight'] / total:.0%}",
                                item["reason"])
                      for key, item in template["weights"].items()),
        available=template["available"], reason=template["unavailable_reason"],
        leader=None if bands is None else bands.leader,
        best=() if bands is None else tuple(_row(entry, names) for entry in bands.best),
        rest=() if bands is None else tuple(_row(entry, names) for entry in bands.rest),
        thin=() if bands is None else tuple(_row(entry, names) for entry in bands.thin),
        may_qualify=len({row.model for row in answer.may_qualify}),
        blend=tuple(BlendTerm(_label(term.dimension, registry), term.share, term.estimated,
                              tuple(names.get(model, model) for model in term.leaders),
                              term.p_best)
                    for term in answer.blend),
    )


def _comparisons(domain: str, loaded: Any, registry: Any, names: dict[str, str],
                 candidate: dict[str, str]) -> list[Comparison]:
    """Pairs among the domain's strongest models with enough evidence to band."""
    spec = parse_spec({"spec_version": 1, "where": ["model.lifecycle = active"],
                       "optimize": {"max": domain}, "explain": "none"}, facets=registry.facet)
    bands = decide(spec, loaded, facets=registry.facet).bands
    if bands is None:
        return []
    field = len(bands.best) + len(bands.rest) + len(bands.thin)
    banded = sorted((*bands.best, *bands.rest), key=lambda entry: (-entry.estimates[0].value,
                                                                   entry.model))
    sides: list[tuple[Side, Distribution]] = []
    for entry in banded[:COMPARE_TOP]:
        # The estimate is the model's, so any of its candidates reads it.
        estimate = loaded.capability_estimate(candidate[entry.model], domain)
        item = entry.estimates[0]
        sides.append((Side(entry.model, names.get(entry.model, entry.model),
                           Estimate(domain, item.value, item.interval[0], item.interval[1],
                                    item.benchmarks, item.direct_benchmarks), entry.p_best),
                      Distribution(estimate.value, estimate.sd)))
    return [
        Comparison(domain=domain, domain_name=registry.domain(domain).name, a=a, b=b,
                   p_a=p_at_least(da, db), p_b=p_at_least(db, da), field=field)
        for (a, da), (b, db) in combinations(sides, 2)
    ]


def _build(root: Path, as_of: date) -> Pages:
    loaded = landing.loaded_snapshot(str(root), as_of,
                                     landing.input_digest(root, as_of, snapshot_only=True))
    registry = default()
    names = {card.model_id: card.display_name for card in load_models(root)}
    catalogue = load_catalogue(registry=registry)
    categories = {row["id"]: row["name"] for row in catalogue["categories"]}
    tiers = {row["id"]: row["name"] for row in catalogue["tiers"]}
    templates = _template_rows(loaded, registry, catalogue["templates"])
    uses = tuple(_use_case(row, loaded, registry, names, categories, tiers) for row in templates)
    domains = list(dict.fromkeys(domain for use in uses for domain in use.domains))
    candidate = {loaded.model_of(cid): cid for cid in loaded.candidates()}
    comparisons = tuple(pair for domain in domains
                        for pair in _comparisons(domain, loaded, registry, names, candidate))
    paths = [pair.path for pair in comparisons]
    if len(paths) != len(set(paths)):
        raise ValueError("two comparison pages share a path")
    return Pages(as_of=as_of.isoformat(), band_probability=BAND_PROBABILITY,
                 thin_width=THIN_INTERVAL_WIDTH, interval_level=INTERVAL_LEVEL,
                 categories=tuple(categories.items()), tiers=tuple(tiers.items()),
                 uses=uses, comparisons=comparisons)


def _rows(raw: list[dict[str, Any]]) -> tuple[Row, ...]:
    return tuple(Row(**(row | {"estimates": tuple(Estimate(**item) for item in row["estimates"])}))
                 for row in raw)


def _side_from(raw: dict[str, Any]) -> Side:
    return Side(**(raw | {"estimate": Estimate(**raw["estimate"])}))


def _from_dict(raw: dict[str, Any]) -> Pages:
    uses = tuple(UseCase(**(row | {
        "domains": tuple(row["domains"]),
        "musts": tuple(Condition(**item) for item in row["musts"]),
        "prefers": tuple(Condition(**item) for item in row["prefers"]),
        "best": _rows(row["best"]), "rest": _rows(row["rest"]), "thin": _rows(row["thin"]),
        "blend": tuple(BlendTerm(**(item | {"leaders": tuple(item["leaders"])}))
                       for item in row["blend"]),
    })) for row in raw["uses"])
    comparisons = tuple(Comparison(**(row | {"a": _side_from(row["a"]), "b": _side_from(row["b"])}))
                        for row in raw["comparisons"])
    return Pages(**(raw | {
        "categories": tuple(tuple(row) for row in raw["categories"]),
        "tiers": tuple(tuple(row) for row in raw["tiers"]),
        "uses": uses, "comparisons": comparisons,
    }))


def build_data(root_value: str, as_of: date) -> Pages:
    """Compute the pages' data once per repository input set, across build workers."""
    root = Path(root_value).resolve()
    digest = landing.input_digest(root, as_of, Path(__file__))
    cache = Path(tempfile.gettempdir()) / f"modelspec-uses-{digest}.json"
    if cache.is_file():
        return _from_dict(json.loads(cache.read_text(encoding="utf-8")))
    data = _build(root, as_of)
    temporary = cache.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(asdict(data), ensure_ascii=False), encoding="utf-8")
    temporary.replace(cache)
    return data


# ── formatting: every number on a page passes through one of these ─────────


def num(value: float) -> str:
    return f"{value:.2f}".replace("-", "−")


def pct(value: float) -> str:
    text = f"{value:.0%}"
    if text in {"0%", "100%"} and 0 < value < 1:
        text = f"{value:.2%}"
    return text


def money(value: float) -> str:
    return f"${value:,.3f}"


def when(data: Pages) -> str:
    return date.fromisoformat(data.as_of).strftime("%-d %B %Y")


def _e(text: str) -> str:
    return html.escape(text)


def _lower(text: str) -> str:
    """Lower-case a name for use mid-sentence, keeping acronyms such as EU."""
    return text if text[1:2].isupper() else text[:1].lower() + text[1:]


# ── rendering ────────────────────────────────────────────────────────────────


def _header() -> str:
    return (f'<header class="site-head">{landing_chrome.lockup()}<nav>'
            '<a href="/use/">Use cases</a><a href="/compare/">Comparisons</a>'
            '<a href="/method/">How it decides</a>'
            f'<a class="button primary" href="{DECIDE_PATH}">Open the board</a></nav></header>')


def _page(data: Pages, *, title: str, description: str, path: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{_e(title)} | ModelSpec</title>'
        f'<meta name="description" content="{_e(description)}">'
        f'<meta property="og:description" content="{_e(description)}">'
        f'<link rel="canonical" href="{brand.SITE}{path}">{brand.head_links()}'
        f'{brand.social_meta(_e(title), path=path)}'
        '<link rel="stylesheet" href="/landing-assets/landing.css">'
        '<link rel="stylesheet" href="/landing-assets/method.css">'
        f'<link rel="stylesheet" href="/{ASSET}">{landing_chrome.lockup_style()}</head>'
        f'<body>{_header()}<main class="uses">{body}</main>'
        f'{landing_chrome.footer(detail=f"Computed from the {when(data)} snapshot. Nobody pays to rank higher.")}'
        '</body></html>\n'
    )


def _range(low: float, high: float) -> str:
    return f"{num(low)} to {num(high)}"


def _evidence(estimate: Estimate) -> str:
    noun = "benchmark" if estimate.benchmarks == 1 else "benchmarks"
    return f"{estimate.benchmarks} {noun}, {estimate.direct} direct"


def _model_link(model: str, name: str) -> str:
    return f'<a href="/m/{_e(model)}/">{_e(name)}</a>'


def _band_table(rows: tuple[Row, ...], data: Pages, *, leader: str | None) -> str:
    head = ('<tr><th scope="col">Model</th><th scope="col">Score</th>'
            f'<th scope="col">{pct(data.interval_level)} range</th><th scope="col">P(best)</th>'
            '<th scope="col">P(at least the leader)</th><th scope="col">Cost per task</th>'
            '<th scope="col">Evidence</th></tr>')
    body = ""
    for row in rows:
        p_best = "—" if row.p_best is None else pct(row.p_best)
        beats = ("leader" if row.model == leader else
                 "—" if row.p_beats_leader is None else pct(row.p_beats_leader))
        cost = "no published price" if row.cost is None else money(row.cost)
        evidence = "; ".join(_evidence(item) for item in row.estimates) or "exact facts only"
        body += (f'<tr><th scope="row">{_model_link(row.model, row.name)}</th>'
                 f'<td>{num(row.score)}</td><td>{_range(row.score_low, row.score_high)}</td>'
                 f'<td>{p_best}</td><td>{beats}</td><td>{cost}</td><td>{evidence}</td></tr>')
    return f'<div class="table-wrap"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>'


def _verdict(use: UseCase, data: Pages) -> str:
    if not use.available:
        return ('<p class="verdict none"><b>No answer on this snapshot.</b> '
                f'{_e(use.reason or "")}</p>')
    if use.leader is None:
        return ('<p class="verdict thin"><b>Not enough evidence to name a best model.</b> Every '
                'ranked model has a capability range wider than '
                f'{num(data.thin_width)}, so none is banded. They are listed below as they are.</p>')
    leader = next(row for row in use.best if row.model == use.leader)
    if len(use.best) == 1:
        return (f'<p class="verdict"><b>{_e(leader.name)} leads, and the evidence separates it.</b> '
                f'No other model has a {pct(data.band_probability)} or better chance of scoring at '
                'least as well.</p>')
    others = [_e(row.name) for row in use.best if row.model != use.leader]
    each = "has" if len(others) == 1 else "each have"
    return (f'<p class="verdict"><b>The evidence can\'t separate {len(use.best)} models.</b> '
            f'{_e(leader.name)} has the top score. {", ".join(others)} {each} a '
            f'{pct(data.band_probability)} or better chance of scoring at least as well, so '
            'the board lists them together as best.</p>')


def _blend(use: UseCase) -> str:
    items = ""
    for term in use.blend:
        lead = ", ".join(_e(name) for name in term.leaders) or "no model with enough evidence"
        sure = "" if term.p_best is None else f", P(best on this alone) {pct(term.p_best)}"
        items += (f'<li><b>{pct(term.share)}</b><span>{_e(term.label)}'
                  f'{"" if term.estimated else ", exact"}</span>'
                  f'<small>Leads on this alone: {lead}{sure}</small></li>')
    return f'<ol class="blend">{items}</ol>' if items else ""


def _conditions(title: str, rows: tuple[Condition, ...]) -> str:
    items = "".join(f'<li><code>{_e(row.text)}</code><span>{_e(row.reason)}</span></li>'
                    for row in rows)
    return f'<div class="conditions"><h3>{title}</h3><ul>{items}</ul></div>' if items else ""


def use_page(use: UseCase, data: Pages) -> str:
    decide_href = f"{DECIDE_PATH}?template={use.id}" if use.available else DECIDE_PATH
    decide_label = "Open this on the board" if use.available else "Open the board"
    bands = ""
    if use.best:
        bands += f'<h2>Best</h2>{_band_table(use.best, data, leader=use.leader)}'
    if use.rest:
        bands += ('<h2>The rest</h2><p>Enough evidence, and the leader is ahead of each with '
                  f'better than {pct(1 - data.band_probability)} probability.</p>'
                  f'{_band_table(use.rest, data, leader=use.leader)}')
    if use.thin:
        bands += ('<h2>Not enough evidence</h2><p>A capability range wider than '
                  f'{num(data.thin_width)}. These are never banded with the leader, however high '
                  f'their score.</p>{_band_table(use.thin, data, leader=use.leader)}')
    if use.may_qualify:
        noun = "model" if use.may_qualify == 1 else "models"
        bands += (f'<p class="may">{use.may_qualify} more {noun} may qualify: a fact a Must '
                  'needs is not published for them yet. <a href="/method/#unknown">Unknown '
                  'is never a zero.</a></p>')
    blend = _blend(use)
    current = ' aria-current="page"'
    siblings = "".join(
        f'<li><a href="{other.path}"{current if other.id == use.id else ""}>'
        f'{_e(other.tier_name)}</a></li>'
        for other in data.uses if other.category == use.category)
    pairs = [pair for pair in data.comparisons if pair.domain in use.domains]
    compare = "".join(f'<li><a href="{pair.path}">{_e(pair.a.name)} vs {_e(pair.b.name)}, '
                      f'{_e(_lower(pair.domain_name))}</a></li>' for pair in pairs[:COMPARE_TOP])
    body = (
        f'<section class="use-hero"><p class="eyebrow">{_e(use.category_name)} · '
        f'{_e(use.tier_name)}</p><h1>{_e(use.name)}</h1><p class="lede">{_e(use.purpose)}</p>'
        f'<p class="tradeoff">{_e(use.tradeoff)}</p>{_verdict(use, data)}'
        f'<div class="actions"><a class="button primary" href="{decide_href}">{decide_label}</a>'
        f'<code>modelspec decide --template {_e(use.id)}</code></div></section>'
        f'<section class="answer"><p class="note">The {when(data)} snapshot, answered by the '
        'same engine as the board. A score is the weighted blend on the feasible set\'s scale. '
        '<a href="/method/#ties">How ties work</a>.</p>'
        f'{bands}</section>'
        + (f'<section class="how"><h2>What the ranking mixes</h2>{blend}<p>{_e(use.teaches)}</p>'
           '</section>' if blend else '')
        + '<section class="spec"><h2>The template</h2>'
        + _conditions("Must", use.musts) + _conditions("Prefer", use.prefers)
        + '<p>Change any of it on the board. The answer recomputes, and shows its work.</p></section>'
        + f'<nav class="related" aria-label="Related"><div><h2>{_e(use.category_name)}, other '
          f'trade-offs</h2><ul>{siblings}</ul></div>'
        + (f'<div><h2>Head to head</h2><ul>{compare}</ul></div>' if compare else '')
        + '</nav>'
    )
    title = f"Best AI model for {_lower(use.category_name)}: {_lower(use.tier_name)}"
    return _page(data, title=title, description=f"{use.purpose} {use.tradeoff}",
                 path=use.path, body=body)


def _side(side: Side, pair: Comparison) -> str:
    estimate = side.estimate
    p_best = "—" if side.p_best is None else pct(side.p_best)
    proxy = ("" if estimate.direct else
             f'<p class="warn">No direct measure of {_e(_lower(pair.domain_name))}: this estimate '
             'rests on proxy benchmarks only.</p>')
    return (f'<article><h2>{_model_link(side.model, side.name)}</h2><dl>'
            f'<dt>Estimate</dt><dd>{num(estimate.value)}</dd>'
            f'<dt>Range</dt><dd>{_range(estimate.low, estimate.high)}</dd>'
            f'<dt>P(best of {pair.field})</dt><dd>{p_best}</dd>'
            f'<dt>Evidence</dt><dd>{_evidence(estimate)}</dd></dl>{proxy}</article>')


def compare_page(pair: Comparison, data: Pages) -> str:
    a, b = pair.a, pair.b
    domain = _lower(pair.domain_name)
    if pair.separated:
        verdict = (f'<p class="verdict"><b>The evidence separates them: {_e(a.name)} is ahead '
                   f'on {_e(domain)}.</b> {_e(b.name)} has a {pct(pair.p_b)} chance of scoring at '
                   f'least as well. Below {pct(data.band_probability)}, the board ranks two '
                   'models apart.</p>')
    else:
        verdict = (f'<p class="verdict"><b>The evidence can\'t separate them on {_e(domain)}.</b> '
                   f'{_e(b.name)} has a {pct(pair.p_b)} chance of scoring at least as well as '
                   f'{_e(a.name)}. At {pct(data.band_probability)} or more, the board lists two '
                   'models together. Choose between them on cost, context or terms.</p>')
    uses = "".join(f'<li><a href="{use.path}">{_e(use.name)}</a></li>'
                   for use in data.uses if pair.domain in use.domains and use.available)
    body = (
        f'<section class="use-hero"><p class="eyebrow">Head to head · {_e(pair.domain_name)}</p>'
        f'<h1>{_e(a.name)} vs {_e(b.name)} for {_e(domain)}</h1>{verdict}'
        f'<div class="actions"><a class="button primary" href="{DECIDE_PATH}">Put both on the '
        'board</a></div></section>'
        f'<section class="pair">{_side(a, pair)}{_side(b, pair)}</section>'
        f'<section class="answer"><p class="note">Estimated ability in {_e(domain)}, on the '
        f'engine\'s shared scale, from every admitted benchmark; each range is the central '
        f'{pct(data.interval_level)}. P(best) is against the {pair.field} active models '
        f'ranked in this domain on the {when(data)} snapshot. <a href="/method/#estimate">How '
        'the estimate works</a>.</p></section>'
        + (f'<nav class="related" aria-label="Related"><div><h2>Use cases that rank on '
           f'{_e(domain)}</h2><ul>{uses}</ul></div></nav>' if uses else '')
    )
    title = f"{a.name} vs {b.name} for {domain}"
    description = (f"{a.name} and {b.name} compared on {domain}: estimates, ranges, P(best) and "
                   "whether the evidence separates them.")
    return _page(data, title=title, description=description, path=pair.path, body=body)


def use_index(data: Pages) -> str:
    by_cell = {(use.category, use.tier): use for use in data.uses}
    head = "".join(f'<th scope="col">{_e(name)}</th>' for _, name in data.tiers)
    rows = ""
    for category, name in data.categories:
        cells = ""
        for tier, _ in data.tiers:
            use = by_cell.get((category, tier))
            cells += ("<td>—</td>" if use is None else
                      f'<td><a href="{use.path}">{_e(use.tradeoff)}</a></td>')
        rows += f'<tr><th scope="row">{_e(name)}</th>{cells}</tr>'
    body = ('<section class="use-hero"><p class="eyebrow">Use cases</p><h1>Which AI model for '
            'the job?</h1><p class="lede">Each page is one template, answered by the engine on '
            f'the {when(data)} snapshot: the models the evidence can\'t separate, the rest, and '
            'the ones with too little evidence to say.</p></section>'
            f'<section class="answer"><div class="table-wrap"><table class="grid"><thead><tr>'
            f'<th scope="col"><span class="visually-hidden">Use case</span></th>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>')
    return _page(data, title="Which AI model for the job", path=USE_ROOT, body=body,
                 description="Use-case answers from sourced evidence: best, balanced, budget, "
                             "fastest and private choices, with ties stated plainly.")


def compare_index(data: Pages) -> str:
    state = {True: "separated", False: "can't separate"}
    sections = ""
    for domain in dict.fromkeys(pair.domain for pair in data.comparisons):
        pairs = [pair for pair in data.comparisons if pair.domain == domain]
        items = "".join(
            f'<li><a href="{pair.path}">{_e(pair.a.name)} vs {_e(pair.b.name)}</a>'
            f'<span>{state[pair.separated]}</span></li>'
            for pair in pairs)
        sections += f'<h2>{_e(pairs[0].domain_name)}</h2><ul class="pairs">{items}</ul>'
    body = ('<section class="use-hero"><p class="eyebrow">Comparisons</p><h1>Head to head, '
            'where the evidence can answer.</h1><p class="lede">Pairs of the strongest models '
            'in each domain, and only models with enough evidence. Each page says whether the '
            f'evidence separates them.</p></section><section class="answer">{sections}</section>')
    return _page(data, title="AI model comparisons", path=COMPARE_ROOT, body=body,
                 description="Model-versus-model comparisons with ranges, P(best), and a plain "
                             "answer on whether the evidence separates them.")


def write(tree: Path, data: Pages) -> dict[str, Any]:
    """Write every page and the stylesheet. Returns the sitemap paths."""
    pages = {USE_ROOT: use_index(data), COMPARE_ROOT: compare_index(data)}
    pages |= {use.path: use_page(use, data) for use in data.uses}
    pages |= {pair.path: compare_page(pair, data) for pair in data.comparisons}
    for path, text in pages.items():
        out = tree / path.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    asset = tree / ASSET
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_bytes((Path(__file__).parent / "landing_assets" / "uses.css").read_bytes())
    return {"sitemap_paths": list(pages)}
