---
id: shc_proxy
name: ProxySender
aliases:
  - shc_proxy_med
  - ProxySender
page_kind: benchmark
category: domain
subcategory: "patient versus proxy sender of portal messages"
status: active
summary: >
  Private MedHELM task: decide whether a clinician-facing portal message was
  sent by the patient or by a proxy such as a parent or spouse.
measures: >
  ProxySender tests whether a model can read an English patient-portal message
  sent to a clinician and decide if a proxy user (parent, spouse, or other
  caregiver) sent it rather than the patient. HELM's example is a message that
  begins "Hi Dr. Lee, this is Jane's mom." The census id is shc_proxy; the
  runnable HELM scenario is shc_proxy_med.
task_format: >
  Joint multiple-choice generation. The instance prompt still says A for yes
  (proxy) or B for no. After 16 October 2025 the adapter also names C as a
  legal letter, while the prompt text was not updated to define C.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Main metric is exact_match. Gold labels are asserted to be in {A, B, C}
    after the October 2025 fix. Class mix and a human baseline for the 300
    items were not published.
dataset:
  size: 300
  size_note: >
    Nature Medicine Extended Data Table 1 reports 300 instances evaluated,
    private and new, cited as ME38 with PrivacyDetection. HELM reads
    medhelm-PROXY-dataset_filtered.csv with prompt, context, and label.
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
last_updated: "2025-10"
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
    - shc_privacy
    - shc_ptbm
    - shc_sei
    - shc_sequoia
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated numeric top exact-match for ProxySender was recovered from a
    parsed leaderboard table. The October 2025 label-set change can make older
    and newer runs hard to compare.
contamination:
  risk: low
  note: >
    The 300 items are a private dataset. Nature Medicine groups 14 such private
    sets, not all from Stanford Health Care. The cited 2025 research letter is
    public but is not a download of this CSV.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: shc_proxy_med
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - classification
  - patient-portal
  - pediatrics
  - private-dataset
  - medhelm
  - stanford-health-care
sources:
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_proxy_scenario.py
    title: "HELM shc_proxy_scenario.py (SHCPROXYMedScenario, ProxySender)"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/commit/a363f41c
    title: "HELM commit Fix Proxy scenario (#3911), 2025-10-16"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (shc_proxy_med run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM run_entries_medhelm_private_stanford.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (ProxySender group)"
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

ProxySender asks who wrote a message that landed in a clinician's inbox: the
patient, or a proxy such as a parent or spouse. HELM's example is a portal
message that identifies the sender as "Jane's mom." The published MedHELM
prompt asks whether the message was sent by a proxy user, with A for yes and B
for no. Language is English. Modality is text.

This is a sender-identity screen, not a clinical-advice generator. PubMed's
summary of the cited letter also mentions drafting an appropriate reply; HELM's
scenario does not score that generation step.

## How it is scored

HELM scores exact match of the output letter to the gold label. The Nature
Medicine methods text still shows a binary A/B prompt and a binary gold
example. On 16 October 2025, HELM pull request 3911 changed
POSSIBLE_ANSWER_CHOICES from [A, B] to [A, B, C] and changed adapter
instructions to "Answer A, B, or C." The instance prompt in
`create_benchmark` still tells the model to answer A for yes or B for no and
never defines C. A report should say which code revision it used. No class
prior or human baseline for the 300 items was published.

## Dataset and licence

Extended Data Table 1 reports 300 instances evaluated, private and new, cited
with PrivacyDetection as ME38. HELM loads medhelm-PROXY-dataset_filtered.csv
with prompt, context, and label, and tags every row as test. The messages are
Stanford Health Care portal text and are not released. No data licence was
found. HELM code is Apache 2.0.

## Who publishes it

The cited letter is Tse, Zahedivash, Anoshiravani, Carlson, Haberkorn, and
Morse, JAMA Pediatrics, 1 January 2025, DOI 10.1001/jamapediatrics.2024.4438,
PMID 39495530, pages 93-94. HELM added the scenario on 8 April 2025. MedHELM
(Bedi et al., Nature Medicine 2026; arXiv 2505.23802) reports the suite score.
Taxonomy: Patient Communication and Education, patient-provider messaging.

## Lineage

ProxySender is not PrivacyDetection, which asks whether a message leaks
confidential facts, and not MedConfInfo, which screens adolescent visit notes
for parental access. Those three tasks are related pediatric communication
checks, not one evaluation under three names. Other Stanford Health Care siblings include shc_bmt, shc_cdi, shc_ent, shc_gip,
shc_ptbm, shc_sei, and shc_sequoia. There is no MedHELM family page.

## Saturation and contamination

Saturation is unknown. The October 2025 third-label change is a further reason
not to treat early and late HELM runs as one series. Contamination risk is low
for the private CSV. The public letter could leak the idea of the task without
leaking these 300 messages.

## How to run it

Run HELM scenario `shc_proxy_med` with the private `data_path`. Stanford
entries are in `run_entries_medhelm_private_stanford.conf`. Current adapter
instructions are "Answer A, B, or C." The instance string still says A or B.
The multiple-choice helper defaults to five shots, but only a test split
exists, so the run is effectively zero-shot. Pin the HELM revision when
comparing scores. No lm-eval, Inspect, OpenCompass, or BIG-bench twin was
confirmed.

## Reading the numbers

A high exact-match score means the model usually matched the gold sender label
on these 300 portal messages under HELM's letter protocol. It does not mean the
model wrote a safe reply, which the cited letter also discusses and HELM does
not score here. Check whether C was a legal label in that run, and read the
number next to PrivacyDetection rather than as a general pediatric-chat score.
