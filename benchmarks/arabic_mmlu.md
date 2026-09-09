---
id: arabic_mmlu
name: "ArabicMMLU"
aliases:
  - "Arabic MMLU"
  - "MBZUAI/ArabicMMLU"
page_kind: benchmark
category: knowledge
subcategory: "native Modern Standard Arabic multitask exam QA (40 subjects, not a translation of English MMLU)"
status: active
summary: "14,575 native Arabic multiple-choice exam questions across 40 subjects, sourced from school and professional tests in eight countries rather than translated from English MMLU."
measures: >
  ArabicMMLU tests whether a model can answer multiple-choice questions written in Modern Standard
  Arabic and drawn from real school, university and professional exams across North Africa, the Levant
  and the Gulf. The 40 subjects span STEM, social science, humanities, Arabic language, and an "other"
  group that includes driving tests and general knowledge. The authors built it because Arabic LLM
  papers had been scoring models on English MMLU translated into Arabic, which cannot test
  Arabic-specific history, law, civics or driving content. Over half the items are described as
  tailored to Arabic-speaking contexts.
task_format: >
  Multiple-choice question answering in Modern Standard Arabic, with 2 to 5 options and one correct
  answer. Some items, especially Arabic Language (General), include a reading-passage Context field.
  The original paper scores open models by first-token letter probability (A-E as needed) and closed
  models by a regex on the first generated token. HELM instead uses joint multiple-choice generation
  with Arabic instruction text and Arabic option letters (أ ب ج د هـ), scored by exact_match.
metric:
  name: "accuracy (paper); exact_match (HELM)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 29.0
  human_baseline: null
  baseline_note: >
    The paper's Table 4 reports a measured random baseline of 29.0% average accuracy (25.8% to 32.3%
    by subject group), above a naive four-option 25% because option count varies from 2 to 5. Two
    native annotators checking 100 random items with the answer key found 96% of keys correct; the
    authors treat 96% as the maximum score the benchmark can meaningfully support, not as a human
    exam-taker baseline.
dataset:
  size: 14575
  size_note: >
    14,575 unique questions, matching both the paper and the Hugging Face `All` config
    (14,455 test + 120 dev). Summing every per-subject config plus `All` yields 29,150 rows because
    `All` duplicates the 40 subject configs; this page uses 14,575. The paper says the set was
    filtered down from more than 15,000 collected items. Subject sizes on the datasets-server range
    from 30 (Arabic Language (Middle School), Computer Science (Middle School)) to 1,412 (Biology
    (High School)).
  url: "https://huggingface.co/datasets/MBZUAI/ArabicMMLU"
  license: >
    The GitHub README states Creative Commons Attribution-NonCommercial-ShareAlike 4.0; the Hugging
    Face card tag is cc-by-nc-4.0. The paper PDF does not state a licence. This page leaves the SPDX
    id unset rather than picking one of those two readings.
  languages:
    - ar
  modalities:
    - text
  splits: "per-subject `dev` and `test`, plus an `All` aggregate (14,455 test / 120 dev); HELM maps Hugging Face `dev` to its train split for in-context examples"
  public_test_set: true
publisher:
  org: "Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), with Prince Sattam bin Abdulaziz University, KFUPM, Core42, NYU Abu Dhabi and the University of Melbourne"
  authors:
    - "Fajri Koto"
    - "Haonan Li"
    - "Sara Shatnawi"
    - "Jad Doughman"
    - "Abdelrahman Boda Sadallah"
    - "Aisha Alraeesi"
    - "Khalid Almubarak"
    - "Zaid Alyafeai"
    - "Neha Sengupta"
    - "Shady Shehata"
    - "Nizar Habash"
    - "Preslav Nakov"
    - "Timothy Baldwin"
  url: "https://github.com/mbzuai-nlp/ArabicMMLU"
paper:
  title: "ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic"
  arxiv: "2402.12840"
  url: "https://arxiv.org/abs/2402.12840"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/mbzuai-nlp/ArabicMMLU"
released: "2024-02"
last_updated: "2024-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - madinah_qa
saturation:
  status: open
  top_score: 72.5
  as_of: "2024-02"
  note: >
    The paper's own zero-shot Table 4 gives GPT-4 (gpt-4-0613) 72.5% average accuracy, 10 points above
    the best open Arabic-centric model, Jais-chat 30B at 62.3%, and well below the authors' 96%
    label-noise ceiling. No later independent top score was read for this page.
contamination:
  risk: high
  note: >
    Questions come from real public exams, the full set with answers has been on GitHub and Hugging
    Face without gating since February 2024, and HELM's scenario metadata dates the content to
    "before 2024." The authors say they cannot assert that GPT-4's pretraining is free of
    contamination. No held-out private split is described.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "arabic_mmlu"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec `arabic_mmlu:subset=<name>` (experimental Arabic leaderboard module). Do not confuse
    this with lm-evaluation-harness `arabic_leaderboard_arabic_mmlu`, which loads OALL/Arabic_MMLU
    (AceGPT's machine-translated English MMLU, subjects such as abstract_algebra), not MBZUAI/ArabicMMLU.
tags:
  - arabic
  - knowledge
  - multiple-choice
  - exam-qa
  - native-language
  - mmlu-style
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/arabic_mmlu_scenario.py"
    title: "HELM ArabicMMLUScenario (loads MBZUAI/ArabicMMLU, pinned revision, exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_run_specs.py"
    title: "HELM arabic_run_specs.py (arabic_mmlu run spec, Arabic letters, exact_match)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI/ArabicMMLU"
    title: "MBZUAI/ArabicMMLU dataset card (40 subjects plus All, licence tag cc-by-nc-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI/ArabicMMLU"
    title: "MBZUAI/ArabicMMLU Hugging Face API (created 2024-02-21, sha 7aa530e, licence tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=MBZUAI/ArabicMMLU"
    title: "MBZUAI/ArabicMMLU datasets-server split sizes (All: 14,455 test / 120 dev)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/mbzuai-nlp/ArabicMMLU/main/README.md"
    title: "mbzuai-nlp/ArabicMMLU README (14,575 questions, 40 tasks, CC BY-NC-SA 4.0 statement, authors)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.12840"
    title: "ArabicMMLU arXiv abstract page (2402.12840)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.12840"
    title: "ArabicMMLU full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2402.12840.pdf"
    title: "ArabicMMLU PDF (Table 4 GPT-4 72.5%, random 29.0%, 96% label check, 2-5 options)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2024.findings-acl.334/"
    title: "ArabicMMLU ACL Anthology page (Findings of ACL 2024)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OALL/Arabic_MMLU"
    title: "OALL/Arabic_MMLU (AceGPT translated MMLU; not this benchmark)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arabic_leaderboard_complete/arabic_leaderboard_arabic_mmlu/arabic_leaderboard_arabic_mmlu_abstract_algebra.yaml"
    title: "lm-eval arabic_leaderboard_arabic_mmlu_abstract_algebra.yaml (dataset_path OALL/Arabic_MMLU)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-005"
---

## What it measures

ArabicMMLU asks a model to pick the correct option on a multiple-choice exam question written in Modern Standard Arabic. The questions come from real school, university and professional tests collected with native speakers, covering eight countries in North Africa, the Levant and the Gulf. Subjects run from primary-school maths and Islamic studies to professional law and driving tests, so a score mixes Arabic reading with local facts rather than one skill.

This is not a translation of English [MMLU](mmlu.md). Arabic-centric models had been scored on English MMLU rendered into Arabic, which cannot test Arabic-specific civics, history or driving content. OpenAI's [MMMLU](mmmlu.md) later translated original MMLU into Arabic by another route; that is still the English item set.

## How it is scored

The paper reports accuracy averaged over all questions. Open models are scored by the probability of the first generated letter (A-E as needed). GPT-3.5 and GPT-4 (gpt-4-0613) are scored by a regex on the first generated token; unmatched outputs get a random letter. Table 4 is zero-shot. Random guessing is 29.0% on average because items have two to five options. Two annotators checking 100 keyed items judged 96% of keys correct; the authors treat 96% as the highest score the set can meaningfully support.

HELM's `arabic_mmlu` scenario loads `MBZUAI/ArabicMMLU` at revision `7aa530e2893ac420352b3f5c1a1310c010e9758b`, prepends any Context passage, and scores joint multiple-choice generation with an Arabic instruction and letters أ ب ج د هـ, using `exact_match` on the test split. That is not the paper's English-prompt, English-letter setup, which the authors found best of four combinations. A HELM number and a paper number are not interchangeable.

## Dataset and licence

14,575 unique questions in 40 subject configs, matching the paper and the Hugging Face `All` config (14,455 test + 120 dev). Summing every config double-counts because `All` repeats the subjects. The authors filtered more than 15,000 collected items down to this unique set. Answers are public. HELM concatenates a Context passage when that field is non-empty.

The GitHub README licences the dataset as CC BY-NC-SA 4.0. The Hugging Face card tag is `cc-by-nc-4.0` (no ShareAlike). The paper PDF does not state a licence. [MadinahQA](madinah_qa.md) redistributes two Arabic-language subjects under CC BY-NC 4.0 on its own card.

## Who publishes it

Fajri Koto, Haonan Li, Sara Shatnawi, Jad Doughman, Abdelrahman Boda Sadallah, Aisha Alraeesi, Khalid Almubarak, Zaid Alyafeai, Neha Sengupta, Shady Shehata, Nizar Habash, Preslav Nakov and Timothy Baldwin, at MBZUAI with Prince Sattam bin Abdulaziz University, KFUPM, Core42, NYU Abu Dhabi and the University of Melbourne. Posted as arXiv:2402.12840 on 21 February 2024 (Hugging Face the same day) and published at Findings of ACL 2024.

## Lineage

ArabicMMLU is an MMLU-style native exam suite, like [CMMLU](cmmlu.md) and [GreekMMLU](greekmmlu.md), not a child of English [MMLU](mmlu.md). [MadinahQA](madinah_qa.md) is the Arabic Language (General) and Grammar subjects released standalone (615 + 368 questions). HELM also registers `mbzuai_human_translated_arabic_mmlu`, a human-translated English-MMLU variant.

Name collisions matter. lm-evaluation-harness `arabic_leaderboard_arabic_mmlu` loads `OALL/Arabic_MMLU`, which that card traces to AceGPT's `MMLUArabic` directory -- English MMLU subjects such as abstract_algebra. This repository's [arabic_leaderboard_complete](arabic_leaderboard_complete.md) README called that group natively sourced; the YAML and card show the translated set, not `MBZUAI/ArabicMMLU`. [Arabic EXAMS](arabic_exams.md) is a different, smaller slice of Hardalov et al.'s EXAMS corpus.

## Saturation and contamination

On the paper's zero-shot English-prompt protocol, GPT-4 reached 72.5% in February 2024, with Jais-chat 30B at 62.3% the strongest open Arabic-centric model tested -- well below the 96% label-noise ceiling. No later public top score was confirmed here. Contamination risk is high: the items are real exams, answers have been downloadable since February 2024, and the authors decline to claim GPT-4 is uncontaminated.

## How to run it

HELM: `arabic_mmlu:subset=<subject>` in the experimental Arabic run-specs module. Underscores in the subset name become spaces to match Hugging Face configs such as `Islamic Studies`. Inspect-evals and OpenCompass implementations were not found at the paths checked. lm-evaluation-harness has no task named `arabic_mmlu`; `arabic_leaderboard_arabic_mmlu` is the AceGPT translation.

Compare numbers only when prompt language, option letters, shot count and Context handling match.

## Reading the numbers

A high score means the model can read MSA exam prose and handle facts from Arabic-speaking school systems, including material absent from English MMLU. It does not measure dialect, and it does not use the same items as MMMLU-ar or AceGPT's translated MMLU. HELM scores generated Arabic letters; the paper's headline table is zero-shot option ranking under an English prompt -- name the harness before comparing. Given public keys, an unusually high score on a model trained after early 2024 needs a second, less exposed Arabic knowledge set.
