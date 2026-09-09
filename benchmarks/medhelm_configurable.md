---
id: medhelm_configurable
name: MedHELM Configurable
aliases: [MedHELM]
page_kind: family
category: domain
subcategory: biomedical evaluation framework
status: active
summary: MedHELM Configurable is a HELM scenario wrapper for configurable biomedical datasets, prompts, references, and metrics.
measures: This identifier names a configurable evaluation scenario rather than one fixed dataset. A benchmark configuration supplies a CSV dataset, prompt template, description, and one or more metrics.
task_format: Configuration-defined biomedical prompt with optional correct and incorrect answers.
metric: {name: "", direction: higher_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "The metric is selected by each configuration."}
dataset: {size: null, size_note: "Dataset size is configuration-dependent.", url: https://github.com/stanford-crfm/helm, license: "", languages: [], modalities: [text], splits: test, public_test_set: null}
publisher: {org: Stanford CRFM HELM, authors: [], url: https://github.com/stanford-crfm/helm}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No aggregate leaderboard is meaningful without a selected configuration.}
contamination: {risk: unknown, note: Each configuration has its own data and exposure profile.}
harness: {lm_eval: "", inspect_evals: "", helm: medhelm_configurable, opencompass: "", bigbench: "", other: ""}
tags: [medical, configurable, evaluation-framework]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medhelm_configurable_scenario.py
    title: HELM MedHELM configurable scenario
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/tree/main/src/helm/benchmark/run_specs/medhelm
    title: HELM MedHELM run specifications
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

MedHELM Configurable is a scenario wrapper for biomedical evaluations. It does not identify one fixed question set. A configuration supplies a description, CSV dataset, prompt file, and metric definitions, allowing different medical tasks to run through a common HELM path.

The scenario supports templates populated from dataset columns and can include correct and incorrect answer references. Its language and clinical domain therefore depend on the selected configuration.

## How it is scored

The configuration names the main metric and can list additional metrics. The wrapper supports ordinary reference-based grading and a `jury_score` path for LLM-as-judge evaluations. There is no single metric, maximum, or baseline for the identifier as a whole.

## Dataset and licence

Each configuration points to its own CSV dataset and prompt file. The wrapper requires a `correct_answer` column unless `jury_score` is the sole metric, and parses `incorrect_answers` as JSON when present. Aggregate size and licence are therefore configuration-specific and not established here.

## Who publishes it

The wrapper is maintained in Stanford CRFM’s HELM repository. The inspected source does not establish a separate MedHELM paper, author list, or leaderboard for this configurable identifier.

## Lineage

This is a family or framework page. Individual MedHELM configurations should be represented separately when their dataset and metric definitions are known. No fixed predecessor or successor was established.

## Saturation and contamination

Saturation and contamination cannot be assessed without selecting a configuration. A public prompt or dataset may have a different exposure profile from a restricted clinical set.

## How to run it

Use HELM’s `medhelm_configurable` scenario with a scenario name and configuration path. It verifies the prompt and dataset files, reads the CSV, fills template fields, and emits test instances. Record the exact configuration, prompt, dataset revision, and metric set.

## Reading the numbers

A score belongs to a particular MedHELM configuration, not to this wrapper in isolation. It may measure answer matching, judging, or another configured objective. Always report the configuration identity and metric definition before comparing results.

The wrapper’s flexibility makes bare benchmark names ambiguous. A complete citation should include the configuration file, data revision, prompt template, and metric list.
