---
id: infinite_bench_en_qa
name: "∞Bench: En.QA (English Question Answering)"
page_kind: subset
category: long-context
subcategory: "long-document open-ended question answering over English novels"
status: active
summary: "∞Bench's open-ended English QA split: answer a free-text question after reading a novel averaging around 193K tokens, scored by token-level F1 against the reference answer."
measures: >
  Given a full English novel (averaging about 192,600 tokens of context) and a question that requires
  aggregating scattered details (for example, a running total) or filtering out one specific fact among
  many similar candidates, the model produces a short free-text answer rather than choosing among options,
  as En.MC does. Questions come from the same human annotation pipeline as En.MC, and the reference prompt
  instructs the model to answer concisely, so the task combines long-range retrieval-and-reasoning with the
  separate demand of producing a short, precisely matched answer rather than a discursive one.
task_format: >
  Open-ended, free-text question answering over a long document, with generation capped at a short number
  of output tokens; scored automatically against a reference answer rather than by an LLM judge.
metric:
  name: "F1 (token-level, SQuAD-style, against the reference answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    No random baseline applies to free-text F1 scoring. The reference implementation takes the best F1
    across the recorded ground-truth answer(s) for each question. No human baseline is established here.
dataset:
  size: 351
  size_note: >
    351 examples, averaging about 192,600 input tokens and 4.8 output tokens, per the ∞Bench paper's Table
    2 -- the longest average input context of the three English book tasks. Human-annotated, from the same
    pool of modified English novels as En.MC and En.Sum. Hugging Face split name longbook_qa_eng, within
    the shared xinrongzhang2022/InfiniteBench dataset.
  url: "https://huggingface.co/datasets/xinrongzhang2022/InfiniteBench"
  license: "MIT, per the OpenBMB/InfiniteBench GitHub repository; see the infinitebench family page."
  languages:
    - en
  modalities:
    - text
  splits: "longbook_qa_eng: 351 examples, single evaluation split (no train/validation)"
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
  top_score: 22.22
  as_of: "2024-02"
  note: >
    At release, GPT-4 led this specific task with an F1 of 22.22, ahead of Kimi-Chat (16.52), Claude 2
    (11.97) and YaRN-Mistral-7B-128K (9.55) -- far below the ceiling implied by max_score 100, and the
    lowest-scoring of the three English book tasks for every model tested, consistent with open-ended
    generation being harder to score well on than multiple-choice or ROUGE-scored summarisation. As with
    the infinitebench family page, this pass found no independently maintained current leaderboard, so
    today's standing on this specific split is not established.
contamination:
  risk: medium
  note: >
    The underlying novels are real published books plausibly already present in pretraining corpora
    independent of this benchmark, but the specific questions and reference answers are ∞Bench's own human
    annotations, public without gating since February 2024. No source read for this page states a measured
    contamination rate.
harness:
  helm: "infinite_bench_en_qa"
  opencompass: "InfiniteBench_enqa"
  other: >
    OpenCompass scores this task with a dedicated LongBenchF1Evaluator. HELM applies its general-purpose
    open-ended-generation metric bundle (exact match, quasi-exact match, F1, ROUGE-L, BLEU-1, BLEU-4) via
    its run spec rather than naming one metric in the scenario code itself, unlike En.MC and En.Sum, whose
    scenario classes each declare a single main_metric. Both harnesses cap generation at 40 output tokens,
    matching the paper's own decoding cap for this task.
tags:
  - long-context
  - question-answering
  - retrieval
  - reasoning
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
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/infinite_bench_en_qa_scenario.py"
    title: "HELM infinite_bench_en_qa scenario implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/long_context_run_specs.py"
    title: "HELM long_context_run_specs.py (infinite_bench_en_qa run spec and metrics)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/infinitebench/infinitebenchenqa/infinitebench_enqa_gen_a1640c.py"
    title: "OpenCompass infinitebench_enqa dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [∞Bench (InfiniteBench)](infinitebench.md) family.

## What it measures

Given a full English novel (averaging about 192,600 tokens, the longest context of ∞Bench's three English
book tasks) and a question requiring aggregation of scattered details or filtering out one fact among
similar candidates, the model must produce a short free-text answer -- not pick from options, as En.MC
does. Questions share En.MC's annotation pipeline, and the reference prompt asks for a concise answer, so
the task tests both finding the right information across a long document and stating it precisely rather
than embedding it in a longer response.

## Reading the numbers

A high En.QA F1 shows a model can both locate scattered or filtered facts across a long document and phrase
a short answer matching a reference closely enough for token-level F1 to reward it -- a harder combination
than En.MC's multiple-choice version of the same retrieval task, which is why even the strongest 2024
baselines scored roughly a third as high here as on En.MC. Because F1 compares surface tokens rather than
meaning, a correct answer phrased very differently from the reference can still score poorly, so a low
number does not always mean the model missed the fact. Read it alongside En.MC and En.Sum on the
[∞Bench](infinitebench.md) family page rather than alone, since the three English book tasks probe the same
skill through different formats.
