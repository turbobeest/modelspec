---
id: niah
name: "NIAH (Inspect Evals Needle in a Haystack)"
aliases:
  - "inspect_evals/niah"
  - "Needle in a Haystack (Inspect Evals)"
page_kind: benchmark
category: long-context
subcategory: "Inspect Evals in-context retrieval over NeedleBench English haystacks"
status: active
summary: "Inspect Evals NIAH: plant English needles in long haystacks and score recall with a 1–10 LLM judge across a length-by-depth grid."
measures: >
  Inspect Evals niah tests whether a long-context model can retrieve a planted
  fact (the needle) from a long English passage (the haystack). The
  implementation, contributed by Owen Parsons, builds a length-by-depth grid
  at evaluation time. Haystacks and needle phrases come from Hugging Face
  opencompass/NeedleBench (en_haystack_texts and retrieval_needles, English
  needles only). This is the Inspect Evals task named niah, not NVIDIA
  [ruler](ruler.md) niah_* tasks, not OpenCompass [needlebench](needlebench.md)
  keyword scoring, and not Greg Kamradt's original notebook as a harness.
task_format: >
  Generated long prompt in; short free-text answer out; second model call
  grades the answer. Default grid: min_context 10000, max_context 120000,
  n_contexts 15, n_positions 15, n_needles 1, sample_method fixed, n_runs 1
  (eval.yaml dataset_samples 225). Solver inserts the needle then applies
  MAIN_PROMPT. Scorer is model_graded_qa with Kamradt-style 1/3/5/7/10
  instructions, grade_pattern r"(\\d+)", and history limited to the needle
  question so the judge does not reread the haystack.
metric:
  name: overall_accuracy (mean of numeric LLM-judge grades; also per-length and per-position means)
  direction: higher_is_better
  unit: ""
  max_score: 10.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The judge prompt asks for 1, 3, 5, 7, or 10 only. README heatmaps treat
    those integers as the plotted scores and note that judges often emit 1 or
    10 (mistral-small sometimes emitted 0). subset_accuracy_combinations
    averages the numeric Score.value as overall_accuracy. Whether inspect_ai
    rescales that capture to 0–1 was not confirmed from inspect_ai source
    opened here; the rubric maximum is 10. No human-rater figure is published
    for this Inspect grid.
dataset:
  size: 225
  size_note: >
    eval.yaml dataset_samples is 225, matching the default 15×15×1 grid, not
    a frozen item file. Size changes with min_context, max_context,
    n_contexts, n_positions, n_needles, and n_runs. README experimental plots
    used a different grid (9 lengths from 2k to 27k tokens, 10 positions,
    n_runs 10 or 5) and are not the default 225. Hugging Face assets are
    pinned at revision 651d7c8f4eae047b3f47ca24e92e09f2acf64af5.
  url: "https://huggingface.co/datasets/opencompass/NeedleBench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "generated at eval time from NeedleBench test configs; no train split"
  public_test_set: true
publisher:
  org: "UK AI Security Institute (Inspect Evals); NeedleBench assets from OpenCompass"
  authors:
    - "Owen Parsons"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/niah"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/niah"
released: "2025-12"
last_updated: "2026-08"
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
    README heatmaps for mistral-small-latest and mistral-medium-latest are
    images without a published overall_accuracy table. The text says the
    medium model scored worse than the small model, partly from judge
    "unrelated" refusals. No numeric top cell was transcribed from those
    plots. Default 10k–120k grid results were not published in the README.
contamination:
  risk: medium
  note: >
    Needles, questions, and haystacks are public in opencompass/NeedleBench.
    Placement is generated at run time, so the exact prompt is not a fixed
    dump, but the facts and essays are. Scoring is a second model call
    (default: the active task model). Judge errors (treating fictional
    needles as world-knowledge fails) can look like retrieval fails.
harness:
  lm_eval: ""
  inspect_evals: "niah"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect eval inspect_evals/niah; extra inspect-evals[niah] (pandas).
    eval.yaml version 3-A, group Reasoning, dataset_samples 225. eval.yaml
    arxiv field points at 2407.01437 (Larimar), which is not this task's
    method paper.
tags:
  - long-context
  - retrieval
  - needle-in-a-haystack
  - inspect-evals
  - llm-judge
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/README.md"
    title: "Inspect Evals niah README (grid defaults, Kamradt rubric, changelog through 3-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/eval.yaml"
    title: "eval.yaml (version 3-A, dataset_samples 225, NeedleBench pin, arxiv 2407.01437)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/niah.py"
    title: "niah.py (defaults 10k–120k, 15×15, TOKEN_BUFFER 100)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/utils/dataset_generation.py"
    title: "dataset_generation.py (NeedleBench configs, English needle filter, revision pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/utils/scoring.py"
    title: "scoring.py (1–10 rubric, overall_accuracy, unscored parse misses in 3-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/niah/utils/prompting.py"
    title: "prompting.py (MAIN_PROMPT and question wrapper)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/NeedleBench"
    title: "opencompass/NeedleBench dataset card (MIT; created 2024-07-21)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2407.11963"
    title: "NeedleBench paper (dataset source; not cited in niah README)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2407.01437"
    title: "Larimar NIAH paper (eval.yaml arxiv field; different work)"
    accessed: "2026-09-08"
  - url: "https://github.com/gkamradt/LLMTest_NeedleInAHaystack"
    title: "Kamradt Needle in a Haystack (current main README is v2 CLI; 1-10 rubric not on that page)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-062 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-062"
---

## What it measures

Inspect Evals niah hides one English fact in a long English passage and asks the model to retrieve it. Context length and needle depth vary on a grid. Owen Parsons contributed the Inspect task. Haystacks and needles are loaded from Hugging Face `opencompass/NeedleBench`, then trimmed and inserted with tiktoken. Needles that are not labelled English are dropped. The test is retrieval under length, not multi-needle reasoning and not OpenCompass [needlebench](needlebench.md) keyword scoring.

## How it is scored

A task model answers from the full haystack. A judge model then grades only the question, the gold, and that answer on a 1–10 rubric that the Inspect README attributes to Kamradt. The Kamradt main README opened here is a v2 CLI and does not reprint that list. The haystack is not passed to the judge. Code averages the numeric grades as `overall_accuracy` and as per-length and per-position means. Version 3-A (2026-08-20) treats a digit-free judge completion as unscored (NaN), not as 0. If no judge is set, scoring uses the active model; a different judge can be passed.

## Dataset and licence

There is no frozen test file. `eval.yaml` records 225 samples for the default 15 lengths × 15 depths × 1 run. Changing `-T` knobs changes the count. Assets are `en_haystack_texts` and `retrieval_needles` at revision `651d7c8f4eae047b3f47ca24e92e09f2acf64af5`. inspect_evals is MIT. Hugging Face tags NeedleBench MIT as well. English only in this filter.

## Who publishes it

UK AI Security Institute ships the task in inspect_evals (`inspect_evals/niah`). NeedleBench data come from OpenCompass (paper arXiv:2407.11963). The README scoring write-up points at Kamradt's GitHub, not at a new NIAH paper. `eval.yaml` sets `arxiv` to 2407.01437, which is IBM's Larimar memory paper, not this Inspect grid.

## Lineage

Kamradt's Needle in a Haystack notebook popularised the heatmap. OpenCompass [needlebench](needlebench.md) packaged essays and needles; [needlebench_v2](needlebench_v2.md) follows. NVIDIA [ruler](ruler.md) adds niah_single_* and multi-key variants with exact-match scoring. This id is the Inspect Evals wrapper: NeedleBench English assets, Kamradt-style LLM judge, default 10k–120k grid. It is not an alias of those pages.

## Saturation and contamination

No numeric overall_accuracy table was opened here. README plots cover Mistral small and medium on a shorter 2k–27k grid and warn that the judge sometimes marks a correct fictional needle as unrelated. Needles and haystacks are public. Placement is generated, so the prompt is not a single leaked JSON, but the facts are.

## How to run it

Install `inspect-evals[niah]` (pandas). Run `inspect eval inspect_evals/niah`. Defaults are 10k–120k tokens, 15 lengths, 15 positions, one fixed needle, one run (225 samples). Override with `-T min_context=...` and related knobs. Tokenisation uses tiktoken; unknown model names fall back to a default encoder. Compare only runs that share grid, needle sampling, judge model, and eval version (3-A changed unscored handling).

## Reading the numbers

A high `overall_accuracy` means the judge assigned high 1–10 grades on that grid, not that the model matched a string. The README shows judges clustering at 1 and 10, and sometimes penalising a correct needle because it is fictional. Do not compare this number to [needlebench](needlebench.md) keyword scores or to [ruler](ruler.md) `niah_single_1`. Quote context length, depth grid, `n_runs`, judge model, and eval version. The default 225-sample 10k–120k run is not the Mistral heatmap protocol in the README.
