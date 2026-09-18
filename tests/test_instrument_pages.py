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
