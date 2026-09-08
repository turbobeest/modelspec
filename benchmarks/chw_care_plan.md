---
id: chw_care_plan
name: "NoteExtract (MedHELM chw_care_plan)"
aliases:
  - "NoteExtract"
  - "CHW Care Plan"
  - "chw_care_plan"
page_kind: benchmark
category: domain
subcategory: "structured extraction from community-health-worker care-plan notes"
status: active
summary: "MedHELM private NoteExtract task: rewrite a community health worker care-plan note into a fixed clinical template, scored by an LLM jury."
measures: >
  This id is HELM's chw_care_plan scenario, shown on the MedHELM leaderboard
  as NoteExtract. It is not MTSamples, MIMIC-BHC, or a Stanford Health Care
  shc_* task. Each item is an English free-form care-plan note in the CSV
  column "MO Note". The prompt asks the model to extract chief complaint and
  history-of-present-illness fields (onset, provoking/palliating factors,
  quality, region/radiation, severity, timing, related symptoms) and to write
  "Not mentioned" rather than infer. The paper describes the same work as
  restructuring community health worker care plans into a specified format
  without a gold-standard response.
task_format: >
  Zero-shot generation. HELM adapter instructions: "Follow the instructions
  provided regarding conversion of a patient note into a specified format."
  Empty input and output nouns. max_train_instances=0, max_tokens=768.
  Official private run entries pass data_path=/share/pi/nigam/datasets/CHW_Dataset.csv.
metric:
  name: "chw_care_plan_accuracy (HELM LLM-jury average of accuracy, structure, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml display name is NoteExtract Jury Score. The annotator
    rates accuracy, structure, and clarity on 1-5 (not completeness). The
    Nature/arXiv paper says NoteExtract has no gold response, so the jury
    swapped completeness for structure. HELM still attaches the source "MO
    Note" as the tagged reference and also logs summarization metrics
    (BERTScore, distilbert-base-uncased). Default jury in
    helm.benchmark.scenarios.medhelm/judges.yaml: GPT-4o (2024-05-13), Llama
    3.3 70B Instruct, Claude 3.7 Sonnet. LLMJuryMetric averages every 1-5
    axis score; default_score is 1.0 when annotations are missing. No
    clinician human baseline for this scenario was published.
dataset:
  size: null
  size_note: >
    The notes are not public. Official HELM rows load a private CSV at
    /share/pi/nigam/datasets/CHW_Dataset.csv and skip rows whose "MO Note"
    is NaN. MedHELM Table 7 lists NoteExtract as access Private, curation
    New, category Patient Communication and Education. No instance count
    for this CSV was stated in the scenario, the schema, or the ar5iv HTML
    of arXiv:2505.23802. Nature Medicine author metadata includes Nirmal
    Ravi at eHealth Africa Clinics, Kano, Nigeria; the paper table does not
    itself name a country for the notes. HELM code is Apache-2.0; that
    licence does not cover the CSV.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/chw_care_plan_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT only, from the caller-supplied CSV"
  public_test_set: false
publisher:
  org: "Stanford CRFM / MedHELM"
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
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/chw_care_plan_scenario.py"
released: "2025"
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
    The MedHELM paper says the Figure 3 heatmap's strongest cells are on
    NoteExtract, so the task may not separate frontier models as sharply as
    harder MedHELM sets. No numeric top jury score was read from the
    leaderboard or the paper tables opened here.
contamination:
  risk: low
  note: >
    The evaluation CSV is private (MedHELM private run-entry file, not the
    public conf). Pretraining on these notes is unlikely. The prompt template
    and scoring code are public in HELM.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "chw_care_plan"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medhelm
  - clinical
  - note-extraction
  - private-data
  - llm-jury
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/chw_care_plan_scenario.py"
    title: "HELM CHWCarePlanScenario (MO Note, OPQRST-style prompt, scenario name chw_care_plan)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/chw_care_plan_annotator.py"
    title: "CHWCarePlanAnnotator (accuracy, structure, clarity on 1-5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "get_chw_care_plan_run_spec (zero-shot, max_tokens 768, jury metric)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml (NoteExtract display name, chw_care_plan_accuracy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medhelm/judges.yaml"
    title: "Default MedHELM jury models"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf"
    title: "Private Stanford run entries (CHW_Dataset.csv; not in the public conf)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/llm_jury_metrics.py"
    title: "LLMJuryMetric (mean of 1-5 axis scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/docs/medhelm.md"
    title: "HELM MedHELM docs (public / gated / private run-entry files)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "stanford-crfm/helm Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM preprint (arXiv:2505.23802, submitted 2025-05-26)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.23802"
    title: "MedHELM full text (Table 7 NoteExtract private/new; no-gold jury; heatmap note)"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41591-025-04151-2"
    title: "Nature Medicine article (published 2026-01-20; Nirmal Ravi affiliation Kano, Nigeria)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/medhelm/latest/"
    title: "MedHELM leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-030 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-030"
---

## What it measures

chw_care_plan is HELM's code name for MedHELM NoteExtract. The model reads a free-form community health worker care-plan note and must fill a fixed English template: chief complaint plus history-of-present-illness slots. The prompt forbids guessing; missing facts should be "Not mentioned." Inputs are English clinical text from a private CSV, not a public Hub dataset.

This is not [mtsamples_procedures](mtsamples_procedures.md), [mtsamples_replicate](mtsamples_replicate.md), or [mimic_bhc](mimic_bhc.md), which generate plans or hospital-course summaries from other note sources. It is also not a Stanford Health Care `shc_*` scenario.

## How it is scored

The headline metric is `chw_care_plan_accuracy`, an LLM-jury mean of accuracy, structure, and clarity, each 1–5. The paper says NoteExtract has no gold answer, so the jury uses structure instead of completeness. HELM still stores the original "MO Note" as the tagged reference and adds BERTScore-style summarization metrics, which assume a gold string those jury axes do not. The default jury is GPT-4o, Llama 3.3 70B Instruct, and Claude 3.7 Sonnet, using Stanford Health Care deployments in the bundled judges file. Missing annotations default to 1.0. Official rows are zero-shot with a 768-token cap. The run-spec docstring calls the task "summarize doctor-patient dialogues"; the scenario Python and the paper describe care-plan restructuring. Prefer the scenario and the paper.

## Dataset and licence

Official reproductions point at `/share/pi/nigam/datasets/CHW_Dataset.csv` in `run_entries_medhelm_private_stanford.conf`. That path is not in the public MedHELM run-entry file. Rows without an "MO Note" are skipped. Table 7 of the MedHELM paper labels the benchmark Private and New under Patient Communication and Education. No n was given in the sources opened for this page. HELM's repository is Apache-2.0; the notes are not.

## Who publishes it

MedHELM is a Stanford CRFM evaluation, with equal first authors Suhana Bedi, Hejie Cui, Miguel Fuentes, and Alyssa Unell on the peer-reviewed paper and Nigam H. Shah as last author. The arXiv preprint (2505.23802) is dated 26 May 2025. Nature Medicine published the article on 20 January 2026 (issue March 2026). CRFM hosts the leaderboard. Nature author metadata lists Nirmal Ravi at eHealth Africa Clinics, Kano, Nigeria; that is an affiliation, not a published collection-site statement for the CSV.

## Lineage

NoteExtract is one of the 18 newly formulated MedHELM benchmarks, not a wrap of an older shared task. It sits with other private clinical-note work in HELM but does not share items with MTSamples or MIMIC-BHC. No successor id exists in this repository.

## Saturation and contamination

The paper's heatmap discussion names NoteExtract as the strongest-performing benchmark among the 35, which is a reason to treat a high jury score as a weak separator of frontier models. No numeric top score was copied from the live leaderboard. The CSV is private, so training-set contamination of the notes themselves is unlikely; the prompt template is public.

## How to run it

Install HELM with MedHELM extras and call `helm-run` with spec `chw_care_plan` and a `data_path` to a CSV that has an "MO Note" column. Official leaderboard rows use the Stanford private run-entry file and Stanford Health Care model deployments. Anyone else must supply their own path and deployments. There is no lm-evaluation-harness, inspect_evals, or OpenCompass task under this id.

## Reading the numbers

A high NoteExtract jury score means the judges thought the rewrite was accurate, well structured, and clear on these private notes, not that the model can write a billable encounter note in another clinic. Because there is no gold extraction, completeness is not scored; a fluent template that omits facts the note actually contained can still look structured. Do not compare the 1–5 jury mean to exact-match medical QA or to BERTScore on the same run. Look at other MedHELM private note tasks and at a harder public clinical-extraction set alongside it. The live leaderboard shows unnormalized metrics; the paper heatmap is normalized for display.
