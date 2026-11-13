# MODEL-472 compound qualifier

Round 2 starts at `71b95a0824f2768c1fd0193c8f9bc045746c6d60`.
The head is the commit that updates this note. Read it with
`git log -1 --format=%H -- docs/evidence/MODEL-472-compound-qualifier.md`.

Eight Arena rows on four cards were refused because the matcher found a
compound display name and the verifier then read the bare sibling. Three of
those cards sit inside a top 10. Counts only. No card values.

## What changed

Ownership is `_reading_subject_matches` in `decision/verify.py`. A subject
with exactly one compound parenthesis matches a claim name when two parts
agree. The name outside the parenthesis is an ordered token sequence. The
qualifier inside it is a multiset: counts stay, order does not. A subset, a
reordered version, or a repeated token does not match.

A slug has no parenthesis. The compound fallback applies only when the slug holds exactly one eight-digit token that is a valid calendar date (`YYYYMMDD`, a real month and day) and the display name has exactly one compound parenthesis that holds exactly that same date. The slug is cut at that date: tokens before it are the ordered name; tokens after it, plus the date, are the qualifier multiset. On the display side, tokens outside the parenthesis are the ordered name and tokens inside are the qualifier multiset. The pair matches only when the ordered names are equal and the multisets are equal. A slug with no such date or with two or more, a parenthesis with no date or a different one, or a display name with more than one parenthesis: the fallback does not apply, and what `main` does for that pair still happens. An effort word, `thinking`, a size such as `32k`, or a non-date eight-digit token before the date is a name token, so it cannot cross into the qualifier (`acme-orbit-max-20251101-high-32k`, `acme-orbit-32k-20251101-high` and `acme-orbit-12345678-20251101-high-32k` do not match the rows `Acme Orbit (Max, High, 32K, 20251101)`, `Acme Orbit (32K, High, 20251101)` and `Acme Orbit (12345678, High, 32K, 20251101)`; `acme-thinking-2-20251101-high-32k` matches `Acme Thinking 2 (High, 32K, 20251101)` and not `Acme 2 (Thinking, High, 32K, 20251101)`). Normalisation is the same on both sides: `+` becomes ` plus `, case is folded, every other run of non-alphanumeric characters becomes one space.

Known, not introduced here and not fixed here: a few pairs already compare equal on `main` through the older flatten path (`Acme Orbit Max (High, 32K, d)` against `Acme Orbit (Max, High, 32K, d)`, and `... Thinking (32K, d)` against `... (Thinking 32K, d)`). This change neither adds nor removes them. Every pair this change turns from refused to matched is an exact compound row.

`_colliding_compound_identities` uses that same identity. It was
`_colliding_compound_token_sets`. Two compound rows with one identity are
refused.

`split_model_cell` does not strip a compound parenthesis, so its identity
string still cannot express a reordered qualifier. It returns the one effort
word inside the parenthesis and keeps every token, including that word, in
the identity. `Thinking 16K` is not an effort level. `(High)` alone still
strips. A hyphenated slug still names no effort. Sorting every name there
would also own `Beta Alpha` for `Alpha Beta`. That case stays refused.

`structured_name_effort` is unchanged. `(High)` still names `High`.
`example-model-high` still names none. An effort word followed by a comma
still names none.

`_diffs` does not treat a null claim effort as a contradiction when that
compound effort stays in the identity and the reading did not state an
effort column. A claim that names an effort still has to match it.

## Names that still compare equal

Case is folded. Punctuation collapses, as does every other non-alphanumeric
run, so `4.5`, `4-5`, and `4 5` are one sequence. `+` and the word `plus`
are one token. Qualifier order is free, both inside the parenthesis and
after the slug's cut. `(High, 32K, 20251101)`, `(32K, 20251101, High)`, and
`acme-orbit-4-5-20251101-high-32k` are one identity.

`acme-orbit-5-4-20251101-high-32k` against
`Acme Orbit 4.5 (High, 32K, 20251101)` does not compare equal.

## Writer

`scripts/refresh_leaderboards.py` was not edited.

A stored slug does not spell `high`. `_effort_spelled_by_stored_name`
(lines 2642–2655) does not spell it when the last token is `32k`, and
`_verifier_named_effort` (lines 2621–2628) finds no parenthesis on the slug.
The card effort stays null for (a) and (c). Copying `high` onto those cards
would still be the stage-3 gate at lines 872–878 and
`_copy_matched_reading` at lines 764–772. This round does not change them.

A stored id that is the display name itself is different. `split_model_cell`
returns `high` for `(High, 32K, 20251101)`. `_verifier_named_effort` reads
that, and `_copy_matched_reading` writes `effort: high` onto a null card.
`check_score_only` accepts it: null may become the level the unchanged
stored name already spells.

## Tests

Python 3.12.3, pytest 9.2.0, Git 2.43.0. Serial, `-q -p no:cacheprovider`,
no `-n`. Exit codes read directly. No full local suite. The interpreter path
is omitted.

### Round 1, before the first production change

Exit 1. 5 failed, 7 passed, in 0.73s. The five failures were the compound
effort, the High-32K row, a stated `high`, the Thinking-16K row, and two
rows with one token set. The other seven passed on unchanged code.

### Round 1, green

`tests/test_arena_compound_qualifier.py`: exit 0, 12 passed in 0.45s.
`tests/test_decision_verify.py`: exit 0, 457 passed in 2.74s.
`tests/test_leaderboard_refresh.py`: exit 0, 141 passed in 11.45s.
`tests/test_writer_isolation.py`: exit 0, 288 passed, 8 skipped, in 9.29s.

### Round 2, red, before this production change

Exit 1. 3 failed, 14 passed, in 0.52s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_arena_compound_qualifier.py
```

`test_compound_refuses_a_reordered_version`:
`_reading_subject_matches` returned True for
`acme-orbit-5-4-20251101-high-32k`.

`test_compound_refuses_a_version_token_moved_after_the_qualifier`:
returned True for `acme-orbit-4-20251101-high-32k-5`.

`test_compound_refuses_a_repeated_token_collapsing`:
returned True for `Acme Orbit 4.4 (High, 32K, 20251101)` against
`acme-orbit-4-20251101-high-32k`.

The other fourteen passed on that code, including (a), (b), and (c), and
including the display-name effort write. That write was already what the
writer did. This round records it.

### Round 2, green

Same command. Exit 0. 17 passed in 0.56s.

The five new tests: a reordered version is refused and the card is not
written; a version token after the qualifier is refused and the card is not
written; a repeated `4` does not collapse, in the direct call and on the
refresh path; (a), (b), and (c) still own their rows; a stored display name
writes `effort: high` and `check_score_only` accepts it.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py
```

Exit 0. 457 passed in 2.13s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_leaderboard_refresh.py
```

Exit 0. 141 passed in 11.31s.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_writer_isolation.py
```

Exit 0. 288 passed, 8 skipped, in 9.19s.

`tests/shard_durations.json` already has this file at 0.141 seconds. The
0.95 coverage gate does not need a new row.

## Callers

`_reading_subject_matches` is also called from `compare`,
`_verify_evidence_reading`, `_llm_published_subject`, and the general
`verify` loop. The compound match applies only when the subject has one
compound parenthesis. `(Think)` is one token. `(High)` still takes the old
split. No name in `tests/test_decision_verify.py` changed result.

## What was not observed

No full local suite. No live board. No private card value. CI was not
checked when this note was written. `scripts/refresh_leaderboards.py` was
not changed. `structured_name_effort("example-model-high")` is still `None`.
`split_model_cell("model-high-32k")` effort is still `None`.
