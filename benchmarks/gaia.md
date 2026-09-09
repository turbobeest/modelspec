---
id: gaia
name: GAIA
aliases:
  - "General AI Assistants"
  - "GAIA: a benchmark for General AI Assistants"
  - "gaia-benchmark/GAIA"
page_kind: benchmark
category: agentic
subcategory: "real-world assistant questions requiring tools, browsing, and files"
status: active
summary: "466 real-world assistant questions needing tools and browsing; 300 test answers are held out and scoring is quasi-exact match."
measures: >
  GAIA asks conceptually simple assistant questions that still need reasoning, web
  browsing, file reading, and other tools. Answers are a number, a short string, or a
  comma-separated list, so scoring can be automatic. The authors wrote 466 questions:
  146 Level 1 (at most one tool, few steps), 245 Level 2 (roughly 5–10 steps, mixed
  tools), and 75 Level 3 (long action sequences). English questions; some items attach
  a spreadsheet, image, audio, or other file. Humans scored 92% overall in the paper.
  GPT-4 with plugins scored 15% in the abstract (Table 4: 30.3 / 9.7 / 0 by level).
task_format: >
  Zero-shot assistant prompt, optional attached file. Inspect default solver is a ReAct
  agent with bash, Python, and a web browser inside Docker. Default split is validation
  (answers present). Test split has no scores in-harness; those answers go to the public
  leaderboard. Tasks: gaia (2023_all), gaia_level1, gaia_level2, gaia_level3.
metric:
  name: "accuracy (quasi-exact match after type-specific normalisation)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 92
  baseline_note: >
    Paper human score 92% overall (Table 4 by level: 93.9 / 91.8 / 87.3 on 146 / 245 /
    75 questions). GPT-4 9.1 / 2.6 / 0; GPT-4 Turbo 13.0 / 5.5 / 0; AutoGPT 14.4 / 0.4 /
    0; GPT-4 + plugins 30.3 / 9.7 / 0; search engine 7.4 / 0 / 0. Abstract quotes 15%
    for GPT-4 with plugins versus 92% human. No current leaderboard top score was read
    for this page (the Space front-end did not yield a static table).
dataset:
  size: 466
  size_note: >
    Paper: 466 questions (146 + 245 + 75 by level); 166 annotated developer questions
    released and 300 test questions released without answers. Inspect eval.yaml validation
    counts: gaia 165, gaia_level1 53, gaia_level2 86, gaia_level3 26 (53+86+26=165). The
    paper's 166 versus Inspect's 165 is a one-item disagreement on the public validation
    split. Hugging Face repo gaia-benchmark/GAIA is gated (auto) with an extra_gated
    prompt not to reshare crawlable copies. Configs 2023_all / 2023_level1 / 2023_level2
    / 2023_level3, each with test and validation parquet.
  url: "https://huggingface.co/datasets/gaia-benchmark/GAIA"
  license: ""
  languages:
    - en
  modalities:
    - text
    - image
    - audio
    - document
  splits: "validation (answers in the developer set) and test (answers withheld for the leaderboard)"
  public_test_set: false
publisher:
  org: "FAIR, Meta and Hugging Face (paper affiliations); AutoGPT and Meta GenAI also listed"
  authors:
    - "Grégoire Mialon"
    - "Clémentine Fourrier"
    - "Craig Swift"
    - "Thomas Wolf"
    - "Yann LeCun"
    - "Thomas Scialom"
  url: "https://huggingface.co/gaia-benchmark"
paper:
  title: "GAIA: a benchmark for General AI Assistants"
  arxiv: "2311.12983"
  url: "https://arxiv.org/abs/2311.12983"
  year: 2023
leaderboard_url: "https://huggingface.co/spaces/gaia-benchmark/leaderboard"
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gaia"
released: "2023-11"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2023-11"
  note: >
    Paper GPT-4 + plugins is 15% overall versus a 92% human ceiling, so the 2023 table
    is open. Later agent systems report much higher validation numbers on the public
    leaderboard; this page did not scrape that live table, so no 2026 top_score is
    recorded.
contamination:
  risk: medium
  note: >
    Questions are public. Test answers are withheld and the Hub repo is gated against
    resharing. Validation answers are in the developer set, so validation scores can
    leak into training. The authors designed questions so the final answer is unlikely
    to appear as plain text in crawls.
harness:
  lm_eval: ""
  inspect_evals: "gaia, gaia_level1, gaia_level2, gaia_level3"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official scorer (Apache-2.0) is copied into Inspect from the leaderboard Space.
    Hugging Face access token required (HF_TOKEN). Docker required for the default
    agent. Inspect 3-A (2026-04-21) replaced basic_agent with react; 3-B (2026-08-03)
    pinned sandbox image digests. extra inspect-evals[gaia].
tags:
  - agentic
  - tool-use
  - web
  - inspect-evals
  - multimodal
sources:
  - url: "https://arxiv.org/abs/2311.12983"
    title: "GAIA: a benchmark for General AI Assistants (arXiv:2311.12983)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2311.12983"
    title: "GAIA paper HTML (466 questions, levels, Table 4, 166/300 split, 92% human)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/gaia-benchmark/GAIA"
    title: "Hugging Face dataset API (gated auto, 2023_all configs, created 2023-10-20)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/gaia-benchmark/leaderboard"
    title: "GAIA leaderboard Space (Apache-2.0 Space card; live ranks not extracted)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gaia/README.md"
    title: "Inspect Evals GAIA README (450-question blurb, 165 validation, Docker, HF_TOKEN)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gaia/eval.yaml"
    title: "Inspect eval.yaml (165 / 53 / 86 / 26 validation counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gaia/scorer.py"
    title: "Inspect scorer.py (quasi-exact match copied from the official Space scorer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-044 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-044"
---

## What it measures

GAIA is a tool-using assistant exam. Each item is a short factual question a person can answer with a browser, a calculator, and ordinary files, but a bare LLM usually cannot. Levels mark how many tools and steps the authors expected. Some prompts attach a file. The skill is robust tool use on messy real questions, not professional-exam recall.

Inspect's README says "450 questions"; the paper counts 466. This page uses 466 from the paper and records Inspect's 165-row validation default separately.

## How it is scored

Quasi-exact match after normalisation: numbers ignore `$`, `%`, and commas; strings case-fold and drop spaces and punctuation; lists compare element-wise. Inspect copies the official leaderboard scorer (Apache-2.0). The test split has no targets in the dataset, so Inspect cannot score it; submit to the Hugging Face Space. Default Inspect split is validation.

Paper GPT-4 + plugins numbers used hand-picked plugins and are marked non-reproducible in Table 4.

## Dataset and licence

Four hundred and sixty-six questions, 300 of them test without answers. Hugging Face `gaia-benchmark/GAIA` is gated. The Hub API lists no SPDX licence for the dataset; the leaderboard Space card is Apache-2.0. Inspect's copy of the scorer is Apache-2.0; Inspect itself is MIT. Modalities on the Hub include text, image, audio, and documents.

Paper developer set 166 versus Inspect validation 165: one-item gap, not resolved here.

## Who publishes it

Grégoire Mialon and Thomas Scialom (Meta FAIR / GenAI) with Clémentine Fourrier and Thomas Wolf (Hugging Face) and Craig Swift (AutoGPT) and Yann LeCun. arXiv 21 November 2023. Hub dataset created 20 October 2023, last modified 28 October 2025. Inspect port by max-kaufmann, version 3-B.

## Lineage

No predecessor page. [assistant_bench](assistant_bench.md) reuses the GAIA leaderboard template and cites GAIA as a related agent suite. GAIA is not a web-only sandbox like Mind2Web.

## Saturation and contamination

The 2023 table is far below the 92% human score. Later agents on the public leaderboard are not recorded here. Validation answers are public to anyone who passes the gate, so validation numbers can be contaminated. Test answers stay on the leaderboard path.

## How to run it

Request Hub access, set `HF_TOKEN`, install Docker, then `uv run inspect eval inspect_evals/gaia` (or `gaia_level1` / `_level2` / `_level3`). extra `inspect-evals[gaia]`. Inspect 3-A changed the default agent to `react` and 3-B pinned image digests. Message budget is `--message-limit` (default 100), not the old `max_messages` task flag.

## Reading the numbers

A validation accuracy is not a test-leaderboard score. Name the split, the agent (browser or not), and the Inspect version. Level 1 can be solved with one lookup; Level 3 is not. Pair with [assistant_bench](assistant_bench.md) for longer web tasks, not with closed-book quizzes.
