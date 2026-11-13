# MODEL-482 a reading the live board no longer publishes

Base `8d74c676a46149207f89da2e4a361d1340d40d29`. Branch `model-482-b`.
The commits after that base are the change. The latest one that touches
this note is `git log -1 --format=%H -- docs/evidence/MODEL-482-not-published-since.md`.

## What the key means

`not_published_since` is an optional ISO date on a benchmark evidence row.
It is the day the weekly refresh first saw the source list that row with no
value. The stored score stays. The row stays a ranking input. Nothing else
on the row moves: score, `observed_at`, `evidence_date`, `date_type`,
`effort`, `model_id_as_evaluated`, `quality_flags`, `verified_at`, sources,
or `id`.

The key is not part of `evidence_id` and not part of
`evidence_verification_value`. `Evidence` forbids unknown keys and inherits
the field from `BenchmarkEvidence`. A dump omits the key when it is absent,
so an old row does not grow a null. A non-ISO value is rejected. An empty
string is rejected.

No version constant moved. `card_schema_version` stays `3.0`,
`FORMAT_VERSION` stays `2`, and the decision contract gains no field. The
field is optional and has a default, so old cards still validate. No enum
was widened.

## Who sets it

`scripts/refresh_leaderboards.py`, on a declared board only. The
declaration is `BoardReading.explicit_empty_cells`, default off, set from
`UNPUBLISHED_CELL_BOARDS`, which names the MathArena boards and no other.
A mark is written only when that same read parsed the table, exactly one
row matches the stored name, the value key is present on that row with a
value of None (a missing key is a re-shaped read, not an empty cell), at
least three other rows carry a number, the board has at least two tracked
card rows, and every tracked card row of the board is present in the same
read (the completeness rule below). The written day is the run's observation day. It is quoted so
the next YAML load stays a string. If the key is already set, the stored
day is left as it is and the file is not rewritten.

These reads mark nothing and stay the existing failure:

- the board has no numeric value or fewer than three scored neighbours
- a tracked row of the board is missing from the read, or the board has a
  single tracked row
- the value key is missing on the matched row
- the board is not declared
- the stored name matches no row
- the stored name matches several rows, including when one cell is empty
  (a sibling whose score agrees is not used)
- the fetch failed, or the projector raised, so no board was built

When a later read finds a value, the key is removed and the reading is
written like any other reading. The Arena dataset path never sets the key.

On MathArena the key means the source lists the model without a measured
value: an empty cell, or a cell the site estimated (`data-predicted`). The
projector drops both, because `document` drops a None. Reading a declared
board therefore puts the value key back as None on a named row that has
none, in `_reading_from_projection`; an undeclared board gets no such
help. A predicted cell on a row that already holds a stored measured score
is treated like an empty one. A non-empty string is not treated as absent.

The guard accepts the key added, or removed, and nothing else on the row.
One date replaced by another is refused, with or without other changes.

The markdown report and `report.json` have their own section and key:
newly marked, still marked, and unmarked this run, by card and benchmark,
with `observed_at` as last seen (or `evidence_date` when `observed_at` is
absent). Those rows are not in the Failures table. The section is omitted
when there are no marks. The JSON key is always present.

Marks are not `changes` and not `reconfirmed`. The weekly workflow was not
edited. Its `GITHUB_OUTPUT` lines stay the existing counts. A run whose
only writes are new marks still has `updates` of zero, so that job does
not open a pull request. A typical run reconfirms some other board, and
the marks ride along on that pull request. The markdown report may name
cards. That report is the private step summary. The workflow file does
not print the new key.

`check_score_only` accepts a row whose only change is this key added or
removed, and counts that class as `not_published_since`. The key together
with any other changed field is judged by the existing rule for that
other field, and is not counted in this class.

## Who reads it

`scripts/accuracy.py` `_live_observation_date`. A retained record that
carries a non-empty key is not a live reading, so `stale_live_leaderboard`
and `undated_live_leaderboard` do not fire for it. Every other row that
cites the same live source ages as before. A blank string is not a mark.
The freshness count `not_published_since` is always present. The summary
names the count only when it is not zero. `check_private_freshness` keeps
counts and clears details, so the private detail is that count and adds
no card name. `scripts/accuracy_public.py` was not changed. Its public
summary does not read the key.

`pipeline/render.py` `evidence_section`. A row with the key shows the
score as before, then `no longer published by the source; last seen
<observed_at>`. When `observed_at` is absent, the date is `evidence_date`.
No row in the frozen public image has the key, so no rendered page changes
today. The proof is the existing Python render tests plus one invented
row. `web/` was not touched, and the npm site build was not run.

The capability fit does not read the key. A snapshot built from a marked
row and from the same row unmarked gives the same capability estimate,
the same evidence value, and the same quality flags.

## Tests

Python 3.12.3, pytest 9.2.0, git 2.43.0. Interpreter
`/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python`. Serial,
`-q -p no:cacheprovider`, no `-n`. Exit codes read directly. No full
local suite.

Red, before the production change. Exit 1. 21 failed, 3 passed, 198
deselected, 1.32s. The three that already passed were the ranking
comparison (the fit ignores an unknown key), the public-summary lock,
and the lock that the workflow file does not name the key.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_not_published_since.py tests/test_accuracy.py tests/test_relations.py \
  tests/test_decision_capability.py -k not_published --tb=line
```

Green, after the change. Exit 0.

- The same `-k not_published` command: 24 passed, 198 deselected, 0.80s.
- `tests/test_leaderboard_refresh.py tests/test_arena_revision.py tests/test_accuracy.py tests/test_writer_isolation.py tests/test_class_fit.py tests/test_decision_model.py tests/test_decision_capability.py`: 808 passed, 8 skipped, 63.27s.
- `tests/test_relations.py tests/test_legal.py tests/test_attach_evidence.py`: 133 passed, 211.30s.
- `tests/test_not_published_since.py` alone: 18 passed, 0.36s. That is the duration recorded for the shard check.
- `tests/test_ci_workflows.py::test_shard_timings_cover_the_current_suite_and_browser_modules` after that record: 1 passed, 0.28s.

The first CI run failed that same check: 367 of 387 modules were measured, short of 95 percent, because the new file had no duration. No other shard failed that run.

Invented names and invented scores only. No private card value is in
this note.

## Outcomes

(a) The row is present, its cell is empty, and another row has a number:
newly marked, only the key is written, and the row is not a failure.
(b) No cell on the board has a number: `no unique row`, no key.
(c) The stored name is missing: `no unique row`, no key.
(d) The fetch fails and no board is built: the failure is kept, no key.
A projector that raises is the same path.
(e) A marked row has a value again: the key is removed and the reading
is written as any other. Last seen is the old `observed_at`.
(f) A marked row is still empty on a later run: nothing is written, and
the stored day stays.
(g) Two rows match the stored name and one cell is empty: `no unique row`,
no key, including when the other row's score agrees with the stored score.

(h) The value key is missing: `no unique row`, no key. The board is
undeclared, fewer than three scored neighbours, a tracked row missing, a
single tracked row: no key, each with its own reason (below). 3 of 10, 5 of
10, 6 of 10 and all scored: marked, when the read is complete.

(MODEL-482-C replaced the half rule of the first version; (b) now reads
"fewer than three scored neighbours" and is not `no unique row`.)

## The completeness rule (MODEL-482-C)

The first version also required at least half of a board's other rows to be
numeric. The first live run marked nothing: each MathArena board has 24 rows,
8 with a number, and that is its normal state. The half rule tested how full
a board is, not whether the read is complete, and it was refused under the
same text as a name that matches nothing.

A row on a declared board is marked only when all hold in one read: (a) the
stored name matches exactly one row, whose value key is present and None;
(b) at least three other rows carry a number; (c) every card row the
catalogue tracks on that board matches exactly one row of the read, with or
without a value; (d) the board has at least two tracked rows. "Tracked" is
the set of card evidence rows the run plans for that board (the same filter
`_plan_observations` applies: benchmark id on the board, source URL accepted
by it), taken over every card in the run and decided for the whole board
before any row is marked, so the order of processing cannot change the
outcome. If one tracked row matches no row or several, no row of that board
is marked in that run.

Each refusal has its own text, all counted in the report class
`empty-cell-not-marked` (`no-unique-row` stays for a name that matches no row
or several, and for a missing value key):

- `empty cell for '<name>' on a board that does not declare empty cells; not marked`
- `empty cell for '<name>' with fewer than 3 other rows scored; not marked`
- `empty cell for '<name>' while the tracked row of <card id> (<benchmark>) is missing from the read; not marked`
- `empty cell for '<name>' on a board with a single tracked row; not marked`

The card id appears in the failure table of the private report only. The
workflow log keeps counts.

On a declared board a value the projector dropped is restored as None, so
"missing" and "empty" are the same thing there. What protects a read is (b),
(c) and (d): a page that served only some rows, lost a tracked row, or no
longer prints any number marks nothing. What the rule does not protect
against is a page change that empties the cells while keeping every tracked
row present and three other rows numeric. That read marks. The report lists
every newly marked row, and a person reads it before the refresh merges.

The weakest read that still marks: two or more tracked rows, all present once
each, three other rows numeric, and the row's own cell empty. That is
acceptable because the mark is reversible (a later value removes it, the
score stays, ranking is unchanged) and every newly marked row is listed.

The parser: `project_matharena` splits the table by `<tr` and reads table 0.
On the recorded 2026-09-29 pages the `<tr` count is the row count plus one
(the header row in `thead`), `model-name` cells equal the projected rows, and
there is one table. A row is dropped only when its cell count differs from the
header's, which the recorded pages do not have. A live page with about 50
`<tr` against 24 rows was not re-read here and is not explained by these
fixtures.

## Not observed

- No npm site build, and no edit under `web/`.
- No Worker memory probe. The key is not on the frozen public image.
- No run of the weekly workflow, and no edit of it.
- No full local suite.
- `tests/shard_durations.json` records `tests/test_not_published_since.py`
  at 0.36s, the time that file took alone. The other unmeasured modules
  were already unmeasured on the base. The eight-way shard summary still
  balances the packed shards.
