"""Render page-specific social cards from build data with Playwright."""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from pipeline import entity

if TYPE_CHECKING:
    from pipeline.landing import LandingData, PlotModel

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1200
HEIGHT = 630
LANDING_IMAGE = "og-card-landing.png"
DECIDE_IMAGE = "og-card-decide.png"
PRICING_IMAGE = "og-card-pricing.png"
RENDER_ENV = "MODELSPEC_RENDER_SOCIAL_CARDS"


def render_enabled() -> bool:
    """True when the site build must render the PNG cards (needs npm and Chromium)."""
    return os.environ.get(RENDER_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class SocialCard:
    """One social-card render request."""

    filename: str
    alt: str
    headline: str
    content: str
    #: ``long`` sets a two-sentence headline smaller so it keeps its lines.
    headline_class: str = ""


@dataclass(frozen=True)
class CardRegistration:
    """A card factory and the page whose metadata points at its output."""

    page: str
    title: str
    filename: str
    factory: Callable[[LandingData | None], SocialCard]
    source_page: Path | None = None


def landing_tie_line(data: LandingData) -> str:
    """The landing card's data sentence, shared with its HTML assertion."""
    others = len(data.tie) - 1
    if others == 0:
        return "On coding, the evidence separates the top model from every other."
    models = "model" if others == 1 else "models"
    return (
        f"On coding, the evidence can't tell {others} {models} apart from the top one. "
        f"The cheapest costs {data.ratio:.1f}× less."
    )


def _point(model: PlotModel, data: LandingData) -> tuple[float, float]:
    import math

    axes = data.axes
    x = 34 + 362 * (
        (math.log(model.cost) - math.log(axes.cost_min))
        / (math.log(axes.cost_max) - math.log(axes.cost_min))
    )
    y = 226 - 180 * (
        (model.estimate - axes.capability_min)
        / (axes.capability_max - axes.capability_min)
    )
    return x, y


def _boxes_intersect(first: tuple[float, float, float, float],
                     second: tuple[float, float, float, float]) -> bool:
    return (
        min(first[2], second[2]) > max(first[0], second[0])
        and min(first[3], second[3]) > max(first[1], second[1])
    )


def _callout_position(data: LandingData) -> tuple[float, float, float, float]:
    """Place the landing label without covering any plotted point."""
    point_x, point_y = _point(data.cheapest, data)
    scale = 420 / 430
    y_offset = (270 - 270 * scale) / 2
    css_x = point_x * scale
    css_y = y_offset + point_y * scale
    width, height, gap = 190, 72, 12
    point_radius = 8
    point_boxes = []
    for model in data.models:
        x, y = _point(model, data)
        radius = 8 if model.id == data.cheapest_id else 5
        point_boxes.append((
            x * scale - radius * scale,
            y_offset + y * scale - radius * scale,
            x * scale + radius * scale,
            y_offset + y * scale + radius * scale,
        ))
    candidates = (
        (css_x + point_radius + gap, css_y - height / 2),
        (css_x - point_radius - gap - width, css_y - height / 2),
        (css_x - width / 2, css_y - point_radius - gap - height),
        (css_x - width / 2, css_y + point_radius + gap),
        (css_x + point_radius + gap, css_y - point_radius - gap - height),
        (css_x - point_radius - gap - width, css_y - point_radius - gap - height),
        (css_x + point_radius + gap, css_y + point_radius + gap),
        (css_x - point_radius - gap - width, css_y + point_radius + gap),
    )
    for left, top in candidates:
        box = (left, top, left + width, top + height)
        if (left >= 8 and top >= 8 and box[2] <= 412 and box[3] <= 232
                and not any(_boxes_intersect(box, point) for point in point_boxes)):
            leader_x = min(max(css_x, left), left + width) / scale
            leader_css_y = min(max(css_y, top), top + height)
            leader_y = (leader_css_y - y_offset) / scale
            return left, top, leader_x, leader_y
    # Dense plots get a label lane above the SVG instead of losing evidence.
    left, top = 108, -50
    return left, top, (left + width / 2) / scale, 0


def _landing_plot(data: LandingData) -> str:
    circles = []
    cheapest_point = _point(data.cheapest, data)
    for model in data.models:
        x, y = _point(model, data)
        colour = "#3FB68B" if model.id == data.cheapest_id else ("#5AA9EC" if model.tied else "#738097")
        radius = 8 if model.id == data.cheapest_id else 5
        circles.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{colour}"'
            f' data-plot-point data-tied="{str(model.tied).lower()}"'
            f'{" data-cheapest-point" if model.id == data.cheapest_id else ""}'
            f' opacity="{1 if model.tied else .45}"/>'
        )
    point_x, point_y = cheapest_point
    callout_left, callout_top, leader_end_x, leader_end_y = _callout_position(data)
    return (
        '<div class="plot" aria-label="A compact view of the landing tie plot">'
        '<svg viewBox="0 0 430 270" aria-hidden="true">'
        '<line class="y-axis" data-y-axis x1="24" y1="18" x2="24" y2="240"/>'
        '<line class="x-axis" x1="24" y1="240" x2="414" y2="240"/>'
        + "".join(circles)
        + f'<line class="callout-leader" x1="{point_x:.1f}" y1="{point_y:.1f}" '
        f'x2="{leader_end_x:.1f}" y2="{leader_end_y:.1f}"/></svg>'
        f'<em data-cheapest-callout style="left:{callout_left:.1f}px;top:{callout_top:.1f}px">'
        f'{html.escape(data.cheapest.name)}</em>'
        '<span data-y-axis-label>capability estimate</span><b>cost per task →</b></div>'
    )


def landing_card(data: LandingData) -> SocialCard:
    """Create the landing card from the same computed data as the page."""
    from pipeline.landing import HEADLINE, HEADLINE_LEAD

    tie_line = landing_tie_line(data)
    return SocialCard(
        filename=LANDING_IMAGE,
        alt=f"ModelSpec. {HEADLINE} {tie_line}",
        headline=html.escape(HEADLINE_LEAD),
        content=f'<p class="tie-line">{html.escape(tie_line)}</p>{_landing_plot(data)}',
        headline_class="long",
    )


def decide_card() -> SocialCard:
    """Create the decision-board card; its facet art makes no data claims."""
    facets = "".join(
        f'<li><i aria-hidden="true"></i>{label}</li>'
        for label in ("Doesn't matter", "Must", "Prefer")
    )
    return SocialCard(
        filename=DECIDE_IMAGE,
        alt="ModelSpec Decide: Which AI model fits your job?",
        headline="Which AI model<br>fits your job?",
        content=f'<ul class="facets">{facets}</ul>',
    )


def pricing_card() -> SocialCard:
    """Create the pricing card from the tiers and production feature flags."""
    from pipeline import pricing, worker_flags

    tiers = pricing.load_tiers(ROOT)
    variables = worker_flags.production_vars(ROOT)
    x402_live = pricing.x402_is_live(
        worker_flags.enabled(variables, "X402_ENABLED"),
        worker_flags.enabled(variables, "X402_MAINNET"),
    )
    agent_line, rate_range = pricing.hero_summary(
        tiers,
        access_enforced=worker_flags.enabled(variables, "ACCESS_ENFORCED"),
        x402_live=x402_live,
    )
    return SocialCard(
        filename=PRICING_IMAGE,
        alt=f"ModelSpec pricing: People decide free. {agent_line} {rate_range}.",
        headline=f"People decide free.<br>{html.escape(agent_line)}",
        content=(f'<div class="pricing-rate"><span>Configured rates</span>'
                 f'<strong>{html.escape(rate_range)}</strong></div>'),
    )


def _landing_factory(data: LandingData | None) -> SocialCard:
    if data is None:
        raise ValueError("the landing social card requires LandingData")
    return landing_card(data)


def _decide_factory(data: LandingData | None) -> SocialCard:
    return decide_card()


def _pricing_factory(data: LandingData | None) -> SocialCard:
    return pricing_card()


CARD_REGISTRY = (
    CardRegistration(page="/", title=entity.TITLE,
                     filename=LANDING_IMAGE,
                     factory=_landing_factory),
    CardRegistration(
        page="/decide/",
        title="ModelSpec Facet Board · Decide",
        filename=DECIDE_IMAGE,
        factory=_decide_factory,
        source_page=ROOT / "web" / "decide.html",
    ),
    CardRegistration(page="/pricing/", title="ModelSpec pricing",
                     filename=PRICING_IMAGE, factory=_pricing_factory),
)


def card_for_page(page: str, data: LandingData | None = None) -> SocialCard:
    """Build the registered card for one public page."""
    registration = next(item for item in CARD_REGISTRY if item.page == page)
    return registration.factory(data)


def card_filenames() -> tuple[str, ...]:
    """Return the deploy allowlist from the registered definitions."""
    return tuple(item.filename for item in CARD_REGISTRY)


def social_meta_for_page(page: str, data: LandingData | None = None) -> str:
    """Build a page's social tags from its registered card mapping."""
    from pipeline import brand

    registration = next(item for item in CARD_REGISTRY if item.page == page)
    card = registration.factory(data)
    return brand.social_meta(
        registration.title,
        path=registration.page,
        image_name=card.filename,
        image_alt=card.alt,
    )


def render_card_html(card: SocialCard) -> str:
    """Render a self-contained template; callers only supply copy and art."""
    font_root = (ROOT / "site" / "fonts").as_uri()
    mark = (ROOT / "brand" / "2a" / "modelspec-mark-transparent.svg").read_text(
        encoding="utf-8"
    )
    mark = mark.replace("<metadata>", '<metadata style="display:none">', 1)
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Instrument;src:url("{font_root}/instrument-sans-latin-wdth-normal.woff2")}}
@font-face{{font-family:JetBrains;src:url("{font_root}/jetbrains-mono-latin.woff2")}}
*{{box-sizing:border-box}}html,body{{margin:0;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden}}
body{{background:#0B1426;color:#EEF2F7;font-family:Instrument,Arial,sans-serif;position:relative;padding:62px 74px 54px 92px;display:flow-root}}
body:before{{content:"";position:absolute;left:42px;top:0;bottom:0;width:3px;background:#F2C94C}}
body:after{{content:"";position:absolute;left:0;right:0;bottom:38px;height:5px;background:#3FB68B}}
.brand{{display:flex;align-items:center;gap:17px;font:650 27px Instrument;letter-spacing:-.5px;position:relative;z-index:2;width:max-content}}.brand svg{{width:52px;height:52px}}.brand span{{font-weight:400}}
h1{{font-size:64px;line-height:78px;letter-spacing:-2.7px;margin:68px 0 22px;width:620px;max-height:240px;overflow:hidden;overflow-wrap:anywhere;position:relative;z-index:1}}h1.long{{font-size:48px;line-height:58px;letter-spacing:-1.8px;margin:40px 0 20px;width:600px;max-height:232px}}.tie-line{{font:22px/1.45 JetBrains,monospace;color:#C7D1E0;width:590px;max-height:104px;overflow:hidden;overflow-wrap:anywhere;margin:0;position:relative;z-index:1}}
.plot{{position:absolute;right:56px;bottom:67px;width:420px;height:270px;color:#8491A5;font:13px JetBrains}}
.plot svg{{position:absolute;inset:0}}.plot .y-axis{{stroke:#F2C94C;stroke-width:2}}.plot .x-axis{{stroke:#3FB68B;stroke-width:4}}.plot .callout-leader{{stroke:#3FB68B;stroke-width:1.5}}.plot span{{position:absolute;right:406px;top:73px;width:34px;height:126px;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center}}.plot b{{position:absolute;right:8px;bottom:2px;font-weight:400}}
.plot em{{position:absolute;width:190px;height:72px;display:flex;align-items:center;padding:0 6px;background:transparent;color:#EEF2F7;font:600 14px/1.15 Instrument;font-style:normal;overflow:hidden;overflow-wrap:anywhere;text-shadow:-2px -2px 2px #0B1426,2px -2px 2px #0B1426,-2px 2px 2px #0B1426,2px 2px 2px #0B1426,0 0 5px #0B1426}}
.facets{{position:absolute;right:78px;top:182px;width:335px;margin:0;padding:0;list-style:none;font:24px JetBrains}}
.facets li{{display:flex;align-items:center;gap:18px;border-bottom:1px solid #2A3B5C;padding:20px 5px}}.facets i{{width:22px;height:22px;border:2px solid #5AA9EC;border-radius:3px}}.facets li:nth-child(2) i{{background:#F2C94C;border-color:#F2C94C}}.facets li:nth-child(3) i{{background:#3FB68B;border-color:#3FB68B}}
.pricing-rate{{position:absolute;right:78px;top:322px;width:420px;border-left:3px solid #5AA9EC;padding:10px 0 10px 24px}}.pricing-rate span{{display:block;color:#8491A5;font:18px JetBrains;margin-bottom:8px}}.pricing-rate strong{{display:block;color:#EEF2F7;font:600 30px Instrument}}
</style></head><body><div class="brand" data-content-block>{mark}<b>Model<span>Spec</span></b></div><h1 class="{card.headline_class}" data-content-block>{card.headline}</h1>{card.content.replace('class="tie-line"', 'class="tie-line" data-content-block').replace('class="plot"', 'class="plot" data-content-block').replace('class="facets"', 'class="facets" data-content-block')}</body></html>'''


def _render_jobs(jobs: list[dict[str, str]]) -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory(prefix="modelspec-social-cards-") as directory:
        manifest = Path(directory) / "manifest.json"
        report = Path(directory) / "layout.json"
        manifest.write_text(json.dumps(jobs), encoding="utf-8")
        subprocess.run(
            ["node", str(ROOT / "web" / "scripts" / "render-social-cards.mjs"),
             str(manifest), str(report)],
            cwd=ROOT,
            check=True,
        )
        return json.loads(report.read_text(encoding="utf-8"))


def render_card(card: SocialCard, out_path: Path) -> dict[str, object]:
    """Render one supplied card to PNG and return its Chromium layout report."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="modelspec-social-card-") as directory:
        source = Path(directory) / "card.html"
        source.write_text(render_card_html(card), encoding="utf-8")
        return _render_jobs([{"source": str(source), "output": str(out_path)}])[0]


def render(tree: Path, data: LandingData) -> list[SocialCard]:
    """Render all current cards to ``tree`` and fail on any browser error."""
    cards = [item.factory(data) for item in CARD_REGISTRY]
    tree.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="modelspec-social-cards-") as directory:
        scratch = Path(directory)
        jobs = []
        for index, card in enumerate(cards):
            source = scratch / f"card-{index}.html"
            source.write_text(render_card_html(card), encoding="utf-8")
            jobs.append({"source": str(source), "output": str(tree / card.filename)})
        _render_jobs(jobs)
    return cards


def sync_page_meta() -> None:
    """Replace registered static-page metadata between generated markers."""
    start = "<!-- social-card-meta:start -->"
    end = "<!-- social-card-meta:end -->"
    for registration in CARD_REGISTRY:
        if registration.source_page is None:
            continue
        source = registration.source_page.read_text(encoding="utf-8")
        before, separator, rest = source.partition(start)
        if not separator or end not in rest:
            raise ValueError(f"{registration.source_page} lacks social-card metadata markers")
        _, _, after = rest.partition(end)
        metadata = social_meta_for_page(registration.page)
        indented = "    " + metadata.rstrip().replace("\n", "\n    ")
        registration.source_page.write_text(
            f"{before}{start}\n{indented}\n    {end}{after}", encoding="utf-8"
        )


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "filenames":
        print(" ".join(card_filenames()))
    elif command == "sync-meta":
        sync_page_meta()
    else:
        raise SystemExit("usage: python -m pipeline.social_cards {filenames|sync-meta}")
