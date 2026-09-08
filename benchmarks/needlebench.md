---
id: needlebench
name: "NeedleBench"
aliases:
  - "NeedleBench v1"
  - "needlebench"
page_kind: benchmark
category: long-context
subcategory: "bilingual synthetic needle retrieval, multi-needle reasoning, and ancestral trace"
status: superseded
summary: "OpenCompass long-context suite that plants synthetic needles in English and Chinese haystacks at chosen lengths and depths, plus an Ancestral Trace Challenge."
measures: >
  NeedleBench builds a long prompt and asks a model to recover or reason over planted facts
  ("needles"). Information-sparse tasks put one or more synthetic facts into a haystack of Paul
  Graham essays (English) or ChineseDomainModelingEval passages (Chinese), at a chosen token length
  and depth. Single-needle retrieval (S-RT) asks for one fact. Multi-needle retrieval (M-RT) asks
  for several. Multi-needle reasoning (M-RS) asks the model to combine two to five facts. The
  Ancestral Trace Challenge (ATC) is information-dense: every sentence is a kinship fact and there
  is no filler. English and Chinese. Text only. OpenCompass v1 length packs are 4k, 8k, 32k, 128k,
  200k and 1000k (the 256k pack is in needlebench_v2, not this tree).
task_format: >
  Long generated prompt in; short free-text answer out. OpenCompass v1 sparse scoring
  (NeedleBenchOriginEvaluator) is 100 if a core keyword appears, else 0.2 times Levenshtein
  similarity to the reference. ATC in the later paper uses boxed exact match; v1 configs do not.
  OpenCompass v1 uses NeedleBenchOriginDataset, a GPT-4 tokenizer length target, and a length buffer.
metric:
  name: "OpenCompass v1: keyword hit 100 else 0.2 x Levenshtein similarity; v1 paper overall weights 0.4/0.3/0.3 on S-RT/M-RT/M-RS"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline is defined. The v3 paper reports per-model tables at 32K and 128K
    for open models, and a separate ATC table. Those ATC numbers use the later power-of-two needle
    counts, which OpenCompass documents as a v2 change, so they are not treated as v1 tops here.
dataset:
  size: null
  size_note: >
    Synthetic generator, not a fixed item list. Hugging Face `opencompass/NeedleBench` packages
    needles and haystacks (configs retrieval_needles, multi_needle_reasoning_needle, atc_needles,
    en_haystack_texts, zh_haystack_texts; datasets-server reports 6,804 packaged rows). Eval item
    count depends on length, depth grid and repeats (OpenCompass 4k single-needle uses lengths
    1000–4000 step 1000, 20 linear depths, 10 repeats, English and Chinese).
  url: "https://huggingface.co/datasets/opencompass/NeedleBench"
  license: MIT
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "generated at eval time from packaged needles and haystacks; Hugging Face configs are test-only source files"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory and Tsinghua University"
  authors:
    - "Mo Li"
    - "Songyang Zhang"
    - "Taolin Zhang"
    - "Haodong Duan"
    - "Yunxin Liu"
    - "Kai Chen"
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/needlebench"
paper:
  title: "NeedleBench: Evaluating LLM Retrieval and Reasoning Across Varying Information Densities"
  arxiv: "2407.11963"
  url: "https://arxiv.org/abs/2407.11963"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/needlebench"
released: "2024-07"
last_updated: "2025-09"
lineage:
  family: ""
  predecessor: ""
  successors:
    - needlebench_v2
  variants:
    - needlebench_v2
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    OpenCompass marks this config tree deprecated in favour of needlebench_v2. The v3 paper's 32K
    table (Qwen-2.5-72B overall 81.76) is a later protocol and is not recorded as a v1 top score.
    Retrieval tasks in that paper are near ceiling for recent open models; multi-needle reasoning is
    not.
contamination:
  risk: medium
  note: >
    Retrieval needles are synthetic. v1 multi-needle reasoning needles come from R4C/HotpotQA
    Wikipedia derivations; the v1 paper warns models may answer from pretraining. Haystacks are
    public essays and Chinese domain text. The generator is public, so needle strings can be memorised.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "needlebench (length packs needlebench_4k … needlebench_1000k plus atc; e.g. abbr Length{n}Depth{d}_origin_en_4k)"
  bigbench: ""
  other: "OpenCompass README in this directory states the suite is deprecated and points to needlebench_v2."
tags:
  - long-context
  - retrieval
  - needle-in-haystack
  - bilingual
  - superseded
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench/readme.md"
    title: "OpenCompass needlebench README (deprecated; tasks S-RT, M-RT, M-RS, ATC; points to v2)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench/needlebench_4k/needlebench_4k.py"
    title: "OpenCompass needlebench_4k aggregator (single, multi-retrieval, 2–5 needle reasoning, en/zh)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench/needlebench_4k/needlebench_single_4k.py"
    title: "v1 4k single-needle config (GPT-4 tokenizer, 10 repeats, PaulGrahamEssays / zh_finance)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2407.11963"
    title: "NeedleBench paper (arXiv:2407.11963; v1 2024-07-16, v3 2025-09-17)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.11963v3"
    title: "NeedleBench v3 HTML (tasks, metrics, 32K/128K tables, ATC)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/NeedleBench"
    title: "Hugging Face opencompass/NeedleBench (MIT; 6,804 rows packaged)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/NeedleBench/raw/main/README.md"
    title: "NeedleBench dataset card (MIT; task list; citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/needlebench/origin.py"
    title: "OpenCompass v1 NeedleBenchOriginEvaluator (keyword 100 else 0.2 x Levenshtein)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2407.11963v1"
    title: "NeedleBench v1 HTML (R4C/HotpotQA M-RS needles; ATC 2–19 steps; weighted overall 0.4/0.3/0.3)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=opencompass/NeedleBench"
    title: "datasets-server size for opencompass/NeedleBench (6,804 packaged rows)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-007"
---

## What it measures

NeedleBench tests whether a model can find planted facts in a long English or Chinese prompt and, in harder settings, combine them. Sparse tasks hide one or more statements in a haystack of essays or domain articles, at a chosen depth. The model must return the fact (S-RT, M-RT) or answer a question that needs several facts (M-RS). v1 M-RS needles come from R4C/HotpotQA Wikipedia text, not the fictional kinship facts used later. ATC drops the haystack: the prompt is a chain of kinship sentences, and every sentence matters. OpenCompass v1 packs 4k, 8k, 32k, 128k, 200k and 1000k. The suite is bilingual by construction, not a translation of an English-only needle test.

It is not [ruler](ruler.md) (Nvidia's 13-task synthetic generator) and not [longbench](longbench.md) (real-document tasks at shorter lengths). Greg Kamradt's Needle-in-a-Haystack test is the retrieval ancestor; there is no page for that test here.

## How it is scored

OpenCompass v1 sparse scoring (`NeedleBenchOriginEvaluator`) is 100 if a core keyword appears, else 0.2 times Levenshtein similarity to the reference. That matches the v1 paper's α=0.2 rule and is not the later binary 100/0 used in [needlebench_v2](needlebench_v2.md). The v1 paper's overall is a weighted mean of S-RT 0.4, M-RT 0.3 and M-RS 0.3, averaged over lengths, depths and 10 repeats. ATC in the v3 paper uses exact match on a boxed name, plus a weighted average over needle counts and an ENL-50 depth. OpenCompass v1 configs do not implement that boxed metric; the v1 paper's ATC used 2–19 reasoning steps and circular multiple-choice scoring. No human baseline is published. Do not mix a v1 overall with a v2 overall.

## Dataset and licence

There is no fixed test cardinality. Prompts are built at run time from Hugging Face `opencompass/NeedleBench` (MIT): `needles.jsonl`, bilingual multi-needle JSON, `names.json`, Paul Graham essays, and Chinese domain jsonl files. Hugging Face datasets-server reports 6,804 packaged rows; that is source files, not an eval N. OpenCompass code is Apache-2.0. arXiv v3 of the paper is CC BY 4.0. Needles are public, so answers are public.

## Who publishes it

Mo Li, Songyang Zhang, Taolin Zhang, Haodong Duan, Yunxin Liu and Kai Chen (Tsinghua University and Shanghai AI Laboratory). arXiv:2407.11963, first version 16 July 2024; v3 17 September 2025. Code lives in OpenCompass. No separate live leaderboard HTML was opened for this page.

## Lineage

NeedleBench extends passkey and NIAH tests with bilingual haystacks, multi-needle reasoning and ATC. OpenCompass directory `needlebench` is this version. [needlebench_v2](needlebench_v2.md) replaces it in the same repo: fictional M-RS needles, power-of-two ATC counts, equal-weight overall. Related pages: [ruler](ruler.md), [longbench](longbench.md), [longbenchv2](longbenchv2.md), [infinitebench](infinitebench.md).

## Saturation and contamination

OpenCompass calls v1 deprecated. The v3 paper shows near-perfect single- and multi-retrieval for recent 7B-plus models at 32K and 128K, and much lower multi-needle reasoning (Qwen-2.5-72B 45.93 at 32K in that table). Those figures are not copied into `top_score` because the paper's later text matches the v2 protocol. Contamination risk is medium: retrieval needles are synthetic, but v1 M-RS needles are Wikipedia-derived (R4C), and the generator and haystacks are public.

## How to run it

OpenCompass: `opencompass/configs/datasets/needlebench/` with length subdirs `needlebench_4k`, `needlebench_8k`, `needlebench_32k`, `needlebench_128k`, `needlebench_200k`, `needlebench_1000k` and `atc`. Example abbr `Length1000Depth0_origin_en_4k`. Path `opencompass/needlebench`. Tokenizer `gpt-4`, 10 repeats, English buffer 600 / Chinese 200 on the 4k single-needle script. The same README tells users to switch to `needlebench_v2`. Not found in lm-evaluation-harness `super_glue` or `bigbench/generate_until` listings opened here.

## Reading the numbers

A high S-RT score means the model can copy one planted sentence from a long prompt at that length and depth. It does not mean the model can integrate many facts or ignore filler. M-RS and ATC are the harder heads. Name the length pack, language, depth grid and whether the run is v1 or v2 before comparing two NeedleBench numbers. For current OpenCompass numbers, use [needlebench_v2](needlebench_v2.md).
