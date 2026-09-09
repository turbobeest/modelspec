---
id: scbench
name: "scBench"
aliases:
  - "scBench: Evaluating AI Agents on Single-Cell RNA-seq Analysis"
  - "scbench"
page_kind: benchmark
category: agentic
subcategory: "agentic single-cell RNA-seq analysis on .h5ad snapshots with deterministic graders"
status: active
summary: "An agent benchmark of verifiable scRNA-seq analysis problems; inspect_evals ships a 30-task public canonical slice, while the paper describes 394 held-out tasks."
measures: >
  scBench (LatchBio) asks an agent to analyse a real single-cell RNA-seq snapshot stored as
  AnnData `.h5ad` and write structured answers to `eval_answer.json`. Tasks cover quality
  control, normalization, dimensionality reduction, clustering, cell typing, differential
  expression, and trajectory analysis across sequencing platforms. Graders are deterministic
  (numeric tolerance, multiple choice, marker-gene precision/recall, label-set Jaccard,
  distribution comparison). The agent must load the data; a memorised textbook answer fails
  if it never touches the file. inspect_evals, the census harness for this id, runs the public
  canonical subset (30 tasks, five platforms), not the full paper set.
task_format: >
  Agentic code execution in a sandbox. inspect_evals defaults to mini-SWE-agent via
  inspect-swe inside Docker, with a react()+bash fallback. Timeout defaults: 600s task,
  300s bash. Answers are read only from eval_answer.json; there is no text-parsing fallback.
metric:
  name: "accuracy (fraction of tasks passed); stderr also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports 29-53% accuracy across eight frontier models on 394 tasks under
    mini-SWE-agent with three replicates; the best listed figure in that HTML is 52.8%.
    inspect_evals' own 30-task table (eval version 1-A) has OpenAI gpt-5.1 at 43.3% ± 9.2%.
    The latchbio README table later lists 57.95% for claude-opus-4-8 on 195 evaluations.
    Those three denominators are not interchangeable.
dataset:
  size: 394
  size_note: >
    Paper (arXiv:2602.09063, 9 February 2026): 394 verifiable problems, six platforms, seven
    task categories. inspect_evals README and eval.yaml: public canonical subset of 30 tasks
    across Chromium, CSGenetics, Illumina, MissionBio and ParseBio (CANONICAL_EVAL_COUNT=30);
    the full set is described there as 394 and not publicly released. The latchbio/scbench
    README instead states 195 problems, six platforms including BD Rhapsody, six task
    categories, and six public canonical examples. This page records 394 as the paper's count
    and treats 195 vs 394 as an unresolved disagreement.
  url: "https://github.com/latchbio/scbench"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "inspect_evals: 30 canonical JSON evals; paper full set held out"
  public_test_set: false
publisher:
  org: "LatchBio"
  authors:
    - "Kenny Workman"
    - "Zhen Yang"
    - "Harihara Muralidharan"
    - "Aidan Abdulali"
    - "Hannah Le"
  url: "https://latch.bio/scbench"
paper:
  title: "scBench: Evaluating AI Agents on Single-Cell RNA-seq Analysis"
  arxiv: "2602.09063"
  url: "https://arxiv.org/abs/2602.09063"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/latchbio/scbench"
released: "2026-02"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 52.8
  as_of: "2026-02"
  note: >
    Paper: best of eight models 52.8% on 394 tasks, mini-SWE-agent, three replicates
    (as_of the 9 February 2026 arXiv posting). inspect_evals 30-task run: 43.3% for
    gpt-5.1-2025-11-13. latchbio README (checked 2026-09-08) lists 57.95% for
    claude-opus-4-8 / Claude Code on 195 evaluations. Scores still sit far from 100.
    top_score records the paper's 52.8 on the 394-task protocol.
contamination:
  risk: low
  note: >
    The paper's full item set is described as unreleased to limit training leakage.
    inspect_evals ships 30 public JSON definitions and downloads `.h5ad` files from
    Hugging Face retroam/scbench-data at runtime, so that canonical slice is public
    (medium risk for those 30). Answers are computed from the data by graders, not
    stored as free text in the prompt.
harness:
  lm_eval: ""
  inspect_evals: "scbench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Upstream CLI: `scbench run` with agents minisweagent, claudecode, openaicodex.
    inspect_evals extra: pip install inspect-evals[scbench]; Docker compose ships
    scanpy/anndata. Not THUDM SCBench (KV-cache long-context; no page in this repo).
tags:
  - agentic
  - biology
  - single-cell
  - rna-seq
  - sandbox
sources:
  - url: "https://arxiv.org/abs/2602.09063"
    title: "scBench paper abs: 394 tasks, 29-53% accuracy, 9 February 2026"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2602.09063"
    title: "scBench paper HTML: 394-task table, 52.8% best, six platforms"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/latchbio/scbench/main/README.md"
    title: "latchbio/scbench README: 195 tasks claim, Apache-2.0, grader families"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scbench/README.md"
    title: "inspect_evals scbench README: 30 canonical tasks, 394-paper note"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scbench/eval.yaml"
    title: "eval.yaml: task scbench, 30 samples, arXiv 2602.09063, version 2-A"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scbench/dataset.py"
    title: "CANONICAL_EVAL_COUNT=30, five platforms, seven categories"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT licence (wrapper); upstream repo is Apache-2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/latchbio/scbench/main/LICENSE"
    title: "latchbio/scbench Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

scBench tests whether an agent can carry out a real scRNA-seq analysis step on a frozen `.h5ad` file. The prompt is English. The work is code: load AnnData, compute a QC metric, cluster, call cell types, or compare distributions, then write JSON. inspect_evals runs 30 public canonical tasks on five platforms (Chromium, CSGenetics, Illumina, MissionBio, ParseBio). The paper describes 394 tasks on six platforms. This is biology-agent evaluation, not the unrelated THUDM SCBench long-context suite, which has no page here.

## How it is scored

Each task has a deterministic grader. Numeric answers use tolerance. Gene lists use precision/recall against markers. Sets use Jaccard. The inspect_evals scorer reads only `eval_answer.json` in the sandbox working directory. The reported metric is accuracy with stderr. The paper averages three mini-SWE-agent replicates with t-interval CIs. inspect_evals' 30-task table is a different sample: gpt-5.1 43.3%, Gemini 3 Pro 36.7%, Claude Sonnet 4.5 30.0% in their eval report. Docker vs the original LocalEnvironment, 16 KiB tool-output truncation, and timeout semantics all shift scores.

## Dataset and licence

The paper: 394 problems, six platforms, seven categories. inspect_evals: 30 JSON files under `evals_canonical`, Apache-2.0 upstream, MIT wrapper. Large `.h5ad` objects download from `retroam/scbench-data` at runtime; cold cache can consume the 600s task limit. The latchbio README's 195-task, six-example public set disagrees with both the paper's 394 and inspect_evals' 30. Full-set answers are not on GitHub. Licence of the Latch-hosted data files beyond the Apache-2.0 repo was not separately stated.

## Who publishes it

LatchBio authors Workman, Yang, Muralidharan, Abdulali and Le. arXiv:2602.09063, 9 February 2026, q-bio.GN. inspect_evals packaging is by contributor retroam, eval version 2-A dated 22 April 2026 in the changelog. Project page: latch.bio/scbench.

## Lineage

Standalone. SpatialBench is named in the paper as a companion for spatial transcriptomics, without a page here. Not [SciCode](scicode.md) (research coding) and not [SciBench](scibench.md) (textbook problems). Not THUDM SCBench.

## Saturation and contamination

Paper best 52.8% on 394 tasks; later README 57.95% on 195. Either way the ceiling is open. The hidden full set lowers contamination relative to a fully public CSV. The 30 canonical JSONs and Hub `.h5ad` files are public and can leak.

## How to run it

`inspect eval inspect_evals/scbench` after `pip install inspect-evals[scbench]`. Prefer `inspect-swe` and `-T agent=minisweagent` to match the paper. Raise `--time-limit` on a cold Hugging Face cache. Upstream: `scbench run` from latchbio/scbench. Do not compare a 30-task inspect run with a 394-task paper table or a 195-task README table.

## Reading the numbers

A high accuracy means the agent wrote grader-passing JSON after touching the snapshot, not that it can design a new assay or write a paper. Platform effects are large in the paper (40-point swings). Name the harness (mini-SWE-agent vs Claude Code vs the react fallback), the task count, and whether `.h5ad` download time was inside the timeout. Pair with SpatialBench if the claim is single-cell analysis in general.
