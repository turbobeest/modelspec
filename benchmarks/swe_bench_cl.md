---
id: swe_bench_cl
name: SWE-Bench-CL
aliases: ["SWE-bench-CL"]
page_kind: benchmark
category: coding
subcategory: "continual learning over SWE-bench Verified sequences"
status: proposed
summary: "A 273-task continual-learning reformulation of SWE-bench Verified: eight chronological repository sequences with forgetting and transfer metrics."
measures: >
  SWE-Bench-CL asks whether a coding agent improves, transfers, and avoids
  forgetting as it walks a stream of GitHub issues from one repository. The
  underlying issues are SWE-bench Verified tasks, reordered into curricula
  instead of scored as i.i.d. bugs.
task_format: >
  Eight repository sequences (273 tasks total) are ordered first by issue
  creation time, then by human-estimated fix time. After each task, evaluation
  can re-test earlier tasks. The authors also describe a LangGraph agent with
  FAISS memory as a reference scaffold, not as a required runtime.
metric:
  name: "average accuracy (plus forgetting, transfer, and CL-Score)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper defines ACC, forgetting, forward/backward transfer, tool-use efficiency, CL-P/CL-S, and a composite CL-Score. It does not publish a completed frontier-model table on those metrics."
dataset:
  size: 273
  size_note: >
    Eight sequences from SWE-bench Verified repositories with at least 15
    tasks each: django/django 50, sympy/sympy 50, sphinx-doc/sphinx 44,
    matplotlib/matplotlib 34, scikit-learn/scikit-learn 32, astropy/astropy 22,
    pydata/xarray 22, pytest-dev/pytest 19 (273 total). Difficulty buckets
    follow Verified wall-clock labels (<15 min, 15 min-1 h, 1-4 h, >4 h).
  url: "https://github.com/thomasjoshi/agents-never-forget"
  license: MIT
  languages: [Python]
  modalities: [code, text]
  splits: "eight repository sequences; no separate train/test split"
  public_test_set: true
publisher:
  org: "Independent course project (COMS 4995)"
  authors: [Thomas Joshi, Shayan Chowdhury, Fatih Uysal]
  url: "https://github.com/thomasjoshi/agents-never-forget"
paper:
  title: "SWE-Bench-CL: Continual Learning for Coding Agents"
  arxiv: "2507.00014"
  url: "https://arxiv.org/abs/2507.00014"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/thomasjoshi/agents-never-forget"
released: "2025-06"
last_updated: ""
lineage:
  family: swe_bench
  predecessor: swe_bench_verified
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No maintained leaderboard was found. A trial against the stock SWE-bench
    harness produced low pass rates that the authors attribute to container
    mismatch with Verified-derived sequences, not to a calibrated CL ranking.
contamination:
  risk: high
  note: >
    Every item is a SWE-bench Verified instance, hence a public merged pull
    request. Sequencing does not hide gold patches. Continual-learning metrics
    can still be informative if the agent is not allowed to reread hidden tests.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference code is eval_v1 (SWE-bench Docker harness), eval_v2_agent
    (LangGraph plus FAISS), and eval_v3_swe-agent in
    thomasjoshi/agents-never-forget. The README also names eval_v3_agent; the
    repository folder is eval_v3_swe-agent. The authors report that official
    SWE-bench dump containers do not line up cleanly with this Verified-derived
    order.
tags: [coding, agentic, continual-learning, github-issues, python]
sources:
  - url: "https://arxiv.org/abs/2507.00014"
    title: "SWE-Bench-CL (arXiv:2507.00014v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2507.00014v1"
    title: "SWE-Bench-CL HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/thomasjoshi/agents-never-forget"
    title: "thomasjoshi/agents-never-forget README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/thomasjoshi/agents-never-forget/main/LICENSE"
    title: "SWE-Bench-CL MIT licence"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-Bench-CL measures continual learning on software issues, not single-shot
repair. An agent walks a chronological sequence of Verified tasks from one
Python repository, then another. The intended skills are accumulating project
knowledge, transferring across related files, and keeping earlier fixes working.

The issues themselves are the familiar SWE-bench Verified bugs. What changes is
order and scoring: tasks are grouped into eight repository curricula with
difficulty ramps, and file-overlap metadata marks possible dependencies.

## How it is scored

The paper defines a performance matrix after each new task. From that matrix it
derives average accuracy, forgetting, forward and backward transfer, tool-use
efficiency, CL-plasticity, CL-stability, and a composite CL-Score. A single
"% resolved" number is not the intended headline. No completed frontier-model
table on those metrics appears in the paper. A stock-harness trial is presented
mainly to show that i.i.d. SWE-bench containers are a poor fit.

## Dataset and licence

The GitHub repository is MIT-licensed. The JSON curriculum contains 273 tasks
across django, sympy, sphinx, matplotlib, scikit-learn, astropy, xarray, and
pytest. Construction keeps Verified fields (problem statement, gold patch, tests)
and adds sequence position, difficulty, and overlapping files. There is no
held-out private split.

## Who publishes it

Thomas Joshi, Shayan Chowdhury, and Fatih Uysal posted arXiv:2507.00014 on
2025-06-13 (the 2507 identifier is an arXiv cs.LG overflow id). The README
frames the work as a Columbia COMS 4995 course project with Prof. Richard Zemel,
advised by Tom Zollo. Code and data live at github.com/thomasjoshi/agents-never-forget.
No project leaderboard site was found. The paper outlines CL experiments as
ongoing rather than reporting a completed frontier-model table.

## Lineage

This is a protocol on [SWE-bench Verified](swe_bench_verified.md), not a new
issue pool. It should not be merged with Verified scores or with
[SWE-bench Lite](swe_bench_lite.md). It is also not a live-updating set like
[SWE-bench-Live](swe_bench_live.md). The authors note that SWE-bench dump
images target original SWE-bench and Lite, which is why they shipped their own
eval scripts.

## Saturation and contamination

Saturation is unknown; there is no public ranking of current agents on the CL
metrics. Contamination risk is high for the same reason Verified is high: gold
patches are public. Sequential scoring can still reveal forgetting even when
some individual bugs are familiar.

## How to run it

Use the repository's `data/SWE-Bench-CL-Curriculum.json` and one of the
`eval_v1`, `eval_v2_agent`, or `eval_v3_swe-agent` entry points. Say whether
memory retrieval was on, and whether you re-tested prior tasks after each new
issue. Do not report a number from the official `swebench` CLI on these
sequences as a SWE-Bench-CL score.

## Reading the numbers

A CL-Score or forgetting figure is only comparable under the same retest
schedule and memory policy. A high final accuracy with large forgetting means
the agent is still solving isolated Verified bugs, not learning the repo.
Until a maintained leaderboard exists, treat published figures as protocol
demonstrations. Pair any result with a standard Verified score on the same
model so the i.i.d. baseline is visible.
