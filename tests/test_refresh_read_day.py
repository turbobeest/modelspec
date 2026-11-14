"""A read day beside an unchanged publish date is retold, so the row can be re-confirmed (MODEL-486-B).

Invented rows, scores and dates. No network.
"""

from __future__ import annotations

from pathlib import Path

from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import _arena_guard_card, _guard_result

PUBLISH = "2026-11-02"
STALE = "configuration still quotes the previous reading"


def _row(configuration: str, *, observed_at: str, score: float = 1234.5) -> dict:
    return {
        "score": score,
        "interval": [1210.0, 1250.0],
        "n": 2222,
        "effort": None,
        "model_id_as_evaluated": "Example Model",
        "evidence_date": PUBLISH,
        "observed_at": observed_at,
        "verified_at": observed_at,
        "configuration": configuration,
        "benchmark_version": "text / overall",
    }


def _sentence(read: str, *, rank: int = 3, votes: int = 2222, lo: str = "1210.00",
              hi: str = "1250.00", publish: str = PUBLISH, tail: str = "") -> str:
    return (
        "LMArena leaderboard dataset, CC BY 4.0, category overall, "
        f"leaderboard_publish_date {publish}, read {read}. "
        f"Rank {rank}, {votes} votes, interval [{lo}, {hi}].{tail}"
    )


def _observation(*, score: float = 1234.5, publish: str = PUBLISH, rank: int = 3,
                 votes: int = 2222, interval=(1210.0, 1250.0)):
    return refresh.RowObservation(
        card="lab/example", model_id="lab/example", model="Example Model",
        benchmark="arena_elo_overall", old_value=1234.5, new_value=score,
        source="fixture-arena", observed_date="x", evidence_date=publish,
        reading_interval=interval, reading_n=votes, reading_publish_date=publish,
        reading_revision="a" * 40, reading_checked=True, reading_rank=rank,
    )


def _run(old: dict, day: str, observation=None):
    return refresh._copy_matched_reading(
        old, observation or _observation(), observed_at=day,
    )


def _written(old: dict, day: str, observation=None) -> dict:
    new, reason = _run(old, day, observation)
    assert reason is None
    assert new is not None
    return {**new, "observed_at": day, "verified_at": day}


def test_a_row_the_last_run_wrote_is_reconfirmed_on_the_next_day() -> None:
    # Run 1 saw a new publish date: it wrote the read day and observed_at itself.
    old = _row(_sentence("2026-11-05", publish="2026-10-01"), observed_at="2026-10-01")
    first = _written(old, "2026-11-10")
    assert first["configuration"] == _sentence("2026-11-10")
    assert first["observed_at"] == "2026-11-10"

    second = _written(first, "2026-11-11")

    assert second["configuration"] == _sentence("2026-11-11")
    assert second["observed_at"] == "2026-11-11"
    assert {k: v for k, v in second.items() if k not in {"configuration", "observed_at", "verified_at"}} == {
        k: v for k, v in first.items() if k not in {"configuration", "observed_at", "verified_at"}
    }

    third = _written(
        second, "2026-11-12",
        _observation(score=1240.25, publish="2026-11-12", rank=2, votes=2300,
                     interval=(1215.0, 1262.0)),
    )
    assert third["score"] == 1240.25
    assert third["configuration"] == _sentence(
        "2026-11-12", rank=2, votes=2300, lo="1215.00", hi="1262.00", publish="2026-11-12",
    )


def test_the_same_day_twice_is_byte_identical() -> None:
    once = _written(_row(_sentence("2026-11-10"), observed_at="2026-11-10"), "2026-11-11")
    twice = _written(once, "2026-11-11")

    assert twice == once
    assert twice["configuration"] == _sentence("2026-11-11")


def test_no_read_clause_is_left_exactly_as_written() -> None:
    sentence = (
        "LMArena leaderboard dataset, category overall, leaderboard_publish_date "
        f"{PUBLISH}. Rank 3, 2222 votes, interval [1210.00, 1250.00]."
    )
    old = _row(sentence, observed_at="2026-11-10")
    new, reason = _run(old, "2026-11-11")

    assert reason is None
    assert new is not None
    assert new["configuration"] == sentence


def test_the_snapshot_sentence_stays_when_the_publish_date_is_unchanged() -> None:
    snapshot = (
        " The live arena.ai board read 2026-10-01 still shows this snapshot "
        "(same vote counts)."
    )
    old = _row(_sentence("2026-10-20", tail=snapshot), observed_at="2026-10-20")
    new, reason = _run(old, "2026-11-11")

    assert reason is None
    assert new is not None
    assert new["configuration"] == _sentence("2026-11-11", tail=snapshot)


def test_a_stored_day_quoted_outside_the_read_clause_is_still_refused() -> None:
    old = _row(
        _sentence("2026-11-10", tail=" Checked on 2026-11-10."), observed_at="2026-11-10",
    )
    new, reason = _run(old, "2026-11-11")

    assert new is None
    assert reason == STALE


def test_two_read_dates_only_the_one_beside_the_publish_date_is_retold() -> None:
    # The second read date is the stored observed_at, which the writer cannot retell.
    refused = _row(
        _sentence("2026-11-10", tail=" Earlier read 2026-11-10."), observed_at="2026-11-10",
    )
    assert _run(refused, "2026-11-11") == (None, STALE)

    # The second read date is some other day: it stays as written.
    kept = _row(
        _sentence("2026-11-10", tail=" Earlier read 2026-10-01."), observed_at="2026-11-10",
    )
    new, reason = _run(kept, "2026-11-11")
    assert reason is None
    assert new is not None
    assert new["configuration"] == _sentence("2026-11-11", tail=" Earlier read 2026-10-01.")


def test_the_score_only_guard_accepts_the_retold_read_day(tmp_path: Path) -> None:
    before_text = _arena_guard_card("2026-11-12").replace(
        "evidence_date: '2026-09-01'", f"evidence_date: '{PUBLISH}'",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n"
        f"    configuration: leaderboard_publish_date {PUBLISH}, read 2026-11-12. "
        "Rank 3, 2222 votes.\n",
    )
    after_text = before_text.replace("read 2026-11-12", "read 2026-11-13").replace(
        "observed_at: '2026-11-12'", "observed_at: '2026-11-13'",
    ).replace("verified_at: '2026-11-12'", "verified_at: '2026-11-13'")
    assert after_text != before_text

    assert _guard_result(tmp_path, before_text, after_text).ok
