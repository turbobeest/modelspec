---
id: screenspot_pro_tools
name: "ScreenSpot-Pro (with tools)"
aliases:
  - ScreenSpot-Pro agentic
  - ScreenSpot-Pro zoom-in
page_kind: subset
category: agentic
subcategory: GUI grounding, tool-augmented
status: active
summary: ScreenSpot-Pro scores produced by an iterative search, crop or zoom strategy instead of a single-shot prediction over the full screenshot.
measures: >
  This id captures ScreenSpot-Pro scores produced with some form of tool use or multi-step search
  rather than a single-shot grounding prediction over the full-resolution screenshot. No specific
  Anthropic or OpenAI system card documenting a named model's paired with-tools/without-tools
  ScreenSpot-Pro score was found in this research, so a single canonical tool setting is not
  established here. What is established, directly from the benchmark's own paper and its
  actively-maintained leaderboard: the field's dominant "tool" pattern on this task is an iterative
  zoom, crop or planner-guided search loop that progressively narrows the search region, rather than
  browsing or code execution. The paper's own proposed method, ScreenSeekeR, is an example: a planner
  model guides a cascaded search over image crops. Where a specific model's tool configuration is not
  documented by its source, treat that configuration as unknown rather than assuming it matches
  another source's setup.
task_format: >
  Same screenshot-plus-instruction grounding task as screenspot_pro, but the model (or a wrapper
  around it) may take multiple steps — for example, requesting a cropped or zoomed view, or using a
  separate planner model to guide the search — before committing to a final point.
metric:
  name: click accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    Directly comparable to screenspot_pro's click-in-box accuracy on the same 1,581 instructions; not
    comparable across different tool/search strategies, which vary in how many steps or how much
    compute they use per instruction.
dataset:
  size: 1581
  size_note: "Same instruction set as screenspot_pro; see that page for dataset detail."
  url: https://huggingface.co/datasets/likaixin/ScreenSpot-Pro
  license: MIT
  languages:
    - en
  modalities:
    - image
    - text
  splits: single evaluation set, no train/test split
  public_test_set: true
publisher:
  org: Independent research collaboration (Hong Kong Baptist University and collaborators)
  authors: []
  url: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding
paper:
  title: "ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use"
  arxiv: "2504.07981"
  url: https://arxiv.org/abs/2504.07981
  year: 2025
leaderboard_url: https://gui-agent.github.io/grounding-leaderboard/
repo_url: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding
released: "2025-01"
last_updated: "2026-08"
lineage:
  family: screenspot_pro
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 82.7
  as_of: "2026-08"
  note: >
    The project's leaderboard's current top entry (82.7%, fetched directly for this page) is an
    explicitly "zoom-in" variant of a specialized grounding model. The paper's own launch-era example
    of the same pattern was smaller but clearer: ScreenSeekeR lifted its base model, OS-Atlas-7B, from
    18.9% to 48.1% using only a cascaded search strategy, with no additional training.
contamination:
  risk: low
  note: "Same considerations as screenspot_pro; tool use does not add a distinct leakage pathway for an image-grounding task."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No dedicated harness task name confirmed; see screenspot_pro for the base task and its own evaluation scripts."
tags:
  - agentic
  - gui-grounding
  - computer-use
  - tool-use
sources:
  - url: https://arxiv.org/abs/2504.07981
    title: "ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use (arXiv:2504.07981)"
    accessed: "2026-09-08"
  - url: https://gui-agent.github.io/grounding-leaderboard/
    title: "ScreenSpot-Pro Leaderboard (results data)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

Part of the [ScreenSpot-Pro](screenspot_pro.md) family.

## What it measures

This id covers ScreenSpot-Pro scores produced with some form of iterative search, cropping or zooming
rather than a single-shot prediction over the full screenshot. No Anthropic or OpenAI system card
pairing one named model's with-tools and without-tools ScreenSpot-Pro scores was found in this
research, so treat any single tool configuration as unconfirmed unless its source states it. What is
directly established, from the paper and its maintained leaderboard, is the general pattern: the
paper's proposed ScreenSeekeR method uses a planner model to guide a cascaded search over image crops,
and the leaderboard's strongest current entries are explicitly labelled "zoom-in" or agentic variants.

## Reading the numbers

At launch, the paper's own comparison showed the pattern clearly: adding a search strategy lifted its
base grounding model from 18.9% to 48.1% accuracy with no additional training, using a planner model
(GPT-4o) that itself scored under 1% at direct grounding — evidence a weak "planner" can still
meaningfully guide a stronger search process. The current leaderboard extends that pattern: top entries
are consistently zoom-in or agentic variants, not single-shot predictions. Strategies differ in steps,
compute, and how much of the image they inspect, so do not treat two "with tools" scores as comparable
without checking the strategy, and do not assume any lab's system card has published a matched pair
for this benchmark.
