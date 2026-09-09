---
id: dischargeme
name: "DischargeMe (MedHELM)"
aliases:
  - "Discharge Me!"
  - "DischargeMe"
  - "BioNLP ACL'24 Discharge Me"
page_kind: benchmark
category: domain
subcategory: "discharge-instruction and brief-hospital-course generation from MIMIC-IV notes"
status: active
summary: "MedHELM's gated wrap of the BioNLP 2024 DischargeMe shared task: write Brief Hospital Course and Discharge Instructions from MIMIC-IV notes and radiology text."
measures: >
  This id is HELM's dischargeme scenario, not the Codabench shared-task score by itself.
  Each item is a MIMIC-IV emergency admission. HELM strips the gold target section from the
  discharge note, pairs the remainder with one radiology report, and asks the model to write
  either the Brief Hospital Course or the Discharge Instructions. English clinical text.
  The intended skill is clinically accurate generation of those two discharge-summary sections,
  not full-note drafting and not the separate MIMIC-BHC corpus.
task_format: >
  Zero-shot generation (max_train_instances=0). HELM instructions: given discharge text,
  radiology text, and a named target document, return that document. max_tokens=300 by
  default; some gated run entries raise num_output_tokens to 4000. Two HELM instances per
  remaining admission (one per target section).
metric:
  name: "dischargeme_accuracy (HELM LLM-jury mean of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml display name is DischargeMe Jury Score. DischargeMeAnnotator rates
    accuracy, completeness and clarity 1-5 against the gold section; LLMJuryMetric averages
    those scores (default_score 1.0 if none return). HELM also attaches summarization metrics
    including BERTScore with distilbert-base-uncased. The shared task instead averages BLEU-4,
    ROUGE-1/2/L, BERTScore, METEOR, AlignScore and MEDCON on a hidden 250-sample slice, plus
    later clinician 1-5 ratings for top teams. Those tables are not on the HELM 1-5 jury scale.
dataset:
  size: 14702
  size_note: >
    HELM DischargeMeScenario states it uses PhysioNet discharge-me 1.3 phase I test
    (14,702 admissions) after merging diagnosis, discharge, target, radiology, ED stay and
    triage tables, dropping duplicate hadm_id, and inner-joining targets. Each remaining row
    becomes two HELM test instances (BHC and discharge instructions), so the generation count
    can reach twice the admission count; the post-merge n is not published. PhysioNet v1.3
    full corpus: 109,168 admissions (train 68,785, validation 14,719, phase I test 14,702,
    phase II test 10,962), 409,359 radiology reports. Shared-task scoring used a hidden 250
    samples, not the full HELM load.
  url: "https://physionet.org/content/discharge-me/1.3/"
  license: "PhysioNet Credentialed Health Data License 1.5.0 (DUA 1.5.0; CITI training required)"
  languages:
    - en
  modalities:
    - text
  splits: "PhysioNet: train/validation/phase I test/phase II test; HELM: phase I test only, both mapped to HELM test"
  public_test_set: false
publisher:
  org: "Stanford AIMI (shared task); Stanford CRFM (MedHELM scenario)"
  authors:
    - "Justin Xu"
    - "Jean-Benoit Delbrouck"
    - "Andrew Johnston"
    - "Louis Blankemeier"
    - "Curtis Langlotz"
  url: "https://stanford-aimi.github.io/discharge-me/"
paper:
  title: "Discharge Me: BioNLP ACL'24 Shared Task on Streamlining Discharge Documentation"
  arxiv: ""
  url: "https://doi.org/10.13026/0zf5-fx50"
  year: 2024
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/dischargeme_scenario.py"
released: "2024-04"
last_updated: "2024-04"
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
    MedHELM lists dischargeme on the gated healthcare leaderboard. Public HTML for that
    board did not yield a static top jury cell here. Shared-task Codabench/Google Sheet
    overall scores were not re-read as a HELM jury number.
contamination:
  risk: low
  note: >
    Official files are PhysioNet credentialed (DUA 1.5.0 and CITI Data or Specimens Only
    Research). HELM gated run entries pass a local physionet.org tree
    (/share/pi/nigam/data/physionet.org). Web-scale crawls are unlikely to contain this
    labelled dump. Underlying MIMIC-IV-Note and MIMIC-IV-ED still appear in credentialed
    research use. Sending notes to a third-party API violates the DUA.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "dischargeme"
  opencompass: ""
  bigbench: ""
  other: "MedHELM gated; helm-run needs data_path to PhysioNet discharge-me 1.3. Shared-task scoring is separate (Stanford-AIMI/discharge-me)."
tags:
  - biomedical
  - clinical-notes
  - summarization
  - medhelm
  - gated
  - llm-jury
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/dischargeme_scenario.py"
    title: "HELM DischargeMeScenario (v1.3 phase I test; BHC and discharge instructions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_dischargeme_spec (zero-shot, max_tokens 300, LLM jury)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/dischargeme_annotator.py"
    title: "DischargeMeAnnotator (accuracy, completeness, clarity 1-5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/llm_jury_metrics.py"
    title: "LLMJuryMetric (mean of annotator 1-5 scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml DischargeMe Jury Score"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_gated.conf"
    title: "MedHELM gated run entries (local physionet.org path)"
    accessed: "2026-09-08"
  - url: "https://physionet.org/content/discharge-me/1.3/"
    title: "PhysioNet Discharge Me v1.3 (109,168 admissions; credentialed licence)"
    accessed: "2026-09-08"
  - url: "https://stanford-aimi.github.io/discharge-me/"
    title: "Shared-task site (hidden 250-sample scoring; 8 overlap metrics)"
    accessed: "2026-09-08"
  - url: "https://github.com/Stanford-AIMI/discharge-me"
    title: "Stanford-AIMI/discharge-me scoring scripts"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-039 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-039"
---

## What it measures

DischargeMe, as MedHELM runs it, is generation of two discharge-summary sections. The model reads an English discharge note with the gold target stripped out, plus a radiology report, and must write either the Brief Hospital Course or the Discharge Instructions. Xu and colleagues built the corpus from MIMIC-IV-Note and MIMIC-IV-ED for the BioNLP 2024 shared task. HELM keeps only the phase I test split and scores both targets as separate instances. The skill is clinically usable section writing, not the full note and not [MIMIC-BHC](mimic_bhc.md).

## How it is scored

HELM is zero-shot. The headline metric `dischargeme_accuracy` is an LLM jury: annotator models score accuracy, completeness and clarity from 1 to 5 against the gold section. `LLMJuryMetric` averages those scores. Overlap metrics including BERTScore are logged as well. The shared task used a different protocol: mean of eight lexical and factual metrics on a hidden 250 examples, then clinician 1–5 review for top teams. Do not put a Codabench overall next to a HELM jury point. Default decoding is 300 tokens; several gated entries allow 4,000.

## Dataset and licence

PhysioNet project `discharge-me` v1.3 (published 12 April 2024) holds 109,168 admissions. Licence is PhysioNet Credentialed Health Data License 1.5.0 with DUA 1.5.0 and CITI training. HELM does not ship the notes. The scenario loads `test_phase_1` under a local PhysioNet tree and documents 14,702 admissions. Shared-task rules forbid sending the notes through a third-party API.

## Who publishes it

Shared task: Justin Xu, Jean-Benoit Delbrouck, Andrew Johnston, Louis Blankemeier and Curtis Langlotz at Stanford AIMI, BioNLP at ACL 2024. Dataset host: PhysioNet. HELM packaging and the MedHELM leaderboard: Stanford CRFM. The HELM scenario citation mixes PhysioNet DOIs; v1.3 is doi:10.13026/0zf5-fx50, while 10.13026/27pt-1259 is the latest-version DOI on the same page.

## Lineage

No predecessor page in this repository. Related MedHELM clinical generation: [MIMIC-BHC](mimic_bhc.md) (Brief Hospital Course from a preprocessed MIMIC-IV note, different corpus and prompt), [MIMIC-RRS](mimic_rrs.md) (radiology findings to impression) and [ACI-Bench](aci_bench.md) (dialogue to note). The shared-task site lists DischargeMe among clinical NLG evaluations; this id is the HELM wrap of that dataset.

## Saturation and contamination

No public HELM jury top cell was read. Contamination risk is low for the labelled files because they sit behind a PhysioNet DUA. MIMIC-IV notes still circulate in credentialed research. A strong jury score means the model matched gold sections on this gated split under HELM's short generation cap, not that a hospital can file the text.

## How to run it

HELM task name `dischargeme`. Gated MedHELM run entries pass `data_path` to a downloaded PhysioNet 1.3 tree. Annotator models come from the jury config. Shared-task scoring code lives at Stanford-AIMI/discharge-me and is not the HELM jury. HELM entered maintenance mode on 1 June 2026.

## Reading the numbers

A high DischargeMe Jury Score means an LLM panel found the generated section close to the gold BHC or instructions on accuracy, completeness and clarity. It does not measure clinician time saved, patient comprehension, or safety of advice. Compare only jury-to-jury, and only when token limits and annotator models match. Pair it with [MIMIC-BHC](mimic_bhc.md) if the question is hospital-course narrative alone.
