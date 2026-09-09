---
id: game24
name: "Game of 24"
aliases:
  - game-of-24
  - "ToT Game of 24"
  - Game24
page_kind: benchmark
category: math
subcategory: "four-number arithmetic puzzles scored by exact use of each number to make 24"
status: active
summary: "Four-number puzzles that must equal 24; OpenCompass runs a five-puzzle Tree-of-Thoughts slice of the Princeton Game-of-24 set."
measures: >
  Game of 24 is a grade-school puzzle: given four integers, use each exactly once with
  +, -, *, / to make 24. Yao et al. 2023 (Tree of Thoughts) scrape 1,362 ranked games
  from 4nums.com and test the hard band indexed 901–1000. Success is a valid expression
  that equals 24 and uses the four inputs once each. OpenCompass dataset Game24Dataset
  loads Hugging Face test-time-compute/game-of-24 (or a local CSV) and then slices
  `data[900:905]`, i.e. five puzzles, not the paper's 100. The OpenCompass config uses
  ToTInferencer (propose / value / greedy, n_evaluate_sample=3, n_select_sample=5),
  matching the paper's Game-of-24 ToT setup.
task_format: >
  OpenCompass generation with a Tree-of-Thoughts inferencer and Game24PromptWrapper
  (standard, chain-of-thought, and propose/value prompts copied from the ToT repo).
  ZeroRetriever. Game24Evaluator checks the extracted expression with sympy and a
  digit-multiset check. Temperature 0.7 in game24_gen_52a460.py with do_sample=False.
metric:
  name: "accuracy (share of puzzles whose expression uses the four numbers once and equals 24)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    ToT paper Table 2 / Fig. 3 on indices 901–1000 (100 games), GPT-4: IO 7.3%, CoT 4.0%,
    CoT-SC 9.0%, ToT b=1 45%, ToT b=5 74%. A later reproduced ToT log in the official
    repo scored 69% instead of 74%. GPT-3.5 + ToT 19%. No OpenCompass leaderboard figure
    was found for the five-item slice. Human solve rates on 4nums.com vary by rank;
    the HF card summarises rank 900–1100 as roughly 80–90% human solve rate, which is
    not a model baseline.
dataset:
  size: 5
  size_note: >
    OpenCompass Game24Dataset.load returns only data[900:905] (five puzzles). The
    upstream 4nums.com scrape and the ToT paper use 1,362 games, with evaluation on
    100 games (1-based 901–1000, Python 900:1000). Hugging Face
    test-time-compute/game-of-24 reports train split num_examples 1362 in dataset_info
    and "1,361 unique" in the card prose. This id follows the OpenCompass task, so
    size is 5.
  url: "https://huggingface.co/datasets/test-time-compute/game-of-24"
  license: "MIT (Hugging Face card, ToT repository, and ToT LICENSE, Copyright 2023 Shunyu Yao); OpenCompass Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass: five-item slice of the HF train / CSV list at indices 900–904; ToT paper: 100-item test band 901–1000"
  public_test_set: true
publisher:
  org: "Princeton NLP (ToT paper and original task); OpenCompass (harness config)"
  authors:
    - "Shunyu Yao"
    - "Dian Yu"
    - "Jeffrey Zhao"
    - "Izhak Shafran"
    - "Thomas L. Griffiths"
    - "Yuan Cao"
    - "Karthik Narasimhan"
  url: "https://github.com/princeton-nlp/tree-of-thought-llm"
paper:
  title: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
  arxiv: "2305.10601"
  url: "https://arxiv.org/abs/2305.10601"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/princeton-nlp/tree-of-thought-llm"
released: "2023-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 74
  as_of: "2023-05"
  note: >
    74 is GPT-4 ToT (b=5) on the 100-puzzle paper split, not an OpenCompass 5-puzzle
    result. A five-item slice can swing wildly and may already be trivial for 2026
    models. Treat OpenCompass game24 scores as non-comparable to the paper table.
contamination:
  risk: high
  note: >
    Puzzles come from 4nums.com, public long before 2023, and the ToT prompts and
    logs are in a public GitHub repo. Any pretraining crawl of that site or repo can
    contain both puzzles and solutions.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "game24 (opencompass/configs/datasets/game24/game24_gen_52a460.py; abbr game24, type Game24Dataset)"
  bigbench: ""
  other: >
    Reference ToT implementation: princeton-nlp/tree-of-thought-llm, task Game24Task,
    scripts/game24/*.sh. OpenCompass path default 'test-time-compute/game-of-24'.
    No inspect_evals, lm-eval, or HELM task was confirmed.
tags:
  - math
  - tree-of-thoughts
  - opencompass
  - arithmetic
sources:
  - url: "https://arxiv.org/abs/2305.10601"
    title: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models (arXiv:2305.10601)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2305.10601"
    title: "ToT paper HTML (1,362 games, indices 901–1000, GPT-4 ToT 74%)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/test-time-compute/game-of-24"
    title: "test-time-compute/game-of-24 dataset card (MIT, 1362 rows, paper subset note)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/test-time-compute/game-of-24"
    title: "Hugging Face dataset API (created 2025-10-29, license mit, 1362 train examples)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-nlp/tree-of-thought-llm/master/README.md"
    title: "Official ToT README (Game of 24 quick start, 69% vs 74% reproduced log)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-nlp/tree-of-thought-llm/master/LICENSE"
    title: "ToT MIT License (Copyright 2023 Shunyu Yao)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/game24/game24_gen_52a460.py"
    title: "OpenCompass game24_gen_52a460.py (ToTInferencer, abbr game24)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/game24.py"
    title: "OpenCompass Game24Dataset (slice data[900:905], sympy evaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-044 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-044"
---

## What it measures

Game of 24 is the familiar four-number puzzle. The model must write an arithmetic expression that uses each given integer once and evaluates to 24. Yao et al. used it to show that Tree of Thoughts search beats chain-of-thought on GPT-4. OpenCompass reuses those prompts and the ToT inferencer.

The OpenCompass task this id names does not run the paper's 100-game band. `Game24Dataset.load` keeps only five puzzles (`data[900:905]`). A 100% OpenCompass score is five items.

## How it is scored

A prediction counts if its digits match the four inputs as a multiset and `sympy.simplify(expr) == 24`. The config reports `acc score`. The paper reports success rate on 100 hard games. GPT-4 ToT with beam 5 reached 74% there; IO 7.3% and CoT 4.0%. The official ToT repo later reproduced 69% on the same setting. Those figures are not OpenCompass results.

## Dataset and licence

Puzzles come from 4nums.com (1,362 ranked games). Hugging Face `test-time-compute/game-of-24` is MIT and lists 1,362 train rows (card prose says 1,361 unique). ToT code is MIT (Copyright 2023 Shunyu Yao). OpenCompass is Apache-2.0. All puzzles and many solutions are public.

## Who publishes it

The task definition is Yao, Yu, Zhao, Shafran, Griffiths, Cao, and Narasimhan, arXiv 17 May 2023 (v2 3 December 2023), Princeton NLP. OpenCompass maintainers wrapped it as `game24`. The Hugging Face copy under `test-time-compute/` was created 29 October 2025; it is a republication, not a new eval.

## Lineage

This is a ToT experiment task, not a large math suite. It is not GSM8K or MATH. No family page. No inspect_evals task was found.

## Saturation and contamination

GPT-4 already solved 74% of the hard 100 with ToT in 2023. The OpenCompass five-item slice is too small to rank 2026 models. Contamination is high: 4nums.com and the ToT GitHub logs are long-public.

## How to run it

OpenCompass: include `opencompass.configs.datasets.game24.game24_gen_52a460` (`abbr='game24'`). Needs the ToT inferencer and sympy. Official paper protocol: `princeton-nlp/tree-of-thought-llm` scripts under `scripts/game24/`, start 900 end 1000. Do not mix a 5-item OpenCompass run with a 100-item ToT table.

## Reading the numbers

Ask which split was used. Five OpenCompass puzzles cannot support a model ranking. A ToT 74% is a 2023 GPT-4 search result on 100 hard games, not a base-model zero-shot score. If you care about current arithmetic reasoning, use [gsm8k](gsm8k.md) or [math](math.md) instead of this slice.
