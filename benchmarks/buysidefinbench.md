---
id: buysidefinbench
name: BuySideFinBench
aliases: []
page_kind: benchmark
category: domain
subcategory: "buy-side equity-research and valuation reasoning (bilingual multiple-choice)"
status: active
summary: A single-contributor, bilingual Chinese/English OpenCompass benchmark of 180 multiple-choice questions testing buy-side equity-research skills such as DCF valuation and three-statement linkage.
measures: >
  BuySideFinBench targets the analytical skills of a buy-side equity-research analyst rather than
  the sell-side, news-driven or surface-level knowledge tasks its own documentation says dominate
  existing finance benchmarks. It covers six subjects: tracing cash impact across the income
  statement, balance sheet and cash-flow statement; discounted-cash-flow valuation mechanics;
  comparable-company analysis; interpreting financial ratios in context; IFRS-versus-US-GAAP
  accounting-standard distinctions; and sensitivity/scenario analysis. Every subject is offered in
  both Chinese and English, so a score can also be read as a same-skill language comparison.
  Questions are original scenarios or paraphrased from public materials -- CFA/CICPA preparatory
  texts, SEC/HKEXnews/CSRC filing examples, and IFRS Foundation/FASB publications -- rather than
  reproduced exam content.
task_format: >
  Four-option multiple-choice question (A-D) in one of six buy-side analysis subjects and one of
  two languages; the model returns a single letter answer, prompted five-shot from each subset's
  own five-question dev split.
metric:
  name: "accuracy (exact match after answer normalization)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Four options per question give a naive random baseline of 25%; the source documentation states
    no adjusted or measured baseline. No human baseline, and no third-party reported model scores,
    were found for this page. Because each of the 12 subject/language subsets is scored separately
    (`BuySideFinBench-<subset>` in OpenCompass output), a single averaged "BuySideFinBench score" is
    not itself defined by the source -- a reporter must state how it aggregated the 12 subset
    accuracies.
dataset:
  size: 180
  size_note: >
    12 subsets (6 subjects x 2 languages), each with 5 dev questions (used as five-shot exemplars)
    and 10 test questions (scored): 180 instances total, of which 120 are scored test items and 60
    are exemplar items. Confirmed directly against the Hugging Face dataset's own config metadata.
  url: "https://huggingface.co/datasets/cindy90/BuySideFinBench"
  license: "Apache License 2.0, per both the Hugging Face dataset card and the OpenCompass documentation page"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "12 subsets x (5-question dev / 10-question test); dev used only as five-shot exemplars, test is scored"
  public_test_set: true
publisher:
  org: ""
  authors: []
  url: "https://huggingface.co/datasets/cindy90/BuySideFinBench"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/BuySideFinBench"
released: "2026-07"
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
  note: >
    No independently reported model scores on BuySideFinBench -- from a maintained leaderboard or
    from other papers -- were found for this page, likely reflecting how recently the benchmark was
    merged into OpenCompass (2026-07-09) and its very small evaluation footprint (120 scored items).
contamination:
  risk: medium
  note: >
    Every question and its gold answer is public on both Hugging Face and GitHub, so a model trained
    after mid-2026 could plausibly have seen it; the benchmark's short time in public circulation as
    of this page's research date (about two months) limits how much exposure has accumulated so far.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "BuySideFinBench_gen (BuySideFinBench_gen_ca1704.py)"
  bigbench: ""
  other: ""
tags:
  - finance
  - domain
  - multiple-choice
  - bilingual
  - valuation
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/BuySideFinBench/README.md"
    title: "OpenCompass BuySideFinBench dataset README"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/BuySideFinBench/BuySideFinBench_gen_ca1704.py"
    title: "OpenCompass BuySideFinBench_gen_ca1704.py (evaluation config)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cindy90/BuySideFinBench"
    title: "cindy90/BuySideFinBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/pull/2446"
    title: "OpenCompass PR #2446, \"[Feature] Add BuySideFinBench dataset for buy-side financial analysis\""
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BuySideFinBench targets the analytical skills of a buy-side equity-research analyst, a gap its own documentation says existing finance benchmarks in the OpenCompass ecosystem leave open by testing sell-side, news-driven tasks (sentiment, summarization, headline interpretation) or surface-level CFA-style knowledge instead. It spans six subjects: tracing cash impact across the three linked financial statements, discounted-cash-flow valuation mechanics, comparable-company analysis, interpreting financial ratios in context rather than just computing them, IFRS-versus-US-GAAP accounting-standard distinctions, and sensitivity/scenario analysis. Every subject appears in both Chinese and English, so a score can double as a same-skill language comparison.

Questions are either original analytical scenarios built from publicly known company financials or paraphrased from public preparatory and standard-setting material -- CFA and CICPA exam-prep texts, SEC EDGAR, HKEXnews and CSRC disclosure examples, and IFRS Foundation and FASB publications -- rather than reproduced copyrighted exam content. It is a single-turn, text-only, four-option multiple-choice task.

## How it is scored

Scoring is plain accuracy: OpenCompass's `AccEvaluator` checks the extracted answer letter against the gold option after normalization, following the same `FixKRetriever` (five-shot) / `GenInferencer` / `AccEvaluator` pattern OpenCompass uses for its existing FinanceIQ dataset, which the author states was a deliberate choice for direct comparability. With four options, a naive random baseline is 25%; no adjusted baseline, human baseline, or third-party reported model score was found for this page. Because each of the 12 subject/language subsets is reported separately (as `BuySideFinBench-<subset>`), a single averaged "BuySideFinBench score" is not itself defined by the source -- a reporter would need to state how it combined the 12 subset accuracies.

## Dataset and licence

The dataset totals 180 instances: 6 subjects x 2 languages = 12 subsets, each with 5 dev questions (used only as five-shot in-context exemplars) and 10 test questions (scored), for 120 scored items and 60 exemplar items overall. It is hosted at `cindy90/BuySideFinBench` on Hugging Face and released under the Apache 2.0 licence, per both the Hugging Face dataset card and the OpenCompass documentation page. Every item, in both splits, carries a public gold answer; there is no held-out portion.

## Who publishes it

BuySideFinBench was contributed to OpenCompass by a single Hugging Face and GitHub user under the handle `cindy90` (Hugging Face account created July 2025; this dataset is that account's only public Hugging Face upload). No institutional affiliation, full name, or peer-reviewed paper was found: its only citation is a self-authored `@misc` entry dated 2026. The contribution was opened as OpenCompass pull request #2446 on 2026-05-13 and merged on 2026-07-09, which this page uses as its release date. This is a community contribution to the OpenCompass ecosystem rather than a benchmark from an academic or industry research group, and its provenance should be weighed accordingly.

## Lineage

BuySideFinBench has no predecessor or successor tracked in this repository. Its own documentation positions it explicitly against other finance benchmarks in the OpenCompass ecosystem it characterises as sell-side or surface-level: FinanceIQ, whose five-shot/`AccEvaluator` evaluation pattern it explicitly reuses for comparability, and FinEval, CFLUE, FinNLP and FPB -- none of which yet have a page in this repository. It is unrelated to `finbench` (documented separately here: a ten-dataset, Kaggle-sourced credit-risk and fraud tabular-classification benchmark) and to `financebench` (Patronus AI's SEC-filings open-book question-answering benchmark, also documented separately). A reader should not conflate any of these three differently-scoped "finance benchmark" names.

## Saturation and contamination

No saturation status can be established: this page found no independently reported model scores on BuySideFinBench, from either a maintained leaderboard or another paper, most likely because the benchmark was only merged into OpenCompass on 2026-07-09 and has a very small evaluation footprint (120 scored items).

Contamination risk is medium: every question and its gold answer is public on both Hugging Face and GitHub, so a model trained after mid-2026 could plausibly have seen it, though the benchmark's short time in public circulation as of this page's research date (roughly two months) limits how much exposure could have accumulated so far.

## How to run it

OpenCompass ships `BuySideFinBench_gen` (`opencompass/configs/datasets/BuySideFinBench/BuySideFinBench_gen_ca1704.py`), which downloads the 12 subsets from Hugging Face automatically, prompts each five-shot from its own dev split via `FixKRetriever`, generates a free-form response with `GenInferencer`, extracts the option letter with `first_option_postprocess`, and scores with `AccEvaluator`. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because prompts are written entirely in the subset's own language (Chinese for `_zh` subsets, English for `_en`), a model's Chinese and English subset scores reflect both financial reasoning and language-specific instruction-following at once.

## Reading the numbers

A high score suggests a model can trace three-statement cash effects, reason through DCF mechanics, and apply accounting-standard distinctions in a structured multiple-choice setting -- a narrower, more mechanical test than actually building a valuation model from scratch, a limitation the benchmark's own documentation acknowledges alongside its small scale. With only 10 scored questions per subject/language cell, a handful of items can swing a subset's accuracy sharply, so any single-subset score is a rough signal rather than a precise measurement. Because this is an unreviewed, single-contributor community dataset with no independent replication or leaderboard found, corroborate any reported BuySideFinBench number against the model's performance on better-established finance benchmarks before drawing conclusions from it.
