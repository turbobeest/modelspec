---
id: mastermath2024v1
name: "Mastermath2024v1 (OpenCompass)"
aliases:
  - "Mastermath2024v1"
  - "mastermath2024v1_gen"
page_kind: benchmark
category: math
subcategory: "Chinese kaoyan Mathematics Paper 1 four-option multiple choice"
status: unknown
summary: "OpenCompass four-option Chinese kaoyan math MCQ loader; item count is not published in the configs."
measures: >
  mastermath2024v1, in this id, is OpenCompass's MastermathDatasetv1: Chinese
  four-option multiple-choice items loaded from a local CSV named
  kaoyan_math_1_mcq_Sheet1.csv. The filename points at Mathematics Paper 1 of
  China's postgraduate entrance examination (kaoyan), not the Gaokao papers in
  [gaokaobench](gaokaobench.md) and not the mixed-licence KaoshiDataset in
  [kaoshi](kaoshi.md). The model sees the stem plus options A–D and must emit
  a letter. The skill is exam-style Chinese math choice, not free-response
  contest math.
task_format: >
  Zero-shot generation. OpenCompass ZeroRetriever + GenInferencer. Chinese
  prompt appends 选项 (A)–(D) and asks for the form 正确答案是 (insert answer).
  first_option_postprocess with options ABCD extracts the first A/B/C/D.
  MastermathDatasetv1Evaluator then exact-matches the letter.
metric:
  name: "accuracy (exact match of extracted A/B/C/D)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four labelled options, so uniform chance is 25% if every item is single
    choice. The loader always reads four option columns. No human baseline is
    in the OpenCompass files opened here. Score is 100 * correct / n.
dataset:
  size: null
  size_note: >
    OpenCompass loads ./data/mastermath2024v1/kaoyan_math_1_mcq_Sheet1.csv and
    skips a header row whose second cell is question. No row count, zip
    listing, or paper was opened. The 0.2.2.rc1 OpenCompassData table lists
    math401 but not mastermath. Size is not established.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/mastermath2024v1"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "single CSV loaded as the eval set; no train split in the loader"
  public_test_set: true
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/mastermath2024v1"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/mastermath2024v1"
released: "2024-07"
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
    No score table for this OpenCompass abbr was opened. Do not reuse a
    [kaoshi](kaoshi.md) kaoyan-math cell as Mastermath2024v1.
contamination:
  risk: high
  note: >
    Real kaoyan Mathematics Paper 1 items are widely copied in Chinese prep
    books and web dumps. The CSV path is a local OpenCompass data file, not a
    gated Hub set. No canary or holdout is described in the loader.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "mastermath2024v1"
  bigbench: ""
  other: "config abbr Mastermath2024v1; import mastermath2024v1_gen"
tags:
  - math
  - chinese
  - multiple-choice
  - kaoyan
  - opencompass
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mastermath2024v1/mastermath2024v1_gen_be6318.py"
    title: "OpenCompass mastermath2024v1_gen_be6318.py (CSV name, Chinese prompt, ABCD)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/mastermath2024v1/mastermath2024v1_gen.py"
    title: "OpenCompass mastermath2024v1_gen.py pointer"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/mastermath2024v1.py"
    title: "MastermathDatasetv1 loader and letter-match evaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (harness, not the CSV)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/releases/tag/0.2.2.rc1"
    title: "OpenCompassData 0.2.2.rc1 listing (math401 present; mastermath absent)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/commits/main/opencompass/configs/datasets/mastermath2024v1/mastermath2024v1_gen_be6318.py"
    title: "GitHub history: mastermath2024v1_gen_be6318.py first listed 2024-07-31 (46cc789)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/text_postprocessors.py"
    title: "first_option_postprocess used on ABCD"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-056 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-056"
---

## What it measures

mastermath2024v1 is OpenCompass's packaging of a Chinese four-option math exam CSV. The loader reads question, A, B, C, D, and answer from `kaoyan_math_1_mcq_Sheet1.csv`. The filename is Mathematics Paper 1 of kaoyan, the national postgraduate entrance exam, in a 2024 v1 snapshot. The model must pick A–D. That is exam choice under a Chinese prompt, not a worked solution and not English contest math such as [math](math.md). It is also not [kaoshi](kaoshi.md), which uses a different class and a broader mix of licence and kaoyan papers.

## How it is scored

OpenCompass generates a free-text reply, then `first_option_postprocess` takes the first A/B/C/D it can regex out. MastermathDatasetv1Evaluator exact-matches that letter to the CSV answer and reports accuracy as a percentage. There is no chain-of-thought parse, no numeric tolerance, and no circular option rotation. Four options give a 25% chance rate if every row is single-choice. No human baseline was in the files opened here. A report that only says "kaoyan math" may be [kaoshi](kaoshi.md) instead.

## Dataset and licence

The config path is `./data/mastermath2024v1/` and the file name is `kaoyan_math_1_mcq_Sheet1.csv`. The loader skips a header when column 1 equals `question`. Item count is not in the Python config, the dataset class, or the 0.2.2.rc1 OpenCompassData listing (that listing does include math401). Hugging Face had no `mastermath` dataset hit. The exam questions' copyright is not stated. OpenCompass itself is Apache-2.0; that does not licence the CSV. Treat the local file as public once you have the OpenCompass data drop, but do not invent a SPDX id.

## Who publishes it

OpenCompass / Shanghai AI Laboratory ship the loader. No paper, named exam compiler, or maintained leaderboard for this id was opened. Authors are not listed on the config. The config file is in the OpenCompass tree as of 2024-07-31 (commit 46cc789 on `mastermath2024v1_gen_be6318.py`).

## Lineage

This is not [gaokaobench](gaokaobench.md) (Gaokao 2010–2022) and not [ceval](ceval.md). It is not [mathbench](mathbench.md), even though both live in OpenCompass math configs. [kaoshi](kaoshi.md) also has kaoyan mathematics, but KaoshiDataset and KaoshiEvaluator are a different prompt and scorer. No predecessor or successor page in this repository points at mastermath2024v1.

## Saturation and contamination

No public score table was opened, so saturation is unknown. Kaoyan Paper 1 items circulate in prep dumps, so contamination risk is high if the CSV is real exam text. The loader describes no canary and no hidden test.

## How to run it

Place the CSV at `data/mastermath2024v1/kaoyan_math_1_mcq_Sheet1.csv`. Import `mastermath2024v1_datasets` from `mastermath2024v1_gen` (which re-exports `mastermath2024v1_gen_be6318.py`). The runnable OpenCompass dataset name is `mastermath2024v1`; the abbr inside the config is `Mastermath2024v1`. Zero-shot only. Prompt language is Chinese. Extraction failures become wrong letters, not skipped rows.

## Reading the numbers

A high Mastermath2024v1 accuracy means the model usually emitted the gold A–D after this prompt and regex. It does not mean the model can write a kaoyan proof, handle non-MC formats, or match a [kaoshi](kaoshi.md) math cell. Because n is unpublished here, do not treat a percentage as comparable across forks unless both logs show the same CSV length. Check that the report used `first_option_postprocess` rather than a raw string match on the whole completion.
