---
id: lingoly
name: "LingOly"
aliases:
  - "LINGOLY"
  - "Linguistic Olympiad Benchmark"
page_kind: benchmark
category: reasoning
subcategory: "olympiad-level linguistic reasoning puzzles in low-resource and extinct languages"
status: active
summary: "1,133 UK-Linguistics-Olympiad-style puzzles across 90+ mostly low-resource languages, scored on direct accuracy and a no-context control that penalises memorisation."
measures: >
  LingOly gives a model a full linguistics-olympiad problem sheet -- background on an unfamiliar,
  usually very low-resource or extinct, language, a set of example words or sentences, and one or
  more sub-questions -- then asks it to answer specific sub-questions using only the patterns shown
  on the sheet. Six question formats appear (including translation into and out of the target
  language, pattern completion, and match-up tasks) across five levels of human difficulty. Because
  the target languages are deliberately obscure, a correct answer should come from in-context
  pattern generalisation rather than from facts the model already knew about the language, and the
  benchmark also tests whether a model can follow the sheet's often intricate formatting instructions.
task_format: >
  Free-text answer generation from a full problem-sheet prompt (background, worked examples, and the
  specific sub-question), with the model told to return a JSON object keyed by sub-question number;
  answers are graded per sub-question, not per sheet.
metric:
  name: "exact match accuracy, plus a no-context delta"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    There is no meaningful random-guess baseline for free-text linguistic translation, so the paper
    instead reports a no-context control: the same sub-questions asked without the problem sheet's
    background and worked examples. The gap between full-context and no-context accuracy (the paper
    calls this delta_NC) is the primary check against memorisation rather than genuine in-context
    reasoning. On the harder problems, even the strongest of the 11 models the paper evaluated in
    2024 reached only 38.7% full-context accuracy, a 24.7-point improvement over its own no-context
    score.
dataset:
  size: 1133
  size_note: >
    1,133 problems across 6 question formats and 5 human-difficulty levels, drawn from more than 90
    languages and dialects (the paper notes the exact count depends on how variants are counted),
    ranging from higher-resource languages such as Dutch to extremely low-resource ones such as
    Yawalapiti (paper-reported fewer than 10 native speakers); a small number of problems use
    constructed variants of real languages or language games. The public release is gated on
    Hugging Face behind an acceptable-use agreement and carries a canary string. The inspect_evals
    reference implementation separately reports evaluating 408 "samples" for the full dataset, a
    unit (most plausibly problem sheets rather than individual sub-questions) this page could not
    reconcile against the paper's 1,133-problem count.
  url: "https://huggingface.co/datasets/ambean/lingOly"
  license: >
    The Hugging Face dataset card states CC BY-NC-ND 4.0 plus an acceptable-use policy that forbids
    redistributing questions or answers in a web-scrapable plain-text format and forbids training
    directly on the benchmark. The GitHub repository itself carries no machine-readable licence
    (GitHub's own API reports its licence as unassigned).
  languages:
    - "90+ languages and dialects, mostly low-resource or extinct (not enumerated here; see the paper's appendix for the full list)"
  modalities:
    - text
  splits: "single evaluation pool, no train/test split; access requires accepting the dataset's acceptable-use terms on Hugging Face"
  public_test_set: true
publisher:
  org: "University of Oxford (Oxford Internet Institute), with co-authors at Stanford University, the UK Linguistics Olympiad and Meedan"
  authors:
    - "Andrew M. Bean"
    - "Simi Hellsten"
    - "Harry Mayne"
    - "Jabez Magomere"
    - "Ethan A. Chi"
    - "Ryan Chi"
    - "Scott A. Hale"
    - "Hannah Rose Kirk"
  url: "https://github.com/am-bean/lingOly"
paper:
  title: "LingOly: A Benchmark of Olympiad-Level Linguistic Reasoning Puzzles in Low-Resource and Extinct Languages"
  arxiv: "2406.06196"
  url: "https://arxiv.org/abs/2406.06196"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/am-bean/lingOly"
released: "2024-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 41.7
  as_of: "2025-06"
  note: >
    This page found no continuously maintained public leaderboard for LingOly. The paper's own
    headline figure -- even the top of 11 evaluated models reached only 38.7% accuracy on the
    harder problems in 2024 -- shows deliberate headroom by design. The most recent confirmed
    figure found here is inspect_evals' own reproduction: GPT-4o scoring 41.7% full-context accuracy
    (versus 13.6% with no context) over the complete 408-sample evaluation set in June 2025, next to
    a paper-reported score of 37.6% for the same model on the same metric. inspect_evals attributes
    the gap between its number and the paper's to implementation and model-stochasticity
    differences rather than a scoring disagreement.
contamination:
  risk: low
  note: >
    The benchmark was deliberately built from very low-resource and extinct languages specifically
    to reduce the odds that any exact problem was already in a model's training data, and the
    public release is gated behind an acceptable-use agreement (no redistribution in scrapable
    plain text, no training directly on the benchmark) plus a canary string. Risk is not zero:
    accepting the Hugging Face gate does grant the full problem set with answers, and the benchmark
    has been available that way since June 2024.
harness:
  lm_eval: "lingoly (group over lingoly_context and lingoly_nocontext)"
  inspect_evals: "lingoly"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - linguistics
  - reasoning
  - low-resource-languages
  - olympiad
  - contamination-resistant
sources:
  - url: "https://arxiv.org/abs/2406.06196"
    title: "LingOly: A Benchmark of Olympiad-Level Linguistic Reasoning Puzzles in Low-Resource and Extinct Languages"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2406.06196"
    title: "LingOly paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/am-bean/lingOly"
    title: "am-bean/lingOly GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ambean/lingOly"
    title: "ambean/lingOly dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/lingoly/README.md"
    title: "inspect_evals lingoly task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lingoly/README.md"
    title: "lm-evaluation-harness lingoly task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LingOly gives a model a full linguistics-olympiad problem sheet: background on an unfamiliar, usually very low-resource or extinct, language, a set of worked examples, and one or more sub-questions, drawn from real UK Linguistics Olympiad-style material. The model must answer specific sub-questions -- translating a phrase, completing a pattern, matching forms -- using only the information on the sheet. Six question formats and five levels of human difficulty are represented, across more than 90 languages and dialects, from higher-resource languages such as Dutch down to languages the paper reports have fewer than ten living speakers.

Because the target languages are deliberately obscure, a correct answer should reflect in-context pattern generalisation rather than facts the model already knew about the language going in, and following the sheet's often intricate formatting and instruction-following demands is itself part of what the benchmark tests.

## How it is scored

Models generate free text, prompted to return a JSON object keyed by sub-question number, and answers are graded by exact match after normalisation, per sub-question rather than per sheet. There is no meaningful random-guess baseline for free-text translation, so LingOly instead reports a no-context control: the same sub-questions asked without the background and worked examples that would let a model actually solve them from the sheet. The gap between full-context and no-context accuracy (see Saturation and contamination for figures) is the paper's main defence against a model getting credit for having memorised a public puzzle rather than reasoning from what it was given.

## Dataset and licence

LingOly totals 1,133 problems across 6 formats and 5 difficulty levels, drawn from more than 90 languages and dialects (the paper notes the exact count depends on how variants are counted); a small number use constructed variants of real languages or language games. The public release is hosted on Hugging Face (`ambean/lingOly`) but gated behind an acceptable-use agreement forbidding scrapable-plain-text redistribution and direct training on the benchmark, and carries a canary string. The dataset card states CC BY-NC-ND 4.0; the GitHub repository carries no machine-readable licence field. inspect_evals' own results table separately reports evaluating 408 "samples" for the complete dataset, a unit -- most plausibly problem sheets rather than individual sub-questions -- this page could not reconcile against the paper's 1,133-problem count.

## Who publishes it

LingOly comes from Andrew M. Bean, Simi Hellsten, Harry Mayne, Jabez Magomere, Scott A. Hale and Hannah Rose Kirk at the University of Oxford's Oxford Internet Institute, together with Ethan A. Chi and Ryan Chi at Stanford University; Hellsten is also affiliated with the UK Linguistics Olympiad and Hale with Meedan. The paper was posted to arXiv in June 2024 and received an oral presentation at the NeurIPS 2024 Datasets and Benchmarks track. The authors maintain the reference implementation at `github.com/am-bean/lingOly`.

## Lineage

This repository does not track a predecessor for LingOly; it draws its puzzles from genuine linguistics-olympiad material rather than from an earlier computational benchmark. The same authors later released LingOly-TOO (also called L2), which re-uses 82 of the original LingOly problems but applies templatised orthographic obfuscation to counter answering by guessing or memorisation; it is documented by its own paper (arXiv:2503.02972) and repository (`github.com/jkhouja/L2`) but does not yet have a page in this repository.

## Saturation and contamination

No continuously maintained public leaderboard was found for LingOly. The original paper's own framing already shows deliberate headroom: even its top model of 11 evaluated reached only 38.7% accuracy on the harder problems in 2024. The most recent confirmed figure available here is inspect_evals' June 2025 reproduction, which scored GPT-4o at 41.7% full-context accuracy against 13.6% with no context, versus a paper-reported 37.6% for the same model -- a gap inspect_evals attributes to implementation and stochasticity differences rather than disagreement about the score. Contamination risk is low by design: the deliberately low-resource and extinct language selection, the Hugging Face access gate with its no-redistribution and no-training terms, and the canary string all work against a problem showing up verbatim in a training corpus, though the risk is not zero once a user accepts the gate and receives the full answer set.

## How to run it

lm-evaluation-harness implements LingOly as a task group named `lingoly`, combining a `lingoly_context` task (full sheet, exact match against the reference answer) and a `lingoly_nocontext` task (background and examples stripped out) and computing the delta between them. inspect_evals ships the same design as the `lingoly` task, reading directly from the gated Hugging Face dataset and reporting both a full-context score and a no-context delta. Neither HELM, OpenCompass nor BIG-bench was confirmed to carry a LingOly task in the sources reviewed for this page.

## Reading the numbers

A high LingOly score is meaningful only alongside its own no-context companion score: a model that does nearly as well without the problem sheet as with it is more likely retrieving something memorised than reasoning from the examples given, while a large full-context-minus-no-context gap is closer to the in-context generalisation the benchmark is trying to isolate. Because the dataset spans five difficulty levels and highly uneven language-resource levels, an aggregate score can hide a model that does well on easy, higher-resource-language problems while failing consistently on the hardest, most obscure ones -- the paper itself found scores fell as language resourcing dropped. Treat LingOly as evidence about a narrow, deliberately unfamiliar kind of multi-step pattern reasoning and instruction-following, not as a general linguistics or translation-quality benchmark.
