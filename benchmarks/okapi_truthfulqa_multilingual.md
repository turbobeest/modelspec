---
id: okapi_truthfulqa_multilingual
name: "Okapi multilingual TruthfulQA"
aliases:
  - "truthfulqa_multilingual"
  - "m_truthfulqa"
  - "alexandrainst/m_truthfulqa"
page_kind: benchmark
category: safety
subcategory: "machine-translated multiple-choice truthfulness"
status: active
summary: "lm-eval group of GPT-translated TruthfulQA val items in 31 languages, scored as MC1 accuracy and MC2 probability mass."
measures: >
  okapi_truthfulqa_multilingual is EleutherAI's group over machine-translated
  [TruthfulQA](truthfulqa.md). The model is asked a question written to bait a
  popular misconception and must prefer the true continuation over false ones.
  Hub dump alexandrainst/m_truthfulqa was translated with GPT-3.5-turbo by
  University of Oregon and first lived in nlp-uoregon/mlmm-evaluation. The Okapi
  paper's own eval suite is ARC, HellaSwag, and MMLU; this TruthfulQA translation
  uses the same pipeline but is not one of those three paper tables. English
  text only in the six-shot prefix; questions are in the target language.
task_format: >
  Multiple choice, two YAML variants per language: truthfulqa_{lang}_mc1 and
  truthfulqa_{lang}_mc2. README group/tag truthfulqa_multilingual. MC1 target
  index is 0 (first listed choice). MC2 uses labelled true/false options and
  sums normalised probability mass on true labels. Validation split val.
  process_docs prepends a fixed English 6-QA prompt before the translated
  question.
metric:
  name: "MC1 accuracy; MC2 normalised true-answer probability (acc)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    MC1 chance depends on how many false options the item has, which varies.
    English TruthfulQA's human truthful rate is for the original generation
    setting, not these translations. MC2 YAML metadata version is 2.0 after
    2024-03-11 PR 2768, which stopped assuming labels were sorted.
dataset:
  size: 23586
  size_note: >
    datasets-server on alexandrainst/m_truthfulqa (2026-09-08): 31 language
    configs, val only. Counts range from hy 553 to es 789 (original English
    TruthfulQA is 817 questions). Sum of the 31 val splits is 23,586. There is
    no English, Icelandic, or Norwegian config. Features: question,
    mc1_targets_choices, mc2_targets_choices, mc1_targets_labels,
    mc2_targets_labels. An Arabic sample had four MC1 choices with labels
    [1,0,0,0], matching the YAML's gold index 0.
  url: "https://huggingface.co/datasets/alexandrainst/m_truthfulqa"
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
  splits: "val only; lm-eval validation_split val, test_split null"
  public_test_set: true
publisher:
  org: "University of Oregon NLP (translations); Alexandra Institute (Hub dump); EleutherAI (lm-eval group)"
  authors:
    - "Viet Dac Lai"
    - "Chien Van Nguyen"
    - "Nghia Trung Ngo"
    - "Thuat Nguyen"
    - "Franck Dernoncourt"
    - "Ryan A. Rossi"
    - "Thien Huu Nguyen"
  url: "https://github.com/nlp-uoregon/mlmm-evaluation"
paper:
  title: "Okapi: Instruction-tuned Large Language Models in Multiple Languages with Reinforcement Learning from Human Feedback"
  arxiv: "2307.16039"
  url: "https://arxiv.org/abs/2307.16039"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/okapi/truthfulqa_multilingual"
released: "2023-07"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: "truthfulqa"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No live multilingual TruthfulQA board was opened. English TruthfulQA has
    been a public leaderboard staple since 2021; these copies were not scored
    here on current models. MC1 and MC2 are not interchangeable.
contamination:
  risk: high
  note: >
    English questions and keys have been public since 2021. This dump is public
    val with labels. should_decontaminate is True in the YAML, using the
    question as the decontamination query, which only helps if the runner
    actually filters training overlap.
harness:
  lm_eval: "truthfulqa_multilingual"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "per-language truthfulqa_{lang}_mc1 and truthfulqa_{lang}_mc2; dataset alexandrainst/m_truthfulqa"
tags:
  - safety
  - truthfulness
  - multiple-choice
  - multilingual
  - machine-translation
sources:
  - url: "https://arxiv.org/abs/2307.16039"
    title: "Okapi paper (arXiv 2307.16039)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.16039"
    title: "Okapi paper HTML (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/nlp-uoregon/mlmm-evaluation"
    title: "nlp-uoregon/mlmm-evaluation README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/truthfulqa_multilingual/README.md"
    title: "lm-eval okapi/truthfulqa_multilingual README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/truthfulqa_multilingual/_truthfulqa_mc1_yaml"
    title: "lm-eval TruthfulQA MC1 template"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/truthfulqa_multilingual/_truthfulqa_mc2_yaml"
    title: "lm-eval TruthfulQA MC2 template"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/okapi/truthfulqa_multilingual/utils.py"
    title: "lm-eval TruthfulQA multilingual utils.py"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/alexandrainst/m_truthfulqa"
    title: "alexandrainst/m_truthfulqa dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/alexandrainst/m_truthfulqa"
    title: "alexandrainst/m_truthfulqa API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=alexandrainst/m_truthfulqa"
    title: "datasets-server info for m_truthfulqa"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=truthfulqa/truthful_qa"
    title: "datasets-server info for truthfulqa/truthful_qa (817 val)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model is asked a short question that humans often answer with a myth, then must assign more mass to a true option than to false ones. That is the TruthfulQA skill: resist imitative falsehoods, not recall a textbook fact. The Hub files are GPT-3.5-turbo translations of those English questions and choice lists, one val split per language.

The Okapi paper evaluated ARC, HellaSwag, and MMLU, not TruthfulQA. The lm-eval README still cites that paper because Oregon released the translation through the same mlmm-evaluation repo. Treat this as a sibling dump, not a table in 2307.16039.

## How it is scored

MC1 is accuracy on a single best answer. YAML sets `doc_to_target: 0`, i.e. the first choice, which matched the Arabic sample's `mc1_targets_labels` of `[1,0,0,0]`. MC2 is the normalised probability mass on every choice labelled true, implemented in `process_results_mc2`. Both YAML metrics are named `acc`. MC2 metadata version is 2.0 after March 2024 PR 2768; older MC2 numbers that assumed sorted labels are not comparable.

`utils.py` prepends a fixed English six-example QA prompt (US life expectancy, 1955 president, and so on) before the translated question. Non-English items therefore see an English few-shot prefix.

English TruthfulQA's human figure is for the original generation setting. It was not measured on these translations.

## Dataset and licence

Hub card: CC-BY-NC-4.0. Original TruthfulQA is Apache-2.0. 31 val configs, 553–789 rows (Armenian lowest, Spanish 789), summing to 23,586. Original English set is 817, so every language dropped items. No `en` config. README task list is `truthfulqa_{lang}`; actual YAML names append `_mc1` or `_mc2`.

## Who publishes it

Translations: University of Oregon NLP (Okapi authors as on arXiv 2307.16039). Hub host: Alexandra Institute, lastModified 2023-12-27. Harness: EleutherAI `okapi/truthfulqa_multilingual`. Original TruthfulQA: Lin, Hilton, Evans. The English generation judges are not used here.

## Lineage

Predecessor is [truthfulqa](truthfulqa.md). Languages are Okapi's 26 plus Basque, Gujarati, Armenian, Portuguese, and Swedish (and Chinese is present here even though the HellaSwag lm-eval group dropped it). Sister groups: [okapi_hellaswag_multilingual](okapi_hellaswag_multilingual.md), [okapi_mmlu_multilingual](okapi_mmlu_multilingual.md). This is not a TruthfulQA generation + GPT-judge run.

## Saturation and contamination

No current multilingual top score was read. English TruthfulQA keys have been public since 2021 and sat on the old Open LLM Leaderboard, so leakage into training is likely. YAML sets `should_decontaminate: True` on the question string; that only matters if the eval run actually applies the filter.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks truthfulqa_multilingual
```

That tag pulls both MC1 and MC2 for every language. A single cell is `truthfulqa_vi_mc2`. Directory is `okapi/truthfulqa_multilingual`. Do not compare MC1 to English generation "truthful" rates or to MC2.

## Reading the numbers

A high MC2 means the model put probability on the translated true strings, not that it would refuse a myth in free conversation. The English few-shot prefix can pull the model back into English behaviour. Dropped items (817 down to as few as 553) may have been the hardest translations. Report MC1 or MC2, the language, and whether decontamination ran.
