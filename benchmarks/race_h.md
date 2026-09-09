---
id: race_h
name: "RACE-H (inspect_evals)"
aliases:
  - "RACE-H"
  - "race-high"
page_kind: subset
category: reasoning
subcategory: "inspect_evals generation wrap of RACE high-school English-exam reading comprehension"
status: active
summary: "inspect_evals task for RACE-H: pick one of four answers to a high-school English-exam question about a passage."
measures: >
  race_h is the high-school slice of RACE (Lai et al., EMNLP 2017), packaged by inspect_evals.
  The model reads an English exam passage written for Chinese students, a question or cloze,
  and four options, then must emit ANSWER: <letter>. Questions are meant to need inference,
  not span copy. This page is the inspect_evals protocol. The dataset, splits, and licence
  are documented on [race](race.md).
task_format: >
  Four-way multiple choice, English, generation. inspect_evals template requires the entire
  response to be 'ANSWER: $LETTER'. Solver is multiple_choice; scorer is choice(). Temperature
  0. Shuffle default True. Hugging Face ehovy/race config high, split test, revision
  2fec9fd81f1dc971569a9b729c43f2f0e6436637.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 95
  baseline_note: >
    Four options. inspect_evals scores accuracy() plus stderr clustered on article_hash.
    The 95% human figure is the RACE paper's ceiling on the full exam set, not a separate
    RACE-H-only rater study. eval.yaml lists dataset_samples 3498, matching the high test split.
dataset:
  size: 3498
  size_note: >
    inspect_evals eval.yaml: 3,498 samples on ehovy/race config high, test split. race.md
    reports the same high test count (train 62,445 / validation 3,451 / test 3,498). The
    task then calls filter_duplicate_ids because of Hugging Face discussion #4; the post-filter
    count was not re-counted here.
  url: "https://huggingface.co/datasets/ehovy/race"
  license: "Non-commercial research use only (custom RACE licence; Hugging Face tags it 'other')"
  languages:
    - en
  modalities:
    - text
  splits: "inspect_evals scores the public high test split only"
  public_test_set: true
publisher:
  org: "Carnegie Mellon University (dataset); inspect_evals packaging by UK AI Security Institute"
  authors:
    - "Guokun Lai"
    - "Qizhe Xie"
    - "Hanxiao Liu"
    - "Yiming Yang"
    - "Eduard Hovy"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/race_h"
paper:
  title: "RACE: Large-scale ReAding Comprehension Dataset From Examinations"
  arxiv: "1704.04683"
  url: "https://arxiv.org/abs/1704.04683"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/race_h"
released: "2017-04"
last_updated: "2026-02"
lineage:
  family: race
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No inspect_evals leaderboard cell was opened. race.md records that the original RACE
    leaderboard URL is dead. lm-eval's task named `race` also uses the high split, but with
    log-likelihood scoring, so those numbers are not this task.
contamination:
  risk: high
  note: >
    Same public test answers as RACE since 2017. See [race](race.md). inspect_evals does not
    hold labels out.
harness:
  lm_eval: ""
  inspect_evals: "race_h"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Run: inspect eval inspect_evals/race_h. Version 2-A (2026-02-16). Prompt template follows
    OpenAI simple-evals multiple-choice format. OpenCompass abbr race-high is PPLInferencer
    plus AccEvaluator on the high split. lm-eval task `race` is RACE-H (dataset_name high,
    output_type multiple_choice) with log-likelihood accuracy, not this ANSWER: LETTER template.
tags:
  - race
  - subset
  - reading-comprehension
  - multiple-choice
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/race_h/README.md"
    title: "inspect_evals race_h README (RACE-H, simple-evals template, accuracy, changelog 2-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/race_h/race_h.py"
    title: "race_h.py (ehovy/race high test, pin 2fec9fd, ANSWER letter template, duplicate filter)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/race_h/eval.yaml"
    title: "eval.yaml (dataset_samples 3498, version 2-A, arXiv 1704.04683)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (packaging; dataset remains RACE non-commercial)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1704.04683"
    title: "RACE paper (arXiv:1704.04683)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/race/race.yaml"
    title: "lm-eval race.yaml (dataset_name high, multiple_choice acc on test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/race/race_ppl_a138cd.py"
    title: "OpenCompass race_ppl_a138cd.py (abbr race-high, PPLInferencer, AccEvaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-068 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-068"
---

Part of the [RACE](race.md) family.

## What it measures

inspect_evals `race_h` is RACE-H only: high-school English-exam passages, questions, and four options from Lai et al. 2017. The model must answer with `ANSWER: A`–`D`. The prompt is the OpenAI simple-evals multiple-choice template, not lm-eval's log-likelihood ranking. Middle-school RACE-M is out of scope. Full dataset facts live on [race](race.md).

## Reading the numbers

eval.yaml counts 3,498 high-test items; duplicates are then dropped. Chance is 25%. A number from this task is a generation letter match at temperature 0, so it is not OpenCompass `race-high` (PPL ranking) and not lm-eval `race` (log-likelihood accuracy), even though all three read the high test split. The 95% human figure is the original paper's full-RACE ceiling. Test answers have been public since 2017, so treat a high score as exam-style reading on a leaked set, not as hidden-test comprehension.
