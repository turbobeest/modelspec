---
id: cvalues
name: "CValues"
aliases:
  - "CValues-Responsibility"
  - "CVALUES"
page_kind: benchmark
category: safety
subcategory: "Chinese human-values alignment (safety vs responsibility multiple-choice)"
status: active
summary: "Chinese two-choice value-alignment eval whose public OpenCompass slice is 1,712 responsibility items that ask which of two replies is more responsible."
measures: >
  CValues tests whether a Chinese LLM prefers the safer or more responsible of two
  replies to a sensitive prompt. The paper splits the skill into safety (level-1:
  refuse harm) and responsibility (level-2: refuse and still give a constructive
  answer). OpenCompass, which is how this id is wired in this repository, ships
  only the public responsibility multiple-choice slice. The model sees one Chinese
  question and two replies labelled A and B after a rewrite of 回复1/回复2, and must
  name the better reply.
task_format: >
  Two-way multiple choice in Chinese. OpenCompass generates a free-text answer,
  then first_capital_postprocess plus AccEvaluator score the A/B letter.
  Zero-shot (ZeroRetriever). The authors' own script instead parses 回复1/回复2
  and reports accuracy both with and without refusals.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Labels in the released jsonl are balanced 856 回复1 and 856 回复2, so chance is
    50%. The paper's Table 4 (automatic eval) put ChatGPT at 92.8% on
    responsibility (level-2) and 93.0% on safety (level-1) when refusals count as
    errors; starred columns that drop refusals are 92.8% and 93.6%. No human
    accuracy on the multiple-choice form is in the paper. OpenCompass does not
    implement the paper's refusal-excluded Acc* column.
dataset:
  size: 1712
  size_note: >
    1,712 non-empty rows in X-PLUG/CValues dataset/cvalues_responsibility_mc.jsonl
    (paper Table 5 also says 1,712 responsibility multiple-choice prompts).
    Meta: 1,328 easy (ChatGPT-rewritten negatives) and 384 hard (expert-rejected
    negatives); eight domain_en values, largest social_science 350, law 276,
    barrier_free 250. The paper additionally describes 2,600 safety
    multiple-choice prompts and 2,100 human evaluation prompts (1,300 safety +
    800 responsibility); the GitHub README says those safety files stay closed
    as sensitive. Human responsibility prompts are released separately as 0.6k
    rows. CValues-Comparison (145k preference pairs) is a training/comparison
    set, not this eval.
  url: "https://github.com/X-PLUG/CValues/blob/main/dataset/cvalues_responsibility_mc.jsonl"
  license: "Apache-2.0"
  languages:
    - zh
  modalities:
    - text
  splits: "single jsonl loaded as Hugging Face 'train'; OpenCompass sets train_split and test_split both to train"
  public_test_set: true
publisher:
  org: "Alibaba Group (X-PLUG) and Beijing Jiaotong University"
  authors:
    - "Guohai Xu"
    - "Jiayi Liu"
    - "Ming Yan"
    - "Haotian Xu"
    - "Jinghui Si"
    - "Zhuoran Zhou"
    - "Peng Yi"
    - "Xing Gao"
    - "Jitao Sang"
    - "Rong Zhang"
    - "Ji Zhang"
    - "Chao Peng"
    - "Fei Huang"
    - "Jingren Zhou"
  url: "https://github.com/X-PLUG/CValues"
paper:
  title: "CValues: Measuring the Values of Chinese Large Language Models from Safety to Responsibility"
  arxiv: "2307.09705"
  url: "https://arxiv.org/abs/2307.09705"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/X-PLUG/CValues"
released: "2023-07"
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
    Paper Table 4 (PDF) puts ChatGPT at 93.0% Level-1 Acc and 92.8% Level-2 Acc
    on the automatic multiple-choice form (Acc* 93.6 / 92.8). No current public
    leaderboard for this OpenCompass slice was opened for this page.
contamination:
  risk: high
  note: >
    The 1,712 responsibility items have been public on GitHub since 2023, with
    gold 回复1/回复2 labels in the same file. The paper also notes that automatic
    multiple-choice mainly tests whether a model can recognise an irresponsible
    reply, not whether it would produce one.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "CValues-Responsibility"
  bigbench: ""
  other: "Official script code/cvalues_eval.py parses 回复1/回复2; OpenCompass config is opencompass/configs/datasets/cvalues/cvalues_responsibility_gen.py (hash-suffixed copy cvalues_responsibility_gen_543378.py)."
tags:
  - chinese
  - safety
  - responsibility
  - multiple-choice
  - alignment
  - opencompass
sources:
  - url: "https://arxiv.org/abs/2307.09705"
    title: "CValues paper (arXiv:2307.09705)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2307.09705"
    title: "CValues PDF (Table 4 ChatGPT 93.0 / 92.8 Acc, 93.6 / 92.8 Acc*)"
    accessed: "2026-09-08"
  - url: "https://github.com/X-PLUG/CValues"
    title: "X-PLUG/CValues repository (README, Apache-2.0 LICENSE, dataset listing)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/X-PLUG/CValues/main/dataset/cvalues_responsibility_mc.jsonl"
    title: "cvalues_responsibility_mc.jsonl (1,712 items, domains, easy/hard)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/X-PLUG/CValues/main/code/cvalues_eval.py"
    title: "Official CValues evaluator (acc vs acc*)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/cvalues/cvalues_responsibility_gen.py"
    title: "OpenCompass CValues-Responsibility config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/cvalues.py"
    title: "OpenCompass CValuesDataset loader (回复1/回复2 to A/B)"
    accessed: "2026-09-08"
  - url: "https://www.modelscope.cn/datasets/damo/CValues-Comparison"
    title: "ModelScope CValues-Comparison dataset page (paper companion set)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-037 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-037"
---

## What it measures

CValues is a Chinese alignment test. The authors wanted to know not only whether a model refuses a harmful request, but whether it can also give a responsible alternative. Safety (level-1) is the refuse-harm bar. Responsibility (level-2) asks for a reply that is still useful after the refusal. This page documents the public automatic form of that second bar: a two-choice Chinese prompt that pairs a question with one better and one worse reply.

OpenCompass is the harness that registered the `cvalues` id. It does not run the unpublished safety multiple-choice set or the human pairwise protocol.

## How it is scored

OpenCompass appends “请直接给出答案：” to the item prompt, samples a completion, maps the first capital letter, and scores exact A/B accuracy. Chance is 50% on the balanced 1,712-item file. The authors' `cvalues_eval.py` instead parses 回复1/回复2 and reports two figures: `acc` over every item, and `acc*` after dropping refusals and unparseable output. Those two numbers are not interchangeable with the OpenCompass letter score. The paper also ran a separate human evaluation on free-form replies; that protocol is not what OpenCompass reports.

## Dataset and licence

The runnable public set is `cvalues_responsibility_mc.jsonl`: 1,712 rows, Apache-2.0 in the X-PLUG/CValues LICENSE. Each row has a Chinese prompt, a gold 回复1 or 回复2 label, and `meta_info` with domain and difficulty. Easy items (1,328) use a ChatGPT-rewritten negative; hard items (384) use a reply an expert rejected. Eight `domain_en` values appear in the file (social_science 350, law 276, barrier_free 250, environmental_science 238, psychology 238, data_science 194, intimate_relationship 142, lesser_known_major 24). The paper counted 4,312 multiple-choice prompts in total; 2,600 safety items remain unreleased. CValues-Comparison on ModelScope is a 145k preference corpus (116k/29k train/test), not this benchmark.

## Who publishes it

Alibaba's X-PLUG group with Beijing Jiaotong University, corresponding author Ming Yan. The paper appeared on arXiv on 19 July 2023. Code and the public jsonl live at X-PLUG/CValues. OpenCompass maintains the `CValues-Responsibility` dataset config. No independent live leaderboard was opened for this page.

## Lineage

CValues is not a translation of an English safety suite and has no family page here. It is not CValues-Comparison, 100PoisonMpts, or the human-only safety prompt set. Those are sibling artefacts from the same paper. No successor id exists in this repository.

## Saturation and contamination

Table 4 already put 2023 ChatGPT at 93.0% / 92.8% Acc (safety / responsibility) on the automatic form, so the multiple-choice slice may no longer separate current chat models. That is a 2023 table, not a 2026 leaderboard, so saturation is left unknown. Gold labels have been public since 2023, so contamination risk is high. The paper itself says multiple-choice mainly tests recognition of a bad reply, not generation of a good one.

## How to run it

Copy `cvalues_responsibility_mc.jsonl` to OpenCompass `data/cvalues_responsibility_mc.jsonl` (the loader is local-only). Run the `CValues-Responsibility` dataset from `opencompass/configs/datasets/cvalues/`. Compare OpenCompass letter accuracy only to other OpenCompass runs. X-PLUG `cvalues_eval.py` needs a `response` field and a model-specific evaluator name (`chatgpt`, `chatglm`, `moss`, `ziya`, `chinese_alpaca-7b`, `chinese_alpaca-13b`).

## Reading the numbers

A high OpenCompass score means the model picked the labelled responsible reply on these 1,712 Chinese pairs. It does not mean the model would write that reply, pass a human expert review, or stay safe on the unpublished safety set. Check whether a reported figure used A/B letters or 回复1/回复2, and whether refusals were dropped. Read it beside a generation-based Chinese safety eval, not as a general helpfulness score.
