---
id: arena_elo_style_control
name: "Arena Elo — Style Control"
aliases:
  - "Chatbot Arena Style Control"
  - "LMArena Style Control"
  - "Arena Score, style-controlled"
page_kind: subset
category: human-preference
subcategory: "pairwise human preference, style-adjusted"
status: active
summary: "A style-adjusted Arena ranking that regresses out response length and markdown formatting so ratings lean more on substance than presentation."
measures: >
  arena_elo_style_control applies a style adjustment to the same votes and the same Bradley-Terry
  fit used elsewhere in the arena_elo family, rather than drawing on a different vote pool. LMSYS
  adds response length and markdown formatting (header, bold and list counts, each expressed as a
  normalised difference between the two compared responses) as extra regressors in the logistic
  regression that produces Arena ratings, so the resulting model coefficients are adjusted for —
  controlled for — those style effects instead of reflecting them. It can be layered onto Overall
  or onto a category such as Hard Prompts.
task_format: "Same anonymous, randomized side-by-side text chat as the underlying category; ratings are recomputed with response-length and markdown-count features included in the regression."
metric:
  name: "Elo"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Same anchored, open-ended scale as the arena_elo family; style coefficients are reported separately from the model ratings themselves."
dataset:
  size: null
  size_note: "Same live vote corpus as the arena_elo family; no separate vote count for the style-controlled fit was found from a source read for this page."
  url: "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
  license: "CC BY 4.0"
  languages: []
  modalities:
    - text
  splits: ""
  public_test_set: null
publisher:
  org: "LMSYS (Large Model Systems Organization), UC Berkeley Sky Computing Lab (founding org); operates today as Arena (formerly LMArena)"
  authors:
    - "Tianle Li"
    - "Anastasios Angelopoulos"
    - "Wei-Lin Chiang"
  url: "https://arena.ai"
paper:
  title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
  arxiv: "2403.04132"
  url: "https://arxiv.org/abs/2403.04132"
  year: 2024
leaderboard_url: "https://arena.ai/leaderboard/text"
repo_url: "https://github.com/lm-sys/FastChat"
released: "2024-08"
last_updated: "2025-06"
lineage:
  family: arena_elo
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current score snapshot for the style-controlled fit specifically was captured from a source read for this page; see arena_elo_overall for the current state of the unfiltered text leaderboard."
contamination:
  risk: low
  note: "Same as the arena_elo family: prompts are live user submissions, not a fixed, publishable answer key."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness; ratings come only from live votes on the platform, refit with style features included. LMSYS published a Google Colab notebook and vote/style data alongside the original analysis."
tags:
  - human-preference
  - chatbot
  - elo
  - style-control
sources:
  - url: "https://arxiv.org/abs/2403.04132"
    title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (arXiv)"
    accessed: "2026-09-08"
  - url: "https://www.lmsys.org/blog/2024-08-28-style-control"
    title: "Does style matter? Disentangling style and substance in Chatbot Arena (LMSYS blog)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
    title: "lmarena-ai/leaderboard-dataset (Hugging Face dataset card, CC BY 4.0)"
    accessed: "2026-09-24"
  - url: "https://arena.ai/blog/style-control"
    title: "Does Style Matter? (Arena blog, updated republication)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
domains:
  - {id: chat_preference, directness: direct}
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

arena_elo_style_control applies a style adjustment to the same votes and the same Bradley-Terry
fit used elsewhere in the arena_elo family, rather than drawing on a different vote pool. LMSYS
adds response length and markdown formatting (header, bold and list counts, each expressed as a
normalised difference between the two compared responses) as extra regressors in the logistic
regression that produces Arena ratings, so the resulting model coefficients are adjusted for —
controlled for — those style effects rather than reflecting them. It can be layered onto Overall
or onto a category such as Hard Prompts.

## Reading the numbers

Style control exists because length and markdown habits measurably move the plain Arena ranking:
in LMSYS's own analysis, controlling for both moved GPT-4o-mini and Grok-2-mini below most
frontier models, while Claude 3.5 Sonnet, Claude 3 Opus and Llama-3.1-405B-Instruct rose, and
Claude 3.5 Sonnet tied for first in the Hard Prompts subset once style was controlled. A large gap
between a model's plain and style-controlled rating is itself informative: it suggests a
meaningful share of its plain-board standing comes from formatting and verbosity rather than
substance. The authors describe this as a first step, not a causal isolation of style from
quality, since length and genuine quality (for example, a chain-of-thought explanation) can be
correlated for legitimate reasons.

## Source and attribution

Since MODEL-123 this key holds the style-controlled **overall** text board and nothing
else. Values come only from LMArena's Hugging Face dataset
[lmarena-ai/leaderboard-dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset),
licensed **CC BY 4.0**, never from lmarena.ai itself: the `text_style_control` subset,
category `overall`, `latest` split, at the dataset revision pinned in
`api/ranking/engine.py` (`ARENA_SNAPSHOT`). The ranker converts a rating to twice its
expected win rate against that snapshot's leader, so the leader scores 100, and a value
read on any other date does not count. Attribution: LMArena, Arena leaderboard dataset,
CC BY 4.0. The per-category style-controlled boards have their own keys, `arena_sc_*`.
