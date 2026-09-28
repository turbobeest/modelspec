---
id: arena_sc_longer_query
name: Arena Longer Query (style control)
aliases: []
page_kind: subset
category: human-preference
subcategory: pairwise human preference, long prompts
status: active
summary: 'Arena Longer Query (style control): Arena''s crowd-preference rating on its longer query board,
  read from the CC BY 4.0 Hugging Face dataset.'
measures: The style-controlled Arena rating computed only from battles whose prompt Arena labels as a
  longer query. The length threshold is not established from a source read for this page.
task_format: Anonymous side-by-side battles between two models; a person votes for the better response.
metric:
  name: Arena score (Bradley-Terry, Elo scale)
  direction: higher_is_better
  unit: ''
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: Open-ended scale; only differences between models on one board are meaningful.
dataset:
  size: null
  size_note: Live vote corpus; per-model vote counts are in the dataset's vote_count column.
  url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  license: CC BY 4.0
  languages: []
  modalities:
  - text
  splits: latest, full
  public_test_set: null
publisher:
  org: Arena (formerly LMArena, LMSYS)
  authors: []
  url: https://arena.ai
paper:
  title: 'Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference'
  arxiv: '2403.04132'
  url: https://arxiv.org/abs/2403.04132
  year: 2024
leaderboard_url: https://arena.ai/leaderboard
repo_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
released: ''
last_updated: 2026-09
lineage:
  family: arena_elo
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 1524.11
  as_of: 2026-09
  note: Top rating 1524.11 on the 2026-09-13 snapshot. A rating scale has no ceiling; saturation shows
    as the top models overlapping within their confidence intervals.
contamination:
  risk: low
  note: Prompts are live user submissions and votes are collected continuously; there is no fixed answer
    key to leak.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: No offline harness; ratings come only from live votes on Arena.
tags:
- human-preference
- arena
- elo
- style-control
sources:
- url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  title: lmarena-ai/leaderboard-dataset (Hugging Face dataset card, CC BY 4.0)
  accessed: '2026-09-24'
- url: https://arxiv.org/abs/2403.04132
  title: Chatbot Arena (arXiv)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: chat_preference, directness: direct}
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

The style-controlled Arena rating computed only from battles whose prompt Arena labels as a longer query. The length threshold is not established from a source read for this page.

## Reading the numbers

Long prompts are often documents to summarise or rewrite, which is why the summarization profile weights this board. It is still a preference vote, not a faithfulness check. ModelSpec does not use the raw rating. Arena ratings are Bradley-Terry scores on the Elo scale, so only gaps carry meaning. The ranker converts a rating to twice its expected win rate against this board's leader on the pinned snapshot (1524.11 on 2026-09-13), which puts the leader at 100. A value read on any other date does not count. Votes are crowd preferences from Arena users, so a high rating means people preferred the answers, not that the answers were checked.

## Source and attribution

Values come only from LMArena's Hugging Face dataset [lmarena-ai/leaderboard-dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset), licensed **CC BY 4.0**, never from lmarena.ai itself. ModelSpec reads the `text_style_control` subset, category `longer_query`, `latest` split, at dataset revision `1880dbebff5b`. Arena states this board's publish date as 2026-09-13. Attribution: LMArena, Arena leaderboard dataset, CC BY 4.0.
