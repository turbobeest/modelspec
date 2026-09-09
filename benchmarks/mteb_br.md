---
id: mteb_br
name: "MTEB-BR"
aliases: ["MTEB-BR: A Multilingual Benchmark for Issue Resolving"]
page_kind: benchmark
category: embedding
subcategory: Brazilian-Portuguese text embeddings
status: active
summary: "MTEB-BR evaluates agents that modify repositories to resolve issues across Java, TypeScript, JavaScript, Go, Rust, C and C++."
measures: "Embedding quality on native Brazilian-Portuguese classification, similarity, clustering, retrieval and reranking tasks."
task_format: "Text-embedding tasks with category-specific labels, similarities, retrieval and reranking judgments."
metric:
  name: task score
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper evaluates issue-resolution success with representative agent methods; no random or human baseline is established here."
dataset:
  size: 22
  size_note: "The paper reports 22 native tasks across seven categories."
  url: "https://huggingface.co/datasets/ByteDance-Seed/MTEB-BR"
  license: ""
  languages: [pt]
  modalities: [text]
  splits: "The opened sources do not establish a stable train/dev/test split for the 1,632 benchmark instances."
  public_test_set: true
publisher:
  org: "MTEB-BR authors"
  authors: []
  url: "https://arxiv.org/abs/2607.04581v2"
paper:
  title: "MTEB-BR: A Multilingual Benchmark for Issue Resolving"
  arxiv: "2607.04581"
  url: "https://arxiv.org/abs/2607.04581"
  year: 2026
leaderboard_url: ""
repo_url: "https://arxiv.org/abs/2607.04581v2"
released: "2026-07"
last_updated: ""
lineage:
  family: text embedding evaluation
  predecessor: SWE-bench
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current saturation ceiling was established in the sources opened for this page."
contamination:
  risk: medium
  note: "The benchmark and repositories are public; the source does not establish a contamination audit or private rotating holdout."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The paper evaluates Agentless, SWE-agent and OpenHands; use the repository's task environments and test execution protocol."
tags: [embedding, agents, multilingual, issue-resolution]
sources:
  - url: "https://arxiv.org/abs/2607.04581"
    title: "MTEB-BR paper"
    accessed: "2026-09-09"
  - url: "https://arxiv.org/abs/2607.04581v2"
    title: "Official MTEB-BR repository"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-09"
  researched_by: "GPT-5.6 Luna, luna-stream-c-005 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MTEB-BR measures issue resolution across software ecosystems beyond Python. An agent receives an issue and a repository state, edits files, and must produce a patch that addresses the issue. The benchmark covers Java, TypeScript, JavaScript, Go, Rust, C, and C++.

The paper evaluates 93 models and reports bootstrap confidence intervals, paired-bootstrap significance and discrimination analysis.

## How it is scored

Success is determined by the benchmark's repository tests and issue-resolution protocol, summarized as task score. Reproduce results with the same agent harness, patch policy, test commands, timeout and environment. The paper compares Agentless, SWE-agent and OpenHands, but this page does not infer a universal score from those model-specific experiments.

## Dataset and licence

The benchmark contains issue-resolution tasks tied to multilingual repositories and their test environments. The opened paper and repository establish the benchmark and public data release but do not establish a single dataset licence or a stable train/dev/test split for the 1,632 benchmark instances. Confirm the repository and dataset cards before redistribution.

## Who publishes it

MTEB-BR is maintained in the official `multi-swe-bench/multi-swe-bench` repository and described by the paper “MTEB-BR: A Multilingual Benchmark for Issue Resolving” (arXiv:2607.04581, 2026). The opened sources did not provide a complete author list in a form suitable for this record.

## Lineage

MTEB-BR extends the issue-resolution setting associated with SWE-bench to seven programming languages. The authors also describe Multi-SWE-RL as a related, larger release for training research, rather than a successor benchmark score set.

## Saturation and contamination

The repositories and issue data are public, so models or agents exposed to them can be contaminated. The opened sources do not establish a contamination study, rotating holdout or current saturation ceiling.

## How to run it

Use the official repository's task environments and test commands. Record the language, repository revision, agent harness, patch policy, timeout, dependency setup and test outcomes for every task. Report aggregate task score together with per-language results.

## Reading the numbers

A higher task score means more issue instances were resolved under the selected execution protocol. Results depend on environment setup, tests, agent interaction budget and whether failures are caused by patch quality or infrastructure. Compare runs only when those conditions match.
