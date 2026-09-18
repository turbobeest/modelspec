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


def test_the_section_counter_is_scoped_to_the_generated_page_column() -> None:
    """A bare h2 rule would number and indent every heading on the landings."""
    assert re.search(r"(?:^|\})h2(?:::before)?\{", r.CSS, re.M) is None
    assert ":where(.page) h2{" in r.CSS
    assert ":where(.page) h2::before{content:counter(sec" in r.CSS


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
