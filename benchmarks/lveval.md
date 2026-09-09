---
id: lveval
name: "LV-Eval"
aliases: ["LVEval", "LV-Eval: A Balanced Long-Context Benchmark with 5 Length Levels Up to 256K"]
page_kind: benchmark
category: long-context
subcategory: "bilingual long-context QA with confusion injection and keyword-recall scoring, five length levels to 256k words"
status: active
summary: "A bilingual long-context QA benchmark with 11 datasets at five length levels from 16k to 256k words, built to fight knowledge leakage with confusing-fact insertion and keyword-recall metrics."
measures: >
  LV-Eval gives a model a long bilingual (English/Chinese) document, built by mixing real supporting
  passages with distracting ones, and asks a single-hop or multi-hop question over it. It spans 11
  datasets -- six single-hop (including a fact-recall pressure test styled on needle-in-a-haystack)
  and five multi-hop, several adapted from sources such as LooGLE, HotpotQA-derived data, CMRC and
  DuReader -- each rendered at five length levels (16k, 32k, 64k, 128k, 256k words) using the same
  underlying question-answer pairs, so a model's degradation curve across lengths can be measured
  directly rather than compared across different questions. Most datasets additionally insert
  GPT-4-generated, human-revised "confusing facts" into the context and apply keyword-and-phrase
  replacement, so a model must reason from the given text rather than lean on memorized or
  common-sense knowledge, which the authors argue inflates scores on benchmarks built from
  unaltered public documents.
task_format: >
  A long document (16k-256k words) mixing supporting and distracting passages, sometimes with
  inserted confusing facts, plus a single-hop or multi-hop question; a short free-form answer out,
  evaluated with greedy decoding. Ten of the 11 datasets are scored with a two-stage keyword-recall
  metric built from manually annotated answer keywords and a blacklist of non-informative words;
  the remaining two (cmrc-mixup, dureader-mixup) use a plain F1 or ROUGE-L variant with the same
  word blacklist.
metric:
  name: "keyword-recall-based F1 (most datasets), F1 with word blacklist (cmrc-mixup), or ROUGE-L with word blacklist (dureader-mixup); averaged per length level and across datasets"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    LV-Eval does not establish a fixed random-guess or human baseline; it is designed instead for
    relative, controlled comparison of the same model across its five length levels and against
    other evaluated models. The paper's own reference points are other LLMs: at release, the
    strongest 2023-era open model tested, ChatGLM3-6B-32k, scored 30.70% at the easiest (16k) level,
    falling to 7.17% at 256k.
dataset:
  size: 8645
  size_note: >
    11 datasets share 1,331 unique question-answer pairs (596 single-hop, 735 multi-hop), each
    rendered as a separate graded context at all five length levels, for 8,645 total test instances
    (summed directly from the per-dataset context counts the authors publish). The two fact-recall
    datasets (factrecall-en, factrecall-zh) hold only one QA pair each, repeated across 200
    differently arranged contexts per length level, as a dedicated "needle in a haystack" pressure
    test. The Hugging Face dataset card's own description text says "12 finegrained tasks," but only
    11 are named in the paper, in the README's task tables, and as ZIP files in the repository; that
    description text appears to be an error in the card rather than a 12th task this page could
    locate.
  url: "https://huggingface.co/datasets/Infinigence/LVEval"
  license: "MIT for the code and packaging (GitHub LICENSE file and the Hugging Face license tag); the GitHub repository also ships a separate LICENSE_CC file (CC BY-SA 4.0) without stating which of the two covers the released data itself versus the evaluation code."
  languages: ["en", "zh"]
  modalities: ["text"]
  splits: "test only, no train/validation split; each of the 11 datasets is pre-split into five length-level variants (e.g. hotpotwikiqa_mixup_16k ... _256k)"
  public_test_set: true
publisher:
  org: "Tsinghua University; Infinigence-AI; Shanghai Jiao Tong University; The Chinese University of Hong Kong; Shanghai Artificial Intelligence Laboratory"
  authors: ["Tao Yuan", "Xuefei Ning", "Dong Zhou", "Zhijie Yang", "Shiyao Li", "Minghui Zhuang", "Zheyue Tan", "Zhuyu Yao", "Dahua Lin", "Boxun Li", "Guohao Dai", "Shengen Yan", "Yu Wang"]
  url: "https://github.com/infinigence/LVEval"
paper:
  title: "LV-Eval: A Balanced Long-Context Benchmark with 5 Length Levels Up to 256K"
  arxiv: "2402.05136"
  url: "https://arxiv.org/abs/2402.05136"
  year: 2024
leaderboard_url: "https://github.com/infinigence/LVEval"
repo_url: "https://github.com/infinigence/LVEval"
released: "2024-02"
last_updated: "2024-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Not saturated. The originally published (2024) reference table shows every 7B-scale model well
    below 50% even at the easiest 16k level, falling into single digits by 256k. The paper's most
    recent text revision (v3, Oct 2025, per arXiv's own revision history) reports a wider 15-model
    sweep including Moonshot-v1-128k, Qwen2.5-72B-Instruct and Llama-3.1-70B-Instruct, stating that
    "both Qwen2.5-72B and Moonshot-v1 obtain average scores exceeding 40 at 16k and 32k lengths" --
    still well short of a ceiling, and this page could not locate an exact top-score figure for that
    expanded run, only this qualitative statement, so top_score is left unset rather than estimated.
    The GitHub repository itself has not been pushed to since August 2024, so this newer 15-model
    comparison exists only in the revised paper text, not as a rerunnable reference table.
contamination:
  risk: low
  note: >
    LV-Eval was built specifically to reduce two contamination-adjacent problems the authors call
    "knowledge leakage": documents mixing in confusing, GPT-4-generated facts and keyword/phrase
    replacement in both context and answers are meant to force reliance on the given text rather
    than on facts a model may already know from pretraining. That said, several source datasets
    (LooGLE, HotpotQA-derived data, CMRC, DuReader) are themselves older public benchmarks, and the
    full LV-Eval test set and its answers have been public and downloadable since February 2024 with
    no held-out portion, so exact-instance memorization by a model trained afterward is possible even
    though the authors' mitigations target a different, subtler leakage problem.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "lveval (per-dataset configs under opencompass/configs/datasets/lveval/, e.g. lvevalhotpotwikiqa_mixup, lvevalfactrecall_en; no lm-evaluation-harness, inspect_evals or HELM implementation was found during this research)"
  bigbench: ""
  other: "The authors' own prediction.py / evaluation.py scripts in infinigence/LVEval are the reference implementation, with batch shell scripts for data-parallel or single-GPU evaluation and a separate script for API-based commercial models."
tags: ["long-context", "bilingual", "question-answering", "multi-hop", "needle-in-a-haystack", "knowledge-leakage", "keyword-recall"]
sources:
  - url: "https://arxiv.org/abs/2402.05136"
    title: "LV-Eval: A Balanced Long-Context Benchmark with 5 Length Levels Up to 256K (Yuan et al., arXiv:2402.05136)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.05136"
    title: "LV-Eval, full text (ar5iv, reflecting the Oct 2025 v3 revision)"
    accessed: "2026-09-08"
  - url: "https://github.com/infinigence/LVEval"
    title: "infinigence/LVEval GitHub repository (README, LICENSE, LICENSE_CC, evaluation scripts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Infinigence/LVEval"
    title: "Infinigence/LVEval dataset card and API metadata, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/lveval"
    title: "OpenCompass lveval dataset configs (11 per-dataset subdirectories)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LV-Eval gives a model a long bilingual (English or Chinese) document, assembled by mixing real
supporting passages with distracting ones, and asks a single-hop or multi-hop question over it. It
spans 11 datasets -- six single-hop, including a fact-recall pressure test styled on
needle-in-a-haystack, and five multi-hop -- several adapted from earlier sources such as LooGLE,
HotpotQA-derived data, CMRC and DuReader. Each of the 11 datasets is rendered at five length levels
(16k, 32k, 64k, 128k and 256k words) using the same underlying question-answer pairs, so a model's
degradation curve across lengths can be measured directly rather than inferred by comparing
different questions at different lengths.

Most datasets also insert GPT-4-generated, human-revised "confusing facts" into the context and
apply keyword-and-phrase replacement to both the context and the reference answers. Both techniques
are meant to force a model to reason from the given text rather than lean on memorized or
common-sense knowledge, which the authors argue inflates scores on long-context benchmarks built
from unaltered public documents.

## How it is scored

Ten of the 11 datasets use a two-stage, keyword-recall-based metric: manually annotated "answer
keywords" (the critical words or phrases in the reference answer) must be recalled above a
threshold before a second stage removes blacklisted, non-informative words and computes F1 against
the remaining text. The two exceptions, cmrc-mixup and dureader-mixup, use a plain F1 or ROUGE-L
score with the same word blacklist but no keyword-recall gate, because their reference answers are
already concise or already long-form respectively. There is no single fixed random or human
baseline; the benchmark is built for controlled comparison of a model against itself across the
five length levels and against other evaluated models, not against an absolute ceiling.

## Dataset and licence

The 11 datasets share 1,331 unique question-answer pairs (596 single-hop, 735 multi-hop), each
rendered as a graded context at all five length levels, for 8,645 total test instances by this
page's count of the authors' published per-dataset context totals. The two fact-recall datasets
hold just one QA pair each, repeated across 200 differently arranged contexts per length level as a
dedicated pressure test. The GitHub repository is MIT-licensed for its code, matching the Hugging
Face dataset card's license tag, but the repository also carries a separate LICENSE_CC file (CC
BY-SA 4.0) without stating which licence governs the released data versus the evaluation scripts.
The Hugging Face card's own description text claims "12 finegrained tasks," but only 11 are named
in the paper, the README's task tables and the repository's ZIP files -- this page could not locate
a 12th task and treats that count as an error in the card.

## Who publishes it

Tao Yuan, Xuefei Ning, Dong Zhou, Zhijie Yang, Shiyao Li, Minghui Zhuang, Zheyue Tan, Zhuyu Yao,
Dahua Lin, Boxun Li, Guohao Dai, Shengen Yan and Yu Wang published LV-Eval in February 2024, with
affiliations spanning Tsinghua University, Infinigence-AI, Shanghai Jiao Tong University, The
Chinese University of Hong Kong and Shanghai Artificial Intelligence Laboratory. Infinigence-AI
hosts the reference repository and the Hugging Face dataset. The GitHub repository has not been
pushed to since August 2024, but the paper text itself was revised as recently as October 2025
(arXiv v3) to report results on a wider set of newer models, without an accompanying code or
reference-table update.

## Lineage

LV-Eval has no formal predecessor or successor tracked in this repository. Its stated motivation is
a gap in earlier long-context benchmarks, which the authors say average only 5k-21k words of context
and are vulnerable to "knowledge leakage" from unaltered, previously public source documents. This
repository separately catalogues several other long-context suites built around related but distinct
ideas -- `longbench` and `longbenchv2` (bilingual and English long-context suites from a different,
Tsinghua/Zhipu.AI-led team), `infinitebench` (English/Chinese, pushing past 100K tokens with a
different 12-task mix) and `ruler` (NVIDIA's length-controllable synthetic suite) -- none of which
shares data, authorship or its specific confusing-fact-insertion technique with LV-Eval.

## Saturation and contamination

LV-Eval is not saturated. The originally published 2024 reference table shows every evaluated
7B-scale model well below 50% even at the easiest 16k level, falling into single digits by 256k. The
paper's October 2025 text revision reports a wider 15-model sweep adding Moonshot-v1-128k,
Qwen2.5-72B-Instruct and Llama-3.1-70B-Instruct, stating these newer, larger models "obtain average
scores exceeding 40 at 16k and 32k lengths" -- still well short of a ceiling, though this page could
not locate an exact figure for that run beyond this qualitative statement. Contamination risk is
assessed as low: the benchmark's confusing-fact insertion and keyword replacement are specifically
designed to blunt reliance on memorized or common-sense knowledge, though several of its source
datasets are older public benchmarks in their own right, and the full LV-Eval test set has been
public since February 2024 with no held-out portion.

## How to run it

OpenCompass ships all 11 datasets as separate per-dataset configs under
`opencompass/configs/datasets/lveval/` (for example `lvevalhotpotwikiqa_mixup`,
`lvevalfactrecall_en`), aggregated into a single `LVEval_datasets` list; no lm-evaluation-harness,
inspect_evals or HELM implementation was found during this research. The authors' own
`prediction.py` and `evaluation.py` scripts in infinigence/LVEval remain the reference
implementation, with batch shell scripts for data-parallel local evaluation and a separate script
for API-based commercial models such as GPT-4. Because the keyword-recall metric depends on manually
annotated answer keywords and a word blacklist rather than plain string overlap, and because model
context windows shorter than the target length force middle-truncation, reported scores can be
sensitive to how a given harness handles truncation and answer-keyword matching even at the same
nominal length.

## Reading the numbers

A strong LV-Eval score, especially one that holds up at 128k-256k rather than only at 16k-32k, is
comparatively good evidence a model can actually use a long context under adversarial conditions --
distractor passages, inserted confusing facts and knowledge-leakage mitigations all working against
simple retrieval or memorization. Because scores are reported per length level and blend a
keyword-recall metric that differs from plain F1 or ROUGE-L, always check which length level and
which underlying metric produced a given number before comparing it across models or against another
long-context benchmark. A model's degradation curve across the five lengths, not just its score at
one length, is the more informative signal LV-Eval is built to expose.
