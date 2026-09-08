---
id: glue_qqp
name: "GLUE: QQP (Quora Question Pairs)"
page_kind: subset
category: composite
subcategory: "duplicate question detection (sentence pair, English community Q&A)"
status: superseded
summary: "GLUE's largest task: judge whether two Quora questions ask the same thing, scored by the mean of accuracy and F1 because the classes are unbalanced."
measures: >
  Two English questions posted to the community question-and-answer site Quora, with a label for whether
  they are duplicates -- semantically asking the same thing -- or not. QQP is GLUE's largest task by far:
  hundreds of thousands of question pairs, versus low thousands for most of the rest of the suite. The
  classes are imbalanced (63% negative, per the GLUE paper), which is why, as with MRPC, GLUE scores QQP by
  the mean of accuracy and F1 rather than accuracy alone.
task_format: >
  Binary sentence-pair classification (duplicate / not duplicate), commonly cast by harnesses as a two-way
  multiple-choice or yes/no generation task. Scored by the mean of accuracy and F1.
metric:
  name: "mean of accuracy and F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    No single random baseline is stated by the paper; it reports roughly 63% of examples labelled "not
    duplicate." No task-specific human baseline is established here; see the glue family page.
dataset:
  size: 40430
  size_note: >
    40,430 validation rows (the split used for most published scoring), 363,846 train and 390,965 test
    rows -- QQP is GLUE's largest task by training-set size. The Hugging Face mirror's test-split labels
    are all -1 placeholders, so, unlike MRPC, only the validation split carries real labels for local
    evaluation.
  url: "https://huggingface.co/datasets/nyu-mll/glue"
  license: "Dataset card licence: other; see the glue family page for the composite-licence explanation."
  languages:
    - en
  modalities:
    - text
  splits: "train (363,846), validation (40,430), test (390,965, hidden labels)"
  public_test_set: false
publisher:
  org: "New York University"
  authors:
    - "Alex Wang"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://gluebenchmark.com/"
paper:
  title: "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding"
  arxiv: "1804.07461"
  url: "https://arxiv.org/abs/1804.07461"
  year: 2019
leaderboard_url: "https://gluebenchmark.com/leaderboard"
repo_url: "https://github.com/nyu-mll/GLUE-baselines"
released: "2018-04"
lineage:
  family: glue
harness:
  lm_eval: "qqp (tag: glue; dataset nyu-mll/glue, config qqp; scores acc and f1)"
  opencompass: "GLUE_QQP (its ppl config defines evaluation on both validation and test splits; since QQP's public test labels are hidden -1 placeholders, a 'QQP-test' score from that config cannot be meaningful -- only the validation-split score is)"
tags:
  - composite
  - classification
  - sentence-pair
  - duplicate-detection
  - glue-subset
  - superseded
sources:
  - url: "https://arxiv.org/abs/1804.07461"
    title: "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding (Wang et al., arXiv:1804.07461)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1804.07461"
    title: "GLUE, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/nyu-mll/glue"
    title: "nyu-mll/glue dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=nyu-mll/glue&config=qqp&split=test&offset=0&length=20"
    title: "nyu-mll/glue QQP test-split rows (confirming hidden -1 labels), Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/glue/qqp/default.yaml"
    title: "lm-evaluation-harness glue/qqp task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/GLUE_QQP/GLUE_QQP_ppl_250d00.py"
    title: "OpenCompass GLUE_QQP ppl config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [GLUE](glue.md) family.

## What it measures

Two English questions posted to the community question-and-answer site Quora, with a label for whether
they are duplicates -- semantically asking the same thing -- or not. QQP is GLUE's largest task by far:
hundreds of thousands of question pairs, versus low thousands for most of the rest of the suite. The
classes are imbalanced (63% negative, per the GLUE paper), which is why, as with MRPC, GLUE scores QQP by
the mean of accuracy and F1 rather than accuracy alone.

## Reading the numbers

A high QQP score shows a model can spot when two differently phrased questions want the same answer, a
skill closer to intent-matching in a search or support setting than to general reading comprehension. Its
sheer size relative to the rest of GLUE means QQP performance can dominate impressions of a fine-tuned
multi-task model's average even when the model is weaker on GLUE's smaller, harder tasks. Unlike MRPC,
QQP's official test-set labels are hidden, so any "QQP test accuracy" reported outside the official
leaderboard is either a validation-split number in practice or, if run through a harness config that
naively scores the dummy-labelled test split, not a real measurement at all. See the
[GLUE](glue.md) family page for the benchmark's saturation history and contamination notes, which apply
here too.
