---
id: graphwalks
name: "GraphWalks"
aliases:
  - "Graphwalks"
page_kind: family
category: long-context
subcategory: "multi-hop graph traversal in long context"
status: active
summary: "OpenAI's long-context eval that hides a directed graph of hashed node names in the prompt and asks the model to run a breadth-first search or list a node's parents."
measures: >
  GraphWalks fills a model's context window with a directed graph, written out as an edge list of
  hexadecimal-hash node names, then asks the model to perform one of two operations starting from a
  random node: a breadth-first search (BFS) that returns the nodes reachable at an exact depth, or a
  "parents" query that returns every node with a direct edge into a given target node. OpenAI built it
  specifically because simpler long-context tests -- finding one "needle" fact, or its own OpenAI-MRCR
  benchmark, which disambiguates between several similar requests -- can in principle be solved by one
  read-through of the prompt. GraphWalks cannot: correctly tracing even a shallow BFS requires jumping
  between multiple, scattered positions in the context and combining them, so it specifically tests
  multi-hop reasoning over a long context rather than single-pass retrieval.
task_format: >
  A prompt containing three worked examples, then a large directed graph as an edge list of hex-hash
  node ids, then an instruction to perform a BFS from a node at a given depth or to find a node's
  parents. The model must reply with the resulting node set on the prompt's final line, formatted as
  "Final Answer: [node1, node2, ...]".
metric:
  name: "F1 score (node-set overlap)"
  direction: higher_is_better
  unit: "F1 x100"
  max_score: 100
  baseline_note: >
    F1 is computed from the overlap between the model's returned node set and the ground-truth set:
    recall = overlap / |ground truth|, precision = overlap / |model's set|, F1 = the harmonic mean of
    the two. OpenAI's original scoring scores an empty ground truth against any non-empty prediction as
    an F1 of 1.0 by the standard formula's typical convention (0 when precision+recall is 0); Anthropic's
    Claude Opus 4.6 system card documents changing this specific edge case so that an empty prediction
    against an empty ground truth scores 1.0 instead of 0, which is not the same fix and makes scores
    computed under the two conventions not directly comparable. No fixed random-guess or human baseline
    is established, since both depend on the size of the (randomly generated) graph in a given prompt.
dataset:
  size: 1150
  size_note: >
    About 1,150 rows in the Hugging Face dataset's single "train" split (used purely for evaluation,
    not training), each with a `prompt`, an `answer_nodes` list, a `prompt_chars` length and a
    `problem_type` of either `bfs` or `parents`. The data is split across two parquet files by prompt
    length: `graphwalks_128k_and_shorter.parquet` and `graphwalks_256k_to_1mil.parquet`; the dataset
    card does not break out how many rows of each problem type fall in each file, so an exact per-bucket,
    per-task count is not established here.
  url: "https://huggingface.co/datasets/openai/graphwalks"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "single 'train' split (~1,150 rows), bucketed into two files by prompt length rather than by train/test"
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
  family: ""
  predecessor: ""
  successors: []
  variants:
    - graphwalks_bfs_256k_1m
    - graphwalks_parents_256k_1m
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    OpenAI reported GPT-4.1 at 61.7% aggregate accuracy at the benchmark's April 2025 launch, "matching
    the performance of o1 and beating GPT-4o handily," without a context-length breakdown. At the harder,
    longest context band, Anthropic's Claude Opus 4.6 system card (2026-02) reports a wide spread by
    task: parents queries are close to solved for the best model (Claude Opus 4.6 at 95.1-95.4%, Claude
    Sonnet 4.5 at 81.0%), while BFS queries still leave real headroom (Claude Opus 4.6 at 61.1-61.5%,
    Claude Sonnet 4.5 at 44.9%) -- see the two variant pages for the specific numbers this family page
    is averaging over.
contamination:
  risk: medium
  note: >
    Graphs and node names are synthetically generated, not drawn from an existing public corpus, so the
    classic risk of an old, indexed answer key leaking into training data does not apply the way it does
    for a scraped-text benchmark. But the dataset itself, prompts and correct answers included, has been
    openly downloadable from Hugging Face since April 2025, so a model trained directly on these exact
    published rows could match answers by memorising this fixed set rather than by tracing the graph
    fresh, since GraphWalks reuses the same published examples across evaluation runs rather than
    generating new graphs each time.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness was found to carry GraphWalks. The grading code is published in the
    Hugging Face dataset card's README. Anthropic's Claude Opus 4.6 system card documents three specific
    departures from that reference code when it ran the eval: an edge-case fix to the F1 formula for
    empty ground truth, a prompt clarification that BFS answers must include only nodes at exactly the
    requested depth (the original public prompt was ambiguous about this), and a fix for 24 of 400
    "parents" rows in the shorter, `128k_and_shorter` file whose ground truth wrongly included the
    target node itself due to graph self-loops -- a fix OpenAI's dataset changelog credits to that same
    system card.
tags:
  - long-context
  - graph-traversal
  - multi-hop-reasoning
  - openai
  - synthetic
sources:
  - url: "https://openai.com/index/gpt-4-1/"
    title: "Introducing GPT-4.1 in the API, OpenAI (2025-04-14)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/openai/graphwalks"
    title: "openai/graphwalks dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://www-cdn.anthropic.com/6a5fa276ac68b9aeb0c8b6af5fa36326e0e166dd/Claude%20Opus%204.6%20System%20Card.pdf"
    title: "Claude Opus 4.6 System Card, section 2.18.2 GraphWalks (Anthropic, 2026-02)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GraphWalks fills a model's context window with a directed graph -- nodes named with hexadecimal hashes,
edges listed one per line -- then asks it to perform one of two operations starting from a random node:
a breadth-first search that returns the nodes reachable at an exact depth, or a "parents" query that
returns every node with a direct edge into a given target. OpenAI introduced it alongside OpenAI-MRCR (a
needle-disambiguation benchmark) when launching GPT-4.1, specifically because a model could in principle
solve a needle-retrieval or MRCR-style problem with a single read-through of the prompt. GraphWalks is
built so a single pass is not enough: correctly tracing even a shallow search requires jumping between
scattered positions in the context and combining what is found there, targeting multi-hop reasoning
rather than single-pass retrieval.

## How it is scored

Models are graded on F1 over the returned node set against the ground-truth set: recall is the fraction
of correct nodes returned, precision is the fraction of returned nodes that are correct, and F1 is their
harmonic mean. Answers must appear on the prompt's final line as "Final Answer: [node1, node2, ...]";
responses that do not match this format score as empty. Because the underlying dataset is fixed rather
than regenerated per run, and because vendors have found and fixed genuine scoring bugs after
publication (see Lineage and How to run it), an F1 score's exact value depends on which version of the
grading logic produced it, not solely on the model being tested.

## Dataset and licence

The Hugging Face dataset `openai/graphwalks` holds about 1,150 rows in a single MIT-licensed "train"
split, each row a prompt (three worked examples plus one graph-and-operation problem), its correct
answer node set, the prompt's character length, and whether the problem is a `bfs` or `parents` task.
Rows are split across two parquet files by prompt length -- `graphwalks_128k_and_shorter.parquet` and
`graphwalks_256k_to_1mil.parquet` -- rather than by train and test; the dataset card does not publish a
row count broken down by problem type within each file. There is no separate held-out test split: the
same published rows are the entire evaluation set.

## Who publishes it

OpenAI released GraphWalks on Hugging Face on 11 April 2025 and announced it three days later in the
"Introducing GPT-4.1 in the API" blog post, alongside OpenAI-MRCR, as one of two new long-context evals
it was open-sourcing. No accompanying academic paper was found; the dataset card and blog post are the
primary documentation, and OpenAI continues to maintain the dataset, including a February 2026 bugfix
credited to an external system card (see Lineage).

## Lineage

GraphWalks has no formal predecessor; it was released as a companion to OpenAI-MRCR, a different
long-context benchmark testing disambiguation between similar requests rather than graph traversal. Two
context-length-specific benchmark pages exist in this repository as `graphwalks_bfs_256k_1m` and
`graphwalks_parents_256k_1m`, both `lineage.family: graphwalks`; a shorter-context bucket (128K tokens
or less) and a full-range "1M" cut used in at least one vendor system card are documented in the
underlying dataset but do not yet have their own pages here. The dataset's own changelog credits a
correction to Anthropic's Claude Opus 4.6 system card, an unusual instance of a benchmark's maintainer
fixing a bug a downstream evaluator found.

## Saturation and contamination

At launch, OpenAI reported GPT-4.1 scoring 61.7% aggregate accuracy, "matching the performance of o1 and
beating GPT-4o handily," without breaking the number down by context length. At the harder, longest
context band that this repository's two variant pages track, scores split sharply by task: "parents"
queries are close to solved for the strongest model (Claude Opus 4.6 above 95%) but leave a real gap to
other models (Claude Sonnet 4.5 near 81%), while BFS queries leave substantial headroom across the board
(Claude Opus 4.6 near 61%, Claude Sonnet 4.5 near 45%). Contamination risk is medium: the graphs are
synthetic and not drawn from any pre-existing public corpus, but the fixed set of published prompts and
answers has been downloadable since April 2025, so direct memorisation cannot be ruled out for models
trained after that date.

## How to run it

No major third-party harness carries GraphWalks. The grading code lives in the Hugging Face dataset
card's README. Anthropic has published specific, documented departures from that reference code: a fix
to how the F1 formula handles an empty ground truth, a clarified BFS prompt requiring nodes at exactly
the target depth rather than "reachable" nodes more loosely, and a correction to 24 of 400 mislabeled
"parents" ground-truth rows in the shorter context file. Scores computed before and after these fixes
are not guaranteed to be comparable, and the benchmark's short public history means this kind of
correction may recur.

## Reading the numbers

A high GraphWalks score shows a model can correctly trace a multi-hop path through a graph scattered
across a long context, not merely retrieve one fact from it -- a different skill from
needle-in-a-haystack tests. Because BFS and parents queries behave very differently, and scores depend
on which context-length bucket was tested, do not read one aggregate GraphWalks number as
representative; check the specific task and context length, and prefer this repository's
`graphwalks_bfs_256k_1m` and `graphwalks_parents_256k_1m` pages for numbers tied to a stated context
band. Given the documented scoring-bug history, treat a score reported before 2026 with some caution
relative to one reported after.
