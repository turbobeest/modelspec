---
id: ifevalcode
name: "IFEvalCode"
aliases: []
page_kind: benchmark
category: instruction-following
subcategory: "instruction-following applied to code generation: functional correctness and constraint adherence scored as two independent axes"
status: active
summary: "IFEvalCode scores code models on two independent checks per problem: functional correctness, and whether the code also obeys an explicit style or structural instruction, across eight languages."
measures: >
  IFEvalCode gives a model a natural-language coding prompt that bundles an ordinary programming task
  with an explicit, checkable constraint on the code itself -- a naming convention, a required
  language construct such as a list comprehension or ternary operator, a formatting rule, or a ban on
  comments. Every one of the 810 problems is offered in both Chinese and English, and spans eight
  languages: Python, Java, JavaScript, TypeScript, C++, C#, PHP and Shell. The benchmark's stated point
  is that code-generation evaluations that check only correctness miss a second, largely independent
  failure mode: a model can write working code that ignores the instructions layered on top of the
  underlying task, the same gap IFEval (in this repository) measures for natural-language responses.
task_format: >
  Single-turn code generation: given a prompt combining a coding task with an instruction constraint,
  the model produces a solution for a named entry-point function. Each problem ships its own executable
  `check_correctness` function (functional test cases) and `check_instruction` function (a
  language-aware static or regex check of the submitted code, for example scanning variable names for
  snake_case or checking that no list comprehension appears in the source). Execution happens inside a
  per-language Docker sandbox.
metric:
  name: "correctness accuracy, instruction-adherence accuracy, and overall accuracy (share of samples passing both checks at once), reported overall and per language"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Correctness and instruction adherence are scored independently per sample and averaged; overall
    accuracy additionally requires both checks to pass on the same sample, which is stricter and
    consistently lower than either component alone. No random or human baseline applies to free-form
    code generation.
dataset:
  size: 810
  size_note: >
    810 problems across eight programming languages (counted directly from the released file: Python
    105, C# 103, Java 102, C++ 100, JavaScript 100, PHP 100, Shell 100, TypeScript 100), each with both
    a Chinese and an English prompt. The paper's own abstract describes "1.6K test samples" across
    "seven programming languages," naming Python, Java, JavaScript, TypeScript, Shell, C++ and C# but
    omitting PHP. The released test set and the inspect_evals implementation both include PHP as an
    eighth language and total 810 rows (1,620 if each row's two language versions are counted
    separately, which reconciles with the abstract's "1.6K" figure). This page follows the released
    dataset and the harness implementation, both read directly.
  url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/IfEvalCode-testset"
  license: ""
  languages: [English, Chinese]
  modalities: [text, code]
  splits: "single 'train' split used as the evaluation set (810 rows); no separate held-out test split is named"
  public_test_set: true
publisher:
  org: "Hosted under the Multilingual-Multimodal-NLP organisation on Hugging Face; individual authors' institutional affiliations were not confirmed from a source read for this page"
  authors: ["Jian Yang", "Wei Zhang", "Shukai Liu", "Linzheng Chai", "Yingshui Tan", "Jiaheng Liu", "Ge Zhang", "Wangchunshu Zhou", "Guanglin Niu", "Zhoujun Li", "Binyuan Hui", "Junyang Lin"]
  url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/IfEvalCode-testset"
paper:
  title: "IFEvalCode: Controlled Code Generation"
  arxiv: "2507.22462"
  url: "https://arxiv.org/abs/2507.22462"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/ifevalcode"
released: "2025-07"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 23.5
  as_of: "2026-02"
  note: >
    inspect_evals' own February 2026 evaluation report (200 samples per model) put gemini-3-pro-preview
    at 23.5% overall accuracy and gpt-5.2 at 19.0%, both far below their much higher per-axis scores
    (correctness alone in the 45-56% range) -- overall accuracy requires both checks to pass on the same
    sample, which is a harder bar than either axis alone. The paper's own broader run (810 samples, 40+
    models, closed models only shown per-axis rather than combined) put its best per-axis averages
    around 39% correctness and 24% instruction adherence. Both readings show a benchmark that still
    separates models rather than one near a ceiling.
contamination:
  risk: medium
  note: >
    The dataset was released in August 2025, roughly a year before this research; every problem's exact
    functional tests and instruction checks -- effectively an answer key -- are public in the same
    Hugging Face file as the prompts. No source read for this page reported evidence of contamination
    inflating scores, and the low overall-accuracy numbers as of February 2026 argue against widespread
    leakage so far, but the tests being bundled openly with the prompts is a structural risk that grows
    the longer the dataset sits in public view.
harness:
  lm_eval: ""
  inspect_evals: "ifevalcode"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Requires `pip install inspect-evals[ifevalcode]` and a Docker sandbox (per-language toolchains,
    declared in the task's `compose.yaml`); a 2026-04-21 fix to the harness notes that TypeScript
    correctness previously always scored 0% because `tsc` could not resolve `require()` calls, which
    matters when comparing scores measured before and after that date.
tags: [instruction-following, coding, multilingual, bilingual, verifiable, code-generation]
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ifevalcode/README.md"
    title: "IFEvalCode task README, inspect_evals"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ifevalcode/ifevalcode.py"
    title: "ifevalcode.py: task definition, supported languages, dataset revision"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2507.22462"
    title: "IFEvalCode: Controlled Code Generation"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Multilingual-Multimodal-NLP/IfEvalCode-testset"
    title: "Multilingual-Multimodal-NLP/IfEvalCode-testset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=Multilingual-Multimodal-NLP/IfEvalCode-testset"
    title: "IfEvalCode-testset split info and features, datasets-server"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/IfEvalCode-testset/resolve/main/IFEvalCode.jsonl"
    title: "IFEvalCode.jsonl: the 810 released problems"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

IFEvalCode gives a model a coding prompt that bundles an ordinary programming task with an explicit,
checkable constraint on the code itself: a naming convention, a required language construct such as a list
comprehension, a formatting rule, or a ban on comments. Every one of its 810 problems is offered in both
Chinese and English and spans eight languages -- Python, Java, JavaScript, TypeScript, C++, C#, PHP and
Shell. The benchmark's premise is that correctness-only code evaluations miss a second, largely independent
failure mode: a model can write working code that quietly drops the instructions layered on top of the
task. That framing mirrors IFEval (in this repository), which measures the same kind of gap for
natural-language responses rather than code; IFEvalCode's own materials do not cite IFEval directly in what
was read for this page, but the shared name and the same decoupled-metric design make the relationship
clear.

## How it is scored

A model produces one function per problem, targeting a named entry point. Each problem carries its own
executable `check_correctness` function (functional test cases run against the submission) and
`check_instruction` function (a static or regex check of the source, for example scanning variable names
for snake_case or confirming a required list comprehension is present), evaluated inside a per-language
Docker sandbox. Correctness and instruction adherence are scored independently and averaged across the
set; overall accuracy additionally requires both checks to pass on the same sample, which is consistently
the lowest of the three numbers reported.

## Dataset and licence

810 problems across eight programming languages (105 Python, 103 C#, 102 Java, 100 each of C++, JavaScript,
PHP, Shell and TypeScript), each with a Chinese and an English version of the prompt, hosted on Hugging Face
with no licence field set. The paper's own abstract describes "1.6K test samples" across "seven programming
languages," listing Python, Java, JavaScript, TypeScript, Shell, C++ and C# but not PHP; the released file
and the inspect_evals harness both include PHP as an eighth language, and 810 problems times two language
versions each reconciles with the abstract's "1.6K" figure. This page follows what the released dataset and
harness actually contain.

## Who publishes it

The paper "IFEvalCode: Controlled Code Generation" lists twelve authors -- Jian Yang, Wei Zhang, Shukai Liu,
Linzheng Chai, Yingshui Tan, Jiaheng Liu, Ge Zhang, Wangchunshu Zhou, Guanglin Niu, Zhoujun Li, Binyuan Hui
and Junyang Lin -- posted to arXiv in July 2025. The released test set is hosted under the
Multilingual-Multimodal-NLP organisation on Hugging Face. The inspect_evals implementation used for the
harness numbers on this page is credited to contributor PranshuSrivastava.

## Lineage

No predecessor or successor is tracked for this id in this repository. It sits alongside IFEval, IFBench
and AdvancedIF (all in this repository) as a benchmark built around the same idea -- score instruction
compliance separately from task success -- applied here to code instead of natural-language text, and
alongside Inverse IFEval (also in this repository) as another 2025-era instruction-following benchmark, though
Inverse IFEval targets instructions that conflict with a model's trained habits rather than code-specific
constraints. None of those relationships were confirmed as a direct citation from IFEvalCode's own paper or
README in the sources read for this page.

## Saturation and contamination

This benchmark is not saturated. inspect_evals' own February 2026 run (200 samples per model) scored
gemini-3-pro-preview at 23.5% overall accuracy and gpt-5.2 at 19.0%, both well below their correctness-only
scores in the 45-56% range -- overall accuracy demands both checks pass on the same sample. The paper's
broader 810-sample run across 40+ models showed a similar pattern for closed models: correctness averages
in the high 30s to low 40s (percent) alongside instruction-adherence averages in the low-to-mid 20s.
Contamination risk is medium: the dataset is a year old as of this research and every problem's exact test
code is public alongside its prompt, which functions as an answer key, though the still-low overall-accuracy
scores argue against significant leakage so far.

## How to run it

The reference implementation is inspect_evals' `ifevalcode` task (`pip install inspect-evals[ifevalcode]`),
which runs generated code inside a per-language Docker sandbox declared in the task's own `compose.yaml`.
Results are not directly comparable across all reporting dates: a 2026-04-21 fix corrected TypeScript
correctness, which previously always scored 0% because the `tsc` invocation could not resolve `require()`
calls against installed Node type declarations. Separately, the paper's own README-reproduced Table 3 lists
byte-identical per-language scores for o1-mini, o3-mini and o4-mini across all eight languages and both
metrics, which reads as a transcription artifact in that table rather than three different models scoring
identically, and is worth checking against the original paper before treating those three rows as
independent data points.

## Reading the numbers

A high correctness score means the generated code runs and passes its tests, nothing more; a high
instruction-adherence score means the code's style or structure matched the prompt's stated constraint,
independent of whether the code works. Overall accuracy, which needs both at once, is the harder and more
informative number if the use case actually requires both -- current frontier models clear it well under a
quarter of the time. Because the benchmark ships bilingual prompts, a gap between a model's Chinese and
English scores on the same underlying problems is also worth checking before trusting an aggregate number
across languages.
