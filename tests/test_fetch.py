"""Firecrawl fetch path: credit budget is enforced in code, markdown is default."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.benchmarks.fetch import (
    DEFAULT_BUDGET,
    CachedPage,
    CreditBudgetExceeded,
    CreditGuard,
    load_named_cache,
    refuse_expensive_formats,
    remaining_credits,
    scrape,
    write_named_cache,
)


def _credit_payload(remaining: int) -> dict:
    return {"success": True, "data": {"remainingCredits": remaining, "planCredits": 5000}}


class _FakeResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return json.dumps(self._payload).encode()


def test_default_budget_is_conservative() -> None:
    assert DEFAULT_BUDGET <= 50


def test_expensive_formats_are_refused() -> None:
    with pytest.raises(ValueError, match="expensive"):
        refuse_expensive_formats(["json"])
    with pytest.raises(ValueError, match="expensive"):
        refuse_expensive_formats(["markdown", "highlight"])
    refuse_expensive_formats(["markdown"])
    refuse_expensive_formats(["markdown", "links"])


def test_remaining_credits_reads_v2_team_endpoint() -> None:
    captured: dict[str, str] = {}

    def fake_urlopen(req, timeout=30):
        captured["url"] = req.full_url
        captured["auth"] = req.get_header("Authorization") or req.headers.get("Authorization")
        return _FakeResp(_credit_payload(5569))

    # urllib.request.urlopen is used; Request stores headers with header_items
    with patch("scripts.benchmarks.fetch.urllib.request.urlopen", side_effect=fake_urlopen):
        assert remaining_credits("sk-test") == 5569
    assert captured["url"] == "https://api.firecrawl.dev/v2/team/credit-usage"


def test_guard_aborts_when_spend_reaches_budget() -> None:
    remaining = {"n": 100}

    def fake_remaining(_key: str) -> int:
        return remaining["n"]

    with patch("scripts.benchmarks.fetch.remaining_credits", side_effect=fake_remaining):
        guard = CreditGuard(key="sk-test", budget=2)
        guard.start()
        remaining["n"] = 99  # spent 1
        guard.assert_within_budget(url="https://example.com/a")
        remaining["n"] = 98  # spent 2 == budget
        with pytest.raises(CreditBudgetExceeded) as exc:
            guard.assert_within_budget(url="https://example.com/b")
        assert exc.value.spent == 2
        assert exc.value.budget == 2
        assert exc.value.opening == 100


def test_guard_aborts_before_a_scrape_that_would_cross_the_budget() -> None:
    remaining = {"n": 50}

    def fake_remaining(_key: str) -> int:
        return remaining["n"]

    with patch("scripts.benchmarks.fetch.remaining_credits", side_effect=fake_remaining):
        guard = CreditGuard(key="sk-test", budget=1)
        guard.start()
        remaining["n"] = 49
        with pytest.raises(CreditBudgetExceeded):
            guard.assert_within_budget(estimated=1)


def test_named_cache_preserves_observation_date(tmp_path: Path) -> None:
    page = write_named_cache(
        "https://example.com/board",
        "# hello",
        tmp_path,
        fetched_at="2026-09-01",
        extra_meta={"fetcher": "http_get"},
    )
    loaded = load_named_cache("https://example.com/board", tmp_path)
    assert loaded is not None
    assert loaded.from_cache
    assert loaded.observation_date == "2026-09-01"
    assert loaded.text == "# hello"
    assert page.fetched_at == "2026-09-01"


def test_scrape_does_not_call_firecrawl_when_named_cache_exists(tmp_path: Path) -> None:
    write_named_cache(
        "https://example.com/board",
        "cached markdown",
        tmp_path,
        fetched_at="2026-09-02",
    )
    with patch("scripts.benchmarks.fetch.urllib.request.urlopen") as mocked:
        data = scrape("https://example.com/board", named_cache_dir=tmp_path)
    mocked.assert_not_called()
    assert data["markdown"] == "cached markdown"
    assert data["fetched_at"] == "2026-09-02"


def test_scrape_refuses_json_format_by_default() -> None:
    with pytest.raises(ValueError, match="expensive"):
        scrape("https://example.com", formats=["json"])
