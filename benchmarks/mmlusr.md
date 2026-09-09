---
id: mmlusr
name: "MMLU-SR"
aliases:
  - "MMLU-SR"
  - "MMLU Symbol Replacement"
  - "MMLU-R"
page_kind: benchmark
category: reasoning
subcategory: "symbol-replacement stress test over 57 MMLU subjects"
status: active
summary: "An MMLU variant that replaces key terms with defined dummy symbols to separate conceptual reasoning from surface pattern matching."
measures: >
  MMLU-SR asks the model to answer familiar MMLU questions after replacing key
  terms with invented symbols and definitions. It has question-only, answer-only,
  and question-and-answer variants across the 57 MMLU subjects. The task stays
  text-only and multiple choice while changing terminology.
task_format: >
  Four-option multiple choice. The replaced term is paired with a definition in the
  prompt. The lm-evaluation-harness exposes aggregate, question-only, answer-only,
  and subject tasks; the original paper also describes a fine-tuning evaluation.
metric:
  name: "accuracy (acc)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: "The public tasks use four answer choices, so uniform-choice chance is 25%; no human score was established."
dataset:
  size: 42639
  size_note: "The Hugging Face repository reports 42,639 rows across three variants, each with development/train and test data over 57 subjects."
  url: "https://huggingface.co/datasets/NiniCat/MMLU-SR"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "question_only, answer_only, and question_and_answer variants; each has train/dev and test files"
  public_test_set: true
publisher:
  org: "MMLU-SR authors"
  authors:
    - "Wentian Wang"
    - "Sarthak Jain"
    - "Paul Kantor"
    - "Jacob Feldman"
    - "Lazaros Gallos"
    - "Hao Wang"
  url: "https://github.com/Wang-ML-Lab/MMLU-SR"
paper:
  title: "MMLU-SR: A Benchmark for Stress-Testing Reasoning Capability of Large Language Models"
  arxiv: "2406.15468"
  url: "https://arxiv.org/abs/2406.15468"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/Wang-ML-Lab/MMLU-SR"
released: "2024-06"
last_updated: "2025-05"
lineage:
  family: "mmlu"
  predecessor: "mmlu"
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: "The paper reports substantial drops after symbol replacement; no current leaderboard top score was established."
contamination:
  risk: high
  note: "MMLU-SR modifies public MMLU questions and publishes its test files. The symbol substitutions reduce exact-string overlap but do not establish low contamination."
harness:
  lm_eval: "mmlusr"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - mmlu
  - reasoning
  - symbol-replacement
  - multiple-choice
sources:
  - url: "https://arxiv.org/html/2406.15468"
    title: "MMLU-SR paper HTML"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/NiniCat/MMLU-SR"
    title: "Official MMLU-SR dataset card"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlusr/README.md"
    title: "lm-evaluation-harness MMLU-SR README"
    accessed: "2026-09-08"
  - url: "https://github.com/Wang-ML-Lab/MMLU-SR"
    title: "Official MMLU-SR repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

## What it measures

MMLU-SR tests whether a model can preserve the meaning of an MMLU question when a key term is replaced by a made-up symbol. The prompt supplies a definition for the symbol. The benchmark covers the same broad academic subjects as MMLU, including STEM, humanities, social sciences, and professional topics.

It has three variants: replacement in the question, replacement in answer choices, and replacement in both. This changes terminology while retaining the underlying question structure. It is a reasoning stress test, not a new subject exam.

## How it is scored

The harness reports multiple-choice accuracy. Each item has four choices, giving a 25% uniform-choice baseline. Aggregate `mmlusr` contains the three replacement settings, while `mmlusr_question_only`, `mmlusr_answer_only`, and subject tasks expose narrower slices.

The paper also discusses fine-tuning and a few-shot setup. Those results are not interchangeable with a zero-shot harness run. Report the replacement variant, subject aggregation, and shot count with every score.

## Dataset and licence

The official Hub card reports 42,639 rows across the three configurations. Each configuration has development/train and test data covering 57 subjects. The Hub metadata labels the dataset MIT. Questions are derived from MMLU and the public test files include answer labels.

## Who publishes it

Wentian Wang, Sarthak Jain, Paul Kantor, Jacob Feldman, Lazaros Gallos, and Hao Wang introduced MMLU-SR in 2024. The authors maintain the GitHub release, while EleutherAI maintains the lm-evaluation-harness task group.

## Lineage

MMLU-SR is a variant of [MMLU](mmlu.md), not a subject page. Its three replacement modes are variants of one benchmark. It is distinct from [MMLU-Pro](mmlu_pro.md), [MMLU-Pro+](mmlu_pro_plus.md), and MMLU-Redux.

## Saturation and contamination

The paper reports large performance reductions after replacing terminology, leaving room for separation. A current frontier saturation value is not established. Underlying MMLU questions and MMLU-SR test files are public, so contamination risk is high even though the dummy symbols alter surface form.

## How to run it

Use `lm_eval --tasks mmlusr` or a named subject/variant task. Match the harness version because task files and few-shot handling can change. The original repository also documents a fine-tuned evaluation, which should be reported separately from harness in-context evaluation.

## Reading the numbers

A high score means the model selected the answer after applying the supplied replacement definitions. A drop relative to ordinary MMLU can indicate reliance on familiar terminology, but it can also reflect awkward definitions or prompt formatting. Compare all three replacement modes with the corresponding MMLU subjects under the same evaluation budget.
