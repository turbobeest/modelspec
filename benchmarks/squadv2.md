---
id: squadv2
name: "SQuAD 2.0 (lm-evaluation-harness squadv2)"
aliases:
  - "SQuAD2"
page_kind: subset
category: reasoning
subcategory: "extractive reading comprehension with unanswerable questions, as implemented by lm-evaluation-harness's squadv2 task"
status: saturated
summary: >-
  lm-evaluation-harness's squadv2 task runs the SQuAD 2.0 validation set, scoring exact match and F1
  separately for answerable and unanswerable questions via the official squad_v2 metric.
measures: >
  This is the lm-evaluation-harness implementation of SQuAD 2.0 (task name `squadv2`): given a
  Wikipedia passage and a question, the model must generate the answer text found in the passage, or
  the harness estimates a "no answer" probability from loglikelihoods when the question is one of
  the adversarially written unanswerable questions that make up SQuAD 2.0's added difficulty over
  SQuAD 1.1. See [SQuAD](squad.md) for the full history and dataset detail shared by both SQuAD
  versions; this page documents the specific harness variant that model cards in this repository
  score under the id `squadv2`.
task_format: >
  lm-evaluation-harness loads the `lighteval/squad_v2` mirror's validation split and formats each
  item as "Title: {title}\n\nBackground: {context}\n\nQuestion: {question}\n\nAnswer:", generating a
  free-text answer; for unanswerable items it estimates a no_answer_probability from the model's
  loglikelihoods rather than requiring a literal refusal string.
metric:
  name: "Hugging Face evaluate 'squad_v2' metric: exact match and F1 overall, plus HasAns_exact/f1 (answerable-only), NoAns_exact/f1 (unanswerable-only) and best_exact/best_f1 (threshold-optimised) submetrics"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 89.452
  baseline_note: >
    Human baseline (86.831 EM / 89.452 F1) is the figure from the official SQuAD 2.0 leaderboard, as
    documented on the [SQuAD](squad.md) page; lm-evaluation-harness's own run does not separately
    publish a human baseline. Because squadv2 reports HasAns/NoAns/best submetrics alongside the
    overall EM/F1, a single headline number can obscure very different answerable-question and
    unanswerable-question performance.
dataset:
  size: 11873
  size_note: >
    lm-evaluation-harness's squadv2 task runs the `lighteval/squad_v2` mirror's validation split,
    which holds 11,873 question-answer pairs, matching the public SQuAD 2.0 dev split documented on
    [SQuAD](squad.md). The task config enables decontamination checks using the passage context as
    the query. Train is available in the mirror but is not used for zero/few-shot evaluation by this
    task.
  url: "https://huggingface.co/datasets/lighteval/squad_v2"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "lm-evaluation-harness squadv2 runs the SQuAD 2.0 validation split only (11,873 pairs); no test split exists"
  public_test_set: false
publisher:
  org: "Stanford University (original dataset); EleutherAI maintains this harness implementation"
  authors:
    - "Pranav Rajpurkar"
    - "Robin Jia"
    - "Percy Liang"
  url: "https://github.com/EleutherAI/lm-evaluation-harness"
paper:
  title: "Know What You Don't Know: Unanswerable Questions for SQuAD"
  arxiv: "1806.03822"
  url: "https://arxiv.org/abs/1806.03822"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/squadv2"
released: "2018-06"
last_updated: ""
lineage:
  family: "squad"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    lm-evaluation-harness does not run its own leaderboard for this task; saturation is inherited
    from the underlying SQuAD 2.0 dataset, whose official leaderboard has sat above human F1 since
    2019 (see [SQuAD](squad.md)). No harness-specific top score was found for this page.
contamination:
  risk: high
  note: >
    The SQuAD 2.0 validation data this task reads has been publicly downloadable since 2018 and is
    one of the most widely mirrored NLP evaluation files in existence; see [SQuAD](squad.md) for full
    discussion. The task config's decontamination flag suggests the harness's own maintainers treat
    this as a live contamination risk worth checking for.
harness:
  lm_eval: "squadv2"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reading-comprehension
  - question-answering
  - extractive-qa
  - saturated
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/squadv2/task.py"
    title: "lm-evaluation-harness squadv2/task.py source (task name squadv2, lighteval/squad_v2 mirror, prompt template, HasAns/NoAns/best submetrics, decontamination flag)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1806.03822"
    title: "Rajpurkar, Jia & Liang, 'Know What You Don't Know: Unanswerable Questions for SQuAD' (ACL 2018 abstract)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

Part of the [SQuAD](squad.md) family: this is the specific lm-evaluation-harness task (name
`squadv2`) that runs SQuAD 2.0's validation set, requiring a model to extract an answer from a
Wikipedia passage while a large share of questions have no supported answer at all. Unlike some
other harnesses' SQuAD 2.0 implementations, this task does not require a literal refusal string;
instead it estimates a no-answer probability from the model's own loglikelihoods. See
[SQuAD](squad.md) for the shared dataset history, licence and split details common to both SQuAD
versions.

## Reading the numbers

Because squadv2 reports separate HasAns (answerable-only), NoAns (unanswerable-only) and
threshold-optimised best_exact/best_f1 submetrics alongside overall EM/F1, a single headline number
can hide a model that is strong at extraction but poor at abstention, or vice versa -- check the
submetrics before comparing models on this task alone. Scores are not directly comparable to
OpenCompass's [squad20](squad20.md) task or other harnesses' SQuAD 2.0 implementations without
checking prompt wording and how each expects a "no answer" response, since squadv2's loglikelihood-based
abstention differs from a literal refusal string. As with the base [SQuAD](squad.md) benchmark, the
official leaderboard has sat above human F1 since 2019, so a high score here mainly confirms basic
extractive reading and abstention rather than differentiating capable modern models.
