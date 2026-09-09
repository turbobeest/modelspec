---
id: iwslt2017
name: "IWSLT 2017 (OpenCompass English-German)"
aliases:
  - "IWSLT 2017"
  - "IWSLT2017"
  - "iwslt2017-en-de"
page_kind: benchmark
category: translation
subcategory: "OpenCompass TED English-to-German text translation (sacreBLEU, BM25 1-shot)"
status: active
summary: "OpenCompass wrap of IWSLT 2017 TED English-to-German: generate German from English and score with sacreBLEU, using one BM25 in-context example."
measures: >
  OpenCompass iwslt2017 is not the full 2017 IWSLT campaign. The configs
  load Hugging Face `iwslt2017` with name `iwslt2017-en-de` and ask the
  model to translate English TED-style sentences into German. The 2017
  workshop also ran multilingual many-to-many TED translation (including
  zero-shot pairs), a dialogue task, and a lecture ASR+MT task. Those
  other tracks are not what this id runs. Text in, German text out. Speech
  is not used. [promptbench](promptbench.md) later wraps the same en-de
  pair under adversarial instructions; that is a different OpenCompass
  directory.
task_format: >
  Generation with BM25Retriever ice_num=1. Default config
  iwslt2017_gen.py re-exports iwslt2017_gen_d0ebd1: HUMAN prompt
  "Please translate the following English statements to German:\n{en}"
  and BOT target `{de}`. Two other prompt files exist (bare `{en} = {de}`,
  and a SYSTEM-role variant). reader_cfg uses input_columns en,
  output_column de, train_split validation. DatasetReader still scores
  the default test split.
metric:
  name: "BLEU (Hugging Face evaluate sacrebleu via BleuEvaluator)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass BleuEvaluator is HuggingfaceEvaluator(metric='sacrebleu'),
    not the campaign's mteval-v13a.pl BLEU/NIST/TER package. Both
    prediction and reference pass general_cn_postprocess, which runs
    jieba on the original string. That postprocessor is named for
    Chinese; using it on German is a protocol quirk, not the 2017
    official scorer. No OpenCompass leaderboard BLEU for this wrap was
    read. The 2017 paper's multilingual averages (Table 3: 17.10-21.13
    BLEU on the four zero-shot pairs) are not this bilingual OpenCompass
    number.
dataset:
  size: 8079
  size_note: >
    Hugging Face IWSLT/iwslt2017 config iwslt2017-en-de: train 206,112,
    validation 888, test 8,079 (card and API, accessed 2026-09-08).
    OpenCompass uses the 888 validation rows as the BM25 pool and, by
    DatasetReader default, the 8,079-row test split for scoring. The
    2017 overview paper's in-domain tst2017 average is 1,146 sentences
    across 20 multilingual pairs (Table 2). That campaign count and the
    Hugging Face 8,079-row en-de test split do not match; the extra HF
    rows are not explained in the card.
  url: "https://huggingface.co/datasets/IWSLT/iwslt2017"
  license: "CC-BY-NC-ND-4.0"
  languages:
    - en
    - de
  modalities:
    - text
  splits: "Hugging Face train 206,112 / validation 888 / test 8,079; OpenCompass ICE from validation, eval on test"
  public_test_set: true
publisher:
  org: "IWSLT 2017 organizers (FBK, KIT, NAIST, Microsoft); OpenCompass wrap by OpenCompass Authors"
  authors:
    - "Mauro Cettolo"
    - "Marcello Federico"
    - "Luisa Bentivogli"
    - "Jan Niehues"
    - "Sebastian Stüker"
    - "Katsuhito Sudoh"
    - "Koichiro Yoshino"
    - "Christian Federmann"
  url: "https://sites.google.com/site/iwsltevaluation2017/TED-tasks"
paper:
  title: "Overview of the IWSLT 2017 Evaluation Campaign"
  arxiv: ""
  url: "https://aclanthology.org/2017.iwslt-1.1/"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/iwslt2017"
released: "2017"
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
    High-resource TED English-German is an old MT pair. No current
    OpenCompass LLM BLEU for this config was read, so a ceiling is not
    recorded. Do not treat 2017 workshop BLEU tables as this wrap.
contamination:
  risk: high
  note: >
    TED transcripts and translations have been public for years (WIT3 /
    TED open translation, Hugging Face dump). The OpenCompass test split
    is the public HF test split, not a hidden 2017 evaluation server.
    Leakage into web-scale training is expected.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "iwslt2017 (default iwslt2017_gen -> iwslt2017_gen_d0ebd1; also 69ce16 and b4a814 prompt hashes)"
  bigbench: ""
  other: "IWSLT2017Dataset load_dataset(**kwargs) flattening the translation field. Not confirmed in lm-eval from files opened for this page."
tags:
  - translation
  - ted
  - german
  - opencompass
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/iwslt2017/iwslt2017_gen.py"
    title: "OpenCompass iwslt2017_gen.py (re-exports d0ebd1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/iwslt2017/iwslt2017_gen_d0ebd1.py"
    title: "Default en-de config (BM25 1-shot, BleuEvaluator, general_cn_postprocess)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/iwslt2017/iwslt2017_gen_69ce16.py"
    title: "Alternate `{en} = {de}` prompt config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/iwslt2017/iwslt2017_gen_b4a814.py"
    title: "Alternate SYSTEM-role prompt config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/iwslt2017.py"
    title: "IWSLT2017Dataset (load_dataset, flatten translation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_hf_evaluator.py"
    title: "BleuEvaluator uses evaluate metric sacrebleu"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/text_postprocessors.py"
    title: "general_cn_postprocess (jieba on original text)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/IWSLT/iwslt2017/resolve/main/README.md"
    title: "Hugging Face IWSLT 2017 card (CC-BY-NC-ND, split table, citation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/IWSLT/iwslt2017"
    title: "Hugging Face dataset API (iwslt2017-en-de 206112/888/8079)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2017.iwslt-1.1/"
    title: "Cettolo et al. 2017 IWSLT overview (ACL Anthology)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2017.iwslt-1.1.pdf"
    title: "Cettolo et al. 2017 PDF (TED multilingual task, tst2017 ~1146)"
    accessed: "2026-09-08"
  - url: "https://sites.google.com/site/iwsltevaluation2017/TED-tasks"
    title: "IWSLT 2017 Multilingual Task site (official vs unofficial pairs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (harness, not the TED data)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-051 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-051"
---

## What it measures

OpenCompass `iwslt2017` translates English TED-style sentences into German. The model sees one English line and must write German. Retrieval adds one similar validation sentence via BM25. The underlying corpus is the IWSLT 2017 TED text dump on Hugging Face, config `iwslt2017-en-de`.

The 2017 workshop was broader. Cettolo et al. describe a multilingual many-to-many TED task over English, German, Dutch, Italian, and Romanian, plus unofficial bilingual pairs with Arabic, French, Japanese, Chinese, German, and Korean, a dialogue task, and a lecture task. This id does not run those tracks. It is text MT, not speech. [promptbench](promptbench.md) attacks the instruction on the same en-de pair; that is a robustness wrap, not this config.

## How it is scored

OpenCompass `BleuEvaluator` loads Hugging Face `evaluate`'s `sacrebleu` metric. That is not the 2017 official mix of mteval-v13a.pl BLEU, NIST, and TER on detokenized NIST XML. Both the prediction and the German reference are passed through `general_cn_postprocess`, which tokenises with jieba. That is a Chinese-oriented helper applied to German. Prompt hash matters: `d0ebd1` (default) is not `{en} = {de}` (`69ce16`) and not the SYSTEM-role file (`b4a814`). All three use BM25 with one in-context example from the validation split.

## Dataset and licence

Hugging Face reports 206,112 train, 888 validation, and 8,079 test sentence pairs for `iwslt2017-en-de`. OpenCompass sets `train_split='validation'`, so the 888-row split is the BM25 pool. `DatasetReader` defaults `test_split` to `test`, so scoring is the 8,079-row test split unless a caller overrides it. The 2017 paper's Table 2 gives an average tst2017 size of 1,146 sentences for the 20 multilingual pairs. That campaign figure and the HF 8,079-row en-de test set disagree; this page records both. The HF card states Creative Commons BY-NC-ND and points at the TED Talks usage policy. OpenCompass itself is Apache-2.0. References are public.

## Who publishes it

IWSLT 2017 was organised by Cettolo, Federico, Bentivogli (FBK), Niehues and Stüker (KIT), Sudoh and Yoshino (NAIST), and Federmann (Microsoft). The overview paper is ACL Anthology 2017.iwslt-1.1 (Tokyo, 14-15 December 2017). In-domain TED data were distributed via WIT3. OpenCompass Authors maintain the LLM wrap under `configs/datasets/iwslt2017`. Hugging Face dataset `IWSLT/iwslt2017` is the copy the loader expects.

## Lineage

TED translation has been an IWSLT track since 2010; 2017 added multilingual and zero-shot conditions. This repository's [flores](flores.md) family is a later many-language eval, not a successor of this wrap. [promptbench](promptbench.md) reuses IWSLT 2017 en-de with AttackInferencer. There is no `iwslt2016` page here. Do not treat an OpenCompass `iwslt2017` BLEU as a 2017 workshop submission.

## Saturation and contamination

English-German TED is a high-resource pair and is old enough that modern LLMs may sit high on sacreBLEU. No current OpenCompass number was read, so saturation is left unknown. TED text has been public for years, so contamination risk is high. The HF test split is not a hidden evaluation-server set.

## How to run it

In OpenCompass, import `iwslt2017_datasets` from `configs/datasets/iwslt2017/iwslt2017_gen.py` (d0ebd1) or name a hashed prompt file. The dataset class is `IWSLT2017Dataset`. It calls `load_dataset` with `path='iwslt2017'` and `name='iwslt2017-en-de'`, then flattens the `translation` dict. Quote the prompt hash, sacreBLEU, jieba postprocess, and the 8,079-row test split. A campaign mteval BLEU on tst2017 is a different number. lm-eval task names were not confirmed from files opened for this page.

## Reading the numbers

A strong OpenCompass BLEU here means fluent English-to-German on this TED-like test split under BM25 1-shot. It does not measure speech translation, zero-shot multilingual TED, or robustness to attacked instructions. jieba on German can move BLEU relative to a plain sacreBLEU script. The 8,079-row HF test set is much larger than the 2017 tst2017 average, so a paper table and an OpenCompass run are not interchangeable. Pair this id with [flores](flores.md) if you need many languages, and with [promptbench](promptbench.md) if you care about prompt attacks on the same pair.
