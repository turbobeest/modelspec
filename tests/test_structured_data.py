"""JSON-LD on the live pages, and the crawl audit that checks it (MODEL-218)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline import structured_data as sd
from scripts import seo_audit

ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = re.compile(r'<script type="application/ld\+json" data-structured-data>(.*?)</script>',
                     re.DOTALL)


def _tree(tmp_path: Path, *, snapshot: bool = False) -> Path:
    tree = tmp_path / "modelspec"
    (tree / "api" / "decision").mkdir(parents=True)
    (tree / "api" / "build.json").write_text(json.dumps(
        {"built_at": "2026-09-29T19:11:08+00:00", "export_schema_version": "3.0"}))
    (tree / "api" / "index.json").write_text(json.dumps({"count": 1372}))
    if snapshot:
        (tree / "api" / "decision" / "snapshot.json.gz").write_bytes(b"\x1f\x8b")
    for path in ("/", *sd.CRUMBS):
        page = tree / path.lstrip("/") / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("<!doctype html><html lang=en><head><title>t</title></head>"
                        "<body><h1>t</h1></body></html>")
    return tree


def _graph(tree: Path, path: str) -> list[dict]:
    html = (tree / path.lstrip("/") / "index.html").read_text()
    blocks = _SCRIPT.findall(html)
    assert len(blocks) == 1, f"{path}: {len(blocks)} blocks"
    return json.loads(blocks[0])["@graph"]


def _types(nodes: list[dict]) -> list[str]:
    return ["/".join(n["@type"]) if isinstance(n["@type"], list) else n["@type"] for n in nodes]


def test_every_page_gets_one_block_and_a_rerun_replaces_it(tmp_path: Path) -> None:
    tree = _tree(tmp_path)

    assert sd.inject(tree, ROOT) == ["/", *sd.CRUMBS]
    sd.inject(tree, ROOT)

    assert _types(_graph(tree, "/")) == [
        "Organization", "WebSite", "Dataset",
        "WebAPI/SoftwareApplication", "SoftwareApplication",
    ]
    assert _types(_graph(tree, "/decide/")) == ["BreadcrumbList", "WebApplication"]
    assert _types(_graph(tree, "/legal/terms/")) == ["BreadcrumbList"]


def test_a_page_without_a_head_end_tag_gets_the_block_at_the_end(tmp_path: Path) -> None:
    tree = _tree(tmp_path)
    (tree / "decide" / "index.html").write_text("<!doctype html><title>Decide</title>")
    sd.inject(tree, ROOT)

    html = (tree / "decide" / "index.html").read_text()

    assert html.startswith("<!doctype html><title>Decide</title><script")
    assert _types(_graph(tree, "/decide/")) == ["BreadcrumbList", "WebApplication"]


def test_a_missing_page_is_skipped(tmp_path: Path) -> None:
    tree = _tree(tmp_path)
    (tree / "pricing" / "index.html").unlink()

    assert "/pricing/" not in sd.inject(tree, ROOT)


def test_the_breadcrumb_names_the_page_and_links_home(tmp_path: Path) -> None:
    tree = _tree(tmp_path)
    sd.inject(tree, ROOT)

    crumbs = _graph(tree, "/legal/neutrality/")[0]["itemListElement"]

    assert [(c["position"], c["name"], c["item"]) for c in crumbs] == [
        (1, "ModelSpec", "https://modelspec.dev/"),
        (2, "Neutrality commitment", "https://modelspec.dev/legal/neutrality/"),
    ]


def test_the_dataset_offers_no_download_and_no_free_flag(tmp_path: Path) -> None:
    tree = _tree(tmp_path, snapshot=True)
    sd.inject(tree, ROOT)

    dataset = _graph(tree, "/")[2]

    assert "distribution" not in dataset
    assert "isAccessibleForFree" not in dataset
    assert "delayed image" in dataset["description"]
    assert dataset["version"] == "3.0"
    assert dataset["dateModified"] == "2026-09-29T19:11:08+00:00"
    assert "1372 AI models" in dataset["description"]


def test_every_object_passes_the_audit_rich_result_rules(tmp_path: Path) -> None:
    tree = _tree(tmp_path, snapshot=True)
    sd.inject(tree, ROOT)

    errors = [
        (path, message)
        for path in ("/", *sd.CRUMBS)
        for node in _graph(tree, path)
        for level, message in seo_audit.check_json_ld(node)
        if level == "error"
    ]

    assert errors == []


def test_configured_profiles_become_the_organization_same_as(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "brand" / "social").mkdir(parents=True)
    (root / "brand" / "social" / "profiles.json").write_text(json.dumps(
        {"x": "modelspecdev", "instagram": "", "tiktok": "", "linkedin": "modelspec-dev"}))
    (root / "pyproject.toml").write_text('[project]\nname = "modelspec-dev"\nversion = "9.9.9"\n')
    tree = _tree(tmp_path)
    sd.inject(tree, root)

    nodes = _graph(tree, "/")

    assert nodes[0]["sameAs"] == [
        "https://github.com/turbobeest/modelspec",
        "https://x.com/modelspecdev", "https://www.linkedin.com/company/modelspec-dev/"]
    assert nodes[3]["name"] == "ModelSpec API"
    assert all("downloadUrl" not in node for node in nodes)


def test_markup_in_a_value_cannot_end_the_script() -> None:
    html = sd.script([{"@type": "Thing", "name": "<!--<script></script><b>"}])

    assert html.count("<") == 2
    assert json.loads(_SCRIPT.search(html).group(1))["@graph"][0]["name"] == "<!--<script></script><b>"


def test_nothing_is_rated_or_reviewed(tmp_path: Path) -> None:
    tree = _tree(tmp_path, snapshot=True)
    sd.inject(tree, ROOT)

    for path in ("/", *sd.CRUMBS):
        for node in _graph(tree, path):
            assert not {"aggregateRating", "review"} & set(node), path


def _site(pages: dict[str, tuple[int, str, bytes]]):
    def get(url: str):
        status, kind, body = pages.get(url, (404, "text/html", b""))
        return status, {"content-type": kind}, body
    return get


def _html(path: str, *, robots: str = "", extra: str = "") -> bytes:
    meta = f'<meta name="robots" content="{robots}">' if robots else ""
    return (f'<html lang="en"><head><title>T</title><meta name="description" content="d">'
            f'<meta property="og:image" content="https://x.test/o.png">{meta}'
            f'<link rel="canonical" href="https://x.test{path}"></head>'
            f"<body><h1>T</h1>{extra}</body></html>").encode()


def test_the_audit_names_a_noindex_sitemap_page_an_orphan_and_a_dead_link() -> None:
    discovery = {f"https://x.test{p}": (200, "text/plain", b"x") for p in seo_audit.DISCOVERY}
    site = {
        **discovery,
        "https://x.test/robots.txt": (200, "text/plain", b"Sitemap: https://x.test/sitemap.xml"),
        "https://x.test/sitemap.xml": (200, "application/xml",
                                       b"<loc>https://x.test/</loc><loc>https://x.test/a/</loc>"),
        "https://x.test/": (200, "text/html",
                            _html("/", extra='<a href="/a/">a</a><a href="/b/">b</a>'
                                             '<a href="/gone/">g</a>')),
        "https://x.test/a/": (200, "text/html", _html("/a/", robots="noindex")),
        "https://x.test/b/": (200, "text/html", _html("/b/")),
    }

    _, findings, _ = seo_audit.audit("https://x.test", get=_site(site))

    errors = sorted((f.where, f.what) for f in findings if f.level == "error")
    assert errors == [
        ("/a/", "in the sitemap but noindex"),
        ("/b/", "indexable, self-canonical, not in the sitemap"),
        ("/gone/", "answers 404 (linked from /)"),
    ]


def test_the_audit_applies_the_rich_result_rules() -> None:
    assert seo_audit.check_json_ld({"@type": "Dataset", "name": "n", "description": "short"}) == [
        ("error", "Dataset: description is 5 chars (50-5000)")]
    assert seo_audit.check_json_ld({"@type": "Dataset", "name": "n", "description": "d" * 50,
                                    "distribution": {"@type": "DataDownload"}}) == [
        ("error", "Dataset: distribution without contentUrl")]
    assert seo_audit.check_json_ld({"@type": "BreadcrumbList", "itemListElement": [
        {"position": 1, "name": "a"}, {"position": 2, "name": "b"}]}) == [
        ("error", "BreadcrumbList: item 1 lacks item URL")]
    assert seo_audit.check_json_ld({"@type": "Article"}) == [
        ("error", "Article: headline missing"), ("warn", "Article: author missing"),
        ("warn", "Article: datePublished missing"), ("warn", "Article: image missing")]
