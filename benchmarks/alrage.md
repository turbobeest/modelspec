---
id: alrage
name: "ALRAGE"
aliases:
  - "OALL/ALRAGE"
page_kind: benchmark
category: knowledge
subcategory: "Arabic open-book RAG question answering, GPT-4o graded"
status: active
summary: "OALL's 2,106-item Arabic passage QA set; HELM grades free-form answers with GPT-4o, using the public train split as the test set."
measures: >
  ALRAGE is an Arabic open-book question answering task built to look like retrieval-augmented
  generation. HELM shows the model an Arabic question and a block of suggested passages
  (`candidates`), then asks it to write an answer. The gold string is a short reference answer,
  not a multiple-choice letter. The language is Arabic. The skill is using the supplied passages,
  not browsing the web, and not the closed-book exam mix in [alghafa](alghafa.md).
task_format: >
  Open-ended generation. HELM concatenates "السؤال:" plus the question and "السياقات المقترحة:"
  plus `candidates`. The generation adapter uses Arabic instructions, max_tokens 100, and no stop
  sequences. Scoring is an LLM judge, not string match, despite leftover exact_match metadata on
  the scenario class.
metric:
  name: alrage_score
  direction: higher_is_better
  unit: "0-1"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's Arabic schema headline is alrage_score: GPT-4o (openai/gpt-4o-2024-11-20) returns an
    integer 0-10 that the annotator divides by 10 and clips to [0, 1]. The scenario class still
    lists main_metric exact_match; that field is stale relative to the run spec and schema.
dataset:
  size: 2106
  size_note: >
    Hugging Face datasets-server and the dataset card both report 2,106 rows in a single train
    split on OALL/ALRAGE (revision 4827b2ed2436aea578e84d9bd4150b66ab8bbe0e, the pin HELM uses).
    HELM loads that train split and tags every instance TEST_SPLIT. Fields: id, question,
    gold_answer, candidates.
  url: "https://huggingface.co/datasets/OALL/ALRAGE"
  license: ""
  languages:
    - ar
  modalities:
    - text
  splits: "HF train (2,106) used as HELM test; no separate public test split"
  public_test_set: true
publisher:
  org: "OALL (Open Arabic LLM Leaderboard); HELM scenario by Stanford CRFM"
  authors: []
  url: "https://huggingface.co/datasets/OALL/ALRAGE"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/alrage_scenario.py"
released: "2024-11"
last_updated: "2024-11"
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
    No dated ALRAGE leaderboard cell was read (OALL and HELM Arabic pages did not yield a static
    table). HELM marks the run spec EXPERIMENTAL.
contamination:
  risk: medium
  note: >
    Questions, candidate passages, and gold answers have been public on Hugging Face since
    14 November 2024 (createdAt and lastModified that day). HELM evaluates the entire public
    train file. No canary or private test is described. The set is newer than AlGhafa, so
    training-set leakage is less certain but still plausible for models trained after late 2024.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "alrage"
  opencompass: ""
  bigbench: ""
  other: "HELM run spec alrage; annotator ALRAGEAnnotator; metric ALRAGEMetric. OALL/v2_results scores community|alrage_qa with llm_as_judge, which is not the HELM GPT-4o-2024-11-20 alrage_score snapshot."
tags:
  - arabic
  - rag
  - open-ended
  - llm-judge
  - helm
  - oall
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/alrage_scenario.py"
    title: "HELM ALRAGEScenario (OALL/ALRAGE pin, prompt template, stale exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_run_specs.py"
    title: "HELM alrage run spec (generation adapter, annotator, ALRAGEMetric)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/alrage_annotator.py"
    title: "ALRAGEAnnotator (GPT-4o-2024-11-20, 0-10 Arabic judge prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/alrage_metric.py"
    title: "ALRAGEMetric (alrage_score from annotator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic.yaml"
    title: "HELM schema_arabic.yaml (alrage_score judged by GPT-4o; main_name alrage_score)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OALL/ALRAGE/raw/main/README.md"
    title: "OALL/ALRAGE dataset card (2,106 train rows; no prose licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/OALL/ALRAGE"
    title: "Hugging Face dataset API (created 2024-11-14, sha 4827b2ed…)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=OALL/ALRAGE"
    title: "datasets-server (train: 2106 examples)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_arabic.conf"
    title: "HELM Arabic run entries (alrage:max_train_instances=0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OALL/v2_results"
    title: "OALL v2_results schema (community|alrage_qa llm_as_judge)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-025 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-025"
---

## What it measures

ALRAGE gives a model an Arabic question and a bundle of suggested passages, then asks for a free-form Arabic answer. HELM's prompt labels those two blocks explicitly. The intended use is retrieval-augmented generation with the passages already in the prompt: the model is not required to call a retriever. It is not closed-book [alghafa](alghafa.md) multiple choice, and it is not an English RAG bench.

## How it is scored

The published HELM metric is `alrage_score`. After generation, `ALRAGEAnnotator` sends the question, model answer, and gold answer to `openai/gpt-4o-2024-11-20` with an Arabic rubric that demands a single number from 0 to 10. That number is divided by 10 and clipped to [0, 1]. Temperature for the judge is 0. A parse failure becomes 0.0. The scenario class still advertises `main_metric: exact_match`; the run spec and `schema_arabic.yaml` use `alrage_score` instead. Do not report string exact_match as the HELM headline.

## Dataset and licence

`OALL/ALRAGE` has 2,106 rows in one train split (id, question, gold_answer, candidates). HELM scores that whole file as test. The card was created 14 November 2024 and has no licence field in `cardData` or the README opened here, so licence is not established. Gold answers are public.

## Who publishes it

The dataset is published by the OALL organisation on Hugging Face. No separate ALRAGE paper was found on the card or in HELM. Stanford CRFM added the HELM scenario, annotator, and metric under experimental Arabic run specs. OALL's public space is the practical leaderboard URL; HELM's Arabic UI did not yield a static table when fetched.

## Lineage

ALRAGE is a later Arabic HELM/OALL task, not a revision of [alghafa](alghafa.md). OALL `v2_results` includes `community|alrage_qa` scored with `llm_as_judge`, alongside Native AlGhafa configs, ArabicMMLU, arabic_exams, MadinahQA, AraTrust, and human-translated MMLU. That v2 judge is not this HELM GPT-4o-2024-11-20 `alrage_score`. No successor id exists in this repository.

## Saturation and contamination

Saturation is not established. Contamination risk is medium: the full item bank, including gold answers, has been public since November 2024, and HELM does not hold out a private split. Models trained after that date may have seen the file. The judge model is a specific GPT-4o snapshot; later GPT-4o aliases are not the same scorer.

## How to run it

HELM run spec name `alrage` (`get_alrage_spec` in `arabic_run_specs.py`). Official Arabic entries use `alrage:max_train_instances=0`. Reproducing HELM requires the GPT-4o-2024-11-20 annotator, not exact_match. The run spec is marked EXPERIMENTAL, and HELM entered maintenance mode on 1 June 2026. OALL v2 reports `alrage_qa` with `llm_as_judge`; that cell is not interchangeable with HELM `alrage_score`. lm-evaluation-harness, Inspect Evals, and OpenCompass were not confirmed to ship an `alrage` task.

## Reading the numbers

A high `alrage_score` means this GPT-4o judge liked the Arabic answer relative to the gold string, given the passages in the prompt. It does not measure retrieval quality, citation faithfulness beyond the judge prompt, or closed-book Arabic knowledge. Compare only runs that name the same judge snapshot and the same 2,106-row file. If a reporter quotes exact_match on ALRAGE, they are not using HELM's published headline. An OALL v2 `llm_as_judge` cell is a different protocol.
