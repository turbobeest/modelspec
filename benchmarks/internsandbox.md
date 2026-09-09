---
id: internsandbox
name: "InternSandbox"
aliases:
  - "InternSandboxBenchmark"
  - "internsandbox"
page_kind: benchmark
category: reasoning
subcategory: "OpenCompass suite of 80 verifiable puzzle, logic and BBH-style sandboxes"
status: unknown
summary: "OpenCompass generation eval over 80 named sandboxes, graded by intern_sandbox verifiers on local InternSandboxBenchmark_verified_V0.3.1 jsonl."
measures: >
  InternSandbox, in OpenCompass, is a battery of short reasoning environments.
  Each sandbox is a named jsonl (sudoku, maze, game24, BBH-style tasks,
  KOR-Bench-style logic/operation/puzzle names, and other grid puzzles).
  The model sees a prompt and writes a free-text answer. InternSandboxEvaluator
  imports intern_sandbox, builds {data_source}Sandbox, and calls verify_score
  on the prediction against json-encoded ground_truth. It is a verifiable
  puzzle/logic suite, not a code-execution jail.
task_format: >
  Zero-shot chat generation. The template sets a system line "You are a
  helpful assistant." and a human {prompt}. GenInferencer produces the
  completion. Scoring is per-sandbox accuracy: mean verify_score over the
  jsonl, with short_penalty and format_penalty left false in the shipped
  config. Dataset abbrs are internsandbox-{sandbox}.
metric:
  name: "accuracy (mean intern_sandbox verify_score per sandbox)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each sandbox has its own verifier. No uniform chance rate or human
    baseline is stated in the OpenCompass config files opened here.
dataset:
  size: null
  size_note: >
    OpenCompass lists 80 sandbox names in internsandbox_gen_44b982.py and
    loads ./data/InternSandboxBenchmark_verified_V0.3.1/{sandbox}.jsonl with
    local_mode=True. Row counts in those jsonl files were not opened (the
    data path is local, not in the GitHub configs tree). InternBootcamp's
    paper describes a related Bootcamp-Eval set of 9,232 samples across 118
    tasks; that count is not confirmed to be this V0.3.1 dump.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/internsandbox"
  license: ""
  languages: []
  modalities:
    - text
  splits: "one jsonl per sandbox, used as the eval set"
  public_test_set: false
publisher:
  org: "OpenCompass; related InternLM InternBootcamp work from Shanghai AI Laboratory"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/internsandbox"
paper:
  title: "InternBootcamp: Boosting LLM Reasoning with Verifiable Task Scaling"
  arxiv: "2508.08636"
  url: "https://arxiv.org/abs/2508.08636"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/InternLM/InternBootcamp"
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
    No OpenCompass leaderboard cell for internsandbox was read. The
    InternBootcamp paper reports that frontier models still underperform on
    Bootcamp-Eval; that figure is not copied here as an InternSandbox score.
contamination:
  risk: unknown
  note: >
    Many sandbox names overlap public puzzles and public benchmarks (BBH,
    KOR-Bench, Game of 24). The V0.3.1 jsonl files themselves were not
    opened, so reuse versus fresh generation is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "internsandbox"
  bigbench: ""
  other: >
    Import internsandbox_datasets from
    opencompass.configs.datasets.internsandbox.internsandbox_gen (re-exports
    internsandbox_gen_44b982). Requires the intern_sandbox package at
    scoring time. local_mode=True; data are not downloaded by the loader.
tags:
  - opencompass
  - internlm
  - puzzles
  - logic
  - verifiable-rewards
  - reasoning
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/internsandbox/internsandbox_gen.py"
    title: "internsandbox_gen.py (re-exports internsandbox_datasets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/internsandbox/internsandbox_gen_44b982.py"
    title: "internsandbox_gen_44b982.py (80 sandbox names, GenInferencer, local V0.3.1 path)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/internsandbox.py"
    title: "InternSandboxDataset and InternSandboxEvaluator (intern_sandbox verify_score)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2508.08636"
    title: "InternBootcamp paper abstract (arXiv:2508.08636, 12 Aug 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2508.08636"
    title: "InternBootcamp HTML (Bootcamp-Eval 9,232 samples / 118 tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/InternLM/InternBootcamp/main/README.md"
    title: "InternBootcamp/InternAgentHarness README (eval entry points; not the OC jsonl)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0 (harness, not the local jsonl)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-050 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-050"
---

## What it measures

OpenCompass InternSandbox asks a chat model to solve one prompt from a named sandbox and then hands the completion to a programmatic verifier. The shipped list has 80 names: grid puzzles (sudoku, maze, nonograms, minesweeper), arithmetic puzzles (game24, cryptomath), many `korLogic*` / `korOperation*` / `korPuzzle*` tasks, and several `bbeh*` tasks that echo BIG-Bench Hard. The skill is verifiable puzzle and logic reasoning, not tool use in a live OS sandbox.

This page documents the OpenCompass config, not every InternBootcamp environment. InternBootcamp (Li et al., 2025) is a large generator-and-verifier framework with a Bootcamp-Eval set of 9,232 items over 118 tasks. The OpenCompass path is `InternSandboxBenchmark_verified_V0.3.1`. Those two dumps were not shown to be the same file.

## How it is scored

Each sandbox is a separate dataset. The evaluator averages `verify_score` over its jsonl. `short_penalty` and `format_penalty` are off in the published config. There is no official macro-average in that file; reporters who mean across 80 sandboxes must say so. Do not mix a verifier score with regex exact match on [korbench](korbench.md) or [bbh](bbh.md).

## Dataset and licence

Jsonl files live at a local data path and were not counted here. Language is not declared. OpenCompass is Apache-2.0; that does not licence the jsonl. InternBootcamp's GitHub default branch did not yield a LICENSE file in this research pass.

## Who publishes it

OpenCompass hosts the dataset config. Scoring imports a third-party `intern_sandbox` module (not the `internbootcamp` package name). The closest paper is InternBootcamp (Li et al., arXiv:2508.08636, 12 August 2025, Shanghai AI Laboratory). The OpenCompass YAML does not cite that paper, so this page does not treat those authors as InternSandbox config authors. The InternLM GitHub default branch README is now InternAgentHarness; it is not the OpenCompass jsonl dump.

## Lineage

Related evaluations in this repository include [korbench](korbench.md) (Knowledge-Orthogonal Reasoning, not Korean), [bbh](bbh.md) and [game24](game24.md). InternSandbox reuses those *kinds* of tasks under verifier classes. It is not an alias of those pages. It is also not WildClawBench or a container-escape CTF.

## Saturation and contamination

No OpenCompass table for these 80 abbrs was read. Several names match public benchmarks, so treat leakage as possible and unmeasured. The jsonl generation recipe was not opened.

## How to run it

Install OpenCompass, install `intern_sandbox`, place `InternSandboxBenchmark_verified_V0.3.1` under `./data/`, then import `internsandbox_datasets`. Compare one sandbox at a time unless the reporter publishes a defined mean. Changing `short_penalty` or `format_penalty` changes the number.

## Reading the numbers

A high InternSandbox accuracy means the verifier accepted the model's text on that sandbox's jsonl. It does not mean the model matched the official KOR-Bench or BBH protocol, and it does not mean the 9,232-item Bootcamp-Eval score. Quote the sandbox name, V0.3.1, and penalty flags. If the jsonl cannot be shared, the number is not auditable.
