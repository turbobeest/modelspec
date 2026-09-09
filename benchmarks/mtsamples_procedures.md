---
id: mtsamples_procedures
name: "MTSamples Procedures (MedHELM)"
aliases:
  - "MTSamples-Procedures"
  - "mtsample_procedure"
page_kind: benchmark
category: domain
subcategory: "operative-note plan, summary or findings generation from a surgical transcription"
status: active
summary: "MedHELM wrap of MTSamples surgical notes: generate a plan or findings from an operative transcription, scored by an LLM jury plus overlap metrics."
measures: >
  This id is HELM's mtsamples_procedures scenario in MedHELM, not a standalone
  shared-task paper and not the mixed-specialty mtsamples_replicate scenario.
  Each item is an English transcribed operative note from MTSamples.com, copied
  into raulista1997/benchmarkdata. HELM strips PLAN, SUMMARY and FINDINGS from
  the prompt and asks the model for a treatment plan. The reference is the first
  of those three sections that exists. Nature Medicine lists the task under
  clinical note generation / recording procedures.
task_format: >
  Zero-shot generation. HELM instructions: "Here are information about a patient,
  return a reasonable treatment plan for the patient." Input noun Patient Notes,
  output noun Answer. max_train_instances=0, max_tokens=512.
metric:
  name: "mtsamples_procedures_accuracy (HELM LLM-jury average of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml display name is MTSamples Procedures Jury Score. HELM also
    logs summarization overlap (BERTScore with distilbert-base-uncased). The jury
    is the default MedHELM panel in judges.yaml: GPT-4o, Llama 3.3 70B Instruct,
    Claude 3.7 Sonnet. LLMJuryMetric averages every 1-5 axis score; default_score
    is 1.0 when annotations are missing. No clinician human baseline for this
    scenario was published. Do not treat the jury as exact-match accuracy.
dataset:
  size: null
  size_note: >
    At HELM pin c4c252443fa9c52afb6960f53e51be278639bea2 the Git tree has 429
    .txt files under mtsample_procedure. HELM keeps only notes that contain a
    PLAN, SUMMARY or FINDINGS section, so the scored n is at most 429 and was
    not independently counted here. Two sampled notes (for example Appendectomy)
    have none of those headers, so many files are likely dropped. The live
    MTSamples.com homepage (2026-09-08) advertises 5,043 samples in 40
    specialties, including 1,113 surgery reports; HELM uses the 429-file GitHub
    folder, not that full catalogue. MedHELM marks the benchmark public and
    reformulated. No SPDX licence is stated in HELM or the data README. The
    site allows educational print/share with credit and says samples are
    user-contributed and not guaranteed complete.
  url: "https://github.com/raulista1997/benchmarkdata/tree/c4c252443fa9c52afb6960f53e51be278639bea2/mtsample_procedure"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT only, from filtered GitHub .txt files"
  public_test_set: true
publisher:
  org: "Stanford CRFM / MedHELM; source notes from MTSamples.com, packaged by raulista1997/benchmarkdata"
  authors:
    - "Suhana Bedi"
    - "Hejie Cui"
    - "Miguel Fuentes"
    - "Alyssa Unell"
    - "Michael Wornow"
    - "Yifan Mai"
    - "Percy Liang"
    - "Nigam H. Shah"
  url: "https://crfm.stanford.edu/helm/medhelm/latest/"
paper:
  title: "Holistic evaluation of large language models for medical tasks with MedHELM"
  arxiv: "2505.23802"
  url: "https://www.nature.com/articles/s41591-025-04151-2"
  year: 2026
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mtsamples_procedures_scenario.py"
released: "2025"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mtsamples_replicate
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM reports category-level Clinical Note Generation scores around 0.73-0.85
    on a normalised 0-1 scale for nine 2025 models (arXiv 2505.23802v2 abstract),
    not a per-scenario jury top score. The public leaderboard did not yield a copied
    mtsamples_procedures figure here.
contamination:
  risk: high
  note: >
    MTSamples transcriptions have been public on mtsamples.com and on GitHub.
    Nature Medicine lists MTSamples Procedures among datasets that are publicly
    accessible without restrictions. Gold PLAN/SUMMARY/FINDINGS strings are in
    the same files HELM downloads.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mtsamples_procedures"
  opencompass: ""
  bigbench: ""
  other: "MedHELM run spec mtsamples_procedures; main_metric mtsamples_procedures_accuracy, main_split test."
tags:
  - medical
  - clinical-notes
  - generation
  - helm
  - medhelm
  - llm-jury
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mtsamples_procedures_scenario.py"
    title: "HELM mtsamples_procedures_scenario.py (pin, filters, PLAN/SUMMARY/FINDINGS)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_mtsamples_procedures_spec (prompt, jury, BERTScore)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml (MTSamples Procedures Jury Score)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/annotation/mtsamples_procedures_annotator.py"
    title: "MTSamplesProceduresAnnotator (1-5 accuracy, completeness, clarity)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/medhelm/judges.yaml"
    title: "MedHELM default jury models"
    accessed: "2026-09-08"
  - url: "https://github.com/raulista1997/benchmarkdata"
    title: "raulista1997/benchmarkdata (MedHELM data source; 429 procedure .txt at pin)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM arXiv 2505.23802"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41591-025-04151-2"
    title: "Nature Medicine 2026 MedHELM article"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.23802"
    title: "MedHELM HTML (public reformulated; gold-standard quality note)"
    accessed: "2026-09-08"
  - url: "https://www.mtsamples.com/"
    title: "MTSamples.com homepage (5,043 samples; educational-use credit request)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

HELM `mtsamples_procedures` asks a model to write a short English treatment
plan from a transcribed surgical note. The note comes from MTSamples.com
operative samples. HELM deletes any PLAN, SUMMARY or FINDINGS section from
the input. The hidden section is the reference.

This is a MedHELM clinical-note-generation task, not an exam QA set, and not
[ACI-Bench](aci_bench.md) dialogue-to-note. It is also not
[mtsamples_replicate](mtsamples_replicate.md), which uses a broader specialty
dump and a different strip rule.

## How it is scored

The schema main metric is `mtsamples_procedures_accuracy`: a three-model jury
rates accuracy, completeness and clarity on a 1-5 scale. The metric is the
mean of those scores. HELM also records BERTScore and other summarization
overlap stats. The run spec is zero-shot with 512 max tokens. A missing jury
annotation falls back to 1.0. The MedHELM paper found this gold text can be
messy; the jury is told to use the reference only when needed.

## Dataset and licence

The scenario pins Git commit `c4c2524` and lists `.txt` files under
`mtsample_procedure`. That tree has 429 notes. Only notes with PLAN, SUMMARY
or FINDINGS become instances, so the eval n is unknown without a filtered
count. No SPDX licence appears in HELM or in the data README. Nature Medicine
calls the benchmark public. The underlying site is a user-contributed transcription
sample catalogue that asks for credit on reuse.

## Who publishes it

MedHELM is Stanford CRFM and Stanford Medicine (Bedi, Cui, Fuentes, Unell and
colleagues; arXiv 2505.23802, Nature Medicine 2026). The notes are MTSamples
samples mirrored by `raulista1997/benchmarkdata`. The live board is
crfm.stanford.edu/helm/medhelm.

## Lineage

No predecessor in this repository. Sibling [mtsamples_replicate](mtsamples_replicate.md)
uses `mtsamples_processed` (1,269 files at its pin) and only strips PLAN.
[ACI-Bench](aci_bench.md), [MIMIC-BHC](mimic_bhc.md) and [MIMIC-RRS](mimic_rrs.md)
are other MedHELM generation tasks with different sources.

## Saturation and contamination

No per-task top jury score was copied from a rendered board. Clinical note
generation is a relatively high MedHELM category, but that is not this
scenario's number. Contamination is high because the notes and reference
spans are public.

## How to run it

`helm-run` with run spec `mtsamples_procedures`. Confirm the jury models
match `judges.yaml` before comparing to MedHELM. Do not mix with
`mtsamples_replicate` or with string-overlap-only numbers.

## Reading the numbers

A high jury score means three LLMs judged the plan close to the note's own
PLAN, SUMMARY or FINDINGS on a 1-5 scale. It is not proof of safe surgical
documentation. Gold sections can be incomplete, and the public samples are
old. Prefer gated EHR note tasks when the claim is real-hospital writing.
