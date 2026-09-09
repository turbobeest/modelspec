---
id: charxiv_reasoning_tools
name: "CharXiv Reasoning (with tool use)"
aliases:
  - "CharXiv-R w/ tools"
page_kind: subset
category: multimodal
subcategory: "chart reasoning, tool-assisted"
status: active
summary: "CharXiv Reasoning scored with the model given a tool during the eval -- an image-cropping tool in the one vendor report this page found -- instead of the static chart image alone."
measures: >
  This id captures CharXiv Reasoning scores produced when the model was allowed to use a tool while
  answering, rather than the base benchmark's default of a single static chart image and no tool
  access. Tool use of this kind is not part of CharXiv's own official protocol; it is an evaluation
  choice individual vendors make when they report the benchmark. The one primary source this page
  found that defines the tool explicitly is Anthropic's Claude Opus 4.6 system card (2026-02), which
  evaluated Claude Opus 4.6 and Claude Opus 4.5 with "a simple image-cropping tool" available -- letting
  the model zoom into a region of the chart before answering, rather than reading the whole image at
  its original resolution. The same system card documents reasoning models more generally (OpenAI's o3
  and o4-mini, per their own system card) using tools including image cropping and Python-based
  analysis as part of their chain of thought, so cropping specifically targets the kind of fine
  print, dense legends and closely spaced data points that make CharXiv's charts hard to read at a
  glance.
task_format: >
  The same open-ended, one-question-per-chart format as CharXiv Reasoning, except the model may
  invoke a tool -- in the documented case, cropping into the chart image -- before producing its
  final free-text answer.
lineage:
  family: charxiv
harness:
  other: >
    Not a harness task in its own right; it is an evaluation condition (tool access on or off) that
    individual system cards choose to report alongside the base benchmark, not a distinct dataset or
    reference script.
tags:
  - multimodal
  - chart-reasoning
  - tool-use
  - charxiv
sources:
  - url: "https://www-cdn.anthropic.com/6a5fa276ac68b9aeb0c8b6af5fa36326e0e166dd/Claude%20Opus%204.6%20System%20Card.pdf"
    title: "Claude Opus 4.6 System Card, section 2.19.3 CharXiv Reasoning (Anthropic, 2026-02)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2406.18521"
    title: "CharXiv: Charting Gaps in Realistic Chart Understanding in Multimodal LLMs (Wang et al., arXiv:2406.18521)"
    accessed: "2026-09-08"
  - url: "https://openai.com/index/o3-o4-mini-system-card/"
    title: "OpenAI o3 and o4-mini System Card overview page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

Part of the [CharXiv](charxiv.md) family; the tool-assisted variant of
[CharXiv Reasoning](charxiv_reasoning.md).

## What it measures

This id is CharXiv Reasoning re-scored with the model given a tool during the eval, not a new question
set. The only primary source this page found defining the tool is Anthropic's Claude Opus 4.6 system
card: "a simple image-cropping tool" that lets the model zoom into a region of the chart before
answering, rather than reading the static image at base resolution. That card reports the gap this
creates: Claude Opus 4.6 rose from 68.5% without the tool to 77.4% with it; Claude Opus 4.5 rose from
65.7% to 68.7% under the same two settings, both on CharXiv's 1,000-question validation split. No other
tool-use definition was confirmed from a primary source, so treat "tool use" here as vendor-specific,
not standardised.

## Reading the numbers

A higher tools score than no-tools score suggests CharXiv's difficulty is partly a resolution problem,
not purely a reasoning gap; the roughly 9-point lift for Claude Opus 4.6 supports that reading. Because
no CharXiv-wide standard defines "tools," do not assume two vendors' `_tools` scores used the same tool;
compare a model's own tools-versus-no-tools pair from one source, not tools scores across vendors. See
[CharXiv Reasoning](charxiv_reasoning.md) for the underlying benchmark's saturation and contamination
notes, which apply here too.
