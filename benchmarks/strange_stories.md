---
id: strange_stories
name: "Strange Stories"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "theory of mind / social reasoning"
status: active
summary: "BIG-bench task built on a clinical theory-of-mind battery that asks a model to infer characters' beliefs, intentions and non-literal meaning from short narratives."
measures: "Strange Stories gives the model a short naturalistic narrative in which a character says something that is not literally true -- a lie, a joke, a white lie, sarcasm, a misunderstanding -- and asks a forced-choice question about a character's mental state or intent, such as why they said what they said. It adapts a clinical psychology battery originally used to test theory-of-mind (ToM) impairment in autism and other conditions, where ToM is the ability to infer others' unobservable beliefs, desires and intentions. The task targets social/emotional reasoning that typically develops in children from about age 4, rather than factual recall or symbolic manipulation."
task_format: "Zero-shot forced choice per item: multiple choice among several answer options (multiple_choice subtask) or a boolean true/false judgment (boolean subtask)."
metric:
  name: "multiple choice grade"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "BIG-bench's standard multiple_choice_grade metric scores the probability mass a model places on the correct option among the given choices; because the number of options varies per item and per subtask (boolean items are 2-way, multiple_choice items have more options), no single random-baseline percentage applies across the whole task. Neither subtask's task.json or README states a measured human baseline."
dataset:
  size: 174
  size_note: "174 multiple-choice queries total (0 free-text), split across two subtasks: 121 items in the multiple_choice subtask and 53 items in the boolean subtask (counts read directly from each subtask's task.json). The task README says it builds on Happe (1994) and White et al. (1998)'s original clinical items plus about 100 new question-answer pairs written by the task authors."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strange_stories"
  license: "Apache-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "single set, no train/test split (174 items across the boolean and multiple_choice subtasks)"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors: ["Yifu Chen", "Aitor Lewkowycz", "Francesca Happé"]
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strange_stories"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strange_stories"
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
  note: "The task's own README states that GPT-3 (zero-shot and few-shot) failed to show child-level performance at the time of authoring, but no source consulted here gives a recent, dated top score for current frontier models, so current saturation status is not established."
contamination:
  risk: high
  note: "The full item set, including the correct target scores, has been publicly hosted in the BIG-bench GitHub repository since 2022 despite a canary GUID string included specifically to let data curators filter it out of training corpora; whether that canary is honored by any given model's training pipeline is unknown."
harness:
  lm_eval: "bigbench_strange_stories_multiple_choice"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "strange_stories"
  other: ""
tags: ["theory of mind", "social reasoning", "narrative understanding", "big-bench-lite"]
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strange_stories"
    title: "strange_stories task directory, BIG-bench"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/strange_stories/README.md"
    title: "strange_stories README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/strange_stories/task.json"
    title: "strange_stories parent task.json"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/strange_stories/multiple_choice/task.json"
    title: "strange_stories multiple_choice subtask.json"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/strange_stories/boolean/task.json"
    title: "strange_stories boolean subtask.json"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game (BIG-bench paper)"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/blob/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bigbench/generate_tasks.py"
    title: "lm-evaluation-harness BIG-bench task generator"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

Strange Stories tests theory of mind: the capacity to infer a character's unobservable beliefs, desires, intentions and emotions from a short narrative. Each item presents a brief story in which someone says something that is not a literal, straightforward statement of fact -- a lie, a white lie, a joke, sarcasm, an excuse, a misunderstanding, a persuasion attempt -- and asks the model a question such as why the character said what they said, framed as a multiple-choice or boolean judgment.

The task adapts a clinical psychology battery originally built to diagnose theory-of-mind impairment (for example in autism), which the BIG-bench authors argue exercises a kind of social/emotional reasoning distinct from factual knowledge or symbolic manipulation, and which humans develop from roughly age 4 onward. It is text-only and in English.

## How it is scored

Both subtasks use BIG-bench's `multiple_choice_grade` metric, which scores the log-probability mass a model assigns to the correct option relative to the other listed options for that item, with the score aggregated across items as a percentage. The boolean subtask poses a binary (true/false) judgment per item; the multiple_choice subtask offers a longer list of answer options that include deliberately plausible-but-wrong distractors, some constructed to have high surface overlap with the question so that a model relying on pattern matching rather than inference is more likely to pick the trap answer. Evaluation is zero-shot; the task authors report that few-shot prompting did not improve GPT-3's performance at the time.

## Dataset and licence

The task has 174 items in total, split into two subtasks: 121 in `multiple_choice` and 53 in `boolean` (both counts verified directly from each subtask's `task.json`). The items combine the original clinical stimuli from Happé (1994) and White et al. (1998) with roughly 100 new question-answer pairs written by the task's authors, converting the original open-ended clinical interview format into forced choice for automated grading. There is a single set with no train/test split; all items and their correct answers are published in the BIG-bench repository under the Apache-2.0 licence, alongside a canary GUID string intended to flag the file for exclusion from model training corpora.

## Who publishes it

Strange Stories was contributed to BIG-bench by Yifu Chen, Aitor Lewkowycz and Francesca Happé (the original 1994 battery's author), and appears in the BIG-bench collaboration's 2022 paper "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models." It carries the `BIG-bench Lite` keyword, marking it as part of BIG-bench's smaller curated subset. There is no independent leaderboard beyond the auto-generated performance plots checked into the task's own `results/` directory.

## Lineage

The task has no confirmed predecessor or successor benchmark in this repository; it is one of several BIG-bench tasks targeting social/theory-of-mind reasoning (alongside tasks such as `social_iqa`-style benchmarks elsewhere), but no direct lineage relationship was verified from a primary source for this page.

## Saturation and contamination

The task's README states that GPT-3, in both zero-shot and few-shot settings, failed to reach child-level theory-of-mind performance at the time of writing, but that is a 2022-era observation, and no source reviewed here gives a dated, current top score for frontier models, so present-day saturation status is not established. Contamination risk is high: the full item set and correct answers have been openly hosted on GitHub since 2022, and while the task includes a canary string meant to let data curators exclude it from training sets, there is no way to confirm from these sources whether any given model's training data actually honored it.

## How to run it

The task runs through the standard BIG-bench JSON task interface as `strange_stories` (with `boolean` and `multiple_choice` as its two runnable subtasks). lm-evaluation-harness generates its BIG-bench wrappers programmatically from the `hails/bigbench` Hugging Face mirror, producing `bigbench_strange_stories_multiple_choice` (and a `bigbench_strange_stories_generate_until` variant) rather than a single unqualified task name. No inspect_evals, HELM or OpenCompass integration was confirmed from a primary source for this page. Because the two subtasks use different numbers of answer options, aggregate scores should be read alongside the boolean/multiple_choice breakdown rather than as one undifferentiated number.

## Reading the numbers

A high score suggests a model can track non-literal speech -- lies, sarcasm, jokes, white lies -- and infer why a character said it, which is a narrower and more specific capability than general reading comprehension. A low score does not necessarily mean a model lacks any social reasoning; the task's own design intentionally includes distractor options built to exploit surface pattern-matching, so failures can reflect susceptibility to that trap rather than an absence of theory-of-mind reasoning. Given the small item count (174) and public availability of the answers since 2022, single-digit score differences between models should not be over-interpreted, and scores from models released well after 2022 should be read with contamination in mind.
