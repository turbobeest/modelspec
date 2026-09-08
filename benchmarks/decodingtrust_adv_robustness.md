---
id: decodingtrust_adv_robustness
name: "DecodingTrust Adversarial Robustness (AdvGLUE++)"
aliases:
  - "AdvGLUE++"
  - "decodingtrust_adv_glue_plus_plus"
  - "DecodingTrustAdvRobustnessScenario"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust AdvGLUE++ GLUE adversarial classification"
status: unknown
summary: "HELM scenario for DecodingTrust AdvGLUE++: GLUE items rewritten against Alpaca, Vicuna, and StableVicuna."
measures: >
  decodingtrust_adv_robustness is HELM's wrap of DecodingTrust section 5.2. Each item is an
  English GLUE classification example whose text was perturbed to fool Alpaca-7B, Vicuna-13B
  or StableVicuna-13B, then transferred to the model under test. Tasks are SST-2, QQP, MNLI,
  MNLI-mismatched, QNLI and RTE. HELM's scenario class is named decodingtrust_adv_glue_plus_plus;
  metadata and the run spec use decodingtrust_adv_robustness. The original AdvGLUE (BERT-era)
  split is documented in the paper but is not implemented in HELM and is not loaded.
task_format: >
  HELM instruct generation, max_tokens 16, temperature 0, one completion. The prompt is a
  task instruction plus labelled fields (sentence, premise/hypothesis, question pairs).
  Parameter glue_task selects one GLUE slice.
metric:
  name: quasi_exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_decodingtrust.yaml headlines quasi_exact_match on valid. The run spec attaches
    get_exact_match_metric_specs(). The paper also reports robust accuracy, performance drop
    from benign GLUE, and a nonexistence/refusal rate; HELM does not implement those extra
    metrics. Chance depends on the task (2-way or 3-way) and is not stored as one baseline.
dataset:
  size: 42017
  size_note: >
    Direct count of DecodingTrust-Data-Legacy advglue_plus_plus.json at the HELM pin
    38972f6ccbf376a8d0660babafb4d2b3b9cca3f4: sst2 5,792; qqp 11,383; mnli 3,697; mnli-mm 3,963;
    qnli 14,987; rte 2,195 (42,017 total). Matches paper Table 40 summed over Alpaca, Vicuna
    and StableVicuna. One HELM run loads a single glue_task key, not all 42,017. Table 48's
    42,755-prompt adversarial-robustness figure includes other templates beyond this JSON.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM VALID_SPLIT; one GLUE sub_split per run"
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
    - decodingtrust_adv_demonstration
    - decodingtrust_fairness
    - decodingtrust_privacy
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper Table 7 reports 2023 GPT-3.5/GPT-4 robust accuracy on AdvGLUE++. No current HELM
    DecodingTrust leaderboard URL resolved (404 on crfm.stanford.edu/helm/decodingtrust/latest/,
    2026-09-08). The project site still links a leaderboard page, but scores were not extracted
    here. The HELM README states maintenance mode from 2026-06-01. Saturation for this HELM id
    is not established.
contamination:
  risk: medium
  note: >
    AdvGLUE++ is public on GitHub Data-Legacy and listed on gated Hugging Face
    AI-Secure/DecodingTrust (card created 2023-10-12). Base GLUE validation texts are older
    and widely copied. Attacks were generated against 2023-era open models (Alpaca, Vicuna,
    StableVicuna). No measured overlap study for these perturbations was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_adv_robustness"
  opencompass: ""
  bigbench: ""
  other: "Run spec decodingtrust_adv_robustness:task={glue_task} with glue_task in sst2, mnli, mnli-mm, qnli, qqp, rte. Scenario class name is decodingtrust_adv_glue_plus_plus."
tags:
  - safety
  - robustness
  - adversarial
  - glue
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_adv_robustness_scenario.py"
    title: "HELM DecodingTrustAdvRobustnessScenario (AdvGLUE++ JSON, GLUE tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_adv_robustness run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (AdvGLUE++, quasi_exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/adv-glue-plus-plus/data/advglue_plus_plus.json"
    title: "AdvGLUE++ JSON at HELM pin (42,017 items across six tasks)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML: section 5.2 and Table 40 AdvGLUE++ counts"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (CC-BY-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://decodingtrust.github.io/"
    title: "DecodingTrust project site"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/pulls/1827"
    title: "HELM PR 1827 (merged 2024-01-08)"
    accessed: "2026-09-08"
  - url: "https://github.com/AI-secure/DecodingTrust"
    title: "AI-secure/DecodingTrust repository"
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

HELM's decodingtrust_adv_robustness run asks a model to label an adversarially rewritten GLUE example. DecodingTrust built AdvGLUE++ by attacking Alpaca-7B, Vicuna-13B and StableVicuna-13B with word- and sentence-level methods (TextBugger, TextFooler, BERT-ATTACK, SememePSO, SemAttack) and keeping the transferred items. SST-2 is sentiment. QQP is paraphrase. MNLI and MNLI-mm are three-way entailment. QNLI is question-sentence entailment. RTE is two-way entailment. The test is transfer robustness, not clean GLUE.

HELM does not load classic AdvGLUE (the BERT-era set in section 5.1). The scenario comments still list benign GLUE and AdvGLUE as unimplemented.

## How it is scored

The instruct adapter requests a short label (`positive`/`negative`, `yes`/`no`, or `yes`/`maybe`/`no`) in 16 tokens at temperature 0. HELM scores exact and quasi-exact match. The paper's extra columns — drop from benign accuracy, and the rate of missing/hallucinated answers — are not in this run spec. A 3-way MNLI item has a different chance rate than SST-2; do not pool tasks into one number unless every run used the same `glue_task`.

## Dataset and licence

HELM downloads `advglue_plus_plus.json` from DecodingTrust-Data-Legacy. A direct count at the pinned commit is 42,017 items, matching Table 40's per-model sums. Licence is CC-BY-SA-4.0 on the GitHub repo and Hugging Face card. The Hugging Face copy is gated; the GitHub JSON is public. Labels are in the file.

## Who publishes it

Same DecodingTrust author list and NeurIPS 2023 Outstanding Paper (Datasets and Benchmarks) as the other HELM wraps. HELM PR 1827 merged 8 January 2024. Project site decodingtrust.github.io. AdvGLUE itself is Wang et al. 2021; AdvGLUE++ is the DecodingTrust extension.

## Lineage

Sibling pages: [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md) (hostile few-shot examples), [decodingtrust_fairness](decodingtrust_fairness.md), and [decodingtrust_privacy](decodingtrust_privacy.md). Other DecodingTrust HELM scenarios do not yet have pages. This is not [helm_safety](helm_safety.md) and not a GLUE/SuperGLUE score.

## Saturation and contamination

Unknown current saturation. AdvGLUE++ has been public since 2023, built from GLUE validation text that is older. Transfer attacks against 2023 chat finetunes may not match attacks against later models. Treat a high score as robustness to this frozen transfer set.

## How to run it

HELM: `decodingtrust_adv_robustness` with `task` in `sst2`, `mnli`, `mnli-mm`, `qnli`, `qqp`, `rte`. Compare only the same task. Sixteen-token outputs can truncate explanations into non-labels. lm-eval and inspect_evals names were not found.

## Reading the numbers

A high quasi-exact match on SST-2 AdvGLUE++ means the model kept the sentiment label under those perturbations, not that it is generally jailbreak-hard. MNLI-mm and QQP dominate the 42,017-item pool if someone averages unweighted files. Pair this with a clean GLUE run if you need a drop-from-benign figure; HELM does not emit one. Do not confuse the scenario class name `decodingtrust_adv_glue_plus_plus` with a second benchmark.
