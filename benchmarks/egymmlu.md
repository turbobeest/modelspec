---
id: egymmlu
name: "EgyMMLU"
aliases:
  - "Egy MMLU"
  - "UBC-NLP/EgyMMLU"
page_kind: benchmark
category: knowledge
subcategory: "Egyptian Arabic multitask multiple-choice (44 subjects translated from MMLU and ArabicMMLU)"
status: active
summary: "Egyptian Arabic multiple-choice exam of 22,027 items across 44 subjects, translated from MMLU and ArabicMMLU."
measures: >
  EgyMMLU tests whether a model can answer multiple-choice questions written in
  Egyptian Arabic. The 44 subjects mix English MMLU topics (for example
  professional_law, moral_scenarios) with ArabicMMLU topics (islamic_studies,
  driving_test, arabic_language). Some items include a context passage. The
  skill is dialectal exam QA, not a from-scratch Egyptian curriculum. It is
  not native [ArabicMMLU](arabic_mmlu.md) and not English [MMLU](mmlu.md).
task_format: >
  Multiple-choice with lettered options A-E as needed. lm-eval builds an
  Egyptian-Arabic prompt from egy_subject, optional context, question, and
  choices. Target is the integer answer index mapped to a letter. Group
  egymmlu aggregates size-weighted acc across subjects.
metric:
  name: "accuracy (acc), size-weighted across subjects in group egymmlu"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option count varies with the source item (MMLU is four-option; ArabicMMLU
    uses 2-5). No published random or human-taker baseline for the Egyptian
    text. NileChat Table 1 reports model accuracy, not a human exam score.
dataset:
  size: 22027
  size_note: >
    lm-eval README and the NileChat-linked card state 22,027 questions in 44
    subjects. Hugging Face per-config sums (datasets-server 2026-09-08):
    21,792 test + 235 dev = 22,027. Subject test sizes range from 39
    (philosophy_ar) to 2,210 (islamic_studies). Dev rows are few-shot seeds
    (3, 5, 6, 9, or 12 per subject).
  url: "https://huggingface.co/datasets/UBC-NLP/EgyMMLU"
  license: "MIT"
  languages:
    - arz
  modalities:
    - text
  splits: "per-subject dev (few-shot) and test; group egymmlu scores test, first_n few-shot from dev"
  public_test_set: true
publisher:
  org: "UBC-NLP (University of British Columbia)"
  authors:
    - "Abdellah El Mekki"
    - "Houdaifa Atou"
    - "Omer Nacar"
    - "Shady Shehata"
    - "Muhammad Abdul-Mageed"
  url: "https://huggingface.co/datasets/UBC-NLP/EgyMMLU"
paper:
  title: "NileChat: Towards Linguistically Diverse and Culturally Aware LLMs for Local Communities"
  arxiv: "2505.18383"
  url: "https://arxiv.org/abs/2505.18383"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/egymmlu"
released: "2025-05"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: "mmlu"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    English MMLU is saturated at the frontier. NileChat Table 1 gives zero-shot
    EGY MMLU for small models (Qwen3-1.7B 28.53, ar-stablelm-2-chat 41.56). No
    current frontier aggregate was read. Leave saturation unknown.
contamination:
  risk: high
  note: >
    Source English MMLU and public ArabicMMLU items are widely used in training
    corpora. This release is a public machine translation of those items.
    ArabicMMLU's own licence is more restrictive than MIT (see Dataset). No
    measured leakage rate for the Egyptian strings was opened.
harness:
  lm_eval: "egymmlu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group egymmlu aggregates egymmlu_mmlu and egymmlu_ar_mmlu. Subject tasks are
    egymmlu_<subject>. Tags include egymmlu_stem, egymmlu_social_sciences,
    egymmlu_humanities, egymmlu_language, egymmlu_other.
tags:
  - egyptian-arabic
  - multiple-choice
  - mmlu
  - translation
  - knowledge
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egymmlu/README.md"
    title: "lm-eval EgyMMLU README (22,027 items, 44 subjects, gemma-3-27b-it)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egymmlu/_egymmlu.yaml"
    title: "group egymmlu (size-weighted acc over mmlu and ar_mmlu subgroups)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egymmlu/_default_egymmlu_template_yaml"
    title: "default template (UBC-NLP/EgyMMLU, test + first_n few-shot from dev)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/egymmlu/utils.py"
    title: "Egyptian-Arabic multiple-choice prompt helper"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/UBC-NLP/EgyMMLU"
    title: "UBC-NLP/EgyMMLU card (arz; MIT link to hendrycks/test)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=UBC-NLP/EgyMMLU"
    title: "datasets-server (44 configs; 21792 test + 235 dev)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.18383"
    title: "NileChat (arXiv:2505.18383)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2505.18383"
    title: "NileChat HTML (translation pipeline and Table 1 EGY MMLU)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.emnlp-main.556/"
    title: "NileChat ACL Anthology (EMNLP 2025)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Original MMLU paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-040 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-040"
---

## What it measures

EgyMMLU is a 44-subject multiple-choice exam in Egyptian Arabic. Roughly half the subjects are translated English [MMLU](mmlu.md) topics. The rest come from [ArabicMMLU](arabic_mmlu.md), including Islamic studies, driving tests, and Arabic language. The model must pick the gold option in Masri. It does not add new Egyptian-written exam items. It is not [egyhellaswag](egyhellaswag.md).

## How it is scored

lm-eval group `egymmlu` reports size-weighted `acc` over all subject tasks. Subgroups `egymmlu_mmlu` and `egymmlu_ar_mmlu` split by source. Category tags cover STEM, social sciences, humanities, language, and other. The prompt is Egyptian Arabic. Few-shot uses `first_n` rows from each subject's `dev` split. NileChat Table 1 is zero-shot; Appendix D is 3-shot. Do not average those two.

## Dataset and licence

Hub configs sum to 22,027 rows: 21,792 test and 235 dev. That matches the lm-eval README total. Largest test subject is islamic_studies (2,210); smallest is philosophy_ar (39). The card claims MIT and links `hendrycks/test`. ArabicMMLU, one of the two sources, is published as CC-BY-NC-SA-4.0 on GitHub and cc-by-nc-4.0 on its Hub card. This page records MIT as the EgyMMLU card statement and flags the source-licence clash.

## Who publishes it

The same NileChat authors (UBC-NLP) released EgyMMLU with EgyHellaSwag (arXiv:2505.18383, EMNLP 2025). The Hub dataset was created 2025-05-24. EleutherAI lm-eval is the public runner.

## Lineage

Predecessor pages in this repo are [mmlu](mmlu.md) and [arabic_mmlu](arabic_mmlu.md). EgyMMLU is not an MMLU subject subset. Moroccan MMLU in NileChat uses Shang et al. (2025) and has no page here. Do not fold this id into `mmlu` scores.

## Saturation and contamination

English MMLU no longer separates frontier models. This dialect translation still might, but no recent leaderboard cell was read. Source items are old and public, so contamination of the underlying facts is likely. Translation errors are a separate ceiling: NileChat Appendix C scores sampled EgyMMLU items on 1–5 correctness and dialectness.

## How to run it

```
lm_eval --model hf --model_args pretrained=<model> --tasks egymmlu
```

Subject tasks are `egymmlu_<subject>` (for example `egymmlu_biology`). The translator named in the harness README (`google/gemma-3-27b-it`) disagrees with the paper (Command R+ following Shang et al.). Record which note you follow. Few-shot shot count must be stated.

## Reading the numbers

A high `egymmlu` mean means the model picked gold letters on these translated items, weighted toward large subjects such as islamic_studies and professional_law. It is not a native Egyptian school exam. Compare with English MMLU, ArabicMMLU, and EgyHellaSwag rather than treating one number as dialect competence.
