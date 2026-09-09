---
id: entity_matching
name: "Entity matching (HELM)"
aliases:
  - "entity_matching"
  - "HELM EntityMatching"
  - "EntityMatching"
page_kind: benchmark
category: reasoning
subcategory: "HELM Yes/No matching of pre-blocked Magellan/DeepMatcher row pairs"
status: unknown
summary: "HELM generation task that asks whether two serialized table rows refer to the same entity, scored with exact match on Yes/No."
measures: >
  entity_matching is HELM's pre-blocked entity-matching scenario. The model
  reads two serialized rows and must answer Yes or No to "Are A and B the same?"
  The scenario class can load thirteen Magellan/DeepMatcher sets (structured,
  textual, and dirty). The HELM paper reports three: Beer, Abt-Buy, and dirty
  iTunes-Amazon. Pairs come already blocked; HELM does not run blocking. Train
  negatives are downsampled to the positive count before prompt sampling.
  English product, beer, and music rows. Open generation of Yes/No, not F1 over
  a ranked matcher. Laurel Orr implemented the scenario. It is not
  [entity_data_imputation](entity_data_imputation.md) and not Ditto.
task_format: >
  Input pattern in the scenario: "Product A is …. Product B is …. Are A and B
  the same?". HELM default adapter: generation, instructions "Are Product A and
  Product B the same? Yes or No?", output noun Answer, max_train_instances 5,
  max_tokens 5, temperature 0. Scenario.name is entity_matching; run spec names
  include the dataset argument.
metric:
  name: "quasi_exact_match (schema); run spec attaches exact-match metrics; paper uses exact-match accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Labels are Yes/No but positives are rare (DeepMatcher: Beer 68/450, Abt-Buy
    1028/9575, dirty iTunes-Amazon 132/539), so always answering No is a strong
    accuracy baseline. The HELM paper (E.3.11) says the literature usually uses
    F1 on 1/0 outputs, but HELM reports exact-match accuracy because the model
    may fail to emit Yes/No. schema_classic.yaml headlines quasi_exact_match.
    Narayan et al. 2022 scored F1. These are not interchangeable. No human
    baseline is given.
dataset:
  size: null
  size_note: >
    HELM paper appendix E.3.11 train-dev-test: Beer 269/92/92, Abt-Buy
    5744/1917/1917, dirty iTunes-Amazon 322/110/110. DeepMatcher Datasets.md
    totals for those three are 450 (68 pos), 9,575 (1,028 pos), and 539 (132 pos).
    The paper splits sum to 453, 9,578, and 542, three pairs off the DeepMatcher
    table. Mean input tokens in the appendix are 515, 838, and 1,255; output
    tokens 2. The scenario can also load iTunes_Amazon, Fodors_Zagats, DBLP_ACM,
    DBLP_GoogleScholar, Amazon_Google, Walmart_Amazon, Company, and the other
    dirty dumps; those are not the HELM paper's three-dataset mean. Train is
    then class-balanced by downsampling negatives.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_matching_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "DeepMatcher train/valid/test CSVs; HELM main_split test; train negatives downsampled to the positive count"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors:
    - "Laurel Orr"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_matching_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/entity_matching_scenario.py"
released: "2022-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No numeric HELM classic leaderboard cell was read (the public page is a
    JavaScript app). HELM entered maintenance mode on 2026-06-01. Narayan et al.
    2022 report GPT-3 few-shot F1 on Magellan sets; that is a different metric
    and is not copied here as a HELM top score.
contamination:
  risk: medium
  note: >
    Magellan/DeepMatcher dumps have been public at pages.cs.wisc.edu since the
    SIGMOD 2018 DeepMatcher release, and HELM downloads those zips. Gold Yes/No
    labels are in train.csv/valid.csv/test.csv. Product titles are ordinary web
    text. entity_matching_scenario_fixed_random_state.py pins numpy state from a
    CodaLab blob so later runs can match official HELM sampling.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "entity_matching"
  opencompass: ""
  bigbench: ""
  other: "Run spec entity_matching:dataset={Beer|Abt_Buy|Dirty_iTunes_Amazon|…}. Default ADAPT_GENERATION, max_train_instances=5, max_tokens=5. schema_classic lists the group under targeted reasoning."
tags:
  - helm
  - structured-data
  - entity-matching
  - generation
  - reasoning
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/entity_matching_scenario.py"
    title: "HELM entity_matching_scenario.py (13 DeepMatcher dumps, Yes/No generation, train downsample)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/entity_matching_scenario_fixed_random_state.py"
    title: "Fixed numpy state for reproducing official HELM entity-matching samples"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_entity_matching_spec (5-shot generation, exact-match metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (Entity matching group; quasi_exact_match; taxonomy language listed as synthetic)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_generation_adapter_spec defaults (max_train_instances 5, max_tokens 5, temperature 0)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML appendix E.3.11 Entity Matching (three Magellan sets; exact match not F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/anhaidgroup/deepmatcher/master/Datasets.md"
    title: "DeepMatcher Datasets.md (labeled-pair sizes and positive counts)"
    accessed: "2026-09-08"
  - url: "http://pages.cs.wisc.edu/~anhai/papers1/deepmatcher-sigmod18.pdf"
    title: "Mudgal et al., Deep Learning for Entity Matching (SIGMOD 2018)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.14778/3007263.3007314"
    title: "Konda et al., Magellan (PVLDB 2016)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2205.09911"
    title: "Narayan et al., Can Foundation Models Wrangle Your Data? (F1 prompting protocol)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2205.09911"
    title: "Narayan et al. HTML (Magellan EM; F1, not HELM exact match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (classic leaderboard; maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not a dataset licence)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-041 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-041"
---

## What it measures

entity_matching asks whether two serialized table rows refer to the same real-world entity. HELM does not run blocking: it loads pre-blocked labeled pairs from the DeepMatcher Magellan dumps. Each row is flattened to `attribute: value` phrases. The prompt always calls the rows "Product A" and "Product B," including on beer and music tables. The model must generate Yes or No. The scenario class lists thirteen dumps. The HELM paper's reported mean uses three of them: Beer (structured), Abt-Buy (textual), and dirty iTunes-Amazon. Train negatives are downsampled to the positive count so few-shot examples are class-balanced; test is not. This is not Ditto, not Magellan the system, and not [entity_data_imputation](entity_data_imputation.md).

## How it is scored

schema_classic.yaml headlines `quasi_exact_match` on the test split. The run spec attaches `get_exact_match_metric_specs()` plus generative-harms metrics. Appendix E.3.11 says the matching literature usually reports F1, but HELM uses exact-match accuracy so a non-Yes/No completion counts as wrong. Narayan et al. 2022, whose serialization HELM cites, scored F1. Those three numbers are not the same. Defaults are five-shot generation, `max_tokens=5`, temperature 0. Always-No accuracy is high because positives are scarce, so an accuracy near 85% on Beer can be a trivial policy.

## Dataset and licence

DeepMatcher Datasets.md gives labeled-pair totals Beer 450 (68 positive), Abt-Buy 9,575 (1,028), dirty iTunes-Amazon 539 (132). HELM appendix E.3.11 gives splits 269/92/92, 5744/1917/1917, and 322/110/110. Those triples sum to 453, 9,578, and 542, each three pairs above the DeepMatcher table. Downloads are `http://pages.cs.wisc.edu/~anhai/data1/deepmatcher_data/…/{dataset.lower()}_exp_data.zip`. Official HELM sampling pins numpy state from a CodaLab JSON so later runs can match the original train draws. No dataset licence string appears in the scenario, schema, or DeepMatcher page, so license is left empty. HELM code is Apache-2.0. schema_classic lists language as synthetic; the rows are crawled product, beer, and music records.

## Who publishes it

Stanford CRFM released the scenario with HELM (arXiv 2211.09110, November 2022). Laurel Orr implemented it. Underlying dumps are the Magellan/DeepMatcher collection (Konda et al., PVLDB 2016; Mudgal et al., SIGMOD 2018). Prompt style follows Narayan et al. 2022 and Ditto-style serialization (Li et al. 2020). The classic HELM leaderboard still lists the name. HELM entered maintenance mode on 2026-06-01.

## Lineage

This id is a HELM wrapper around public matching dumps, not a new labeled corpus. Magellan is the 2016 system paper HELM's metadata cites. DeepMatcher is the 2018 dump layout HELM actually downloads. Narayan et al. 2022 is the prompting study; it reports F1, not HELM exact match. [entity_data_imputation](entity_data_imputation.md) is the paired HELM cleaning scenario. There is no Ditto or Magellan page in this repository.

## Saturation and contamination

No current HELM classic cell was parsed from the JavaScript frontend. Contamination risk is medium: labels sit in public CSVs and product titles are ordinary web text. A model that always emits No will look strong on accuracy and weak on F1. Compare only the same dataset, the same metric name, and the same shot count.

## How to run it

HELM: `entity_matching:dataset=Beer`, `entity_matching:dataset=Abt_Buy`, or `entity_matching:dataset=Dirty_iTunes_Amazon` for the paper's three-set mean. Other `dataset=` keys exist in the scenario class. Default is five-shot generation with a five-token cap. Do not compare a HELM exact-match column with a Narayan or Ditto F1. Reproducing an official HELM draw needs the pinned numpy state file.

## Reading the numbers

A high HELM exact-match score on Beer means the model emitted the gold Yes/No on that test split under five-shot generation. Because the test set is still imbalanced, that number can be a No-default. It does not measure blocking quality, multilingual matching, or dirty-text robustness unless you ran the dirty dump. Pair it with [entity_data_imputation](entity_data_imputation.md) if the claim is about structured-data wrangling, and say which dump and whether the column was accuracy or F1.
