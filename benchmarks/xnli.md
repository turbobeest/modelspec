---
id: xnli
name: "XNLI (Cross-lingual Natural Language Inference)"
aliases:
  - "Cross-lingual NLI"
  - "facebook/xnli"
page_kind: benchmark
category: reasoning
subcategory: "15-language three-way textual entailment"
status: active
summary: "Cross-lingual three-way NLI in 15 languages: given a premise and hypothesis, choose entailment, contradiction, or neutral."
measures: >
  XNLI tests whether a model can decide, in each of 15 languages, if a premise
  sentence entails a hypothesis, contradicts it, or neither (neutral). The
  English pairs come from MultiNLI's development and test genres. Professional
  translators produced the other 14 languages so the same labels apply across
  the parallel set. The original use was cross-lingual transfer: train NLI in
  English, test in another language without target-language NLI labels.
task_format: >
  Three-way classification (entailment / neutral / contradiction). lm-evaluation-harness
  scores multiple-choice log-likelihood over a cloze: premise + ", {right}?
  {Yes|Also|No}, " + hypothesis, with those cue words translated per language
  in utils.py. The group `xnli` averages accuracy across 15 language tasks,
  weighted by size.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three labels, so uniform chance is 33.3%. The paper does not publish a
    single pooled human-accuracy ceiling comparable to a model score; it
    reports translator-based construction and NLI baselines instead.
dataset:
  size: 112500
  size_note: >
    Paper: 7,500 English MultiNLI development and test pairs translated into
    14 further languages (French, Spanish, German, Greek, Bulgarian, Russian,
    Turkish, Arabic, Vietnamese, Thai, Chinese, Hindi, Swahili, Urdu), 112,500
    annotated pairs in all. Facebook README: 5,000 test and 2,500 development
    pairs per language. Hugging Face `facebook/xnli` per-language configs list
    5,010 test, 2,490 validation and 392,702 train (the train split is
    MultiNLI-scale, machine-translated for non-English configs), which does
    not match 5,000 / 2,500 exactly.
  url: "https://huggingface.co/datasets/facebook/xnli"
  license: "CC BY-NC 4.0"
  languages:
    - ar
    - bg
    - de
    - el
    - en
    - es
    - fr
    - hi
    - ru
    - sw
    - th
    - tr
    - ur
    - vi
    - zh
  modalities:
    - text
  splits: "per language: train (392,702 on Hugging Face) / validation (2,490) / test (5,010); paper describes 2,500 dev and 5,000 test"
  public_test_set: true
publisher:
  org: "Facebook AI, with New York University"
  authors:
    - "Alexis Conneau"
    - "Ruty Rinott"
    - "Guillaume Lample"
    - "Adina Williams"
    - "Samuel R. Bowman"
    - "Holger Schwenk"
    - "Veselin Stoyanov"
  url: "https://github.com/facebookresearch/XNLI"
paper:
  title: "XNLI: Evaluating Cross-lingual Sentence Representations"
  arxiv: "1809.05053"
  url: "https://arxiv.org/abs/1809.05053"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/XNLI"
released: "2018-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - xnli_eu
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current dedicated leaderboard top score was confirmed from a source
    opened here. The 2018 paper reports several MT and aligned-encoder
    baselines, not a present-day LLM ceiling.
contamination:
  risk: high
  note: >
    Development and test labels have been public since 2018 on the Facebook
    download and on Hugging Face, and the English source is MultiNLI. No
    held-out private test is described. This assessment is from publicity
    and age, not a measured leakage study.
harness:
  lm_eval: "xnli"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group `xnli` aggregates xnli_ar, xnli_bg, xnli_de, xnli_el, xnli_en,
    xnli_es, xnli_fr, xnli_hi, xnli_ru, xnli_sw, xnli_th, xnli_tr, xnli_ur,
    xnli_vi, xnli_zh. Common YAML sets training_split train and
    validation_split validation with no test_split, so lm-eval scores the
    2,490-item validation split unless a reporter overrides it. Prompt cues
    were translated word-by-word with Google Translate and may differ from
    XGLM/mGPT. Basque [xnli_eu](xnli_eu.md) is a later extension, not one of
    these 15 tasks.
tags:
  - nli
  - cross-lingual
  - entailment
  - multilingual
  - classification
sources:
  - url: "https://arxiv.org/abs/1809.05053"
    title: "XNLI: Evaluating Cross-lingual Sentence Representations (arXiv:1809.05053)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1809.05053"
    title: "XNLI paper HTML (15 languages, 112,500 pairs, MultiNLI source, OANC note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/XNLI/master/README.md"
    title: "facebookresearch/XNLI README (5,000 test / 2,500 dev, 15 languages)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/XNLI/master/LICENSE"
    title: "facebookresearch/XNLI LICENSE (CC BY-NC 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/facebook/xnli/raw/main/README.md"
    title: "Hugging Face facebook/xnli card (split counts; licence field unfilled)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/xnli"
    title: "facebook/xnli API metadata (5,010 test / 2,490 validation / 392,702 train)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli/README.md"
    title: "lm-evaluation-harness xnli README (group, 15 tasks, cloze prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli/_xnli.yaml"
    title: "lm-eval xnli group (size-weighted mean accuracy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli/xnli_common_yaml"
    title: "lm-eval xnli_common_yaml (facebook/xnli, validation split, acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli/utils.py"
    title: "lm-eval xnli utils.py (per-language Yes/Also/No cues)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-016 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-016"
---

## What it measures

XNLI is three-way natural language inference in 15 languages. The model sees a premise and a hypothesis and must choose entailment, contradiction or neither (neutral). English items are MultiNLI development and test pairs. Professional translators produced French, Spanish, German, Greek, Bulgarian, Russian, Turkish, Arabic, Vietnamese, Thai, Chinese, Hindi, Swahili and Urdu so the same labels hold across a parallel corpus. The 2018 question was cross-lingual transfer: train NLI in English, test in another language without new NLI annotation.

It is not [ANLI](anli.md), which is English-only and adversarial. Basque [xnli_eu](xnli_eu.md) is a 2024 add-on, not one of the original 15.

## How it is scored

Each pair is a three-way class, so chance is 33.3%. Papers often report accuracy per language and a macro average. lm-evaluation-harness instead builds three full-sentence options — premise + a translated "right? Yes/Also/No," + hypothesis — and picks the sequence with highest likelihood. The `xnli` group then takes a size-weighted mean of `acc` over the 15 `xnli_*` tasks. Those cue words were translated with Google Translate and the harness README warns they may not match XGLM or mGPT. The common YAML names `validation` as the eval split and does not set `test_split`, so a default lm-eval run is the 2,490-row validation set, not the 5,010-row test set.

## Dataset and licence

The paper counts 7,500 English MultiNLI development and test pairs translated into 14 languages, 112,500 labelled pairs. The Facebook README splits that as 5,000 test and 2,500 development per language. Hugging Face `facebook/xnli` lists 5,010 test, 2,490 validation and 392,702 train per language config; the train split is MultiNLI-scale and, for non-English configs, machine-translated rather than professionally translated eval data. Labels are public.

The GitHub LICENSE is Creative Commons Attribution-NonCommercial 4.0. The Hugging Face card's licensing section is unfilled. The paper also notes that most MultiNLI source sentences follow the OANC licence, with US public-domain fiction from *Captain Blood*.

## Who publishes it

Alexis Conneau, Ruty Rinott, Guillaume Lample, Adina Williams, Samuel R. Bowman, Holger Schwenk and Veselin Stoyanov, at Facebook AI and New York University. Posted as arXiv:1809.05053 on 13 September 2018 and published at EMNLP 2018. Data and code sit at github.com/facebookresearch/XNLI. No dedicated live leaderboard was confirmed here.

## Lineage

XNLI extends MultiNLI (and, behind that, SNLI) into a 15-language eval. [ANLI](anli.md) is a later English adversarial NLI set, not a successor. [xnli_eu](xnli_eu.md) adds Basque via machine translation, post-edits and a native test set. Harness language ids such as `xnli_gl` in [galician_bench](galician_bench.md) are separate translations, not this group.

## Saturation and contamination

No current top score was read from a leaderboard for this page. The 2018 baselines are MT and aligned encoders, not today's LLMs. Contamination risk is high: eval labels have been downloadable since 2018, and the English text is MultiNLI.

## How to run it

lm-eval: group `xnli`, or a single `xnli_en` / `xnli_ar` / … task. Dataset `facebook/xnli`. Default eval split is validation. OpenCompass, inspect_evals, HELM and BIG-bench paths were not confirmed here.

Name the language, split (validation vs test) and prompt template before comparing numbers. A size-weighted group mean is not a macro-average over languages.

## Reading the numbers

A high XNLI score means the model can do three-way entailment in that language's wording, not that it was trained on that language's NLI. Cross-lingual transfer, translate-train and translate-test are different protocols and should not be averaged together. lm-eval's cloze with Yes/Also/No is not the same as a fine-tuned classifier head on the 5,010-item test set. For Basque, use [xnli_eu](xnli_eu.md). Given fully public keys since 2018, an unusually high score on a model trained after that year needs a second NLI set.
