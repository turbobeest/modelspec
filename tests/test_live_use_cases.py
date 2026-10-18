"""MODEL-219 use-case discovery in the tree published to Cloudflare Pages."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import live, surface_lint

BASE = "https://modelspec.dev"
INDEX = "/use-cases/"
ANSWERED = "/use-cases/coding/budget-coding/"
THIN = "/use-cases/coding/coding-fastest/"
UNLISTED = "/use-cases/coding/unlisted-example/"
IMAGE_DATE = "2026-01-17"


def _write(tree: Path, path: str, text: str) -> None:
    target = tree / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


@pytest.fixture
def composed(tmp_path: Path) -> tuple[Path, Path]:
    source, web, out = tmp_path / "source", tmp_path / "web", tmp_path / "live"
    tree = source / "modelspec"
    for directory in live.KEEP_DIRS:
        (tree / directory).mkdir(parents=True, exist_ok=True)
    for name in live.KEEP_FILES:
        _write(tree, name, "{}" if name.endswith(".json") else "<html><head></head><body>Fixture</body></html>")
    _write(tree, "api/build.json", json.dumps({
        "export_schema_version": "3.0", "built_at": "2026-10-17T00:00:00Z",
    }))
    _write(tree, "_headers", "/*\n  X-Content-Type-Options: nosniff\n")
    _write(source, "data-image.json", json.dumps({"as_of": IMAGE_DATE}))
    _write(tree, "method/index.html", '<html><head></head><body><a href="/use-cases/">Use-case examples</a></body></html>')
    for path in (INDEX, ANSWERED, THIN, UNLISTED):
        robots = "noindex, follow" if path == THIN else "index, follow"
        _write(tree, path.lstrip("/") + "index.html",
               f'<html><head><meta name="robots" content="{robots}"></head><body>{path}</body></html>')
    _write(tree, "sitemap.xml", (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}{INDEX}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        f'<url><loc>{BASE}{ANSWERED}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        f'<url><loc>{BASE}/models/</loc><lastmod>2026-10-17</lastmod></url>'
        '<url><loc>https://other.test/use-cases/foreign/</loc><lastmod>2026-10-17</lastmod></url>'
        '</urlset>'
    ))
    _write(source, "benchgraph/_redirects", "/   https://modelspec.dev/             301\n")
    (web / "assets").mkdir(parents=True)
    for name in ("decide.html", "decide-details.html", "decision.html"):
        _write(web, name, '<html><head></head><body><div id="root"></div></body></html>')
    live.build(source, web, out)
    return source, out / "modelspec"


def test_live_method_link_reaches_use_case_index(composed: tuple[Path, Path]) -> None:
    source, tree = composed
    page = surface_lint.Page((tree / "method/index.html").read_text())
    assert INDEX in page.links
    assert live.resolves(tree, INDEX)
    assert (tree / "use-cases/index.html").read_bytes() == (
        source / "modelspec/use-cases/index.html"
    ).read_bytes()


def test_live_sitemap_preserves_only_source_use_case_entries(composed: tuple[Path, Path]) -> None:
    _, tree = composed
    urls = dict(surface_lint.sitemap_entries((tree / "sitemap.xml").read_text()))
    use_cases = {url for url in urls if "/use-cases/" in url}
    assert use_cases == {BASE + INDEX, BASE + ANSWERED}
    assert live.resolves(tree, THIN)
    assert "noindex" in surface_lint.Page((tree / THIN.lstrip("/") / "index.html").read_text()).meta["robots"]
    assert BASE + THIN not in urls
    assert live.resolves(tree, UNLISTED)
    assert BASE + UNLISTED not in urls
    assert BASE + "/models/" not in urls


def test_live_use_case_lastmod_preserves_public_image_date(composed: tuple[Path, Path]) -> None:
    source, tree = composed
    image_date = json.loads((source / "data-image.json").read_text())["as_of"]
    urls = dict(surface_lint.sitemap_entries((tree / "sitemap.xml").read_text()))
    assert {url: urls.get(url) for url in (BASE + INDEX, BASE + ANSWERED)} == {
        BASE + INDEX: image_date,
        BASE + ANSWERED: image_date,
    }
