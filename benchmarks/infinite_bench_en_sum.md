---
id: infinite_bench_en_sum
name: "∞Bench: En.Sum (English Summarisation)"
page_kind: subset
category: long-context
subcategory: "long-document summarisation of English novels"
status: active
summary: "∞Bench's summarisation split: produce a concise summary of a full English novel averaging around 104K tokens, scored by ROUGE-L-Sum against a web-sourced reference summary."
measures: >
  Given a full English novel (averaging about 103,500 tokens of context), the model must produce a concise
  summary, capped at 1,200 output tokens in the reference setup. Reference summaries are sourced from the
  web and manually filtered to remove non-summary content such as reader comments, then, like the other
  English book tasks, subjected to ∞Bench's key-entity replacement to reduce the chance a model recognises
  the specific book from pretraining alone. Unlike En.MC and En.QA, which test locating and combining
  specific facts, En.Sum tests whether a model can compress an entire long document's content, not just
  retrieve isolated details from it.
task_format: >
  Free-text summary generation over a full-length novel, evaluated automatically against a single
  reference summary rather than by an LLM judge or human raters.
metric:
  name: "ROUGE-L-Sum"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    No random baseline applies to ROUGE scoring. The reference implementation computes ROUGE-L-Sum with
    the Hugging Face `evaluate` library's rouge metric, comparing the generated summary against one
    reference summary per book. No human baseline is established here.
dataset:
  size: 103
  size_note: >
    103 examples, averaging about 103,500 input tokens and 1,100 output (reference-summary) tokens, per
    the ∞Bench paper's Table 2 -- the smallest of ∞Bench's 12 tasks by example count and the shortest
    average input context of the three English book tasks. Human-annotated (reference summaries manually
    filtered), from the same pool of modified English novels as En.MC and En.QA. Hugging Face split name
    longbook_sum_eng, within the shared xinrongzhang2022/InfiniteBench dataset.
  url: "https://huggingface.co/datasets/xinrongzhang2022/InfiniteBench"
  license: "MIT, per the OpenBMB/InfiniteBench GitHub repository; see the infinitebench family page."
  languages:
    - en
  modalities:
    - text
  splits: "longbook_sum_eng: 103 examples, single evaluation split (no train/validation)"
  public_test_set: true
publisher:
  org: "Department of Computer Science and Technology, Tsinghua University"
  authors:
    - "Xinrong Zhang"
    - "Yingfa Chen"
    - "Shengding Hu"
    - "Zihang Xu"
    - "Junhao Chen"
    - "Moo Khai Hao"
    - "Xu Han"
    - "Zhen Leng Thai"
    - "Shuo Wang"
    - "Zhiyuan Liu"
    - "Maosong Sun"
  url: "https://github.com/OpenBMB/InfiniteBench"
paper:
  title: "∞Bench: Extending Long Context Evaluation Beyond 100K Tokens"
  arxiv: "2402.13718"
  url: "https://arxiv.org/abs/2402.13718"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/OpenBMB/InfiniteBench"
released: "2024-02"
lineage:
  family: infinitebench
saturation:
  status: unknown
  top_score: 17.93
  as_of: "2024-02"
  note: >
    At release, Kimi-Chat led this specific task with a ROUGE-L-Sum of 17.93, ahead of GPT-4 (14.73),
    Claude 2 (14.45) and YaRN-Mistral-7B-128K (9.09) -- uniformly low scores across every model tested,
    which is typical of ROUGE-style metrics scored against a single reference summary rather than evidence
    every model summarised poorly. As with the infinitebench family page, this pass found no independently
    maintained current leaderboard, so today's standing on this specific split is not established.
contamination:
  risk: medium
  note: >
    The underlying novels are real published books plausibly already present in pretraining corpora, and
    the reference summaries are themselves sourced from the web (then filtered), so some reference
    summaries could plausibly overlap with pretraining text independent of this benchmark; ∞Bench's
    key-entity replacement is intended to reduce, not eliminate, that risk. No source read for this page
    states a measured contamination rate.
harness:
  helm: "infinite_bench_en_sum"
  opencompass: "InfiniteBench_ensum"
  other: >
    OpenCompass scores this task with a generic RougeEvaluator. HELM's scenario metadata names rouge_l as
    its main_metric. Both harnesses cap generation at 1,200 output tokens by default, matching the paper's
    own decoding cap for this task.
tags:
  - long-context
  - summarization
  - generation
  - english
  - infinitebench-subset
sources:
  - url: "https://arxiv.org/abs/2402.13718"
    title: "∞Bench: Extending Long Context Evaluation Beyond 100K Tokens"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.13718"
    title: "∞Bench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/xinrongzhang2022/InfiniteBench"
    title: "xinrongzhang2022/InfiniteBench dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenBMB/InfiniteBench/blob/main/src/compute_scores.py"
    title: "OpenBMB/InfiniteBench reference scoring implementation (compute_scores.py)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/infinite_bench_en_sum_scenario.py"
    title: "HELM infinite_bench_en_sum scenario implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/long_context_run_specs.py"
    title: "HELM long_context_run_specs.py (infinite_bench_en_sum run spec and metrics)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/infinitebench/infinitebenchensum/infinitebench_ensum_gen_cfbc08.py"
    title: "OpenCompass infinitebench_ensum dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [∞Bench (InfiniteBench)](infinitebench.md) family.

## What it measures

Given a full English novel (averaging about 103,500 tokens, the shortest context of ∞Bench's three English
book tasks), the model must produce a concise summary, capped at 1,200 output tokens in the reference
setup. Reference summaries are sourced from the web and manually filtered, then, like the other English
book tasks, subjected to key-entity replacement to reduce the chance a model recognises the specific book
from pretraining alone. Unlike En.MC and En.QA, which test locating and combining specific facts, En.Sum
tests whether a model can compress a whole long document rather than retrieve isolated details from it.

## Reading the numbers

A ROUGE-L-Sum score here reflects lexical overlap with one reference summary, not an independent judgement
of quality -- a genuinely good summary phrased differently from the reference can still score low, and the
uniformly low 2024 baselines (all under 18) are as much a property of this metric against a single
reference as of the models' summarisation ability. Treat En.Sum as complementary to En.MC and En.QA rather
than a replacement: it tests whether a model can compress a whole long document, while the other two test
whether it can retrieve and combine specific facts from one. Read it alongside those splits on the
[∞Bench](infinitebench.md) family page, and note that the family page's contamination and
current-leaderboard caveats apply here too.
