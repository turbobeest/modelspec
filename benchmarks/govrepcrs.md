---
id: govrepcrs
name: "GovRepcrs (OpenCompass / GovReport CRS)"
aliases:
  - "GovRepcrs"
  - "govrepcrs_gen"
  - "GovReport CRS"
page_kind: benchmark
category: long-context
subcategory: "OpenCompass BLEU summarization of Congressional Research Service reports"
status: unknown
summary: "OpenCompass English summarization of Congressional Research Service reports from GovReport, scored with BLEU rather than ROUGE."
measures: >
  govrepcrs is OpenCompass's loader for the Congressional Research Service
  (CRS) half of GovReport (Huang, Cao, Parulian, Ji, and Wang, NAACL 2021).
  The model reads a long English CRS report (title plus nested section
  paragraphs) and writes an English summary. It does not load GAO reports,
  which are the other half of GovReport. The skill is long-document
  summarization of US policy reports, not short news summarization.
task_format: >
  Zero-shot generation. Prompt: "Please summarize the following English
  report in English:" then the content. GenInferencer max_out_len 500,
  max_seq_len 8192, batch_size 4. ZeroRetriever. Reader uses test for both
  train_split and test_split. Dataset abbr GovRepcrs. Path ./data/govrep/.
metric:
  name: BLEU
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass eval_cfg uses BleuEvaluator. Predictions and references pass
    through general_cn_postprocess even though the prompt and reports are
    English. The GovReport paper reports ROUGE, not BLEU, and uses much
    longer decoder settings than max_out_len 500. No official BLEU human
    baseline is in the OpenCompass config. Scale (0-1 vs 0-100) was not
    re-read from BleuEvaluator.
dataset:
  size: null
  size_note: >
    GovReport paper: 19,466 reports total (12,228 GAO + 7,238 CRS), split by
    publication date to 17,519 train / 974 validation / 973 test. Hugging Face
    ccdv/govreport-summarization lists 17,517 / 973 / 973 on the combined
    document config (train 17,517 vs paper 17,519; validation 973 vs paper
    974). OpenCompass GovRepcrsDataset reads only
    gov-report/split_ids/crs_{train,valid,test}.ids and JSON under
    gov-report/crs/. Exact CRS-only split sizes were not counted from those
    id files. OpenCompass scores the test split.
  url: "https://github.com/luyang-huang96/LongDocSum"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "paper: train/valid/test by date on each source; OpenCompass loads CRS train, valid, test and evaluates test"
  public_test_set: true
publisher:
  org: "University of Michigan and University of Illinois Urbana-Champaign (GovReport); OpenCompass (harness wrap)"
  authors:
    - "Luyang Huang"
    - "Shuyang Cao"
    - "Nikolaus Parulian"
    - "Heng Ji"
    - "Lu Wang"
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/govrepcrs"
paper:
  title: "Efficient Attentions for Long Document Summarization"
  arxiv: "2104.02112"
  url: "https://arxiv.org/abs/2104.02112"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/govrepcrs"
released: "2021-04"
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
    No OpenCompass leaderboard BLEU cell for GovRepcrs was read. GovReport
    paper ROUGE numbers use a different metric, both GAO and CRS, and longer
    outputs, so they are not a BLEU ceiling.
contamination:
  risk: medium
  note: >
    CRS reports and expert summaries are public US government documents and
    the GovReport release is public. OpenCompass evaluates the published test
    split. How much of that text appears in pretraining was not measured here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "govrepcrs"
  bigbench: ""
  other: "Config entry points govrepcrs_gen.py (re-exports db7930) and govrepcrs_gen_aa5eb3.py; dataset class GovRepcrsDataset; abbr GovRepcrs."
tags:
  - opencompass
  - summarization
  - long-document
  - government
  - bleu
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/govrepcrs/govrepcrs_gen.py"
    title: "OpenCompass govrepcrs_gen.py (imports db7930)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/govrepcrs/govrepcrs_gen_db7930.py"
    title: "govrepcrs_gen_db7930.py (chat prompt, BLEU, max_out_len 500)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/govrepcrs/govrepcrs_gen_aa5eb3.py"
    title: "govrepcrs_gen_aa5eb3.py (plain-string prompt, same BLEU setup)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/govrepcrs.py"
    title: "GovRepcrsDataset (CRS-only JSON loader)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2104.02112"
    title: "Huang et al., Efficient Attentions for Long Document Summarization"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2104.02112"
    title: "GovReport paper full text (19,466 docs; 12,228 GAO / 7,238 CRS; splits)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ccdv/govreport-summarization"
    title: "ccdv/govreport-summarization (combined 17,517 / 973 / 973; no licence field)"
    accessed: "2026-09-08"
  - url: "https://github.com/luyang-huang96/LongDocSum"
    title: "LongDocSum repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-046 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-046"
---

## What it measures

govrepcrs asks a model to summarise a long English CRS report. OpenCompass builds the input from the report title and nested section text. The target is the expert summary shipped with GovReport. CRS notes cover US policy. They are shorter on average than GAO reports in the same collection, but still thousands of words. This id is not the full GovReport mix of GAO plus CRS.

The 2021 paper introduced GovReport to stress long-document attention. Salient facts are spread through the source, not packed in the lead. OpenCompass keeps that domain and cuts the source type to CRS only.

## How it is scored

OpenCompass generates with a 8,192-token context cap and a 500-token output cap, then scores BLEU. Two configs exist: a plain string prompt (`aa5eb3`) and a system/human/bot chat template (`db7930`, the default import). Both use zero shots. Both run `general_cn_postprocess` on English text. The paper's main numbers are ROUGE with longer generations. A GovRepcrs BLEU is not a GovReport ROUGE.

## Dataset and licence

Huang et al. count 19,466 reports: 12,228 GAO and 7,238 CRS. Combined date splits are 17,519 / 974 / 973 in the paper. The Hugging Face `ccdv/govreport-summarization` card table is 17,517 / 973 / 973. OpenCompass never loads GAO JSON. CRS-only row counts from `crs_*.ids` were not enumerated here. Mean GovReport document length in the paper is about 9,400 words; mean summary about 553 words, which already exceeds the 500-token decode cap.

CRS and GAO reports are US government publications. The Hugging Face card has no licence field. The arXiv paper is CC-BY-4.0; that is the article licence, not a dataset SPDX on the card. OpenCompass code is Apache-2.0. Test summaries are public.

## Who publishes it

Luyang Huang, Shuyang Cao, Nikolaus Parulian, Heng Ji, and Lu Wang released GovReport with Hepos at NAACL 2021 (arXiv:2104.02112, 5 April 2021, revised 11 April). Data and code sit at LongDocSum and gov-report-data.github.io. OpenCompass added `GovRepcrsDataset` and the `govrepcrs` configs. There is no OpenCompass-hosted leaderboard page that this research opened.

## Lineage

GovReport sits with other long-document summarization sets such as PubMed and arXiv in the paper's tables. This repository already has [legal_summarization](legal_summarization.md) (HELM legal wrap) and [cnn_dailymail_abisee](cnn_dailymail_abisee.md). Those are different corpora. No `govreport` family page exists here. This id is the OpenCompass CRS wrap, not a new item set.

## Saturation and contamination

BLEU saturation for GovRepcrs is not established. Paper ROUGE gains from reading more than 1k tokens are a different protocol. Reports and summaries have been public since 2021, so overlap with pretraining is plausible. OpenCompass does not refresh the test ids.

## How to run it

Place GovReport under `./data/govrep/` so `gov-report/crs/` and `gov-report/split_ids/crs_*.ids` exist. Import `govrepcrs_datasets` from `govrepcrs_gen.py` (db7930) or `govrepcrs_gen_aa5eb3.py`. Compare BLEU only across the same prompt file. Do not mix with ROUGE from the NAACL paper or with GAO-inclusive runs.

## Reading the numbers

A GovRepcrs BLEU is English CRS summarization under a 500-token cap. It does not measure GAO reports, faithfulness, or full 10k-token reading. The Chinese postprocessor on English output is a harness quirk. If two papers disagree by a few combined-split counts (17,519 vs 17,517 train), that is the published tables, not a new test set. Prefer the paper's ROUGE when the claim is about GovReport as published, and this BLEU when the claim is an OpenCompass run.
