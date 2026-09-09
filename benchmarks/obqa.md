---
id: obqa
name: OpenBookQA
aliases: [OBQA]
page_kind: benchmark
category: knowledge
subcategory: open-book question answering
status: active
summary: OpenBookQA tests multi-step science question answering with a small open book of facts and four answer choices.
measures: OpenBookQA asks grade-school science questions that require combining a supplied salient fact with common knowledge and language understanding. It is designed as an open-book exam style evaluation.
task_format: Four-choice multiple-choice question, optionally accompanied by a fact; output A, B, C, or D.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 25, human_baseline: null, baseline_note: ""}
dataset:
  size: 500
  size_note: Main configuration has 4,957 train, 500 validation, and 500 test examples; the additional configuration has the same split counts.
  url: https://huggingface.co/datasets/allenai/openbookqa
  license: ""
  languages: [English]
  modalities: [text]
  splits: train, validation, test
  public_test_set: true
publisher: {org: Allen Institute for AI, authors: [Todor Mihaylov, Peter Clark, Tushar Khot, Ashish Sabharwal], url: https://allenai.org/data/open-book-qa}
paper: {title: "Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering", arxiv: "", url: https://aclanthology.org/N18-1021/, year: 2018}
leaderboard_url: ""
repo_url: https://huggingface.co/datasets/allenai/openbookqa
released: "2018"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [bangla_openbookqa]}
saturation: {status: watch, top_score: null, as_of: "", note: The dataset is widely used and public, but no current authoritative top score was established.}
contamination: {risk: high, note: The 2018 questions and answer keys are public and old enough to plausibly occur in training data.}
harness: {lm_eval: "openbookqa", inspect_evals: "", helm: "", opencompass: obqa, bigbench: "", other: ""}
tags: [science, commonsense, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/obqa/obqa_gen_9069e4.py
    title: OpenCompass OpenBookQA configuration
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/allenai/openbookqa
    title: AllenAI OpenBookQA dataset card
    accessed: "2026-09-08"
  - url: https://aclanthology.org/N18-1021/
    title: OpenBookQA paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: GPT-5.6 Luna independent review, luna-batch-017}
---

## What it measures

OpenBookQA measures multi-step reasoning over elementary science questions. Each question is multiple choice, and the dataset’s additional configuration can provide a salient fact before the question. The intended skill combines that fact with common knowledge and language comprehension.

## How it is scored

OpenCompass uses an accuracy evaluator and extracts the first answer option among A, B, C, and D. Four choices imply a 25 percent uniform-choice baseline. Prompt templates differ between the main and fact-augmented configurations, so their scores should be reported separately.

## Dataset and licence

The public dataset card reports 4,957 training, 500 validation, and 500 test examples for both main and additional configurations. It describes English text fields including question stem, choices, answer key, and, for additional data, `fact1`. The dataset card does not state a licence.

## Who publishes it

The dataset was released by the Allen Institute for AI and introduced at EMNLP 2018 by Mihaylov, Clark, Khot, and Sabharwal. OpenCompass and lm-evaluation-harness provide integrations. No current authoritative leaderboard was established.

## Lineage

OpenBookQA is a standalone benchmark. This repository also contains `bangla_openbookqa`, a language variant, but it is a separate evaluation and should not be merged into the English score.

## Saturation and contamination

The public 2018 test set creates high contamination risk. The benchmark remains useful for comparability, but scores can reflect memorization as well as reasoning. No authoritative current saturation measurement was found.

## How to run it

OpenCompass exposes `openbookqa` and `openbookqa_fact`. Both use zero-shot retrieval, generation, accuracy evaluation, and first-option postprocessing; the fact variant includes `fact1` in the prompt. The lm-evaluation-harness task is `openbookqa`; prompt details may differ.

## Reading the numbers

A high score indicates success on the benchmark’s short science questions under its fixed choices. It does not establish broad scientific reasoning, robust open-book retrieval, or resistance to memorization. Record whether facts were supplied and which split and prompt implementation were used.

The fact-augmented configuration is especially sensitive to prompt wording: supplying the salient fact changes the information available to the model. Results should therefore identify the main or additional configuration rather than calling both simply OpenBookQA.
