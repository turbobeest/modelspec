---
id: taco
name: "TACO (Topics in Algorithmic COde generation)"
aliases:
  - "Topics in Algorithmic COde generation"
  - "BAAI/TACO"
  - "FlagOpen/TACO"
page_kind: benchmark
category: coding
subcategory: "competition-style Python generation graded by test-case execution"
status: active
summary: "BAAI TACO: 1,000 competition-style Python problems (plus a 25k-problem train split) scored by executing generated code as pass@k."
measures: >
  TACO gives a model a natural-language programming-contest statement, optional
  starter code, and a call-based or stdin convention, and requires a Python
  program that passes the problem's hidden tests. Items come from contest sites
  rather than interview-style function stubs. Each row also carries topic,
  algorithm, skill, and difficulty labels so reporters can slice the 1,000-item
  test set. English problem text, Python solutions. This is not
  [mc_taco](mc_taco.md) (temporal commonsense) and not [tac](tac.md) (travel
  agents).
task_format: >
  Free-form Python generation. OpenCompass TACODataset loads Hugging Face
  BAAI/TACO, evaluates the test split, and prepends starter plus
  "Use Standard Input format" or "Use Call-Based format". The default
  taco_gen_c7893a config is zero-shot, max_out_len 512, num_repeats 1.
  taco_levels_gen_411572 runs one config per difficulty with max_out_len 1024.
metric:
  name: "pass@k (OpenCompass TACOEvaluator; FlagOpen compute_metric.py)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    A generation counts if every test case returns true under a 10-second
    process timeout. OpenCompass reports pass@1/10/100 when enough samples
    exist; the default OpenCompass config uses num_repeats 1, so only pass@1
    is defined. Paper Table 5 (temperature 0.7): GPT-4 pass@1 31.50 easy,
    19.00 medium, 13.00 medium_hard, 4.50 hard, 2.00 very_hard. OpenCompass
    README pass@1 on the pooled test set: CodeLlama-7b-Python 0.7,
    internlm2-chat-20b-sft-hf 2.7. No human contestant baseline is in the
    sources opened here.
dataset:
  size: 26443
  size_note: >
    Hugging Face BAAI/TACO ALL config: 25,443 train and 1,000 test
    (card lastModified 2024-06-19). The paper abstract (arXiv 2312.14852)
    says 25,433 train and 1,000 test plus up to 1.55 million reference
    solutions. The ten-problem train gap is unresolved; evaluation uses the
    1,000-row test split. FlagOpen reports about 202.3 tests per problem
    and zero test problems without answers. Difficulties: EASY, MEDIUM,
    MEDIUM_HARD, HARD, VERY_HARD. Skills include data structures, sorting,
    range queries, complete search, amortized analysis, dynamic programming,
    bit manipulation, and greedy algorithms.
  url: "https://huggingface.co/datasets/BAAI/TACO"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "train 25,443 / test 1,000 (Hub ALL config); OpenCompass scores test"
  public_test_set: true
publisher:
  org: "Beijing Academy of Artificial Intelligence (BAAI) / FlagOpen"
  authors:
    - "Rongao Li"
    - "Jie Fu"
    - "Bo-Wen Zhang"
    - "Tao Huang"
    - "Zhihong Sun"
    - "Chen Lyu"
    - "Guang Liu"
    - "Zhi Jin"
    - "Ge Li"
  url: "https://github.com/FlagOpen/TACO"
paper:
  title: "TACO: Topics in Algorithmic COde generation dataset"
  arxiv: "2312.14852"
  url: "https://arxiv.org/abs/2312.14852"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/FlagOpen/TACO"
released: "2023-12"
last_updated: "2024-06"
lineage:
  family: ""
  predecessor: apps
  successors: []
  variants: []
saturation:
  status: open
  top_score: 31.5
  as_of: "2023-12"
  note: >
    Paper Table 5 GPT-4 easy pass@1 is 31.5, falling to 2.0 on very_hard.
    That is one model on one slice, not a pooled SOTA. OpenCompass's
    listed 2023-era chat models sit at 0.7–2.7 pass@1 on the full test
    set. No later public leaderboard cell was opened here.
contamination:
  risk: high
  note: >
    Problems, tests, and many solutions have been public on Hugging Face
    and GitHub since December 2023, and the source contest sites are
    widely crawled. FlagOpen updated tests on 2024-06-19 after APPS-style
    judge bugs. A 2025-12-03 file lists special-judge test problems.
    No post-hoc TACO memorisation study was opened here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "TACO"
  bigbench: ""
  other: "OpenCompass also ships TACO-EASY, TACO-MEDIUM, TACO-MEDIUM_HARD, TACO-HARD, TACO-VERY_HARD via taco_levels_gen_411572.py. Official eval is FlagOpen/TACO compute_metric.py."
tags:
  - coding
  - competitive-programming
  - python
  - pass-at-k
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2312.14852"
    title: "TACO paper abstract (submitted 22 Dec 2023, v3 27 Dec 2023)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2312.14852"
    title: "TACO paper HTML (25,433 train claim, Table 5 GPT-4 pass@1)"
    accessed: "2026-09-08"
  - url: "https://github.com/FlagOpen/TACO"
    title: "FlagOpen/TACO repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FlagOpen/TACO/main/README.md"
    title: "FlagOpen TACO README (25,443/1,000, 202.3 tests/problem, 2024-06-19 tests)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FlagOpen/TACO/main/LICENSE"
    title: "FlagOpen/TACO Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/BAAI/TACO"
    title: "Hub API BAAI/TACO (apache-2.0, 25443/1000, lastModified 2024-06-19)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/BAAI/TACO/raw/main/README.md"
    title: "Hub card BAAI/TACO (English questions, Python solutions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/taco/README.md"
    title: "OpenCompass taco README (pass@1 table, BAAI/TACO path)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/taco/taco_gen_c7893a.py"
    title: "OpenCompass taco_gen_c7893a.py (abbr TACO, max_out_len 512, num_repeats 1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/taco/taco_levels_gen_411572.py"
    title: "OpenCompass taco_levels_gen_411572.py (TACO-EASY through TACO-VERY_HARD)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/taco.py"
    title: "OpenCompass TACODataset/TACOEvaluator (BAAI/TACO test split, pass@k)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-073 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

TACO (Topics in Algorithmic COde generation) asks a model to write a Python program from a contest-style English statement. Unlike [humaneval](humaneval.md), the prompt is a full problem, not a docstring over a stub. Unlike [apps](apps.md), every test item ships with reference solutions and finer labels (topic, algorithm, skill, difficulty). The model must satisfy hidden tests, using either a function call or stdin/stdout, as the starter line indicates. Language is English for the statement and Python for the code.

## How it is scored

Scoring is execution. FlagOpen and OpenCompass run generated code on the problem's input/output lists and count a problem solved only if every case passes. The metric is pass@k: the chance that at least one of k samples is fully correct. OpenCompass `TACOEvaluator` uses a 10-second global timeout per generation and reports pass@1, pass@10, and pass@100 when `num_repeats` is large enough. The default `TACO` config sets `num_repeats` to 1 and `max_out_len` to 512, so those runs are single-sample pass@1 with a short decode cap. The paper's GPT-4 numbers use temperature 0.7 and are broken out by difficulty, not pooled. OpenCompass's README table is pooled pass@1 on small 2023 chat models (0.7–2.7) and is not GPT-4.

## Dataset and licence

The live Hub config `BAAI/TACO` ALL has 25,443 train rows and 1,000 test rows (card dated 19 June 2024). The paper abstract says 25,433 train; that ten-row gap is not explained in the files opened here. Evaluation is the 1,000-row test split. FlagOpen's comparison table claims about 202.3 tests per problem and no empty-answer test items, versus [apps](apps.md)'s thinner tests. Difficulties are EASY through VERY_HARD; skill tags include sorting, dynamic programming, and greedy algorithms. The Hub card, FlagOpen LICENSE, and GitHub copy are Apache-2.0. Tests and solutions are public.

## Who publishes it

Rongao Li, Jie Fu, Bo-Wen Zhang (corresponding), Tao Huang, Zhihong Sun, Chen Lyu, Guang Liu, Zhi Jin, and Ge Li, at BAAI, Shandong Normal University, and Peking University. The paper is arXiv 2312.14852, submitted 22 December 2023 (v3 27 December 2023). Code and data: `FlagOpen/TACO` and `BAAI/TACO`. OpenCompass wraps the Hub test split. No maintained official leaderboard URL was confirmed; Papers with Code is linked from the Hub card but was not used as a citation here.

## Lineage

TACO is built as a harder, larger follow-on to function-completion sets such as [humaneval](humaneval.md) and to contest sets such as [apps](apps.md), which the README treats as a quoted source of judge code. CodeContests is compared in the same table but has no page here yet. [live_code_bench](live_code_bench.md) is a later live contest eval, not a TACO fork. This id is not [mc_taco](mc_taco.md) and not [tac](tac.md).

## Saturation and contamination

Paper GPT-4 is 31.5 pass@1 on easy and 2.0 on very_hard, so a pooled number can hide a collapse on hard items. OpenCompass's listed models are near 1–3 pass@1. No 2026 SOTA cell was opened. Contamination risk is high: contest pages, Hub dumps, and 1.55 million solutions have been public since 2023. FlagOpen patched tests on 19 June 2024 and later listed special-judge cases; quote that revision if you compare to older numbers.

## How to run it

Official: generate with `FlagOpen/TACO` `generation.py`, then `compute_metric.py`. OpenCompass: dataset abbr `TACO` (`taco_gen_c7893a.py`) or `TACO-EASY` … `TACO-VERY_HARD`. Both load `BAAI/TACO` test. Do not compare a 512-token `num_repeats=1` OpenCompass run with a 200-sample FlagOpen pass@100. lm-evaluation-harness, inspect_evals, HELM, and BIG-bench were not confirmed to ship this dataset under this id.

## Reading the numbers

A high TACO pass@1 means generated Python often passes contest tests on that split and difficulty. It does not mean the model writes readable or efficient code, and it does not transfer to hidden live contests. Always name k, temperature, decode length, and whether the slice is pooled or EASY-only. GPT-4's 31.5 is easy-only; very_hard in the same table is 2.0. Prefer the 2024-06 Hub tests over the 2023 dump.
