"""Firecrawl fetch path: credit budget is enforced in code, markdown is default."""

from __future__ import annotations

import json
from contextlib import contextmanager
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


class _FirecrawlMock:
    """Credit-usage GET plus scrape POST. Decrements remaining only on POST.

    `metadata` (and `spend_on_scrape`) are read fresh on every POST, so a
    test can mutate them between two `scrape()` calls on the same mock to
    simulate the document's real size changing (or becoming knowable) on a
    second attempt -- e.g. a low-budget truncated fetch followed by a
    higher-budget one that gets the whole document.
    """

    def __init__(
        self,
        remaining: int,
        *,
        spend_on_scrape: int = 1,
        metadata: dict | None = None,
    ) -> None:
        self.remaining = remaining
        self.spend_on_scrape = spend_on_scrape
        self.metadata = metadata
        self.posts: list[dict] = []

    def urlopen(self, req, timeout=30):
        url = req.full_url
        if "credit-usage" in url:
            return _FakeResp(_credit_payload(self.remaining))
        if req.get_method() == "POST":
            body = json.loads(req.data.decode()) if req.data else {}
            self.posts.append(body)
            self.remaining -= self.spend_on_scrape
            data: dict = {"markdown": "ok"}
            if self.metadata is not None:
                data["metadata"] = self.metadata
            return _FakeResp({"success": True, "data": data})
        raise AssertionError(f"unexpected {req.get_method()} {url}")


@contextmanager
def _scrape_harness(tmp_path: Path, mock: _FirecrawlMock):
    with (
        patch("scripts.benchmarks.fetch.HASH_CACHE", tmp_path / "hash"),
        patch("scripts.benchmarks.fetch.resolve_key", return_value="sk-test"),
        patch("scripts.benchmarks.fetch.urllib.request.urlopen", side_effect=mock.urlopen),
    ):
        yield mock


def test_pdf_worst_case_over_budget_is_not_sent(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        with pytest.raises(CreditBudgetExceeded) as exc:
            scrape(
                "https://example.com/cerebras-datasheet.pdf",
                guard=guard,
                max_pages=13,
                named_cache_dir=tmp_path / "raw",
            )
    assert mock.posts == []
    assert exc.value.spent == 0
    assert exc.value.budget == 10


def test_pdf_within_budget_is_sent_with_page_cap(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/short.pdf",
            guard=guard,
            max_pages=5,
            named_cache_dir=tmp_path / "raw",
        )
    assert len(mock.posts) == 1
    parser = mock.posts[0]["parsers"][0]
    assert parser["type"] == "pdf"
    assert parser["maxPages"] == 5


def test_pdf_defaults_to_capping_pages_at_remaining_budget(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/doc.pdf",
            guard=guard,
            named_cache_dir=tmp_path / "raw",
        )
    assert mock.posts[0]["parsers"][0]["maxPages"] == 10


def test_html_scrape_within_budget_proceeds(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=50)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=1)
        guard.start()
        scrape(
            "https://example.com/board",
            guard=guard,
            named_cache_dir=tmp_path / "raw",
        )
    assert len(mock.posts) == 1


def test_per_request_cost_is_recorded_from_balance_delta(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=3)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/page",
            guard=guard,
            named_cache_dir=tmp_path / "raw",
        )
    assert guard.last_request_cost == 3
    assert guard.request_costs[-1] == ("https://example.com/page", 3)


def test_unbounded_pdf_requires_opt_in_and_omits_page_cap(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=13)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/long.pdf",
            guard=guard,
            allow_unbounded=True,
            named_cache_dir=tmp_path / "raw",
        )
    assert len(mock.posts) == 1
    parsers = mock.posts[0].get("parsers") or []
    assert all("maxPages" not in (p if isinstance(p, dict) else {}) for p in parsers)
    assert guard.last_request_cost == 13


def test_expensive_formats_still_refused_on_pdf_path(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=20)
        guard.start()
        with pytest.raises(ValueError, match="expensive"):
            scrape(
                "https://example.com/doc.pdf",
                formats=["json"],
                guard=guard,
                max_pages=2,
                named_cache_dir=tmp_path / "raw",
            )
    assert mock.posts == []


def test_budget_already_spent_refuses_even_unbounded_opt_in(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        mock.remaining = 90  # budget fully spent by earlier requests
        for kwargs in ({}, {"allow_unbounded": True}):
            with pytest.raises(CreditBudgetExceeded):
                scrape(
                    "https://example.com/next.pdf",
                    guard=guard,
                    named_cache_dir=tmp_path / "raw",
                    **kwargs,
                )
    assert mock.posts == []


def test_page_cap_shrinks_as_budget_is_spent(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=7)
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape("https://example.com/a.pdf", guard=guard, named_cache_dir=tmp_path / "raw")
        scrape("https://example.com/b.pdf", guard=guard, named_cache_dir=tmp_path / "raw")
    assert [p["parsers"][0]["maxPages"] for p in mock.posts] == [10, 3]


def test_per_request_spend_is_written_to_cache_metadata(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=4)
    raw = tmp_path / "raw"
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape("https://example.com/four-pages.pdf", guard=guard, named_cache_dir=raw)
    cached = load_named_cache("https://example.com/four-pages.pdf", raw)
    assert cached is not None
    assert cached.meta["credits_spent"] == 4
    assert cached.meta["credits_remaining_before"] == 100
    assert cached.meta["credits_remaining_after"] == 96
    assert cached.meta["max_pages"] == 10


def test_hash_cache_hit_needs_no_key_and_no_network(tmp_path: Path) -> None:
    import hashlib

    hash_dir = tmp_path / "hash"
    hash_dir.mkdir()
    url, formats = "https://example.com/cached.pdf", ["markdown"]
    # Pre-page-cap cache key: url|formats. Existing cached responses must still hit.
    digest = hashlib.sha256((url + "|" + ",".join(formats)).encode()).hexdigest()[:24]
    (hash_dir / f"{digest}.json").write_text(json.dumps({"markdown": "cached"}))
    with (
        patch("scripts.benchmarks.fetch.HASH_CACHE", hash_dir),
        patch("scripts.benchmarks.fetch.resolve_key", return_value=None),
        patch("scripts.benchmarks.fetch.urllib.request.urlopen") as mocked,
    ):
        data = scrape(url, formats=formats)
    mocked.assert_not_called()
    assert data["markdown"] == "cached"


def test_pdf_truncated_by_metadata_is_flagged_and_warns(tmp_path: Path, capsys) -> None:
    # Firecrawl's own metadata.totalPages > metadata.numPages says outright
    # that a 30-page document was cut down to the 10 pages we paid for.
    mock = _FirecrawlMock(
        remaining=100, spend_on_scrape=10, metadata={"numPages": 10, "totalPages": 30}
    )
    raw = tmp_path / "raw"
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape("https://example.com/big.pdf", guard=guard, named_cache_dir=raw)
    cached = load_named_cache("https://example.com/big.pdf", raw)
    assert cached is not None
    assert cached.meta["truncated"] is True
    assert cached.meta["num_pages"] == 10
    assert cached.meta["total_pages"] == 30
    assert "truncated" in capsys.readouterr().err.lower()


def test_pdf_fully_parsed_is_not_flagged_truncated_even_at_the_cap(tmp_path: Path) -> None:
    # totalPages == numPages: the document just happens to be exactly as
    # long as the cap, not longer. Metadata overrides the cost heuristic.
    mock = _FirecrawlMock(
        remaining=100, spend_on_scrape=5, metadata={"numPages": 5, "totalPages": 5}
    )
    raw = tmp_path / "raw"
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/exactly-five.pdf",
            guard=guard,
            max_pages=5,
            named_cache_dir=raw,
        )
    cached = load_named_cache("https://example.com/exactly-five.pdf", raw)
    assert cached is not None
    assert cached.meta["truncated"] is False


def test_pdf_truncation_falls_back_to_cost_heuristic_without_metadata(tmp_path: Path) -> None:
    # Firecrawl omits numPages/totalPages ("omitted when it cannot be
    # determined"); a PDF billed at its own page cap is treated as possibly
    # truncated rather than silently assumed complete.
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=10)
    raw = tmp_path / "raw"
    with _scrape_harness(tmp_path, mock):
        guard = CreditGuard(key="sk-test", budget=10)
        guard.start()
        scrape(
            "https://example.com/opaque.pdf",
            guard=guard,
            max_pages=10,
            named_cache_dir=raw,
        )
    cached = load_named_cache("https://example.com/opaque.pdf", raw)
    assert cached is not None
    assert cached.meta["truncated"] is True
    assert cached.meta["num_pages"] is None
    assert cached.meta["total_pages"] is None


def test_truncated_pdf_is_not_replayed_from_cache_once_budget_grows(tmp_path: Path) -> None:
    mock = _FirecrawlMock(remaining=100, spend_on_scrape=10)
    raw = tmp_path / "raw"
    url = "https://example.com/big-datasheet.pdf"

    with _scrape_harness(tmp_path, mock):
        low_guard = CreditGuard(key="sk-test", budget=10)
        low_guard.start()
        scrape(url, guard=low_guard, named_cache_dir=raw)
    assert len(mock.posts) == 1
    assert mock.posts[0]["parsers"][0]["maxPages"] == 10
    cached = load_named_cache(url, raw)
    assert cached is not None
    assert cached.meta["truncated"] is True

    # Same URL, much larger budget, and the document turns out to need only
    # 12 pages -- the whole thing fits well under the new cap.
    mock.spend_on_scrape = 12
    mock.metadata = {"numPages": 12, "totalPages": 12}
    with _scrape_harness(tmp_path, mock):
        high_guard = CreditGuard(key="sk-test", budget=50)
        high_guard.start()
        second = scrape(url, guard=high_guard, named_cache_dir=raw)

    # The truncated copy was not served from either cache -- a second real
    # request went out.
    assert len(mock.posts) == 2
    assert second["markdown"] == "ok"
    cached_after = load_named_cache(url, raw)
    assert cached_after is not None
    assert cached_after.meta["truncated"] is False
    assert cached_after.meta["num_pages"] == 12
