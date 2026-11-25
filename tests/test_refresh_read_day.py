"""A read day beside an unchanged publish date is retold, so the row can be re-confirmed (MODEL-486-B).

Invented rows, scores and dates. No network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import _arena_guard_card, _card, _guard_result



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


# MODEL-505: every board retells its one read day; renamed-effort rows are named.

EPOCH = ("Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (x.csv), "
         "read 2026-09-24. Run started 2026-08-14T18:29:12.000Z; effort high.")
SCALE = "Scale Labs leaderboard entry read 2026-09-25; entry created 2026-04-08; effort thinking."
SWEBENCH = "Official SWE-bench leaderboard (swebench.com), Verified board, read 2026-09-25. Agent X."
DAY = "2026-11-19"


def _observation_505(score: float = 50.0):
    return refresh.RowObservation(
        card="lab/example", model_id="lab/example", model="Example", benchmark="b",
        old_value=50.0, new_value=score, source="fixture", observed_date=DAY,
        evidence_date="2026-08-14",
    )


def _old_505(configuration: str) -> dict:
    return {"score": 50.0, "configuration": configuration, "evidence_date": "2026-08-14",
            "observed_at": "2026-11-16", "model_id_as_evaluated": "Example"}


@pytest.mark.parametrize("text,was", [(EPOCH, "2026-09-24"), (SCALE, "2026-09-25"),
                                      (SWEBENCH, "2026-09-25")])
def test_the_one_read_day_is_retold_and_nothing_else_moves(text, was) -> None:
    new, reason = refresh._copy_matched_reading(_old_505(text), _observation_505(), observed_at=DAY)
    assert reason is None
    assert new["configuration"] == text.replace(f"read {was}", f"read {DAY}")


def test_same_day_twice_is_identical() -> None:
    once, _ = refresh._copy_matched_reading(_old_505(EPOCH), _observation_505(), observed_at=DAY)
    twice, _ = refresh._copy_matched_reading(once, _observation_505(), observed_at=DAY)
    assert once == twice


@pytest.mark.parametrize("text", [
    "No day here. Run started 2026-08-14.",
    "re-read 2026-09-24 of the page.",
    "page read 2026-09-24 and page read 2026-09-25.",
])
def test_no_read_or_two_reads_stay_as_written(text) -> None:
    new, _ = refresh._copy_matched_reading(_old_505(text), _observation_505(), observed_at=DAY)
    assert new["configuration"] == text


def _guard_pair(after_config_day: str) -> tuple[str, str]:
    before = _card("2026-09-24").replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: Board entry read 2026-09-25; entry created 2026-04-08.\n",
    )
    after = _card("2026-11-19").replace(
        "    date_type: published\n",
        "    date_type: published\n"
        f"    configuration: Board entry read {after_config_day}; entry created 2026-04-08.\n",
    )
    return before, after


def test_score_only_guard_accepts_the_retold_read_day_on_a_dated_source(tmp_path: Path) -> None:
    before, after = _guard_pair("2026-11-19")
    assert _guard_result(tmp_path, before, after).ok


def test_score_only_guard_refuses_any_other_day(tmp_path: Path) -> None:
    before, after = _guard_pair("2026-10-01")
    assert not _guard_result(tmp_path, before, after).ok


def _board(names):
    return refresh.BoardReading(
        key="matharena", source_id="x", benchmark_ids=frozenset({"aime_2026"}),
        source_url="https://matharena.ai/competition_tables/aime--aime_2026",
        observed_at=DAY,
        rows=tuple({"model": n, "mean_score": 0.9667, "observed_at": DAY} for n in names),
        value_field="mean_score", fraction=True, snapshot_ref="sha256:" + "0" * 64,
        row_template={"unit": "percent"},
    )


def _evidence(name: str, effort=None) -> dict:
    return {"benchmark_id": "aime_2026", "model_id_as_evaluated": name, "score": 96.67,
            "unit": "percent", "effort": effort,
            "source_url": "https://matharena.ai/competition_tables/aime--aime_2026"}


def _plan(board, evidence):
    return refresh._plan_observations("lab/m", "lab/m", [evidence], board)


def test_think_row_is_refused_with_a_named_reason_when_the_board_states_efforts() -> None:
    obs, failures, _ = _plan(_board(["Kimi K3 (max)", "Kimi K3 (high)"]), _evidence("Kimi K3 (Think)"))
    assert not obs
    assert [f.reason for f in failures] == [refresh._BOARD_RENAMED_TO_EFFORT]
    assert refresh._skip_class(failures[0].reason) == "effort"


def test_a_stored_name_that_states_the_same_effort_still_matches() -> None:
    obs, failures, _ = _plan(_board(["Kimi K3 (max)", "Kimi K3 (high)"]), _evidence("Kimi K3 (max)"))
    assert not failures and len(obs) == 1


def test_an_absent_row_keeps_the_no_unique_row_reason() -> None:
    _, failures, _ = _plan(_board(["Other Model (max)"]), _evidence("Kimi K3 (Think)"))
    assert [f.reason for f in failures] == ["no unique row for 'Kimi K3 (Think)'"]
