---
id: unnatural_in_context_learning
name: "Unnatural In-Context Learning"
aliases: ["BIG-bench Unnatural In-Context Learning"]
page_kind: benchmark
category: reasoning
subcategory: "few-shot program induction on synthetic formats"
status: active
summary: "Synthetic identity, date, reversal and arithmetic subtasks test in-context pattern induction outside natural training distributions."
measures: "Few-shot examples define synthetic transformations; the model must produce the next output. Subtasks cover identity, date formats, reversal and unusual two-digit addition."
task_format: "Free-text numerical or symbolic completion with variable numbers of demonstrations."
metric: {name: "exact completion accuracy", direction: higher_is_better, unit: "%", max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "Subtasks have different output spaces, so one random baseline is not established."}
dataset:
  size: 73420
  size_note: "The task header reports 73,420 free-text dummy-model queries; this is not a stated train/test split."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/unnatural_in_context_learning"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "aggregate synthetic subtasks; no train/test split stated"
  public_test_set: true
publisher: {org: "BIG-bench collaboration", authors: ["Frieda Rong", "Percy Liang"], url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/unnatural_in_context_learning"}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: "https://arxiv.org/abs/2206.04615", year: 2022}
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench"
released: "2022"
last_updated: ""
lineage: {family: "big_bench", predecessor: "", successors: [], variants: [identity, dates, dates_unnatural_content, dates_unnatural_form, dates_unnatural_content_and_form, unnatural_addition_2_digit, reverse_natural_content, reverse_to_natural_content]}
saturation: {status: unknown, top_score: null, as_of: "", note: "Historical GPT-3 analyses do not establish a current aggregate ceiling."}
contamination: {risk: medium, note: "Generated distributions and task code are public; the authors say direct training on them defeats the experiment."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "unnatural_in_context_learning", other: ""}
tags: [big-bench, in-context-learning, synthetic, program-induction]
sources:
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/unnatural_in_context_learning/README.md", title: "BIG-bench Unnatural In-Context Learning README", accessed: "2026-09-09"}
  - {url: "https://ai.stanford.edu/blog/in-context-learning/", title: "SAIL in-context learning analysis", accessed: "2026-09-09"}
  - {url: "https://arxiv.org/abs/2005.14165", title: "GPT-3 few-shot learners paper", accessed: "2026-09-09"}
  - {url: "https://arxiv.org/abs/2206.04615", title: "BIG-bench paper", accessed: "2026-09-08"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

Unnatural In-Context Learning tests whether a model infers a transformation when formatting is unusual. It includes identity, date transformations, reversals and two-digit addition where the subtraction symbol stands for addition.

The examples are synthetic, so the model must attend to local patterns rather than ordinary semantic associations. This is a controlled probe of in-context learning and program induction.

## How it is scored

The task uses exact completion accuracy over generated examples. Subtasks have different output spaces, so an aggregate must state subtask weighting and shot count. The README reports historical GPT-3 results for selected subtasks rather than a current unified leaderboard.

Report demonstration number and order, delimiters and generation normalization. More shots can help or hurt depending on the transformation and context window.

## Dataset and licence

The task is programmatically generated. It defines finite distributions for dates, alphabetic strings, common five-letter words and two-digit arithmetic. Reverse subtasks use a public Norvig word list. The header reports 73,420 free-text dummy-model queries but does not present that as a conventional split.

A separate licence for generated examples is not established. The Norvig list has its own source terms.

## Who publishes it

BIG-bench hosts the task, documented in the 2022 BIG-bench paper. Frieda Rong and Percy Liang are the task's credited authors. The task README links to their companion SAIL blog analysis and to the 2020 GPT-3 paper, which motivated the subtask designs but does not itself describe this dataset. No current standalone leaderboard was established.

## Lineage

The task extends synthetic few-shot experiments described in the GPT-3 paper and SAIL blog. It is not an MMLU subset. Its named subtasks are variants with different input and output distributions.

## Saturation and contamination

The task is public and algorithmic, so training directly on its distributions could solve it. The authors explicitly say this would defeat the intended experiment. No current saturation or refreshed hidden distribution was established.

## How to run it

Run BIG-bench task unnatural_in_context_learning. Report subtasks separately when possible, preserving shot count, order, format markers and exact matching.

## Reading the numbers

A high score can show that a model inferred a transformation from examples. It does not show broad reasoning or knowledge. Public distributions make memorization possible. Pair it with held-out synthetic transformations and natural-language evaluations.

