---
id: glue_cola
name: "GLUE: CoLA (Corpus of Linguistic Acceptability)"
page_kind: subset
category: composite
subcategory: "linguistic acceptability judgement (single-sentence, English)"
status: superseded
summary: "GLUE's single-sentence task: judge whether an English sentence is grammatically acceptable, scored by Matthews correlation because the acceptable/unacceptable classes are unbalanced."
measures: >
  One English sentence, drawn from books and journal articles on linguistic theory, and one judgement: is
  it a grammatically acceptable sentence of English, or not. Unlike most of the rest of GLUE, this is a
  single-sentence task -- there is no second sentence to compare it against. About 70% of the training
  examples are labelled acceptable (6,023 of 8,551, per the Hugging Face datasets-server's own column
  statistics), unbalanced enough that raw accuracy would reward always guessing the majority class, which
  is why GLUE scores CoLA by Matthews correlation coefficient instead of accuracy.
task_format: >
  Binary single-sentence classification (acceptable / unacceptable), commonly cast by harnesses as a
  two-way multiple-choice or yes/no generation task. Scored by Matthews correlation coefficient (MCC), a
  -1-to-1 correlation measure, not by accuracy.
metric:
  name: "Matthews correlation coefficient (MCC)"
  direction: higher_is_better
  unit: "correlation, -1 to 1"
  max_score: 1
  random_baseline: 0
  baseline_note: >
    0 is the MCC value of an uninformed classifier (for example, one that always predicts the majority
    class); MCC ranges from -1 (total disagreement) to 1 (perfect prediction), unlike most of GLUE's other
    tasks, which report 0-100 accuracy or F1. No task-specific human baseline is established here; see the
    glue family page for the benchmark-wide diagnostic-set human baseline.
dataset:
  size: 1043
  size_note: >
    1,043 validation rows (the split used for most published scoring, since test labels are hidden), 8,551
    train rows (70.4% labelled acceptable, per Hugging Face datasets-server statistics) and 1,063 test
    rows. The Hugging Face mirror's test-split labels are all -1 placeholders, confirming CoLA's real test
    labels are not public.
  url: "https://huggingface.co/datasets/nyu-mll/glue"
  license: "Dataset card licence: other; see the glue family page for the composite-licence explanation."
  languages:
    - en
  modalities:
    - text
  splits: "train (8,551), validation (1,043), test (1,063, hidden labels)"
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
  lm_eval: "cola (tag: glue; dataset nyu-mll/glue, config cola; scored by mcc)"
  opencompass: "GLUE_CoLA (its ppl config scores plain accuracy, not Matthews correlation -- a real difference from the paper and from lm-evaluation-harness)"
tags:
  - composite
  - classification
  - single-sentence
  - mcc
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
  - url: "https://datasets-server.huggingface.co/statistics?dataset=nyu-mll/glue&config=cola&split=train"
    title: "nyu-mll/glue CoLA train-split column statistics, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=nyu-mll/glue&config=cola&split=test&offset=0&length=3"
    title: "nyu-mll/glue CoLA test-split rows (confirming hidden -1 labels), Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/glue/cola/default.yaml"
    title: "lm-evaluation-harness glue/cola task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/GLUE_CoLA/GLUE_CoLA_ppl_77d0df.py"
    title: "OpenCompass GLUE_CoLA ppl config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [GLUE](glue.md) family.

## What it measures

One English sentence, drawn from books and journal articles on linguistic theory, and one judgement: is it
a grammatically acceptable sentence of English, or not. Unlike most of the rest of GLUE, CoLA is a
single-sentence task -- there is no second sentence or passage to compare it against. About 70% of the
training examples are labelled acceptable (6,023 of 8,551), unbalanced enough that raw accuracy would
reward a model for always guessing the majority class, which is the paper's stated reason for scoring CoLA
by Matthews correlation coefficient instead.

## Reading the numbers

A high CoLA correlation shows a model can flag ungrammatical English reliably across the sentence types
this corpus draws on, which lean toward tricky, textbook-style edge cases rather than everyday prose -- it
does not necessarily predict grammaticality judgement on informal or non-English text. Remember the metric
is a correlation, not a percentage: a score of 0 is uninformative, not "half right," and a given point gap
means more near the ceiling than near 0. Because OpenCompass's CoLA configuration reports accuracy rather
than MCC, a "CoLA score" from that harness is not comparable to one computed the standard way -- check which
metric actually produced a number before comparing scores across sources. See the [GLUE](glue.md) family
page for the benchmark's saturation history and contamination notes, which apply here too.
