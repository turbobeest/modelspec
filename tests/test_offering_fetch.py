"""Offering fetch stages retain only permitted sources and bound paid requests."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import httpx
import pytest

from decision.firecrawl import FirecrawlFetcher
from decision.model import Source
from decision.sources import FetchResult, fingerprint_bytes

URL = "https://ai.google.dev/gemini-api/docs/pricing"
BODY = b"<html><body>fixture price text</body></html>"
MONTH = datetime.now(UTC).strftime("%Y-%m")
TERMS = {"ai.google.dev": "restricts", "docs.x.ai": "forbids"}


class Reader:
    def __init__(self, result=None):
        self.result = result or FetchResult("unreachable", 403)
        self.calls = []

    def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.result


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / "credits.json"
    path.write_text(json.dumps({"schema_version": 1, "months": {MONTH: 0}}))
    return path


@pytest.fixture
def paid_factory(monkeypatch):
    from decision import firecrawl

    monkeypatch.setattr(firecrawl, "FIRECRAWL_HOSTS", frozenset({"ai.google.dev"}))
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-offering-fixture")

    def make(handler=None):
        calls = []

        def serve(request):
            if request.url.path == "/v2/team/credit-usage":
                return httpx.Response(200, json={
                    "success": True, "data": {"remainingCredits": 1000},
                })
            calls.append(request)
            if handler:
                return handler(request)
            return httpx.Response(200, json={
                "success": True,
                "data": {"rawHtml": BODY.decode(), "metadata": {"statusCode": 200}},
            })

        def factory(*, allowance):
            return FirecrawlFetcher(allowance=allowance, transport=httpx.MockTransport(serve))

        return factory, calls

    return make


def offering_fetcher(**kwargs):
    from scripts.offering_fetch import OfferingFetcher

    return OfferingFetcher(kwargs.pop("primary", Reader()), lab=kwargs.pop("lab", "google"),
                           terms=TERMS, renderer=kwargs.pop("renderer", Reader()), **kwargs)


def stages(fetcher, url=URL):
    fetcher.fetch(url)
    fetcher.render(url)
    return fetcher.fallback(url)


def test_paid_fallback_requires_both_earlier_stages(ledger, paid_factory):
    factory, calls = paid_factory()
    fetcher = offering_fetcher(ledger=ledger, firecrawl_factory=factory)
    assert fetcher.fallback(URL).outcome == "unreachable"
    fetcher.fetch(URL)
    assert fetcher.fallback(URL).outcome == "unreachable"
    fetcher.render(URL)
    assert fetcher.fallback(URL).outcome == "ok"
    assert len(calls) == 1


def test_primary_and_render_do_not_enable_paid_requests(ledger, paid_factory):
    factory, calls = paid_factory()
    fetcher = offering_fetcher(primary=Reader(FetchResult("ok", 200, body=BODY)),
                              ledger=ledger, firecrawl_factory=factory)
    assert fetcher.fetch(URL).body == BODY
    assert fetcher.render(URL).outcome == "unreachable"
    assert calls == []
    assert fetcher.credits_spent == 0


def test_renderer_receives_registered_recipe():
    source = Source.model_validate({
        "id": "fixture-pricing", "url": URL, "kind": "provider_documentation",
        "normaliser": "html-default",
        "cited_regions": [{"id": "price", "locator": {"kind": "css", "value": "#price"}}],
    })
    renderer = Reader(FetchResult("ok", 200, body=BODY))
    fetcher = offering_fetcher(renderer=renderer, sources={source.id: source})
    fetcher.fetch(URL)
    assert fetcher.render(URL).body == BODY
    assert len(renderer.calls) == 1
    assert renderer.calls[0][1]["prepare"].selectors == ("#price",)


def test_per_run_limit_stops_at_five_requests(ledger, paid_factory):
    factory, calls = paid_factory()
    fetcher = offering_fetcher(ledger=ledger, firecrawl_factory=factory)
    outcomes = [stages(fetcher, f"{URL}?model={n}").outcome for n in range(6)]
    assert outcomes == ["ok"] * 5 + ["unreachable"]
    assert len(calls) == fetcher.credits_spent == 5
    assert json.loads(ledger.read_text())["months"][MONTH] == 5


def test_monthly_limit_survives_new_fetcher_instances(ledger, paid_factory):
    ledger.write_text(json.dumps({"schema_version": 1, "months": {MONTH: 98}}))
    factory, calls = paid_factory()
    outcomes = [stages(offering_fetcher(ledger=ledger, firecrawl_factory=factory)).outcome
                for _ in range(3)]
    assert outcomes == ["ok", "ok", "unreachable"]
    assert len(calls) == 2
    assert json.loads(ledger.read_text())["months"][MONTH] == 100


@pytest.mark.parametrize("contents", [None, "not json", "{}", "[]",
                                     '{"schema_version":1,"months":null}',
                                     '{"schema_version":1,"months":{}}',
                                     '{"schema_version":1,"months":{"2026-99":1}}'])
def test_missing_or_invalid_ledger_fails_closed(tmp_path, paid_factory, contents):
    path = tmp_path / "ledger.json"
    if contents is not None:
        path.write_text(contents)
    factory, calls = paid_factory()
    result = stages(offering_fetcher(ledger=path, firecrawl_factory=factory))
    assert result.outcome == "unreachable" and "ledger" in result.error
    assert calls == []


def test_symlink_ledger_fails_closed(tmp_path, ledger, paid_factory):
    linked = tmp_path / "link.json"
    linked.symlink_to(ledger)
    factory, calls = paid_factory()
    assert stages(offering_fetcher(ledger=linked, firecrawl_factory=factory)).outcome == "unreachable"
    assert calls == []


def test_paid_failure_keeps_reservation_before_request(ledger, paid_factory):
    def fail(_request):
        assert json.loads(ledger.read_text())["months"][MONTH] == 1
        return httpx.Response(503)

    factory, calls = paid_factory(fail)
    fetcher = offering_fetcher(ledger=ledger, firecrawl_factory=factory)
    assert stages(fetcher).outcome == "unreachable"
    assert len(calls) == fetcher.credits_spent == 1
    assert json.loads(ledger.read_text())["months"][MONTH] == 1
    assert BODY not in ledger.read_bytes()


def test_interrupted_request_keeps_reservation(ledger, paid_factory):
    def interrupt(_request):
        raise KeyboardInterrupt("fixture interruption")

    factory, calls = paid_factory(interrupt)
    with pytest.raises(KeyboardInterrupt, match="fixture interruption"):
        stages(offering_fetcher(ledger=ledger, firecrawl_factory=factory))
    assert len(calls) == 1
    assert json.loads(ledger.read_text())["months"][MONTH] == 1


def test_concurrent_requests_cannot_both_take_last_credit(ledger, paid_factory):
    ledger.write_text(json.dumps({"schema_version": 1, "months": {MONTH: 99}}))
    factory, calls = paid_factory()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: stages(offering_fetcher(
            ledger=ledger, firecrawl_factory=factory)), range(2)))
    assert sorted(result.outcome for result in results) == ["ok", "unreachable"]
    assert len(calls) == 1
    assert json.loads(ledger.read_text())["months"][MONTH] == 100


def test_cite_only_fetch_returns_hash_without_bytes_or_fallback(ledger, paid_factory):
    url = "https://docs.x.ai/docs/models"
    primary = Reader(FetchResult("ok", 200, body=BODY))
    renderer = Reader()
    factory, calls = paid_factory()
    fetcher = offering_fetcher(primary=primary, renderer=renderer, lab="xai", ledger=ledger,
                              firecrawl_factory=factory)
    result = fetcher.fetch(url)
    assert result.outcome == "ok" and result.body == b""
    assert result.snapshot_ref == fingerprint_bytes(BODY)
    assert fetcher.render(url).outcome == "unreachable"
    assert fetcher.fallback(url).outcome == "unreachable"
    assert renderer.calls == [] and calls == []
    assert BODY not in ledger.read_bytes()


@pytest.mark.parametrize("url", ["https://example.com/pricing",
                               "https://zap" "ier.com/pricing",
                               "https://ai.google.dev:bad/pricing"])
def test_unapproved_hosts_never_reach_readers(url):
    primary, renderer = Reader(), Reader()
    fetcher = offering_fetcher(primary=primary, renderer=renderer)
    assert stages(fetcher, url).outcome == "unreachable"
    assert primary.calls == [] and renderer.calls == []


def test_cross_party_redirect_result_never_returns_bytes():
    primary = Reader(FetchResult("ok", 200, body=BODY,
                                resolved_urls=("https://example.com/pricing",)))
    result = offering_fetcher(primary=primary).fetch(URL)
    assert result.outcome == "unreachable" and result.body == b""


def test_live_http_adapter_hashes_cite_only_and_blocks_cross_party_redirects():
    from scripts.offering_fetch import OfferingHTTPFetcher

    seen = []

    def request(req):
        seen.append(str(req.url))
        if req.url.path == "/redirect":
            return httpx.Response(302, headers={"location": "https://example.com/price"})
        return httpx.Response(200, content=BODY, headers={"content-type": "text/html"})

    with httpx.Client(transport=httpx.MockTransport(request)) as client:
        fetcher = OfferingHTTPFetcher(client, lab="xai", terms=TERMS,
                                      retries=0, min_host_interval=0)
        result = fetcher.fetch("https://docs.x.ai/docs/models")
        assert result.body == b"" and result.snapshot_ref == fingerprint_bytes(BODY)
        denied = fetcher.fetch("https://docs.x.ai/redirect")
        assert denied.outcome == "unreachable" and denied.body == b""
    assert seen == ["https://docs.x.ai/docs/models", "https://docs.x.ai/redirect"]


def test_chromium_refuses_redirect_before_restricted_response(monkeypatch):
    pytest.importorskip("playwright.sync_api")
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    from scripts import offering_fetch

    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.path)
            if self.path == "/start":
                self.send_response(302)
                self.send_header("Location", "/restricted")
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h1>Restricted fixture source bytes</h1>")

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"

    def policy(url, *_args):
        return None if url == origin + "/start" else "restricted fixture origin"

    monkeypatch.setattr(offering_fetch, "source_block", policy)
    monkeypatch.setattr(offering_fetch, "source_fetch_block", policy)
    try:
        with offering_fetch.OfferingFetcher(Reader(), lab="google", terms={}) as fetcher:
            fetcher.fetch(origin + "/start")
            assert fetcher.render(origin + "/start").outcome == "unreachable"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert seen == ["/start"]
