---
id: infinite_bench_en_mc
name: "∞Bench: En.MC (English Multiple-Choice)"
page_kind: subset
category: long-context
subcategory: "long-document multiple-choice question answering over English novels"
status: active
summary: "∞Bench's English multiple-choice split: pick the correct answer among four options after reading a novel averaging around 184K tokens, testing aggregation and filtering, not just retrieval."
measures: >
  Given a full English novel (averaging about 184,400 tokens of context) and a question that requires
  locating and combining information spread across the book, the model picks one of four answer options;
  annotators were instructed to write challenging, plausible distractors. Questions follow the same
  annotation pipeline as En.QA, split into two reasoning styles: aggregation (compiling scattered details,
  such as a running total) and filtering (picking out one specific detail among many similar candidates,
  such as what a character wore at a particular point in the story). Because the answer is chosen from four
  given options rather than freely generated, En.MC isolates whether a model can find and combine the right
  long-range information without also being penalised for open-ended answer phrasing.
task_format: >
  Four-option multiple-choice question answering over a long document; the model's free-text response is
  parsed for a single letter (A-D) and compared against the labelled option, functioning as an
  exact-match/accuracy score rather than a log-likelihood comparison.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: >
    25% is the four-option random-guess rate. The reference implementation extracts an A-D letter from the
    model's generated text (falling back to phrase matching such as "answer is") rather than comparing
    token log-likelihoods, so a model that fails to follow the answer format can score below chance. No
    human baseline is established here.
dataset:
  size: 229
  size_note: >
    229 examples, averaging about 184,400 input tokens and 5.3 output tokens, per the ∞Bench paper's Table
    2. Human-annotated, drawn from the same pool of modified English novels as En.QA and En.Sum. Hugging
    Face split name longbook_choice_eng, within the shared xinrongzhang2022/InfiniteBench dataset.
  url: "https://huggingface.co/datasets/xinrongzhang2022/InfiniteBench"
  license: "MIT, per the OpenBMB/InfiniteBench GitHub repository; see the infinitebench family page."
  languages:
    - en
  modalities:
    - text
  splits: "longbook_choice_eng: 229 examples, single evaluation split (no train/validation)"
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
  top_score: 72.49
  as_of: "2024-02"
  note: >
    At release, Kimi-Chat led this specific task at 72.49%, ahead of GPT-4 (67.25%), Claude 2 (62.88%) and
    YaRN-Mistral-7B-128K (27.95%) -- a wide spread, and meaningfully higher than the ∞Bench 12-task average
    for every model, since the four-option format gives a coarser, easier-to-partially-solve signal than
    open-ended tasks like En.QA. As with the infinitebench family page, this pass found no independently
    maintained current leaderboard, and long-context capability has advanced substantially since February
    2024, so today's standing on this specific split is not established.
contamination:
  risk: medium
  note: >
    The underlying novels are real published books plausibly already present in pretraining corpora
    independent of this benchmark, but the specific questions, distractor options and correct-letter
    pairing are ∞Bench's own human annotations, public without gating since February 2024. No source read
    for this page states a measured contamination rate.
harness:
  helm: "infinite_bench_en_mc"
  opencompass: "InfiniteBench_enmc"
  other: >
    HELM's scenario filters out examples whose context-plus-options word count exceeds a configurable
    budget (131,072 words by default) before scoring, so the exact instance count HELM evaluates can be
    smaller than the full 229-example set depending on that setting; "words" here is HELM's own truncation
    unit, not the token counts the paper reports. OpenCompass's config runs the full set with a 40-token
    generation cap and first-letter-option post-processing, scored by its AccEvaluator.
tags:
  - long-context
  - multiple-choice
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
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/infinite_bench_en_mc_scenario.py"
    title: "HELM infinite_bench_en_mc scenario implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/long_context_run_specs.py"
    title: "HELM long_context_run_specs.py (infinite_bench_en_mc run spec and metrics)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/infinitebench/infinitebenchenmc/infinitebench_enmc_gen_3a4102.py"
    title: "OpenCompass infinitebench_enmc dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
---

Part of the [∞Bench (InfiniteBench)](infinitebench.md) family.

## What it measures

Given a full English novel (averaging about 184,400 tokens of context) and a question requiring
information spread across the book, the model picks one of four answer options, written to be challenging
and plausible. Questions follow the same annotation pipeline as En.QA, split between aggregation (compiling
scattered details, such as a running total) and filtering (picking one detail out of several similar
candidates). Choosing among given options rather than generating free text isolates long-range
retrieval-and-reasoning from the separate skill of producing a well-formed open-ended answer.

## Reading the numbers

A high En.MC score shows a model can locate and combine facts across a genuinely long document when the
answer only has to be recognised, not composed -- an easier bar than En.QA's free-text version of the same
skill, and the 2024 baselines bear that out (the leading En.MC score was roughly three times En.QA's).
Because the reference scorer extracts an answer letter from free text, a model that answers correctly but
doesn't follow the expected format can be marked wrong, so a low score can reflect instruction-following as
much as comprehension. Read it alongside En.QA and En.Sum on the [∞Bench](infinitebench.md) family page
rather than alone, since the three English book tasks probe the same skill through different formats.
