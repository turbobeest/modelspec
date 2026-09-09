---
id: mimic_bhc
name: "MIMIC-BHC (MedHELM)"
aliases:
  - "MIMIC-IV-BHC"
  - "MIMIC-IV-Ext-BHC"
  - "Brief Hospital Course"
page_kind: benchmark
category: domain
subcategory: "discharge-note summarization into a Brief Hospital Course"
status: active
summary: "MedHELM's gated wrap of MIMIC-IV-BHC: write a Brief Hospital Course from a discharge note, scored by an LLM jury plus overlap metrics."
measures: >
  This id is HELM's mimic_bhc scenario, not the authors' original BLEU and
  BERTScore study by itself. MIMIC-IV-BHC pairs a preprocessed MIMIC-IV
  discharge note with the Brief Hospital Course section of that stay. HELM
  prompts the model to summarize the note into a BHC (zero-shot, max 1,024
  tokens) and grades the text with an LLM jury on accuracy, completeness and
  clarity (1–5) as mimic_bhc_accuracy, while also logging summarization
  overlap metrics. Inputs and outputs are English clinical text.
task_format: >
  Zero-shot generation. HELM instructions: "Summarize the clinical note into
  a brief hospital course." Input noun Clinical Note, output noun Brief
  Hospital Course. max_train_instances=0, max_tokens=1024.
metric:
  name: "mimic_bhc_accuracy (HELM LLM-jury average of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's main metric is the jury score (schema_medhelm.yaml display name
    MIMIC-BHC Jury Score). HELM also attaches summarization metrics
    (BERTScore with distilbert-base-uncased, and related overlap scores).
    The 2024 JAMIA paper instead reports BLEU and BERT-Score plus a five-
    clinician reader study on 30 notes. Those figures are not on the HELM
    1–5 jury scale. No HELM jury human baseline was published.
dataset:
  size: 270033
  size_note: >
    PhysioNet MIMIC-IV-Ext-BHC v1.2.0 and the JAMIA/arXiv paper both state
    270,033 note–BHC pairs (mean input 2,267±914 tokens, mean BHC 564±410).
    Source notes: MIMIC-IV-Note, 331,794 discharge summaries from 145,915
    patients (paper). The paper's own modelling used 2,000/100 train/test
    draws inside three context-length bins, not the full 270,033. HELM
    comments out train/validate, reads a local JSON/JSONL of input/target
    fields, and keeps only TEST_SPLIT; the row count of that HELM file is
    not published. MedHELM gated runs point at
    /share/pi/nigam/data/bhc-mimiciv/mimic_iv_bhc.json.
  url: "https://physionet.org/content/labelled-notes-hospital-course/1.2.0/"
  license: "PhysioNet Credentialed Health Data License 1.5.0 (DUA 1.5.0; CITI training required)"
  languages:
    - en
  modalities:
    - text
  splits: "PhysioNet corpus 270,033 pairs; paper bins 2,000/100 per context range; HELM test-only from a local file of unpublished size"
  public_test_set: false
publisher:
  org: "Stanford University (MIMI / CRFM MedHELM packaging)"
  authors:
    - "Asad Aali"
    - "Dave Van Veen"
    - "Yamin Ishraq Arefeen"
    - "Jason Hom"
    - "Christian Bluethgen"
    - "Eduardo Pontes Reis"
    - "Sergios Gatidis"
    - "Namuun Clifford"
    - "Joseph Daws"
    - "Arash S. Tehrani"
    - "Jangwon Kim"
    - "Akshay S. Chaudhari"
  url: "https://crfm.stanford.edu/helm/medhelm/latest"
paper:
  title: "A dataset and benchmark for hospital course summarization with adapted large language models"
  arxiv: "2403.05720"
  url: "https://doi.org/10.1093/jamia/ocae312"
  year: 2024
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mimic_bhc_scenario.py"
released: "2024-03"
last_updated: "2025-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mimic_rrs
    - mimic_repsum
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM lists mimic_bhc on the gated healthcare leaderboard. Public
    HTML for that board did not yield a static top jury score here, so
    saturation is unknown. The paper's GPT-4 ICL vs fine-tuned Llama2-13B
    comparison is on BLEU/BERT-Score and a 30-note reader study, not HELM
    jury points.
contamination:
  risk: low
  note: >
    Official files are PhysioNet credentialed (access policy: DUA plus CITI
    Data or Specimens Only Research). HELM registers the scenario in
    run_entries_medhelm_gated.conf, not the public run-entry file. Web-scale
    crawls are unlikely to contain this labelled dump. Underlying MIMIC-IV
    notes still appear in credentialed research use.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mimic_bhc"
  opencompass: ""
  bigbench: ""
  other: "MedHELM gated; helm-run needs data_path to a local MIMIC-IV-BHC JSON/JSONL"
tags:
  - biomedical
  - clinical-notes
  - summarization
  - medhelm
  - gated
  - llm-jury
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mimic_bhc_scenario.py"
    title: "HELM mimic_bhc_scenario.py (270,033 notes; test-only JSONL)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_mimic_bhc_spec (zero-shot, LLM jury)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml MIMIC-BHC Jury Score"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/docs/medhelm.md"
    title: "MedHELM access levels (gated = PhysioNet)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_medhelm_gated.conf"
    title: "MedHELM gated run entries (mimic_iv_bhc.json path)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.05720"
    title: "Aali et al. hospital course summarization (arXiv 2403.05720)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1093/jamia/ocae312"
    title: "JAMIA 2024 paper (doi:10.1093/jamia/ocae312)"
    accessed: "2026-09-08"
  - url: "https://physionet.org/content/labelled-notes-hospital-course/1.2.0/"
    title: "PhysioNet MIMIC-IV-Ext-BHC v1.2.0 (published 2025-02-03)"
    accessed: "2026-09-08"
  - url: "https://github.com/StanfordMIMI/clin-bhc-summ"
    title: "StanfordMIMI/clin-bhc-summ (PhysioNet DOI 10.13026/fh2q-4148)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

MIMIC-BHC, as MedHELM runs it, is discharge-note summarization. The model
reads an English clinical note derived from MIMIC-IV and must write the
Brief Hospital Course — the narrative of the stay that clinicians actually
file. Aali et al. built MIMIC-IV-BHC by stripping, sectioning and pairing
notes with their BHC targets. HELM's prompt is a single instruction:
summarize the clinical note into a brief hospital course.

## How it is scored

HELM is zero-shot (`max_train_instances=0`). The headline metric
`mimic_bhc_accuracy` is an LLM jury: annotator models score accuracy,
completeness and clarity from 1 to 5 against the gold BHC
(`MIMICBHCAnnotator`). HELM still computes summarization overlap
(BERTScore and related metrics) on the same outputs. The 2024 paper's
BLEU/BERT-Score tables and the five-clinician preference study on 30
notes are a different protocol. Do not put a JAMIA BLEU next to a HELM
jury point.

## Dataset and licence

PhysioNet project MIMIC-IV-Ext-BHC
(`labelled-notes-hospital-course` v1.2.0, published 3 February 2025)
and the paper both give 270,033 pairs. Licence is PhysioNet Credentialed
Health Data License 1.5.0 with DUA 1.5.0 and CITI training. HELM does
not ship the notes; gated run entries pass a local `mimic_iv_bhc.json`.
The paper separately samples 2,000/100 splits inside 0–1,024, 1,024–2,048
and 2,048–4,096 token bins for its own experiments.

## Who publishes it

Dataset and JAMIA 2024 paper: Asad Aali and colleagues at Stanford
(doi:10.1093/jamia/ocae312; arXiv 2403.05720, March 2024). Reference
code: github.com/StanfordMIMI/clin-bhc-summ. The HELM scenario and
MedHELM leaderboard are Stanford CRFM.

## Lineage

No predecessor page in this repository. Related MedHELM clinical
generation tasks: [MIMIC-RRS](mimic_rrs.md) (radiology
findings→impression on MIMIC-III) and [ACI-Bench](aci_bench.md)
(dialogue to visit note). [mimic_repsum](mimic_repsum.md) is a separate
lm-eval findings→impression wrap over a MIMIC-III hospital-course Hugging
Face dump, not this BHC task.

## Saturation and contamination

No public top jury score is recorded here. Contamination is graded low
for the official labelled files because they sit behind PhysioNet
credentialing and HELM's gated run list.

## How to run it

Credentialed PhysioNet access, then `helm-run` with scenario `mimic_bhc`
and `data_path` to the local JSON. MedHELM docs class this as gated
(`run_entries_medhelm_gated.conf`). Jury models come from
`jury_config_path`. Without the same jury and the same local file, scores
are not comparable.

## Reading the numbers

A high HELM jury score means annotator models judged the generated BHC
accurate, complete and clear relative to the gold section. It is not a
claim that a physician would sign the note, and it is not the paper's
BLEU number. The gold BHC is itself a clinician-written section of the
same stay, so overlap can reward style matching. Look at [ACI-Bench](aci_bench.md)
or [HealthBench](healthbench.md) for other clinical generation settings,
and never treat a public-web "MIMIC summarization" score as this gated
task.
