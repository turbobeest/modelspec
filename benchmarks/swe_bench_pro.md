---
id: swe_bench_pro
name: SWE-bench Pro
aliases: ["SWE-Bench Pro"]
page_kind: benchmark
category: coding
subcategory: "GitHub issue resolution / patch generation"
status: active
summary: "Scale AI's harder, contamination-resistant successor in spirit to SWE-bench Verified: 1,865 long-horizon tasks across public copyleft, held-out and private commercial codebases."
measures: >
  SWE-bench Pro follows the same task shape as SWE-bench — resolve a real issue in a real repository
  with a patch — but selects for longer, more involved changes and for source code that is unlikely to
  be in a model's training data. Scale AI built it because frontier models were already scoring above
  70% on SWE-bench Verified, and wanted a benchmark that separates genuine software-engineering ability
  from memorised or near-memorised solutions on well-known open-source Python projects.
task_format: >
  Given an issue and repository access, the system produces a patch, applied and graded inside a
  container against the repository's own tests, in the same fail-to-pass / pass-to-pass style as
  SWE-bench. Tasks are deliberately long-horizon: the paper reports resolved instances require
  changes averaging 107.4 lines of code across 4.1 files, more than a typical SWE-bench Verified fix.
metric:
  name: "% resolved"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline published."
dataset:
  size: 1865
  size_note: >
    1,865 instances across 41 actively maintained repositories, split into three subsets: 731 public
    instances from 11 repositories released under strong copyleft licences (for example GPL), chosen
    because their licence terms make inclusion in training data legally unattractive; 858 held-out
    instances from 12 further public repositories, kept out of the open release; and 276 commercial
    instances from 18 private, proprietary startup codebases under formal partnership with Scale. Each
    repository contributes roughly 50-100 tasks.
  url: "https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro"
  license: MIT
  languages: [Go, Python, JavaScript, TypeScript]
  modalities: [code, text]
  splits: "public (731, open), held-out (858, withheld), commercial (276, withheld)"
  public_test_set: false
publisher:
  org: "Scale AI (Scale Research Team)"
  authors: [Xiang Deng, Jeff Da, Edwin Pan, Yannis Yiming He, Charles Ide, Kanak Garg, Niklas Lauffer, Andrew Park, Nitin Pasari, Chetan Rane, Karmini Sampath, Maya Krishnan, Srivatsa Kundurthy, Sean Hendryx, Zifan Wang, Vijay Bharadwaj, Jeff Holm, Raja Aluri, Chen Bo Calvin Zhang, Noah Jacobson, Bing Liu, Brad Kenstler]
  url: "https://scale.com/research/swe_bench_pro"
paper:
  title: "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?"
  arxiv: "2509.16941"
  url: "https://arxiv.org/abs/2509.16941"
  year: 2025
leaderboard_url: "https://labs.scale.com/leaderboard/swe_bench_pro_public"
repo_url: "https://github.com/scaleapi/SWE-bench_Pro-os"
released: "2025-09"
last_updated: "2025-11"
lineage:
  family: swe_bench
  predecessor: swe_bench_verified
  successors: []
  variants: []
saturation:
  status: open
  top_score: 23.3
  as_of: "2025-09"
  note: >
    At release, the best models (GPT-5 at 23.3%, Claude Opus 4.1 at 23.1%) resolved under a quarter of
    public-subset tasks, a steep drop from the 70%+ scores the same class of model reaches on SWE-bench
    Verified. Weaker or older models score far lower still (GPT-4o 4.9%, DeepSeek/Qwen-3 32B 3.4%),
    giving wide separation between models. Scores drop further on the private commercial subset,
    consistent with the benchmark's contamination-resistance goal. This is an early, wide-open
    benchmark, not a saturated one.
contamination:
  risk: low
  note: >
    Low by explicit design rather than by independent audit: the public subset is drawn from
    strong-copyleft-licensed repositories that Scale argues are unlikely to appear in training data for
    legal reasons, and the commercial subset is entirely private code obtained under partnership,
    unpublished anywhere a crawler could reach it. This reflects the publisher's stated design intent;
    it was not independently verified for this page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The paper's own results use the SWE-Agent scaffold. Scale publishes evaluation code
    (swe_bench_pro_eval.py) and Docker-based test infrastructure in the SWE-bench_Pro-os repository,
    supporting distributed evaluation with configurable worker counts.
tags: [coding, agentic, github-issues, patch-generation, contamination-resistant, long-horizon, private-eval]
sources:
  - url: "https://scale.com/blog/swe-bench-pro"
    title: "SWE-Bench Pro: Raising the Bar for Agentic Coding"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2509.16941"
    title: "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?"
    accessed: "2026-09-07"
  - url: "https://github.com/scaleapi/SWE-bench_Pro-os"
    title: "scaleapi/SWE-bench_Pro-os repository"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-bench Pro measures the same core skill as SWE-bench — turning a real issue into a patch a
repository's own tests accept — but is built specifically to resist the two failure modes Scale AI
argues undermine SWE-bench Verified at the frontier: data contamination and tasks that are easier than
real engineering work. Instances require substantial, multi-file changes rather than small localized
fixes, and are drawn from code that is legally or practically unlikely to have entered a model's
training data.

## How it is scored

Scoring follows the SWE-bench pattern: a generated patch is applied inside a container and graded by
running tests derived from the original fix, with fail-to-pass tests confirming the issue is resolved
and pass-to-pass tests confirming nothing else broke. Scale's own evaluation used the SWE-Agent scaffold
to produce the headline numbers, and its released evaluation scripts support running the same protocol
at scale with distributed workers.

## Dataset and licence

The evaluation code is MIT-licensed. The dataset totals 1,865 instances across 41 repositories, but only
the 731-instance public subset (11 repositories, all under strong copyleft licences such as GPL) is
openly released; 858 further held-out instances and 276 private commercial instances (from 18 startups,
under formal partnership) are kept back specifically so they cannot leak into future training runs.
Tasks average 107.4 lines of code changed across 4.1 files, a materially larger footprint than a typical
SWE-bench Verified fix.

## Who publishes it

SWE-bench Pro is a Scale AI Research Team project, led by Xiang Deng and Jeff Da with more than a dozen
co-authors, first published 2025-09-19 (blog) and 2025-09-21 (arXiv paper), with a revised paper version
in November 2025. Scale maintains the dataset, open-source evaluation repository and two separate
leaderboards.

## Lineage

SWE-bench Pro is not part of the official swebench.com project; it is an independent benchmark from
Scale AI that explicitly positions itself as picking up "where SWE-Bench Verified leaves off," reusing
SWE-bench's task format and fail-to-pass/pass-to-pass scoring convention while sourcing new, harder,
contamination-resistant tasks. It is catalogued in this repository as a member of the `swe_bench` family
alongside `swe_bench_verified`, `swe_bench_multilingual`, `swe_bench_multimodal` and `swe_bench_agent`.

## Saturation and contamination

The benchmark is wide open: the best models resolve under a quarter of public-subset tasks, with a long
tail of weaker models scoring in the single digits, and scores drop again on the private commercial
subset (for example Claude Opus 4.1 from roughly 23% to 17.8%, GPT-5 from roughly 23% to 14.9%, per
Scale's own reporting). Contamination risk is low by design — copyleft licensing for the public set,
full privacy for the commercial set — though that is the publisher's own claim about its methodology
rather than something this page independently verified.

## How to run it

Public-subset evaluation uses the open SWE-bench_Pro-os repository's Docker-based harness and evaluation
scripts; the held-out and commercial subsets are only accessible through Scale's own leaderboard
submission process, so those numbers cannot be independently reproduced by a third party. Because the
published results use a specific scaffold (SWE-Agent), scores from other harnesses are not guaranteed to
be comparable without checking which scaffold produced them.

## Reading the numbers

A SWE-bench Pro score in the 20s should be read as evidence of real difficulty separation at the current
frontier, not as a sign the benchmark is broken: it is designed to be hard, and its low scores relative
to SWE-bench Verified are the point, not a bug. The gap between a model's public-subset and
commercial-subset scores is itself informative — a large gap suggests a model leans on some form of
prior exposure or overfitting to public conventions rather than general code-repair skill.
