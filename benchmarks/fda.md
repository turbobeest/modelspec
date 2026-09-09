---
id: fda
name: "FDA (BASED information extraction)"
aliases:
  - "BASED FDA"
  - "EVAPORATE FDA"
page_kind: benchmark
category: domain
subcategory: "zero-shot key-value extraction from FDA 510(k) PDF chunks"
status: unknown
summary: "Zero-shot extraction of labelled values from chunked FDA 510(k) PDFs; lm-eval scores whether the gold value appears in a short continuation."
measures: >
  fda is not a drug-approval exam and not an FDA-wide leaderboard. It is the
  information-extraction slice that Arora et al. 2024 (BASED) built on the FDA
  510(k) PDFs labelled in Arora et al. 2023 (EVAPORATE). The model sees a text
  chunk from a premarket-notification review plus a field name, and must
  continue with the value of that field. English text only. The original
  EVAPORATE setting used 100 PDFs (up to about 20 pages) and 16 gold
  attributes sampled from FDA 510(k) reviews since 1996. BASED and lm-eval
  score chunked prompts, not whole-document OpenIE.
task_format: >
  Zero-shot generate-until. Prompt template is "{chunk}\\n{key}:" after
  stripping surrounding whitespace from the Hugging Face `text` field. The
  model may emit at most 48 tokens, stopping at a newline. Scoring is
  case-insensitive substring match of the stripped gold `value`.
metric:
  name: contains
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-eval reports the mean of a binary contains indicator: 1 if the gold
    value appears anywhere in the continuation, ignoring case. BASED calls
    this accuracy. There is no published random or human baseline for the
    1,102-prompt Hugging Face split. Short or common gold strings can match
    by chance; the 48-token cap limits how much extra text the model can dump.
dataset:
  size: 1102
  size_note: >
    Hugging Face `hazyresearch/based-fda` default config has a single
    validation split of 1,102 examples (dataset-viewer and card both say
    1,102). Fields are doc_id, file_name, key, value, text. lm-eval exposes
    only that validation split (no train, no test). EVAPORATE's raw FDA
    setting was 100 PDFs and 16 attributes; the 1,102 figure is the BASED
    chunked prompt set, not 100 documents.
  url: "https://huggingface.co/datasets/hazyresearch/based-fda"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "validation only (1,102); no train or test split in the Hub card or in lm-eval"
  public_test_set: true
publisher:
  org: "Hazy Research (Stanford University and collaborators)"
  authors:
    - "Simran Arora"
    - "Sabri Eyuboglu"
    - "Michael Zhang"
    - "Aman Timalsina"
    - "Silas Alberti"
    - "Dylan Zinsley"
    - "James Zou"
    - "Atri Rudra"
    - "Christopher Ré"
  url: "https://github.com/HazyResearch/based-evaluation-harness"
paper:
  title: "Simple linear attention language models balance the recall-throughput tradeoff"
  arxiv: "2402.18668"
  url: "https://arxiv.org/abs/2402.18668"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/fda"
released: "2024-02"
last_updated: "2026-06"
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
    BASED Table 1 reports FDA among recall-intensive tasks for small linear
    attention models. No current public leaderboard cell for the 1,102-prompt
    lm-eval task was opened here, so no top_score is recorded.
contamination:
  risk: medium
  note: >
    The 1,102 prompts and gold values are public on Hugging Face
    (created 2024-03-12). Source PDFs are public FDA 510(k) reviews. BASED
    chunks at 1,920 tokens, which is not a hidden test set. No source opened
    here demonstrated memorisation of this split.
harness:
  lm_eval: "fda"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    ConfigurableTask class `FDA` in lm_eval/tasks/fda/task.py;
    DATASET_PATH hazyresearch/based-fda; VERSION 1. v1 (2026-06-22, PR 3795)
    strips whitespace on prompt and gold; v0 scores are not comparable.
tags:
  - information-extraction
  - fda-510k
  - long-context-recall
  - generate-until
  - medical-devices
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fda/README.md"
    title: "lm-eval fda README (BASED protocol, EVAPORATE citations, v1 changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fda/task.py"
    title: "lm-eval FDA task class (contains metric, 48-token generate_until)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fda/fda.yaml"
    title: "lm-eval fda.yaml (task: fda)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hazyresearch/based-fda"
    title: "Hugging Face hazyresearch/based-fda (1,102 validation examples)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hazyresearch/based-fda"
    title: "Hub API card for based-fda (no licence tag)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.18668"
    title: "BASED paper HTML (FDA appendix: 1,920-token chunks, contains accuracy)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.18668"
    title: "BASED paper abstract (arXiv:2402.18668)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2304.09433"
    title: "EVAPORATE paper HTML (100 FDA 510(k) PDFs, 16 gold attributes)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2304.09433"
    title: "EVAPORATE paper abstract (arXiv:2304.09433)"
    accessed: "2026-09-08"
  - url: "https://github.com/HazyResearch/evaporate"
    title: "HazyResearch/evaporate repository (no licence in GitHub API)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-043 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-043"
---

## What it measures

fda tests whether a language model can copy a labelled field out of a long
FDA 510(k) review chunk. The prompt is the chunk, a newline, and the field
name followed by a colon. The gold is the string that annotators treated as
that field's value. BASED built the prompts for small, not instruction-tuned
models: the task is next-token continuation, not a JSON schema dump.

The documents come from EVAPORATE's FDA setting: 100 premarket-notification
PDFs scraped from the FDA site, converted to text, with 16 attributes that
five database graduate students all agreed were useful. BASED then splits
those texts into 1,920-token chunks and keeps every key-value pair that
falls inside a chunk. Hugging Face `based-fda` stores 1,102 such prompts.

## How it is scored

lm-eval generates until a newline or 48 tokens, then checks whether the gold
value is a case-insensitive substring of that continuation. The headline
number is the mean of those 0/1 flags. BASED's appendix uses the same
template and the same "contains" rule and calls it accuracy. It is not span
F1, not exact match of the whole field, and not EVAPORATE's OpenIE pair F1
over full documents. v1 of the lm-eval task (2026-06-22, PR 3795) strips
leading and trailing whitespace from prompt and gold; older contains scores
are not comparable.

## Dataset and licence

The runnable set is `hazyresearch/based-fda`, validation only, 1,102 rows.
The Hub card and dataset-viewer both report that count. The card has no
licence field. The EVAPORATE GitHub repository also has no licence in the
GitHub API, so licence is left empty. HazyResearch/based-evaluation-harness
is MIT; that covers the harness, not this prompt file. Source PDFs are US
government 510(k) reviews; that does not licence the BASED split.

## Who publishes it

Hazy Research authors. EVAPORATE (Arora, Yang, Eyuboglu, Narayan, Hojel,
Trummer, Ré; arXiv 2023-04, later PVLDB) collected the PDFs and labels.
BASED (Arora, Eyuboglu, Zhang, Timalsina, Alberti, Zinsley, Zou, Rudra, Ré;
arXiv 2024-02) defined the chunked zero-shot protocol that lm-eval copies.
EleutherAI maintains the harness task.

## Lineage

EVAPORATE is a document-IE system paper, not this prompt set. BASED reuses
the FDA labels as one recall-intensive probe beside SWDE and a reformatted
SQuAD. There is no family page in this repository. Do not confuse the id
with FAERS, MedQA, or any FDA staff exam.

## Saturation and contamination

No current top score for the 1,102-prompt split was read from a leaderboard.
BASED used the task to separate small linear-attention models, not to claim
a ceiling. The prompts are public. Gold values also appear in the public
510(k) PDFs, so substring leakage into pretraining is plausible.

## How to run it

`lm_eval --tasks fda`. The YAML only names class `task.FDA`. Do not report a
v0 contains number next to a v1 number. Inspect and HELM do not ship this
id. EVAPORATE-CODE+ F1 on 100 PDFs is a different metric and a different
unit of analysis.

## Reading the numbers

A high contains score means the gold string showed up in a 48-token
continuation after the field name. It does not mean the model filled a
schema, calibrated a 510(k) decision, or extracted every attribute in a
20-page PDF. Short values match more easily than long ones. Compare only
against other BASED/lm-eval FDA runs that use the same whitespace handling.
Look at SWDE in the same BASED suite if the question is recall over HTML
rather than FDA text.
