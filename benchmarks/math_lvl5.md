---
id: math_lvl5
name: "MATH Lvl 5"
aliases: ["MATH Level 5", "MATH-Hard", "leaderboard_math_hard", "math_hard"]
page_kind: subset
category: math
subcategory: "competition mathematics, hardest difficulty level"
status: unknown
summary: "The 1,324 level-5 problems of the MATH test split, 4-shot, exact match: the Open LLM Leaderboard v2 math task. Not MATH-500."
measures: >
  Part of the [MATH](math.md) family. The model is given the hardest tier (level 5 of 5) of the MATH
  test split: 1,324 English competition problems in algebra, counting and probability, geometry,
  intermediate algebra, number theory, prealgebra and precalculus. It sees four worked examples, then
  must write a solution whose final answer matches the reference exactly. It tests multi-step
  symbolic reasoning and strict answer formatting.
task_format: "Free-response, 4-shot Minerva-style prompt; the final answer is compared to the reference by exact match."
metric:
  name: "exact match"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "The Open LLM Leaderboard documentation treats the lower bound as 0 because random generation is unlikely to produce a correct answer. No human baseline for this slice was found."
dataset:
  size: 1324
  size_note: "1,324 test rows in lighteval/MATH-Hard, read from the Hugging Face datasets-server; the same count appears as n-samples in the leaderboard's own results files."
  url: "https://huggingface.co/datasets/lighteval/MATH-Hard"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "test, 1,324 rows over seven subject configs; a 2,304-row train split supplies few-shot material"
  public_test_set: true
publisher:
  org: "Hugging Face (Open LLM Leaderboard); MATH by UC Berkeley"
  authors: []
  url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about"
paper:
  title: "Measuring Mathematical Problem Solving With the MATH Dataset"
  arxiv: "2103.03874"
  url: "https://arxiv.org/abs/2103.03874"
  year: 2021
leaderboard_url: "https://huggingface.co/datasets/open-llm-leaderboard/contents"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/leaderboard/math"
released: "2024-06"
last_updated: ""
lineage:
  family: math
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No top score is recorded here from a source this catalogue can cite."
contamination:
  risk: high
  note: "The MATH test split and its solutions have been public since 2021."
harness:
  lm_eval: "leaderboard_math_hard"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Seven subtasks, leaderboard_math_<subject>_hard, read from the dataset_path lighteval/MATH-Hard in the leaderboard's results files."
tags:
  - math
  - open-llm-leaderboard
  - subset
sources:
  - url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about"
    title: "Open LLM Leaderboard about page: 'We keep only level 5 MATH questions and call it MATH Lvl 5'"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/docs/leaderboards/open_llm_leaderboard/normalization"
    title: "Open LLM Leaderboard normalisation: MATH lower bound 0"
    accessed: "2026-09-24"
  - url: "https://datasets-server.huggingface.co/size?dataset=lighteval/MATH-Hard"
    title: "lighteval/MATH-Hard split sizes (test 1,324, train 2,304)"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/datasets/lighteval/MATH-Hard"
    title: "lighteval/MATH-Hard dataset card (licence MIT)"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/api/datasets/lighteval/MATH-Hard"
    title: "lighteval/MATH-Hard API metadata (created 2024-06-12)"
    accessed: "2026-09-24"
  - url: "https://huggingface.co/datasets/open-llm-leaderboard/results/blob/main/google/mt5-small/results_2025-02-13T18-27-04.338360.json"
    title: "Open LLM Leaderboard results file (config: lighteval/MATH-Hard, 4-shot, exact_match; 1,324 samples)"
    accessed: "2026-09-24"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/leaderboard/math"
    title: "lm-evaluation-harness leaderboard math tasks"
    accessed: "2026-09-24"
freshness:
  researched: "2026-09-24"
  researched_by: "Claude Opus 5.5, MODEL-116"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Part of the [MATH](math.md) family. MATH Lvl 5 keeps only the level-5 problems from the MATH test
split, 1,324 in all, and asks for a free-response answer after four worked examples. The Open LLM
Leaderboard v2 ran it as `leaderboard_math_hard` on `lighteval/MATH-Hard`. It is a different
problem set from [MATH-500](math_500.md). MATH-500 samples all five levels, so scores on the two
are not interchangeable.

## Reading the numbers

Scores in this catalogue are the leaderboard's "MATH Lvl 5 Raw" column times 100. They are not the
normalised "MATH Lvl 5" column. Before MODEL-116 the enrichment scripts stored these values under
`math_500`, which made small open models look far weaker at MATH-500 than they are. Exact match is
strict, so a model that solves a problem but formats the answer differently scores zero on it. An
exact 0.0 can be a real score for a tiny model. It can also mean a run failed: GLM-4-9B scored 0
on every subject here, although its own model card reports 30.4 on MATH. Compare MATH Lvl 5
scores only with other MATH Lvl 5 scores from the same leaderboard run.
