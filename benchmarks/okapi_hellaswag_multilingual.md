---
id: okapi_hellaswag_multilingual
name: "Okapi multilingual HellaSwag"
aliases:
  - "hellaswag_multilingual"
  - "m_hellaswag"
  - "alexandrainst/m_hellaswag"
page_kind: benchmark
category: reasoning
subcategory: "machine-translated four-way commonsense sentence continuation"
status: active
summary: "lm-eval group of GPT-translated HellaSwag val sets in 30 languages; four-way continuation, scored acc and acc_norm."
measures: >
  okapi_hellaswag_multilingual is EleutherAI's lm-evaluation-harness group over
  machine-translated HellaSwag. The model reads an activity label plus a short
  scene and must pick which of four endings is the everyday next step. Items
  come from ActivityNet captions and WikiHow, same as English [HellaSwag](hellaswag.md).
  University of Oregon translated the English set with ChatGPT (GPT-3.5-turbo)
  for the Okapi paper; Alexandra Institute hosts the Hub dump and added Icelandic
  and Norwegian. Text only. This is not native-writer Darija or Egyptian Arabic
  HellaSwag.
task_format: >
  Four-way multiple choice. Runnable tasks are hellaswag_{ar,bn,ca,da,de,es,eu,fr,
  gu,hi,hr,hu,hy,id,it,kn,ml,mr,ne,nl,pt,ro,ru,sk,sr,sv,ta,te,uk,vi}. YAML tag
  and README group: hellaswag_multilingual. Prompt is activity_label + ": " +
  ctx_a/ctx_b after WikiHow-bracket cleanup; target is the original label field;
  metrics acc and acc_norm. Split is val only.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four endings, so chance is 25%. The English HellaSwag abstract (Zellers et al.,
    2019) gives >95% human accuracy; that figure does not transfer to these
    translations. The Okapi paper reports 7B BLOOM/LLaMA tables, not a human rater
    study on the translated items.
dataset:
  size: 275384
  size_note: >
    Hugging Face datasets-server on alexandrainst/m_hellaswag (accessed 2026-09-08):
    33 language configs with a val split only, 8,413–9,485 rows each (ta 8,413,
    sk 9,485). Sum of the 30 configs that have lm-eval YAML is 275,384. English
    config is 9,368, not the original 10,042-row HellaSwag validation set
    (Rowan/hellaswag). Okapi paper text says 9,162 HellaSwag questions. Hub card and
    siblings include zh (data/zh/val.jsonl); that config was not in datasets-server
    dataset_info. lm-eval ships no YAML for en, is, nb, or zh.
  url: "https://huggingface.co/datasets/alexandrainst/m_hellaswag"
  license: "CC-BY-NC-4.0"
  languages:
    - ar
    - bn
    - ca
    - da
    - de
    - es
    - eu
    - fr
    - gu
    - hi
    - hr
    - hu
    - hy
    - id
    - it
    - kn
    - ml
    - mr
    - ne
    - nl
    - pt
    - ro
    - ru
    - sk
    - sr
    - sv
    - ta
    - te
    - uk
    - vi
  modalities:
    - text
  splits: "val only (HF split name val); lm-eval validation_split val, test_split null"
  public_test_set: true
publisher:
  org: "University of Oregon NLP (Okapi translations); Alexandra Institute (Hub dump); EleutherAI (lm-eval group)"
  authors:
    - "Viet Dac Lai"
    - "Chien Van Nguyen"
    - "Nghia Trung Ngo"
    - "Thuat Nguyen"
    - "Franck Dernoncourt"
    - "Ryan A. Rossi"
    - "Thien Huu Nguyen"
  url: "https://github.com/nlp-uoregon/Okapi"
paper:
  title: "Okapi: Instruction-tuned Large Language Models in Multiple Languages with Reinforcement Learning from Human Feedback"
  arxiv: "2307.16039"
  url: "https://arxiv.org/abs/2307.16039"
  year: 2023
leaderboard_url: "https://huggingface.co/spaces/uonlp/open_multilingual_llm_leaderboard"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/okapi/hellaswag_multilingual"
released: "2023-07"
last_updated: "2024-02"
lineage:
  family: ""
  predecessor: "hellaswag"
  successors: []
  variants:
    - darijahellaswag
    - egyhellaswag
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated numeric cell was read from the uonlp Open Multilingual LLM Leaderboard
    space. English HellaSwag is saturated; these translations still show large
    7B-era gaps in the Okapi paper (Table 4 BLOOM RLHF high-resource HellaSwag
    group mean 46.6) and were not re-scored here on current frontier models.
contamination:
  risk: high
  note: >
    Labels are public. Source is a GPT translation of the 2019 HellaSwag
    validation set, which is itself widely mirrored. Translation artifacts can
    leak the English original. One Arabic sample row still had an English
    activity_label; how often that happens was not counted.
harness:
  lm_eval: "hellaswag_multilingual"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "per-language tasks hellaswag_{lang}; directory okapi/hellaswag_multilingual; dataset alexandrainst/m_hellaswag"
tags:
  - commonsense
  - multiple-choice
  - multilingual
  - machine-translation
  - hellaswag
sources:
  - url: "https://arxiv.org/abs/2307.16039"
    title: "Okapi paper (arXiv 2307.16039)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.16039"
    title: "Okapi paper HTML (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/nlp-uoregon/Okapi"
    title: "nlp-uoregon/Okapi repository README"
    accessed: "2026-09-08"
  - url: "https://github.com/nlp-uoregon/mlmm-evaluation"
    title: "nlp-uoregon/mlmm-evaluation README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/hellaswag_multilingual/README.md"
    title: "lm-eval okapi/hellaswag_multilingual README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/hellaswag_multilingual/_hellaswag_yaml"
    title: "lm-eval _hellaswag_yaml template"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/hellaswag_multilingual/hellaswag_ar.yaml"
    title: "lm-eval hellaswag_ar.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/hellaswag_multilingual/utils.py"
    title: "lm-eval hellaswag_multilingual utils.py"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Rowan/hellaswag"
    title: "Rowan/hellaswag dataset card (English original)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1905.07830"
    title: "HellaSwag paper (arXiv 1905.07830)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/alexandrainst/m_hellaswag"
    title: "alexandrainst/m_hellaswag dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/alexandrainst/m_hellaswag"
    title: "alexandrainst/m_hellaswag API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=alexandrainst/m_hellaswag"
    title: "datasets-server info for m_hellaswag"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The task is ordinary HellaSwag commonsense: given a short scene, pick the plausible next sentence among four endings. Contexts still come from ActivityNet video captions and WikiHow how-tos. What changes is the language. University of Oregon built the translations with ChatGPT so Okapi could score multilingual instruction-tuned models on the same Open LLM Leaderboard tasks that English models already used.

lm-eval's group is not a new native-language exam. It is a machine-translated copy of the English validation items, hosted as `alexandrainst/m_hellaswag`. That is a different object from [DarijaHellaSwag](darijahellaswag.md) or [EgyHellaSwag](egyhellaswag.md), which were rewritten into a dialect rather than bulk-translated for Okapi.

## How it is scored

Each item is four-way multiple choice, so chance is 25%. The YAML reports mean `acc` and length-normalised `acc_norm`, the same pair English HellaSwag uses in the harness. There is no test split in this dump: every language config is `val` only. The template does not set a shot count, so a run is zero-shot unless the CLI passes `num_fewshot`. The Okapi paper says it followed the Hugging Face Open LLM Leaderboard / Eleuther harness; it does not restate a shot count, so paper tables and a default lm-eval run need not match.

The English HellaSwag human figure (>95% in Zellers et al., 2019) does not apply here. No translated-set human baseline was read.

## Dataset and licence

Alexandra Institute's card states CC-BY-NC-4.0. Okapi's own DATA_LICENSE badge is the same non-commercial clause. Original English HellaSwag is MIT; this dump is not.

datasets-server (2026-09-08) lists 33 val configs, about 8.4k–9.5k rows each after translation drop-out, not the original 10,042 on Rowan/hellaswag. The 30 YAML tasks sum to 275,384 val rows. The Okapi paper quotes 9,162 HellaSwag questions; the Hub English config is 9,368. Both are below the English original. Hub README says Icelandic used Miðeind Greynir and Norwegian used DeepL; remaining languages used GPT-3.5-turbo, first released in `nlp-uoregon/mlmm-evaluation`. lm-eval YAML covers 30 languages and skips Hub extras `en`, `is`, `nb`, and `zh`. The card and Hub siblings include `zh`; that config was not in datasets-server `dataset_info`.

Features match English HellaSwag (`ctx_a`, `ctx_b`, `endings`, `activity_label`, `label`). One Arabic row still had an English activity label.

## Who publishes it

The Okapi paper is Viet Dac Lai, Chien Van Nguyen, Nghia Trung Ngo, Thuat Nguyen, Franck Dernoncourt, Ryan A. Rossi, and Thien Huu Nguyen (University of Oregon NLP, with Adobe co-authors), arXiv 2307.16039, 29 July 2023. Evaluation scripts live in `nlp-uoregon/mlmm-evaluation`. The Hugging Face copy is `alexandrainst/m_hellaswag` (lastModified 2024-02-12). EleutherAI wraps it under `lm_eval/tasks/okapi/hellaswag_multilingual`. Oregon also points at a Hugging Face space, `uonlp/open_multilingual_llm_leaderboard`.

## Lineage

Predecessor is English [HellaSwag](hellaswag.md) (Zellers et al., 2019). Okapi translated ARC, HellaSwag, and MMLU for 26 languages (Russian, German, Chinese, French, Spanish, Italian, Dutch, Vietnamese, Indonesian, Arabic, Hungarian, Romanian, Danish, Slovak, Ukrainian, Catalan, Serbian, Croatian, Hindi, Bengali, Tamil, Nepali, Malayalam, Marathi, Telugu, Kannada). The lm-eval HellaSwag group drops Chinese and adds Basque, Gujarati, Armenian, Portuguese, and Swedish. Related dialect pages in this repository: [darijahellaswag](darijahellaswag.md), [egyhellaswag](egyhellaswag.md). Sister Okapi harness groups: [okapi_mmlu_multilingual](okapi_mmlu_multilingual.md) and [okapi_truthfulqa_multilingual](okapi_truthfulqa_multilingual.md). TruthfulQA was not one of the three Okapi paper evals; ARC multilingual is in the same `okapi/` folder but is not this page.

## Saturation and contamination

English HellaSwag no longer separates frontier models. These copies still can, because translation quality and tokenisation vary, but no current top score was read from a live board. Contamination risk is high: the English val labels have been public since 2019, this dump is public, and a model can learn the English item and the translation together.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks hellaswag_multilingual
```

Or a single language, `hellaswag_vi`. Directory on disk is `lm_eval/tasks/okapi/hellaswag_multilingual`; the runnable group/tag is `hellaswag_multilingual`, not the census path string. Dataset path in YAML is `alexandrainst/m_hellaswag`, split `val`. Compare numbers only when shot count, metric (`acc` vs `acc_norm`), and language set match. The original mlmm-evaluation repo is a separate checkout with its own download script.

## Reading the numbers

A high score on one language means the model ranks the translated ending above three distractors, not that it has native commonsense in that language. ChatGPT translation can preserve English cues, drop items, or leave labels untranslated, so a gap versus English HellaSwag mixes capability and translation noise. Do not average the 30 YAML tasks with Hub `en`/`is`/`nb` or with [global_mmlu](global_mmlu.md)-style professional translations. Look at per-language scores, and put [HellaSwag](hellaswag.md) beside them if you need the English ceiling.
