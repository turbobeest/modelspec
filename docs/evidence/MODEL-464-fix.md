# MODEL-464 execution evidence

Base `d38f02f02067af4be58004d9956f0b89269c1d97`.
Worktree `/Users/terbeest/dev/worktrees/model-464`, branch `model-464`.

The evidence commit is the one that adds this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-464-fix.md`.

Item commits:

- Clause 1 ranks only the named slice-1 boards. That commit refused a board under 11 rows. The review default admits a short board. `28391c78e0f60c64e750f4f290f50f0dbafafdf1`
- Clause 3 counts the providers on the card, unioned with offerings. `c5cee39ca65103e4e2ddd14c30a3c31f9c272443`
- The vision fixture call is wrapped to the 100 character line limit. `9dd4e2909a4a87fe899d870f1273f81bf63c92d9`

## Tools

Python 3.14.4 and pytest 9.1.1 from `/Users/terbeest/dev/modelspec/.venv/bin/python`. Ruff 0.16.6. Git 2.50.1.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. The private proposer runs went through `~/.codex-g2/heavy.sh`. No local full suite. No site build.

`ruff check scripts/premier_slice1.py scripts/premier_live.py tests/test_premier_live.py` printed `All checks passed!` and exited 0.

The frozen suite below was run after the clause 1 commit. A later commit changed the row-count default. Its checks are in Default row minimum.

## Clause 1

Command, from the worktree, before the clause 1 change:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py
```

Red, exit 1. 5 failed, 16 passed in 3.38s.

- `test_live_board_respects_direction_versions_and_model_identity`
- `test_live_vision_domain_keeps_the_existing_vision_quota` expected `vision` and got `frontier-generation`
- `test_board_shorter_than_the_top_10_admits_nobody`
- `test_unmapped_benchmark_does_not_open_a_board`
- `test_named_board_with_ten_rows_selects_nobody`

The same command after the change exited 0. 22 passed in 2.64s.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_slice1.py
```

Exit 0. 7 passed in 48.03s. That run includes the frozen `--check`.

After that commit, a live proposal required 11 rows and the frozen check used `APPROVED_LINEUP_MINIMUM_ROWS` of 1. The review default is now `APPROVED_LINEUP_MINIMUM_ROWS`, which is 1. A board of any length admits its top 10. `STRICT_CLAUSE1_ROWS` is 11, and it applies only when `STRICT_BOARD_ROWS` is on. `--check` and a live proposal both follow that switch. The checked lineup file is unchanged.

## Clause 3

The five new clause 3 tests, run before the clause 3 change, exited 1. 5 failed, 22 deselected in 0.62s.

- `test_card_recorded_providers_satisfy_clause_3` raised `StopIteration`
- `test_lab_api_switch_drops_a_card_that_reaches_three_only_through_it` raised `AttributeError` because `COUNT_LAB_API` was missing
- `test_an_offering_fills_out_the_card_providers` raised `StopIteration`
- `test_cite_only_guaranteed_facts_follow_the_approved_switch` raised `StopIteration`
- `test_fixture_follows_the_approved_rule` was missing `shelf/wide-model`

The full live file after the change exited 0. 27 passed in 2.81s. The same command after the line wrap exited 0. 27 passed in 2.78s.

`COUNT_LAB_API` and `CITE_ONLY_FACTS_COUNT_AS_VERIFIED` both default to true. Card providers stay, offerings in the major-provider set are unioned in, and a cite-only guaranteed fact counts when the verification log records it. Setting either switch to false is the stricter check.

A snapshot citation does not count unless that log records the fact. `test_snapshot_cited_fact_without_log_verification_does_not_count` failed while the citation-status branch was still there. The focused command was:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py::test_snapshot_cited_fact_without_log_verification_does_not_count
```

Exit 1. 1 failed in 1.20s. The fixture card was selected on clause 3.

The same file after the branch was removed:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py
```

Exit 0. 28 passed in 3.05s. `ruff check scripts/premier_live.py tests/test_premier_live.py` printed `All checks passed!` and exited 0. The switch test still shows that setting `CITE_ONLY_FACTS_COUNT_AS_VERIFIED` to false refuses a cite-only card the log did verify.

## Private re-run

This section records the run that required 11 rows. The default no longer requires that. The strict switch reproduces these aggregates. The default run is in Default row minimum.

Both runs used a detached worktree of the private data repo. The approval-era worktree is the approval-era seed. The current worktree is current main. Neither commit hash is recorded here. The proposer wrote a proposal file and a membership diff, an aggregator kept only the counts below, and those files were deleted. The worktrees were removed after this file was written.

Approval-era command, as of 2026-09-30, exit 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/premier_slice1.py \
  --data-dir <approval-era worktree> --as-of 2026-09-30 \
  --output <scratch proposal> --diff <scratch diff>
```

Current command, as of 2026-11-11, exit 0. A pass dated 2026-11-10 was discarded. The counts below are the 2026-11-11 run that required 11 rows.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/premier_slice1.py \
  --data-dir <current main worktree> --as-of 2026-11-11 \
  --output <scratch proposal> --diff <scratch diff>
```

The approved file on the approval-era checkout selects 44. Its counts are clause 1 cards 70, clause 2 pool 45, clause 3 pool 7, and missing top-10 rows 0. Selected by quota: frontier-generation 18, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1. The file quotas are 12, 6, 6, 2, 4, and 1 in that same order. Its release window starts 2026-06-26.

Approval-era proposer, as of 2026-09-30, on the run that required 11 rows. Selected 31. Clause 1 cards 22. Clause 2 pool 37. Clause 3 pool 8. Added 0. Removed 13. Selected by quota: frontier-generation 15, open-weights-generation 11, embedding 0, rerank 0, vision 4, decision 1. The live window starts 2026-07-02. Eight selected models carry clause 3. The approved file has 7 selected models that carry clause 3.

Current proposer, as of 2026-11-11, on the run that required 11 rows. Selected 31. Clause 1 cards 22. Clause 2 pool 24. Clause 3 pool 8. Added 1, and that seat is clause 2 only. Removed 14. Selected by quota matches the approval-era run: frontier-generation 15, open-weights-generation 11, embedding 0, rerank 0, vision 4, decision 1. The live window starts 2026-08-13. Eight selected models carry clause 3.

The clause 2 pools differ across two catalogues and two window starts, 2026-07-02 and 2026-08-13.

## Approval-era differences

These differences are from the run that required 11 rows.

Every one of the 13 absences is a named clause. Removed-reason counts: clause 1 outside quota 1, clause 2 outside quota 2, no current clause 10.

Nine approved clause 1 seats have no current clause on that run. Each live board has fewer than 11 rows, which that run required, so clause 1 admits nobody there.

One approved clause 1 seat is still in a live top 10 and is outside its group quota.

Two approved seats had clauses 1 and 2 and lost clause 1 on that run because each live board has fewer than 11 rows. Both releases are on or after 2026-07-02. One of those labs still has a clause 1 model, so the seat remains clause 2 and is outside that quota. The other lab has no clause 1 model left, so clause 2 does not apply and the seat has no current clause.

One approved clause 2 seat has no clause 1 board and is outside the clause 2 quota.

None of the 13 is a seat whose only clause 1 boards are the two named boards that have no mapped evidence benchmark id. The quota gaps against the approved 44 are frontier-generation 3, open-weights-generation 2, embedding 6, and rerank 2. Those four gaps sum to 13.

The review re-ran the approval-era command above after the snapshot-cited branch was removed. Exit 0. The aggregates are the same: selected 31, clause 1 cards 22, clause 2 pool 37, clause 3 pool 8. Selected by quota is unchanged: frontier-generation 15, open-weights-generation 11, embedding 0, rerank 0, vision 4, decision 1. Added 0. Removed 13. The detached worktree was removed after these counts were taken.

Clause 1 cards fall from 70 to 22. Forty-nine approved clause 1 cards are absent and one card enters. Thirty-seven of the absent cards rank only on boards with fewer than 11 rows, which that run required. One of those 37 ranks only on a named board that has no mapped evidence benchmark id. The other 12 do not appear on the live rows of a board that still has at least 11 rows.

Clause 2 pool falls from 45 to 37. Seven approved clause 2 cards belong to a lab with no model on a live clause 1 board. One was released before the live window start, 2026-07-02.

Clause 3 pool rises from 7 to 8. The extra card reaches three providers only after offerings are unioned onto the card. No approved clause 3 card drops out. Eight selected models carry clause 3. The approved file has 7.

## Current differences

These differences are from the run that required 11 rows. That run selected 31.

The run removes 14 approved seats and adds 1 clause 2 seat. Removed-reason counts: clause 1 outside quota 2, clause 2 outside quota 1, no current clause 11.

On that run, nine are clause 1 seats on a board under 11 rows, with no current clause. One clause 1 seat is still in a live top 10 and is outside its quota. Two seats that had clauses 1 and 2 lost clause 1 on a short board and have no current clause. One seat that had both clauses is still in a live top 10 and is outside the clause 1 quota. One clause 2 seat has no clause 1 board and is outside the clause 2 quota.

Of the three seats that had both clauses, two releases are before 2026-08-13 and one is on or after that date. Two of those labs have no clause 1 model left. One lab still has a clause 1 model.

The gap from that run's 31 to the approved 44 is mainly clause 1. Nine of the removed seats rank only on boards with fewer than 11 rows, which that run required, and keep no other clause.

## Default row minimum

`4300692232ca1677510f5a906a2d7495d778ce40` makes the approved lineup's row count the default. A board of any length admits its top 10. `STRICT_BOARD_ROWS` is off unless `--strict-board-rows` is set.

The new test failed on the previous default. `test_five_row_board_admits_its_five_by_default` expected five admitted rows and got five refused rows. `test_board_shorter_than_the_top_10_admits_nobody` raised `AttributeError` because `STRICT_BOARD_ROWS` was missing. Command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py::test_board_shorter_than_the_top_10_admits_nobody tests/test_premier_live.py::test_five_row_board_admits_its_five_by_default
```

Exit 1. 2 failed in 0.28s.

After the change:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py
```

Exit 0. 30 passed in 3.04s.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_slice1.py
```

Exit 0. 7 passed in 49.42s. `ruff check scripts/premier_slice1.py scripts/premier_live.py tests/test_premier_live.py` printed `All checks passed!` and exited 0.

The re-run below uses that default. Both commands exited 0. They went through `~/.codex-g2/heavy.sh`. The proposer wrote a proposal and a membership diff, an aggregator kept the counts, and those files were deleted. The detached worktrees were removed after the counts were taken.

Approval-era command, as of 2026-09-30:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/premier_slice1.py \
  --data-dir <approval-era worktree> --as-of 2026-09-30 \
  --output <scratch proposal> --diff <scratch diff>
```

Current command, as of 2026-11-11:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/premier_slice1.py \
  --data-dir <current main worktree> --as-of 2026-11-11 \
  --output <scratch proposal> --diff <scratch diff>
```

`--report` with no flag still prints the approved counts: selected 44, clause 1 cards 70, clause 2 pool 45, clause 3 pool 7.

Approval-era proposer, as of 2026-09-30. Selected 41. Clause 1 cards 34. Clause 2 pool 43. Clause 3 pool 8. Added 0. Removed 3. Selected by quota: frontier-generation 15, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1. The live window starts 2026-07-02. Eight selected models carry clause 3. The approved file has 7.

Current proposer, as of 2026-11-11. Selected 41. Clause 1 cards 34. Clause 2 pool 26. Clause 3 pool 8. Added 1. Removed 4. Selected by quota matches the approval-era run. The live window starts 2026-08-13. The added seat is frontier-generation and clause 2 only, and the release is on or after 2026-11-06. Eight selected models carry clause 3.

The strict switch on the same catalogues and dates reproduces the earlier run. Approval-era: selected 31, clause 1 cards 22, clause 2 pool 37, clause 3 pool 8. Current: selected 31, clause 1 cards 22, clause 2 pool 24, clause 3 pool 8. Selected by quota on both: frontier-generation 15, open-weights-generation 11, embedding 0, rerank 0, vision 4, decision 1.

The approved file selects 44. Its counts are clause 1 cards 70, clause 2 pool 45, clause 3 pool 7. Selected by quota: frontier-generation 18, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1. Its release window starts 2026-06-26.

Clause 1 is 34 on both catalogues. Thirty-seven approved clause 1 cards have no row on a live named board, and one card enters. Of the 37, 35 are active and 2 are sunset. Thirty-six have approved evidence on a frozen board of at least 11 rows. One has approved evidence only on a board with no mapped evidence benchmark id. The entrant is in the top 10 of a board of at least 11 rows, and the row date is inside the past year. Twelve of the 34 are in the top 10 only on a board under 11 rows. The strict switch drops those 12 and counts 22. Losing 37 and gaining 1 changes the clause 1 count from 70 to 34.

Clause 2 on the approval-era catalogue is 43. One approved card was released before the live window, 2026-07-02. One belongs to a lab with no live clause 1 model. No card enters. Losing 2 changes the clause 2 count from 45 to 43.

Clause 2 on the current catalogue is 26. Twenty-four approved cards were released before the live window, 2026-08-13. One belongs to a lab with no live clause 1 model. Six cards enter that are not in the approval-era catalogue. Losing 25 and gaining 6 changes the clause 2 count from 45 to 26.

Clause 3 is 8 on both catalogues. No approved clause 3 card drops out. The extra card reaches three providers only after an offering is unioned onto the card.

The approval-era selection removes 3 frontier-generation seats and adds none. Two of the removed seats still carry clauses 1 and 2 and sit outside the frontier quota. One carries clause 2 only and sits outside that quota. Every other group matches the approved count. The frontier count goes from 18 to 15.

The current selection removes 4 frontier-generation seats and adds 1. Three removed seats still carry clauses 1 and 2 and sit outside the frontier quota. One removed seat carries clause 2 only and sits outside that quota. The added seat carries clause 2 only and falls inside the five-day protected window. The frontier count goes from 18 to 15. Every other group matches the approved count.

## Not observed

The local full pytest suite was not run. The site build was not run. Pull-request checks were not run when this file was written. No card id, per-card count, or private data commit is in this file.
