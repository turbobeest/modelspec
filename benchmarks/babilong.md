---
id: babilong
name: "BABILong"
aliases:
  - "bAbILong"
page_kind: benchmark
category: long-context
subcategory: "long-context reasoning over bAbI tasks embedded in distractor text"
status: active
summary: "Embeds the 20 classic bAbI reasoning tasks as needles inside long PG19 book text, testing whether models can find and combine scattered facts at context lengths up to millions of tokens."
measures: >
  BABILong tests whether a model can locate and combine facts scattered across an extremely long
  document, rather than concentrated near the question. It takes the 20 classic bAbI tasks --
  synthetic reasoning problems originally designed to isolate single skills such as single-fact
  retrieval, two- or three-fact chaining, counting, listing, and simple induction or deduction --
  and embeds each task's fact sentences inside long passages of unrelated book text drawn from the
  PG19 corpus, so the relevant sentences sit surrounded by large amounts of plausible-looking but
  irrelevant narrative. A model must find the scattered facts within that noise and answer a
  question that depends on combining them correctly. Because the amount of distractor text is
  controlled independently of the underlying reasoning task, BABILong isolates a model's ability to
  use a long context from its ability to solve the reasoning problem itself.
task_format: "A long document built from PG19 book excerpts with bAbI fact sentences and a question inserted at controlled positions; free-form short-answer output, evaluated at fixed context lengths from 0k tokens up to 10M (extended to 50M in fine-tuned recurrent-memory experiments)."
metric:
  name: "accuracy (per-task answer match), typically averaged over QA1-QA5 as a headline figure"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No fixed random or human baseline applies since answer formats vary by task (a name, a location, a count, a yes/no). The paper instead evaluates each model at a series of fixed context lengths and reports degradation relative to that same model's own 0k (no-distractor) accuracy, so headroom is defined relative to a model's short-context ceiling rather than one universal reference number."
dataset:
  size: null
  size_note: "BABILong is a generator, not one fixed item count: the reference implementation pre-generates fixed splits at lengths the paper states as 0k, 4k, 8k, 16k, 32k, 64k, 128k, 512k, 1M and 10M tokens, for each of the 20 bAbI tasks (QA1-QA20); the Hugging Face RMT-team/babilong mirror additionally lists 2k and 256k configurations. lm-evaluation-harness's reference task reports 1,000 samples per QA task at 0k."
  url: "https://huggingface.co/datasets/RMT-team/babilong"
  license: "Apache-2.0 (code and PG-19 background text); BSD (underlying bAbI task source)"
  languages: ["en"]
  modalities: ["text"]
  splits: "configs by context length (0k through 10M tokens) x 20 QA tasks (QA1-QA20); QA1-QA5 support the full length range, QA6-QA20 are provided at 0k in the reference implementation"
  public_test_set: true
publisher:
  org: ""
  authors: ["Yuri Kuratov", "Aydar Bulatov", "Petr Anokhin", "Ivan Rodkin", "Dmitry Sorokin", "Artyom Sorokin", "Mikhail Burtsev"]
  url: "https://github.com/booydar/babilong"
paper:
  title: "BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack"
  arxiv: "2406.10149"
  url: "https://arxiv.org/abs/2406.10149"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/RMT-team/babilong"
repo_url: "https://github.com/booydar/babilong"
released: "2024-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: "The benchmark was explicitly built with large headroom: the paper's own headline finding is that popular LLMs use only 10-20% of their available context effectively, with accuracy dropping sharply as both length and reasoning complexity increase. No source consulted here gives a recent top score, but the scale of drop-off the authors report at long lengths indicates the benchmark still separates models well there."
contamination:
  risk: medium
  note: "The 20 underlying bAbI tasks have been public since 2015 and are widely known, so a model could plausibly have learned their reasoning templates during pretraining. The specific long-context instances are dynamically generated from PG19 text rather than a single fixed file, which limits but does not eliminate exposure, since reference pre-generated splits are also distributed openly."
harness:
  lm_eval: "babilong"
  inspect_evals: ""
  helm: ""
  opencompass: "babilong"
  bigbench: ""
  other: "lm-evaluation-harness also exposes babilong_longctx, covering QA1-QA5 at lengths up to 128k tokens; OpenCompass carries per-length configs (babilong_0k ... babilong_1m) plus rawprompt variants of each"
tags: ["long-context", "synthetic", "babi", "needle-in-a-haystack", "reasoning"]
sources:
  - url: "https://arxiv.org/abs/2406.10149"
    title: "BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2406.10149"
    title: "BABILong (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/booydar/babilong"
    title: "booydar/babilong repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/RMT-team/babilong"
    title: "RMT-team/babilong dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=RMT-team/babilong"
    title: "RMT-team/babilong dataset splits (datasets-server)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/babilong"
    title: "lm-evaluation-harness babilong task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/babilong"
    title: "OpenCompass babilong dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BABILong tests whether a model can locate and combine facts scattered across an extremely long document, rather than concentrated near the question. It takes the 20 classic bAbI tasks -- synthetic reasoning problems originally designed to isolate single skills such as single-fact retrieval, multi-fact chaining, counting, listing, and simple induction or deduction -- and embeds each task's fact sentences inside long passages of unrelated book text drawn from the PG19 corpus, so the relevant sentences sit surrounded by plausible-looking but irrelevant narrative. A model must find the scattered facts within that noise and answer a question that depends on combining them correctly.

Because the amount of distractor text is controlled independently of the underlying reasoning task, BABILong isolates a model's ability to actually use a long context from its ability to solve the reasoning problem itself -- the same QA1-QA20 tasks are near-trivial at 0k (no distractor) context and become progressively harder purely as a function of length as more distractor text is added.

## How it is scored

Each task is scored by whether the model's generated answer matches the expected answer (a name, a location, a count, a yes/no, or similar short response depending on the task); the headline figure most commonly reported is accuracy averaged over QA1-QA5, the five tasks the authors treat as the core reasoning set, though all 20 can be scored individually. There is no fixed random or human baseline; instead, the paper evaluates each model at a series of fixed context lengths and reports how accuracy degrades as length increases from a model's own 0k (short-context) performance, since headroom is defined relative to a model's own short-context ceiling rather than a universal reference number.

## Dataset and licence

BABILong is a generator rather than one fixed file: it produces test instances by sampling PG19 book text as background and inserting bAbI task sentences and a question at controlled positions. The reference implementation pre-generates fixed evaluation splits at ten lengths described in the paper -- 0k, 4k, 8k, 16k, 32k, 64k, 128k, 512k, 1M and 10M tokens -- for each of the 20 QA tasks; the Hugging Face `RMT-team/babilong` mirror additionally lists 2k and 256k length configurations. The authors state the code and the PG-19 background text are Apache 2.0 licensed, while the underlying bAbI task data carries its original BSD licence; no single combined licence covers the assembled dataset.

## Who publishes it

BABILong was introduced in "BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack" by Yuri Kuratov, Aydar Bulatov, Petr Anokhin, Ivan Rodkin, Dmitry Sorokin, Artyom Sorokin and Mikhail Burtsev, at the NeurIPS 2024 Datasets and Benchmarks Track; author affiliations were not confirmed from a source opened during this research. The authors maintain the implementation at github.com/booydar/babilong, the dataset at huggingface.co/datasets/RMT-team/babilong, and a leaderboard at huggingface.co/spaces/RMT-team/babilong.

## Lineage

BABILong builds directly on Facebook AI Research's original bAbI task suite (Weston et al., 2015), not yet a page here, reusing its 20 reasoning-task templates as the "needles" hidden inside long documents rather than proposing new reasoning tasks. It has no successor or variant id tracked in this repository. Alongside other long-context suites here -- [LongBench](longbench.md), testing moderate lengths of roughly 5,000-15,000 words across real document types, and [RULER](ruler.md), a synthetic suite covering retrieval, tracing and aggregation over similarly extreme lengths -- BABILong isolates multi-hop reasoning over scattered facts as its distinguishing angle, closer in spirit to RULER's synthetic construction than LongBench's realistic-document focus, though built from a different task set than either.

## Saturation and contamination

The benchmark was explicitly built with large headroom: the paper's headline finding is that popular LLMs use only 10-20% of their available context effectively, with accuracy dropping sharply as length and reasoning complexity increase, and testing extends up to 10 million tokens in the standard splits and 50 million in fine-tuned recurrent-memory experiments. No source consulted gives a recent top score, but the scale of drop-off the authors report indicates the benchmark still separates models well at longer lengths. The 20 underlying bAbI tasks have been public since 2015, so a model could plausibly have learned their reasoning templates during pretraining; the long-context instances are dynamically generated from PG19 text rather than fixed, which limits but does not eliminate memorization risk, since reference pre-generated splits are also distributed openly.

## How to run it

lm-evaluation-harness exposes a `babilong` group covering all 20 QA tasks at 0k context, and a separate `babilong_longctx` group covering QA1-QA5 up to 128k tokens; OpenCompass carries per-length configurations (`babilong_0k` through `babilong_1m`) plus "rawprompt" variants of each. Because scores can come from several context lengths, any subset of the 20 tasks, and either formatting, a bare "BABILong score" is not comparable across papers without confirming all three.

## Reading the numbers

A strong BABILong score at a given length means a model can actually find and use information placed anywhere in a context of that size, which is a stronger and more direct test than a model's advertised maximum context window -- a number that says nothing about whether the model can use that much context effectively. Because accuracy on this benchmark typically declines with length for every model tested so far, compare scores only at matched context lengths, and treat a model's claimed context window as an upper bound on capability rather than evidence of it.
