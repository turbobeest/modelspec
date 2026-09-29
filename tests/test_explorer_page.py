"""The graph novelty page and its self-contained runtime assets.

The explorer is a hand-written canvas page. Its JavaScript must come from the
vendored copies, never a CDN, and its shell follows the landing page rather
than the retired catalogue navigation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import build as builder  # noqa: E402
from pipeline import landing_chrome  # noqa: E402

EXPLORER = ROOT / "web3d/explorer.html"
VENDOR = ROOT / "web3d/vendor"


def _page() -> str:
    return EXPLORER.read_text(encoding="utf-8")


def _script_sources(page: str) -> list[str]:
    return re.findall(r"<script\b[^>]*\bsrc=\"([^\"]+)\"", page)


def test_the_explorer_uses_the_landing_system_and_requests_no_space_grotesk() -> None:
    page = _page()
    assert '<link rel="stylesheet" href="/landing-assets/landing.css">' in page
    assert 'class="graph-header"' in page
    assert 'class="mark"' in page
    assert '<nav' not in page
    assert "Space+Grotesk" not in page
    assert "Space Grotesk" not in page


def test_the_explorer_loads_script_only_from_the_vendored_directory() -> None:
    assert _script_sources(_page()) == ["/graph/vendor/three.min.js",
                                        "/graph/vendor/3d-force-graph.min.js"]


def test_every_vendored_script_the_explorer_loads_exists_and_is_documented() -> None:
    readme = (VENDOR / "README.md").read_text(encoding="utf-8")
    for src in _script_sources(_page()):
        name = src.removeprefix("/graph/vendor/")
        assert (VENDOR / name).is_file(), name
        assert f"`{name}`" in readme, name


def test_the_built_explorer_carries_the_landing_shell_and_its_libraries(tmp_path) -> None:
    ms = tmp_path / "modelspec"
    assert builder.ship_explorer(ROOT, ms, '<p class="fresh">as of 2026-09-18</p>') is True
    built = (ms / "graph/index.html").read_text(encoding="utf-8")

    assert landing_chrome.lockup() in built
    assert '<a href="/legal/terms/">Terms</a>' in built
    assert '<a href="/legal/privacy/">Privacy</a>' in built
    assert '<a href="/legal/neutrality/">Neutrality</a>' in built
    assert "/decide/" not in built
    assert "/downselect/" not in built
    assert '<div id="freshness"><p class="fresh">as of 2026-09-18</p></div>' in built
    assert sorted(p.name for p in (ms / "graph/vendor").iterdir()) == [
        "3d-force-graph.min.js", "three.min.js"]


def test_the_detail_panel_no_longer_builds_page_links_in_script() -> None:
    page = _page()
    assert "pageFor" not in page
    assert "dGo" not in page


def test_controls_are_native_keyboard_targets_and_the_page_explains_itself() -> None:
    page = _page()
    assert '<button id="close" type="button" aria-label="Close">' in page
    assert 'document.createElement("button")' in page
    assert "Models, providers, benchmarks, platforms, and the evidence links between them." in page
