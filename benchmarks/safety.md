---
id: safety
name: "OpenCompass safety (Perspective toxicity)"
aliases:
  - "safety_gen"
  - "safety_datasets"
page_kind: benchmark
category: safety
subcategory: "OpenCompass generation-toxicity probe on a local prompt file"
status: unknown
summary: "OpenCompass runs free-text completions on prompts from a local safety.txt file and scores toxicity with Google Perspective API."
measures: >
  OpenCompass `safety` is a generation-toxicity probe, not a named
  standalone paper. The model sees one prompt per line from
  `./data/safety.txt` and writes a free-text continuation. Perspective
  API then scores TOXICITY on that continuation. English and Chinese
  are requested on the API call; the prompt file's language mix is not
  established here. This is not [helm_safety](helm_safety.md), not
  [autobencher_safety](autobencher_safety.md), and not the separate
  OpenCompass RealToxicPrompts config.
task_format: >
  Zero-shot GenInferencer. PromptTemplate is the raw `{prompt}` string.
  ZeroRetriever. SafetyDataset builds a Hugging Face DatasetDict with a
  test split only (idx, prompt). output_column is idx because there is
  no gold string. ToxicEvaluator does not use references.
metric:
  name: "Perspective toxicity (expected_max_toxicity, toxic_frac_valid, avg_toxicity_score)"
  direction: lower_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    ToxicEvaluator default threshold is 0.5. It returns
    expected_max_toxicity (max valid score), valid_frac, toxic_frac_valid
    (share of valid completions at or above 0.5), and avg_toxicity_score.
    Empty Perspective comments become toxicity_score -1 and are dropped
    as NaN. No random or human baseline is in the config.
dataset:
  size: null
  size_note: >
    SafetyDataset counts one non-empty line as one prompt. The file
    `./data/safety.txt` is not in the OpenCompass git tree opened here
    (local_mode True via get_data_path). OpenCompass dataset-index.yml
    has no `safety` entry, so a published item count was not established.
    OpenCompassData zip listings on release 0.2.2.rc1 also did not name
    the file in the HTML opened here.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/safety"
  license: ""
  languages: []
  modalities:
    - text
  splits: "test only; train_split and test_split both set to test"
  public_test_set: true
publisher:
  org: "OpenCompass"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/safety"
released: "2023"
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
    No public leaderboard or score table for this config was opened.
    Perspective scores are not comparable to refusal accuracy on
    [helm_safety](helm_safety.md).
contamination:
  risk: unknown
  note: >
    If safety.txt is distributed in OpenCompass data zips, the prompts
    are public. The file was not readable from the repository, so overlap
    with RealToxicPrompts or other toxicity sets is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "safety"
  bigbench: ""
  other: "safety_datasets in safety_gen.py re-exports safety_gen_7ce197.py; evaluator ToxicEvaluator (Perspective API, env PerspectiveAPIkey)."
tags:
  - safety
  - toxicity
  - perspective-api
  - opencompass
  - generation
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/safety/safety_gen.py"
    title: "safety_gen.py (re-exports safety_datasets from safety_gen_7ce197)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/safety/safety_gen_7ce197.py"
    title: "safety_gen_7ce197.py (SafetyDataset, ./data/safety.txt, ToxicEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/safety.py"
    title: "SafetyDataset loader (one prompt per non-empty line, test split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_toxic_evaluator.py"
    title: "ToxicEvaluator (Perspective TOXICITY, default thr 0.5, en/zh)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/dataset-index.yml"
    title: "OpenCompass dataset-index.yml (no safety dataset entry; RealToxicPrompts is separate)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/docs/en/get_started/installation.md"
    title: "OpenCompass dataset preparation (OpenCompassData zips into ./data)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/safety"
    title: "OpenCompass configs/datasets/safety directory (two Python files)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-070 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-070"
---

## What it measures

OpenCompass `safety` measures how toxic a model's completions are on a list of prompts. Each item is one line from `./data/safety.txt`. The model generates freely. Google Perspective API then assigns a TOXICITY score to that text.

It is a generation probe, not a refusal quiz and not a comment classifier. It is not [helm_safety](helm_safety.md), not [autobencher_safety](autobencher_safety.md), and not OpenCompass RealToxicPrompts, which has its own config directory.

## How it is scored

`ToxicEvaluator` calls Perspective's comment analyzer with attribute TOXICITY and languages `en` and `zh`. Default threshold is 0.5. Reported numbers are expected_max_toxicity, valid_frac, toxic_frac_valid, and avg_toxicity_score. Lower toxicity is better. Empty comments are invalid (score -1) and dropped. You need a `PerspectiveAPIkey`. There is no gold label.

## Dataset and licence

The loader keeps every non-empty line. The prompt file is not in the git tree; `get_data_path(..., local_mode=True)` expects it under `./data`. OpenCompass dataset-index.yml does not list a `safety` dataset, so the line count is not established. OpenCompass code is Apache-2.0. The prompt file's own licence is not stated in the files opened here.

## Who publishes it

OpenCompass (open-compass/opencompass). The config is `safety_gen.py` pointing at `safety_gen_7ce197.py`. No dedicated paper is attached in dataset-index.yml. The GitHub repository was created 2023-06-15; a finer first-commit date for this config was not read.

## Lineage

`ToxicEvaluator` comments that it is normally used for RealToxicPrompts but can score toxicity in general. RealToxicPrompts remains a separate OpenCompass dataset with its own paper (arxiv 2009.11462). Do not treat this id as an alias of that eval, or of HELM Safety.

## Saturation and contamination

No score table for `safety_datasets` was opened, so saturation is unknown. Prompt leakage cannot be judged until `safety.txt` is identified. Completions are judged live by Perspective, so the metric is not a fixed public answer key.

## How to run it

Import `safety_datasets` from `opencompass.configs.datasets.safety.safety_gen`. Place `data/safety.txt` locally. Set `PerspectiveAPIkey`. Zero-shot generation only; the 7ce197 file is the current prompt version. Numbers need the same Perspective key, threshold, and prompt file to compare.

## Reading the numbers

A low toxic_frac_valid means few completions crossed 0.5 on Perspective, not that the model refuses harmful asks. Max toxicity is one worst completion. Compare only against other Perspective runs on the same file. For refusal and policy coverage use [helm_safety](helm_safety.md) or a dedicated red-team set.
