---
id: vstar_bench
name: "V*Bench"
aliases: ["VStar_Bench", "vstar-bench", "V-Star Bench"]
page_kind: benchmark
category: multimodal
subcategory: "high-resolution visual search and grounding"
status: active
summary: "A 191-question visual-question-answering test built from high-resolution, visually crowded images, designed so a model cannot answer correctly without precisely locating a small target detail."
measures: >
  V*Bench shows a model a high-resolution photograph (drawn from the SA-1B dataset, averaging
  2246x1582 pixels) that is visually crowded with detail, and asks a multiple-choice question that
  can only be answered correctly by finding and closely inspecting one small, specific region -- an
  object's colour or material, or the relative position between two objects -- rather than reading
  the image at a glance. It targets a gap the authors identified in multimodal LLMs of the time:
  models that performed well on benchmarks built from smaller, sparser images failed once the
  informative detail was small relative to the whole frame, because they lacked any mechanism for
  deliberately searching the image the way a person visually scans a crowded scene for something
  specific.
task_format: "Multiple-choice visual question answering: one high-resolution image plus a question in, one selected option out (four options for attribute questions, two for spatial-relationship questions)."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 37.5
  human_baseline: null
  baseline_note: >
    Random-guess baseline is approximate: attribute-recognition questions offer four options (25%
    chance) and spatial-relationship questions offer two (50% chance), for a size-weighted blended
    random baseline near 37.5% (115 four-option plus 76 two-option questions); the paper does not
    report this figure directly. No controlled human baseline is published.
dataset:
  size: 191
  size_note: >
    191 questions over 191 high-resolution images from the SA-1B (Segment Anything 1B) dataset,
    split into two sub-tasks: attribute recognition (115 samples, e.g. an object's colour or
    material) and spatial relationship reasoning (76 samples, the relative position between two
    objects). Confirmed by summing the two sub-task counts in the paper and by the Hugging Face
    datasets-server's single "test" split of 191 rows.
  url: "https://huggingface.co/datasets/craigwu/vstar_bench"
  license: ""
  languages: ["en"]
  modalities: ["image", "text"]
  splits: "single 'test' split, 191 rows (115 attribute recognition, 76 spatial relationship reasoning)"
  public_test_set: true
publisher:
  org: "New York University; UC San Diego"
  authors: ["Penghao Wu", "Saining Xie"]
  url: "https://vstar-seal.github.io/"
paper:
  title: "V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs"
  arxiv: "2312.14135"
  url: "https://arxiv.org/abs/2312.14135"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/penghao-wu/vstar"
released: "2023-12"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 75.39
  as_of: "2023-12"
  note: >
    In the paper's own Table 1, the strongest off-the-shelf model tested, GPT-4V (as accessed October
    2023), scored 54.97% overall (51.30% attribute, 60.52% spatial); the authors' own SEAL
    architecture, built around the V* guided visual search mechanism this benchmark was designed to
    motivate, reached 75.39% (74.78%/76.31%). SEAL is a purpose-built research system rather than a
    general frontier model, so its score should not be read as representative of an off-the-shelf
    multimodal LLM. No later, updated leaderboard was found during this research; treat these as the
    benchmark's original launch-era numbers rather than a current picture.
contamination:
  risk: low
  note: >
    Images are drawn from SA-1B, and the specific 191 questions were newly written and curated by
    the authors for this benchmark rather than sourced from an existing public QA dataset, so
    exact-answer memorization is less likely than for a benchmark built from pre-existing text. The
    images and answers have nonetheless been publicly downloadable since December 2023.
harness:
  lm_eval: ""
  inspect_evals: "vstar_bench_attribute_recognition, vstar_bench_spatial_relationship_reasoning (two separate tasks, not one combined score)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The authors' own vstar_bench_eval.py in the penghao-wu/vstar repository is the reference implementation; a separate visual_search.py evaluates the V* search mechanism itself against annotated target-object bounding boxes."
tags: ["multimodal", "visual-search", "high-resolution", "visual-grounding", "multiple-choice"]
sources:
  - url: "https://arxiv.org/abs/2312.14135"
    title: "V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs (Wu and Xie, 2023)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2312.14135"
    title: "V* paper, full text (ar5iv HTML) -- benchmark composition and Table 1 baseline results"
    accessed: "2026-09-08"
  - url: "https://github.com/penghao-wu/vstar"
    title: "penghao-wu/vstar GitHub repository (MIT licence, benchmark format, evaluation scripts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/craigwu/vstar_bench"
    title: "craigwu/vstar_bench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/vstar_bench"
    title: "inspect_evals vstar_bench README (two-task split, scoring)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

V*Bench shows a model a high-resolution photograph -- drawn from the SA-1B dataset, averaging
2246x1582 pixels and chosen to be visually crowded with detail -- and asks a multiple-choice question
answerable only by finding and closely inspecting one small, specific region of the image.
Attribute-recognition questions ask about a property (colour, material) of a named object;
spatial-relationship questions ask how two objects are positioned relative to each other. Both
require precise visual grounding rather than a glance at the whole scene. The authors built it to
expose a gap in multimodal LLMs of the time: strong performance on benchmarks built from smaller or
sparser images did not carry over once the informative detail became small relative to the frame,
because those models had no mechanism for deliberately searching an image the way a person visually
scans a crowded scene for something specific.

## How it is scored

Each question is graded as simple multiple-choice accuracy: four options for attribute-recognition
questions, two (binary) for spatial-relationship questions, with the first-listed option correct by
default in the released annotation format. There is no partial credit and no free-response grading
involved. A size-weighted blended random-guess baseline works out to roughly 37.5% given the 115
four-option and 76 two-option questions, though the paper itself does not report this figure
directly.

## Dataset and licence

The benchmark consists of 191 questions over 191 images: 115 for attribute recognition and 76 for
spatial relationship reasoning, hosted as a single "test" split on Hugging Face
(`craigwu/vstar_bench`). Images come from SA-1B (Meta's Segment Anything 1B image corpus, itself
released under its own research-use dataset licence, separate from V*Bench's own terms). No licence
is stated on the `craigwu/vstar_bench` Hugging Face dataset card itself; the code repository that
hosts the benchmark (`penghao-wu/vstar`) is MIT-licensed, but that licence covers the evaluation code
rather than the benchmark's images and annotations explicitly. Both test images and questions were
selected and written by human annotators specifically to resist guessing without accurate visual
grounding.

## Who publishes it

V*Bench was introduced by Penghao Wu and Saining Xie, spanning New York University and UC San Diego,
in "V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs" (arXiv, December 2023). The
benchmark is a component of that paper rather than an independent release: it exists to demonstrate
the value of the paper's own proposed visual-search mechanism (V*) and the SEAL architecture built
around it. The authors maintain the reference repository and a project page; no separate organisation
runs an independent leaderboard.

## Lineage

V*Bench has no predecessor or successor benchmark in this repository. It was constructed specifically
to contrast with existing multimodal benchmarks the authors judged too easy or too low-resolution to
require deliberate visual search, rather than as a revision of an earlier benchmark. Inspect Evals
implements it as two separate tasks -- `vstar_bench_attribute_recognition` and
`vstar_bench_spatial_relationship_reasoning` -- which this repository does not yet document as their
own subset pages.

## Saturation and contamination

At the benchmark's introduction (Table 1 of the paper, using GPT-4V as accessed October 2023), the
strongest general-purpose model tested scored 54.97% overall; the authors' own SEAL system, built
around the V* search mechanism the paper introduces, reached 75.39%, a result the paper frames as
evidence for guided visual search rather than as a fair baseline for a general frontier model. No
updated leaderboard or more recent third-party evaluation table was found during this research, so
current saturation status for 2025-2026 multimodal models is not established here -- current-
generation vision-language models are commonly evaluated against V*Bench in their own technical
reports, but this research did not locate a maintained, comparable table of those results.
Contamination risk is low: the questions were newly authored for this benchmark rather than drawn
from an existing public QA corpus, though the images and answers have been downloadable since
December 2023.

## How to run it

The authors' own repository (`penghao-wu/vstar`) is the reference implementation, with
`vstar_bench_eval.py` scoring a model's multiple-choice answers and a separate `visual_search.py` for
evaluating the V* search mechanism itself against the dataset's annotated bounding boxes. Inspect
Evals packages the benchmark as two independent tasks with a built-in multiple-choice scorer,
splitting attribute recognition from spatial-relationship reasoning rather than reporting one
combined score; running both together (via `inspect eval-set`) is the closest match to the paper's
original combined reporting. No lm-evaluation-harness, HELM, BIG-bench or OpenCompass task was
confirmed for this benchmark during this research.

## Reading the numbers

A high V*Bench score shows a model can locate and reason about a small, specific detail in a large,
cluttered image rather than only handling prominent, easily-noticed visual elements -- a meaningfully
different skill from general VQA competence. Because the benchmark is small (191 questions),
single-digit-question differences move the percentage score noticeably, so treat close scores between
two models with caution. The original paper's own comparison mixed a specialised research system
(SEAL) in with general-purpose models, so when reading a reported score, check whether it reflects an
off-the-shelf multimodal LLM or a system built with extra visual-search tooling specifically for this
kind of task.
