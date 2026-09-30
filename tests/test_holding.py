"""Holding mode: the product pages dark, the data still up (Jamie, 2026-09-24).

One real build (what `pipeline.build` publishes, and what modelspec production
gets when `SITE_MODE=live`), and the modelspec holding tree `pipeline.holding`
derives from it (what modelspec production gets otherwise, including when the
variable is unset). benchgraph.dev is the same redirect file in both.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cli.modelspec import snapshot  # noqa: E402
from pipeline import brand  # noqa: E402
from pipeline import build as builder  # noqa: E402
from pipeline import holding  # noqa: E402
from pipeline import legal  # noqa: E402
from pipeline import live  # noqa: E402
from pipeline import landing  # noqa: E402
from pipeline import social_cards  # noqa: E402
from pipeline import structured_data  # noqa: E402
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
    # The decide app is a Vite build CI makes in web/; a stand-in is enough here.
    web = out / "web"
    (web / "assets").mkdir(parents=True)
    (web / "decide.html").write_text("<!doctype html><title>Decide</title>", encoding="utf-8")
    (web / "assets" / "decide-x.js").write_text("", encoding="utf-8")
    (web / "assets" / "main-x.js").write_text("", encoding="utf-8")
    assert live.main(["build", "--src", str(out / "dist"), "--web", str(web),
                      "--out", str(out / "dist-live")]) == 0
    return {"real": out / "dist", "holding": out / "dist-holding", "live": out / "dist-live"}


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


def test_the_holding_root_is_the_landing_and_the_404_stays_dark(trees):
    tree = trees["holding"] / "modelspec"
    page = (tree / "index.html").read_text(encoding="utf-8")
    not_found = (tree / "404.html").read_text(encoding="utf-8")
    assert "Model routers make educated guesses." in page
    assert "Board opening soon" in page
    assert '<link rel="canonical" href="https://modelspec.dev/">' in page
    assert 'content="noindex"' not in page
    assert "ModelSpec is in preparation. Check back soon." in not_found
    assert '<meta name="robots" content="noindex">' in not_found
    assert 'rel="canonical"' not in not_found


def test_the_holding_tree_is_exactly_its_expected_file_set(trees):
    ms = trees["holding"] / "modelspec"
    top = sorted(p.name + ("/" if p.is_dir() else "") for p in ms.iterdir())
    card = [social_cards.LANDING_IMAGE] if social_cards.render_enabled() else []
    assert top == sorted(["api/", "legal/", "fonts/", "landing-assets/",
                          "feedback-assets/", "openapi.yaml",
                          *brand.FILES, *card, *holding.WRITTEN])
    for name in (*brand.FILES, *card):
        assert (ms / name).read_bytes() == (trees["real"] / "modelspec" / name).read_bytes(), name


def test_the_holding_page_links_the_2a_icons_and_social_card(trees):
    page = (trees["holding"] / "modelspec" / "index.html").read_text(encoding="utf-8")
    assert brand.head_links() in page
    card = social_cards.landing_card(landing.extract_data(page))
    assert brand.social_meta(
        landing.TITLE, image_name=card.filename, image_alt=card.alt,
    ) in page


def test_headers_index_only_the_root_and_robots_names_no_sitemap(trees):
    for site in SITES:
        tree = trees["holding"] / site
        headers = (tree / "_headers").read_text(encoding="utf-8")
        assert headers.startswith("/*\n  X-Robots-Tag: noindex\n")
        assert "/\n  ! X-Robots-Tag\n" in headers
        assert "/index.html\n  ! X-Robots-Tag\n" in headers
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


def test_the_dark_404_does_not_leak_model_names_or_scores(trees):
    text = _visible_text(
        (trees["holding"] / "modelspec" / "404.html").read_text(encoding="utf-8")
    ).lower()
    for model in load_models(ROOT):
        assert model.display_name.lower() not in text
    assert not re.search(r"\d", text)


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
    assert len(worker) == 4, worker
    mcp = (ROOT / "mcp" / "src" / "server.ts").read_text(encoding="utf-8")
    assert "/api/rank/profiles.json`" in mcp
    always_published = [path for path in worker if path != "/api/decision/snapshot.json.gz"]
    paths = [*snapshot.PARTS.values(), *snapshot.OPTIONAL_PARTS.values(), *always_published,
             "/api/rank/profiles.json", "/api/rank/class-fit.json", "/api/build.json"]
    for path in paths:
        assert (ms / path.lstrip("/")).is_file(), path
    # MCP `model_info` reads /api/models/<provider>/<slug>.json for any card.
    for model in load_models(ROOT)[:25]:
        assert (ms / "api" / "models" / f"{model.model_id}.json").is_file(), model.model_id
    assert (ms / "api" / "catalogue.json").is_file()
    assert any((ms / "api" / "benchmarks").glob("*.json"))


# ── the full source tree used to derive holding ──────────────────────────────

def test_full_build_still_contains_every_source_page_before_composition(trees):
    """The workflow derives holding before replacing dist with the live composition."""
    ms, bg = trees["real"] / "modelspec", trees["real"] / "benchgraph"
    assert len(list((ms / "m").glob("*/*/index.html"))) == len(load_models(ROOT))
    for rel in ("sitemap.xml", "llms.txt", "llms-full.txt", "index.md", "_worker.js",
                ".well-known/mcp.json", "openapi.yaml", "auth.md", "pricing/index.html",
                "downselect/index.html", "graph/index.html", "models/index.html",
                "decide/index.html", "landing-assets/landing.css", "landing-assets/landing.js"):
        assert (ms / rel).is_file(), rel
    files = sorted(path.relative_to(bg).as_posix() for path in bg.rglob("*") if path.is_file())
    assert files == ["_redirects"]
    assert (bg / "_redirects").read_text(encoding="utf-8") == builder.BENCHGRAPH_REDIRECTS
    assert "in preparation" not in (ms / "index.html").read_text(encoding="utf-8")
    headers = (ms / "_headers").read_text(encoding="utf-8")
    assert "X-Robots-Tag" not in headers
    assert '</llms.txt>; rel="describedby"' in headers
    assert 'Content-Type: application/linkset+json' in headers
    assert "Sitemap:" in (ms / "robots.txt").read_text(encoding="utf-8")


def test_a_redirect_only_benchgraph_is_copied_and_modelspec_still_goes_dark(tmp_path):
    src = tmp_path / "src"
    ms = src / "modelspec"
    for rel in ("api", "legal", "fonts", "landing-assets", "feedback-assets"):
        (ms / rel).mkdir(parents=True)
    decision = ms / "api" / "decision" / "snapshot.json.gz"
    decision.parent.mkdir()
    decision.write_bytes(b"signed snapshot fixture")
    model = landing.PlotModel("model", "Fixture Model", .1, 1, 0, 2, True)
    data = landing.LandingData(
        "2026-09-27", 1, 40_000, 4_000, 10_000, (model,), "model", "model", 1,
        1000, 1000, 0, (), 0,
        landing._plot_axes([model]),
    )
    (ms / "index.html").write_text(
        landing.render(data, variant="live"),
        encoding="utf-8",
    )
    for name in ("landing.css", "landing.js"):
        (ms / "landing-assets" / name).write_text("fixture", encoding="utf-8")
    bg = src / "benchgraph"
    bg.mkdir()
    (bg / "_redirects").write_text(builder.BENCHGRAPH_REDIRECTS, encoding="utf-8")
    out = tmp_path / "out"
    assert holding.main(["build", "--src", str(src), "--out", str(out)]) == 0
    assert (out / "benchgraph" / "_redirects").read_bytes() == (bg / "_redirects").read_bytes()
    assert list(_files(out / "benchgraph")) == ["_redirects"]
    assert holding.violations(out / "modelspec", "modelspec") == []
    assert (out / "modelspec" / "api" / "decision" / "snapshot.json.gz").read_bytes() == (
        decision.read_bytes()
    )
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


# ── the live tree (MODEL-214) ────────────────────────────────────────────────

def test_the_live_tree_publishes_agent_discovery_and_every_link_in_it_resolves(trees):
    ms = trees["live"] / "modelspec"
    for rel in live.DISCOVERY:
        assert (ms / rel).is_file(), rel
    assert live.dead_links(ms) == []
    llms = (ms / "llms.txt").read_text(encoding="utf-8")
    for url in ("https://modelspec.dev/llms-full.txt", "https://modelspec.dev/auth.md",
                "https://modelspec.dev/.well-known/mcp.json"):
        assert url in llms
    assert 'type="text/markdown" href="/index.md"' in (ms / "index.html").read_text(encoding="utf-8")
    for page in live.PAGES:
        assert live.resolves(ms, page), page


def test_every_live_page_carries_one_json_ld_graph(trees):
    ms = trees["live"] / "modelspec"
    assert set(live.PAGES) == {"/", *structured_data.CRUMBS}
    for page in live.PAGES:
        html = (ms / page.lstrip("/") / "index.html").read_text(encoding="utf-8")
        blocks = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
        assert len(blocks) == 1, page
        assert json.loads(blocks[0])["@graph"], page


def test_the_live_tree_is_an_allowlist(trees):
    ms = trees["live"] / "modelspec"
    for gone in ("m", "p", "b", "models", "providers", "benchmarks", "downselect",
                 "_worker.js", "_routes.json", "functions", "instrument.css",
                 "assets/main-x.js"):
        assert not (ms / gone).exists(), gone
    assert (ms / "assets" / "decide-x.js").is_file()
    decide = (ms / "decide" / "index.html").read_text(encoding="utf-8")
    not_found = (ms / "404.html").read_text(encoding="utf-8")
    assert not_found != decide
    assert '<meta name="robots" content="noindex">' in not_found
    assert 'rel="canonical"' not in not_found
    for href in ("/", "/decide/", "/method/"):
        assert f'href="{href}"' in not_found, href
    assert _files(trees["live"] / "benchgraph") == _files(trees["real"] / "benchgraph")
    for rel in ("api", "legal"):
        assert _files(ms / rel) == _files(trees["real"] / "modelspec" / rel), rel
    assert "Sitemap: https://modelspec.dev/sitemap.xml" in (ms / "robots.txt").read_text(encoding="utf-8")
    headers = (ms / "_headers").read_text(encoding="utf-8")
    assert "X-Robots-Tag" not in headers
    assert '</llms.txt>; rel="describedby"' in headers
    assert 'Content-Type: application/linkset+json' in headers
    assert "/api/*\n  Access-Control-Allow-Origin: *\n" in headers


def test_dead_links_names_a_discovery_file_the_tree_lacks(tmp_path):
    (tmp_path / "index.html").write_text(
        '<link rel="alternate" type="text/markdown" href="/index.md">'
        '<a href="/models/">Models</a><a href="//cdn.example/x">cdn</a>'
        '<code>https://modelspec.dev/api/</code>', encoding="utf-8")
    (tmp_path / "llms.txt").write_text(
        "- https://modelspec.dev/decide/\n- https://modelspec.dev/auth.md\n", encoding="utf-8")
    (tmp_path / "_headers").write_text('/*\n  Link: </sitemap.xml>; rel="sitemap"\n',
                                       encoding="utf-8")
    (tmp_path / "decide").mkdir()
    (tmp_path / "decide" / "index.html").write_text("", encoding="utf-8")
    dead = live.dead_links(tmp_path)
    assert "llms.txt: /auth.md" in dead
    assert "llms.txt: /decide/" not in dead
    assert "index.md: missing" in dead
    assert "index.html: /index.md" in dead
    # MODEL-214: the legal pages' nav still named the retired v1 catalogue.
    assert "index.html: /models/" in dead
    assert not [line for line in dead if "cdn.example" in line or line == "index.html: /api/"]
    assert "method/index.html: missing" in dead
    assert "_headers: /sitemap.xml" in dead


def test_smoke_reports_each_discovery_path_that_is_not_served_as_built():
    link = '</llms.txt>; rel="describedby", </.well-known/api-catalog>; rel="api-catalog", </sitemap.xml>; rel="sitemap"'

    def fetch(url):
        if url.endswith("/llms.txt"):
            return 404, {}, b""
        if url.endswith("/api-catalog"):
            return 200, {"content-type": "application/octet-stream"}, b"{}"
        if url == "https://modelspec.dev/":
            return 200, {"link": link.replace(', </sitemap.xml>; rel="sitemap"', "")}, b"ok"
        return 200, {"content-type": "application/linkset+json", "link": link}, b"ok"

    assert live.smoke("https://modelspec.dev", fetch) == [
        "/llms.txt: 404",
        "/.well-known/api-catalog: Content-Type 'application/octet-stream', not application/linkset+json",
        '/: Link header lacks rel="sitemap"',
    ]


def test_the_workflow_assembles_live_with_the_module_and_smokes_discovery():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python -m pipeline.live build --src dist-v1 --web web/dist --out dist" in text
    assert "python -m pipeline.live smoke --origin https://modelspec.dev" in text
    assert "python -m pipeline.live smoke --origin https://internal.modelspec-7np.pages.dev" in text


def test_each_headers_file_has_one_star_rule_carrying_everything(trees):
    # Cloudflare Pages drops the earlier of two `/*` rules (MODEL-238 regression).
    needed = {
        "live": ("Link:", "Strict-Transport-Security:", "Permissions-Policy:",
                 "X-Content-Type-Options:", "Content-Security-Policy:", "X-Frame-Options:"),
        "holding": ("Strict-Transport-Security:", "X-Content-Type-Options:",
                    "Content-Security-Policy:", "X-Frame-Options:"),
    }
    for name, wanted in needed.items():
        lines = (trees[name] / "modelspec" / "_headers").read_text(encoding="utf-8").splitlines()
        assert lines.count("/*") == 1, name
        start = lines.index("/*") + 1
        rule = []
        for line in lines[start:]:
            if not line.startswith("  "):
                break
            rule.append(line.strip())
        for header in wanted:
            assert any(r.startswith(header) for r in rule), (name, header)


def test_every_executable_inline_script_is_in_the_policy_and_both_trees_carry_it(trees):
    exec_types = {"", "module", "text/javascript", "application/javascript"}
    inline = re.compile(r"<script((?:\s[^>]*)?)>(.*?)</script>", re.S)
    for name in ("live", "holding"):
        ms = trees[name] / "modelspec"
        policy = next(line for line in (ms / "_headers").read_text(encoding="utf-8").splitlines()
                      if "Content-Security-Policy:" in line)
        assert "X-Frame-Options: DENY" in (ms / "_headers").read_text(encoding="utf-8")
        assert "frame-ancestors 'none'" in policy
        for page in ms.rglob("*.html"):
            for attrs, body in inline.findall(page.read_text(encoding="utf-8")):
                if "src=" in attrs:
                    continue
                kind = re.search(r'type="([^"]*)"', attrs)
                if kind and kind.group(1) not in exec_types:
                    continue
                digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
                assert f"'sha256-{digest}'" in policy, (name, page.name)


def test_legacy_v1_urls_redirect_to_decide_and_the_api_is_untouched(trees):
    rules = (trees["live"] / "modelspec" / "_redirects").read_text(encoding="utf-8")
    for source in ("/models", "/models/", "/providers/", "/benchmarks/", "/downselect/",
                   "/m/*", "/p/*", "/b/*"):
        assert f"{source}  /decide/  301\n" in rules, source
    assert "/landing/  /  301\n" in rules
    assert "/api" not in rules
