---
id: glue_mrpc
name: "GLUE: MRPC (Microsoft Research Paraphrase Corpus)"
page_kind: subset
category: composite
subcategory: "paraphrase detection (sentence pair, English news)"
status: superseded
summary: "GLUE's paraphrase task: judge whether two English news sentences mean the same thing, scored by the mean of accuracy and F1 because the classes are unbalanced."
measures: >
  Two English sentences, automatically pulled from online news sources, with a human annotation for
  whether they are semantically equivalent -- a paraphrase judgement, not a similarity score. The task is
  binary sentence-pair classification: given both sentences, decide equivalent or not. The classes are
  imbalanced (68% positive, per the GLUE paper), which is why GLUE scores MRPC by the mean of accuracy and
  F1 rather than accuracy alone.
task_format: >
  Binary sentence-pair classification (equivalent / not equivalent), commonly cast by harnesses as a
  two-way multiple-choice or yes/no generation task. Scored by the mean of accuracy and F1.
metric:
  name: "mean of accuracy and F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    No single random baseline is stated by the paper; with roughly 68% of examples labelled "equivalent,"
    always predicting the majority class scores well on accuracy alone, which is part of why F1 is averaged
    in alongside it. No task-specific human baseline is established here; see the glue family page.
dataset:
  size: 408
  size_note: >
    408 validation rows (the split used for most published scoring), 3,668 train and 1,725 test rows.
    Unlike most other GLUE tasks, MRPC's Hugging Face test-split labels are real, publicly disclosed labels
    rather than -1 placeholders: the corpus already had a public test set (Dolan and Brockett, 2005) before
    GLUE adopted it, so GLUE did not need to hide it.
  url: "https://huggingface.co/datasets/nyu-mll/glue"
  license: "Dataset card licence: other; see the glue family page for the composite-licence explanation."
  languages:
    - en
  modalities:
    - text
  splits: "train (3,668), validation (408), test (1,725, publicly labelled)"
  public_test_set: true
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
  lm_eval: "mrpc (tag: glue; dataset nyu-mll/glue, config mrpc; scores acc and f1)"
  opencompass: "GLUE_MRPC (evaluates both validation and test splits, unlike GLUE_QQP, since MRPC's test labels are genuinely public)"
tags:
  - composite
  - classification
  - sentence-pair
  - paraphrase
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
  - url: "https://datasets-server.huggingface.co/rows?dataset=nyu-mll/glue&config=mrpc&split=test&offset=0&length=20"
    title: "nyu-mll/glue MRPC test-split rows (confirming public, non-dummy labels), Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/glue/mrpc/default.yaml"
    title: "lm-evaluation-harness glue/mrpc task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/GLUE_MRPC/GLUE_MRPC_ppl_96564c.py"
    title: "OpenCompass GLUE_MRPC ppl config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [GLUE](glue.md) family.

## What it measures

Two English sentences, automatically pulled from online news sources, with a human annotation for whether
they are semantically equivalent -- a paraphrase judgement, not a similarity score like STS-B. The task is
binary sentence-pair classification: given both sentences, decide equivalent or not equivalent. The classes
are imbalanced (68% positive, per the GLUE paper), which is why GLUE scores MRPC by the mean of accuracy
and F1 rather than accuracy alone.

## Reading the numbers

A high MRPC score shows a model can recognise when two differently worded English news sentences describe
the same fact, a narrower skill than general similarity judgement and specific to short, formal news
prose. Because the score averages accuracy and F1, a model can lift its number by improving either the
overall hit rate or its balance between false positives and false negatives -- the two components are
worth checking separately if a score looks unusual. MRPC is unusual among GLUE tasks in that its official
test-set labels are public, so, unlike CoLA or QQP, a "test accuracy" figure reported here can actually be
verified against real labels rather than being a validation-split number in disguise. See the
[GLUE](glue.md) family page for the benchmark's saturation history and contamination notes, which apply
here too.
