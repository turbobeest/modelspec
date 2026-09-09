---
id: starr_patient_instructions
name: "STARR Patient Instructions (PatientInstruct)"
aliases:
  - "PatientInstruct"
page_kind: benchmark
category: domain
subcategory: "clinical patient communication: generate personalized post-procedure discharge instructions from real clinical case data"
status: active
summary: >-
  A MedHELM scenario, built from private Stanford Health Care records, that asks a model to write
  post-procedure patient instructions from a diagnosis, procedure and clinical notes.
measures: >
  STARR Patient Instructions (displayed as "PatientInstruct" in MedHELM's taxonomy) gives a model
  real-world clinical case details -- a diagnosis, the planned or performed procedure, and the
  history-and-physical and operative notes -- and asks it to generate clear, actionable
  post-procedure instructions appropriate for a patient recovering from that intervention. It sits
  in MedHELM's "Patient Communication and Education" category and tests clinical note synthesis and
  patient-facing communication, not diagnostic or decision-support reasoning.
task_format: >
  Text generation, zero-shot (all instances are assigned to the test split; no in-context training
  examples are drawn from the data itself). Each instance is built from a record with five fields --
  Diagnosis, ActualProcedure, HistoryPhysicalNoteText, OperativeNoteText and
  DischargeInstructionNoteText -- filtered to records marked QC="TRUE"; the model receives the first
  four as input and its output is compared against the real DischargeInstructionNoteText as
  reference.
metric:
  name: "LLMJuryMetric ('starr_patient_instructions_accuracy', an LLM-as-judge score from a jury of annotator models) combined with automatic summarization metrics (BERTScore-based) via HELM's summarization metric suite"
  direction: higher_is_better
  unit: "score"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Not established from the sources read for this page; the MedHELM paper's public tables do not
    give a specific numeric baseline or ceiling for this metric in the material read.
dataset:
  size: null
  size_note: >
    Exact instance count is not published; the MedHELM paper lists this as a "New" benchmark with
    "Private" access, built from Stanford's STARR-OMOP clinical data repository, covering after-visit
    instructions for outpatient surgeries and procedures with discharge within 24 hours. Records are
    filtered to those with a QC="TRUE" quality-control flag before use. The dataset cannot be shared
    outside Stanford's institutional data use agreements because it contains real patient records, so
    an item count was not confirmed from a public source for this page.
  url: ""
  license: "Not public; restricted under Stanford Health Care institutional data use agreements and patient privacy protections, per the MedHELM paper"
  languages:
    - en
  modalities:
    - text
  splits: "All instances assigned to the test split (zero-shot); no public train/validation split"
  public_test_set: false
publisher:
  org: "Stanford Center for Research on Foundation Models (CRFM), in partnership with Stanford Health Care"
  authors:
    - "Suhana Bedi"
    - "Hejie Cui"
    - "Miguel Fuentes"
  url: "https://crfm-helm.readthedocs.io/en/latest/medhelm/"
paper:
  title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks"
  arxiv: "2505.23802"
  url: "https://arxiv.org/abs/2505.23802"
  year: 2025
leaderboard_url: "https://crfm-helm.readthedocs.io/en/latest/medhelm/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/starr_patient_instructions_scenario.py"
released: "2025-05"
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
    Not established from the sources read for this page; the MedHELM paper reports aggregate
    findings across its 35-benchmark suite (advanced reasoning models scoring highest overall, with
    Claude 3.5 Sonnet offering comparable results at lower estimated cost) but no per-benchmark score
    for this specific scenario was found in the material read.
contamination:
  risk: low
  note: >
    The dataset is drawn from real, private Stanford Health Care patient records under institutional
    data use agreements and is explicitly not publicly shareable, so it cannot appear in web-scale
    pretraining corpora the way public benchmarks can. This also means results cannot be
    independently reproduced or audited outside Stanford's own evaluation infrastructure.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "starr_patient_instructions"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - clinical
  - medical
  - patient-communication
  - generation
  - private-dataset
  - helm
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/starr_patient_instructions_scenario.py"
    title: "HELM starr_patient_instructions_scenario.py source (scenario description, STARR-OMOP data source, five required fields, QC filter, test-only split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "HELM MedHELM schema (display name PatientInstruct, taxonomy: text generation / clinician / post-procedure, metric list including starr_patient_instructions_accuracy)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "Bedi et al., 'MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks' (arXiv abstract: authors, 5 categories/22 subcategories/121 tasks/35 benchmarks, 9 LLMs evaluated)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2505.23802v2"
    title: "MedHELM paper HTML (Table 7/8: PatientInstruct listed under Patient Communication & Education, curation status New, access Private)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-004"
---

## What it measures

STARR Patient Instructions, shown as "PatientInstruct" in MedHELM's own taxonomy, gives a model real
clinical case details -- a diagnosis, the procedure performed, and the history-and-physical and
operative notes -- and asks it to generate clear, actionable instructions for a patient recovering
from that procedure. It falls under MedHELM's "Patient Communication and Education" category and
targets clinician-facing-to-patient-facing text synthesis: turning clinical documentation into
instructions a patient can actually follow, not diagnosis or treatment-planning reasoning.

## How it is scored

HELM combines two kinds of metric. Automatic summarization metrics (a BERTScore-based comparison
against the real discharge instructions on file) run alongside an LLM-as-judge score named
`starr_patient_instructions_accuracy`, computed by HELM's LLMJuryMetric, which uses a panel of
annotator language models to rate generated instructions rather than relying on surface overlap with
the reference text alone. No numeric ceiling, random baseline or human baseline for this specific
metric was found in the sources read for this page.

## Dataset and licence

The scenario is built from Stanford's STARR-OMOP clinical data repository, covering after-visit
instructions for outpatient surgeries and procedures with same-day (within 24 hours) discharge. Each
instance requires five fields -- Diagnosis, ActualProcedure, HistoryPhysicalNoteText,
OperativeNoteText and DischargeInstructionNoteText -- and only records flagged QC="TRUE" are used.
The MedHELM paper lists this benchmark as newly created for the study with "Private" access: it
cannot be shared outside Stanford's institutional data use agreements and patient privacy
protections, so no public URL, licence or exact item count was found for this page.

## Who publishes it

The scenario was built by the Stanford Center for Research on Foundation Models (CRFM) in
partnership with Stanford Health Care, as part of the MedHELM evaluation suite described in Bedi et
al., "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks" (2025), a
multi-institution collaboration with 81 listed authors including Percy Liang and Nigam H. Shah. HELM
maintains the code and documentation for running it.

## Lineage

This scenario has no predecessor, successor or variant tracked in this repository. The MedHELM paper
reports 13 newly developed benchmarks and 14 benchmarks with private access (STARR Patient
Instructions is one of both, per its "New"/"Private" listing), out of 35 benchmarks total spanning
MedHELM's five task categories; the paper does not specify how many of the 14 private benchmarks
came from the Stanford Health Care partnership specifically versus other private sources. None of
MedHELM's other benchmarks have pages in this repository yet.

## Saturation and contamination

No per-benchmark leaderboard score for this specific scenario was found in the sources read for this
page; the MedHELM paper's headline results are reported in aggregate across its full 35-benchmark
suite (advanced reasoning models led, with Claude 3.5 Sonnet reported as competitive at lower
estimated cost), not broken out per task in the material read, so saturation status is not
established. Contamination risk is low: because the data is a private, real-patient clinical
resource restricted by institutional data use agreements, it is not part of any public web crawl and
cannot appear in general pretraining corpora, though this also means independent verification of
results is only possible within Stanford's own evaluation setup.

## How to run it

Implemented in HELM as the `starr_patient_instructions` scenario
(`helm/benchmark/scenarios/starr_patient_instructions_scenario.py`), paired with the
`StarrPatientInstructionsAnnotator` for the LLM-jury scoring step. Because the underlying clinical
data is private, the scenario cannot be run outside Stanford's own HELM deployment with access to
the STARR-OMOP source files; no other harness (lm-evaluation-harness, inspect_evals, OpenCompass,
BIG-bench) implementation exists for it.

## Reading the numbers

A strong score here suggests a model can turn dense clinical documentation into instructions a real
patient could plausibly follow after a procedure, a practically important but narrow skill distinct
from clinical reasoning or diagnosis. Because scoring blends an LLM-jury judgment with automatic
summarization metrics, results depend on which models serve as judges, a choice that is not
independently confirmed from the sources read for this page; because the dataset is private and
results are not independently reproducible outside Stanford's infrastructure, treat any score on this
benchmark as reported, not independently verifiable.
