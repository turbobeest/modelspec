---
id: usaco
name: "USACO"
aliases:
  - "USACOBench"
page_kind: benchmark
category: coding
subcategory: "olympiad-level competitive programming (algorithmic problem solving)"
status: active
summary: >-
  A 307-problem benchmark built from USA Computing Olympiad contests that tests whether a model
  can write a Python program that passes hidden stdin/stdout test cases under time and memory limits.
measures: >
  USACO gives a model a competitive-programming problem statement, drawn from real USA Computing
  Olympiad contests, and asks it to write a Python program that reads from standard input and
  writes to standard output. Problems span four official USACO difficulty tiers (bronze, silver,
  gold, platinum), so solving them requires algorithmic problem solving, not just syntactic code
  generation: correct handling of edge cases, algorithmic techniques appropriate to the tier
  (from basic simulation at bronze to advanced data structures and graph algorithms at platinum),
  and code that runs within contest time and memory constraints.
task_format: >
  A model receives the problem statement and must produce a Python solution; inspect_evals extracts
  the code from a ```python markdown block. The solution is executed against 10-17 hidden
  stdin/expected-stdout test cases per problem inside a sandboxed environment with CPU time and
  memory limits, and is scored correct only if it matches expected output exactly on every test
  case. The original paper reports pass@1 under zero-shot chain-of-thought prompting as its main
  number and also studies inference-time methods (retrieval over episodic knowledge, self-reflection,
  human-in-the-loop hints).
metric:
  name: "pass@1 (fraction of problems solved by a single generated solution passing all hidden tests)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 0.0
  human_baseline: 35.83
  baseline_note: >
    Human baseline of 35.83% average pass@1 is taken from past USACO contest performance, as
    reported in the paper and echoed in the inspect_evals task metadata. Random baseline is
    effectively 0 since problems require generated, executable code rather than a choice among
    options.
dataset:
  size: 307
  size_note: >
    307 curated problems (the "usaco_subset307" set used in the paper's main results): 123 bronze,
    100 silver, 63 gold, and 21 platinum, each with 10-17 hidden test cases. The dataset authors
    also released a larger "usaco_v2" set of 484 problems covering all USACO problems with test
    cases available up to September 2023; inspect_evals supports loading either version but
    defaults to the 307-problem set used in the paper.
  url: "https://princeton-nlp.github.io/USACOBench/"
  license: ""
  languages:
    - en
  modalities:
    - text
    - code
  splits: "No train/test split; all 307 (or 484) problems are used as a single evaluation set, distributed via a Google Drive link from the project's GitHub repository"
  public_test_set: true
publisher:
  org: "Princeton NLP Group"
  authors:
    - "Quan Shi"
    - "Michael Tang"
    - "Karthik Narasimhan"
    - "Shunyu Yao"
  url: "https://princeton-nlp.github.io/USACOBench/"
paper:
  title: "Can Language Models Solve Olympiad Programming?"
  arxiv: "2404.10952"
  url: "https://arxiv.org/abs/2404.10952"
  year: 2024
leaderboard_url: "https://hal.cs.princeton.edu/usaco"
repo_url: "https://github.com/princeton-nlp/USACO"
released: "2024-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 20.2
  as_of: "2024-04"
  note: >
    At release, GPT-4 scored 8.7% pass@1 zero-shot chain-of-thought and 20.2% with the paper's
    best inference-time method (self-reflection plus retrieval over episodic knowledge), both far
    below the 35.83% human contestant average, so the benchmark was clearly unsaturated. No
    maintained leaderboard tracking current frontier-model scores across all four difficulty tiers
    was independently confirmed for this page beyond the HAL leaderboard listing, so present-day
    saturation is not established.
contamination:
  risk: medium
  note: >
    Problems and reference solutions come from real, publicly archived USACO contests dating back
    years before the paper's release, and the paper's data (problem text, official analyses,
    reference code) is distributed openly, so exact problem statements and even solutions could
    appear in training data for models trained on contest-archive scrapes or on the released
    dataset itself. The 484-problem usaco_v2 extension only goes up to problems with test cases
    available by September 2023, so newer real USACO contests held after that date are not
    covered and would be less contaminated if used instead.
harness:
  lm_eval: ""
  inspect_evals: "usaco"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - coding
  - competitive-programming
  - algorithms
  - agentic
sources:
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/usaco"
    title: "inspect_evals usaco task directory README (dataset description, 307-problem breakdown by tier, scoring method, example pass@1 figures)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/usaco/usaco.py"
    title: "inspect_evals usaco.py implementation: usaco_subset307 vs usaco_v2 (484 problems) dataset options, sandboxed scorer, code-block extraction"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/usaco/eval.yaml"
    title: "inspect_evals usaco eval.yaml metadata: coding group, human baseline pass@1 0.3583, arxiv 2404.10952 reference"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2404.10952"
    title: "Can Language Models Solve Olympiad Programming? (Shi, Tang, Narasimhan, Yao, 2024): 307 problems (123/100/63/21 by tier), 10-17 hidden tests per problem, GPT-4 8.7% zero-shot CoT pass@1, 20.2% best method, human average 35.83%"
    accessed: "2026-09-08"
  - url: "https://github.com/princeton-nlp/USACO"
    title: "princeton-nlp/USACO repository README: usaco307 vs usaco_v2 (484 problems, test cases up to September 2023) dataset description and data access via Google Drive"
    accessed: "2026-09-08"
  - url: "https://hal.cs.princeton.edu/usaco"
    title: "Holistic Agent Leaderboard (HAL) USACO leaderboard page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

USACO gives a model a competitive-programming problem statement drawn from real USA Computing
Olympiad contests and asks it to write a Python program that reads input from stdin and writes the
correct output to stdout. The 307 problems span the four official USACO difficulty tiers, bronze
through platinum, so the benchmark exercises a range of algorithmic problem solving: careful
simulation and edge-case handling at the easy end, and advanced data structures, dynamic
programming or graph algorithms at the hard end, in addition to producing runnable, correctly
formatted code.

## How it is scored

A generated solution is extracted from a Python code block and run against 10 to 17 hidden
stdin/expected-stdout test cases per problem inside a sandboxed environment with CPU time and
memory limits matching contest constraints. The problem counts as solved (pass@1) only if the
program's output matches the expected output exactly on every hidden test case; there is no partial
credit for passing some but not all tests. The paper's headline numbers use zero-shot chain-of-thought
prompting and a single sample per problem; it separately studies inference-time methods such as
self-reflection and retrieval over episodic knowledge, and a human-in-the-loop hint condition, which
are not directly comparable to the single-sample pass@1 numbers.

## Dataset and licence

The benchmark's main set holds 307 problems (123 bronze, 100 silver, 63 gold, 21 platinum), each
paired with its official problem statement, 10 to 17 hidden test cases, a reference solution, and
(for many problems) the official contest analysis. The authors also released a larger 484-problem
"usaco_v2" set covering all USACO problems with available test cases through September 2023. No
explicit licence for the dataset was found in the paper or the GitHub repository read for this
page; data is distributed via a Google Drive link referenced from the repository rather than
through a licensed dataset host.

## Who publishes it

USACO was introduced by Quan Shi, Michael Tang, Karthik Narasimhan and Shunyu Yao of the Princeton
NLP Group in the 2024 paper "Can Language Models Solve Olympiad Programming?" The project
maintains its own site and GitHub repository, and results are also tracked on Princeton's Holistic
Agent Leaderboard (HAL).

## Lineage

USACO is not built as a subset or successor of an earlier benchmark tracked in this repository; it
adapts an existing, decades-old human competition (the USA Computing Olympiad) into a language
model evaluation set. It has no predecessor or successor page in this repository. inspect_evals
implements it as a single task with a configurable dataset version (the 307-problem paper set or
the 484-problem extended set) rather than as separate subset pages.

## Saturation and contamination

At release, GPT-4 solved only 8.7% of problems zero-shot with chain-of-thought prompting, rising to
20.2% with the paper's best inference-time method, both well short of the reported 35.83% average
human contestant pass rate, so the benchmark was clearly unsaturated in 2024. No maintained,
independently confirmed leaderboard tracking current frontier-model scores across all four
difficulty tiers was found for this page beyond a listing on the Holistic Agent Leaderboard, so
present-day saturation is not established. Contamination risk is medium: the problems are drawn
from publicly archived real contests that predate the paper, and the curated dataset itself
(statements, hidden tests, reference solutions and official analyses) is openly distributed, so
models trained on contest-archive scrapes or on the released benchmark files could have seen exact
problems and solutions.

## How to run it

Run via inspect_evals with the `usaco` task, which loads either the 307-problem paper subset or
the 484-problem extended set, executes generated code in a sandboxed Docker environment with CPU
and memory limits, and reports pass@1 with standard error. The original paper's evaluation harness
and data are in the `princeton-nlp/USACO` GitHub repository. Numbers are hard to compare across
reports that differ in prompting strategy (plain zero-shot vs. chain-of-thought vs. retrieval or
self-reflection methods), number of samples per problem, or which of the two dataset versions was
used.

## Reading the numbers

A high pass@1 on USACO shows a model can turn an olympiad-style problem statement into working,
efficient Python code that handles edge cases correctly under real contest constraints, a
meaningfully harder bar than typical function-completion coding benchmarks. Because scores are
reported per difficulty tier, an aggregate number can hide a model that solves nearly all bronze
problems but almost none at platinum; check the tier breakdown before treating one score as
representative. The gap to the 35.83% human average, and the large jump from zero-shot to
inference-time methods in the original paper, both indicate most gains here as of the paper's
release came from search and self-correction strategies rather than raw model capability alone.
