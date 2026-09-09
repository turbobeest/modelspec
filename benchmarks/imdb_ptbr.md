---
id: imdb_ptbr
name: "IMDb PT-BR (HELM)"
aliases:
  - "imdb_pt"
  - "maritaca-ai/imdb_pt"
  - "IMDB PT-BR"
page_kind: benchmark
category: reasoning
subcategory: "Brazilian Portuguese binary movie-review sentiment (Maritaca translation; HELM scenario)"
status: unknown
summary: "HELM scenario that classifies Maritaca's Portuguese IMDb reviews as positivo or negativo; the scored test file has 5,000 balanced rows."
measures: >
  imdb_ptbr asks a model to read a Portuguese movie review and label it
  positivo or negativo. HELM wraps Maritaca AI's Hub dump maritaca-ai/imdb_pt,
  a Portuguese translation of the Stanford Large Movie Review Dataset. The
  English source used only strongly polar reviews. The probe is Brazilian
  Portuguese sentiment classification, not English [imdb](imdb.md) and not
  HELM's contrast-set English IMDb scenario.
task_format: >
  Binary sentiment generation in Portuguese. HELM's run spec prompts with
  two fixed in-context reviews, then "Resenha:" and "Classe:", and expects
  positivo or negativo. The scenario maps Hub labels 0/1 to those strings.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Two classes, and the 5,000-row test.csv is balanced 2,500/2,500, so
    uniform chance is 50%. HELM also attaches classification metric specs
    beside exact match. No Portuguese human baseline was found. English IMDb
    transformer ceilings of 95-97% on the Stanford page must not be copied
    here.
dataset:
  size: 5000
  size_note: >
    HELM loads Hub splits train (25,000) and test (5,000) from
    maritaca-ai/imdb_pt and does not load test_all (25,000). A csv count of
    test.csv is 5,000 rows, 2,500 positivo and 2,500 negativo; that is the
    size recorded here as the published test file. The loader description
    still repeats the English "25,000 for testing" line, which matches
    test_all rather than test. This page did not hash texts to prove whether
    test is a subset of test_all.
  url: "https://huggingface.co/datasets/maritaca-ai/imdb_pt"
  license: ""
  languages:
    - pt
  modalities:
    - text
  splits: "train 25,000 / test 5,000 / test_all 25,000; HELM get_instances uses train and test"
  public_test_set: true
publisher:
  org: "Maritaca AI (Portuguese dump); Stanford CRFM HELM (scenario); Stanford NLP (English source dataset)"
  authors:
    - "Andrew L. Maas"
    - "Raymond E. Daly"
    - "Peter T. Pham"
    - "Dan Huang"
    - "Andrew Y. Ng"
    - "Christopher Potts"
  url: "https://huggingface.co/datasets/maritaca-ai/imdb_pt"
paper:
  title: "Learning Word Vectors for Sentiment Analysis"
  arxiv: ""
  url: "https://aclanthology.org/P11-1015/"
  year: 2011
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/imdb_ptbr_run_specs.py"
released: "2023-01"
last_updated: "2023-04"
lineage:
  family: ""
  predecessor: "imdb"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No HELM leaderboard schema or numeric cell for imdb_ptbr was found
    (there is no schema_imdb_ptbr.yaml next to schema_tweetsentbr.yaml).
    English IMDb is saturated on this repository's imdb page; that ceiling
    was not re-measured on the Portuguese dump.
contamination:
  risk: high
  note: >
    Train, test, and test_all labels are public on the Hub (dataset created
    2023-01-26). The English reviews have been public since 2011. HELM
    scores the public test split. No canary or held-out key is described.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "imdb_ptbr"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec function is decorated imdb_ptbr but the Python def is still
    named get_tweetsentbr_spec. Scenario class IMDB_PTBRScenario sets
    name = "simple_classification"; the runnable HELM name is the run spec
    imdb_ptbr. Dataset load_dataset("maritaca-ai/imdb_pt").
tags:
  - sentiment-classification
  - portuguese
  - brazil
  - helm
  - translation
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/imdb_ptbr_scenario.py"
    title: "HELM IMDB_PTBRScenario (maritaca-ai/imdb_pt; labels negativo/positivo; train+test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/imdb_ptbr_run_specs.py"
    title: "HELM run spec imdb_ptbr (generation, exact_match + classification metrics, 2-shot Portuguese instructions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/maritaca-ai/imdb_pt"
    title: "Hub API (created 2023-01-26, lastModified 2023-04-01, empty license field)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=maritaca-ai/imdb_pt"
    title: "datasets-server (train 25000, test 5000, test_all 25000; ClassLabel negativo/positivo)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/maritaca-ai/imdb_pt/resolve/main/imdb_pt.py"
    title: "Hub loader (translated to Portuguese; cites Maas et al. 2011; no licence field)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/maritaca-ai/imdb_pt"
    title: "Hub dataset page"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/imdb_scenario.py"
    title: "HELM English imdb_scenario.py (contrast-set English IMDb, not this task)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/maritaca-ai/imdb_pt/resolve/main/test.csv"
    title: "test.csv (5,000 rows, 2,500/2,500 labels)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-049 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-049"
---

## What it measures

imdb_ptbr is binary sentiment on Portuguese movie reviews. The model reads one review and must answer positivo or negativo. HELM's instructions are in Brazilian Portuguese and include two short labeled examples before the item.

The text comes from Maritaca AI's `maritaca-ai/imdb_pt` dump, described only as a translation of the Stanford IMDb polarity set. This page did not find a translation-method paper. It is not the English [imdb](imdb.md) HELM scenario, which still scores English reviews and swaps in contrast-set edits.

## How it is scored

The HELM run spec `imdb_ptbr` uses a generation adapter (`Resenha` / `Classe`) and reports exact match plus classification metrics. Target strings are `positivo` and `negativo`. The 5,000-row `test` split is balanced, so chance is 50%.

The scenario class loads both Hub `train` (25,000) and `test` (5,000). It does not load `test_all`. How many in-context Hub rows HELM actually samples on top of the two hard-coded instruction examples was not read from `get_generation_adapter_spec`. Quasi-exact English IMDb scoring on HELM is a different scenario.

## Dataset and licence

Hub splits: 25,000 train, 5,000 test, 25,000 test_all. Features are `text` and a ClassLabel `negativo`/`positivo`. The loader still cites Maas et al. 2011 and repeats "25,000 for testing," which matches `test_all`, not `test`.

No licence is set on the Hub API, the loader, or the dataset card. The English IMDb page in this repository also has no formal licence. Treat reuse terms as not established. All splits including labels are public.

## Who publishes it

Maritaca AI hosts the Portuguese files (Hub created 2023-01-26, last updated 2023-04-01). The English collection is Maas, Daly, Pham, Huang, Ng, and Potts, ACL 2011. Stanford CRFM HELM adds the `imdb_ptbr` scenario and run spec. No dedicated HELM schema or leaderboard file for this id was found. The cited paper is the English dataset paper, not a PT-BR write-up.

## Lineage

Predecessor is [imdb](imdb.md). HELM's English `imdb` run spec is a sibling, not an alias: it reads `aclImdb` and contrast sets. Other Brazilian Portuguese HELM ids in this repository include [enem_challenge](enem_challenge.md) and [healthqa_br](healthqa_br.md); they are exam QA, not sentiment. There is no `tweetsentbr` page here yet, even though the imdb_ptbr run-spec function is still named `get_tweetsentbr_spec`.

## Saturation and contamination

No current Portuguese score was read, so saturation stays unknown. Do not import the English 95-97% transformer ceiling. Contamination risk is high: labels are public, the English reviews are old, and HELM scores a public test file.

## How to run it

HELM run spec name is `imdb_ptbr`. Scenario class is `IMDB_PTBRScenario` in `imdb_ptbr_scenario.py`. The class `.name` field is `simple_classification`; use the run spec name, not that string, when comparing reports. No lm-eval or OpenCompass task with this id was found.

## Reading the numbers

A high exact-match rate means the model emitted the gold Portuguese polarity on Maritaca's test rows under HELM's prompt. It does not measure English IMDb, robustness contrast sets, or general Portuguese. Because `test` is 5,000 public rows and `test_all` is a different 25,000-row file, check which split a report used. Translation quality is not documented, so errors may be translation artifacts rather than model failures.
