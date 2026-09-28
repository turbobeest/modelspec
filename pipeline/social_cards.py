"""Render page-specific social cards from build data with Playwright."""

from __future__ import annotations

import html
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipeline.landing import LandingData, PlotModel

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1200
HEIGHT = 630
LANDING_IMAGE = "og-card-landing.png"
DECIDE_IMAGE = "og-card-decide.png"


@dataclass(frozen=True)
class SocialCard:
    """One card render request; pricing can add another instance later."""

    filename: str
    alt: str
    headline: str
    content: str


def landing_tie_line(data: LandingData) -> str:
    """The landing card's data sentence, shared with its HTML assertion."""
    return (
        f"The evidence can't tell {len(data.tie) - 1} models apart from the top one. "
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


def _landing_plot(data: LandingData) -> str:
    circles = []
    for model in data.models:
        x, y = _point(model, data)
        colour = "#3FB68B" if model.id == data.cheapest_id else ("#5AA9EC" if model.tied else "#738097")
        radius = 8 if model.id == data.cheapest_id else 5
        circles.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{colour}"'
            f' opacity="{1 if model.tied else .45}"/>'
        )
    return (
        '<div class="plot" aria-label="A compact view of the landing tie plot">'
        '<svg viewBox="0 0 430 270" aria-hidden="true">'
        '<line class="y-axis" x1="24" y1="18" x2="24" y2="240"/>'
        '<line class="x-axis" x1="24" y1="240" x2="414" y2="240"/>'
        + "".join(circles)
        + '</svg><span>capability estimate</span><b>cost per task →</b></div>'
    )


def landing_card(data: LandingData) -> SocialCard:
    """Create the landing card from the same computed data as the page."""
    tie_line = landing_tie_line(data)
    return SocialCard(
        filename=LANDING_IMAGE,
        alt=f"ModelSpec: Your model is a guess. {tie_line}",
        headline="Your model is a guess.",
        content=f'<p class="tie-line">{html.escape(tie_line)}</p>{_landing_plot(data)}',
    )


def decide_card() -> SocialCard:
    """Create the decision-board card; its facet art makes no data claims."""
    facets = "".join(
        f'<li><i aria-hidden="true"></i>{label}</li>'
        for label in ("Doesn't matter", "Must", "Prefer")
    )
    return SocialCard(
        filename=DECIDE_IMAGE,
        alt="ModelSpec Decide: Set what matters. Watch the field narrow.",
        headline="Set what matters.<br>Watch the field narrow.",
        content=f'<ul class="facets">{facets}</ul>',
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
.brand{{display:flex;align-items:center;gap:17px;font:650 27px Instrument;letter-spacing:-.5px;position:relative;z-index:2}}.brand svg{{width:52px;height:52px}}.brand span{{font-weight:400}}
h1{{font-size:70px;line-height:.98;letter-spacing:-3px;margin:68px 0 22px;max-width:720px;position:relative;z-index:1}}.tie-line{{font:22px/1.45 JetBrains,monospace;color:#C7D1E0;max-width:690px;margin:0;position:relative;z-index:1}}
.plot{{position:absolute;right:56px;bottom:67px;width:420px;height:270px;color:#8491A5;font:13px JetBrains}}
.plot svg{{position:absolute;inset:0}}.plot .y-axis{{stroke:#F2C94C;stroke-width:2}}.plot .x-axis{{stroke:#3FB68B;stroke-width:4}}.plot span{{position:absolute;left:-52px;top:112px;transform:rotate(-90deg)}}.plot b{{position:absolute;right:8px;bottom:2px;font-weight:400}}
.facets{{position:absolute;right:78px;top:182px;width:335px;margin:0;padding:0;list-style:none;font:24px JetBrains}}
.facets li{{display:flex;align-items:center;gap:18px;border-bottom:1px solid #2A3B5C;padding:20px 5px}}.facets i{{width:22px;height:22px;border:2px solid #5AA9EC;border-radius:3px}}.facets li:nth-child(2) i{{background:#F2C94C;border-color:#F2C94C}}.facets li:nth-child(3) i{{background:#3FB68B;border-color:#3FB68B}}
</style></head><body><div class="brand">{mark}<b>Model<span>Spec</span></b></div><h1>{card.headline}</h1>{card.content}</body></html>'''


def render(tree: Path, data: LandingData) -> list[SocialCard]:
    """Render all current cards to ``tree`` and fail on any browser error."""
    cards = [landing_card(data), decide_card()]
    tree.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="modelspec-social-cards-") as directory:
        scratch = Path(directory)
        jobs = []
        for index, card in enumerate(cards):
            source = scratch / f"card-{index}.html"
            source.write_text(render_card_html(card), encoding="utf-8")
            jobs.append({"source": str(source), "output": str(tree / card.filename)})
        manifest = scratch / "manifest.json"
        manifest.write_text(json.dumps(jobs), encoding="utf-8")
        subprocess.run(
            ["node", str(ROOT / "web" / "scripts" / "render-social-cards.mjs"), str(manifest)],
            cwd=ROOT,
            check=True,
        )
    return cards
