---
id: logiqa
name: LogiQA
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "logical reasoning reading comprehension, from Chinese civil-service exam questions"
status: active
summary: "LogiQA scores multiple-choice logical reasoning questions taken from China's National Civil Servants Examination, translated into English by professional translators."
measures: >
  LogiQA tests deductive logical reasoning through reading comprehension: the model is given a short
  passage and a question, then must pick the correct one of four candidate answers. Questions come from
  "publically available questions of the National Civil Servants Examination of China," a real exam
  designed to test critical thinking rather than recall, and were not written for the benchmark. The paper
  organises items into five overlapping categories of deductive reasoning -- categorical, sufficient
  conditional, necessary conditional, disjunctive and conjunctive reasoning -- though a single question can
  draw on more than one category at once.
task_format: >
  Four-option multiple-choice reading comprehension: a short context passage, a question about it, and four
  answer candidates, with the model returning a single choice. The dataset was released in both its
  original Chinese and a professionally produced English translation (five translators, three proofreaders),
  so the same questions can be evaluated in either language.
metric:
  name: "accuracy (and length-normalized accuracy, acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 86
  baseline_note: >
    The paper reports a human-annotator average of 86% accuracy and a "ceiling" figure of 95-96% (counting
    a question correct if any one of three annotators answered it correctly), against a 25% random baseline
    for the four-option format.
dataset:
  size: 8678
  size_note: >
    8,678 question instances, split 7,376 train / 651 validation / 651 test per the source GitHub
    repository's README (the paper itself describes this as an approximate 80/10/10 split). Both a Chinese
    and an English-translation version are released, each with the same split sizes.
  url: "https://github.com/lgw863/LogiQA-dataset"
  license: >
    Not stated by the paper or by the original GitHub repository, which carries no LICENSE file; the
    authors describe the dataset only as "freely available." The EleutherAI/logiqa Hugging Face mirror used
    by lm-evaluation-harness lists its own licence tag as "other" without further detail.
  languages: ["zh", "en"]
  modalities: ["text"]
  splits: "7,376 train / 651 validation / 651 test"
  public_test_set: true
publisher:
  org: "Fudan University and Westlake University"
  authors: ["Jian Liu", "Leyang Cui", "Hanmeng Liu", "Dandan Huang", "Yile Wang", "Yue Zhang"]
  url: "https://github.com/lgw863/LogiQA-dataset"
paper:
  title: "LogiQA: A Challenge Dataset for Machine Reading Comprehension with Logical Reasoning"
  arxiv: "2007.08124"
  url: "https://arxiv.org/abs/2007.08124"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/lgw863/LogiQA-dataset"
released: "2020-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 35.31
  as_of: "2020-07"
  note: >
    At release, the best baseline the authors tested, RoBERTa, reached only 35.31% test accuracy, well
    below the 86% human-annotator average and the 95-96% ceiling figure -- a large machine/human gap at the
    time. No current leaderboard or recent (2025- or 2026-era) model score was found during this research
    pass, and this repository's own model cards do not carry a logiqa score either, so present-day standing
    is not established here; given how far general reading-comprehension multiple-choice performance has
    advanced since 2020, current scores are plausibly much closer to, at, or above the human figures quoted
    above, but that is this page's inference, not a sourced reading.
contamination:
  risk: high
  note: >
    The question set, including test-split answers, has been publicly downloadable without gating since
    2020, giving it roughly six years of exposure to web crawls and model training corpora by this research
    date (2026-09-08). The lm-evaluation-harness task config sets `should_decontaminate: true` and defines
    a decontamination query over each item's context passage, marking it as text its maintainers consider
    worth checking against training corpora.
harness:
  lm_eval: "logiqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness registers the task as `logiqa`, reading the EleutherAI/logiqa mirror and scoring
    `acc` and `acc_norm` over the English-language multiple-choice format. Its task config sets no few-shot
    count, so it runs zero-shot by default. Not confirmed in the HELM, OpenCompass or BIG-bench task lists.
tags: ["logical-reasoning", "reading-comprehension", "multiple-choice", "chinese", "civil-service-exam"]
sources:
  - url: "https://arxiv.org/abs/2007.08124"
    title: "LogiQA: A Challenge Dataset for Machine Reading Comprehension with Logical Reasoning"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2007.08124"
    title: "LogiQA, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/lgw863/LogiQA-dataset"
    title: "lgw863/LogiQA-dataset repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/lgw863/LogiQA-dataset/master/README.md"
    title: "lgw863/LogiQA-dataset: README.md"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/logiqa/logiqa.yaml"
    title: "lm-evaluation-harness: logiqa task config"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/logiqa"
    title: "EleutherAI/logiqa dataset card API, Hugging Face"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LogiQA tests deductive logical reasoning through reading comprehension: the model is given a short context
passage and a question about it, then must pick the correct one of four candidate answers. Questions come
from real, publicly available items from China's National Civil Servants Examination, a competitive exam
designed to test candidates' critical thinking and problem-solving rather than recall, and were not written
for the benchmark. The paper tags items by five (sometimes overlapping) categories of deductive reasoning:
categorical reasoning, sufficient conditional reasoning ("if P then Q"), necessary conditional reasoning
("P only if Q"), disjunctive reasoning ("either... or...") and conjunctive reasoning ("both... and...").

The dataset was released in both its original Chinese and a professionally produced English translation --
five professional translators worked on it, with three additional proofreaders -- so the same underlying
questions can be evaluated in either language.

## How it is scored

Models are graded on accuracy: the share of four-option questions answered correctly, giving a 25% random
baseline. lm-evaluation-harness additionally reports `acc_norm`, a length-normalized accuracy variant
common for multiple-choice tasks whose answer options vary in token length, and runs the task zero-shot by
default. The paper itself reports a human-annotator average of 86% and notes that treating a question as
correct if any one of three annotators got it right raises that figure to a 95-96% "ceiling," giving a
frame of reference well above what its own baseline models reached.

## Dataset and licence

8,678 question instances, split 7,376 train / 651 validation / 651 test in both the Chinese original and
the English translation. Neither the paper nor the authors' GitHub repository states a formal licence; the
repository carries no LICENSE file, and the authors describe the data only as "freely available." The
EleutherAI/logiqa Hugging Face mirror that lm-evaluation-harness reads separately tags its own licence as
"other," without elaborating. Test-split answers are included in the public files in the same format as
every other split, so there is no gating.

## Who publishes it

LogiQA was introduced by Jian Liu (Fudan University) together with Leyang Cui, Hanmeng Liu, Dandan Huang,
Yile Wang and Yue Zhang (Westlake University and the Westlake Institute for Advanced Study), and accepted at
IJCAI 2020. The authors maintain the reference data at github.com/lgw863/LogiQA-dataset; the
EleutherAI/logiqa Hugging Face mirror used by lm-evaluation-harness is maintained by that separate project.

## Lineage

LogiQA has no predecessor catalogued in this repository. A separate, larger dataset from an overlapping
author team, LogiQA 2.0 (hosted at github.com/csitfun/LogiQA2.0), was published later as an improved logical
reasoning resource; it is a distinct dataset with its own release and is not catalogued in this repository,
so a score reported simply as "LogiQA" should specify which version it used -- this page's id and figures
cover only the original 2020 dataset (LogiQA v1).

## Saturation and contamination

At release, the strongest baseline the authors tested, RoBERTa, reached only 35.31% test accuracy against
an 86% human-annotator average and a 95-96% ceiling figure, a wide machine/human gap at the time. No current
leaderboard or recent model score was found during this research pass, and no model card in this repository
carries a logiqa score, so present-day standing cannot be established here; given how far general
multiple-choice reading-comprehension performance has advanced industry-wide since 2020, current scores are
plausibly much closer to, at, or above the human figures quoted above, though that is this page's inference
rather than a sourced reading. Contamination risk is high: the question set, including test-split answers,
has been public without gating since 2020, roughly six years by this research date, and the
lm-evaluation-harness task config itself sets `should_decontaminate: true`, flagging LogiQA's text as
something its maintainers consider worth checking against training corpora.

## How to run it

lm-evaluation-harness registers the task as `logiqa`, reading the EleutherAI/logiqa mirror and reporting
`acc` and `acc_norm` zero-shot over the English-language version, with no few-shot count set in its task
config. It was not confirmed in the HELM, OpenCompass or BIG-bench task lists during this research pass, so
a score attributed to one of those suites should not be assumed without checking a specific implementation.
Because the dataset ships in both Chinese and English, always check which language version a reported score
used.

## Reading the numbers

A high LogiQA score shows a model can apply categorical, conditional, disjunctive and conjunctive deductive
reasoning to short passages in the style of a real civil-service exam, not necessarily broader logical or
mathematical reasoning in other formats. Given the large reported human/model gap at the benchmark's 2020
release, and the absence of any confirmed recent score in this research pass, treat any current LogiQA
number with real caution about training-data exposure, since the dataset has been fully public with answers
for roughly six years. Always check whether a reported score used the original 2020 dataset (this page) or
the separate, larger LogiQA 2.0 release, since the two are not the same benchmark and are not directly
comparable.
