---
id: shc_privacy
name: PrivacyDetection
aliases:
  - shc_privacy_med
  - PrivacyDetection
page_kind: benchmark
category: domain
subcategory: "confidential content in patient portal messages"
status: active
summary: >
  Private MedHELM task: decide whether a patient-portal message contains
  confidential or privacy-leaking information, answering A for yes or B for no.
measures: >
  PrivacyDetection tests whether a model can read an English patient-portal
  message and say whether it contains confidential or privacy-leaking
  information that should be protected. HELM metadata describes messages from
  patients or caregivers. The census id is shc_privacy; the runnable HELM
  scenario is shc_privacy_med.
task_format: >
  Joint multiple-choice generation. HELM instructs the model to review clinical
  messages for confidential information and answer A for yes or B for no.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Main metric is exact_match of A or B. No published class balance or human
    privacy-officer baseline for the 300 MedHELM items was found.
dataset:
  size: 300
  size_note: >
    Nature Medicine Extended Data Table 1 reports 300 instances evaluated,
    private and new, cited as ME38 with ProxySender. HELM reads
    medhelm-PRIVACY-dataset_filtered.csv with prompt, context, and label.
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
    - Gabriel Tse
    - Aydin Zahedivash
    - Arash Anoshiravani
    - Jennifer Carlson
    - William Haberkorn
    - Keith E. Morse
  url: https://pubmed.ncbi.nlm.nih.gov/39495530/
paper:
  title: "Large Language Model Responses to Adolescent Patient and Proxy Messages"
  arxiv: ""
  url: https://pubmed.ncbi.nlm.nih.gov/39495530/
  year: 2025
leaderboard_url: https://crfm.stanford.edu/helm/medhelm/latest/
repo_url: https://github.com/stanford-crfm/helm
released: "2025-04"
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
    - shc_gip
    - shc_proxy
    - shc_ptbm
    - shc_sei
    - shc_sequoia
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated numeric top exact-match for PrivacyDetection was recovered from a
    parsed leaderboard table.
contamination:
  risk: low
  note: >
    The 300 items are listed as a private dataset. Nature Medicine groups 14
    such private sets, not all from Stanford Health Care. HELM cites Tse et al.
    2025, a public research letter whose full item set is not this CSV.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_privacy_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - privacy
  - patient-portal
  - private-dataset
  - medhelm
  - stanford-health-care
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_privacy_scenario.py
    title: "HELM shc_privacy_scenario.py (SHCPRIVACYMedScenario, PrivacyDetection)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_privacy_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (PrivacyDetection group)"
    accessed: "2026-09-08"
  - url: https://pubmed.ncbi.nlm.nih.gov/39495530/
    title: "Tse et al., JAMA Pediatrics 2025 (PMID 39495530)"
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

PrivacyDetection asks whether a patient-portal message leaks confidential
information. HELM's methods example is a short portal note ("Hi, just wanted to
confirm that my test came…") and a yes/no question about confidential content.
The required answer is A for yes or B for no.

Two HELM texts disagree about how the messages were made. The class docstring
says the messages were generated by an LLM from patient notes, then checked for
confidential content. The published metadata and Nature Medicine table describe
portal messages from patients or caregivers. This page records both readings and
does not pick one.

## How it is scored

HELM uses joint multiple-choice adaptation with "Answer A or B." and exact
match of the letter. The methods appendix also shows a second output format
("privacy-leaking or non-privacy-leaking") in the same PrivacyDetection write-up;
the runnable scenario file still demands A or B. Official MedHELM numbers should
be read as letter exact match unless a report says otherwise. No class prior or
human baseline for the 300 items was found.

## Dataset and licence

Extended Data Table 1 reports 300 instances evaluated, private and new, grouped
with ProxySender as citation ME38. HELM loads
medhelm-PRIVACY-dataset_filtered.csv. All instances are test. The CSV is not
public. No data licence was found. HELM code is Apache 2.0.

## Who publishes it

HELM and MedHELM cite Tse, Zahedivash, Anoshiravani, Carlson, Haberkorn, and
Morse, JAMA Pediatrics, 1 January 2025, DOI 10.1001/jamapediatrics.2024.4438,
PMID 39495530, pages 93-94. PubMed's plain-language summary of that letter is
about telling adolescent patient messages from parent or guardian messages and
then drafting a reply. That is closer to ProxySender than to a leak classifier.
Treat Tse et al. as the cited pediatric-portal paper, not as proof that
PrivacyDetection is the letter's published generation task.

MedHELM (Bedi et al., 2026) hosts the harness. The HELM file was added on
8 April 2025 in the "SHC additional datasets" change, after MedHELM V1.

## Lineage

This is not MedConfInfo (shc_conf), which labels adolescent visit notes for
parental access. It is not ProxySender (shc_proxy), which labels who sent the
message. Both privacy and proxy cite the same 2025 letter and share the ME38
footnote; they remain separate HELM scenarios. Other Stanford Health Care siblings include shc_bmt, shc_cdi, shc_ent, shc_gip,
shc_ptbm, shc_sei, and shc_sequoia. There is no MedHELM family page.

## Saturation and contamination

Saturation is unknown. Contamination risk is low for the private 300 items. The
cited letter is public and short; it could leak task framing without leaking
this CSV.

## How to run it

Run HELM scenario `shc_privacy_med` with the private `data_path`. Stanford
entries are in `run_entries_medhelm_private_stanford.conf`. Adapter
instructions are "Answer A or B." The helper defaults to five shots, but there
is no train split, so the run is effectively zero-shot. Do not compare a
free-text "privacy-leaking" label run with the official A/B exact-match. No
other harness was confirmed.

## Reading the numbers

A high score means the model usually matched the gold yes or no on whether
these 300 messages were judged confidential. It is not a HIPAA certification
and not a jailbreak eval. Because HELM's own description of the source messages
conflicts, check which construction a report used before treating two
PrivacyDetection numbers as the same task. Read it with ProxySender and
MedConfInfo, not with general safety averages.
