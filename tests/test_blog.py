"""MODEL-223: observe the fixture blog through its static output."""

from __future__ import annotations

import base64
import json
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import pytest
import yaml

from pipeline.export import Build

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "blog"
SLUG = "2026-09-26-alpha"
POST = f"/blog/{SLUG}/"
KEYS = {
    key: base64.b64decode(value)
    for key, value in json.loads((FIXTURE / "public-keys.json").read_text()).items()
}
BUILD = Build("2b0770af", "2026-09-26T00:00:00Z", date(2026, 9, 26))
ATOM = {"a": "http://www.w3.org/2005/Atom"}


@pytest.fixture
def blog_root(tmp_path, monkeypatch):
    root = tmp_path / "source"
    shutil.copytree(FIXTURE, root / "blog")
    standard = root / "docs" / "method" / "release-breakdown-standard.md"
    standard.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "docs" / "method" / standard.name, standard)
    monkeypatch.setenv("BLOG_ENABLED", "true")
    return root


def publish(root, revision=1):
    path = root / "blog" / "posts" / SLUG / "post.yaml"
    metadata = yaml.safe_load(path.read_text())
    metadata["status"] = "published"
    metadata["revisions"][revision - 1].update(
        {
            "published": date(2026, 9, 26),
            "approved_by": "fixture-reviewer",
            "approval": "https://github.com/turbobeest/modelspec/pull/0#fixture-only",
        }
    )
    path.write_text(yaml.safe_dump(metadata))


def write_blog(root, out):
    from pipeline import blog

    return blog.write(out, root, BUILD, public_keys=KEYS)


def test_published_markdown_renders_sections_provenance_tags_and_feeds(blog_root, tmp_path):
    publish(blog_root)
    out = tmp_path / "site"
    result = write_blog(blog_root, out)
    page = (out / POST.lstrip("/") / "index.html").read_text()
    for heading in (
        "Claims and evidence",
        "Where it lands",
        "Cost",
        "Hardware",
        "Not measured yet",
        "Sources and decisions",
        "Reproduce this",
    ):
        assert heading in page
    assert "<table>" in page and 'id="fn-1"' in page
    assert 'class="lockup"' in page and "color-scheme:dark" in page
    assert f'<link rel="canonical" href="https://modelspec.dev{POST}">' in page
    assert "Not published: a draft" not in page
    breakdown = json.loads((FIXTURE / "posts" / SLUG / "r1" / "breakdown.json").read_text())
    after = breakdown["generated_from"]["after"]
    snapshot_path = f"/api/decision/snapshots/{after['snapshot_id']}.json.gz"
    assert snapshot_path in page
    assert after["content_hash"] in page and after["key_id"] in page
    assert (out / snapshot_path.lstrip("/")).read_bytes() == (
        FIXTURE / "snapshots" / f"{after['snapshot_id']}.json.gz"
    ).read_bytes()
    for decision in breakdown["decisions"]:
        assert f'id="{decision["decision_id"]}"' in page
        assert f"#{decision['decision_id']}" in page
        assert decision["spec_hash"] in page
    assert "python -m release_blog render --breakdown" in page
    assert f"/blog/{SLUG}/r1/breakdown.json" in page
    assert '<a href="/blog/tags/lab/lab/">' in page
    assert '<a href="/blog/tags/model/lab-alpha/">' in page
    assert '<a href="/blog/tags/domain/software-engineering/">' in page
    for tag in ("lab/lab", "model/lab-alpha", "domain/software-engineering"):
        assert SLUG in (out / "blog" / "tags" / tag / "index.html").read_text()
    assert POST in result["sitemap_paths"]
    assert f"{POST}r1/" in result["sitemap_paths"]
    assert "Alpha model release breakdown" in (out / "blog" / "index.html").read_text()
    atom = ET.parse(out / "blog" / "feed.xml").getroot()
    assert atom.tag == "{http://www.w3.org/2005/Atom}feed"
    entry = atom.find("a:entry", ATOM)
    assert entry is not None
    assert entry.findtext("a:title", namespaces=ATOM) == "Alpha model release breakdown"
    assert entry.findtext("a:updated", namespaces=ATOM) == "2026-09-26T00:00:00Z"
    assert entry.find("a:link", ATOM).attrib["href"] == f"https://modelspec.dev{POST}r1/"
    rss = ET.parse(out / "blog" / "rss.xml").getroot()
    assert rss.tag == "rss" and rss.attrib["version"] == "2.0"
    assert rss.findtext("channel/item/title") == "Alpha model release breakdown"
    assert rss.findtext("channel/item/link") == f"https://modelspec.dev{POST}r1/"
    ld = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S)
    assert ld is not None
    graph = json.loads(ld.group(1))
    assert graph["@context"] == "https://schema.org"
    article = next(node for node in graph["@graph"] if node["@type"] == "Article")
    assert article["headline"] == "Alpha model release breakdown"
    assert article["datePublished"] == "2026-09-26"
    assert article["mainEntityOfPage"] == f"https://modelspec.dev{POST}"
    assert article["image"] == f"https://modelspec.dev{POST}r1/og-card.png"
    assert f'property="og:image" content="{article["image"]}"' in page


@pytest.mark.parametrize("flag", [None, "", "false", "TRUE", "1"])
def test_disabled_blog_has_no_pages_feeds_nav_or_sitemap(blog_root, tmp_path, monkeypatch, flag):
    publish(blog_root)
    if flag is None:
        monkeypatch.delenv("BLOG_ENABLED")
    else:
        monkeypatch.setenv("BLOG_ENABLED", flag)
    result = write_blog(blog_root, tmp_path / "site")
    assert not (tmp_path / "site" / "blog").exists()
    assert result["sitemap_paths"] == []


def test_draft_post_never_reaches_output(blog_root, tmp_path):
    write_blog(blog_root, tmp_path / "site")
    assert not (tmp_path / "site" / "blog" / SLUG).exists()
    assert SLUG not in (tmp_path / "site" / "blog" / "feed.xml").read_text()


@pytest.mark.parametrize(
    "text,problem",
    [
        ("A reading of 71 percent.", "bare digit"),
        ("The result looks inflated.", "refused"),
        ("{{n:/missing}}", "pointer"),
        ("{{n:/model/name}}", "cited"),
        ("[extra](https://affiliate.example/?tracking=one)", "outbound"),
    ],
)
def test_invalid_commentary_refuses_the_build(blog_root, tmp_path, text, problem):
    publish(blog_root)
    (blog_root / "blog" / "posts" / SLUG / "commentary.md").write_text(text)
    with pytest.raises(ValueError, match=problem):
        write_blog(blog_root, tmp_path / "site")


def test_unapproved_revision_and_unsigned_snapshot_are_refused(blog_root, tmp_path):
    publish(blog_root)
    metadata = blog_root / "blog" / "posts" / SLUG / "post.yaml"
    text = metadata.read_text()
    metadata.write_text(text.replace("fixture-reviewer", "''"))
    with pytest.raises(ValueError, match="approval"):
        write_blog(blog_root, tmp_path / "site")
    metadata.write_text(text)
    with pytest.raises(ValueError, match="key|signature"):
        from pipeline import blog

        blog.write(tmp_path / "other", blog_root, BUILD, public_keys={})


def test_snapshot_path_matches_worker_history_contract():
    from pipeline.blog import SNAPSHOT_PATH

    # Read the actual Worker's constant without importing its runtime bindings.
    source = (ROOT / "api" / "worker" / "src" / "entry.py").read_text()
    assert f'DECISION_HISTORY_TEMPLATE = "{SNAPSHOT_PATH}"' in source


def test_blog_is_not_in_holding_allowlist():
    from pipeline.holding import KEEP_DIRS

    assert "blog" not in KEEP_DIRS["modelspec"]


@pytest.mark.parametrize(
    "url,sources",
    [
        ("javascript:alert", {"javascript:alert"}),
        ("/\\affiliate.example/path", set()),
    ],
)
def test_blog_markdown_refuses_executable_or_disguised_external_urls(url, sources):
    from pipeline.blog_markdown import render

    with pytest.raises(ValueError, match="outbound"):
        render(f"[source]({url})", sources)


def test_corrections_update_feed_timestamp_and_get_their_own_entries(blog_root, tmp_path):
    publish(blog_root)
    correction = {
        "id": "c1",
        "date": date(2026, 10, 1),
        "revision": 1,
        "field": "/claims_vs_evidence/claims/0/claim",
        "was": {"value": 70, "record_id": "fixture-old", "snapshot_id": "snap_old"},
        "now": {"value": 69, "record_id": "fixture-new", "snapshot_id": "snap_new"},
        "effect": "The lab reading has a correction.",
        "fix_pr": "https://github.com/turbobeest/modelspec/pull/0#fixture-only",
    }
    (blog_root / "blog" / "posts" / SLUG / "corrections.yaml").write_text(
        yaml.safe_dump([correction])
    )
    write_blog(blog_root, tmp_path / "site")
    feed = ET.parse(tmp_path / "site" / "blog" / "feed.xml").getroot()
    assert feed.findtext("a:updated", namespaces=ATOM) == "2026-10-01T00:00:00Z"
    entries = feed.findall("a:entry", ATOM)
    assert len(entries) == 2
    assert entries[0].findtext("a:id", namespaces=ATOM) == f"https://modelspec.dev{POST}#c1"
    page = (tmp_path / "site" / "blog" / SLUG / "index.html").read_text()
    assert page.index("Corrections") < page.index("Claims and evidence")


def test_preview_writes_draft_charts_and_breakdown_without_discovery(
    blog_root, tmp_path, monkeypatch
):
    from pipeline import blog
    from release_blog import gates

    monkeypatch.setattr(gates, "load_public_keys", lambda: KEYS)
    out = tmp_path / "preview"
    assert blog.main(["preview", SLUG, "--root", str(blog_root), "--out", str(out)]) == 0
    revision = out / "blog" / SLUG / "r1"
    assert (revision / "breakdown.json").is_file()
    assert len(list((revision / "charts").glob("*.svg"))) == 3
    assert 'content="noindex, nofollow"' in (revision / "index.html").read_text()
    assert not list(out.rglob("feed.xml")) and not list(out.rglob("sitemap.xml"))


def test_site_build_includes_fixture_blog_from_public_root_only(tmp_path, monkeypatch):
    from pipeline import build
    from release_blog import gates

    root = tmp_path / "public-root"
    root.mkdir()
    for item in ROOT.iterdir():
        if item.name not in {"blog", "dist", ".git", ".artifacts"}:
            (root / item.name).symlink_to(item, target_is_directory=item.is_dir())
    shutil.copytree(FIXTURE, root / "blog")
    publish(root)
    monkeypatch.setenv("BLOG_ENABLED", "true")
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    monkeypatch.setattr(gates, "load_public_keys", lambda: KEYS)
    out = tmp_path / "dist"
    assert build.main(["--root", str(root), "--out", str(out)]) == 0
    assert (out / "modelspec" / "blog" / SLUG / "index.html").is_file()
    sitemap = ET.parse(out / "modelspec" / "sitemap.xml")
    assert f"https://modelspec.dev{POST}" in [
        node.text for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    ]
