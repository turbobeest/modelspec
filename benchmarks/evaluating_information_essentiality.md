---
id: evaluating_information_essentiality
name: "Evaluating Information Essentiality"
aliases:
  - "The Essential, the Excessive, and the Extraneous"
page_kind: subset
category: reasoning
subcategory: "BIG-bench data-sufficiency task: judging whether given statements are necessary to answer a question (68 items)"
status: superseded
summary: "A tiny, 68-item BIG-bench task modelled on GMAT-style data-sufficiency questions, testing whether a model can tell which of two statements are necessary, sufficient, or redundant to answer a question."
measures: >
  Evaluating Information Essentiality poses a question, sometimes with brief context, followed by two
  supporting statements, and asks the model to judge which combination of those statements is
  sufficient to answer the question: statement 1 alone, statement 2 alone, either alone, both together,
  or neither. Unlike a typical exam question that hands the model exactly the information it needs, this
  task requires the model to first decide whether the information it has been given is enough at all --
  a skill the authors argue matters for real-world settings where relevant information is often
  incomplete or mixed with irrelevant detail, closer to a GMAT-style "data sufficiency" question than a
  standard reading-comprehension item.
task_format: >
  Five-option multiple choice, scored with BIG-bench's `multiple_choice_grade` metric; every one of the
  68 items uses the same five-way answer structure (64 items share one canonical wording, 4 substitute
  "the question can be answered without either statement" for the "neither is sufficient" option).
metric:
  name: multiple_choice_grade
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 20.0
  human_baseline: null
  baseline_note: >
    Every item offers exactly five options, so random guessing scores 20%. The task's own README reports
    baseline accuracies indistinguishable from that: GPT-2 at 23.5% (0-shot) and 25.0% (1-shot),
    OpenAI-GPT (GPT-1) at the same two figures, and GPT-2-Medium at 19.1% for both. No human baseline is
    published.
dataset:
  size: 68
  size_note: >
    68 items in total, confirmed directly from the task's own data file. All data and examples were
    created by the task's authors rather than drawn from an existing corpus, specifically so the
    questions are, in the authors' own words, "fictitious and cannot be simply looked up" -- the
    README's own Limitations section acknowledges this small size "may not be sufficient to obtain a
    precise evaluation."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/evaluating_information_essentiality"
  license: "Apache-2.0, inherited from the BIG-bench repository as a whole"
  languages:
    - en
  modalities:
    - text
  splits: "no train/test split in the original task; the harness's Hugging Face mirror additionally exposes train (52) and validation (16) pools for few-shot sampling, while the scored default split covers all 68 items"
  public_test_set: true
publisher:
  org: ""
  authors:
    - "Anantharaman S. Iyer"
    - "Niveditha S. Iyer"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/evaluating_information_essentiality"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/evaluating_information_essentiality"
released: "2021-07"
last_updated: ""
lineage:
  family: big_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The only reported scores this page found are the task's own 2021-era GPT-2/GPT-1/GPT-2-Medium
    baselines, all within a few points of the 20% chance rate. This task is not one of the 23 tasks
    carried into BIG-bench Hard (confirmed directly against the BIG-Bench-Hard repository's own task
    list), the BIG-bench descendant most commonly reported today, and its own 68-item size limits how
    precise any score on it can be, so a present-day saturation read is not established.
contamination:
  risk: low
  note: >
    The task's own design notes state plainly that "all data and examples in this task have been
    created by the authors" and are fictitious, specifically to avoid the item being answerable by
    lookup -- a stronger, source-confirmed mitigation than most benchmarks built from pre-existing
    exam or web material can claim. The exact 68 published items have themselves been public since
    mid-2021, so verbatim memorisation of this specific set is not impossible, but there was no
    pre-existing corpus for a model to have absorbed before that.
harness:
  lm_eval: "bigbench_evaluating_information_essentiality_multiple_choice (loads hails/bigbench, config evaluating_information_essentiality_zero_shot)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "evaluating_information_essentiality"
  other: ""
tags:
  - reasoning
  - multiple-choice
  - big-bench
  - logical-reasoning
  - data-sufficiency
  - subset
sources:
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/evaluating_information_essentiality/README.md"
    title: "BIG-bench evaluating_information_essentiality README (task description, authors, baseline table, design notes)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/evaluating_information_essentiality/task.json"
    title: "evaluating_information_essentiality task.json, downloaded and counted directly (68 examples; answer-option structure)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/google/BIG-bench/pulls/280"
    title: "GitHub PR #280, \"Added Information Essentiality Evaluation Task\" (merge date, 2021-07-15)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bigbench/multiple_choice/evaluating_information_essentiality.yaml"
    title: "lm-evaluation-harness bigbench multiple_choice evaluating_information_essentiality.yaml (exact runnable task name and dataset config)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hails/bigbench&config=evaluating_information_essentiality_zero_shot"
    title: "hails/bigbench evaluating_information_essentiality_zero_shot split sizes, Hugging Face datasets-server (default split: 68 rows)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

Part of the [BIG-bench](big_bench.md) family.

## What it measures

Evaluating Information Essentiality poses a question, sometimes with brief context, followed by two
supporting statements, and asks the model to judge which combination is sufficient to answer it:
statement 1 alone, statement 2 alone, either alone, both together, or neither -- a five-way structure
modelled on GMAT-style "data sufficiency" questions rather than a standard reading-comprehension format.
Unlike most QA tasks, which hand the model exactly the information it needs, this one requires the model
to first judge whether the information given is even enough, testing recognition of redundancy and
insufficiency rather than only retrieval or arithmetic. All 68 items were authored specifically for this
task -- fictitious scenarios the creators note "cannot be simply looked up" -- rather than adapted from
an existing dataset.

## Reading the numbers

At only 68 items, this task was never meant to produce a precise measurement, a limitation its own
authors acknowledge directly, and its 2021-era baselines (GPT-2, GPT-1 and GPT-2-Medium, all in the
19-25% range against a 20% chance rate) show no model tested at release could separate essential from
extraneous information reliably. No current-model score was found, and the task did not carry into
BIG-bench Hard, so treat any single reported number here as a coarse signal at best -- useful mainly
alongside other reasoning benchmarks, not as a precise standalone ranking.
