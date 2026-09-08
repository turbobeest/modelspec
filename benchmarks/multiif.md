---
id: multiif
name: "Multi-IF"
aliases:
  - "MultiIF"
  - "facebook/Multi-IF"
page_kind: benchmark
category: instruction-following
subcategory: "multi-turn multilingual verifiable instruction following"
status: active
summary: "IFEval-style verifiable instruction following extended to three-turn conversations in eight languages, 4,501 dialogues."
measures: >
  Multi-IF tests whether a model still obeys mechanically checkable
  instructions when those constraints span three dialogue turns and eight
  languages. Each user turn adds or restates IFEval-style rules (length,
  keywords, format). Scoring uses the same strict and loose program checks
  as [IFEval](ifeval.md), applied per turn. The English prompts were
  translated into seven other languages with an LLM, then audited by
  professional annotators.
task_format: >
  Three-turn chat. The model answers turn 1, then turn 2 given the history,
  then turn 3. Each turn has an instruction-id list and kwargs for the
  IFEval checkers. OpenCompass MultiIFDataset builds a six-message dialogue
  (user/assistant × 3) and scores with MultiIFEvaluator. Official code is
  facebookresearch/Multi-IF on the `facebook/Multi-IF` CSV.
metric:
  name: "mean of prompt-level and instruction-level strict and loose accuracy, per turn and overall"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same four IFEval-style rates (prompt/instruction × strict/loose), now
    reported per turn. The paper's "Average" is the mean of those four rates
    across languages. OpenCompass overall is the mean of three per-turn
    overalls, each the mean of the four rates. No random or human baseline.
    Paper: o1-preview 0.877 turn 1 to 0.707 turn 3, language-averaged.
dataset:
  size: 4501
  size_note: >
    Paper and Hugging Face `facebook/Multi-IF`: 4,501 multilingual
    conversations of three turns, in English plus French, Russian, Hindi,
    Italian, Portuguese, Spanish and Chinese. File multiIF_20241018.csv.
    The dataset card's "Data Splits" heading says test (4,501). The Hub
    viewer and datasets-server size endpoint expose a single split named
    train with 4,501 rows. OpenCompass loads path `opencompass/MultiIF` and
    skips rows whose turn_3_prompt is empty, so the runnable count can be
    lower than 4,501. The public Hugging Face page for opencompass/MultiIF
    returned 404 here.
  url: "https://huggingface.co/datasets/facebook/Multi-IF"
  license: "CC BY-NC 2.0"
  languages:
    - en
    - fr
    - ru
    - hi
    - it
    - pt
    - es
    - zh
  modalities:
    - text
  splits: "Hub split name train (4,501); dataset card labels that split test"
  public_test_set: true
publisher:
  org: "Meta (Facebook AI)"
  authors:
    - "Yun He"
    - "Di Jin"
    - "Chaoqi Wang"
    - "Chloe Bi"
    - "Karishma Mandyam"
    - "Hejia Zhang"
    - "Chen Zhu"
    - "Ning Li"
    - "Tengyu Xu"
    - "Hongjiang Lv"
    - "Shruti Bhosale"
    - "Chenguang Zhu"
    - "Karthik Abinav Sankararaman"
    - "Eryk Helenowski"
    - "Melanie Kambadur"
    - "Aditya Tayade"
    - "Hao Ma"
    - "Han Fang"
    - "Sinong Wang"
  url: "https://github.com/facebookresearch/Multi-IF"
paper:
  title: "Multi-IF: Benchmarking LLMs on Multi-Turn and Multilingual Instructions Following"
  arxiv: "2410.15553"
  url: "https://arxiv.org/abs/2410.15553"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/Multi-IF"
released: "2024-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ifeval
  successors: []
  variants: []
saturation:
  status: open
  top_score: 70.7
  as_of: "2024-11"
  note: >
    Paper: among 14 models, o1-preview's language-averaged accuracy falls
    from 0.877 at turn 1 to 0.707 at turn 3 (arXiv v2, 13 November 2024).
    Turn-3 70.7% is the hardest headline they report, not a saturated
    ceiling. No later leaderboard figure was confirmed here.
contamination:
  risk: medium
  note: >
    Prompts and instruction ids have been public on Hugging Face
    (facebook/Multi-IF) since October 2024. Scoring is mechanical, so
    memorising a fluent reply is less directly rewarded than on a fixed
    QA key, but the prompt set itself is easy to scrape.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MultiIF"
  bigbench: ""
  other: >
    OpenCompass dataset abbr `Multi-IF`, class MultiIFDataset, multi-round
    GenInferencer, MultiIFEvaluator (strict/loose × prompt/instruction ×
    three turns). Official scripts:
    multi_turn_instruct_following_eval_vllm.py and `_api.py` in
    facebookresearch/Multi-IF, reading multiIF_20241018.csv. Code licence
    Apache-2.0; dataset licence CC BY-NC 2.0.
tags:
  - instruction-following
  - multi-turn
  - multilingual
  - verifiable
  - ifeval-style
sources:
  - url: "https://arxiv.org/abs/2410.15553"
    title: "Multi-IF (arXiv:2410.15553)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2410.15553"
    title: "Multi-IF paper HTML (4,501 conversations, 8 languages, o1-preview 0.877→0.707)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/facebook/Multi-IF/raw/main/README.md"
    title: "facebook/Multi-IF card (CC BY-NC 2.0, 4,501 test rows, field list)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/Multi-IF"
    title: "facebook/Multi-IF API metadata (licence, languages, CSV)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=facebook/Multi-IF"
    title: "facebook/Multi-IF datasets-server size (train split, 4,501 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/Multi-IF/main/README.md"
    title: "facebookresearch/Multi-IF README (eval scripts, Apache-2.0 code)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/Multi-IF/main/LICENSE"
    title: "Multi-IF code Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MultiIF/MultiIF_gen.py"
    title: "OpenCompass MultiIF_gen.py (abbr Multi-IF, path opencompass/MultiIF)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/MultiIF/multiif.py"
    title: "MultiIFDataset / MultiIFEvaluator (skip empty turn 3, four rates × 3 turns)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-016 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-016"
---

## What it measures

Multi-IF asks whether a model can follow checkable instructions across a three-turn conversation, and whether that still works after the same prompt is translated. Each turn carries IFEval-style constraints — word counts, keywords, punctuation, format — that a program can grade. Turn two and turn three keep earlier constraints in play while adding new ones. The English set was translated into French, Russian, Hindi, Italian, Portuguese, Spanish and Chinese by an LLM and then checked by professional annotators, for 4,501 three-turn conversations in eight languages.

It extends [IFEval](ifeval.md). It is not [AdvancedIF](advancedif.md), which uses expert rubrics and an LLM judge.

## How it is scored

Each response is run through IFEval's strict and loose checkers. Strict requires the raw text to satisfy every instruction. Loose also tries stripped markdown and dropped first/last lines. Four rates are reported per turn: prompt-level and instruction-level, each strict and loose. The paper averages those four rates across languages. OpenCompass's MultiIFEvaluator repeats that per turn, then averages the three turn overalls into one `overall`. The paper's running example is o1-preview falling from 0.877 at turn 1 to 0.707 at turn 3 on that language-averaged accuracy.

## Dataset and licence

Hugging Face `facebook/Multi-IF` ships `multiIF_20241018.csv` with 4,501 conversations. The card calls that split test; the Hub viewer and datasets-server name it train. Fields include per-turn prompt, instruction-id list, kwargs, and a language tag. The dataset card licence is CC BY-NC 2.0. The evaluation repository is Apache-2.0. OpenCompass is configured with `path='opencompass/MultiIF'`; that Hugging Face id returned 404 here, so the public copy used here is `facebook/Multi-IF`. OpenCompass skips rows with an empty `turn_3_prompt`.

## Who publishes it

Yun He, Di Jin, Chaoqi Wang, Chloe Bi and co-authors at Meta. Posted as arXiv:2410.15553 on 21 October 2024 (v2 13 November 2024). Data: huggingface.co/datasets/facebook/Multi-IF. Code: github.com/facebookresearch/Multi-IF.

## Lineage

Predecessor: [ifeval](ifeval.md), whose instruction types and strict/loose checkers Multi-IF reuses. [AdvancedIF](advancedif.md) and [ifbench](ifbench.md) are other instruction-following lines, not drop-in replacements. OpenCompass `MultiIF` is this benchmark's harness spelling.

## Saturation and contamination

Turn-3 language-averaged 70.7% for o1-preview (November 2024) still separates models; the paper's point is that extra turns and non-Latin scripts raise the error rate. Prompts have been public since October 2024. Scoring is programmatic, which blunts but does not remove scrape risk.

## How to run it

Official: clone facebookresearch/Multi-IF, download `facebook/Multi-IF`, run the vLLM or API eval script on `multiIF_20241018.csv`. OpenCompass: dataset family `MultiIF`, abbr `Multi-IF`, multi-round generation. lm-eval, inspect_evals, HELM and BIG-bench implementations were not found at the paths checked.

A turn-1 number is not a turn-3 number. An English-only slice is not the eight-language average. OpenCompass `overall` averages three turns; the paper's tables split turns.

## Reading the numbers

A high Multi-IF score means the model kept obeying checkable constraints while the conversation moved. It does not measure helpfulness, tone, or rubric-style instructions that a program cannot check. Non-Latin languages (Hindi, Russian, Chinese) were harder in the paper; an English-only figure will look better. Pair it with [IFEval](ifeval.md) for single-turn English and with a judged suite if you care about instructions that are not mechanically verifiable.
