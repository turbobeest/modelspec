---
id: cabbq
name: "CaBBQ (Catalan Bias Benchmark for Question Answering)"
aliases:
  - "Catalan Bias Benchmark for Question Answering"
  - "Catalan BBQ"
page_kind: benchmark
category: safety
subcategory: "social bias in Catalan question answering"
status: active
summary: "Catalan multiple-choice QA, parallel with EsBBQ, testing stereotype use under ambiguous context and accuracy once the context names the answer."
measures: >
  CaBBQ asks whether a model falls back on stereotypes about groups in Spain
  when a Catalan context is under-informative, and whether it can ignore that
  stereotype once a disambiguating sentence is added. Each item has a context,
  a question, and three answers (two groups plus an unknown option). Ten
  categories cover age, disability, gender, LGBTQIA, nationality, appearance,
  race/ethnicity, religion, SES, and Spanish region. It is a cultural
  adaptation of English BBQ, not a translation-only copy.
task_format: >
  Three-way multiple-choice QA in Catalan. lm-eval group `cabbq` scores by
  log-likelihood over ans0, ans1, and several unknown phrasings collapsed to
  index 2. Prompts use Context / Pregunta / Resposta.
metric:
  name: "acc_ambig and acc_disambig (higher better); bias_score_ambig and bias_score_disambig (near 0 better)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Accuracy is reported separately for ambiguous and disambiguated items.
    Bias scores use the BBQ-style formulas in the paper; 0 means errors are
    not skewed toward the stereotyped group. lm-eval marks bias_score_* as
    higher_is_better false. No random or human baseline is given in the sources
    opened here. Group aggregates are micro-averages (weight_by_size true).
dataset:
  size: 27320
  size_note: >
    Paper and Hugging Face README table: 323 templates → 27,320 instances
    across 10 category configs (Age 4,068; Disability 2,832; Gender 4,832;
    LGBTQIA 2,000; Nationality 504; Physical Appearance 3,528; Race/Ethnicity
    3,716; Religion 648; SES 4,204; Spanish Region 988). The live parquet
    configs sum to 27,344 because PhysicalAppearance has 3,552 rows rather
    than 3,528. Test split only.
  url: "https://huggingface.co/datasets/BSC-LT/CaBBQ"
  license: "CC-BY-4.0"
  languages:
    - ca
  modalities:
    - text
  splits: "test only, one Hugging Face config per social category"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center, Language Technologies Unit"
  authors:
    - "Valle Ruiz-Fernández"
    - "Mario Mina"
    - "Júlia Falcão"
    - "Luis Vasquez-Reina"
    - "Anna Sallés"
    - "Aitor Gonzalez-Agirre"
    - "Olatz Perez-de-Viñaspre"
  url: "https://github.com/langtech-bsc/SpainBBQ"
paper:
  title: "EsBBQ and CaBBQ: The Spanish and Catalan Bias Benchmarks for Question Answering"
  arxiv: "2507.11216"
  url: "https://arxiv.org/abs/2507.11216"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/langtech-bsc/SpainBBQ"
released: "2025-07"
last_updated: "2025-09"
lineage:
  family: ""
  predecessor: bbq
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper finds models often fail ambiguous items and that higher QA
    accuracy can track higher bias scores. No single current ceiling was
    confirmed here. Accuracy approaching 100% would still leave the bias
    scores informative.
contamination:
  risk: medium
  note: >
    Templates and labels are public (CC BY 4.0) as of 2025. The card forbids
    using CaBBQ as training data. No memorisation study was opened here.
harness:
  lm_eval: cabbq
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group `cabbq` runs cabbq_age, cabbq_disability_status, cabbq_gender,
    cabbq_lgbtqia, cabbq_nationality, cabbq_physical_appearance,
    cabbq_race_ethnicity, cabbq_religion, cabbq_ses, cabbq_spanish_region
    on BSC-LT/CaBBQ. Parallel Spanish group is `esbbq` (no page in this
    repository yet).
tags:
  - bias
  - social-bias
  - safety
  - catalan
  - question-answering
sources:
  - url: "https://arxiv.org/abs/2507.11216"
    title: "EsBBQ and CaBBQ paper (arXiv:2507.11216)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2507.11216"
    title: "EsBBQ and CaBBQ full text (ar5iv); 27,320 instances, 323 templates"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/BSC-LT/CaBBQ"
    title: "BSC-LT/CaBBQ dataset card (CC-BY-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/BSC-LT/CaBBQ"
    title: "Hugging Face API metadata (per-config row counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cabbq/README.md"
    title: "lm-evaluation-harness cabbq README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cabbq/cabbq.yaml"
    title: "lm-eval cabbq group (micro-averaged metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cabbq/_cabbq_common_yaml"
    title: "lm-eval CaBBQ prompt and metric list"
    accessed: "2026-09-08"
  - url: "https://github.com/langtech-bsc/SpainBBQ"
    title: "langtech-bsc/SpainBBQ (renamed from EsBBQ-CaBBQ; Apache-2.0 LICENSE.txt)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-029 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-029"
---

## What it measures

CaBBQ is a Catalan social-bias QA set. The model reads a short context and a question about two people or groups, then chooses among two named answers and an unknown option. Ambiguous contexts contain no fact that would justify picking a group. Disambiguated contexts add a sentence that names the correct group. The test is whether the model leans on a stereotype when it should abstain, and whether it can override that stereotype when the text is clear.

The ten categories are tuned to Spain (including a Spanish-region slice), not to US BBQ templates unchanged. EsBBQ is the Spanish-language twin; there is no `esbbq` page in this repository yet.

## How it is scored

lm-evaluation-harness reports four group metrics: accuracy on ambiguous items, accuracy on disambiguated items, and a bias score on each subset. Accuracy should be high. Bias scores should sit near zero; the harness treats them as lower-is-better. Unknown answers are matched to several Catalan phrasings so the model is not rewarded for one token. Group totals are micro-averages across documents (`weight_by_size: true`). Headline accuracy without the matching bias score hides the failure mode the paper cares about.

## Dataset and licence

The paper and the dataset-card table give 323 templates and 27,320 instances. Hugging Face parquet configs currently sum to 27,344; Physical Appearance is 3,552 rows on the Hub versus 3,528 in the table. The Hub card licence is CC BY 4.0. Split is test-only. The card says not to train on CaBBQ. Templates and generation code now live at langtech-bsc/SpainBBQ; the paper’s EsBBQ-CaBBQ URL redirects there. That repository’s LICENSE.txt is Apache-2.0, which is not the same SPDX as the dataset card.

## Who publishes it

Valle Ruiz-Fernández, Mario Mina, Júlia Falcão, Luis Vasquez-Reina, Anna Sallés, Aitor Gonzalez-Agirre and Olatz Perez-de-Viñaspre released EsBBQ and CaBBQ in July 2025 (arXiv:2507.11216). Curation is credited to the Language Technologies Unit at the Barcelona Supercomputing Center, with funding notes for Projecte Aina and ALIA.

## Lineage

Design predecessor is English [BBQ](bbq.md) (Parrish et al.). CaBBQ is a new Catalan corpus with Spain-specific templates, not a harness spelling of BBQ. Jin et al. 2024 (arXiv:2307.16778) is cited for template-transfer classes (simply-transferred, target-modified, newly-created). EsBBQ is the parallel Spanish set and is not yet a page here.

## Saturation and contamination

No current ceiling was confirmed. The paper reports that models often miss ambiguous items and that higher accuracy can come with higher bias. Labels have been public since 2025, so leakage is possible, but the intended use is evaluation-only.

## How to run it

`lm-eval --tasks cabbq` runs all ten category tasks on `BSC-LT/CaBBQ`. Category tasks are `cabbq_age`, `cabbq_ses`, and so on. Compare only numbers that used the same unknown-option list and the same micro versus macro rule. Do not drop the bias scores.

## Reading the numbers

High disambiguated accuracy with a large positive ambiguous bias score means the model answers when it should say it does not know, and does so in the stereotyped direction. Compare CaBBQ with EsBBQ and with English BBQ only as a family of protocols, not as one number. A Catalan-only model that looks strong on generic QA can still fail the ambiguous slice.
