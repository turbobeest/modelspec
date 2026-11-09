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
    assert "https://modelspec.dev/api/index.json" not in text
    assert "No data download or local decision cache" in text
    assert "Three ways in:" in text
    assert "uvx --from modelspec-dev modelspec" in text
    assert "pipx install modelspec-dev" in text
    assert "pip install modelspec-dev" in text
    assert "delayed image" in text
    assert "https://modelspec.dev/api/rank/profiles.json" in text
    assert "Null means not researched." in text
    assert "Decision CLI" not in text
    assert "https://modelspec.dev/api/coverage.json" in text
    assert "modelspec decide --template <id>" not in text
    assert "¢" not in text


def test_llms_txt_carries_the_flag_derived_checkout_line() -> None:
    from pipeline import agent_copy

    assert agent_copy.key_procurement() in _text()


def test_llms_txt_offers_no_catalogue_download() -> None:
    text = _text()
    assert "https://modelspec.dev/api/catalogue.json" not in text
    assert "https://benchgraph.dev" not in text
    assert MCP_ENDPOINT in text
    assert API_DOCS in text


def test_the_site_build_writes_llms_txt_through_the_helper() -> None:
    source = (REPO_ROOT / "pipeline" / "build.py").read_text(encoding="utf-8")
    assert 'llms_txt(site="ModelSpec", base="https://modelspec.dev", build=build,' in source


def test_llms_txt_includes_the_generated_coverage_summary():
    from pipeline import coverage, landing
    data = landing.build_data(str(REPO_ROOT), date.today())
    text = llms_txt(site="ModelSpec", base="https://modelspec.dev",
                    build=Build(commit="test", built_at="2026-10-04", as_of=date.today()),
                    coverage=data.coverage)
    assert coverage.summary(data.coverage) in text
    assert coverage.provider_summary(data.coverage) in text


def test_llms_does_not_claim_measured_nine_month_age_without_lag_manifest(tmp_path, monkeypatch):
    from scripts.data_lag import LAG_MONTHS, read_manifest
    monkeypatch.chdir(tmp_path)
    assert read_manifest(tmp_path) is None
    text = llms_txt(
        site="ModelSpec", base="https://modelspec.test",
        build=Build("fixture", "2026-11-09T00:00:00Z", date(2026, 11, 9)),
    )
    assert "about nine months old" not in text
    assert "starts with a frozen image" in text
    assert "at least nine months earlier once enough history exists" in text
    assert "data-image.json records the provenance" in text
    assert LAG_MONTHS == 9
