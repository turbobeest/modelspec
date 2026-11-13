# MODEL-472 Arena effort respelling

Base `618b0a8a34b778829b409e570eb63bc455072083`. Branch `model-472-fix`.
The commit that adds this file is the change. Read it with
`git log -1 --format=%H -- docs/evidence/MODEL-472-arena-effort-respelling.md`.

The November Arena revision spells effort in parentheses. The writer already
finds the unique row by normalised full name. It left `effort` null when the
stored `model_id_as_evaluated` spells that level with a hyphen, and the
verifier then skipped the row. 448 Arena rows on 18 premier-lineup cards
stayed on the older publish date. 31 of 37 Arena boards have a top 10 that
mixes publish dates. Counts only; no card values.

## What changed

On an Arena dataset-root row, one dataset row whose full normalised name
equals the stored `model_id_as_evaluated` is that row. A null `effort` may
become the level `structured_name_effort` reads on the dataset name when the
stored name already spells it: a parenthesis, or a trailing token in
`minimal`, `low`, `medium`, `high`, `xhigh`, `max`. `model_id_as_evaluated`
is not rewritten. The cited row is still the matcher's row.

Refusals, before a write: `dataset names an effort the stored name does not`;
`stored name spells a different effort than the dataset row`; `two dataset
rows normalise to the stored name`; `card effort is already a different
level`. A prefix, a suffix, or an interior token is not a match.
`check_score_only` allows null to that spelled level only on a refreshed
Arena dataset-root row, with that row's own figures.

`render_report`, the fitted pull-request body, and `report.json` carry
`Arena boards with a mixed top 10: N of M`, plus per board
`rows_at_new_publish_date`, `rows_at_older_publish_date`, and
`mixed_top_10`. The fitter keeps the count line. It keeps the table when the
shortened body still fits.

`scripts/premier_slice1.py` checks a live slice-1 top 10 before ranking.
More than one `evidence_date` in that top 10 exits non-zero and names the
board and the counts. `--allow-mixed-boards` continues. `--check` does not
run the check. `.github/private-writers/lineup-proposer.yml` was not edited.
Its `set -euo pipefail` already stops the proposal step on a non-zero exit.
The workflow checks out the pinned engine, so the refusal applies when that
pin moves.

Not done: an atomic whole-board skip, card edits, and deleting date sentences.

## Tests

Python 3.12.3 and pytest 9.2.0 from
`/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python`. Git 2.43.0.
Serial, `-q -p no:cacheprovider`, no `-n`. Exit codes read directly. No full
local suite.

Red, from the worktree, before the production change. Exit 1. 16 failed,
14 passed, in 2.26s.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py::test_score_only_check_accepts_a_hyphenated_effort_the_stored_name_spells \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_stored_name_adopts_the_parenthetical_effort \
  tests/test_leaderboard_refresh.py::test_a_stored_name_without_the_effort_token_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_stored_name_that_spells_another_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_two_dataset_rows_that_normalise_alike_are_not_written \
  tests/test_leaderboard_refresh.py::test_a_card_effort_already_at_another_level_is_not_overwritten \
  tests/test_leaderboard_refresh.py::test_a_parenthetical_name_matches_only_the_stored_name_that_spells_it \
  tests/test_leaderboard_refresh.py::test_the_report_counts_rows_left_on_an_older_publish_date \
  tests/test_leaderboard_refresh.py::test_the_pull_request_body_keeps_the_mixed_board_line \
  tests/test_leaderboard_refresh.py::test_the_guard_accepts_the_writers_arena_fixture_row \
  tests/test_premier_live.py::test_the_proposer_refuses_a_mixed_top_10 \
  tests/test_premier_live.py::test_allow_mixed_boards_still_proposes \
  tests/test_premier_live.py::test_a_mixed_date_inside_the_top_10_refuses \
  tests/test_premier_live.py::test_a_lower_is_better_top_10_uses_the_low_scores \
  tests/test_premier_live.py::test_a_dateless_seat_does_not_count_as_a_second_publish_date \
  tests/test_premier_live.py::test_mixed_publish_dates_names_the_board_and_the_counts
```

The hyphenated accept was refused by `check_score_only`. The writer reported
`effort expected None found 'high'` and did not write. A stored name with no
effort token got that verifier reason instead of `dataset names an effort
the stored name does not`. A different spelled effort was `no unique row`.
Two dataset rows that normalise alike produced no failure. An effort already
set to another level was a verifier diff. The name helper and
`mixed_publish_dates` were missing. The report had no mixed-top-10 line, and
the fitter dropped it. The proposer exited 0 on a mixed top 10.
`--allow-mixed-boards` was an unrecognized argument.

Green, same interpreter, after the change. The new tests: 22 passed in
1.85s, exit 0. Focused files plus writer isolation: 541 passed, 8 skipped,
in 92.61s, exit 0.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py tests/test_arena_revision.py \
  tests/test_premier_slice1.py tests/test_premier_live.py \
  tests/test_writer_isolation.py
```

The 8 skips were already in those files. `tests/test_premier_slice1.py`
includes the approved `--check` comparison and passed.

## Not observed

- No live Arena fetch and no refresh of the private catalogue.
- No edit of ranking floors, `decision/verify.py`, registry files, or frozen data.
- No run of `.github/private-writers/lineup-proposer.yml`.
- Pull-request checks were not read at the time of this commit.
