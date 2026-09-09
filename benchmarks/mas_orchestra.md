---
id: mas_orchestra
name: MASBench
aliases:
  - MASBench
  - MasBench
  - MASBENCH
  - MAS-Orchestra
page_kind: benchmark
category: agentic
subcategory: controlled multi-agent versus single-agent task graphs
status: active
summary: >
  MASBench varies synthetic task graphs on five axes so a run can show when a
  multi-agent system beats a single agent, rather than quoting one headline score.
measures: >
  Each item is an English question plus a dependency graph of subtasks. Five
  axes set the graph: Depth (longest answer-containing chain), Horizon
  (intermediate answers that must be carried forward), Breadth (maximum
  in-degree), Parallel (independent components), and Robustness (subtasks
  with an adversarial note). Most items come from the iGSM math generator.
  Robustness mixes iGSM steps with RULER needle-in-a-haystack notes. The
  question is whether a multi-agent system (MAS) outperforms a single-agent
  system (SAS) as those axes grow. MAS-Orchestra, in the same paper, is the
  training method that uses this suite; this page documents the evaluation.
task_format: >
  Text question with an explicit or implicit subtask graph. Axis-specific
  train and test splits. Scoring is Avg@8 accuracy. Horizon and Robustness
  also check intermediate answers; Depth, Breadth, and Parallel score the
  final answer only (Parallel allows multiple finals).
metric:
  name: Avg@8 accuracy
  direction: higher_is_better
  unit: ''
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports Avg@8 accuracy for SAS versus MAS on each axis, with
    Qwen2.5-7B-Instruct as a typical orchestrator init and stronger or weaker
    sub-agents. Public-benchmark tables in the same paper (AIME, HotpotQA,
    BrowseComp+, GPQA) use percent-style scores for the MAS-Orchestra method
    and are not MASBench axis scores. Math checks use Hugging Face
    Math-Verify; other public benchmarks in that table use
    Llama-3.3-70B-Instruct as a judge.
dataset:
  size: 4583
  size_note: >
    Hugging Face card Salesforce/MASBench (configs as of 2026-06-11), test
    splits: depth 1,609, horizon 702, breadth 676, parallel 396, robustness
    1,200 (sum 4,583). Matching train splits: 3,993 / 2,174 / 2,000 / 1,807 /
    3,000. A combine config has 22,948 train rows and an empty test split.
    Paper v5 instead lists test sizes 1,195 / 567 / 676 / 567 / 600. Axis
    values range from 2 to 12. Train and test are generated with different
    hashes to avoid template overlap.
  url: https://huggingface.co/datasets/Salesforce/MASBench
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: >
    Per-axis train/test configs depth, horizon, breadth, parallel, robustness,
    plus a combine training config. See size_note for the paper versus Hub
    test-count mismatch.
  public_test_set: true
publisher:
  org: Salesforce AI Research, with MIT and University of Wisconsin-Madison
  authors:
    - Zixuan Ke
    - Yifei Ming
    - Austin Xu
    - Ryan Chin
    - Xuan-Phi Nguyen
    - Prathyusha Jwalapuram
    - Jiayu Wang
    - Semih Yavuz
    - Caiming Xiong
    - Shafiq Joty
  url: https://github.com/SalesforceAIResearch/MAS-Orchestra
paper:
  title: 'MAS-Orchestra: Understanding and Improving Multi-Agent Reasoning Through Holistic Orchestration and Controlled Benchmarks'
  arxiv: '2601.14652'
  url: https://arxiv.org/abs/2601.14652
  year: 2026
leaderboard_url: ''
repo_url: https://github.com/SalesforceAIResearch/MAS-Orchestra
released: '2026-01'
last_updated: '2026-06'
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ''
  note: >
    Axis plots in the paper show MAS gains that depend on structure and
    sub-agent strength, including cases where SAS wins on long sequential
    Depth. There is no single saturated headline number for MASBench itself.
contamination:
  risk: medium
  note: >
    Items are synthetic (iGSM, with RULER NIAH notes on Robustness). The
    authors state non-overlapping train/test hashes and no template overlap.
    The Hub dataset is public, including test splits, so later models could
    see the questions.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: 'Reference training and evaluation code in github.com/SalesforceAIResearch/MAS-Orchestra; dataset at huggingface.co/datasets/Salesforce/MASBench.'
tags:
  - multi-agent
  - orchestration
  - synthetic
  - iGSM
  - reasoning
sources:
  - url: https://arxiv.org/abs/2601.14652
    title: 'MAS-Orchestra (arXiv abs v5)'
    accessed: '2026-09-08'
  - url: https://arxiv.org/html/2601.14652v5
    title: 'MAS-Orchestra (arXiv HTML v5)'
    accessed: '2026-09-08'
  - url: https://github.com/SalesforceAIResearch/MAS-Orchestra
    title: 'SalesforceAIResearch/MAS-Orchestra repository'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/SalesforceAIResearch/MAS-Orchestra/main/README.md
    title: 'MAS-Orchestra README'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/SalesforceAIResearch/MAS-Orchestra/main/LICENSE.txt
    title: 'MAS-Orchestra Apache-2.0 LICENSE.txt'
    accessed: '2026-09-08'
  - url: https://huggingface.co/datasets/Salesforce/MASBench
    title: 'Salesforce/MASBench dataset card'
    accessed: '2026-09-08'
  - url: https://huggingface.co/datasets/Salesforce/MASBench/raw/main/README.md
    title: 'Salesforce/MASBench README'
    accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: 'Grok Build, batch-078 (Codex coordinated)'
  reviewed: ''
  reviewed_by: ''
---

## What it measures

MASBench is a controlled text suite for a simple question: when does a multi-agent system beat one agent? Each item is an English problem plus a subtask graph. Five axes change that graph. Depth lengthens the chain that holds the answer. Horizon adds intermediate answers the solver must keep. Breadth raises how many parents a subtask has. Parallel adds independent pieces. Robustness plants a short wrong note on some subtasks.

Most graphs come from iGSM math. Robustness weaves in needle-in-a-haystack notes from RULER. The suite is not a mobile GUI test. MAS-Orchestra, the training method in the same paper, learns to emit a whole agent system as one function-calling step. This page is about MASBench, the evaluation that method sits on.

## How it is scored

The paper reports Avg@8 accuracy for SAS and MAS on each axis. Horizon and Robustness grade intermediate answers as well as the final one. Depth, Breadth, and Parallel grade the final answer (Parallel may have several). Verification is therefore part of the axis, not a separate leaderboard.

Public-benchmark tables in the same paper (AIME24/25, HotpotQA, BrowseComp+, GPQA) score the MAS-Orchestra orchestrator, not MASBench. Those tables use percent-style numbers and a mix of Math-Verify and a Llama-3.3-70B-Instruct judge. Do not paste an AIME row into a MASBench cell.

## Dataset and licence

The Hub card `Salesforce/MASBench` is Apache-2.0. Test counts there (accessed 2026-09-08) are depth 1,609, horizon 702, breadth 676, parallel 396, robustness 1,200. Train counts match the paper on every axis except the test column. Paper v5 lists test sizes 1,195 / 567 / 676 / 567 / 600. This page treats the Hub card as the current dump and records the paper's older test counts as a disagreement. Axis values run from 2 to 12. The combine config is train-only (22,948 rows).

The paper licence on arXiv v5 is CC BY-SA 4.0. The code licence is Apache-2.0. The Hub card also warns that original iGSM and RULER terms still apply.

## Who publishes it

Salesforce AI Research leads, with Ryan Chin (MIT) and Jiayu Wang (University of Wisconsin-Madison). Corresponding authors are Zixuan Ke and Shafiq Joty. arXiv v1 is 21 January 2026; v5 is 21 May 2026. The GitHub README and Hub card mark ICML 2026. The GitHub citation block omits Jiayu Wang; the arXiv author list includes him.

## Lineage

iGSM supplies controllable math graphs. RULER supplies the Robustness notes. Related Salesforce work named in the README includes MAS-Zero and IlluMAS; those are not this suite. [mas_bench](mas_bench.md) is a different project: Android GUI-shortcut agents from Zhejiang University and vivo. The census id is `mas_orchestra` because the paper title is MAS-Orchestra; the evaluation's own name is MASBench.

## Saturation and contamination

Gains are not universal. Sequential Depth can favor SAS. Robustness is where MAS is supposed to hold up when SAS collapses. Test questions are public on the Hub, so later training runs could see them. Generation hashes are the authors' leakage control, not a hidden test set.

## How to run it

Download [Salesforce/MASBench](https://huggingface.co/datasets/Salesforce/MASBench). The training stack is [SalesforceAIResearch/MAS-Orchestra](https://github.com/SalesforceAIResearch/MAS-Orchestra) (conda env, verl, GRPO configs). Example scripts train an orchestrator on one axis or on a public set such as BrowseComp+. No lm-eval or inspect task name was found. Report the axis, the orchestrator, the sub-agent, and Avg@8, not a lone accuracy.

## Reading the numbers

A MAS win on Parallel or Robustness does not imply a win on Depth. Read the five axes before quoting a gain. AIME or GPQA figures in the paper measure the trained orchestrator on public exams, not MASBench. Do not confuse this suite with [mas_bench](mas_bench.md). Cost is part of the method story (the paper claims large efficiency gains for MAS-Orchestra) and is not a MASBench metric.
