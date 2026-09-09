---
id: swiss_bench_sbp_002
name: "Swiss-Bench SBP-002"
aliases:
  - "Swiss-Bench 002"
  - "SBP-002"
page_kind: benchmark
category: domain
subcategory: "applied Swiss regulatory compliance (FINMA, Legal-CH, EFK) in DE/FR/IT"
status: unknown
summary: "Trilingual Swiss regulatory-compliance eval of 395 expert items; a three-judge panel found even the top model only 38.2% correct under zero retrieval."
measures: >
  Swiss-Bench SBP-002 tests whether a frontier LLM can give usable Swiss regulatory
  advice from parameters alone. Items cover three domains: FINMA financial supervision,
  Swiss federal law (Legal-CH, including nDSG and Code of Obligations plus EU AI Act
  impact on Swiss firms), and Swiss Federal Audit Office (EFK) control scenarios.
  Seven task types mix regulatory Q&A, hallucination detection, gap analysis,
  jurisdiction discrimination, statutory interpretation, case analysis and legal
  translation. The author contrasts this applied-compliance setting with Swiss exam
  recall (LEXam) and Swiss legal translation (SwiLTra-Bench).
task_format: >
  Single-turn user prompt, no system prompt and no retrieval, temperature 0, max
  4,096 output tokens. Languages are German, French and Italian. Judges return three
  numeric dimensions; a grade is computed from those numbers.
metric:
  name: "correct rate (C%) from majority-vote C/P/I grades"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Judges score Legal Accuracy (weight 0.5), Citation Accuracy (0.3) and Completeness
    (0.2) in {0, 0.5, 1.0}. Combined S maps to C if S>=0.8, P if 0.5<=S<0.8, I if
    S<0.5. The headline number is the share of items graded C by majority vote of
    GPT-4o, Claude Sonnet 4 and Qwen3-235B. Weighted kappa on a 30-item calibration
    set is 0.605.
dataset:
  size: 395
  size_note: >
    395 scored items from a larger pool of about 2,000 candidates (seed 42). Domain
    counts: FINMA 178, Legal-CH 169, EFK 48. Languages: German 150, French 148,
    Italian 97. Eighteen extra English items exist but are excluded from reported
    scores. Task counts: regulatory Q&A 104, hallucination detection 63, gap analysis
    59, jurisdiction discrimination 58, statutory interpretation 46, case analysis 35,
    legal translation 30.
  url: "https://github.com/FUenal/swiss-bench"
  license: "CC-BY-NC-SA-4.0"
  languages:
    - de
    - fr
    - it
  modalities:
    - text
  splits: "single evaluation set of 395 items; no separate public test split described"
  public_test_set: true
publisher:
  org: "Fatih Uenal, University of Colorado Boulder"
  authors:
    - "Fatih Uenal"
  url: "https://github.com/FUenal/swiss-bench"
paper:
  title: "Swiss-Bench SBP-002: A Frontier Model Comparison on Swiss Legal and Regulatory Tasks"
  arxiv: "2603.23646"
  url: "https://arxiv.org/abs/2603.23646"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/FUenal/swiss-bench"
released: "2026-03"
last_updated: "2026-03"
lineage:
  family: ""
  predecessor: ""
  successors:
    - swiss_bench_003
  variants: []
saturation:
  status: open
  top_score: 38.2
  as_of: "2026-03"
  note: >
    Qwen 3.5 Plus 38.2% C (95% Wilson CI 33.6-43.1) on 20 March 2026 runs. Gemini 2.5
    Flash 35.4%. Six models sit in a 13-21% band. Legal translation and case analysis
    are much easier than regulatory Q&A, hallucination detection and gap analysis.
contamination:
  risk: medium
  note: >
    Expert-written 2026 items, so they are unlikely to be in older pretraining dumps.
    The GitHub README publishes the benchmark under CC BY-NC-SA 4.0 and the paper
    warns that the compact 395-item set is easy to overfit if later models train on it.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - swiss
  - legal
  - regulatory
  - multilingual
  - llm-as-judge
sources:
  - url: "https://arxiv.org/abs/2603.23646"
    title: "Swiss-Bench SBP-002 paper (arXiv:2603.23646v1)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2603.23646"
    title: "Swiss-Bench SBP-002 HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/FUenal/swiss-bench"
    title: "FUenal/swiss-bench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FUenal/swiss-bench/main/README.md"
    title: "Swiss-Bench SBP-002 README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SBP-002 asks a model for applied Swiss compliance guidance, not exam recall. A typical item is a German, French or Italian prompt about FINMA rules, nDSG/OR questions, or EFK audit controls.

The seven task types range from answering a provision, spotting a planted legal falsehood, and finding a compliance gap, to telling Swiss law from nearby EU or German rules, interpreting statutes, analysing a fact pattern, and translating legal terms. There is no retrieval. The score is parametric knowledge plus citation hygiene.

## How it is scored

Three blinded judges (GPT-4o, Claude Sonnet 4, Qwen3-235B) each emit Legal Accuracy, Citation Accuracy and Completeness. A deterministic formula turns those into C, P or I. Majority vote of the three grades is the item result. The headline metric is C%.

On a 30-item calibration set, structured scoring raised weighted kappa from 0.512 to 0.605. A Swiss MLaw expert reviewed 100 German reference answers: Legal Accuracy 1.0 on all 100, 73 C / 27 P / 0 I. The P grades were mostly missing page pins in FINMA cites or a thin Swiss/German contrast, not fabricated law.

All runs used temperature 0 on 20 March 2026. Nine models went through OpenRouter; Gemini 2.5 Flash used the Google AI API.

## Dataset and licence

395 items after stratified sampling from about 2,000 candidates. FINMA 178, Legal-CH 169, EFK 48. German 150, French 148, Italian 97. French and Italian items were GPT-4o translations of German sources with an author-led terminology audit, not an independent translator.

The GitHub README states CC BY-NC-SA 4.0. The arXiv HTML also shows a CC BY-NC-SA 4.0 paper licence. The paper says dataset, rubrics and tooling are at github.com/FUenal/swiss-bench.

## Who publishes it

Fatih Uenal (University of Colorado Boulder) is the sole author. SBP-001 was an unpublished 30-item pilot. There is no live third-party leaderboard; the paper and README are the score tables.

## Lineage

This is not LEXam, SwiLTra-Bench, Swiss-Judgment-Prediction or LegalBench. Those cover exams, translation, judgment prediction or US law. SBP-002 is applied Swiss regulatory work.

[swiss_bench_003](swiss_bench_003.md) is the next Swiss-Bench paper (SBP-003). It adds HAAS D7/D8 reliability and security items. The SBP-003 paper says the two result tables are not comparable: different tasks, dates, scoring and a partly different model list.

## Saturation and contamination

The benchmark is hard under zero retrieval. Qwen 3.5 Plus reaches 38.2% C with 47.3% I. Mean C% is about 72% on legal translation and 69% on case analysis, but below 9% on regulatory Q&A, hallucination detection and gap analysis. FINMA and EFK are much harder than Legal-CH. EFK's 48 items are all regulatory Q&A, so domain and task type are confounded.

Italian C% looks higher, but 30.9% of Italian items are the two easy task types versus 6.7% of German items. Do not read that as an Italian-language effect.

Items are recent and expert-written, which lowers accidental pretraining overlap, but the small public set is easy to overfit once it circulates.

## How to run it

No lm-eval or inspect_evals task name was confirmed. Reproduce from the GitHub protocol: temperature 0, no system prompt, no retrieval, the published judge prompt, majority vote.

Changing judges, adding RAG, or mixing languages without the composition table will move C% a lot. Claude Sonnet 4 is both a judge and an evaluand; a two-judge sensitivity check in the appendix left its tier unchanged.

## Reading the numbers

38% C means the model was graded fully correct on about two in five isolated Swiss prompts, not that it is deployable. The author says no tested model is fit for unattended Swiss regulatory work in this setting.

Compare task types before models. A model that translates well can still fail hallucination detection. Read [swiss_bench_003](swiss_bench_003.md) for security and self-graded reliability; do not average the two papers.
