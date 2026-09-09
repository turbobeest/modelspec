---
id: mimiciv_billing_code
name: "MIMIC-IV Billing Code (MedHELM)"
aliases:
  - "MIMIC-IV Billing Code"
  - "mimiciv_icd10"
page_kind: benchmark
category: domain
subcategory: "ICD-10 billing-code extraction from discharge notes"
status: active
summary: "MedHELM's gated MIMIC-IV task: extract ICD-10 codes from an English discharge note and score micro-F1 against gold codes."
measures: >
  This id is HELM's mimiciv_billing_code scenario, not MIMIC-IV-BHC summarization
  and not MedConceptsQA. The model reads an English clinical note (column text)
  and must list ICD-10 billing codes (column target). HELM extracts code-shaped
  tokens from the generation and compares them to gold as a multi-label set.
  Inputs are English clinical text. Outputs are code strings.
task_format: >
  Zero-shot generation. Instruction: "Given the following clinical note, identify
  all relevant ICD-10 codes." Input noun Note, output noun Predicted ICD-10 Codes,
  max_tokens 256, max_train_instances 0. Some MedHELM gated entries raise
  num_output_tokens to 4000. The scenario tags every row as TEST_SPLIT.
metric:
  name: "mimiciv_billing_code_f1 (micro-F1 over extracted ICD-10 codes)"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml names mimiciv_billing_code_f1 on test (display name
    MIMICBillingF1). The metric also logs precision and recall. Codes are parsed
    with a regex (letter plus digits, optional dotted suffix), markdown bold is
    stripped, and sklearn micro-F1 is computed after multi-label binarization.
    The MedHELM paper describes micro-F1 for ICD-10 assignment. No random or
    human baseline is stated in the metric file.
dataset:
  size: null
  size_note: >
    HELM reads a local Feather file with columns text and target. Official gated
    runs use /share/pi/nigam/data/medhelm/mimiciv_billing_codes/mimiciv_icd10.feather.
    The row count of that file is not published in the scenario or in the opened
    MedHELM table text. MedHELM lists the benchmark as gated and existing, derived
    from MIMIC-IV discharge summaries paired with ICD-10 codes.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM test-only from a gated Feather file of unpublished size"
  public_test_set: false
publisher:
  org: "Stanford CRFM and collaborators (MedHELM); notes from MIMIC-IV"
  authors:
    - "Suhana Bedi"
    - "Hejie Cui"
    - "Miguel Fuentes"
    - "Alyssa Unell"
  url: https://crfm.stanford.edu/helm/medhelm/latest
paper:
  title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks"
  arxiv: "2505.23802"
  url: https://arxiv.org/abs/2505.23802
  year: 2025
leaderboard_url: https://crfm.stanford.edu/helm/medhelm/latest
repo_url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mimiciv_billing_code_scenario.py
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mimic_bhc
    - mimic_rrs
    - mimic_repsum
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The MedHELM paper singles this task out as one of the harder suite members
    and plots normalized 0-1 heatmap cells, not a raw F1 ceiling. No numeric
    MIMICBillingF1 top was read from the JavaScript leaderboard.
contamination:
  risk: medium
  note: >
    The HELM Feather file is gated. MIMIC-IV discharge text is widely reused in
    credentialed clinical NLP, so note language may still overlap training data
    even when this eval file is not public.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mimiciv_billing_code"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec mimiciv_billing_code. Metric class MIMICIVBillingCodeMetric. Official
    entries in run_entries_medhelm_gated.conf with data_path to mimiciv_icd10.feather.
tags:
  - medical
  - icd-10
  - coding
  - helm
  - medhelm
  - gated
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/mimiciv_billing_code_scenario.py
    title: "HELM mimiciv_billing_code_scenario.py"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/mimiciv_billing_code_metrics.py
    title: "HELM MIMICIVBillingCodeMetric (micro-F1 regex extractor)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (mimiciv_billing_code run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (mimiciv_billing_code_f1)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_gated.conf
    title: "HELM gated MedHELM run entries (mimiciv_icd10.feather)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2505.23802
    title: "MedHELM paper (arXiv:2505.23802)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2505.23802v2
    title: "MedHELM HTML (Appendix C: MIMIC-IV Billing Code Gated, Existing; harder heatmap column)"
    accessed: "2026-09-08"
  - url: https://crfm.stanford.edu/helm/medhelm/latest/
    title: "HELM MedHELM leaderboard shell (JavaScript; no numeric cells in HTML)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`mimiciv_billing_code` is MedHELM's ICD-10 assignment task. The model reads an English discharge note and must emit the billing codes for that stay. HELM then parses code-like tokens from the free text. The skill is multi-label clinical coding, not note summarization and not multiple-choice concept QA.

Appendix C of arXiv:2505.23802v2 lists MIMIC-IV Billing Code as Gated and Existing, built from MIMIC-IV notes paired with ICD-10 codes. The public HELM tree does not include the Feather rows.

## How it is scored

The headline metric is `mimiciv_billing_code_f1`, micro-F1 over unique extracted codes, with matching precision and recall. The extractor looks for tokens such as `J18.9` after stripping markdown bold. Gold lists in the Feather file are joined with commas, then parsed with the same regex. Unparseable model text yields empty predictions. Scores are fractions in 0-1. No random or human baseline is stated. The MedHELM paper's normalized heatmap is a different display scale.

## Dataset and licence

HELM loads `mimiciv_icd10.feather` from a caller `data_path`. Official gated entries use a Stanford MedHELM path. The row count was not published in the opened scenario, metric, or arXiv table text. A separate PhysioNet landing page for this exact Feather extract was not opened. MIMIC-IV itself is credentialed health data; no licence string for the HELM extract was found. HELM code is Apache-2.0.

## Who publishes it

The wrap is part of MedHELM (arXiv:2505.23802, 26 May 2025), from Stanford CRFM with medical collaborators. Equal first authors on that paper include Suhana Bedi, Hejie Cui, Miguel Fuentes and Alyssa Unell. Underlying notes come from MIMIC-IV. CRFM hosts the leaderboard.

## Lineage

This is not [mimic_bhc](mimic_bhc.md), which writes a Brief Hospital Course and uses a jury. It is not [mimic_rrs](mimic_rrs.md) or [mimic_repsum](mimic_repsum.md). It is not [med_concepts_qa](med_concepts_qa.md), which asks multiple-choice questions about named codes. Sibling MedHELM administration tasks include [shc_cdi](shc_cdi.md). There is no MedHELM family page.

## Saturation and contamination

Saturation is unknown. The paper flags this task as relatively hard in the 35-benchmark suite, which is not a ceiling reading. Contamination risk is medium: the eval file is gated, but MIMIC-IV notes are a standard credentialed corpus in clinical NLP.

## How to run it

Run HELM with scenario `mimiciv_billing_code` and a `data_path` to the Feather file. Official entries are in `run_entries_medhelm_gated.conf`. The adapter is zero-shot with a 256-token cap unless a run overrides it. Public reproduction needs PhysioNet-style access to the notes and the pairing file. No matching lm-eval, Inspect, OpenCompass or BIG-bench task was confirmed.

## Reading the numbers

A high micro-F1 means the regex found the same ICD-10 tokens as the gold list, not that a coder would bill the stay that way. Extra prose, missing dots, or truncated lists hurt the score. It does not measure summary quality or exam knowledge. Pair it with a human-coded sample if coding quality matters, and do not mix it with MIMIC-BHC jury points.
