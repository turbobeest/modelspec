---
id: okapi_arc_multilingual
name: "Okapi ARC multilingual (lm-eval)"
aliases:
  - "arc_multilingual"
  - "okapi/arc_multilingual"
  - "m_arc"
page_kind: benchmark
category: reasoning
subcategory: "machine-translated ARC-Challenge multiple-choice QA in 31 lm-eval languages"
status: active
summary: "lm-eval group of GPT-3.5-translated ARC-Challenge questions in 31 languages on alexandrainst/m_arc, scored with acc and acc_norm."
measures: >
  okapi_arc_multilingual is EleutherAI's lm-evaluation-harness group over
  machine-translated AI2 ARC-Challenge items. Each item is a science question
  with labelled options and one gold letter. University of Oregon Okapi
  translated ARC, HellaSwag, and MMLU with ChatGPT/GPT-3.5-turbo for
  multilingual RLHF eval (arXiv:2307.16039). Alexandra Institute hosts the
  Hugging Face mirror alexandrainst/m_arc and adds Icelandic (Greynir) and
  Norwegian Bokmål (DeepL). English ids in the mirror are ARC-Challenge
  paths, not ARC-Easy. This is not English [arc](arc.md) or
  [arc_challenge](arc_challenge.md).
task_format: >
  Multiple-choice log-likelihood. Template query is "Question: {instruction}
  \\nAnswer:" with choices from option_a..option_e when present. Gold is the
  index of answer in A–E. should_decontaminate true. Tag/group
  arc_multilingual. Per-language tasks are arc_ar, arc_bn, … arc_zh (31
  names). YAML validation_split is "validation"; the Hub configs use split
  name "val".
metric:
  name: "accuracy (acc); acc_norm also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    English test in the mirror is 1,162 four-option, 4 three-option, and 3
    five-option items (1,169 rows). Uniform four-way chance is 25% and is
    recorded here; it slightly overstates chance on the five-way items.
    Original English ARC human figures do not transfer to these translations.
    No Okapi paper aggregate for this 31-language lm-eval group was opened.
dataset:
  size: 36004
  size_note: >
    Hugging Face alexandrainst/m_arc datasets-server size (2026-09-08): 87,391
    rows across 34 language configs. lm-eval lists 31 tasks and omits en, is,
    and nb (79,642 rows if those 31 configs are summed; 36,004 test rows,
    1,100–1,170 per language). English mirror splits are train 1,116 / val
    298 / test 1,169, against original ARC-Challenge 1,119 / 299 / 1,172.
    Armenian (hy) is the smallest config opened (2,478). Gaps are translation
    dropouts, not a second Easy split.
  url: "https://huggingface.co/datasets/alexandrainst/m_arc"
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
    - zh
  modalities:
    - text
  splits: "Hub configs expose train / val / test per language; lm-eval YAML names the middle split validation"
  public_test_set: true
publisher:
  org: "University of Oregon NLP (Okapi); Hugging Face mirror by Alexandra Institute"
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
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/okapi/arc_multilingual"
released: "2023-07"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: arc
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current public leaderboard cell for the 31-language lm-eval group was
    opened here. English ARC-Challenge is separately treated as saturated on
    [arc](arc.md); that ceiling does not automatically apply to these
    translations.
contamination:
  risk: high
  note: >
    Source ARC-Challenge items and answers have been public since 2018.
    Okapi translations have been public since 2023 (mlmm-evaluation, then
    alexandrainst/m_arc). should_decontaminate is on in the YAML. Machine
    translation can still leak English science facts even when the surface
    string is new.
harness:
  lm_eval: "arc_multilingual"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Directory lm_eval/tasks/okapi/arc_multilingual. Tag/group arc_multilingual
    over 31 tasks named arc_{lang}. Dataset alexandrainst/m_arc. Not the
    English ai2_arc group. Sibling Okapi directories hellaswag_multilingual,
    mmlu_multilingual, and truthfulqa_multilingual have no pages here yet.
tags:
  - science-qa
  - multiple-choice
  - multilingual
  - machine-translation
  - arc
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/arc_multilingual/README.md"
    title: "lm-eval Multilingual ARC README (Okapi paper, 31 task names, group arc_multilingual)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/arc_multilingual/_arc_yaml"
    title: "_arc_yaml (tag arc_multilingual, acc/acc_norm, validation_split validation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/arc_multilingual/utils.py"
    title: "utils.py (Question:/Answer: prompt, option_a–e, gold index)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/arc_multilingual/arc_ar.yaml"
    title: "arc_ar.yaml (dataset alexandrainst/m_arc, config ar)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/alexandrainst/m_arc"
    title: "alexandrainst/m_arc card (CC-BY-NC-4.0, GPT-3.5/Greynir/DeepL note)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/alexandrainst/m_arc"
    title: "Hugging Face API dataset object (created 2023-12-27, lastModified 2024-01-15)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=alexandrainst/m_arc"
    title: "datasets-server size (87,391 rows, 34 configs, per-split counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/alexandrainst/m_arc/resolve/main/data/en/test.jsonl"
    title: "English test.jsonl (1,169 ARC-Challenge rows; option counts)"
    accessed: "2026-09-08"
  - url: "https://github.com/nlp-uoregon/Okapi"
    title: "Okapi repository (26-language claim, CC BY NC 4.0 badge, eval pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/nlp-uoregon/Okapi/main/DATA_LICENSE"
    title: "Okapi DATA_LICENSE file (ODC-By text; disagrees with README CC-BY-NC badge)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2307.16039"
    title: "Okapi paper (submitted 2023-07-29)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.16039"
    title: "Okapi paper HTML (ARC/HellaSwag/MMLU translated with ChatGPT)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-062 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-062"
---

## What it measures

okapi_arc_multilingual is grade-school science multiple-choice QA after machine translation. Each item is one question plus A–D (sometimes E) options. Gold ids in the English mirror start with `ARC-Challenge/`, so this is the Challenge pool, not ARC-Easy. Okapi used ChatGPT to translate the Hugging Face Open LLM Leaderboard English sets into many languages. Alexandra Institute republished them as `alexandrainst/m_arc` and added Icelandic and Norwegian Bokmål with other translators. The lm-eval group scored here has 31 language tasks and skips those two plus English.

## How it is scored

lm-eval uses multiple-choice log-likelihood. Metrics are `acc` and length-normalised `acc_norm`. The prompt is `Question: …` then `Answer:`. Empty option fields are dropped, so a few items are three-way or five-way. `should_decontaminate` is on. Few-shot, if used, is meant to come from `train`; the YAML names the Hub `val` split `validation`, which may not load under that name.

## Dataset and licence

datasets-server reports 87,391 rows in 34 configs. The 31 lm-eval languages sum to 36,004 test rows (about 1,100–1,170 each) and 79,642 rows including train and val. English in the mirror is 1,116 / 298 / 1,169 against original Challenge 1,119 / 299 / 1,172. Hugging Face cardData licence is CC-BY-NC-4.0. Okapi's README badge says the same. The Okapi `DATA_LICENSE` file is ODC-By text, which disagrees; this page follows the Hub card for `m_arc`. Original English ARC is CC-BY-SA-4.0.

## Who publishes it

The 2023 Okapi paper (Lai, Van Nguyen, Ngo, Nguyen, Dernoncourt, Rossi, Nguyen; arXiv:2307.16039) describes the translations as eval data for multilingual RLHF. Code and models sit at nlp-uoregon/Okapi. Eval scripts were first pointed at nlp-uoregon/mlmm-evaluation. EleutherAI packages the 31-language group. Alexandra Institute maintains the Hub dataset (created 2023-12-27, last modified 2024-01-15).

## Lineage

Predecessor is English [arc](arc.md) / [arc_challenge](arc_challenge.md). Okapi also shipped translated HellaSwag, MMLU, and later a truthfulqa_multilingual directory in the same lm-eval tree; those ids have no pages here yet. Do not treat `arc_ar` in this group as an Arabic-from-scratch science exam. Do not average these 31 numbers with English ARC-Easy.

## Saturation and contamination

No 31-language top score was opened here. English Challenge is already a leaked 2018 exam. The translations have been public since 2023. A strong translated score can still be English science recall plus translation quality, not new reasoning.

## How to run it

`lm_eval --tasks arc_multilingual` runs the tagged group. Single languages are `arc_zh`, `arc_ar`, and the other 29 names in the README list. Data: `alexandrainst/m_arc` with `dataset_name` set to the ISO code. Compare `acc` with `acc_norm` only when the reporter says which one. If few-shot loading looks for split `validation`, check that the Hub split is actually `val`.

## Reading the numbers

A high `arc_zh` test score means the model preferred the gold option on about 1,170 translated Challenge items, not that it matched English ARC-Challenge. Quote the language, `acc` versus `acc_norm`, and the split. The Hub English config is not in this lm-eval group. Licence is non-commercial on the Hub card. Translation error is a silent extra difficulty: some languages drop more items (Armenian 2,478 total versus English 2,583).
