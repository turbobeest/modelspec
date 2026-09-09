---
id: mimic_rrs
name: "MIMIC-RRS (MedHELM)"
aliases:
  - "MIMIC RRS"
  - "Radiology Report Summarization"
page_kind: benchmark
category: domain
subcategory: "radiology findings-to-impression summarization"
status: active
summary: "MedHELM's gated wrap of MIMIC-RRS on MIMIC-III: generate an Impression from Findings, scored by an LLM jury plus overlap metrics."
measures: >
  This id is HELM's mimic_rrs scenario. Chen et al. (ACL 2023) released
  MIMIC-RRS as findings–impression pairs from MIMIC-III and MIMIC-CXR across
  CT, MR and X-ray and several anatomies. HELM's scenario file states it
  uses only the MIMIC-III reports, loading test.findings.tok and
  test.impression.tok from a local directory. The model writes an Impression
  from Findings. MedHELM's main score is an LLM jury (mimic_rrs_accuracy);
  overlap metrics are logged as well. English clinical text.
task_format: >
  Zero-shot generation. HELM: "Generate the impression section of the
  radiology report based on its findings. This will not be used to diagnose
  nor treat any patients. Be as concise as possible." Input Findings,
  output Impression, max_tokens=128, max_train_instances=0.
metric:
  name: "mimic_rrs_accuracy (HELM LLM-jury average of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Schema display name is MIMIC-RRS Jury Score. HELM also runs
    summarization metrics (BERTScore distilbert-base-uncased and related
    overlap scores). Chen et al. reported ROUGE-style and factuality
    metrics on their own splits, not this 1–5 jury. No HELM jury human
    baseline is published.
dataset:
  size: null
  size_note: >
    Chen et al. Table 2: 207,782 reports in full MIMIC-RRS (79,779
    MIMIC-III across 11 modality-anatomy pairs plus 128,003 MIMIC-CXR chest
    X-ray). HELM's docstring says it uses only MIMIC-III and quotes 73,259
    reports — that does not match the paper's 79,779 MIMIC-III count, and
    this page records both rather than choosing one. HELM reads only the
    test split files (test.findings.tok / test.impression.tok); the HELM
    test cardinality is not published. Gated paths use
    /share/pi/nigam/data/rrs-mimiciii/all.
  url: "https://arxiv.org/abs/2211.08584"
  license: "PhysioNet credentialed access for MIMIC-III source notes; Chen et al. release reconstruction scripts, not a public labelled dump"
  languages:
    - en
  modalities:
    - text
  splits: "Chen et al. put CT abdomen/pelvis, CT chest, CT neck, CT spine, CT head, MR head and X-ray chest in train/validation/test and hold MR pelvis/spine/neck, MR abdomen and CT sinus as OOD tests; HELM uses the test files only"
  public_test_set: false
publisher:
  org: "Stanford University (AIMI / CRFM MedHELM packaging); The Chinese University of Hong Kong, Shenzhen (Chen, Wan)"
  authors:
    - "Zhihong Chen"
    - "Maya Varma"
    - "Xiang Wan"
    - "Curtis Langlotz"
    - "Jean-Benoit Delbrouck"
  url: "https://crfm.stanford.edu/helm/medhelm/latest"
paper:
  title: "Toward Expanding the Scope of Radiology Report Summarization to Multiple Anatomies and Modalities"
  arxiv: "2211.08584"
  url: "https://aclanthology.org/2023.acl-short.41/"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mimic_rrs_scenario.py"
released: "2023"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mimic_bhc
    - mimic_repsum
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM reports the gated task, but no static top jury score was
    captured from public HTML. Chen et al.'s own ROUGE-style tables are a
    different metric and a different (paper) split.
contamination:
  risk: low
  note: >
    MIMIC-III requires PhysioNet credentialing. HELM lists mimic_rrs only
    in run_entries_medhelm_gated.conf. Chen et al. note that some clinical
    LMs were pretrained on MIMIC-III overlapping this set and therefore
    excluded those models from their paper experiments.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mimic_rrs"
  opencompass: ""
  bigbench: ""
  other: "MedHELM gated; helm-run needs data_path to a directory with test.findings.tok and test.impression.tok"
tags:
  - biomedical
  - radiology
  - summarization
  - medhelm
  - gated
  - llm-jury
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mimic_rrs_scenario.py"
    title: "HELM mimic_rrs_scenario.py (MIMIC-III only; 73,259 in docstring)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_mimic_rrs_spec"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/annotation/mimic_rrs_annotator.py"
    title: "HELM MIMICRRSAnnotator jury prompt"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml MIMIC-RRS"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_medhelm_gated.conf"
    title: "MedHELM gated run entries (rrs-mimiciii/all)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.08584"
    title: "Chen et al. arXiv 2211.08584 (79,779 MIMIC-III + 128,003 MIMIC-CXR)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2023.acl-short.41/"
    title: "ACL 2023 short paper"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/docs/medhelm.md"
    title: "MedHELM access levels"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

MIMIC-RRS, in MedHELM, is radiology report summarization: given the
Findings section, write the Impression. Chen, Varma, Wan, Langlotz and
Delbrouck (ACL 2023) built MIMIC-RRS so the task would cover more than
chest X-ray — CT, MR and X-ray, and anatomies including head, spine,
abdomen and pelvis. HELM's scenario restricts itself to MIMIC-III files
and does not load MIMIC-CXR.

## How it is scored

HELM is zero-shot with a 128-token cap. The named metric
`mimic_rrs_accuracy` averages LLM-jury scores for accuracy, completeness
and clarity (1–5) against the gold Impression. Summarization overlap
metrics run in parallel. Chen et al. instead reported lexical overlap and
a factuality metric on their paper splits. A HELM jury point and a 2023
ROUGE number are not the same evaluation.

## Dataset and licence

Chen et al. Table 2: 207,782 pairs total — 79,779 from MIMIC-III and
128,003 from MIMIC-CXR. HELM's module docstring says 73,259 MIMIC-III
reports. That 73,259 vs 79,779 disagreement is unresolved here; neither
figure is treated as HELM's test size, which is the length of the local
`test.*.tok` files and is unpublished. Source notes are MIMIC-III
(PhysioNet credentialed). Chen et al. release reconstruction code and
splits rather than a fully public labelled corpus.

## Who publishes it

The dataset paper is ACL 2023 (arXiv 2211.08584, November 2022). Zhihong
Chen and Xiang Wan are at CUHK Shenzhen; Maya Varma, Curtis Langlotz and
Jean-Benoit Delbrouck are at Stanford AIMI. MedHELM packaging and the
`mimic_rrs` scenario are Stanford CRFM.

## Lineage

Not an alias of [mimic_repsum](mimic_repsum.md). That lm-eval task uses
`dmacres/mimiciii-hospitalcourse-meta` and ROUGE/BLEU/RadGraph, not Chen
et al.'s tokenized files and not HELM's jury. Related MedHELM generation:
[mimic_bhc](mimic_bhc.md) (discharge BHC) and [ACI-Bench](aci_bench.md).

## Saturation and contamination

No public HELM top score is recorded. Contamination is low for the
official credentialed files; Chen et al. already warned that some
MIMIC-pretrained clinical models overlap this test set.

## How to run it

PhysioNet access to MIMIC-III, reconstruct or obtain the tokenized
findings/impression files, then `helm-run` scenario `mimic_rrs` with
`data_path` to that directory. Gated MedHELM only. Match jury models
before comparing `mimic_rrs_accuracy`.

## Reading the numbers

A high jury score means annotator models thought the Impression captured
the Findings. It does not replace a radiologist's sign-off, and it is
easy to confuse with other MIMIC "report summarization" harnesses that
use different files and metrics. Check whether a number is HELM jury,
Chen et al. overlap, or [mimic_repsum](mimic_repsum.md) RadGraph before
ranking models.
