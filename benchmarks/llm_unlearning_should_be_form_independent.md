---
id: llm_unlearning_should_be_form_independent
name: ORT (Out-of-Distribution Robustness Testing)
aliases:
  - ORT
  - ORT Benchmark
  - Out-of-Distribution Robustness Testing
  - LLM Unlearning Should Be Form-Independent
page_kind: benchmark
category: safety
subcategory: form-independent LLM unlearning (forget vs retain, four query formats)
status: active
summary: >
  ORT checks whether an unlearning method erases knowledge of a real person
  across four query forms, not only the form used in the unlearning samples.
measures: >
  ORT is a text-only English unlearning test. Each target is a well-known real
  person. After unlearning, the model is queried on a forget set about that
  person and on a retain set about other people. The same facts appear in four
  formats: simple QA, fill-in-the-blank, multiple-choice labels, and
  subtoken-inducing QA that forces character-level tokens. A method that only
  suppresses the training form can still answer the other three. The paper
  calls that failure Form-Dependent Bias. Utility is checked separately on
  MMLU, TruthfulQA, TriviaQA, and AlpacaEval rather than inside ORT itself.
task_format: >
  Single-target unlearning, then prompt-based probes. Training corpora come in
  three styles (unstructured text, refusal QA, preference pairs). Evaluation
  prompts are QA, fill-in-the-blank, multiple-choice, or subtoken QA on both
  the forget set and the retain set.
metric:
  name: joint probability of the gold answer given the prompt
  direction: lower_is_better
  unit: ''
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The headline ORT number is P(gold answer | prompt). On the forget set,
    lower is the desired unlearning outcome. On the retain set the same
    probability should stay high, so retain scores are not lower-is-better.
    The paper's main table averages the first 100 of 200 targets in a
    single-target setting on Llama3-8B-Instruct and Mistral-7B-Instruct-v0.3.
    Utility uses ordinary higher-is-better scores: 5-shot MMLU accuracy,
    6-shot TruthfulQA MC1, 6-shot TriviaQA F1, and AlpacaEval n-gram entropy.
dataset:
  size: 35052
  size_note: >
    Table II of the paper: 200 unlearning targets; 12,294 forget-set evaluation
    entries (QA 2,879, FB 3,268, MCP 3,268, subtoken QA 2,879) and 22,758
    retain-set entries (QA 5,533, FB 5,846, MCP 5,846, subtoken QA 5,533).
    Each target has 300+ training samples per corpus format. MCP and subtoken
    QA were converted from QA/FB with gemini-2.5-flash-preview-04-17 so that
    they probe the same facts in a different token form. Part of the data is
    restructured from RWKU.
  url: https://github.com/Acruxos/ORT
  license: ''
  languages:
    - en
  modalities:
    - text
  splits: >
    200 targets, each with forget and retain probes in four formats. The
    authors report averages on the first 100 targets. The evaluation files
    sit under LLaMA-Factory/data/ORT/Target in the official repo.
  public_test_set: true
publisher:
  org: Beijing University of Posts and Telecommunications, Shandong University, and Institute of Automation, Chinese Academy of Sciences
  authors:
    - Xiaotian Ye
    - Mengqi Zhang
    - Shu Wu
  url: https://github.com/Acruxos/ORT
paper:
  title: LLM Unlearning Should Be Form-Independent
  arxiv: '2506.07795'
  url: https://arxiv.org/abs/2506.07795
  year: 2025
leaderboard_url: ''
repo_url: https://github.com/Acruxos/ORT
released: '2025-06'
last_updated: '2025-07'
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ''
  note: >
    Table I shows large gaps between QA/FB and MCP/subtoken probes for GA, NPO,
    RT, and DPO. The authors' ROCR method is a training-free unlearning
    procedure, not a saturated leaderboard score. No public live leaderboard
    was found.
contamination:
  risk: high
  note: >
    Targets are 200 prominent real people whose biographies already sit in
    pretraining, which is the point of the RWKU-style setup. Evaluation items
    and training corpora are public (GitHub plus Google Drive / Baidu mirrors).
    MCP and subtoken items were LLM-rewritten from the same facts.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: 'Official scripts run_expr_lora.py and summarize.py in github.com/Acruxos/ORT (not an lm-eval or inspect task).'
tags:
  - unlearning
  - safety
  - form-dependence
  - RWKU
  - probability
  - privacy
sources:
  - url: https://arxiv.org/abs/2506.07795
    title: 'LLM Unlearning Should Be Form-Independent (arXiv abs)'
    accessed: '2026-09-08'
  - url: https://arxiv.org/html/2506.07795v1
    title: 'LLM Unlearning Should Be Form-Independent (arXiv HTML v1)'
    accessed: '2026-09-08'
  - url: https://github.com/Acruxos/ORT
    title: 'Acruxos/ORT repository'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/Acruxos/ORT/main/README.md
    title: 'Acruxos/ORT README'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/Acruxos/ORT/main/LICENSE
    title: 'Acruxos/ORT MIT LICENSE'
    accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: 'Grok Build, batch-078 (Codex coordinated)'
  reviewed: ''
  reviewed_by: ''
---

## What it measures

ORT asks whether an unlearning method forgot a person, or only the wording it was trained on. Each of 200 well-known people is a forget target. After unlearning, the model is asked about that person and about other people, in four English text formats.

Simple QA and fill-in-the-blank reuse answer tokens from the training corpora. Multiple-choice asks for a label such as A or B. Subtoken QA asks for the same string one character at a time, so the tokenizer emits unseen pieces. A method that only breaks the trained form can still leak the fact in the other formats.

## How it is scored

The main score is the joint probability of the gold answer given the prompt. On the forget set, that probability should fall. On the retain set, it should stay high. The paper reports both, for all four formats, as averages over the first 100 targets on Llama3-8B-Instruct and Mistral-7B-Instruct-v0.3.

There is no single official composite. A reader has to look at forget versus retain together. Utility is a separate suite: 5-shot MMLU, 6-shot TruthfulQA MC1, 6-shot TriviaQA F1, and AlpacaEval n-gram entropy. Those checks catch collapse that a low forget-set probability would hide.

## Dataset and licence

Table II lists 200 targets, 12,294 forget probes, and 22,758 retain probes. Each target has 300+ training samples in each of three corpus styles: unstructured text for gradient-ascent methods, refusal QA for rejection tuning, and preference pairs for DPO. The authors' ROCR method does not use those corpora; it takes the target name as a concept.

Part of the data is restructured from RWKU. MCP and subtoken items were rewritten from QA and FB with gemini-2.5-flash-preview-04-17 so they test the same facts. The evaluation files are public. The repository LICENSE is MIT; a separate dataset licence is not stated beyond that file.

## Who publishes it

Xiaotian Ye (BUPT), Mengqi Zhang (Shandong University), and Shu Wu (CASIA NLPR/MAIS) released the paper on arXiv on 9 June 2025. The code and data layout live at [Acruxos/ORT](https://github.com/Acruxos/ORT). The GitHub description labels the work as S&P 2026. The arXiv HTML v1 does not name a venue. There is no public live leaderboard.

## Lineage

ORT extends RWKU's 200 real-person targets with two extra formats meant to force unseen tokens. This repository has no RWKU page. Related unlearning evaluation in-tree is [WMDP](wmdp.md), which scores hazardous-knowledge QA rather than form transfer. The same paper proposes ROCR, a training-free concept-redirection method; that is a method, not a successor benchmark. The census id is the paper title; the evaluation's own name is ORT.

## Saturation and contamination

Current unlearning baselines in Table I still depend on format, so the suite is open. Famous-person facts are in pretraining by design, and the probes are public, so contamination risk is high if someone treats ORT like a closed exam. It is a diagnostic for unlearning methods, not a knowledge contest.

## How to run it

Clone [Acruxos/ORT](https://github.com/Acruxos/ORT). Download the ORT data (Google Drive or Baidu links in the README) into `LLaMA-Factory/data/ORT`. Point `MODEL_PATHS` at local checkpoints. `run_expr_lora.py` runs GA, NPO, RT, DPO, ROCR, or the original model; `summarize.py` writes a CSV. The README asks for a GPU with at least 48 GB. The main paper numbers use the first 100 targets in a single-target setting. No lm-eval, inspect, HELM, OpenCompass, or BIG-bench task name was found.

## Reading the numbers

A strong ORT result is a drop on all four forget formats with retain probabilities still near the base model, plus intact MMLU and TruthfulQA. A drop only on QA or fill-in-the-blank is Form-Dependent Bias, not erasure. Do not compare a forget-set probability to an accuracy number from [WMDP](wmdp.md) or to ROUGE-style TOFU scores. Report forget, retain, and utility together. The authors' ROCR numbers are one method on this suite, not a ceiling for the benchmark.
