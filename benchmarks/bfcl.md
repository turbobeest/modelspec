---
id: bfcl
name: "BFCL (Berkeley Function-Calling Leaderboard)"
aliases:
  - "Berkeley Function-Calling Leaderboard"
  - "Berkeley Function Calling Leaderboard"
  - "BFCL"
page_kind: benchmark
category: agentic
subcategory: "tool use, multi-turn function calling, and agentic memory/web search"
status: active
summary: "UC Berkeley leaderboard for LLM function calling: single-turn AST match, live user data, multi-turn backends, and agentic memory/web-search tasks."
measures: >
  BFCL tests whether a model can call tools rather than only talk. A sample is a user
  request plus JSON tool schemas. Single-turn items (V1 original, V2 live/user-contributed)
  require the model to emit the right function name and arguments, scored by AST match
  against a gold call. Multi-turn items (V3) run against stateful backends such as a file
  system or trading bot and score final state and responses. Agentic items (V4) either
  chain web search or write and later read a memory snapshot across sessions, scored on
  the final text answer. Python, Java, JavaScript and a small SQL category are included.
  English user text; tools are typed JSON.
task_format: >
  Tool-calling. inspect_evals task inspect_evals/bfcl (optional bfcl_prereqs for V4 memory).
  Official CLI is bfcl-eval. Categories are selected with a categories parameter. Default
  inspect run is V1+V2+V3 except rest and format_sensitivity.
metric:
  name: accuracy
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Headline is per-category and overall accuracy (correct tool use / items). Official
    leaderboard also tracks cost and latency, which this page does not treat as the
    primary score. No human baseline was read from the official blog or inspect README.
dataset:
  size: 4981
  size_note: >
    inspect_evals default categories (V1+V2+V3 except rest and format_sensitivity) are
    documented as 4,981 samples. CATEGORIES.md counts: single-turn 3,981 including sql
    (100) and live_multiple (1,053); five multi-turn categories × 200 = 1,000. V4 memory
    is 155 questions × three backends (465) plus two web-search categories × 100 (200);
    those are opt-in. rest (70) is unimplemented in inspect and retired upstream. The
    2026-03-06 inspect report ran 3,981 single-turn samples.
  url: "https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "per-category JSON files in bfcl_eval/data; no train split"
  public_test_set: true
publisher:
  org: "UC Berkeley (Gorilla / Sky Computing Lab)"
  authors:
    - "Shishir G. Patil"
    - "Huanzhi Mao"
    - "Charlie Cheng-Jie Ji"
    - "Fanjia Yan"
    - "Vishnu Suresh"
    - "Ion Stoica"
    - "Joseph E. Gonzalez"
  url: "https://gorilla.cs.berkeley.edu/leaderboard.html"
paper:
  title: "The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models"
  arxiv: ""
  url: "https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html"
  year: 2024
leaderboard_url: "https://gorilla.cs.berkeley.edu/leaderboard.html"
repo_url: "https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard"
released: "2024"
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
    The official leaderboard page did not yield a dated numeric top row in the static
    HTML opened here (client-rendered). inspect_evals reports Claude Haiku 4.5 at 0.806
    overall on 3,981 single-turn samples (2026-03-06) and 0.419 on a 1,000-item V3
    multi-turn run (2026-03-24); those are the port's numbers, not the live Berkeley
    board.
contamination:
  risk: medium
  note: >
    Evaluation JSON is public in the Gorilla repository. V2 is user-contributed "live"
    data intended to be less likely to sit in pretraining than V1. V4 web search hits
    the live web. No measured contamination study was opened here.
harness:
  lm_eval: ""
  inspect_evals: "bfcl"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official package is bfcl-eval (not the unrelated PyPI project named bfcl). inspect
    also ships bfcl_prereqs for V4 memory snapshots. inspect pins Gorilla commit
    dac44e7ac9db5ff26a01ab0c1ec5de5a1e703b7a. rest and format_sensitivity are not
    runnable in the inspect port.
tags:
  - tool-use
  - function-calling
  - agentic
  - multi-turn
  - ast
sources:
  - url: "https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html"
    title: "BFCL V1 blog (citation, authors, last updated 2024-08-19)"
    accessed: "2026-09-08"
  - url: "https://gorilla.cs.berkeley.edu/leaderboard.html"
    title: "Berkeley Function Calling Leaderboard"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ShishirPatil/gorilla/main/berkeley-function-call-leaderboard/README.md"
    title: "Official BFCL README (V1–V4 blogs, bfcl-eval install)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ShishirPatil/gorilla/main/berkeley-function-call-leaderboard/TEST_CATEGORIES.md"
    title: "Official BFCL test-category list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ShishirPatil/gorilla/main/LICENSE"
    title: "gorilla repository Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/bfcl/README.md"
    title: "inspect_evals BFCL README (4,981 default samples, category tables, 2026 reports)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/bfcl/bfcl.py"
    title: "inspect_evals bfcl.py (task name bfcl, default V1–V3 categories, Gorilla commit pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/bfcl/utils/CATEGORIES.md"
    title: "inspect_evals CATEGORIES.md (per-category sample counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT licence (harness port, not the dataset)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-028 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-028"
---

## What it measures

BFCL measures tool use. The model is given a user request and one or more JSON function schemas and must call the right function with the right arguments, or abstain when nothing fits (irrelevance/relevance). V1 covers simple, parallel, multiple, language-specific (Java, JavaScript), SQL, and executable-style items. V2 repeats the formats on user-contributed live items. V3 is multi-turn against stateful backends. V4 is agentic: multi-hop web search, or a two-phase memory test where the same model first stores facts (`bfcl_prereqs`) and later answers questions from a snapshot. User language is English.

This is not a coding benchmark such as HumanEval: success is a well-formed, correctly argued tool call (or a correct final answer after tools), not a passing unit test of generated programs.

## How it is scored

Single-turn V1/V2 items use AST matching against a gold call, with separate checkers for irrelevance (do not call) and relevance (do call). V3 compares backend state and responses after a dialogue. V4 checks whether the final text contains the expected answer. The inspect port reports overall accuracy plus per-category accuracy. The official leaderboard also publishes cost and latency, which are not the inspect headline. Protocol differences that break comparability include: which category list was run; whether function-calling native APIs or prompted JSON were used; whether V4 memory used a complete snapshot from the same model; and whether web search had a SerpAPI key. inspect does not implement `rest` (retired upstream) or `format_sensitivity` (a meta-index).

## Dataset and licence

inspect documents 4,981 default samples (3,981 single-turn + 1,000 multi-turn) drawn from the Gorilla `bfcl_eval/data` files. V4 adds 465 memory evaluations of the same 155 questions on three backends, plus 200 web-search items. Data are public JSON in the Gorilla tree. The Gorilla repository is Apache-2.0; that is the licence read for the official package. inspect_evals itself is MIT. There is no held-out private test split in the sources opened here.

## Who publishes it

The Gorilla group at UC Berkeley: Shishir G. Patil, Huanzhi Mao, Charlie Cheng-Jie Ji, Fanjia Yan, Vishnu Suresh, Ion Stoica and Joseph E. Gonzalez (authors as listed in the V1 blog citation). The V1 blog is dated as last updated 2024-08-19. The same citation is an NeurIPS 2024 inproceedings entry titled "The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models"; the cite key says 2025 while the `year` field says 2024. No arXiv id was confirmed (a guessed 2402.08147 is a different paper, VerMCTS). The live board is gorilla.cs.berkeley.edu/leaderboard.html. The UK AI Security Institute inspect_evals port is a third-party reimplementation.

## Lineage

BFCL is a standalone tool-use leaderboard, not an alias of Gorilla OpenFunctions model cards. It grew in place: V1 AST single-turn, V2 live, V3 multi-turn, V4 agentic memory and web search. No predecessor or successor page exists in this repository. It is unrelated to BIG-bench, Belebele, or BIRD-SQL despite sharing none of those names.

## Saturation and contamination

A current official top score was not recovered from the static leaderboard HTML. inspect's own 2026-03 single-turn run still left headroom (Haiku 4.5 at 0.806) and V3 multi-turn was much lower (0.419 on Haiku; 0.273 on a 10% GPT-5.1 sample). Treat those as port results. Public JSON plus live web search makes contamination medium for V1 and lower for V2/V4 web, without a measured leakage study.

## How to run it

Official: install `bfcl-eval` and run `bfcl generate` then `bfcl evaluate` with a model and `--test-category` list. inspect: `inspect eval inspect_evals/bfcl` (pip extra `inspect-evals[bfcl]`); V4 memory needs `bfcl_prereqs` with the same model and `snapshot_id`, and web search needs `SERPAPI_API_KEY`. Do not compare a default inspect 4,981-item run to an official all-category score that includes V4 or `rest`.

## Reading the numbers

A high overall accuracy means the model produced acceptable calls on the mix of categories that were actually run. Single-turn Python can look strong while Java, JavaScript, SQL, irrelevance, or multi-turn stay weak; inspect's Haiku table is an example (simple_python 0.928 vs simple_javascript 0.220 vs sql 0.440). V4 memory scores measure a different skill (what to store, then how to retrieve it) and require a completed prereq snapshot. Always name the category set, the BFCL version, and whether the run used native function calling.
