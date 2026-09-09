---
id: shc_gip
name: HospiceReferral
aliases:
  - shc_gip_med
  - HospiceReferral
page_kind: benchmark
category: domain
subcategory: "hospice eligibility from palliative care notes"
status: active
summary: >
  Private Stanford Health Care MedHELM task: from a palliative care note, answer
  yes or no on whether the patient is eligible for hospice referral.
measures: >
  HospiceReferral tests whether a model can read an English palliative care
  consultation note and decide if the patient is eligible for hospice care.
  HELM's class docstring frames it as a gold-standard referral set used to check
  hospice referral decisions. The census id is shc_gip; the runnable HELM
  scenario is shc_gip_med. HELM sources do not expand the letters GIP.
task_format: >
  Joint multiple-choice generation. HELM requires A for yes or B for no, with no
  extra text, given the CSV question and the palliative note.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Main metric is exact_match on A or B. No published class balance or human
    hospice-coordinator baseline was found for this private set.
dataset:
  size: 1000
  size_note: >
    Nature Medicine Extended Data Table 1 reports 1000 instances evaluated,
    private and new. HELM reads medhelm-GIP-dataset_filtered.csv with prompt,
    context, and label columns and tags every row as test.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "test only (HELM TEST_SPLIT); no published train or validation split"
  public_test_set: false
publisher:
  org: "Stanford Health Care and Stanford CRFM (MedHELM)"
  authors:
    - Suhana Bedi
    - Hejie Cui
    - Miguel Fuentes
    - Alyssa Unell
    - Nigam H. Shah
  url: https://crfm.stanford.edu/helm/medhelm/latest/
paper:
  title: "Holistic evaluation of large language models for medical tasks with MedHELM"
  arxiv: "2505.23802"
  url: https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/
  year: 2026
leaderboard_url: https://crfm.stanford.edu/helm/medhelm/latest/
repo_url: https://github.com/stanford-crfm/helm
released: "2025-03"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - shc_bmt
    - shc_cdi
    - shc_conf
    - shc_ent
    - shc_privacy
    - shc_proxy
    - shc_ptbm
    - shc_sei
    - shc_sequoia
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated numeric top exact-match for HospiceReferral was recovered from a
    parsed leaderboard table.
contamination:
  risk: low
  note: >
    Listed among the 14 private MedHELM datasets that cannot be shared, which
    is the authors' stated protection against training inclusion. Those 14 are
    not all Stanford Health Care records.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_gip_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - hospice
  - palliative-care
  - private-dataset
  - medhelm
  - stanford-health-care
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_gip_scenario.py
    title: "HELM shc_gip_scenario.py (SHCGIPMedScenario, HospiceReferral)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_gip_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (HospiceReferral group)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2505.23802
    title: "MedHELM arXiv:2505.23802"
    accessed: "2026-09-08"
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/
    title: "MedHELM Nature Medicine author manuscript (PMC13267972)"
    accessed: "2026-09-08"
  - url: https://crfm-helm.readthedocs.io/en/latest/medhelm/
    title: "MedHELM documentation"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE
    title: "stanford-crfm/helm Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-001 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-001"
---

## What it measures

HospiceReferral asks whether a palliative care note supports referring the
patient to hospice. HELM's methods text says the context is a palliative care
consultation with medical history and clinical status relevant to hospice
eligibility. The model must answer A for yes or B for no. The census spelling
is shc_gip; HELM's display name is HospiceReferral. This page does not expand
GIP, because the scenario, schema, and papers never spell those letters out.

The task is English clinical text, closed labels, one turn. It is an
end-of-life operations decision, not a general prognosis exam.

## How it is scored

HELM uses joint multiple-choice adaptation with instructions "Answer A or B."
and scores exact match of the letter. The schema names exact_match on test as
the main metric. Quasi-exact and prefix variants are also stored. No human
hospice-team baseline or class prior was published for the 1000-item private
set, so a 50 percent chance line is not established.

## Dataset and licence

Extended Data Table 1 reports 1000 instances evaluated, private and new. HELM
loads medhelm-GIP-dataset_filtered.csv with prompt, context, and label, and
tags every instance as test. Taxonomy in the paper: Administration and
Workflow, scheduling resources and staff. HELM metadata says who is a hospital
administrator and when is end-of-care.

The notes are Stanford Health Care records and are not released. No data
licence was found. HELM code is Apache 2.0.

## Who publishes it

HospiceReferral is a new private MedHELM benchmark from Stanford Health Care
and Stanford CRFM (Bedi, Cui, Fuentes, Unell, Shah and colleagues). Preprint:
arXiv:2505.23802, 26 May 2025. Journal: Nature Medicine, 20 January 2026. The
HELM scenario entered the public tree with MedHELM V1 on 19 March 2025. The
leaderboard is at https://crfm.stanford.edu/helm/medhelm/latest/.

## Lineage

This is not ClinicReferral (shc_sequoia_med), which uses palliative notes to
decide Sequoia clinic eligibility, and not ENT-Referral, which is a three-way
specialist triage task. It is also not a public hospice-policy quiz. Sibling pages include shc_bmt, shc_cdi, shc_conf, shc_ent, shc_privacy,
shc_proxy, shc_ptbm, shc_sei, and shc_sequoia (ClinicReferral). There is no
MedHELM family page.

## Saturation and contamination

Saturation is unknown; no numeric HospiceReferral top score was parsed here.
Contamination risk is low because the authors keep the 1000 notes private.
Public web text about hospice criteria could still inflate scores without
memorizing this CSV; that effect was not measured.

## How to run it

Run HELM scenario `shc_gip_med` with `data_path` pointing at the private CSV.
Official Stanford rows are in `run_entries_medhelm_private_stanford.conf`.
Adapter instructions are "Answer A or B." The multiple-choice helper defaults
to five in-context examples, but only a test split exists, so the run is
effectively zero-shot. Outside reproduction needs the CSV, which Stanford does
not publish. No lm-eval, Inspect, OpenCompass, or BIG-bench twin was confirmed.

## Reading the numbers

A high exact-match score means the model usually matched the gold hospice
yes or no on these palliative notes. It does not mean the model should make
hospice decisions: the labels are local, the metric is a single letter, and
end-of-life criteria include values the note may not state. Compare it with
ClinicReferral and ENT-Referral in the same suite, not with open-ended
summarization scores.
