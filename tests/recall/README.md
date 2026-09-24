# Recall set (MODEL-139)

Research phase of slice 1. These files restate the independent audit's 20
questions and record what a correct decision may contain. They are data.
They do not encode the decision contract. That waits on MODEL-135.

**Jamie approves this set before it gates anything.** Nothing here fails a
build, blocks a merge, or defines a passing decision until that approval.

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
