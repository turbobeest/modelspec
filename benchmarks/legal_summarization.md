---
id: legal_summarization
name: "Legal summarization (HELM)"
aliases:
  - "billsum_legal_summarization"
  - "multilexsum_legal_summarization"
  - "eurlexsum_legal_summarization"
page_kind: benchmark
category: domain
subcategory: "HELM English legal-document summarization (BillSum, MultiLexSum, EurLexSum)"
status: unknown
summary: "HELM group that scores English summaries of US bills, US civil-rights case writeups, and EU acts with ROUGE-2."
measures: >
  legal_summarization is HELM's group over three published legal summarization
  corpora, not a new item set. The model receives a truncated source document
  and must write a summary. BillSum uses US bill text. MultiLexSum, in this
  harness, feeds the expert long summary and asks for the short summary, not
  the raw multi-document case file. EurLexSum uses the English EU legal act
  and its official summary. HELM currently loads only English EurLexSum.
  Generation, English text.
task_format: >
  Prompt pattern in the scenario docstring: "Summarize the given document.
  Document: … Summary: …". Three @run_spec_function names share groups
  legal_summarization and summarization. Temperature default 0.3. Scenario
  class .name is "summarization", which is not a run spec.
metric:
  name: rouge_2
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml sets main_name rouge_2 and main_split test for all three
    run groups, with additional summarization_metrics, bias and toxicity.
    get_summarization_metric_specs is passed a task key matching each dataset.
    No official random or human baseline is defined in the scenario. There is
    no published average across BillSum, MultiLexSum and EurLexSum.
dataset:
  size: null
  size_note: >
    Three corpora, scored separately. BillSum (FiscalNote/billsum, CC0-1.0):
    train 18,949, test 3,269, ca_test 1,237; HELM does not mention ca_test.
    Train items are further filtered to 200–800 whitespace tokens; all splits
    truncate at 2,048 tokens. MultiLexSum (allenai/multi_lexsum, HELM config
    v20220616): Hugging Face card table lists 3,177/454/908 cases with
    2,210/312/616 short summaries; HELM skips empty summary/short rows and
    uses summary/long as the input. EurLexSum English JSONL counted here:
    train 1,129, validation 187, test 188 (CC-BY-4.0). HELM train-length
    filters: MultiLexSum 100–400 tokens, EurLexSum 400–1,600; doc_max_length
    1,024 and 2,048 respectively. Exact HELM test n after filters was not
    re-run.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_summarization_scenario.py"
  license: "Mixed: BillSum CC0-1.0; MultiLexSum ODC-By (summaries/metadata CC BY-NC); EurLexSum CC-BY-4.0; HELM code Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "per dataset train/validation/test as published; BillSum has no validation split; HELM main_split test"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM); datasets from FiscalNote, Allen AI / Civil Rights Litigation Clearinghouse, and Heidelberg EUR-Lex-Sum"
  authors:
    - "Joel Niklaus"
    - "Anastassia Kornilova"
    - "Vladimir Eidelmann"
    - "Zejiang Shen"
    - "Dennis Aumiller"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_summarization_scenario.py"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_summarization_scenario.py"
released: "2023-04"
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
    No numeric HELM classic leaderboard cell was read (the public page is a
    JavaScript app). HELM entered maintenance mode on 2026-06-01. The three
    datasets remain separately reported in summarization papers.
contamination:
  risk: medium
  note: >
    All three source corpora are public Hugging Face datasets (BillSum 2019,
    MultiLexSum 2022, EurLexSum 2022). HELM's grouping has been in the
    repository since PR 1454 merged 2023-04-05. Gold summaries are in the
    downloadable files.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "billsum_legal_summarization"
  opencompass: ""
  bigbench: ""
  other: "Also multilexsum_legal_summarization and eurlexsum_legal_summarization in classic_run_specs.py. Group name legal_summarization. Scenario.name summarization is not a @run_spec_function. HELM also has a separate legal_contract_summarization scenario, not this id."
tags:
  - legal
  - summarization
  - helm
  - billsum
  - multilexsum
  - eurlexsum
  - rouge
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/legal_summarization_scenario.py"
    title: "HELM legal_summarization_scenario.py (BillSum, MultiLexSum long→short, EurLexSum English, ROUGE-2 metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py (three run specs, length caps, temperature 0.3)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (rouge_2 main_metric for the three groups)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/FiscalNote/billsum"
    title: "FiscalNote/billsum card (CC0-1.0; train 18949, test 3269, ca_test 1237)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/multi_lexsum"
    title: "allenai/multi_lexsum card (ODC-By / CC BY-NC summaries; split table; v20220616)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/dennlinger/eur-lex-sum"
    title: "dennlinger/eur-lex-sum card (CC-BY-4.0; 24 EU languages; 187/188 aligned val/test)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1910.00523"
    title: "BillSum: A Corpus for Automatic Summarization of US Legislation"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.10883"
    title: "Multi-LexSum: Real-World Summaries of Civil Rights Lawsuits at Multiple Granularities"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2210.13448"
    title: "EUR-Lex-Sum: A Multi- and Cross-lingual Dataset for Long-form Summarization in the Legal Domain"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/pull/1454"
    title: "HELM PR 1454 Add legal summarization scenarios (Joel Niklaus, merged 2023-04-05)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01; classic leaderboard URL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-011 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-011"
---

## What it measures

legal_summarization is HELM's wrapper around three English legal summarization
sets. The model reads a truncated document and writes a summary. BillSum is US
congressional bill text to a bill summary. MultiLexSum in this scenario is not
the original multi-document task: HELM copies the expert long summary into the
prompt and scores the short summary. EurLexSum is an EU legal act (the
`reference` field) paired with the Publications Office summary, English config
only, even though the source dataset has 24 languages. This is not
[legalbench](legalbench.md), not [legal_support](legal_support.md), and not
HELM's separate contract-summarization scenario.

## How it is scored

schema_classic.yaml names ROUGE-2 as the headline on the test split for each of
the three groups. HELM also records other ROUGE/BLEU-style summarization
metrics plus generative-harm scores. Defaults: sampling temperature 0.3;
BillSum max_tokens 1,024; MultiLexSum 256 tokens with a two-sentence adapter
hint; EurLexSum 2,048 tokens. Those caps come from the dataset papers as cited
in classic_run_specs.py, then reduced "for economic reasons" on training
document length. There is no official macro-average across the three datasets.
A BillSum ROUGE-2 is not a MultiLexSum ROUGE-2.

## Dataset and licence

BillSum on Hugging Face (FiscalNote/billsum) lists CC0-1.0 and 18,949 / 3,269 /
1,237 rows for train, test and California extra test. HELM's BillSum path
loads hub name `billsum` and ignores `ca_test` in the scenario code. MultiLexSum
is ODC-By for the dataset distribution, with case summaries and metadata under
CC BY-NC on the card; HELM pins Hugging Face config `v20220616`. The card table
gives 616 test rows with a short summary; HELM drops empty short fields, so
scored n is that non-empty subset, not 908 cases. EurLexSum is CC-BY-4.0. The
English JSONL files counted here have 1,129 train, 187 validation and 188 test
rows, matching the paper's 375 fully aligned acts split 187/188. HELM code is
Apache-2.0 and does not set the dataset licences.

## Who publishes it

Joel Niklaus added the HELM scenario in PR 1454, merged 2023-04-05. The
underlying sets are Kornilova and Eidelmann, BillSum (arXiv 1910.00523, ACL
anthology D19-5406); Shen and colleagues, Multi-LexSum (arXiv 2206.10883); and
Aumiller, Chouhan and Gertz, EUR-Lex-Sum (arXiv 2210.13448). Stanford CRFM
maintains the harness. HELM's classic leaderboard URL still exists; the
framework entered maintenance mode on 2026-06-01.

## Lineage

This id is a HELM grouping, not a fourth corpus. Each dataset remains a
standalone summarization resource with its own paper. HELM also ships
legal_contract_summarization, [legalbench](legalbench.md) tasks, LexGLUE and
LEXTREME; those are different scenarios. [arabic_legal](arabic_legal.md) is
UAE-law Arabic QA, not summarization.

## Saturation and contamination

No current HELM ROUGE-2 table was parsed from the JavaScript classic frontend.
The three public corpora predate the HELM wrapper, so web-trained models may
have seen bills, clearinghouse summaries, or EUR-Lex HTML. Treat contamination
as at least medium. Truncation to 1,024–2,048 whitespace tokens means a high
score is not evidence the model read a 200-page case file.

## How to run it

HELM Classic: `billsum_legal_summarization`, `multilexsum_legal_summarization`,
or `eurlexsum_legal_summarization`. All three attach groups `legal_summarization`
and `summarization`. There is no `@run_spec_function("legal_summarization")`.
Compare numbers only within one dataset, one truncation, one max_tokens, and
the same ROUGE implementation. Do not treat long-to-short MultiLexSum as the
NeurIPS multi-document setting.

## Reading the numbers

A high BillSum ROUGE-2 means n-gram overlap with US bill summaries on HELM's
truncated test bills. A high MultiLexSum score in HELM means the model
compressed an already-written long summary toward the short one. A high
EurLexSum score is overlap with EU official summaries of English acts, 188 test
documents in the files counted here. None of these scores is legal advice
quality, citation correctness, or multilingual coverage. Read them beside
[legalbench](legalbench.md) if the claim is about legal reasoning rather than
summary wording.
