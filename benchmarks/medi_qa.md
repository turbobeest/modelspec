---
id: medi_qa
name: MEDIQA (HELM)
aliases:
  - MEDIQA
  - MEDIQA-QA
  - MEDIQA 2019 QA
  - mediqa_qa
page_kind: benchmark
category: domain
subcategory: consumer health question answering
status: active
summary: HELM's generation wrap of MEDIQA 2019 Task 3, scoring a free-form answer to a consumer health question with an LLM jury against the expert-ranked gold answer.
measures: >
  This id is HELM's `medi_qa` scenario, not the 2019 ranking shared task as originally scored, and
  not MedQA. MEDIQA 2019 Task 3 gave a consumer health question plus CHiQA's retrieved answers and
  asked systems to filter and re-rank them. HELM instead takes the test questions, uses the
  expert-ranked number-one answer as the reference, and asks the model to generate an answer from
  the question alone. Inputs and outputs are English text. The original shared task also had NLI
  and recognizing-question-entailment tracks; those are not this id.
task_format: >
  Zero-shot generation. HELM's prompt is "Answer the following consumer health question." The model
  writes free text (max 1,024 tokens). An LLM jury then rates the output against the gold answer.
metric:
  name: "medi_qa_accuracy (HELM LLM-jury average of accuracy, completeness and clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's main metric is an LLM jury, not the 2019 ranking metrics. Each judge scores accuracy,
    completeness and clarity on a 1-5 scale; those scores are averaged. HELM also logs ROUGE and
    BERTScore. The 2019 shared task scored ranking with accuracy, MRR, precision and Spearman's
    rho; its headline QA figure was 78.3% among 72 teams. Those ranking numbers are not on the
    same scale as HELM's jury score. No random or human baseline was established for the HELM
    generation protocol.
dataset:
  size: 150
  size_note: >
    HELM evaluates only the test split of `bigbio/mediqa_qa` (150 questions, 1,107 associated
    answers in the 2019 release). The same Hugging Face mirror also has train_live_qa_med (104
    questions, 839 answers from TREC-2017 LiveQA medical data), train_alexa (104 questions, 862
    answers) and validation (25 questions, 234 answers). HELM's scenario file comments those
    splits out and keeps a zero-shot test-only setup. Each question carries a list of candidate
    answers with SystemRank, ReferenceRank and ReferenceScore; HELM keeps the ReferenceRank=1
    answer as the gold string.
  url: https://huggingface.co/datasets/bigbio/mediqa_qa
  license: "CC-BY-4.0 on the authors' GitHub release; Hugging Face bigbio/mediqa_qa lists licence as unknown"
  languages:
    - en
  modalities:
    - text
  splits: "HELM: 150-question test only. Original release also has 104+104 train and 25 validation questions."
  public_test_set: true
publisher:
  org: "U.S. National Library of Medicine (LHC/NLM) and IBM Research; HELM scenario by Stanford CRFM"
  authors:
    - Asma Ben Abacha
    - Chaitanya Shivade
    - Dina Demner-Fushman
  url: https://sites.google.com/view/mediqa2019
paper:
  title: "Overview of the MEDIQA 2019 Shared Task on Textual Inference, Question Entailment and Question Answering"
  arxiv: ""
  url: https://aclanthology.org/W19-5039/
  year: 2019
leaderboard_url: https://www.aicrowd.com/challenges/mediqa-2019-question-answering-qa/leaderboards
repo_url: https://github.com/abachaa/MEDIQA2019
released: "2019-08"
last_updated: ""
lineage:
  family: ""
  predecessor: live_qa
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The 2019 shared-task QA track reached 78.3% under ranking metrics. No HELM MedHELM leaderboard
    figure for `medi_qa_accuracy` was established from the pages opened for this research, so
    saturation of the HELM protocol is unknown.
contamination:
  risk: high
  note: >
    Test questions, candidate answers and reference ranks have been public on GitHub since 2019,
    including the labelled test file MEDIQA2019-Task3-QA-TestSet-wLabels.xml.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: medi_qa
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec `medi_qa` loads MediQAScenario from bigbio/mediqa_qa at revision
    9288641f4c785c95dc9079fa526dabb12efdb041, generates zero-shot, annotates with MediQAAnnotator,
    and reports medi_qa_accuracy plus summarisation metrics.
tags:
  - medical
  - consumer-health
  - generation
  - llm-judge
  - helm
sources:
  - url: https://aclanthology.org/W19-5039/
    title: "Overview of the MEDIQA 2019 Shared Task (ACL Anthology)"
    accessed: "2026-09-08"
  - url: https://aclanthology.org/W19-5039.pdf
    title: "MEDIQA 2019 overview PDF"
    accessed: "2026-09-08"
  - url: https://github.com/abachaa/MEDIQA2019
    title: "abachaa/MEDIQA2019 GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/bigbio/mediqa_qa
    title: "bigbio/mediqa_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=bigbio/mediqa_qa
    title: "bigbio/mediqa_qa datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medi_qa_scenario.py
    title: "HELM MediQAScenario source"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (medi_qa run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/medi_qa_annotator.py
    title: "HELM MediQAAnnotator source"
    accessed: "2026-09-08"
  - url: https://sites.google.com/view/mediqa2019
    title: "MEDIQA 2019 shared-task site"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

`medi_qa` is HELM's wrap of MEDIQA 2019 Task 3, not MedQA and not the original ranking contest as
scored. The 2019 task gave a consumer health question and a list of answers from NLM's CHiQA
system, then asked teams to drop bad answers and re-rank the rest. HELM keeps the 150 test
questions, takes the expert's rank-1 answer as gold, and asks the model to generate an answer from
the question alone. The input is English consumer prose; the output is free text.

MEDIQA 2019 also ran medical NLI and recognizing-question-entailment tracks. Those datasets and
metrics are separate. This page is only the QA track as HELM reports it.

## How it is scored

HELM's main metric is `medi_qa_accuracy`, an LLM-jury average. Each judge rates accuracy,
completeness and clarity on a 1-5 scale against the gold answer. HELM also records ROUGE and
BERTScore. The 2019 shared task used ranking accuracy, MRR, precision and Spearman's rho, and
quoted 78.3% as the QA-track headline among 72 teams. A HELM jury point is not that percentage.
No random or human baseline was established for the generation protocol.

## Dataset and licence

The 2019 QA release has two 104-question training sets (LiveQA-Med and Alexa), a 25-question
validation set and a 150-question test set, with 839, 862, 234 and 1,107 associated answers.
HELM loads `bigbio/mediqa_qa` and uses only `test`. The authors' GitHub README states CC BY 4.0.
The Hugging Face mirror lists the licence as unknown. Answers and ranks are public.

## Who publishes it

Asma Ben Abacha and Dina Demner-Fushman (Lister Hill Center, NLM) and Chaitanya Shivade (IBM)
organised MEDIQA 2019 at ACL-BioNLP in Florence, August 2019. The overview is ACL Anthology
W19-5039. Stanford CRFM added the HELM scenario. The 2019 ranking leaderboard remains on AIcrowd.

## Lineage

Do not fold this into [MedQA](medqa.md). MedQA is USMLE-style multiple choice. One training file
reuses TREC-2017 LiveQA medical questions, which this repository already documents as
[live_qa](live_qa.md); HELM does not evaluate that split here. Later MEDIQA-Chat and MEDIQA-Sum
shared tasks, and the [aci_bench](aci_bench.md) notes that used them, are different datasets.

## Saturation and contamination

The 2019 ranking track is a historical contest. Whether HELM's jury metric still separates current
models was not established from a live MedHELM table during this research. Contamination risk is
high: the labelled test XML has been on GitHub since 2019.

## How to run it

In HELM, the run spec is `medi_qa`. It generates zero-shot with the instruction "Answer the
following consumer health question.", annotates with `MediQAAnnotator`, and reports
`medi_qa_accuracy`. Judge models come from HELM's jury config; the exact default judges were not
read from a populated config file here. Do not compare a HELM jury score with a 2019 ranking
accuracy without saying so.

## Reading the numbers

A strong HELM `medi_qa` score means a jury of judge models liked the generated answer relative to
CHiQA's expert-picked reference, not that the system ranked CHiQA candidates the way 2019 teams
did. It also does not measure licensing-exam knowledge (that is MedQA). Check whether a reported
figure is jury score, ROUGE/BERTScore, or 2019 ranking accuracy before comparing models.
