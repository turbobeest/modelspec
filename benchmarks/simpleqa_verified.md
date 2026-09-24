---
id: simpleqa_verified
name: SimpleQA Verified
aliases:
- SimpleQA-Verified
page_kind: benchmark
category: knowledge
subcategory: short-form factual recall
status: active
summary: 1,000 short factoid questions from Google's cleaned-up SimpleQA; ModelSpec holds Epoch AI's proportion-correct
  score.
measures: 'SimpleQA Verified asks 1,000 short factual questions with one verifiable answer each, across
  politics, science and technology, art, sports, geography, music and history. It measures parametric
  knowledge: what a model can recall without tools.'
task_format: A single question, answered in free text with no tools; a grader model labels the answer
  correct, incorrect or not attempted.
metric:
  name: proportion correct (Epoch AI protocol)
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: Google's paper reports an F1 of overall-correct and correct-given-attempted; ModelSpec's
    key holds Epoch AI's simple proportion correct, which is a different number.
dataset:
  size: 1000
  size_note: 1,000 prompts.
  url: https://arxiv.org/abs/2509.07968
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: single test set
  public_test_set: true
publisher:
  org: Google (Google DeepMind and Google Research)
  authors:
  - Lukas Haas
  - Gal Yona
  - Giovanni D'Antonio
  - Sasha Goldshtein
  - Dipanjan Das
  url: https://arxiv.org/abs/2509.07968
paper:
  title: 'SimpleQA Verified: A Reliable Factuality Benchmark to Measure Parametric Knowledge'
  arxiv: '2509.07968'
  url: https://arxiv.org/abs/2509.07968
  year: 2025
leaderboard_url: https://epoch.ai/benchmarks/simpleqa-verified
repo_url: ''
released: 2025-09
last_updated: 2026-08
lineage:
  family: ''
  predecessor: simpleqa
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: 2026-09
  note: Epoch AI's runs still separate current models widely; a top score was not recorded here.
contamination:
  risk: medium
  note: The questions are public. Epoch AI suspects one model (Qwen3-Max-Instruct) of contamination and
    says so on its page.
harness:
  other: Epoch AI runs it with Inspect; its implementation is linked from the benchmark page.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- factuality
- knowledge
- hallucination
sources:
- url: https://arxiv.org/abs/2509.07968
  title: SimpleQA Verified (arXiv)
  accessed: '2026-09-24'
- url: https://epoch.ai/benchmarks/simpleqa-verified
  title: SimpleQA Verified (Epoch AI benchmark page)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
---

## What it measures

A model gets a short factual question, such as a date, a name, a number or a place, and must answer from memory. The benchmark targets parametric knowledge and hallucination: a confident wrong answer is the failure it exists to count. Epoch AI reports the topic mix as politics 18%, science and technology 16%, art 15%, sports 12%, geography 11%, music 10%, history 5% and other 14%.

## How it is scored

A grader model labels each answer correct, incorrect or not attempted. Google's paper combines overall accuracy and accuracy on attempted questions into an F1 score. Epoch AI instead reports the simple proportion answered correctly, and since 27 August 2026 it appends an anti-abstention instruction to every question and has retired the scores measured without it. ModelSpec's `simpleqa_verified` key holds Epoch AI's proportion correct. An F1 value from Google's leaderboard or a provider's card is a different number and must not be written under this key.

## Dataset and licence

1,000 prompts, derived from OpenAI's SimpleQA. Google de-duplicated the questions, balanced topics and reconciled answer sources, and improved the autorater prompt. The licence of the question set was not established from a source read for this page.

## Who publishes it

Lukas Haas, Gal Yona, Giovanni D'Antonio, Sasha Goldshtein and Dipanjan Das at Google published it on 9 September 2025 (arXiv 2509.07968, revised 10 March 2026). Google maintains the official leaderboard. Epoch AI runs its own evaluations of current models and publishes them in its benchmark data under CC BY 4.0.

## Lineage

It succeeds OpenAI's SimpleQA (`simpleqa`), fixing noisy and incorrect labels, topic bias and redundant questions. It replaces the proposed Artificial Analysis Omniscience key in the chat profile: both measure short-form factual recall, and no profile weight may rest on Artificial Analysis (MODEL-117).

## Saturation and contamination

Scores on current models still spread widely, so it is not saturated. The questions are public, so training contamination is possible; Epoch AI flags a suspected case on its page. The anti-abstention change raised scores for models that used to decline often, so scores from before and after 27 August 2026 are not comparable.

## How to run it

Epoch AI's implementation is linked from its benchmark page, and the paper links the dataset, code and leaderboard. Results depend on the grader model and on whether an anti-abstention instruction is used, so a number is only comparable with numbers from the same protocol.

## Reading the numbers

A high score means the model recalls many specific facts; it does not mean the model knows when it does not know, because Epoch AI's protocol asks it to guess. Read it beside a model's refusal behaviour if hallucination risk is the concern. It says nothing about reasoning or retrieval with tools.
