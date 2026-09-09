---
id: arabculture
name: "ArabCulture"
aliases:
  - "Arab Culture"
  - "arab_culture"
  - "ArabicCulture"
  - "MBZUAI/ArabCulture"
page_kind: benchmark
category: reasoning
subcategory: "native MSA cultural commonsense, 13 countries, 3-way MCQ"
status: active
summary: "3,482 native Modern Standard Arabic three-choice commonsense items across 13 countries; lm-eval group arab_culture, not translated English CSQA."
measures: >
  ArabCulture tests whether a model can finish a culturally grounded commonsense
  statement written in Modern Standard Arabic. Native speakers from 13 countries
  wrote the items. They cover 12 daily-life domains and 54 subtopics (social norms,
  food, family, and similar), not school-exam facts. Each item is three-way
  multiple choice. The countries sit in four regions: Gulf (KSA, UAE, Yemen),
  Levant (Lebanon, Syria, Palestine, Jordan), North Africa (Tunisia, Algeria,
  Morocco, Libya), and Nile Valley (Egypt, Sudan). It is not a translation of
  English commonsense sets and not [arabic_mmlu](arabic_mmlu.md).
task_format: >
  Three-option MCQ in MSA. lm-eval's arab_culture path ranks choice letters by
  log-likelihood (A/B/C or أ/ب/ج). A completion variant concatenates each option
  to the stem. Optional English vs Arabic prompt wrappers and optional region or
  country context are toggled with COUNTRY, REGION, and ARABIC environment variables.
metric:
  name: "accuracy (acc; lm-eval also reports acc_norm); size-weighted mean across country tasks"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three options per item, so chance is 1/3 if options are balanced. The paper
    reports no human-solver baseline. Table 3 (English prompt, MCQ) puts GPT-4o
    at 88.5% with no location, 89.6% with region, and 90.0% with region plus
    country. Open-weight models up to 32B are described as struggling.
dataset:
  size: 3482
  size_note: >
    Paper and Hugging Face country configs both total 3,482 test items: Algeria
    271, Egypt 265, Jordan 290, KSA 261, Lebanon 255, Libya 239, Morocco 276,
    Palestine 273, Sudan 256, Syria 279, Tunisia 261, UAE 283, Yemen 273. One
    test split per country; no train split. Table 2 of the paper also reports
    country-specific vs shared-culture shares.
  url: "https://huggingface.co/datasets/MBZUAI/ArabCulture"
  license: "CC-BY-NC-SA-4.0"
  languages:
    - ar
  modalities:
    - text
  splits: "per-country test only (13 Hugging Face configs named by country)"
  public_test_set: true
publisher:
  org: "MBZUAI, with SDAIA, Al-Balqa Applied University, and Khalifa University"
  authors:
    - "Abdelrahman Sadallah"
    - "Junior Cedric Tonga"
    - "Khalid Almubarak"
    - "Saeed Almheiri"
    - "Farah Atif"
    - "Chatrine Qwaider"
    - "Karima Kadaoui"
    - "Sara Shatnawi"
    - "Yaser Alesh"
    - "Fajri Koto"
  url: "https://huggingface.co/datasets/MBZUAI/ArabCulture"
paper:
  title: "Commonsense Reasoning in Arab Culture"
  arxiv: "2502.12788"
  url: "https://arxiv.org/abs/2502.12788"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arab_culture"
released: "2025-02"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 90.0
  as_of: "2025-02"
  note: >
    Paper Table 3, English MCQ, GPT-4o with region and country in the prompt:
    90.0%. That is the strongest figure read here, not a 2026 live leaderboard.
    Three-way chance is 33%. Open-weight 32B-class models in the same table sit
    well below GPT-4o, so the set still separates models.
contamination:
  risk: medium
  note: >
    Items and keys have been on Hugging Face since 12 December 2024 (card
    lastModified 23 May 2025) under CC-BY-NC-SA-4.0. They were written by hired
    native speakers rather than translated from English CSQA, which lowers the
    chance they sat in older English crawls. They are still public test labels.
harness:
  lm_eval: "arab_culture"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Region groups arab_culture_gulf, arab_culture_levant, arab_culture_nile_valley, arab_culture_north_africa; country tasks arab_culture_{egypt,ksa,...}. README also names group arabculture and a completion variant arab_culture_completion; the YAML group field is arab_culture."
tags:
  - arabic
  - commonsense
  - culture
  - multiple-choice
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2502.12788"
    title: "Commonsense Reasoning in Arab Culture (arXiv:2502.12788, submitted 18 Feb 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.12788"
    title: "ArabCulture paper HTML (3,482 items, 13 countries, Table 3 GPT-4o 90.0%)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI/ArabCulture"
    title: "MBZUAI/ArabCulture dataset card (CC-BY-NC-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI/ArabCulture"
    title: "Hugging Face dataset API (per-country test counts summing to 3,482)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=MBZUAI/ArabCulture"
    title: "datasets-server size for MBZUAI/ArabCulture"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/README.md"
    title: "lm-eval arab_culture README (groups, MCQ vs completion, env flags)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/_arab_culture.yaml"
    title: "YAML group arab_culture (acc, weight_by_size true)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/_default_arab_culture_mcq_template_yaml"
    title: "MCQ template (dataset_path MBZUAI/ArabCulture, acc and acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/utils_mcq.py"
    title: "utils_mcq.py (3 options; COUNTRY/REGION/ARABIC env flags)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/_generate_configs.py"
    title: "Country-to-region map used to generate per-country YAMLs"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arab_culture/arab_culture_egypt.yaml"
    title: "Example country task arab_culture_egypt"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

ArabCulture is a three-choice commonsense test in Modern Standard Arabic. The model sees a short culturally specific stem and three continuations. The right choice depends on everyday knowledge in one of 13 Arab countries, not on translated English trivia. Native speakers wrote and checked the items. The paper frames two protocols: letter-ranked multiple choice, and a completion setup that scores each option as a continuation.

The assigned wiki id is `arabculture`. The lm-eval YAML group is `arab_culture`. The README also lists a group named `arabculture`; that string is not the `group:` field in `_arab_culture.yaml`.

## How it is scored

lm-eval reports `acc` and `acc_norm`, then a size-weighted mean across the four region groups. Chance is one in three. The paper's main table uses English prompt text and varies location context: none, region only, or region plus country. English prompts beat Arabic prompts for most models they tried. GPT-4o reached 90.0% MCQ with region and country in the English prompt (Table 3). No human-solver accuracy is published.

Prompt flags are environment variables. `utils_mcq.py` sets COUNTRY, REGION, and ARABIC to true only when the env value is the string `"True"`. An unset variable therefore yields all-false (no location, English choice letters), which is easy to miss if you expect Python-truthy defaults.

## Dataset and licence

3,482 test items, matching the paper and the sum of the 13 Hugging Face configs. Hugging Face tags the dataset `cc-by-nc-sa-4.0`. Answers are public. The lm-eval README points at github.com/fajri91/ArabicCulture; that URL returned 404 on 2026-09-08. Use the Hugging Face card as the dataset home.

Workers had to be native speakers who had lived in the country for at least ten years, with parents from that country. Authors did a second pass to mark items that were country-specific versus shared.

## Who publishes it

Sadallah, Tonga, Almubarak, Almheiri, Atif, Qwaider, Kadaoui, Shatnawi, Alesh and Koto. Affiliations on the paper and card include MBZUAI, SDAIA, Al-Balqa Applied University and Khalifa University. arXiv:2502.12788, submitted 18 February 2025. Hugging Face createdAt is 12 December 2024; lastModified 23 May 2025.

## Lineage

This is not [arabic_mmlu](arabic_mmlu.md) (native exam questions) and not [mmluarabic](mmluarabic.md) (translated MMLU). [aradice](aradice.md) has a small native cultural slice (the paper's comparison table lists AraDiCE-Culture at 180 items) plus translated English NLU. ArabCulture is the larger from-scratch cultural commonsense set. It is not [alghafa](alghafa.md).

## Saturation and contamination

GPT-4o's 90% English MCQ reading still leaves headroom, and smaller open models in the paper sit far lower. Labels have been public since late 2024. Because the text is original MSA, English-only memorisation is a weaker story than for translated CSQA, but the test set is not held out.

## How to run it

`lm_eval --tasks arab_culture` runs the four region groups. Per-country names look like `arab_culture_egypt`. Do not pass the census spelling `ArabCulture` as a task directory; that path 404s. Set `ARABIC=True` for Arabic wrappers and letters; set `REGION=True` and `COUNTRY=True` together if you want location in the prompt (country without region asserts). Compare only runs that match prompt language and location flags.

## Reading the numbers

A high score means the model ranked the culturally correct continuation on these MSA stems, under one prompt language and one location setting. It is not a general Arabic exam score and not a dialect-understanding score (items are MSA). Report English vs Arabic prompts separately. The 90% GPT-4o figure is one paper cell, not a live leaderboard.
