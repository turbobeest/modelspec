"""MODEL-235: fallback requests, accounting and replay use fake transports only."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml

from decision import firecrawl
from decision.firecrawl import FirecrawlFetcher, firecrawl_allowed
from decision.sources import FetchResult, fingerprint_bytes
from scripts import price_reread
from scripts import price_reread_fallback as fallback
from tests.test_price_reread import (
    API_URL,
    PLANS_URL,
    RENDERED_URL,
    TODAY,
    ReplayFetcher,
    page,
)
from tests.test_price_reread import (
    estate as estate,
)

ROOT = Path(__file__).resolve().parents[1]
MONTH = "2026-10"
KEY = "fc-fixture-secret-never-networked"
PLAN = "https://chatgpt.com/pricing/"
HELP = "https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex"
API = "https://learn.chatgpt.com/api-pricing"


@pytest.fixture(autouse=True)
def fake_key(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", KEY)


def payload(html="<html><body>fixture pricing</body></html>", status=200):
    return {"success": True, "data": {"rawHtml": html, "metadata": {"statusCode": status}}}


def scraper(*, allowance=12, response=None, status=200, handler=None, balance_handler=None):
    calls = []

    def serve(request):
        if request.url.path == "/v2/team/credit-usage":
            assert request.method == "GET"
            if balance_handler:
                return balance_handler(request)
            return httpx.Response(200, json={"success": True, "data": {"remainingCredits": 1000}})
        calls.append(request)
        assert str(request.url) == "https://api.firecrawl.dev/v2/scrape"
        if handler:
            return handler(request)
        return httpx.Response(status, json=payload() if response is None else response)

    return FirecrawlFetcher(allowance=allowance, transport=httpx.MockTransport(serve)), calls


@pytest.mark.parametrize(
    "url",
    [
        PLAN,
        HELP,
        API,
        "https://learn.chatgpt.com/docs/pricing",
        "https://docs.x.ai/developers/models/grok",
        "http://x.ai/pricing?utm_source=fixture",
    ],
)
def test_exact_registry_hosts_are_allowed(url):
    assert firecrawl_allowed(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://unlisted.chatgpt.com/pricing",
        "https://chatgpt.com.example/pricing",
        "https://example.com/chatgpt.com",
        "https://example.com@chatgpt.com/pricing",
        "https://chatgpt.com:8443/pricing",
        "https://chatgpt.com:not-a-port/pricing",
        "file:///chatgpt.com/pricing",
    ],
)
def test_other_hosts_and_credentials_never_make_a_paid_request(url):
    fetcher, calls = scraper()
    assert fetcher.fetch(url).outcome == "unreachable"
    assert calls == [] and fetcher.credits_spent == 0


def test_raw_html_request_is_fresh_and_disables_per_page_parsers():
    fetcher, calls = scraper()
    result = fetcher.fetch(PLAN)
    assert result == FetchResult(
        "ok",
        200,
        body=b"<html><body>fixture pricing</body></html>",
        content_type="text/html",
        charset="utf-8",
    )
    [request] = calls
    assert request.headers["Authorization"] == "Bearer " + KEY
    assert json.loads(request.content) == {
        "url": PLAN,
        "formats": ["rawHtml"],
        "onlyMainContent": False,
        "maxAge": 0,
        "parsers": [],
        "timeout": 60000,
        "skipTlsVerification": False,
    }
    assert request.extensions["timeout"] == {"connect": 10, "read": 65, "write": 65, "pool": 65}
    assert fetcher.credits_spent == 1


def test_no_key_means_no_request(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY")
    fetcher, calls = scraper()
    assert fetcher.fetch(PLAN).error == "FIRECRAWL_API_KEY is not configured"
    assert calls == [] and fetcher.credits_spent == 0


@pytest.mark.parametrize(
    "failure,reason",
    [
        ("network", "Firecrawl team balance request failed"),
        ("timeout", "Firecrawl team balance read timed out"),
        ("http", "Firecrawl team balance HTTP 503"),
        ("redirect", "Firecrawl team balance HTTP 302"),
        ("json", "Firecrawl team balance response is invalid"),
        ("shape", "Firecrawl team balance response is invalid"),
        ("duplicate", "Firecrawl team balance response is invalid"),
        ("oversize", "Firecrawl team balance response is invalid"),
    ],
)
def test_balance_failures_make_zero_scrapes_and_record_why(
    failure, reason, capsys, caplog
):
    balance_reads = []

    def balance(request):
        balance_reads.append(request)
        if failure == "network":
            raise httpx.ConnectError(KEY, request=request)
        if failure == "timeout":
            raise httpx.ReadTimeout(KEY, request=request)
        if failure in {"http", "redirect"}:
            return httpx.Response(503 if failure == "http" else 302, json={"error": KEY})
        if failure == "json":
            return httpx.Response(200, content=b"not JSON")
        if failure == "duplicate":
            return httpx.Response(200, content=b'{"success":true,"success":false}')
        if failure == "oversize":
            return httpx.Response(200, content=b"x" * (firecrawl.MAX_BALANCE_RESPONSE_BYTES + 1))
        return httpx.Response(200, json={"success": True, "data": {"remainingCredits": True}})

    # The Firecrawl client stays for the admission fallback (MODEL-570 removed it from
    # the price re-read fallback); its balance check is exercised directly.
    paid, calls = scraper(balance_handler=balance)
    assert paid.prepare() is False
    assert calls == []
    assert len(balance_reads) == 1
    assert balance_reads[0].headers["Authorization"] == "Bearer " + KEY
    assert balance_reads[0].extensions["timeout"] == dict.fromkeys(
        ("connect", "read", "write", "pool"), 10
    )
    assert paid.fetch(PLAN).error == reason  # No retry after a failed balance read.
    assert len(balance_reads) == 1 and calls == []
    assert paid.credits_spent == 0 and paid.stop_reason == reason
    assert KEY not in str(paid.stop_reason) + capsys.readouterr().out + caplog.text


@pytest.mark.parametrize("value", [None, -1, True, "1000", [], {}, float("inf"), float("nan")])
def test_invalid_balance_values_fail_closed(value):
    paid, calls = scraper(
        balance_handler=lambda _: httpx.Response(
            200, content=json.dumps({"success": True, "data": {"remainingCredits": value}}).encode()
        )
    )
    assert paid.fetch(PLAN).error == "Firecrawl team balance response is invalid"
    assert calls == [] and paid.credits_spent == 0


@pytest.mark.parametrize(
    "body",
    [
        [],
        {"success": False},
        {"success": "true", "data": {}},
        {"success": True},
        {"success": True, "data": []},
        {"success": True, "data": {}},
        {"success": True, "data": {"remainingCredits": 1000}, "error": KEY},
    ],
)
def test_invalid_balance_shapes_fail_closed(body):
    paid, calls = scraper(balance_handler=lambda _: httpx.Response(200, json=body))
    assert paid.fetch(PLAN).error == "Firecrawl team balance response is invalid"
    assert calls == [] and paid.credits_spent == 0


@pytest.mark.parametrize(
    "remaining,spend", [(0, 0), (99, 0), (99.5, 0), (100, 1), (100.5, 1), (101, 1), (1000, 1)]
)
def test_team_balance_floor_is_one_hundred(remaining, spend):
    assert firecrawl.FIRECRAWL_MIN_TEAM_BALANCE == 100
    paid, calls = scraper(
        balance_handler=lambda _: httpx.Response(
            200, json={"success": True, "data": {"remainingCredits": remaining}}
        )
    )
    result = paid.fetch(PLAN)
    assert len(calls) == paid.credits_spent == spend
    assert paid.team_balance == remaining
    if spend:
        assert result.outcome == "ok"
    else:
        assert result.error == "Firecrawl team balance below minimum of 100 credits"


def test_balance_is_read_before_each_scrape_and_is_not_charged():
    requests = []
    balances = iter([101, 100, 99])

    def serve(request):
        requests.append((request.method, request.url.path))
        if request.method == "GET":
            return httpx.Response(
                200, json={"success": True, "data": {"remainingCredits": next(balances)}}
            )
        return httpx.Response(200, json=payload())

    paid = FirecrawlFetcher(allowance=12, transport=httpx.MockTransport(serve))
    assert paid.fetch(PLAN).outcome == "ok"
    assert paid.fetch(HELP).outcome == "ok"
    assert paid.fetch(API).outcome == "unreachable"
    assert paid.credits_spent == 2
    assert requests == [
        ("GET", "/v2/team/credit-usage"),
        ("POST", "/v2/scrape"),
        ("GET", "/v2/team/credit-usage"),
        ("POST", "/v2/scrape"),
        ("GET", "/v2/team/credit-usage"),
    ]


@pytest.mark.parametrize("remaining", [99, 99.5])
def test_low_team_balance_is_recorded_without_reserving_a_credit(remaining):
    paid, calls = scraper(
        balance_handler=lambda _: httpx.Response(
            200, json={"success": True, "data": {"remainingCredits": remaining}}
        )
    )
    assert paid.prepare() is False
    assert calls == [] and paid.credits_spent == 0 and paid.team_balance == remaining
    assert paid.stop_reason == "Firecrawl team balance below minimum of 100 credits"


@pytest.mark.parametrize(
    "field,value",
    [
        ("fake", "true"),
        ("fake", True),
        ("credits_reserved", 0),
        ("allowance", True),
        ("allowance", 13),
        ("prior_month_spend_known", -1),
        ("unreadable_ledgers", True),
        ("team_balance", True),
        ("team_balance", KEY),
        ("team_balance", float("nan")),
        ("stop_reason", KEY),
    ],
)
def test_new_artifact_accounting_rejects_forged_values_and_credentials(tmp_path, field, value):
    directory = artifact(tmp_path, fallback_manifest=True)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest.update(
        schema_version=2,
        fake=False,
        credits_reserved=1,
        allowance=12,
        prior_month_spend_known=0,
        unreadable_ledgers=0,
        team_balance=1000,
        stop_reason=None,
    )
    manifest[field] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="invalid fallback"):
        fallback.read_fallback(directory)


@pytest.mark.parametrize("status", [200, 403, 503])
def test_independent_per_run_cap_stops_at_twelve_even_when_allowance_is_forged(status):
    fetcher, calls = scraper(allowance=1000, status=status)
    results = [fetcher.fetch(PLAN) for _ in range(15)]
    assert len(calls) == fetcher.credits_spent == 12
    assert all(r.error == "Firecrawl credit allowance exhausted" for r in results[12:])


@pytest.mark.parametrize("allowance", [-1, True, 1.5, "12"])
def test_invalid_allowance_is_rejected(allowance):
    with pytest.raises(ValueError, match="allowance"):
        scraper(allowance=allowance)


@pytest.mark.parametrize(
    "response",
    [
        [],
        True,
        1,
        {"success": False, "error": KEY},
        {"success": "true", "data": {}},
        {"success": True, "data": []},
        {"success": True, "data": {"rawHtml": 3}},
        {"success": True, "data": {"rawHtml": "fixture", "metadata": []}},
        {"success": True, "data": {"rawHtml": "fixture", "metadata": {"statusCode": True}}},
        payload(""),
        payload(status=403),
        payload(status=700),
        payload(KEY),
        payload("<html>fixture</html>") | {"error": KEY},
    ],
)
def test_bad_responses_are_unreachable_and_do_not_echo_the_secret(response, capsys, caplog):
    fetcher, calls = scraper(response=response)
    result = fetcher.fetch(PLAN)
    assert result.outcome == "unreachable"
    assert len(calls) == fetcher.credits_spent == 1
    assert KEY not in repr(result) + capsys.readouterr().out + capsys.readouterr().err + caplog.text


@pytest.mark.parametrize("status", [301, 400, 401, 403, 429, 500])
def test_non_success_http_responses_are_unreachable_without_retrying(status):
    fetcher, calls = scraper(status=status, response={"error": KEY})
    assert fetcher.fetch(PLAN).error == f"Firecrawl HTTP {status}"
    assert len(calls) == fetcher.credits_spent == 1


def test_timeout_messages_cannot_leak_credentials(capsys, caplog):
    def timeout(request):
        raise httpx.ReadTimeout(KEY, request=request)

    fetcher, calls = scraper(handler=timeout)
    result = fetcher.fetch(PLAN)
    assert result.error == "Firecrawl request failed or invalid JSON"
    assert len(calls) == fetcher.credits_spent == 1
    captured = capsys.readouterr()
    assert KEY not in captured.out + captured.err + caplog.text + repr(result)


@pytest.mark.parametrize(
    "body",
    [
        b"not JSON",
        b'{"success":',
        b'"\\ud800"',
        b'{"success":true,"success":false}',
        b"[" * 1500 + b"0" + b"]" * 1500,
    ],
)
def test_invalid_json_is_unreachable(body):
    fetcher, _ = scraper(handler=lambda _: httpx.Response(200, content=body))
    assert fetcher.fetch(PLAN).outcome == "unreachable"


def test_response_size_is_bounded_while_streaming(monkeypatch):
    class Chunks(httpx.SyncByteStream):
        def __iter__(self):
            yield b"x" * 64
            yield b"x" * 64
            pytest.fail("oversize response must stop reading")

    monkeypatch.setattr(firecrawl, "MAX_FIRECRAWL_RESPONSE_BYTES", 63)
    fetcher, _ = scraper(handler=lambda _: httpx.Response(200, stream=Chunks()))
    assert fetcher.fetch(PLAN).error == "Firecrawl response exceeds 20 MiB"
    assert firecrawl.MAX_FIRECRAWL_RESPONSE_BYTES == 63


def artifact(directory, urls=None, *, ok=False, fallback_manifest=False, spent=None, version=1,
             skipped=None):
    urls = (HELP,) if urls is None else urls
    directory.mkdir(parents=True, exist_ok=True)
    pages = {}
    for index, url in enumerate(urls):
        name = f"page-{index}.html"
        if ok:
            (directory / name).write_bytes(page("plans.html"))
        pages[url] = {
            "file": name,
            "outcome": "ok" if ok else "unreachable",
            "status": 200 if ok else 403,
            "error": None if ok else "HTTP 403",
        }
    if not fallback_manifest:
        for url, entry in pages.items():
            if entry["outcome"] == "ok":
                entry["resolved_urls"] = [url]
        manifest = pages
    elif version == fallback.SCHEMA_VERSION:
        for url, entry in pages.items():
            if entry["outcome"] == "ok":
                entry["resolved_urls"] = [url]
        manifest = {
            "schema_version": version,
            "month": MONTH,
            "credits_spent": 0 if spent is None else spent,
            "reader": "playwright",
            "fake": False,
            "pages": pages,
            "skipped": skipped or {},
        }
    else:
        manifest = {
            "schema_version": 1,
            "month": MONTH,
            "credits_spent": len(pages) if spent is None else spent,
            "pages": pages,
        }
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return directory


def name_terms_register(directory, monkeypatch, terms):
    """A synthetic private terms register, named for this test (MODEL-565, MODEL-570)."""
    from decision.retention import cite_only_hosts

    (directory / "registry").mkdir(parents=True, exist_ok=True)
    (directory / "registry" / "source-terms.json").write_text(json.dumps(terms))
    (directory / "registry" / "sources.yaml").write_text('{"schema_version": 1, "sources": []}')
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(directory))
    cite_only_hosts.cache_clear()


#: Synthetic classes: the example hosts keep copies, the vendor hosts are cite-only.
TERMS = {
    "plans.example": "permits", "rendered.example": "permits", "api.example": "permits",
    "chatgpt.com": "cite-only", "help.openai.com": "cite-only", "x.ai": "cite-only",
}


@pytest.fixture(autouse=True)
def terms_register(tmp_path_factory, monkeypatch):
    # Outside tmp_path: several tests use tmp_path itself as a month ledger.
    name_terms_register(tmp_path_factory.mktemp("terms"), monkeypatch, TERMS)
    yield
    from decision.retention import cite_only_hosts

    cite_only_hosts.cache_clear()


FIXTURE_HTML = (b"<html><body><h1>Fixture pricing</h1><p>Pro is twenty dollars a month, "
                b"billed monthly.</p></body></html>")


class StubReader:
    """Stands in for the class-checked Playwright fetcher: no browser, no network."""

    def __init__(self, results=None, *, default=None):
        self.results = dict(results or {})
        self.default = default
        self.fetched = []

    def fetch(self, url, *, prepare=None):
        self.fetched.append(url)
        result = self.results.get(url, self.default)
        if result is None:
            return FetchResult("ok", 200, body=FIXTURE_HTML,
                               content_type="text/html", charset="utf-8", resolved_urls=(url,),
                               retrieved_at=datetime(2026, 10, 6, 7, 41))
        return result(url) if callable(result) else result


def run_fallback(root, tmp_path, *, render=None, plain=None, reader=None, fake=False,
                 unavailable=None):
    output = tmp_path / "fallback"
    fallback.fallback_to(
        root=root,
        rendered=price_reread.RenderedReplayFetcher(render or artifact(tmp_path / "render")),
        directory=output,
        month=MONTH,
        plain=ReplayFetcher({PLAN: [b"ok"], API: [b"ok"]}) if plain is None else plain,
        reader=reader,
        fake=fake,
        unavailable=unavailable,
    )
    return output


@pytest.fixture
def retainable_sources(monkeypatch):
    for name, url in (("PLAN", PLANS_URL), ("HELP", RENDERED_URL), ("API", API_URL)):
        monkeypatch.setitem(globals(), name, url)
    monkeypatch.setattr(firecrawl, "FIRECRAWL_HOSTS", firecrawl.FIRECRAWL_HOSTS | {
        "plans.example", "rendered.example", "api.example",
    })


@pytest.fixture
def allowed_estate(estate, retainable_sources):
    return estate


@pytest.mark.parametrize("url", [PLAN, HELP, API])
def test_new_cite_only_fallback_keeps_only_hash_and_retrieval_date(estate, tmp_path, url):
    root, _ = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(registry.read_text().replace(RENDERED_URL, url))
    reader = StubReader()
    output = run_fallback(root, tmp_path, render=artifact(tmp_path / "render", urls=(url,)),
                          plain=ReplayFetcher({}), reader=reader)
    assert reader.fetched == [url]
    replay, spent = fallback.read_fallback(output)
    result = replay.fetch(url)
    assert spent == 0
    assert result.outcome == "ok"
    assert result.body == b""
    assert result.snapshot_ref == fingerprint_bytes(FIXTURE_HTML)
    assert result.retrieved_at is not None
    assert replay.manifest[url]["citation"]["url"] == url
    assert list(output.iterdir()) == [output / "manifest.json"]
    assert "Fixture pricing" not in (output / "manifest.json").read_text()


def test_a_page_whose_every_hop_keeps_copies_keeps_its_bytes_and_chain(allowed_estate, tmp_path):
    root, _ = allowed_estate
    hops = (HELP, "https://plans.example/moved", "https://api.example/final")
    body = page("plans.html")
    reader = StubReader({HELP: FetchResult("ok", 200, body=body, content_type="text/html",
                                           resolved_urls=hops)})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, spent = fallback.read_fallback(output)
    assert spent == 0 and reader.fetched == [HELP]
    assert replay.manifest[HELP]["resolved_urls"] == list(hops)
    result = replay.fetch(HELP)
    assert (result.outcome, result.body, result.resolved_urls) == ("ok", body, hops)
    assert "bytes kept=1" in replay.spend_line and "skipped=0" in replay.spend_line


def test_a_cite_only_hop_keeps_the_hash_only(allowed_estate, tmp_path):
    root, _ = allowed_estate
    hops = (HELP, "https://help.openai.com/en/articles/1")
    reader = StubReader({HELP: FetchResult("ok", 200, body=FIXTURE_HTML + b"<p>cite-only text</p>",
                                           content_type="text/html", resolved_urls=hops)})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    assert replay.manifest[HELP]["citation"]["resolved_urls"] == list(hops)
    assert replay.fetch(HELP).body == b""
    assert list(output.iterdir()) == [output / "manifest.json"]
    assert "cite-only text" not in (output / "manifest.json").read_text()


@pytest.mark.parametrize("error,listed", [
    ("redirect_unclassified:unclassed.example", "redirect_unclassified:unclassed.example"),
    ("terms_register_unreadable", "terms_register_unreadable"),
    ("ambiguous URL", "unwalkable chain: ambiguous URL"),
    ("source redirect limit reached", "unwalkable chain: source redirect limit reached"),
    ("redirect after load not followed",
     "unwalkable chain: redirect after load not followed"),
    ("excluded source", "unwalkable chain: excluded source"),
])
def test_a_refused_host_or_unwalkable_chain_is_skipped_and_listed(
        allowed_estate, tmp_path, capsys, error, listed):
    root, _ = allowed_estate
    reader = StubReader({HELP: FetchResult("unreachable", error=error)})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    assert replay.manifest == {} and replay.skipped == {HELP: listed}
    assert f"skipped=1. Skipped: {HELP} ({listed})." in replay.spend_line
    assert list(output.iterdir()) == [output / "manifest.json"]


def test_an_ok_read_with_an_unclassed_hop_keeps_no_byte(allowed_estate, tmp_path):
    """The guard refuses an unclassed hop before it is sent; the fallback checks again."""
    root, _ = allowed_estate
    reader = StubReader({HELP: FetchResult(
        "ok", 200, body=b"<p>unclassed text</p>", content_type="text/html",
        resolved_urls=(HELP, "https://unclassed.example/page"))})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    assert replay.manifest == {}
    assert replay.skipped == {HELP: "redirect_unclassified:unclassed.example"}
    assert list(output.iterdir()) == [output / "manifest.json"]
    assert "unclassed text" not in (output / "manifest.json").read_text()


def test_the_real_rendered_fetcher_refuses_an_unclassed_start_host_before_a_page_opens(
        allowed_estate, tmp_path, tmp_path_factory, monkeypatch):
    """The guarded Playwright path (MODEL-565) checks the start host before any request."""
    import sys
    from types import ModuleType

    from decision.sources import RenderedFetcher

    sync_api = ModuleType("playwright.sync_api")
    sync_api.Error = type("Error", (Exception,), {})
    sync_api.TimeoutError = type("TimeoutError", (sync_api.Error,), {})
    monkeypatch.setitem(sys.modules, "playwright", ModuleType("playwright"))
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)
    name_terms_register(tmp_path_factory.mktemp("unclassed-terms"), monkeypatch,
                        {"plans.example": "permits", "api.example": "permits"})
    reader = RenderedFetcher()

    def no_page():
        pytest.fail("a page was opened for an unclassed host")

    reader._context = SimpleNamespace(new_page=no_page, pages=())
    output = run_fallback(allowed_estate[0], tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    assert replay.skipped == {HELP: "redirect_unclassified:rendered.example"}
    assert replay.manifest == {}


def test_a_plain_failed_read_is_recorded_unreachable_and_never_replayed_as_ok(
        allowed_estate, tmp_path):
    root, _ = allowed_estate
    reader = StubReader({HELP: FetchResult("unreachable", 503, error="HTTP 503")})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    assert replay.manifest[HELP]["outcome"] == "unreachable"
    primary = ReplayFetcher({HELP: [None]})
    assert fallback.FallbackFetcher(primary, replay).fetch(HELP).outcome == "unreachable"
    assert list(output.iterdir()) == [output / "manifest.json"]


def test_without_playwright_every_needed_page_is_a_listed_skip(allowed_estate, tmp_path):
    root, _ = allowed_estate
    output = run_fallback(root, tmp_path, plain=ReplayFetcher({PLAN: [None], API: [b"ok"]}),
                          unavailable="Playwright unavailable (ImportError)")
    replay, spent = fallback.read_fallback(output)
    assert spent == 0 and replay.manifest == {}
    assert replay.skipped == {PLAN: "Playwright unavailable (ImportError)",
                              HELP: "Playwright unavailable (ImportError)"}
    assert "pages read=0" in replay.spend_line and "skipped=2" in replay.spend_line


@pytest.mark.parametrize("alias", [False, True])
def test_failed_recipe_is_never_read_again(allowed_estate, tmp_path, alias):
    root, _ = allowed_estate
    path = root / "registry" / "sources.yaml"
    registry = yaml.safe_load(path.read_text())
    source = next(s for s in registry["sources"] if s["url"] == HELP)
    recipe = [{"action": "wait_text", "selector": "#prices", "text": "US East"}]
    if alias:
        registry["sources"].append({
            **source, "id": "recipe-alias", "rendered_interactions": recipe,
        })
    else:
        source["rendered_interactions"] = recipe
    path.write_text(yaml.safe_dump(registry))
    directory = artifact(tmp_path / "render")
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest[HELP].update(status=200, error="interaction failed: selection did not complete")
    manifest_path.write_text(json.dumps(manifest))
    rendered = price_reread.RenderedReplayFetcher(directory)
    reader = StubReader()
    output = run_fallback(root, tmp_path, render=directory, reader=reader)
    assert reader.fetched == []
    replay, spent = fallback.read_fallback(output)
    assert replay.manifest == {} and replay.skipped == {} and spent == 0
    assert rendered.fetch(HELP).outcome == "unreachable"


@pytest.mark.parametrize("render_ok,missing", [(False, False), (True, False), (False, True)])
def test_only_actual_failed_render_entries_are_read(
    allowed_estate, tmp_path, render_ok, missing
):
    root, _ = allowed_estate
    render = artifact(tmp_path / "render", urls=() if missing else (HELP,), ok=render_ok)
    reader = StubReader()
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    output = run_fallback(root, tmp_path, render=render, reader=reader)
    assert reader.fetched == ([] if render_ok or missing else [HELP])
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    replay, spent = fallback.read_fallback(output)
    assert spent == 0 and set(replay.manifest) == set(reader.fetched)


def test_a_not_modified_render_entry_is_not_a_failed_fetch(allowed_estate, tmp_path):
    root, _ = allowed_estate
    directory = artifact(tmp_path / "render")
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest[HELP].update(outcome="not_modified", status=304)
    path.write_text(json.dumps(manifest))
    reader = StubReader()
    run_fallback(root, tmp_path, render=directory, reader=reader)
    assert reader.fetched == []


def test_plain_http_failures_are_eligible_but_unlisted_hosts_are_filtered(estate, tmp_path):
    root, _ = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(registry.read_text().replace(PLANS_URL, PLAN))
    plain = ReplayFetcher({PLAN: [None]})
    reader = StubReader()
    run_fallback(root, tmp_path, render=artifact(tmp_path / "render", urls=(RENDERED_URL,)),
                 plain=plain, reader=reader)
    assert plain.fetched == [PLAN]
    assert reader.fetched == [PLAN]


def test_the_fallback_never_builds_a_firecrawl_client_or_reads_its_key():
    source = (ROOT / "scripts" / "price_reread_fallback.py").read_text()
    for name in ("FirecrawlFetcher", "FakeFirecrawlFetcher", "DisabledFirecrawlFetcher",
                 "firecrawl_opted_in", "httpx", "FIRECRAWL_API_KEY\")"):
        assert name not in source, name
    assert not hasattr(fallback, "FirecrawlFetcher")


def test_a_playwright_artifact_counts_zero_in_the_month_ledger(tmp_path):
    artifact(tmp_path / "known", urls=tuple(f"{PLAN}{n}" for n in range(7)), fallback_manifest=True)
    artifact(tmp_path / "playwright", urls=(PLAN,), fallback_manifest=True, version=3,
             skipped={HELP: "Playwright unavailable (ImportError)"})
    assert fallback.monthly_budget(tmp_path, MONTH) == fallback.MonthlyBudget(12, 7, 0)


@pytest.mark.parametrize("forgery", ["spent", "reader", "skip-reason", "overlap", "host"])
def test_a_forged_playwright_artifact_is_unreadable(tmp_path, forgery):
    directory = artifact(tmp_path / "bad", urls=(PLAN,), fallback_manifest=True, version=3)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    if forgery == "spent":
        manifest["credits_spent"] = 1
    elif forgery == "reader":
        manifest["reader"] = "firecrawl"
    elif forgery == "skip-reason":
        manifest["skipped"] = {HELP: 7}
    elif forgery == "overlap":
        manifest["skipped"] = {PLAN: "listed twice"}
    else:
        manifest["skipped"] = {"https://unlisted.example/": "not a fallback host"}
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        fallback.read_fallback(directory)


def test_a_firecrawl_artifact_is_never_replayed_as_evidence(tmp_path, retainable_sources):
    replay, spent = fallback.read_fallback(artifact(tmp_path, fallback_manifest=True, ok=True))
    assert spent == 1 and replay.legacy
    result = fallback.FallbackFetcher(ReplayFetcher({HELP: [None]}), replay).fetch(HELP)
    assert result.outcome == "unreachable" and result.body == b""


def test_monthly_ledger_math_stops_at_sixty(tmp_path):
    for index, spent in enumerate([12, 12, 12, 12, 7]):
        artifact(
            tmp_path / str(index),
            urls=tuple(f"{PLAN}{n}" for n in range(spent)),
            fallback_manifest=True,
        )
    assert fallback.monthly_budget(tmp_path, MONTH).allowance == 5
    artifact(tmp_path / "last", urls=tuple(f"{PLAN}{n}" for n in range(5)), fallback_manifest=True)
    assert fallback.monthly_budget(tmp_path, MONTH).allowance == 0


def test_monthly_accounting_keeps_known_spend_and_unreadable_count_separate(tmp_path):
    artifact(tmp_path / "known", urls=tuple(f"{PLAN}{n}" for n in range(7)), fallback_manifest=True)
    (tmp_path / "unreadable").mkdir()
    assert fallback.monthly_budget(tmp_path, MONTH) == fallback.MonthlyBudget(12, 7, 1)


@pytest.mark.parametrize(
    "forgery",
    [
        "unreadable",
        "missing",
        "negative",
        "too-large",
        "bool",
        "understated",
        "wrong-month",
        "wrong-shape",
        "symlink",
        "duplicate",
        "traversal",
        "oversize",
        "deep-json",
    ],
)
def test_unreadable_and_forged_ledgers_reserve_twelve_instead_of_increasing_the_budget(
    tmp_path,
    forgery,
):
    for index in range(4):
        artifact(
            tmp_path / str(index),
            urls=tuple(f"{PLAN}{n}" for n in range(12)),
            fallback_manifest=True,
        )
    directory = artifact(tmp_path / "bad", fallback_manifest=True)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    if forgery == "unreadable":
        path.write_text("not JSON")
    elif forgery == "deep-json":
        path.write_text("[" * 1500 + "0" + "]" * 1500)
    elif forgery == "missing":
        path.unlink()
    elif forgery == "symlink":
        path.unlink()
        path.symlink_to(tmp_path / "0" / "manifest.json")
    elif forgery == "oversize":
        with path.open("wb") as body:
            body.truncate(price_reread.MAX_RENDERED_MANIFEST_BYTES + 1)
    elif forgery == "duplicate":
        path.write_text('{"credits_spent":1,"credits_spent":0}')
    else:
        if forgery in {"negative", "too-large", "bool", "understated"}:
            manifest["credits_spent"] = {
                "negative": -60,
                "too-large": 100,
                "bool": True,
                "understated": 0,
            }[forgery]
        elif forgery == "wrong-month":
            manifest["month"] = "2026-09"
        elif forgery == "wrong-shape":
            manifest["pages"] = []
        elif forgery == "traversal":
            manifest["pages"][HELP]["file"] = "../page.html"
        path.write_text(json.dumps(manifest))
    assert fallback.monthly_budget(tmp_path, MONTH).allowance == 0


def test_empty_ledger_never_allows_more_than_twelve_and_missing_ledger_allows_nothing(tmp_path):
    assert fallback.monthly_budget(tmp_path, MONTH).allowance == 12
    assert fallback.monthly_budget(tmp_path / "missing", MONTH).allowance == 0


@pytest.mark.parametrize("primary_ok", [True, False])
def test_replay_keeps_successful_primary_html_and_only_replaces_failure(
    tmp_path, primary_ok, retainable_sources
):
    replay, _ = fallback.read_fallback(
        artifact(tmp_path, fallback_manifest=True, ok=True, version=3))
    primary = ReplayFetcher({HELP: [b"primary HTML" if primary_ok else None]})
    result = fallback.FallbackFetcher(primary, replay).fetch(HELP)
    assert result.body == (b"primary HTML" if primary_ok else page("plans.html"))
    assert primary.fetched == [HELP]


def test_fallback_artifact_reuses_the_render_validator(tmp_path, retainable_sources):
    directory = artifact(tmp_path, fallback_manifest=True, ok=True, version=3)
    (directory / "page-0.html").unlink()
    (directory / "page-0.html").symlink_to(ROOT / "scripts" / "price_reread.py")
    with pytest.raises(ValueError, match="symlink"):
        fallback.read_fallback(directory)


def test_cli_replay_reconfirms_without_constructing_a_paid_fetcher(
    allowed_estate,
    tmp_path,
    monkeypatch,
    capsys,
):
    root, store = allowed_estate
    rendered = artifact(tmp_path / "render")
    paid = artifact(tmp_path / "fallback", fallback_manifest=True, ok=True,
                    version=3)
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(price_reread, "CopyStore", lambda: store)
    monkeypatch.setattr(
        price_reread,
        "Fetcher",
        lambda **_: ReplayFetcher({PLAN: [page("plans.html")], API: [page("api-pricing.html")]}),
    )
    monkeypatch.delenv("FIRECRAWL_API_KEY")

    def forbidden(**_):
        pytest.fail("replay must never construct a paid fetcher")

    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", forbidden)
    report = tmp_path / "report.json"
    assert (
        price_reread.main(
            [
                "--rendered-from",
                str(rendered),
                "--fallback-from",
                str(paid),
                "--today",
                TODAY.isoformat(),
                "--report-json",
                str(report),
            ]
        )
        == 0
    )
    assert json.loads(report.read_text())["counts"]["unchanged"] == 6
    assert ("Playwright fallback: no Firecrawl, credits used=0; pages read=1"
            in capsys.readouterr().out)


class StubBrowser:
    """A context manager standing in for the guarded ``RenderedFetcher`` in CLI runs."""

    def __init__(self, reader):
        self.reader = reader
        self.entered = 0

    def __call__(self, *_, **__):
        return self

    def __enter__(self):
        self.entered += 1
        return self.reader

    def __exit__(self, *_):
        return None


def test_cli_fallback_reads_through_the_guarded_renderer_and_never_builds_firecrawl(
    allowed_estate,
    tmp_path,
    monkeypatch,
    capsys,
    caplog,
):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 15, tzinfo=tz)

    monkeypatch.setattr(price_reread, "datetime", FrozenDateTime)
    root, _ = allowed_estate
    rendered = artifact(tmp_path / "render")
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    artifact(ledger / "known", urls=tuple(f"{PLAN}{n}" for n in range(7)), fallback_manifest=True)
    summary = tmp_path / "step-summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    # Even opted in with a key, no Firecrawl client is constructed (MODEL-570).
    monkeypatch.setenv("PRICE_REREAD_FIRECRAWL_OPT_IN", "1")
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )

    def forbidden(*_, **__):
        pytest.fail("fallback mode must not build Firecrawl or a store, or run verification")

    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", forbidden)
    monkeypatch.setattr(price_reread, "CopyStore", forbidden)
    monkeypatch.setattr(price_reread, "run", forbidden)
    reader = StubReader({API: FetchResult("unreachable", error="redirect_unclassified:x.example")})
    browser = StubBrowser(reader)
    monkeypatch.setattr(price_reread, "RenderedFetcher", browser)
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    output = tmp_path / "fallback"
    assert price_reread.main([
        "--fallback-from-render", str(rendered), "--fallback-to", str(output),
        "--fallback-ledger", str(ledger),
    ]) == 0
    assert browser.entered == 1 and sorted(reader.fetched) == sorted([PLAN, HELP, API])
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["credits_spent"] == 0 and manifest["reader"] == "playwright"
    assert set(manifest["pages"]) == {PLAN, HELP}
    assert manifest["skipped"] == {API: "redirect_unclassified:x.example"}
    replay, _ = fallback.read_fallback(output)
    assert summary.read_text() == replay.spend_line + "\n"
    assert replay.spend_line.startswith(
        "Playwright fallback: no Firecrawl, credits used=0; pages read=2; bytes kept=2; ")
    assert fallback.monthly_budget(ledger, "2026-10").known_spend == 7
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    captured = capsys.readouterr()
    assert KEY not in json.dumps(manifest) + captured.out + captured.err + caplog.text


@pytest.mark.parametrize("failure", [ImportError, RuntimeError])
def test_cli_without_playwright_is_green_and_lists_every_needed_page(
        allowed_estate, tmp_path, monkeypatch, capsys, failure):
    root, _ = allowed_estate
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )

    def missing(*_, **__):
        raise failure("no browser")

    monkeypatch.setattr(price_reread, "RenderedFetcher", missing)
    output = tmp_path / "fallback"
    assert price_reread.main([
        "--fallback-from-render", str(artifact(tmp_path / "render")), "--fallback-to",
        str(output), "--fallback-ledger", str(ledger),
    ]) == 0
    manifest = json.loads((output / "manifest.json").read_text())
    why = f"Playwright unavailable ({failure.__name__})"
    assert manifest["pages"] == {} and manifest["skipped"] == {PLAN: why, HELP: why, API: why}
    assert "skipped=3" in capsys.readouterr().out


def test_a_failed_fallback_read_never_advances_a_last_read(allowed_estate, tmp_path, monkeypatch):
    """A skipped or failed fallback leaves every verification record and offering as it was."""
    root, store = allowed_estate
    rendered = artifact(tmp_path / "render")
    replay_dir = artifact(tmp_path / "fallback", urls=(PLAN,), fallback_manifest=True,
                          version=3, skipped={API: "redirect_unclassified:x.example"})
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(price_reread, "CopyStore", lambda: store)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    report = tmp_path / "report.json"
    assert price_reread.main([
        "--rendered-from", str(rendered), "--fallback-from", str(replay_dir),
        "--today", TODAY.isoformat(), "--report-json", str(report), "--write",
    ]) == 0
    counts = json.loads(report.read_text())["counts"]
    assert counts["unchanged"] == counts["changed"] == 0
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before


def test_cli_validates_the_render_artifact_before_starting_a_browser(
    tmp_path, monkeypatch
):
    (tmp_path / "manifest.json").write_text("[]")

    def forbidden(*_, **__):
        pytest.fail("an invalid rendered manifest must fail before a browser starts")

    monkeypatch.setattr(price_reread, "RenderedFetcher", forbidden)
    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", forbidden)
    with pytest.raises(SystemExit) as exc:
        price_reread.main(
            [
                "--fallback-from-render",
                str(tmp_path),
                "--fallback-to",
                str(tmp_path / "out"),
                "--fallback-ledger",
                str(tmp_path / "ledger"),
            ]
        )
    assert exc.value.code == 2


@pytest.mark.parametrize(
    "args",
    [
        ["--fallback-from-render", "in"],
        ["--fallback-to", "out"],
        ["--fallback-ledger", "ledger"],
        ["--fallback-from", "in"],
        [
            "--fallback-from-render",
            "in",
            "--fallback-to",
            "out",
            "--fallback-ledger",
            "ledger",
            "--write",
        ],
        ["--rendered", "--fallback-from-render", "in"],
    ],
)
def test_fallback_cli_rejects_incomplete_or_writing_modes(args):
    with pytest.raises(SystemExit) as exc:
        price_reread.main(args)
    assert exc.value.code == 2


def workflow():
    return yaml.safe_load((ROOT / ".github" / "private-writers" / "price-reread.yml").read_text())


@pytest.mark.parametrize("fake", [False, True])
def test_fallback_workflow_argv_uses_isolated_python_and_passes_both_artifacts_and_ledger(
    tmp_path, fake
):
    name = (
        "Fake fallback demo without credentials or network"
        if fake
        else "Read only failed eligible pages"
    )
    step = next(s for s in workflow()["jobs"]["fallback"]["steps"] if s.get("name") == name)
    script = """python() { printf '%s\\n' "$@" > "$RUNNER_TEMP/argv"; }
""" + step["run"]
    subprocess.run(
        ["bash", "-c", script],
        check=True,
        capture_output=True,
        env={**os.environ, "RUNNER_TEMP": str(tmp_path)},
    )
    expected = [
        "-I",
        "-m",
        "scripts.price_reread",
        "--fallback-from-render",
        str(tmp_path / "rendered"),
        "--fallback-to",
        str(tmp_path / "fallback"),
        "--fallback-ledger",
        str(tmp_path / "firecrawl-ledger"),
    ]
    assert (tmp_path / "argv").read_text().splitlines() == expected + (
        ["--fallback-fake"] if fake else []
    )
    assert "secrets." not in json.dumps(step)


def test_workflow_needs_no_spend_gate_retains_a_full_month_and_replays_when_skipped():
    """MODEL-570: the fallback reads through Playwright, so no Firecrawl gate, key or ledger."""
    jobs = workflow()["jobs"]
    assert "github.ref == 'refs/heads/main'" in jobs["fallback"]["if"]
    text = (ROOT / ".github" / "private-writers" / "price-reread.yml").read_text()
    assert "PRICE_REREAD_FIRECRAWL" not in text and "FIRECRAWL_API_KEY" not in text
    assert "secrets." not in json.dumps(jobs["fallback"])
    names = [s.get("name") for s in jobs["fallback"]["steps"]]
    assert "Restore this UTC month's fallback ledger" not in names
    install = next(s for s in jobs["fallback"]["steps"]
                   if s.get("name") == "Install fallback dependencies")
    render = next(s for s in jobs["render"]["steps"]
                  if s.get("name") == "Install render dependencies")
    # The same hash-pinned Playwright and Chromium as the render job.
    assert install["run"] == render["run"]
    assert jobs["fallback"]["needs"] == "render"
    assert jobs["fallback"]["permissions"] == {"contents": "read", "actions": "read"}
    assert jobs["reread"]["needs"] == ["render", "fallback"]
    assert jobs["reread"]["if"] == (
        "always() && needs.render.result == 'success' && "
        "(needs.fallback.result == 'success' || needs.fallback.result == 'skipped')"
    )
    upload = next(
        s for s in jobs["fallback"]["steps"] if s.get("uses") == "actions/upload-artifact@v4"
    )
    assert upload["if"] == "always()" and upload["with"]["retention-days"] == 35
    # One artifact per attempt: a rerun never collides with the first attempt's upload, and
    # the re-read downloads the one this attempt wrote.
    name = "price-reread-fallback-${{ github.run_attempt }}"
    download = next(s for s in jobs["reread"]["steps"]
                    if s.get("name") == "Download fallback pages when present")
    assert upload["with"]["name"] == download["with"]["name"] == name
    assert "price-reread-fallback\n" not in text
    assert "FIRECRAWL" not in json.dumps(jobs["reread"])
    triggers = workflow()["on"]
    assert triggers["workflow_dispatch"]["inputs"]["fallback_fake"] == {
        "description": "Run the isolated fallback demo with fake HTML, zero credits and no key",
        "type": "boolean",
        "default": False,
    }


@pytest.mark.parametrize(
    "event,attempt,fake,ref,job_runs,read_runs,fake_runs",
    [
        ("schedule", 1, False, "main", True, True, False),
        ("schedule", 2, False, "main", True, True, False),
        ("schedule", 1, False, "other", False, False, False),
        ("workflow_dispatch", 1, False, "main", False, False, False),
        ("workflow_dispatch", 1, True, "main", True, False, True),
        ("workflow_dispatch", 2, True, "main", True, False, True),
        ("workflow_dispatch", 1, True, "other", False, False, False),
        ("pull_request", 1, True, "main", False, False, False),
    ],
)
def test_workflow_reads_on_schedule_and_allows_a_keyless_demo(
    event, attempt, fake, ref, job_runs, read_runs, fake_runs
):
    job = workflow()["jobs"]["fallback"]
    context = {
        "github": SimpleNamespace(event_name=event, run_attempt=attempt, ref=f"refs/heads/{ref}"),
        "inputs": SimpleNamespace(fallback_fake=fake),
    }

    def permits(condition):
        return bool(
            eval(
                condition.replace("&&", " and ").replace("||", " or "),
                {"__builtins__": {}},
                context,
            )
        )

    runs = permits(job["if"])
    assert runs is job_runs
    read = next(s for s in job["steps"] if s.get("name") == "Read only failed eligible pages")
    demo = next(
        s
        for s in job["steps"]
        if s.get("name") == "Fake fallback demo without credentials or network"
    )
    assert (runs and permits(read["if"])) is read_runs
    assert (runs and permits(demo["if"])) is fake_runs
    assert "env" not in demo and "env" not in read


def test_cli_fake_artifact_and_reread_never_treat_fake_bodies_as_evidence(
    allowed_estate, tmp_path, monkeypatch, capsys
):
    root, store = allowed_estate
    rendered = artifact(tmp_path / "render")
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    output = tmp_path / "fallback"
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.delenv("FIRECRAWL_API_KEY")
    monkeypatch.setattr(price_reread, "ROOT", root)

    def forbidden(*_, **__):
        pytest.fail("fake fallback must not construct an HTTP client or a paid fetcher")

    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", forbidden)
    monkeypatch.setattr(httpx, "Client", forbidden)
    monkeypatch.setattr(price_reread, "Fetcher", forbidden)
    monkeypatch.setattr(price_reread, "RenderedFetcher", forbidden)
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert (
        price_reread.main(
            [
                "--fallback-from-render",
                str(rendered),
                "--fallback-to",
                str(output),
                "--fallback-ledger",
                str(ledger),
                "--fallback-fake",
            ]
        )
        == 0
    )
    replay, spent = fallback.read_fallback(output)
    assert spent == 0 and replay.fake is True
    assert set(replay.manifest) == {PLAN, HELP, API}
    for url, entry in replay.manifest.items():
        body = (output / entry["file"]).read_bytes()
        assert b"FAKE" in body and url.encode() in body
        assert body == fallback.FakeReader().fetch(url).body
    assert summary.read_text() == replay.spend_line + "\n"
    assert "Playwright fallback FAKE: no Firecrawl, credits used=0" in replay.spend_line
    assert KEY not in capsys.readouterr().out + summary.read_text()

    # Even bodies that would verify real prices cannot become evidence when
    # the validated artifact says the run was fake.
    for url, entry in replay.manifest.items():
        (output / entry["file"]).write_bytes(
            page("api-pricing.html" if url == API else "plans.html")
        )
    monkeypatch.setattr(price_reread, "CopyStore", lambda: store)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )
    report = tmp_path / "report.json"
    markdown = tmp_path / "report.md"
    assert (
        price_reread.main(
            [
                "--rendered-from",
                str(rendered),
                "--fallback-from",
                str(output),
                "--today",
                TODAY.isoformat(),
                "--report-json",
                str(report),
                "--report-md",
                str(markdown),
                "--write",
            ]
        )
        == 0
    )
    result = json.loads(report.read_text())
    assert result["counts"]["unchanged"] == result["counts"]["changed"] == 0
    assert result["not_reread"]["fallback was a fake run"] == 6
    assert all(s["copy"] is None for s in result["sources"].values())
    assert replay.spend_line in markdown.read_text()
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before


AWS_PRICING = "https://aws.amazon.com/bedrock/pricing/"


def test_a_fallback_around_a_replay_never_passes_a_preparation(tmp_path, retainable_sources):
    """Run 38037233884: the AWS preparation reached FallbackFetcher(replay).fetch."""
    rendered = tmp_path / "rendered"
    rendered.mkdir()
    (rendered / "aws.html").write_bytes(b"<html><body>captured</body></html>")
    (rendered / "manifest.json").write_text(json.dumps({AWS_PRICING: {
        "file": "aws.html", "outcome": "ok", "status": 200, "error": None,
        "resolved_urls": [AWS_PRICING]}}))
    replay, _ = fallback.read_fallback(
        artifact(tmp_path / "fallback", fallback_manifest=True, ok=True, version=3))
    wrapped = fallback.FallbackFetcher(price_reread.RenderedReplayFetcher(rendered), replay)
    result = price_reread._fetch_rendered(wrapped, AWS_PRICING, ("aws-pricing",))
    assert (result.outcome, result.body) == ("ok", b"<html><body>captured</body></html>")


def test_a_fallback_around_a_live_renderer_keeps_the_preparation(tmp_path, retainable_sources):
    class LiveRenderer(price_reread.RenderedFetcher):
        def __init__(self):
            self.prepared = []

        def fetch(self, url, *, prepare=None):
            self.prepared.append(prepare)
            return FetchResult("ok", 200, body=b"live", content_type="text/html")

    live = LiveRenderer()
    replay, _ = fallback.read_fallback(
        artifact(tmp_path, fallback_manifest=True, ok=True, version=3))
    result = price_reread._fetch_rendered(fallback.FallbackFetcher(live, replay),
                                          AWS_PRICING, ("aws-pricing",))
    assert result.body == b"live"
    assert live.prepared == [price_reread.RENDERED_PREPARATIONS["aws-pricing"]]


def test_firecrawl_is_never_constructed_even_with_a_key_and_the_old_opt_in(
    allowed_estate, tmp_path, monkeypatch
):
    """MODEL-570: the fallback has no Firecrawl path left, opted in or not."""
    root, _ = allowed_estate
    rendered = artifact(tmp_path / "render")
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    monkeypatch.setenv("FIRECRAWL_API_KEY", "present-but-unused")
    monkeypatch.setenv("PRICE_REREAD_FIRECRAWL_OPT_IN", "1")
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )

    def forbidden(*_, **__):
        pytest.fail("a Firecrawl client or HTTP client was constructed")

    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", forbidden)
    monkeypatch.setattr(firecrawl, "DisabledFirecrawlFetcher", forbidden)
    monkeypatch.setattr(httpx, "Client", forbidden)
    monkeypatch.setattr(price_reread, "RenderedFetcher", StubBrowser(StubReader()))
    out = tmp_path / "out"
    assert price_reread.main(
        ["--fallback-from-render", str(rendered), "--fallback-to", str(out),
         "--fallback-ledger", str(ledger)]) == 0
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["credits_spent"] == 0 and set(manifest["pages"]) == {PLAN, HELP, API}


# --- MODEL-570 review: retaining allowlist, complete cite-only reads, strict artifacts ---------


@pytest.mark.parametrize("value,kept", [
    ("permits", True), ("restricts", True),
    ("unclear", False), ("", False), ("reviewing", False),
])
def test_only_an_explicit_retaining_class_keeps_bytes(
        allowed_estate, tmp_path, tmp_path_factory, monkeypatch, value, kept):
    root, _ = allowed_estate
    name_terms_register(tmp_path_factory.mktemp("class-terms"), monkeypatch,
                        {**TERMS, "hop.example": value})
    hops = (HELP, "https://hop.example/page")
    reader = StubReader({HELP: FetchResult("ok", 200, body=FIXTURE_HTML, resolved_urls=hops,
                                           content_type="text/html")})
    output = run_fallback(root, tmp_path, reader=reader)
    replay, _ = fallback.read_fallback(output)
    if kept:
        assert replay.fetch(HELP).body == FIXTURE_HTML and replay.skipped == {}
    else:
        assert replay.manifest == {}
        assert replay.skipped == {HELP: f"no retaining class:hop.example:{value or 'empty'}"}
        assert list(output.iterdir()) == [output / "manifest.json"]


@pytest.mark.parametrize("body,error,listed", [
    (FIXTURE_HTML, "rendered preparation failed: timeout",
     "partial read: rendered preparation failed: timeout"),
    (b"<html><body>Loading</body></html>", None,
     "cite-only read failed: shell_page:text_below_40_chars"),
    (b"   ", None, "cite-only read failed: shell_page:empty_body"),
])
def test_a_partial_or_shell_cite_only_read_is_a_failed_read_with_no_hash(
        estate, tmp_path, body, error, listed):
    root, _ = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(registry.read_text().replace(RENDERED_URL, HELP))
    reader = StubReader({HELP: FetchResult("ok", 200, body=body, error=error,
                                           content_type="text/html", resolved_urls=(HELP,))})
    output = run_fallback(root, tmp_path, render=artifact(tmp_path / "render", urls=(HELP,)),
                          plain=ReplayFetcher({}), reader=reader)
    replay, _ = fallback.read_fallback(output)
    entry = replay.manifest[HELP]
    assert entry["outcome"] == "unreachable" and entry["error"] == listed
    assert "citation" not in entry
    assert list(output.iterdir()) == [output / "manifest.json"]
    result = fallback.FallbackFetcher(ReplayFetcher({HELP: [None]}), replay).fetch(HELP)
    assert result.outcome == "unreachable" and result.snapshot_ref is None


@pytest.mark.parametrize("forgery", ["no-chain", "empty-chain", "unclear-hop", "cite-only-hop",
                                     "unclassed-hop", "stray-file"])
def test_a_kept_page_without_a_retaining_chain_is_never_replayed(
        tmp_path, tmp_path_factory, monkeypatch, retainable_sources, forgery):
    name_terms_register(tmp_path_factory.mktemp("chain-terms"), monkeypatch,
                        {**TERMS, "hop.example": "unclear"})
    directory = artifact(tmp_path / "fallback", fallback_manifest=True, ok=True, version=3)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    entry = manifest["pages"][HELP]
    if forgery == "no-chain":
        del entry["resolved_urls"]
    elif forgery == "empty-chain":
        entry["resolved_urls"] = []
    elif forgery == "unclear-hop":
        entry["resolved_urls"] = [HELP, "https://hop.example/page"]
    elif forgery == "cite-only-hop":
        entry["resolved_urls"] = [HELP, "https://help.openai.com/en/articles/1"]
    elif forgery == "unclassed-hop":
        entry["resolved_urls"] = [HELP, "https://unclassed.example/page"]
    else:
        (directory / "stale.html").write_bytes(b"<p>an earlier run's page</p>")
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        fallback.read_fallback(directory)
    assert fallback.monthly_budget(tmp_path, MONTH).unreadable_ledgers == 1


def test_a_kept_page_needs_a_terms_register_to_be_replayed(tmp_path, monkeypatch,
                                                           retainable_sources):
    directory = artifact(tmp_path / "fallback", fallback_manifest=True, ok=True, version=3)
    monkeypatch.delenv("MODELSPEC_DATA_DIR")
    with pytest.raises(ValueError, match="retaining-class"):
        fallback.read_fallback(directory)


@pytest.mark.parametrize("leftover", ["file", "dir"])
def test_the_fallback_refuses_an_output_directory_with_earlier_files(
        allowed_estate, tmp_path, monkeypatch, leftover):
    root, _ = allowed_estate
    output = tmp_path / "fallback"
    output.mkdir()
    if leftover == "file":
        (output / "0123.html").write_bytes(b"<p>stale</p>")
    else:
        (output / "old").mkdir()
    reader = StubReader()
    with pytest.raises(ValueError, match="new or empty"):
        run_fallback(root, tmp_path, reader=reader)
    assert reader.fetched == []
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(price_reread, "RenderedFetcher", StubBrowser(reader))
    monkeypatch.setattr(price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None]}))
    with pytest.raises(SystemExit) as exc:
        price_reread.main(["--fallback-from-render", str(artifact(tmp_path / "render")),
                           "--fallback-to", str(output), "--fallback-ledger", str(tmp_path)])
    assert exc.value.code == 2 and reader.fetched == []


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("damage", ["missing-retrieved-at", "retrieved-at-number",
                                    "citation-chain-number"])
def test_a_malformed_entry_makes_the_artifact_unreadable_and_never_raises(
        tmp_path, version, damage):
    ledger = tmp_path / "ledger"
    directory = artifact(ledger / "bad", urls=(PLAN,), fallback_manifest=True,
                         version=3 if version == 3 else 1)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    if version == 2:
        manifest.update(schema_version=2, fake=False, credits_reserved=1, allowance=12,
                        prior_month_spend_known=0, unreadable_ledgers=0, team_balance=1000,
                        stop_reason=None)
    entry = manifest["pages"][PLAN]
    entry.update(outcome="ok", status=200, error=None)
    entry["citation"] = {"url": PLAN, "snapshot_ref": "sha256:" + "0" * 64,
                         "retrieved_at": "2026-10-06T07:41:00+00:00", "resolved_urls": [PLAN]}
    if damage == "missing-retrieved-at":
        del entry["citation"]["retrieved_at"]
    elif damage == "retrieved-at-number":
        entry["citation"]["retrieved_at"] = 7
    else:
        entry["citation"]["resolved_urls"] = 7
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        fallback.read_fallback(directory)
    # Counted unreadable: the full 12-credit reservation, never an exception.
    assert fallback.monthly_budget(ledger, MONTH) == fallback.MonthlyBudget(12, 0, 1)


# --- MODEL-570 review round 2: entry shapes, partial cite-only reads, required chains --------

CITATION = {"url": HELP, "snapshot_ref": "sha256:" + "0" * 64,
            "retrieved_at": "2026-10-06T07:41:00+00:00", "resolved_urls": [HELP]}


@pytest.mark.parametrize("version", [1, 3])
@pytest.mark.parametrize("entry", [None, [], "ok", {"file": "page-0.html"},
                                   {"file": "page-0.html", "status": 200, "error": None}])
def test_a_malformed_entry_shape_is_an_unreadable_artifact(tmp_path, version, entry):
    ledger = tmp_path / "ledger"
    directory = artifact(ledger / "bad", urls=(PLAN,), fallback_manifest=True, version=version)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["pages"][PLAN] = entry
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        fallback.read_fallback(directory)
    assert fallback.monthly_budget(ledger, MONTH) == fallback.MonthlyBudget(12, 0, 1)


def _cite_only_render(tmp_path, entry):
    directory = tmp_path / "render"
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps({HELP: entry}))
    return directory


def test_a_cite_only_entry_with_a_preparation_error_is_never_replayed_as_a_citation(tmp_path):
    entry = {"file": "x.html", "outcome": "ok", "status": 200,
             "error": "rendered preparation failed: timeout", "citation": CITATION}
    replay = price_reread.RenderedReplayFetcher(_cite_only_render(tmp_path, entry))
    result = replay.fetch(HELP)
    assert result.outcome == "unreachable" and result.snapshot_ref is None
    assert result.retrieved_at is None and "cite-only read failed" in result.error


def test_a_cite_only_fallback_entry_with_an_error_never_replaces_a_failed_primary(tmp_path):
    directory = tmp_path / "fallback"
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps({
        "schema_version": 3, "month": MONTH, "credits_spent": 0, "reader": "playwright",
        "fake": False, "skipped": {},
        "pages": {HELP: {"file": "x.html", "outcome": "ok", "status": 200,
                         "error": "rendered preparation failed: timeout",
                         "citation": CITATION}}}))
    replay, _ = fallback.read_fallback(directory)
    result = fallback.FallbackFetcher(ReplayFetcher({HELP: [None]}), replay).fetch(HELP)
    assert result.outcome == "unreachable" and result.snapshot_ref is None


def test_render_to_never_writes_ok_with_an_error_for_a_cite_only_page(estate, tmp_path):
    root, _ = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(registry.read_text().replace(RENDERED_URL, HELP))
    reader = StubReader({HELP: FetchResult("ok", 200, body=FIXTURE_HTML, content_type="text/html",
                                           error="rendered preparation failed: timeout",
                                           resolved_urls=(HELP,))})
    output = tmp_path / "render"
    price_reread.render_to(root=root, directory=output, rendered=reader)
    entry = json.loads((output / "manifest.json").read_text())[HELP]
    assert entry["outcome"] == "unreachable" and "citation" not in entry
    assert entry["error"] == "cite-only read failed: rendered preparation failed: timeout"
    assert list(output.iterdir()) == [output / "manifest.json"]


def test_the_fallback_never_writes_ok_with_an_error(allowed_estate, tmp_path):
    root, _ = allowed_estate
    reader = StubReader({HELP: FetchResult("ok", 200, body=FIXTURE_HTML, content_type="text/html",
                                           error="rendered preparation failed: timeout",
                                           resolved_urls=(HELP,))})
    output = run_fallback(root, tmp_path, reader=reader)
    manifest = json.loads((output / "manifest.json").read_text())
    assert all(e["outcome"] != "ok" or e["error"] is None for e in manifest["pages"].values())
    assert manifest["pages"][HELP]["outcome"] == "unreachable"
    assert list(output.iterdir()) == [output / "manifest.json"]


@pytest.mark.parametrize("kind", ["retained-missing", "retained-empty", "citation-missing",
                                  "citation-empty", "citation-bad-hop"])
def test_a_replayable_entry_without_a_chain_is_refused_at_admission(
        tmp_path, retainable_sources, kind):
    if kind.startswith("retained"):
        url = RENDERED_URL
        entry = {"file": "page.html", "outcome": "ok", "status": 200, "error": None}
        if kind == "retained-empty":
            entry["resolved_urls"] = []
        directory = tmp_path / "render"
        directory.mkdir()
        (directory / "page.html").write_bytes(FIXTURE_HTML)
    else:
        url = "https://help.openai.com/en/articles/1"
        citation = {**CITATION, "url": url, "resolved_urls": [url]}
        if kind == "citation-missing":
            del citation["resolved_urls"]
        elif kind == "citation-empty":
            citation["resolved_urls"] = []
        else:
            citation["resolved_urls"] = [7]
        entry = {"file": "x.html", "outcome": "ok", "status": 200, "error": None,
                 "citation": citation}
        directory = tmp_path / "render"
        directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps({url: entry}))
    with pytest.raises(ValueError):
        price_reread.RenderedReplayFetcher(directory)
