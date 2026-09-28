---
id: arena_sc_industry_software_it_services
name: Arena Software and IT Services (style control)
aliases: []
page_kind: subset
category: human-preference
subcategory: pairwise human preference, software and IT occupation category
status: active
summary: 'Arena Software and IT Services (style control): Arena''s style-controlled preference rating
  over software and IT services prompts.'
measures: Arena's style-controlled preference rating over software and IT services prompts.
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
  size_note: Live vote corpus; each row reports its vote count.
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
  top_score: null
  as_of: 2026-09
  note: A rating scale has no ceiling; overlapping intervals indicate weak separation.
contamination:
  risk: low
  note: Prompts are live user submissions and votes have no fixed answer key to leak.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: No offline harness; ratings come from Arena votes.
tags:
- human-preference
- arena
- elo
sources:
- url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  title: lmarena-ai/leaderboard-dataset (CC BY 4.0)
  accessed: '2026-09-27'
- url: https://arxiv.org/abs/2403.04132
  title: Chatbot Arena (arXiv)
  accessed: '2026-09-27'
freshness:
  researched: '2026-09-27'
  researched_by: Codex GPT-5, MODEL-191
  reviewed: ''
  reviewed_by: ''
domains:
- id: chat_preference
  directness: direct
- id: software_engineering
  directness: proxy
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

Arena's style-controlled preference rating over software and IT services prompts. The value measures preference, not correctness.

## Reading the numbers

The rating is a Bradley-Terry score on an Elo scale. Compare values only within this board and
the same observation. ModelSpec keeps the board's confidence interval and vote count in each
evidence row. The source observation used for this page was read on 2026-09-27.

## Source and attribution

Values come only from the pinned [LMArena Hugging Face dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset), licensed CC BY
4.0. ModelSpec reads config `text_style_control`, category `industry_software_and_it_services`, split `latest`, at
revision `1880dbebff5ba3e2dd3865ecf6fc43539c2099db`. The board states its own publication date per row.
