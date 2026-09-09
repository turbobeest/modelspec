---
id: medication_qa
name: MedicationQA
aliases:
  - Medication_QA
  - Medication QA MedInfo 2019
  - MedInfo2019-QA-Medications
page_kind: benchmark
category: domain
subcategory: consumer medication question answering
status: active
summary: Open-ended consumer questions about medications paired with trusted reference answers drawn from DailyMed, MedlinePlus and similar sources.
measures: >
  MedicationQA tests whether a model can answer a real consumer question about a drug in plain
  English. Questions come from MedlinePlus users and always have a drug as the focus. Types include
  information, dose, usage, side effects, indication and interaction, among 25 labels in the gold
  standard. Each item pairs the question with one expert-retrieved reference answer and its source
  URL. HELM treats the whole set as a zero-shot generation task. It is not MedQA, not MEDIQA 2019
  ranking, and not a multiple-choice exam.
task_format: >
  Zero-shot generation. HELM's instruction is "Please answer the following consumer health
  question." The model writes free text (max 512 tokens in the HELM run spec).
metric:
  name: "medication_qa_accuracy (HELM LLM-jury average of accuracy, completeness and clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's main metric is an LLM jury on 1-5 ratings of accuracy, completeness and clarity, plus
    ROUGE and BERTScore. The 2019 paper does not report end-to-end answer accuracy for modern LLMs;
    it reports Bi-LSTM-CRF focus recognition and CNN question-type identification on this corpus.
    No random or human answering baseline was established from the sources reviewed.
dataset:
  size: 674
  size_note: >
    The paper and GitHub README state 674 question-answer pairs. Answers were taken from DailyMed
    (290), MedlinePlus (128) and other sites (256). HELM downloads MedInfo2019-QA-Medications.xlsx
    and drops rows whose Answer cell is pandas-NA, then scores every remaining row as test. The
    spreadsheet used range is A1:F691 (header plus 690 data rows). In this review every data row
    had a non-empty Answer cell, so HELM would keep 690 rows, 16 more than the published 674. Mean
    token lengths from the paper's Table 2 were not recovered from the PDF text layer.
  url: https://github.com/abachaa/Medication_QA_MedInfo2019
  license: "CC-BY-4.0 on the GitHub README for the dataset; the MEDINFO 2019 article itself is CC BY-NC 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "No official train/dev/test split; HELM treats the filtered spreadsheet as a single test set."
  public_test_set: true
publisher:
  org: "Lister Hill National Center for Biomedical Communications, U.S. National Library of Medicine; HELM scenario by Stanford CRFM"
  authors:
    - Asma Ben Abacha
    - Yassine Mrabet
    - Mark Sharp
    - Travis Goodwin
    - Sonya E. Shooshan
    - Dina Demner-Fushman
  url: https://github.com/abachaa/Medication_QA_MedInfo2019
paper:
  title: "Bridging the Gap Between Consumers' Medication Questions and Trusted Answers"
  arxiv: ""
  url: https://pubmed.ncbi.nlm.nih.gov/31437878/
  year: 2019
leaderboard_url: ""
repo_url: https://github.com/abachaa/Medication_QA_MedInfo2019
released: "2019"
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
    No standing LLM leaderboard for HELM's medication_qa_accuracy was found during this research.
    The 2019 paper's CNN question-type accuracy (75.7% on a 14-type collapse) is not an answering
    score and is not recorded as top_score.
contamination:
  risk: high
  note: >
    The gold spreadsheet has been public on GitHub since 2019, with questions, answers and source
    URLs ungated.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: medication_qa
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec `medication_qa` loads MedicationQAScenario, generates zero-shot, annotates with
    MedicationQAAnnotator, and reports medication_qa_accuracy plus summarisation metrics.
tags:
  - medical
  - consumer-health
  - medication
  - generation
  - llm-judge
  - helm
sources:
  - url: https://github.com/abachaa/Medication_QA_MedInfo2019
    title: "abachaa/Medication_QA_MedInfo2019 GitHub repository"
    accessed: "2026-09-08"
  - url: https://pubmed.ncbi.nlm.nih.gov/31437878/
    title: "PubMed record for the MEDINFO 2019 MedicationQA paper"
    accessed: "2026-09-08"
  - url: https://lhncbc.nlm.nih.gov/LHC-publications/PDF/pub9965.pdf
    title: "NLM PDF of Bridging the Gap Between Consumers' Medication Questions and Trusted Answers"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medication_qa_scenario.py
    title: "HELM MedicationQAScenario source"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (medication_qa run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/medication_qa_annotator.py
    title: "HELM MedicationQAAnnotator source"
    accessed: "2026-09-08"
  - url: https://doi.org/10.3233/SHTI190176
    title: "IOS Press DOI 10.3233/SHTI190176"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

MedicationQA asks a model to answer a real consumer question about a drug. The questions were
submitted to MedlinePlus, then filtered so that a drug name is the focus and the wording is
answerable. Types span information, dose, usage, side effects, indication, interaction and other
labels, 25 in all. Each gold item has one reference answer that annotators retrieved from
DailyMed, MedlinePlus, other NIH or government sites, or a short list of trusted publishers. The
task is English, open-ended, and about medication facts a patient might ask, not a clinical
vignette or an exam item.

HELM uses that gold file as a generation benchmark. The model sees only the question. It does not
see the candidate pages the original annotators searched.

## How it is scored

HELM's main metric is `medication_qa_accuracy`, an LLM-jury mean of accuracy, completeness and
clarity, each on a 1-5 scale against the gold answer. ROUGE and BERTScore are logged as well. The
2019 paper does not publish an LLM answering score. It reports a Bi-LSTM-CRF for drug-name focus
recognition and a CNN for question type, plus a qualitative look at CHiQA. Those figures are not
substitutes for the HELM jury score. No random-guess or human answering baseline was found.

## Dataset and licence

The paper and README state 674 pairs. DailyMed supplied 290 answers, MedlinePlus 128, and other
sites 256. There is no official train/dev/test split. The xlsx used range is A1:F691, and every
one of the 690 data rows had an Answer cell in this review, so a HELM `Answer.isna()` filter would
keep 690 items rather than 674. The GitHub README licences the dataset as CC BY 4.0. The MEDINFO
2019 article PDF is marked CC BY-NC 4.0. Use the dataset licence for the spreadsheet and do not
treat the article licence as a second dataset term.

## Who publishes it

Asma Ben Abacha, Yassine Mrabet, Mark Sharp, Travis Goodwin, Sonya E. Shooshan and Dina
Demner-Fushman at NLM's Lister Hill Center released the corpus with the MEDINFO 2019 paper
(DOI 10.3233/SHTI190176). Stanford CRFM added the HELM scenario. No standing public answering
leaderboard was found.

## Lineage

This is not [MedQA](medqa.md) and not [medi_qa](medi_qa.md). MedQA is USMLE multiple choice.
`medi_qa` is HELM's wrap of MEDIQA 2019 Task 3, a ranking set built from CHiQA output. MedicationQA
is a later NLM gold set of medication questions only. [MeQSum](meqsum.md) summarises long consumer
questions; it does not answer them. [live_qa](live_qa.md) is the TREC-2017 LiveQA medical test set.

## Saturation and contamination

No current HELM leaderboard number was established here, so saturation is unknown. Contamination
risk is high: questions, answers and URLs have been public since 2019.

## How to run it

In HELM, the run spec is `medication_qa`. It generates zero-shot and annotates with
`MedicationQAAnnotator`. Judge models come from HELM's jury config; the populated default was not
opened here. Compare only jury scores with other HELM MedHELM jury scores, not with 2019 CNN type
accuracy.

## Reading the numbers

A high HELM score means judge models thought the generated answer matched a trusted drug-label
snippet on accuracy, completeness and clarity. It does not mean the model is safe to advise
patients, and it does not test exam-style diagnosis. Many gold answers are copied from DailyMed or
MedlinePlus, so overlap with those pages can inflate a score. Read it next to MEDIQA and LiveQA
for broader consumer QA, not as a clinical-reasoning exam.
