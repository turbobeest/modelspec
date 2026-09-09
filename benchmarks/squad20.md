---
id: squad20
name: "SQuAD 2.0 (OpenCompass squad20)"
aliases:
  - "SQuAD2.0"
page_kind: subset
category: reasoning
subcategory: "extractive reading comprehension with unanswerable questions, as implemented by OpenCompass's squad20 config"
status: saturated
summary: >-
  OpenCompass's squad20 task runs the SQuAD 2.0 dev set, prompting a model to extract an answer span
  or say "impossible to answer" for adversarial unanswerable questions.
measures: >
  This is the OpenCompass harness implementation of SQuAD 2.0 (id `squad20`, config abbreviation
  `squad2.0`): given a Wikipedia passage and a question, the model must either return the answer
  text found in the passage or state that the question is impossible to answer, since over 50,000
  of SQuAD 2.0's questions are adversarially written to closely resemble answerable ones while
  having no supported answer in the passage. See [SQuAD](squad.md) for the full history and dataset
  detail shared by both SQuAD 1.1 and 2.0; this page documents the specific harness variant that
  model cards in this repository score under the id `squad20`.
task_format: >
  OpenCompass reads `dev-v2.0.json` locally and prompts: "According to the above passage, answer the
  following question. If it is impossible to answer according to the passage, answer 'impossible to
  answer'", followed by the question, with generation capped at 50 tokens.
metric:
  name: "SQuAD20Evaluator (Exact Match / F1 against reference answers, with a literal 'impossible to answer' string scored against unanswerable questions)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 89.452
  baseline_note: >
    Human baseline (86.831 EM / 89.452 F1) is the figure from the official SQuAD 2.0 leaderboard, as
    documented on the [SQuAD](squad.md) page; OpenCompass's own run does not separately publish a
    human baseline.
dataset:
  size: 11873
  size_note: >
    OpenCompass's squad20 config reads the public SQuAD 2.0 development split (dev-v2.0.json), which
    holds 11,873 question-answer pairs per the dataset's own published split metadata (see
    [SQuAD](squad.md) for the full train/dev breakdown of both SQuAD versions). OpenCompass evaluates
    only against this dev split, not the officially held-out hidden test set.
  url: "https://huggingface.co/datasets/rajpurkar/squad_v2"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass squad20 runs the SQuAD 2.0 development split only (11,873 pairs); train is not used by this harness config"
  public_test_set: false
publisher:
  org: "Stanford University (original dataset); OpenCompass (open-compass) maintains this harness implementation"
  authors:
    - "Pranav Rajpurkar"
    - "Robin Jia"
    - "Percy Liang"
  url: "https://github.com/open-compass/opencompass"
paper:
  title: "Know What You Don't Know: Unanswerable Questions for SQuAD"
  arxiv: "1806.03822"
  url: "https://arxiv.org/abs/1806.03822"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/squad20"
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
    OpenCompass does not run its own leaderboard for this config; saturation is inherited from the
    underlying SQuAD 2.0 dataset, whose official leaderboard has sat above human F1 since 2019 (see
    [SQuAD](squad.md)). No OpenCompass-specific top score was found for this page.
contamination:
  risk: high
  note: >
    The dev-v2.0.json file this config reads has been publicly downloadable since 2018 and is one of
    the most widely mirrored NLP evaluation files in existence; see [SQuAD](squad.md) for full
    discussion.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "squad2.0"
  bigbench: ""
  other: ""
tags:
  - reading-comprehension
  - question-answering
  - extractive-qa
  - saturated
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/squad20/squad20_gen_1710bc.py"
    title: "OpenCompass squad20_gen_1710bc.py config (dataset abbr squad2.0, prompt wording, SQuAD20Evaluator, dev-v2.0.json source)"
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

Part of the [SQuAD](squad.md) family: this is the specific OpenCompass task (id `squad20`, config
abbreviation `squad2.0`) that runs SQuAD 2.0's development set, requiring a model to either extract
an answer span from a Wikipedia passage or declare a question impossible to answer, since a large
share of SQuAD 2.0's questions are adversarially written to have no supported answer. See
[SQuAD](squad.md) for the shared dataset history, licence and split details common to both SQuAD
versions.

## Reading the numbers

OpenCompass prompts with an explicit "answer 'impossible to answer'" instruction, a different literal
refusal string than other harnesses use for the same underlying dataset (see [SQuAD](squad.md)'s How
to run it section for the comparison with inspect_evals and lm-evaluation-harness), so a squad20
score is not directly comparable to a score reported under a different harness's SQuAD 2.0 task
without checking the refusal wording and generation length cap (50 tokens here). Because the official
SQuAD 2.0 leaderboard has sat above human F1 since 2019, a high squad20 score mainly confirms basic
extractive reading and abstention over short, clean passages rather than differentiating capable
models, and elevated performance is at least as plausibly explained by the dataset's age and
ubiquity in training data as by genuine reading comprehension.
