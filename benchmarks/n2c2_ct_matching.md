---
id: n2c2_ct_matching
name: "N2C2-CT Matching (HELM)"
aliases:
  - "N2C2-CT"
  - "n2c2 2018 Track 1"
  - "n2c2 cohort selection"
page_kind: benchmark
category: domain
subcategory: "HELM MedHELM wrap of n2c2 2018 clinical-trial cohort selection"
status: active
summary: "MedHELM yes/no matching of n2c2 2018 patients to one inclusion criterion from de-identified notes, scored with exact match."
measures: >
  n2c2_ct_matching is HELM's MedHELM scenario for the 2018 n2c2 Track 1 cohort-selection task.
  The model reads 2–5 de-identified English notes for one patient and must say whether that
  patient meets a single named inclusion criterion (for example ADVANCED-CAD or HBA1C). Labels
  are patient-level met / not met from Stubbs et al. 2019. HELM's prompt text follows Wornow et
  al. 2024, with expanded criterion definitions. Official gated run entries only instantiate
  three of the thirteen criteria. This is note-based eligibility, not de-identification and not
  the SHC privacy scenarios.
task_format: >
  Zero-shot joint multiple choice. Adapter instructions "Answer A for yes, B for no."
  max_train_instances 0. Scenario references are the strings "yes" and "no". Run spec name
  n2c2_ct_matching:subject={CRITERION}. data_path must point at local train/ and test/ XML
  folders. get_instances currently loads only the test split.
metric:
  name: "exact_match (HELM schema); n2c2 literature uses micro/macro F1 on met vs not-met"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Criteria are badly unbalanced (Stubbs table: KETO-1YR had one met label, later called an
    annotation error), so 50% is not a fair chance rate. The 2018 challenge ranked systems on
    overall micro-averaged F1 (met F1 averaged with not-met F1). Wornow et al. Table 1 reports
    GPT-4 0.93 overall micro-F1 and 0.81 overall macro-F1 with their ACIN prompt, not HELM's
    exact_match column. Prior SOTA in that table is 0.91 micro-F1 / 0.75 macro-F1. Annotator
    Cohen's kappa on the original labels was 0.54 (Wornow citing Stubbs). Those F1 figures are
    not HELM exact_match.
dataset:
  size: 288
  size_note: >
    Stubbs et al. 2019 / Wornow et al. 2024: 288 patients, 202 train (70%) and 86 test, each with
    2–5 notes (Wornow: mean 2,711 words). Thirteen inclusion criteria, no exclusion criteria.
    Source notes are the 2014 i2b2/UTHealth longitudinal narratives; patients are diabetic
    records from Mass General and Brigham and Women's. HELM official
    run_entries_medhelm_gated.conf only lists subjects ABDOMINAL, ADVANCED-CAD and CREATININE
    against a private Stanford path. The scenario class can take any of the 13 keys in
    LONG_DEFINITIONS. XML is not in the HELM repo.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/n2c2_ct_matching_scenario.py"
  license: "n2c2 data-use agreement (notes are not public); HELM code Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "original train 202 / test 86; HELM scenario emits test only; main_split test"
  public_test_set: false
publisher:
  org: "n2c2 / Harvard DBMI (dataset); Stanford CRFM (HELM MedHELM scenario)"
  authors:
    - "Amber Stubbs"
    - "Michele Filannino"
    - "Ergin Soysal"
    - "Samuel Henry"
    - "Özlem Uzuner"
  url: "https://doi.org/10.1093/jamia/ocz163"
paper:
  title: "Cohort selection for clinical trials: n2c2 2018 shared task track 1"
  arxiv: ""
  url: "https://doi.org/10.1093/jamia/ocz163"
  year: 2019
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/n2c2_ct_matching_scenario.py"
released: "2018"
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
    2018 challenge: 47 teams; top systems near 0.91 micro-F1 (Oleynik et al. rule system, cited
    by Wornow as prior SOTA 0.91 micro / 0.75 macro). Wornow Table 1 GPT-4 ACIN is 0.93 micro-F1
    / 0.81 macro-F1, not a MedHELM exact_match cell. The MedHELM board was not read as a number
    here. Official HELM rows cover three criteria, not thirteen.
contamination:
  risk: low
  note: >
    Notes are distributed under an n2c2 data-use agreement and are not in the public HELM tree.
    Gated MedHELM entries use /share/pi/nigam/data/medhelm/n2c2_ct_matching. Criterion names and
    definitions are public in the papers and in the scenario file. Pretraining on the raw notes
    is unlikely for models without that DUA.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "n2c2_ct_matching"
  opencompass: ""
  bigbench: ""
  other: >
    MedHELM run spec get_n2c2_ct_matching_spec in medhelm_run_specs.py. schema_medhelm.yaml
    group n2c2_ct_matching, display name N2C2-CT Matching, main_metric exact_match, main_split
    test, taxonomy Medical Research Assistance. Official rows in
    run_entries_medhelm_gated.conf.
tags:
  - medhelm
  - clinical
  - eligibility
  - n2c2
  - gated
  - classification
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/n2c2_ct_matching_scenario.py"
    title: "HELM n2c2_ct_matching_scenario.py (288 patients, 13 criteria, Wornow prompt, test-only loader)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "medhelm_run_specs.py get_n2c2_ct_matching_spec (A/B joint MC, 0-shot, exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml N2C2-CT Matching group"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_gated.conf"
    title: "run_entries_medhelm_gated.conf (subjects ABDOMINAL, ADVANCED-CAD, CREATININE)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1093/jamia/ocz163"
    title: "Stubbs et al., JAMIA 2019, n2c2 2018 Track 1 (Crossref abstract: 288 patients, 13 criteria)"
    accessed: "2026-09-08"
  - url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6798568/"
    title: "PMC6798568 Stubbs et al. (202 train / 86 test, 47 teams, criterion list)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.05125"
    title: "Wornow et al., Zero-Shot Clinical Trial Patient Matching with LLMs (arXiv:2402.05125)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.05125"
    title: "Wornow et al. HTML (splits, Table 1 GPT-4 ACIN 0.93/0.81 F1, kappa 0.54)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest/"
    title: "MedHELM leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-061 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-061"
---

## What it measures

n2c2_ct_matching asks whether one patient meets one clinical-trial inclusion rule, using only that patient's de-identified notes. HELM concatenates the notes with dates, names the criterion, pastes a long definition, and asks a yes/no question. The thirteen rules come from real trial language (drug abuse, HbA1c band, recent MI, English-speaking, and others) and were annotated for the 2018 n2c2 Track 1 shared task. Notes are American English longitudinal narratives originally used in the 2014 i2b2/UTHealth set. HELM's wording follows Wornow et al. 2024 rather than the short original definitions. This is eligibility classification, not [shc_privacy](shc_privacy.md) de-identification.

## How it is scored

MedHELM's schema headline is exact match on the test split. The run spec uses joint multiple choice with instructions to answer A for yes and B for no, zero in-context notes. The 2018 shared task and Wornow instead report micro- and macro-averaged F1 on met versus not-met, because several criteria are rare. Wornow Table 1's GPT-4 0.93 micro-F1 / 0.81 macro-F1 is that paper's ACIN (all criteria, individual notes) system, not this adapter. Do not convert F1 into HELM exact match. There is no usable 50% chance line once class skew is in play.

## Dataset and licence

288 patients, 202 train and 86 test, 13 binary labels each. Stubbs et al. describe 47 participating teams. HELM does not ship the XML; gated Stanford entries point at an internal path. Official `run_entries_medhelm_gated.conf` only names ABDOMINAL, ADVANCED-CAD and CREATININE, so a MedHELM row may be three criteria rather than thirteen. The scenario's `get_instances` skips the train folder even though `max_train_instances` is already 0. Notes sit under an n2c2 data-use agreement. HELM's repository is Apache-2.0; that does not license the records.

## Who publishes it

The dataset is the 2018 National NLP Clinical Challenges Track 1, organized around Harvard DBMI / n2c2, with the overview paper by Amber Stubbs, Michele Filannino, Ergin Soysal, Samuel Henry and Özlem Uzuner (JAMIA, November 2019, DOI 10.1093/jamia/ocz163). HELM's scenario and MedHELM board are Stanford CRFM. Wornow, Lozano, Dash, Jindal, Mahaffey and Shah (arXiv:2402.05125; NEJM AI 2024) supply the prompt formulation HELM copies.

## Lineage

Track 1 reused 2014 i2b2/UTHealth narratives and framed them as trial cohort selection. Wornow turned the same labels into a zero-shot LLM matching benchmark. HELM MedHELM then wrapped that prompt as `n2c2_ct_matching`. It is not a family page, and it is not the other n2c2 tracks (de-identification, ADE). No predecessor id in this repository.

## Saturation and contamination

Rule-based 2018 systems already sat near 0.91 micro-F1. Wornow's GPT-4 ACIN run reached 0.93 micro-F1 and 0.81 macro-F1 under a different prompt than HELM. Whether MedHELM exact match still separates current models on the three gated criteria was not read off the live board. Notes are gated, so training-set leakage of the XML is a smaller risk than for public JSON tasks; criterion text is public.

## How to run it

Install HELM, obtain the n2c2 2018 XML under a DUA, and run spec `n2c2_ct_matching` with `data_path` and `subject`. Official reproductions use `run_entries_medhelm_gated.conf` and Stanford Health Care deployments. There is no lm-evaluation-harness, inspect_evals or OpenCompass task. Compare only rows that name the same `subject` list.

## Reading the numbers

A high MedHELM exact-match on this id means the model answered A/B in line with the met/not-met tag for the criteria that were actually run, usually three in the gated file. It is not Wornow's F1, not the 2018 challenge ranking, and not performance on the ten criteria those entries omit. Rare labels (ketoacidosis, decision-making) can dominate error analysis. Look at per-criterion cells, and look at a second clinical-notes task before treating the number as general chart-review skill.
