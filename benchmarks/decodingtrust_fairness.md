---
id: decodingtrust_fairness
name: "DecodingTrust Fairness"
aliases:
  - "DecodingTrustFairnessScenario"
  - "DecodingTrust - Fairness"
page_kind: benchmark
category: safety
subcategory: "HELM wrap of DecodingTrust Adult income fairness (yes/no)"
status: unknown
summary: "HELM scenario for DecodingTrust fairness: yes/no Adult income prediction, scored for accuracy and group gaps."
measures: >
  decodingtrust_fairness is HELM's wrap of DecodingTrust section 10, limited to the Adult income
  task. Each item is an English paragraph of census-style attributes (age, education, sex,
  race, hours, and the rest of Adult's 14 fields; the jsonl templates say 1996). The model must
  answer whether annual income exceeds $50k with exactly yes or no. The paper's fairness section
  reports Adult only and varies sensitive attributes (sex, race) and few-shot base-rate parity.
  Hugging Face also lists unused Crime jsonl files. HELM's scenario only implements
  task=predict_annual_income (Adult files). HELM's FairnessMetric then estimates demographic
  parity difference and equalized odds difference using a "sex Female" substring.
task_format: >
  HELM instruct generation, max_tokens 16, temperature 0, max_train_instances 0. Parameters:
  task, train_base_rate, test_base_rate, num_train, num_test, which select one jsonl filename.
metric:
  name: "quasi_exact_match (headline); demographic_parity_difference; equalized_odds_difference"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_decodingtrust.yaml headlines quasi_exact_match on valid and also lists DPD and EOD
    as lower-is-better fairness metrics. The run spec attaches FairnessMetric plus exact-match
    specs. Adult is two-way yes/no (chance 50% if balanced, which these base-rate files are not).
    No human baseline is stated. HELM's schema blurb for equalized_odds_difference incorrectly
    talks about OoD refusal; the paper and FairnessMetric use fairlearn's EOD on yes/no labels.
dataset:
  size: 200
  size_note: >
    Paper section 10: 200 Adult test samples per constructed base-rate slice. HELM jsonl
    adult_32_200_train_br_0.0_test_br_0.5.jsonl has 200 lines (direct count) and a 32-item
    examples array on each line. Zero-shot Adult files are named adult_0_200_*. Hugging Face
    also lists crime_0_300_* files; HELM's TASK_DESCRIPTIONS does not map them. Filename
    num_train does not add extra HELM adapter shots: get_instruct_adapter_spec sets
    max_train_instances=0, and the scenario prompt uses only raw_item["input"], not the jsonl
    examples array.
  url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM VALID_SPLIT; one Adult jsonl per parameter combo"
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
    - decodingtrust_adv_robustness
    - decodingtrust_privacy
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper Tables 30–33 report 2023 GPT-3.5/GPT-4 accuracy, DPD and EOD under different Adult
    base rates. No current HELM DecodingTrust leaderboard URL resolved (404 on
    crfm.stanford.edu/helm/decodingtrust/latest/, 2026-09-08). The project site still links a
    leaderboard page, but scores were not extracted here. The HELM README states maintenance
    mode from 2026-06-01.
contamination:
  risk: medium
  note: >
    Adult is a long-public UCI table; DecodingTrust's templated paragraphs and labels are
    public on GitHub Data-Legacy and listed on gated Hugging Face AI-Secure/DecodingTrust
    (card created 2023-10-12). No measured overlap study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_fairness"
  opencompass: ""
  bigbench: ""
  other: "Run spec decodingtrust_fairness:task={task} (scenario args also include train_base_rate, test_base_rate, num_train, num_test)."
tags:
  - safety
  - fairness
  - adult-income
  - helm
  - decodingtrust
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_fairness_scenario.py"
    title: "HELM DecodingTrustFairnessScenario (Adult jsonl naming, yes/no task)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_fairness run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/decodingtrust_fairness_metrics.py"
    title: "HELM FairnessMetric (DPD, EOD, sex Female detector)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (fairness group, quasi_exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust-Data-Legacy/38972f6ccbf376a8d0660babafb4d2b3b9cca3f4/data/fairness/fairness_data/adult_32_200_train_br_0.0_test_br_0.5.jsonl"
    title: "Adult 32/200 jsonl sample (200 lines, yes/no labels)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML: section 10 fairness metrics and Adult setup"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/DecodingTrust/resolve/main/README.md"
    title: "Hugging Face DecodingTrust README (CC-BY-SA-4.0, fairness configs)"
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

HELM's decodingtrust_fairness run turns one Adult record into a short English bio and asks whether that person's income is above $50k. DecodingTrust section 10 uses that task to probe dependence on sensitive attributes and on the base-rate mix of few-shot examples. The paper's fairness write-up reports Adult only. Hugging Face lists `crime_0_300_*` jsonl files, but HELM has no Crime task name. The metric class treats a prompt containing `sex Female` as group 0 and every other prompt as group 1, so race-gap tables from the paper are not what HELM emits.

## How it is scored

The instruct adapter is zero-shot (`max_train_instances=0`) even when the filename contains `num_train=32`. The counted `adult_32_200_*` file has a 32-item `examples` array on every line, but the scenario copies only `raw_item["input"]`, so those shots never enter the HELM prompt. Completions are matched as yes/no for accuracy. `FairnessMetric` maps yes-like keywords to 1, no-like to 0, skips ambiguous strings, then calls fairlearn for demographic parity difference and equalized odds difference. Lower DPD/EOD is fairer; higher quasi-exact match is more accurate. The paper notes that accuracy can rise as the test base rate becomes more skewed.

## Dataset and licence

Adult slices are 200 labelled paragraphs per file. Crime files named `crime_0_300_*` exist on Hugging Face and in Data-Legacy but are unused by HELM; this review did not count those rows. Licence is CC-BY-SA-4.0. Hugging Face `AI-Secure/DecodingTrust` is gated; GitHub Data-Legacy is public. Labels are in the jsonl (`"yes"` / `"no"`). HELM's reference output text is `0` or `1`, which `FairnessMetric` parses as `y_true`.

## Who publishes it

DecodingTrust authors as on arXiv:2306.11698 (NeurIPS 2023 Outstanding Paper, Datasets and Benchmarks). HELM wrap: PR 1827, 8 January 2024. Adult is the UCI income table (Kohavi 1996); the jsonl bios say 1996. Project site: decodingtrust.github.io.

## Lineage

Siblings: [decodingtrust_adv_robustness](decodingtrust_adv_robustness.md), [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md), and [decodingtrust_privacy](decodingtrust_privacy.md). Other DecodingTrust HELM scenarios still lack pages. This is not [bbq](bbq.md) (ambiguous QA stereotypes) and not [helm_safety](helm_safety.md).

## Saturation and contamination

Unknown current saturation. Adult text is old and public; these 200-row templates have been public since 2023. A model that always answers "no" can look fair and inaccurate, or the reverse, depending on the slice's base rate. Compare DPD/EOD and accuracy together.

## How to run it

HELM: `decodingtrust_fairness` with `task=predict_annual_income` and the four numeric args that pick a jsonl name. Do not compare a `train_br_0.0` file to a `test_base_rate_1.0` file as the same score. Sixteen-token truncations and hedging ("yes, but") are dropped by the keyword filter before DPD/EOD. lm-eval and inspect_evals names were not found.

## Reading the numbers

Quasi-exact match on these 200 bios is income classification, not a general fairness certificate. HELM's DPD/EOD only split on the `sex Female` string, so they are not the paper's race columns. Because HELM does not inject the jsonl few-shot array, a `num_train=32` run spec is still a zero-shot HELM prompt unless you verify the rendered input. Read accuracy and gap metrics on the same slice; a higher score on a skewed test set can be the bias the benchmark is meant to show.
