---
id: oab_exams
name: OAB Exams
aliases: [Brazilian Bar Exam]
page_kind: benchmark
category: domain
subcategory: legal knowledge
status: active
summary: OAB Exams evaluates Portuguese legal question answering on Brazilian bar examinations from 2010 through 2018.
measures: The benchmark uses objective multiple-choice questions from the Brazilian OAB bar examination. It tests legal knowledge across areas of Brazilian law in Brazilian Portuguese.
task_format: Multiple-choice questions with four or more labelled choices; select the answer text.
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: No human baseline was supplied by the scenario source.
dataset:
  size: 2210
  size_note: The Hugging Face API reports 2,210 rows in the train split; HELM skips rows marked nullified at runtime, so the scored count is lower or equal.
  url: https://huggingface.co/datasets/eduagarcia/oab_exams
  license: ""
  languages: [Portuguese]
  modalities: [text]
  splits: train (used as test by HELM)
  public_test_set: true
publisher:
  org: eduagarcia (dataset release)
  authors: []
  url: https://huggingface.co/datasets/eduagarcia/oab_exams
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: https://huggingface.co/datasets/eduagarcia/oab_exams
released: ""
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
  note: No authoritative leaderboard was established.
contamination:
  risk: medium
  note: Historical exams are public through the dataset release; exposure in model training was not measured.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: oab_exams
  opencompass: ""
  bigbench: ""
  other: ""
tags: [law, portuguese, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/oab_exams_scenario.py
    title: HELM OAB Exams scenario
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/eduagarcia/oab_exams
    title: OAB Exams dataset card
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated)
  reviewed: "2026-09-08"
  reviewed_by: GPT-5.6 Luna independent review, luna-batch-017
---

## What it measures

OAB Exams measures legal question answering in Brazilian Portuguese. The source describes the OAB exam as a mandatory test for people who want to practise law in Brazil. Its objective phase covers all areas of law through multiple-choice questions.

The dataset also describes a written phase, but the HELM scenario evaluates only the objective questions. It loads the dataset’s `train` split and presents each question without retrieved legal material.

## How it is scored

HELM creates one reference for the correct choice and untagged references for the incorrect choices. Accuracy over the selected answer is the natural metric. The source does not provide a human baseline or a universal score report.

## Dataset and licence

The scenario says the dataset contains exams from 2010 through 2018. The Hugging Face dataset API reports 2,210 train rows; HELM skips rows marked `nullified`, so the scored count depends on the release contents. The dataset is text, in Portuguese, and the source does not establish a licence.

## Who publishes it

The runnable scenario is maintained in Stanford HELM. The data release is `eduagarcia/oab_exams` on Hugging Face. The sources read do not identify a paper, original exam-authoring committee, or current leaderboard.

## Lineage

OAB Exams is a legal-domain evaluation collection. The sources read do not establish a predecessor, successor, or separate repository variant.

## Saturation and contamination

Saturation is unknown. Historical exam questions are public in the released dataset, and model training exposure is possible, but no measurement was found. Scores should therefore be treated as a test of legal question answering under this particular historical sample.

## How to run it

Use HELM’s `oab_exams` scenario. It loads `eduagarcia/oab_exams`, iterates over `train`, removes nullified questions, and evaluates answer text against the keyed choice. The scenario tags the task as knowledge, multiple choice, and `pt-br`; prompt and language handling should be recorded.

## Reading the numbers

A high score indicates familiarity with the legal concepts and wording represented in the selected exams. It does not establish legal advice quality, professional qualification, or performance on the written phase. Compare scores only when filtering of nullified questions and answer-choice formatting match. A current legal evaluation should be paired with newer law and citation checks.
