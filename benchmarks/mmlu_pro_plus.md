---
id: mmlu_pro_plus
name: "MMLU-Pro+"
aliases:
  - "MMLU Pro Plus"
  - "MMLU-Pro+"
page_kind: benchmark
category: reasoning
subcategory: "multi-correct multiple-choice reasoning across 14 MMLU-Pro subjects"
status: active
summary: "A 12,032-question MMLU-Pro extension that adds multi-correct pairs to test higher-order reasoning and shortcut resistance."
measures: >
  MMLU-Pro+ presents academic multiple-choice questions with up to ten options. It
  modifies MMLU-Pro questions so some options assert that two answers are both
  correct. The benchmark tests whether a model can identify valid pairs and resist
  anchoring on a familiar single answer across 14 subjects.
task_format: >
  Multiple choice, usually with ten options. Questions include true-positive pairs,
  partial false-positive pairs, and complete false-positive pairs. The paper reports
  accuracy plus shortcut selection ratio and correct pair identification ratio.
metric:
  name: "accuracy; shortcut selection ratio; correct pair identification ratio"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper does not establish a single random or human benchmark baseline for all reported metrics."
dataset:
  size: 12032
  size_note: "The paper states 12,032 questions: 3,718 true-positive modifications, 2,124 partial false-positive, and 2,029 complete false-positive items, with the remainder unchanged."
  url: "https://github.com/asgsaeid/mmlu-pro-plus"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Single evaluation collection in the paper and lm-evaluation-harness task group; no public train/test split was established here."
  public_test_set: true
publisher:
  org: "Autodesk AI Research"
  authors:
    - "Saeid Asgari Taghanaki"
    - "Aliasgahr Khani"
    - "Amir Khasahmadi"
  url: "https://github.com/asgsaeid/mmlu-pro-plus"
paper:
  title: "MMLU-Pro+: Evaluating Higher-Order Reasoning and Shortcut Learning in LLMs"
  arxiv: "2409.02257"
  url: "https://arxiv.org/abs/2409.02257"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/asgsaeid/mmlu-pro-plus"
released: "2024-09"
last_updated: "2026-05"
lineage:
  family: "mmlu_pro"
  predecessor: "mmlu_pro"
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: "The paper reports separation among six evaluated models; no current leaderboard top score was established."
contamination:
  risk: high
  note: "The benchmark is a public modification of MMLU-Pro, which itself builds on public MMLU questions. The paper does not provide a measured leakage rate."
harness:
  lm_eval: "mmlu_pro_plus"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - mmlu
  - reasoning
  - multiple-choice
  - multi-correct
  - shortcut-learning
sources:
  - url: "https://arxiv.org/html/2409.02257"
    title: "MMLU-Pro+ paper HTML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlu-pro-plus/README.md"
    title: "lm-evaluation-harness MMLU-Pro+ task README"
    accessed: "2026-09-08"
  - url: "https://github.com/asgsaeid/mmlu-pro-plus"
    title: "Official MMLU-Pro+ repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

## What it measures

MMLU-Pro+ extends MMLU-Pro with questions that can contain more than one correct answer. It covers biology, business, chemistry, computer science, economics, engineering, health, history, law, math, other, philosophy, physics, and psychology. The prompt remains text-only multiple choice.

The central challenge is recognizing whether a pair of statements is jointly correct. This probes higher-order reasoning and anchoring behavior. It is an extension of MMLU-Pro, not a replacement for the original MMLU family.

## How it is scored

The primary score is accuracy over the answer choices. The paper also reports shortcut selection ratio and correct pair identification ratio. A response that selects a familiar single answer can fail when the correct choice is a pair. The harness group contains 14 subject tasks and follows the MMLU-style evaluation interface.

The dataset construction has three pair types. True-positive pairs combine the original correct answer with a new correct answer. Partial false-positive pairs combine one correct and one incorrect answer. Complete false-positive pairs combine two incorrect answers. Published paper tables used zero-shot-style multiple-choice evaluation; shot settings should be recorded by the reporter.

## Dataset and licence

The paper describes 12,032 questions over 14 subjects. It reports 3,718 true-positive modifications, 2,124 partial false-positive items, and 2,029 complete false-positive items. The remaining questions are not described as a new pair category. GPT-4o generated the new correct options for true-positive pairs, followed by human auditing of 100 examples from each group.

The official repository does not establish a dataset licence in the sources opened here. Questions and answers are public through the release, so the test material is not held out.

## Who publishes it

Saeid Asgari Taghanaki, Aliasgahr Khani, and Amir Khasahmadi introduced MMLU-Pro+ in an Autodesk AI Research paper accepted to the NeurIPS 2024 Safe Generative AI workshop. The official repository and EleutherAI lm-evaluation-harness maintain runnable configurations.

## Lineage

MMLU-Pro+ is a direct extension of [MMLU-Pro](mmlu_pro.md), which derives from [MMLU](mmlu.md). It keeps MMLU-Pro’s 14 subject groups while changing answer construction. It should not be merged with MMLU-Pro or MMLU scores.

## Saturation and contamination

The paper reports meaningful gaps across six evaluated models and describes MMLU-Pro+ as harder than MMLU-Pro. A current saturation point is not established. Contamination risk is high because the underlying MMLU and MMLU-Pro material is public, and the MMLU-Pro+ release is also public. The paper does not report a dedicated contamination study.

## How to run it

Use `lm_eval --tasks mmlu_pro_plus` with the current lm-evaluation-harness task group (the repository directory is named `mmlu-pro-plus`, but the runnable group id uses underscores). The task contains 14 subject names under the group. Report whether chat templates, few-shot examples, or a custom answer parser were used. Pair-identification metrics require the MMLU-Pro+ reference implementation; ordinary accuracy alone does not expose shortcut selection.

## Reading the numbers

A high accuracy means the model selected the intended answer option on this modified MMLU-Pro collection. It does not prove that the model discovered a general theory of multiple-valid-answer reasoning. Shortcut and pair-identification ratios help explain whether errors come from selecting one familiar option or missing the valid pair. Compare with MMLU-Pro under a matched prompt and shot protocol.
