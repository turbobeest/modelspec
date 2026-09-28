"""Render page-specific social cards from build data with Playwright."""

from __future__ import annotations

import html
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

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
        + f'</svg><em>{html.escape(data.cheapest.name)}</em>'
        '<span>capability estimate</span><b>cost per task →</b></div>'
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


def _landing_factory(data: LandingData | None) -> SocialCard:
    if data is None:
        raise ValueError("the landing social card requires LandingData")
    return landing_card(data)


def _decide_factory(data: LandingData | None) -> SocialCard:
    return decide_card()


CARD_REGISTRY = (
    CardRegistration(page="/", title="ModelSpec — your model is a guess",
                     filename=LANDING_IMAGE,
                     factory=_landing_factory),
    CardRegistration(
        page="/decide/",
        title="ModelSpec Facet Board · Decide",
        filename=DECIDE_IMAGE,
        factory=_decide_factory,
        source_page=ROOT / "web" / "decide.html",
    ),
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
h1{{font-size:64px;line-height:78px;letter-spacing:-2.7px;margin:68px 0 22px;width:620px;max-height:240px;overflow:hidden;overflow-wrap:anywhere;position:relative;z-index:1}}.tie-line{{font:22px/1.45 JetBrains,monospace;color:#C7D1E0;width:590px;max-height:104px;overflow:hidden;overflow-wrap:anywhere;margin:0;position:relative;z-index:1}}
.plot{{position:absolute;right:56px;bottom:67px;width:420px;height:270px;color:#8491A5;font:13px JetBrains}}
.plot svg{{position:absolute;inset:0}}.plot .y-axis{{stroke:#F2C94C;stroke-width:2}}.plot .x-axis{{stroke:#3FB68B;stroke-width:4}}.plot span{{position:absolute;left:-52px;top:112px;transform:rotate(-90deg)}}.plot b{{position:absolute;right:8px;bottom:2px;font-weight:400}}
.plot em{{position:absolute;left:34px;top:7px;width:350px;font:600 16px/1.2 Instrument;font-style:normal;overflow-wrap:anywhere}}
.facets{{position:absolute;right:78px;top:182px;width:335px;margin:0;padding:0;list-style:none;font:24px JetBrains}}
.facets li{{display:flex;align-items:center;gap:18px;border-bottom:1px solid #2A3B5C;padding:20px 5px}}.facets i{{width:22px;height:22px;border:2px solid #5AA9EC;border-radius:3px}}.facets li:nth-child(2) i{{background:#F2C94C;border-color:#F2C94C}}.facets li:nth-child(3) i{{background:#3FB68B;border-color:#3FB68B}}
</style></head><body><div class="brand" data-content-block>{mark}<b>Model<span>Spec</span></b></div><h1 data-content-block>{card.headline}</h1>{card.content.replace('class="tie-line"', 'class="tie-line" data-content-block').replace('class="plot"', 'class="plot" data-content-block').replace('class="facets"', 'class="facets" data-content-block')}</body></html>'''


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
