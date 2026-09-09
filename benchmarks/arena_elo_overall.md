---
id: arena_elo_overall
name: "Arena Elo — Overall (Text)"
aliases:
  - "LMArena Overall"
  - "Chatbot Arena Overall leaderboard"
page_kind: benchmark
category: human-preference
subcategory: "overall text leaderboard"
status: active
summary: "The headline, non-style-controlled Elo ranking of chat models on the Arena (LMArena / Chatbot Arena) text leaderboard."
measures: >
  arena_elo_overall is the headline column on the Arena text leaderboard: an Elo-style rating
  built from anonymous, pairwise human votes across all text-chat conversations on the
  platform, with no filtering by topic and no adjustment for response style or length. It is
  the single number most "who's #1" claims about chat models are based on.
task_format: "Anonymous, randomized side-by-side text chat across all topics; a user votes for the preferred response, feeding one platform-wide rating per model."
metric:
  name: "Elo"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "No fixed random baseline or maximum; ratings are relative to the current pool of rated models."
dataset:
  size: null
  size_note: "Same live, ever-growing vote corpus as the arena_elo family, filtered to the Text arena (as opposed to the platform's separate Vision, WebDev, Document, Text-to-Image and Agent arenas)."
  url: "https://huggingface.co/lmarena-ai"
  license: ""
  languages: []
  modalities:
    - text
  splits: ""
  public_test_set: null
publisher:
  org: "LMSYS (Large Model Systems Organization), UC Berkeley Sky Computing Lab (founding org); operates today as Arena (formerly LMArena)"
  authors:
    - "Wei-Lin Chiang"
    - "Lianmin Zheng"
    - "Ying Sheng"
    - "Anastasios Nikolas Angelopoulos"
    - "Tianle Li"
    - "Dacheng Li"
    - "Hao Zhang"
    - "Banghua Zhu"
    - "Michael Jordan"
    - "Joseph E. Gonzalez"
    - "Ion Stoica"
  url: "https://arena.ai"
paper:
  title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
  arxiv: "2403.04132"
  url: "https://arxiv.org/abs/2403.04132"
  year: 2024
leaderboard_url: "https://lmarena.ai/leaderboard"
repo_url: "https://github.com/lm-sys/FastChat"
released: "2023-04"
last_updated: ""
lineage:
  family: arena_elo
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 1507
  as_of: "2026-09"
  note: "On access, the top of the overall text leaderboard clustered tightly: the leading model held a rating of 1507 (±5), with several others within about 15 points and overlapping confidence intervals — consistent with an open, still-separating field rather than a saturated one. There is no fixed ceiling on an Elo-style scale."
contamination:
  risk: low
  note: "Prompts are live user submissions, not a fixed answer key; see the arena_elo family page for the live-voting gaming concerns that apply here too."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness: this figure comes only from live votes on the Text arena, aggregated by the platform's own Bradley-Terry pipeline. Historical vote snapshots on Hugging Face (lmarena-ai) let researchers refit ratings offline but cannot add new votes."
tags:
  - human-preference
  - chatbot
  - elo
  - overall
sources:
  - url: "https://arxiv.org/abs/2403.04132"
    title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (arXiv)"
    accessed: "2026-09-07"
  - url: "https://www.lmsys.org/blog/2023-05-03-arena/"
    title: "Chatbot Arena: Benchmarking LLMs in the Wild with Elo Ratings (LMSYS blog, founding post)"
    accessed: "2026-09-07"
  - url: "https://arena.ai/how-it-works"
    title: "How It Works (Arena)"
    accessed: "2026-09-07"
  - url: "https://lmarena.ai/leaderboard"
    title: "Arena Leaderboard Overview (Text: Overall board read on access date)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

arena_elo_overall is the headline column on the Arena (formerly Chatbot Arena / LMArena) text
leaderboard: an Elo-style rating built from anonymous, pairwise human votes across all
text-chat conversations on the platform, with no filtering by topic and no adjustment for
response style or length. It is the single number most "who's #1" claims about chat models
are based on.

## How it is scored

Votes across every text conversation category feed one Bradley-Terry fit (maximum likelihood
over the full vote history), producing a rating and a 95% confidence interval per model.
Unlike the coding, math and hard-prompts subsets, arena_elo_overall does not filter which
prompts count; unlike arena_elo_style_control, it does not adjust for response length or
markdown formatting, so a model that tends to produce longer or more heavily formatted answers
can rate higher here even where a style-controlled comparison would narrow the gap.

## Dataset and licence

Same live, ever-growing vote corpus as the arena_elo family, filtered to the Text arena
specifically (as opposed to the platform's separate Vision, WebDev, Document, Text-to-Image
and Agent arenas). No fixed size or public licence for the underlying vote data was
established from a source read for this page; periodic historical snapshots are released as
open datasets on Hugging Face (lmarena-ai).

## Who publishes it

Same organisation as the family page: launched April 2023 by LMSYS at UC Berkeley, formally
described in "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference" (arXiv,
March 2024; ICML 2024), and operated today as Arena (arena.ai), following an interim LMArena
rebrand.

## Lineage

arena_elo_overall is the `arena_elo` family's default, unfiltered view; its siblings in this
repository are `arena_elo_coding`, `arena_elo_math`, `arena_elo_hard_prompts`,
`arena_elo_style_control` and `arena_elo_vision`. It has no separate predecessor or successor
of its own.

## Saturation and contamination

As of this page's access on 2026-09-07, the top of the overall text leaderboard clustered
tightly: the leading model held a rating of 1507 (±5), with several others within about 15
points and overlapping confidence intervals, consistent with an open, still-separating field
rather than a saturated one — there is no fixed ceiling on this scale. Contamination risk is
low in the train/test sense (see the family page); the same live-voting gaming concerns apply.

## How to run it

No offline harness reproduces this figure; it comes only from live votes on the Text arena,
aggregated by the platform's own Bradley-Terry pipeline. Historical vote snapshots on Hugging
Face (lmarena-ai) let researchers refit ratings offline for research purposes, but cannot add
new votes.

## Reading the numbers

Because arena_elo_overall folds in every topic and does not control for style, treat it as a
broad popularity-and-helpfulness signal rather than a capability score: a model can rank
highly here partly because of formatting and verbosity habits that arena_elo_style_control
would discount. Always check the confidence interval before reading a small gap as meaningful,
and cross-reference arena_elo_hard_prompts or a specific category subset if you care about a
harder or narrower slice of ability than "overall."
