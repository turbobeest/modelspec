---
id: hrm8k
name: HRM8K
aliases: []
page_kind: family
category: math
subcategory: multilingual mathematical reasoning
status: active
summary: HRM8K evaluates Korean and English mathematical reasoning on 8,011 parallel bilingual problems.
measures: HRM8K tests mathematical problem solving when instructions and questions are presented in Korean, with aligned English versions. It combines translated problems from established benchmarks with original Korean exam problems.
task_format: Free-form mathematical solution generation in Korean or English.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The harness README does not define a human baseline."}
dataset: {size: 8011, size_note: "The harness README describes 8,011 evaluation instances.", url: https://huggingface.co/datasets/HAERAE-HUB/HRM8K, license: "MIT", languages: [Korean, English], modalities: [text], splits: test, public_test_set: true}
publisher: {org: HAERAE-HUB, authors: [Hyunwoo Ko, Guijin Son, Dasol Choi], url: https://huggingface.co/datasets/HAERAE-HUB/HRM8K}
paper: {title: "Understand, Solve and Translate: Bridging the Multilingual Mathematical Reasoning Gap", arxiv: "2501.02448", url: https://arxiv.org/abs/2501.02448, year: 2025}
leaderboard_url: ""
repo_url: https://huggingface.co/datasets/HAERAE-HUB/HRM8K
released: "2025"
last_updated: "2025-07"
lineage: {family: "", predecessor: "", successors: [], variants: [hrm8k_en]}
saturation: {status: open, top_score: null, as_of: "", note: No current authoritative leaderboard was established.}
contamination: {risk: medium, note: The benchmark, training data, and models are public; exposure may vary by language and source.}
harness: {lm_eval: hrm8k, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [math, korean, multilingual]
sources:
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/hrm8k/README.md
    title: lm-evaluation-harness HRM8K README
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2501.02448
    title: HRM8K paper
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/HAERAE-HUB/HRM8K
    title: HRM8K dataset card
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/HAERAE-HUB/HRM8K
    title: Hugging Face dataset API record (license mit, five test-split configs)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-048 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-batch-048}
---

## What it measures

HRM8K evaluates multilingual mathematical reasoning. The Korean benchmark contains 8,011 problems with Korean instruction and questions; the harness also documents an English `hrm8k_en` version.

The collection combines translations from GSM8K, MATH, OmniMath, and MMMLU with original problems curated from Korean mathematics exams. It is intended to study the gap between solving in English and understanding Korean input.

## How it is scored

The harness task family includes GSM8K, KSM, MATH, MMMLU, and OmniMath variants in Korean and English. It recommends temperature 0.7, top-p 0.95, and up to 2,048 generated tokens, while the default harness decoding is greedy. The README does not give one aggregate formula or human baseline.

## Dataset and licence

The official harness README states 8,011 evaluation instances and links `HAERAE-HUB/HRM8K`. The benchmark, training data, and models are publicly released. The Hugging Face dataset card lists an MIT licence, and each of the five source-task configs ships a single `test` split (for example `gsm8k_test.csv`).

## Who publishes it

Ko, Son, and Choi introduced HRM8K in “Understand, Solve and Translate: Bridging the Multilingual Mathematical Reasoning Gap,” arXiv:2501.02448. EleutherAI’s harness integrates the tasks. No current leaderboard was established.

## Lineage

HRM8K has Korean and English variants and five named source-task variants. They should be reported separately because language and source benchmark differ.

## Saturation and contamination

The benchmark remains open in the available evidence. Public source datasets create medium exposure risk, and synthetic training data are also public. Exposure may differ between translated Korean items and original exam problems.

## How to run it

Use the `hrm8k` task group or a specific `hrm8k_{gsm8k|ksm|math|mmmlu|omni_math}` task. The English counterparts use the `hrm8k_en_` prefix. Record decoding parameters, task variant, and harness version.

## Reading the numbers

A high score indicates mathematical problem-solving success in a specified language and source family. It does not isolate translation quality from mathematical reasoning, and it does not establish broad Korean language competence. Compare language-matched variants and decoding settings.

The stated research goal distinguishes comprehension from mathematical reasoning. That interpretation requires paired Korean and English results on comparable items, rather than one pooled score.
