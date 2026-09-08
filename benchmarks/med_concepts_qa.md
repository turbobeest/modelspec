---
id: med_concepts_qa
name: MedConceptsQA
aliases:
  - MedConceptsQA
  - medconceptsqa
page_kind: benchmark
category: domain
subcategory: medical coding concept multiple-choice
status: active
summary: Four-option questions that ask a model to pick the correct description of an ICD or ATC medical code among related distractors, across three difficulty levels.
measures: >
  MedConceptsQA tests whether a model can map a medical code to its official description. Each
  item names one code from ICD-9-CM or ICD-10-CM (diagnoses), ICD-9-PCS or ICD-10-PCS (procedures),
  or ATC (drugs), then offers four English descriptions. Only one description matches the given
  code. Distractors are sampled from the same vocabulary at a controlled graph distance, so hard
  items pit a code against near neighbours that share a parent. It is a single-turn, English,
  text-only multiple-choice task about code literacy rather than clinical vignettes or exam
  reasoning, which sets it apart from MedQA and MedMCQA.
task_format: >
  Four-option multiple choice. The model returns a letter A-D. EleutherAI's lm-evaluation-harness
  uses four-shot by default (first_n from the dev split) and also supports zero-shot.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Four balanced options, with the correct letter placed at random, so uniform guessing is 25%.
    No human baseline was reported in the paper or on the authors' GitHub leaderboard.
dataset:
  size: 819832
  size_note: >
    Hugging Face config `all` reports 60 dev and 819,772 test examples (819,832 total). That total
    matches the paper's per-vocabulary table once the 60 later-held-out dev items are included.
    Each of the 15 vocabulary-by-difficulty configs holds 4 dev items; test counts run from 4,434
    (icd9proc_hard) to 190,983 (icd10proc easy and medium). The paper's published evaluation samples
    250 items per vocabulary, difficulty and shot setting rather than scoring the full test set.
  url: https://huggingface.co/datasets/ofir408/MedConceptsQA
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: "60 dev / 819,772 test on the `all` config; 15 vocabulary-by-difficulty configs with 4 dev items each"
  public_test_set: true
publisher:
  org: Ben-Gurion University of the Negev
  authors:
    - Ofir Ben Shoham
    - Nadav Rappoport
  url: https://github.com/nadavlab/MedConceptsQA
paper:
  title: "MedConceptsQA: Open Source Medical Concepts QA Benchmark"
  arxiv: "2405.07348"
  url: https://arxiv.org/abs/2405.07348
  year: 2024
leaderboard_url: https://github.com/nadavlab/MedConceptsQA
repo_url: https://github.com/nadavlab/MedConceptsQA
released: "2024-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 61.911
  as_of: "2024-05"
  note: >
    The authors' GitHub README leaderboard, which matches the paper's GPT-4 figures, puts
    gpt-4-0125-preview at 52.489% zero-shot and 61.911% four-shot, both well below 100% and well
    above the 25% chance rate. Several 70B medical and general models sit in the high 40s to high
    50s few-shot. No later dated public tracker was found during this research.
contamination:
  risk: medium
  note: >
    Questions are generated from public medical-code vocabularies and have been downloadable with
    answers on Hugging Face since May 2024. They are not copied from licensing exams, but the full
    labelled set is ungated.
harness:
  lm_eval: med_concepts_qa
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group `med_concepts_qa` averages accuracy across five vocabulary groups (icd9cm, icd10cm,
    icd9proc, icd10proc, atc). Each group is the tag of three tasks (`easy`, `medium`, `hard`),
    for 15 runnable task names such as `med_concepts_qa_atc_easy`. Dataset path is
    ofir408/MedConceptsQA. The authors' README evaluates with `--limit 250` and `--num_fewshot` 0 or 4.
tags:
  - medical
  - multiple-choice
  - medical-coding
  - icd
  - atc
sources:
  - url: https://arxiv.org/abs/2405.07348
    title: "MedConceptsQA: Open Source Medical Concepts QA Benchmark"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2405.07348
    title: "MedConceptsQA HTML full text on ar5iv"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ofir408/MedConceptsQA
    title: "ofir408/MedConceptsQA dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/ofir408/MedConceptsQA
    title: "ofir408/MedConceptsQA Hugging Face API"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=ofir408/MedConceptsQA
    title: "ofir408/MedConceptsQA datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://github.com/nadavlab/MedConceptsQA
    title: "nadavlab/MedConceptsQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/med_concepts_qa/README.md
    title: "med_concepts_qa task README, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/med_concepts_qa/_med_concepts_qa.yaml
    title: "med_concepts_qa group config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/med_concepts_qa/_default_template_yaml
    title: "med_concepts_qa default template, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

MedConceptsQA asks a model to identify the official description of a medical code. Each question
names one code from ICD-9-CM, ICD-10-CM, ICD-9-PCS, ICD-10-PCS or ATC, then lists four English
descriptions. Only one description is correct. Easy distractors are drawn from anywhere in the same
vocabulary. Medium and hard distractors come from codes a few graph edges away, so hard items look
alike. The task is English text, single-turn, and about code meaning rather than a patient vignette.

That focus is the point. Clinical notes often store diagnoses, procedures and drugs as codes, not
prose. A model that scores well on MedQA can still fail here if it cannot tell neighbouring ICD
strings apart.

## How it is scored

The metric is four-option accuracy. Chance is 25%, because the correct letter is placed at random.
The paper evaluates each vocabulary and difficulty with zero-shot and four-shot prompts, sampling
250 items and repeating three times for a 95% confidence interval. Aggregates average those runs.
EleutherAI's group `med_concepts_qa` instead averages accuracy across the five vocabulary groups,
each of which already averages its easy, medium and hard tasks. The authors' own harness command
uses `--limit 250`, so a number from a full 819k-item run is not comparable to the published tables.

## Dataset and licence

Hugging Face reports 819,832 examples on the `all` config (60 dev, 819,772 test), matching the
paper's per-cell counts once the 60 dev items are included. Fifteen configs split the five
vocabularies by easy, medium and hard. The Hugging Face card states Apache-2.0. Answers ship with
the files. The authors also published the work in *Computers in Biology and Medicine* (2024).

## Who publishes it

Ofir Ben Shoham and Nadav Rappoport at Ben-Gurion University of the Negev introduced the benchmark
in May 2024 (arXiv:2405.07348). Code lives at nadavlab/MedConceptsQA. That README is the standing
leaderboard; it invites submissions by GitHub issue. No separate hosted leaderboard was found.

## Lineage

This is not a variant of MedQA, MedMCQA or PubMedQA. Those pages cover exam vignettes or abstract
yes/no/maybe questions. MedConceptsQA is generated from PyHealth vocabulary graphs. No successor
id exists in this repository.

## Saturation and contamination

The authors' README still lists gpt-4-0125-preview first, at 52.489% zero-shot and 61.911%
four-shot, matching the paper. Several 70B models land in the high 40s to high 50s few-shot.
Clinical models in the paper sat near chance. The ceiling is not in reach. Contamination risk is
medium: the labelled set has been public since May 2024, but items are generated from public code
tables rather than copied from exams.

## How to run it

In lm-evaluation-harness, run group `med_concepts_qa`, or a single task such as
`med_concepts_qa_icd10cm_hard`. The template scores multiple-choice accuracy on ofir408/MedConceptsQA
with four-shot from the four-item dev split unless you set `--num_fewshot 0`. The authors' README
uses `--limit 250`. Compare shot count, limit and whether the figure is one vocabulary or the
five-group mean before lining numbers up.

## Reading the numbers

A high score means the model can pick the right gloss for a billing or drug code among close
neighbours, not that it can diagnose or prescribe. The paper's own case study shows GPT-4 dropping
from the mid-90s on easy ICD-9-CM to the low 50s on hard items, so an aggregate hides that slide.
Look at MedQA or MedMCQA for vignette reasoning, and treat any MedConceptsQA figure that does not
state shot count and sample size as incomparable.
