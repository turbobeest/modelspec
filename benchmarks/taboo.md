---
id: taboo
name: "Taboo"
aliases: []
page_kind: benchmark
category: generation
subcategory: "constrained definition generation and comprehension, two-agent self-play word game"
status: unknown
summary: "BIG-bench self-play game: one model instance must define a target word without using forbidden related words, and a second instance must guess it."
measures: >
  Taboo implements the party game of the same name as a two-model self-play task. Given a target
  word and a list of "taboo" words closely related to it (drawn from word embeddings), one model
  instance must produce a definition of the target that avoids using any of the taboo words; a
  second model instance then reads only that definition and must guess the target word. The task
  jointly tests constrained, creative language generation (defining a concept under vocabulary
  restrictions) and language comprehension (inferring a specific concept from an indirect
  description), and can be run at different difficulty levels by varying how many taboo words are
  forbidden.
task_format: "Free-response, two-phase, programmatic self-play: model A generates a definition under a word-avoidance constraint, model B (or the same model) guesses the target from that definition."
metric:
  name: "combined score (definition penalty + guesser reward)"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    task.py scores the first (defining) response by subtracting one point for each forbidden
    ("taboo") word it uses, and scores the second (guessing) response as 1 divided by the guesser's
    response length if the target word appears in it, 0 otherwise. The two phase-scores are combined
    (the task documentation describes summing/averaging them). With a default constraint level of
    k=5 forbidden words (out of a configurable max_k=10), the achievable score range runs from
    -k up to 1.0; no random-guess or human baseline is published.
dataset:
  size: 100
  size_note: >
    taboo_data.json contains 100 examples, each pairing one target word with a list of associated
    taboo (forbidden) words drawn from word embeddings. The task README additionally describes the
    benchmark as "0 multiple choice and 200 free text queries," consistent with each of the 100
    target-word items generating two free-text queries (one prompting the definer, one prompting
    the guesser).
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/taboo"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "single set of 100 target-word items, no train/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors:
    - "Dar Gilboa"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/taboo"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/taboo"
released: "2022"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No dedicated leaderboard or paper table reporting per-model scores on this task was located; as a programmatic self-play task with a tunable difficulty constant (k), its scores also are not necessarily comparable across evaluations run at different k values."
contamination:
  risk: low
  note: >
    The task score depends on live, generated multi-turn interaction between two model instances
    (or roles) rather than on recalling a fixed gold text, so memorizing taboo_data.json's target
    and taboo-word lists would not by itself guarantee a good score; the model must still generate a
    valid constrained definition and correctly infer the target from it at evaluation time.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "taboo"
  other: ""
tags:
  - bigbench
  - self-play
  - constrained-generation
  - word-game
  - programmatic-task
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/taboo"
    title: "BIG-bench: taboo task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/taboo/README.md"
    title: "taboo README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/taboo/task.py"
    title: "taboo task.py implementation"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/taboo/taboo_data.json"
    title: "taboo_data.json"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench"
    title: "BIG-bench repository (archived 2026-04-17)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-007"
---

## What it measures

Taboo is a BIG-bench "programmatic" task that turns the party game Taboo into a two-phase
model-vs-model evaluation. For each of 100 target words, the task supplies a list of closely
related "taboo" words (selected via word embeddings) that a definer must avoid. One model instance
plays the definer: it must describe the target word well enough for a listener to guess it, without
using any of the forbidden taboo words. A second model instance (which never sees the target word)
plays the guesser: it reads only the definition and must name the target concept.

This jointly exercises constrained creative generation — finding a way to communicate a concept
while avoiding the words that would make it easy — and inference under indirection, since the
guesser must recover a specific target from an intentionally roundabout description. Difficulty can
be tuned by changing how many taboo words are forbidden.

## How it is scored

`task.py` scores the definer's response by subtracting one point for every forbidden word it uses
(so violating the constraint directly lowers the score), and scores the guesser's response as
1 divided by the length of its response if the target word appears in it, or 0 if it does not,
rewarding short, confident, correct guesses over long ones. These two phase-scores are combined
into an overall score. The default configuration constrains the definer to avoid `k=5` taboo words
out of a configurable maximum of 10, giving an achievable range from roughly `-k` up to 1.0. No
random-guess or human-performance baseline is published for this task.

## Dataset and licence

`taboo_data.json` contains 100 examples, each an object with a `target` word and its list of
`taboos`. The task README separately describes the benchmark as containing "200 free text queries,"
consistent with each of the 100 items producing two prompts at evaluation time — one for the
definer role and one for the guesser role. All target words and their taboo lists are visible in
the public JSON file, under the BIG-bench repository's Apache-2.0 licence.

## Who publishes it

The task was contributed to BIG-bench by Dar Gilboa. BIG-bench itself is described in "Beyond the
Imitation Game: Quantifying and extrapolating the capabilities of language models"
(arXiv:2206.04615, 2022; later published in Transactions on Machine Learning Research), a
large multi-author collaboration coordinated by Google researchers. The `google/BIG-bench`
repository was archived by its owner on 2026-04-17 and is now read-only, so no further maintenance
or leaderboard updates should be expected from that source.

## Lineage

Taboo is a standalone BIG-bench task with no stated predecessor or successor. It belongs to a small
family of BIG-bench "self-play" or "repeated interaction" tasks (per its own keywords) in which a
model or pair of model instances interacts with itself rather than answering a single static
question, distinguishing it from BIG-bench's more numerous static multiple-choice tasks; no other
task in this repository is currently identified as a direct variant of it.

## Saturation and contamination

No dedicated leaderboard or paper table reporting per-model scores on this task was located, so
saturation status is unknown. Because the task is a tunable, programmatic self-play evaluation
(scores depend on the chosen taboo-word-count parameter `k` and on which two model calls play
definer versus guesser), scores are also not automatically comparable across different evaluation
configurations. Contamination risk is judged low: even if a model has seen `taboo_data.json`
verbatim, doing well still requires generating a fresh, valid constrained definition and making a
correct live inference from it, rather than reproducing a memorized answer.

## How to run it

The canonical implementation is the task directory in the archived `google/BIG-bench` repository
(`bigbench/benchmark_tasks/taboo`), which uses a custom `task.py` (a "programmatic" BIG-bench task
rather than a plain JSON multiple-choice task) to orchestrate the two-phase definer/guesser
interaction and compute the combined score. It was not found among the tasks reimplemented in
EleutherAI's lm-evaluation-harness `bigbench` task set, so reproducing it requires the original
`bigbench` Python package, including its self-play orchestration logic.

## Reading the numbers

A high combined score indicates a model can both generate a useful, constraint-respecting
definition and correctly infer a target concept from another model's indirect description — a
proxy for constrained generation and pragmatic language understanding rather than for stored
factual knowledge. Because the game is self-play, a strong score can also depend on whether the
same model plays both roles or a different model plays the guesser, and on the specific
taboo-word-count setting used, so any reported figure should be read together with those evaluation
details rather than as a single universal number.
