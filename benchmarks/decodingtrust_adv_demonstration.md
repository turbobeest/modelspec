---
id: decodingtrust_adv_demonstration
name: "DecodingTrust Adversarial Demonstrations"
aliases:
  - "AdvDemo"
  - "decodingtrust_adv_demo"
  - "DecodingTrustAdvDemoScenario"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust in-context adversarial demonstrations"
status: unknown
summary: "HELM scenario for DecodingTrust's adversarial-demonstration tests: counterfactual, spurious, and backdoored in-context examples."
measures: >
  decodingtrust_adv_demonstration is HELM's wrap of DecodingTrust section 7. The model must
  classify a short English text after a prompt that may contain (1) a counterfactual neighbor
  with the opposite label, (2) demonstrations that all share a spurious heuristic, or (3)
  backdoored SST-2 demonstrations. Tasks include SNLI-CAD premise/hypothesis revisions, four
  MSGS linguistic probes, six NLI spurious-correlation slices, and SST-2 backdoor setups.
  The skill is whether in-context examples can flip or trap the label, not ordinary NLI accuracy.
task_format: >
  HELM instruct generation, max_tokens 16, temperature 0, max_train_instances 0. Demonstrations
  are already inside each jsonl record; the scenario concatenates them as "Answer:" blocks.
  Parameters: perspective, data, demo_name, description.
metric:
  name: quasi_exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM schema_decodingtrust.yaml headlines quasi_exact_match on the valid split. The run spec
    attaches get_exact_match_metric_specs() (exact_match plus quasi_exact_match). Backdoor
    jsonl files are split into asr and cacc groups in the original benchmark; HELM still reports
    exact-match family scores, not a separate ASR metric. No random or human baseline is stated
    for the HELM wrap.
dataset:
  size: null
  size_note: >
    No single HELM instance count: the scenario loops seeds (3 for counterfactual/backdoor, 5
    for spurious) and, for backdoor, both asr and cacc jsonl files. DecodingTrust Table 48
    counted 233,100 prompts for the authors' full adversarial-demonstration evaluation, which
    is not one HELM run. Hugging Face config adv_demonstration lists many splits under
    AI-Secure/DecodingTrust (gated). HELM downloads from AI-secure/DecodingTrust-Data-Legacy
    at commit 38972f6ccbf376a8d0660babafb4d2b3b9cca3f4.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM VALID_SPLIT; sub_split is seed or asr_/cacc_ plus seed"
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
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - decodingtrust_adv_robustness
    - decodingtrust_fairness
    - decodingtrust_privacy
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The 2023 paper reports GPT-3.5/GPT-4 tables for counterfactual, spurious, and backdoor
    settings. No current HELM DecodingTrust leaderboard URL resolved (crfm.stanford.edu/helm/decodingtrust/latest/ returned 404 on 2026-09-08). The project site still links a leaderboard page, but scores were not extracted here. The HELM README states maintenance mode from 2026-06-01. Saturation for this HELM id is not established.
contamination:
  risk: medium
  note: >
    Demonstration files are public on GitHub DecodingTrust-Data-Legacy and listed on the gated
    Hugging Face card (created 2023-10-12). SNLI-CAD, MSGS and SST-2 sources are older public
    datasets. No measured training-set overlap study for these jsonl packs was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_adv_demonstration"
  opencompass: ""
  bigbench: ""
  other: "Run spec decodingtrust_adv_demonstration:perspective=...,data=...,demo_name=...,description=... ; HELM PR 1827 also cited presentation/run_specs_decodingtrust.conf, which 404s on current main."
tags:
  - safety
  - robustness
  - in-context-learning
  - adversarial
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_adv_demonstration_scenario.py"
    title: "HELM DecodingTrustAdvDemoScenario (perspectives, seeds, prompt merge)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_adv_demonstration run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (AdvDemo, quasi_exact_match, valid split)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/pulls/1827"
    title: "HELM PR 1827 DecodingTrust Scenarios (merged 2024-01-08)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698, NeurIPS 2023 Outstanding Paper)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML: section 7 and Table 48 prompt counts"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face AI-Secure/DecodingTrust README (CC-BY-SA-4.0, gated extra fields)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/AI-Secure/DecodingTrust"
    title: "Hugging Face DecodingTrust dataset API (license, configs, gated)"
    accessed: "2026-09-08"
  - url: "https://decodingtrust.github.io/"
    title: "DecodingTrust project site"
    accessed: "2026-09-08"
  - url: "https://github.com/AI-secure/DecodingTrust"
    title: "AI-secure/DecodingTrust repository (CC-BY-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-008"
---

## What it measures

This HELM scenario tests whether a model keeps the right label when the in-context examples are hostile. DecodingTrust section 7 studies three demonstration attacks. Counterfactual: a nearby example with the opposite label, from SNLI-CAD or from MSGS linguistic probes (control raising, irregular form, progressive main verb, adjective presence). Spurious: NLI demonstrations that all follow one fallible heuristic (PP, adverb, embedded verb, relative clauses, passive). Backdoor: SST-2 demonstrations that teach a trigger such as the token `cf`. The user input is still a short English classification item; the trap is in the few-shot prefix.

## How it is scored

HELM generates one completion of at most 16 tokens at temperature 0 and scores exact / quasi-exact match against the jsonl `label`. `schema_decodingtrust.yaml` headlines `quasi_exact_match` on `valid`. The original paper also reports attack success on backdoored inputs versus clean accuracy (`asr` / `cacc` files). HELM loads both file types as ordinary labelled instances, so a single mean mix those two pools unless you split on `sub_split`. Chance depends on the option set (`yes`/`no`, `yes`/`maybe`/`no`, `positive`/`negative`) and is not recorded as one random baseline.

## Dataset and licence

Files live under `data/adv_demonstration/` in DecodingTrust-Data-Legacy (HELM pins `38972f6ccbf376a8d0660babafb4d2b3b9cca3f4`). Hugging Face `AI-Secure/DecodingTrust` lists the same tree, licence `cc-by-sa-4.0`, with a gated access form. Instance count for one HELM invocation depends on `perspective`, `data`, `demo_name` and seeds; the paper's 233,100-prompt figure is the authors' full sweep, not this scenario's default. Answers are public.

## Who publishes it

DecodingTrust is Wang, Chen, Pei, Xie, Kang, Zhang, Xu, Xiong, Dutta, Schaeffer, Truong, Arora, Mazeika, Hendrycks, Lin, Cheng, Koyejo, Song and Li (arXiv 20 June 2023, v5 26 February 2024). NeurIPS 2023 Outstanding Paper, Datasets and Benchmarks. HELM added the wrap in PR 1827, merged 8 January 2024. Project site: decodingtrust.github.io. The original evaluation code is AI-secure/DecodingTrust.

## Lineage

No DecodingTrust family page exists here yet. Sibling HELM pages: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md) (AdvGLUE++ input attacks), [decodingtrust_fairness](decodingtrust_fairness.md) (Adult income), and [decodingtrust_privacy](decodingtrust_privacy.md). Other HELM wraps without pages: `decodingtrust_ood_robustness`, `decodingtrust_machine_ethics`, `decodingtrust_toxicity_prompts`, `decodingtrust_stereotype_bias`. This is not [helm_safety](helm_safety.md), which averages five different safety sets.

## Saturation and contamination

The 2023 GPT-4 tables are not a current leaderboard. Demonstration jsonl has been public since 2023. SNLI, SST-2 and MSGS are older still. A model can look robust because it ignores few-shot examples, which is a different skill from resisting a crafted attack.

## How to run it

HELM: `decodingtrust_adv_demonstration` with `perspective` in `{counterfactual, spurious, backdoor}`, plus `data`, `demo_name` and `description` from the scenario maps. `cf` and `zero` demo names skip extra seeds. PR 1827's `run_specs_decodingtrust.conf` path 404s on current HELM main; the Python run spec remains. Compare only runs that share perspective, data, demo_name, description and seed list.

## Reading the numbers

A high quasi-exact match on counterfactual demos means the model did not copy the adjacent flipped label. On backdoor `asr` files, a high match can mean the backdoor failed or that labels happen to coincide; read `asr` and `cacc` separately. Do not average this id with [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md): one attacks the demonstrations, the other attacks the test sentence. Sixteen-token truncations can also look like refusals.
