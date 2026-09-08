---
id: zerobench
name: "ZeroBench"
aliases: []
page_kind: benchmark
category: multimodal
subcategory: "visual reasoning, adversarially filtered to be unsolved at release"
status: active
summary: "100 hand-made visual reasoning questions filtered so no evaluated frontier model answered any correctly at release, plus 334 subquestions to track partial progress."
measures: >
  ZeroBench pairs one or more images with a question requiring multi-step visual reasoning -- careful
  counting, spatial relations, fine detail extraction, cross-referencing several parts of an image --
  built by a pool of more than 20 human question creators and then adversarially filtered: any
  candidate question that a baseline model answered correctly was discarded. The surviving 100 "main"
  questions are ones no model in the authors' 20-model baseline set solved at release. Because a set of
  yes/no answers this hard would still be impossible to fully differentiate, each main question also
  has, on average, 3.3 companion "subquestions" (334 in total) covering the intermediate reasoning
  steps, which let a model that fails the main question still show partial progress. Images are mostly
  natural photographs (70 of 100) rather than synthetic compositions (30 of 100), and mostly single-image
  questions (93 of 100, with 7 requiring more than one image).
task_format: >
  Open-ended, free-text answers, required in the format "{final_answer}". Grading is exact string
  match against the reference answer, with no partial credit on the main questions, since the authors
  found no distance metric could fairly cover the diversity of correct-answer formats; questions with
  binary, multiple-choice or small-integer (under 10) answers were deliberately excluded during
  curation to keep guessing from working.
metric:
  name: "accuracy (pass@1 / pass@5 / pass^5)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 29.5
  baseline_note: >
    29.5% (standard deviation 27.1) is the paper's human baseline, from 15 evaluators (undergraduate
    and postgraduate students) each working a partition of the 100 questions with only the image(s) and
    question text, no external resources; inter-rater reliability across five duplicated question sets
    was a Pearson correlation of 0.82. The very high standard deviation reflects genuinely uneven
    difficulty across question sets (some near 0%, some near-perfect) rather than inconsistent grading,
    per the authors. No fixed random-guess baseline is established, since answers are open-ended free
    text and the authors deliberately excluded guessable answer formats.
dataset:
  size: 100
  size_note: >
    100 main questions, drawn from a pool of 140 candidate questions narrowed through a three-step
    pipeline: difficulty feedback against early baselines, human review for answerability and format
    (106 questions passed this step), then adversarial filtering that discarded any question a baseline
    model answered correctly (the strongest baseline scored just 4 of 106 before this final cut). A
    further 334 subquestions (about 3.3 per main question) were written during review to break each
    main question into its component reasoning steps. 93 of the 100 main questions use a single image,
    7 use multiple images; 70 use natural (photographic) images and 30 use synthetic ones.
  url: "https://huggingface.co/datasets/jonathan-roberts1/zerobench"
  license: ""
  languages:
    - en
  modalities:
    - image
    - text
  splits: "main questions (100) + subquestions (334); a single evaluation set, no train/test division"
  public_test_set: false
publisher:
  org: "University of Cambridge"
  authors:
    - "Jonathan Roberts"
    - "Mohammad Reza Taesiri"
    - "Ansh Sharma"
    - "Akash Gupta"
    - "Samuel Roberts"
    - "Ioana Croitoru"
    - "Simion-Vlad Bogolin"
    - "Jialu Tang"
    - "Florian Langer"
    - "Vyas Raina"
    - "Vatsal Raina"
    - "Hanyi Xiong"
    - "Vishaal Udandarao"
    - "Jingyi Lu"
    - "Shiyang Chen"
    - "Sam Purkis"
    - "Tianshuo Yan"
    - "Wenye Lin"
    - "Gyungin Shin"
    - "Qiaochu Yang"
    - "Anh Totti Nguyen"
    - "David I. Atkinson"
    - "Aaditya Baranwal"
    - "Alexandru Coca"
    - "Mikah Dang"
    - "Sebastian Dziadzio"
    - "Jakob D. Kunz"
    - "Kaiqu Liang"
    - "Alexander Lo"
    - "Brian Pulfer"
    - "Steven Walton"
    - "Charig Yang"
    - "Kai Han"
    - "Samuel Albanie"
  url: "https://github.com/jonathan-roberts1/zerobench"
paper:
  title: "ZeroBench: An Impossible Visual Benchmark for Contemporary Large Multimodal Models"
  arxiv: "2502.09696"
  url: "https://arxiv.org/abs/2502.09696"
  year: 2025
leaderboard_url: "https://zerobench.github.io/"
repo_url: "https://github.com/jonathan-roberts1/zerobench"
released: "2025-02"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    All 20 baselines evaluated at release scored 0% pass@1 and 0% pass^5 (correct on all of 5 samples);
    the best, Gemini 2 Flash Thinking, reached 5% pass@5 (correct on at least one of 5 samples). Tracking
    a further 26 models over the following year, the paper reports state-of-the-art climbing to 19%
    pass@5 (Gemini 3 Pro) and 6% pass^5 (GPT-5.2) -- real but still small progress against a 100-point
    scale, and the paper notes 47% of the 100 main questions had been answered correctly at least once,
    by at least one of the 46 evaluated models, cumulatively. The authors state this slower-than-typical
    erosion, compared to other hard benchmarks tracked over the same period, supports the benchmark's
    intended longevity.
contamination:
  risk: medium
  note: >
    The dataset ships a canary string (a superset of the BIG-bench canary string) specifically so
    benchmark data can be filtered out of future training corpora, and the Hugging Face repository is
    access-gated rather than freely downloadable. The authors are explicit that "canary strings are
    intended to discourage direct training on our benchmark, but [are] no guarantee." The benchmark's
    empirically slow saturation over its first 18 months is offered by the authors as partial evidence
    against severe contamination, though the questions and images have still been publicly discussed
    and red-teamed by outside users since release.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness was found to carry ZeroBench. The authors' GitHub repository publishes
    the reference prompt (a zero-shot chain-of-thought instruction ending in an explicit "{final_answer}"
    format requirement) and grading code (exact match after parsing the bracketed answer). Two decoding
    regimes are used: greedy, seeded decoding for a single deterministic pass@1 attempt, and stochastic
    decoding (temperature 0.7, top-p 0.95) sampled five times for pass@5 and pass^5. Because recent
    "thinking" models often run best at fixed, higher temperatures, the authors report only pass@5 and
    pass^5, not pass@1, for models evaluated after the initial release.
tags:
  - multimodal
  - visual-reasoning
  - adversarial-filtering
  - unsolved-at-release
  - exact-match
sources:
  - url: "https://arxiv.org/abs/2502.09696"
    title: "ZeroBench: An Impossible Visual Benchmark for Contemporary Large Multimodal Models (Roberts et al., arXiv:2502.09696)"
    accessed: "2026-09-08"
  - url: "https://github.com/jonathan-roberts1/zerobench"
    title: "jonathan-roberts1/zerobench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jonathan-roberts1/zerobench"
    title: "jonathan-roberts1/zerobench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://zerobench.github.io/"
    title: "ZeroBench project page and leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ZeroBench pairs one or more images with a question that demands multi-step visual reasoning: careful
counting, spatial relations, fine visual detail, or cross-referencing several parts of an image at once,
rather than a single glance-and-answer. The 100 main questions were written by a pool of more than 20
human question creators, then adversarially filtered -- any candidate a baseline model answered
correctly was discarded -- so the surviving set was, by construction, unsolved by every model in the
authors' 20-model baseline at release. Most main questions (93 of 100) use a single image; most images
(70 of 100) are ordinary photographs rather than synthetic compositions. Because a 100-question,
all-or-nothing set gives little signal about partial progress, each main question also carries several
companion "subquestions" (334 in total, averaging 3.3 per question) covering the intermediate reasoning
steps.

## How it is scored

Both main questions and subquestions are graded by exact string match: the model must place its answer
in curly braces, like "{final_answer}", and that text is compared directly against the reference answer,
with no partial credit. The authors chose exact match deliberately, having found no distance-based metric
that fairly covered the diversity of valid answer formats across 100 hand-written questions; they also
excluded binary, multiple-choice and small-integer (under 10) answers during curation specifically to
keep guessing from inflating scores. Because thinking-style models often perform best at higher, fixed
sampling temperatures, the authors track three metrics rather than one: pass@1 (a single deterministic
attempt), pass@5 (correct on at least one of five stochastic samples) and pass^5 (correct on all five) --
and report only the latter two for models evaluated after the initial release, since single-sample pass@1
becomes unstable for high-temperature models.

## Dataset and licence

100 main questions survived a three-step pipeline that started from 140 candidates: difficulty feedback
against early baseline models, then human review for answerability, formatting and sufficient difficulty
(106 questions passed this step), then adversarial filtering that discarded any question a baseline
model got right (the strongest scored just 4 of 106 before that final cut). 334 subquestions were
written alongside this process. The GitHub repository is released under the MIT licence; the Hugging
Face dataset repository is access-gated and carries a canary string to keep it out of future training
corpora, and this page did not find a separate published licence tag for the dataset content itself.

## Who publishes it

ZeroBench was introduced by Jonathan Roberts and 33 co-authors, led from the University of Cambridge with
contributors at numerous other institutions, and posted to arXiv in February 2025; the paper was accepted
at ICML 2026. The authors maintain the GitHub repository, the gated Hugging Face dataset, and a public
project page and leaderboard at zerobench.github.io, which they have continued updating -- including an
evaluation-protocol correction in August 2026 -- well past the original release.

## Lineage

ZeroBench names no direct predecessor or successor in this repository, but the paper positions itself
against a line of "difficulty-first" benchmarks built to resist quick saturation -- ARC-AGI, GPQA, GRAB,
HumanEval-V, VibeEval and the concurrently developed Humanity's Last Exam -- arguing those eroded faster
than intended and that ZeroBench's adversarial filtering was designed to hold up longer. No successor
benchmark building directly on ZeroBench was identified.

## Saturation and contamination

At release, all 20 evaluated baselines scored 0% on both pass@1 and pass^5; the single best, Gemini 2
Flash Thinking, managed 5% pass@5. Tracking 26 further models over the following year, the paper reports
state-of-the-art climbing to 19% pass@5 (Gemini 3 Pro) and 6% pass^5 (GPT-5.2), with 47% of the 100 main
questions solved at least once by at least one of the 46 models evaluated cumulatively -- real movement,
but still far from saturated on a 100-point scale. Contamination risk is medium: the dataset carries a
canary string and gated access specifically to deter training-set inclusion, but the authors themselves
note this "is no guarantee," and 18 months of public discussion and red-teaming since release make some
exposure plausible even so; the benchmark's comparatively slow score growth over that period is the
authors' own partial evidence against severe leakage.

## How to run it

No major third-party harness was found to carry ZeroBench. The authors' GitHub repository is the
reference implementation: a fixed zero-shot chain-of-thought prompt ending in an explicit
bracketed-answer instruction, and exact-match grading code after parsing that bracket. Reported scores
differ by decoding regime (one greedy pass for pass@1 versus five stochastic samples at temperature 0.7
for pass@5 and pass^5), and for models released after the original evaluation, only pass@5 and pass^5
are typically reported, so a bare "ZeroBench score" without a stated metric name is ambiguous.

## Reading the numbers

A non-zero ZeroBench score is meaningful on its own, given the benchmark was built so no evaluated model
could score at release; a pass^5 score above zero specifically means a model answered a question
correctly and consistently across five independent attempts, not just once by chance. Because pass@1
becomes unreliable for high-temperature "thinking" models, prefer pass@5 and pass^5 when comparing
recent models, and check which of the three metrics a reported number uses before comparing it to
another. Even the strongest scores remain well below the human baseline's already-low 29.5% mean, so
treat any ZeroBench number as a measure of remaining headroom, not near-human capability.
