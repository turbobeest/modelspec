---
id: lab_bench_figqa
name: "LAB-Bench: FigQA"
aliases:
  - FigQA
page_kind: benchmark
category: domain
subcategory: biology research - figure interpretation
status: active
summary: 226 multiple-choice questions that give a model only a biology-paper figure image, no caption or text, and ask it to reason about the figure's content.
measures: >
  FigQA is one of seven task categories in FutureHouse's LAB-Bench, a suite built to test practical
  biology-research skills rather than textbook recall. FigQA shows the model an image of a figure
  taken from a biology research paper, with no caption, surrounding text or paper title, and asks a
  multiple-choice question that usually requires integrating information from several elements of the
  figure at once. The task's authors describe it as a visual analogue of multi-hop text benchmarks
  such as HotpotQA. It requires a model to be multi-modal but was designed, by its authors, to need no
  external tool use: the image alone should contain everything needed to answer.
task_format: >
  Multiple-choice question over a single figure image (no caption or paper text provided), five or
  more options including an explicit option to decline for lack of information.
metric:
  name: precision (correct / attempted)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    LAB-Bench reports two scores throughout: accuracy (correct / all questions) and precision
    (correct / attempted, i.e. excluding declined questions); coverage (attempted / all) is reported
    separately. Because models decline at very different rates, precision and accuracy can diverge
    substantially for the same model, and both are worth reading rather than either alone. The original
    paper gives no single printed human-baseline percentage for FigQA (human performance is shown only
    as a line on a bar chart); Anthropic's Claude 4 System Card (May 2025) plots a FigQA human baseline
    at roughly three-quarters correct, well above every model shown in that chart.
dataset:
  size: 226
  size_note: >
    226 questions, one of eight rows in the paper's category table (LitQA2 248, SuppQA 102, FigQA 226,
    TableQA 305, DbQA 650 across 10 subtasks, ProtocolQA 135, SeqQA 750 across 15 subtasks,
    CloningScenarios 41), for a combined LAB-Bench total of over 2,400 questions. FutureHouse makes
    roughly 80% of each subtask public and holds back the rest to monitor for future contamination.
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
  authors:
    - Jon M. Laurent
    - Joseph D. Janizek
    - Michael Ruzo
    - Michaela M. Hinks
    - Michael J. Hammerling
    - Siddharth Narayanan
    - Manvitha Ponnapati
    - Andrew D. White
    - Samuel G. Rodriques
  url: https://github.com/Future-House/LAB-Bench
paper:
  title: "LAB-Bench: Measuring Capabilities of Language Models for Biology Research"
  arxiv: "2407.10362"
  url: https://arxiv.org/abs/2407.10362
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/Future-House/LAB-Bench
released: "2024-07"
last_updated: "2025-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - lab_bench_figqa_tools
saturation:
  status: open
  top_score: 54.9
  as_of: "2025-11"
  note: >
    At the July 2024 release, all models the authors tested showed "near-random" FigQA precision
    except Claude 3.5 Sonnet, which scored well above the rest. Anthropic's Claude 4 System Card (May
    2025) later found Claude Opus 4 and Claude Sonnet 4 scoring lower than Claude Sonnet 3.7 had on
    this specific task even as they improved elsewhere. The most recent figure found in this research,
    Claude Opus 4.5's no-tools, no-reasoning baseline of 54.9% (Anthropic, November 2025), remains well
    below the roughly 75% human baseline shown in the same source, so the task is not saturated.
contamination:
  risk: low
  note: >
    FutureHouse withholds roughly 20% of each subtask, including FigQA, specifically to monitor for
    contamination, and the public/private split performance is reported separately in the paper's
    supplemental material. Because FigQA questions are built from arbitrary figures the authors
    screenshotted from papers rather than from a fixed, widely mirrored public file, the paper's own
    limitations discussion does not flag it as a high leakage risk the way heavily-circulated
    benchmarks are.
harness:
  lm_eval: ""
  inspect_evals: lab_bench_figqa
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - domain
  - biology
  - multimodal
  - multiple-choice
  - figure-interpretation
sources:
  - url: https://arxiv.org/abs/2407.10362
    title: "LAB-Bench: Measuring Capabilities of Language Models for Biology Research (arXiv:2407.10362)"
    accessed: "2026-09-08"
  - url: https://github.com/Future-House/LAB-Bench
    title: "Future-House/LAB-Bench (repository description and licence)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/futurehouse/lab-bench
    title: "futurehouse/lab-bench dataset card"
    accessed: "2026-09-08"
  - url: https://www.anthropic.com/claude-4-system-card
    title: "System Card: Claude Opus 4 & Claude Sonnet 4 (Anthropic, May 2025), Section 7.2.4.7"
    accessed: "2026-09-08"
  - url: https://www.anthropic.com/claude-opus-4-5-system-card
    title: "System Card: Claude Opus 4.5 (Anthropic, November 2025), Section 2.21"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/lab_bench
    title: "inspect_evals: lab_bench_figqa task implementation"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FigQA is one of seven task categories in LAB-Bench, a suite FutureHouse built to test practical
biology-research skills — literature search, figure and table interpretation, database navigation,
protocol understanding, and DNA/protein sequence manipulation — rather than textbook-style recall. The
task shows a model an image of a figure taken from a biology research paper, deliberately stripped of
its caption, surrounding text and paper title, and asks a multiple-choice question that usually
requires integrating several elements of the figure at once. Its authors compare it to a visual
version of multi-hop text benchmarks like HotpotQA. FigQA requires the model to be multi-modal but,
unlike some other LAB-Bench tasks, was designed to need no external tool use.

## How it is scored

Every question offers an explicit "insufficient information" option alongside the substantive
choices, so LAB-Bench reports two headline numbers: accuracy (correct answers divided by all
questions) and precision (correct answers divided only by questions the model chose to attempt).
Coverage — the attempted share — is reported alongside both, since models vary widely in how often
they decline. The paper's own results show this matters: some models achieve reasonable precision by
attempting few, easy-seeming questions, while others attempt nearly everything and post lower
precision as a result. A supplemental open-answer variant (removing the multiple-choice options)
showed materially lower scores for the two models tested, indicating some multiple-choice performance
comes from eliminating implausible distractors rather than true comprehension.

## Dataset and licence

FigQA contributes 226 of LAB-Bench's more than 2,400 total questions, alongside LitQA2 (248), SuppQA
(102), TableQA (305), DbQA (650 across 10 subtasks), ProtocolQA (135), SeqQA (750 across 15 subtasks)
and CloningScenarios (41). Questions were generated manually by the paper's authors and contracted
biology experts, who selected papers, extracted a figure, and wrote a question that couldn't be
answered from the figure's caption or surrounding text alone. The dataset is released under CC BY-SA
4.0 and hosted on Hugging Face (`futurehouse/lab-bench`); FutureHouse publishes roughly 80% of each
subtask's questions and withholds the remainder to monitor for contamination going forward.

## Who publishes it

LAB-Bench comes from FutureHouse, a nonprofit AI-for-science research lab, with authors Jon M.
Laurent, Joseph D. Janizek, Michael Ruzo, Michaela M. Hinks, Michael J. Hammerling, Siddharth
Narayanan, Manvitha Ponnapati, Andrew D. White and Samuel G. Rodriques. The paper was submitted to
NeurIPS 2024's Datasets and Benchmarks track and posted to arXiv in July 2024. FutureHouse maintains
the reference dataset and states an intent to keep expanding LAB-Bench over time; there is no
separate, continuously updated public leaderboard beyond the dataset repository itself.

## Lineage

FigQA has no named predecessor; it is one of eight sibling task categories introduced together in the
original LAB-Bench paper, several of which (LitQA2, SuppQA, DbQA, SeqQA) are explicitly tool-dependent
by design in a way FigQA is not. This repository tracks one direct variant, `lab_bench_figqa_tools`,
covering FigQA scores produced when a model is given tool access such as an image-cropping tool,
rather than the untooled default this page describes.

## Saturation and contamination

At release, LAB-Bench's authors found FigQA the hardest category in the suite: most models scored
near-random precision, with Claude 3.5 Sonnet a clear outlier above the rest. Progress since has been
uneven rather than steadily upward — Anthropic's Claude 4 System Card (May 2025) found Claude Opus 4
and Claude Sonnet 4 scoring *below* Claude Sonnet 3.7 on this specific task, even as those models
improved on other LAB-Bench categories. The most recent figure located in this research, Claude Opus
4.5's untooled baseline of 54.9% (Anthropic, November 2025), still sits well under the roughly 75%
human baseline plotted in the same source. Contamination risk is comparatively low: FutureHouse
withholds a private portion of each subtask specifically to monitor for it, and FigQA's images are not
a single widely-mirrored file that would circulate easily.

## How to run it

UK AISI's `inspect_evals` package implements this task under the exact id `lab_bench_figqa`, pulling
from the same public Hugging Face subset. The original paper's own evaluation ran every model without
external tools and used k-shot prompting; Anthropic's system cards have since evaluated it both this
way and with tool access, using 0-shot prompting in the more recent case, so scores from different
sources may not share a prompting protocol even when both report "no tools."

## Reading the numbers

A strong FigQA score suggests a model can extract and cross-reference quantitative or structural
information from an unlabelled scientific figure, a narrower and more visually demanding skill than
general chart or document QA. It does not by itself indicate broader biology-research competence —
that is closer to what LAB-Bench's other, more tool-dependent categories test. Because coverage
(willingness to attempt a question) varies so much between models, always check whether a reported
number is accuracy or precision before comparing two models, and treat FigQA scores from before and
after a change in tool access or prompting protocol as not directly comparable.
