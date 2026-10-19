"""Content writers found by the round-two repository audit."""

import io
import json
import os
import subprocess
import sys
import urllib.request
import urllib.response
from email.message import Message
from types import SimpleNamespace

import httpx
import pytest

from scripts.benchmarks import census
from scripts.policy import audit_provider_defaults, distribution_licence
from decision.retention import open_retained_source


SENTINEL = "ROUND2_SOURCE_TEXT_MUST_NOT_REACH_DISK"


class Response(io.BytesIO):
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url

    def geturl(self):
        return self.url


def stub_response(monkeypatch, response):
    def open_response(*args, **kwargs):
        return response

    monkeypatch.setattr(urllib.request, "urlopen", open_response)
    monkeypatch.setattr(urllib.request, "build_opener", lambda *handlers: SimpleNamespace(open=open_response))


@pytest.fixture
def redirected_source(monkeypatch):
    calls = []

    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append(request.full_url)
            headers = Message()
            if request.full_url == "https://huggingface.co/api/models/lab/model":
                code, body = 200, json.dumps({"siblings": [{"rfilename": "LICENSE"}]}).encode()
            elif request.full_url == "https://x.ai/license":
                code, body = 302, b""
                headers["Location"] = "https://example.test/final"
            elif request.full_url == "https://example.test/final":
                code, body = 200, json.dumps({"excerpt": SENTINEL}).encode()
            elif request.full_url == "https://example.test/ordinary":
                code, body = 302, b""
                headers["Location"] = "https://example.test/final"
            else:
                code, body = 302, b""
                headers["Location"] = "https://x.ai/license"
            response = urllib.response.addinfourl(io.BytesIO(body), headers, request.full_url, code)
            response.msg = "OK" if code == 200 else "Found"
            return response

    build_opener = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "urlopen", build_opener(Transport()).open)
    monkeypatch.setattr(urllib.request, "build_opener",
                        lambda *handlers: build_opener(*handlers, Transport()))
    return calls


@pytest.mark.parametrize("final", ["https://x.ai/license", "https://DOCS.X.AI.:8443/license"])
def test_licence_download_refuses_cite_only_redirect_before_document_write(tmp_path, monkeypatch, final):
    monkeypatch.setattr(distribution_licence, "get_json", lambda url: {
        "siblings": [{"rfilename": "LICENSE"}], "cardData": {"license": "other"},
    })
    response = Response(SENTINEL.encode(), final)
    stub_response(monkeypatch, response)
    row = distribution_licence.inspect("lab/model", tmp_path)
    assert row["licence_files"][0]["error"] is not None
    assert SENTINEL not in json.dumps(row)
    assert not list(tmp_path.iterdir())
    assert response.closed


def test_ordinary_licence_download_keeps_document_and_result(tmp_path, monkeypatch):
    monkeypatch.setattr(distribution_licence, "get_json", lambda url: {
        "siblings": [{"rfilename": "LICENSE"}], "cardData": {"license": "other"},
    })
    stub_response(monkeypatch, Response(
        SENTINEL.encode(), "https://huggingface.co/lab/model/resolve/main/LICENSE"))
    row = distribution_licence.inspect("lab/model", tmp_path)
    assert row["licence_files"][0]["head"] == SENTINEL
    assert (tmp_path / "lab__model__LICENSE").read_text() == SENTINEL


@pytest.mark.parametrize("cached", [False, True])
def test_census_search_retains_citation_without_restricted_snippets(tmp_path, monkeypatch, cached):
    import hashlib

    monkeypatch.setattr(census, "CENSUS", tmp_path)
    monkeypatch.setattr(census, "resolve_key", lambda: "synthetic-test-key")
    restricted = {"url": "https://www.perplexity.ai/research", "title": SENTINEL,
                  "description": SENTINEL, "markdown": SENTINEL}
    ordinary = {"url": "https://example.test/benchmark", "title": "Ordinary benchmark",
                "description": "An ordinary search excerpt"}
    payload = [restricted, ordinary]
    if cached:
        cache = tmp_path / "cache"
        cache.mkdir()
        key = hashlib.sha256(b"benchmarks|10").hexdigest()[:24]
        (cache / f"search_{key}.json").write_text(json.dumps(payload))
    monkeypatch.setattr(census.urllib.request, "urlopen", lambda *a, **k: Response(
        json.dumps({"data": {"web": payload}}).encode(), "https://api.firecrawl.dev/v2/search"))
    results = census.firecrawl_search("benchmarks", 10)
    assert results[1] == ordinary
    assert results[0]["url"] == restricted["url"]
    assert len(results[0]["snapshot_ref"]) == 64
    if cached:
        assert results[0]["retrieved_at"] is None
    else:
        assert results[0]["retrieved_at"]
    assert SENTINEL not in json.dumps(results)
    assert all(SENTINEL.encode() not in p.read_bytes() for p in tmp_path.rglob("*") if p.is_file())
    assert census.firecrawl_search("benchmarks", 10) == results


def test_census_aggregator_does_not_write_leads_from_cite_only_redirect(monkeypatch):
    monkeypatch.setattr(census, "SOURCES", {
        "scrape_allow": ["example.test"], "aggregator_pages": ["https://example.test/boards"],
    })
    monkeypatch.setattr(census, "leads", [])
    monkeypatch.setattr(census, "scrape", lambda *a, **k: {
        "markdown": f"NewEval {SENTINEL}", "metadata": {"url": "https://x.ai/research"},
    })
    monkeypatch.setattr(census.time, "sleep", lambda _: None)
    census.src_aggregators()
    assert census.leads == []


def test_census_registry_refuses_cite_only_redirect_before_extracting_text(monkeypatch):
    stub_response(monkeypatch, Response(SENTINEL.encode(), "https://x.ai/research"))
    with pytest.raises(ValueError, match="cite-only"):
        census.get("https://example.test/registry")


def test_census_refuses_restricted_intermediate_before_following_redirect(redirected_source):
    with pytest.raises(ValueError, match="cite-only"):
        census.get("https://example.test/start")
    assert redirected_source == ["https://example.test/start"]


def test_licence_never_writes_restricted_intermediate_redirect(tmp_path, redirected_source):
    row = distribution_licence.inspect("lab/model", tmp_path)
    assert SENTINEL not in json.dumps(row)
    assert row["licence_files"][0]["error"] is not None
    assert not list(tmp_path.iterdir())
    assert redirected_source == ["https://huggingface.co/api/models/lab/model",
                                 "https://huggingface.co/lab/model/resolve/main/LICENSE"]


def test_licence_json_refuses_restricted_intermediate_before_reading(redirected_source):
    with pytest.raises(ValueError, match="cite-only"):
        distribution_licence.get_json("https://example.test/start")
    assert redirected_source == ["https://example.test/start"]


def test_retained_source_refuses_direct_host_without_opening(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("a direct cite-only source must not be opened")

    monkeypatch.setattr(urllib.request, "build_opener", unexpected)
    with pytest.raises(ValueError, match="cite-only"):
        open_retained_source("https://DOCS.X.AI.:8443/license", timeout=12)


def test_retained_source_opens_ordinary_request_once_with_its_options(monkeypatch):
    response = Response(SENTINEL.encode(), "https://example.test/license")
    calls = []

    def open_response(request, *, timeout):
        calls.append((request, timeout))
        return response

    monkeypatch.setattr(urllib.request, "build_opener", lambda *handlers: SimpleNamespace(open=open_response))
    request = urllib.request.Request("https://example.test/license", data=b"ordinary request",
                                     headers={"User-Agent": "test-reader"}, method="POST")
    with open_retained_source(request, timeout=12) as result:
        assert result.read() == SENTINEL.encode()
    assert calls == [(request, 12)]
    assert calls[0][0].data == b"ordinary request"
    assert calls[0][0].get_header("User-agent") == "test-reader"
    assert response.closed


def test_retained_source_preserves_ordinary_redirects(redirected_source):
    with open_retained_source("https://example.test/ordinary", timeout=12) as response:
        assert json.load(response) == {"excerpt": SENTINEL}
    assert redirected_source == ["https://example.test/ordinary", "https://example.test/final"]


def test_licence_standalone_cli_works_without_pythonpath_or_source_requests(tmp_path):
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    output = tmp_path / "licences"
    completed = subprocess.run([sys.executable, str(distribution_licence.__file__), str(output)],
                               input="", text=True, capture_output=True, cwd=tmp_path, env=env,
                               timeout=20, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads((output / "_results.json").read_text()) == []
    assert "0 repositories" in completed.stdout


@pytest.mark.parametrize("redirect", [False, True])
def test_provider_licence_audit_does_not_derive_notes_from_cite_only_documents(redirect):
    link = "https://example.test/licence" if redirect else "https://docs.x.ai/licence"

    def reply(request):
        if request.url.path == "/api/models/lab/model":
            return httpx.Response(200, json={"cardData": {"license_link": link}})
        if str(request.url) == link and redirect:
            return httpx.Response(302, headers={"location": "https://docs.x.ai/licence"})
        if request.url.host == "docs.x.ai":
            return httpx.Response(200, text=SENTINEL)
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(reply), follow_redirects=True) as client:
        result = audit_provider_defaults.fetch_hf(client, "lab/model")
    assert "license_file_text" not in result
    assert SENTINEL not in json.dumps(result)


def test_provider_licence_audit_preserves_ordinary_document():
    def reply(request):
        if request.url.path == "/api/models/lab/model":
            return httpx.Response(200, json={"cardData": {"license_link": "https://example.test/licence"}})
        if request.url.host == "example.test":
            return httpx.Response(200, text=SENTINEL)
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(reply)) as client:
        result = audit_provider_defaults.fetch_hf(client, "lab/model")
    assert result["license_file_text"] == SENTINEL
