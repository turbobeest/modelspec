---
id: swe_bench_science
name: SWE-bench Science
aliases: ["SWE-bench-Science"]
page_kind: benchmark
category: coding
subcategory: "scientific software engineering / repository-level repair"
status: active
summary: "119 repository-level scientific coding tasks across 98 GitHub projects and 20 domains, scored by held-out programmatic verifiers."
measures: >
  SWE-bench Science tests whether a coding agent can change a real scientific
  computing repository while preserving domain contracts such as units, file
  formats, numerics, and geometry. Each task starts from a fixed baseline commit
  and is checked in a clean environment, not by matching a gold patch.
task_format: >
  The agent works in a pinned environment image, then a separate verifier image
  applies the candidate patch, rebuilds if needed, and runs held-out tests.
  Tasks are grouped into issue-driven, expert-exploratory, and
  engineering-integration paradigms. Default runs use 96 unrestricted-license
  tasks; 23 restricted-license tasks require an explicit opt-in.
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "Pass@1 requires every applicable private test to pass. The leaderboard also reports public/private, fail-to-pass, pass-to-pass, and per-paradigm rates. No human baseline is published."
dataset:
  size: 119
  size_note: >
    119 release tasks (ids 001-119) from 98 GitHub repositories and 20
    benchmark-level scientific domains. Default selection: 96 unrestricted
    tasks. Restricted selection: 23 tasks (18 GPL-family plus five others).
    A 91-task science-knowledge ablation split is marked in tasks.csv. A
    Hard70 subset was defined on 2026-08-28 from the 70 tasks with lowest mean
    reward across 12 complete model runs. Per-task language labels are mostly
    Python (103), with smaller C++, C, Fortran, MATLAB/Octave, and mixed
    bindings counts.
  url: "https://huggingface.co/datasets/OpenMOSS-Team/SWE-bench-Science"
  license: MIT
  languages: [Python, C++, C, Fortran, MATLAB]
  modalities: [code, text]
  splits: "119 tasks; default 96 unrestricted; 23 restricted opt-in; 91-task ablation; Hard70 subset"
  public_test_set: false
publisher:
  org: OpenMOSS
  authors: [Zhipeng Xu, Jiahao Lu, Yining Zheng, Yuxin Wang, Xipeng Qiu]
  url: "https://swescience.github.io/"
paper:
  title: "SWE-bench Science: Can Coding Agents Resolve Engineering Tasks in Science?"
  arxiv: "2608.19799"
  url: "https://arxiv.org/abs/2608.19799"
  year: 2026
leaderboard_url: "https://swescience.github.io/"
repo_url: "https://github.com/OpenMOSS/SWE-bench-Science"
released: "2026-08"
last_updated: "2026-09"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: []
  variants: [swe_bench_verified]
saturation:
  status: open
  top_score: 47.9
  as_of: "2026-09"
  note: >
    Leaderboard updated 2026-09-01: Claude-Opus-5 (max) with Claude Code at
    47.90% overall pass@1, then DeepSeek-V4-Pro (max) 42.02% and GPT-5.6-sol
    (max) 40.34%. Hard70 is much lower (21.43% for the same Claude run). Public
    tests are near ceiling for top models; private tests are the binding
    constraint.
contamination:
  risk: medium
  note: >
    Source repositories are public scientific GitHub projects, so pretraining
    may include surrounding code. The release withholds gold patches, private
    verifier tests, credentials, and trajectories. That limits answer leakage
    relative to vanilla SWE-bench, but does not hide the public codebases.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Harbor-format tasks run with Pier (pinned datacurve-pier==0.3.0). Agents
    such as Claude Code, Codex, and mini-swe-agent are selected at runtime.
    Not confirmed in lm-evaluation-harness, HELM, OpenCompass, or BIG-bench.
tags: [coding, agentic, scientific-computing, docker, harbor, pier, long-horizon]
sources:
  - url: "https://arxiv.org/abs/2608.19799"
    title: "SWE-bench Science (arXiv:2608.19799v2)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OpenMOSS-Team/SWE-bench-Science"
    title: "OpenMOSS-Team/SWE-bench-Science dataset card"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenMOSS/SWE-bench-Science"
    title: "OpenMOSS/SWE-bench-Science repository"
    accessed: "2026-09-08"
  - url: "https://swescience.github.io/"
    title: "SWE-bench Science leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OpenMOSS-Team/SWE-bench-Science/raw/main/data/statistics.md"
    title: "SWE-bench Science release statistics"
    accessed: "2026-09-09"
  - url: "https://huggingface.co/datasets/OpenMOSS-Team/SWE-bench-Science/raw/main/data/tasks.csv"
    title: "SWE-bench Science tasks.csv"
    accessed: "2026-09-09"
  - url: "https://raw.githubusercontent.com/OpenMOSS/SWE-bench-Science/main/LICENSE"
    title: "SWE-bench Science MIT licence"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-bench Science asks a coding agent to repair or extend real scientific software.
The model gets a repository at a fixed commit and must produce a change that keeps
scientific contracts intact: units, coordinate systems, file formats, and numerical
invariants. Ordinary GitHub-issue benchmarks rarely test those contracts.

Each of the 119 tasks sits in one of three paradigms. Issue-driven tasks follow a
reported defect. Expert-exploratory tasks need domain judgement. Engineering-
integration tasks stitch scientific code into a larger workflow. Most tasks are
Python; a minority use C, C++, Fortran, or MATLAB/Octave.

## How it is scored

The headline metric is pass@1 on private verifier tests. A trial counts only if
every applicable held-out test passes after a clean rebuild. The public leaderboard
also lists public-test rate, fail-to-pass, pass-to-pass, and scores for the three
paradigms. Public tests are much easier than private ones: the leading Claude Code
run is at 96.64% public and 47.90% overall. There is no published human baseline.

## Dataset and licence

The release metadata and tooling are MIT. Upstream scientific sources keep their
own licences; 23 tasks need `--allow-restricted-licenses` because of GPL-family
code or restricted materials (18 GPL-family rows plus five other restricted rows).
Hugging Face ships `data/tasks.csv` (119 rows, 98 distinct `repository_url` values)
and thin Harbor bundles. Fine-grained `domain` strings in the CSV are more
numerous than the paper's 20 benchmark-level domains. Docker Hub holds one
environment image and one verifier image per task, pinned by linux/amd64 digest.
Gold patches and private tests are not in the public dataset.

## Who publishes it

OpenMOSS authors Zhipeng Xu, Jiahao Lu, Yining Zheng, Yuxin Wang, and Xipeng Qiu
posted arXiv:2608.19799 on 2026-08-20 (v2 on 2026-09-01). The dataset, GitHub
docs, and leaderboard are dated August–September 2026. The project site is
swescience.github.io.

## Lineage

The work sits in the [SWE-bench](swe_bench.md) family as a scientific-computing
variant, not a drop-in replacement for [SWE-bench Verified](swe_bench_verified.md).
It borrows the repository-level, test-graded shape but uses Harbor/Pier instead of
the SWE-bench CLI, and it holds out verifier tests. It is unrelated to Lab-bench
or other science QA sets.

## Saturation and contamination

Top overall pass@1 is 47.90% as of 2026-09-01, with a wide spread down to 7.56%.
Hard70 remains at 21.43% for the leader. The benchmark is open. Public scientific
repos create medium contamination risk; withheld verifiers reduce answer copying
but not exposure to the surrounding code.

## How to run it

Download the Hugging Face dataset, materialize a selection with
`scripts/materialize.py`, and run Pier (`datacurve-pier==0.3.0`) with Docker
linux/amd64 support. Name the selection (default 96, all 119, ablation 91, or
Hard70), the agent, and the model. Do not compare a public-test number with
overall pass@1.

## Reading the numbers

A high overall pass@1 means the agent preserved private scientific checks, not
that it merely compiled or passed the public smoke tests. Report the paradigm
split: engineering-integration is much harder than expert-exploratory for the
current leader (27.78% vs 65.31%). Pair the score with Verified or SWE-bench Pro
if you need a general software-engineering baseline rather than a science-stack
one.
