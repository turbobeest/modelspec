"""Offline source-admission checks at workflow transport boundaries."""

import io
import json
import socket
import urllib.request
import urllib.response
from email.message import Message
from contextlib import nullcontext

import httpx
import pytest

from decision.sources import Fetcher
from scripts import process_release_signals as release
from scripts.benchmarks import fetch as fc
from scripts.curation import watch

HOSTS = ("artificial" + "analysis.ai", "za" + "pier.com")
START = "https://example.test/start"
END = "https://example.test/end"
BODY = "SourceFixture458"
offline_reader = fc.remaining_credits


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    def refuse(*args, **kwargs):
        raise AssertionError("live network disabled")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(fc, "HASH_CACHE", tmp_path / "hash")
    monkeypatch.setattr(fc, "resolve_key", lambda: "fixture-key")
    monkeypatch.setattr(fc, "remaining_credits", lambda _: 100)


def urllib_transport(monkeypatch, hops, calls):
    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append(request.full_url)
            index = hops.index(request.full_url)
            headers = Message()
            if index + 1 < len(hops):
                headers["Location"] = hops[index + 1]
                code, body = 302, b""
            else:
                code, body = 200, BODY.encode()
            response = urllib.response.addinfourl(io.BytesIO(body), headers, request.full_url, code)
            response.msg = "OK" if code == 200 else "Found"
            return response
    build = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "build_opener", lambda *handlers: build(*handlers, Transport()))


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
@pytest.mark.parametrize("redirect", [False, True], ids=["direct", "redirect"])
def test_shared_transport_enforces_source_admission(host, redirect):
    refused = str(httpx.URL(f"https://docs.{host.upper()}.:443/page"))
    hops = [START, refused, END] if redirect else [refused]
    calls = []
    def serve(request):
        calls.append(str(request.url))
        index = hops.index(str(request.url))
        return (httpx.Response(302, headers={"location": hops[index + 1]})
                if index + 1 < len(hops) else httpx.Response(200, text=BODY))
    with httpx.Client(transport=httpx.MockTransport(serve)) as client:
        result = Fetcher(client, retries=0, min_host_interval=0).fetch(hops[0])
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert calls == ([START] if redirect else [])


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
@pytest.mark.parametrize("mode", ["direct", "redirect", "cached"])
def test_curation_enforces_source_admission(tmp_path, monkeypatch, host, mode):
    refused = f"https://{host}/page"
    url = refused if mode == "direct" else START
    hops = [START, refused, END] if mode == "redirect" else [url]
    calls = []
    urllib_transport(monkeypatch, hops, calls)
    bench = tmp_path / "bench"
    bench.mkdir()
    (bench / "probe.md").write_text(f"---\nstatus: active\nsources:\n- url: {url}\n---\nfixture\n")
    state = tmp_path / "state"
    if mode == "cached":
        state.mkdir()
        (state / f"{watch.state_key(url)}.json").write_text(json.dumps({
            "url": url, "resolved_urls": [refused], "hash": "old"}))
        (state / f"{watch.state_key(url)}.txt").write_text(BODY)
        assert watch.load_state(state, url)[1] == ""
    paid = watch.FirecrawlBudget(cap=1, allow={watch.host_of(url)})
    def no_paid(*args, **kwargs):
        pytest.fail("refused source must not reach paid transport")
    monkeypatch.setattr(fc, "scrape", no_paid)
    report = watch.watch(["probe"], state, bench_dir=bench,
                         fetcher=lambda source: watch.http_fetch(source, retries=0),
                         firecrawl=paid, js_hosts={watch.host_of(url)}, max_workers=1)
    assert report["baselined"] == 0
    assert report["changes"] == []
    assert len(report["failures"]) == 1
    assert report["failures"][0]["kinds"] == []
    assert paid.calls == 0
    assert calls == ([START] if mode == "redirect" else [])
    if mode != "cached":
        assert not list(state.glob("*.txt"))


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
@pytest.mark.parametrize("mode", ["http", "redirect", "paid", "hash", "named", "metadata", "citation", "orphan_named"])
def test_benchmark_transport_enforces_source_admission(tmp_path, monkeypatch, host, mode):
    refused = f"https://{host}/page"
    calls = []
    raw = tmp_path / "raw"
    if mode in {"http", "redirect"}:
        hops = [START, refused, END] if mode == "redirect" else [refused]
        urllib_transport(monkeypatch, hops, calls)
        with pytest.raises(ValueError, match="excluded"):
            fc.load_or_get(hops[0], raw, fetch=True)
        assert calls == ([START] if mode == "redirect" else [])
    else:
        url = START if mode in {"metadata", "citation", "orphan_named"} else refused
        if mode in {"hash", "metadata"}:
            fc.HASH_CACHE.mkdir()
            fc.hash_cache_path(url, ["markdown"], max_pages=1).write_text(json.dumps({
                "markdown": BODY, "metadata": {"sourceURL": refused}}))
        if mode == "citation":
            fc.HASH_CACHE.mkdir()
            fc.hash_cache_path(url, ["markdown"], max_pages=1).with_suffix(".citation.json").write_text(
                json.dumps({"url": url, "resolved_urls": [refused]}))
        if mode == "orphan_named":
            raw.mkdir()
            _, meta = fc.named_paths(url, raw)
            meta.write_text(json.dumps({"url": url, "resolved_urls": [refused]}))
        if mode == "named":
            raw.mkdir()
            path, meta = fc.named_paths(url, raw)
            path.write_text(BODY)
            meta.write_text(json.dumps({"url": refused}))
            assert fc.load_named_cache(url, raw) is None
        def paid(req, **kwargs):
            calls.append(req)
            return io.BytesIO(json.dumps({"success": True, "data": {"markdown": BODY}}).encode())
        monkeypatch.setattr(fc, "open_source_request", paid)
        with pytest.raises(ValueError, match="excluded"):
            fc.scrape(url, guard=fc.CreditGuard("fixture", 1), max_pages=1, named_cache_dir=raw)
        assert calls == []
    if mode not in {"hash", "named", "metadata", "citation", "orphan_named"}:
        assert not list(tmp_path.rglob("*.json"))
        assert not list(tmp_path.rglob("*.md"))


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
@pytest.mark.parametrize("redirect", [False, True], ids=["direct", "redirect"])
def test_release_transport_enforces_source_admission(monkeypatch, host, redirect):
    refused = f"https://{host}/page"
    hops = [START, refused, END] if redirect else [refused]
    calls = []
    def serve(request):
        calls.append(str(request.url))
        index = hops.index(str(request.url))
        return (httpx.Response(302, headers={"location": hops[index + 1]})
                if index + 1 < len(hops) else httpx.Response(200, text=BODY))
    with httpx.Client(transport=httpx.MockTransport(serve)) as client:
        monkeypatch.setattr(release.httpx, "Client", lambda: nullcontext(client))
        with pytest.raises(ValueError, match="excluded"):
            release._fetch(hops[0])
    assert calls == ([START] if redirect else [])


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
def test_paid_endpoint_enforces_source_admission(tmp_path, monkeypatch, host):
    refused = f"https://{host}/page"
    calls = []
    urllib_transport(monkeypatch, [fc.SCRAPE_URL, refused], calls)
    monkeypatch.setattr(urllib.request, "urlopen", urllib.request.build_opener().open)
    with pytest.raises(ValueError, match="excluded"):
        fc.scrape(START, guard=fc.CreditGuard("fixture", 1), max_pages=1)
    assert calls == [fc.SCRAPE_URL]
    assert not list(tmp_path.rglob("*.json"))


def test_allowed_redirects_preserve_response_and_origins(monkeypatch, tmp_path):
    hops, calls = [START, END], []
    urllib_transport(monkeypatch, hops, calls)
    result = watch.http_fetch(START, retries=0)
    assert result.ok and result.text == BODY
    assert result.resolved_urls == tuple(hops)
    calls.clear()
    page = fc.load_or_get(START, tmp_path / "raw", fetch=True)
    assert page.text == BODY
    assert calls == hops
    def serve(request):
        return (httpx.Response(302, headers={"location": "/end"})
                if str(request.url) == START else httpx.Response(200, text=BODY))
    with httpx.Client(transport=httpx.MockTransport(serve)) as client:
        result = Fetcher(client, retries=0, min_host_interval=0).fetch(START)
        assert result.outcome == "ok" and result.body == BODY.encode()
        assert result.resolved_urls == tuple(hops)
        monkeypatch.setattr(release.httpx, "Client", lambda: nullcontext(client))
        result = release._fetch(START)
        assert result.url == END and result.body == BODY.encode()


def test_source_redirect_preserves_httpx_credential_handling():
    seen = []
    def serve(request):
        seen.append(request.headers.get("authorization"))
        return (httpx.Response(302, headers={"location": "https://other.test/end"})
                if str(request.url) == START else httpx.Response(200, text=BODY))
    with httpx.Client(auth=("fixture", "secret"), transport=httpx.MockTransport(serve)) as client:
        result = Fetcher(client, retries=0, min_host_interval=0).fetch(START)
    assert result.outcome == "ok"
    assert len(seen) == 2 and seen[0] is not None and seen[1] is None


@pytest.mark.parametrize("host", HOSTS, ids=["family-one", "family-two"])
def test_usage_endpoint_enforces_source_admission(monkeypatch, host):
    calls = []
    urllib_transport(monkeypatch, [fc.CREDIT_USAGE_URL, f"https://{host}/page"], calls)
    # Exercise the real account reader independently of the fixture's balance fake.
    with pytest.raises(ValueError, match="excluded"):
        offline_reader("fixture")
    assert calls == [fc.CREDIT_USAGE_URL]
