---
id: sports_understanding
name: "Sports Understanding"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "commonsense plausibility judgement about sports actions and athletes"
status: active
summary: >-
  A BIG-bench task that asks a model to judge whether a made-up sentence pairing an athlete with a
  sport-specific action is plausible or implausible.
measures: >
  Sports Understanding presents a short statement combining a real athlete's name with a
  sport-specific action (and sometimes a competition), such as an athlete "threw a touchdown" or
  "scored a goal," and asks the model to classify the statement as plausible or implausible. Getting
  it right requires knowing which sport a given athlete plays and which actions are appropriate to
  that sport, i.e. domain-specific commonsense and sports knowledge rather than general reasoning.
task_format: >
  Zero-shot binary multiple-choice classification: the model picks "plausible" or "implausible" for
  each of 986 combinatorially generated statements pairing an athlete with an action drawn from four
  major North American sports plus soccer, with some pairings sport-appropriate and others
  deliberately mismatched.
metric:
  name: "Multiple choice grade (accuracy on the plausible/implausible binary choice)"
  direction: higher_is_better
  unit: "accuracy"
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: null
  baseline_note: >
    The task is a balanced binary choice, so chance performance is 0.5. No human baseline figure is
    given in the source read for this page.
dataset:
  size: 986
  size_note: >
    986 multiple-choice queries, confirmed from the task's own README and task.json in the
    BIG-bench repository, generated combinatorially by pairing athletes from four major North
    American sports plus soccer with sport-appropriate or deliberately mismatched actions.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sports_understanding"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Single BIG-bench task file of 986 examples; no separate train/validation/test split is defined by the task itself"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); task author Ethan Kim"
  authors:
    - "Ethan Kim"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sports_understanding"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sports_understanding"
released: "2021"
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
  note: >
    No maintained standalone leaderboard for this task was found for this page. It is included as
    one of the 23 tasks in BIG-bench Hard (BBH), a subset selected because the original BIG-bench
    paper found no prior language model beat average human rater performance on it, which implies
    it was not saturated at BIG-bench's original 2022 evaluation; whether current frontier models
    have since saturated it is not established from a source read for this page.
contamination:
  risk: medium
  note: >
    The 986-example task file has been publicly downloadable in the BIG-bench GitHub repository
    since 2021 and is additionally redistributed as part of BIG-bench Hard, a widely used
    fine-tuning and evaluation subset, increasing the chance the exact items appear in training
    corpora relative to a less-reused BIG-bench task. The README does carry a canary GUID intended
    to let maintainers exclude the task from future training corpora, but that convention only
    protects against crawlers that honour it, so exposure in general web-scale training data cannot
    be ruled out.
harness:
  lm_eval: "bbh_zeroshot_sports_understanding"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "sports_understanding"
  other: >
    Also ships as `sports_understanding.json` among the 23 tasks in BIG-bench Hard (BBH).
    lm-evaluation-harness carries several BBH variants for it (zero-shot, few-shot, and
    chain-of-thought versions of each) under its `bbh` task group; the confirmed zero-shot task name
    is `bbh_zeroshot_sports_understanding`. Scores reported under different variant names are not
    directly comparable without checking shot count and whether chain-of-thought was used.
tags:
  - commonsense
  - sports
  - classification
  - big-bench
  - bbh
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sports_understanding"
    title: "BIG-bench sports_understanding task directory (README: task description, 986 examples, multiple_choice_grade metric, author, keywords)"
    accessed: "2026-09-08"
  - url: "https://github.com/suzgunmirac/BIG-Bench-Hard/tree/main/bbh"
    title: "BIG-Bench-Hard repository bbh/ directory listing confirming sports_understanding.json is one of the 23 BBH tasks"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bbh/zeroshot/sports_understanding.yaml"
    title: "lm-evaluation-harness BBH zero-shot sports_understanding.yaml (task name bbh_zeroshot_sports_understanding, prompt template, answer extraction)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

Sports Understanding gives a model a short statement pairing a real athlete with a sport-specific
action, for example an athlete described as throwing a touchdown or scoring a goal, and asks whether
the statement is plausible or implausible. Answering correctly needs domain knowledge of which sport
a given athlete plays and which actions belong to that sport, so the task exercises a narrow,
factual form of commonsense (sports trivia plus action-sport matching) rather than general reasoning.

## How it is scored

The task is a balanced binary multiple-choice classification, scored with BIG-bench's
multiple_choice_grade metric (accuracy on the plausible/implausible choice); chance performance is
0.5 since the two options are roughly balanced by construction. No human baseline figure was found
in the sources read for this page.

## Dataset and licence

The task holds 986 multiple-choice examples, generated combinatorially by pairing athletes from four
major North American sports (the exact sports are not itemised beyond "four major North American
sports" plus soccer) with actions that are either appropriate to that athlete's sport or deliberately
mismatched, producing plausible and implausible statements respectively. No explicit licence is
stated for the task's word/name lists in the BIG-bench directory itself.

## Who publishes it

The task was contributed to BIG-bench by Ethan Kim as part of the broader, multi-author BIG-bench
collaboration coordinated by Google researchers. No separate standalone paper describing this task
in isolation was found; it is documented in the task's own README and task.json, and separately
described in the BIG-bench Hard paper as one of the tasks selected for that harder subset.

## Lineage

Sports Understanding is one of several hundred independent BIG-bench tasks. It was later selected as
one of the 23 tasks that make up BIG-bench Hard (BBH), a subset chosen because prior language models
had not exceeded average human rater performance on it in the original BIG-bench evaluation; BBH
does not have its own page in this repository yet. The task has no predecessor or successor tracked
here.

## Saturation and contamination

No maintained standalone leaderboard for this task was found. Its inclusion in BIG-bench Hard signals
that, as of BIG-bench's original evaluation, no model tested had beaten average human performance on
it, but whether current frontier models have since closed or exceeded that gap is not established
from a source read for this page, so saturation status is marked "watch" rather than confirmed
saturated or open. Contamination risk is medium: the task has been public since 2021 and is further
amplified by its reuse inside the widely adopted BIG-bench Hard subset; its README carries a canary
GUID, but that convention only protects against crawlers that honour it.

## How to run it

Run as the `sports_understanding` task in the BIG-bench repository
(`bigbench/benchmark_tasks/sports_understanding`), or via BIG-bench Hard's
`sports_understanding.json`. lm-evaluation-harness implements several BBH variants of it under its
`bbh` task group (zero-shot, few-shot and chain-of-thought forms); the confirmed zero-shot task name
is `bbh_zeroshot_sports_understanding`, which prompts with a plain "Q: ... A:" template and extracts
a yes/plausible or no/implausible answer via regex. Scores from the two source repositories, and
across BBH's own variant task names, are not directly comparable without checking shot count and
prompt format.

## Reading the numbers

A high score shows a model has reliable, largely memorisable sports trivia (which athlete plays
which sport) combined with correct sport-action matching, not deeper reasoning. Because the task
was originally chosen for BIG-bench Hard on the grounds that models had not yet beaten human raters
on it, a score well above 0.5 on a modern model is a meaningful signal of progress rather than a
saturated, uninformative result, but the exact current gap to human performance and the risk that
frontier models have seen the fixed item set during training are both not established here.
