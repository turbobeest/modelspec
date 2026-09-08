---
id: shc_cdi
name: CDI-QA
aliases:
  - shc_cdi_med
  - CDI-QA
page_kind: benchmark
category: domain
subcategory: "clinical documentation integrity verification from notes"
status: active
summary: >
  Private Stanford Health Care MedHELM task: verify from a hospital note whether
  a documented clinical condition is supported, answering A for yes or B for no.
measures: >
  CDI-QA tests whether a model can use an English inpatient note to answer a
  clinical documentation integrity (CDI) verification question, such as whether
  a named condition is supported by the chart. HELM places the task under
  Administration and Workflow, care coordination and planning. The census id is
  shc_cdi; the runnable HELM scenario is shc_cdi_med.
task_format: >
  Joint multiple-choice generation. HELM fills a template with the CSV question
  and note and requires A for yes or B for no, with no extra text.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Main metric is exact_match on the test split. Class balance and a human CDI
    specialist baseline were not published for this private set.
dataset:
  size: 1000
  size_note: >
    Nature Medicine Extended Data Table 1 reports 1000 instances evaluated.
    HELM reads a private filtered CSV (medhelm-CDI-dataset_filtered.csv) with
    prompt, context, and label columns and tags every row as test.
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
    - shc_conf
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
    No dated numeric top exact-match for CDI-QA was recovered from a parsed
    leaderboard table. The paper heatmap is an image, not a numeric dump.
contamination:
  risk: low
  note: >
    Listed among the 14 private MedHELM datasets that cannot be redistributed
    because of institutional agreements and patient privacy. Those 14 are not
    all Stanford Health Care records.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_cdi_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - private-dataset
  - medhelm
  - stanford-health-care
  - documentation
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_cdi_scenario.py
    title: "HELM shc_cdi_scenario.py (SHCCDIMedScenario, CDI-QA)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_cdi_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (CDI-QA group)"
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

CDI-QA is a chart-verification task, not a billing-code extractor and not a
diagnosis exam. The model is given an English hospital admission note and a
question that a clinical documentation integrity review would ask, for example
whether the note supports a named condition. HELM's methods example uses
findings relevant to verifying a condition such as acute kidney injury. The
required output is A for yes or B for no.

The work is hospital operations: queries written against prior notes so that a
model, or a human CDI specialist, can confirm that the chart backs a clinical
statement. Language is English. Modality is text.

## How it is scored

HELM uses joint multiple-choice adaptation and exact match of the single letter
to the gold label. The schema lists exact_match on test as the main metric;
quasi-exact and prefix variants are also computed. The paper's gold-standard
example for this task is the letter A. No human CDI-reviewer baseline or class
prior was published, so a 50 percent chance line is not established.

## Dataset and licence

Extended Data Table 1 reports 1000 instances evaluated, private and newly
curated. HELM reads prompt, context, and label from a private CSV named
medhelm-CDI-dataset_filtered.csv in the Stanford run file. All rows become test
instances. The HELM class docstring and Nature Medicine Extended Data Table 1 say
"Clinical Document Integrity." The methods appendix and HELM metadata say
"Clinical Documentation Integrity." This page records both spellings.

The notes are not public. Nature Medicine lists CDI-QA among 14 private
datasets blocked by institutional agreements and patient privacy; that group
is not limited to Stanford Health Care. No data licence was found. HELM code
is Apache 2.0.

## Who publishes it

CDI-QA is a MedHELM private benchmark from Stanford Health Care's partnership
with Stanford CRFM. The peer-reviewed suite paper is Bedi, Cui, Fuentes, Unell
and colleagues, Nature Medicine, 20 January 2026 (arXiv:2505.23802, May 2025).
The journal lists Bedi as corresponding author.
The HELM scenario shipped in MedHELM V1 on 19 March 2025. The live board is
https://crfm.stanford.edu/helm/medhelm/latest/.

## Lineage

This is a new EHR-based administration task, not a reformulation of a public
CDI corpus. It is not MIMIC-IV Billing Code, which asks for ICD-10 codes from
discharge text, and it is not ClinicReferral (shc_sequoia_med), which is a
separate Sequoia clinic referral set. Sibling pages include shc_bmt, shc_conf, shc_ent, shc_gip, shc_privacy,
shc_proxy, shc_ptbm, shc_sei, and shc_sequoia (ClinicReferral). There is no
MedHELM family page.

## Saturation and contamination

Saturation is unknown; this page did not obtain a numeric CDI-QA leaderboard
cell. Contamination risk is low because the item set is private and was built
for MedHELM rather than scraped from a public leaderboard. That does not make
the labels immune to generic clinical-language overlap, only to wholesale
memorization of this CSV.

## How to run it

Run HELM with scenario `shc_cdi_med` and a `data_path` to the private CSV.
Official entries are in `run_entries_medhelm_private_stanford.conf`. Adapter
instructions are "Answer A or B." The multiple-choice helper defaults to five
shots, but the scenario emits only TEST_SPLIT, so HELM's trainer sampler has
nothing to draw and the protocol is effectively zero-shot. Public reproduction
of the 1000-item score is not possible without Stanford's file. No matching
task was confirmed in lm-evaluation-harness, Inspect Evals, OpenCompass, or
BIG-bench.

## Reading the numbers

A strong CDI-QA exact-match means the model usually agreed with the gold yes or
no on these documentation-integrity checks. It does not show that the model can
write a query, code a bill, or catch every clinically unsafe omission. Treat
the number as a single-site operations proxy. Compare it with other MedHELM
administration tasks (ENT-Referral, HospiceReferral, ClinicReferral) scored the
same way, not with ROUGE on note generation.
