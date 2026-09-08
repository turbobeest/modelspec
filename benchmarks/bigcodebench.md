---
id: bigcodebench
name: BigCodeBench
aliases: []
page_kind: benchmark
category: coding
subcategory: function-calling / library-use code generation
status: active
summary: >-
  1,140 Python tasks that require chaining calls across 139 real libraries, testing whether a model can
  use diverse tools correctly rather than write self-contained algorithmic code.
measures: >
  BigCodeBench asks a model to write a Python function that correctly uses one or more calls into real,
  popular libraries (data processing, visualization, networking, cryptography and more) to satisfy either
  a structured docstring (the Complete split) or a condensed natural-language instruction (the Instruct
  split). This targets a different skill than algorithmic benchmarks like HumanEval or MBPP: knowing
  which library function to call, with which arguments, and how to combine several such calls correctly,
  rather than implementing logic from scratch in the standard library alone.
task_format: >
  Given a function signature with a docstring (Complete) or a natural-language instruction (Instruct), the
  model generates a Python function body; the generated code is executed against an average of 5.6 unit
  test cases per task with about 99% branch coverage.
metric:
  name: "Pass@1 (including a \"calibrated\" variant that accounts for omitted setup code)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: 97
  baseline_note: >
    97% is the paper's reported pass rate for the reference/human solutions. The best model at the
    paper's June 2024 release reached up to 60% pass@1 on the Complete split and under 50% on the harder,
    more natural-language Instruct split.
dataset:
  size: 1140
  size_note: >
    1,140 tasks, each usable in two prompt styles (Complete: structured docstring; Instruct: condensed
    natural-language instruction) rather than 1,140 separate items per style. Tasks call an average of 4.7
    function-call combinations across an average of 2.8 library combinations, drawn from 723 distinct
    function calls across 139 popular Python libraries. A curated, more natural-language-aligned Hard
    subset holds approximately 150 of the 1,140 tasks. The Hugging Face dataset has been revised across at
    least five versions (v0.1.0_hf through v0.1.4) for bug fixes, each holding the same 1,140 rows.
  url: https://huggingface.co/datasets/bigcode/bigcodebench
  license: Apache-2.0
  languages:
    - Python
  modalities:
    - code
    - text
  splits: >-
    1,140 tasks; Complete and Instruct are two prompt formats over the same tasks, not separate item
    sets; a curated ~150-task Hard subset also exists
  public_test_set: true
publisher:
  org: "BigCode project (multi-institution community collaboration)"
  authors:
    - Terry Yue Zhuo
    - Minh Chien Vu
    - Jenny Chim
    - Han Hu
    - Wenhao Yu
    - Ratnadira Widyasari
    - Imam Nur Bani Yusuf
    - Haolan Zhan
    - Junda He
    - Indraneil Paul
    - Simon Brunner
    - Chen Gong
    - Thong Hoang
    - Armel Randy Zebaze
    - Xiaoheng Hong
    - Wen-Ding Li
    - Jean Kaddour
    - Ming Xu
    - Zhihan Zhang
    - Prateek Yadav
    - Naman Jain
    - Alex Gu
    - Zhoujun Cheng
    - Jiawei Liu
    - Qian Liu
    - Zijian Wang
    - Binyuan Hui
    - Niklas Muennighoff
    - David Lo
    - Daniel Fried
    - Xiaoning Du
    - Harm de Vries
    - Leandro Von Werra
  url: https://github.com/bigcode-project/bigcodebench
paper:
  title: "BigCodeBench: Benchmarking Code Generation with Diverse Function Calls and Complex Instructions"
  arxiv: "2406.15877"
  url: https://arxiv.org/abs/2406.15877
  year: 2024
leaderboard_url: https://huggingface.co/spaces/bigcode/bigcodebench-leaderboard
repo_url: https://github.com/bigcode-project/bigcodebench
released: "2024-06"
last_updated: "2025-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.0
  as_of: "2024-06"
  note: >
    The paper's own headline number: the best model reached up to 60% pass@1 on the Complete split at
    the June 2024 release, well below the 97% human/reference rate, and under 50% on the harder Instruct
    split. The project's Hugging Face Space leaderboard reported 163 models evaluated as of a 2025-01-22
    release note, but that Space did not render through this research's tooling, so a current top score
    was not confirmed here; treat the 60% figure as the original-paper number, not a live one.
contamination:
  risk: medium
  note: >
    Task prompts and canonical solutions were written and reviewed by the author team rather than mined
    verbatim from an existing public corpus, which limits (but does not eliminate) direct memorisation
    risk. The dataset has been public since June 2024, is downloaded in large volume (over a million
    Hugging Face downloads), and is a common target for code-model fine-tuning and evaluation, so
    exposure during later pretraining or instruction-tuning is plausible.
harness:
  lm_eval: ""
  inspect_evals: bigcodebench
  helm: bigcodebench
  opencompass: bigcodebench
  bigbench: ""
  other: >
    The reference `bigcodebench` CLI (pip install bigcodebench) takes --split [complete|instruct] and
    --subset [full|hard] flags and executes candidate code in a sandbox (e2b, gradio, or local). HELM's
    BigCodeBenchScenario loads bigcode/bigcodebench at a specific dataset revision and takes a version
    parameter (v0.1.0_hf, v0.1.1, v0.1.2, v0.1.3). inspect_evals/bigcodebench always uses the Complete
    prompt, noting that the Complete prompt contains examples not seen in the Instruct prompt, and runs
    generated code in a Docker sandbox. OpenCompass ships a large family of full/hard x complete/instruct
    config combinations under its bigcodebench dataset folder. EvalPlus's own public leaderboard
    (evalplus.github.io) does not carry BigCodeBench scores directly — it only links to BigCodeBench's own
    site as a separate resource — despite BigCodeBench crediting EvalPlus's test-augmentation methodology
    in its evaluation framework.
tags:
  - coding
  - function-calling
  - library-use
  - python
  - pass-at-1
  - sandboxed-execution
sources:
  - url: https://arxiv.org/abs/2406.15877
    title: "BigCodeBench: Benchmarking Code Generation with Diverse Function Calls and Complex Instructions"
    accessed: "2026-09-08"
  - url: https://github.com/bigcode-project/bigcodebench
    title: "bigcode-project/bigcodebench repository (README, CLI usage, citation)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/bigcode/bigcodebench
    title: "bigcode/bigcodebench dataset card and structure (1,140 tasks, apache-2.0, v0.1.0-v0.1.4)"
    accessed: "2026-09-08"
  - url: https://bigcode-bench.github.io/
    title: "BigCodeBench project site (Hard subset, leaderboard link)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/bigcodebench_scenario.py
    title: "HELM bigcodebench_scenario.py (BigCodeBenchScenario)"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/bigcodebench
    title: "inspect_evals bigcodebench task (always uses Complete prompt)"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/bigcodebench
    title: "OpenCompass bigcodebench dataset configs (full/hard x complete/instruct)"
    accessed: "2026-09-08"
  - url: https://evalplus.github.io/leaderboard.html
    title: "EvalPlus leaderboard (HumanEval+/MBPP+ only; links out to BigCodeBench rather than hosting it)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BigCodeBench asks a model to write a Python function that correctly uses one or more calls into real,
popular libraries — data processing, visualization, networking, cryptography and more — to satisfy either
a structured docstring (the Complete split) or a condensed natural-language instruction (the Instruct
split). This targets a different skill than algorithmic benchmarks like HumanEval (`humaneval`) or MBPP
(`mbpp`): knowing which library function to call, with which arguments, and how to combine several such
calls correctly, rather than implementing logic from scratch against the standard library alone.

Tasks are deliberately compositional: on average a task calls 4.7 function-call combinations drawn from
2.8 different libraries, pulled from a pool of 723 distinct function calls across 139 popular Python
libraries, so success requires broad, correct tool knowledge rather than one narrow API.

## How it is scored

Generated code is executed against held-out unit tests — an average of 5.6 test cases per task, reaching
about 99% branch coverage — and scored as Pass@1 under greedy decoding. The paper also reports a
"calibrated" Pass@1 that accounts for setup code a model's response may have omitted when it was implied
by the prompt rather than restated, to avoid penalising reasonable omissions. Reference human solutions
pass at 97%; the best model at the paper's original release reached up to 60% on Complete and under 50% on
the harder Instruct split, which strips away the docstring's structure in favour of a shorter natural-
language instruction the model must interpret itself.

## Dataset and licence

The dataset holds 1,140 tasks, each available in both the Complete and Instruct prompt styles rather than
as separate item pools, plus a curated Hard subset of roughly 150 tasks selected for closer alignment with
real-world, Stack-Overflow-style queries. It is released under an Apache-2.0 licence on Hugging Face
(bigcode/bigcodebench) and has been revised across at least five dataset versions (v0.1.0_hf through
v0.1.4) for bug fixes, each holding the same 1,140-row count. Tasks are Python; docstrings and instructions
are in English.

## Who publishes it

BigCodeBench comes from a 33-author collaboration under the BigCode project, led by Terry Yue Zhuo with
co-authors including Minh Chien Vu, Jenny Chim, Niklas Muennighoff, Binyuan Hui, Daniel Fried, Harm de
Vries and Leandro von Werra, spanning institutions including Monash University, CSIRO's Data61, TU
Darmstadt, Singapore Management University and Inria. The paper was posted to arXiv in June 2024 and
accepted as an Oral paper at ICLR 2025. The project maintains its site at bigcode-bench.github.io and a
Hugging Face Space leaderboard, reporting 163 models evaluated as of a January 2025 release note.

## Lineage

BigCodeBench extends the single-function, algorithm-focused style of HumanEval and MBPP to tasks that
require chaining calls across many real libraries; it explicitly credits EvalPlus's test-case augmentation
methodology in its own evaluation framework, though EvalPlus's own leaderboard does not carry BigCodeBench
results. It has no formally named predecessor or successor benchmark id, and no variant subset (including
its own Hard tier) has a separate page in this repository yet.

## Saturation and contamination

The paper's own headline result — up to 60% pass@1 on Complete and under 50% on Instruct, against a 97%
human/reference rate — leaves clear room below the ceiling, so this page reads BigCodeBench as open. The
project's Hugging Face Space leaderboard reports having evaluated 163 models by January 2025, but the
Space did not render through this research's tooling, so a current top score was not independently
confirmed; treat the 60%/97% figures as the original paper's numbers rather than a live leaderboard
snapshot. Contamination risk sits at medium: tasks and canonical solutions were authored and reviewed by
the paper's team rather than mined verbatim from an existing corpus, which limits direct memorisation, but
the dataset is heavily downloaded and a common fine-tuning and evaluation target, so exposure during later
training is plausible.

## How to run it

The reference `bigcodebench` command-line tool takes `--split [complete|instruct]` and `--subset
[full|hard]` flags and executes candidate code in a sandbox (`e2b`, `gradio`, or `local`). HELM's
`BigCodeBenchScenario` loads a specific dataset version (v0.1.0_hf through v0.1.3) rather than always the
latest. inspect_evals' `bigcodebench` task always uses the Complete prompt — noting that Complete contains
examples not present in Instruct — and runs generated code in a Docker sandbox. OpenCompass ships the
widest config surface, with separate full/hard and complete/instruct combinations. Because split, subset,
sandbox backend and dataset version can all differ between these implementations, confirm all four before
treating two BigCodeBench numbers as comparable.

## Reading the numbers

A high BigCodeBench score shows a model can correctly select and chain real library calls to solve a
task, not just write self-contained algorithmic code — a skill closer to everyday software engineering
than HumanEval or MBPP test. Because the gap between the Complete and Instruct splits is large, always
check which split a score used: an Instruct number reflects the added difficulty of interpreting a
condensed natural-language request, while a Complete number does not. With reference solutions at 97% and
the best reported models still well below that at the original release, BigCodeBench had clear headroom
as of this research, though a current leaderboard number could not be independently confirmed here.
