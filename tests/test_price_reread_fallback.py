"""MODEL-235: fallback requests, accounting and replay use fake transports only."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
import yaml

from decision import firecrawl
from decision.firecrawl import FirecrawlFetcher, firecrawl_allowed
from decision.sources import FetchResult
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
API = "https://x.ai/pricing"


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
    failure, reason, allowed_estate, tmp_path, capsys, caplog
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

    paid, calls = scraper(balance_handler=balance)
    root, _ = allowed_estate
    output = tmp_path / "fallback"
    fallback.fallback_to(
        root=root,
        rendered=price_reread.RenderedReplayFetcher(artifact(tmp_path / "render")),
        directory=output,
        month=MONTH,
        plain=ReplayFetcher({PLAN: [None], API: [None]}),
        firecrawl=paid,
        budget=fallback.MonthlyBudget(12, 7, 1),
    )
    assert calls == []
    assert len(balance_reads) == 1
    assert balance_reads[0].headers["Authorization"] == "Bearer " + KEY
    assert balance_reads[0].extensions["timeout"] == dict.fromkeys(
        ("connect", "read", "write", "pool"), 10
    )
    assert paid.fetch(PLAN).error == reason  # No retry after a failed balance read.
    assert len(balance_reads) == 1 and calls == []
    replay, spent = fallback.read_fallback(output)
    manifest = (output / "manifest.json").read_text()
    assert spent == paid.credits_spent == 0
    assert replay.manifest == {}
    assert json.loads(manifest)["stop_reason"] == reason
    assert reason in replay.spend_line and "team balance=unread" in replay.spend_line
    assert KEY not in manifest + replay.spend_line + capsys.readouterr().out + caplog.text


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
def test_low_team_balance_is_recorded_without_reserving_a_credit(
    remaining, allowed_estate, tmp_path
):
    root, _ = allowed_estate
    paid, calls = scraper(
        balance_handler=lambda _: httpx.Response(
            200, json={"success": True, "data": {"remainingCredits": remaining}}
        )
    )
    output = tmp_path / "fallback"
    fallback.fallback_to(
        root=root,
        rendered=price_reread.RenderedReplayFetcher(artifact(tmp_path / "render")),
        directory=output,
        month=MONTH,
        plain=ReplayFetcher({PLAN: [None], API: [None]}),
        firecrawl=paid,
        budget=fallback.MonthlyBudget(12, 0, 0),
    )
    replay, spent = fallback.read_fallback(output)
    assert spent == 0 and calls == [] and replay.manifest == {}
    assert json.loads((output / "manifest.json").read_text())["team_balance"] == remaining
    assert f"team balance={remaining}" in replay.spend_line
    assert "Stopped: Firecrawl team balance below minimum of 100 credits" in replay.spend_line


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


def artifact(directory, urls=(HELP,), *, ok=False, fallback_manifest=False, spent=None):
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
    manifest = (
        {
            "schema_version": 1,
            "month": MONTH,
            "credits_spent": len(pages) if spent is None else spent,
            "pages": pages,
        }
        if fallback_manifest
        else pages
    )
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return directory


@pytest.fixture
def allowed_estate(estate):
    root, store = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(
        registry.read_text()
        .replace(PLANS_URL, PLAN)
        .replace(API_URL, API)
        .replace(RENDERED_URL, HELP)
    )
    return root, store


@pytest.mark.parametrize("render_ok,missing", [(False, False), (True, False), (False, True)])
def test_only_actual_failed_render_entries_are_fetched(
    allowed_estate, tmp_path, render_ok, missing
):
    root, _ = allowed_estate
    rendered = price_reread.RenderedReplayFetcher(
        artifact(tmp_path / "render", urls=() if missing else (HELP,), ok=render_ok)
    )
    paid, calls = scraper()
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    fallback.fallback_to(
        root=root,
        rendered=rendered,
        directory=tmp_path / "fallback",
        month=MONTH,
        plain=ReplayFetcher({PLAN: [b"ok"], API: [b"ok"]}),
        firecrawl=paid,
        budget=fallback.MonthlyBudget(paid.allowance, 0, 0),
    )
    assert [json.loads(c.content)["url"] for c in calls] == ([] if render_ok or missing else [HELP])
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    _, spent = fallback.read_fallback(tmp_path / "fallback")
    assert spent == len(calls)


def test_a_not_modified_render_entry_is_not_a_failed_fetch(allowed_estate, tmp_path):
    root, _ = allowed_estate
    directory = artifact(tmp_path / "render")
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest[HELP].update(outcome="not_modified", status=304)
    path.write_text(json.dumps(manifest))
    paid, calls = scraper()
    fallback.fallback_to(
        root=root,
        rendered=price_reread.RenderedReplayFetcher(directory),
        directory=tmp_path / "fallback",
        month=MONTH,
        plain=ReplayFetcher({PLAN: [b"ok"], API: [b"ok"]}),
        firecrawl=paid,
        budget=fallback.MonthlyBudget(paid.allowance, 0, 0),
    )
    assert calls == []


def test_plain_http_failures_are_eligible_but_unlisted_hosts_are_filtered(estate, tmp_path):
    root, _ = estate
    registry = root / "registry" / "sources.yaml"
    registry.write_text(registry.read_text().replace(PLANS_URL, PLAN))
    rendered = price_reread.RenderedReplayFetcher(
        artifact(tmp_path / "render", urls=(RENDERED_URL,))
    )
    plain = ReplayFetcher({PLAN: [None]})
    paid, calls = scraper()
    fallback.fallback_to(
        root=root,
        rendered=rendered,
        directory=tmp_path / "fallback",
        month=MONTH,
        plain=plain,
        firecrawl=paid,
        budget=fallback.MonthlyBudget(paid.allowance, 0, 0),
    )
    assert plain.fetched == [PLAN]
    assert [json.loads(c.content)["url"] for c in calls] == [PLAN]


@pytest.mark.parametrize("allowance", [0, 1, 2])
def test_fallback_stops_before_the_next_call_exceeds_the_monthly_allowance(
    allowed_estate,
    tmp_path,
    allowance,
):
    root, _ = allowed_estate
    rendered = price_reread.RenderedReplayFetcher(artifact(tmp_path / "render"))
    paid, calls = scraper(allowance=allowance)
    fallback.fallback_to(
        root=root,
        rendered=rendered,
        directory=tmp_path / "fallback",
        month=MONTH,
        plain=ReplayFetcher({PLAN: [None], API: [None]}),
        firecrawl=paid,
        budget=fallback.MonthlyBudget(paid.allowance, 0, 0),
    )
    replay, spent = fallback.read_fallback(tmp_path / "fallback")
    assert len(calls) == spent == allowance
    assert len(replay.manifest) == allowance
    assert KEY not in (tmp_path / "fallback" / "manifest.json").read_text()


def test_spend_is_checkpointed_before_a_request_can_be_interrupted(allowed_estate, tmp_path):
    root, _ = allowed_estate
    directory = tmp_path / "fallback"

    def interrupted(_):
        manifest = json.loads((directory / "manifest.json").read_text())
        assert manifest["credits_spent"] == 1
        assert manifest["pages"][HELP]["error"] == "Firecrawl attempt interrupted"
        raise KeyboardInterrupt

    paid, _ = scraper(handler=interrupted)
    with pytest.raises(KeyboardInterrupt):
        fallback.fallback_to(
            root=root,
            rendered=price_reread.RenderedReplayFetcher(artifact(tmp_path / "render")),
            directory=directory,
            month=MONTH,
            plain=ReplayFetcher({PLAN: [b"ok"], API: [b"ok"]}),
            firecrawl=paid,
            budget=fallback.MonthlyBudget(paid.allowance, 0, 0),
        )
    _, spent = fallback.read_fallback(directory)
    assert spent == 1


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
def test_replay_keeps_successful_primary_html_and_only_replaces_failure(tmp_path, primary_ok):
    replay, _ = fallback.read_fallback(artifact(tmp_path, fallback_manifest=True, ok=True))
    primary = ReplayFetcher({HELP: [b"primary HTML" if primary_ok else None]})
    result = fallback.FallbackFetcher(primary, replay).fetch(HELP)
    assert result.body == (b"primary HTML" if primary_ok else page("plans.html"))
    assert primary.fetched == [HELP]


def test_fallback_artifact_reuses_the_render_validator(tmp_path):
    directory = artifact(tmp_path, fallback_manifest=True, ok=True)
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
    paid = artifact(tmp_path / "fallback", fallback_manifest=True, ok=True)
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
    assert "Firecrawl fallback: credits reserved/used=1" in capsys.readouterr().out


def test_cli_fallback_writes_only_an_artifact_and_redacts_error_responses(
    allowed_estate,
    tmp_path,
    monkeypatch,
    capsys,
    caplog,
):
    root, _ = allowed_estate
    rendered = artifact(tmp_path / "render")
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    artifact(ledger / "known", urls=tuple(f"{PLAN}{n}" for n in range(7)), fallback_manifest=True)
    (ledger / "unreadable").mkdir()
    summary = tmp_path / "step-summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    paid, calls = scraper(response={"success": False, "error": KEY})
    monkeypatch.setattr(price_reread, "ROOT", root)
    monkeypatch.setattr(
        price_reread, "Fetcher", lambda **_: ReplayFetcher({PLAN: [None], API: [None]})
    )
    monkeypatch.setattr(firecrawl, "FirecrawlFetcher", lambda **_: paid)

    def forbidden(*_, **__):
        pytest.fail("fallback mode must not construct a browser/store or run verification")

    monkeypatch.setattr(price_reread, "RenderedFetcher", forbidden)
    monkeypatch.setattr(price_reread, "CopyStore", forbidden)
    monkeypatch.setattr(price_reread, "run", forbidden)
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    output = tmp_path / "fallback"
    assert (
        price_reread.main(
            [
                "--fallback-from-render",
                str(rendered),
                "--fallback-to",
                str(output),
                "--fallback-ledger",
                str(ledger),
            ]
        )
        == 0
    )
    assert len(calls) == 3
    manifest = (output / "manifest.json").read_text()
    assert json.loads(manifest)["credits_spent"] == 3
    assert json.loads(manifest)["credits_reserved"] == 3
    assert json.loads(manifest)["allowance"] == 12
    assert json.loads(manifest)["prior_month_spend_known"] == 7
    assert json.loads(manifest)["unreadable_ledgers"] == 1
    assert json.loads(manifest)["team_balance"] == 1000
    assert summary.read_text() == (
        "Firecrawl fallback: credits reserved/used=3; allowance=12; prior month spend known=7; "
        "unreadable ledgers=1; team balance=1000.\n"
    )
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
    captured = capsys.readouterr()
    assert KEY not in manifest + summary.read_text() + captured.out + captured.err + caplog.text


def test_cli_validates_the_render_artifact_before_constructing_a_paid_fetcher(
    tmp_path, monkeypatch
):
    (tmp_path / "manifest.json").write_text("[]")

    def forbidden(**_):
        pytest.fail("an invalid rendered manifest must fail before configuring Firecrawl")

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
        else "Fetch only failed eligible pages"
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
    if fake:
        assert "secrets." not in json.dumps(step)


def test_workflow_is_off_by_default_retains_a_full_month_and_replays_when_skipped():
    jobs = workflow()["jobs"]
    assert "vars.PRICE_REREAD_FIRECRAWL == 'true'" in jobs["fallback"]["if"]
    assert "github.ref == 'refs/heads/main'" in jobs["fallback"]["if"]
    assert "github.run_attempt == 1" in jobs["fallback"]["if"]
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
    assert "FIRECRAWL" not in json.dumps(jobs["reread"])
    triggers = workflow()["on"]
    assert triggers["workflow_dispatch"]["inputs"]["fallback_fake"] == {
        "description": "Run the isolated fallback demo with fake HTML, zero credits and no key",
        "type": "boolean",
        "default": False,
    }


@pytest.mark.parametrize(
    "event,gate,attempt,fake,ref,job_runs,paid_runs,fake_runs",
    [
        ("schedule", "true", 1, False, "main", True, True, False),
        ("schedule", "false", 1, False, "main", False, False, False),
        ("schedule", "true", 2, False, "main", False, False, False),
        ("schedule", "true", 1, False, "other", False, False, False),
        ("workflow_dispatch", "true", 1, False, "main", False, False, False),
        ("workflow_dispatch", "false", 1, False, "main", False, False, False),
        ("workflow_dispatch", "false", 1, True, "main", True, False, True),
        ("workflow_dispatch", "true", 1, True, "main", True, False, True),
        ("workflow_dispatch", "false", 2, True, "main", True, False, True),
        ("workflow_dispatch", "true", 1, True, "other", False, False, False),
        ("pull_request", "true", 1, True, "main", False, False, False),
    ],
)
def test_workflow_spends_only_on_schedule_and_allows_a_keyless_ungated_demo(
    event, gate, attempt, fake, ref, job_runs, paid_runs, fake_runs
):
    job = workflow()["jobs"]["fallback"]
    context = {
        "github": SimpleNamespace(event_name=event, run_attempt=attempt, ref=f"refs/heads/{ref}"),
        "vars": SimpleNamespace(PRICE_REREAD_FIRECRAWL=gate),
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
    paid = next(s for s in job["steps"] if s.get("name") == "Fetch only failed eligible pages")
    demo = next(
        s
        for s in job["steps"]
        if s.get("name") == "Fake fallback demo without credentials or network"
    )
    assert (runs and permits(paid["if"])) is paid_runs
    assert (runs and permits(demo["if"])) is fake_runs
    assert "env" not in demo


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
        assert body == firecrawl.FakeFirecrawlFetcher().fetch(url).body
    assert summary.read_text() == replay.spend_line + "\n"
    assert "FAKE: credits reserved/used=0; allowance=0" in replay.spend_line
    assert "team balance=unread" in replay.spend_line
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


def test_failed_monthly_lookup_stops_the_workflow_step(tmp_path):
    step = next(
        s
        for s in workflow()["jobs"]["fallback"]["steps"]
        if s.get("name") == "Restore this UTC month's fallback ledger"
    )
    script = "gh() { return 7; }\n" + step["run"]
    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        env={
            **os.environ,
            "RUNNER_TEMP": str(tmp_path),
            "REPO": "fixture/repo",
            "WORKFLOW_FILE": "price-reread.yml",
            "CURRENT_RUN_ID": "99",
        },
    )
    assert result.returncode == 7


AWS_PRICING = "https://aws.amazon.com/bedrock/pricing/"


def test_a_fallback_around_a_replay_never_passes_a_preparation(tmp_path):
    """Run 38037233884: the AWS preparation reached FallbackFetcher(replay).fetch."""
    rendered = tmp_path / "rendered"
    rendered.mkdir()
    (rendered / "aws.html").write_bytes(b"<html><body>captured</body></html>")
    (rendered / "manifest.json").write_text(json.dumps({AWS_PRICING: {
        "file": "aws.html", "outcome": "ok", "status": 200, "error": None}}))
    replay, _ = fallback.read_fallback(artifact(tmp_path, fallback_manifest=True, ok=True))
    wrapped = fallback.FallbackFetcher(price_reread.RenderedReplayFetcher(rendered), replay)
    result = price_reread._fetch_rendered(wrapped, AWS_PRICING, ("aws-pricing",))
    assert (result.outcome, result.body) == ("ok", b"<html><body>captured</body></html>")


def test_a_fallback_around_a_live_renderer_keeps_the_preparation(tmp_path):
    class LiveRenderer(price_reread.RenderedFetcher):
        def __init__(self):
            self.prepared = []

        def fetch(self, url, *, prepare=None):
            self.prepared.append(prepare)
            return FetchResult("ok", 200, body=b"live", content_type="text/html")

    live = LiveRenderer()
    replay, _ = fallback.read_fallback(artifact(tmp_path, fallback_manifest=True, ok=True))
    result = price_reread._fetch_rendered(fallback.FallbackFetcher(live, replay),
                                          AWS_PRICING, ("aws-pricing",))
    assert result.body == b"live"
    assert live.prepared == [price_reread.RENDERED_PREPARATIONS["aws-pricing"]]
