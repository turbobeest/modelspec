---
id: decodingtrust_ood_robustness
name: "DecodingTrust OoD Robustness"
aliases:
  - "DecodingTrust - OoD Robustness"
  - "DecodingTrustOODRobustnessScenario"
  - "decodingtrust_ood"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust section 6 (SST-2 styles + RealtimeQA knowledge)"
status: unknown
summary: "HELM scenario for DecodingTrust out-of-distribution robustness: style-shifted SST-2 sentiment and RealtimeQA knowledge with optional refusal."
measures: >
  decodingtrust_ood_robustness is HELM's wrap of DecodingTrust section 6. Style runs take an
  English SST-2 sentence after a style transform (Shakespeare word/sentence, Bible, romantic,
  tweet, augmentation, or the untransformed base) and require exactly positive or negative.
  Knowledge runs prepend "Today is {date}" to a RealtimeQA item (qa_2020 or qa_2023) and ask
  for a multiple-choice letter; an I-don't-know option can be appended. Few-shot style uses
  eight demonstrations; knowledge uses five, including MMLU-topic demos (global facts,
  machine learning, moral scenarios, US foreign policy) or 2021 QA.
task_format: >
  Style: HELM instruct or 8-shot instruct, max_tokens 16, temperature 0. Knowledge: joint
  multiple-choice adapter, max_tokens 16, max_train_instances 5. Parameters: ood_type, task,
  demo_name, run_id, idk.
metric:
  name: "quasi_exact_match (style); ood_knowledge_rr / ood_knowledge_macc (knowledge)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Style runs attach exact-match specs; schema headlines quasi_exact_match on valid.
    Knowledge runs attach OODKnowledgeMetric: accuracy, refusal rate (rr), and meaningful
    accuracy macc = acc / (1 − rr). Higher rr and macc are described as more reliable.
    SST-2 is two-way. RealtimeQA items are four-way, five-way when idk adds option E.
    No human baseline is stated.
dataset:
  size: null
  size_note: >
    No single HELM instance count: one run is one style key or one knowledge year. Direct
    count of Data-Legacy style.json at HELM pin 38972f6: 872 dev sentences in each of 11
    style keys (base, augment, shake_w, shake_p0, shake_p0.6, bible_p0, bible_p0.6,
    romantic_p0, romantic_p0.6, tweet_p0, tweet_p0.6) and 8-shot train_demo lists.
    knowledge.json test: qa_2020 855 items, qa_2023 263 items; each demo list has 5 items.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM VALID_SPLIT for test prompts; TRAIN_SPLIT for in-file demonstrations"
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
    Paper section 6 reports 2023 GPT-3.5/GPT-4 style accuracy and knowledge rr/macc. No
    current HELM DecodingTrust leaderboard URL resolved (404 on
    crfm.stanford.edu/helm/decodingtrust/latest/, 2026-09-08). HELM README states
    maintenance mode from 2026-06-01. The scenario get_metadata() block still names
    decodingtrust_adv_demonstration; run spec and schema use ood_robustness.
contamination:
  risk: medium
  note: >
    Style items are transformed SST-2, a long-public GLUE split. Knowledge items are
    RealtimeQA dated questions; 2023 items were future relative to many 2023 training
    cutoffs but are now public in Data-Legacy and on gated Hugging Face
    AI-Secure/DecodingTrust. No measured overlap study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_ood_robustness"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec decodingtrust_ood_robustness:ood_type={style|knowledge},task=...,demo_name=...,run_id=...,idk=...
    Scenario class name is decodingtrust_ood. Style and knowledge attach different metrics.
tags:
  - safety
  - robustness
  - ood
  - sst2
  - realtimeqa
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_ood_robustness_scenario.py"
    title: "HELM DecodingTrustOODRobustnessScenario (style/knowledge JSON, metadata copy-paste)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_ood_robustness run spec (style vs knowledge adapters)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/decodingtrust_ood_knowledge_metrics.py"
    title: "HELM OODKnowledgeMetric (acc, rr, macc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (ood_robustness group)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_decodingtrust.conf"
    title: "HELM DecodingTrust run entries for OoD style and knowledge"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/ood/README.md"
    title: "Data-Legacy OOD README (style.json and knowledge.json)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML section 6 (OOD style, knowledge, demonstrations)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (ood config, CC-BY-SA-4.0)"
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

HELM's decodingtrust_ood_robustness run is two different tests under one id. Style is SST-2 sentiment after a synthetic style shift: the model must answer positive or negative on 872 English sentences per style key. Knowledge is dated multiple-choice current-events QA from RealtimeQA, with "Today is {date}" in the prompt, meant to probe answers beyond a training cutoff. Optional `idk` adds an E choice ("I don't know"). In-context demos can match the test style, use the base style, or (for 2020 QA) come from MMLU-like topics. This is not [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), even though the scenario's get_metadata() still copies that name.

## How it is scored

Style is scored as exact / quasi-exact match on positive/negative. Knowledge uses OODKnowledgeMetric: parse A–E, count refusals (letter E or keywords such as "don't know" / "sorry"), then report acc, refusal rate, and macc = acc / (1 − rr). The metric will divide by zero if every item is a refusal. Schema treats rr and macc as higher-is-better. Do not average a style exact-match with a knowledge macc.

## Dataset and licence

Each style key has 872 labelled sentences; eleven keys are in style.json. Knowledge test has 855 (2020) and 263 (2023) questions. Licence is CC-BY-SA-4.0. Hugging Face lists `ood/style.jsonl` and `ood/knowledge.jsonl`; HELM downloads `style.json` and `knowledge.json` from Data-Legacy. Labels are public.

## Who publishes it

DecodingTrust authors as on arXiv:2306.11698 (NeurIPS 2023 Datasets and Benchmarks Track). Style starts from SST-2 (Socher et al. / GLUE). Knowledge starts from RealtimeQA. HELM wrap: Stanford CRFM. Project site: decodingtrust.github.io.

## Lineage

Siblings with pages: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md), [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), [decodingtrust_fairness](decodingtrust_fairness.md), [decodingtrust_privacy](decodingtrust_privacy.md), [decodingtrust_machine_ethics](decodingtrust_machine_ethics.md), [decodingtrust_stereotype_bias](decodingtrust_stereotype_bias.md), [decodingtrust_toxicity_prompts](decodingtrust_toxicity_prompts.md). Not [adv_glue](adv_glue.md) and not [glue](glue.md) SST-2.

## Saturation and contamination

Unknown current saturation. SST-2 is old; 2023 RealtimeQA is no longer future knowledge. Compare 2020 and 2023 years separately. HELM entered maintenance mode on 2026-06-01.

## How to run it

HELM: `decodingtrust_ood_robustness` with `ood_type=style` or `knowledge`. Style tasks include `base`, `shake_w`, `shake_p0.6`, `bible_p0.6`, `tweet_p0.6`, and the rest of TASK["style"]. Knowledge tasks are `qa_2020` and `qa_2023`. `run_id` 0–2 selects a demo list and turns on 8-shot (style) or 5-shot (knowledge). lm-eval and inspect_evals names were not found.

## Reading the numbers

A high style score is sentiment accuracy on transformed SST-2, not general style transfer. A high knowledge macc can hide mass refusal if you ignore rr; read both. `idk=1` changes the option set, so it is not the same task as `idk=0`. Demo_name `global_facts` on 2020 QA is an out-of-domain shot mix, not a 2020-news few-shot. Do not cite the scenario metadata display name AdvDemo for these runs.
