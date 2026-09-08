---
id: graphwalks_bfs_256k_1m
name: "GraphWalks BFS (256K-1M context)"
aliases:
  - "GraphWalks BFS, 256K subset of 1M"
page_kind: benchmark
category: long-context
subcategory: "multi-hop graph traversal, breadth-first search, long context"
status: active
summary: "GraphWalks' breadth-first-search task, scored only on prompts from the dataset's longest file, spanning roughly 256K to 1M tokens of context."
measures: >
  This id covers GraphWalks' breadth-first-search (BFS) operation, scored specifically on prompts
  drawn from the openai/graphwalks dataset's longest file, `graphwalks_256k_to_1mil.parquet`, whose
  prompts range from about 256,000 up to roughly 1 million characters of context. Given a directed
  graph written as an edge list of hex-hash node names, a starting node and a target depth, the model
  must return exactly the set of nodes reachable at that depth -- not nodes at intermediate depths, and
  not the starting node itself. Because the graph is scattered across a prompt near the top of what
  even long-context models support, this variant specifically tests whether multi-hop traversal still
  works correctly at the harder end of a model's supported context length, not just at short range.
task_format: >
  A prompt with three worked examples followed by a large directed graph and a "perform a BFS from
  node X with depth N" instruction, drawn only from the dataset's 256K-to-1M-token file. The model
  replies with "Final Answer: [node1, node2, ...]" on the prompt's last line.
metric:
  name: "F1 score (node-set overlap)"
  direction: higher_is_better
  unit: "F1 x100"
  max_score: 100
  baseline_note: >
    F1 is the harmonic mean of precision and recall over the model's returned node set versus the
    ground-truth set. Anthropic's Claude Opus 4.6 system card documents a scoring fix specific to this
    metric (an empty prediction against an empty ground truth now scores 1.0, rather than 0 under the
    original formula's typical convention), so scores computed before and after that fix are not
    directly comparable. No random-guess or human baseline is established; guessing performance would
    depend on the size of each prompt's specific graph, which is not fixed.
dataset:
  size: null
  size_note: >
    Drawn from the `graphwalks_256k_to_1mil.parquet` file of the openai/graphwalks Hugging Face
    dataset (about 297MB, versus about 22MB for the shorter `128k_and_shorter` file), filtered to
    `problem_type == "bfs"`. The dataset card gives a total of about 1,150 rows across both files and
    both problem types combined, but does not publish a row count broken out by file and task, so an
    exact BFS-only row count for this specific bucket is not established here.
  url: "https://huggingface.co/datasets/openai/graphwalks"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "single 'train' split, filtered to the 256K-1M-token file and the bfs problem type"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: []
  url: "https://huggingface.co/datasets/openai/graphwalks"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/openai/graphwalks"
released: "2025-04"
last_updated: "2026-03"
lineage:
  family: graphwalks
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 61.5
  as_of: "2026-02"
  note: >
    Anthropic's Claude Opus 4.6 system card reports Claude Opus 4.6 at 61.5% (a lower "thinking budget"
    setting the card labels "64k") and 61.1% ("max effort"), versus Claude Sonnet 4.5 at 44.9% under the
    same evaluation, both on this 256K-to-1M-token bucket. A roughly 17-point gap between two models
    from the same vendor, and a top score well under half the maximum, indicate this task still
    separates models clearly rather than sitting near a ceiling.
contamination:
  risk: medium
  note: >
    The graph in each prompt is synthetically generated, so there is no pre-existing public answer key
    to leak from an older corpus. But the specific published rows in `graphwalks_256k_to_1mil.parquet`,
    prompts and correct node sets included, have been downloadable from Hugging Face since the
    dataset's 2025-04 release, so a model trained directly on this file could match answers on these
    exact prompts by memorisation rather than by genuinely tracing the graph.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness carries this benchmark. The grading code lives in the Hugging Face
    dataset card's README. Anthropic's Claude Opus 4.6 system card documents running this bucket under
    two different "thinking budget" settings (labelled "64k" and "max") and getting a slightly higher
    score under the smaller of the two (61.5% versus 61.1%), a reminder that inference-time settings,
    not just the model, move this number.
tags:
  - long-context
  - graph-traversal
  - breadth-first-search
  - 1m-context
  - openai
sources:
  - url: "https://openai.com/index/gpt-4-1/"
    title: "Introducing GPT-4.1 in the API, OpenAI (2025-04-14)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/openai/graphwalks"
    title: "openai/graphwalks dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://www-cdn.anthropic.com/6a5fa276ac68b9aeb0c8b6af5fa36326e0e166dd/Claude%20Opus%204.6%20System%20Card.pdf"
    title: "Claude Opus 4.6 System Card, section 2.18.2 GraphWalks, Table 2.18.A (Anthropic, 2026-02)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This id is GraphWalks' breadth-first-search (BFS) operation, scored only on the dataset's longest
prompts. The underlying openai/graphwalks dataset splits its roughly 1,150 rows across two files by
prompt length; this benchmark draws exclusively from the harder, longer file,
`graphwalks_256k_to_1mil.parquet`, whose prompts run from about 256,000 up to roughly 1 million
characters. Given a directed graph as an edge list of hex-hash node names, a starting node and a target
depth, the model must return exactly the nodes reachable at that depth -- excluding both the starting
node and any node at an intermediate depth. Because the graph is scattered across a prompt near the top
of what even long-context models support, a correct answer requires the model to actually trace edges
across the full span of the context rather than rely on the graph clustering near the start or end,
which shorter needle-style tests can miss.

## How it is scored

Grading compares the model's returned node set to the ground truth using F1: recall is the share of
correct nodes returned, precision is the share of returned nodes that are correct, and F1 is their
harmonic mean. The model must format its answer as "Final Answer: [node1, node2, ...]" on the response's
last line; anything else is scored as an empty answer. Anthropic's Claude Opus 4.6 system card documents
running this specific bucket under two different internal "thinking budget" settings and reports both
(61.5% at a smaller budget the card calls "64k," 61.1% at "max effort" for the same model), so a single
model's score is not fixed even holding the benchmark constant -- inference-time settings move it too.

## Dataset and licence

Rows come from `graphwalks_256k_to_1mil.parquet` in the MIT-licensed `openai/graphwalks` Hugging Face
dataset, filtered to `problem_type == "bfs"`. That file is about 297MB, next to about 22MB for the
dataset's shorter, `128k_and_shorter` companion file. The dataset card publishes a combined total of
about 1,150 rows across both files and both problem types (`bfs` and `parents`) but does not break that
figure down by file and task, so this page cannot state an exact row count specific to this bucket.
There is no separate held-out test split; the same published rows are the entire evaluation set.

## Who publishes it

OpenAI released the openai/graphwalks dataset on Hugging Face on 11 April 2025, announcing it three days
later in the "Introducing GPT-4.1 in the API" blog post as a new long-context, multi-hop reasoning eval.
The blog post's own headline number (GPT-4.1 at 61.7% aggregate accuracy) was not broken down by context
length; the specific 256K-to-1M-token bucket this page covers is documented instead in later vendor
system cards, including Anthropic's Claude Opus 4.6 system card (2026-02), which is this page's primary
source for bucket-specific scores.

## Lineage

This page is a `graphwalks`-family benchmark, filtered to the BFS task and the dataset's longest,
256K-to-1M-token file. A sibling page, `graphwalks_parents_256k_1m`, covers the same context-length
bucket for the "parents" operation instead of BFS; the two tasks score very differently at this context
length (parents is close to solved for the strongest model, BFS is not), so they should be read as
separate benchmarks rather than interchangeable. A shorter-context bucket (128K tokens and under) and a
full-range cut some system cards label "1M" exist in the underlying dataset and at least one vendor's
reporting, but neither has its own page in this repository yet.

## Saturation and contamination

Anthropic's Claude Opus 4.6 system card reports Claude Opus 4.6 at 61.5% (61.1% under a "max effort"
setting) against Claude Sonnet 4.5 at 44.9% on this bucket -- a roughly 17-point gap between two models
from the same lab, and a top score well under half the maximum, both signs this task still separates
models clearly rather than approaching a ceiling. Contamination risk is medium: the graphs themselves
are synthetically generated with no pre-existing public answer key, but the specific published rows in
this file have been downloadable since April 2025, so a model trained directly on them could match
answers by memorising this fixed set rather than genuinely tracing the graph.

## How to run it

No major third-party harness carries this benchmark. The reference grading code is published in the
Hugging Face dataset card's README. Reported scores can differ by the vendor's own inference-time
settings even for the same model -- Anthropic's own two settings for Claude Opus 4.6 differ by 0.4
points on this bucket -- and by whether a reporter has adopted the scoring fixes documented in
Anthropic's system card (see the graphwalks family page). Treat scores from different sources, or from
before versus after early 2026, as not strictly comparable.

## Reading the numbers

A high score here shows a model can correctly trace a breadth-first search through a graph spread across
a prompt near the top of its supported context length, not just retrieve one fact from it. Because this
id isolates the hardest, longest-context bucket and the BFS task specifically, expect scores well below
what the same model gets on the easier "parents" task at the same context length, and below what
shorter-context GraphWalks buckets would show for the same model. Check the specific reporter's
inference-time settings (thinking budget, sampling) before comparing two scores, since those move the
number by several points even without changing the model.
