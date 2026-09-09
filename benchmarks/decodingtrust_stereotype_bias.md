---
id: decodingtrust_stereotype_bias
name: "DecodingTrust Stereotype Bias"
aliases:
  - "DecodingTrust - Stereotype Bias"
  - "DecodingTrustStereotypeBiasScenario"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust section 4 (1,152 stereotype statements × 3 system prompts)"
status: unknown
summary: "HELM scenario for DecodingTrust stereotypes: agree/disagree with 1,152 statements across 16 topics, 24 groups, and 3 system prompts."
measures: >
  decodingtrust_stereotype_bias is HELM's wrap of DecodingTrust section 4. Each English user
  prompt states a stereotype and tells the model to append agree or disagree. There are 16
  topics (HIV, terrorists, drug addiction, intelligence, greed, parenting, country,
  technology, weakness, driving, crime, drug dealing, jobs, leadership, STEM, hygiene) and
  24 demographic groups spanning race/ethnicity, gender/orientation, nationality, age,
  religion, disability, and socioeconomic status. Three system-prompt types — benign,
  untargeted jailbreak, and targeted jailbreak — are stored as tags. Every statement is a
  stereotype; the paper treats agreement as the biased outcome.
task_format: >
  HELM instruct generation, num_outputs 25, max_tokens 150, temperature 1. The scenario
  loads stereotype_bias_data.jsonl and does not take a task argument (the run function
  still declares unused task: str).
metric:
  name: decodingtrust_stereotype_bias
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper section 4.2 defines agreementIndex = n_agree / 25 in [0, 1] (higher means more
    agreement with the stereotype). HELM schema_decodingtrust.yaml names
    decodingtrust_stereotype_bias as 1 − agreementIndex and marks it higher-is-better, plus
    decodingtrust_stereotype_bias_rejection_rate. StereotypeMetric classifies each
    completion with agree / disagree / no-response phrase lists, then after every instance
    adds 1 − (agree_matrix.mean() / n_completions) as a 24×16×3 count matrix fills, so the
    HELM Stat is a mean of running values, not one paper-style index. No random or human
    baseline is published.
dataset:
  size: 3456
  size_note: >
    Direct count of Data-Legacy stereotype_bias_data.jsonl at HELM pin
    38972f6ccbf376a8d0660babafb4d2b3b9cca3f4: 3,456 lines = 1,152 user prompts × 3 system
    types. Paper and the stereotype README: 1,152 user prompts (16 topics × 3 variants ×
    24 groups). HELM tags copy sys_prompt_type_tag from the jsonl; the benign value is
    misspelled "beningn" in that file (1,152 rows).
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT; one jsonl, three system-prompt tags"
  public_test_set: true
publisher:
  org: "DecodingTrust authors (UIUC / Stanford / collaborators); HELM wrap by Stanford CRFM"
  authors:
    - "Boxin Wang"
    - "Weixin Chen"
    - "Hengzhi Pei"
    - "Chulin Xie"
    - "Mintong Kang"
    - "Chenhui Zhang"
    - "Chejian Xu"
    - "Zidi Xiong"
    - "Ritik Dutta"
    - "Rylan Schaeffer"
    - "Sang T. Truong"
    - "Simran Arora"
    - "Mantas Mazeika"
    - "Dan Hendrycks"
    - "Zinan Lin"
    - "Yu Cheng"
    - "Sanmi Koyejo"
    - "Dawn Song"
    - "Bo Li"
  url: "https://decodingtrust.github.io/"
paper:
  title: "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models"
  arxiv: "2306.11698"
  url: "https://arxiv.org/abs/2306.11698"
  year: 2023
leaderboard_url: "https://decodingtrust.github.io/"
repo_url: "https://github.com/AI-secure/DecodingTrust"
released: "2023-06"
last_updated: "2024-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - decodingtrust_adv_demonstration
    - decodingtrust_adv_robustness
    - decodingtrust_fairness
    - decodingtrust_privacy
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper section 4 reports 2023 GPT-3.5/GPT-4 agreement heatmaps, not a single ceiling.
    No current HELM DecodingTrust leaderboard URL resolved (404 on
    crfm.stanford.edu/helm/decodingtrust/latest/, 2026-09-08). HELM README states
    maintenance mode from 2026-06-01. StereotypeMetric indexes SYS_PROMPT_TYPE
    ["benign","untargeted","targeted"]; the jsonl's "beningn" tag is not in that list.
contamination:
  risk: medium
  note: >
    Manually written prompts, public in Data-Legacy since 2023, listed on gated Hugging
    Face AI-Secure/DecodingTrust. No measured memorisation study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_stereotype_bias"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec decodingtrust_stereotype_bias (run entries pass task=all, ignored by the
    scenario). 25 samples per prompt, temperature 1, max_tokens 150.
tags:
  - safety
  - bias
  - stereotype
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_stereotype_bias_scenario.py"
    title: "HELM DecodingTrustStereotypeBiasScenario (1,152-prompt docstring; jsonl tags)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/decodingtrust_stereotype_bias_metrics.py"
    title: "HELM StereotypeMetric (agreement phrases; 1 − mean agree)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_stereotype_bias run spec (25 outputs, temperature 1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (1 − agreementIndex)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/stereotype/README.md"
    title: "Data-Legacy stereotype README (1,152 user prompts, 25 generations)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML section 4.2 (agreementIndex, n=25)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (stereotype config, CC-BY-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://decodingtrust.github.io/"
    title: "DecodingTrust project site"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-038 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-038"
---

## What it measures

HELM's decodingtrust_stereotype_bias run shows an English stereotype and asks the model to agree or disagree. DecodingTrust section 4 wrote 1,152 user prompts from 16 topics, three phrasings each, and 24 demographic groups. HELM expands that to 3,456 instances by repeating each prompt under benign, untargeted, and targeted system-prompt tags. Every item is a stereotype, so the intended behaviour is disagreement. This is not [bbq](bbq.md) ambiguous QA and not [crows_pairs](crows_pairs.md) likelihood comparison.

## How it is scored

The paper's agreementIndex is agrees / 25 completions. HELM schema text treats `decodingtrust_stereotype_bias` as one minus that mean (higher is less agreement) plus a rejection rate. StereotypeMetric instead adds `1 − (agree_matrix.mean() / n_completions)` after every instance while a 24×16×3 count matrix fills, so the HELM Stat is a mean of running values, not one grid-wide 1−agreementIndex. Completions are keyword-classified; mixed agree+disagree strings fall through to NO_RESPONSE except for a few "as an AI" corners. Temperature is 1 with 25 samples, matching the paper's n=25. Schema `main_split` is valid; the scenario emits TEST_SPLIT.

## Dataset and licence

1,152 unique user prompts; 3,456 HELM rows after three system types. Licence is CC-BY-SA-4.0. The jsonl is public on Data-Legacy; Hugging Face is gated. The benign tag in the file HELM downloads is spelled `beningn`. StereotypeMetric looks up `benign`, so a stock HELM score on that jsonl can raise ValueError unless the tag is patched.

## Who publishes it

DecodingTrust authors as on arXiv:2306.11698 (NeurIPS 2023 Datasets and Benchmarks Track). Prompts are original to this paper, not BBQ. HELM wrap: Stanford CRFM. Project site: decodingtrust.github.io.

## Lineage

Siblings with pages: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md), [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), [decodingtrust_fairness](decodingtrust_fairness.md), [decodingtrust_privacy](decodingtrust_privacy.md), [decodingtrust_machine_ethics](decodingtrust_machine_ethics.md), [decodingtrust_ood_robustness](decodingtrust_ood_robustness.md), [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md). Appendix B.3 of the paper also discusses a standard stereotype benchmark; that extra protocol is not this HELM id.

## Saturation and contamination

Unknown current saturation. The statements have been public since 2023. Phrase-matching under-counts hedges that never say "I agree" verbatim. HELM entered maintenance mode on 2026-06-01.

## How to run it

HELM: `decodingtrust_stereotype_bias` (run entries add `task=all`, which the scenario ignores). Do not compare HELM's inverted 1−agreementIndex to a paper heatmap of raw agreementIndex. Confirm whether the loader rewrites `beningn` before trusting a HELM number. lm-eval and inspect_evals names were not found.

## Reading the numbers

A high HELM bias score here means low keyword agreement with these 1,152 statements, not a general fairness certificate. Targeted system prompts are a different condition from benign. 25 samples at temperature 1 are part of the metric; a single greedy decode is not the same task. Read rejection rate beside the inverted agreement: a model that always refuses can look unbiased.
