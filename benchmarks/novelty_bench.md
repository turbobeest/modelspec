---
id: novelty_bench
name: NoveltyBench
aliases:
  - "novelty-bench"
  - "NoveltyBench: Evaluating Language Models for Humanlike Diversity"
page_kind: benchmark
category: generation
subcategory: "output diversity across repeated generations (mode collapse)"
status: active
summary: Tests whether a model can produce several genuinely different, still-good answers to the same prompt across repeated samples, rather than near-duplicate outputs; current models fall well short of human writers.
measures: >
  NoveltyBench targets mode collapse: the tendency of a language model to give the same or barely-
  reworded answer every time it is sampled on a prompt that legitimately has many good answers
  (write a riddle, name a capital city in Africa, pick a favourite car). It generates k independent
  completions (10 by default) per prompt across 1,100 prompts designed or filtered to admit
  multiple valid, meaningfully different responses -- spanning randomness, underspecified factual
  recall, creative writing, and subjective opinion -- and asks whether the k outputs are actually
  distinct, useful alternatives rather than trivial rewordings of one underlying answer.
task_format: >
  For each prompt, a model produces k independent samples. A fine-tuned classifier groups the k
  outputs into equivalence classes based on whether a user who saw one would gain anything from
  seeing another; a separate reward model scores each output's quality. Two metrics are reported per
  prompt and averaged across the dataset: distinct_k, the count of equivalence classes among the k
  samples, and utility_k, a patience-weighted cumulative score that credits only the first
  (highest-quality, earliest-generated) output in each class, discounted by a patience factor for
  later, still-novel classes.
metric:
  name: "distinct_k (count of functionally distinct outputs among k generations) and utility_k (patience-weighted cumulative utility of novel outputs)"
  direction: higher_is_better
  unit: "count (distinct_k, out of k); utility points (utility_k, reward-model scale 1-10)"
  max_score: 10.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Two related but distinct metrics share this page's single metric block: distinct_k counts how
    many of the k (default 10) generations fall into different functional-equivalence classes, so it
    is naturally capped at k; utility_k sums each novel class's quality score (mapped to a 1-10 scale
    via reward-model calibration against MT-Bench), discounted by a patience factor p=0.8 for each
    successive novel class, and the reference implementation's own documentation states this is
    "maximum 10" under its default settings. The paper's headline finding is that current models
    show markedly less output diversity than human writers (each NBCURATED prompt has 8 independent
    human-written reference answers for comparison), and that within a model family, a larger model
    is often less diverse than a smaller one -- diversity does not track capability. Scores also
    depend on which reward model grades quality: inspect_evals' own comparison of its
    reimplementation against the paper, using GPT-4o-mini, found distinct_k close (2.62 vs. the
    paper's 2.65) but utility_k diverging more (3.55 vs. 3.11), attributed to a different default
    quality-scoring model.
dataset:
  size: 1100
  size_note: >
    1,100 prompts total: 100 in NBCURATED, hand-written across four categories (randomness,
    e.g. "roll a make-believe 20-sided die"; underspecified factual knowledge with multiple valid
    answers, e.g. "list a capital city in Africa"; creative writing, e.g. riddles and short stories;
    and subjective opinion, e.g. "what's the best car to get in 2023") with 8 independent human-
    annotator reference responses per prompt; and 1,000 in NBWILDCHAT, drawn from the 1-million-
    conversation WildChat corpus of real ChatGPT interactions and filtered down using Llama Guard 3
    (removing inappropriate content), IP-based deduplication (for topic diversity), and GPT-4o
    classification (selecting prompts likely to elicit genuinely diverse responses).
  url: https://huggingface.co/datasets/yimingzhang/novelty-bench
  license: MIT (code repository); the Hugging Face dataset card itself carries no separate data licence tag
  languages:
    - en
  modalities:
    - text
  splits: "curated (100 prompts) and wildchat (1,000 prompts), both used in full as evaluation sets; no train split"
  public_test_set: true
publisher:
  org: Carnegie Mellon University
  authors:
    - Yiming Zhang
    - Harshita Diddee
    - Susan Holm
    - Hanchen Liu
    - Xinyue Liu
    - Vinay Samuel
    - Barry Wang
    - Daphne Ippolito
  url: https://novelty-bench.github.io/
paper:
  title: "NoveltyBench: Evaluating Language Models for Humanlike Diversity"
  arxiv: "2504.05228"
  url: https://arxiv.org/abs/2504.05228
  year: 2025
leaderboard_url: https://novelty-bench.github.io/
repo_url: https://github.com/novelty-bench/novelty-bench
released: "2025-04"
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
  note: >
    Not established as a single ranked figure: the paper's headline result is qualitative rather
    than a leaderboard-style top score -- current state-of-the-art models are significantly less
    diverse than human writers, and larger models within a family are often less diverse than their
    smaller counterparts. inspect_evals' own README reports only two illustrative model runs
    (gpt-5-nano and gpt-5.2) rather than a maintained ranked leaderboard, so this page does not
    assert a current top_score.
contamination:
  risk: medium
  note: >
    NBWILDCHAT is drawn from WildChat, a public corpus of real ChatGPT conversations that could
    itself overlap with later training data, and several NBCURATED prompts are generic enough (for
    example, common riddles) that a specific answer could be memorised. However, because scoring
    depends on generating multiple genuinely different good answers under repeated sampling rather
    than matching one gold answer, ordinary answer-leakage contamination is a smaller threat here
    than to accuracy-style benchmarks -- the phenomenon under test, mode collapse from training, is
    to some extent the same mechanism contamination concerns usually describe.
harness:
  lm_eval: ""
  inspect_evals: "novelty_bench (packaged with its own isolated environment under packages/novelty_bench/ due to conflicting dependencies)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - generation
  - diversity
  - creativity
  - mode-collapse
  - sampling
sources:
  - url: https://arxiv.org/abs/2504.05228
    title: "NoveltyBench: Evaluating Language Models for Humanlike Diversity (Zhang et al., arXiv:2504.05228)"
    accessed: "2026-09-08"
  - url: https://github.com/novelty-bench/novelty-bench
    title: "novelty-bench/novelty-bench GitHub repository (README, MIT licence)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/yimingzhang/novelty-bench
    title: "yimingzhang/novelty-bench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/novelty_bench
    title: "inspect_evals novelty_bench task README (parameters, scoring method, evaluation comparison)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

NoveltyBench tests a specific failure mode most accuracy-oriented benchmarks cannot see: mode
collapse, where a model gives essentially the same answer every time it is sampled on a prompt that
legitimately admits many good, different answers. It draws on 1,100 prompts split into NBCURATED
(100 hand-written prompts across randomness, underspecified factual recall, creative writing and
subjective opinion, each with 8 independent human reference answers) and NBWILDCHAT (1,000 prompts
automatically filtered from the WildChat corpus of real ChatGPT conversations for diversity
potential). For each prompt, a model generates several independent samples, and the benchmark asks
whether those samples are meaningfully different from each other -- not merely differently worded --
and whether each one is still a good answer.

The paper's central finding is that current frontier models fall well short of human writers on this
measure, and that scaling up a model within a family often reduces rather than increases its output
diversity, challenging the assumption that stronger models on standard benchmarks are also more
useful for tasks that reward varied output.

## How it is scored

Two metrics are computed per prompt from k independent generations (10 by default): distinct_k
counts how many of the k outputs fall into different functional-equivalence classes, where two
outputs are considered equivalent only if a user who saw one would gain nothing from also seeing the
other; utility_k sums the quality score of the first (best, earliest) output in each novel class,
discounted by a patience factor (p=0.8 by default) for each additional distinct class found, so a
model that front-loads its best, most different answers scores higher than one that needs many
samples to diversify. Equivalence is judged by a fine-tuned DeBERTa-v3-large classifier (trained on
1,000 human-annotated pairs of same-prompt outputs), and quality is scored by a reward model --
Skywork-Reward-Gemma-2-27B-v0.2 in the original paper, or a smaller Skywork-Reward-V2-Qwen3-1.7B in
the faster default configuration inspect_evals ships -- with reward mapped to a 1-10 utility scale
via MT-Bench calibration. Because the reward model choice measurably shifts utility_k (inspect_evals'
own comparison found a meaningful gap between its and the paper's utility_k for the same model, while
distinct_k stayed close), the two metrics are not equally robust to reimplementation.

## Dataset and licence

NBCURATED contributes 100 prompts across four categories designed to admit multiple valid answers,
each paired with 8 independent human-written reference responses (the paper notes this likely
understates true human diversity, given a homogeneous annotator pool). NBWILDCHAT contributes 1,000
prompts drawn from the 1-million-conversation WildChat corpus, filtered through Llama Guard 3 for
safety, IP-based deduplication for topical spread, and a GPT-4o classifier selecting prompts likely
to elicit genuinely different responses. The reference code repository, `novelty-bench/novelty-bench`,
is released under the MIT licence; the Hugging Face dataset card for the prompt data itself carries
no separate licence tag, which this page reports rather than assumes.

## Who publishes it

NoveltyBench was published in April 2025 by Yiming Zhang, Harshita Diddee, Susan Holm, Hanchen Liu,
Xinyue Liu, Vinay Samuel, Barry Wang and Daphne Ippolito at Carnegie Mellon University. The authors
maintain the reference implementation and a project site with evaluation results and submission
instructions for new models at `novelty-bench.github.io`.

## Lineage

NoveltyBench has no predecessor or successor tracked in this repository. UK AISI's inspect_evals
project maintains an independent reimplementation with its own isolated dependency environment
(needed because the classifier and reward-model dependencies conflict with other evals in that
repository) and a configurable choice of quality-scoring reward model, which is a meaningful
implementation variant rather than a distinct benchmark: it can produce different utility_k numbers
from the original paper for the same model, as noted above.

## Saturation and contamination

Saturation is better read qualitatively than numerically here: the paper's own conclusion is that
current state-of-the-art models produce significantly less diversity than human writers, and that
larger models in a family are often less diverse than smaller siblings -- a pattern inconsistent with
approaching a ceiling. No maintained, ranked leaderboard was found (inspect_evals reports only two
illustrative model runs), so this page does not assert a current top score.

Contamination risk is medium. NBWILDCHAT prompts come from a public real-conversation corpus that
could itself surface in later pretraining data, and a handful of NBCURATED prompts are generic enough
that a specific "correct" answer could be memorised. This matters less than for accuracy benchmarks,
though, because NoveltyBench does not reward matching one gold answer -- it rewards producing several
different good answers under repeated sampling, and mode collapse (the phenomenon under test) is
itself a training-time effect related to, but not identical with, benchmark-specific memorisation.

## How to run it

The authors' own repository provides a four-stage pipeline (inference, partition, score, summarise)
run via `src/inference.py`, `src/partition.py` and `src/score.py`, with a default patience value of
0.8. inspect_evals packages an independent implementation as the `novelty_bench` task, configurable
via `dataset_split` (curated or wildchat), `num_generations` (default 10), `equivalence_threshold`
(default 0.102), and a choice between a small or large quality-scoring reward model; because it ships
its own isolated Python environment (`packages/novelty_bench/`) due to dependency conflicts, it must
be installed separately from the rest of that repository. One implementation detail worth checking
when comparing scores: the equivalence classifier truncates each response to its first 128 tokens
before comparison, matching its fine-tuning setup, so long responses that diverge only after that
point are scored as if identical.

## Reading the numbers

A high distinct_k means a model actually varies its answer across repeated samples rather than
returning near-duplicates -- useful for applications like brainstorming, creative writing, or
"regenerate" buttons where a user wants a genuinely different option, not just different wording. A
high utility_k means those distinct answers are also good, front-loaded, and arrive without wasting
many samples on redundant output. Neither metric says anything about a model's raw capability or
correctness on tasks with one right answer, and because the reward model used to grade quality
measurably shifts utility_k between implementations, compare utility_k scores only when you know they
came from the same scoring configuration; distinct_k is more directly comparable across
implementations.
