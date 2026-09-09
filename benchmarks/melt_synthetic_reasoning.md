---
id: melt_synthetic_reasoning
name: "HELM MELT synthetic reasoning (abstract symbols)"
aliases:
  - "melt_synthetic_reasoning_pattern_match"
  - "melt_synthetic_reasoning_variable_substitution"
  - "melt_synthetic_reasoning_induction"
page_kind: benchmark
category: reasoning
subcategory: "Vietnamese LIME-style pattern match, substitution and induction"
status: unknown
summary: "HELM MELT's Vietnamese LIME-style tasks: match a pattern, substitute variables, or induce a rule over abstract symbols filled with Vietnamese words."
measures: >
  melt_synthetic_reasoning is HELM's Vietnamese abstract-symbol reasoning scenario,
  inspired by LIME (Wu et al., 2021). Each item is built from shuffled rule symbols
  X/Y/Z and math symbols +,-,*,=, a substitution into Vietnamese animal and fruit
  phrases, and the string after substitution. Three modes exist: pattern_match
  (pick the matching rule from four candidates), variable_substitution (apply a
  dictionary to a rule), and induction (recover the rule from two substituted
  results). Vietnamese words are fillers. The symbols are synthetic.
task_format: >
  Open generation. Run spec melt_synthetic_reasoning:mode={pattern_match,
  variable_substitution, induction}. Instruction "Hãy giải bài toán sau.", input
  noun Bài toán, output noun Lời giải, five in-context examples, stop at newline,
  max_tokens 50. HELM main_split is test.
metric:
  name: "quasi_exact_match (schema); run spec attaches exact-match metrics"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_melt.yaml and get_metadata set main_metric / main_name quasi_exact_match
    on test. get_melt_synthetic_reasoning_spec uses get_exact_match_metric_specs()
    plus Vietnamese generative-harms metrics. Report which column you read.
    Pattern-match items have four candidate rules; no official random baseline is
    stated. No human baseline is given.
dataset:
  size: 5000
  size_note: >
    MELTSyntheticReasoningScenario generates 1,000 train, 5,000 validation and
    5,000 test instances per mode with numpy RandomState(42). size is the 5,000-item
    test split HELM scores. Three modes exist, so a full three-mode run scores
    15,000 test items. There is no downloaded corpus. Tokens come from hardcoded
    ANIMALS and FRUITS lists in melt_synthetic_reasoning_scenario.py.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_synthetic_reasoning_scenario.py"
  license: "Apache-2.0"
  languages:
    - vi
  modalities:
    - text
  splits: "generated train 1,000 / validation 5,000 / test 5,000 per mode (seed 42)"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM MELT scenarios)"
  authors: []
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_synthetic_reasoning_scenario.py"
paper:
  title: "LIME: Learning Inductive Bias for Primitives of Mathematical Reasoning"
  arxiv: "2101.06223"
  url: https://arxiv.org/abs/2101.06223
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_synthetic_reasoning_scenario.py"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - melt_srn
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No MELT leaderboard URL resolved from opened HELM files. Saturation on the
    Vietnamese generated set is not established. The English HELM synthetic_reasoning
    paper figures are a different generator and language.
contamination:
  risk: low
  note: >
    Items are generated inside HELM from a fixed seed and a small Vietnamese
    vocabulary. They are not a crawled labelled test set. A model could still have
    seen English LIME or HELM's English synthetic_reasoning generator.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "melt_synthetic_reasoning:mode=pattern_match|variable_substitution|induction"
  opencompass: ""
  bigbench: ""
  other: >
    Source file helm.benchmark.scenarios.melt_synthetic_reasoning_scenario. Class
    name field is synthetic_reasoning, the same string as the English scenario.
    Distinct from melt_synthetic_reasoning_natural (melt_srn).
tags:
  - synthetic
  - reasoning
  - vietnamese
  - helm
  - melt
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/melt_synthetic_reasoning_scenario.py
    title: "HELM melt_synthetic_reasoning_scenario.py"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/melt_run_specs.py
    title: "HELM melt_run_specs.py (melt_synthetic_reasoning)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_melt.yaml
    title: "HELM schema_melt.yaml (quasi_exact_match; medical-domain group blurb)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_melt.conf
    title: "HELM run_entries_melt.conf"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2101.06223
    title: "LIME (Wu et al., 2021), arXiv:2101.06223"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_scenario.py
    title: "English HELM synthetic_reasoning_scenario.py (sibling generator)"
    accessed: "2026-09-08"
  - url: https://aclanthology.org/2024.findings-naacl.182/
    title: "Truong et al., NAACL Findings 2024 Vietnamese LLM evaluation (not cited by the scenario file)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`melt_synthetic_reasoning` is HELM's Vietnamese LIME-style probe. The generator builds a pattern from rule symbols X, Y, Z and math symbols, then fills those symbols with short Vietnamese animal or fruit phrases. In pattern_match, the model sees four candidate rules and one substituted result and must emit the true rule. In variable_substitution, it applies a "bởi …" dictionary to a rule. In induction, it sees two substituted results and must recover the rule. The language of the fillers is Vietnamese. The skill is symbol manipulation, not Vietnamese world knowledge.

schema_melt.yaml groups this under "MELT Scenarios" and still describes that group as medical-domain work. The opened task code is Vietnamese synthetic reasoning. This page follows the task code.

## How it is scored

Scenario metadata and schema_melt.yaml set `quasi_exact_match` on the test split. The run spec attaches HELM exact-match metrics and Vietnamese generative-harms metrics. A score is a fraction in 0-1. Pattern-match items have four candidates, but no official random baseline is given. No human baseline is given. Easy to mix this column with [melt_srn](melt_srn.md) `f1_set_match`.

## Dataset and licence

There is no download. `MELTSyntheticReasoningScenario` draws 1,000 train, 5,000 validation and 5,000 test puzzles per mode with seed 42. HELM scores the 5,000 test items. The generator lives in HELM, licensed Apache-2.0. A separate dataset licence is not stated. Hugging Face mirrors used by other MELT tasks are not used here.

## Who publishes it

Stanford CRFM ships the generator with HELM's MELT scenarios. The file cites LIME (Wu, Rabe, Li, Ba, Grosse, Szegedy; ICML 2021, arXiv:2101.06223). HELM authors of the Vietnamese wrapper are not listed in the Python file. Truong et al. (NAACL Findings 2024) published a 10-task Vietnamese LLM evaluation suite; the opened HELM scenario does not cite that paper, and the expansion of "MELT" is not stated in the schema. No MELT leaderboard URL was found in the opened schema or README-adjacent files.

## Lineage

This is not the English HELM task [synthetic_reasoning](synthetic_reasoning.md), which uses English animal and fruit fillers and English prompt nouns. It is not [melt_srn](melt_srn.md) (`melt_synthetic_reasoning_natural`), which writes Vietnamese if-then sentences and scores set-overlap F1. The scenario class `name` is `synthetic_reasoning`, the same string as the English class; runnable names still start with `melt_synthetic_reasoning:mode=`. Sibling MELT file-slugs include [melt_ir](melt_ir.md), [melt_knowledge](melt_knowledge.md) and [melt_translation](melt_translation.md).

## Saturation and contamination

Saturation is unknown. Contamination risk is low for the Vietnamese strings, which are produced at evaluation time from a tiny vocabulary. English LIME pretraining or HELM's English generator could still leak the pattern.

## How to run it

`run_entries_melt.conf` lists:

```
melt_synthetic_reasoning:model=text_code,mode=pattern_match
melt_synthetic_reasoning:model=text_code,mode=variable_substitution
melt_synthetic_reasoning:model=text_code,mode=induction
```

Five in-context examples come from the generated train split. max_tokens is 50. Do not report a score as `melt_synthetic_reasoning` without the mode. The natural-language runs are a different spec.

## Reading the numbers

A high quasi-exact match means the model copied the LIME pattern in Vietnamese fillers, often from the five-shot prompt. It is not proof of Vietnamese reading, medical knowledge, or multi-step proof. Compare modes separately, and pair a strong score with a non-synthetic Vietnamese set. Do not average it with [melt_srn](melt_srn.md).
