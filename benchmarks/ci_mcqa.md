---
id: ci_mcqa
name: CIMCQA
aliases: []
page_kind: benchmark
category: domain
subcategory: "CS education concept-inventory multiple-choice questions"
status: unknown
summary: A HELM scenario for CS-education concept-inventory multiple-choice questions that cannot be run outside its authors because the item data is private.
measures: >
  ci_mcqa is the internal name HELM (Stanford's Holistic Evaluation of Language Models) uses for a
  scenario class called CIMCQAScenario, registered as the run spec "ci_mcqa". The scenario's own
  docstring describes it as "a multiple-choice question answering (MCQA) dataset designed to study
  concept inventories in CS Education." A concept inventory is a standardized instrument used in
  education research to detect specific, well-documented misconceptions a learner holds about a
  subject; the format originated in physics education and has since been adapted to other fields,
  including, here, computer science. Each item is a short question with several lettered answer
  options and exactly one option marked correct in the source data.
task_format: >
  Multiple-choice question answering; HELM's adapter instructs the model to answer with a single
  letter chosen from the options given. The scenario code reads a separate test split and a
  (normally disabled) few-shot training split from local files.
metric:
  name: "exact match (single-letter multiple-choice accuracy)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM scores this run spec with its standard exact-match metric family. No random or human
    baseline is established here: the scenario cannot be run outside its authors and no results were
    found published anywhere, and a random baseline would in any case depend on the number of options
    per question, which is set by the private data and not confirmed by this research.
dataset:
  size: null
  size_note: >
    Not established. CIMCQAScenario.get_instances reads two files that ship with neither HELM nor any
    public mirror this research could find: restricted/bdsi_multiple_answers_removed.json (test split)
    and restricted/mock_bdsi_multiple_answers_removed.json (a training split used only if a
    commented-out few-shot code path is enabled). The scenario class also names a Google Drive link as
    its DATASET_DOWNLOAD_URL; this research did not attempt to access it, since the data is by
    definition restricted. No item count, subject breakdown or sample question could be read from any
    source available here.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "not established (a private test split and a private, normally-unused training split)"
  public_test_set: false
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/ci_mcqa_scenario.py"
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
    No score for ci_mcqa on any model was found published anywhere. The run spec is absent from every
    one of HELM's schema_*.yaml files, the configuration files that drive HELM's own public leaderboard
    tables, which is consistent with the scenario being archival rather than actively reported.
contamination:
  risk: low
  note: >
    The underlying question data has never had a public release that this research could find; access
    is explicitly gated behind a private link controlled by the paper's (unidentified) authors. That
    does not rule out the item text appearing elsewhere, but nothing reviewed here suggests it is
    otherwise public.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "ci_mcqa"
  opencompass: ""
  bigbench: ""
  other: >
    Registered only in HELM's experimental_run_specs.py (function get_ci_mcqa_spec, run spec name
    "ci_mcqa", group "CIMCQA"); not present in any of HELM's schema_*.yaml display configs, so no
    HELM-hosted leaderboard surfaces it.
tags:
  - cs-education
  - concept-inventory
  - multiple-choice
  - helm
  - non-reproducible
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/ci_mcqa_scenario.py"
    title: "CIMCQAScenario source, stanford-crfm/helm"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/experimental_run_specs.py"
    title: "get_ci_mcqa_spec run spec, stanford-crfm/helm experimental_run_specs.py"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/pull/2465"
    title: "Adding CIMCQA Scenario (#2465), stanford-crfm/helm"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ci_mcqa is the internal name HELM (Stanford's Holistic Evaluation of Language Models) uses for a scenario class called `CIMCQAScenario`, registered as the run spec "ci_mcqa". The scenario's own docstring describes it plainly: "CIMCQA is a multiple-choice question answering (MCQA) dataset designed to study concept inventories in CS Education." A concept inventory is a standardized instrument used in education research to detect specific, well-documented misconceptions a learner holds about a subject -- the format originated in physics education (the Force Concept Inventory is the best-known example) and has since been adapted to other fields, including, here, computer science. Each item is a short question with several lettered answer options and exactly one option marked correct in the source data.

Beyond that docstring, this page could not establish more about the underlying test: no paper, author list, or public description of which CS concepts the inventory probes was found in HELM's own repository or through a general search for the phrase "concept inventory" alongside computer science and large language models.

## How it is scored

HELM's run spec (`get_ci_mcqa_spec`) wires CIMCQA to a standard multiple-choice-joint adapter and HELM's exact-match metric family: the model is told to answer with the single letter of the correct option, and its answer is compared against the gold letter. The adapter's boilerplate instructions illustrate the format with an example that has options A through F, but that instruction text is shared across several of HELM's experimental multiple-choice scenarios, not evidence that CIMCQA questions actually carry six options; the true number of options per question is set by the private data itself and was not confirmed here.

## Dataset and licence

This is the central fact about ci_mcqa: it cannot be run by anyone outside the scenario's original authors. Its `get_instances` method reads two files that ship with neither HELM nor any public mirror -- `restricted/bdsi_multiple_answers_removed.json` for the test split and `restricted/mock_bdsi_multiple_answers_removed.json` for a training split (used only if a commented-out few-shot code path is turned on) -- and the scenario class names a Google Drive link as its `DATASET_DOWNLOAD_URL`, which this research did not attempt to open since access is by definition restricted. The scenario's own docstring is explicit: "NOTE: This code is for archival purposes only. The scenario cannot be run because it requires private data. Please contact the paper authors for more information." No item count, subject list, licence or sample question could be established from any source available to this research; `dataset.size` is left empty rather than guessed.

## Who publishes it

The HELM scenario code was contributed to stanford-crfm/helm by GitHub user Murtz5253 in pull request #2465, merged 10 June 2024, with no description beyond its title, "Adding CIMCQA Scenario." Stanford's CRFM team maintains the HELM codebase that hosts this scenario, but that is a statement about who maintains the harness, not who created the underlying test: the scenario's own docstring attributes the data to "a pre-publication paper" without naming it, and no arXiv preprint, workshop paper or blog post describing a CS-education concept-inventory MCQA dataset under this name was located during this research.

## Lineage

No predecessor, successor or variant of ci_mcqa is known. It is easy to confuse with HELM's separate CodeInsights family of scenarios (`codeinsights_correct_code`, `codeinsights_student_coding`, `codeinsights_student_mistake`, `codeinsights_code_efficiency`, `codeinsights_edge_case`), which live in neighbouring files under HELM's scenarios and run-specs directories and also evaluate CS-education material -- C++ solutions to foundational programming-course assignments, mimicking student coding style -- but these are entirely separate scenarios with their own classes, datasets and run specs; nothing in either code path references the other.

## Saturation and contamination

No score for ci_mcqa on any model was found published anywhere, so saturation is recorded as unknown rather than guessed. The run spec is absent from every one of HELM's `schema_*.yaml` files, the configuration files that drive HELM's own public leaderboard tables (`schema_classic.yaml`, `schema_lite.yaml`, `schema_capabilities.yaml` and the rest), consistent with the scenario being archival rather than live. Contamination risk is assessed as low: the question data has never had a public release that this research could find, and access is explicitly gated behind a private link, which limits, without fully ruling out, the chance the exact item text sits in a model's training data.

## How to run it

In principle, HELM's run command with the run-spec name `ci_mcqa` would invoke `CIMCQAScenario` through HELM's standard pipeline. In practice this only works for someone holding the private `restricted/` data files, and the code path is not exercised by HELM's own continuous evaluation. There is no lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation of this benchmark.

## Reading the numbers

There are no numbers to read: this page exists to record what the `ci_mcqa` id names inside HELM's source rather than to report a score, since none could be found. If a model card or leaderboard ever shows a `ci_mcqa` figure, treat it cautiously and ask for its source, since the reference implementation cannot be independently re-run or checked against the original data by a third party, and the item count, subject coverage and difficulty of the underlying concept inventory are all unconfirmed from any public source available to this research.
