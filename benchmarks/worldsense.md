---
id: worldsense
name: WorldSense
aliases: []
page_kind: benchmark
category: reasoning
subcategory: reasoning
status: active
summary: WorldSense is a synthetic benchmark that tests whether a model can maintain a consistent world model while controlling for dataset bias.
measures: WorldSense tests whether a model can maintain a consistent internal world model from a set of statements, across three problem types and two difficulty grades, while controlling for the response-position and label biases that let models shortcut similar tasks.
task_format: "Text input describing a small scenario (e.g. object placements or a scheduling puzzle) with three problem types: Infer (judge a statement true or false), Compl (pick the correct statement among three options), and Consist (judge whether a set of statements is possible or impossible)."
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The harness also reports standard error and a weighted accuracy that adjusts for tuple ID, problem name and problem size, to control for known response biases."}
dataset: {size: null, size_note: "Exact dataset size was not stated in the README or paper abstract read for this page.", url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/worldsense, license: "", languages: [en], modalities: [text], splits: "", public_test_set: null}
publisher: {org: "", authors: [Youssef Benchekroun, Megi Dervishi, Mark Ibrahim, Jean-Baptiste Gaya, Xavier Martinet, Grégoire Mialon, Thomas Scialom, Emmanuel Dupoux, Dieuwke Hupkes, Pascal Vincent], url: https://arxiv.org/abs/2311.15930}
paper: {title: "WorldSense: A Synthetic Benchmark for Grounded Reasoning in Large Language Models", arxiv: "2311.15930", url: https://arxiv.org/abs/2311.15930, year: 2023}
leaderboard_url: ""
repo_url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/worldsense
released: "2023-11"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "Items are synthetically generated, which limits exposure to pre-existing training corpora, but no contamination study was found."}
harness: {inspect_evals: worldsense, lm_eval: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, reasoning, synthetic, bias-controlled]
sources:
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/worldsense/worldsense.py
    title: worldsense task source (Inspect Evals)
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/worldsense/README.md
    title: worldsense task README (Inspect Evals)
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2311.15930
    title: "WorldSense: A Synthetic Benchmark for Grounded Reasoning in Large Language Models"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-001 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-001"}
---
## What it measures

WorldSense is a synthetic benchmark designed to test whether a model can build and reliably reason over a small internal "world model" from a set of natural-language statements, while controlling for dataset biases that let models shortcut similar tasks without real understanding. The Inspect Evals implementation exposes a single `worldsense` task covering three problem types: Infer (judge whether a statement is true or false given the scenario), Compl (pick the one correct statement out of three options), and Consist (judge whether a set of statements is jointly possible or impossible). Each item also carries a difficulty grade, "trivial" (solvable from the statements alone) or "normal" (requiring the model to actually track world state).

## How it is scored

The task is scored by accuracy on the underlying true/false or multiple-choice judgement, with standard error reported alongside. Because the benchmark is explicitly built to control for response-position and label-frequency biases, the harness also computes a weighted accuracy that adjusts for tuple ID, problem name and problem size, intended to be more robust to a model exploiting superficial answer patterns than raw accuracy alone.

## Dataset and licence

WorldSense's items are synthetically generated rather than drawn from an existing text corpus, built around templated scenarios such as object placement and scheduling puzzles. Neither the Inspect Evals README nor the paper abstract read for this page states a total item count or an explicit dataset licence; both are left unknown here rather than guessed.

## Who publishes it

WorldSense was introduced by Youssef Benchekroun, Megi Dervishi, Mark Ibrahim, Jean-Baptiste Gaya, Xavier Martinet, Grégoire Mialon, Thomas Scialom, Emmanuel Dupoux, Dieuwke Hupkes and Pascal Vincent in "WorldSense: A Synthetic Benchmark for Grounded Reasoning in Large Language Models" (arXiv:2311.15930, submitted November 2023). Author affiliation was not confirmed from the sources opened for this page and is left unstated. The UK Government's AI Security Institute (via the Inspect Evals project) maintains this harness integration; no separate public leaderboard was found.

## Lineage

No predecessor or successor benchmark was identified for WorldSense in the sources read for this page. It is one of several synthetic, bias-controlled reasoning benchmarks that emerged around 2023-2024 in response to concerns that natural-corpus reasoning benchmarks can be solved via surface patterns rather than genuine world modelling; related benchmarks of that kind are not yet pages in this repository.

## Saturation and contamination

No saturation status was established from the sources read for this page. The original paper reports that GPT-3.5, GPT-4 and Llama-2-chat all make errors even with as few as three objects in the scenario, exhibit response biases, and do not reliably improve with chain-of-thought prompting; fine-tuning improved scores but did not generalise beyond the trained problem space, per the abstract. Because items are synthetically generated rather than scraped from existing text, direct verbatim contamination is less likely than for corpus-derived benchmarks, but this was not independently studied in the sources read.

## How to run it

Run the `worldsense` task in the Inspect Evals framework (`UKGovernmentBEIS/inspect_evals`). Results can be filtered or aggregated by problem type (Infer, Compl, Consist), problem name and difficulty grade; report which subset and grade a score covers, since the "trivial" and "normal" grades are designed to have very different difficulty.

## Reading the numbers

A high WorldSense score, especially on the "normal" grade, indicates a model can track and reason over an explicit small world model rather than answering from surface statement patterns; a model that scores well only on "trivial" items has not demonstrated that. Because the benchmark's own weighted-accuracy metric exists specifically to correct for response-position and label biases, a raw accuracy figure without the weighted variant should be treated cautiously. The original paper's finding that even strong 2023-era chat models erred with as few as three tracked objects suggests this benchmark can surface reasoning limits that other, less bias-controlled tasks miss.
