---
id: compassbench_20_v1_1_public
name: "CompassBench v1.1 (public)"
aliases:
  - "compassbench_20_v1_1_public"
page_kind: subset
category: composite
subcategory: "publicly redistributed, item-reduced release of CompassBench v1.1's six-category composite"
status: unknown
summary: "The publicly redistributed, reduced-item release of CompassBench v1.1: the same six-category structure, with some code tasks restricted to their first five test cases."
measures: >
  Structurally identical to `compassbench_20_v1_1`: the same six category groups (language, knowledge,
  reasoning, math, code, agent) built from the same dataset-configuration code, confirmed by diffing
  the two ids' configuration files directly. Every difference found is mechanical rather than
  substantive -- dataset abbreviations gain a `_public` suffix and read from a separate
  `data/compassbench_v1.1.public/` directory instead of `data/compassbench_v1.1/` -- except for three
  code datasets (`mbpp_cn`, `sanitized_mbpp`, `TACO`), where the public configuration adds
  `test_range='[0:5]'`, restricting evaluation to each item's first five test cases instead of the
  full set. This id exists so a score can be reproduced outside OpenCompass's own leaderboard
  infrastructure without necessarily exposing the full item set those internal runs use.
task_format: "Identical task formats to compassbench_20_v1_1 (circular multiple choice, BLEU/ROUGE generation, pass@1 code execution); see that page."
metric:
  name: "same top-level 'average' construction as compassbench_20_v1_1, computed over the public item set"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No score for this specific public-item configuration was found in the sources read for this page; see compassbench_20_v1_1 for what is and is not established about headline numbers."
dataset:
  size_note: >
    Same category and constituent-dataset structure as compassbench_20_v1_1, with three code datasets
    (mbpp_cn, sanitized_mbpp, TACO) confirmed to run on only their first five test cases per item in
    this variant rather than the full set; no other item-count reduction was confirmed from the
    configuration diff for this page.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1_public"
  license: ""
  languages:
    - en
    - zh
  modalities:
    - text
    - code
  splits: "single evaluation set per constituent dataset, reduced to 5 test cases per item for mbpp_cn, sanitized_mbpp and TACO"
  public_test_set: true
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://rank.opencompass.org.cn/home"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1_public"
released: ""
last_updated: ""
lineage:
  family: compassbench_20_v1_1
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Not established; see compassbench_20_v1_1."
contamination:
  risk: high
  note: >
    Higher risk than the full-item id by construction: this is the copy meant for outside
    reproduction, so its exact items are more likely to circulate publicly and, over time, appear in
    training data, the ordinary risk of any openly re-runnable evaluation set. The three code datasets
    restricted to five test cases each somewhat limit how much of those specific items is exposed
    through published outputs, but do not eliminate the risk for the rest of the composite.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "compassbench_20_v1_1_public (opencompass/configs/datasets/compassbench_20_v1_1_public/{agent,code,knowledge,language,math,reason}; aggregated by opencompass/configs/summarizers/compassbench_v1_1_objective_public.py, which programmatically re-derives the full v1.1 summarizer by suffixing every subset name with _public)"
  bigbench: ""
  other: ""
tags:
  - composite
  - opencompass
  - compassbench
  - public-subset
  - chinese
  - bilingual
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1_public"
    title: "opencompass configs/datasets/compassbench_20_v1_1_public"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1_public/code/compassbench_v1_1_code_gen_986f01.py"
    title: "compassbench_20_v1_1_public code config, diffed directly against the compassbench_20_v1_1 version (test_range='[0:5]' on mbpp_cn, sanitized_mbpp, TACO)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/summarizers/compassbench_v1_1_objective_public.py"
    title: "compassbench_v1_1_objective_public.py summarizer (imports and mechanically re-suffixes the full v1.1 summarizer)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

Part of the [CompassBench v1.1](compassbench_20_v1_1.md) family.

## What it measures

This id is the publicly redistributed release of `compassbench_20_v1_1`'s six-category composite (language, knowledge, reasoning, math, code, agent), not a different evaluation. Diffing the two ids' configuration files directly shows every difference is mechanical: dataset names gain a `_public` suffix and point at a separate `data/compassbench_v1.1.public/` directory, and the aggregation summarizer is generated programmatically from the full-version summarizer by the same renaming rule. The one substantive change found is that three code datasets -- `mbpp_cn`, `sanitized_mbpp` and `TACO` -- are restricted to each item's first five test cases (`test_range='[0:5]'`) rather than the full set, consistent with OpenCompass holding back part of the full item set from open redistribution.

## Reading the numbers

A score on this id is not guaranteed to match a score on `compassbench_20_v1_1` for the same model, because the two evaluate different item sets on at least the three restricted code datasets, and possibly more that this page's configuration diff did not surface. Use this id when reproducing a CompassBench-style run outside OpenCompass's own infrastructure; use the parent id when the source is OpenCompass's own leaderboard. Read both against the parent page's category breakdown, since the category and scoring structure is otherwise identical.
