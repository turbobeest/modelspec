---
id: okapi_mmlu_multilingual
name: "Okapi multilingual MMLU"
aliases:
  - "m_mmlu"
  - "mmlu_multilingual"
  - "alexandrainst/m_mmlu"
page_kind: benchmark
category: knowledge
subcategory: "machine-translated four-choice academic knowledge"
status: active
summary: "lm-eval tag m_mmlu: ChatGPT-translated MMLU in 34 language configs, four-choice accuracy on the test split."
measures: >
  okapi_mmlu_multilingual is EleutherAI's wrap of Alexandra Institute's
  alexandrainst/m_mmlu. Each item is a four-option academic question in one
  language, flattened from English [MMLU](mmlu.md) subjects. The model must pick
  A–D. University of Oregon translated most languages with GPT-3.5-turbo for
  Okapi; Icelandic used Greynir and Norwegian used DeepL. This is not a
  native-exam suite such as [ArabicMMLU](arabic_mmlu.md) or [GreekMMLU](greekmmlu.md),
  and it is not [Global-MMLU](global_mmlu.md).
task_format: >
  Four-option multiple choice. Prompt is instruction plus A–D options and
  "Answer:". Target is the answer letter. fewshot_split is train with sampler
  first_n; test_split is test. Runnable tasks are m_mmlu_{lang} for 34 Hub
  configs. YAML tag is m_mmlu. There is no README in this harness folder.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four options, so chance is 25%. English MMLU's expert-level estimate does not
    transfer. Okapi paper tables are 7B BLOOM/LLaMA runs via the Eleuther harness,
    not a human study on the translations.
dataset:
  size: 13258
  size_note: >
    Hugging Face datasets-server on alexandrainst/m_mmlu (2026-09-08): 34 language
    configs, each with train/val/test. English test is 13,258 (train 277, val
    1,449). Test sizes range from hy 10,891 to es 13,334. Sum of all 34 test
    splits is 432,116; that is translations of the same questions, not unique
    English items. Original cais/mmlu test is 14,042; Okapi
    paper text says 13,062. Train rows are 215–280 per language (Nepali 215, several
    languages 280), not MMLU's 5 few-shot items per subject. Features: instruction,
    option_a–d, answer, id.
  url: "https://huggingface.co/datasets/alexandrainst/m_mmlu"
  license: "CC-BY-NC-4.0"
  languages:
    - ar
    - bn
    - ca
    - da
    - de
    - en
    - es
    - eu
    - fr
    - gu
    - hi
    - hr
    - hu
    - hy
    - id
    - is
    - it
    - kn
    - ml
    - mr
    - nb
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
  splits: "train / val / test per language; lm-eval scores test and takes few-shot from train"
  public_test_set: true
publisher:
  org: "University of Oregon NLP (Okapi translations); Alexandra Institute (Hub dump); EleutherAI (lm-eval tasks)"
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
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/okapi/mmlu_multilingual"
released: "2023-07"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: "mmlu"
  successors: []
  variants:
    - global_mmlu
    - arabic_mmlu
    - greekmmlu
    - egymmlu
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    English MMLU is at the expert ceiling for frontier models. No current numeric
    top score was read for these translations. Okapi's own 7B tables show smaller
    RLHF gains on MMLU than on ARC/HellaSwag, which the paper attributes to Alpaca-
    style instructions not covering professional subjects.
contamination:
  risk: high
  note: >
    Test labels are public. Source is a GPT translation of public MMLU. A model
    can memorise English items or the translated strings. CC-BY-NC-4.0 on the Hub
    card does not reduce leakage.
harness:
  lm_eval: "m_mmlu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "directory okapi/mmlu_multilingual; per-language tasks m_mmlu_{lang}; dataset alexandrainst/m_mmlu"
tags:
  - knowledge
  - multiple-choice
  - multilingual
  - machine-translation
  - mmlu
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
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/mmlu_multilingual/_default_yaml"
    title: "lm-eval m_mmlu _default_yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/mmlu_multilingual/m_mmlu_ar.yaml"
    title: "lm-eval m_mmlu_ar.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/mmlu_multilingual/_generate_configs.py"
    title: "lm-eval mmlu_multilingual _generate_configs.py"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/alexandrainst/m_mmlu"
    title: "alexandrainst/m_mmlu dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/alexandrainst/m_mmlu"
    title: "alexandrainst/m_mmlu API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=alexandrainst/m_mmlu"
    title: "datasets-server info for m_mmlu"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=cais/mmlu"
    title: "datasets-server info for cais/mmlu (English test 14,042)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model answers a four-choice academic question in a target language. Subjects still span the MMLU mix of STEM, humanities, social science, and professional topics. The Hub dump flattens those subjects into one `instruction` field plus four options, so a run is a language-level accuracy, not the 57-subject grid of [MMLU](mmlu.md).

Oregon translated English MMLU with ChatGPT for Okapi so RLHF models could be scored beyond English. Alexandra Institute added Icelandic (Greynir) and Norwegian (DeepL) and published `alexandrainst/m_mmlu`. That is machine translation of existing English items, not a locally written exam.

## How it is scored

YAML metric is mean accuracy on the letter A–D. Chance is 25%. `test_split` is `test`. Few-shot examples come from `train` with `first_n`, but the YAML does not pin `num_fewshot`, so the CLI decides the shot count. Original MMLU reporting is usually 5-shot from five hand-picked dev items per subject. Here the train split is 215–280 mixed rows per language, so a 5-shot run is not the Hendrycks protocol even when someone passes `num_fewshot=5`.

The Okapi paper says it used the Eleuther harness following the Open LLM Leaderboard. Compare a new number to those tables only if shot count and language match.

## Dataset and licence

Hub card licence is CC-BY-NC-4.0. Okapi data is also CC BY NC 4.0. Original MMLU is MIT.

datasets-server (2026-09-08) has 34 configs. English test is 13,258 versus 14,042 on `cais/mmlu` and 13,062 in the Okapi paper. Per-language test counts run from 10,891 (Armenian) to 13,334 (Spanish). Summing 34 test splits (432,116) double-counts translations of the same questions. Train/val exist for few-shot and are smaller than English MMLU's validation set. An Arabic sample row was fully Arabic with answer `C` and an id like `sociology/test/49`.

## Who publishes it

Okapi authors as on arXiv 2307.16039 (Lai, Van Nguyen, Ngo, Nguyen, Dernoncourt, Rossi, Nguyen), 29 July 2023, University of Oregon NLP. Reference eval code: `nlp-uoregon/mlmm-evaluation`. Hub host: Alexandra Institute, lastModified 2024-03-11. lm-eval tasks sit in `okapi/mmlu_multilingual` without a folder README; configs are generated by `_generate_configs.py`. Oregon advertises `uonlp/open_multilingual_llm_leaderboard`.

## Lineage

Predecessor is [MMLU](mmlu.md). Okapi's original 26 languages are listed on the mlmm-evaluation README. lm-eval's 34 configs add English, Icelandic, Norwegian, Basque, Gujarati, Armenian, Portuguese, and Swedish. Later professionally translated or natively written suites include [global_mmlu](global_mmlu.md), [arabic_mmlu](arabic_mmlu.md), [greekmmlu](greekmmlu.md), and [egymmlu](egymmlu.md); those are not this dump. Sister groups: [okapi_hellaswag_multilingual](okapi_hellaswag_multilingual.md) and [okapi_truthfulqa_multilingual](okapi_truthfulqa_multilingual.md).

## Saturation and contamination

English MMLU is saturated at the frontier. These translations still show 7B-scale gaps in the 2023 paper, but no 2026 leaderboard cell was opened here. Contamination is high: public English MMLU plus a public translation. A score can be memorisation of either.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks m_mmlu
```

Or `m_mmlu_zh`, `m_mmlu_ar`, and so on. The census path `okapi/mmlu_multilingual` is a directory, not the YAML `task:` name. Dataset is `alexandrainst/m_mmlu`. Record `num_fewshot`. Do not mix this accuracy with Global-MMLU or with a subject-level English MMLU mean.

## Reading the numbers

A strong `m_mmlu_fr` score means the model picks the translated letter, not that it would pass a French university exam. Translation can simplify wording, drop hard items (counts are below 14,042), or keep English proper nouns. Report language and shot count. For a culturally labelled, professionally translated MMLU, use [global_mmlu](global_mmlu.md) instead of this Okapi dump.
