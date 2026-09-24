---
id: vending_bench_2
name: Vending-Bench 2
aliases: []
page_kind: benchmark
category: agentic
subcategory: long-horizon business simulation
status: active
summary: Andon Labs' year-long simulated vending business; the score is the agent's bank balance at the
  end, in US dollars.
measures: An agent runs a simulated vending machine business for a year, finding and negotiating with
  suppliers by email, stocking the machine and setting prices. It measures long-horizon coherence and
  business judgement.
task_format: A long-running agent loop with web search, email, storage and machine tools, over one simulated
  year.
metric:
  name: final money balance
  direction: higher_is_better
  unit: USD
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: Every run starts with a $500 balance; the board reports the mean over 5 runs.
dataset:
  size: null
  size_note: One simulated environment, run 5 times per model.
  url: https://andonlabs.com/evals/vending-bench-2
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: ''
  public_test_set: null
publisher:
  org: Andon Labs
  authors: []
  url: https://andonlabs.com/evals/vending-bench-2
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: https://andonlabs.com/evals/vending-bench-2
repo_url: ''
released: 2025-11
last_updated: 2026-09
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 15514.7
  as_of: 2026-09
  note: The board has no ceiling; the leader read on 2026-09-24 was GPT-6 Astra at $15,514.70.
contamination:
  risk: low
  note: A simulated, stochastic year cannot be memorised.
harness:
  other: Andon Labs runs it; the system prompt is published on the page.
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
tags:
- agentic
- long-horizon
- simulation
sources:
- url: https://andonlabs.com/evals/vending-bench-2
  title: Vending-Bench 2 (Andon Labs)
  accessed: '2026-09-24'
- url: https://epoch.ai/data/benchmark_data.zip
  title: Epoch AI benchmark data, vending_bench_2_external.csv (CC BY 4.0)
  accessed: '2026-09-24'
freshness:
  researched: '2026-09-24'
  researched_by: Claude Opus 5.5, MODEL-123
  reviewed: ''
  reviewed_by: ''
domains:
  - {id: agentic_tool_use, directness: direct}
---

## What it measures

Andon Labs asks a model to make as much money as possible running a vending machine over a simulated year. It must find suppliers on the web, negotiate by email, move stock and set prices, while some suppliers are adversarial, deliveries slip and customers demand refunds. A run takes 3,000 to 6,000 messages. It measures whether an agent stays coherent and competent over a very long horizon.

## How it is scored

The score is the bank balance after one year, in US dollars, averaged over 5 runs. Every run starts with $500 and pays a $2 daily fee; a model that cannot pay for more than 10 consecutive days is terminated early. The score has no ceiling. ModelSpec normalises it between the $500 starting balance and $30,000, a bound chosen with about 18 months of headroom at the board's trend, and a test fails before a card reaches it.

## Dataset and licence

There is no dataset: the benchmark is a simulated environment operated by Andon Labs. Its licence terms were not established from a source read for this page.

## Who publishes it

Andon Labs publishes the board and runs the evaluations. Epoch AI copies the results into its benchmark data under CC BY 4.0.

## Lineage

It succeeds the original Vending-Bench, which Andon Labs now marks deprecated, adding adversarial suppliers, delays and refunds, and simpler scoring. Vending-Bench Arena adds competing agents and is a separate board. The agentic profile weights Vending-Bench 2 since MODEL-123.

## Saturation and contamination

Not saturated: the board shows a wide spread and a leader that rises month on month. The simulation is stochastic, so memorisation does not help.

## How to run it

Only Andon Labs runs it, and it publishes the system prompt the agent receives. A provider quoting its own Vending-Bench 2 number should cite the board. Andon Labs notes that the top models keep a steady rate of tool use through the whole year and source products at good prices, by negotiating or by finding better suppliers.

## Reading the numbers

A higher balance means a model ran the business better over the year. The spread between runs is large, so compare means with the reported interval. It tests planning and persistence, not coding or knowledge.
