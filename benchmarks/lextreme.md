---
id: lextreme
name: "LEXTREME"
aliases:
  - "Lextreme"
  - "Multilingual Legal Benchmark for Natural Language Understanding"
page_kind: family
category: domain
subcategory: "multilingual legal NLU (11 datasets, 18 HELM tasks, 24 EU languages in the paper)"
status: active
summary: "Multilingual legal suite of 11 datasets / 18 HELM tasks; paper aggregate 61.3 for XLM-R large, later GitHub table higher for legal-adapted encoders."
measures: >
  LEXTREME scores legal NLU across languages rather than English-only
  [lex_glue](lex_glue.md). HELM implements 18 configs: Brazilian judgment
  and unanimity, German argument mining, three Greek Legal Code levels,
  Swiss judgment prediction, two online ToS tasks, COVID-19 emergency
  events, three MultiEURLEX EuroVoc levels, and five NER sets (Greek,
  Romanian, Brazilian, MAPA coarse and fine). Inputs are court text,
  legislation, or ToS sentences. HELM is generation over those labels,
  not the paper's encoder fine-tunes.
task_format: >
  HELM run spec lextreme:subset=<config> or subset=all. Dataset
  joelito/lextreme. Generation adapter, input noun Passage, output noun
  Answer. NER outputs a quoted token-label sequence. MultiEURLEX input is
  a dict of languages; HELM picks one language at random per example.
metric:
  name: "classification_macro_f1 (HELM schema); paper uses dataset and language aggregate scores"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml main_name classification_macro_f1, main_split test.
    The paper's headline is two harmonic-mean aggregates (dataset and
    language), both 61.3 for XLM-R large. The GitHub README later table
    lists XLM-R-large dataset aggregate 66.1 and language aggregate 53.7,
    with Legal-XLM-LF-base 66.9 dataset aggregate. Those encoder numbers
    are not HELM generation scores. NER is a different output space.
dataset:
  size: null
  size_note: >
    Do not add the 18 test splits: MultiEURLEX level 1/2/3 share the same
    documents (train 817,239 / val 112,500 / test 115,000 in the project
    README). Other test n from that README include SJP 17,357, GLC 9,516,
    GAM 3,078, MAPA 10,590, BCD-J 405. The 2023 paper selects 11 datasets
    and 24 languages. The Hugging Face card (lastModified 2026-05-20) now
    lists a 12th dataset, Ukrainian court decisions, and language uk;
    HELM's TASK_CODE_MAPPING still has the original 18 configs.
  url: "https://huggingface.co/datasets/joelito/lextreme"
  license: "CC-BY-4.0 on the Hugging Face card; arXiv HTML for 2301.13126v3 is CC BY-NC-SA 4.0"
  languages:
    - bg
    - cs
    - da
    - de
    - el
    - en
    - es
    - et
    - fi
    - fr
    - ga
    - hr
    - hu
    - it
    - lt
    - lv
    - mt
    - nl
    - pl
    - pt
    - ro
    - sk
    - sl
    - sv
    - uk
  modalities:
    - text
  splits: "per config train/validation/test as published or 80/10/10 when the source had none; HELM scores test"
  public_test_set: true
publisher:
  org: "University of Bern / Bern University of Applied Sciences / Stanford (Niklaus) and co-authors; Stanford CRFM (HELM scenario)"
  authors:
    - "Joel Niklaus"
    - "Veton Matoshi"
    - "Pooja Rani"
    - "Andrea Galassi"
    - "Matthias Stürmer"
    - "Ilias Chalkidis"
  url: "https://github.com/JoelNiklaus/LEXTREME"
paper:
  title: "LEXTREME: A Multi-Lingual and Multi-Task Benchmark for the Legal Domain"
  arxiv: "2301.13126"
  url: "https://aclanthology.org/2023.findings-emnlp.200/"
  year: 2023
leaderboard_url: "https://github.com/JoelNiklaus/LEXTREME"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/lextreme_scenario.py"
released: "2023-01"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: "lex_glue"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 61.3
  as_of: "2023-01"
  note: >
    Paper: XLM-R large dataset and language aggregates both 61.3. GitHub
    README later reports higher dataset aggregates (Legal-XLM-LF-base 66.9)
    and a 53.7 language aggregate for XLM-R-large. Either way the suite is
    far from 100. ChatGPT is described as struggling. No HELM generation
    top score was read.
contamination:
  risk: high
  note: >
    Every source dataset was already public. The Hub builder
    joelniklaus/lextreme (card also served as joelito/lextreme) has been
    public since 2022-08-01, with a 2026-05-20 card update. HELM loads
    labels with the text.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "lextreme:subset=<task>"
  opencompass: ""
  bigbench: ""
  other: "Group lextreme. Dataset joelito/lextreme. 18 HELM configs; Ukrainian court decisions are on the Hub card but not in HELM's mapping."
tags:
  - legal
  - multilingual
  - nlu
  - ner
  - helm
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/lextreme_scenario.py"
    title: "HELM lextreme_scenario.py (18 configs, instructions, NER formatting, MultiEURLEX language sample)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py (lextreme:subset=..., generation adapter)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (classification_macro_f1)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/joelito/lextreme/raw/main/README.md"
    title: "Hugging Face LEXTREME card (CC-BY-4.0; 12 datasets / 21 tasks including Ukrainian)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/joelito/lextreme"
    title: "Hugging Face API (id joelniklaus/lextreme; lastModified 2026-05-20; 25 languages including uk)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/JoelNiklaus/LEXTREME/main/README.md"
    title: "JoelNiklaus/LEXTREME README (18-task table, later encoder aggregates)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2301.13126"
    title: "LEXTREME paper HTML (11 datasets, 24 languages, XLM-R large 61.3)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2301.13126v3"
    title: "arXiv HTML v3 (license line CC BY-NC-SA 4.0; 8 Jan 2024)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2023.findings-emnlp.200/"
    title: "EMNLP 2023 Findings anthology page"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2301.13126"
    title: "arXiv abs (v1 2023-01-30; v3 2024-01-08)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

LEXTREME tests legal classification and NER in many European languages.
A model may see a Brazilian appeal, German Urteilsstil sentences, Greek
legislation, Swiss Federal Supreme Court facts, a consumer ToS clause, a
COVID-era statute sentence, an EU act, or a NER sentence from Greek,
Romanian, Brazilian, or EUR-Lex text. Outputs are topic or judgment labels,
unfair-clause tags, or per-token entity tags. The paper’s point is that
English-only legal suites such as [lex_glue](lex_glue.md) miss multilingual
legal systems. HELM does not implement the Ukrainian court-decision configs
that the 2026 Hub card added.

## How it is scored

Niklaus et al. fine-tune multilingual encoders and report a dataset
aggregate and a language aggregate, each a nested harmonic mean. In the
paper, XLM-R large scores 61.3 on both. The project README later prints
different encoder aggregates (for example XLM-R-large 66.1 dataset / 53.7
language, Legal-XLM-LF-base 66.9 dataset). HELM classic instead headlines
`classification_macro_f1` on generation runs `lextreme:subset=...`. Shot
limits are 1–5 and max tokens range from 5 to several hundred for NER.
MultiEURLEX examples keep one randomly chosen language. A HELM number is
not the paper aggregate.

## Dataset and licence

Hugging Face `joelito/lextreme` (API id `joelniklaus/lextreme`) is the
builder HELM loads. The card licence is CC-BY-4.0. The arXiv v3 HTML
licence line is CC BY-NC-SA 4.0. Source datasets keep their own terms; the
paper excluded sets without a redistributable licence. Per-config sizes
are in the GitHub README (for example Swiss judgment test 17,357,
MultiEURLEX test 115,000 documents). Do not sum those tests into one n.
Labels are public.

## Who publishes it

Joel Niklaus, Veton Matoshi, Pooja Rani, Andrea Galassi, Matthias Stürmer,
and Ilias Chalkidis released the suite on arXiv on 30 January 2023 and at
EMNLP 2023 Findings. Code and encoder tables are in JoelNiklaus/LEXTREME.
Stanford CRFM added the HELM classic scenario. HELM entered maintenance
mode on 2026-06-01.

## Lineage

Predecessor: [lex_glue](lex_glue.md) as the English legal multi-task
template. Several LEXTREME sources overlap that world (ToS unfairness,
EUR-Lex labels) but the languages and configs differ. No successor id is
in this repository. [legalbench](legalbench.md) is English LLM reasoning,
not this encoder suite.

## Saturation and contamination

Even the best published encoder aggregates sit in the 60s, so the suite is
still open on that protocol. Generative HELM saturation was not read.
Source corpora are old and public, so contamination risk is high.

## How to run it

Paper reproduction: `python main.py` in JoelNiklaus/LEXTREME (encoder
fine-tunes, optional W&B). HELM: `lextreme:subset=swiss_judgment_prediction`
or another key from `TASK_CODE_MAPPING`. NER formatting uses a quoted
`"token" "token"` delimiter. MultiEURLEX scores will move if the language
sampler seed changes. Do not drop a Ukrainian config into HELM without new
code.

## Reading the numbers

A strong dataset aggregate means the model is decent across these legal
tasks after you fold languages inside each dataset. A strong language
aggregate means it does not only win on Portuguese or English. A HELM
generation F1 on one subset is neither of those headlines. The suite does
not score contract drafting, retrieval, or US bar exams. Prefer the paper
aggregates for encoder claims and named HELM subsets for generative claims,
and say which of the two XLM-R-large tables you used.
