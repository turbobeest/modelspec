---
id: arabic_finance
name: "Arabic Finance (HELM Arabic Enterprise)"
aliases:
  - "arabic_finance_mcq"
  - "arabic_finance_bool"
  - "arabic_finance_calculation"
  - "Arabic Enterprise finance"
page_kind: benchmark
category: domain
subcategory: "Arabic (and English) finance textbook QA: 3-way MCQ, yes/no, numeric calculation"
status: unknown
summary: "HELM's Arabic Enterprise finance set: 299 textbook-derived items in three formats (3-way MCQ, yes/no, numeric calculation), in Arabic or English."
measures: >
  arabic_finance is HELM's finance slice of the stanford-crfm/arabic-enterprise dataset. Each
  item is a short finance question drawn, per HELM's schema, from English-language finance
  textbooks and machine-translated into Arabic. The same 299 rows are stored with English and
  Arabic question, choice and answer fields. HELM splits them into three task formats: 23
  three-option multiple-choice questions (task=mcq), 57 yes/no verifications (task=bool), and
  219 numeric calculation problems (task=calcu). A run is one format and one language (default
  Arabic). It is text-only professional-finance QA, not [financebench](financebench.md) (English
  SEC-filing QA) and not [financeiq](financeiq.md).
task_format: >
  Three HELM run specs share one CSV. MCQ: pick one of three labelled choices (CSV uses A/B/C;
  the Arabic adapter remaps prefixes to أ/ب/ج). Bool: answer نعم/لا or Yes/No. Calculation:
  write reasoning, then a numeric answer inside \\boxed{}; an LLM annotator judges mathematical
  equivalence.
metric:
  name: "exact_match (MCQ); quasi_exact_match (bool, schema headline); calculation_accuracy (calculation)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    MCQ has three options on every item (the scenario asserts len(references)==3), so chance
    is 1/3 if options are balanced. Bool is two-way (Yes/No or نعم/لا). Calculation is free
    numeric; no chance rate. There is no single combined arabic_finance score in
    schema_arabic_enterprise.yaml: each format is its own run group with its own main_name.
    Bool's run spec attaches get_exact_match_metric_specs() (exact_match plus
    quasi_exact_match); the schema headline for bool is quasi_exact_match. Calculation
    accuracy is a 0/1 LLM-judge score averaged over items.
dataset:
  size: 299
  size_note: >
    299 test rows in stanford-crfm/arabic-enterprise config finance (Hugging Face
    datasets-server and a direct count of finance.csv). By task field: mcq 23, bool 57,
    calcu 219. cap_group values in the CSV are Multi 50, NM 50, SP 50, TR 50, TU 50, FF 49;
    HELM's schema does not define those codes, so they are not interpreted here. One test
    split only. Default language is Arabic; English is available via lang=en.
  url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
  license: "CC-BY-4.0"
  languages:
    - ar
    - en
  modalities:
    - text
  splits: "single test split, 299 rows; HELM filters by task=mcq|bool|calcu"
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
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/arabic_finance_scenario.py"
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
    No public Arabic Enterprise leaderboard URL was found. The dataset card calls this a
    proposed dataset. Run specs are marked EXPERIMENTAL. HELM entered maintenance mode on
    2026-06-01. No model card in this repository currently cites this id.
contamination:
  risk: medium
  note: >
    The full test CSV, including English and Arabic answers, has been public on Hugging Face
    since 20 April 2026 (dataset createdAt; lastModified 29 April 2026). HELM pins revision
    35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26. Schema text says the questions come from
    English finance textbooks via machine translation, so some English stems may exist in
    earlier web crawls even if this packaging is new.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "arabic_finance_mcq"
  opencompass: ""
  bigbench: ""
  other: "arabic_finance_bool; arabic_finance_calculation. Parent Scenario.name arabic_finance is not a @run_spec_function. Default lang=ar; English via lang=en (run name gains :lang=en)."
tags:
  - finance
  - arabic
  - helm
  - multiple-choice
  - calculation
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/arabic_finance_scenario.py"
    title: "HELM arabic_finance_scenario.py (parent class and bool/mcq/calcu subclasses; pinned HF revision)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_enterprise_run_specs.py"
    title: "HELM arabic_enterprise_run_specs.py (run spec names, adapters, metrics; EXPERIMENTAL banner)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic_enterprise.yaml"
    title: "HELM schema_arabic_enterprise.yaml (headlines, textbook-MT description, main metrics)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise"
    title: "stanford-crfm/arabic-enterprise dataset card (CC-BY-4.0; proposed dataset; finance/legal/content_generation)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=stanford-crfm/arabic-enterprise"
    title: "datasets-server info (finance test: 299 examples)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanford-crfm/arabic-enterprise/resolve/main/finance.csv"
    title: "finance.csv downloaded and counted (299 rows: mcq 23, bool 57, calcu 219)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/arabic_finance_calculation_annotator.py"
    title: "ArabicFinanceCalculationAnnotator (GPT-5.4 2026-03-05 judge, 0/1 mathematical equivalence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/arabic_finance_calculation_metric.py"
    title: "ArabicFinanceCalculationMetric (calculation_accuracy from annotator score)"
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

arabic_finance tests whether a model can answer short finance questions in Modern Standard
Arabic (or, optionally, in English). HELM's schema says the questions come from English finance
textbooks and were machine-translated into Arabic. The Hugging Face dataset stores both
languages on every row. A run is one of three formats, not a mix: 23 three-option multiple-choice
items, 57 true/false items, and 219 calculation items that need a number. The skill mix is
textbook recall, a binary truth judgement, and arithmetic over a finance formula. It is not
open-book filing QA. That is [financebench](financebench.md). It is not Arabic high-school exams
([arabic_exams](arabic_exams.md)).

The assigned id is the parent Scenario class `arabic_finance`. HELM does not register a run spec
under that exact name. The runnable names are `arabic_finance_mcq`, `arabic_finance_bool` and
`arabic_finance_calculation`.

## How it is scored

MCQ uses joint multiple-choice generation. The CSV labels every choice A/B/C, including on
Arabic rows. The Arabic adapter remaps those option prefixes to أ, ب, ج and the model must
emit one of those letters. In English it emits A, B or C. Headline metric is exact_match.
Three options give a 1/3 chance rate if the labels are balanced.

Bool asks whether a passage is true. Arabic instructions require نعم or لا; English requires
Yes or No. The run spec attaches exact-match style metrics; schema_arabic_enterprise.yaml names
`quasi_exact_match` as the bool headline. Those two names are not the same; a reported bool
score should say which one was used.

Calculation asks for reasoning and a final numeric answer wrapped in `\boxed{}`. An annotator
model (`openai/gpt-5.4-2026-03-05`, temperature 0) judges whether the output is mathematically
equivalent to the reference and writes a 0 or 1. `calculation_accuracy` is the mean of those
scores. Changing the judge model changes the number. There is no official combined score across
the three formats.

The generation adapter defaults to up to five in-context examples, but the scenario only emits
a test split, so the runs are zero-shot unless some other HELM path injects train items (not
established from the files opened here).

## Dataset and licence

`stanford-crfm/arabic-enterprise`, config `finance`, split `test`, has 299 rows. Direct count of
finance.csv matches the datasets-server figure. Task field: mcq 23, bool 57, calcu 219. The card
licence is CC BY 4.0. The card text is one sentence: a proposed dataset for enterprise LLM use
cases in Arabic. Created 20 April 2026; HELM pins revision
`35e114eda2e3450e0e69cf6bda9d3a2f54bf6f26`. Answers are public in both languages. HELM's code
licence is Apache-2.0 and does not replace the dataset licence.

## Who publishes it

Stanford CRFM publishes the dataset and the HELM scenarios. Git history on the scenario file
names Yifan Mai on the 2026-03 and 2026-04 commits, including the switch to the stanford-crfm
Hugging Face org (PR 4236, 29 April 2026). No paper, author list, or public leaderboard for
this slice was found. The dataset card does not name textbook sources beyond HELM's schema
sentence.

## Lineage

This is one of three Arabic Enterprise configs (finance, legal, content_generation). The legal
slice is [arabic_legal](arabic_legal.md). It is not LegalBench, FinanceBench, or the Open Arabic
LLM Leaderboard aggregations ([arabic_leaderboard_complete](arabic_leaderboard_complete.md)).
Run specs are labelled EXPERIMENTAL and may change. No successor id exists in this repository.

## Saturation and contamination

No top score is recorded. Twenty-three MCQ items and fifty-seven bool items are small enough
that a single-run percentage will bounce. The 219 calculation items are the only slice large
enough to look like a benchmark, and they depend on a specific GPT-5.4 judge. The full CSV has
been public since April 2026, so models trained after that date can have seen the answers.
Textbook stems may have been public in English earlier.

## How to run it

`pip install crfm-helm`, then for example
`helm-run --run-entries arabic_finance_mcq --suite my-suite` (Arabic default),
`arabic_finance_bool:lang=en`, or `arabic_finance_calculation`. Do not pass `arabic_finance`
without a suffix; that is not a run-spec function. HELM has been in maintenance mode since
1 June 2026. Compare only the same format, language, and metric name. Calculation scores from
a different judge are a different evaluation.

## Reading the numbers

A high MCQ exact_match on 23 items is a noisy three-way quiz, not a finance-professional exam.
A high bool score is yes/no accuracy on 57 statements. A high calculation_accuracy means the
configured GPT-5.4 judge accepted the boxed number as equivalent 219 times at most; it is not
a human grader and not exact string match. Never average the three formats unless you say you
invented that average. Read [arabic_legal](arabic_legal.md) for UAE-law questions from the same
dataset repo, and an English open-book filing benchmark such as [financebench](financebench.md)
if you need a different finance skill.
