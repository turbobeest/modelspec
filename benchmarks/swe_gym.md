---
id: swe_gym
name: SWE-Gym
aliases: []
page_kind: benchmark
category: coding
subcategory: agent training environment with held-out evaluation
status: active
summary: SWE-Gym is a training environment of real Python issue-resolution tasks; agents trained on it are typically reported by resolve rate on SWE-bench Verified and Lite, not a separate SWE-Gym leaderboard.
measures: >
  SWE-Gym provides real-world Python task instances (a codebase snapshot, an executable runtime, unit
  tests and a natural-language issue) for training and verifying software-engineering agents. It is
  built to be run against, not just read: an agent explores the repository, edits code and executes
  tests inside the provided environment. The paper's own reported numbers measure what training on
  SWE-Gym does for resolve rate on the separate SWE-bench Verified and Lite test sets, plus a "Lite"
  234-instance subset of SWE-Gym itself used for lighter-weight evaluation during development.
task_format: >
  Text input (issue description) with repository and executable test access; output is a patch, graded
  by running hidden tests recovered from the originating pull request.
metric:
  name: "% resolved (patch passes FAIL_TO_PASS and PASS_TO_PASS tests)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The headline numbers in the paper (32.0% and 26.0%) are resolve rates on SWE-bench Verified and Lite after training on SWE-Gym, not a SWE-Gym-native leaderboard score."
dataset:
  size: 2438
  size_note: "Paper abstract: 2,438 real-world Python task instances from real GitHub issues/PRs. The GitHub README states 2,400 real tasks from 11 Python repositories, plus a 234-instance 'Lite' evaluation subset; the two counts (2,438 vs 2,400) were not reconciled from these sources."
  url: "https://github.com/SWE-Gym/SWE-Gym"
  license: Apache-2.0
  languages: [Python]
  modalities: [code, text]
  splits: "full task set plus a 234-instance Lite evaluation subset"
  public_test_set: true
publisher:
  org: ""
  authors: [Jiayi Pan, Xingyao Wang, Graham Neubig, Navdeep Jaitly, Heng Ji, Alane Suhr, Yizhe Zhang]
  url: "https://github.com/SWE-Gym/SWE-Gym"
paper:
  title: "Training Software Engineering Agents and Verifiers with SWE-Gym"
  arxiv: "2412.21139"
  url: "https://arxiv.org/abs/2412.21139"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/SWE-Gym/SWE-Gym"
released: "2024-12"
last_updated: "2025-06"
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "Task instances come from public GitHub issues/PRs; no contamination study for SWE-Gym itself was found in this check. Its own downstream comparisons are reported against SWE-bench Verified/Lite, whose contamination is tracked separately on those pages."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, coding-agent, agent-training, reinforcement-learning]
sources:
  - url: "https://arxiv.org/abs/2412.21139"
    title: "Training Software Engineering Agents and Verifiers with SWE-Gym"
    accessed: "2026-09-08"
  - url: "https://github.com/SWE-Gym/SWE-Gym"
    title: "SWE-Gym repository (README, license)"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-004 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-004"}
---
## What it measures

SWE-Gym is described by its authors as "the first environment for training real-world software engineering agents." Each instance pairs a real GitHub issue with a runnable codebase snapshot, an executable test suite and a natural-language task description, so an agent can explore the repository, make edits and run tests inside the environment rather than answering a static prompt. It is primarily a training resource: the paper trains language-model agents and separately trained verifiers on SWE-Gym trajectories, then measures the resulting agents on the independent SWE-bench Verified and Lite test sets.

## How it is scored

The standard metric is percent resolved: a submitted patch passes if it makes the issue's originally-failing tests pass while not breaking previously-passing tests (the FAIL_TO_PASS/PASS_TO_PASS protocol used across the SWE-bench family). The paper's headline results — up to 19 percentage points of absolute gain, reaching 32.0% and 26.0% on SWE-bench Verified and Lite respectively using verifiers trained on SWE-Gym trajectories — are downstream numbers on those external test sets, not a SWE-Gym-specific leaderboard score. SWE-Gym also has its own 234-instance "Lite" subset used for faster internal evaluation during development.

## Dataset and licence

The paper's abstract states 2,438 real-world Python task instances; the project's GitHub README instead states 2,400 real tasks drawn from 11 Python repositories. This discrepancy was not resolved from the sources checked and should be flagged rather than rounded to one figure. The repository is licensed Apache-2.0. Data and trained models are also distributed via a SWE-Gym Hugging Face organisation. All tasks are Python; answers (the reference patches and tests) are part of the public release.

## Who publishes it

"Training Software Engineering Agents and Verifiers with SWE-Gym" (arXiv:2412.21139) is by Jiayi Pan, Xingyao Wang, Graham Neubig, Navdeep Jaitly, Heng Ji, Alane Suhr and Yizhe Zhang. The first version was posted in December 2024; a revised version appeared in June 2025, and the paper was accepted at ICML 2025. The `SWE-Gym` GitHub organisation maintains the code, environments and Docker images used to run it.

## Lineage

SWE-Gym is not a subset of SWE-bench, but its evaluation protocol and metric are the same FAIL_TO_PASS/PASS_TO_PASS resolve-rate used by SWE-bench, SWE-bench Verified and SWE-bench Lite, and its own results are reported against those test sets. No formal predecessor or successor relationship is stated in the paper.

## Saturation and contamination

Saturation is not established for SWE-Gym itself since it functions as a training environment rather than a fixed leaderboard target; the relevant ceiling questions belong to SWE-bench Verified and Lite, tracked on their own pages. Contamination risk for SWE-Gym's own task set is unknown: its instances are drawn from public GitHub issues and pull requests, and no contamination study specific to SWE-Gym was found in this check.

## How to run it

The reference implementation, Docker-based execution environments and the 234-instance Lite evaluation subset are in the `SWE-Gym/SWE-Gym` GitHub repository, with data and models also on Hugging Face. There is no lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench integration confirmed as of this check. Numbers reported against "SWE-Gym" should specify whether they refer to the internal Lite evaluation subset or to downstream SWE-bench Verified/Lite results after training on SWE-Gym, since these are different things measured on different test sets.

## Reading the numbers

A model card citing SWE-Gym is usually describing a training resource, not a single benchmark number: check whether the reported score is SWE-Gym's own Lite subset or a downstream SWE-bench Verified/Lite resolve rate produced by an agent or verifier trained on SWE-Gym data. A strong downstream number shows the training environment produced a more capable agent on those external tests; it does not by itself describe SWE-Gym's own difficulty or ceiling. Compare only matching test sets and protocol versions, and note the paper's own instance-count discrepancy (2,438 vs 2,400) when citing dataset size.
