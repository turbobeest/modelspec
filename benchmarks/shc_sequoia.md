---
id: shc_sequoia
name: "ClinicReferral"
aliases:
  - "shc_sequoia_med"
  - "Sequoia clinic referral"
page_kind: benchmark
category: domain
subcategory: "palliative-care note classification: Sequoia clinic referral eligibility"
status: active
summary: "Private MedHELM binary task: from a palliative-care note, decide whether a patient is eligible for referral to Stanford's Sequoia clinic."
measures: >
  ClinicReferral (HELM scenario shc_sequoia_med) tests whether a model can read English
  palliative-care notes and answer curated yes/no questions about referral to the Sequoia
  clinic. HELM's scenario docstring calls the items "manually curated answers to several
  questions for Sequoia clinic referrals." The prompt numbers each item and requires `A`
  (yes) or `B` (no) with no extra text. MedHELM places the task in Administration and
  Workflow and describes it as determining referral eligibility from palliative-care notes
  to help automate clinic workflows.
task_format: "Binary A/B classification over a question plus note context; English text; HELM multiple-choice joint adaptation."
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two-way A/B choice gives a 50% random-guess rate. No human accuracy, inter-annotator
    agreement, or published model exact-match on this HELM CSV was found in the scenario
    file, schema, or MedHELM paper.
dataset:
  size: 326
  size_note: >
    Nature Medicine Table 1 (PMC13267972) reports 326 instances evaluated for ClinicReferral,
    private and new. HELM still loads a private CSV (medhelm-sequoia-dataset_filtered.csv)
    with columns question, context, and label; this page does not independently count that
    file. Unlike shc_ptbm and shc_sei, no separate methods paper describing this item set
    was cited from the scenario.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM exposes a single test split from a local CSV; no public train/validation/test counts"
  public_test_set: false
publisher:
  org: "Stanford Health Care / Stanford CRFM (MedHELM)"
  authors: []
  url: "https://crfm.stanford.edu/helm/medhelm/latest"
paper:
  title: "Holistic evaluation of large language models for medical tasks with MedHELM"
  arxiv: "2505.23802"
  url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/"
  year: 2026
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_sequoia_scenario.py"
released: "2025-05"
last_updated: "2026-01"
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
    MedHELM lists ClinicReferral as a private, newly formulated benchmark. No static
    exact-match top score was read from the public leaderboard page. Table 8 of the
    MedHELM paper reports a minimum detectable effect of 0.050 ± 0.011 for
    ClinicReferral, which is a sample-size statistic, not an accuracy.
contamination:
  risk: low
  note: >
    MedHELM marks the benchmark private. HELM run entries appear only in
    run_entries_medhelm_private_stanford.conf, with an internal Databricks CSV path.
    No public item dump was found, so public pretraining is unlikely to include the
    notes or labels.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "shc_sequoia_med"
  opencompass: ""
  bigbench: ""
  other: "MedHELM private Stanford run entries; helm-run needs data_path to a local CSV"
tags:
  - biomedical
  - clinical-notes
  - referral
  - palliative-care
  - medhelm
  - private
  - classification
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_sequoia_scenario.py"
    title: "HELM shc_sequoia_scenario.py (SHCSequoiaMedScenario)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM medhelm_run_specs.py (shc_sequoia_med run spec)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "HELM schema_medhelm.yaml (ClinicReferral)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/docs/medhelm.md"
    title: "MedHELM documentation (access levels)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf"
    title: "MedHELM private Stanford run entries (shc_sequoia_med CSV path)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks (arXiv:2505.23802)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.23802"
    title: "MedHELM full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest"
    title: "MedHELM leaderboard (JavaScript shell; scores not recovered as static text)"
    accessed: "2026-09-08"
  - url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/"
    title: "MedHELM Nature Medicine author manuscript (PMC13267972), Table 1 instances evaluated"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_multiple_choice_adapter_spec default max_train_instances=5"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-002 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-002"
---

## What it measures

ClinicReferral asks a model to answer yes/no questions about whether a patient should be referred to Stanford's Sequoia clinic, using text from palliative-care notes. HELM feeds a numbered question and a context field and requires `A` or `B` only. The MedHELM schema describes the skill as pre-referral classification for a hospital administrator. Unlike the two ADHD SHC tasks, the scenario file does not name an age group, a year range, or a journal paper. The only primary descriptions are the HELM docstring ("manually curated answers to several questions") and the MedHELM table row ("manually curated answers to questions regarding patient referrals to the Sequoia clinic").

The task is workflow classification on private notes, not a public referral-policy exam. What "Sequoia clinic" covers beyond that HELM sentence is not established from the sources opened for this page.

## How it is scored

HELM uses exact match on the A/B label, test split, with multiple-choice joint adaptation and the instruction "Answer A or B." Exact match is a 0–1 fraction; this page writes random guessing as 50% on two options. The helper defaults to five in-context examples, but the scenario tags every CSV row as `TEST_SPLIT`, so the protocol is effectively zero-shot. No published human baseline, majority baseline, or model exact-match for this CSV was found. The MedHELM paper's 0.050 ± 0.011 figure for ClinicReferral is a minimum detectable effect in Appendix E, not a score.

## Dataset and licence

The scenario reads a local CSV with `question`, `context`, and `label` (not the `prompt`/`context`/`label` columns used by the ADHD scenarios). Private Stanford run entries name `medhelm-sequoia-dataset_filtered.csv`. Nature Medicine Table 1 reports 326 instances evaluated. Class balance and a data licence are not published. MedHELM marks the benchmark private and lists it among fourteen Stanford Health Care datasets blocked by institutional agreements. There is no public dataset URL.

## Who publishes it

Stanford CRFM publishes the evaluation as part of MedHELM (Bedi, Cui, Fuentes, Unell, Wornow, and co-authors). The peer-reviewed suite paper is Nature Medicine, 20 January 2026 (doi:10.1038/s41591-025-04151-2; PMC13267972; arXiv:2505.23802, 26 May 2025). The notes come from Stanford Health Care. No separate Sequoia-clinic methods paper was cited in the scenario. The MedHELM author list is long; this page does not copy it in full. Display name ClinicReferral and scenario name `shc_sequoia_med` are from HELM's schema and Python.

## Lineage

This page is the HELM scenario whose census id is `shc_sequoia`. It sits with other private SHC MedHELM tasks (`shc_cdi`, `shc_ent`, `shc_gip`) under Administration and Workflow. It is not the ADHD pair `shc_ptbm` / `shc_sei`, which use different notes and questions. This repository has no MedHELM family page. No predecessor dataset was named.

## Saturation and contamination

Saturation is unknown: no public exact-match table was recovered from the JavaScript leaderboard. Contamination risk is low if the notes never left SHC, which is the access model MedHELM documents for private benchmarks. That is an access claim, not a measured membership test.

## How to run it

Run HELM spec `shc_sequoia_med` with `data_path` pointing at the private CSV. Official reproductions use `run_entries_medhelm_private_stanford.conf` and Stanford Health Care model deployments. Adapter instructions are "Answer A or B." The multiple-choice helper defaults to five shots, but only test instances exist, so official rows are effectively zero-shot. Public MedHELM install docs (`docs/medhelm.md`) explain public vs gated vs private run-entry files; this scenario is private. No lm-evaluation-harness, inspect_evals, or OpenCompass task was found.

## Reading the numbers

A high ClinicReferral score means the model matches SHC's curated A/B labels on this unpublished referral CSV under HELM's prompt. It does not show that the model can run a palliative-care clinic, apply another health system's referral rules, or answer free-text referral questions. Nature Medicine evaluated 326 instances; class balance and current leaderboard cells are still not public as static text. Treat any leaked number as incomparable unless the reporter names this HELM spec and this CSV. If you need a public administration-style clinical task, this is the wrong row; if you need ADHD note classification, use `shc_ptbm` or `shc_sei`.
