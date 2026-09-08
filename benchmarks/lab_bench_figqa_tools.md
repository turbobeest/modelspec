---
id: lab_bench_figqa_tools
name: "LAB-Bench: FigQA (with tools)"
aliases:
  - FigQA with tools
page_kind: subset
category: domain
subcategory: biology research - figure interpretation, tool-augmented
status: active
summary: The same 226 LAB-Bench FigQA questions scored when a model has an image-cropping tool and extended reasoning available, instead of answering from a single look at the figure.
measures: >
  This id captures LAB-Bench FigQA scores produced with tool access, rather than from a single pass
  over the figure. The one documented case found in this research is specific and narrower than
  "tools" in general: Anthropic's Claude Opus 4.5 System Card (November 2025, Section 2.21) evaluates
  models "with a simple image cropping tool and a reasoning token budget of 32,768 tokens," contrasted
  against a baseline with neither tool nor extended thinking. That is a combination of one visual tool
  and extended reasoning, not web search or code execution. Treat any other source's "with tools"
  FigQA number as unverified until its own configuration is confirmed; the original LAB-Bench paper
  itself predicted FigQA specifically was unlikely to benefit much from tool use, since it is a
  perception task rather than a retrieval one.
task_format: >
  Same figure-only multiple-choice questions as lab_bench_figqa, but the model may use an
  image-cropping tool (per Anthropic's documented setting) and, in that same setting, an extended
  reasoning budget before answering.
metric:
  name: precision (correct / attempted)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    Anthropic's Figure 2.21.A reports these as plain "Score" values with 95% confidence intervals under
    0-shot prompting; whether that score is accuracy or precision in LAB-Bench's original sense is not
    stated in the passages reviewed for this page.
dataset:
  size: 226
  size_note: "Same question set as lab_bench_figqa; see that page for dataset detail."
  url: https://huggingface.co/datasets/futurehouse/lab-bench
  license: CC BY-SA 4.0
  languages:
    - en
  modalities:
    - image
    - text
  splits: public subset released on Hugging Face; a private held-out portion is not released
  public_test_set: true
publisher:
  org: FutureHouse
  authors: []
  url: https://github.com/Future-House/LAB-Bench
paper:
  title: "LAB-Bench: Measuring Capabilities of Language Models for Biology Research"
  arxiv: "2407.10362"
  url: https://arxiv.org/abs/2407.10362
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/Future-House/LAB-Bench
released: "2024-07"
last_updated: "2025-11"
lineage:
  family: lab_bench_figqa
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 69.2
  as_of: "2025-11"
  note: >
    Anthropic's Claude Opus 4.5 System Card (Nov 2025, Figure 2.21.A) reports, with image-cropping
    tool and reasoning versus baseline: Claude Opus 4.1 48.1% to 54.1%, Claude Sonnet 4.5 52.3% to
    63.7%, Claude Opus 4.5 54.9% to 69.2%. The uplift from the added tool and reasoning was larger for
    stronger models, and even the best tooled score remains below the roughly 75% human baseline shown
    in the same source.
contamination:
  risk: low
  note: "Same held-out private portion as lab_bench_figqa; no additional contamination pathway specific to the tooled condition was found in this research."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No dedicated harness task name confirmed for the tool-augmented condition specifically; see lab_bench_figqa for the base task."
tags:
  - domain
  - biology
  - multimodal
  - tool-use
sources:
  - url: https://www.anthropic.com/claude-opus-4-5-system-card
    title: "System Card: Claude Opus 4.5 (Anthropic, November 2025), Section 2.21, Figure 2.21.A"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2407.10362
    title: "LAB-Bench: Measuring Capabilities of Language Models for Biology Research (arXiv:2407.10362)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

Part of the [LAB-Bench: FigQA](lab_bench_figqa.md) family.

## What it measures

This id is LAB-Bench FigQA scored with tool access rather than from a single look at the figure. The
tool setting is specific, not generic: the one documented instance found here, Anthropic's Claude Opus
4.5 System Card (November 2025), pairs "a simple image cropping tool" with a 32,768-token
extended-reasoning budget, against a baseline run with neither. That is worth noting because
LAB-Bench's own authors predicted FigQA was among the categories least likely to benefit from tool
use, reasoning it tests visual perception rather than retrieval. A cropping tool that lets a model
inspect fine figure detail more closely helped regardless.

## Reading the numbers

Anthropic's figures show the cropping-tool-plus-reasoning condition beating the untooled baseline by
6 to 14 points across three model generations, largest for the strongest model tested (Claude Opus
4.5: 54.9% to 69.2%). Stronger models extracting more benefit from the same added tool is itself
notable, and cuts against assuming tool access mostly helps weaker models catch up. Even the best
tooled score remains well under the roughly 75% human baseline in the same source, so this stays
open and unsaturated. Only one lab's configuration is documented here, so do not rank this figure
against a differently-configured "with tools" score without confirming what tools that source used.
