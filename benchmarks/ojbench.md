---
id: ojbench
name: OJBench
aliases: []
page_kind: benchmark
category: coding
subcategory: competitive programming
status: active
summary: OJBench evaluates competitive-level code reasoning on 232 NOI and ICPC programming problems.
measures: OJBench tests whether a model can reason about and produce solutions for difficult programming-contest problems. The paper describes problems drawn from NOI and ICPC competitions.
task_format: Natural-language programming problem prompt; generate a code solution evaluated by an online-judge style checker.
metric: {name: Pass@8, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The paper evaluates eight candidate solutions per problem."}
dataset: {size: 232, size_note: "159 NOI and 73 ICPC problems; difficulty counts are 36 easy, 79 medium, and 117 hard.", url: https://huggingface.co/datasets/opencompass/ojbench, license: "", languages: [English], modalities: [text, code], splits: "", public_test_set: true}
publisher: {org: OJBench authors, authors: [Zhexu Wang, Yiping Liu, Yejie Wang, Wenyang He, Bofei Gao, Muxi Diao, Yanxu Chen, Kelin Fu, Flood Sung, Zhilin Yang, Tianyu Liu, Weiran Xu], url: https://arxiv.org/abs/2506.16395}
paper: {title: "OJBench: A Competition Level Code Benchmark For Large Language Models", arxiv: "2506.16395", url: https://arxiv.org/abs/2506.16395, year: 2025}
leaderboard_url: https://he-ren.github.io/OJBench/
repo_url: https://github.com/open-compass/opencompass
released: "2025-06"
last_updated: "2026-03"
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: open, top_score: null, as_of: "", note: The paper reports that state-of-the-art reasoning models still struggle; no current top score was established.}
contamination: {risk: medium, note: Competition problems are public, but the paper’s exposure analysis was not established from the source read.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: ojbench, bigbench: "", other: online judge}
tags: [code-generation, competitive-programming, reasoning]
sources:
  - url: https://arxiv.org/abs/2506.16395
    title: OJBench paper
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ojbench/ojbench_gen.py
    title: OpenCompass OJBench configuration
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: GPT-5.6 Luna independent review, luna-batch-017}
---

## What it measures

OJBench measures competitive programming ability at the level of NOI and ICPC problems. It targets code reasoning and solution generation rather than short code completion.

The paper describes 232 problems and evaluates a range of closed and open models. A model receives a programming problem and must generate a solution that passes the benchmark’s judging procedure.

## How it is scored

The paper reports Pass@8: eight candidate solutions are generated and a problem counts as passed when the judging procedure accepts a solution. The paper describes complete test-case judging and supports Python and C++; exact compiler and timeout settings remain implementation details.

## Dataset and licence

The paper reports 232 problems from NOI and ICPC, with 159 from NOI and 73 from ICPC. The public OpenCompass path is `opencompass/ojbench`. A dataset licence and split structure were not established.

## Who publishes it

OJBench was introduced in the 2025 paper by Wang and colleagues (arXiv:2506.16395). OpenCompass publishes a runnable integration and dataset path. No current standalone leaderboard was established.

## Lineage

OJBench is a standalone competitive-programming benchmark. The sources read do not establish a predecessor, successor, or repository variant.

## Saturation and contamination

The paper reports that even leading reasoning models struggle, supporting an open status. The underlying contest problems are publicly available, so training exposure is plausible. No dedicated contamination study was established.

## How to run it

Use OpenCompass’s `ojbench` configuration with zero-shot retrieval and generation. It prompts the model with the problem text and evaluates generated code using an online judge. Record the language, execution limits, judge version, and number of candidates because they materially affect Pass@8.

## Reading the numbers

A high pass rate indicates that generated programs satisfy the judge on this difficult contest set. It does not measure maintainability, explanation quality, or software engineering outside contest constraints. Compare only runs with the same language, tool access, time limits, and judge implementation.

The benchmark’s difficulty also makes failure analysis valuable. A pass rate alone does not distinguish parsing mistakes, algorithmic errors, resource-limit failures, and incomplete reasoning, so reports should retain per-problem outcomes where possible.
