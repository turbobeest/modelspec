---
id: codecompass
name: "CodeCompass"
aliases:
  - "CodeComPass"
  - "codecompass_gen_cpp"
page_kind: benchmark
category: coding
subcategory: "OpenCompass C++ pass@1 on 270 SAGA-tested contest problems"
status: active
summary: "OpenCompass C++ pass@1 on CodeCompass: 270 recent AtCoder, Codeforces and Nowcoder problems with SAGA-generated tests."
measures: >
  CodeCompass is a code-generation benchmark from Shanghai AI Laboratory's
  OpenCompass line. The model reads an English online-judge statement and must
  emit a self-contained C++ program that reads stdin and writes stdout.
  OpenCompass extracts a ```cpp fence, compiles it, and runs the problem's
  test cases. The problems are 270 AtCoder, Codeforces, and Nowcoder tasks
  from June 2024 onward, with SAGA-generated tests (paper: 50.54 cases per
  problem on average). The same paper also reports Python pass@1; the shipped
  OpenCompass config only builds a C++ dataset (abbr codecompass_gen_cpp).
  It is not CompassBench and not Ericsson's CodeCompass static-analysis tool.
task_format: >
  Zero-shot generation. OpenCompass PromptTemplate round is the processed
  {prompt}: an expert-C++ system block plus [[Problem begin]]...[[Problem end]].
  GenInferencer max_out_len 2048. Evaluator CodeCompassEvaluator, k_list=[1],
  timeout 15s (or the problem's Time Limit), 16 worker processes.
metric:
  name: pass@1
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass metrics.py uses the unbiased pass@k estimator; the hashed
    config sets k_list=[1] only. Paper Table 6 (Pass@1) lists Qwen3-235B-A22B
    at 43.70% C++ and 36.30% Python, DeepSeek-Chat-R1 38.15% / 34.07%,
    GPT-4o (2024-11-20) 20.74% / 14.44%. Those paper rows include Python;
    OpenCompass's checked-in config is C++ only. No random baseline.
dataset:
  size: 270
  size_note: >
    Paper Table 4 / Appendix E: 270 problems, Easy 27.04%, Medium 32.59%,
    Hard 40.37%, average 50.54 SAGA tests per problem, sources AtCoder,
    Codeforces, Nowcoder, contests from June 2024. Hugging Face
    opencompass/CodeCompass v0 (also mirrored as MichaelErchi/CodeCompass in
    the loader homepage) stores problems.parquet plus a large cases.parquet.
    Downloaded problems.parquet (209,193 bytes) but did not independently
    row-count it (no pyarrow). Nowcoder text in that file includes Chinese.
  url: "https://huggingface.co/datasets/opencompass/CodeCompass"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
    - code
  splits: "Hub config v0 test split only; OpenCompass reader train_split='test'"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory (OpenCompass); Xi'an Jiaotong University"
  authors:
    - "Zihan Ma"
    - "Taolin Zhang"
    - "Maosong Cao"
    - "Junnan Liu"
    - "Wenwei Zhang"
    - "Minnan Luo"
    - "Songyang Zhang"
    - "Kai Chen"
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/codecompass"
paper:
  title: "Rethinking Verification for LLM Code Generation: From Generation to Testing"
  arxiv: "2507.06920"
  url: "https://arxiv.org/abs/2507.06920"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/datasets/codecompass"
released: "2025-07"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 43.7
  as_of: "2025-07"
  note: >
    Paper Table 6 best C++ Pass@1 among listed models is Qwen3-235B-A22B at
    43.70%. GPT-4o is 20.74% C++. No later public OpenCompass leaderboard
    table for abbr codecompass_gen_cpp was read.
contamination:
  risk: medium
  note: >
    Problems are linked to public contest pages from June 2024 onward, chosen
    to reduce leakage versus older HumanEval-style sets. Tests are
    SAGA-generated and public on the Hub. Contest statements themselves may
    still appear in crawls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "codecompass_gen_cpp"
  bigbench: ""
  other: "Hashed config opencompass/configs/datasets/codecompass/codecompass_gen_079a6c.py; dataset path opencompass/CodeCompass; evaluator CodeCompassEvaluator."
tags:
  - coding
  - competitive-programming
  - pass-at-k
  - cpp
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2507.06920"
    title: "Rethinking Verification for LLM Code Generation (arXiv:2507.06920v2)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2507.06920"
    title: "Paper HTML (270 problems, Table 6 Pass@1, SAGA tests)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/CodeCompass/raw/main/README.md"
    title: "Hugging Face opencompass/CodeCompass card (Apache-2.0, v0 fields)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/CodeCompass"
    title: "Hub API (created 2025-06-03, lastModified 2025-08-01, apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/codecompass/codecompass_gen_079a6c.py"
    title: "OpenCompass hashed C++ generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/codecompass/CodeCompass.py"
    title: "CodeCompassCodeGenerationDataset (C++ system prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/codecompass/evaluator.py"
    title: "CodeCompassEvaluator (pass@1, 16 workers, timeout 15)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/codecompass/metrics.py"
    title: "pass@k estimator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-032 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-032"
---

## What it measures

CodeCompass asks a model to solve a recent contest problem in C++. The OpenCompass prompt calls the model an expert C++ programmer, pastes the statement between `[[Problem begin]]` markers, and requires a self-contained program that uses standard input and output. Scoring runs the extracted code against the problem's test list.

The 270 statements come from AtCoder, Codeforces, and Nowcoder contests held from June 2024. Tests are SAGA-generated (paper: 50.54 per problem). The paper also prints Python Pass@1. The only hashed OpenCompass config is C++ (`codecompass_gen_cpp`). This is not [compassbench_v1_3](compassbench_v1_3.md) and not Ericsson's CodeCompass code-comprehension product.

## How it is scored

`CodeCompassEvaluator` extracts a ```cpp block, looks up tests by `question_id`, and executes with a process pool (default 16 workers, 15 s, or the statement's time limit). `metrics.py` estimates pass@k; the config requests k=1 only. A problem counts as correct when at least one generation passes every test in that sample. Empty extraction skips the item in the evaluator loop, so a silent no-code reply can disappear from the denominator.

Paper Table 6 is Pass@1 for C++ and Python with SAGA tests. Qwen3-235B-A22B is 43.70% C++ and 36.30% Python. GPT-4o (2024-11-20) is 20.74% / 14.44%. Those rows are not an OpenCompass log dump.

## Dataset and licence

Table 4: 270 problems, Easy 27.04%, Medium 32.59%, Hard 40.37%. Hub dataset `opencompass/CodeCompass` config `v0` has `problems.parquet` and `cases.parquet`; the card licence is Apache-2.0 and lists language English. The custom loader homepage also names `MichaelErchi/CodeCompass`. Cases are JSON strings of `{case_id, input, output}`. OpenCompass sets `train_split='test'`. Nowcoder statements in the downloaded `problems.parquet` include Chinese titles; this page did not independently row-count the parquet (no pyarrow).

## Who publishes it

Zihan Ma, Taolin Zhang, Maosong Cao, Junnan Liu, Wenwei Zhang, Songyang Zhang, and Kai Chen (Shanghai AI Laboratory) with Minnan Luo (Xi'an Jiaotong University) posted arXiv 2507.06920 on 9 July 2025 (v2 10 July 2025). The paper's main artifact is SAGA/TCGBench; CodeCompass is the SAGA-enhanced generation set. OpenCompass code is Apache-2.0. Hub createdAt is 3 June 2025; lastModified 1 August 2025. No separate leaderboard URL was found.

## Lineage

The paper positions CodeCompass against thin-test suites such as [humaneval](humaneval.md) and [live_code_bench](live_code_bench.md), and compares verifiers to LiveCodeBench-v6 on 101 shared AtCoder problems. CompassBench pages in this repository are composite OpenCompass exams, not this dataset. Ericsson CodeCompass is unrelated static analysis.

## Saturation and contamination

Table 6's best listed C++ Pass@1 is 43.70%, so the set still separates models. Statements are public contest pages from 2024–2025. SAGA tests are on the Hub, so a trainer can overfit the verifier. The June 2024 cutoff is the authors' leakage control, not a hidden split.

## How to run it

OpenCompass dataset abbr `codecompass_gen_cpp` from `codecompass_gen_079a6c.py`. Load `opencompass/CodeCompass` with `trust_remote_code=True`. Execution needs a local C++ toolchain. A Python Pass@1 from the paper is not this config. lm-eval, HELM, and inspect_evals names were not found.

## Reading the numbers

A 40% OpenCompass pass@1 means about two in five C++ programs passed every attached SAGA test, not that the model matches an official contest ranking. Python Table 6 rows are a different language. Skip-on-empty-extract can inflate a score if many replies have no fence. Read beside LiveCodeBench only when the problem overlap and test suites match; they do not, except for the paper's 101-problem verifier study.
