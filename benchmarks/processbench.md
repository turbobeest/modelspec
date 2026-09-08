---
id: processbench
name: "ProcessBench"
aliases: []
page_kind: benchmark
category: math
subcategory: "step-level error localisation in mathematical reasoning traces"
status: active
summary: "3,400 human-annotated math solutions, mostly contest-level, where the model must name the earliest wrong step or report that the trace is clean."
measures: >
  ProcessBench tests whether a model can find mistakes in someone else's math, not whether it
  can solve the problem from scratch. Each item is a contest- or school-level problem plus a
  step-by-step solution whose first error (or lack of error) was labelled by human experts.
  The model must return the index of that earliest bad step, or -1 if every step is correct.
  The suite is aimed at process reward models and at general models prompted as critics.
task_format: >
  English generation. OpenCompass wraps each step in <paragraph_i> tags and asks for a
  paragraph-by-paragraph critique with the final index in \\boxed{}. Official Qwen code uses
  the same earliest-error / -1 protocol. Subsets: gsm8k, math, olympiadbench, omnimath.
metric:
  name: "F1 of error_acc and correct_acc"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    error_acc is accuracy on traces that contain an error (label != -1). correct_acc is
    accuracy on fully correct traces (label == -1). F1 is their harmonic mean, used as the
    headline so a model cannot win by always crying error or always saying clean. No random
    or human baseline is published. The paper's Table 3 top critic is o1-mini at 87.9 F1.
dataset:
  size: 3400
  size_note: >
    Hugging Face datasets-server and the paper agree on 3,400 cases: gsm8k 400, MATH 1,000,
    OlympiadBench 1,000, Omni-MATH 1,000. Problems come from those four public test sets;
    solutions are model-generated and then annotated. The paper's appendix count table
    (207+193, 594+406, 661+339, 759+241) is the error/correct split inside each subset.
  url: "https://huggingface.co/datasets/Qwen/ProcessBench"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "four named splits used as test sets: gsm8k, math, olympiadbench, omnimath"
  public_test_set: true
publisher:
  org: "Qwen Team, Alibaba Inc."
  authors:
    - "Chujie Zheng"
    - "Zhenru Zhang"
    - "Beichen Zhang"
    - "Runji Lin"
    - "Keming Lu"
    - "Bowen Yu"
    - "Dayiheng Liu"
    - "Jingren Zhou"
    - "Junyang Lin"
  url: "https://github.com/QwenLM/ProcessBench"
paper:
  title: "ProcessBench: Identifying Process Errors in Mathematical Reasoning"
  arxiv: "2412.06559"
  url: "https://arxiv.org/abs/2412.06559"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/QwenLM/ProcessBench"
released: "2024-12"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 87.9
  as_of: "2024-12"
  note: >
    Table 3 of the paper (arXiv 2412.06559, experiments as published December 2024) gives
    o1-mini 87.9 mean F1 as the strongest critic, ahead of QwQ-32B-Preview at 71.5 and
    GPT-4o-0806 at 61.9. OlympiadBench and Omni-MATH F1 remain well below GSM8K. Those
    figures predate later reasoning models and are not a live leaderboard.
contamination:
  risk: medium
  note: >
    Underlying problems are from public GSM8K, MATH, OlympiadBench and Omni-MATH tests.
    The annotated traces and labels are public on Hugging Face (Apache-2.0). The annotation
    layer is newer (December 2024) than the source problems. No publisher contamination
    study of the labels was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    processbench_gsm8k, processbench_math, processbench_olympiadbench, processbench_omnimath
    (ProcessBenchEvalDataset + ProcessBenchEvaluator; example examples/eval_ProcessBench.py)
  bigbench: ""
  other: "Official evaluation scripts and prompts live in github.com/QwenLM/ProcessBench."
tags:
  - math
  - process-supervision
  - prm
  - error-detection
  - english
sources:
  - url: "https://arxiv.org/abs/2412.06559"
    title: "ProcessBench arXiv abs (submitted 9 Dec 2024; ACL 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2412.06559"
    title: "ProcessBench paper full text (ar5iv), including Table 3 and subset sizes"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Qwen/ProcessBench/raw/main/README.md"
    title: "Qwen/ProcessBench dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Qwen/ProcessBench"
    title: "Qwen/ProcessBench Hugging Face API (Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Qwen/ProcessBench"
    title: "Qwen/ProcessBench row counts (400/1000/1000/1000)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/QwenLM/ProcessBench/main/README.md"
    title: "Official ProcessBench GitHub README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ProcessBench/README.md"
    title: "OpenCompass ProcessBench README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ProcessBench/processbench_gen.py"
    title: "OpenCompass processbench_gen.py critic prompt"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/ProcessBench.py"
    title: "OpenCompass ProcessBenchEvalDataset and F1 evaluator"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

ProcessBench asks a model to audit a written math solution. Each of the 3,400 items pairs a problem with a step-by-step trace. Human annotators mark the earliest incorrect step, or mark the trace fully correct (label -1). Three experts have to agree; the pool expands up to five if they do not. The model must return that index, not a repaired solution and not a final-answer check.

Problems are drawn from four public English math tests: GSM8K (400), MATH (1,000), OlympiadBench (1,000) and Omni-MATH (1,000). All but GSM8K are contest or Olympiad difficulty. Solutions are generated by language models and then labelled; the Hugging Face sample shows a Qwen2-7B-Instruct generator field.

## How it is scored

Two accuracies are computed. `error_acc` is how often the predicted index matches the label on traces that contain an error. `correct_acc` is how often the model outputs -1 on clean traces. The headline is the harmonic mean (F1) of those two percentages, so a model that always flags an error cannot top the board. OpenCompass's `ProcessBenchEvaluator` implements that split and pulls the index from the last `\\boxed{}`. The paper reports F1 per subset and a four-subset mean. Protocol for critics is prompted generation; PRMs are scored by taking the earliest step they mark wrong.

## Dataset and licence

`Qwen/ProcessBench` is Apache-2.0. The 3,400-row count matches the paper. Labels and full traces are public. There is no hidden test split.

## Who publishes it

Qwen Team, Alibaba: Chujie Zheng, Zhenru Zhang, Beichen Zhang, Runji Lin, Keming Lu, Bowen Yu, Dayiheng Liu, Jingren Zhou and Junyang Lin (several corresponding). arXiv 2412.06559 was submitted on 9 December 2024. The official repository and the OpenCompass README both list ACL 2025 as the venue. Code and prompts: https://github.com/QwenLM/ProcessBench.

## Lineage

ProcessBench is not a re-run of [GSM8K](gsm8k.md), [MATH](math.md) or [Omni-MATH](omni_math.md). Those supply the problems; this benchmark scores process critique of generated traces. It is the evaluation companion to Qwen's process-reward-model work, not a successor that replaces those answer-level tests. No later ProcessBench version is recorded in this repository.

## Saturation and contamination

Table 3 (December 2024) puts o1-mini at 87.9 mean F1, QwQ-32B-Preview at 71.5 and GPT-4o-0806 at 61.9. GSM8K is much easier than OlympiadBench and Omni-MATH (o1-mini 93.2 versus 87.2 and 82.4 on those two). That spread, and the drop for existing PRMs off GSM8K/MATH, is why saturation is open. The 87.9 figure is the paper's own critic number, not a live board. Underlying problems are old public tests; the annotated traces are newer and also public, so contamination risk is medium.

## How to run it

OpenCompass: `python run.py examples/eval_ProcessBench.py`, tasks `processbench_gsm8k`, `processbench_math`, `processbench_olympiadbench`, `processbench_omnimath`. The official GitHub `code/` folder is the authors' critic and PRM scoring. No lm-eval, HELM or inspect_evals task was found. Compare a PRM run to a critic run only after checking the prompt and how "earliest error" is read from scores versus from boxed text.

## Reading the numbers

A high F1 means the model both catches the first real mistake and leaves clean traces alone. Final-answer accuracy on GSM8K or MATH does not substitute: ProcessBench can fail a model that gets the right number from a wrong step, and can pass a critic that never solves the problem. Look at the four subsets separately; a GSM8K-only F1 overstates contest-level process skill.
