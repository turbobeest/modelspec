"""MODEL-505: a re-confirmed row of any board retells its one read day; renamed-effort rows are named.

Invented rows, scores and dates. No network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import _card, _guard_result

EPOCH = ("Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (x.csv), "
         "read 2026-09-24. Run started 2026-08-14T18:29:12.000Z; effort high.")
SCALE = "Scale Labs leaderboard entry read 2026-09-25; entry created 2026-04-08; effort thinking."
SWEBENCH = "Official SWE-bench leaderboard (swebench.com), Verified board, read 2026-09-25. Agent X."
DAY = "2026-11-19"


def _observation(score: float = 50.0):
    return refresh.RowObservation(
        card="lab/example", model_id="lab/example", model="Example", benchmark="b",
        old_value=50.0, new_value=score, source="fixture", observed_date=DAY,
        evidence_date="2026-08-14",
    )


def _old(configuration: str) -> dict:
    return {"score": 50.0, "configuration": configuration, "evidence_date": "2026-08-14",
            "observed_at": "2026-11-16", "model_id_as_evaluated": "Example"}


@pytest.mark.parametrize("text,was", [(EPOCH, "2026-09-24"), (SCALE, "2026-09-25"),
                                      (SWEBENCH, "2026-09-25")])
def test_the_one_read_day_is_retold_and_nothing_else_moves(text, was) -> None:
    new, reason = refresh._copy_matched_reading(_old(text), _observation(), observed_at=DAY)
    assert reason is None
    assert new["configuration"] == text.replace(f"read {was}", f"read {DAY}")


def test_same_day_twice_is_identical() -> None:
    once, _ = refresh._copy_matched_reading(_old(EPOCH), _observation(), observed_at=DAY)
    twice, _ = refresh._copy_matched_reading(once, _observation(), observed_at=DAY)
    assert once == twice


@pytest.mark.parametrize("text", [
    "No day here. Run started 2026-08-14.",
    "re-read 2026-09-24 of the page.",
    "page read 2026-09-24 and page read 2026-09-25.",
])
def test_no_read_or_two_reads_stay_as_written(text) -> None:
    new, _ = refresh._copy_matched_reading(_old(text), _observation(), observed_at=DAY)
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
