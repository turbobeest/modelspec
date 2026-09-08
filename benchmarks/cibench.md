---
id: cibench
name: CIBench
aliases: []
page_kind: benchmark
category: agentic
subcategory: "code-interpreter tool use across interactive, multi-step data-science notebooks"
status: active
summary: OpenCompass's interactive benchmark for LLM code-interpreter agents -- 234 multi-step data-science tasks (1,900+ questions) across ten Python libraries, scored end-to-end and in an error-corrected oracle mode.
measures: >
  CIBench tests whether an LLM agent can use a Python code interpreter to carry out a realistic,
  multi-step data-science workflow, rather than just produce an isolated code snippet for one
  self-contained problem. Each task is a simulated, interactive IPython/Jupyter session of 10 to 15
  progressive steps of increasing complexity, built around one of ten widely used Python libraries
  (lightgbm, matplotlib, nltk, opencv, pandas, pytorch, scipy, seaborn, sklearn, tensorflow), with a
  Chinese-language translation of the same task set, plus a separate, smaller six-library
  open-ended "generation" split (matplotlib, opencv, pandas, pytorch, scipy, seaborn). Tasks were
  built with an LLM-human cooperative method: an advanced LLM (GPT-4) proposed instructions and code
  in notebook form, and human experts then wrote reusable template tasks from the common patterns
  observed, so each template can be instantiated over multiple interchangeable underlying datasets.
  It is a multi-turn, tool-use task combining natural-language instructions, generated code, and the
  code interpreter's own output (including numbers, text and rendered plots) at each step.
task_format: >
  A sequence of 10 to 15 interconnected natural-language instructions per task, each requiring the
  model to write and execute Python code in a live IPython kernel and use the returned output to
  inform its next step; evaluated in two modes -- end-to-end, where the model must solve every step
  unaided, and oracle, where the model is handed the correct code whenever it fails a step, which
  isolates a step's individual difficulty from upstream error compounding.
metric:
  name: "process-oriented (tool-call rate, executable rate) and output-oriented (numeric accuracy, text score, visualization score) metrics"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper defines two metric families rather than one headline number: process-oriented metrics
    (tool-call rate, executable rate) checking whether the model engages the code interpreter
    correctly, and output-oriented metrics (numeric accuracy, text score, visualization score)
    checking whether its results are correct; the official leaderboard reports an "Avg" column
    defined as the mean of the numeric, text and visualization scores across both modes. The paper
    states the best open-source model it tested lagged GPT-4 by 10.0 percentage points on its
    aggregate results. No fixed random or human baseline applies to this open-ended, tool-use task.
dataset:
  size: 234
  size_note: >
    234 tasks comprising more than 1,900 individual interconnected questions/steps, per the paper's
    own comparison table against related datasets (DS-1000: 1,000 questions; MINT: 586; CodeGen: 115
    tasks; QwenAgent: 295 questions). Built across ten Python libraries for the main "template" split
    (with a Chinese-translated version of the same tasks) and six libraries for a separate, smaller
    "generation" split; this page could not confirm an exact split-by-split question-count breakdown
    from the sources read.
  url: "https://github.com/open-compass/opencompass/releases/download/0.2.4.rc1/cibench_dataset.zip"
  license: "Apache License 2.0, per the open-compass/CIBench GitHub repository's licence"
  languages:
    - en
    - zh
  modalities:
    - text
    - code
  splits: "template split (ten libraries, English and Chinese versions) and a separate six-library generation split; exact train/test partitioning not established"
  public_test_set: true
publisher:
  org: "Shanghai Artificial Intelligence Laboratory, with ShanghaiTech University"
  authors:
    - Chuyu Zhang
    - Songyang Zhang
    - Yingfan Hu
    - Haowen Shen
    - Kuikun Liu
    - Zerun Ma
    - Fengzhe Zhou
    - Wenwei Zhang
    - Xuming He
    - Dahua Lin
    - Kai Chen
  url: "https://open-compass.github.io/CIBench/"
paper:
  title: "CIBench: Evaluating Your LLMs with a Code Interpreter Plugin"
  arxiv: "2407.10499"
  url: "https://arxiv.org/abs/2407.10499"
  year: 2024
leaderboard_url: "https://open-compass.github.io/CIBench/leaderboard.html"
repo_url: "https://github.com/open-compass/CIBench"
released: "2024-07"
last_updated: "2024-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 75.5
  as_of: "2024-07"
  note: >
    The official leaderboard's top entry, GPT-4-1106-preview, scores an average of 75.5 (mean of
    numeric/text/visualization scores across both modes), with gpt-4o close behind at 74.5 and a
    clear drop to Llama-3-70B-Instruct at 65.5 -- real separation among models, not a collapsed
    ceiling. However, every one of the 24 models on the public leaderboard is a mid-2024-era or
    earlier model (GPT-4-1106-preview, gpt-4o, Llama-3, Qwen, DeepSeek, InternLM2, Mixtral, Yi,
    Vicuna, ChatGLM3, Llama-2); this page found no evidence the leaderboard has been updated with any
    model released since. Given how much frontier tool-use capability has advanced since mid-2024,
    current-generation saturation on CIBench is not established from this stale snapshot.
contamination:
  risk: medium
  note: >
    The reference task set has been publicly downloadable as a GitHub release asset since mid-2024,
    with gold outputs used for scoring, so a model trained since then could plausibly have seen it;
    the paper's own construction method (reusable templates instantiable over interchangeable
    datasets) may partly limit naive memorisation of one fixed transcript, but this page found no
    publisher statement or independent study demonstrating actual leakage into a specific model's
    training data, so it does not go beyond "medium."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "cibench_template (ten libraries, English and Chinese), cibench_generation (six libraries)"
  bigbench: ""
  other: "Reference implementation: the open-compass/CIBench GitHub repository, built on Lagent (InternLM's agent framework) and OpenCompass."
tags:
  - agentic
  - coding
  - tool-use
  - code-interpreter
  - data-science
  - multi-turn
sources:
  - url: "https://arxiv.org/abs/2407.10499"
    title: "CIBench: Evaluating Your LLMs with a Code Interpreter Plugin (Zhang, Zhang, Hu et al., arXiv:2407.10499)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.10499"
    title: "CIBench: Evaluating Your LLMs with a Code Interpreter Plugin (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/CIBench"
    title: "open-compass/CIBench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://open-compass.github.io/CIBench/leaderboard.html"
    title: "CIBench official leaderboard"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CIBench/CIBench_template_gen_e6b12a.py"
    title: "OpenCompass CIBench_template_gen_e6b12a.py (evaluation config)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CIBench tests whether an LLM agent can use a Python code interpreter to carry out a realistic, multi-step data-science workflow, rather than produce an isolated code snippet for one self-contained problem. Each task is a simulated, interactive IPython session of 10 to 15 progressive steps of increasing complexity, built around one of ten widely used Python libraries -- lightgbm, matplotlib, nltk, opencv, pandas, pytorch, scipy, seaborn, sklearn and tensorflow -- with a Chinese-language translation of the same task set, plus a separate, smaller six-library open-ended "generation" split.

Tasks were built with an LLM-human cooperative method: GPT-4 proposed instructions and code in notebook form, and human experts then wrote reusable template tasks from the common patterns observed, so each template can be instantiated over multiple interchangeable underlying datasets. It is a multi-turn, tool-use task: the model's code, the interpreter's returned output (numbers, text, and rendered plots), and the next instruction all chain together across a session, unlike single-shot code-generation benchmarks.

## How it is scored

CIBench evaluates in two distinct modes. In end-to-end mode, the model must solve every step of a session unaided, so an early mistake can cascade into later steps. In oracle mode, the model is handed the correct code whenever it fails a step, which isolates that step's individual difficulty from upstream error compounding. Two metric families apply in both modes: process-oriented metrics (tool-call rate, whether the model invokes the interpreter at all; executable rate, whether its code runs without error) and output-oriented metrics (numeric accuracy, text score, and a visualization score for generated plots). The official leaderboard's "Avg" column is the mean of the three output-oriented scores across both modes. The paper reports its strongest open-source model trailing GPT-4 by 10.0 percentage points in aggregate. Because CIBench reports several distinct sub-scores rather than one number, a single reported "CIBench score" should specify which mode and which metric it names.

## Dataset and licence

CIBench comprises 234 tasks totalling more than 1,900 individual interconnected questions, according to the paper's own comparison against related interactive-coding datasets. The reference data is distributed as a zip archive attached to an OpenCompass GitHub release, covering the ten-library template split in both English and Chinese plus the smaller six-library generation split; this page could not confirm an exact per-split question-count breakdown. The `open-compass/CIBench` reference repository is released under the Apache 2.0 licence. All task prompts and gold outputs needed for scoring are public.

## Who publishes it

CIBench was published in July 2024 (revised through at least November 2024) by Chuyu Zhang and Yingfan Hu (contributing equally), with project lead Songyang Zhang, and co-authors Haowen Shen, Kuikun Liu, Zerun Ma, Fengzhe Zhou, Wenwei Zhang, Dahua Lin and Kai Chen, all at the Shanghai Artificial Intelligence Laboratory, together with Xuming He at ShanghaiTech University. The `open-compass` GitHub organisation maintains both the standalone `CIBench` reference repository and the dataset's integration into the broader OpenCompass evaluation platform, and publishes a project page and leaderboard.

## Lineage

CIBench has no predecessor or successor tracked in this repository. It was built using Lagent, Shanghai AI Laboratory's own agent framework, and the same organisation later published a separate `lagent-cibench` GitHub repository (September 2024) integrating the benchmark more tightly with Lagent-based agents; that repository is not a distinct benchmark id in this repository. The paper's own related-work comparison places CIBench alongside DS-1000, MINT, CodeGen and QwenAgent as prior interactive or tool-use coding evaluations, none of which currently have a page in this repository; CIBench distinguishes itself from all of them by combining multi-turn, consecutive steps with mandatory code-interpreter use and both output- and process-oriented scoring in the same benchmark.

## Saturation and contamination

The official leaderboard's top entry, GPT-4-1106-preview, scores an average of 75.5, with gpt-4o close behind at 74.5 and a clear drop to Llama-3-70B-Instruct at 65.5 -- real separation among models rather than a collapsed ceiling, and well short of the 100-point maximum. However, every one of the 24 models on the public leaderboard dates to mid-2024 or earlier, and this page found no evidence the leaderboard has been updated with any model released since. Given how far frontier tool-use capability has advanced since mid-2024, current-generation saturation is not established from this now-stale snapshot.

Contamination risk sits at medium: the reference task set, with gold outputs, has been publicly downloadable since mid-2024, so a model trained since then could plausibly have seen it. The benchmark's reusable-template construction may somewhat limit naive memorisation of one fixed transcript, but no publisher statement or independent study demonstrating actual leakage was found.

## How to run it

The reference implementation lives in the `open-compass/CIBench` GitHub repository, built on Lagent and OpenCompass; OpenCompass itself ships the dataset as `cibench_template` (ten libraries, English and Chinese) and `cibench_generation` (six libraries), using an `AgentInferencer` that lets the model call the code interpreter across each session's consecutive steps and a dedicated `CIBenchEvaluator` for scoring. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because scores depend heavily on which of the ten-plus libraries a subset covers, which mode (end-to-end or oracle) was used, and which sub-metric is quoted, a single aggregate "CIBench score" needs all three specified before it can be compared to another.

## Reading the numbers

A high CIBench score indicates a model can chain code-interpreter calls across a multi-step data-science workflow and recover useful numeric, textual and visual results along the way -- a meaningfully different skill from generating a single correct function in isolation. Process metrics and output metrics can diverge: the paper notes open-source models frequently call the tool successfully (high tool-call and executable rates) yet still produce wrong numeric or visual results, so a strong process score alone does not imply a strong output score. Because the public leaderboard has not visibly been refreshed with any post-2024 model, treat any CIBench number for a current frontier model as unverified against this benchmark's own official standings, and check the mode (end-to-end versus oracle) before comparing scores, since oracle mode is deliberately easier by design.
