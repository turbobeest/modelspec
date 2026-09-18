"""404 pages must not tell crawlers they are the homepage (MODEL-89)."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import build as builder  # noqa: E402
from pipeline import render as r  # noqa: E402
from pipeline.export import Build  # noqa: E402

BUILD = Build(commit="abc", built_at="2026-09-18T00:00:00Z", as_of=date(2026, 9, 18))

CANONICAL = re.compile(r"""rel=["']canonical["']""", re.I)
CANONICAL_HREF = re.compile(
    r'<link\s+rel="canonical"\s+href="([^"]+)"',
    re.I,
)
ROBOTS = re.compile(
    r'<meta\s+name="robots"\s+content="([^"]+)"',
    re.I,
)


def _robots_tokens(html: str) -> list[str]:
    match = ROBOTS.search(html)
    assert match is not None
    return [token.strip() for token in match.group(1).lower().split(",")]


def _own_url(origin: str, site_root: Path, page: Path) -> str:
    return f"{origin}/{page.parent.relative_to(site_root).as_posix()}/"


def test_rendered_404_has_no_canonical_and_is_noindex() -> None:
    html = r.not_found("ModelSpec", BUILD, r.MS_NAV, "https://modelspec.dev/")
    assert CANONICAL.search(html) is None
    assert 'property="og:url"' not in html
    assert "noindex" in _robots_tokens(html)
    html = r.not_found("benchgraph", BUILD, r.BG_NAV, "https://benchgraph.dev/")
    assert CANONICAL.search(html) is None
    assert "noindex" in _robots_tokens(html)


@pytest.fixture(scope="module")
def dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The tree CI builds: `python -m pipeline.build --out dist`."""
    out = tmp_path_factory.mktemp("dist")
    assert builder.main(["--out", str(out), "--root", str(ROOT)]) == 0
    return out


def test_built_404_html_has_no_canonical_and_is_noindex(dist: Path) -> None:
    for site in ("modelspec", "benchgraph"):
        html = (dist / site / "404.html").read_text(encoding="utf-8")
        assert CANONICAL.search(html) is None, site
        assert "noindex" in _robots_tokens(html), site


def test_built_sample_pages_canonical_is_own_url(dist: Path) -> None:
    samples = (
        ("https://modelspec.dev", dist / "modelspec",
         sorted((dist / "modelspec" / "m").glob("*/*/index.html"))[:5]),
        ("https://modelspec.dev", dist / "modelspec",
         sorted((dist / "modelspec" / "p").glob("*/index.html"))[:5]),
        ("https://benchgraph.dev", dist / "benchgraph",
         sorted((dist / "benchgraph" / "b").glob("*/index.html"))[:5]),
    )
    for origin, root, pages in samples:
        assert len(pages) == 5, origin
        for page in pages:
            html = page.read_text(encoding="utf-8")
            match = CANONICAL_HREF.search(html)
            assert match is not None, page
            assert match.group(1) == _own_url(origin, root, page), page
