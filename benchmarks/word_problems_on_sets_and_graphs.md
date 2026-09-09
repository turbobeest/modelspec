---
id: word_problems_on_sets_and_graphs
name: Word Problems on Sets and Graphs
aliases: []
page_kind: benchmark
category: reasoning
subcategory: logical reasoning
status: active
summary: A BIG-bench free-response task that checks whether a model tracks set membership and graph paths across three small synthetic puzzle types.
measures: BIG-bench's word_problems_on_sets_and_graphs task tests whether a model can track set membership, graph reachability, and set operations across three synthetic word-problem styles, without relying on surface word co-occurrence.
task_format: "Free-text generation. The model reads a short narrative (e.g. fruits added to and removed from a basket) and must produce the final answer as free text; responses are keyword-checked rather than graded on exact wording or grammar."
metric: {name: keyword-match score, direction: higher_is_better, unit: points, max_score: 1, random_baseline: null, human_baseline: null, baseline_note: "Scoring adds 1 point per correctly mentioned item and subtracts 1 point per incorrectly mentioned item, normalised so perfect performance equals 1.0; a GPT-2 baseline is reported in the task README at well below 1.0 on all three sub-tasks."}
dataset: {size: 3000, size_note: "3,000 free-text queries across three sub-tasks: Fruit Basket (set membership after additions/removals, up to 11 fruit types), Acquaintances (shortest path through a social graph), and Student Classes (set union/intersection/difference, up to 14 students and 12 classes).", url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/word_problems_on_sets_and_graphs, license: Apache-2.0, languages: [en], modalities: [text], splits: "", public_test_set: null}
publisher: {org: "", authors: [Benjamin Inden], url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/word_problems_on_sets_and_graphs}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/word_problems_on_sets_and_graphs
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "Task items appear to be programmatically generated from templates, so contamination risk depends on whether a model's training data included the BIG-bench repository itself rather than any external corpus."}
harness: {bigbench: word_problems_on_sets_and_graphs, lm_eval: "", inspect_evals: "", helm: "", opencompass: "", other: ""}
tags: [benchmark, logical-reasoning, synthetic]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/word_problems_on_sets_and_graphs/README.md
    title: word_problems_on_sets_and_graphs task README (BIG-bench)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-001 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-001"}
---
## What it measures

This BIG-bench task, authored by Benjamin Inden, packages three related synthetic word-problem styles that test whether a language model tracks the state of a small world rather than pattern-matching on word co-occurrence. Fruit Basket tracks which fruits remain in a basket after a sequence of additions and removals (up to 11 fruit types). Acquaintances asks the model to find a path through a small social-acquaintance graph. Student Classes asks the model to compute set operations — union, intersection, difference — over class rosters (up to 14 students, up to 12 classes).

## How it is scored

Responses are free text, not multiple choice, and are graded by keyword matching rather than exact string or grammatical correctness: for Fruit Basket, the score adds one point for each correct fruit named and subtracts one point for each incorrect fruit named, normalised so a perfect answer scores 1.0. The task README reports a GPT-2 baseline (50 trials) scoring 0.0293 on Fruit Basket, -0.1799 on Acquaintances, and 0.0 on Student Classes, all far below the 1.0 ceiling.

## Dataset and licence

The task contains 3,000 free-text queries in total across the three sub-tasks, all zero multiple-choice. Items are programmatically generated within the stated limits (up to 11 fruit types, 14 students, 12 classes). The task is distributed inside the BIG-bench repository, which is released under the Apache-2.0 licence; the task README does not state a separate licence.

## Who publishes it

The task was contributed to Google's BIG-bench collection by Benjamin Inden. BIG-bench itself is a large, community-contributed benchmark suite; no separate author organisation or standalone leaderboard for this specific task was found.

## Lineage

This is a standalone BIG-bench task with no stated predecessor or successor. It belongs to BIG-bench's broader collection of logical- and world-modelling tasks, but the source read for this page did not identify sibling tasks that share its exact combinatorial-reasoning format.

## Saturation and contamination

No saturation data for current models was found; the only reported baseline in the source is GPT-2, which scores far below ceiling on all three sub-tasks. Because items are template-generated, training-data exposure would most plausibly come from the BIG-bench GitHub repository itself rather than from an external corpus, but no study of this was found.

## How to run it

Run the `word_problems_on_sets_and_graphs` task in Google's BIG-bench harness. Because scoring is keyword-based rather than exact-match, harness implementations that post-process model output differently (e.g. stripping punctuation or requiring an exact list format) can change scores; check the scoring function against the version used for any reported number.

## Reading the numbers

A high score shows a model can maintain and query a small explicit world state (a set of items, a graph, or class rosters) purely from a natural-language narrative, without needing structured input. Because scoring is keyword-based, a model can score well by naming the right items in free text even with imperfect grammar, and can lose points for including plausible-sounding but wrong items. The task's small, bounded combinatorics (at most 14 students or 11 fruit types) mean it is not a stress test of scale, only of whether the model tracks state correctly at all; compare it alongside other logical-reasoning tasks before drawing conclusions about general reasoning ability.
