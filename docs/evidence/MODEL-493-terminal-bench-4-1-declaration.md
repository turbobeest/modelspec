# MODEL-493-F: the Terminal-Bench 4.1 declaration and its board-name check

The Terminal-Bench leaderboard at `https://www.tbench.ai/` serves version 4.1.
This change declares that board as its own benchmark, makes the read check the
board's own name, and retires the 4.0 declaration.

## What is declared

In `collect_readings` (`scripts/refresh_leaderboards.py`):

| field | value |
|---|---|
| key | `terminal-bench-4-1` |
| benchmark | `terminal_bench_v4_1` (its own item in the capability fit; never a re-pointed 4.0 id) |
| read address and card address | `https://www.tbench.ai/` (no redirect; the default final-address rule applies, no exception) |
| source id | `model-493-evidence-terminal-bench-4-1-json` |
| projector | `_project_tbench`, value field `accuracy` |
| expected board name | `4-1-0`, with the title `Terminal-Bench 4.1` as a second witness |

The source id is new because the one registered for this address names the 4.0
board, and one id must not stand for two versions. `load_sources` refuses a
board whose source id is not registered, so the private data repository must
add a `registry/sources.yaml` entry for the new id (url `https://www.tbench.ai/`,
`volatility: live`, region `rows`) before its engine pin moves to this change.
This repository holds no registry edit.

With no `terminal_bench_v4_1` row on any card, the declaration reads the board
and files nothing for it. That is expected until the data change adds the page
and the first rows.

## The board-name check

`_project_tbench` runs `_check_tbench_board` on the bytes it was given, before
any row is projected.

The page's shape (read from the live page on 2026-11-14): the React payload
carries one dehydrated query whose `data` object holds the `leaderboard`
identity object (with `name` `4-1-0` and `title` `Terminal-Bench 4.1`) and,
as its sibling key, the one `rows` list of the board. A second `leaderboard`
key on the page is a React prop whose value is a list, not an identity.

The rule: the page holds exactly one `"leaderboard"` identity object, it
carries the expected name (and the expected title when it has one), and the
projected rows are the single `"rows"` list that is a direct key of the same
enclosing object as that identity. Otherwise the check raises
`BoardVersionMismatch`, whose text is

    board_version: expected name 4-1-0 (title Terminal-Bench 4.1), found <what the page says>

The same failure covers a missing name, a page with no leaderboard object, a
page with more than one (even if one of them is named correctly), a second row
list anywhere, and rows that are not beside the named identity. It reaches the report the way
`redirected` does: a `RowFailure` for the board, with nothing filed (no
observation, no row change, `observed_at` does not move, `not_published_since`
is neither set nor removed). Other boards in the run are unaffected.

`scripts/data_trust/sample.py` calls the same projector without arguments; the
expected name defaults to the declared one, so it gets the check too. A page of
another version makes that sample read "unreadable", because the mismatch is a
`ValueError` the sampler already catches.

The update path narrows a page's rows by effort only when the stored row has an
`effort:` key (or spells the effort in its name), so the first 4.1 rows must be
filed with `effort:`.

## What a `board_version` failure means

The page at this address no longer calls itself Terminal-Bench 4.1: the board
changed version. Declare the new version as its own benchmark with its own id,
page and source. Never re-point `terminal_bench_v4_1` at it, and never relax
the expected name to make the failure go away.

## What was retired

The 4.0 declaration (`terminal_bench_v4_0` at
`https://www.tbench.ai/leaderboard/terminal-bench/4.0`) is removed. That
address redirects to the 4.1 board, so since the final-address rule it failed
every week as `redirected` and filed nothing, and its card rows are marked
`not_published_since`. A failure that repeats every week teaches readers to
ignore failures. The board-name check replaces that loud failure with one that
fires only when something changed. Nothing refreshes the 4.0 rows again; they
stay as the last 4.0 readings.

The redirect tests in `tests/test_refresh_final_address.py` now use the 4.1
declaration as their example (a redirect from `https://www.tbench.ai/` to
another address). They prove what they proved before. The structural test on
`_fetch` is unchanged: 7 default calls; the Terminal-Bench read goes through
`collect`'s default reader, which is a reference and not a call.
