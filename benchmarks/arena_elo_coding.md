---
id: arena_elo_coding
name: "Arena Elo — Coding"
aliases:
  - "Chatbot Arena Coding leaderboard"
  - "LMArena Coding category"
page_kind: subset
category: human-preference
subcategory: "pairwise human preference, coding prompts"
status: active
summary: "The Arena text leaderboard's Coding category: Elo ratings computed only from anonymous votes on programming-related prompts."
measures: >
  arena_elo_coding restricts the same live, anonymous pairwise-vote pool behind the Arena text
  leaderboard to conversations classified as coding or programming prompts, then fits the
  platform's usual Bradley-Terry rating on that subset alone. It is a category filter selected
  from the leaderboard's own Category view, not a separately collected benchmark, and it is a
  different product from Arena's dedicated Code Arena / WebDev arena, which scores full
  web-app-building tasks rather than filtering the general chat vote pool by topic.
task_format: "Anonymous, randomized side-by-side text chat restricted to prompts tagged as coding or programming; a user votes for the preferred response."
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
  size_note: "Same live vote corpus as the arena_elo family, filtered to conversations tagged as coding-related; no separate published vote count for this slice was found from a source read for this page."
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
  - coding
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

arena_elo_coding is the Coding view of the Arena text leaderboard: the same live, anonymous
pairwise-vote pool behind the overall leaderboard, filtered to conversations tagged as coding or
programming prompts before the platform's Bradley-Terry rating is fit. It is selected from the
leaderboard's own Category control, not a separately collected benchmark. It is also a different
product from Arena's dedicated Code Arena / WebDev arena, which tests models on building complete
web applications rather than filtering general chat votes by topic — the two should not be
confused when reading scores.

## Reading the numbers

A high arena_elo_coding rating says voters preferred that model's responses specifically on
coding-flavoured prompts — it reflects human judgement of a chat response, not execution of the
code against tests, so it is a different kind of signal from a pass@1 score on a code-execution
benchmark. Style is not controlled in this default view, so a model with more thorough or
better-formatted explanations can rate higher independent of whether its code is more correct;
check arena_elo_style_control for a length-and-markdown-adjusted view, and check the reported
confidence interval before treating a small gap between two models as meaningful. Read this
alongside a correctness-checked coding benchmark rather than in place of one.
