---
id: screenspot_pro
name: ScreenSpot-Pro
aliases:
  - ScreenSpot Pro
page_kind: benchmark
category: agentic
subcategory: GUI grounding
status: active
summary: 1,581 instructions testing whether a model can point to the right UI element in authentic, high-resolution screenshots of 23 professional applications.
measures: >
  ScreenSpot-Pro tests GUI grounding in professional software: given a natural-language instruction
  and a screenshot, a model must locate the precise on-screen element the instruction refers to. Unlike
  earlier grounding benchmarks built around everyday consumer apps and mobile screens, every image here
  is an authentic, expert-captured screenshot from real professional workflows in fields like CAD,
  scientific computing, creative software and IDEs, at native high resolution (over 1080p) rather than
  a cropped or downscaled view. Targets are correspondingly tiny: on average a target occupies about
  0.07% of the screenshot area, versus 2.01% on the original ScreenSpot benchmark this one extends.
task_format: >
  A screenshot plus a natural-language instruction describing an action ("open the layers panel", for
  example); the model outputs a single point or coordinate. Targets are additionally labelled as either
  text or icon.
metric:
  name: click accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    A prediction counts as correct when the model's output point falls inside the human-annotated
    bounding box for the instruction's target element, the same click-in-box protocol used by the
    original ScreenSpot benchmark this one extends; overall accuracy is the share of the 1,581
    instructions solved this way (the project reports a micro-average across categories). No formal
    random or human baseline is published; the paper instead reports that GPT-4o, a general frontier
    model used zero-shot, scored only 0.9% direct grounding accuracy on this benchmark.
dataset:
  size: 1581
  size_note: >
    1,581 instructions over authentic screenshots spanning 23 applications across five industries
    (development and programming, creative, CAD and engineering, scientific and analytical, office)
    plus a sixth "operating system commons" category, across three operating systems (Windows, macOS,
    Linux). About 62.6% of targets are text elements and the remainder are icons.
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
  authors:
    - Kaixin Li
    - Ziyang Meng
    - Hongzhan Lin
    - Ziyang Luo
    - Yuchen Tian
    - Jing Ma
    - Zhiyong Huang
    - Tat-Seng Chua
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
  family: ""
  predecessor: ""
  successors: []
  variants:
    - screenspot_pro_tools
saturation:
  status: open
  top_score: 82.7
  as_of: "2026-08"
  note: >
    At release, the best existing GUI grounding model (OS-Atlas-7B) scored 18.9%, and the paper's own
    proposed search method (ScreenSeekeR) reached 48.1% without additional training. The project's own
    leaderboard, fetched directly for this page, lists its current top entry at 82.7% (a "zoom-in"
    variant of a specialized grounding model, not a general frontier chat model), dated by the
    leaderboard page's own "last updated" notice rather than a specific submission date. Scores remain
    well below the ceiling and continue to separate models meaningfully.
contamination:
  risk: low
  note: >
    Screenshots are authentic captures of real professional software use rather than text drawn from
    the open web, so the usual internet-scale pretraining leakage pathway is less direct. The paper
    does not discuss contamination as a concern; risk mainly comes from the dataset and its answer
    bounding boxes being publicly downloadable, which could let later models be tuned specifically on
    these images.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The authors' own repository ships eval_screenspot_pro.py and a parallel variant, requiring an
    OpenAI-compatible API key; results are typically submitted to the project's own leaderboard rather
    than run through a third-party harness.
tags:
  - agentic
  - gui-grounding
  - computer-use
  - multimodal
  - professional-software
sources:
  - url: https://arxiv.org/abs/2504.07981
    title: "ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use (arXiv:2504.07981)"
    accessed: "2026-09-08"
  - url: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding
    title: "likaixin2000/ScreenSpot-Pro-GUI-Grounding (readme.md, LICENSE)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/likaixin/ScreenSpot-Pro
    title: "likaixin/ScreenSpot-Pro dataset card"
    accessed: "2026-09-08"
  - url: https://gui-agent.github.io/grounding-leaderboard/
    title: "ScreenSpot-Pro Leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ScreenSpot-Pro tests GUI grounding — locating the exact on-screen element an instruction refers to —
in professional software rather than the everyday consumer apps earlier grounding benchmarks focused
on. Given a screenshot and a natural-language instruction, a model must output the location of the
target element. Every image is an authentic, expert-captured screenshot from real professional
workflows (CAD, scientific computing, creative tools, IDEs and more) at native high resolution, so
targets are far smaller relative to the frame than on earlier benchmarks: about 0.07% of the
screenshot area on average, against 2.01% on the original ScreenSpot benchmark this one extends.

The authors built it because professional software had been left out of prior GUI agent research,
which concentrated on web browsing and mobile use, and because high resolution, small targets and
cluttered interfaces degrade grounding accuracy sharply compared to simpler consumer screens.

## How it is scored

A prediction is correct when the model's output point falls inside the human-annotated bounding box
for the target element, the click-in-box protocol used by the original ScreenSpot benchmark this one
extends. Overall accuracy is a micro-average across the benchmark's 1,581 instructions, with a
per-category breakdown across the six application groupings. No random baseline is meaningful given
how small targets are; the paper instead reports GPT-4o, used zero-shot as a general-purpose model
rather than a specialized grounder, scoring only 0.9% — illustrating how much this task rewards
purpose-built grounding models over general chat models.

## Dataset and licence

The benchmark comprises 1,581 instructions over screenshots spanning 23 applications across five
industry groupings (development and programming, creative, CAD and engineering, scientific and
analytical, office) plus operating-system-level tasks, across Windows, macOS and Linux. Experts with
at least five years of experience in each application recorded the tasks themselves, using a
purpose-built capture tool triggered by a shortcut key so annotations reflected real work rather than
staged scenarios; each instance was reviewed by at least two annotators. About 62.6% of targets are
text elements, the remainder icons. The dataset and code are released under the MIT licence and
distributed through Hugging Face (`likaixin/ScreenSpot-Pro`) and GitHub.

## Who publishes it

The paper was written by Kaixin Li, Ziyang Meng, Hongzhan Lin, Ziyang Luo, Yuchen Tian, Jing Ma,
Zhiyong Huang and Tat-Seng Chua. The project and dataset were first released in January 2025, with the
arXiv preprint posted that April and the work later presented at a Workshop on Reasoning and Planning
for Large Language Models. The authors maintain the dataset, evaluation code and a public leaderboard
directly; the benchmark has since been cited or adopted as an evaluation set by several other GUI-agent
projects, including Microsoft's OmniParser v2, Qwen2.5-VL and UI-TARS.

## Lineage

ScreenSpot-Pro is a direct successor to ScreenSpot (Cheng et al.), extending it from cropped,
easy-usage screenshots to authentic high-resolution professional software, and is commonly cited
alongside ScreenSpot-v2 as part of the same evaluation lineage; neither has its own page in this
repository yet. This repository tracks one direct variant, `screenspot_pro_tools`, covering scores
produced when a model uses an iterative search or agentic loop rather than single-shot grounding.

## Saturation and contamination

The benchmark opened very hard: the best existing grounding model at release, OS-Atlas-7B, scored
18.9%, and the paper's own proposed method, ScreenSeekeR (a cascaded visual search guided by a
planner model), pushed that to 48.1% without any additional training. The project's own leaderboard,
fetched directly for this page, currently lists its top entry at 82.7%, held by a specialized
grounding model using an iterative "zoom-in" strategy rather than a general frontier chat model —
consistent with the paper's own finding that reducing the search area is the single most effective
lever on this task. Scores still span a wide range across the leaderboard, so the benchmark separates
models well and is not saturated. Contamination risk is comparatively low, since the images are
authentic screen captures rather than text scraped from the public web.

## How to run it

The authors' repository ships `eval_screenspot_pro.py` (and a parallel variant) against an
OpenAI-compatible API; results are typically submitted to the project's own leaderboard rather than
run through a third-party harness such as lm-evaluation-harness or inspect_evals, neither confirmed to
include this task. Because top leaderboard entries mix single-shot grounding, iterative zoom or crop
strategies, and fully agentic planner-guided search, comparing two scores requires checking which
strategy each used — the distinction `screenspot_pro_tools` is meant to isolate.

## Reading the numbers

A high ScreenSpot-Pro score indicates a model, or a model paired with a grounding strategy, can find
small, specific UI elements in dense professional software — a prerequisite for reliable computer-use
agents in real work tools, not just consumer apps. It does not measure whether an agent can complete a
multi-step task in that software, only whether it can locate one element given a clear instruction.
Because the leaderboard is dominated by specialized fine-tuned grounders rather than general frontier
chat models, a strong general-purpose model's plain score can understate its usefulness once paired
with a search or zoom strategy — why the gap between this page and `screenspot_pro_tools` often
matters more than either number alone.
