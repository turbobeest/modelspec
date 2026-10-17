"""MODEL-126: benchmark pages live on modelspec.dev; benchgraph.dev only redirects."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import build as builder  # noqa: E402

REDIRECTS = (
    "/   https://modelspec.dev/             301\n"
    "/*  https://modelspec.dev/:splat       301\n"
)
NEEDLE = b"https://benchgraph.dev"


@pytest.fixture(scope="module")
def dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    assert builder.main(["--out", str(out), "--root", str(ROOT)]) == 0
    return out


def _catalogue_ids(dist: Path) -> list[str]:
    payload = json.loads(
        (dist / "modelspec" / "api" / "catalogue.json").read_text(encoding="utf-8"))
    return [row["id"] for row in payload["benchmarks"]]


def test_every_catalogue_benchmark_is_published(dist: Path) -> None:
    ids = _catalogue_ids(dist)
    assert ids
    ms = dist / "modelspec"
    missing_pages = [bid for bid in ids if not (ms / "b" / bid / "index.html").is_file()]
    missing_json = [
        bid for bid in ids if not (ms / "api" / "benchmarks" / f"{bid}.json").is_file()
    ]
    assert missing_pages == []
    assert missing_json == []


def test_catalogue_page_and_sitemap_list_benchmark_pages(dist: Path) -> None:
    ms = dist / "modelspec"
    assert (ms / "benchmarks" / "index.html").is_file()
    assert (ms / "api" / "catalogue.json").is_file()
    sitemap = (ms / "sitemap.xml").read_text(encoding="utf-8")
    missing = [
        bid for bid in _catalogue_ids(dist)
        if f"https://modelspec.dev/b/{bid}/" not in sitemap
    ]
    assert missing == []
    assert "https://modelspec.dev/benchmarks/" in sitemap


def test_benchgraph_tree_is_the_redirect_file(dist: Path) -> None:
    bg = dist / "benchgraph"
    files = sorted(path.relative_to(bg).as_posix() for path in bg.rglob("*") if path.is_file())
    assert files == ["_redirects"]
    assert (bg / "_redirects").read_text(encoding="utf-8") == REDIRECTS


def test_modelspec_pages_do_not_name_benchgraph_dev(dist: Path) -> None:
    root = dist / "modelspec"
    hits = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith("legal/"):
            continue
        if NEEDLE in path.read_bytes():
            hits.append(rel)
    assert hits == []


def test_use_case_pages_are_published_with_image_dates_and_method_discovery(dist: Path) -> None:
    from pipeline import surface_lint
    from decision.templates import load_templates

    tree = dist / "modelspec"
    templates = load_templates()
    image_date = builder.use_case_image_date(ROOT).isoformat()
    assert (tree / "use-cases/index.html").is_file()
    assert 'href="/use-cases/"' in (tree / "method/index.html").read_text()
    entries = dict(surface_lint.sitemap_entries((tree / "sitemap.xml").read_text()))
    for template in templates:
        path = f'/use-cases/{template["category"]}/{template["id"]}/'
        page = surface_lint.Page((tree / path.lstrip("/") / "index.html").read_text())
        url = "https://modelspec.dev" + path
        if "noindex" in page.meta["robots"]:
            assert url not in entries
        else:
            assert entries[url] == image_date
        assert page.ld
    assert entries["https://modelspec.dev/use-cases/"] == image_date
