"""MODEL-24 part 2: one stylesheet for every page on both sites.

The landings and the wizard are hand-written HTML. Their colours and fonts were
copied in by hand and had drifted from the generated pages, so they now link
`/instrument.css`, which the build writes from the same constant the generated
pages inline.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import build as builder  # noqa: E402
from pipeline import render as r  # noqa: E402
from pipeline.export import Build  # noqa: E402
from pipeline.load import Benchmark, Catalogue  # noqa: E402

BUILD = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))

STATIC_PAGES = {
    "modelspec landing": ROOT / "site/holding/index.html",
    "benchgraph landing": ROOT / "site/benchgraph/index.html",
    "benchgraph landing template": ROOT / "site/benchgraph/build/index.tpl.html",
    "wizard": ROOT / "web3d/downselect.v2.html",
    "graph explorer": ROOT / "web3d/explorer.html",
}


def _inline_css(page: str) -> str:
    return re.search(r"<style>(.*?)</style>", page, re.S).group(1)


# ── one source for the tokens ────────────────────────────────────────────────

def test_instrument_css_is_written_to_both_sites_and_matches_the_inlined_sheet(tmp_path) -> None:
    ms, bg = tmp_path / "modelspec", tmp_path / "benchgraph"
    builder._ship_instrument(ROOT, ms, bg)
    inlined = _inline_css(r.not_found("benchgraph", BUILD, r.BG_NAV, "https://benchgraph.dev/"))
    for site in (ms, bg):
        sheet = (site / "instrument.css").read_text(encoding="utf-8")
        assert sheet == inlined
        assert "--accent:#f5b342;" in sheet
        assert '[data-site="benchgraph"]{--accent:#38bdf8}' in sheet
        assert (site / "fonts" / "archivo-latin.woff2").is_file()
        assert (site / "fonts" / "jetbrains-mono-latin.woff2").is_file()
        assert (site / "fonts" / "JetBrainsMono-OFL.txt").is_file()


def test_the_section_counter_is_scoped_to_the_generated_page_column() -> None:
    """A bare h2 rule would number and indent every heading on the landings."""
    assert re.search(r"(?:^|\})h2(?:::before)?\{", r.CSS, re.M) is None
    assert ":where(.page) h2{" in r.CSS
    assert ":where(.page) h2::before{content:counter(sec" in r.CSS


def _bare_rule(selector: str) -> str:
    rule = re.search(r"(?:^|\})" + selector + r"\{([^}]*)\}", r.CSS, re.M)
    assert rule, f"{selector} is not declared"
    return rule.group(1)


def test_long_unbroken_text_stays_inside_a_phone_width() -> None:
    """At 375px the neutrality page's JSON block made the page 1,069px wide, and
    a repository URL used as link text made a benchmark page 396px wide."""
    assert "overflow-x:auto" in _bare_rule("pre")
    assert "overflow-wrap:break-word" in _bare_rule("p")
    assert "overflow-wrap:break-word" in _bare_rule("li")


# ── the static pages ─────────────────────────────────────────────────────────

def _stylesheets(page: str) -> list[str]:
    return re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"|'
                      r'<link[^>]*href="([^"]+)"[^>]*rel="stylesheet"', page)


def test_each_static_page_links_the_shared_sheet() -> None:
    for name, path in STATIC_PAGES.items():
        page = path.read_text(encoding="utf-8")
        assert '<link rel="stylesheet" href="/instrument.css">' in page, name


def _styles(page: str) -> str:
    """Every stylesheet and style attribute on the page, not its SVG artwork."""
    return ("".join(re.findall(r"<style>(.*?)</style>", page, re.S))
            + "".join(re.findall(r'style="([^"]*)"', page)))


def test_no_static_page_requests_space_grotesk() -> None:
    """The benchgraph logo's generated SVG still names the face in a presentation
    attribute. That requests nothing, and the page's CSS outranks it."""
    for name, path in STATIC_PAGES.items():
        page = path.read_text(encoding="utf-8")
        assert "Space+Grotesk" not in page, name
        assert "Space Grotesk" not in _styles(page), name


def test_no_static_page_loads_a_font_from_a_cdn() -> None:
    for name, path in STATIC_PAGES.items():
        page = path.read_text(encoding="utf-8")
        remote = [href for pair in _stylesheets(page) for href in pair
                  if href.startswith(("http:", "https:", "//"))]
        assert remote == [], (name, remote)
        assert "@font-face" not in page, name
        assert "fonts.googleapis.com" not in page, name
        assert "fonts.gstatic.com" not in page, name
        assert "/fonts/jetbrains-mono-latin.woff2" in page, name


def test_static_page_styles_take_every_colour_and_family_from_a_token() -> None:
    """Hex literals in a static page are how the drift started."""
    for name, path in STATIC_PAGES.items():
        styles = _styles(path.read_text(encoding="utf-8"))
        assert re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", styles) == [], name
        families = re.findall(r"font-family:\s*([^;}]+)", styles)
        assert all(f.strip().startswith("var(--") for f in families), (name, families)


def test_the_benchgraph_landing_root_is_marked_as_benchgraph() -> None:
    for key in ("benchgraph landing", "benchgraph landing template"):
        page = STATIC_PAGES[key].read_text(encoding="utf-8")
        assert '<html lang="en" data-site="benchgraph">' in page, key


def test_the_benchgraph_landing_matches_its_template_outside_the_placeholders() -> None:
    template = STATIC_PAGES["benchgraph landing template"].read_text(encoding="utf-8")
    page = STATIC_PAGES["benchgraph landing"].read_text(encoding="utf-8")
    literal = re.split(r"(\{\{[A-Z_]+\}\})", template)
    pattern = "".join(".*?" if re.fullmatch(r"\{\{[A-Z_]+\}\}", part) else re.escape(part)
                      for part in literal)
    assert re.fullmatch(pattern, page, re.S), "index.html has drifted from index.tpl.html"


def _today(page: str) -> str:
    match = re.search(r'<p class="today">.*?</p>', page)
    assert match, "landing has no p.today"
    return match.group(0)


def test_the_benchgraph_landing_does_not_hardcode_headline_counts() -> None:
    """Baked 164/549/10,887 read as the page count and went stale in git."""
    for key in ("benchgraph landing", "benchgraph landing template"):
        today = _today(STATIC_PAGES[key].read_text(encoding="utf-8"))
        assert "{{N_PAGES}}" in today and "{{N_BENCH}}" in today, key
        assert "{{N_MODELS}}" in today and "{{N_SCORES}}" in today, key
        assert "benchmark pages" in today and "benchmarks with reported scores" in today, key
        assert re.search(r"\d", today) is None, key


def test_benchgraph_landing_statistics_come_from_the_build() -> None:
    html = builder.wire_benchgraph_landing(
        '<p class="today">Today the graph holds <b>164</b> benchmarks across '
        '<b>549</b> scored models, <b>10,887</b> scores in all, each carrying '
        "the date it was taken.</p>",
        {"pages": 1200, "scored_benchmarks": 3, "scored_models": 5, "scores": 9000},
    )
    assert html == (
        '<p class="today">Today the graph holds <b>1,200</b> benchmark pages and '
        '<b>3</b> benchmarks with reported scores, across <b>5</b> scored models, '
        '<b>9,000</b> scores in all, each carrying the date it was taken.</p>'
    )
    assert "164" not in html and "549" not in html and "10,887" not in html


def test_a_benchgraph_landing_that_lost_its_today_line_fails_the_build() -> None:
    try:
        builder.wire_benchgraph_landing("<body>no figures</body>", {
            "pages": 1, "scored_benchmarks": 1, "scored_models": 1, "scores": 1})
    except ValueError as err:
        assert "p.today" in str(err)
    else:
        raise AssertionError("a landing without p.today must not build")


def test_benchgraph_asset_script_does_not_import_pillow_until_png() -> None:
    src = (ROOT / "site/benchgraph/build/build.py").read_text(encoding="utf-8")
    before, sep, _after = src.partition("def write_png_assets")
    assert sep, "PNG rendering must live in write_png_assets"
    assert "PIL" not in before
    assert "from PIL import" in _after


# ── the landing's calls to action ────────────────────────────────────────────

LANDING_ANSWER = ('<div class="a">That question, answered from evidence, '
                  'and kept current as the models change underneath you.</div>')


def test_the_landing_calls_to_action_use_the_shared_button_classes() -> None:
    html = builder.wire_landing(LANDING_ANSWER, {"models": 1, "providers": 1, "edges": 1,
                                                 "benchmarks": 1, "fields": 1})
    cta = html.split(LANDING_ANSWER, 1)[1]
    assert cta == ('\n      <div class="btns go">'
                   '<a class="btn primary" href="/downselect/">Answer it now &rarr;</a>'
                   '<a class="btn" href="/graph/">Explore the graph</a>'
                   '<a class="btn" href="/models/">Browse every model</a></div>')
    assert re.search(r"#[0-9a-fA-F]{3,8}\b", cta) is None
    assert "style=" not in cta


def test_the_landing_statistics_become_a_stat_strip() -> None:
    html = builder.wire_landing(
        '<section><div class="stats" aria-label="x"><div class="cell"><span class="lab">'
        'model cards</span><div class="val">OLD</div></div></div></section>',
        {"models": 1225, "providers": 47, "edges": 37020, "benchmarks": 1106, "fields": 693})
    assert "OLD" not in html
    assert ('<div class="cell"><span class="lab">model cards</span>'
            '<div class="val">1,225</div></div>') in html
    assert html.endswith("</div></section>")


# ── the benchmark page's facts ───────────────────────────────────────────────

LONG_NOTE = ("Random guessing scores 25 percent on four-option items; the published human "
             "expert baseline is 81 percent, measured on a 200-item subset.")


def _bench(front: dict) -> str:
    bench = Benchmark("demo", Path("benchmarks/demo.md"), {"name": "Demo", **front}, "")
    return r.benchmark_page(bench, BUILD, Catalogue(as_of=date(2026, 9, 15)), [])


def test_a_long_note_sits_behind_its_own_disclosure_and_a_short_fact_does_not() -> None:
    html = _bench({"category": "reasoning",
                   "metric": {"name": "accuracy", "baseline_note": LONG_NOTE},
                   "saturation": {"note": LONG_NOTE.replace("25", "30")}})
    disclosures = re.findall(r"<details class=\"note\">.*?</details>", html, re.S)
    assert disclosures[0] == ('<details class="note"><summary><span class="lab">Baseline note'
                              f'</span></summary><p>{r.esc(LONG_NOTE)}</p></details>')
    assert len(disclosures) == 2
    assert "Saturation note" in disclosures[1]
    outside = re.sub(r"<details.*?</details>", "", html, flags=re.S)
    assert '<span class="lab">Category</span><div class="val">reasoning</div>' in outside
    assert '<span class="lab">Metric</span><div class="val">accuracy</div>' in outside
    assert LONG_NOTE not in outside
    assert html.index('class="stats facts"') < html.index("<h2>Notes</h2>")


def test_the_disposition_keeps_the_catalogue_spec_wording() -> None:
    html = _bench({"metric": {"baseline_note": LONG_NOTE}})
    assert '<p><span class="pill unassessed">unassessed</span></p>' in html
    assert ('<div class="notice">This page is a discovery lead. Nobody has yet assessed it '
            "against the catalogue contract, so it carries no disposition. Absence of evidence "
            "here is not evidence of staleness.</div>") in html


def test_a_page_with_no_long_facts_has_no_notes_section() -> None:
    html = _bench({"category": "coding"})
    assert "<h2>Notes</h2>" not in html and "<details" not in html


# ── one nav per site ─────────────────────────────────────────────────────────

STATIC_NAV_PAGES = ("site/holding/index.html", "site/benchgraph/build/index.tpl.html",
                    "site/benchgraph/index.html", "web3d/downselect.v2.html",
                    "web3d/explorer.html")


def test_static_pages_hold_the_placeholder_and_no_nav_of_their_own() -> None:
    for page in STATIC_NAV_PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        assert text.count(r.NAV_PLACEHOLDER) == 1, page
        assert "<nav" not in text, page


def test_the_generated_shell_and_the_static_pages_share_one_nav() -> None:
    build = Build(commit="abc", built_at="2026-09-18T00:00:00Z", as_of=date(2026, 9, 18))
    for site, links in (("ModelSpec", r.MS_NAV), ("benchgraph", r.BG_NAV)):
        page = r.shell(title="t", description="d", canonical="https://x/", body="",
                       build=build, site=site, nav_links=links)
        assert r.site_nav(site, links) in page
    filled = builder.with_site_nav(f"<body>{r.NAV_PLACEHOLDER}</body>",
                                   r.site_nav("ModelSpec", r.MS_NAV), "landing")
    assert filled == ('<body><nav><a class="brand" href="/">ModelSpec</a><div class="links">'
                      '<a href="/downselect/">Downselect</a><a href="/graph/">Graph</a>'
                      '<a href="/models/">Models</a><a href="/providers/">Providers</a>'
                      '<a href="https://benchgraph.dev/benchmarks/">Benchmarks</a>'
                      '<a href="/api/index.json">API</a></div></nav></body>')


def test_a_page_that_lost_its_placeholder_fails_the_build() -> None:
    try:
        builder.with_site_nav("<body>no nav here</body>", "<nav></nav>", "site/holding/index.html")
    except ValueError as err:
        assert "site/holding/index.html" in str(err)
    else:
        raise AssertionError("a page without the placeholder must not build")


# ── the wizard's score bar ───────────────────────────────────────────────────

SEGMENTS = ("bench", "cap", "type", "ctx", "cost")


def test_each_score_part_has_its_own_hue_in_the_shared_sheet() -> None:
    """A restyle once turned the five parts into shades of the accent, which
    made the bar unreadable at a glance. The operator asked for distinct hues."""
    values = {}
    for seg in SEGMENTS:
        match = re.search(rf"--seg-{seg}:(#[0-9a-fA-F]{{6}});", r.CSS)
        assert match, f"--seg-{seg} is not a literal colour in the shared sheet"
        values[seg] = match.group(1).lower()
    assert values == {"bench": "#63c9d9", "cap": "#78b5a2", "type": "#f5b342",
                      "ctx": "#8fa4d4", "cost": "#9aa5b6"}


def test_the_wizard_draws_every_part_from_the_shared_tokens() -> None:
    wizard = (ROOT / "web3d/downselect.v2.html").read_text(encoding="utf-8")
    for seg in SEGMENTS:
        assert f'"var(--seg-{seg})"' in wizard
        assert f"--seg-{seg}:" not in wizard  # defined once, in /instrument.css
