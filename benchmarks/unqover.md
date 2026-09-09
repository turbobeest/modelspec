---
id: unqover
name: "UnQover"
aliases: ["UNQOVERing Stereotyping Biases via Underspecified Questions"]
page_kind: benchmark
category: safety
subcategory: "stereotyping bias in underspecified QA"
status: active
summary: "UnQover probes gender, nationality, ethnicity and religion stereotypes with underspecified span-question-answering templates."
measures: "A paragraph names two candidates and asks an underspecified question. The model scores both spans even though context does not justify choosing either. Perturbations isolate stereotype bias from positional and question-attribute errors."
task_format: "Generated span-based QA templates covering gender-occupation, nationality, ethnicity and religion, with candidate-order and polarity perturbations."
metric: {name: "fairness (1 minus bias intensity); consistency alongside it", direction: higher_is_better, unit: "score", max_score: 1, random_baseline: null, human_baseline: null, baseline_note: "The README defines fairness and consistency but gives no random or human baseline."}
dataset:
  size: 10552928
  size_note: "BIG-bench's generated header reports 10,552,928 multiple-choice dummy-model queries."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/unqover"
  license: ""
  languages: [en]
  modalities: [text]
  splits: "generated gender-occupation, nationality, ethnicity and religion datasets; no train/test split stated"
  public_test_set: true
publisher: {org: "BIG-bench collaboration", authors: ["Tao Li", "Daniel Khashabi", "Tushar Khot", "Ashish Sabharwal", "Vivek Srikumar"], url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/unqover"}
paper: {title: "UNQOVERing Stereotyping Biases via Underspecified Questions", arxiv: "", url: "https://aclanthology.org/2020.findings-emnlp.311/", year: 2020}
leaderboard_url: ""
repo_url: "https://github.com/allenai/unqover"
released: "2020-11"
last_updated: ""
lineage: {family: "big_bench", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "Historical transformer analyses do not establish a current ceiling."}
contamination: {risk: high, note: "Templates and source lists are public; the paper does not establish resistance to full-task training."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "unqover", other: ""}
tags: [big-bench, safety, bias, question-answering, social-bias]
sources:
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/unqover/README.md", title: "BIG-bench UnQover README", accessed: "2026-09-09"}
  - {url: "https://aclanthology.org/2020.findings-emnlp.311/", title: "UNQOVER paper", accessed: "2026-09-09"}
  - {url: "https://github.com/allenai/unqover", title: "AllenAI UnQover implementation", accessed: "2026-09-09"}
  - {url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/unqover/task.py", title: "BIG-bench UnQover task.py", accessed: "2026-09-08"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

UnQover tests whether a QA model assigns stereotype-linked scores when a paragraph leaves the answer unresolved. A typical item names two people with different protected properties and asks about an attribute. Both candidate spans are plausible, so a fair model should not prefer one based only on the protected property.

It covers gender-occupation, nationality, ethnicity and religion. Candidate order and question polarity are perturbed to separate bias from positional dependence and failure to understand the queried attribute.

## How it is scored

The task reports bias intensity, count-based bias, average answer probability, positional error and attributive error. Headline metrics are fairness, one minus bias intensity, and consistency, which combines answer probability with the two error measures. Fairness and consistency range from 0 to 1 and are higher-is-better; components use their own directions.

Candidate probabilities need not sum to one. High fairness can be misleading when both candidates receive low probability or the model is inconsistent, so report consistency and answer probability too.

## Dataset and licence

BIG-bench generates examples from templates for four stereotype classes. Sources include occupations, manually selected attributes, names, nationalities, ethnicities and religions. The generated header reports 10,552,928 multiple-choice dummy-model queries, not a conventional train/test split.

The opened sources do not establish one licence for the combined generated data. Source materials may have separate terms.

## Who publishes it

BIG-bench credits Tao Li, Daniel Khashabi, Tushar Khot, Ashish Sabharwal and Vivek Srikumar. The underlying paper appeared in Findings of EMNLP 2020. The AllenAI repository contains implementation and metrics. No current standalone leaderboard was established.

## Lineage

UnQover is based on the 2020 paper and appears as a BIG-bench task. Internally, task.py scores four subtasks keyed gender, nationality, ethnicity and religion, but none of these has its own page or a separate BIG-bench id in this repository. UnQover is related to BBQ and StereoSet but uses underspecified span QA and its own fairness and consistency metrics. No successor was established.

## Saturation and contamination

Templates and source lists are public, so contamination risk is high. The paper discusses robustness to a few memorized examples but not full-task training. Current saturation is unknown.

## How to run it

Run BIG-bench task unqover with span scoring and candidate-order and polarity perturbations. Record model type, span scoring method and aggregation over the four datasets. Do not replace fairness with ordinary QA accuracy.

## Reading the numbers

Higher fairness means lower measured stereotype-linked bias on this template set. It does not show that a model is free of social bias. Inspect consistency and answer probability before interpreting fairness. Pair UnQover with BBQ and evaluations across cultures.

