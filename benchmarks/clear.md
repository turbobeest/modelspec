---
id: clear
name: CLEAR (MedHELM)
aliases:
  - CLinical Entity Augmented Retrieval
  - MedHELM CLEAR
page_kind: benchmark
category: domain
subcategory: three-way history classification from English clinical notes (MedHELM)
status: active
summary: "MedHELM three-way classification of whether a clinical note supports, denies, or is uncertain about a patient's history of one of 13 conditions."
measures: >
  clear is HELM's MedHELM scenario that asks a model to read an English clinical
  note and decide whether the patient has a history of one named condition.
  Each condition is a separate run. The thirteen conditions are alcohol
  dependence, ADHD, bipolar disorder, chronic pain, homelessness, liver disease,
  major depression, personality disorder, PTSD, substance use disorder, suicidal
  behavior, tobacco dependence, and unemployment. The paper HELM cites is a
  retrieval method (CLinical Entity Augmented Retrieval) evaluated on labeled
  notes; HELM does not run that RAG pipeline. It scores a three-way letter
  choice on the notes themselves.
task_format: >
  Zero-shot joint multiple choice. HELM instructions name A/B/C for has history,
  does not, or uncertain. max_train_instances=0 and max_tokens=1 in the run spec.
  The scenario also embeds the same three options in the input. Private Stanford
  MedHELM entries cap evaluation at 100 instances per condition and pass a local
  data_path of per-condition .xlsx files.
metric:
  name: exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Three letter options would be one-in-three only if labels were uniform; HELM
    does not publish a class prior, so no numeric chance rate is stored.
    Lopez et al. report F1 for their RAG extractor, not exact-match letter
    accuracy on this prompt, so those F1 figures are not a HELM baseline.
dataset:
  size: null
  size_note: >
    Per-condition counts are not in the HELM scenario. Files are named
    {condition}.xlsx with columns text and result_human (1 / 0 / 2). Lopez et al.
    evaluate 18 variables on about 20,000 notes across Stanford MOUD (13
    clinical variables) and CheXpert imaging labels. HELM's thirteen names match
    the MOUD-style clinical set, not the chest-x-ray labels. MedHELM private
    run entries are not a dataset card: they set max_eval_instances=100.
  url: "https://www.nature.com/articles/s41746-024-01377-1"
  license: "CC BY 4.0 (paper); clinical notes are not a public dump"
  languages:
    - en
  modalities:
    - text
  splits: "HELM assigns every loaded row to test (zero-shot); no public train/test files"
  public_test_set: false
publisher:
  org: Stanford University School of Medicine; MedHELM / Stanford CRFM wrap
  authors:
    - Ivan Lopez
    - Akshay Swaminathan
    - Karthik Vedula
    - Sanjana Narayanan
    - Fateme Nateghi Haredasht
    - Stephen P. Ma
    - April S. Liang
    - Steven Tate
    - Manoj Maddali
    - Robert Joseph Gallo
    - Nigam H. Shah
    - Jonathan H. Chen
  url: "https://www.nature.com/articles/s41746-024-01377-1"
paper:
  title: "Clinical entity augmented retrieval for clinical information extraction"
  arxiv: ""
  url: "https://www.nature.com/articles/s41746-024-01377-1"
  year: 2025
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/clear_scenario.py"
released: "2025-01"
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
    Lopez et al. report RAG F1 as high as 1.00 on some variables with GPT-4, which
    is a different task than HELM's A/B/C exact match. MedHELM's public run list
    does not include clear; private Stanford entries do. No HELM exact-match
    ceiling was read from the JavaScript leaderboard shell.
contamination:
  risk: low
  note: >
    Notes sit behind a local data_path of Excel files and are absent from
    MedHELM's public run configuration. They are de-identified EHR text, not a
    Hugging Face test set. Leakage into general pretraining is less likely than
    for public quizzes, but shared-care Stanford text could still overlap other
    internal dumps.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: clear
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical-nlp
  - classification
  - helm
  - medhelm
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/clear_scenario.py"
    title: "HELM CLEARScenario"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_clear_spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "HELM schema_medhelm.yaml CLEAR group"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41746-024-01377-1"
    title: "Lopez et al. 2025, npj Digital Medicine"
    accessed: "2026-09-08"
  - url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11743751/"
    title: "PMC full text of Lopez et al. 2025"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_public.conf"
    title: "MedHELM public run entries (no clear)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf"
    title: "MedHELM private Stanford run entries for clear"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest/"
    title: "MedHELM leaderboard shell"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

HELM's `clear` scenario is a clinical reading test. The model sees an English patient note and a target condition. It must choose whether the patient has a history of that condition, does not, or whether the note is uncertain. HELM maps those human labels 1, 0, and 2 onto A, B, and C.

The name CLEAR in the cited paper is CLinical Entity Augmented Retrieval, a NER-and-ontology pipeline for extracting variables from notes. HELM cites Lopez et al. (npj Digital Medicine, 19 January 2025) but does not call that retriever. It classifies the labeled note with a multiple-choice prompt. The thirteen HELM condition keys line up with the paper's Stanford MOUD-style clinical variables, not with CheXpert imaging labels.

## How it is scored

`schema_medhelm.yaml` sets `exact_match` on the test split as the main metric. The run spec loads `get_exact_match_metric_specs` only. The adapter is joint multiple choice, zero in-context examples, one output token. Instructions tell the model to reply with A, B, or C and nothing else.

Lopez et al. report F1 for extraction with and without their retriever (abstract averages 0.90 / 0.86 / 0.79 for CLEAR vs embedding RAG vs full note). Those F1 numbers are not HELM exact-match. Do not paste them onto a MedHELM table. A one-in-three chance rate would apply only if labels were uniform, which is not established here.

## Dataset and licence

HELM reads `{condition}.xlsx` from a caller-supplied `data_path`. Rows need `text` and `result_human`. Empty rows are skipped. Every kept row is placed in the test split. Item counts per file are not in the scenario code.

The paper describes about 20,000 notes and 18 variables, including 13 clinical variables on Stanford MOUD data and imaging labels on CheXpert. The article is CC BY 4.0. The notes are de-identified EHR text and are not shipped in HELM. MedHELM's public run file has no `clear` entries. The private Stanford file points at a cluster path and sets `max_eval_instances=100` per condition.

## Who publishes it

Ivan Lopez, Akshay Swaminathan, and coauthors at Stanford (medicine, biomedical data science, and related units) published the 2025 paper, with Nigam H. Shah and Jonathan H. Chen among the senior authors. Stanford CRFM added the MedHELM scenario (`CLEARScenario`, run-spec function `clear`). There is no public Hugging Face dataset for the HELM tables.

## Lineage

The paper is an information-extraction method paper. HELM reused the labeled-note idea as a standalone classification benchmark. This repository has no family page for MedHELM. Sibling MedHELM wraps include [medcalc_bench](medcalc_bench.md) (calculator questions) and [mtsamples_replicate](mtsamples_replicate.md) (treatment-plan generation). Those are different skills and different corpora.

Other projects also use the acronym CLEAR. This id is the MedHELM clinical-note scenario, not a radiology foundation model or a reporting checklist.

## Saturation and contamination

GPT-4 reaching F1 1.00 on some variables in the paper is saturation of their RAG extractor, not of HELM's letter match. Whether MedHELM exact-match still has headroom was not read from the JavaScript leaderboard.

Because the Excel files are local and omitted from the public run list, contamination risk is low relative to public exam sets. It is not zero for models that may have seen overlapping Stanford notes.

## How to run it

The HELM function is `clear`. The run name is `clear:condition={condition}`. You must pass `data_path` to a directory that already contains the thirteen `.xlsx` files. Without those files the scenario raises a missing-file error. Private Stanford entries also pass `max_eval_instances=100` and, for some reasoning models, `num_output_tokens=4000`.

A local HELM run with a different cap, a different verbalizer, or the paper's retriever is a different number. There is no lm-eval or OpenCompass task with this id.

## Reading the numbers

A high HELM exact-match means the model often picked the same A/B/C letter as the human label on that condition's notes. It does not mean the model extracted the variable with the paper's CLEAR retriever. It does not measure treatment quality or diagnosis. Compare conditions separately; HELM does not define a thirteen-condition macro average in the scenario. If a report used only 100 notes, say so, because that is the private MedHELM cap, not a published test cardinality.
