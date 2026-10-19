"""Every reported redirect origin participates in retention decisions."""

import json
import sys
from types import ModuleType, SimpleNamespace

import httpx
import pytest

from decision.firecrawl import FirecrawlFetcher
from decision.sources import CopyStore, RenderedFetcher, fingerprint_bytes
from scripts.benchmarks import fetch


START = "https://example.test/start"
RESTRICTED = "https://x.ai/pricing"
PAGE = b"Synthetic restricted page bytes"


@pytest.mark.parametrize("metadata", [
    {"url": RESTRICTED},
    {"sourceURL": START, "url": RESTRICTED},
])
def test_hash_cache_does_not_replay_any_restricted_metadata_origin(tmp_path, monkeypatch, metadata):
    monkeypatch.setattr(fetch, "HASH_CACHE", tmp_path)
    monkeypatch.setattr(fetch, "resolve_key", lambda: None)
    fetch.hash_cache_path(START, ["markdown"]).write_text(json.dumps({
        "markdown": PAGE.decode(), "metadata": metadata,
    }))
    with pytest.raises(SystemExit, match="no Firecrawl key"):
        fetch.scrape(START)


def test_hash_cache_citation_marker_blocks_historical_body(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "HASH_CACHE", tmp_path)
    monkeypatch.setattr(fetch, "resolve_key", lambda: None)
    path = fetch.hash_cache_path(START, ["markdown"])
    path.write_text(json.dumps({"markdown": PAGE.decode(), "metadata": {"sourceURL": START}}))
    path.with_suffix(".citation.json").write_text(json.dumps({
        "url": START, "snapshot_ref": fingerprint_bytes(PAGE),
        "retrieved_at": "2026-10-19T12:00:00Z", "resolved_urls": [RESTRICTED],
    }))
    with pytest.raises(SystemExit, match="no Firecrawl key"):
        fetch.scrape(START)


def test_named_cache_checks_all_redirect_origins_before_writing(tmp_path):
    page = fetch.write_named_cache(START, PAGE.decode(), tmp_path, fetched_at="2026-10-19",
                                  extra_meta={"final_url": START, "resolved_urls": [RESTRICTED]})
    assert not page.path.exists()
    assert fetch.load_named_cache(START, tmp_path) is None


def test_firecrawl_preserves_both_reported_origin_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "synthetic-test-key")

    def respond(request):
        if request.method == "GET":
            return httpx.Response(200, json={"success": True, "data": {"remainingCredits": 200}})
        return httpx.Response(200, json={"success": True, "data": {
            "rawHtml": PAGE.decode(), "metadata": {
                "statusCode": 200, "sourceURL": "https://chatgpt.com/api-pricing/", "url": RESTRICTED,
            },
        }})

    renderer = FirecrawlFetcher(allowance=3, transport=httpx.MockTransport(respond))
    result = renderer.fetch("https://chatgpt.com/api-pricing/")
    assert result.outcome == "ok"
    store = CopyStore(tmp_path)
    ref = store.put(result.body, source_url="https://chatgpt.com/api-pricing/",
                    resolved_urls=result.resolved_urls)
    assert not store.path(ref).exists()


def test_rendered_fetch_preserves_intermediate_redirect_origin(tmp_path, monkeypatch):
    sync_api = ModuleType("playwright.sync_api")
    sync_api.Error = type("PageError", (Exception,), {})
    sync_api.TimeoutError = type("PageTimeout", (sync_api.Error,), {})
    monkeypatch.setitem(sys.modules, "playwright", ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    first = SimpleNamespace(url=START, redirected_from=None)
    middle = SimpleNamespace(url=RESTRICTED, redirected_from=first)
    last = SimpleNamespace(url="https://example.test/final", redirected_from=middle)
    response = SimpleNamespace(status=200, url=last.url, request=last)
    page = SimpleNamespace(url=last.url, goto=lambda *a, **kw: response,
                           wait_for_load_state=lambda *a, **kw: None,
                           content=lambda: PAGE.decode(), close=lambda: None)
    renderer = RenderedFetcher()
    renderer._context = SimpleNamespace(new_page=lambda: page)
    result = renderer.fetch(START)
    assert result.outcome == "ok"
    store = CopyStore(tmp_path)
    ref = store.put(result.body, source_url=START, resolved_urls=result.resolved_urls)
    assert not store.path(ref).exists()
