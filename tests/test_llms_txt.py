"""llms.txt names the MCP endpoint and the API docs (MODEL-3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pipeline.build import API_DOCS, MCP_ENDPOINT, RANK_API, llms_txt
from pipeline.export import Build

REPO_ROOT = Path(__file__).resolve().parent.parent


def _text() -> str:
    return llms_txt(
        site="ModelSpec",
        base="https://modelspec.dev",
        build=Build(commit="abcdef1234567890", built_at="2026-09-18T00:00:00+00:00",
                    as_of=date(2026, 9, 18)),
    )


def test_llms_txt_names_the_mcp_endpoint_and_api_docs() -> None:
    text = _text()
    assert MCP_ENDPOINT in text
    assert API_DOCS in text
    assert RANK_API in text
    assert "https://modelspec.dev/api/index.json" in text
    assert "Null means not researched." in text


def test_benchgraph_llms_txt_uses_its_own_index_but_the_same_mcp() -> None:
    text = llms_txt(
        site="benchgraph",
        base="https://benchgraph.dev",
        build=Build(commit="abcdef1234567890", built_at="2026-09-18T00:00:00+00:00",
                    as_of=date(2026, 9, 18)),
    )
    assert "https://benchgraph.dev/api/index.json" in text
    assert MCP_ENDPOINT in text
    assert API_DOCS in text


def test_the_site_build_writes_llms_txt_through_the_helper() -> None:
    source = (REPO_ROOT / "pipeline" / "build.py").read_text(encoding="utf-8")
    assert "llms_txt(site=site, base=base, build=build)" in source
