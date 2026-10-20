"""The admission fallback spends only against a durable, capped monthly ledger."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import httpx
import pytest

from decision.firecrawl import FirecrawlFetcher
from decision.sources import FetchResult, fingerprint_bytes
from scripts.admission_fallback import AdmissionFallback
from scripts.price_reread_fallback import monthly_budget, read_fallback

MONTH = "2026-10"
URL = "https://help.openai.com/en/articles/admission-fixture"
BODY = b"<html><body>admission-fallback-private-fixture</body></html>"


class Primary:
    def __init__(self, result=None):
        self.result = result or FetchResult("unreachable", 403, error="HTTP 403")

    def fetch(self, url):
        return self.result


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / MONTH
    path.mkdir()
    return path


@pytest.fixture
def paid_factory(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-fixture-no-network")

    def make(*, handler=None, body=BODY, redirects=()):
        paid_calls = []

        def serve(request):
            if request.url.path == "/v2/team/credit-usage":
                return httpx.Response(
                    200, json={"success": True, "data": {"remainingCredits": 1000}}
                )
            paid_calls.append(request)
            if handler is not None:
                return handler(request)
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "data": {
                        "rawHtml": body.decode(),
                        "metadata": {"statusCode": 200, "resolved_urls": list(redirects)},
                    },
                },
            )

        def factory(*, allowance):
            return FirecrawlFetcher(allowance=allowance, transport=httpx.MockTransport(serve))

        return factory, paid_calls

    return make


def history(ledger, spent):
    """Create valid prior-run artifacts without any retained source bodies."""
    for index, start in enumerate(range(0, spent, 12)):
        credits = min(12, spent - start)
        directory = ledger / f"previous-{index}"
        directory.mkdir()
        pages = {
            f"https://help.openai.com/prior/{index}/{number}": {
                "file": f"page-{number}.html",
                "outcome": "unreachable",
                "status": None,
                "error": "Historical reservation",
            }
            for number in range(credits)
        }
        (directory / "manifest.json").write_text(
            json.dumps(
                {"schema_version": 1, "month": MONTH, "credits_spent": credits, "pages": pages}
            )
        )


def test_monthly_cap_is_fifty_across_separate_invocations(ledger, paid_factory):
    history(ledger, 47)
    factory, calls = paid_factory()
    outcomes = [
        AdmissionFallback(Primary(), ledger, month=MONTH, firecrawl_factory=factory).fetch(URL)
        for _ in range(4)
    ]
    assert [result.outcome for result in outcomes] == ["ok", "ok", "ok", "unreachable"]
    assert "50" in outcomes[-1].error
    assert len(calls) == 3
    budget = monthly_budget(ledger, MONTH)
    assert budget.known_spend == 50 and budget.unreadable_ledgers == 0


def test_missing_ledger_fails_closed_without_creating_it(tmp_path, paid_factory):
    missing = tmp_path / "not-restored"
    factory, calls = paid_factory()
    result = AdmissionFallback(
        Primary(), missing, month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result.outcome == "unreachable" and "ledger" in result.error
    assert calls == [] and not missing.exists()


def test_unreadable_prior_runs_each_reserve_twelve_credits(ledger, paid_factory):
    for number in range(4):
        (ledger / f"unreadable-{number}").mkdir()
    factory, calls = paid_factory()
    fetcher = AdmissionFallback(Primary(), ledger, month=MONTH, firecrawl_factory=factory)
    assert fetcher.fetch(URL).outcome == "ok"
    assert fetcher.fetch(URL).outcome == "ok"
    assert fetcher.fetch(URL).outcome == "unreachable"
    assert len(calls) == 2
    budget = monthly_budget(ledger, MONTH)
    assert budget.known_spend == 2 and budget.unreadable_ledgers == 4


def test_paid_failure_keeps_durable_reservation(ledger, paid_factory):
    def fail(request):
        budget = monthly_budget(ledger, MONTH)
        assert budget.known_spend == 1 and budget.unreadable_ledgers == 0
        return httpx.Response(503)

    factory, calls = paid_factory(handler=fail)
    result = AdmissionFallback(
        Primary(), ledger, month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result.outcome == "unreachable" and len(calls) == 1
    assert monthly_budget(ledger, MONTH).known_spend == 1
    assert all(BODY not in path.read_bytes() for path in ledger.rglob("*") if path.is_file())


def test_interrupted_request_still_has_readable_spend(ledger, paid_factory):
    def interrupt(request):
        assert monthly_budget(ledger, MONTH).known_spend == 1
        raise KeyboardInterrupt("fixture interruption")

    factory, calls = paid_factory(handler=interrupt)
    with pytest.raises(KeyboardInterrupt, match="fixture interruption"):
        AdmissionFallback(Primary(), ledger, month=MONTH, firecrawl_factory=factory).fetch(URL)
    assert len(calls) == 1
    [directory] = list(ledger.iterdir())
    _, spent = read_fallback(directory, month=MONTH)
    assert spent == 1


def test_successful_primary_never_uses_paid_fetch_or_ledger(tmp_path, paid_factory):
    factory, calls = paid_factory()
    expected = FetchResult("ok", 200, body=BODY)
    result = AdmissionFallback(
        Primary(expected), tmp_path / "missing", month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result == expected and calls == []


@pytest.mark.parametrize(
    "url",
    [
        "https://unlisted.help.openai.com/page",
        "https://help.openai.com.example/page",
        "https://example.com@help.openai.com/page",
        "https://help.openai.com:8443/page",
        "https://artificial" "analysis.ai/page",
        "https://zap" "ier.com/page",
        "https://perplexity.ai/page",
    ],
)
def test_unapproved_hosts_never_spend(ledger, paid_factory, url):
    factory, calls = paid_factory()
    result = AdmissionFallback(
        Primary(), ledger, month=MONTH, firecrawl_factory=factory
    ).fetch(url)
    assert result.outcome == "unreachable"
    assert calls == [] and list(ledger.iterdir()) == []


def test_excluded_redirect_never_triggers_paid_retry(ledger, paid_factory):
    factory, calls = paid_factory()
    primary = Primary(
        FetchResult("ok", 200, body=BODY, resolved_urls=("https://zap" "ier.com/page",))
    )
    result = AdmissionFallback(
        primary, ledger, month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result.outcome == "unreachable" and result.body == b""
    assert calls == [] and list(ledger.iterdir()) == []


def test_missing_credential_does_not_reserve_credits(ledger, paid_factory, monkeypatch):
    factory, calls = paid_factory()
    monkeypatch.delenv("FIRECRAWL_API_KEY")
    result = AdmissionFallback(
        Primary(), ledger, month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result.outcome == "unreachable" and calls == []
    assert monthly_budget(ledger, MONTH).known_spend == 0
    assert list(ledger.iterdir()) == []


@pytest.mark.parametrize("paid", [False, True])
def test_cite_only_response_has_hash_and_no_page_bytes(ledger, paid_factory, paid):
    restricted = "https://docs.x.ai/models/admission-fixture"
    factory, calls = paid_factory(redirects=(restricted,))
    primary = Primary() if paid else Primary(
        FetchResult("ok", 200, body=BODY, resolved_urls=(restricted,))
    )
    result = AdmissionFallback(
        primary, ledger, month=MONTH, firecrawl_factory=factory
    ).fetch(restricted)
    assert result.outcome == "ok" and result.body == b""
    assert result.snapshot_ref == fingerprint_bytes(BODY)
    assert result.retrieved_at is not None
    assert len(calls) == int(paid)
    assert all(BODY not in path.read_bytes() for path in ledger.rglob("*") if path.is_file())
    if paid:
        [directory] = list(ledger.iterdir())
        _, spent = read_fallback(directory, month=MONTH)
        assert spent == 1


def test_concurrent_fetches_cannot_both_take_last_credit(ledger, paid_factory):
    history(ledger, 49)
    ready = Barrier(2)

    class ConcurrentPrimary:
        def fetch(self, url):
            ready.wait(timeout=5)
            return FetchResult("unreachable", 403)

    factory, calls = paid_factory()

    def fetch():
        return AdmissionFallback(
            ConcurrentPrimary(), ledger, month=MONTH, firecrawl_factory=factory
        ).fetch(URL)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: fetch(), range(2)))
    assert sorted(result.outcome for result in results) == ["ok", "unreachable"]
    assert len(calls) == 1
    assert monthly_budget(ledger, MONTH).known_spend == 50


def test_ledger_symlink_fails_closed(tmp_path, ledger, paid_factory):
    linked = tmp_path / "linked"
    linked.symlink_to(ledger, target_is_directory=True)
    factory, calls = paid_factory()
    result = AdmissionFallback(
        Primary(), linked, month=MONTH, firecrawl_factory=factory
    ).fetch(URL)
    assert result.outcome == "unreachable" and calls == []


def test_invalid_month_is_rejected(ledger):
    with pytest.raises(ValueError, match="month"):
        AdmissionFallback(Primary(), ledger, month="2026-13")
