# Recall set (MODEL-139 and MODEL-160)

Research phase of slice 1. These files restate the independent audit's 20
questions and record what a correct decision may contain. They are data.
The contract encodings live in `specs/` (MODEL-146).

**Approved by Jamie on 2026-09-25** (MODEL-146 sign-off): the expected
answers in `expected.yaml` are the reference for slice 1. The specs in
`specs/` encode the questions (contract 1.x); `scripts/recall_run.py` scores
the engine against them and writes `docs/recall/<date>-<snapshot>.md`.

`scripts/recall_run.py` remains a report generator. The PR accuracy profile
compares its verdicts with `baseline.json` and gates changes. The baseline from
`origin/main` on 2026-09-25 is 4 pass, 6 partial, and 10 fail.

The allowed transitions only raise the recorded minimum:

- `pass` may stay `pass`.
- `partial` may stay `partial` or become `pass` after the baseline is updated.
- `fail` may stay `fail` or improve after the baseline is updated.

A regression fails the PR accuracy profile. Its report identifies the question,
the verdict transition, and whether the current finding came from missing data
or engine behavior. An improvement also fails until the contributor records the
higher verdict. The failure prints the update command. That command refuses to
record any regression.

The nightly accuracy profile runs the same comparison as a report-only layer.
Weekly leaderboard refresh pull requests wait for the `Decision accuracy`
workflow to pass before they enable auto-merge.

## Baseline

Generate or raise the baseline from a repository snapshot with:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline --date YYYY-MM-DD
```

MODEL-160 created `baseline.json` from `origin/main` at `f6630a62` with:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline --date 2026-09-25
```

Do not edit verdicts by hand. The command runs all 20 specs, records the snapshot
ID and date, and keeps every existing verdict at the same level or higher.

## Approval guard

A pull request that changes `specs/**`, `expected.yaml`, or this approval record
must have the `recall-approved` label. CI reads the pull request's labels and
changed-file list from GitHub. Only Jamie applies that label. Updating
`baseline.json` after an engine or data improvement does not change an approved
spec or expected answer and does not require the label.

## Method

Read on **2026-09-24**. The questions are the audit's twenty probes. The
audit's own shortlists were a starting point only. Each answer was checked
again against a primary page or an independent board. Catalogue ids were
taken from `models/` at `76eabc11`; that tree then fast-forwarded to
`06d77479` (benchmark chart fixtures). The cards cited here did not change.

Allowed evidence:

- Lab launch posts, model docs, pricing pages, and model cards.
- Independent boards whose terms allow reuse: SWE-bench, Terminal-Bench,
  MathArena, Epoch (CC BY 4.0), Scale's SWE-bench Pro V2 leaderboard, MTEB,
  and the Arena dataset `lmarena-ai/leaderboard-dataset` (CC BY 4.0).

Sources named in `tests/test_removed_sources.py` were not used. Arena numbers
come only from that Hugging Face dataset, snapshot published **2026-09-13**,
read 2026-09-24. A null is recorded as unknown. Unknown capability is
`must_flag` (may qualify), not a guess and not a silent drop.

Where two boards disagree, or a score's interval overlaps the next row, the
file says the evidence cannot separate those models. That is an expected
answer, not a missing one.

## Files

- `questions.yaml` — the twenty questions, restated with their constraints.
- `expected.yaml` — per question, the acceptable set, what must never appear,
  what must be flagged, cards that do not exist yet, and notes. Every entry
  has a source URL and the date it was read.
- `baseline.json` — the minimum accepted verdict for each question, plus the
  snapshot ID, date, and command that generated it.
- `test_load.py` — the YAML loads, the twenty ids match, and every entry has
  a source with an ISO date.

## What this does not do

It does not score models, change `/v1/rank`, or treat one model as the winner
when the evidence does not separate them. Catalogue `model_id`s are mapped
from `models/`. A model with no card is listed under `missing_cards` and is
not given an invented id.
