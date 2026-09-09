---
id: melt_srn
name: "HELM MELT synthetic reasoning (natural language)"
aliases:
  - "melt_synthetic_reasoning_natural"
  - "MELT SRN"
page_kind: benchmark
category: reasoning
subcategory: "Vietnamese synthetic rule-fact deduction"
status: unknown
summary: "HELM's Vietnamese synthetic-reasoning (natural) task: deduce attributes from generated Vietnamese rules and facts, scored by set-overlap F1."
measures: >
  MELT SRN generates Vietnamese rule-and-fact puzzles and asks the model to list what else must be
  true of a subject. Each item is a set of "if … then …" rules, one fact about a person, animal or
  plant, and a prompt asking what can be determined about that subject. The target is the set of
  attributes implied in one reasoning step. Easy mode always uses the specific subject (for example
  a name rather than "một người"). Hard mode substitutes more specific synonyms in the fact. The
  puzzles are synthetic Vietnamese, not mined text.
task_format: >
  Open generation. HELM instruction "Hãy giải quyết vấn đề sau.", input noun "Quy luật", three
  in-context examples, max 20 tokens. Difficulty is a run-spec argument: easy or hard. Main metric
  is f1_set_match on the generated test split.
metric:
  name: f1_set_match
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_melt.yaml and MELTSRNScenario.get_metadata both set main_metric f1_set_match and
    main_split test. The run spec also records iou_set_match and exact_set_match. No random or
    human baseline is stated in the scenario file or schema.
dataset:
  size: 5000
  size_note: >
    Generated at runtime with random.seed(42): 1,000 train, 5,000 validation and 5,000 test instances
    (MELTSRNScenario). The front-matter size is the 5,000-item test split HELM scores. There is no
    downloaded corpus. Subjects and attribute groups are hardcoded Vietnamese vocabularies in
    melt_srn_scenario.py.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_srn_scenario.py"
  license: ""
  languages:
    - vi
  modalities:
    - text
  splits: "generated train 1,000 / validation 5,000 / test 5,000 (seed 42)"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM MELT scenarios)"
  authors: []
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_srn_scenario.py"
paper:
  title: "Transformers as Soft Reasoners over Language"
  arxiv: "2002.05867"
  url: "https://arxiv.org/abs/2002.05867"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_srn_scenario.py"
released: ""
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
    No MELT leaderboard URL resolved (https://crfm.stanford.edu/helm/melt/latest/ returned 404).
    Saturation on the Vietnamese generated set is not established. The English RuleTakers paper
    that inspired the format reports 99% accuracy on its own synthetic English data and 95%+ on
    deeper chaining than seen in training, which is a different item generator and language.
contamination:
  risk: low
  note: >
    Items are generated inside HELM from a fixed seed and a small Vietnamese vocabulary. They are
    not a crawled labelled test set. A model could still have seen the English RuleTakers/LIME
    style, or HELM's own generator if that code was in pretraining, but the Vietnamese strings
    themselves are produced at evaluation time.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "melt_synthetic_reasoning_natural:difficulty=easy and melt_synthetic_reasoning_natural:difficulty=hard (run_entries_melt.conf). Scenario class name is sythetic_reasoning_natural (typo in source)."
  opencompass: ""
  bigbench: ""
  other: "Source file helm.benchmark.scenarios.melt_srn_scenario. Distinct from melt_synthetic_reasoning (pattern_match / variable_substitution / induction)."
tags:
  - synthetic
  - reasoning
  - vietnamese
  - helm
  - melt
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_srn_scenario.py"
    title: "HELM melt_srn_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/melt_run_specs.py"
    title: "HELM melt_run_specs.py (melt_synthetic_reasoning_natural)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_melt.yaml"
    title: "HELM schema_melt.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_melt.conf"
    title: "HELM run_entries_melt.conf"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2002.05867"
    title: "Transformers as Soft Reasoners over Language (Clark, Tafjord, Richardson, arXiv:2002.05867)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/README.md"
    title: "HELM README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

MELT SRN is HELM's Vietnamese synthetic reasoning task in natural language. The generator writes a handful of Vietnamese rules ("Nếu … là …, thì … là …"), one fact about a subject, and a question asking what else follows about that subject. Subjects are drawn from a fixed list of names, animals and plants. Attributes include size, colour, temperature and similar adjectives. Easy mode names the specific individual in the rules. Hard mode uses a more specific synonym in the fact (for example "mát mẻ" for "lạnh"). The model must emit the implied attributes. The language is Vietnamese. The skill is one-step deduction over explicit sentences, not world knowledge.

## How it is scored

The headline metric is `f1_set_match` on the generated test split. The run spec also logs `iou_set_match` and `exact_set_match`. schema_melt.yaml agrees on `f1_set_match` / `test`. Adaptation is generation with three in-context examples and a 20-token cap. Difficulty is `easy` or `hard`; those are separate run entries, not one mixed score. No human or random baseline is stated in the opened HELM files. The English RuleTakers paper that the file cites (Clark, Tafjord and Richardson, 2020) reports 99% accuracy on its own English generator and 95%+ on deeper chaining than seen in training, which is not this Vietnamese set.

## Dataset and licence

There is no download. `MELTSRNScenario.get_instances` draws 1,000 train, 5,000 validation and 5,000 test puzzles with `random.seed(42)`. HELM scores the 5,000 test items. A separate dataset licence is not stated; the generator lives in HELM's repository. The Hugging Face mirrors used by other MELT tasks are not used here. The class `name` field is `sythetic_reasoning_natural` (missing "n"), while the run spec and schema use `melt_synthetic_reasoning_natural` / `synthetic_reasoning_natural`.

## Who publishes it

Stanford CRFM ships the generator as part of HELM's MELT scenarios. The scenario file says it is inspired by "Transformers as Soft Reasoners over Language" (arXiv:2002.05867). schema_melt.yaml instead describes the group as synthetic reasoning based on LIME (Wu et al., 2021). Both citations are HELM's; this page opened the RuleTakers abstract and the schema, not the LIME proceedings. HELM authors of the Vietnamese wrapper are not listed in the file. No MELT leaderboard URL resolved. The expansion of "MELT" is not stated in the opened sources.

## Lineage

This is not the English RuleTakers benchmark and not HELM's other synthetic-reasoning file. `melt_synthetic_reasoning` (still queued in this census) covers pattern_match, variable_substitution and induction, with a different scenario class and exact-match scoring. Do not fold `melt_srn` into that id. Sibling file-slugs in this batch are `melt_ir` and `melt_knowledge`. There is no SuperGLUE overlap.

## Saturation and contamination

Saturation is unknown: no public scores were opened. Contamination risk is low relative to SuperGLUE. The items are generated at eval time from a seed and a short vocabulary, so they are not a static labelled dump that has sat on the web since 2019. A model could still have been trained on English synthetic rule-fact data of the same shape. Compare easy and hard separately; hard mode is the synonym substitution.

## How to run it

HELM run entries in `run_entries_melt.conf`:

`melt_synthetic_reasoning_natural:model=text_code,difficulty=easy`

`melt_synthetic_reasoning_natural:model=text_code,difficulty=hard`

There is no run spec spelled `melt_srn`; that is the source-file slug. Not confirmed in lm-evaluation-harness, OpenCompass, inspect_evals, or BIG-bench. Changing the seed would change the items; the published class hard-codes 42. HELM's README marks the project as in maintenance mode from 1 June 2026.

## Reading the numbers

An `f1_set_match` on MELT SRN is overlap between predicted and gold implied attributes on 5,000 generated Vietnamese puzzles. It is not proof of general logical reasoning, tool use, or Vietnamese world knowledge. Easy and hard are different generators. A score near 1.0 may mean the model copied the one-step pattern from the three-shot prompt. Pair it with a non-synthetic Vietnamese reasoning set, and do not treat it as the same number as `melt_synthetic_reasoning`.
