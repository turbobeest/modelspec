---
id: swe_explore
name: SWE-Explore
aliases: ["SWE-Explore-Bench"]
page_kind: benchmark
category: coding
subcategory: repository exploration / code localization
status: active
summary: SWE-Explore isolates repository exploration from patch generation, scoring the ranked code regions an agent returns for a GitHub issue under a fixed line budget.
measures: >
  Given a repository snapshot and a real GitHub issue, the agent (or retriever) must return a ranked
  list of code regions it believes are relevant to resolving the issue, subject to a fixed line budget
  (100, 300 or 500 lines in the released evaluator). The task separates exploration and localization
  from patch writing, which most issue-resolution benchmarks grade only as a single pass/fail outcome.
  Ground-truth "core" and "optional context" regions are derived from independent, successful repair
  trajectories rather than authored by hand.
task_format: >
  Text input (issue description plus repository access); output is a ranked list of code regions
  (file + line range) within the line budget, not a patch.
metric:
  name: "line-level F1 / nDCG@B (with HitFile, HitRegion, context-efficiency and noise-rate as secondary metrics)"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: "Paper reports downstream resolve rate when a fixed repair model is fed an oracle explorer (59.7%) versus a random explorer (4.7%); this measures the value of exploration, not the exploration metric itself."
dataset:
  size: 848
  size_note: "848 issues across 203 open-source repositories and 10 programming languages."
  url: "https://huggingface.co/datasets/SWE-Explore-Bench/SWE-Explore-Bench"
  license: CC BY-NC-ND 4.0
  languages: []
  modalities: [code, text]
  splits: "single train split (848 rows) in the released Hugging Face dataset"
  public_test_set: true
publisher:
  org: ""
  authors: [Shaoqiu Zhang, Yuhang Wang, Jialiang Liang, Yuling Shi, Wenhao Zeng, Maoquan Wang, Shilin He, Ningyuan Xu, Siyu Ye, Kai Cai, Xiaodong Gu]
  url: "https://github.com/Qiushao-E/SWE-Explore-Bench"
paper:
  title: "SWE-Explore: Benchmarking How Coding Agents Explore Repositories"
  arxiv: "2606.07297"
  url: "https://arxiv.org/abs/2606.07297"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/Qiushao-E/SWE-Explore-Bench"
released: "2026-06"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "Issues and repositories are public GitHub content; no contamination study is stated in the paper. Publication in June 2026 makes prior-training exposure unlikely for older models, but this is not established."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, coding-agent, localization, repository-exploration]
sources:
  - url: "https://arxiv.org/abs/2606.07297"
    title: "SWE-Explore: Benchmarking How Coding Agents Explore Repositories"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2606.07297v1"
    title: "SWE-Explore (HTML, v1)"
    accessed: "2026-09-08"
  - url: "https://github.com/Qiushao-E/SWE-Explore-Bench"
    title: "SWE-Explore-Bench repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/SWE-Explore-Bench/SWE-Explore-Bench"
    title: "SWE-Explore-Bench dataset card"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-004 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-004"}
---
## What it measures

SWE-Explore tests repository exploration on its own, apart from whether a model can eventually write a correct patch. Given a real GitHub issue and a snapshot of the repository just before the fix, the system under test must return a ranked list of code regions it believes are relevant, constrained to a fixed line budget (the released evaluator uses 100, 300 or 500 lines). Most issue-resolution benchmarks grade a single pass/fail patch outcome and hide exploration quality inside that number; SWE-Explore scores the exploration step directly. The 848 issues span 203 open-source repositories across 10 programming languages, so the task is not Python-only.

## How it is scored

Ground truth is not hand-authored: "core" and "optional context" regions are extracted from independent, successful repair trajectories that actually consulted those lines. The paper reports line-level precision, recall and F1, HitFile and HitRegion (fraction of ground-truth files/regions reached), nDCG@B (ranking quality within the line budget), context-efficiency (useful lines returned versus total) and a noise rate. There is no single official percentage score; a reported number should specify which of these metrics it is. Separately, the authors show the value of good exploration downstream: feeding a fixed repair model an oracle explorer's output yields a 59.7% resolve rate versus 4.7% for a random explorer.

## Dataset and licence

848 issues from 203 repositories in 10 languages, released as a single split on Hugging Face (`SWE-Explore-Bench/SWE-Explore-Bench`) under CC BY-NC-ND 4.0. The evaluation code on GitHub (`Qiushao-E/SWE-Explore-Bench`) is MIT-licensed; the dataset itself carries the more restrictive non-commercial, no-derivatives licence, so the two should not be assumed to share terms. The released dataset includes the ground-truth regions, so answers are public.

## Who publishes it

The paper "SWE-Explore: Benchmarking How Coding Agents Explore Repositories" (arXiv:2606.07297, submitted June 2026) is by Shaoqiu Zhang, Yuhang Wang, Jialiang Liang, Yuling Shi, Wenhao Zeng, Maoquan Wang, Shilin He, Ningyuan Xu, Siyu Ye, Kai Cai and Xiaodong Gu. No institutional affiliation is stated on the arXiv abstract page, and no target venue is listed; it is a preprint as of the last check. The GitHub organisation `Qiushao-E` hosts the code and dataset.

## Lineage

SWE-Explore is a standalone benchmark, not a subset of SWE-bench, though it targets the same GitHub-issue setting and compares its oracle/random baselines against downstream SWE-bench-style resolve rates. No predecessor or successor benchmark is named in the paper, and no other page in this repository currently claims it as a variant.

## Saturation and contamination

Saturation is not established: the paper reports method comparisons (5 general-purpose agents, 4 academic localizers, sparse and dense retrievers) but no single leaderboard ceiling. Contamination risk is unknown; the issues and repositories are public GitHub content and the paper does not discuss training-data exposure. Because the dataset was published in June 2026, exposure in the training data of already-released models cannot be assumed either way from this source.

## How to run it

The reference implementation and evaluator are in the `Qiushao-E/SWE-Explore-Bench` GitHub repository, with the dataset loadable via Hugging Face `datasets`. There is no lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench integration confirmed as of this check. Reported numbers should specify the line budget (100/300/500), the number of regions K, and which metric (F1, nDCG@B, HitFile, HitRegion, context-efficiency or noise rate) is being quoted, since these are not interchangeable.

## Reading the numbers

A strong SWE-Explore score means an agent finds and ranks the right code regions early, within a tight line budget — a precursor skill to writing a correct patch, not proof that it can write one. The oracle-vs-random resolve-rate gap (59.7% vs 4.7%) shows exploration quality strongly predicts downstream repair success in this setup, but that link was measured with one fixed repair model and may not transfer to every system. Compare scores only when the line budget and metric match, and treat this as a diagnostic for the retrieval/localization stage of a coding agent rather than a general capability certificate.
