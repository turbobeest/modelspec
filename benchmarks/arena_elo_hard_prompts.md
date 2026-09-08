---
id: arena_elo_hard_prompts
name: "Arena Elo — Hard Prompts"
aliases:
  - "Chatbot Arena Hard Prompts"
  - "LMArena Hard Prompts category"
page_kind: subset
category: human-preference
subcategory: "pairwise human preference, algorithmically hard prompts"
status: active
summary: "An Arena leaderboard built only from votes on prompts an automatic classifier scored as complex and demanding across several hardness criteria."
measures: >
  arena_elo_hard_prompts restricts the same anonymous pairwise-vote pool behind the Arena text
  leaderboard to prompts an automatic classifier scored as demanding. LMSYS defined seven
  hardness criteria — specificity, domain knowledge, complexity, problem-solving, creativity,
  technical accuracy and real-world application — and used Llama-3-70B-Instruct to label whether
  each of over a million Arena prompts met each criterion. Prompts meeting six or more of the
  seven (about 20% of the labelled pool) form the Hard Prompts category, published as separate
  English and Overall (multilingual) leaderboards. A de-duplication step also down-samples very
  common, low-signal prompts (chiefly greetings) before the leaderboard is built.
task_format: "Anonymous, randomized side-by-side text chat restricted to prompts scoring 6 or more of 7 hardness criteria; a user votes for the preferred response."
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
  size_note: "Built from a pool of over 1 million labelled Arena prompts (as of the May 2024 launch post); prompts meeting 6 or more of 7 hardness criteria, about 20% of that pool, qualify for the category."
  url: "https://huggingface.co/lmarena-ai"
  license: ""
  languages: []
  modalities:
    - text
  splits: "Published as two leaderboards: Hard Prompts (English) and Hard Prompts (Overall, multilingual)."
  public_test_set: null
publisher:
  org: "LMSYS (Large Model Systems Organization), UC Berkeley Sky Computing Lab (founding org); operates today as Arena (formerly LMArena)"
  authors:
    - "Tianle Li"
    - "Wei-Lin Chiang"
    - "Lisa Dunlap"
  url: "https://arena.ai"
paper:
  title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
  arxiv: "2403.04132"
  url: "https://arxiv.org/abs/2403.04132"
  year: 2024
leaderboard_url: "https://arena.ai/leaderboard/text"
repo_url: "https://github.com/lm-sys/FastChat"
released: "2024-05"
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
  note: "No current score snapshot for this category specifically was captured from a source read for this page; see arena_elo_overall for the current state of the unfiltered text leaderboard."
contamination:
  risk: low
  note: "Same as the arena_elo family: prompts are live user submissions, not a fixed, publishable answer key."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness; ratings come only from live votes on the platform's Text arena, filtered to this category. The underlying hardness classifier and de-duplication script are open-sourced in the lm-sys/FastChat repository."
tags:
  - human-preference
  - chatbot
  - elo
  - hard-prompts
sources:
  - url: "https://arxiv.org/abs/2403.04132"
    title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (arXiv)"
    accessed: "2026-09-08"
  - url: "https://www.lmsys.org/blog/2024-05-17-category-hard"
    title: "Introducing Hard Prompts Category in Chatbot Arena (LMSYS blog)"
    accessed: "2026-09-08"
  - url: "https://arena.ai/leaderboard/text"
    title: "Text Arena leaderboard (Arena)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

arena_elo_hard_prompts restricts the same anonymous pairwise-vote pool behind the Arena text
leaderboard to prompts an automatic classifier scored as demanding. LMSYS defined seven hardness
criteria — specificity, domain knowledge, complexity, problem-solving, creativity, technical
accuracy and real-world application — and used Llama-3-70B-Instruct to label whether each of over
a million Arena prompts met each one. Prompts meeting six or more of the seven, about 20% of the
labelled pool, form the Hard Prompts category, published as separate English and Overall
leaderboards. A de-duplication step also down-samples very common, low-signal prompts (chiefly
greetings) before the leaderboard is built.

## Reading the numbers

A high arena_elo_hard_prompts rating says a model held up on the more demanding slice of real
user prompts, not just on the easy majority. The category was built specifically because it
reorders models relative to the unfiltered board: at launch, Llama-3-8B-Instruct — rated close to
GPT-4-0314 on the overall English board — dropped sharply here, while Claude 3 Opus moved above
Llama-3-70B-Instruct. Treat a model's Hard-Prompts-versus-Overall gap as a rough signal of how
much of its overall rating rests on easy, low-effort conversations. Style is not controlled in
this default view, so check arena_elo_style_control for a length-and-markdown-adjusted ranking of
this same category, and check confidence intervals before reading small gaps as meaningful.
