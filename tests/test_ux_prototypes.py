"""Guard the MODEL-147 UX prototypes in `docs/ux/`.

They are research artefacts, not production code, but three promises they make
are checkable: every page stands alone (no scripts except from the two allowed
CDNs, no network calls), every page says its data is fictional, and every page
carries the same component block, so the launch report and the social cards
really are drawn by the components the downselect prototypes use.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

import pytest

UX = Path(__file__).resolve().parents[1] / "docs" / "ux"
PROTOTYPES = UX / "prototypes"
PAGES = ("a-guided.html", "b-canvas.html", "c-table.html", "launch-report.html")
ALLOWED_SCRIPT_HOSTS = {"cdnjs.cloudflare.com", "cdn.jsdelivr.net"}
FAKE_MARK = "FICTIONAL SAMPLE DATA"
BEGIN = "/* === ms-components:begin === */"
END = "/* === ms-components:end === */"


def _page(name: str) -> str:
    return (PROTOTYPES / name).read_text(encoding="utf-8")


def test_deliverables_exist():
    for doc in ("downselect-research.md", "prototype-comparison.md"):
        assert (UX / doc).is_file(), doc
    for name in PAGES:
        assert (PROTOTYPES / name).is_file(), name


@pytest.mark.parametrize("name", PAGES)
def test_page_is_self_contained(name):
    html = _page(name)
    for src in re.findall(r"<script[^>]*\bsrc=[\"']([^\"']+)", html, re.I):
        assert urlsplit(src).hostname in ALLOWED_SCRIPT_HOSTS, src
    assert not re.search(r"<link[^>]*rel=[\"']?stylesheet", html, re.I), "external stylesheet"
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(", html), "network call"


@pytest.mark.parametrize("name", PAGES)
def test_page_labels_its_data_as_fictional(name):
    assert FAKE_MARK in _page(name)


def _components(name: str) -> str:
    html = _page(name)
    assert html.count(BEGIN) == 1 and html.count(END) == 1, name
    return html[html.index(BEGIN):html.index(END)]


def test_every_page_carries_the_same_components():
    blocks = {name: _components(name) for name in PAGES}
    first = blocks[PAGES[0]]
    assert len(first) > 5000
    for name, block in blocks.items():
        assert block == first, f"{name} has drifted from {PAGES[0]}"
