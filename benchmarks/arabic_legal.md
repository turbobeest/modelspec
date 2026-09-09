---
id: arabic_legal
name: "Arabic Legal (HELM Arabic Enterprise)"
aliases:
  - "arabic_legal_qa"
  - "arabic_legal_rag"
  - "Arabic Enterprise legal"
page_kind: benchmark
category: domain
subcategory: "UAE-law Arabic short-answer QA, closed-book and open-book"
status: unknown
summary: "HELM's Arabic Enterprise legal set: 200 UAE-law questions scored by an LLM judge, in closed-book and open-book (statute-in-prompt) modes."
measures: >
  arabic_legal is HELM's legal slice of stanford-crfm/arabic-enterprise. Each item is an
  open-ended question in Arabic about United Arab Emirates law, paired with a short Arabic
  reference answer and a statute-like context passage. HELM's schema says Arabic legal experts
  wrote the questions. Two protocols share the same 200 rows: closed-book QA sends only the
  question; open-book RAG prepends the context, then a blank line, then the question. The
  adapter instruction in both cases tells the model to answer briefly in Modern Standard Arabic
  in the setting of UAE law, and to emit the answer only. This is not [legalbench](legalbench.md)
  (English lawyer-authored classification tasks) and not [arabic_exams](arabic_exams.md).
task_format: >
  Short-answer generation in Arabic. arabic_legal_qa: question only. arabic_legal_rag: context
  plus question. An LLM annotator scores 1 if the output is equivalent to the reference answer,
  else 0.
metric:
  name: model_judged_score
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Headline metric in schema_arabic_enterprise.yaml and ArabicLegalMetric is model_judged_score:
    the mean of 0/1 equivalence judgements from ArabicLegalAnnotator (openai/gpt-5.4-2026-03-05,
    temperature 0). ScenarioMetadata on the parent class instead names exact_match as main_metric.
    Those two headlines disagree; reported numbers should say which one was used. No random or
    human baseline is defined for this free-form task. There is no official average of QA and RAG.
dataset:
  size: 200
  size_note: >
    200 test rows in stanford-crfm/arabic-enterprise config legal (Hugging Face datasets-server
    and a direct count of legal.csv). Every row has a non-empty context. original_filename values
    are Arabic statute filenames (for example federal decrees on commercial companies, maritime
    law, civil transactions, bankruptcy). Both HELM protocols iterate the same 200 rows; RAG does
    not add extra items.
  url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
  license: "CC-BY-4.0"
  languages:
    - ar
  modalities:
    - text
  splits: "single test split, 200 rows; HELM runs the same rows as qa or rag"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM Arabic Enterprise)"
  authors:
    - "Yifan Mai (HELM scenario and dataset commits, 2026)"
  url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/arabic_legal_scenario.py"
released: "2026-04"
last_updated: "2026-04"
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
    No public Arabic Enterprise leaderboard URL was found. The dataset card calls this a proposed
    dataset. Run specs are marked EXPERIMENTAL. HELM entered maintenance mode on 2026-06-01. No
    model card in this repository currently cites this id.
contamination:
  risk: medium
  note: >
    Questions, answers and contexts have been public in legal.csv since 20 April 2026 (dataset
    createdAt; lastModified 29 April 2026). HELM pins revision
    35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26. Closed-book scores can be inflated by memorizing
    those 200 answers. Open-book scores still leak the gold answer in the public file, but the
    prompt also supplies the statute passage.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "arabic_legal_qa"
  opencompass: ""
  bigbench: ""
  other: "arabic_legal_rag. Parent Scenario.name arabic_legal is not a @run_spec_function."
tags:
  - legal
  - arabic
  - helm
  - uae-law
  - llm-judge
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/arabic_legal_scenario.py"
    title: "HELM arabic_legal_scenario.py (qa vs rag input construction; pinned HF revision; exact_match in get_metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_enterprise_run_specs.py"
    title: "HELM arabic_enterprise_run_specs.py (arabic_legal_qa / arabic_legal_rag, UAE-law instruction, LLM-judge metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic_enterprise.yaml"
    title: "HELM schema_arabic_enterprise.yaml (closed-book vs open-book descriptions; main_name model_judged_score)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
    title: "stanford-crfm/arabic-enterprise dataset card (CC-BY-4.0; proposed dataset)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=stanford-crfm/arabic-enterprise"
    title: "datasets-server info (legal test: 200 examples)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise/resolve/main/legal.csv"
    title: "legal.csv downloaded and counted (200 rows; context on every row; UAE statute filenames)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/arabic_legal_annotator.py"
    title: "ArabicLegalAnnotator (GPT-5.4 2026-03-05, 0/1 equivalence to the reference answer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/arabic_legal_metric.py"
    title: "ArabicLegalMetric (model_judged_score from annotator)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/stanford-crfm/arabic-enterprise"
    title: "Hugging Face dataset API (created 2026-04-20, revision 35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not the dataset licence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-004 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-004"
---

## What it measures

arabic_legal tests short-answer knowledge of United Arab Emirates law in Arabic. Each of 200
items has a question, a gold answer, and a context passage taken from a named federal statute
file. Closed-book QA (`arabic_legal_qa`) sends only the question. Open-book RAG
(`arabic_legal_rag`) puts the statute passage above the question. Both adapters ask for a brief
Modern Standard Arabic answer in the setting of UAE law, with no extra commentary. HELM's schema
describes the questions as written by Arabic legal experts. The files opened for this page do
not name those experts.

The assigned id is the parent Scenario class `arabic_legal`. The runnable names are
`arabic_legal_qa` and `arabic_legal_rag`. It is not [legalbench](legalbench.md), which is English
and mostly classification. It is not the finance slice of the same repo
([arabic_finance](arabic_finance.md)).

## How it is scored

An annotator model (`openai/gpt-5.4-2026-03-05`, temperature 0) reads the question, the
reference answer and the model output, then must emit a 0 or 1 for equivalence. The metric
`model_judged_score` is the mean of those scores. Changing the judge changes the number. The
parent class's `get_metadata()` instead lists `exact_match` as `main_metric`, while
schema_arabic_enterprise.yaml lists `model_judged_score` for both QA and RAG. A published figure
should say which headline was used. There is no random baseline for free-form legal answers, and
no official average of the two protocols.

The generation adapter default allows up to five in-context examples, but the scenario only
loads the test split, so these runs are zero-shot unless another HELM path injects train items
(not established from the files opened here). Max output tokens is 1000.

## Dataset and licence

`stanford-crfm/arabic-enterprise`, config `legal`, split `test`, has 200 rows. Direct count of
legal.csv matches datasets-server. Every row has context. Filenames point at UAE federal
instruments (commercial companies, maritime law, civil transactions, bankruptcy, tax, and
others). Both protocols use the same 200 rows; RAG is not a second dataset. The card licence is
CC BY 4.0. The card calls the whole hub repo a proposed enterprise dataset. Created 20 April
2026; HELM pins revision `35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26`. Answers and contexts are
public. HELM's code licence is Apache-2.0 and does not replace the dataset licence.

## Who publishes it

Stanford CRFM publishes the dataset and the HELM scenarios. The scenario file lives beside the
finance and content-generation Arabic Enterprise code. No paper or named legal-author list was
found on the dataset card. No public leaderboard URL was found.

## Lineage

This is the legal config of Arabic Enterprise, next to [arabic_finance](arabic_finance.md) and
an article-generation config that is not this assignment. It is not the Open Arabic LLM
Leaderboard aggregations. Run specs are labelled EXPERIMENTAL. No successor id exists in this
repository.

## Saturation and contamination

No top score is recorded. Two hundred short answers judged by one GPT-5.4 prompt are a small,
judge-dependent set. Because the gold answers are public, a closed-book number after April 2026
can reflect memorization of this CSV rather than statute knowledge. The open-book gap (RAG minus
QA) is the more informative contrast: it asks whether the model can use the supplied passage
when it cannot recall the answer.

## How to run it

`pip install crfm-helm`, then `helm-run --run-entries arabic_legal_qa --suite my-suite` or
`arabic_legal_rag`. Do not pass `arabic_legal` without a suffix; that is not a run-spec function.
HELM has been in maintenance mode since 1 June 2026. Compare only the same protocol and the same
judge. Exact string match against the reference, if someone reports it from `get_metadata()`, is
not the schema headline.

## Reading the numbers

A high closed-book `model_judged_score` means the configured GPT-5.4 judge thought the Arabic
output matched the gold short answer. That is not a lawyer's grade and not a guarantee of
correct citation. A high open-book score with a low closed-book score means the model needed the
statute passage. Scores from another judge, or exact_match, are different evaluations. Read
[arabic_finance](arabic_finance.md) for textbook finance items from the same hub repo, and
[legalbench](legalbench.md) for English legal-reasoning tasks with a different skill mix.
