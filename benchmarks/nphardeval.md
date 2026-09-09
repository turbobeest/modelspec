---
id: nphardeval
name: NPHardEval
aliases: []
page_kind: family
category: reasoning
subcategory: algorithmic reasoning
status: active
summary: NPHardEval tests large language models on 900 algorithmic questions spanning complexity classes through NP-hard problems.
measures: NPHardEval evaluates reasoning about graph, routing, matching, and path problems. Its official description says the questions span complexity classes below and through NP-hard problems.
task_format: Zero-shot natural-language problem with structured final answers and brief reasoning.
metric: {name: weighted accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: ""}
dataset:
  size: 900
  size_note: The official OpenCompass README describes 900 algorithmic questions; the repository configuration exposes nine task groups.
  url: https://github.com/casmlab/NPHardEval
  license: Apache-2.0
  languages: [English]
  modalities: [text]
  splits: ""
  public_test_set: true
publisher: {org: CASM Lab, authors: [Lizhou Fan, Wenyue Hua, Lingyao Li, Haoyang Ling, Yongfeng Zhang, Libby Hemphill], url: https://github.com/casmlab/NPHardEval}
paper: {title: "NPHardEval: Dynamic Benchmark on Reasoning Ability of Large Language Models via Complexity Classes", arxiv: "2312.14890", url: https://arxiv.org/abs/2312.14890, year: 2023}
leaderboard_url: ""
repo_url: https://github.com/casmlab/NPHardEval
released: "2023-12"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [hard_GCP, hard_TSP, hard_MSP, cmp_GCP_D, cmp_TSP_D, cmp_KSP, p_BSP, p_EDP, p_SPP]}
saturation: {status: open, top_score: null, as_of: "", note: The official page reports low scores for one model, but no current top score was established.}
contamination: {risk: medium, note: Public problem instances and solutions may enter training data; no exposure study was established.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: NPHardEval, bigbench: "", other: ""}
tags: [reasoning, algorithms, np-hard]
sources:
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/NPHardEval/README.md
    title: OpenCompass NPHardEval README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/NPHardEval/NPHardEval_gen_22aac5.py
    title: OpenCompass NPHardEval configuration
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2312.14890
    title: NPHardEval paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: GPT-5.6 Luna independent review, luna-batch-017}
---

## What it measures

NPHardEval measures algorithmic reasoning with generated answers to graph coloring, traveling-salesperson, matching, and path problems. The official description says its 900 questions span a broad range of complexity classes up to NP-hard problems.

It includes optimization-style and decision-style prompts. Models receive the problem in text and must provide a structured answer, often with concise reasoning.

## How it is scored

OpenCompass configures nine task groups and gives each a task-specific evaluator. The README labels the reported aggregate as weighted accuracy. Because the groups use different answer formats and evaluators, an aggregate score should not be treated as a single uniform item accuracy without checking the task breakdown.

## Dataset and licence

The official repository describes 900 questions and is licensed Apache-2.0. OpenCompass loads local directories for hard GCP, TSP, and MSP tasks; decision variants for GCP, TSP, and KSP; and path variants for BSP, EDP, and SPP. A split protocol was not established.

## Who publishes it

NPHardEval is published by CASM Lab and described in the paper by Fan and colleagues, arXiv:2312.14890. OpenCompass maintains an integration configuration. No current public leaderboard was established.

## Lineage

This is a family page because the official integration exposes nine named task variants: `hard_GCP`, `hard_TSP`, `hard_MSP`, `cmp_GCP_D`, `cmp_TSP_D`, `cmp_KSP`, `p_BSP`, `p_EDP`, and `p_SPP`. No predecessor or successor was established.

## Saturation and contamination

The evaluation remains open in the available evidence. The public README includes a single historical model table, but no current ceiling analysis. Public algorithmic instances create medium contamination risk; no controlled refresh or exposure study was found.

## How to run it

Use OpenCompass’s `NPHardEval` configuration with zero-shot retrieval and generation. It uses task-specific evaluators and a structured prompt format. Record the exact variant, prompt, and evaluator because variants are not interchangeable.

## Reading the numbers

A high score indicates that a model can solve or correctly classify the represented algorithmic instances. It does not prove a general complexity-theory understanding or reliable performance on larger unseen instances. Inspect per-variant results and answer validity, especially when comparing reasoning traces. Tool use and external computation can change the task substantially.
