"""Holding mode: the product pages dark, the data still up (Jamie, 2026-09-24).

One real build (what `pipeline.build` publishes, and what modelspec production
gets when `SITE_MODE=live`), and the modelspec holding tree `pipeline.holding`
derives from it (what modelspec production gets otherwise, including when the
variable is unset). benchgraph.dev is the same redirect file in both.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.modelspec import snapshot  # noqa: E402
from pipeline import build as builder  # noqa: E402
from pipeline import holding  # noqa: E402
from pipeline import legal  # noqa: E402
from pipeline.load import load_models  # noqa: E402

SITES = tuple(holding.SITES)
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-sites.yml"
_STYLE_OR_SCRIPT = re.compile(r"<(style|script)\b[^>]*>.*?</\1>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")


@pytest.fixture(scope="module")
def trees(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    out = tmp_path_factory.mktemp("sites")
    assert builder.main(["--out", str(out / "dist"), "--root", str(ROOT)]) == 0
    assert holding.main(["build", "--src", str(out / "dist"),
                         "--out", str(out / "dist-holding")]) == 0
    return {"real": out / "dist", "holding": out / "dist-holding"}


def _files(tree: Path) -> dict[str, bytes]:
    return {p.relative_to(tree).as_posix(): p.read_bytes()
            for p in sorted(tree.rglob("*")) if p.is_file()}


def _visible_text(raw: str) -> str:
    return _TAG.sub(" ", _STYLE_OR_SCRIPT.sub(" ", raw))


# ── the switch ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw", [None, "", "holding", "LIVE", "Live", " live", "live\n",
                                 "production", "true", "on"])
def test_anything_but_exactly_live_is_holding(raw):
    assert holding.resolve_mode(raw) == holding.HOLDING


def test_exactly_live_is_live():
    assert holding.resolve_mode("live") == holding.LIVE


@pytest.mark.parametrize("env, expected", [(None, "holding"), ("", "holding"),
                                           ("staging", "holding"), ("live", "live")])
def test_the_mode_command_reads_site_mode(env, expected, monkeypatch, capsys):
    if env is None:
        monkeypatch.delenv(holding.MODE_ENV, raising=False)
    else:
        monkeypatch.setenv(holding.MODE_ENV, env)
    assert holding.main(["mode"]) == 0
    assert capsys.readouterr().out == expected + "\n"


def test_the_workflow_sends_the_holding_trees_to_production_unless_live():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "\nenv:\n  SITE_MODE: ${{ vars.SITE_MODE }}\n" in text
    assert "vars.SITE_MODE ||" not in text
    assert "mode=$(python -m pipeline.holding mode)" in text
    assert ('if [ "$mode" = "live" ]; then production=dist; '
            'else production=dist-holding; fi') in text
    deploys = re.findall(r"command: pages deploy (.+?) --project-name=(\w+) --branch=(\w+)", text)
    production = "${{ needs.build.outputs.production || 'dist-holding' }}"
    assert sorted(deploys) == sorted([
        (f"{production}/modelspec", "modelspec", "main"),
        (f"{production}/benchgraph", "benchgraph", "main"),
        ("dist-internal/modelspec", "modelspec", "internal"),
        ("dist/benchgraph", "benchgraph", "internal"),
    ])


# ── the holding trees ────────────────────────────────────────────────────────

def test_the_holding_trees_are_dark(trees):
    for site in SITES:
        tree = trees["holding"] / site
        assert holding.violations(tree, site) == [], site
        for gone in ("sitemap.xml", "llms.txt", "llms-full.txt", "index.md", "_worker.js",
                     "_routes.json", "_redirects", "functions", ".well-known", "auth.md",
                     "m", "p", "b", "models", "providers", "benchmarks", "downselect",
                     "graph", "pricing", "instrument.css"):
            assert not (tree / gone).exists(), (site, gone)
    real = trees["real"] / "benchgraph"
    held = trees["holding"] / "benchgraph"
    assert _files(held) == _files(real)
    assert list(_files(held)) == ["_redirects"]
    assert (held / "_redirects").read_text(encoding="utf-8") == builder.BENCHGRAPH_REDIRECTS
    ms = trees["holding"] / "modelspec"
    assert (ms / "api" / "catalogue.json").is_file()
    assert any((ms / "api" / "benchmarks").glob("*.json"))
    assert not (ms / "b").exists()


def test_the_holding_page(trees):
    for site, name in holding.SITES.items():
        tree = trees["holding"] / site
        page = (tree / "index.html").read_text(encoding="utf-8")
        assert (tree / "404.html").read_bytes() == (tree / "index.html").read_bytes()
        assert f"<h1>{name}</h1>" in page
        assert f"{name} is in preparation. Check back soon." in page
        assert "© Sparks and Sawdust LLC" in page
        assert '<meta name="robots" content="noindex">' in page
        assert 'rel="canonical"' not in page
        assert "/api/" not in page and "api.modelspec.dev" not in page
        assert ('href="/legal/terms/"' in page) == (site == "modelspec")
        assert ('href="/legal/privacy/"' in page) == (site == "modelspec")


def test_headers_noindex_everything_and_robots_names_no_sitemap(trees):
    for site in SITES:
        tree = trees["holding"] / site
        headers = (tree / "_headers").read_text(encoding="utf-8")
        assert headers.startswith("/*\n  X-Robots-Tag: noindex\n")
        assert "Link:" not in headers
        robots = (tree / "robots.txt").read_text(encoding="utf-8")
        assert robots == "User-agent: *\nAllow: /\n"


def test_a_page_left_behind_is_caught(trees, tmp_path):
    tree = tmp_path / "modelspec"
    shutil.copytree(trees["holding"] / "modelspec", tree)
    (tree / "m" / "x").mkdir(parents=True)
    (tree / "m" / "x" / "index.html").write_text("<h1>x</h1>", encoding="utf-8")
    (tree / "sitemap.xml").write_text("<urlset/>", encoding="utf-8")
    bad = holding.violations(tree, "modelspec")
    assert any(line.startswith("m/x/index.html") for line in bad)
    assert any(line.startswith("sitemap.xml") for line in bad)


def test_no_model_name_or_score_leaks_into_any_page_or_text_file(trees):
    names = set()
    for model in load_models(ROOT):
        names.add(model.model_id.lower())
        if len(model.display_name) >= 5:
            names.add(model.display_name.lower())
    checked = 0
    for site in SITES:
        tree = trees["holding"] / site
        for path in sorted(tree.rglob("*")):
            rel = path.relative_to(tree).as_posix()
            if not path.is_file() or rel.startswith(("api/", "fonts/")):
                continue
            if path.suffix not in {".html", ".md", ".txt", ".xml", ".yaml", ""}:
                continue
            text = _visible_text(path.read_text(encoding="utf-8")).lower()
            hits = [n for n in names if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", text)]
            assert not hits, (site, rel, hits[:5])
            if rel in {"index.html", "404.html", "robots.txt"}:
                # No scores, no counts, no ranks: no digits at all.
                assert not re.search(r"\d", text), (site, rel)
            checked += 1
    # index, 404, _headers, robots, openapi.yaml, and the three legal pages.
    # benchgraph's holding page is gone, so it no longer adds files here.
    assert checked >= 8


# ── what stays exactly as the real site publishes it ─────────────────────────

def test_api_legal_and_openapi_are_byte_identical_to_the_real_build(trees):
    for site in SITES:
        held = _files(trees["holding"] / site / "api")
        real = _files(trees["real"] / site / "api")
        assert held == real, site
        assert len(held) > 100, site
    for doc in legal.DOCS:
        rel = Path(legal.LEGAL_ROOT) / doc.slug / "index.html"
        assert (trees["holding"] / "modelspec" / rel).read_bytes() == (
            trees["real"] / "modelspec" / rel).read_bytes(), doc.slug
    assert _files(trees["holding"] / "modelspec" / "legal") == _files(
        trees["real"] / "modelspec" / "legal")
    assert (trees["holding"] / "modelspec" / "openapi.yaml").read_bytes() == (
        ROOT / "api" / "worker" / "openapi.yaml").read_bytes()


def test_every_path_the_cli_workers_and_mcp_fetch_is_still_published(trees):
    ms = trees["holding"] / "modelspec"
    entry = (ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")
    worker = re.findall(r'^[A-Z_]+_PATH = "(/api/[^"]+)"', entry, re.M)
    assert len(worker) == 3, worker
    mcp = (ROOT / "mcp" / "src" / "server.ts").read_text(encoding="utf-8")
    assert "/api/rank/profiles.json`" in mcp
    paths = [*snapshot.PARTS.values(), *snapshot.OPTIONAL_PARTS.values(), *worker,
             "/api/rank/profiles.json", "/api/rank/class-fit.json", "/api/build.json"]
    for path in paths:
        assert (ms / path.lstrip("/")).is_file(), path
    # MCP `model_info` reads /api/models/<provider>/<slug>.json for any card.
    for model in load_models(ROOT)[:25]:
        assert (ms / "api" / "models" / f"{model.model_id}.json").is_file(), model.model_id
    assert (ms / "api" / "catalogue.json").is_file()
    assert any((ms / "api" / "benchmarks").glob("*.json"))


# ── SITE_MODE=live: today's site ─────────────────────────────────────────────

def test_live_production_is_the_real_build_unchanged(trees):
    """Live mode deploys `dist`. Holding mode only reads it."""
    ms, bg = trees["real"] / "modelspec", trees["real"] / "benchgraph"
    assert len(list((ms / "m").glob("*/*/index.html"))) == len(load_models(ROOT))
    for rel in ("sitemap.xml", "llms.txt", "llms-full.txt", "index.md", "_worker.js",
                ".well-known/mcp.json", "openapi.yaml", "auth.md", "pricing/index.html",
                "downselect/index.html", "graph/index.html", "models/index.html"):
        assert (ms / rel).is_file(), rel
    files = sorted(path.relative_to(bg).as_posix() for path in bg.rglob("*") if path.is_file())
    assert files == ["_redirects"]
    assert (bg / "_redirects").read_text(encoding="utf-8") == builder.BENCHGRAPH_REDIRECTS
    assert "in preparation" not in (ms / "index.html").read_text(encoding="utf-8")
    assert "X-Robots-Tag" not in (ms / "_headers").read_text(encoding="utf-8")
    assert "Sitemap:" in (ms / "robots.txt").read_text(encoding="utf-8")


def test_a_redirect_only_benchgraph_is_copied_and_modelspec_still_goes_dark(tmp_path):
    src = tmp_path / "src"
    ms = src / "modelspec"
    for rel in ("api", "legal", "fonts"):
        (ms / rel).mkdir(parents=True)
    (ms / "index.html").write_text("real", encoding="utf-8")
    bg = src / "benchgraph"
    bg.mkdir()
    (bg / "_redirects").write_text(builder.BENCHGRAPH_REDIRECTS, encoding="utf-8")
    out = tmp_path / "out"
    assert holding.main(["build", "--src", str(src), "--out", str(out)]) == 0
    assert (out / "benchgraph" / "_redirects").read_bytes() == (bg / "_redirects").read_bytes()
    assert list(_files(out / "benchgraph")) == ["_redirects"]
    assert holding.violations(out / "modelspec", "modelspec") == []
    assert not (out / "modelspec" / "b").exists()


def test_benchgraph_holding_rejects_anything_but_the_redirect(tmp_path):
    src = tmp_path / "src"
    real = src / "benchgraph"
    real.mkdir(parents=True)
    (real / "index.html").write_text("page", encoding="utf-8")
    with pytest.raises(ValueError):
        holding.build(src, tmp_path / "out-extra")
    (real / "index.html").unlink()
    (real / "_redirects").write_text("/   https://example.test/  301\n", encoding="utf-8")
    with pytest.raises(ValueError):
        holding.build(src, tmp_path / "out-wrong")
    shutil.rmtree(real)
    with pytest.raises(FileNotFoundError):
        holding.build(src, tmp_path / "out-missing")
