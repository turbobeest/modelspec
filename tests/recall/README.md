# Recall answers and frozen-image engine regression test

Research phase of slice 1. These files restate the independent audit's 20
questions and record what a correct decision may contain. They are data.
The contract encodings live in `specs/` (MODEL-146).

**Approved by Jamie on 2026-09-25** (MODEL-146 sign-off): the expected
answers in `expected.yaml` are the reference for slice 1. The specs in
`specs/` encode the questions (contract 1.x); `scripts/recall_run.py` scores
the engine against them and writes `docs/recall/<date>-<snapshot>.md`.

**Approved by Jamie on 2026-09-26** (MODEL-164): the eleven expected-answer
changes documented in
[`docs/recall/2026-09-25-model-161-triage.md`](../../docs/recall/2026-09-25-model-161-triage.md)
are approved.

Jamie decided on 2026-10-01, Q04 option b, that approved answers are judged
against the private data production serves. The private repository runs recall
on every data PR, weekly, and on manual dispatch, with its own baseline at
`reports/recall/baseline.json`. Its summary contains only verdict counts and
question ids. Existing partial answers remain recorded limitations; a drop in
an approved-answer verdict fails the private gate, including a proposed
baseline below the merge-base baseline.

Public CI runs recall as an **engine regression test on the frozen public
image**. `baseline.json` records what that image yields, not a revision of the
approved answers. It currently records 16 pass and 4 partial. Every verdict
below `pass` needs a per-question `frozen_image_reason`. A lower public baseline
requires a new or changed reason explaining the image limitation, with private
recall evidence where available. The current run must still match the proposed
baseline. See [RATCHET.md](RATCHET.md) for the update command and merge-base check.

The expected answers in `expected.yaml` stay unchanged. Changing them or the
specs requires Jamie's approval. The historical sign-offs above still apply.

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
- `test_load.py` — the YAML loads, the twenty ids match, and every entry has
  a source with an ISO date.

## What this does not do

It does not score models, change `/v1/rank`, or treat one model as the winner
when the evidence does not separate them. Catalogue `model_id`s are mapped
from `models/`. A model with no card is listed under `missing_cards` and is
not given an invented id.
