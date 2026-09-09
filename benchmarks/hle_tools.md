---
id: hle_tools
name: "Humanity's Last Exam (with tools)"
aliases:
  - HLE with search
  - HLE tool-use
page_kind: subset
category: reasoning
subcategory: frontier academic knowledge Q&A, tool-augmented
status: active
summary: The same 2,500 HLE questions scored when a model can search, fetch web pages and run code, instead of answering from its own knowledge alone.
measures: >
  This id captures Humanity's Last Exam scores produced while the model had tool access, rather than
  answering closed-book. The specific tool setting varies by reporting source and should be read from
  that source rather than assumed: Anthropic's Claude Opus 4.5 System Card (November 2025) defines its
  "with search" condition as web search, web fetch and code execution, run without extended thinking,
  graded by a separate model (Claude Sonnet 4.5) and explicitly decontaminated by flagging transcripts
  that visited known answer-sheet domains or otherwise showed signs of retrieving rather than deriving
  an answer. Where a source does not document its tool configuration, that configuration is not
  established here.
task_format: >
  Same question set and answer format as `hle`, but the model may call tools (web search, web fetch,
  code execution, or similar, per the reporting source) before producing its final answer.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    Directly comparable to hle's accuracy metric on the same question set; not comparable to hle's
    calibration-error figures, which are not consistently reported for tool-augmented runs.
dataset:
  size: 2500
  size_note: "Same question set as hle; see that page for dataset detail."
  url: https://huggingface.co/datasets/cais/hle
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
    - image
  splits: single public test split, plus a private held-out set not released
  public_test_set: true
publisher:
  org: Center for AI Safety and Scale AI
  authors: []
  url: https://lastexam.ai
paper:
  title: "Humanity's Last Exam"
  arxiv: "2501.14249"
  url: https://arxiv.org/abs/2501.14249
  year: 2025
leaderboard_url: https://agi.safe.ai/dashboard
repo_url: https://github.com/centerforaisafety/hle
released: "2025-01"
last_updated: "2025-11"
lineage:
  family: hle
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 45.8
  as_of: "2025-11"
  note: >
    Anthropic's Claude Opus 4.5 System Card (Nov 2025) charted six models with search enabled: Claude
    Opus 4.1 (22.7%), Claude Sonnet 4.5 (28.4%), GPT-5 (35.2%), GPT-5 Pro (42.0%), Claude Opus 4.5
    (43.2%) and Gemini 3 (45.8%), each roughly 8-13 points above that same model's own no-tools score
    in the same chart.
contamination:
  risk: medium
  note: >
    Higher practical risk than the no-tools condition, since a model with live search access can
    retrieve an answer rather than derive it. Anthropic's November 2025 system card describes manually
    reviewing and re-grading transcripts that showed evidence of this for its own search-enabled runs.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No dedicated harness task name confirmed for the tool-augmented condition specifically; see hle for the base task."
tags:
  - reasoning
  - multi-modal
  - tool-use
  - agentic
sources:
  - url: https://www.anthropic.com/claude-opus-4-5-system-card
    title: "System Card: Claude Opus 4.5 (Anthropic, November 2025), Section 2.16, Figure 2.16.A"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2501.14249
    title: "Humanity's Last Exam (arXiv:2501.14249)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Humanity's Last Exam](hle.md) family.

## What it measures

This id is the same 2,500-question HLE set, scored when the model was allowed tools rather than
answering closed-book. It is a different measurement from `hle`, not a harder or easier version of it:
a model can look up or compute an answer instead of recalling or deriving it. The exact tool setting
differs by source. Anthropic's Claude Opus 4.5 System Card (November 2025) is the clearest documented
case: it defines "with search" as web search, web fetch and code execution, run without extended
thinking and graded by a separate model, with a documented decontamination pass over the transcripts.
Treat any other source's "with tools" HLE number as unverified until its own configuration is known.

## Reading the numbers

Tool access consistently raises HLE scores over the same model's no-tools baseline — Anthropic's
November 2025 figures show roughly an 8 to 13 point gain across six models — reflecting that some HLE
questions are answerable by finding a source online despite the benchmark's intent to resist lookup.
A high `hle_tools` score is therefore better read as research and tool-use competence than pure
knowledge, and should be paired with the same model's plain `hle` score to see how much is retrieval. Contamination is a bigger concern here, since live search can retrieve a
leaked answer directly; check the decontamination method, if any, before trusting a reported number.
