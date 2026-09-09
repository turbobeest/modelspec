---
id: cmo_fib
name: CMO fill-in-the-blank
aliases:
  - cmo_fib
  - Chinese Mathematical Olympiad FIB
  - CMO FIB
page_kind: benchmark
category: math
subcategory: "Chinese Mathematical Olympiad fill-in-the-blank problems (2009–2022)"
status: active
summary: "OpenCompass fill-in-the-blank set of Chinese Mathematical Olympiad problems from 2009–2022, scored with a MATH-style boxed-answer matcher."
measures: >
  cmo_fib is OpenCompass's generation task over fill-in-the-blank problems from
  the Chinese Mathematical Olympiad (CMO), contest years 2009 through 2022.
  The model receives the problem text as origin_prompt / question and must
  produce a final mathematical answer. OpenCompass does not turn the items
  into multiple choice. It is contest math in Chinese, closer to olympiad
  fill-in items than to school word problems such as GSM8K.
task_format: >
  Zero-shot generation. Default configs (cmo_fib_gen_ace24b.py and
  cmo_fib_gen_2783e5.py) append a Chinese chain-of-thought request and ask for
  a \\boxed{} answer. cmo_fib_0shot_notcot_gen_4c6c29.py skips the "step by
  step" line and only asks for a boxed final answer. Dataset abbr cmo_fib;
  path opencompass/cmo_fib. Inferencer max_out_len is 2048 in the ace24b and
  0-shot configs.
metric:
  name: "MATHEvaluator v2 accuracy after math_postprocess_v2"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Open-ended olympiad blanks have no chance rate. The OpenCompass dataset
    README table lists Qwen2.5-Math-72B-Instruct at 46.15%,
    Qwen2.5-Math-7B-Instruct at 42.79%, Qwen2-Math-7B-Instruct at 31.73%,
    Qwen2-Math-1.5B-Instruct at 23.56%, and internlm2-math-7b at 3.37%, plus
    lower figures for general Qwen2.5 chat models. Those rows do not name which
    of the three configs was used.
dataset:
  size: null
  size_note: >
    Item count is not in the OpenCompass configs or the short dataset README.
    The Hub dataset opencompass/cmo_fib returned HTTP 401 (gated or private)
    from both the API and datasets-server, so no split cardinality was read.
    Problems are described as CMO 2009–2022 fill-in-the-blank items.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmo_fib"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "loader reads a JSONL path; no split names in CMOFibDataset"
  public_test_set: true
publisher:
  org: OpenCompass (dataset packaging); problems from the Chinese Mathematical Olympiad
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmo_fib"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmo_fib"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 46.15
  as_of: ""
  note: >
    OpenCompass README: Qwen2.5-Math-72B-Instruct 46.15% on this packaged set.
    That is well below 100% and is a math-specialist instruct model, not a
    dated public leaderboard scrape. The README does not give an as-of month.
contamination:
  risk: high
  note: >
    CMO problems from 2009–2022 are widely mirrored in Chinese contest
    archives and training corpora. Fill-in answers are stored as gold_answer
    in the JSONL the loader reads. No anti-leakage rewrite is described in the
    OpenCompass README.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: cmo_fib
  bigbench: ""
  other: ""
tags:
  - math
  - olympiad
  - chinese
  - opencompass
  - fill-in-the-blank
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmo_fib"
    title: "OpenCompass cmo_fib config directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cmo_fib/README.md"
    title: "OpenCompass cmo_fib README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cmo_fib/cmo_fib_gen.py"
    title: "cmo_fib_gen.py re-export"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cmo_fib/cmo_fib_gen_ace24b.py"
    title: "cmo_fib CoT config ace24b"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cmo_fib/cmo_fib_gen_2783e5.py"
    title: "cmo_fib CoT config 2783e5"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cmo_fib/cmo_fib_0shot_notcot_gen_4c6c29.py"
    title: "cmo_fib 0-shot non-CoT config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/cmo_fib.py"
    title: "OpenCompass CMOFibDataset loader"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

`cmo_fib` asks a model to solve fill-in-the-blank problems from the Chinese Mathematical Olympiad. OpenCompass's short README says the problems cover CMO 2009–2022. The model sees the original prompt as the question and must write a final answer, not pick A–D.

This is contest mathematics in Chinese. It is harder, and differently formatted, than GSM8K-style school word problems. It is not the bilingual multimodal suite [olympiadbench](olympiadbench.md), and it is not AIME.

## How it is scored

OpenCompass uses `MATHEvaluator` version `v2` with `math_postprocess_v2`, the same style of boxed-answer grading used for MATH. Default prompts say, in Chinese, to reason step by step and put the final answer in `\\boxed{}`. A second config asks only for the boxed answer. There is no random baseline.

The README table is the only score sheet opened here. Qwen2.5-Math-72B-Instruct is at 46.15%. Qwen2.5-Math-7B-Instruct is at 42.79%. General Qwen2.5-72B-Instruct is at 20.00% on the same page. The table does not say which hashed config produced those rows.

## Dataset and licence

`CMOFibDataset` reads JSONL, copies `origin_prompt` to `question`, and copies `gold_answer` to `answer`. No n, no split names, and no licence appear in the config folder. Hugging Face `opencompass/cmo_fib` returned 401, so size stays empty. Contest authorship sits with CMO; OpenCompass only packages the eval. OpenCompass code is Apache-2.0; that licence was not verified for this JSONL.

Whether every 2009–2022 fill-in item is present, or only a subset, is not stated in the README.

## Who publishes it

OpenCompass (open-compass/opencompass) hosts the task. No separate academic paper for this packaging was found. CMO itself is the Chinese national olympiad. Authors are left empty rather than guessed from unrelated math papers.

## Lineage

The items are olympiad fill-in blanks, not a new problem campaign. English olympiad pages in this repository include [olympiadbench](olympiadbench.md), [aime](aime.md), and [math](math.md). Those are different contests and different graders. No `cmo` family page exists here. The three OpenCompass configs are prompt variants of one abbr, not three datasets.

## Saturation and contamination

46.15% for a 72B math specialist is still open relative to 100%. General chat models in the same README sit much lower. Past CMO papers are easy to include in pretraining, so a high score can mix memorization with contest skill. OpenCompass does not describe a decontamination filter for this set.

## How to run it

Import `cmo_fib_gen.py` (re-exports `cmo_fib_datasets` from `cmo_fib_gen_ace24b.py`) or pick `cmo_fib_gen_2783e5.py` / `cmo_fib_0shot_notcot_gen_4c6c29.py` explicitly. The Hub path is `opencompass/cmo_fib`. Access may require Hub authentication; this session received 401 without credentials.

Name the config hash when you quote a number. CoT versus no-CoT and `max_out_len` 2048 versus the default are enough to move MATH-style scores.

## Reading the numbers

A 46% MATH-evaluator score means the boxed answer often matched `gold_answer` under OpenCompass's matcher. It does not mean the model can write a full olympiad proof, and it does not transfer to English AIME. Because n is unpublished here, do not convert the percentage into an item count. If a report used the non-CoT config, it is not the default `cmo_fib_gen.py` path. Look at [olympiadbench](olympiadbench.md) or [math](math.md) alongside this id if you need a broader contest picture.
