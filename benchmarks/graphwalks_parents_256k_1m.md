---
id: graphwalks_parents_256k_1m
name: "GraphWalks Parents (256K-1M context)"
aliases:
  - "GraphWalks Parents, 256K subset of 1M"
page_kind: benchmark
category: long-context
subcategory: "multi-hop graph traversal, parent lookup, long context"
status: active
summary: "GraphWalks' parent-finding task, scored only on prompts from the dataset's longest file, spanning roughly 256K to 1M tokens of context."
measures: >
  This id covers GraphWalks' "parents" operation, scored specifically on prompts drawn from the
  openai/graphwalks dataset's longest file, `graphwalks_256k_to_1mil.parquet`, whose prompts range
  from about 256,000 up to roughly 1 million characters. Given a directed graph written as an edge
  list of hex-hash node names and a target node, the model must return exactly the set of nodes with
  an edge leading directly into that target -- its direct predecessors -- excluding the target node
  itself. Unlike the family's BFS task, which must trace outward across multiple hops, a parents query
  needs only a single hop, so it isolates whether a model can find and extract the right edges from a
  long context even when it does not have to chain several lookups together.
task_format: >
  A prompt with three worked examples followed by a large directed graph and a "find the parents of
  node X" instruction, drawn only from the dataset's 256K-to-1M-token file. The model replies with
  "Final Answer: [node1, node2, ...]" on the prompt's last line.
metric:
  name: "F1 score (node-set overlap)"
  direction: higher_is_better
  unit: "F1 x100"
  max_score: 100
  baseline_note: >
    F1 is the harmonic mean of precision and recall over the model's returned node set versus the
    ground-truth set. Anthropic's Claude Opus 4.6 system card documents that a distinct data-quality
    bug affecting "parents" ground truth -- the target node's own self-loops sometimes left it wrongly
    included as its own parent -- was found and fixed in the dataset's shorter, 128K-and-under file, but
    the card states the long-context rows scored here "did not include such self-loops," so this
    specific bucket's ground truth was not affected by that particular bug. No random-guess or human
    baseline is established; guessing performance would depend on each prompt's specific graph, which is
    not fixed.
dataset:
  size: null
  size_note: >
    Drawn from the `graphwalks_256k_to_1mil.parquet` file of the openai/graphwalks Hugging Face
    dataset (about 297MB, versus about 22MB for the shorter `128k_and_shorter` file), filtered to
    `problem_type == "parents"`. The dataset card gives a combined total of about 1,150 rows across
    both files and both problem types, but does not publish a row count broken out by file and task,
    so an exact parents-only row count for this specific bucket is not established here.
  url: "https://huggingface.co/datasets/openai/graphwalks"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "single 'train' split, filtered to the 256K-1M-token file and the parents problem type"
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
  status: watch
  top_score: 95.4
  as_of: "2026-02"
  note: >
    Anthropic's Claude Opus 4.6 system card reports Claude Opus 4.6 at 95.1% ("64k" thinking budget) and
    95.4% ("max effort"), against Claude Sonnet 4.5 at 81.0% on the same bucket. The top score is close
    to the ceiling, which is why this page marks the task "watch" rather than "open," but a roughly
    14-point gap to the next model shown means the task has not fully stopped separating models the way
    a genuinely saturated benchmark would.
contamination:
  risk: medium
  note: >
    The graph in each prompt is synthetically generated, so there is no pre-existing public answer key
    to leak from an older corpus. The specific published rows in `graphwalks_256k_to_1mil.parquet`,
    prompts and correct node sets included, have been downloadable since the dataset's 2025-04 release,
    so a model trained directly on this file could match answers here by memorisation. This bucket was
    also confirmed, in Anthropic's system card, not to carry the self-loop ground-truth bug that
    affected some of the dataset's shorter-context "parents" rows, so its answer key is not known to
    need correction the way that file's was.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness carries this benchmark. The grading code lives in the Hugging Face
    dataset card's README. Anthropic's Claude Opus 4.6 system card documents running this bucket under
    two internal "thinking budget" settings and reports both (95.1% at a smaller budget the card calls
    "64k," 95.4% at "max effort" for the same model), a reminder that inference-time settings move this
    number even for one model.
tags:
  - long-context
  - graph-traversal
  - parent-lookup
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

This id is GraphWalks' "parents" operation, scored only on the dataset's longest prompts. The underlying
openai/graphwalks dataset splits its roughly 1,150 rows across two files by prompt length; this
benchmark draws exclusively from the harder, longer file, `graphwalks_256k_to_1mil.parquet`, whose
prompts run from about 256,000 up to roughly 1 million characters. Given a directed graph as an edge
list of hex-hash node names and one target node, the model must return exactly the nodes with a direct
edge into that target -- its direct predecessors -- excluding the target itself. Unlike the family's BFS
task, which chains several hops together, a parents query needs only one hop, so it isolates whether a
model can locate the right edges without also reasoning across multiple steps.

## How it is scored

Grading compares the model's returned node set to the ground truth using F1: recall is the share of
correct nodes returned, precision is the share of returned nodes that are correct, and F1 is their
harmonic mean. The model must format its answer as "Final Answer: [node1, node2, ...]" on the response's
last line; anything else scores as empty. A distinct, now-documented data-quality issue affected some
"parents" rows in the dataset's shorter, 128K-and-under file (self-loops occasionally left the target
node wrongly listed as its own parent); Anthropic's system card states the long-context rows scored
under this id did not have that problem.

## Dataset and licence

Rows come from `graphwalks_256k_to_1mil.parquet` in the MIT-licensed `openai/graphwalks` Hugging Face
dataset, filtered to `problem_type == "parents"`. That file is about 297MB, next to about 22MB for the
dataset's shorter, `128k_and_shorter` companion file. The dataset card publishes a combined total of
about 1,150 rows across both files and both problem types (`bfs` and `parents`) but does not break that
figure down by file and task, so this page cannot state an exact row count specific to this bucket.
There is no separate held-out test split; the same published rows are the entire evaluation set.

## Who publishes it

OpenAI released the openai/graphwalks dataset on Hugging Face on 11 April 2025, announcing it three days
later in the "Introducing GPT-4.1 in the API" blog post as a new long-context, multi-hop reasoning eval.
That post's headline number was an aggregate BFS score, not broken out by task or context length; the
parents task at this specific context bucket is documented instead in later vendor system cards,
including Anthropic's Claude Opus 4.6 system card (2026-02), this page's primary source for
bucket-specific scores and the self-loop ground-truth bugfix noted above.

## Lineage

This page is a `graphwalks`-family benchmark, filtered to the "parents" task and the dataset's longest,
256K-to-1M-token file. A sibling page, `graphwalks_bfs_256k_1m`, covers the same context-length bucket
for the BFS task instead; the two score very differently here (parents close to solved for the
strongest model, BFS well short of it), so read them as separate benchmarks, not interchangeable. A
shorter-context bucket (128K tokens and under, the file with the documented self-loop bug) and a
full-range cut some system cards label "1M" exist in the underlying dataset but neither has its own
page in this repository yet.

## Saturation and contamination

Anthropic's Claude Opus 4.6 system card reports Claude Opus 4.6 at 95.1% ("64k" setting) to 95.4% ("max
effort"), against Claude Sonnet 4.5 at 81.0% on the same bucket. The top score is close to the ceiling,
which is why this page is marked "watch" rather than "open," though the roughly 14-point gap to the next
model shown means the task has not fully stopped separating models. Contamination risk is medium: the
graphs are synthetically generated with no pre-existing public answer key, but the specific published
rows in this file have been downloadable since April 2025, so a model trained directly on them could
match answers by memorisation rather than genuine lookup; separately, this exact bucket was confirmed by
Anthropic not to carry the self-loop ground-truth bug found in the dataset's shorter-context file.

## How to run it

No major third-party harness carries this benchmark. The reference grading code is published in the
Hugging Face dataset card's README. Reported scores can differ by the vendor's own inference-time
settings even for the same model -- Anthropic's own two settings for Claude Opus 4.6 differ by 0.3
points on this bucket -- and by whether a reporter's copy of the dataset predates the documented
self-loop fix in the shorter-context file (which does not affect this bucket directly, but signals the
dataset has been revised since its 2025-04 release). Treat scores from clearly different dates or
harnesses as not strictly comparable.

## Reading the numbers

A high score here shows a model can locate the right incoming edges for a target node from a prompt near
the top of its supported context length -- a single-hop lookup, not a multi-step trace. Because this
task is easier than the family's BFS task at the same context length, expect noticeably higher scores
here than on `graphwalks_bfs_256k_1m` for the same model; a large gap between a model's parents and BFS
scores says more about multi-hop reasoning specifically than about long-context retrieval in general.
Check the reporter's inference-time settings before comparing two scores, since those alone move this
number by several tenths of a point.
