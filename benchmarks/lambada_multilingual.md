---
id: lambada_multilingual
name: "LAMBADA multilingual (OpenAI MT)"
aliases:
  - "lambada_openai_mt"
  - "lambada_mt"
page_kind: benchmark
category: reasoning
subcategory: "multilingual last-word prediction on machine-translated LAMBADA"
status: active
summary: "lm-eval group of OpenAI-format LAMBADA last-word tests in English and machine-translated German, Spanish, French and Italian (5,153 passages each)."
measures: >
  lambada_multilingual is EleutherAI's lm-evaluation-harness group over five
  OpenAI-format LAMBADA cloze sets. Each item is a narrative passage whose last
  word is withheld; the model must assign higher likelihood to that word than to
  alternatives, using discourse beyond the final sentence. Four configs are
  machine translations of the English OpenAI test split into German, Spanish,
  French and Italian. The fifth, English, loads Hugging Face config `en` rather
  than the `default` config used by lambada_openai. Text only.
task_format: >
  Causal language-model cloze scored as loglikelihood, not free generation.
  Prompt is the passage minus the last whitespace token; the target is a leading
  space plus that token. Runnable task names are lambada_openai_mt_{en,de,es,fr,it}.
metric:
  name: "accuracy (next-word exact match); perplexity also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    YAML metric_list records acc (mean, higher better) and perplexity (lower
    better). No random or human baseline is defined for open-vocabulary next-word
    prediction. The original 2016 LAMBADA paper's human filter applies to English
    source passages, not to these translations.
dataset:
  size: 25765
  size_note: >
    Five Hugging Face configs on EleutherAI/lambada_openai, each with a test split
    of 5,153 examples (en, de, es, fr, it), totalling 25,765 scored passages if
    the group is run in full. The card's `default` config is also 5,153 rows and
    is what lambada_openai uses; this page did not byte-compare `default` with
    `en`. Translations were produced with googletrans (Google Translate) by Sid
    Black, from lambada_test_en.jsonl.
  url: "https://huggingface.co/datasets/EleutherAI/lambada_openai"
  license: "MIT (Hugging Face cardData); README Licensing section cites Modified MIT (OpenAI GPT-2)"
  languages:
    - en
    - de
    - es
    - fr
    - it
  modalities:
    - text
  splits: "test only, 5,153 rows per language config"
  public_test_set: true
publisher:
  org: "EleutherAI (harness group and Hugging Face mirror); original LAMBADA, University of Trento CIMeC and University of Amsterdam"
  authors:
    - "Sid Black"
    - "Denis Paperno"
    - "Germán Kruszewski"
    - "Angeliki Lazaridou"
    - "Quan Ngoc Pham"
    - "Raffaella Bernardi"
    - "Sandro Pezzelle"
    - "Marco Baroni"
    - "Gemma Boleda"
    - "Raquel Fernández"
  url: "https://huggingface.co/datasets/EleutherAI/lambada_openai"
paper:
  title: "The LAMBADA dataset: Word prediction requiring a broad discourse context"
  arxiv: "1606.06031"
  url: "https://arxiv.org/abs/1606.06031"
  year: 2016
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/lambada_multilingual"
released: "2023-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: "lambada"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated numeric leaderboard for the five mt tasks was opened here. English
    LAMBADA was already near ceiling in GPT-3's 2020 paper (see lambada.md).
    Translation quality, not discourse tracking, can dominate the non-English
    numbers.
contamination:
  risk: high
  note: >
    The OpenAI-format English split has been public for years and is widely
    mirrored. The four translations have been on Hugging Face since the dataset
    was created on 2022-12-16 (card lastModified 2025-07-10). YAML sets
    should_decontaminate: true with the full passage as the query. Machine
    translation does not make the items private.
harness:
  lm_eval: "lambada_multilingual"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Runnable tasks lambada_openai_mt_en, lambada_openai_mt_de, lambada_openai_mt_es, lambada_openai_mt_fr, lambada_openai_mt_it. Group tag lambada_multilingual. Distinct from lambada_openai / lambada_standard under the lambada group, and from lambada_multilingual_stablelm."
tags:
  - language-modelling
  - cloze
  - multilingual
  - machine-translation
  - lambada
  - lm-eval
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual/README.md"
    title: "lm-evaluation-harness lambada_multilingual README (group and mt task list)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual/lambada_mt_en.yaml"
    title: "lambada_openai_mt_en YAML (group tag, EleutherAI/lambada_openai, acc and perplexity)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual/lambada_mt_de.yaml"
    title: "lambada_openai_mt_de YAML (include en; task lambada_openai_mt_de; dataset_name de)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada/lambada_openai.yaml"
    title: "lambada_openai YAML (dataset_name default; same scoring template)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/lambada_openai"
    title: "EleutherAI/lambada_openai dataset card (cardData license mit; README Licensing section Modified MIT; 5,153 test rows per en/de/es/fr/it; googletrans script)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/openai/gpt-2/master/LICENSE"
    title: "OpenAI GPT-2 Modified MIT licence (target of the EleutherAI card Licensing link)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/lambada_openai"
    title: "Hugging Face dataset API (created 2022-12-16; lastModified 2025-07-10; split counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/lambada_openai/raw/main/translation_script.txt"
    title: "translation_script.txt (Sid Black; googletrans en→de/fr/it and related dest)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1606.06031"
    title: "Original LAMBADA paper (Paperno et al., 2016)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/commits?path=lm_eval/tasks/lambada_multilingual"
    title: "Harness commits (add lambada_mt tasks 2023-07-05)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-011 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-011"
---

## What it measures

This group asks a language model to predict the last word of a short narrative
passage after seeing the rest of the text. The construction is the OpenAI
reformat of English [LAMBADA](lambada.md): humans could guess the word from the
full passage, not from the last sentence alone. Four of the five configs are
machine translations of that English test split into German, Spanish, French and
Italian. The fifth is English under Hugging Face config `en`. The intended skill
is still discourse tracking, but a wrong translation of the target word can fail
the item even when the model tracked the story.

## How it is scored

Each YAML task uses loglikelihood scoring. Accuracy is the fraction of passages
where the model's next-token ranking matches the gold last word; perplexity is
also reported and is lower-is-better. There is no answer list and no partial
credit. Tokenization of the gold word matters, as on English LAMBADA. The
runnable names are `lambada_openai_mt_en` and the four `lambada_openai_mt_{de,es,fr,it}`
tasks; the group name `lambada_multilingual` runs all five. Do not mix these
numbers with `lambada_openai` or `lambada_standard`.

## Dataset and licence

EleutherAI/lambada_openai publishes five language configs plus `default`, each
with 5,153 test rows on the Hugging Face card and API (created 2022-12-16). The
non-English files were written with googletrans from `lambada_test_en.jsonl` by
Sid Black; the script in the dataset repo names Google Translate front-ends.
The card's YAML `license` field is MIT. The same README's Licensing section
instead says "Modified MIT" and links OpenAI's GPT-2 licence. That is a
disagreement on one card, not a second dataset. Original `cimec/lambada` English
is documented as CC BY 4.0 on [lambada](lambada.md). This page records the
EleutherAI mirror the harness loads, with both MIT and Modified MIT readings.
`default` and `en` report the same 5,153 rows and the same byte size on the
Hugging Face API; they were not hashed against each other here.

## Who publishes it

The passages come from Paperno and colleagues' 2016 LAMBADA set. OpenAI's GPT-2
era reformat is the English source for this mirror. EleutherAI hosts the dataset
and the harness group. The mt YAML files were added to lm-evaluation-harness on
2023-07-05. No organisation runs a dedicated multilingual LAMBADA leaderboard.

## Lineage

Predecessor is English [LAMBADA](lambada.md). This page is the harness group,
not a spelling of `lambada_openai`. A separate directory
`lambada_multilingual_stablelm` exists in the harness and has no page here.
Machine translation is a change of language, not a new discourse filter, so a
strong German score is not evidence that the LAMBADA human filter still holds.

## Saturation and contamination

No current top score for the five mt tasks was read from a leaderboard. English
LAMBADA was already high by 2020. Contamination risk is high: the English items
are old and public, and the translations have been downloadable since December
2022. The YAML enables decontamination queries over the full passage; that only
helps pipelines that actually filter.

## How to run it

In lm-evaluation-harness, run the group `lambada_multilingual` or a single
`lambada_openai_mt_*` task. Each loads `EleutherAI/lambada_openai` with
`dataset_name` set to `en`, `de`, `es`, `fr` or `it`, `test_split: test`.
Scoring is loglikelihood, not generate-until. OpenCompass and HELM names for
this group were not confirmed. Compare two numbers only when they share a
language config and the OpenAI-format detokenization.

## Reading the numbers

A high score on one language means the model assigned the gold last word the
best likelihood on that 5,153-row split. On de/es/fr/it it can also mean the
translation left a locally predictable last word, or that the model memorised
the English story and the translated target. The English mt task may overlap
`lambada_openai` on [lambada](lambada.md). Prefer a native, human-filtered
cloze if the claim is about discourse in that language, and say which of the
five tasks produced the number.
