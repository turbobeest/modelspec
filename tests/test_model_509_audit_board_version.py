"""The trust audit compares a Terminal-Bench claim only with the board its field names (MODEL-509)."""

from __future__ import annotations

from datetime import date

import pytest

from scripts.data_trust import sample

TODAY = date(2026, 11, 19)


@pytest.mark.parametrize("row, reason", [
    ({"field": "terminal_bench_v4_0"}, "board no longer published"),
    ({"field": "terminal_bench_v4_1", "not_published_since": "2026-10-01"}, "not_published_since"),
    ({"field": "terminal_bench_v4_0", "not_published_since": "2026-10-01"}, "not_published_since"),
    ({"field": "terminal_bench_v3"}, "board version not named by an audited field"),
    ({"field": "terminal_bench_v4_1"}, None),
    ({"field": "terminal_bench_v4_1", "not_published_since": None}, None),
    ({"field": "swe_bench_verified"}, None),
])
def test_unauditable(row, reason) -> None:
    assert sample.unauditable(row) == reason


def test_a_skipped_row_is_never_fetched_and_is_named_in_the_report() -> None:
    class Catalogue:
        facts = [
            {"id": "m1", "field": "terminal_bench_v4_0", "kind": "evidence", "provider": "p"},
            {"id": "m2", "field": "terminal_bench_v4_1", "kind": "evidence", "provider": "p",
             "not_published_since": "2026-10-01"},
        ]

    class Fetcher:
        def fetch(self, url):
            pytest.fail("a skipped row reached HTTP")

    outcomes = [sample.reread(f, Catalogue, None, Fetcher(), None, {}, TODAY) for f in Catalogue.facts]
    assert outcomes == [("skipped", "board no longer published"), ("skipped", "not_published_since")]
