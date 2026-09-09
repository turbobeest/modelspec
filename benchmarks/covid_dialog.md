---
id: covid_dialog
name: "COVIDDialog (HELM English medical dialogue)"
aliases:
  - "COVIDDialog"
  - "covid_dialogue"
  - "CovidDialog"
page_kind: benchmark
category: domain
subcategory: "HELM English patient-to-doctor response generation on COVID-19 consultations"
status: unknown
summary: "HELM generation task: read an English COVID-19 patient question and write the doctor's reply, scored with overlap metrics."
measures: >
  covid_dialog is HELM's wrap of the English CovidDialog consultations, not a
  new item set. The model reads a patient's COVID-19 or pneumonia concern and
  must write the doctor's reply. HELM strips a leading "patient: " from the
  source line and prompts with Patient / Doctor. The original English
  collection is described as 603 consultations with id, URL, condition
  description, and dialogue. This is English doctor-response generation, not
  the Chinese Haodf.com dump and not HELM med_dialog.
task_format: >
  Instruction "Generate a response given a patient's questions and concerns."
  then Patient: … / Doctor: … . Default five in-context examples, temperature
  0, max_tokens 128. Run spec name covid_dialog; group COVIDDialog.
metric:
  name: "open-ended overlap (exact_match, quasi_exact_match, f1_score, rouge_l, bleu_1, bleu_4)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    classic_run_specs.py attaches get_open_ended_generation_metric_specs.
    get_generative_harms_metric_specs() is called with both include flags
    left false, so it adds no extra metrics. There is no schema_classic.yaml
    row for COVIDDialog and no published human overlap baseline in the
    sources opened here.
dataset:
  size: 603
  size_note: >
    HELM scenario docstring, quoting UCSD-AI4H/COVID-Dialogue: 603 English
    consultations. HELM loads CodaLab bundle
    0x6f1ac4b2e47043fcbb873b2af1c7ee0c files {train,val,test}.source/.target
    and maps val to HELM valid. Hugging Face lighteval/covid_dialogue, a
    public query/answer mirror, has 490 / 63 / 61 rows (614 total) on the
    datasets-server — 11 more than 603. The original GitHub repository
    returns 404. GordonDoo/COVID-Dialogue is a different Chinese set (957
    conversations). Exact HELM line counts after download were not re-run.
  url: "https://huggingface.co/datasets/lighteval/covid_dialogue"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM: train / valid / test from CodaLab {train,val,test}.source/.target; lighteval mirror 490/63/61"
  public_test_set: true
publisher:
  org: "UCSD AI4H (dataset); Stanford CRFM (HELM scenario)"
  authors:
    - "Zeqian Ju"
    - "Subrato Chakravorty"
    - "Xuehai He"
    - "Shu Chen"
    - "Xingyi Yang"
    - "Pengtao Xie"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/covid_dialog_scenario.py"
paper:
  title: "CovidDialog: Medical Dialogue Datasets about COVID-19"
  arxiv: ""
  url: "https://github.com/UCSD-AI4H/COVID-Dialogue"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/covid_dialog_scenario.py"
released: "2020"
last_updated: "2022-08"
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
    No COVIDDialog block exists in schema_classic.yaml, so this is not a
    Classic headline cell. It is listed in run_entries_biomedical.conf.
    No numeric HELM overlap table was read. HELM entered maintenance mode
    on 2026-06-01.
contamination:
  risk: medium
  note: >
    English consultations have been mirrored (CodaLab upload 2022-08-21;
    lighteval Hub dump created 2023-05-05) with answers in the files. The
    source GitHub repo is gone. Web-trained models may have seen patient
    posts or later copies.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "covid_dialog (biomedical run_entries; group COVIDDialog)"
  opencompass: ""
  bigbench: ""
  other: "lighteval/covid_dialogue on Hugging Face is a 614-row query/answer mirror, not a second HELM scenario."
tags:
  - helm
  - biomedical
  - dialogue
  - covid-19
  - generation
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/covid_dialog_scenario.py"
    title: "HELM covid_dialog_scenario.py (603 consultations, CodaLab bundle, Patient/Doctor split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_covid_dialog_spec (max_tokens 128, open-ended metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_biomedical.conf"
    title: "run_entries_biomedical.conf (covid_dialog:model=biomedical)"
    accessed: "2026-09-08"
  - url: "https://worksheets.codalab.org/rest/bundles/0x6f1ac4b2e47043fcbb873b2af1c7ee0c"
    title: "CodaLab bundle CovidDialog (uuid 0x6f1ac4b2e47043fcbb873b2af1c7ee0c, created 2022-08-21, license field empty)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/lighteval/covid_dialogue"
    title: "lighteval/covid_dialogue card (490/63/61; no licence field)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=lighteval/covid_dialogue"
    title: "datasets-server size for lighteval/covid_dialogue (614 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/GordonDoo/COVID-Dialogue/master/README.md"
    title: "GordonDoo/COVID-Dialogue README (Chinese 957 conversations; not the HELM English set)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-035 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-035"
---

## What it measures

covid_dialog is HELM's English doctor-reply task on CovidDialog. The model sees a patient's COVID-19 or pneumonia concern and must write the doctor's answer. HELM deletes a leading "patient: " and uses a Patient / Doctor template with a short instruction. The scenario cites 603 English consultations from UCSD-AI4H/COVID-Dialogue. That GitHub URL now 404s. This is not the Chinese Haodf.com file in GordonDoo/COVID-Dialogue (957 conversations), and not HELM `med_dialog` (HealthCareMagic / iCliniq).

## How it is scored

`get_covid_dialog_spec` attaches exact match, quasi-exact match, F1, ROUGE-L, BLEU-1, and BLEU-4. The generative-harms helper is called with both include flags false, so it adds nothing. Defaults: five in-context examples, temperature 0, 128 new tokens. There is no COVIDDialog entry in schema_classic.yaml, so Classic has no named headline metric. No human overlap score was in the sources opened here.

## Dataset and licence

HELM downloads `{train,val,test}.source` and `.target` from CodaLab bundle `0x6f1ac4b2e47043fcbb873b2af1c7ee0c` (uploaded 2022-08-21; metadata licence empty). The docstring's 603 figure was not re-counted from those files. Hugging Face `lighteval/covid_dialogue` has 490/63/61 public query/answer rows (614), eleven above 603; this page does not treat that as the HELM n. No SPDX licence was stated on the CodaLab metadata, the lighteval card, or the dead GitHub URL. HELM code is Apache-2.0.

## Who publishes it

The HELM bibtex names Zeqian Ju, Subrato Chakravorty, Xuehai He, Shu Chen, Xingyi Yang, and Pengtao Xie, 2020, with journal URL equal to the now-missing GitHub repo. There is no arXiv id on that citation. Stanford CRFM maintains the scenario. Biomedical runs use `run_entries_biomedical.conf`.

## Lineage

CovidDialog is a 2020 consultation dump; HELM only wraps the English patient/doctor lines. HELM also has `med_dialog` and [meqsum](meqsum.md); those are other datasets. The Chinese COVID-Dialogue README is a separate corpus with Haodf.com copyright, not this id.

## Saturation and contamination

No current HELM F1 or ROUGE table was read. Answers sit in the CodaLab and lighteval files, so treat contamination as at least medium. A high overlap score is n-gram match to one doctor's reply, not clinical safety.

## How to run it

`helm-run` with `covid_dialog` (biomedical conf: `covid_dialog:model=biomedical`). Compare only the same split, shot count, and overlap metric. Do not mix English HELM numbers with Chinese 957-conversation figures.

## Reading the numbers

A high ROUGE-L or F1 means the model echoed the reference doctor's wording on these COVID-era chats. It does not mean the advice is current, safe, or complete. The 603 vs 614 count split is unresolved. Prefer HELM's own split names over the Hub mirror unless the reporter used lighteval. Read beside other medical generation tasks rather than as a standalone clinical exam.
