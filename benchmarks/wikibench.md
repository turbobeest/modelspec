---
id: wikibench
name: "WikiBench (OpenCompass)"
aliases:
  - "opencompass/WikiBench"
  - "wikibench-wiki-single_choice_cn"
page_kind: benchmark
category: knowledge
subcategory: "Chinese four-way multiple-choice questions drawn from Wikipedia-style knowledge"
status: unknown
summary: "OpenCompass Chinese four-way Wikipedia-style MCQ set, usually reported under circular evaluation rather than single-pass accuracy."
measures: >
  OpenCompass WikiBench is a Chinese single-choice knowledge quiz. Each item is a question
  with four options A-D. Prompts and few-shot exemplars are encyclopaedic (biology, places,
  sports, Chinese history). The default configs enable circular evaluation: the same item
  is asked under four option rotations and the model must get every rotation right. This
  page is that OpenCompass dataset, not Wikipedia-article-quality "WikiBench" work from
  the HCI literature.
task_format: >
  Four-way MCQ in Chinese. Three config styles exist: generative zero-shot
  (wikibench_gen.py imports wikibench_gen_f96ece.py), generative chain-of-thought
  (wikibench_gen_0978ad.py), and few-shot perplexity (wikibench_few_shot_ppl_c23d79.py).
  Generation post-processes with first_option_postprocess over ABCD. CircularEvaluator
  is on by default (do_circular = True). Dataset class WikiBenchDataset, path
  opencompass/WikiBench, file single_choice_cn.jsonl.
metric:
  name: "circular accuracy (CircularEvaluator); AccEvaluator if circular is turned off"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Circular eval credits an item only if all four permutations (ABCD, BCDA, CDAB, DABC)
    are answered correctly, which is much stricter than one-shot 25% chance. OpenCompass
    often reports both circular and origin accuracy in other datasets; these WikiBench
    configs attach CircularEvaluator or AccEvaluator only. No official random or human
    baseline was published in the files opened for this page.
dataset:
  size: null
  size_note: >
    Item count is not established. The Hugging Face dataset page for opencompass/WikiBench
    returned 404. datasets-server reported the dataset missing or not accessible without
    authentication (private or gated). OpenCompass datasets_info.py leaves hf_id empty,
    maps the path to ./data/WikiBench/, and publishes
    http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/WikiBench.zip
    (md5 6dac1d1a3133fe1effff185cbf71d928). This page did not download that zip to count
    jsonl rows. Configs only load filename single_choice_cn.jsonl.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/wikibench"
  license: "Apache-2.0 on OpenCompass code. Dataset licence is not stated on a public card (Hub page 404; datasets_info hf_id is empty)."
  languages:
    - zh
  modalities:
    - text
  splits: "single evaluation file single_choice_cn.jsonl; no train/test split in the configs"
  public_test_set: true
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/wikibench"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/wikibench"
released: ""
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
  note: "No leaderboard table for this exact WikiBench config was opened. CompassBench v1.1 knowledge uses the WikiBenchDataset loader on four domain jsonl files under data/compassbench_v1.1/knowledge/, which is a different path and reporting surface."
contamination:
  risk: medium
  note: >
    Items are Wikipedia-style facts with public option letters once the jsonl or OSS zip
    is obtained. The zip URL is public even though the Hub listing is not. Age of the dump
    is not dated in the configs. Risk is medium rather than high because this research
    could not confirm how long the full key has been mirrored on the open web.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "wikibench"
  bigbench: ""
  other: >
    Default import is wikibench_gen_f96ece.wikibench_datasets. Abbreviations look like
    wikibench-wiki-single_choice_cncircular when do_circular is true. Also
    wikibench_few_shot_ppl_c23d79 and wikibench_gen_0978ad.
tags:
  - chinese
  - multiple-choice
  - wikipedia
  - circular-eval
  - opencompass
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/wikibench/wikibench_gen.py"
    title: "wikibench_gen.py imports wikibench_gen_f96ece as the default gen config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/wikibench/wikibench_gen_f96ece.py"
    title: "Zero-shot gen config: WikiBenchDataset, CircularEvaluator, first_option_postprocess"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/wikibench/wikibench_gen_0978ad.py"
    title: "Chain-of-thought gen config (same dataset file, circular eval)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/wikibench/wikibench_few_shot_ppl_c23d79.py"
    title: "Few-shot PPL config with Chinese exemplars and CircularEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/wikibench.py"
    title: "WikiBenchDataset loader (circular permutations ABCD/BCDA/CDAB/DABC)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/datasets_info.py"
    title: "datasets_info.py: local path and OSS WikiBench.zip md5"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache-2.0 licence (code, not a dataset grant)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1/knowledge/compassbench_v1_knowledge_gen_bd74e0.py"
    title: "CompassBench v1.1 knowledge: WikiBenchDataset on compassbench_v1.1 domain jsonl"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/WikiBench"
    title: "opencompass/WikiBench Hub page (404 at review)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.14147"
    title: "CHI 2024 Wikibench (Kuo, Halfaker et al.): Wikipedia community data-curation system, not this MCQ set"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

WikiBench, in OpenCompass, is a Chinese four-option knowledge quiz. The model is given a factoid question and must pick A, B, C or D. Few-shot examples in the PPL config ask about Candida albicans as a fungal model, a square in Ghent, a Turkish footballer, and Chinese administrative history, so the intended skill is encyclopaedic recall rather than exam math or code. Circular evaluation is the default: option order is rotated four ways and the item counts only if every rotation is right.

This is not CHI 2024 Wikibench (Kuo, Halfaker et al.), a Wikipedia-community data-curation system, and it is not a multilingual retrieval benchmark that happens to include wiki in the title.

## How it is scored

Default gen configs use `GenInferencer`, strip the first ABCD letter, and attach `CircularEvaluator`. The few-shot config uses `PPLInferencer` over four answer letters instead. Setting `do_circular` to false switches in `AccEvaluator`. Circular accuracy is not comparable to a one-pass 25%-chance MCQ number. No human score was found in the configs.

## Dataset and licence

The loader reads `single_choice_cn.jsonl` from `opencompass/WikiBench` or `./data/WikiBench/`. The Hub dataset page returned 404; datasets-server treated it as missing or gated. OpenCompass also ships an OSS zip with a published md5. This page did not unpack the zip, so `size` is empty. OpenCompass code is Apache-2.0. No dataset licence string was found on a public card.

## Who publishes it

OpenCompass / Shanghai AI Laboratory. There is no dedicated WikiBench paper in the files opened here. Authors are not listed on the config modules.

## Lineage

[CompassBench v1.1](compassbench_20_v1_1.md) knowledge configs use the same `WikiBenchDataset` loader on four Chinese domain jsonl files (`common_knowledge`, `humanity`, `natural_science`, `social_science`) under `data/compassbench_v1.1/knowledge/`, plus an English cloze set. That is a different path from this page's `single_choice_cn.jsonl`. CompassBench v1.3 later rebuilt knowledge and should not be used as a WikiBench score. No predecessor id is recorded.

## Saturation and contamination

Saturation is unknown without a table or an item count. Contamination is plausible once the jsonl is public. The Hub listing is not readable, but the OSS zip URL is public, so the risk stays medium rather than a demonstrated leak.

## How to run it

In an OpenCompass config, import `wikibench_datasets` from `opencompass.configs.datasets.wikibench.wikibench_gen` (the unversioned gen file points at `wikibench_gen_f96ece`). Download the zip from the OSS URL in `datasets_info.py` if the Hub path is missing. State whether circular eval was on. Do not mix PPL few-shot numbers with zero-shot gen numbers.

## Reading the numbers

A high circular score means the model still picks the same fact when A-D are shuffled, which is harder than a lucky one-shot letter. It is still a closed Chinese wiki quiz, not open-domain browsing. If a model card says "WikiBench" without "circular" or "OpenCompass", check which project they mean before comparing.
