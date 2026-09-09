---
id: newsqa
name: NewsQA
aliases: []
page_kind: benchmark
category: knowledge
subcategory: extractive question answering
status: active
summary: NewsQA tests whether a model can answer questions with text spans from CNN news articles, including unanswerable questions.
measures: NewsQA presents a CNN article and a natural-language question written by a crowd worker. The answer is normally a span in the article, but some questions have no answer in context.
task_format: Passage, question, and answer prompt; extract a span or return No Answer.
metric:
  name: exact match over accepted reference strings (HELM)
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: Official human baseline was not established from the sources read.
dataset:
  size: 12744
  size_note: 12,744 stories and over 119,633 question-answer pairs; the source gives split counts of 92,549 train, 5,166 development, and 5,126 test pairs.
  url: https://github.com/Maluuba/newsqa
  license: ""
  languages: [English]
  modalities: [text]
  splits: train, development, test
  public_test_set: false
publisher:
  org: Maluuba Research
  authors: [Akhilesh N. Rao, et al.]
  url: https://github.com/Maluuba/newsqa
paper:
  title: "NewsQA: A Machine Comprehension Dataset"
  arxiv: "1611.09830"
  url: https://arxiv.org/abs/1611.09830
  year: 2016
leaderboard_url: ""
repo_url: https://github.com/Maluuba/newsqa
released: "2016"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: No current authoritative leaderboard was established.
contamination:
  risk: medium
  note: Articles and questions are publicly documented, but the sources read do not establish training-set exposure for current models.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: newsqa
  opencompass: ""
  bigbench: ""
  other: ""
tags: [question-answering, reading-comprehension, extractive]
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/newsqa_scenario.py
    title: HELM NewsQA scenario
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/1611.09830
    title: NewsQA paper
    accessed: "2026-09-08"
  - url: https://github.com/Maluuba/newsqa
    title: Maluuba NewsQA repository
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated)
  reviewed: "2026-09-08"
  reviewed_by: GPT-5.6 Luna independent review, luna-batch-017
---

## What it measures

NewsQA measures reading comprehension over CNN news articles. Given a passage and question, a model must select the answer span supported by that passage. The scenario also retains questions whose consensus says that no answer appears in the passage.

The task is English text question answering. HELM formats each example as `Passage`, `Question`, and `Answer`, while the dataset was created from articles and crowd-authored questions.

## How it is scored

HELM retains consensus and crowd-worker answer strings as references, including unanswerable cases, and its generic generation metrics can score exact match against accepted references. Reporters should state the HELM metric configuration and treatment of “No Answer”; the scenario itself does not define token-level normalization beyond those references.

## Dataset and licence

HELM describes 12,744 stories and more than 119,633 question-answer pairs: 92,549 training, 5,166 development, and 5,126 test pairs. It says the questions and answers were written by crowd workers. The original training data cannot be redistributed directly because of copyright restrictions; the HELM scenario requires obtaining it through the original instructions. A dataset licence was not established.

## Who publishes it

The benchmark is associated with Maluuba Research and the paper “NewsQA: A Machine Comprehension Dataset” (arXiv:1611.09830). The original repository documents data preparation. HELM maintains a runnable scenario, but no current standalone leaderboard was established.

## Lineage

NewsQA is a standalone reading-comprehension dataset. The sources read do not establish a predecessor, successor, or repository variant.

## Saturation and contamination

Saturation is not established. The data and task are public and old, so exposure in training corpora is plausible; the sources read do not quantify that exposure. Article copyright restrictions affect redistribution, but do not by themselves make the evaluation contamination-safe.

## How to run it

HELM’s `newsqa` scenario reads the restricted `combined-newsqa-data-v1.json`, removes questions marked bad, samples one question per article with `random.seed(0)`, and uses train and validation splits. It accepts consensus and crowd-worker answers, including “No Answer”. Prompt construction, reference selection, and sampling choices can change results.

## Reading the numbers

A strong score indicates reliable extraction from the supplied article and handling of missing answers. It does not measure broad factual knowledge without context, current news knowledge, or long-form explanation. Compare the split, answer normalization, and treatment of unanswerable questions before comparing scores. Report the prompt and whether the restricted data were processed exactly as HELM specifies.
