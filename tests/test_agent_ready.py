"""MODEL-94: agent-readiness of the built sites."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import agent_ready as ar  # noqa: E402
from pipeline import build as builder  # noqa: E402
from pipeline.export import Build  # noqa: E402
from pipeline.load import Benchmark, Catalogue, Model  # noqa: E402

BUILD = Build(commit="abc123def456", built_at="2026-09-18T00:00:00Z", as_of=date(2026, 9, 18))
CANONICAL = re.compile(r"""rel=["']canonical["']""", re.I)
REMOTE_RESOURCE = re.compile(
    r"""<(?:script|img|iframe)\b[^>]*\b(?:src)=["'](https?://[^"']+)["']"""
    r"""|<link\b[^>]*\bhref=["'](https?://[^"']+)["']""",
    re.I,
)
THIRD_PARTY_OK = (
    "https://modelspec.dev/",
    "https://benchgraph.dev/",
)


def _model(model_id: str, **front: object) -> Model:
    provider = model_id.split("/", 1)[0]
    data = {"display_name": model_id, "provider": provider, **front}
    return Model(model_id=model_id, path=ROOT / "models" / f"{model_id}.md",
                 front=data, body="")


def _bench(benchmark_id: str, **front: object) -> Benchmark:
    data = {"name": benchmark_id, **front}
    return Benchmark(benchmark_id=benchmark_id,
                     path=ROOT / "benchmarks" / f"{benchmark_id}.md",
                     front=data, body="")


def _tiny_png(width: int = 1, height: int = 1) -> bytes:
    import zlib
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"\x00" + b"\xff\x00\x00" * width
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


# ── unit ─────────────────────────────────────────────────────────────────────

def test_robots_txt_has_content_signals_and_keeps_allow_and_sitemap() -> None:
    text = ar.robots_txt("https://modelspec.dev")
    assert "https://contentsignals.org/" in text
    assert "Content-Signal: search=yes, ai-input=yes, ai-train=yes" in text
    assert "Allow: /" in text
    assert "Sitemap: https://modelspec.dev/sitemap.xml" in text
    assert "User-agent: *" in text


def test_png_to_ico_wraps_png_without_resampling() -> None:
    png = _tiny_png(64, 64)
    ico = ar.png_to_ico(png)
    assert ico[:4] == b"\x00\x00\x01\x00"
    assert png in ico
    count = struct.unpack_from("<H", ico, 4)[0]
    assert count == 1


def test_wants_markdown_ignores_star_and_html() -> None:
    assert ar.wants_markdown("text/markdown")
    assert ar.wants_markdown("text/markdown, text/html")
    assert ar.wants_markdown("text/markdown; q=0.9")
    assert not ar.wants_markdown("text/html")
    assert not ar.wants_markdown("*/*")
    assert not ar.wants_markdown("text/markdown; q=0")
    assert not ar.wants_markdown(None)


def test_markdown_asset_path_maps_pages_and_skips_api() -> None:
    assert ar.markdown_asset_path("/") == "/index.md"
    assert ar.markdown_asset_path("/m/openai/gpt-4o/") == "/m/openai/gpt-4o/index.md"
    assert ar.markdown_asset_path("/m/openai/gpt-4o") == "/m/openai/gpt-4o/index.md"
    assert ar.markdown_asset_path("/already.md") == "/already.md"
    assert ar.markdown_asset_path("/api/index.json") is None
    assert ar.markdown_asset_path("/fonts/archivo-latin.woff2") is None
    assert ar.markdown_asset_path("/.well-known/mcp.json") is None
    assert ar.markdown_asset_path("/../etc/passwd") is None


def test_model_markdown_keeps_nulls_and_provenance() -> None:
    model = _model(
        "openai/empty",
        display_name="Empty",
        model_type=None,
        licensing={"license_type": None, "commercial_use": "unspecified",
                   "open_weights": False},
        modalities={"text": {"context_window": None}},
        cost={"input": None, "output": None},
    )
    text = ar.model_markdown(model)
    assert "context: null" in text
    assert "pricing: null" in text
    assert "licence: null" in text
    assert "commercial_use: unspecified" in text
    assert "open_weights: false" in text
    assert "github.com/turbobeest/modelspec/blob/main/" in text
    assert "Null means not researched" in text


def test_model_jsonld_has_no_invented_rating() -> None:
    model = _model("acme/one", display_name="One", model_type="llm")
    data = ar.model_jsonld(model)
    assert data["@type"] == "SoftwareApplication"
    assert "aggregateRating" not in data
    assert "review" not in data
    dumped = json.dumps(data)
    assert "ratingValue" not in dumped


def test_api_catalog_lists_rank_policy_and_mcp() -> None:
    catalog = ar.api_catalog()
    anchors = {row["anchor"] for row in catalog["linkset"]}
    assert anchors == {ar.RANK_API, ar.POLICY_API, ar.MCP_ENDPOINT}
    for row in catalog["linkset"]:
        assert row["service-desc"][0]["href"] == ar.OPENAPI_URL
        assert row["service-doc"][0]["href"].startswith("https://github.com/turbobeest/modelspec")


def test_mcp_card_points_at_streamable_http_and_four_tools() -> None:
    card = ar.mcp_card()
    assert card["$schema"] == ar.MCP_SCHEMA
    assert re.fullmatch(ar.MCP_NAME_PATTERN, card["name"])
    assert len(card["description"]) <= ar.MCP_DESCRIPTION_MAX
    assert card["remotes"][0]["url"] == ar.MCP_ENDPOINT
    assert card["remotes"][0]["type"] == "streamable-http"
    assert [t["name"] for t in card["tools"]] == list(ar.MCP_TOOLS)


def test_skills_index_digest_matches_skill_bytes() -> None:
    text = ar.skill_markdown()
    raw = text.encode("utf-8")
    index = ar.skills_index(raw, "/.well-known/agent-skills/modelspec/SKILL.md",
                            ar.skill_description())
    assert index["$schema"] == ar.SKILLS_SCHEMA
    assert index["skills"][0]["digest"] == "sha256:" + hashlib.sha256(raw).hexdigest()
    assert "name: modelspec" in text
    assert "evidence_basis" in text
    assert "Null" in text
    assert ar.MCP_ENDPOINT in text


def test_auth_md_billing_copy_follows_the_flag() -> None:
    """Whether billing is live is `BILLING_ENABLED`'s to say, not the terms'.
    The adopted terms (MODEL-70) do not decide it; this copy follows the flag."""
    text = ar.auth_markdown(ROOT)
    if ar._flag_off(ar.wrangler_vars(ROOT).get("BILLING_ENABLED")):
        assert "Billing is not live" in text
    else:
        assert "Billing is enabled" in text
        assert "Billing is not live" not in text
    assert "test_" in text
    assert "No key is required" in text
    assert ar.RANK_API.split("/v1")[0] in text or "api.modelspec.dev" in text


def test_llms_full_states_cap_and_stays_under_it() -> None:
    models = [_model(f"p/m{i}", display_name=f"M{i}", model_type="llm") for i in range(50)]
    text, stats = ar.llms_full_models(models, cap=2_000)
    assert stats["bytes"] <= 2_000
    assert stats["bytes"] == len(text.encode("utf-8"))
    assert "# cap_bytes: 2000" in text
    match = re.search(r"# bytes: (\d+)", text)
    assert match is not None
    assert int(match.group(1)) == stats["bytes"]
    assert stats["omitted"] > 0
    assert "truncated" in text


def test_middleware_and_worker_share_the_accept_rule() -> None:
    functions = ROOT / "site" / "functions"
    mid = (functions / "_middleware.js").read_text(encoding="utf-8")
    worker = (functions / "_worker.js").read_text(encoding="utf-8")
    for src in (mid, worker):
        assert "text/markdown" in src
        assert "index.md" in src
        assert "ASSETS.fetch" in src
        assert "env.ASSETS" in src


# ── built trees ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    assert builder.main(["--out", str(out), "--root", str(ROOT)]) == 0
    return out


def test_built_robots_on_both_sites(dist: Path) -> None:
    for site, base in (("modelspec", "https://modelspec.dev"),
                       ("benchgraph", "https://benchgraph.dev")):
        text = (dist / site / "robots.txt").read_text(encoding="utf-8")
        assert "Content-Signal: search=yes, ai-input=yes, ai-train=yes" in text
        assert "Allow: /" in text
        assert f"Sitemap: {base}/sitemap.xml" in text
        assert "contentsignals.org" in text


def test_built_favicon_ico_on_both_sites(dist: Path) -> None:
    for site in ("modelspec", "benchgraph"):
        ico = (dist / site / "favicon.ico").read_bytes()
        png = (dist / site / "favicon-64.png").read_bytes()
        assert ico[:4] == b"\x00\x00\x01\x00"
        assert png in ico


def test_built_markdown_twins_and_alternate_links(dist: Path) -> None:
    ms = dist / "modelspec"
    bg = dist / "benchgraph"
    assert (ms / "index.md").is_file()
    assert (bg / "index.md").is_file()
    assert 'rel="alternate" type="text/markdown" href="/index.md"' in (ms / "index.html").read_text(encoding="utf-8")
    assert 'rel="alternate" type="text/markdown" href="/index.md"' in (bg / "index.html").read_text(encoding="utf-8")

    models = sorted((ms / "m").glob("*/*/index.html"))[:8]
    assert models
    for html_path in models:
        md_path = html_path.with_name("index.md")
        assert md_path.is_file(), html_path
        html = html_path.read_text(encoding="utf-8")
        rel = "/" + html_path.parent.relative_to(ms).as_posix() + "/index.md"
        assert f'rel="alternate" type="text/markdown" href="{rel}"' in html
        assert "Null means not researched" in md_path.read_text(encoding="utf-8")

    providers = sorted((ms / "p").glob("*/index.html"))[:5]
    assert providers
    for html_path in providers:
        assert html_path.with_name("index.md").is_file()

    benches = sorted((bg / "b").glob("*/index.html"))[:8]
    assert benches
    for html_path in benches:
        md_path = html_path.with_name("index.md")
        assert md_path.is_file()
        html = html_path.read_text(encoding="utf-8")
        rel = "/" + html_path.parent.relative_to(bg).as_posix() + "/index.md"
        assert f'rel="alternate" type="text/markdown" href="{rel}"' in html


def test_built_api_catalog_rfc9727(dist: Path) -> None:
    path = dist / "modelspec" / ".well-known" / "api-catalog"
    assert path.is_file()
    catalog = json.loads(path.read_text(encoding="utf-8"))
    anchors = {row["anchor"] for row in catalog["linkset"]}
    assert ar.RANK_API in anchors
    assert ar.POLICY_API in anchors
    assert ar.MCP_ENDPOINT in anchors
    headers = (dist / "modelspec" / "_headers").read_text(encoding="utf-8")
    assert "application/linkset+json" in headers
    assert ar.RFC_9727_PROFILE in headers
    assert 'rel="api-catalog"' in headers
    assert (dist / "benchgraph" / ".well-known" / "api-catalog").exists() is False


def test_built_link_headers(dist: Path) -> None:
    ms = (dist / "modelspec" / "_headers").read_text(encoding="utf-8")
    bg = (dist / "benchgraph" / "_headers").read_text(encoding="utf-8")
    assert 'rel="describedby"' in ms and "</llms.txt>" in ms
    assert 'rel="sitemap"' in ms and "</sitemap.xml>" in ms
    assert 'rel="service-desc"' in ms and "</openapi.yaml>" in ms
    assert 'rel="describedby"' in bg
    assert 'rel="api-catalog"' not in bg


def test_built_auth_mcp_and_skills_are_modelspec_only(dist: Path) -> None:
    ms = dist / "modelspec"
    bg = dist / "benchgraph"
    auth = (ms / "auth.md").read_text(encoding="utf-8")
    assert "Billing is enabled" in auth
    assert "Billing is not live" not in auth
    assert "test_" in auth
    card = json.loads((ms / ".well-known" / "mcp.json").read_text(encoding="utf-8"))
    assert card["remotes"][0]["url"] == ar.MCP_ENDPOINT
    assert {t["name"] for t in card["tools"]} == set(ar.MCP_TOOLS)
    assert len(card["description"]) <= ar.MCP_DESCRIPTION_MAX
    assert re.fullmatch(ar.MCP_NAME_PATTERN, card["name"])
    index = json.loads((ms / ".well-known" / "agent-skills" / "index.json").read_text(encoding="utf-8"))
    skill = (ms / ".well-known" / "agent-skills" / "modelspec" / "SKILL.md").read_bytes()
    assert index["skills"][0]["digest"] == "sha256:" + hashlib.sha256(skill).hexdigest()
    assert (bg / "auth.md").exists() is False
    assert (bg / ".well-known" / "mcp.json").exists() is False
    assert (bg / ".well-known" / "agent-skills").exists() is False


def test_built_jsonld_dataset_and_per_page(dist: Path) -> None:
    ms_html = (dist / "modelspec" / "index.html").read_text(encoding="utf-8")
    bg_html = (dist / "benchgraph" / "index.html").read_text(encoding="utf-8")
    assert '"@type": "Dataset"' in ms_html
    assert '"@type": "WebAPI"' in ms_html
    assert ar.RANK_API in ms_html
    assert ar.MCP_ENDPOINT in ms_html
    assert '"@type": "Dataset"' in bg_html
    assert "aggregateRating" not in ms_html
    model_html = next((dist / "modelspec" / "m").glob("*/*/index.html")).read_text(encoding="utf-8")
    assert '"@type": "SoftwareApplication"' in model_html
    assert "aggregateRating" not in model_html
    bench_html = next((dist / "benchgraph" / "b").glob("*/index.html")).read_text(encoding="utf-8")
    assert '"@type": "Dataset"' in bench_html


def test_built_llms_full_under_cap(dist: Path) -> None:
    for site in ("modelspec", "benchgraph"):
        path = dist / site / "llms-full.txt"
        data = path.read_bytes()
        text = data.decode("utf-8")
        assert len(data) <= ar.LLMS_FULL_CAP
        assert f"# cap_bytes: {ar.LLMS_FULL_CAP}" in text
        match = re.search(r"# bytes: (\d+)", text)
        assert match is not None
        assert int(match.group(1)) == len(data)
        assert "## " in text


def test_built_openapi_and_functions_uploaded_alongside(dist: Path) -> None:
    assert (dist / "modelspec" / "openapi.yaml").is_file()
    spec = (dist / "modelspec" / "openapi.yaml").read_text(encoding="utf-8")
    assert "\nopenapi:" in spec or spec.startswith("openapi:")
    for site in ("modelspec", "benchgraph"):
        assert (dist / site / "functions" / "_middleware.js").is_file()
        assert (dist / site / "_worker.js").is_file()
        worker = (dist / site / "_worker.js").read_text(encoding="utf-8")
        assert "text/markdown" in worker
        routes = json.loads((dist / site / "_routes.json").read_text(encoding="utf-8"))
        assert routes["version"] == 1
        assert "/api/*" in routes["exclude"]


def test_built_file_count_under_pages_limit(dist: Path) -> None:
    for site in ("modelspec", "benchgraph"):
        count = sum(1 for path in (dist / site).rglob("*") if path.is_file())
        assert count < ar.PAGES_FILE_LIMIT, f"{site} has {count} files"


def test_built_404_still_has_no_canonical(dist: Path) -> None:
    for site in ("modelspec", "benchgraph"):
        html = (dist / site / "404.html").read_text(encoding="utf-8")
        assert CANONICAL.search(html) is None
        assert "noindex" in html


def test_built_pages_make_no_new_third_party_requests(dist: Path) -> None:
    hits: list[str] = []
    for html_path in dist.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8", errors="replace")
        for match in REMOTE_RESOURCE.finditer(text):
            url = match.group(1) or match.group(2)
            if url.startswith(THIRD_PARTY_OK):
                continue
            if "schema.org" in url:
                continue
            hits.append(f"{html_path.relative_to(dist)}: {url}")
    assert hits == []



def test_auth_md_opens_with_the_auth_md_heading(tmp_path):
    """Agent Readiness looks for an `Auth.md` heading; without it the check
    reports the file as present but malformed."""
    from pipeline.agent_ready import auth_markdown
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert auth_markdown(root).splitlines()[0] == "# Auth.md"
