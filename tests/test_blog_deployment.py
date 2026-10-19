"""MODEL-223 publication controls in the final Pages compositions."""

from __future__ import annotations

import gzip
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from pipeline import holding, live, public_data, structured_data, surface_lint

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "api/decision/snapshots/snap_0123456789abcdef.json.gz"
POST = "/blog/fixture-model/"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def write(tree: Path, name: str, content: str | bytes) -> Path:
    path = tree / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)
    return path


def page(path: str, body: str = "") -> str:
    return (
        '<html><head><link rel="canonical" href="https://modelspec.dev'
        + path
        + '"></head><body><header class="site-head"><nav>'
        '<a href="/decide/">Decide</a></nav></header><h1>Fixture</h1>' + body + "</body></html>"
    )


@pytest.fixture
def built(tmp_path: Path) -> tuple[Path, Path]:
    source, web = tmp_path / "source", tmp_path / "web"
    tree = source / "modelspec"
    for directory in live.KEEP_DIRS:
        (tree / directory).mkdir(parents=True, exist_ok=True)
    for name in live.KEEP_FILES:
        write(tree, name, "{}" if name.endswith(".json") else "")
    for path in live.PAGES:
        write(tree, path.lstrip("/") + "index.html", page(path))
    write(
        tree,
        "api/build.json",
        json.dumps(
            {
                "export_schema_version": "3.0",
                "built_at": "2026-10-13T00:00:00Z",
            }
        ),
    )
    write(tree, "_headers", "/*\n  X-Content-Type-Options: nosniff\n")
    write(tree, "blog/index.html", page("/blog/"))
    write(
        tree,
        POST.lstrip("/") + "index.html",
        page(POST, '<a href="/' + SNAPSHOT + '">Snapshot</a>'),
    )
    write(tree, "blog/feed.xml", "<feed>fixture</feed>")
    write(tree, "blog/fixture-model/og-card.png", b"fixture card")
    write(tree, SNAPSHOT, gzip.compress(b'{"fixture":true}', mtime=0))
    write(
        tree,
        "sitemap.xml",
        (
            '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://modelspec.dev/blog/</loc><lastmod>2026-10-12</lastmod></url>"
            "<url><loc>https://modelspec.dev/blog/fixture-model/</loc>"
            "<lastmod>2026-10-11</lastmod></url></urlset>"
        ),
    )
    write(
        source,
        "benchgraph/_redirects",
        "/   https://modelspec.dev/             301\n/*  https://modelspec.dev/:splat       301\n",
    )
    (web / "assets").mkdir(parents=True)
    write(web, "decide.html", '<html><body><div id="root"></div></body></html>')
    write(web, "decide-details.html", '<html><body><div id="root"></div></body></html>')
    write(web, "decision.html", '<html><body><div id="root"></div></body></html>')
    structured_data.inject(tree)
    return source, web


def test_enabled_blog_survives_live_composition_with_dates_and_navigation(
    built: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BLOG_ENABLED", "true")
    monkeypatch.delenv("INDEXNOW_KEY", raising=False)
    source, web = built
    out = tmp_path / "live"
    live.build(source, web, out)
    tree = out / "modelspec"
    assert (tree / "blog/feed.xml").read_text() == "<feed>fixture</feed>"
    assert (tree / "blog/fixture-model/og-card.png").read_bytes() == b"fixture card"
    assert (tree / SNAPSHOT).read_bytes() == (source / "modelspec" / SNAPSHOT).read_bytes()
    assert (tree / "legal/terms/index.html").read_bytes() == (
        source / "modelspec/legal/terms/index.html"
    ).read_bytes()
    urls = {
        row.findtext("s:loc", namespaces=NS): row.findtext("s:lastmod", namespaces=NS)
        for row in ET.parse(tree / "sitemap.xml").findall("s:url", NS)
    }
    assert urls["https://modelspec.dev/blog/"] == "2026-10-12"
    assert urls["https://modelspec.dev/blog/fixture-model/"] == "2026-10-11"
    for name in ("index.html", "method/index.html", "decide/index.html", "blog/index.html"):
        nav = re.search(r"<nav\b[^>]*>(.*?)</nav>", (tree / name).read_text(), re.S)
        if name == "decide/index.html":
            continue  # The client owns its chrome, unlike static published pages.
        assert nav is not None
        assert '<a href="/blog/">Blog</a>' in nav.group(1)


@pytest.mark.parametrize("value", [None, "", "false", "True", " true", "true\n"])
def test_disabled_blog_stays_out_of_live_pages_sitemap_and_navigation(
    built: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    value: str | None,
) -> None:
    if value is None:
        monkeypatch.delenv("BLOG_ENABLED", raising=False)
    else:
        monkeypatch.setenv("BLOG_ENABLED", value)
    source, web = built
    live.build(source, web, tmp_path / "live")
    tree = tmp_path / "live/modelspec"
    assert not (tree / "blog").exists()
    assert "/blog/" not in (tree / "sitemap.xml").read_text()
    assert "/blog/" not in (tree / "index.html").read_text()
    assert (tree / SNAPSHOT).is_file()


def test_blog_links_are_checked_in_the_final_live_tree(
    built: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BLOG_ENABLED", "true")
    source, web = built
    write(
        source / "modelspec",
        "blog/fixture-model/index.html",
        page(POST, '<a href="/blog/missing/">Missing post</a>'),
    )
    live.build(source, web, tmp_path / "live")
    assert "blog/fixture-model/index.html: /blog/missing/" in live.dead_links(
        tmp_path / "live/modelspec"
    )


def test_retained_snapshot_links_must_resolve_but_build_only_social_cards_can_be_absent(
    built: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BLOG_ENABLED", "true")
    source, web = built
    write(
        source / "modelspec",
        "blog/fixture-model/index.html",
        page(
            POST,
            '<a href="/' + SNAPSHOT + '">Snapshot</a>'
            '<meta property="og:image" content="https://modelspec.dev/blog/fixture-model/r1/og-card.png">',
        ),
    )
    live.build(source, web, tmp_path / "live")
    tree = tmp_path / "live/modelspec"
    (tree / SNAPSHOT).unlink()
    dead = live.dead_links(tree)
    assert "blog/fixture-model/index.html: /" + SNAPSHOT in dead
    assert not any("og-card.png" in finding for finding in dead)


def test_retained_snapshot_is_preserved_while_other_bulk_exports_are_removed(
    tmp_path: Path,
) -> None:
    payload = gzip.compress(b'{"fixture":true}', mtime=0)
    write(tmp_path, SNAPSHOT, payload)
    rejected = (
        "api/decision/snapshots/private.json.gz",
        "api/decision/snapshots/snap_0123456789abcdef/nested.json.gz",
        "api/decision/snapshots/snap_nothex.json.gz",
        "api/decision/snapshots/snap_0123456789abcdef.json",
        "api/private/snap_0123456789abcdef.json.gz",
    )
    for path in rejected:
        write(tmp_path, path, payload)
    write(tmp_path, "_headers", "/*\n  X-Content-Type-Options: nosniff\n")
    public_data.restrict(tmp_path)
    assert (tmp_path / SNAPSHOT).read_bytes() == payload
    assert all(not (tmp_path / name).exists() for name in rejected)


def test_holding_allows_retained_snapshots_and_rejects_blog_pages(tmp_path: Path) -> None:
    write(tmp_path, "index.html", page("/"))
    write(tmp_path, "404.html", '<meta name="robots" content="noindex">')
    write(tmp_path, "_headers", holding.HEADERS)
    write(tmp_path, "robots.txt", holding.ROBOTS)
    write(tmp_path, SNAPSHOT, gzip.compress(b'{"fixture":true}', mtime=0))
    assert holding.violations(tmp_path, "modelspec") == []
    write(tmp_path, "blog/index.html", page("/blog/"))
    assert holding.violations(tmp_path, "modelspec") == [
        "blog/index.html: outside the kept directories",
    ]


def test_surface_lint_accepts_article_structured_data() -> None:
    ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Fixture",
            "image": {"@type": "ImageObject", "url": "https://modelspec.dev/blog/card.png"},
        }
    )
    assert (
        surface_lint.structured_data(
            {
                "blog/fixture-model/index.html": page(
                    POST, '<script type="application/ld+json">' + ld + "</script>"
                )
            }
        )
        == []
    )


def test_workflows_gate_blog_publication_and_notify_only_after_production_deploy() -> None:
    deployment = yaml.safe_load((ROOT / ".github/workflows/deploy-sites.yml").read_text())
    assert deployment["env"]["BLOG_ENABLED"] == "${{ vars.BLOG_ENABLED }}"
    build_step = next(
        step for step in deployment["jobs"]["build"]["steps"] if step.get("name") == "Build"
    )
    assert "INDEXNOW_KEY" in build_step["env"]
    live_step = next(
        step
        for step in deployment["jobs"]["build"]["steps"]
        if "python -m pipeline.live build" in step.get("run", "")
    )
    assert live_step["env"]["INDEXNOW_KEY"] == build_step["env"]["INDEXNOW_KEY"]
    steps = deployment["jobs"]["deploy"]["steps"]
    checkout = next(i for i, step in enumerate(steps) if step.get("uses") == "actions/checkout@v4")
    download = next(
        i for i, step in enumerate(steps) if step.get("uses") == "actions/download-artifact@v4"
    )
    assert checkout < download
    notify = next(step for step in steps if "pipeline.blog_indexnow" in step.get("run", ""))
    assert "needs.build.outputs.mode == 'live'" in notify["if"]
    assert "vars.BLOG_ENABLED == 'true'" in notify["if"]
    assert "steps.creds.outputs.ready == 'true'" in notify["if"]
    assert "--tree dist/modelspec" in notify["run"]
    production = next(
        i
        for i, step in enumerate(steps)
        if step.get("with", {}).get("command", "").startswith("pages deploy")
        and "--project-name=modelspec --branch=main" in step["with"]["command"]
    )
    assert steps.index(notify) > production
    automerge = yaml.safe_load((ROOT / ".github/workflows/automerge.yml").read_text())
    guard = next(
        step["run"]
        for step in automerge["jobs"]["enable"]["steps"]
        if "changed-paths.txt" in step.get("run", "")
    )
    assert re.search(r"\.github/workflows/\*\s*\|\s*blog/\*", guard)


def test_pytest_ci_fetches_the_base_for_publication_history_checks() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/test.yml").read_text())
    checkout = next(
        step
        for step in workflow["jobs"]["pytest-shards"]["steps"]
        if step.get("uses") == "actions/checkout@v4"
    )
    assert checkout.get("with", {}).get("fetch-depth") == 0
