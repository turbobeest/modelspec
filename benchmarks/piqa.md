---
id: piqa
name: PIQA
aliases:
  - Physical Interaction QA
  - Physical IQA
page_kind: benchmark
category: reasoning
subcategory: physical commonsense reasoning
status: active
summary: >-
  Binary-choice physical commonsense reasoning built from instructables.com how-to text; a 2019
  benchmark now close to its human baseline for most current models.
measures: >
  PIQA tests physical commonsense reasoning: given a goal stated in a short sentence, such as how to make
  a hole in a piece of wood, and two candidate solutions, a model must pick the more physically sensible
  one. The dataset was built from instructables.com, a site of how-to instructions for building, cooking
  and everyday physical tasks, so the knowledge required concerns how everyday materials and actions
  behave in the physical world rather than facts a model could simply recite. Solutions were engineered
  to require choosing between a typical, correct-seeming approach and an atypical or physically
  implausible one, rather than between an obviously right and an obviously wrong answer.
task_format: >
  Given a goal sentence and two candidate solutions, the model selects the more physically appropriate
  solution; exactly one of the two is correct.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 94.9
  baseline_note: >
    94.9% human accuracy is a majority vote among annotators who scored at least 90% on a qualification
    task, as reported in the original paper; the authors treat it as a soft ceiling rather than a formal
    maximum.
dataset:
  size: 21000
  size_note: >
    16,000 training, 2,000 validation and 3,000 test examples, per the dataset card. Official test-set
    labels are not public: the project's leaderboard works by emailing predictions to the maintainer
    rather than by public scoring, so most published results, including lm-evaluation-harness's own task,
    evaluate against the 2,000-example validation split rather than the true held-out test set.
  url: https://huggingface.co/datasets/ybisk/piqa
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "16,000 train / 2,000 validation / 3,000 test; test labels are not public"
  public_test_set: false
publisher:
  org: ""
  authors:
    - Yonatan Bisk
    - Rowan Zellers
    - Ronan Le Bras
    - Jianfeng Gao
    - Yejin Choi
  url: https://yonatanbisk.com/piqa/
paper:
  title: "PIQA: Reasoning about Physical Commonsense in Natural Language"
  arxiv: "1911.11641"
  url: https://arxiv.org/abs/1911.11641
  year: 2019
leaderboard_url: https://yonatanbisk.com/piqa/
repo_url: ""
released: "2019-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No current top score from a frontier-lab announcement was found in this research; PIQA appears mainly
    as one line in broad evaluation-harness sweeps rather than as a headline result today, so no specific
    top_score is recorded. It is nonetheless read as saturated: the paper's own 94.9% human baseline is a
    soft ceiling that general-purpose LLMs now routinely approach on the public validation split, leaving
    little room to separate strong current models from each other.
contamination:
  risk: high
  note: >
    Training and validation data have been fully public since 2019 and are effectively guaranteed to
    appear in large web-scraped pretraining corpora by now. The one real protection the design offers —
    withheld test-set labels — depends on an email-submission leaderboard that has seen little active use
    in recent years, so the validation split nearly everyone actually evaluates against should be assumed
    in-distribution for most current models' training data.
harness:
  lm_eval: piqa
  inspect_evals: piqa
  helm: ""
  opencompass: piqa
  bigbench: ""
  other: >
    lm-evaluation-harness's piqa task loads from a re-hosted parquet mirror (dataset path baber/piqa)
    rather than the original ybisk/piqa repository, likely because the original dataset ships a custom
    loading script that current versions of the datasets library will not run without explicitly trusting
    remote code. It evaluates the validation split (not the withheld test split) and reports both acc and
    acc_norm (length-normalised accuracy). No BIG-bench or HELM implementation was confirmed.
tags:
  - commonsense
  - physical-reasoning
  - binary-choice
  - classic-nlp
sources:
  - url: https://arxiv.org/abs/1911.11641
    title: "PIQA: Reasoning about Physical Commonsense in Natural Language"
    accessed: "2026-09-08"
  - url: https://yonatanbisk.com/piqa/
    title: "Official PIQA project page (licence, leaderboard submission process, venue)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ybisk/piqa
    title: "ybisk/piqa dataset card (description, splits, licence: unknown)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/piqa/piqa.yaml
    title: "lm-evaluation-harness piqa.yaml (dataset_path baber/piqa, validation split, acc/acc_norm)"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/piqa
    title: "inspect_evals piqa task"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/piqa
    title: "OpenCompass piqa dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PIQA tests physical commonsense reasoning: given a goal stated in a short sentence, such as how to make a
hole in a piece of wood, and two candidate solutions, a model must pick the more physically sensible one.
The dataset was built from instructables.com, a site of how-to instructions for building, cooking and
everyday physical tasks, so the knowledge required concerns how everyday materials and actions behave in
the physical world rather than facts a model could simply recite. Solutions were engineered to require
choosing between a typical, correct-seeming approach and an atypical or physically implausible one, not
between an obviously right and an obviously wrong answer.

## How it is scored

Models choose between exactly two candidate solutions per goal, so random guessing scores 50%.
lm-evaluation-harness reports both raw accuracy ("acc") and length-normalised accuracy ("acc_norm",
correcting for a model's tendency to prefer longer or shorter completions regardless of content). Human
performance is reported at 94.9%, measured by majority vote among annotators who scored at least 90% on a
qualification task, which the original paper treats as a soft ceiling. The dataset was filtered with
AFLite, an adversarial-filtering algorithm that uses an ensemble of lightweight classifiers on
precomputed embeddings to remove examples a superficial pattern-matcher could already solve, specifically
to reduce annotation artifacts.

## Dataset and licence

PIQA holds 16,000 training, 2,000 validation and 3,000 test examples. Test-set labels are not public: the
original project's leaderboard works by emailing predictions to the maintainer for scoring rather than by
public release, so most published results — including lm-evaluation-harness's own task — evaluate against
the 2,000-example validation split rather than the true held-out test set. Licensing is stated two
different ways in the sources checked for this page: the Hugging Face dataset card (ybisk/piqa) lists the
licence as "unknown," while the original project site (yonatanbisk.com/piqa) states the Academic Free
License ("AFL") v3.0. Both readings are recorded here rather than picking one. English only, text only.

## Who publishes it

PIQA was introduced by Yonatan Bisk, Rowan Zellers and Ronan Le Bras (University of Washington / Allen
Institute for AI), Jianfeng Gao (Microsoft Research AI) and Yejin Choi (University of Washington / Allen
Institute for AI), posted to arXiv in November 2019 and published at AAAI 2020. The authors continue to
host the dataset and leaderboard at yonatanbisk.com/piqa; the Hugging Face mirror (ybisk/piqa) is the copy
most current evaluation harnesses actually load from (directly or via a re-hosted parquet mirror).

## Lineage

PIQA names no formal predecessor. It shares authorship and the AFLite adversarial-filtering methodology
with several sibling commonsense-reasoning benchmarks from the same research community, including
HellaSwag (`hellaswag`) and CommonsenseQA (`commonsense_qa`), both of which have their own pages in this
repository. None of the three is a strict predecessor or successor of another — they read as a family of
same-era, same-method commonsense benchmarks covering different domains (physical actions, event
continuation, and general commonsense QA respectively) rather than as a single lineage. PIQA has no
official successor.

## Saturation and contamination

PIQA is effectively saturated for current frontier models: the paper's own 94.9% human baseline is a soft
ceiling that 2019-era models already approached on easier items, and general-purpose LLMs now routinely
score in the low-to-mid 90s on the public validation split, leaving little room to separate strong models
from each other. No current top score from a frontier-lab announcement was found in this research — PIQA
appears mainly as one line inside broad evaluation-harness sweeps rather than as a headline result — so no
specific current top score is recorded here. Contamination risk is high: the training and validation data
have been fully public since 2019 and are effectively guaranteed to appear in large web-scraped
pretraining corpora by now, and the one real protection the design offers — withheld test labels — depends
on an email-submission leaderboard that has seen little active use in recent years.

## How to run it

lm-evaluation-harness registers the task as `piqa`, evaluating the validation split and reporting both
`acc` and `acc_norm`; it loads from a re-hosted parquet mirror (`baber/piqa`) rather than the original
`ybisk/piqa` repository, likely because the original dataset ships a custom loading script that current
versions of the `datasets` library will not run without explicitly trusting remote code. inspect_evals
registers the same task as `inspect_evals/piqa`. OpenCompass configures it under a `piqa` dataset folder.
No BIG-bench or HELM implementation was confirmed in this research.

## Reading the numbers

A high PIQA score today mostly confirms a model has assimilated widely available physical-commonsense
text, rather than that it reasons live about physical properties, since the validation split nearly
everyone reports against has been public for years and the benchmark sits close to its human baseline for
most current models. PIQA is more useful now as a floor check for smaller or specialised models, where
scores still vary meaningfully, than as a way to separate frontier models from each other. Because
different harnesses may report raw or length-normalised accuracy, and because "PIQA" almost always means
the public validation split rather than the withheld test set, confirm both before comparing two reported
numbers.
