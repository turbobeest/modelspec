---
id: global_mmlu
name: "Global-MMLU"
aliases:
  - "Global MMLU"
  - "CohereLabs/Global-MMLU"
  - "CohereForAI/Global-MMLU"
page_kind: benchmark
category: knowledge
subcategory: "MMLU translated into 42 languages with cultural-sensitivity labels"
status: active
summary: "MMLU's questions in 42 languages, with CS/CA labels on 2,850 items per language; lm-eval ships Lite (15 languages) and full groups."
measures: >
  Global-MMLU tests whether MMLU-style four-choice academic knowledge holds
  after translation, and whether scores move when items need cultural,
  regional, or dialect knowledge. Each language config repeats the MMLU
  question set (14,042 test and 285 dev rows on Hugging Face, matching the
  cais/mmlu mirror used on the [MMLU](mmlu.md) page). A 2,850-question subset
  per language is labelled culturally sensitive (CS) or culturally agnostic
  (CA). The paper finds 28% of questions need culturally sensitive knowledge,
  and 84.9% of geographic items focus on North America or Europe. Translations
  mix professional post-edits (14 languages, including OpenAI MMMLU where
  available), community translations (11), and machine translation (16), plus
  English. This is not a native-exam suite such as [ArabicMMLU](arabic_mmlu.md)
  or [GreekMMLU](greekmmlu.md).
task_format: >
  Four-option multiple choice (A–D). lm-eval prompts
  "{question}\\nA. ...\\nAnswer:" and scores accuracy on the letter.
  Lite groups (`global_mmlu_{lang}`) load CohereLabs/Global-MMLU-Lite; full
  groups (`global_mmlu_full_{lang}`) load CohereLabs/Global-MMLU. YAML sets
  fewshot_split to dev but does not pin a shot count.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four options, so uniform chance is 25%. No human-rater baseline was read
    in the paper HTML or dataset card. Report CS versus CA and language,
    not only a 42-language mean.
dataset:
  size: 14042
  size_note: >
    Hugging Face CohereLabs/Global-MMLU: 42 configs, each with test 14,042 and
    dev 285 (API dataset_info, lastModified 2025-08-14). The 14,042 figure
    matches the cais/mmlu test count on the MMLU page, not the original paper's
    14,079. Paper and lm-eval Lite groups use 15 languages. Hugging Face
    Global-MMLU-Lite v3.0 (May 2026) lists 23 language configs, typically test
    400 (200 CS + 200 CA) and dev 215 (not every config: cs has dev 285; cy
    is test-only). Cultural labels cover 2,850 questions per language on the
    full set. Do not multiply 14,042 by 42 as unique English items; they are
    translations of the same questions.
  url: "https://huggingface.co/datasets/CohereLabs/Global-MMLU"
  license: "Apache-2.0"
  languages:
    - en
    - ar
    - bn
    - es
    - fr
    - hi
    - ru
    - de
    - id
    - it
    - ja
    - ko
    - pt
    - zh
    - yo
    - nl
    - ro
    - uk
    - vi
    - tr
    - pl
    - fa
    - cs
    - he
    - el
    - ms
    - fil
    - te
    - si
    - ne
    - ky
    - sv
    - lt
    - sr
    - mg
    - so
    - ha
    - am
    - sn
    - ig
    - ny
    - sw
  modalities:
    - text
  splits: "per-language `dev` (285) and `test` (14,042) on the full set; original Lite typically `dev` (215) and `test` (400); HF Lite v3.0 has 23 configs"
  public_test_set: true
publisher:
  org: "Cohere Labs (Cohere For AI), with EPFL, Hugging Face, Mila/McGill, AI Singapore, NUS, MIT, KAIST, and other collaborators named on the paper"
  authors:
    - "Shivalika Singh"
    - "Angelika Romanou"
    - "Clémentine Fourrier"
    - "David I. Adelani"
    - "Jian Gang Ngui"
    - "Daniel Vila-Suero"
    - "Peerat Limkonchotiwat"
    - "Kelly Marchisio"
    - "Wei Qi Leong"
    - "Yosephine Susanto"
    - "Raymond Ng"
    - "Shayne Longpre"
    - "Wei-Yin Ko"
    - "Sebastian Ruder"
    - "Madeline Smith"
    - "Antoine Bosselut"
    - "Alice Oh"
    - "Andre F. T. Martins"
    - "Leshem Choshen"
    - "Daphne Ippolito"
    - "Enzo Ferrante"
    - "Marzieh Fadaee"
    - "Beyza Ermis"
    - "Sara Hooker"
  url: "https://huggingface.co/datasets/CohereLabs/Global-MMLU"
paper:
  title: "Global MMLU: Understanding and Addressing Cultural and Linguistic Biases in Multilingual Evaluation"
  arxiv: "2412.03304"
  url: "https://arxiv.org/abs/2412.03304"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/global_mmlu"
released: "2024-12"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    English [MMLU](mmlu.md) is saturated at the frontier, but no current
    Global-MMLU leaderboard top cell was read here. Rankings in the paper
    change between the full set and the CS subset.
contamination:
  risk: high
  note: >
    Items are translations of public MMLU questions whose answers have been
    online since 2020. Full and Lite dumps are public on Hugging Face under
    Apache-2.0. Translation reduces some English leakage but does not hide
    the answer key. No source opened here measured memorisation of the
    translated strings.
harness:
  lm_eval: "global_mmlu_{lang} (Lite, 15 language dirs); global_mmlu_full_{lang} (42 languages)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-eval README says the Lite group supports 14 languages; the default/
    directory listing opened here has 15 language folders including English
    (ar, bn, de, en, es, fr, hi, id, it, ja, ko, pt, sw, yo, zh). That is
    the original Lite set. Hugging Face Global-MMLU-Lite v3.0 (May 2026)
    adds further languages not present in those lm-eval dirs. Full subgroups
    include global_mmlu_full_stem, global_mmlu_full_humanities,
    global_mmlu_full_social_sciences, global_mmlu_full_other. Dataset cards
    also exist under the older CohereForAI namespace in the paper PDF.
tags:
  - knowledge
  - multilingual
  - multiple-choice
  - mmlu
  - cultural-sensitivity
  - translation
sources:
  - url: "https://arxiv.org/abs/2412.03304"
    title: "Global MMLU paper (arXiv:2412.03304), submitted 4 Dec 2024, v2 19 Feb 2025"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2412.03304"
    title: "Paper HTML (42 languages, 28% CS, 2,850 annotated, MMMLU overlap)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CohereLabs/Global-MMLU/raw/main/README.md"
    title: "CohereLabs/Global-MMLU card (Apache-2.0, 14K test, 2,850 CS/CA labels)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CohereLabs/Global-MMLU"
    title: "HF API: 42 configs, test 14042 / dev 285, lastModified 2025-08-14"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CohereLabs/Global-MMLU-Lite/raw/main/README.md"
    title: "Global-MMLU-Lite card (15 languages, 200 CS + 200 CA test)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=CohereLabs/Global-MMLU-Lite"
    title: "datasets-server Lite split counts (test 400 / dev 215 per language)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/global_mmlu/README.md"
    title: "lm-eval global_mmlu README (Lite vs full groups; paper citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/global_mmlu/default/en/_en_template_yaml"
    title: "Lite English template (CohereLabs/Global-MMLU-Lite, acc, A–D)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/global_mmlu/default/en/_global_mmlu_en.yaml"
    title: "Group global_mmlu_en (six subject buckets, acc weighted by size)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-045 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-045"
---

## What it measures

Global-MMLU is MMLU in 42 languages, not a new native exam. Each language config asks the same four-choice academic questions after translation or, for English, in the original. Cohere Labs and collaborators labelled 2,850 items per language as culturally sensitive or culturally agnostic so a score can be split when geography, law, or custom is required. The paper's claim is that translated MMLU over-weights Western facts (28% CS; 84.9% of geographic items about North America or Europe) and that machine translation adds artefacts. [MMMLU](mmmlu.md) is OpenAI's 14-language professional translation of the same English test; Global-MMLU reuses those translations where they exist and adds more languages.

## How it is scored

lm-eval reports accuracy on letters A–D. Lite groups `global_mmlu_{lang}` load Global-MMLU-Lite (400 test items, balanced CS/CA). Full groups `global_mmlu_full_{lang}` load the 14,042-item test set. Subject buckets on Lite English are business, humanities, medical, other, STEM, and social sciences; full subgroups include stem, humanities, social_sciences, and other. YAML points few-shot examples at `dev` but does not set a shot count, so published numbers must name the shot setting. Compare CS versus CA, and human-translated languages versus machine-translated ones, before an overall mean.

## Dataset and licence

Full Hugging Face configs: 42 languages, test 14,042, dev 285, Apache-2.0, last modified 2025-08-14 in the API blob opened here. The paper's Lite slice and lm-eval `default/` groups cover 15 languages (400 test items, balanced CS/CA). Hugging Face Global-MMLU-Lite v3.0 (May 2026) lists 23 language configs and is not the same as that harness group. The 14,042 test count matches the cais/mmlu mirror, not Hendrycks et al.'s 14,079. Paper translation mix: professional post-edits for 14 languages, community for 11, machine for 16, plus English. Older paper URLs use the CohereForAI namespace; the cards opened here are CohereLabs.

## Who publishes it

Shivalika Singh, Angelika Romanou, Clémentine Fourrier, and 21 further co-authors (arXiv:2412.03304, 4 December 2024; v2 19 February 2025). Cohere Labs leads; affiliations on the HTML include EPFL, Hugging Face, Mila/McGill, AI Singapore, NUS, MIT, and KAIST. No separate live leaderboard URL was opened.

## Lineage

Predecessor is [MMLU](mmlu.md). [MMMLU](mmmlu.md) is a related 14-language professional translation, not this 42-language set with CS/CA labels. [ArabicMMLU](arabic_mmlu.md) and [GreekMMLU](greekmmlu.md) are native-sourced exams, not Global-MMLU language configs. [MMLU-Pro](mmlu_pro.md) is a harder English successor, not a multilingual translation.

## Saturation and contamination

English MMLU is saturated at the frontier, but this page did not read a current Global-MMLU top cell, so saturation is left unknown. Public translated MMLU with a public answer key is high contamination risk. The CS subset is the more informative slice when English leakage is a concern, and even that key is public.

## How to run it

In lm-evaluation-harness, `global_mmlu_en` (and the other 14 Lite language groups under `default/`) run the original 15-language Lite. `global_mmlu_full_{lang}` runs all 42 languages. Do not treat the README's "14 languages" Lite line as the file tree: `default/` has 15 folders including `en`. Hugging Face Lite v3.0's extra languages are not those groups. Always name Lite versus full, language, CS/CA, and shot count.

## Reading the numbers

A high Global-MMLU mean can be English MMLU knowledge plus translation quality, not local curriculum knowledge. Native suites such as ArabicMMLU answer a different question. Lite's 400 items are a balanced CS/CA probe, not the 14k test set. Name whether you used the original 15-language Lite (lm-eval `default/`) or Hugging Face Lite v3.0's 23 configs. Machine-translated full-set languages are weaker evidence than human-translated ones. Quote the Hugging Face org (CohereLabs versus older CohereForAI links) and the 14,042 versus 14,079 MMLU test-count gap when comparing to English MMLU.
