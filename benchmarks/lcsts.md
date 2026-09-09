---
id: lcsts
name: "LCSTS (Large-scale Chinese Short Text Summarization)"
aliases:
  - "Large-scale Chinese Short Text Summarization"
page_kind: benchmark
category: generation
subcategory: "Chinese Weibo short-text summarization (OpenCompass generation split)"
status: active
summary: "Chinese short-text summarization from Sina Weibo author summaries; OpenCompass scores the 725-pair test split with jieba-tokenized ROUGE."
measures: >
  LCSTS asks a model to write a short Chinese summary of a Sina Weibo post.
  Gold summaries were written by the post author, not by a third-party
  abstractor. OpenCompass feeds the post text and scores the generated line
  against that author summary. Character-level Chinese, generation, not
  multiple choice.
task_format: >
  OpenCompass LCSTSDataset, abbreviation lcsts, path opencompass/LCSTS.
  Zero-shot GenInferencer. Default config lcsts_gen.py includes
  lcsts_gen_8ee1fe (chat-style HUMAN prompt). Alternate lcsts_gen_9b0b89
  uses a single string template. Evaluator JiebaRougeEvaluator.
metric:
  name: "jieba-tokenized ROUGE-1/2/L F-measure (OpenCompass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    JiebaRougeEvaluator tokenizes prediction and reference with jieba, then
    rouge_chinese F scores × 100 as rouge1, rouge2, rougeL. The 2015 paper
    reports ROUGE on a numeric-ID adaptation of the English ROUGE package
    for RNN baselines, not this jieba setup. No official human ROUGE.
dataset:
  size: 725
  size_note: >
    OpenCompass scores the test split only (test.src.txt / test.tgt.txt, or
    ModelScope split test). The 2015 paper's test set is Part III pairs with
    human relevance 3, 4, or 5: 227 + 301 + 197 = 725. ModelScope card for
    opencompass/LCSTS states train 2,400,591, validation 8,685, test 725.
    Validation 8,685 matches Part II scores 3–5 (2,019 + 3,128 + 3,538).
    Full Part I is 2,400,591 pairs. Hugging Face opencompass/LCSTS returned
    HTTP 401 (gated) in this session.
  url: "https://www.modelscope.cn/datasets/opencompass/LCSTS"
  license: "Apache-2.0 on the ModelScope opencompass/LCSTS card; original 2015 release terms not restated there"
  languages:
    - zh
  modalities:
    - text
  splits: "OpenCompass loads test only; paper/ModelScope also publish train 2,400,591 and validation 8,685"
  public_test_set: true
publisher:
  org: "Harbin Institute of Technology (dataset); OpenCompass (harness config)"
  authors:
    - "Baotian Hu"
    - "Qingcai Chen"
    - "Fangze Zhu"
  url: "https://www.modelscope.cn/datasets/opencompass/LCSTS"
paper:
  title: "LCSTS: A Large Scale Chinese Short Text Summarization Dataset"
  arxiv: "1506.05865"
  url: "https://aclanthology.org/D15-1229/"
  year: 2015
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/lcsts"
released: "2015-09"
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
    ArXiv v4 Table 2 reports RNN-with-context character ROUGE-1/2/L 0.299 /
    0.174 / 0.272 on the paper's numeric-ID protocol. EMNLP 2015 printed lower
    scores that the authors later corrected. No dated OpenCompass jieba cell
    was read here. Weibo author summaries are short and often extractive-looking,
    so modern models may sit high on ROUGE without that proving long-document
    summarization skill.
contamination:
  risk: high
  note: >
    The corpus has been described in an EMNLP 2015 paper and redistributed in
    public LLM eval packs. Author summaries are in the downloadable test
    files. Weibo text from 2015 is likely in web crawls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "lcsts"
  bigbench: ""
  other: "Configs lcsts_gen.py (includes lcsts_gen_8ee1fe) and lcsts_gen_9b0b89.py; dataset class LCSTSDataset."
tags:
  - chinese
  - summarization
  - weibo
  - rouge
  - opencompass
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/lcsts/lcsts_gen.py"
    title: "lcsts_gen.py (default include of lcsts_gen_8ee1fe)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/lcsts/lcsts_gen_8ee1fe.py"
    title: "lcsts_gen_8ee1fe.py (chat prompt, JiebaRougeEvaluator, abbr lcsts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/lcsts/lcsts_gen_9b0b89.py"
    title: "lcsts_gen_9b0b89.py (string prompt variant)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/lcsts.py"
    title: "LCSTSDataset loader (test.src.txt/test.tgt.txt or ModelScope test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_jieba_rouge_evaluator.py"
    title: "JiebaRougeEvaluator (jieba + rouge_chinese F × 100)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/utils/datasets_info.py"
    title: "datasets_info.py mapping opencompass/LCSTS to HF, ModelScope, ./data/LCSTS"
    accessed: "2026-09-08"
  - url: "https://www.modelscope.cn/api/v1/datasets/opencompass/LCSTS"
    title: "ModelScope API (Apache License 2.0; train 2,400,591 / val 8,685 / test 725)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1506.05865"
    title: "LCSTS paper HTML (Part I–III counts; test = Part III scores 3–5)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/D15-1229/"
    title: "EMNLP 2015 anthology page (September 2015, Lisbon)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (harness code)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

LCSTS is a Chinese summarization test built from Sina Weibo. The model reads a
short post and must write a short summary. In the original collection, that
summary is the author’s own highlight line on the post, not a later abstract.
OpenCompass uses only the held-out test pairs. The skill is Chinese short-text
compression, not long-document legal or news summarization.

## How it is scored

OpenCompass runs zero-shot generation. `JiebaRougeEvaluator` segments both
strings with jieba, then reports ROUGE-1/2/L F-measure times 100. A
postprocessor keeps the first line and strips a few list prefixes and quotes.
The default config (`lcsts_gen.py` → `lcsts_gen_8ee1fe`) uses a HUMAN/BOT chat
template. `lcsts_gen_9b0b89` uses a single-string prompt. Those two runs are
not the 2015 paper’s RNN ROUGE, which mapped Chinese to numeric IDs for the
English ROUGE package.

## Dataset and licence

Hu, Chen, and Zhu (EMNLP 2015) released three parts: 2,400,591 training pairs
(Part I), 10,666 Part II pairs with a 1–5 relevance score, and 1,106 Part III
pairs labeled by three annotators. They tested on Part III scores 3–5 (725
pairs). OpenCompass `LCSTSDataset` reads `test.src.txt` and `test.tgt.txt`,
or ModelScope `opencompass/LCSTS` split `test`. The ModelScope card states
Apache License 2.0 and the 725-pair test. Hugging Face `opencompass/LCSTS`
was gated (HTTP 401) here. The 2015 paper does not print an SPDX licence.
Gold summaries are in the test files.

## Who publishes it

The dataset comes from Harbin Institute of Technology (Baotian Hu, Qingcai
Chen, Fangze Zhu). EMNLP 2015 is the paper. OpenCompass maintains the
generation config used as this id. There is no single live LCSTS LLM
leaderboard opened here.

## Lineage

LCSTS is an early Chinese summarization corpus. It is not
[legal_summarization](legal_summarization.md) and not a news-highlight
benchmark such as CNN/DailyMail. No successor id is recorded in this
repository.

## Saturation and contamination

The 2015 neural baselines are not a current ceiling. Whether OpenCompass
ROUGE still separates new models was not read from a dated board. The test
summaries have been public in eval redistributions for years, so
contamination risk is high.

## How to run it

In OpenCompass, use dataset abbr `lcsts` from
`opencompass/configs/datasets/lcsts`. Point `DATASET_SOURCE` at Hugging Face
or ModelScope, or place `test.src.txt` and `test.tgt.txt` under `./data/LCSTS`.
Say which prompt hash you used (`8ee1fe` vs `9b0b89`). Do not cite 2015
ROUGE decimals next to jieba F×100 without a conversion note.

## Reading the numbers

A high jieba ROUGE on 725 Weibo tests means the model matched author
highlights on short social posts. It does not measure long-form Chinese
summarization or faithfulness beyond n-gram overlap. Author lines can be
promotional. Look at ROUGE-2 and ROUGE-L together, and at a news or
document summarization set if that is the use case.
