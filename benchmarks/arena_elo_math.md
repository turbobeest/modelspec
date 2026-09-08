---
id: arena_elo_math
name: "Arena Elo — Math"
aliases:
  - "Chatbot Arena Math leaderboard"
  - "LMArena Math category"
page_kind: subset
category: human-preference
subcategory: "pairwise human preference, math prompts"
status: active
summary: "The Arena text leaderboard's Math category: Elo ratings computed only from anonymous votes on maths-related prompts."
measures: >
  arena_elo_math restricts the same live, anonymous pairwise-vote pool behind the Arena text
  leaderboard to conversations tagged as maths prompts, then fits the platform's usual
  Bradley-Terry rating on that subset alone. It is a category filter selected from the
  leaderboard's own Category view over the same underlying vote pool as arena_elo_overall, not a
  separately collected benchmark and not a graded-answer test: voters compare two chat responses
  to a maths question and pick the one they prefer, without the platform verifying which answer is
  numerically correct.
task_format: "Anonymous, randomized side-by-side text chat restricted to prompts tagged as maths; a user votes for the preferred response."
metric:
  name: "Elo"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Same anchored, open-ended scale as the arena_elo family: no fixed random baseline or maximum."
dataset:
  size: null
  size_note: "Same live vote corpus as the arena_elo family, filtered to conversations tagged as maths-related; no separate published vote count for this slice was found from a source read for this page."
  url: "https://huggingface.co/lmarena-ai"
  license: ""
  languages: []
  modalities:
    - text
  splits: ""
  public_test_set: null
publisher:
  org: "LMSYS (Large Model Systems Organization), UC Berkeley Sky Computing Lab (founding org); operates today as Arena (formerly LMArena)"
  authors: []
  url: "https://arena.ai"
paper:
  title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
  arxiv: "2403.04132"
  url: "https://arxiv.org/abs/2403.04132"
  year: 2024
leaderboard_url: "https://arena.ai/leaderboard/text"
repo_url: "https://github.com/lm-sys/FastChat"
released: ""
last_updated: ""
lineage:
  family: arena_elo
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No category-specific score snapshot was captured from a source read for this page; see arena_elo_overall for the current state of the unfiltered text leaderboard."
contamination:
  risk: low
  note: "Same as the arena_elo family: prompts are live user submissions, not a fixed, publishable answer key."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness; ratings come only from live votes on the platform's Text arena, filtered to this category."
tags:
  - human-preference
  - chatbot
  - elo
  - math
sources:
  - url: "https://arxiv.org/abs/2403.04132"
    title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (arXiv)"
    accessed: "2026-09-08"
  - url: "https://arena.ai/leaderboard/text"
    title: "Text Arena leaderboard (Arena)"
    accessed: "2026-09-08"
  - url: "https://www.lmsys.org/blog/2024-05-17-category-hard"
    title: "Introducing Hard Prompts Category in Chatbot Arena (LMSYS blog; references the leaderboard's Category dropdown)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

arena_elo_math is the Math view of the Arena text leaderboard: the same live, anonymous
pairwise-vote pool behind the overall leaderboard, filtered to conversations tagged as maths
prompts before the platform's Bradley-Terry rating is fit. It is selected from the leaderboard's
own Category control over the same vote pool as arena_elo_overall, not a separately collected
benchmark. Crucially, a vote here reflects which chat response a person preferred, not whether
either response reached the numerically correct answer — the platform does not grade the maths
itself.

## Reading the numbers

A high arena_elo_math rating says voters preferred that model's responses on maths-flavoured
prompts, which in practice rewards clear, well-explained working almost as much as a correct
final answer, since no automatic checker verifies the arithmetic or proof. That makes it a
different kind of signal from a graded maths benchmark with a fixed answer key: a confident,
readable wrong answer can still beat a terser correct one in a vote. Style is not controlled in
this default view either, so check arena_elo_style_control for a length-and-markdown-adjusted
ranking, and check the reported confidence interval before treating a small gap as meaningful.
Read this alongside an answer-verified maths benchmark rather than in place of one.
