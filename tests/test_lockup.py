"""One brand lockup, one scale, on every page (MODEL-213).

`pipeline.landing_chrome` owns the lockup's markup and its CSS. Pages the
pipeline renders call it. The decide app is built without the pipeline, so it
carries a verbatim copy, and these tests are what keeps that copy equal.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pipeline import holding, legal, landing_chrome, pricing
from pipeline.export import Build

ROOT = Path(__file__).resolve().parents[1]
BUILD = Build(commit="0" * 40, built_at="2026-09-29T00:00:00Z", as_of=date(2026, 9, 29))


def _legal_page() -> str:
    doc = legal.DOCS[0]
    return legal.page(doc, (legal.source_dir(ROOT) / doc.source).read_text(encoding="utf-8"), BUILD)


PAGES = {
    "pricing": lambda: pricing.page(json.loads((ROOT / "api/worker/tiers.json").read_text()),
                                    build=BUILD),
    "legal": _legal_page,
    "holding 404": lambda: holding.dark_page(holding.SITES["modelspec"]),
}


@pytest.mark.parametrize("name", PAGES)
def test_the_page_carries_the_shared_lockup_and_its_css(name: str) -> None:
    page = PAGES[name]()
    assert landing_chrome.lockup() in page
    assert landing_chrome.LOCKUP_CSS in page


def test_the_decide_header_scales_by_the_same_rule() -> None:
    css = (ROOT / "web/src/decide/decide.css").read_text(encoding="utf-8")
    assert landing_chrome.LOCKUP_CSS in css


def test_the_holding_404_is_dark_whatever_the_colour_scheme() -> None:
    page = holding.dark_page(holding.SITES["modelspec"])
    assert "prefers-color-scheme" not in page
    assert "color-scheme:dark" in page


@pytest.mark.parametrize("name", ["pricing", "legal", "holding 404"])
def test_the_operator_name_is_escaped_in_html(name: str) -> None:
    """The legal name has an ampersand (Jamie, 2026-09-30). In markup it is `&amp;`."""
    page = PAGES[name]()
    assert "Sparks &amp; Sawdust LLC" in page
    assert "Sparks & Sawdust" not in page


def test_the_shared_footer_escapes_the_operator_name() -> None:
    assert "© Sparks &amp; Sawdust LLC" in landing_chrome.footer()
