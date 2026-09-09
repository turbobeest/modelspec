---
id: ehrshot
name: "EHRSHOT (HELM ehrshot)"
aliases:
  - "EHRSHOT"
  - "EHRShot"
page_kind: benchmark
category: domain
subcategory: "yes/no future-event prediction from structured EHR code sequences"
status: active
summary: "HELM's yes/no wrap of Stanford EHRSHOT: predict a future clinical event from EHR codes, scored by exact match, not the paper's AUROC."
measures: >
  This id is HELM's ehrshot scenario, not the original few-shot AUROC benchmark
  by itself. Each instance is a patient's prior structured EHR codes plus a
  yes/no question: new diagnosis in a year, abnormal lab if drawn now, long
  stay, 30-day readmission, or ICU transfer. HELM converts timelines with
  codes_only and asks the model to answer A/B (yes/no). Inputs are coded
  events, not clinical notes. English prompts. It is not [ehr_sql](ehr_sql.md).
task_format: >
  Zero-shot joint multiple choice. HELM adapter: "Answer A for yes, B for no",
  max_train_instances 0, max_tokens 1. Scenario references are the strings
  yes and no. Lab tasks subsample 10,000 labels. Default max_length 100,000
  tokens; longer prompts are dropped.
metric:
  name: "exact_match (HELM); paper reports AUROC and AUPRC"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    HELM main_metric is exact_match on yes/no. The EHRSHOT paper evaluates
    few-shot AUROC/AUPRC for count-based models and CLMBR-T-base, including
    4-way lab bins and a 14-way chest X-ray task HELM does not wrap. Chance
    on HELM's binary questions is 50% if labels were balanced; they are not.
    No HELM human baseline was published.
dataset:
  size: 6739
  size_note: >
    Paper and project README: 6,739 patients, 41,661,637 clinical events,
    921,499 visits, 15 tasks. HELM implements 14 binary tasks (six new
    diagnoses, five labs as abnormal/normal, three operational outcomes) and
    omits chest X-ray findings. Lab tasks cap at 10,000 labels. HELM instance
    count after that cap and max_length filter is not published. Access is a
    local MEDS-style tree (data.parquet, subject_splits, per-task labels).
  url: "https://redivis.com/datasets/53gc-8rhx41kgt"
  license: "Stanford University Dataset Research Use Agreement"
  languages:
    - en
  modalities:
    - text
  splits: "Paper: canonical train/val/test per task. HELM assigns every loaded row TEST_SPLIT."
  public_test_set: false
publisher:
  org: "Stanford University (Shah Lab / CRFM MedHELM packaging)"
  authors:
    - "Michael Wornow"
    - "Rahul Thapa"
    - "Ethan Steinberg"
    - "Jason A. Fries"
    - "Nigam H. Shah"
  url: "https://ehrshot.stanford.edu"
paper:
  title: "EHRSHOT: An EHR Benchmark for Few-Shot Evaluation of Foundation Models"
  arxiv: "2307.02028"
  url: "https://arxiv.org/abs/2307.02028"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/som-shahlab/ehrshot-benchmark"
released: "2023-07"
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
  note: >
    Paper shows CLMBR-T-base beating a count GBM at k<=64 on aggregated AUROC
    for some task groups, with room left on new-diagnosis tasks. HELM exact
    match is a different scale. MedHELM SPA was not parsed for a top cell.
contamination:
  risk: low
  note: >
    Patient timelines are gated (Redivis research agreement). HELM reads a
    local data_path, not a public JSON test. Prompts still serialize codes
    that exist in OMOP vocabularies. No public-web leakage study was opened.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "ehrshot"
  opencompass: ""
  bigbench: ""
  other: "Run name is ehrshot:subject=<task>; official few-shot AUROC pipeline is som-shahlab/ehrshot-benchmark, not HELM."
tags:
  - ehr
  - clinical
  - helm
  - few-shot-paper
  - binary-classification
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/ehrshot_scenario.py"
    title: "HELM EHRSHOTScenario (14 tasks, codes_only, 10k lab cap, exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "get_ehrshot_spec (A/B yes-no, max_train_instances 0)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2307.02028"
    title: "EHRSHOT paper (arXiv:2307.02028)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2307.02028"
    title: "EHRSHOT HTML (6,739 patients, 15 tasks, research-use licence, AUROC)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/som-shahlab/ehrshot-benchmark/main/README.md"
    title: "ehrshot-benchmark README (label counts, 15 tasks, MEDS zip)"
    accessed: "2026-09-08"
  - url: "https://github.com/som-shahlab/ehrshot-benchmark"
    title: "som-shahlab/ehrshot-benchmark repository"
    accessed: "2026-09-08"
  - url: "https://ehrshot.stanford.edu"
    title: "EHRSHOT project page (cohort stats)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest/"
    title: "MedHELM latest (SPA; not parsed as a score table here)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-040 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-040"
---

## What it measures

HELM `ehrshot` asks a language model whether a future clinical event will happen, given a string of prior EHR codes. Tasks cover first-time diagnoses (MI, celiac, lipids, hypertension, lupus, pancreatic cancer), binary lab abnormality, long length of stay, 30-day readmission, and ICU transfer. The paper also has a chest X-ray findings task; HELM does not. This is coded-event prediction in English prompts, not note understanding.

## How it is scored

HELM uses joint multiple-choice exact match on yes/no (instructions say A/B). Shots are zero (`n_shots` is 0; few-shot example injection is a stub). The paper scores AUROC and AUPRC while increasing k from 1 to the full train set, with a frozen CLMBR encoder plus a logistic head. Lab items in the paper are four-way bins; HELM asks abnormal versus normal. Do not put a HELM exact-match number next to a paper AUROC.

## Dataset and licence

EHRSHOT is 6,739 Stanford Medicine patients with 41.6 million events and 921,499 visits, ages 19–88, at least ten events. Canonical splits exist per task. HELM needs a local MEDS-style directory and marks every instance TEST_SPLIT. Lab tasks sample 10,000 labels. The dataset licence in the paper appendix is the Stanford University Dataset Research Use Agreement, not a Creative Commons SPDX id. Redivis hosts Original, MEDS, and OMOP zips behind that agreement.

## Who publishes it

Michael Wornow, Rahul Thapa, Ethan Steinberg, Jason Fries, and Nigam Shah released the benchmark at NeurIPS 2023 (arXiv:2307.02028). Code is `som-shahlab/ehrshot-benchmark`. Stanford CRFM added the MedHELM scenario. CLMBR-T-base weights are a separate gated Hugging Face artifact.

## Lineage

EHRSHOT is not MIMIC-III/IV ICU prediction and not [ehr_sql](ehr_sql.md). It was built for few-shot foundation-model evaluation on longitudinal OMOP-coded records. Later papers reuse the 15 tasks with LLM embedders; those are not this HELM id.

## Saturation and contamination

The paper leaves headroom on long-horizon new-diagnosis tasks even for CLMBR. HELM saturation is not established. Patient data are gated, so web-scrape contamination of full timelines is unlikely. Serialized code strings can still overlap public ontologies.

## How to run it

HELM: `ehrshot:subject=<task>` with a `data_path` to the MEDS extract. Official AUROC reproduction is `bash run_all.sh` in `ehrshot-benchmark` on Linux with FEMR. Those two pipelines do not share a metric. State the subject name; there is no single HELM aggregate in the scenario file.

## Reading the numbers

A high HELM exact-match score means the model said yes or no in the requested letter format on truncated code lists. It does not mean calibrated risk, few-shot sample efficiency, or chest X-ray skill. Prevalence is skewed, especially for rare diagnoses, so accuracy without AUROC is easy to misread. Prefer the paper's AUROC/AUPRC when comparing clinical encoders.
