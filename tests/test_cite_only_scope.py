"""Cite-only assurance preserves ordinary comparison and scraping behavior."""

import json
import subprocess
from datetime import date

import pytest

from decision.model_comparison import collect_models
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from scripts import fetch_pricing
from scripts.benchmarks import fetch as benchmark_fetch
from tests.snapshot_records import SOURCES, fact, model
from tests.test_fetch import _FakeResp


@pytest.mark.parametrize("state", ["known", "not_disclosed", "requires_contract"])
def test_ordinary_comparison_preserves_known_only_provenance(state):
    record = fact("model", "lab/ordinary", "model.context_window", 128000, state=state)
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model("lab/ordinary", facts=[record])], sources=SOURCES,
    ), as_of=date(2026, 10, 19)))
    body = collect_models(["lab/ordinary"], index)
    shown = next(row for row in body["models"][0]["facts"]
                 if row["facet"] == "model.context_window")
    expected = {"facet": "model.context_window", "state": state,
                "value": 128000 if state == "known" else None, "unit": "tokens"}
    if state == "known":
        expected.update(record_id=record["id"], source_ids=["src-lab-docs"])
    assert shown == expected


def test_ordinary_pricing_scrape_uses_cli_without_python_credit_or_cache(tmp_path, monkeypatch):
    url = "https://pricing.example/prices"
    dest = tmp_path / "pages" / "prices.md"
    markdown = "# Exact pricing markdown\n\nUSD 1.25\n"
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        assert not dest.exists()
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps({
            "markdown": markdown, "metadata": {"sourceURL": url},
        }))

    def no_python_scrape(*args, **kwargs):
        pytest.fail("pricing must keep the existing CLI credentials and credit behavior")

    monkeypatch.setattr(fetch_pricing.subprocess, "run", run)
    monkeypatch.setattr(benchmark_fetch, "scrape", no_python_scrape)
    fetch_pricing.scrape_url(url, dest)
    assert calls == [([
        "firecrawl", "scrape", url, "--wait-for", "4000", "--only-main-content", "--json",
    ], {"check": True, "stdout": subprocess.PIPE, "text": True})]
    assert dest.read_text() == markdown
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")
                  if path.is_file()) == ["pages/prices.md"]


@pytest.mark.parametrize("metadata", [
    {"sourceURL": "https://x.ai/pricing"},
    {"sourceURL": "https://pricing.example/prices", "url": "https://docs.x.ai/models"},
    {"sourceURL": "https://pricing.example/prices",
     "resolved_urls": ["https://WWW.PERPLEXITY.AI.:8443/pro", "https://pricing.example/final"]},
])
def test_pricing_cli_redirect_is_refused_before_markdown_write(tmp_path, monkeypatch, metadata):
    payload = {"markdown": "PAGE SENTINEL MUST NOT REACH DISK", "metadata": metadata}
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        assert "-o" not in command
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload))

    def no_python_scrape(*args, **kwargs):
        pytest.fail("pricing must use one CLI request")

    monkeypatch.setattr(fetch_pricing.subprocess, "run", run)
    monkeypatch.setattr(benchmark_fetch, "scrape", no_python_scrape)
    with pytest.raises(ValueError, match="cite-only"):
        fetch_pricing.scrape_url("https://pricing.example/prices", tmp_path / "page.md")
    assert len(calls) == 1
    assert not list(tmp_path.iterdir())


def test_ordinary_benchmark_scrape_preserves_provider_failure_message(tmp_path, monkeypatch):
    payload = {"success": False, "error": "specific provider failure " + "x" * 400}
    monkeypatch.setattr(benchmark_fetch, "HASH_CACHE", tmp_path)
    monkeypatch.setattr(benchmark_fetch, "resolve_key", lambda: "synthetic-key")
    monkeypatch.setattr(benchmark_fetch, "remaining_credits", lambda _key: 100)
    monkeypatch.setattr(benchmark_fetch.urllib.request, "urlopen",
                        lambda *args, **kwargs: _FakeResp(payload))
    with pytest.raises(RuntimeError) as raised:
        benchmark_fetch.scrape("https://pricing.example/prices")
    assert str(raised.value) == str(payload)[:300]
