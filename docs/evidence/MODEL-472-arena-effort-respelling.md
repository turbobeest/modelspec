# MODEL-472 Arena effort respelling

Base `618b0a8a34b778829b409e570eb63bc455072083`. Branch `model-472-fix`.
Round 2 merged `origin/main` through `95f169da4b3288225497a56ed379fe5428c2ca9d`.
The latest commit that touches this file is the change. Read it with
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

"At the new publish date" is the publish date of the Arena reading this run
matched for that board, not the newest date already on the cards. A row whose
publish date equals that day is at the new date. Every other row on the board
is left at an older date, including when no card row moved. A board the run
did not read is `not read` in each of the three fields and is left out of
`N` and `M`.

The first version of `scripts/premier_slice1.py` checked every live slice-1
board whose rows carry a date. That was wrong. The brief said "whose rows
carry a publish date". Against the data clone that version exits 1 on 9
boards. Six of them are not Arena, and their rows carry each model's own
evaluation date, so they always mix: `epoch-frontiermath-tiers-1-3-v2`,
`epoch-gpqa-diamond`, `epoch-swe-bench-verified`, `scale-hle`,
`swe-bench-pro`, `terminal-bench-4.0`. Once the data repository's engine pin
moves, the lineup proposer would fail on every push.

The check now covers only a board whose every row is an Arena dataset-root
reading. The predicate is the refresh writer's `_arena_reading_row`, imported
once, not copied. A mixed Arena top 10 exits 3 and names those boards and the
counts per date on stderr. `--allow-mixed-boards` still proposes. `--check`
still exits 1 when the proposed membership differs. The approved `--check`
path, with no `--data-dir`, is unchanged. `.github/private-writers/lineup-proposer.yml`
was not edited. Its `set -euo pipefail` already stops the proposal step on
any non-zero exit, before a proposal is opened. The workflow checks out the
pinned engine, so the refusal applies when that pin moves.

Not done: an atomic whole-board skip, card edits, and deleting date sentences.

## Tests

Python 3.12.3, pytest 9.2.0, Git 2.43.0. Serial, `-q -p no:cacheprovider`,
no `-n`. Exit codes read directly. No full local suite. The interpreter path
is omitted.

### First commit

Red, before the production change. Exit 1. 16 failed, 14 passed, in 2.26s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
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
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py tests/test_arena_revision.py \
  tests/test_premier_slice1.py tests/test_premier_live.py \
  tests/test_writer_isolation.py
```

The 8 skips were already in those files. `tests/test_premier_slice1.py`
includes the approved `--check` comparison and passed.

### Round 2

Red, before this round's production change. Exit 1. 5 failed, 6 passed, in
2.53s. The Arena mixed top 10 still exited 1 and also named
`terminal-bench-4.0`. Ten evaluation dates on a non-Arena board raised
`MixedBoards`. `mixed_publish_dates` still named `terminal-bench-4.0`. The
census counted an unread sibling, so the lines were `1 of 2` and `0 of 2`.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_premier_live.py::test_the_proposer_refuses_an_arena_mixed_top_10 \
  tests/test_premier_live.py::test_a_non_arena_board_with_ten_evaluation_dates_does_not_block \
  tests/test_premier_live.py::test_a_changed_membership_check_still_exits_1 \
  tests/test_premier_live.py::test_allow_mixed_boards_still_proposes \
  tests/test_premier_live.py::test_an_arena_board_with_older_dates_only_below_the_top_10_does_not_block \
  tests/test_premier_live.py::test_a_mixed_date_inside_the_top_10_refuses \
  tests/test_premier_live.py::test_a_lower_is_better_top_10_uses_the_low_scores \
  tests/test_premier_live.py::test_a_dateless_seat_does_not_count_as_a_second_publish_date \
  tests/test_premier_live.py::test_mixed_publish_dates_names_the_arena_board_and_the_counts \
  tests/test_leaderboard_refresh.py::test_the_report_counts_rows_left_on_an_older_publish_date \
  tests/test_leaderboard_refresh.py::test_an_unmoved_board_is_all_older_and_an_unread_board_is_not_read
```

Green, that selector plus
`test_a_hyphenated_stored_name_adopts_the_parenthetical_effort`: 12 passed
in 2.72s, exit 0. Focused files plus writer isolation, the same command as
above: 544 passed, 8 skipped, in 91.19s, exit 0.

## Acceptance

Read-only data clone. These two commands, and no command output:

```bash
env PYTHONPATH=$PWD python scripts/premier_slice1.py --data-dir /home/turbobeest/dev/04-modelspec/modelspec-data
env PYTHONPATH=$PWD python scripts/premier_slice1.py --data-dir /home/turbobeest/dev/04-modelspec/modelspec-data --allow-mixed-boards
```

The first command exited 3. Its message named only `arena-text`,
`arena-vision`, and `arena-webdev`. It named none of
`epoch-frontiermath-tiers-1-3-v2`, `epoch-gpqa-diamond`,
`epoch-swe-bench-verified`, `scale-hle`, `swe-bench-pro`,
`terminal-bench-4.0`. The second command exited 0. The same command on
`origin/main` at `95f169da4b3288225497a56ed379fe5428c2ca9d` also exited 0.
The two membership documents were equal: `changed` true, 1 added, 1 removed.

## Not observed

- No live Arena fetch and no refresh of the private catalogue.
- No edit of ranking floors, `decision/verify.py`, registry files, or frozen data.
- No edit under `.github/private-writers/`.
- No run of `.github/private-writers/lineup-proposer.yml`.
- Pull-request checks were not read at the time of this commit.

## Hand-set effort, one renamed row

Base `8bf26fd2dcbd450c112cbdb19a20d796d45c5823`. Branch `model-472-fix2`.
The commit that adds this section is the change. Read it with
`git log -1 --format=%H -- docs/evidence/MODEL-472-arena-effort-respelling.md`.

A stored name with no effort token now matches one dataset row when that
row's parenthetical effort, removed, normalises to the stored name, the
parenthesis is an effort level, and the card's `effort` is already that
level. The reading is written. `effort` and `model_id_as_evaluated` stay.
The match is counted on that board only.

Refusals, before a write: card `effort` null stays `dataset names an effort
the stored name does not`; card `effort` at another level is `card effort
differs from the dataset's only row`; two or more such rows, including when
one equals the card, are `dataset has several effort rows for this name`.
A parenthesis that is not an effort level stays a different name. A
hyphenated dataset name alone stays `no unique row`. When that hyphenated
row shares the board with a parenthetical effort row of the same name, the
next section refuses both. A stored name that already spells an effort still
uses the earlier rule. `check_score_only` is unchanged. A refresh of the
accepted row passes it. Changing that row's `effort` still fails.

### Tests

Python 3.12.3, pytest 9.2.0, Git 2.43.0. Serial, `-q -p no:cacheprovider`,
no `-n`. Exit codes read directly. No full local suite. The interpreter path
is omitted.

Red, before the production change. Exit 1. 6 failed, 4 passed, in 0.97s.
The accepted row was `dataset names an effort the stored name does not`.
One `(High)` row with card `max` was `no unique row for 'some-model'`.
`(High)` and `(Max)` with card `high`, and the same rows with card `max`,
were `dataset names an effort the stored name does not`, because the old
match had already kept only the row at the card's level. Those rows with
card `effort` null were `no unique row for 'some-model'`. The guard test
stopped on that same refusal, so no refresh was written.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_matches_the_datasets_only_renamed_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_null_effort_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_that_differs_from_the_only_row_is_not_written \
  tests/test_leaderboard_refresh.py::test_several_effort_rows_for_one_name_are_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_parenthesis_that_is_not_an_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_dataset_name_is_not_the_hand_set_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_no_parenthesis_in_the_dataset_still_verifies \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_refresh_is_score_only_and_an_effort_change_still_fails
```

The four that passed on that run were the null-effort slug, a `(Preview)`
parenthesis, a hyphenated dataset name, and one row with no parenthesis.

Green, the same selector plus the earlier spelled-name tests. Exit 0.
16 passed in 0.56s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_matches_the_datasets_only_renamed_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_null_effort_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_that_differs_from_the_only_row_is_not_written \
  tests/test_leaderboard_refresh.py::test_several_effort_rows_for_one_name_are_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_parenthesis_that_is_not_an_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_dataset_name_is_not_the_hand_set_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_no_parenthesis_in_the_dataset_still_verifies \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_refresh_is_score_only_and_an_effort_change_still_fails \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_stored_name_adopts_the_parenthetical_effort \
  tests/test_leaderboard_refresh.py::test_a_stored_name_without_the_effort_token_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_stored_name_that_spells_another_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_two_dataset_rows_that_normalise_alike_are_not_written \
  tests/test_leaderboard_refresh.py::test_a_card_effort_already_at_another_level_is_not_overwritten \
  tests/test_leaderboard_refresh.py::test_a_parenthetical_effort_the_card_does_not_name_is_not_written
```

Focused files. Exit 0. 439 passed, 8 skipped, in 21.82s. The 8 skips were
already in those files. Each skip reason was not listed.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py tests/test_writer_isolation.py
```

Outcomes on invented names, through `refresh.run`:

- One `(High)` row, card `high`: written. `effort` stays `high`. `model_id_as_evaluated` stays `some-model`. Verifier `verified`.
- `(High)` and `(Max)`, card `high`: `dataset has several effort rows for this name`. Not written.
- `(High)` and `(Max)`, card `max`: the same reason. Not written.
- One `(High)` row, card `max`: `card effort differs from the dataset's only row`. Not written.
- One row with no parenthesis: written. `effort` stays null. Verifier `verified`.

### Not observed

- No live Arena fetch and no refresh of the private catalogue.
- No edit of `decision/verify.py`, the proposer, a workflow, the registry, or frozen data.
- No change to `check_score_only`. The new refresh passes it; an `effort` edit on that row still fails.
- Pull-request checks were not read at the time of this commit.

## Every effort spelling, before the single renamed row

Base `5abc90a6111516699661d6a22c762a11fa0bf78a`. Branch `model-472-fix2`.
The commit that adds this section is the change. Read it with
`git log -1 --format=%H -- docs/evidence/MODEL-472-arena-effort-respelling.md`.

Before that hand-set case writes, any other row on the board that is the
same model name plus an effort token is `dataset has several effort rows
for this name`. The token is the one the existing helpers already read
(`_name_without_parenthetical_effort`, `_stem_without_trailing_effort`,
`_PARENTHETICAL_EFFORT`). No second recogniser was added. The card's level
does not choose.

### Note

A parenthesis that is not an effort level, for example `(Preview)`, is a
different name and does not count. `Some Model (High)` with `Some Model
(Preview)` and `Other Model (Max)`, card effort `high`, is still written.
A dataset name that is only `(Preview)` stays `no unique row`.

The count treats these as the same name plus an effort:

- One parenthesis whose text is an effort level: `(minimal)`, `(low)`,
  `(medium)`, `(high)`, `(xhigh)`, `(max)`.
- Several of those parentheses: `(Max) (High)`.
- One trailing effort token in a hyphen or slug (`acme-orbit-9-max`), after
  an underscore (`acme_orbit_9_max`), or after a space (`Acme Orbit 9 Max`).
- That same trailing token in brackets: `[High]`.

`(maximum)` is not in that token set, so `Acme Orbit 9 (maximum)` is not
counted. `(max effort)` is not counted. A second trailing slug,
`acme-orbit-9-max-high`, drops only one token and is not a row of
`acme-orbit-9`. An interior token, `acme-high-orbit-9`, is not counted.

### Tests

Python 3.12.3, pytest 9.2.0, Git 2.43.0. Serial, `-q -p no:cacheprovider`,
no `-n`. Exit codes read directly. No full local suite. The interpreter path
is omitted.

Red, before the production change. Exit 1. 3 failed, 2 passed, in 0.60s.
`Acme Orbit 9 (High)` plus `acme-orbit-9-max`, card `high`, wrote the
`(High)` row (no failure). The same board with card `max` was `card effort
differs from the dataset's only row`. `Acme Orbit 9 (Max)` plus `Acme Orbit
9 (Max) (High)`, card `max`, wrote the `(Max)` row (no failure). The single
`(High)` row and the `Acme Orbit 9.1 (High)` neighbour passed.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_refuses_when_a_slug_effort_row_exists \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_refuses_when_a_double_parenthesis_row_exists \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_still_writes_the_single_renamed_row \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_ignores_a_different_model_with_the_same_effort
```

Green, those four tests plus the earlier hand-set and spelled-name tests.
Exit 0. 21 passed in 0.56s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_refuses_when_a_slug_effort_row_exists \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_refuses_when_a_double_parenthesis_row_exists \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_still_writes_the_single_renamed_row \
  tests/test_leaderboard_refresh.py::test_hand_set_effort_ignores_a_different_model_with_the_same_effort \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_matches_the_datasets_only_renamed_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_null_effort_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_that_differs_from_the_only_row_is_not_written \
  tests/test_leaderboard_refresh.py::test_several_effort_rows_for_one_name_are_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_parenthesis_that_is_not_an_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_dataset_name_is_not_the_hand_set_row \
  tests/test_leaderboard_refresh.py::test_a_stored_slug_with_no_parenthesis_in_the_dataset_still_verifies \
  tests/test_leaderboard_refresh.py::test_a_hand_set_effort_refresh_is_score_only_and_an_effort_change_still_fails \
  tests/test_leaderboard_refresh.py::test_a_hyphenated_stored_name_adopts_the_parenthetical_effort \
  tests/test_leaderboard_refresh.py::test_a_stored_name_without_the_effort_token_is_left_for_a_person \
  tests/test_leaderboard_refresh.py::test_a_stored_name_that_spells_another_effort_is_not_written \
  tests/test_leaderboard_refresh.py::test_two_dataset_rows_that_normalise_alike_are_not_written \
  tests/test_leaderboard_refresh.py::test_a_card_effort_already_at_another_level_is_not_overwritten \
  tests/test_leaderboard_refresh.py::test_a_parenthetical_effort_the_card_does_not_name_is_not_written
```

Focused files. Exit 0. 444 passed, 8 skipped, in 21.07s. A repeat with
`-rs` was 444 passed, 8 skipped, in 20.87s. Each skip reason was
`python -m venv is unavailable` in `tests/test_writer_isolation.py`.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py tests/test_writer_isolation.py
```

Outcomes on invented names, through `refresh.run`:

- `Acme Orbit 9 (High)` and `acme-orbit-9-max`, card `high`: `dataset has several effort rows for this name`. Not written.
- The same board, card `max`: the same reason. Not written.
- `Acme Orbit 9 (Max)` and `Acme Orbit 9 (Max) (High)`, card `max`: the same reason. Not written.
- Only `Acme Orbit 9 (High)`, card `high`: written. `effort` stays `high`. `model_id_as_evaluated` stays `acme-orbit-9`. Verifier `verified`.
- `Acme Orbit 9 (High)` and `Acme Orbit 9.1 (High)`, card `high`: the exact name is written. `effort` stays `high`. `model_id_as_evaluated` stays `acme-orbit-9`. Verifier `verified`.

### Not observed

- No live Arena fetch and no refresh of the private catalogue.
- No edit of `decision/verify.py`, the proposer, a workflow, the registry, or frozen data.
- No change to `check_score_only`.
- No second effort-token recogniser. The count calls the helpers above.
- Pull-request checks were not read at the time of this commit.
