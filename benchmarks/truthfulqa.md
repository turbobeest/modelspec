---
id: truthfulqa
name: TruthfulQA
aliases: []
page_kind: benchmark
category: safety
subcategory: truthfulness / imitative falsehood
status: unknown
summary: 817 questions written to bait a model into repeating common human misconceptions, testing truthfulness rather than raw knowledge.
measures: >-
  TruthfulQA gives a model 817 questions across 38 categories - including health, law, finance,
  politics, and topics like conspiracies and superstitions - that were specifically written because
  some humans would answer them falsely due to a popular misconception. It measures whether a model
  repeats that popular falsehood or gives the truthful answer, which the original paper
  distinguishes from ordinary factual-knowledge testing: a model can "know" the correct fact
  internally and still be more likely to output the popular wrong answer, because that is the
  pattern most rewarded in its training text.
task_format: Multiple-choice (pick the true statement from several) and free-form generation, over 817 fixed questions across 38 categories.
metric:
  name: MC1 / MC2 accuracy, or GPT-judge truthful-and-informative rate
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: 94.0
  baseline_note: MC1 scores whether the model assigns the single highest probability to the one correct answer among several options. MC2 is the normalized total probability mass the model puts on all correct answers versus all answers. The generation setting instead scores free-form answers with fine-tuned "GPT-judge" and "GPT-info" classifiers (reported at 90-95% agreement with human raters in the original paper) or with similarity metrics such as BLEURT, ROUGE and BLEU. The paper reports the best model of its time was truthful on 58% of questions against a human baseline of 94%.
dataset:
  size: 817
  size_note: 817 questions across 38 categories; an October 2021 update added roughly 300 additional reference answers to the answer keys.
  url: https://github.com/sylinrl/TruthfulQA
  license: Apache-2.0
  languages:
  - en
  modalities:
  - text
  splits: single validation split
  public_test_set: true
publisher:
  org: not established (academic collaboration)
  authors:
  - Stephanie Lin
  - Jacob Hilton
  - Owain Evans
  url: https://github.com/sylinrl/TruthfulQA
paper:
  title: 'TruthfulQA: Measuring How Models Mimic Human Falsehoods'
  arxiv: '2109.07958'
  url: https://arxiv.org/abs/2109.07958
  year: 2021
leaderboard_url: ''
repo_url: https://github.com/sylinrl/TruthfulQA
released: '2021-09'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: No current model in this evaluation's grep of recent model cards reports TruthfulQA past a 2024-06 release date, and its main aggregator (Hugging Face's Open LLM Leaderboard) is now archived (see contamination note), so there is no live source to establish a present-day ceiling.
contamination:
  risk: high
  note: The full question set, including correct-answer keys, has been public on GitHub since 2021, giving three-plus years of exposure to training crawls. The dataset was also a fixed component of the original (v1) Hugging Face Open LLM Leaderboard, which is one of the most heavily mirrored and referenced eval sets on the web, further increasing the chance of direct or paraphrased leakage into later training data.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- safety
- truthfulness
- misconceptions
- open-llm-leaderboard
sources:
- url: https://arxiv.org/abs/2109.07958
  title: 'TruthfulQA: Measuring How Models Mimic Human Falsehoods (arXiv abstract)'
  accessed: '2026-09-07'
- url: https://github.com/sylinrl/TruthfulQA
  title: sylinrl/TruthfulQA GitHub repository
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/truthfulqa/truthful_qa
  title: truthfulqa/truthful_qa dataset card
  accessed: '2026-09-07'
- url: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
  title: Hugging Face Open LLM Leaderboard (marked "Archived")
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

TruthfulQA is built around a specific trap: its 817 questions, spanning 38 categories from health and law to conspiracies and superstitions, were chosen because some humans answer them falsely due to a popular misconception, not because the true answer is obscure or hard to find. The paper's point is that a language model trained to predict likely human text will tend to reproduce the popular wrong answer even when a correct answer is well represented in its training data, which is a different failure from simply not knowing something. A model that scores well here is resisting the pull of common misinformation, not demonstrating broader expertise.

## How it is scored

TruthfulQA supports two evaluation styles. The multiple-choice setting reports MC1 (does the model put its single highest probability on the one correct answer) and MC2 (what fraction of the model's total probability mass lands on any correct answer versus any incorrect one). The generation setting has the model write a free-form answer, which the original paper scores with fine-tuned "GPT-judge" and "GPT-info" classifier models, reporting 90-95% agreement with human judgments, alongside simpler similarity metrics like BLEURT, ROUGE and BLEU. The paper's headline result - the best contemporary model was truthful on 58% of questions, against a 94% human baseline - used the generation setting.

## Dataset and licence

The dataset is 817 questions across 38 categories, released under the Apache-2.0 licence, with a 2021 update that added around 300 extra reference answers to improve the answer keys. All questions, categories, and answer keys are public in the GitHub repository and the Hugging Face dataset card.

## Who publishes it

TruthfulQA comes from Stephanie Lin, Jacob Hilton and Owain Evans, published at ACL 2022 as "TruthfulQA: Measuring How Models Mimic Human Falsehoods," first posted to arXiv in September 2021. The GitHub repository `sylinrl/TruthfulQA` remains the reference source for the question set and scoring scripts; no actively maintained public leaderboard specifically for TruthfulQA was found.

## Lineage

TruthfulQA was one of the original four tasks on Hugging Face's first Open LLM Leaderboard, alongside ARC, HellaSwag and MMLU. A grep of this repository's own model cards shows no model released after mid-2024 reporting a TruthfulQA score, and the Hugging Face Open LLM Leaderboard space is now marked "Archived," which together suggest TruthfulQA has fallen out of routine use by frontier labs even though no single named successor benchmark was found to have formally replaced it.

## Saturation and contamination

Saturation status is unknown rather than confirmed, because the leaderboard that historically tracked TruthfulQA scores across models is archived and no current model in this repository's own corpus reports a recent score to check against a ceiling. Contamination risk is high: the question-and-answer set has been fully public for several years and was a fixture of one of the most widely mirrored eval suites on the internet, making it very likely to appear, directly or paraphrased, in large web-scale training corpora.

## How to run it

The reference `evaluate.py` script in the `sylinrl/TruthfulQA` repository runs both the multiple-choice and generation settings and computes MC1, MC2, and the classifier-based generation metrics. No lm-evaluation-harness or other standard-harness task name was confirmed for TruthfulQA in the sources reviewed for this page, though it was historically included in the first-generation Open LLM Leaderboard's task suite.

## Reading the numbers

A high TruthfulQA score means a model resists repeating popular misconceptions on this specific set of trap questions, which is a narrow slice of what "truthful" or "safe" means in practice. Because the question-and-answer set is old and fully public, a good score today is at least partly explained by direct exposure during training rather than a general resistance to misinformation, so it is best read alongside newer, less-exposed factuality evals rather than on its own. The MC1/MC2 and generation-judge numbers are not interchangeable, so always check which scoring mode a reported number used before comparing across models.
