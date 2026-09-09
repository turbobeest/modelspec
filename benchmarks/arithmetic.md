---
id: arithmetic
name: "Arithmetic (GPT-3 synthetic arithmetic tasks)"
aliases: []
page_kind: benchmark
category: math
subcategory: "synthetic few-shot arithmetic, GPT-3-derived task family"
status: unknown
summary: "Ten fixed synthetic arithmetic tasks -- 2 to 5 digit addition and subtraction, 2-digit multiplication, one-digit composite expressions -- introduced as one small evaluation in the GPT-3 paper."
measures: >
  The "arithmetic" task family tests basic numeric computation through natural-language word
  problems: a prompt states two (or, for the composite task, three) numbers and an operation in
  English, such as "What is 48 plus 27?", and the model must produce the exact numeric answer.
  lm-evaluation-harness implements ten such tasks, mirroring the ten tasks OpenAI introduced as one
  evaluation among many in the original GPT-3 paper: one-digit composite expressions combining
  addition and multiplication (e.g. 6+(4*8)), 2-, 3-, 4- and 5-digit addition, 2-, 3-, 4- and 5-digit
  subtraction, and 2-digit multiplication. The GPT-3 authors framed this as a test of whether a
  language model could perform simple, unseen computations "on the fly" from its few-shot context,
  not as a benchmark of the multi-step mathematical reasoning that GSM8K or MATH later targeted.
task_format: "A natural-language arithmetic word problem (e.g. 'Q: What is 48 plus 27? A:') in; the model must generate the exact numeric answer as free text, with no chain-of-thought or intermediate steps required or scored."
metric:
  name: "exact-match accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No random or human baseline is defined for this free-form generation task. The GPT-3 paper reports zero-shot, one-shot and few-shot accuracy directly, with a clear jump from zero-shot to few-shot on most of the ten tasks."
dataset:
  size: 20000
  size_note: "2,000 procedurally generated problems per task across the 10 lm-evaluation-harness sub-tasks (matching the GPT-3 paper's own per-task sample size), for 20,000 items total. OpenAI's own openai/gpt-3 data directory additionally holds six-digit addition/subtraction and sum-of-digits files not covered by this 10-task harness split."
  url: "https://github.com/openai/gpt-3/tree/master/data"
  license: ""
  languages: ["en"]
  modalities: ["text"]
  splits: "no train/validation split; each of the 10 tasks is a single fixed 2,000-item evaluation file"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: ["Tom B. Brown", "et al. (OpenAI)"]
  url: "https://github.com/openai/gpt-3"
paper:
  title: "Language Models are Few-Shot Learners"
  arxiv: "2005.14165"
  url: "https://arxiv.org/abs/2005.14165"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arithmetic"
released: "2020-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: "No current top-score figure or dedicated leaderboard was confirmed from a source opened during this research, and no model card currently in this repository cites it. The task caps out at 5-digit addition/subtraction and 2-digit multiplication, well within the range modern frontier models are widely observed to handle reliably, so the spread between strong current models on this specific task family has plausibly collapsed -- though no source consulted here confirms a recent number."
contamination:
  risk: medium
  note: "The fixed 2,000-item files for all ten tasks have been publicly available in OpenAI's repository since 2020, so literal memorization is possible. Correctly computing arithmetic does not strictly require having seen the exact problem before, which makes contamination a weaker practical concern here than for fact-recall benchmarks built the same way."
harness:
  lm_eval: "arithmetic"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["math", "synthetic", "few-shot", "gpt-3-derived", "legacy-benchmark"]
sources:
  - url: "https://arxiv.org/abs/2005.14165"
    title: "Language Models are Few-Shot Learners"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2005.14165"
    title: "Language Models are Few-Shot Learners (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/gpt-3/tree/master/data"
    title: "openai/gpt-3 data directory (arithmetic and word-scramble eval sets)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/gpt-3"
    title: "openai/gpt-3 repository"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arithmetic"
    title: "lm-evaluation-harness arithmetic task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arithmetic/README.md"
    title: "lm-evaluation-harness arithmetic task README"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/arithmetic"
    title: "BIG-bench arithmetic task directory (separately authored, related task sharing this name)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The "arithmetic" task family tests basic numeric computation through natural-language word problems: a prompt states two (or, for the composite task, three) numbers and an operation in English, such as "What is 48 plus 27?", and the model must produce the exact numeric answer. lm-evaluation-harness implements ten such tasks, mirroring the ten OpenAI introduced as one evaluation among many in the GPT-3 paper: one-digit composite expressions combining addition and multiplication (e.g. 6+(4*8)), 2- to 5-digit addition, 2- to 5-digit subtraction, and 2-digit multiplication. The GPT-3 authors framed this as testing whether a model could perform simple, unseen computations "on the fly" from its few-shot context, not as a benchmark of the multi-step reasoning GSM8K or MATH later targeted.

This task family has no standalone publication of its own. It exists only as section 3.9.1 of the GPT-3 paper, and was later packaged into reusable, individually runnable task files by the lm-evaluation-harness maintainers, using the fixed problem sets OpenAI released in its own repository.

## How it is scored

Each answer is graded by exact string match against the correct numeric result; there is no partial credit and no scoring for intermediate reasoning steps, since the original GPT-3 evaluation did not use chain-of-thought prompting. The GPT-3 paper generated 2,000 random problem instances for each of its ten tasks and evaluated models zero-shot, one-shot and few-shot (up to 50 in-context examples), reporting a clear jump in accuracy from zero-shot to few-shot on most tasks; because no chain-of-thought is involved, the score reflects a model's ability to carry out the arithmetic directly rather than to reason through it in text.

## Dataset and licence

Each of the ten lm-evaluation-harness tasks draws on a fixed file of 2,000 procedurally generated problems, for 20,000 items in total, taken directly from the `data/` directory of OpenAI's own `openai/gpt-3` GitHub repository. There is no train/validation split; each task file is a single evaluation set. Neither the `openai/gpt-3` repository nor the lm-evaluation-harness task directory states an explicit data licence for these files, and none was found in the sources consulted for this page.

## Who publishes it

No organisation publishes "arithmetic" as a standalone benchmark. It originates from OpenAI's "Language Models are Few-Shot Learners" (Tom B. Brown and other OpenAI co-authors, May 2020), one of dozens of evaluations used to characterise GPT-3 rather than a dedicated contribution. EleutherAI's lm-evaluation-harness later extracted it into ten standalone, independently runnable tasks using OpenAI's own released problem files, the form in which it is normally run today.

## Lineage

Arithmetic has no predecessor of its own and, having originated inside a broader paper rather than as a dedicated release, no formally tracked successor either. BIG-bench separately hosts a task also named "arithmetic," authored by a different contributor, which the BIG-bench README describes as measuring "similar capabilities" to this one but explicitly extends it with additional cases -- division and higher-digit multiplication -- that the GPT-3/lm-evaluation-harness version does not test. The two are related in spirit but are not the same item set, and a score on one is not a substitute for a score on the other; this page documents the GPT-3/lm-evaluation-harness version specifically. No successor formally replaced synthetic arithmetic as a benchmark, but grade-school and competition math benchmarks such as `gsm8k` and `math` (both in this repository) now serve the role a simple arithmetic sanity check once played in evaluation suites.

## Saturation and contamination

No current top-score figure or dedicated leaderboard for this task family was found; it is not cited by any model card currently in this repository. Because the task caps out at 5-digit addition/subtraction and 2-digit multiplication -- well within the range modern frontier models are widely observed to handle reliably -- the spread between strong current models has plausibly collapsed, though no source consulted confirms a recent number. The fixed 2,000-item files for all ten tasks have been publicly available since 2020, so literal memorization is possible, though correctly computing arithmetic does not strictly require having seen the exact problem before, which makes contamination a weaker concern here than for fact-recall benchmarks built the same way.

## How to run it

lm-evaluation-harness exposes the ten tasks individually (`arithmetic_1dc`, `arithmetic_2da`, `arithmetic_2dm`, `arithmetic_2ds`, `arithmetic_3da`, `arithmetic_3ds`, `arithmetic_4da`, `arithmetic_4ds`, `arithmetic_5da`, `arithmetic_5ds`) under a shared `arithmetic` tag, sourcing its data from OpenAI's `openai/gpt-3` repository; a 2025 update to the harness changed only a prompt-formatting delimiter, not the underlying data. Because BIG-bench's same-named task tests a different, larger set of operations, always confirm which implementation a reported "arithmetic" score used before comparing it to another paper's number.

## Reading the numbers

A high score on this task family shows a model can carry out simple stated arithmetic directly from a natural-language prompt without decomposing it into steps, which is a narrow and, for current frontier models, largely solved capability rather than a test of mathematical reasoning. A low score is more informative than a high one: it can flag a genuine formatting, tokenization or instruction-following problem rather than a reasoning gap, since the arithmetic itself is simple. For a real read on a model's mathematical reasoning, look at `gsm8k` or `math` instead, both of which require multi-step reasoning that this task family was never designed to test.
