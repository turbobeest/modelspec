# MODEL-472 compound qualifier

Base `8bf26fd2dcbd450c112cbdb19a20d796d45c5823`. Branch `model-472-fix3`.
The head is the commit that adds this note. Read it with
`git log -1 --format=%H -- docs/evidence/MODEL-472-compound-qualifier.md`.

Eight Arena rows on four cards were refused because the matcher found a
compound display name and the verifier then read the bare sibling. Three of
those cards sit inside a top 10. Counts only. No card values.

## What changed

Ownership is `_reading_subject_matches` in `decision/verify.py`. A subject
with exactly one compound parenthesis matches a claim name when the two full
token sets are equal. A subset or a prefix does not match. The parenthesis
is a comma- or space-separated list of at least two tokens. Each token is an
effort word, `Thinking` with a context size, a context size such as `32K`,
or an eight-digit date.

`split_model_cell` does not strip that parenthesis, so its identity string
still cannot express a reordered slug. It now returns the one effort word
inside the compound parenthesis and keeps every token, including that word,
in the identity. `Thinking 16K` is not an effort level. `(High)` alone still
strips. A hyphenated slug still names no effort.

`structured_name_effort` is unchanged. `(High)` still names `High`.
`example-model-high` still names none.

`_diffs` does not treat a null claim effort as a contradiction when that
compound effort stays in the identity and the reading did not state an
effort column. A claim that names an effort still has to match it.

`_verify_evidence_reading` refuses a claim when two compound readings share
a token set that equals a claim name. The matcher returns the order that
normalises to the stored string and does not see the other order.
Confirmation would otherwise write that row.

## Why the other two functions were not the ownership change

`split_model_cell` cannot own a reordered token set unless every name is
sorted. Sorting every name would also own `Beta Alpha` for `Alpha Beta`.
That case stays refused. The function changed only so `_diffs` can read the
effort word it already asks for.

`structured_name_effort` does not decide ownership. Returning `High` before
a comma would make the writer refuse the row before verify. The stage-3
gate in `scripts/refresh_leaderboards.py` (lines 872–878) treats a dataset
effort the stored name does not spell as
`dataset names an effort the stored name does not`.
`_effort_spelled_by_stored_name` (lines 2642–2655) does not spell `high` on
a slug whose last token is `32k`. `model-high-32k` stays unnamed.

## Writer file

`scripts/refresh_leaderboards.py` was not edited. The number write does not
need it. Copying `high` onto a null card still needs those two spots and
`_copy_matched_reading` (lines 764–772). That function writes effort from
`observation.reading_effort` or from the stored slug. The stage-3 path does
not set `reading_effort`, and the slug has no parenthesis, so the card
effort stays null.

## Tests

Python 3.12.3, pytest 9.2.0, Git 2.43.0. Serial, `-q -p no:cacheprovider`,
no `-n`. Exit codes read directly. No full local suite. The interpreter path
is omitted.

### Red, before the production change

Exit 1. 5 failed, 7 passed, in 0.73s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_arena_compound_qualifier.py
```

`test_a_compound_parenthesis_names_high_and_keeps_every_token`:
`split_model_cell` effort was `None`, asserted `high`.

`test_a_compound_high_row_is_the_one_the_verifier_reads`: one `RowFailure`.
Unit expected the compound row's Arena score and found the bare sibling's.
Interval, `n`, and score found `None` against the compound row.

`test_a_stated_high_effort_matches_the_compound_row`: the same bare sibling,
plus effort expected `high` found `None`.

`test_a_thinking_budget_row_is_not_the_bare_sibling`: the bare sibling
again. Unit, interval, `n`, and score found `None` against the thinking row.

`test_two_rows_with_one_token_set_are_refused`: `failures` was empty.
`values_changed` was 1. The reordered parenthesis normalises to the stored
string, so the write succeeded.

The other seven tests passed on that unchanged code: a stated `max` effort,
the bare stored name, a different thinking budget, a high name without the
context size, a different parenthesis date, a reordered name with no
compound parenthesis, and a single `(High)`.

### Green

Same command. Exit 0. 12 passed in 0.45s.

Then, still serial:

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py
```

Exit 0. 457 passed in 2.74s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py
```

Exit 0. 141 passed in 11.45s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_writer_isolation.py
```

Exit 0. 288 passed, 8 skipped, in 9.29s.

`tests/test_arena_compound_qualifier.py` had no row in
`tests/shard_durations.json`. Measured coverage of the suite was 367/387,
under the 0.95 gate in
`test_shard_timings_cover_the_current_suite_and_browser_modules`. A JUnit
run of this file alone sums to 0.141 seconds. That row is now in the
durations file. The coverage test then passed, 1 in 0.29s.

## Callers

`_reading_subject_matches` is also called from `compare`,
`_verify_evidence_reading`, `_llm_published_subject`, and the general
`verify` loop. The new match applies only when the subject has exactly one
compound parenthesis and its full token set equals a claim name. No name in
`tests/test_decision_verify.py` changed result.

## What was not observed

No full local suite. No live board. No private card value. CI was not
checked when this note was written. `scripts/refresh_leaderboards.py` was
not changed. `structured_name_effort("example-model-high")` is still `None`.
`split_model_cell("model-high-32k")` effort is still `None`.
