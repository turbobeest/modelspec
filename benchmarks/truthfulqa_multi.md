---
id: truthfulqa_multi
name: "TruthfulQA-Multi"
aliases:
  - "truthfulqa-multi"
  - "Multilingual TruthfulQA"
  - "Truth Knows No Language"
page_kind: benchmark
category: safety
subcategory: "multilingual truthfulness / imitative falsehood (Basque, Catalan, Galician, Spanish, English)"
status: active
summary: "Professionally translated TruthfulQA in Basque, Catalan, Galician and Spanish, plus English, scored with MC2 and generation metrics."
measures: >
  TruthfulQA-Multi keeps the original 817 trap questions and answers, then adds professional
  translations into Spanish, Catalan, Galician and Basque so the same misconceptions can be
  asked outside English. The questions still sit in a US/English cultural frame; translators
  were told not to localise them. The skill is whether a model repeats a popular falsehood
  in that language, not whether it knows obscure facts. The paper splits items into 288
  universal-knowledge questions and 529 time- or context-dependent ones.
task_format: >
  Per language, lm-eval ships MC1 (single best option), MC2 (probability mass on all true
  options), and free-form generation. Prompts are "Q: {question}\\nA:". Generation stops at
  "Q:", ".\\n\\n" or "!\\n\\n". The paper's preferred generation score is an LLM judge, not
  the harness BLEU metrics.
metric:
  name: "MC2 accuracy (lm-eval); paper also reports LLM-as-a-Judge truthfulness"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    MC2 is the normalised probability mass on true MC2 options, as in original TruthfulQA.
    lm-eval generation reports bleu_max, bleu_acc and bleu_diff only; BLEURT and ROUGE
    lines are commented out. The paper instead trains multilingual judges (best reported:
    Gemma 2 9B instruct on machine-translated labels) and correlates them with a 400-answer
    human labelling of truthfulness and informativeness. Original TruthfulQA (Lin et al.,
    arXiv 2109.07958 abstract) reports 94% human truthfulness; that baseline was not
    re-measured here. No random baseline is defined.
dataset:
  size: 817
  size_note: >
    817 validation questions per language config (en, es, ca, gl, eu), parallel to original
    TruthfulQA, plus a 6-example train split used as few-shot. Hugging Face datasets-server
    counted 817/6 for every config on 2026-09-08. Running all five languages scores 4,085
    validation items. 38 misconception categories; 288 universal vs 529 time/context items.
  url: "https://huggingface.co/datasets/HiTZ/truthfulqa-multi"
  license: "Apache-2.0"
  languages:
    - en
    - es
    - ca
    - gl
    - eu
  modalities:
    - text
  splits: "validation (817 scored items) and train (6 few-shot items) per language; no test split"
  public_test_set: true
publisher:
  org: "HiTZ Center - Ixa, University of the Basque Country (UPV/EHU), with Elhuyar, CiTIUS (Universidade de Santiago de Compostela), and Universitat Pompeu Fabra"
  authors:
    - "Blanca Calvo Figueras"
    - "Eneko Sagarzazu"
    - "Julen Etxaniz"
    - "Jeremy Barnes"
    - "Pablo Gamallo"
    - "Iria De Dios Flores"
    - "Rodrigo Agerri"
  url: "https://github.com/hitz-zentroa/truthfulqa-multi"
paper:
  title: "Truth Knows No Language: Evaluating Truthfulness Beyond English"
  arxiv: "2502.09387"
  url: "https://arxiv.org/abs/2502.09387"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/hitz-zentroa/truthfulqa-multi"
released: "2025-02"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: truthfulqa
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper Table 4 (professionally translated set; 12 Llama 3/3.1 and Gemma 2 models,
    7B-70B, base and instruct) was recovered from the ar5iv HTML. Best Judge-LLM cell
    is gemma-2-27b-it at 84.0 English / 79.0 five-language average. Best MC2 average
    in that table is 61.3 for the same model. That is the 2025 paper's table, not a
    live leaderboard. Instruct models beat base twins; Gemma instruct beat Llama
    instruct on the judge. Base-model English scores can look worse because
    "I have no comment" is treated as truthful and is rarer in English.
contamination:
  risk: high
  note: >
    The English items are the 2021 public TruthfulQA set. The translations have been on
    Hugging Face since May 2024 and on GitHub under Apache-2.0. That is ample time for
    crawls. The paper argues machine translation is a viable extra-language extension,
    which also means leaked English items can be rendered into the other four languages.
harness:
  lm_eval: "truthfulqa-multi"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Tag truthfulqa-multi covers the MC tasks. Generation tasks use tag truthfulqa_multi
    (underscore). Runnable names: truthfulqa-multi_mc1_{en,es,ca,gl,eu},
    truthfulqa-multi_mc2_{en,es,ca,gl,eu}, truthfulqa-multi_gen_{en,es,ca,gl,eu}.
    There is no group YAML. Dataset HiTZ/truthfulqa-multi. num_fewshot follows the 6-example
    train split. Paper judges are not in lm-eval.
tags:
  - truthfulness
  - multilingual
  - multiple-choice
  - generation
  - safety
  - misconceptions
sources:
  - url: "https://arxiv.org/abs/2502.09387"
    title: "Truth Knows No Language: Evaluating Truthfulness Beyond English (arXiv abs)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.09387"
    title: "ar5iv HTML of 2502.09387 (methods, MC2 vs judge, 817 items, 6-shot)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/truthfulqa-multi/raw/main/README.md"
    title: "HiTZ/truthfulqa-multi dataset card (Apache-2.0, five language configs)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=HiTZ/truthfulqa-multi"
    title: "datasets-server split counts: 817 validation and 6 train per language"
    accessed: "2026-09-08"
  - url: "https://github.com/hitz-zentroa/truthfulqa-multi"
    title: "hitz-zentroa/truthfulqa-multi repository (Apache-2.0, experiment scripts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/truthfulqa-multi/README.md"
    title: "lm-eval truthfulqa-multi README (task list, paper citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/truthfulqa-multi/truthfulqa-multi_mc_common"
    title: "MC common YAML (HiTZ/truthfulqa-multi, acc, train/validation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/truthfulqa-multi/truthfulqa-multi_gen_common"
    title: "Generation common YAML (BLEU metrics; BLEURT/ROUGE commented out)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2109.07958"
    title: "Original TruthfulQA abstract (817 items, 38 categories, 94% human)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

TruthfulQA-Multi asks the same 817 misconception traps as [TruthfulQA](truthfulqa.md), in English and in professional Spanish, Catalan, Galician and Basque. Each item still has a best answer, extra true answers, and false answers that echo common myths. Translators kept US-centric names and settings instead of rewriting questions for local culture, so a Basque score is not a test of Basque cultural knowledge. The paper's claim is about whether truthfulness holds as language resource level drops, not about covering new falsehoods.

## How it is scored

lm-eval multiple-choice follows the original MC1 and MC2 definitions and reports accuracy. Generation in the harness scores BLEU against true versus false references (`bleu_max`, `bleu_acc`, `bleu_diff`). That is not the paper's main generation protocol. Calvo Figueras et al. label 400 model answers by hand, then train LLM judges; they find a Gemma 2 9B instruct judge agrees with humans more than MC2 does. They also warn that base models often answer with a local "I have no comment," which original TruthfulQA counts as truthful and can inflate non-English base scores. Few-shot uses six train examples. Instruct models are wrapped as user/assistant turns.

## Dataset and licence

Hugging Face `HiTZ/truthfulqa-multi` has five configs (`en`, `es`, `ca`, `gl`, `eu`). Each has 817 validation questions and six train questions. Licence is Apache-2.0 on the dataset card and the GitHub repo. Answers are public. The English side is the original TruthfulQA set, not a new English rewrite.

## Who publishes it

The authors are at HiTZ/Ixa (UPV/EHU), Elhuyar, CiTIUS in Santiago de Compostela, and Universitat Pompeu Fabra. The paper is "Truth Knows No Language: Evaluating Truthfulness Beyond English," arXiv 2502.09387 (v1 13 February 2025; v3 16 June 2025). Code lives at `hitz-zentroa/truthfulqa-multi`. The Hub dataset last-modified 21 May 2025. No separate public leaderboard was opened for this page.

## Lineage

This is a parallel translation of [TruthfulQA](truthfulqa.md), not a new item set. It is not [galician_bench](galician_bench.md)'s `truthfulqa_gl` (proxectonos) and not [catalan_bench](catalan_bench.md)'s `truthfulqa_va`. Those are other localisations. The paper also studies machine-translated copies of the same questions as a cheaper expansion path.

## Saturation and contamination

Table 4 in the paper (ar5iv HTML) has gemma-2-27b-it at 84.0 Judge-LLM English and 79.0 average, with 61.3 MC2 average. That is the 2025 study's best among 12 Llama 3/3.1 and Gemma 2 models, not a live ceiling. Instruct models beat their base twins. Contamination risk is high: English keys have been public since 2021, and the Hub translations since May 2024.

## How to run it

```bash
lm_eval --model hf --model_args pretrained=<model> --tasks truthfulqa-multi
```

That tag runs the MC tasks. Generation tasks are `truthfulqa-multi_gen_{en,es,ca,gl,eu}` under tag `truthfulqa_multi`. Do not treat harness BLEU as the paper's judge number. The authors' judge checkpoints are on Hugging Face collection `HiTZ/multilingual-truthfulqa-682f33d0d1d5a60d13604eb6`; this page did not re-run them.

## Reading the numbers

A high MC2 or judge score means the model avoided this fixed list of myths in that language, not that it is generally honest. Compare languages only on the same metric: MC2 flattens language gaps that the judge and human labels still show. Base-model truthfulness without an informativeness number is easy to misread, especially outside English. Pair this with a locally authored truthfulness set if you care about non-US falsehoods.
