---
id: lcbench
name: "LCBench2023"
aliases:
  - "LCBench"
page_kind: benchmark
category: coding
subcategory: "bilingual (English/Chinese) code generation from LeetCode weekly-contest problems, scored by test execution"
status: active
summary: "OpenCompass's LCBench2023: 581 LeetCode weekly-contest problems (2022-2023) in English and Chinese, scored pass@1 by executing generated code against each problem's tests."
measures: >
  The census hint for this id names an OpenCompass source directory, and opening it shows "lcbench"
  here is LCBench2023, a code-generation benchmark built from LeetCode weekly-contest problems --
  not a long-context benchmark, and not the unrelated AutoML "LCBench" learning-curve dataset that
  also exists under the same short name (see Lineage). LCBench2023 gives a model a
  competitive-programming problem statement, drawn from LeetCode weekly contests held in 2022 and
  2023, plus a set of example test assertions the solution must satisfy, and asks for a Python
  function that solves it. The same 581 problems ship in two parallel versions, one with the
  problem statement in English and one in Chinese, so the same underlying coding task can be
  compared across the two prompt languages.
task_format: >
  A LeetCode-style problem statement plus example assert test cases in (English or Chinese
  version); the model returns Python code in a fenced code block, which is executed against the
  problem's tests in a sandboxed subprocess with a per-attempt timeout, and classified as pass,
  timeout, wrong_answer or failed.
metric:
  name: "pass@1 (share of problems solved on a single sampled generation, by direct test execution); pass@10 and pass@100 are also defined via a repeated-sampling config"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline applies to a free-form code-generation task. OpenCompass's own
    reference table (base and chat models, mostly from the Llama-3/Qwen1.5/InternLM2 generation)
    shows a wide range: the strongest model listed, Llama-3-70B-instruct, reached 45.44% pass@1
    overall, while several small models (for example Qwen1.5-0.5B-chat) scored 0%.
dataset:
  size: 1162
  size_note: >
    581 problems in each of two parallel-language configs (English and Chinese, the same
    underlying LeetCode problems), 1,162 rows total, confirmed directly from the loader code
    (opencompass/datasets/LCBench.py), which reads each config's single JSONL file, holds out the
    first 5 rows as fixed few-shot exemplars, and scores the remaining 576 as the test set --
    1,152 scored problems total across both languages. No standalone Hugging Face dataset page was
    found; the data ships as JSONL files bundled with OpenCompass's own data download rather than
    hosted as a separate, independently citable dataset release.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/LCBench"
  license: "Not stated separately for the problem data. The OpenCompass repository itself is Apache-2.0 (confirmed from its LICENSE file); the underlying problem statements and test cases originate from LeetCode's weekly programming contests, a proprietary third-party source OpenCompass does not separately license."
  languages:
    - en
    - zh
  modalities:
    - code
  splits: "two configs (lcbench_en, lcbench_cn), each a single JSONL file with the first 5 rows used as fixed few-shot exemplars and the remaining 576 rows scored as the test set"
  public_test_set: true
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/LCBench"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 45.44
  as_of: ""
  note: >
    Not saturated on OpenCompass's own reference table: the strongest model listed,
    Llama-3-70B-instruct, reached 45.44% pass@1 overall (46.09% English, 44.79% Chinese), with most
    other models well below that and several very small models (for example Qwen1.5-0.5B-chat)
    scoring 0%. The table itself is not dated, and this page could not confirm exactly when it was
    last regenerated; the model families shown (Llama 3, Qwen1.5, InternLM2, Mixtral 8x22B) suggest
    a 2024 snapshot, but that is an inference from which models appear rather than a confirmed
    date, so as_of is left unset.
contamination:
  risk: high
  note: >
    LeetCode weekly-contest problems are publicly announced and solved by many participants within
    hours of each contest, and write-ups and solutions are routinely posted publicly afterward on
    forums, blogs and code repositories. Because this benchmark draws specifically on 2022-2023
    contests, its items were almost certainly already circulating in public solution threads well
    before most current models' training cutoffs, and the compiled dataset itself, gold test cases
    included, ships directly inside the OpenCompass repository without gating.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "LCBench (task abbreviations lcbench_en, lcbench_cn; loaded via LCDataset, scored via LCEvaluator/LCPassKEvaluator)"
  bigbench: ""
  other: >
    A separate repeat-10 config (lcbench_repeat10_gen.py) resamples each problem 10 times per
    generation for pass@10/pass@100 estimation via the same LCPassKEvaluator, which supports
    k=(1,10,100) by default.
tags:
  - coding
  - code-generation
  - leetcode
  - bilingual
  - pass-at-k
  - competitive-programming
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/LCBench"
    title: "OpenCompass LCBench dataset configs directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/LCBench/README.md"
    title: "LCBench2023 README (description, base/chat model results table), OpenCompass"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/LCBench/lcbench_gen_5ff288.py"
    title: "LCBench pass@1 generation config (prompt template, dataset paths), OpenCompass"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/LCBench.py"
    title: "LCDataset loader and LCEvaluator/LCPassKEvaluator scoring code, OpenCompass"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass repository LICENSE file (Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://github.com/automl/LCBench"
    title: "automl/LCBench GitHub repository (unrelated AutoML learning-curve dataset, cited here only to disambiguate the name)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The census hint for this id names an OpenCompass source directory, and opening it shows "lcbench" here is LCBench2023, a code-generation benchmark built from LeetCode weekly-contest problems -- not a long-context benchmark, and not the unrelated AutoML "LCBench" learning-curve dataset that also exists under the same short name (see Lineage). LCBench2023 gives a model a competitive-programming problem statement, drawn from LeetCode weekly contests held in 2022 and 2023, plus a set of example test assertions the solution must satisfy, and asks for a Python function that solves it. The same 581 problems ship in two parallel versions, one with the problem statement in English and one in Chinese, so the same underlying coding task can be compared across the two prompt languages.

## How it is scored

The model's response is parsed for a fenced Python code block (with fallbacks for markers such as `[BEGIN]`/`[DONE]` seen in some model outputs), which is then executed in a sandboxed subprocess against the problem's test assertions with a per-attempt timeout. Each attempt is classified as `pass`, `timeout`, `wrong_answer` or `failed`, and the headline metric is `pass@1`: the share of problems solved on a single sampled generation. OpenCompass's default configuration prompts with three fixed worked examples hardcoded directly in the prompt template (a form of few-shot prompting) rather than sampling exemplars from the data at random. A separate repeat-10 configuration resamples each problem 10 times so that `pass@10` and `pass@100` can also be estimated, using the same unbiased pass@k estimator popularized by HumanEval-style benchmarks.

## Dataset and licence

581 problems exist in each of two parallel-language configs (English and Chinese, the same underlying LeetCode problems), 1,162 rows total, confirmed directly from the loader code. The loader holds out each config's first 5 rows as fixed few-shot exemplars and scores the remaining 576 as the test set -- 1,152 scored problems total across both languages. No standalone Hugging Face dataset page was found for LCBench2023; the data ships as JSONL files bundled with OpenCompass's own data download rather than as a separately hosted, independently citable release. The OpenCompass repository itself is Apache-2.0 licensed, but that licence covers the harness code, not necessarily the problem content: the underlying statements and test cases originate from LeetCode's weekly programming contests, a proprietary third-party source that OpenCompass does not separately license here.

## Who publishes it

LCBench2023 is maintained by the OpenCompass project (Shanghai AI Laboratory) as one of many task configurations bundled directly into the OpenCompass evaluation repository, rather than released alongside an independent academic paper the way most benchmarks in this repository are. No individual author byline or citation entry was found for this specific task; it is credited to the OpenCompass project as a whole, and OpenCompass's own README table of base- and chat-model results is the only results reference found during this research.

## Lineage

The name "LCBench" is genuinely ambiguous, and this page exists specifically to resolve which project a given "lcbench" citation means. Opening the OpenCompass source the census hint named confirms it as LCBench2023, a bilingual LeetCode-contest coding benchmark, documented on this page. A separate, unrelated project also called LCBench exists in the AutoML literature: a large-scale learning-curve dataset from Zimmer, Lindauer and Hutter's Auto-PyTorch Tabular work (automl/LCBench on GitHub), logging training, validation and test metrics epoch-by-epoch for 2,000 neural-network configurations across 35 OpenML datasets, used to benchmark hyperparameter-optimization and neural-architecture-search methods rather than language models. That AutoML LCBench has nothing to do with code generation, LeetCode, or long-context evaluation. This research also did not find any long-context benchmark actually published under the name "LCBench" -- a plausible-sounding reading given this repository's other "LC"-prefixed long-context suites (longbench, lveval), but not one this page could confirm exists. Anyone citing an "LCBench" score should confirm which of these projects produced it before comparing it to another report.

## Saturation and contamination

Not saturated on OpenCompass's own reference table: the strongest model listed, Llama-3-70B-instruct, reached 45.44% pass@1 overall (46.09% English, 44.79% Chinese), with most other models well below that and several very small models (for example Qwen1.5-0.5B-chat) scoring 0%. The table is not dated, and this page could not confirm exactly when it was last regenerated; the model families shown (Llama 3, Qwen1.5, InternLM2, Mixtral 8x22B) suggest a 2024 snapshot, but that is an inference from which models appear, not a confirmed date.

Contamination risk is high: LeetCode weekly-contest problems are publicly announced and solved by many participants within hours of each contest, and write-ups and solutions are routinely posted publicly afterward on forums, blogs and code repositories. Because this benchmark draws specifically on 2022-2023 contests, its items were almost certainly already circulating in public solution threads well before most current models' training cutoffs, and the compiled dataset itself, gold test cases included, ships directly inside the OpenCompass repository without gating.

## How to run it

OpenCompass implements the benchmark as `LCBench` (task abbreviations `lcbench_en`, `lcbench_cn`), loading each language's JSONL file through `LCDataset` and scoring with `LCEvaluator` or `LCPassKEvaluator` (`opencompass/datasets/LCBench.py`). The default generation config (`lcbench_gen_5ff288.py`) samples one completion per problem for `pass@1`; a separate `lcbench_repeat10_gen.py` config resamples each problem 10 times so `pass@10` and `pass@100` can also be estimated. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found during this research. Because code execution happens in a sandboxed subprocess with a fixed timeout, and because the harness tries several fallback strategies to extract code from a response (fenced blocks, `[BEGIN]`/`[DONE]` markers, or the raw text), reported scores can be sensitive to how cleanly a given model formats its code, independent of whether the underlying solution logic is correct.

## Reading the numbers

A high LCBench2023 pass@1 score is evidence a model can solve fresh-at-the-time competitive-programming problems in working Python, in both English and Chinese phrasing of the same task -- useful for comparing a model's coding ability across the two prompt languages specifically, which most coding benchmarks in this repository do not test. Because the benchmark's problems are pulled from real, publicly discussed contests rather than held out or refreshed, and its contamination risk is high, a very high score is more likely to reflect exposure to public solutions than superior reasoning; weigh it alongside a less contamination-prone coding benchmark before drawing conclusions about general coding ability. Above all, confirm which "LCBench" a reported number refers to -- this bilingual LeetCode benchmark, or the unrelated AutoML learning-curve dataset of the same name -- before comparing it to anything else.
