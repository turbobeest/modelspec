"""MODEL-24 part 3: the graph explorer in the Instrument system.

The explorer is a hand-written canvas page. Its JavaScript must come from the
vendored copies, never a CDN, and it must carry the same nav as every other
modelspec page.
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

EXPLORER = ROOT / "web3d/explorer.html"
VENDOR = ROOT / "web3d/vendor"


def _page() -> str:
    return EXPLORER.read_text(encoding="utf-8")


def _script_sources(page: str) -> list[str]:
    return re.findall(r"<script\b[^>]*\bsrc=\"([^\"]+)\"", page)


def _nav(page: str) -> str:
    return re.search(r"<nav>.*?</nav>", page, re.S).group(0)


def test_the_explorer_links_the_shared_sheet_and_requests_no_space_grotesk() -> None:
    page = _page()
    assert '<link rel="stylesheet" href="/instrument.css">' in page
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


def test_the_built_explorer_carries_the_modelspec_nav_and_its_libraries(tmp_path) -> None:
    ms = tmp_path / "modelspec"
    assert builder.ship_explorer(ROOT, ms, '<p class="fresh">as of 2026-09-18</p>') is True
    built = (ms / "graph/index.html").read_text(encoding="utf-8")

    shell = r.shell(title="t", description="d", canonical="https://modelspec.dev/", body="",
                    build=Build(commit="abc", built_at="2026-09-18T00:00:00Z",
                                as_of=date(2026, 9, 18)),
                    site="ModelSpec", nav_links=r.MS_NAV)
    assert _nav(built) == _nav(shell)
    assert built.count("<nav>") == 1
    assert r.NAV_PLACEHOLDER not in built
    assert '<div id="freshness"><p class="fresh">as of 2026-09-18</p></div>' in built
    assert sorted(p.name for p in (ms / "graph/vendor").iterdir()) == [
        "3d-force-graph.min.js", "README.md", "three.min.js"]
