---
id: needlebench_v2
name: "NeedleBench V2"
aliases:
  - "needlebench_v2"
  - "NeedleBench v2"
page_kind: benchmark
category: long-context
subcategory: "revised bilingual needle retrieval, fictional multi-needle reasoning, power-of-two ATC"
status: active
summary: "OpenCompass revision of NeedleBench: equal-weight retrieval scores, fictional multi-needle facts, and power-of-two Ancestral Trace Challenge depths."
measures: >
  NeedleBench V2 keeps the bilingual long-context layout of NeedleBench and changes the parts that
  leaked knowledge or unbalanced the score. Sparse tasks still plant needles in Paul Graham essays
  or Chinese domain text at a chosen length and depth: single-needle retrieval, multi-needle
  retrieval, and multi-needle reasoning. Multi-needle reasoning no longer uses R4C/MultiHop-style
  needles; it uses fictional kinship facts of the same kind as ATC, so a model cannot answer from
  pretraining. ATC remains information-dense (no filler) but spaces needle counts on powers of two
  (2, 4, …, 512) instead of 1–5. English and Chinese. Text only. Length packs at 4k, 8k, 32k, 128k,
  200k, 256k and 1000k.
task_format: >
  Long generated prompt in; short free-text answer out. Sparse tasks: keyword-aware exact match,
  10 repeats, GPT-4 tokenizer length. ATC: NeedleBenchATCDataset with NeedleBenchATCEvaluator and
  needlebench_atc_postprocess_v2; OpenCompass English 0-shot config uses needle counts
  [2, 4, 8, 16, 32, 64, 128, 256, 512], path opencompass/needlebench, names.json, 10 repeats.
metric:
  name: "equal-weight mean of S-RT, M-RT and M-RS (OpenCompass overall); ATC exact match with weighted average and ENL-50 in the paper"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline. Paper v3 Table 1 (32K overall, information-sparse): Qwen-2.5-72B
    81.76. Table 2 (128K overall): Qwen-2.5-72B 81.02, Gemma-3-27B 80.38. Table 3 ATC weighted
    score: DeepSeek-R1 44.01, ENL-50 256; most small models fail past 2–4 needles.
dataset:
  size: null
  size_note: >
    Still a generator. OpenCompass v2 4k single-needle uses lengths 1000, 2000, 3000, 4000 and depths
    0,10,…,100 (11 depths), 10 repeats, English and Chinese. ATC English 0-shot config builds nine
    needle-count settings times 10 repeats. Hugging Face `opencompass/NeedleBench` (MIT) is the
    needle/haystack source; 6,804 packaged rows are not the eval N.
  url: "https://huggingface.co/datasets/opencompass/NeedleBench"
  license: MIT
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "generated at eval time; ATC needle counts 2^k for k=1..9 in the OpenCompass English 0-shot file"
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
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/needlebench_v2"
paper:
  title: "NeedleBench: Evaluating LLM Retrieval and Reasoning Across Varying Information Densities"
  arxiv: "2407.11963"
  url: "https://arxiv.org/abs/2407.11963"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/needlebench_v2"
released: "2025"
last_updated: "2025-09"
lineage:
  family: ""
  predecessor: needlebench
  successors: []
  variants:
    - needlebench
saturation:
  status: open
  top_score: null
  as_of: "2025-09"
  note: >
    Retrieval heads in paper v3 are near ceiling for recent open models (many 98–100 at 32K/128K).
    Multi-needle reasoning stays below 50 for the best open 32K row (Qwen-2.5-72B 45.93). ATC
    weighted score for DeepSeek-R1 is 44.01 with ENL-50 of 256; GPT-4.1 is 14.13 weighted. No single
    official overall is recorded as top_score.
contamination:
  risk: medium
  note: >
    V2 replaced M-RS needles that may have overlapped training data with fictional ATC-like facts.
    Haystacks and names.json remain public. Medium risk: the generator is public, but items are
    re-sampled.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "needlebench_v2 (length packs needlebench_v2_4k … needlebench_v2_1000k plus atc; ATC abbr NeedleBenchATCDataset-{n}Needle-EN)"
  bigbench: ""
  other: "Not found in lm-evaluation-harness listings opened for this page."
tags:
  - long-context
  - retrieval
  - needle-in-haystack
  - bilingual
  - ancestral-trace
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench_v2/readme.md"
    title: "OpenCompass needlebench_v2 README (scoring, fictional M-RS needles, power-of-two ATC)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench_v2/needlebench_v2_4k/needlebench_v2_4k.py"
    title: "needlebench_v2_4k aggregator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench_v2/needlebench_v2_4k/needlebench_v2_single_4k.py"
    title: "v2 4k single-needle config (11 depths, 10 repeats, en/zh)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/needlebench_v2/atc/atc_0shot_nocot_2_power_en.py"
    title: "ATC English 0-shot config (needle counts 2..512, 10 repeats)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2407.11963"
    title: "NeedleBench paper arXiv:2407.11963 (v3 2025-09-17)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.11963v3"
    title: "NeedleBench v3 HTML (32K/128K/ATC tables, under-thinking analysis)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/NeedleBench"
    title: "Hugging Face opencompass/NeedleBench (MIT)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/needlebench_v2/origin.py"
    title: "OpenCompass v2 NeedleBenchOriginEvaluator (keyword 100 else 0)"
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

NeedleBench V2 is the OpenCompass revision of [needlebench](needlebench.md). The model still faces a long English or Chinese prompt and must return planted facts or a kinship answer. Three sparse tasks remain: find one needle, find several, or reason over several. The reasoning needles are now fictional, in the same style as ATC, because the v1 MultiHop-style facts could be known from pretraining. ATC still has no filler: every sentence is a needed kinship fact. Needle counts go 2, 4, 8, …, 512 rather than 1–5. Length packs run 4k through 1000k tokens.

The v3 paper (same arXiv id, September 2025) is the write-up that matches this protocol, including the “under-thinking” error analysis on ATC. It is not [ruler](ruler.md) and not [longbenchv2](longbenchv2.md).

## How it is scored

OpenCompass v2 overall is a simple average of S-RT, M-RT and M-RS. Sparse scoring in `needlebench_v2/origin.py` is 100 if a core keyword appears, else 0 (no Levenshtein fallback). That replaces v1's 0.4/0.3/0.3 weighted overall and 0.2×Levenshtein miss penalty. ATC is scored separately with `NeedleBenchATCEvaluator` after `needlebench_atc_postprocess_v2`. The paper adds a weighted ATC average (weights proportional to needle count) and ENL-50, the largest needle count with at least 50% exact match. Paper v3 32K overall: Qwen-2.5-72B 81.76. 128K overall: Qwen-2.5-72B 81.02. ATC weighted: DeepSeek-R1 44.01 (ENL-50 256). No human baseline.

## Dataset and licence

Prompts are generated at run time from Hugging Face `opencompass/NeedleBench` (MIT licence on the card). OpenCompass code is Apache-2.0. The 4k single-needle script uses four lengths, eleven depths, ten repeats, English essays and `zh_finance.jsonl`. The English ATC 0-shot file uses `names.json` and nine needle counts times ten repeats. Packaged Hub rows (6,804) are source files, not the eval N. Answers are public because the generator is public.

## Who publishes it

Same authors as NeedleBench: Mo Li, Songyang Zhang, Taolin Zhang, Haodong Duan, Yunxin Liu, Kai Chen (Shanghai AI Laboratory and Tsinghua). OpenCompass hosts the configs. Paper v3 is dated 17 September 2025. No separate v2 paper id. No live leaderboard page was opened.

## Lineage

Predecessor is [needlebench](needlebench.md), which OpenCompass now marks deprecated. V2 keeps the four task names and changes M-RS needles, ATC spacing, prompts and the overall average. Adjacent long-context pages: [ruler](ruler.md), [longbench](longbench.md), [longbenchv2](longbenchv2.md), [infinitebench](infinitebench.md).

## Saturation and contamination

Retrieval is close to saturated for recent open models in the v3 tables. Multi-needle reasoning and ATC still separate models: even DeepSeek-R1 is at 44.01 weighted on ATC, and several reasoning APIs collapse past a few dozen needles. Contamination is medium. V2's fictional M-RS needles reduce one leakage path; haystacks and names remain crawlable.

## How to run it

OpenCompass directory `opencompass/configs/datasets/needlebench_v2/`. Length aggregators such as `needlebench_v2_4k.py` import single, multi-retrieval and 2–5 needle reasoning for English and Chinese. ATC example: `atc/atc_0shot_nocot_2_power_en.py`, abbr `NeedleBenchATCDataset-{n}Needle-EN`. Path `opencompass/needlebench`. Not in lm-eval listings opened here. Name the length pack, language, depth list and whether ATC used CoT before comparing runs.

## Reading the numbers

A v2 overall near 80 usually means retrieval is solved and reasoning is carrying the mean. Read S-RT, M-RT, M-RS and ATC separately. ATC ENL-50 is a depth, not an accuracy. Do not compare a v1 OpenCompass overall to a v2 overall. A strong ATC score means the model kept a kinship chain over many sentences; it does not measure retrieval in noisy documents. Pair with [ruler](ruler.md) or [longbenchv2](longbenchv2.md) if you need non-synthetic long text.
