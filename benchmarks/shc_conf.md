---
id: shc_conf
name: MedConfInfo
aliases:
  - shc_conf_med
  - MedConfInfo
page_kind: benchmark
category: domain
subcategory: "adolescent note confidentiality for parental access"
status: active
summary: >
  Private MedHELM task from Stanford adolescent notes: say whether a visit note
  contains sensitive content that should be withheld from a parent portal view.
measures: >
  MedConfInfo tests whether a model can read an English adolescent encounter
  note and decide if it contains sensitive protected health information that
  should be restricted from parental access under adolescent confidentiality
  rules. HELM's example mentions sexual activity, mental health, or substance
  use discussed in a private portion of a visit. The census id is shc_conf; the
  runnable HELM scenario is shc_conf_med.
task_format: >
  Joint multiple-choice generation. HELM asks for A if the note contains
  sensitive content that should be restricted, or B if not, with no extra text.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM scores exact match of A or B. Rabbani et al. 2024 studied LLM
    classification of confidential content in adolescent notes, but this page
    did not recover a numeric human baseline that applies to the 1000-item
    MedHELM split.
dataset:
  size: 1000
  size_note: >
    Nature Medicine Extended Data Table 1 reports 1000 instances evaluated,
    private and new. HELM reads medhelm-CONF-dataset_filtered.csv with prompt,
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
  org: "Stanford University Department of Pediatrics, Stanford Health Care, and Stanford CRFM (MedHELM)"
  authors:
    - Naveed Rabbani
    - Conner Brown
    - Michael Bedgood
    - Rachel L. Goldstein
    - Jennifer L. Carlson
    - Natalie M. Pageler
    - Keith E. Morse
  url: https://pubmed.ncbi.nlm.nih.gov/38252434/
paper:
  title: "Evaluation of a Large Language Model to Identify Confidential Content in Adolescent Encounter Notes"
  arxiv: ""
  url: https://pubmed.ncbi.nlm.nih.gov/38252434/
  year: 2024
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
    - shc_ent
    - shc_gip
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
    No dated numeric top exact-match for MedConfInfo was recovered from a
    parsed leaderboard table during this research.
contamination:
  risk: low
  note: >
    The 1000 MedHELM items are listed as a private dataset that is not
    redistributed. Nature Medicine groups 14 such private sets, not all from
    Stanford Health Care. The 2024 JAMA Pediatrics research letter is public,
    but that letter is not the HELM CSV.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_conf_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - privacy
  - pediatrics
  - private-dataset
  - medhelm
  - stanford-health-care
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_conf_scenario.py
    title: "HELM shc_conf_scenario.py (SHCCONFMedScenario, MedConfInfo)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_conf_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (MedConfInfo group)"
    accessed: "2026-09-08"
  - url: https://pubmed.ncbi.nlm.nih.gov/38252434/
    title: "Rabbani et al., JAMA Pediatrics 2024 (PMID 38252434)"
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

MedConfInfo asks whether an adolescent visit note contains sensitive material
that should be hidden from a parent or guardian who can see the portal. HELM's
worked example is a checkup note in which a teenager discusses sexual activity
and contraception in the private part of the visit. The model must answer A if
that kind of content is present and should be restricted, or B if not.

The task is English clinical text, single turn, closed labels. It is a privacy
and confidentiality screen on real pediatric notes, not a general PHI de-identifier
and not a chatbot safety eval.

## How it is scored

HELM uses joint multiple-choice prompting ("Answer A or B.") and exact match of
the letter. The methods appendix example gold label is B. Quasi-exact and prefix
exact-match are logged beside the main exact_match metric. This page did not
find a published human-agreement number that applies to the 1000 MedHELM items.
Rabbani and colleagues assessed an LLM on confidential content in adolescent
notes in 2024, but their letter's numeric results were not independently
re-read as full text here.

## Dataset and licence

Extended Data Table 1 reports 1000 instances evaluated, private and new. HELM
loads medhelm-CONF-dataset_filtered.csv with prompt, context, and label, and
marks every instance as test. The notes are not on Hugging Face or GitHub.

HELM cites Rabbani et al., JAMA Pediatrics, 2024
(https://jamanetwork.com/journals/jamapediatrics/fullarticle/2814109). PubMed
records the same title as DOI 10.1001/jamapediatrics.2023.6032, PMID 38252434,
1 March 2024, pages 308-310. This page treats those as one article. The MedHELM
CSV itself remains private; the research letter is not a substitute download.

No data licence was found. HELM code is Apache 2.0.

## Who publishes it

The originating study authors on PubMed are Naveed Rabbani, Conner Brown,
Michael Bedgood, Rachel L. Goldstein, Jennifer L. Carlson, Natalie M. Pageler,
and Keith E. Morse, at Stanford Pediatrics and Lucile Packard Children's
Hospital. MedHELM (Bedi et al., Nature Medicine 2026; arXiv 2505.23802) wraps
the task as shc_conf_med. The HELM file landed in MedHELM V1 on 19 March 2025.
CRFM hosts the leaderboard.

## Lineage

MedConfInfo is a Stanford pediatric confidentiality task, not a copy of
i2b2/n2c2 de-identification shared tasks. It is also not PrivacyDetection
(shc_privacy), which classifies portal messages rather than adolescent visit
notes. Sibling Stanford Health Care pages in this repository include shc_bmt, shc_cdi,
shc_ent, shc_gip, shc_privacy, shc_proxy, shc_ptbm, shc_sei, and shc_sequoia
(ClinicReferral). There is no MedHELM family page.

## Saturation and contamination

Saturation is unknown; no numeric MedConfInfo top score was parsed from the
leaderboard. Contamination risk is low for the 1000 private items. The 2024
letter is public and could leak example wording, but the authors still list
MedConfInfo among datasets they will not redistribute.

## How to run it

Use HELM run spec `shc_conf_med` with `data_path` set to the private CSV.
Stanford's entries are in `run_entries_medhelm_private_stanford.conf`. Adapter
instructions are "Answer A or B." The helper defaults to five in-context
examples, but this scenario has no train split, so the run is effectively
zero-shot. Outside groups cannot rebuild the official score without the file.
No lm-eval, Inspect, OpenCompass, or BIG-bench twin was confirmed.

## Reading the numbers

A high exact-match score means the model usually matched the gold A/B label on
whether these adolescent notes should be restricted from a parent view. It does
not certify a portal privacy filter: the items are from one institution, the
labels are hidden, and exact match does not score which span is confidential.
Read it next to PrivacyDetection and ProxySender, which cover related pediatric
communication risks with different inputs.
