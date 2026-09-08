---
id: shc_ent
name: ENT-Referral
aliases:
  - shc_ent_med
  - ENT-Referral
page_kind: benchmark
category: domain
subcategory: "ear, nose, and throat specialist referral from notes"
status: active
summary: >
  Private Stanford Health Care MedHELM task: from a clinical note, answer whether
  an ENT referral is supported, with A yes, B no, or C no mention.
measures: >
  ENT-Referral tests whether a model can read an unstructured English clinical
  note and decide if the note supports referring the patient to an ear, nose,
  and throat (ENT) specialist. Unlike the binary Stanford Health Care tasks,
  HELM allows a third label, C, for no mention of referral. The census id is
  shc_ent; the runnable HELM scenario is shc_ent_med.
task_format: >
  Joint multiple-choice generation. HELM prefixes a running item counter, then
  asks for A (yes), B (no), or C (no mention), with no extra text.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Main metric is exact_match among A, B, and C. A one-third chance baseline
    would require equal class sizes, which were not published.
dataset:
  size: 1000
  size_note: >
    Nature Medicine Extended Data Table 1 reports 1000 instances evaluated.
    HELM reads medhelm-ENT-dataset_filtered.csv and skips rows whose label cell
    is empty, with a code comment "skip rows with character/encoding issues - 79"
    whose exact meaning (skipped-row count versus an issue id) is not established.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "test only (HELM TEST_SPLIT); empty-label rows dropped; no train split"
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
    No dated numeric top exact-match for ENT-Referral was recovered from a
    parsed leaderboard table.
contamination:
  risk: low
  note: >
    Listed among the 14 private MedHELM datasets that are not redistributed,
    which limits verbatim training leakage of this item set. Those 14 are not
    all Stanford Health Care records.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_ent_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - referral
  - private-dataset
  - medhelm
  - stanford-health-care
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_ent_scenario.py
    title: "HELM shc_ent_scenario.py (SHCENTMedScenario, ENT-Referral)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_ent_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (ENT-Referral group)"
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

ENT-Referral asks whether a patient's note supports sending that patient to an
ear, nose, and throat specialist. HELM's methods example is a 52-year-old with
recurrent sinus infections and nasal complaints. The model must choose A if a
referral is supported, B if it is not, or C if the note never mentions the
issue. That third option is the main protocol difference from binary Stanford
Health Care tasks such as CDI-QA or HospiceReferral.

The input is an English consultation note. The skill is referral triage from
unstructured text, not otolaryngology board-style knowledge.

## How it is scored

The run spec instructs the model to "Answer A, B, or C." HELM scores exact
match of that letter. The paper describes the metric as the fraction of
instances whose classification matches the reference, including the
no-mention class. No published class mix was found, so a 33 percent chance
line is not established. Quasi-exact and prefix exact-match are recorded
alongside exact_match.

## Dataset and licence

Extended Data Table 1 reports 1000 instances evaluated, private and new. HELM
loads medhelm-ENT-dataset_filtered.csv. The scenario skips rows with an empty
label and comments "skip rows with character/encoding issues - 79". Whether 79
is a skipped-row count, a ticket id, or something else was not established;
the paper's 1000 is the figure this page uses for size.

The notes are Stanford Health Care EHR text and are not released. No data
licence was found. HELM code is Apache 2.0.

## Who publishes it

ENT-Referral is a new MedHELM administration benchmark from the Stanford
Health Care and CRFM collaboration (Bedi, Cui, Fuentes, Unell, Shah and
colleagues). The preprint is arXiv:2505.23802 (May 2025); the journal article
is Nature Medicine, 20 January 2026. The HELM scenario was added with MedHELM
V1 on 19 March 2025. Taxonomy: Administration and Workflow, care coordination
and planning.

## Lineage

This is not a public ENT exam set and not ClinicReferral (shc_sequoia_med),
which targets the Sequoia clinic from palliative notes. It is also not
HospiceReferral (shc_gip), which is a binary hospice-eligibility task. Sibling pages include shc_bmt, shc_cdi, shc_conf, shc_gip, shc_privacy,
shc_proxy, shc_ptbm, shc_sei, and shc_sequoia (ClinicReferral). There is no
MedHELM family page.

## Saturation and contamination

Saturation is unknown without a parsed per-task top score. Contamination risk
is low because the CSV is private. The three-way label set also makes
accidental copying from binary yes/no medical quizzes less likely to transfer
cleanly.

## How to run it

Run HELM scenario `shc_ent_med` with the private `data_path`. Stanford entries
are in `run_entries_medhelm_private_stanford.conf`. Adapter instructions are
"Answer A, B, or C." HELM also prepends a 1-based counter to each prompt, so a
reimplementation that drops that counter is not the same task. The adapter
defaults to five shots, but only a test split exists, so the official protocol
is effectively zero-shot. No other harness was confirmed.

## Reading the numbers

A high score means the model usually picked the gold yes, no, or no-mention
label on these ENT triage notes. It does not mean the model should auto-place
referrals: C (no mention) is a valid gold class, and a model that never uses C
can look strong on a two-class subset while failing the published protocol.
Compare only with other MedHELM exact-match referral tasks, and check that the
run allowed three letters.
