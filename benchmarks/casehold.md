---
id: casehold
name: "CaseHOLD (Case Holdings On Legal Decisions)"
aliases:
  - "Case Holdings On Legal Decisions"
page_kind: benchmark
category: domain
subcategory: "US case-law holding identification"
status: active
summary: "53,137 five-way multiple-choice questions that ask which holding statement matches a citing passage mined from US judicial opinions."
measures: >
  CaseHOLD tests whether a model can pick the holding of a cited case from five
  candidate holding sentences. The prompt is the citing passage from a US
  opinion. One candidate is the holding that actually follows in that opinion;
  four are other holdings used as distractors. Holdings are the precedential
  rule of a decision, so the task is legal citation sense-making, not open
  legal advice.
task_format: >
  Five-way multiple choice. The paper reports mean macro F1 over 10 folds.
  HELM loads Hugging Face casehold/casehold config `all`, keeps train and test
  (skips validation), prompts with “Give a letter answer among A, B, C, D, or
  E,” allows two in-context train items, and scores exact match.
metric:
  name: "macro F1 (paper); exact_match (HELM)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: null
  baseline_note: >
    Five options imply 20% chance if answers are uniform. Paper: BiLSTM F1 0.4,
    BERT F1 0.6; domain-pretrained Legal-BERT gained 7.2 F1 points over BERT
    (12% relative). A law-student accuracy of 0.94 is reported only for a
    pilot set, so human_baseline is left unset. HELM does not publish that F1
    protocol.
dataset:
  size: 53137
  size_note: >
    Paper table and Hugging Face config `all`: 53,137 examples (train 42,509,
    validation 5,314, test 5,314). Ten additional fold configs exist. HELM
    uses train+test only (47,823 rows loaded; two shots taken from train).
  url: "https://huggingface.co/datasets/casehold/casehold"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 42,509 / validation 5,314 / test 5,314 on config `all`; 10 CV folds also published"
  public_test_set: true
publisher:
  org: "Stanford RegLab"
  authors:
    - "Lucia Zheng"
    - "Neel Guha"
    - "Brandon R. Anderson"
    - "Peter Henderson"
    - "Daniel E. Ho"
  url: "https://reglab.stanford.edu/data/casehold-benchmark/"
paper:
  title: "When Does Pretraining Help? Assessing Self-Supervised Learning for Law and the CaseHOLD Dataset"
  arxiv: "2104.08671"
  url: "https://arxiv.org/abs/2104.08671"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/reglab/casehold"
released: "2021-06"
last_updated: "2023-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    2021 encoder results (BERT F1 about 0.6) are not a current generative-LLM
    ceiling. No HELM or other live top score was confirmed here.
contamination:
  risk: high
  note: >
    Items are mined from the public Harvard Law case corpus (case.law), with
    a 10% case holdout for task creation. Questions, holdings, and labels have
    been public since 2021 (GitHub, Drive, Hugging Face). Exact-passages from
    opinions are likely in pretraining crawls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: casehold
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec is in enterprise_run_specs.py (`@run_spec_function("casehold")`),
    not classic_run_specs.py. Scenario: casehold_scenario.py. Paper code
    fine-tunes encoders; that is a different protocol from HELM generation.
tags:
  - legal
  - multiple-choice
  - case-law
  - domain
sources:
  - url: "https://arxiv.org/abs/2104.08671"
    title: "CaseHOLD paper (arXiv:2104.08671, ICAIL 2021)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2104.08671"
    title: "CaseHOLD full text (ar5iv); 53,137 items, F1 baselines"
    accessed: "2026-09-08"
  - url: "https://github.com/reglab/casehold"
    title: "reglab/casehold repository (Apache-2.0 LICENSE)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/casehold/casehold"
    title: "casehold/casehold dataset (split sizes)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=casehold/casehold"
    title: "Hugging Face datasets-server split counts"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/casehold_scenario.py"
    title: "HELM CaseHOLDScenario"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "HELM casehold run spec (joint MC, two-shot, exact match)"
    accessed: "2026-09-08"
  - url: "https://reglab.stanford.edu/data/casehold-benchmark/"
    title: "Stanford RegLab CaseHOLD page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-029 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-029"
---

## What it measures

CaseHOLD is a US legal-citation task. The model sees a citing passage from a judicial opinion and five holding sentences. It must choose the holding that belongs to that citation. Holdings are the precedential rule of a case, so the skill is matching a legal proposition to its source context, not drafting a brief.

Items were mined from the Harvard Law case corpus. The authors held out 10% of decisions to build the questions and used the rest to pretrain Legal-BERT. The benchmark is English case law, not statutes or contracts.

## How it is scored

The ICAIL 2021 paper reports mean macro F1 across ten folds for encoder fine-tunes. A BiLSTM sat at F1 0.4 and BERT at about 0.6; custom legal pretraining added 7.2 F1 points over BERT. HELM does not repeat that protocol. It asks for a letter A–E, uses two in-context train examples, and scores exact match. A HELM percentage is not a reproduction of the paper’s F1.

Five-way chance is 20% if the model picks uniformly. A 0.94 law-student accuracy figure in the paper is a pilot, so it is not recorded as human_baseline.

## Dataset and licence

Hugging Face `casehold/casehold` config `all` has 53,137 examples: 42,509 train, 5,314 validation, 5,314 test, matching the paper’s 53,137 count. Fold_1 through fold_10 repeat the task for cross-validation. The GitHub repository LICENSE is Apache-2.0; the Hugging Face card does not fill its own licence field. HELM loads train and test and skips validation.

## Who publishes it

Lucia Zheng, Neel Guha, Brandon R. Anderson, Peter Henderson and Daniel E. Ho (Stanford RegLab) presented the work at ICAIL 2021 in São Paulo (21–25 June 2021; ACM 10.1145/3462757.3466088). arXiv:2104.08671 first appeared 18 April 2021 (v3 6 July 2021). Code is at github.com/reglab/casehold; the project page is at Stanford RegLab. Hugging Face user `casehold` hosts the models and data.

## Lineage

CaseHOLD is not a [LegalBench](legalbench.md) task id. LegalBench is a later 162-task collaboration that HELM samples separately. CaseHOLD remains its own HELM scenario (`casehold` in enterprise_run_specs.py). No successor page is in this repository.

## Saturation and contamination

2021 encoder F1 scores do not tell you where GPT-class models sit. No current top score was confirmed here. Contamination risk is high: opinions are public, the task set has been downloadable since 2021, and the text is real judicial prose rather than synthetic templates.

## How to run it

HELM: `casehold`. Confirm you are looking at exact match with two-shot joint multiple choice, not a fine-tuned Legal-BERT F1. The paper’s reference code fine-tunes BERT-family models on the folds. Mixing those two numbers is the usual comparison error.

## Reading the numbers

A high HELM exact-match score means the model can pick the right holding letter under that prompt. It does not mean the model can argue a case, cite unseen jurisdictions, or beat a lawyer on open research. Prefer paper F1 only when the run used the 10-fold encoder setup. Watch for leakage: these holdings already circulate in public case databases.
