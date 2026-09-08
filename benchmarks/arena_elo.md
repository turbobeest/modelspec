---
id: arena_elo
name: "Arena Elo (Chatbot Arena / LMArena)"
aliases:
  - "Chatbot Arena"
  - "LMArena"
  - "Arena"
page_kind: family
category: human-preference
subcategory: "pairwise human preference"
status: active
summary: "Elo-style ratings of chat models derived from live, anonymous, pairwise human-preference votes on real user prompts."
measures: >
  Arena Elo measures which chatbot response people prefer in head-to-head, blind comparisons —
  a live measurement of human preference on real, unscripted prompts, not accuracy against a
  fixed answer key. A person submits a prompt, receives responses from two anonymised models
  chosen at random, and votes for the one they prefer; model identities are revealed only after
  voting. This repository's subsets cover the overall text leaderboard plus five commonly
  quoted slices: coding, math, a curated "hard prompts" subset, a style-controlled ranking, and
  a separate vision (image+text) leaderboard.
task_format: "Anonymous, randomized side-by-side chat: a user prompts two randomly paired models and votes for the preferred response, or ties/both-bad."
metric:
  name: "Elo"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "No fixed random baseline or maximum: ratings are relative to the pool of models currently rated, on an anchored but open-ended scale."
dataset:
  size: null
  size_note: "No static dataset: a live, ever-growing corpus of anonymous pairwise votes, above 240,000 at the time of the March 2024 paper and far larger since. Historical snapshots are released periodically as open datasets on Hugging Face (lmarena-ai)."
  url: "https://huggingface.co/lmarena-ai"
  license: ""
  languages: []
  modalities:
    - text
    - image
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
  family: ""
  predecessor: ""
  successors: []
  variants:
    - arena_elo_overall
    - arena_elo_coding
    - arena_elo_math
    - arena_elo_hard_prompts
    - arena_elo_style_control
    - arena_elo_vision
saturation:
  status: open
  top_score: null
  as_of: ""
  note: "Ratings are live and continuously updated as new models and votes arrive; frontier models remain within a tight but statistically real band given reported confidence intervals, rather than piled up at a hard ceiling, since an Elo-style scale has no fixed maximum."
contamination:
  risk: low
  note: "Prompts are live user submissions, not a fixed, publishable answer key a model could be trained on in advance. The organisation has instead published its own research on adversarial gaming of leaderboards and on how unreleased models are probed anonymously before launch — a different validity risk from classic train/test leakage."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness: ratings come only from live human votes on the platform (originally served by the open-source FastChat system). The organisation's periodic open vote-data releases and its Arena-Hard-Auto tool approximate arena-style judging offline."
tags:
  - human-preference
  - chatbot
  - elo
  - live-leaderboard
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
    title: "Arena Leaderboard Overview"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Arena Elo measures which chatbot response people prefer in head-to-head, blind comparisons —
a live measurement of human preference on real, unscripted prompts, not accuracy against a
fixed answer key. A person submits a prompt, receives responses from two anonymised models
chosen at random, and votes for the one they prefer; model identities are revealed only after
voting. Prompts come from the platform's own users rather than a curated test set, so the mix
of topics and difficulty shifts over time and by audience. This repository's subset pages
cover the overall text leaderboard plus five commonly quoted slices: coding, math, a curated
"hard prompts" subset, a style-controlled ranking, and a separate vision (image+text)
leaderboard.

## How it is scored

Each vote is a pairwise outcome (A wins, B wins, or tie) between two models. The platform
originally computed ratings with the classic sequential Elo update (the same logistic,
base-10 formula used in chess), but has since moved to a Bradley-Terry model fit by maximum
likelihood over the complete vote history, which treats model strength as fixed and produces
materially more stable ratings with real 95% confidence intervals, rather than ratings that
depend on the order votes happened to arrive in. Ratings sit on an anchored scale with no
fixed maximum, so unlike an accuracy metric there is no "100%" to reach. The Style Control
variant refits the same model after regressing out response length and markdown-formatting
effects, to separate substance from presentation.

## Dataset and licence

There is no static downloadable dataset the way FLORES or MTEB have one: the "dataset" is the
live, ever-growing corpus of anonymous pairwise votes, which stood above 240,000 at the time
of the 2024 paper and has grown enormously since. The organisation periodically releases
historical snapshots of vote and conversation data as open datasets on Hugging Face
(lmarena-ai). A specific licence for the live voting data was not established from a source
read for this page; consult the platform's own Terms of Use and Leaderboard Policy pages for
current terms.

## Who publishes it

Chatbot Arena was launched in April 2023 by LMSYS (Large Model Systems Organization), a group
centred at UC Berkeley's Sky Computing Lab, and first written up in a May 2023 blog post by
Lianmin Zheng, Ying Sheng, Wei-Lin Chiang, Hao Zhang, Joseph E. Gonzalez and Ion Stoica. The
formal paper, "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference" (arXiv,
March 2024; ICML 2024), adds Anastasios Nikolas Angelopoulos, Tianle Li, Dacheng Li, Banghua
Zhu and Michael Jordan to the author list. The project later spun out as its own company,
rebranding first to LMArena and, by 2026, operating as Arena at arena.ai.

## Lineage

Arena Elo has no single predecessor benchmark; its founders cite the general-purpose Elo
rating system from chess and note that an earlier Anthropic paper had already applied
Elo-style rating to language models. In this repository, `arena_elo_overall` is the headline
text leaderboard, and `arena_elo_coding`, `arena_elo_math`, `arena_elo_hard_prompts`,
`arena_elo_style_control` and `arena_elo_vision` are its category and modality subsets. The
platform has since spawned related, separately named efforts from the same organisation —
Arena-Hard-Auto (an offline, judge-based proxy), RouteLLM, Search Arena, and dedicated WebDev,
Document and Text-to-Image arenas — none of which are in scope for this family page.

## Saturation and contamination

Ratings are live and continuously updated as new models and votes arrive, and frontier models
remain within a tight but statistically real band given their reported confidence intervals,
rather than piled up at a hard ceiling — there is no fixed maximum on an Elo-style scale, so
"saturation" in the sense a fixed-answer benchmark uses the word does not quite apply.
Contamination in the train/test-leakage sense is low, since prompts are not a fixed,
publishable answer key a model could be trained on in advance. The live-voting format brings a
different validity risk instead: the organisation has published its own research on
adversarial gaming of leaderboards and on how private, unreleased models are probed anonymously
in the arena before launch, both of which affect how much to trust a ranking rather than
whether the test set leaked.

## How to run it

There is no offline harness: ratings come only from live human votes on the platform,
collected through its own web interface (originally served by the open-source FastChat
system). A team cannot "run" Arena Elo against its own model outside the live platform, though
the organisation's periodic open vote-data releases and its Arena-Hard-Auto tool let
researchers approximate arena-style preference judging offline, without new live human votes.
Numbers are hard to compare across snapshots because the pool of competing models, the prompt
mix, and the rating method itself (sequential Elo before 2024, Bradley-Terry since) have all
changed over the platform's history.

## Reading the numbers

A model's Arena Elo score reflects what a broad, self-selected population of platform users
preferred on the prompts they happened to submit, filtered through whichever category
(coding, math, hard prompts) and style-control setting you are looking at — it is not an
accuracy score and does not verify correctness, only preference. Always check the reported
confidence interval before treating a small ranking gap as meaningful: intervals of several
points or more are common, and two overlapping intervals mean the ranking between those models
is not statistically settled. Prefer the style-controlled and hard-prompts views over the raw
overall score if you specifically want to filter out response-length and formatting bias.
