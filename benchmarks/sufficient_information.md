---
id: sufficient_information
name: "Sufficient Information"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "abstention / answerability judgment"
status: active
summary: "Tiny BIG-bench task of 39 short word problems that checks whether a model answers when given enough information and says 'I do not know' when it is not."
measures: "Sufficient Information gives a model a short word problem and asks it to answer only if the prompt actually contains enough information to determine a correct answer, and to respond 'I do not know' otherwise. For example, 'Jamal is five years old. How old is Jamal?' has a determinate answer ('Five'), while 'Keisha has more phones than Kelsey. Kelsey has two phones. How many phones does Keisha have?' does not, since 'more' is not quantified. The task probes whether a model can recognize the limits of what it has been told, rather than defaulting to always producing a best-effort guess."
task_format: "Free-text, zero-shot generation: the model is given a task prefix instructing it to answer from context or say 'I do not know', then a short word-problem prompt, and must produce the exact expected answer string or the fixed abstention string."
metric:
  name: "exact string match"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Scored by exact_str_match between the model's generated text and the target string (a spelled-out number or short phrase, or the literal 'I do not know'). No random-baseline percentage is defined by the source; the task's own README notes that roughly half of the 39 items have 'I do not know' as the target, so a model that always answers 'I do not know' would score near 50% by this metric alone, which the author flags as a limitation of the task's simplicity."
dataset:
  size: 39
  size_note: "39 free-text examples (0 multiple choice), each a single short input/target pair, counted directly from the task's task.json. All items were written by the task's author; there is no separate train/test split."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sufficient_information"
  license: "Apache-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "single set of 39 items, no train/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors: ["Sam Dillavou"]
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sufficient_information"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sufficient_information"
released: "2022"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The task's own README states the author had not run it on any language model before submitting it to BIG-bench, so there is no baseline result in the primary source at all, let alone a recent one; no other source consulted here gives a dated frontier-model score."
contamination:
  risk: high
  note: "All 39 items and their exact target answers are published in plain text in the task's JSON file in the public BIG-bench GitHub repository, alongside a canary GUID intended to flag it for training-data exclusion. Given the dataset's small size, any exposure during training would be easy for a model to memorize outright."
harness:
  lm_eval: "bigbench_sufficient_information_generate_until"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "sufficient_information"
  other: ""
tags: ["abstention", "answerability", "logical reasoning", "zero-shot", "small-benchmark"]
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sufficient_information"
    title: "sufficient_information task directory, BIG-bench"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/sufficient_information/README.md"
    title: "sufficient_information README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/sufficient_information/task.json"
    title: "sufficient_information task.json"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game (BIG-bench paper)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bigbench/generate_tasks.py"
    title: "lm-evaluation-harness BIG-bench task generator"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/blob/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

Sufficient Information tests whether a model can tell the difference between a question it has enough information to answer and one it does not, rather than always producing its best guess. Each of the task's 39 items is a short word problem: some give exactly the facts needed to compute a determinate answer ("Jamal is five years old. How old is Jamal?" -> "Five"), while others withhold a needed quantity or use vague comparative language ("Keisha has more phones than Kelsey. Kelsey has two phones. How many phones does Keisha have?" -> "I do not know"). The model is instructed up front to answer "I do not know" when the prompt is insufficient, and to answer correctly, with numbers spelled out, when it is not.

The author's stated motivation is that language models are typically trained to always attempt an answer rather than to question whether the posed question is well-formed or fully specified, which is a capability human respondents exercise routinely.

## How it is scored

Model output is graded with exact string match (`exact_str_match`) against a single target string per item -- either a spelled-out number/short phrase or the literal string "I do not know" -- following a fixed task-prefix instruction that tells the model to answer from context or abstain. There is no partial credit and no rescaling; the reported score is the fraction of the 39 items matched exactly. The task's own README notes a specific weakness of this design: because close to half of the items have "I do not know" as their target, a model that always abstains scores near 50% without demonstrating any actual sufficiency judgment, which limits how informative the raw score is on its own.

## Dataset and licence

The dataset is small: 39 free-text examples, each a single input/target pair, all written by the task's sole author (confirmed by counting entries directly in the published `task.json`). There is no train/test split and no external data source; the BIG-bench repository is licensed Apache-2.0.

## Who publishes it

The task was contributed to BIG-bench by Sam Dillavou and appears in the BIG-bench collaboration's 2022 paper "Beyond the Imitation Game." The author's own README states they had not evaluated any language model on the task prior to its inclusion in BIG-bench. There is no independent leaderboard beyond the auto-generated performance plot in the task's `results/` directory.

## Lineage

The task has no family page, predecessor or successor confirmed from a primary source in this repository, and its own README frames it as a first, deliberately simplified pass at testing answerability judgment, suggesting (but not naming) future extensions such as asking the model to state what information is missing.

## Saturation and contamination

No baseline or current score is available from any source consulted here: the author had not tested the task on any model before contributing it, and no later source gives a dated frontier-model result, so saturation status is unknown. Contamination risk is high given the task's small size (39 items) and full public disclosure of both prompts and target answers in the BIG-bench GitHub repository, despite an included canary string meant to flag it for training-data exclusion.

## How to run it

The task runs through BIG-bench's standard JSON task interface as `sufficient_information`, and is included in lm-evaluation-harness's programmatically generated BIG-bench task set, appearing there as `bigbench_sufficient_information_generate_until` (a free-text/generate-until task, since none of its items are multiple choice). No inspect_evals, HELM or OpenCompass integration was confirmed from a primary source for this page.

## Reading the numbers

Because roughly half the items have "I do not know" as the correct answer, a raw score near 50% is uninformative on its own -- it does not distinguish a model that reasons correctly about sufficiency from one that abstains indiscriminately. A meaningful read requires looking at accuracy separately on the answerable and unanswerable subsets (not reported by the task itself) rather than the single aggregate exact-match score. Given the dataset's tiny size (39 items) and full public availability, small score differences between models are not statistically meaningful and results for any model released well after 2022 should be treated with contamination in mind.
