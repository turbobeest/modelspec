"""MODEL-219 use-case discovery in the tree published to Cloudflare Pages."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pipeline import entity, live, surface_lint

BASE = "https://modelspec.dev"
INDEX = "/use-cases/"
ANSWERED = "/use-cases/coding/budget-coding/"
THIN = "/use-cases/coding/coding-fastest/"
UNLISTED = "/use-cases/coding/unlisted-example/"
IMAGE_DATE = "2026-01-17"
COMPARISON_INDEX = "/compare/"
COMPARISON = "/compare/coding-best/lab-alpha-vs-lab-beta/"
COMPARISON_NOINDEX = "/compare/coding-best/lab-alpha-vs-lab-gamma/"
COMPARISON_UNLISTED = "/compare/coding-best/lab-beta-vs-lab-gamma/"
GUIDE_INDEX = "/guides/"
GUIDE = "/guides/how-to-choose-an-ai-model/"
CATEGORY_GUIDE = "/guides/analysis-of-alternatives-vs-model-router-vs-hard-coded-model/"


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
    _write(tree, "method/index.html", '<html><head></head><body><a href="/use-cases/">Use-case examples</a><a href="/compare/">Comparisons</a><a href="/guides/">Guides</a></body></html>')
    for path in (INDEX, ANSWERED, THIN, UNLISTED, COMPARISON_INDEX, COMPARISON,
                 COMPARISON_NOINDEX, COMPARISON_UNLISTED):
        robots = "noindex, follow" if path in (THIN, COMPARISON_NOINDEX) else "index, follow"
        _write(tree, path.lstrip("/") + "index.html",
               f'<html><head><meta name="robots" content="{robots}"></head><body>{path}</body></html>')
    for path in (GUIDE_INDEX, GUIDE, CATEGORY_GUIDE):
        _write(tree, path.lstrip("/") + "index.html",
               '<html><head></head><body><h1>Guide</h1><p>' + 'word ' * 90 + '</p></body></html>')
    _write(tree, "sitemap.xml", (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}{INDEX}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        f'<url><loc>{BASE}{ANSWERED}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        f'<url><loc>{BASE}{COMPARISON_INDEX}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        f'<url><loc>{BASE}{COMPARISON}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
        + "".join(f'<url><loc>{BASE}{path}</loc><lastmod>{IMAGE_DATE}</lastmod></url>'
                  for path in (GUIDE_INDEX, GUIDE, CATEGORY_GUIDE))
        + f'<url><loc>{BASE}/models/</loc><lastmod>2026-10-17</lastmod></url>'
        '<url><loc>https://other.test/use-cases/foreign/</loc><lastmod>2026-10-17</lastmod></url>'
        '<url><loc>https://other.test/compare/foreign/</loc><lastmod>2026-10-17</lastmod></url>'
        '<url><loc>https://other.test/guides/foreign/</loc><lastmod>2026-10-17</lastmod></url>'
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


def test_live_comparisons_preserve_every_page_and_only_source_sitemap_entries(composed) -> None:
    source, tree = composed
    assert COMPARISON_INDEX in surface_lint.Page((tree / "method/index.html").read_text()).links
    for path in (COMPARISON_INDEX, COMPARISON, COMPARISON_NOINDEX, COMPARISON_UNLISTED):
        assert live.resolves(tree, path), path
        rel = path.lstrip("/") + "index.html"
        assert (tree / rel).read_bytes() == (source / "modelspec" / rel).read_bytes()
    urls = dict(surface_lint.sitemap_entries((tree / "sitemap.xml").read_text()))
    assert {url: stamp for url, stamp in urls.items() if "/compare/" in url} == {
        BASE + COMPARISON_INDEX: IMAGE_DATE,
        BASE + COMPARISON: IMAGE_DATE,
    }
    noindex = surface_lint.Page((tree / COMPARISON_NOINDEX.lstrip("/") / "index.html").read_text())
    assert "noindex" in noindex.meta["robots"]


@pytest.mark.parametrize("path", [COMPARISON, COMPARISON_NOINDEX, THIN, GUIDE])
def test_live_checks_links_on_every_worked_example(composed, path) -> None:
    _, tree = composed
    rel = path.lstrip("/") + "index.html"
    _write(tree, rel, '<a href="/missing-comparison-target/">Missing</a>')
    assert f"{rel}: /missing-comparison-target/" in live.dead_links(tree)


def test_live_guides_preserve_pages_navigation_and_image_dates(composed) -> None:
    source, tree = composed
    assert GUIDE_INDEX in surface_lint.Page((tree / "method/index.html").read_text()).links
    for path in (GUIDE_INDEX, GUIDE, CATEGORY_GUIDE):
        assert live.resolves(tree, path), path
        rel = path.lstrip("/") + "index.html"
        assert (tree / rel).read_bytes() == (source / "modelspec" / rel).read_bytes()
    urls = dict(surface_lint.sitemap_entries((tree / "sitemap.xml").read_text()))
    assert {url: stamp for url, stamp in urls.items() if "/guides/" in url} == {
        BASE + path: IMAGE_DATE for path in (GUIDE_INDEX, GUIDE, CATEGORY_GUIDE)
    }


def test_live_thin_page_check_rejects_a_guide_that_needs_javascript(composed, monkeypatch) -> None:
    _, tree = composed
    monkeypatch.setattr(live, "PAGES", ())
    _write(tree, GUIDE.lstrip("/") + "index.html",
           '<html><body><div id="root"></div><script>render()</script></body></html>')
    assert live.thin_pages(tree) == [
        f"{GUIDE}: no <h1> without JavaScript",
        f"{GUIDE}: 0 words without JavaScript; need 80",
    ]


def test_surface_lint_checks_guide_leads() -> None:
    rel = GUIDE.lstrip("/") + "index.html"
    findings = surface_lint.presence({rel: '<p>A different opening.</p>'}, holding=True)
    assert any(row.surface == rel and row.check == "presence.lead" for row in findings)
    assert not any(row.surface == rel for row in surface_lint.presence(
        {rel: f'<p>{entity.ONE_SENTENCE}</p>'}, holding=True,
    ))


def test_surface_lint_accepts_a_visible_defined_term() -> None:
    term = "analysis of alternatives for AI models"
    raw = f'<p>{term}</p><script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "DefinedTerm", "name": term,
    }) + '</script>'
    assert surface_lint.structured_data({"guides/example/index.html": raw}) == []


def test_live_surface_lint_discovers_guides_outside_the_sitemap() -> None:
    visited = []

    def fetch(url):
        visited.append(url)
        if url == BASE + "/sitemap.xml":
            body = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
        elif url == BASE + GUIDE_INDEX:
            body = f'<a href="{GUIDE}">Choosing a model</a>'
        else:
            body = '<html><body>Fixture</body></html>'
        return 200, {}, body.encode()

    texts, _, holding, failures = surface_lint.live_tree(BASE, fetch)
    assert not holding and failures == []
    assert BASE + GUIDE_INDEX in visited
    assert GUIDE.lstrip("/") + "index.html" in texts


@pytest.mark.parametrize("full_tree", [False, True])
def test_surface_lint_guide_freshness_uses_the_image_date(monkeypatch, full_tree) -> None:
    from pipeline import build

    monkeypatch.setattr(build, "use_case_image_date", lambda root: date.fromisoformat(IMAGE_DATE))
    texts = {
        "api/build.json": json.dumps({"built_at": "2026-10-17T00:00:00Z", "commit": "fixture"}),
        "sitemap.xml": '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}{GUIDE}</loc><lastmod>{IMAGE_DATE}</lastmod></url></urlset>',
    }
    if full_tree:
        texts["models/index.html"] = "catalogue"
    dates, notice = surface_lint.expected_lastmods(texts, deployed=False)
    assert notice == ""
    assert dates.get(GUIDE) == IMAGE_DATE
