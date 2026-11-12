# MODEL-467 execution evidence

Base `58748fec44f4055a16e37229764f60467278a5a8`.
The evidence commit is the one that adds this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-467-RULE.md`.

A live proposal keeps every card that is not sunset and holds a current top 10, after the quota loop, in `sort_key` order. The quota still limits seats with no board row. `--quota-cuts-top10` restores the approval-time cut. The approved file, from `--check` with no `--data-dir`, still applies that cut, so `premier/slice-1.yaml` is unchanged.

`counts.over_quota_top10` is how many of those seats no other clause would have kept. Supplemental clauses and the time window already keep their own seats, and those seats are not in the count. `counts.over_quota_top10_by_group` is the same count per group. The approved document does not carry either key.

## Tools

Python 3.14.4 and pytest 9.1.1. Ruff 0.16.6. Git 2.50.1.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. The private proposer runs went through the machine-wide heavy lock, one at a time. No local full suite. No site build.

`ruff check scripts/premier_slice1.py scripts/premier_live.py tests/test_premier_live.py` printed `All checks passed!` and exited 0.

## Red

Command, from the worktree, before the keep rule existed. The fixture names below are invented.

```bash
PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_premier_live.py::test_live_keeps_every_current_top_10_past_a_full_quota \
  tests/test_premier_live.py::test_quota_cuts_top10_reproduces_the_approval_time_cut
```

Exit 1. 2 failed in 0.53s.

`test_live_keeps_every_current_top_10_past_a_full_quota` expected fifteen clause 1 seats and got twelve. The three missing seats were `lab/seat-07`, `lab/seat-08`, and `lab/seat-09`.

`test_quota_cuts_top10_reproduces_the_approval_time_cut` raised `AttributeError` because `KEEP_EVERY_CURRENT_TOP10` was missing.

The count test, before `over_quota_top10` skipped seats another clause already keeps:

```bash
PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_premier_live.py::test_over_quota_count_skips_a_top10_another_clause_keeps
```

Exit 1. 1 failed in 0.51s. `over_quota_top10` was 2. The expected value was 1. The time window already kept the newer top 10.

## Green

```bash
PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider \
  tests/test_premier_live.py tests/test_premier_slice1.py
```

Exit 0. 40 passed in 52.29s. That run includes the frozen `--check`.

With the switch on, a frontier group of quota plus three clause 1 cards selects all of them. A clause 2 card in that full group, outside the five-day window, stays a near-miss. A sunset clause 1 card is not selected. With the switch off, the same fixture cuts the three worst `sort_key` seats and the near-miss text is `clause 1 on frontier-generation; outside that group's slice-1 quota`. No live near-miss uses that sentence while the switch is on.

## Private re-run

Both runs used a detached worktree of the private data checkout. The approval-era worktree is the 2026-09-30 seed. The current worktree is current main. Neither private commit is recorded here. The proposer wrote a proposal and a membership diff, an aggregator kept only the counts below, and those files were deleted. The worktrees were removed after this file was written.

The approved file on both checkouts selects 44. Its counts are clause 1 cards 70, clause 2 pool 45, clause 3 pool 7, and missing top-10 rows 0. Selected by group: frontier-generation 18, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1. The quotas are 12, 6, 6, 2, 4, and 1 in that same order.

Approval-era command, as of 2026-09-30, exit 0. The same command with `--quota-cuts-top10` also exited 0.

```bash
python scripts/premier_slice1.py \
  --data-dir <approval-era seed> --as-of 2026-09-30 \
  --output <scratch proposal> --diff <scratch diff>
```

Current command, as of 2026-11-11, exit 0. The same command with `--quota-cuts-top10` also exited 0.

```bash
python scripts/premier_slice1.py \
  --data-dir <current main> --as-of 2026-11-11 \
  --output <scratch proposal> --diff <scratch diff>
```

The switch-off runs match the default-row aggregates in `docs/evidence/MODEL-464-fix.md` for these two catalogues and dates.

### Approval-era, rule on

Selected 43. Clause 1 cards 34. Clause 2 pool 43. Clause 3 pool 8. Missing top-10 rows 0. `over_quota_top10` 2, all frontier-generation. Added 0. Removed 1, and that reason is clause 2 outside the quota. Clause 1 quota near-misses 0. The live window starts 2026-07-02.

Selected by group: frontier-generation 17, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1.

The lineup is 43. That is one seat under the approved 44. The other groups match the approved file. Frontier-generation is 17 against the approved 18.

### Approval-era, rule off

Selected 41. Clause 1 cards 34. Clause 2 pool 43. Clause 3 pool 8. Missing top-10 rows 0. `over_quota_top10` 0. Added 0. Removed 3: clause 1 outside quota 2, clause 2 outside quota 1. Clause 1 quota near-misses 2. The live window starts 2026-07-02.

Selected by group: frontier-generation 15, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1.

The lineup is 41.

### Current, rule on

Selected 44. Clause 1 cards 34. Clause 2 pool 26. Clause 3 pool 8. Missing top-10 rows 0. `over_quota_top10` 3, all frontier-generation. Added 1, and that seat carries clause 2 only. Removed 1, and that reason is clause 2 outside the quota. Clause 1 quota near-misses 0. The live window starts 2026-08-13.

Selected by group: frontier-generation 18, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1.

The lineup is 44, the same size as the approved file, and the group counts match it. Membership still adds one clause 2 seat and removes one clause 2 seat.

### Current, rule off

Selected 41. Clause 1 cards 34. Clause 2 pool 26. Clause 3 pool 8. Missing top-10 rows 0. `over_quota_top10` 0. Added 1, clause 2 only. Removed 4: clause 1 outside quota 3, clause 2 outside quota 1. Clause 1 quota near-misses 3. The live window starts 2026-08-13.

Selected by group: frontier-generation 15, open-weights-generation 13, embedding 6, rerank 2, vision 4, decision 1.

The lineup is 41.

## Not observed

The local full pytest suite was not run. The site build was not run. No card id from the private catalogue, and no private data commit, is in this file.
