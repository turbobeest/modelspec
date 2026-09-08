---
id: shc_ptbm
name: "ADHD-Behavior"
aliases:
  - "shc_ptbm_med"
  - "PTBM"
  - "parent training in behavior management"
page_kind: benchmark
category: domain
subcategory: "pediatric ADHD clinical-note classification: parent training in behavior management"
status: active
summary: "Private MedHELM binary task: given a pediatric ADHD visit note, say whether the clinician recommended parent training in behavior management."
measures: >
  ADHD-Behavior (HELM scenario shc_ptbm_med) tests whether a model can read an English pediatric
  primary-care note and decide if the clinician recommended parent training in behavior
  management (PTBM). PTBM is the first-line evidence-based treatment for young children with
  ADHD in AAP-style guidelines. The HELM prompt asks for A (yes) or B (no) only. The notes come
  from Packard Children's Health Alliance visits of children aged 4-6 years with an ADHD
  diagnosis, 2015-2019. The same classification problem was first studied as an NLP quality-of-care
  measure, not as a public leaderboard task.
task_format: "Binary A/B classification over a clinical note plus a question; English text; HELM multiple-choice joint adaptation."
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two-way A/B choice gives a 50% random-guess rate. The source paper reports inter-annotator
    agreement F-measure 0.89 on the PTBM recommendation label and BioClinicalBERT test-set
    F1 0.76, precision 0.81, recall 0.72, AUC 0.81 [0.72-0.89] on a 127-note holdout. Those
    figures are for the original NLP pipeline, not for HELM exact-match on the private CSV, so
    they are not recorded as this page's human or top score.
dataset:
  size: 423
  size_note: >
    Nature Medicine Table 1 (PMC13267972) reports 423 instances evaluated for ADHD-Behavior
    (ME28), private and new. That count matches the JAMIA first-ADHD-visit cohort of 423 notes.
    HELM still loads a private CSV (medhelm-PTBM-dataset_filtered.csv); this page does not
    independently count that file. The JAMIA paper split the 423 notes 70/30 into train n=296
    and test n=127, then ran temporal validation on 1,020 later notes (53 model-positive notes
    and 50 sampled negatives were reviewed). Whether every HELM row is one of the 423 first
    visits, the 127-note holdout, or a filter is not established beyond the MedHELM n.
  url: "https://github.com/ybannett/NLP_ADHD"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM exposes a single test split from a local CSV; the paper used train 296 / test 127 plus a 1,020-note temporal-validation pool"
  public_test_set: false
publisher:
  org: "Stanford University School of Medicine (Packard Children's Health Alliance / Stanford Medicine Children's Health); packaged in MedHELM by Stanford CRFM"
  authors:
    - "Malvika Pillai"
    - "Jose Posada"
    - "Rebecca M. Gardner"
    - "Tina Hernandez-Boussard"
    - "Yair Bannett"
  url: "https://crfm.stanford.edu/helm/medhelm/latest"
paper:
  title: "Measuring quality-of-care in treatment of young children with attention-deficit/hyperactivity disorder using pre-trained language models"
  arxiv: ""
  url: "https://doi.org/10.1093/jamia/ocae001"
  year: 2024
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_ptbm_scenario.py"
released: "2024-01"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - shc_sei
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM reports this private task on its healthcare leaderboard, but the public page did
    not render scores as static text here. No HELM exact-match figure is recorded. The 0.056
    figure in the MedHELM paper's Table 8 is a minimum detectable effect, not an accuracy.
contamination:
  risk: low
  note: >
    The notes are protected EHR text. The JAMIA paper states the datasets contain protected
    health information and are not publicly available. HELM lists the scenario only in
    run_entries_medhelm_private_stanford.conf, not in the public MedHELM run-entry file, so
    web-scale pretraining is unlikely to have seen these items or their labels.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "shc_ptbm_med"
  opencompass: ""
  bigbench: ""
  other: "MedHELM private Stanford run entries; helm-run needs data_path to a local CSV"
tags:
  - biomedical
  - clinical-notes
  - adhd
  - medhelm
  - private
  - classification
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_ptbm_scenario.py"
    title: "HELM shc_ptbm_scenario.py (SHCPTBMMedScenario)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM medhelm_run_specs.py (shc_ptbm_med run spec)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "HELM schema_medhelm.yaml (ADHD-Behavior)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/docs/medhelm.md"
    title: "MedHELM documentation (access levels)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf"
    title: "MedHELM private Stanford run entries (shc_ptbm_med CSV path)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1093/jamia/ocae001"
    title: "Pillai et al., JAMIA 2024 (10.1093/jamia/ocae001)"
    accessed: "2026-09-08"
  - url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10990536/"
    title: "PMC10990536 full text of Pillai et al. 2024"
    accessed: "2026-09-08"
  - url: "https://github.com/ybannett/NLP_ADHD"
    title: "ybannett/NLP_ADHD code repository README"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.23802"
    title: "MedHELM full text (ar5iv)"
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

ADHD-Behavior asks a model to read an English pediatric primary-care note and say whether the clinician recommended parent training in behavior management. That recommendation is the first-line treatment for preschool-age children with ADHD in the clinical guidelines the source paper cites. HELM wraps the note and a question in a prompt that allows only `A` (yes) or `B` (no). The notes come from Packard Children's Health Alliance, a community primary-care network affiliated with Stanford Medicine Children's Health, for children aged 4-6 years seen in 2015-2019 with an ICD-10 ADHD diagnosis.

The task is chart review for guideline adherence, not open-ended medical QA. A yes label means the note documents a PTBM recommendation, not that PTBM was delivered or that medication was withheld.

## How it is scored

HELM scores exact match of the A/B choice on its test split (`schema_medhelm.yaml` main metric `exact_match`, main split `test`). Exact match is a 0–1 fraction; this page writes random guessing as 50% on two options. The run spec uses multiple-choice joint adaptation with the instruction "Answer A or B." The helper defaults to five in-context examples, but the scenario tags every CSV row as `TEST_SPLIT`, so the trainer sampler has nothing to draw and the protocol is effectively zero-shot. The JAMIA paper scored a different pipeline: BioClinicalBERT and other pretrained encoders, F1/precision/recall/AUC on a 127-note holdout (BioClinicalBERT F1 0.76). Those numbers are not HELM exact-match and should not be compared to a MedHELM row as if they were the same metric.

No human accuracy on the HELM prompt was published. Inter-annotator agreement on the PTBM label was F-measure 0.89 in the paper, which measures label quality, not model ceiling.

## Dataset and licence

The HELM scenario reads a local CSV with columns `prompt`, `context`, and `label`. Stanford private run entries point at `medhelm-PTBM-dataset_filtered.csv`. Nature Medicine Table 1 reports 423 instances evaluated for ADHD-Behavior. The JAMIA study annotated first ADHD-visit notes for those 423 patients (296/127 train/test) and later reviewed a sample from 1,020 other notes. The CSV is not public. Code for the original NLP pipeline is at `ybannett/NLP_ADHD`. The paper states the EHR datasets contain protected health information and are not publicly available. No SPDX licence for the HELM CSV was published. Nature Medicine lists ADHD-Behavior among fourteen Stanford Health Care datasets blocked by institutional agreements.

## Who publishes it

The clinical dataset and the original quality-of-care study are from Malvika Pillai, Jose Posada, Rebecca M. Gardner, Tina Hernandez-Boussard, and Yair Bannett, published in JAMIA on 19 January 2024 (doi:10.1093/jamia/ocae001; PMID 38244997; PMC10990536). HELM/MedHELM, from Stanford CRFM, packages the classification as scenario `shc_ptbm_med` with display name ADHD-Behavior. The MedHELM paper (arXiv:2505.23802) lists ADHD-Behavior as a private, newly formulated benchmark in clinical decision support. Yair Bannett is also a MedHELM co-author.

## Lineage

This page documents the HELM MedHELM scenario whose census id is `shc_ptbm`. It is not a public NLP benchmark with a downloadable test set. The closest sibling is `shc_sei` (ADHD-MedEffects): same network, but side-effect monitoring in school-age children on medication. Other Stanford Health Care MedHELM scenarios (`shc_sequoia`, `shc_cdi`, `shc_ent`, and further `shc_*` ids) share the private CSV pattern but are different tasks. This repository has no MedHELM family page.

## Saturation and contamination

Saturation on the HELM exact-match metric is not established: the MedHELM leaderboard did not yield a static top score here, and Table 8 in the MedHELM paper reports minimum detectable effect (0.056 ± 0.008 for ADHD-Behavior), not accuracy. Contamination risk is low for public models because the notes are unpublished PHI and the run lives only in the private Stanford MedHELM entry file. The original paper did report lower BioClinicalBERT F1 (0.53) on publicly insured patients, so even a high HELM score would not by itself show fairness across insurance groups.

## How to run it

Install HELM with the MedHELM extras and call `helm-run` with run spec `shc_ptbm_med` and a `data_path` to the CSV. Only authorised Stanford Health Care users can reproduce the official rows (`run_entries_medhelm_private_stanford.conf`). Adapter instructions are "Answer A or B." Official rows are effectively zero-shot, as above. HELM's `schema_medhelm.yaml` taxonomy line for this scenario currently says "Detect ADHD medication side effect monitoring", which is the SEI task; the scenario docstring, display name, and JAMIA citation describe PTBM. Prefer the scenario Python and the paper over that taxonomy string. No lm-evaluation-harness, inspect_evals, or OpenCompass task was found.

## Reading the numbers

A high ADHD-Behavior score means the model often matches clinician chart-review labels for a PTBM recommendation in this network's 4-6-year-old ADHD notes, under HELM's A/B prompt. It does not mean the model can treat ADHD or generalise to other health systems. Do not treat BioClinicalBERT's 0.76 F1 as a HELM baseline, and do not treat MedHELM's 0.056 MDE figure as an accuracy. Compare only HELM exact-match numbers that used the same private CSV and adapter. Pair the score with `shc_sei` for ADHD quality of care more broadly.
