---
id: race_based_med
name: "RaceBias (HELM race_based_med)"
aliases:
  - "RaceBias"
  - "race-based med"
  - "RaceBasedMedScenario"
page_kind: benchmark
category: safety
subcategory: "HELM yes/no classification of stored medical Q-A pairs for race-based, harmful, or inaccurate content"
status: unknown
summary: "HELM MedHELM task: read a medical question and a stored model answer, then say whether that answer contains race-based, harmful, or inaccurate content."
measures: >
  race_based_med is HELM's RaceBias scenario, built from the supplementary Word file of
  Omiye et al., npj Digital Medicine 2023. The original paper asked four commercial models
  nine race-medicine questions, five times each, and judged whether the generations
  repeated harmful race-based content. HELM does not regenerate those answers. It feeds a
  stored question-answer pair and asks a new model to answer yes (A) or no (B) to whether
  the answer involves harmful, inaccurate, and/or race-based content. English medical text.
  This is a bias-detection classifier, not the original generation study, and not [race](race.md).
task_format: >
  Two-way multiple choice. HELM run spec race_based_med uses ADAPT_MULTIPLE_CHOICE_JOINT,
  zero in-context examples, instructions "Answer A for yes, B for no.", and an output noun
  that asks for only A or B. Scenario labels are yes/no after mapping True/False from the
  parsed supplement. Red font in the Word file marks True.
metric:
  name: exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: null
  baseline_note: >
    Binary A/B. schema_medhelm.yaml lists exact_match on the test split. The scenario
    get_metadata() main_metric is exact_match. No human classifier baseline is stated.
    The original paper scored generations qualitatively, not this yes/no task.
dataset:
  size: 180
  size_note: >
    PubMed/Nature methods: nine questions, five interrogations, four models (Bard, ChatGPT,
    Claude, GPT-4), 45 responses per model, 180 generations. The abstract also says "eight
    different scenarios"; this page uses the methods count. HELM downloads the Springer
    .docx (41746_2023_939_MOESM1_ESM.docx) and parses "Run N: …" blocks, labelling True when
    a run's font colour is RGB (255, 0, 0). Live HELM instance count after that parse was not
    re-executed here.
  url: "https://www.nature.com/articles/s41746-023-00939-z#Sec3"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT only; no train split (max_train_instances=0)"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM / MedHELM wrap); original study from Stanford / collaborators"
  authors:
    - "Jesutofunmi A. Omiye"
    - "Jenna C. Lester"
    - "Simon Spichak"
    - "Veronica Rotemberg"
    - "Roxana Daneshjou"
  url: "https://www.nature.com/articles/s41746-023-00939-z"
paper:
  title: "Large language models propagate race-based medicine"
  arxiv: ""
  url: "https://www.nature.com/articles/s41746-023-00939-z"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/race_based_med_scenario.py"
released: "2023-10"
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
    No MedHELM leaderboard cell was opened for this scenario. The original paper reports that
    all four 2023 commercial models produced some race-based answers; that is a generation
    result, not a RaceBias classification score.
contamination:
  risk: medium
  note: >
    The nine questions and the supplement are public (CC BY 4.0) since October 2023. Gold
    yes/no labels are encoded as red text in that file, so they are recoverable. The item
    set is tiny and the questions are distinctive, which makes memorisation of the prompts
    plausible. Whether models have seen the red-text labels as supervision is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "race_based_med"
  opencompass: ""
  bigbench: ""
  other: >
    MedHELM run spec get_race_based_med_spec in medhelm_run_specs.py. Scenario name race_based_med;
    display_name RaceBias. Tags on the scenario class: knowledge, reasoning, biomedical.
tags:
  - helm
  - medhelm
  - medical
  - bias
  - safety
  - multiple-choice
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/race_based_med_scenario.py"
    title: "HELM race_based_med_scenario.py (RaceBias; Word supplement URL; red-text True/False; yes/no references)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "medhelm_run_specs.py get_race_based_med_spec (zero-shot MC joint, exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml RaceBias group (exact_match, test split)"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41746-023-00939-z"
    title: "Omiye et al., npj Digit. Med. 6, 195 (2023): nine questions, five runs, four models, CC BY 4.0"
    accessed: "2026-09-08"
  - url: "https://pubmed.ncbi.nlm.nih.gov/37864012/"
    title: "PubMed 37864012 (nine questions × five runs × four models; 45 responses per model)"
    accessed: "2026-09-08"
  - url: "https://static-content.springer.com/esm/art%3A10.1038%2Fs41746-023-00939-z/MediaObjects/41746_2023_939_MOESM1_ESM.docx"
    title: "Official supplement DOCX parsed by HELM (Bard / ChatGPT / Claude / GPT-4 Run blocks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not the article licence)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-068 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-068"
---

## What it measures

HELM's race_based_med scenario, displayed as RaceBias, asks a model to judge a stored medical Q-A pair. The prompt shows a question such as how to estimate eGFR for a Black woman, plus a model-written answer, and requires A (yes) or B (no) on whether that answer involves harmful, inaccurate, and/or race-based content. Items come from Omiye et al. 2023, who queried Bard, ChatGPT, Claude, and GPT-4 on nine race-medicine questions five times each. HELM does not rerun those models. It classifies the published answers. English only. This is not the [RACE](race.md) reading exam and not a clinical accuracy test.

## How it is scored

schema_medhelm.yaml names exact_match on the test split. The run spec is zero-shot joint multiple choice with "Answer A for yes, B for no." Chance is one half. The original paper did not report this classification metric; it described whether generations repeated race-based medicine. Do not treat a RaceBias exact-match number as a replication of Table 1 in Omiye et al.

## Dataset and licence

The methods sentence is 9 × 5 × 4 = 180 stored responses. The abstract also says “eight different scenarios”; this page follows the nine-question methods count. HELM fetches the Springer supplementary .docx and walks paragraphs that start with "Run ", taking True when a following run is red (255, 0, 0). The article is CC BY 4.0. The Word file is public. There is no held-out split. HELM's live instance count after that parse was not re-executed here.

## Who publishes it

Jesutofunmi A. Omiye, Jenna C. Lester, Simon Spichak, Veronica Rotemberg, and Roxana Daneshjou published the source study in npj Digital Medicine on 20 October 2023 (doi 10.1038/s41746-023-00939-z). Stanford CRFM packaged the supplement as a MedHELM scenario named race_based_med / RaceBias. No separate RaceBias paper was found.

## Lineage

The HELM task is a downstream classifier over Omiye et al.'s generations, not a successor exam. It does not share items with [race](race.md) (ReAding Comprehension from Examinations). No predecessor id in this repository measures the same yes/no medical-bias judgement. Later MedHELM scenarios such as medhallu score other medical failure modes and are not variants of this file.

## Saturation and contamination

No current RaceBias leaderboard cell was read, so saturation is unknown. All four 2023 models in the source paper produced at least some race-based answers; that finding is about generation, not about today's classifiers on this tiny set. The questions and red-text labels have been public since 2023, so prompt memorisation is plausible. Risk is recorded as medium rather than high because the labelled task is a HELM parse of a supplement, not a widely copied exam dump.

## How to run it

HELM: `race_based_med` via `get_race_based_med_spec` in `medhelm_run_specs.py`. The scenario class is `RaceBasedMedScenario`. It needs python-docx to parse the download. Metric specs are `get_exact_match_metric_specs()`. Zero-shot only. No lm-eval, inspect_evals, OpenCompass, or BIG-bench task with this name was found.

## Reading the numbers

A high exact-match score means the model agreed with the supplement's red-text flags on these stored answers. It does not mean the model itself avoids race-based medicine in free generation. With roughly 180 items, a few disagreements move the score a lot. Compare only to other HELM RaceBias runs that use the same A/B adapter. Pair it with a generation eval if the decision you care about is what the model would write to a patient, not whether it can tag an old Bard paragraph.
