---
id: winogrande
name: WinoGrande
aliases: []
page_kind: benchmark
category: reasoning
subcategory: commonsense coreference resolution
status: unknown
summary: A 44k-problem, adversarially filtered successor to the Winograd Schema Challenge, testing commonsense pronoun resolution at scale.
measures: WinoGrande gives a model a short sentence with a blank that must be filled with one of two candidate nouns or phrases, where picking correctly requires commonsense reasoning about the situation rather than grammar or word association. It scales up the original, hand-crafted 273-problem Winograd Schema Challenge to 44,000 problems using crowdsourcing plus an adversarial filtering algorithm (AfLite) that removes items solvable by superficial statistical shortcuts, specifically to stop models from succeeding via spurious dataset bias rather than genuine commonsense understanding.
task_format: Binary fill-in-the-blank choice between two candidate answers for a short sentence.
metric:
  name: accuracy
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: 50.0
  human_baseline: 94.0
  baseline_note: Accuracy on the two-way choice, with 50% as the random baseline. The original paper reports the best contemporary methods reaching 59.4-79.1% depending on training data size, well below the 94.0% human baseline, and notes that models had already reached about 90% on the older, smaller Winograd Schema Challenge, motivating a larger and harder successor.
dataset:
  size: 44000
  size_note: '44,000 problems total; training splits range from 160 (xs) to 40,398 (xl) examples, with fixed 1,267-item dev and 1,767-item test sets shared across all training sizes.'
  url: https://github.com/allenai/winogrande
  license: CC-BY
  languages:
  - en
  modalities:
  - text
  splits: 'train (xs/s/m/l/xl/debiased variants), validation (1,267), test (1,767, labels held out)'
  public_test_set: false
publisher:
  org: Allen Institute for AI (AI2)
  authors:
  - Keisuke Sakaguchi
  - Ronan Le Bras
  - Chandra Bhagavatula
  - Yejin Choi
  url: https://github.com/allenai/winogrande
paper:
  title: 'WinoGrande: An Adversarial Winograd Schema Challenge at Scale'
  arxiv: '1907.10641'
  url: https://arxiv.org/abs/1907.10641
  year: 2019
leaderboard_url: ''
repo_url: https://github.com/allenai/winogrande
released: '2019-07'
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
  note: A grep of this repository's own model cards found no model released after mid-2024 reporting a WinoGrande score, and the Hugging Face Open LLM Leaderboard space that historically tracked it is now marked "Archived," so there is no current source to establish where today's frontier models sit against the ceiling.
contamination:
  risk: high
  note: The dev set (with labels) has been public since 2019 and was a fixture of the original Hugging Face Open LLM Leaderboard, one of the most widely mirrored eval sets on the web; the official test set labels are held out and require a leaderboard submission, but the dev set alone gives several years of plausible exposure to training crawls.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- commonsense
- coreference
- open-llm-leaderboard
sources:
- url: https://arxiv.org/abs/1907.10641
  title: 'WinoGrande: An Adversarial Winograd Schema Challenge at Scale (arXiv abstract)'
  accessed: '2026-09-07'
- url: https://github.com/allenai/winogrande
  title: allenai/winogrande GitHub repository
  accessed: '2026-09-07'
- url: https://huggingface.co/datasets/allenai/winogrande
  title: allenai/winogrande dataset card
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

WinoGrande tests commonsense reasoning through pronoun and reference resolution: each item is a short sentence with a blank, and two candidate fillers, where only real-world understanding of the situation - not grammar, not word co-occurrence - picks out the right one. It is a large-scale, adversarially filtered descendant of the original Winograd Schema Challenge, a set of 273 problems designed by hand specifically to defeat statistical language models. WinoGrande's authors built a much bigger crowdsourced version and then ran an algorithm (AfLite) to strip out any item a model could solve through superficial bias, so that a good score reflects genuine commonsense inference rather than a dataset artifact.

## How it is scored

Each item is scored as a simple binary choice: accuracy is the fraction of items where the model selects the correct filler out of two options, with a 50% random-guess baseline. The paper reports human performance at 94.0% accuracy, against 59.4-79.1% for the best contemporary methods at publication time, depending on how much training data those methods used. AI2's official leaderboard withholds the test-set labels, so an exact-match score on the public dev set is not the same as a verified leaderboard score.

## Dataset and licence

WinoGrande contains 44,000 problems in total, released under a CC-BY licence for the data (the accompanying code is Apache-2.0). Training data is provided in five sizes from 160 to 40,398 examples plus a debiased variant, alongside a fixed 1,267-item validation set and a 1,767-item test set. Validation labels are public; test labels are withheld, and official scoring requires a submission to AI2's leaderboard.

## Who publishes it

WinoGrande was created by Keisuke Sakaguchi, Ronan Le Bras, Chandra Bhagavatula and Yejin Choi at the Allen Institute for AI, published as "WinoGrande: An Adversarial Winograd Schema Challenge at Scale," first posted to arXiv in July 2019 and later awarded an Outstanding Paper award at AAAI 2020. AI2 maintains the GitHub repository and the original submission-based leaderboard.

## Lineage

WinoGrande scales up and hardens the original Winograd Schema Challenge, using adversarial filtering to remove items solvable by spurious correlation rather than genuine reasoning. It was also one of the original tasks on Hugging Face's first Open LLM Leaderboard alongside `truthfulqa`. As with TruthfulQA, a grep of this repository's own model cards shows no model released after mid-2024 reporting a WinoGrande score, consistent with the Open LLM Leaderboard's move away from this original task suite, though no specific successor benchmark was confirmed in the sources reviewed.

## Saturation and contamination

Saturation status is unknown rather than confirmed: no recent model in this repository's corpus reports a current score, and the Hugging Face leaderboard that historically tracked WinoGrande is now archived, so there is no live source to check today's frontier models against a ceiling. Contamination risk is high, since the dev set has been public with labels since 2019 and, like TruthfulQA, was part of one of the most heavily mirrored evaluation suites on the internet - even though the official test set itself remains held out.

## How to run it

The reference data, splits and a scoring script (`eval.py`, producing `metrics.json`) are distributed through the `allenai/winogrande` GitHub repository; scoring against the true test set requires a submission to AI2's leaderboard rather than local evaluation. No lm-evaluation-harness or other standard-harness task name was confirmed for WinoGrande in the sources reviewed for this page, though it was a fixture of the original Open LLM Leaderboard's task suite.

## Reading the numbers

A high WinoGrande accuracy means a model handles this style of adversarially-filtered commonsense pronoun puzzle well, which was a genuinely hard task for pre-2020 models but is a much narrower claim than "the model has commonsense reasoning" in general. Because the public dev set has been available for years inside a widely mirrored leaderboard suite, a strong score today is at least partly attributable to training exposure rather than pure reasoning ability, especially for any model that was not scored against the officially held-out test set. As with TruthfulQA, treat a WinoGrande number reported without a date or evaluation source as hard to place against current models.
