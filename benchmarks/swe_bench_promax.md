---
id: swe_bench_promax
name: SWE-Bench ProMax
aliases: ["SWE-Bench-ProMax", "SWE-bench ProMax"]
page_kind: benchmark
category: coding
subcategory: "multilingual repository-level refactoring"
status: active
summary: "170 expert-curated multilingual refactoring tasks from post-2025 commits; gold patches average 11.4 files and 261.6 lines."
measures: >
  SWE-Bench ProMax tests whether an agent can carry out a large, behaviour-preserving
  refactor in a real repository. Instances come from post-2025 GitHub commits
  tagged as refactoring, not from bug-fix issues. The agent must change many
  files so that a reviewed test suite still passes.
task_format: >
  Given a rewritten issue description and a Dockerized pre-refactor checkout, the
  agent edits the tree. An instance is resolved only if every test in the suite
  passes. Issue text is rewritten from scratch so commit messages do not leak
  the gold patch.
metric:
  name: "resolve rate (pass@1)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline is published. The paper also reports API cost and step counts per instance."
dataset:
  size: 170
  size_note: >
    170 instances from 70 repositories after filtering 29,782 candidates.
    Language counts on the dataset card: Python 29, TypeScript 28, Java 26,
    Go 23, C++ 22, Rust 22, C 20. Gold patches average 11.4 source files and
    261.6 lines of code. Test patches add about 4.5 files and 185.5 lines.
  url: "https://huggingface.co/datasets/swe-bench-promax/SWE-Bench-ProMax"
  license: ""
  languages: [Python, Java, TypeScript, Go, C, C++, Rust]
  modalities: [code, text]
  splits: "single test split of 170 instances"
  public_test_set: true
publisher:
  org: "SWE-Bench-ProMax authors"
  authors: [Yuling Shi, Jinghan Xu, Kelin Fu, Wenhao Zeng, Shilin He, Lei Zhang, Yue Liu, Zelin Zhao, Terry Yue Zhuo, Jialun Cao, Siyu Ye, Tianyu Liu, Kai Cai, Shing-Chi Cheung, Xiaodong Gu]
  url: "https://huggingface.co/datasets/swe-bench-promax/SWE-Bench-ProMax"
paper:
  title: "SWE-Bench ProMax: Benchmarking Agents on Large-Scale Multilingual Code Refactoring"
  arxiv: "2608.09802"
  url: "https://arxiv.org/abs/2608.09802"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-08"
last_updated: "2026-08"
lineage:
  family: swe_bench
  predecessor: swe_bench_verified
  successors: []
  variants: [swe_bench_pro]
saturation:
  status: open
  top_score: 41.2
  as_of: "2026-08"
  note: >
    In the COLM 2026 paper, GPT-5.2 with OpenHands resolved 41.2% of 170
    instances. Claude Sonnet 4.6 reached 38.8% on the same scaffold. mini-swe-agent
    scores are much lower (21.8% for GPT-5.2). No independent public leaderboard
    was found.
contamination:
  risk: medium
  note: >
    Commits are public but dated after January 2025, and issue text is rewritten
    so the gold patch is not sitting in the prompt. That is weaker protection
    than a private corpus, and stronger than shipping raw commit messages.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Dataset-card runner: python src/evaluation/test_run.py with Docker, a
    preds.json file, swe-bench-promax.json, and eval.json. Paper results use
    OpenHands and mini-swe-agent. Not confirmed in lm-eval, HELM, OpenCompass,
    or BIG-bench.
tags: [coding, agentic, refactoring, multilingual, docker, patch-generation]
sources:
  - url: "https://arxiv.org/abs/2608.09802"
    title: "SWE-Bench ProMax (arXiv:2608.09802v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2608.09802v1"
    title: "SWE-Bench ProMax HTML full text"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/swe-bench-promax/SWE-Bench-ProMax"
    title: "swe-bench-promax/SWE-Bench-ProMax dataset card"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-Bench ProMax measures large-scale refactoring, not bug fixing. The agent
receives a rewritten specification and a repository from before a real refactor
commit. It must coordinate edits across many files while keeping behaviour that
the test suite encodes. Gold patches average 11.4 source files and 261.6 lines,
far above typical SWE-bench Verified edits.

The set covers seven languages: Python, Java, TypeScript, Go, C, C++, and Rust.
Tasks with thin cross-file scope were dropped during curation.

## How it is scored

Resolve rate is pass@1: the final tree must pass every test. The paper evaluates
all 170 instances and also reports per-language rates, dollars per instance, and
agent steps. Scaffold choice is part of the result. GPT-5.2 moves from 21.8%
under mini-swe-agent to 41.2% under OpenHands. There is no human baseline.

## Dataset and licence

The public release is 170 JSON instances plus `eval.json` scripts, on Hugging
Face as swe-bench-promax/SWE-Bench-ProMax (created 2026-08-10; last modified
2026-08-26). Source repositories use ordinary open-source licences such as MIT,
Apache-2.0, BSD, and some GPL/AGPL; the dataset card itself does not declare a
licence, so that field is left empty. Gold patches and tests are in the
download. Issue descriptions were rewritten so they do not quote the gold diff.

## Who publishes it

Yuling Shi, Jinghan Xu, Kelin Fu, Wenhao Zeng, Shilin He, Xiaodong Gu, Shing-Chi
Cheung, and co-authors submitted the paper on 2026-08-10. The dataset card says
it was accepted to COLM 2026. Contact listed on the card is yuling.shi@sjtu.edu.cn.
No separate GitHub organisation URL resolved during this research.

## Lineage

ProMax is a SWE-bench-family stress test aimed at Verified saturation and at
thin refactoring sets such as RefactorBench. It is not [SWE-bench Pro](swe_bench_pro.md)
from Scale AI, despite the similar name. SWE-bench Pro targets long-horizon
issue resolution with copyleft and private code. ProMax targets multilingual
refactoring of post-2025 public commits. A promised v2 from post-2026 issues
is not released.

## Saturation and contamination

41.2% resolved is well below Verified's 75%+ regime, and language scores vary
widely, so the set is open. Contamination risk is medium by construction:
commits are after January 2025 and prompts are rewritten, but the code is still
public GitHub.

## How to run it

Use the dataset's Docker runner with a predictions file of `instance_id` and
`model_patch` pairs. Record scaffold, model, and cost. Do not mix OpenHands
numbers with mini-swe-agent numbers. No lm-eval task name was found.

## Reading the numbers

A 40% ProMax score means the agent can finish some multi-file refactors, not
that it matches Verified bug-fix skill. Failed runs in the paper often edit
fewer files than the gold patch and burn extra steps. Compare per-language
rates before treating an overall figure as multilingual competence. TypeScript
is concentrated: the paper says 28 TypeScript instances come from two
repositories, with Angular contributing 25.
