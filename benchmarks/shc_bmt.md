---
id: shc_bmt
name: BMT-Status
aliases:
  - shc_bmt_med
  - BMT-Status
page_kind: benchmark
category: domain
subcategory: "bone marrow transplant status from clinical notes"
status: active
summary: >
  Private Stanford Health Care MedHELM task: given a hematology note, answer yes or no
  on whether the patient later received a bone marrow or stem-cell transplant.
measures: >
  BMT-Status tests whether a model can read an English clinical note from a
  hematology or oncology consultation and answer a binary question about bone
  marrow transplant (BMT), hematopoietic stem cell transplant (HSCT), or
  hematopoietic cell transplant (HCT) status. HELM's published goal is to decide
  whether the patient received a subsequent transplant from the documentation
  alone. The harness id is shc_bmt; the runnable HELM scenario is shc_bmt_med.
task_format: >
  Joint multiple-choice generation. HELM wraps a CSV prompt and note as one
  English string and requires a single token, A for yes or B for no, with no
  extra text.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's schema lists exact_match on the test split as the main metric, with
    quasi and prefix exact-match variants also recorded. Label balance and a
    human rater baseline were not published for this private set.
dataset:
  size: 220
  size_note: >
    Nature Medicine Extended Data Table 1 reports 220 instances evaluated.
    That is the published evaluation count, not a counted CSV. The file is a
    private filtered CSV (medhelm-BMT-dataset_filtered.csv) with prompt,
    context, and label columns. HELM tags every loaded row as test.
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
    - shc_cdi
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
    MedHELM publishes a per-benchmark heatmap, but this page did not recover a
    dated numeric top exact-match for BMT-Status from that figure or from a
    parsed leaderboard table.
contamination:
  risk: low
  note: >
    Nature Medicine lists BMT-Status among 14 private datasets that cannot be
    shared because of institutional agreements and patient privacy, and says
    private sets are held out to limit training inclusion. Those 14 are not all
    Stanford Health Care records.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_bmt_med
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
  - transplant
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_bmt_scenario.py
    title: "HELM shc_bmt_scenario.py (SHCBMTMedScenario, BMT-Status)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_bmt_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (BMT-Status group)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2505.23802
    title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks (arXiv:2505.23802)"
    accessed: "2026-09-08"
  - url: https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/
    title: "Holistic evaluation of large language models for medical tasks with MedHELM (PMC author manuscript)"
    accessed: "2026-09-08"
  - url: https://crfm-helm.readthedocs.io/en/latest/medhelm/
    title: "MedHELM documentation (access levels and private run entries)"
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

BMT-Status asks a model to read a real English hematology or oncology note and
answer a yes-or-no question about transplant status. HELM's scenario text says
the notes concern bone marrow transplant, hematopoietic stem cell transplant, or
hematopoietic cell transplant, and that the target is whether the patient later
received another transplant. The class docstring adds that the gold labels come
from post-transplant status questions, not from a public exam set.

The input is text only. HELM concatenates the CSV question and the note into one
prompt and forbids any answer other than A (yes) or B (no). This is a closed
chart-review item, not free-text generation and not a USMLE-style knowledge
question.

## How it is scored

HELM scores the task with exact match of the generated letter to the gold label,
and also logs quasi-exact and prefix exact-match variants. The schema names
exact_match on the test split as the main metric. Scores are a fraction in
0-1. The Nature Medicine suite heatmap normalizes closed-ended scores to the
same 0-1 scale for display; the live leaderboard is described as showing the
unnormalized metric.

No published random or human baseline for this private set was found. Because
the labels are A or B, a coin-flip number would only be valid if the two classes
were equally common, which was not reported.

## Dataset and licence

Nature Medicine Extended Data Table 1 lists 220 instances evaluated, access
level private, curation status new. HELM loads a caller-supplied CSV with
columns prompt, context, and label, and the Stanford private run file points at
medhelm-BMT-dataset_filtered.csv. Every instance is tagged as the test split.
The scenario does not publish a train split.

The notes are Stanford Health Care EHR text. A table note says "instances
evaluated" is the subset used for scoring, capped near 1,000 for larger sets.
The paper says 14 datasets cannot be shared because of institutional agreements
and patient privacy; that group also includes non-Stanford private sets such as
NoteExtract (Nigeria) and MentalHealth (India). No licence string for the CSV
was found. HELM's evaluation code is Apache 2.0; that licence does not cover
the private notes.

## Who publishes it

The task sits in MedHELM, a Stanford CRFM and Stanford Health Care collaboration
with Microsoft Health and Life Sciences, coordinated by the Center for
Biomedical Informatics Research. Equal first authors on the peer-reviewed paper
are Suhana Bedi, Hejie Cui, Miguel Fuentes, and Alyssa Unell. The Nature
Medicine article lists Bedi as corresponding author; Nigam H. Shah is last
author. The preprint (arXiv:2505.23802) appeared 26 May 2025; the
Nature Medicine article is dated 20 January 2026 (issue March 2026). The HELM
scenario file entered the public repository with MedHELM V1 on 19 March 2025.
CRFM hosts the leaderboard.

## Lineage

BMT-Status is one of the new private Stanford Health Care tasks added so
MedHELM could cover hospital work that public exam sets miss. In the published
taxonomy it sits under Medical Research Assistance, subcategory Recording
research processes, not under Administration. It is not an alias of MedQA,
PubMedQA, or any other public transplant quiz.

Sibling Stanford Health Care HELM scenarios in this repository include shc_cdi
(CDI-QA), shc_conf (MedConfInfo), shc_ent (ENT-Referral), shc_gip
(HospiceReferral), shc_privacy (PrivacyDetection), shc_proxy (ProxySender),
shc_ptbm (ADHD-Behavior), shc_sei (ADHD-MedEffects), and shc_sequoia
(ClinicReferral). There is no MedHELM family page.

## Saturation and contamination

Saturation is not established. MedHELM reports overall win rates and a heatmap
across the suite, but this page could not read a numeric BMT-Status exact-match
from that figure. Contamination risk is low relative to public exam sets: the
authors keep these notes private specifically to reduce training-data inclusion
and to test generalization beyond public medical benchmarks. The 14 private
MedHELM datasets are not all from Stanford Health Care.

## How to run it

The reference run spec is `shc_bmt_med` in stanford-crfm/helm. It requires a
local `data_path` to the private CSV. Official Stanford runs live in
`run_entries_medhelm_private_stanford.conf`. The adapter is joint
multiple-choice with instructions "Answer A or B." HELM's multiple-choice helper
defaults to five in-context examples, but this scenario emits only a test split,
so the in-context sampler has no train instances and the run is effectively
zero-shot.

Outsiders cannot reproduce the official numbers without the CSV. MedHELM's docs
say private-set scores are produced inside Stanford's secure environment;
external models can be submitted for that run via the HELM repository. No
lm-evaluation-harness, Inspect Evals, OpenCompass, or BIG-bench task with this
item set was confirmed.

## Reading the numbers

A high exact-match score means the model usually picked the gold yes or no on
these 220 transplant-status items under HELM's single-letter protocol. It does
not mean the model is safe to use for transplant registry work: the notes are
from one health system, the labels are not public, and the metric ignores
calibrated uncertainty. Compare it with other private Stanford referral and
status tasks in the same suite, not with MedQA accuracy. If two reports disagree,
check that both used `shc_bmt_med` exact match and the same private file.
