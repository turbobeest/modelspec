---
id: shc_sei
name: "ADHD-MedEffects"
aliases:
  - "shc_sei_med"
  - "SEI"
  - "side effects inquiry"
page_kind: benchmark
category: domain
subcategory: "pediatric ADHD clinical-note classification: medication side-effect inquiry"
status: active
summary: "Private MedHELM binary task: given a pediatric ADHD medication-follow-up note, say whether it documents side-effect inquiry."
measures: >
  ADHD-MedEffects (HELM scenario shc_sei_med) tests whether a model can read an English
  pediatric primary-care note and decide if the clinician documented a side effects inquiry
  (SEI) after prescribing ADHD medication. SEI means the note records current side effects
  or an explicit ask about them. It does not include only planning to monitor later or
  counselling about possible future effects. The notes come from Packard Children's Health
  Alliance visits of children aged 6-11 years, 2015-2022, who had at least one ADHD
  medication prescription. Encounters include in-person, telehealth, and telephone notes.
task_format: "Binary A/B classification over a clinical note plus a question; English text; HELM multiple-choice joint adaptation."
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two-way A/B choice gives a 50% random-guess rate. The Pediatrics paper reports LLaMA-13B
    holdout sensitivity 87.2, specificity 86.3, and AUC 0.93 on a 90-note holdout, plus
    Cohen's kappa 0.86 on the first 84 doubly annotated notes. Those figures are for the
    original LLaMA-13B quality-measurement pipeline, not HELM exact-match on the private CSV.
dataset:
  size: 915
  size_note: >
    Nature Medicine Table 1 (PMC13267972) reports 915 instances evaluated for ADHD-MedEffects
    (ME29), private and new. HELM still loads a private CSV (medhelm-SEI-dataset_filtered.csv);
    this page does not independently count that file. The Pediatrics paper annotated 501 notes
    from 119 patients, split 80/20 into train n=411 and holdout test n=90, then sampled 363
    further notes from 15,127 deployment notes for a second test. The study cohort was 1,201
    children and 15,628 ADHD-related notes in total. How the MedHELM 915 relates to those
    paper splits is not established beyond the table.
  url: "https://github.com/ybannett/NLP_ADHD_SEI"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM exposes a single test split from a local CSV; the paper used train 411 / holdout 90 plus a 363-note deployment sample"
  public_test_set: false
publisher:
  org: "Stanford University School of Medicine (Packard Children's Health Alliance / Stanford Medicine Children's Health); packaged in MedHELM by Stanford CRFM"
  authors:
    - "Yair Bannett"
    - "Fatma Gunturkun"
    - "Malvika Pillai"
    - "Jessica E. Herrmann"
    - "Ingrid Luo"
    - "Lynne C. Huffman"
    - "Heidi M. Feldman"
  url: "https://crfm.stanford.edu/helm/medhelm/latest"
paper:
  title: "Applying Large Language Models to Assess Quality of Care: Monitoring ADHD Medication Side Effects"
  arxiv: ""
  url: "https://doi.org/10.1542/peds.2024-067223"
  year: 2024
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_sei_scenario.py"
released: "2024-12"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - shc_ptbm
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM reports this private task, but the public leaderboard did not render a static
    exact-match top score here. Appendix E of the MedHELM arXiv text reports a minimum
    detectable effect of 0.032 ± 0.009 for ADHD-MedEffects, which is a sample-size
    statistic, not an accuracy. The Pediatrics paper's LLaMA-13B holdout AUC 0.93 is a
    different protocol and a different model role (the LLM is the classifier under study,
    not a MedHELM examinee).
contamination:
  risk: low
  note: >
    The Pediatrics paper states the EHR datasets contain protected health information and
    are not publicly available; model code is on GitHub. HELM lists the scenario only in
    run_entries_medhelm_private_stanford.conf. Public pretraining is unlikely to include
    these notes or labels.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "shc_sei_med"
  opencompass: ""
  bigbench: ""
  other: "MedHELM private Stanford run entries; helm-run needs data_path to a local CSV"
tags:
  - biomedical
  - clinical-notes
  - adhd
  - medhelm
  - private
  - classification
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/shc_sei_scenario.py"
    title: "HELM shc_sei_scenario.py (SHCSEIMedScenario)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM medhelm_run_specs.py (shc_sei_med run spec)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "HELM schema_medhelm.yaml (ADHD-MedEffects)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/docs/medhelm.md"
    title: "MedHELM documentation (access levels)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf"
    title: "MedHELM private Stanford run entries (shc_sei_med CSV path)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1542/peds.2024-067223"
    title: "Bannett et al., Pediatrics 2024 (10.1542/peds.2024-067223)"
    accessed: "2026-09-08"
  - url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11978496/"
    title: "PMC11978496 full text of Bannett et al. 2024"
    accessed: "2026-09-08"
  - url: "https://github.com/ybannett/NLP_ADHD_SEI"
    title: "ybannett/NLP_ADHD_SEI code repository README"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.23802"
    title: "MedHELM full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC13267972/"
    title: "MedHELM Nature Medicine author manuscript (PMC13267972), Table 1 instances evaluated"
    accessed: "2026-09-08"
  - url: "https://api.crossref.org/works/10.1542/peds.2024-067223"
    title: "Crossref work 10.1542/peds.2024-067223 (published-online 2024-12-20)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_multiple_choice_adapter_spec default max_train_instances=5"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-002 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-002"
---

## What it measures

ADHD-MedEffects asks a model to read an English pediatric ADHD follow-up note and say whether the clinician documented a side effects inquiry. HELM's prompt defines SEI as explicit asking about current ADHD-medication side effects, or documentation that specific side effects occurred or did not occur. Plans to monitor later, or education about possible future effects without actual monitoring, count as no SEI. The allowed answers are `A` (yes) and `B` (no).

The notes come from Packard Children's Health Alliance children aged 6-11 years, 2015-2022, each prescribed a stimulant or non-stimulant ADHD medicine at least once. In-clinic, telehealth, and telephone encounters are in scope. The original study used this label as a scalable quality metric for guideline-recommended monitoring, not as a public exam.

## How it is scored

HELM scores exact match on A/B (`exact_match`, test split) with multiple-choice joint adaptation and the instruction "Answer A or B." Exact match is a 0–1 fraction; this page writes random guessing as 50% on two options. The helper defaults to five in-context examples, but the scenario tags every CSV row as `TEST_SPLIT`, so the protocol is effectively zero-shot. The Pediatrics paper scored a LLaMA-13B classifier: holdout sensitivity 87.2, specificity 86.3, AUC 0.93 on 90 notes, after an 80/20 split of 501 annotated notes. That is a different role for the LLM (the model *is* the quality measure) and a different metric family than MedHELM exact-match. Inter-annotator kappa was 0.86 on the first 84 doubly labelled notes; that is label reliability, not a human ceiling on the HELM prompt.

## Dataset and licence

HELM reads a local CSV with `prompt`, `context`, and `label`. Private Stanford run entries name `medhelm-SEI-dataset_filtered.csv`. Nature Medicine Table 1 reports 915 instances evaluated. The Pediatrics paper annotated 501 notes (119 patients; 411/90 train/holdout) from a cohort of 1,201 children and 15,628 notes, then annotated 363 of 15,127 remaining notes for deployment testing. The paper states the datasets contain protected health information and are not public; the data-availability paragraph cites `ybannett/NLP_ADHD_SEI`. The methods section of the same PMC article also links `ybannett/NLP_ADHD_PTBM`, which is the sibling PTBM code name; treat `NLP_ADHD_SEI` as the SEI code citation. No SPDX licence for the HELM CSV was published. Nature Medicine lists ADHD-MedEffects among fourteen Stanford Health Care datasets blocked by institutional agreements.

## Who publishes it

The clinical study is by Yair Bannett, Fatma Gunturkun, Malvika Pillai, Jessica E. Herrmann, Ingrid Luo, Lynne C. Huffman, and Heidi M. Feldman, in *Pediatrics* (doi:10.1542/peds.2024-067223; PMID 39701141; PMC11978496). Crossref records published-online as 20 December 2024 and published-print as 1 January 2025. HELM/MedHELM packages the task as `shc_sei_med` with display name ADHD-MedEffects. The MedHELM Nature Medicine paper (20 January 2026; arXiv:2505.23802) lists it as a private, newly formulated benchmark. Bannett is a MedHELM co-author.

## Lineage

This page is the HELM scenario whose census id is `shc_sei`. It is the school-age, medication-monitoring counterpart of `shc_ptbm` (ADHD-Behavior / PTBM recommendations in 4-6-year-olds at the same network). Other `shc_*` MedHELM scenarios share the private SHC CSV pattern but ask different questions. This repository has no MedHELM family page.

## Saturation and contamination

No HELM exact-match top score was read from a static leaderboard. Do not use the MedHELM paper's 0.032 ± 0.009 MDE value as an accuracy. Contamination risk is low: unpublished PHI, private run entries only. The Pediatrics abstract found lower documented SEI in telephone encounters than in clinic/telehealth (51.9% vs 73.0%) and after nonstimulants than stimulants (48.5% vs 61.4%), so a pooled exact-match number can hide those slices. The Results section prints 73.1% for clinic/telehealth and 48.6% after nonstimulants; this page keeps the abstract pair.

## How to run it

Run HELM spec `shc_sei_med` with `data_path` set to the private CSV. Official rows live in `run_entries_medhelm_private_stanford.conf` and require Stanford Health Care access. Adapter instructions are "Answer A or B." The multiple-choice helper defaults to five shots, but only test instances exist, so official rows are effectively zero-shot. HELM's `schema_medhelm.yaml` taxonomy line for this scenario currently says "Classify clinician recommendations for ADHD behavior management", which is the PTBM task; the scenario docstring, display name, and Pediatrics citation describe SEI. The PTBM scenario's taxonomy string is swapped in the same file. Prefer the scenario Python and the paper. No lm-evaluation-harness, inspect_evals, or OpenCompass task was found. Unlike `shc_ptbm`, this scenario file has no `get_metadata()` helper; metadata comes from `schema_medhelm.yaml`.

## Reading the numbers

A high ADHD-MedEffects score means the model often matches chart-review labels for whether a note documents current side-effect monitoring in this network's 6-11-year-old ADHD medication visits. It does not mean the model can manage side effects, choose a stimulant, or work on other EHRs. Do not compare LLaMA-13B's 0.93 holdout AUC to a MedHELM exact-match row. If the clinical question is first-line behavioral treatment in younger children, use `shc_ptbm` instead. If the question is whether a public model can do this at all, the answer is not in a public download: the labels stay inside SHC.
