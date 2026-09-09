---
id: se_bench
name: SE-Bench
aliases:
  - "SE-Bench: Benchmarking Self-Evolution with Knowledge Internalization"
page_kind: benchmark
category: coding
subcategory: "knowledge internalization / self-evolution diagnostic"
status: active
summary: >
  A diagnostic coding test that renames NumPy into a fake library so a score reflects
  whether an agent internalized new APIs, not old knowledge or hard reasoning.
measures: >
  SE-Bench checks whether an agent can absorb a new library and later use it with no
  docs. The authors wrap 268 common NumPy functions as a package named zwc, with
  nonsense identifiers such as zwc.kocito. Inputs and outputs are ZWCArray objects so
  the model cannot call NumPy methods on arrays. Training items include the relevant
  docstring. Test items are ordinary coding problems without that docstring. Single-function
  tests check recall. Multi-function tests require composing at least three APIs. A
  base model scores 0% without docs, so failures are meant to be memory failures.
task_format: >
  English problem statement in; the model writes Python that must call zwc APIs, pass
  hidden tests, and must not import numpy. Training may include API docs; the official
  test run does not.
metric:
  name: "accuracy (test-case + AST constraints)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    A solution counts only if every test case passes, AST checks show the return value
    depends on zwc, and numpy is never imported. Qwen3-8B pass@64 is 0.0% zero-shot on
    zwc, 97.4%/93.6% on the same tasks in NumPy, and 85.3%/70.5% with zwc docs in context
    (paper Table 1). No human baseline was reported.
dataset:
  size: 1417
  size_note: >
    1,417 tasks after consensus filtering: 718 single-function training items, 259
    single-function test items, and 440 multi-function test items. Hugging Face configs
    train / single_test / multiple_test have 718, 259, and 440 rows. The library covers
    268 NumPy functions. Training covers every function at least once.
  url: "https://huggingface.co/datasets/jintailin/SE-Bench"
  license: MIT
  languages:
    - en
  modalities:
    - text
    - code
  splits: "train 718 (single-function); test 699 (259 single-function + 440 multi-function)"
  public_test_set: true
publisher:
  org: THUNLP, Tsinghua University
  authors:
    - Jiarui Yuan
    - Tailin Jin
    - Weize Chen
    - Zeyuan Liu
  url: "https://github.com/thunlp/SE-Bench"
paper:
  title: "SE-Bench: Benchmarking Self-Evolution with Knowledge Internalization"
  arxiv: "2602.04811"
  url: "https://arxiv.org/abs/2602.04811"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/thunlp/SE-Bench"
released: "2026-02"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 54.4
  as_of: "2026-05"
  note: >
    Table 2 (v2, 2026-05) reports mean accuracy over five rollouts. The best
    parameter-update result is Closed-SFT-RL on Qwen3-8B: 54.4% single-function and
    17.9% multi-function. Expel memory search reached 47.1% and 15.5% on the same
    splits. In-context docs still leave a gap to the NumPy upper bound. The ceiling
    is not reached.
contamination:
  risk: low
  note: >
    Function names are random and the package is synthetic, so pretraining should not
    contain the mapping. Tasks and test cases are public on Hugging Face. The diagnostic
    still holds only if models are not trained on this release before the reported run.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference code is thunlp/SE-Bench. Roll out with query_only.py (no docs) or
    query_doc.py, then score in a Docker sandbox via filter_correct_trajectory.py.
    No lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task was found.
tags:
  - coding
  - self-evolution
  - knowledge-internalization
  - synthetic
  - python
sources:
  - url: "https://arxiv.org/abs/2602.04811"
    title: "SE-Bench arXiv abstract (v2, 9 May 2026)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2602.04811v2"
    title: "SE-Bench HTML full text, arXiv 2602.04811v2"
    accessed: "2026-09-08"
  - url: "https://github.com/thunlp/SE-Bench"
    title: "thunlp/SE-Bench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/thunlp/SE-Bench/main/README.md"
    title: "SE-Bench README (protocol, Hugging Face configs, citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/thunlp/SE-Bench/main/LICENCE.md"
    title: "SE-Bench MIT licence (LICENCE.md)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jintailin/SE-Bench"
    title: "jintailin/SE-Bench dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jintailin/SE-Bench"
    title: "Hugging Face Hub API (license:mit, lastModified 2026-05-07)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=jintailin/SE-Bench"
    title: "Hugging Face datasets-server row counts (718 / 259 / 440)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-080 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SE-Bench asks whether an agent can learn a new Python API and later use it with no documentation. The library is a NumPy wrapper named zwc. Each function has a nonsense name. Arrays are wrapped so `.mean()`-style shortcuts fail. Training problems include the matching docstring. Official tests hide that docstring.

Tasks are easy if the mapping is known. The same items are solved at high pass@64 with plain NumPy. They score 0% on zwc with no docs. Multi-function tests need at least three APIs, so the score is not only one-function memorization.

## How it is scored

A run is correct only if tests pass, AST analysis ties the return value to zwc, and numpy is not imported. The headline number is accuracy on that binary rule. Table 1 uses pass@64 to check the design. Table 2 uses the mean of five rollouts.

On Qwen3-8B, Closed-SFT-RL reached 54.4% single-function and 17.9% multi-function. Closed-SFT alone reached 39.6% and 11.6%. Open-SFT, Open-RL, Closed-RL, and Absolute-Zero scored 0.0% on both splits. Expel memory search reached 47.1% and 15.5%, the best memory baseline. With docs in context and no training, Qwen3-8B pass@64 was 85.3% / 70.5%, below the NumPy upper bound of 97.4% / 93.6% because models still hallucinate NumPy names.

## Dataset and licence

After filtering, there are 1,417 tasks: 718 train, 259 single-function test, 440 multi-function test. Hugging Face row counts match. Claude-4.5-sonnet wrote NumPy-form problems. Gemini-2.5-Pro rewrote docs into zwc. A task is kept only if Qwen3-Coder-480B, Gemini-2.5-Pro, and GPT-OSS-120B all solve the NumPy form. Humans checked a 10% sample; all sampled items were valid. The GitHub file `LICENCE.md` and the Hub tag are MIT. Test JSONL includes test cases, so the eval set is public.

## Who publishes it

Jiarui Yuan, Tailin Jin, Weize Chen, and Zeyuan Liu (Tsinghua / THUNLP) posted v1 on 4 February 2026 and v2 on 9 May 2026. The repo citation also lists Zhiyuan Liu and Maosong Sun. Code is thunlp/SE-Bench. Data is jintailin/SE-Bench. No public leaderboard was found.

## Lineage

This is not a general coding contest. [HumanEval](humaneval.md) and [SWE-bench](swe_bench.md) measure writing or patching known languages. SE-Bench hides the language of the library on purpose. It is also not Princeton SAgE. Use it as a diagnostic for self-evolution methods, not as a drop-in coding score.

## Saturation and contamination

The best trained Qwen3-8B result is still 54.4% / 17.9%. Multi-function accuracy is low. The design zero-shot floor is 0%. Names are random, so classic web-scrape contamination of NumPy docs should not help unless the model saw this release. Once the JSONL is in training data, the diagnostic is spent.

## How to run it

Install thunlp/SE-Bench, load `jintailin/SE-Bench`, and follow the README: train only on `datasets/train/`, then evaluate `single_test` and `multiple_test` without docs. Serve the model, roll out with `query_only.py`, start the Docker sandbox, and run `filter_correct_trajectory.py`. Custom rollouts need `query`, `response`, `test_cases`, and `right_exe_result`. Open versus closed training is a real protocol split: docs may be present when collecting traces but must be stripped for Closed-SFT. No standard harness task was found.

## Reading the numbers

A high closed-book score means the mapping is in the weights, not that the model is a better programmer. Open-SFT at 0% with the same traces is the paper's Open-Book Paradox, not a broken eval. Memory methods can look strong by storing the NumPy map. Do not mix pass@64 Table 1 figures with Table 2 five-run means. Report single-function and multi-function accuracy separately, and say whether docs were visible at train and at test.
