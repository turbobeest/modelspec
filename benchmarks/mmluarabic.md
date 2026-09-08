---
id: mmluarabic
name: "MMLUArabic (AceGPT translated MMLU)"
aliases:
  - "Arabic MMLU (AceGPT)"
  - "acegpt_MMLUArabic"
page_kind: benchmark
category: knowledge
subcategory: "machine-translated English MMLU in Arabic (57 subjects)"
status: active
summary: "AceGPT's GPT-3.5-Turbo translation of English MMLU into Arabic across 57 subjects; not the native-exam ArabicMMLU suite."
measures: >
  MMLUArabic, in the OpenCompass and AceGPT sense, is English [MMLU](mmlu.md)
  machine-translated into Arabic. Each item is still a four-option academic
  question on subjects such as abstract_algebra and professional_law. AceGPT
  used Turbo (GPT-3.5-Turbo) for the translation. It measures whether MMLU
  knowledge survives that translation, not whether a model knows Arabic-only
  school content. That native-exam job is [arabic_mmlu](arabic_mmlu.md).
task_format: >
  Four-option multiple-choice in Arabic. OpenCompass reads per-subject CSVs
  with columns input, A, B, C, D, target and scores accuracy. Three configs:
  5-shot generation with first_option_postprocess over ABCD; 5-shot
  perplexity over A–D; zero-shot generation. Task abbrs are
  acegpt_MMLUArabic_{subject}.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four options, so uniform chance is 25%. The AceGPT paper's few-shot table
    reports model accuracy, not a human exam-taker baseline. OpenCompass
    AccEvaluator plus first_option_postprocess on generated runs.
dataset:
  size: null
  size_note: >
    AceGPT's evaluation table labels the set "14k Multiple-choice Questions"
    across 57 tasks. The AceGPT `MMLUArabic/test` tree lists 57 `*_test.csv`
    files whose names match English MMLU subjects; abstract_algebra_test.csv
    has 100 rows, the same as English MMLU abstract algebra. An exact pooled
    row count was not summed here. OpenCompass loads local
    `./data/MMLUArabic/{dev,test}/`.
  url: "https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/MMLUArabic"
  license: ""
  languages:
    - ar
  modalities:
    - text
  splits: "per-subject `dev` (few-shot exemplars) and `test`"
  public_test_set: true
publisher:
  org: "FreedomIntelligence / Shenzhen Research Institute of Big Data, The Chinese University of Hong Kong, Shenzhen, and King Abdullah University of Science and Technology"
  authors:
    - "Huang Huang"
    - "Fei Yu"
    - "Jianqing Zhu"
    - "Xuening Sun"
    - "Hao Cheng"
    - "Dingjie Song"
    - "Zhihong Chen"
    - "Abdulmohsen Alharthi"
    - "Bang An"
    - "Juncai He"
    - "Ziche Liu"
    - "Zhiyi Zhang"
    - "Junying Chen"
    - "Jianquan Li"
    - "Benyou Wang"
    - "Lian Zhang"
    - "Ruoyu Sun"
    - "Xiang Wan"
    - "Haizhou Li"
    - "Jinchao Xu"
  url: "https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/MMLUArabic"
paper:
  title: "AceGPT, Localizing Large Language Models in Arabic"
  arxiv: "2309.12053"
  url: "https://arxiv.org/abs/2309.12053"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/MMLUArabic"
released: "2023-09"
last_updated: ""
lineage:
  family: ""
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    AceGPT paper Table 9 few-shot: AceGPT-13B-base 37.26% on this Arabic MMLU.
    That 2023 open-model figure is not treated as a current ceiling. No later
    independent top score was confirmed here.
contamination:
  risk: high
  note: >
    The items are a public translation of already-public English MMLU, hosted
    as CSVs on GitHub since the AceGPT release. No private split is described.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MMLUArabic"
  bigbench: ""
  other: >
    OpenCompass configs: MMLUArabic_gen (5-shot generation), MMLUArabic_ppl
    (5-shot perplexity), MMLUArabic_zero_shot_gen (ZeroRetriever generation).
    Dataset class MMLUArabicDataset. Do not confuse with HELM `arabic_mmlu` or
    MBZUAI/ArabicMMLU ([arabic_mmlu](arabic_mmlu.md)). lm-eval
    `arabic_leaderboard_arabic_mmlu` loads OALL/Arabic_MMLU, which that
    leaderboard traces to this AceGPT directory.
tags:
  - arabic
  - knowledge
  - multiple-choice
  - machine-translation
  - mmlu-style
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MMLUArabic/README.md"
    title: "OpenCompass MMLUArabic README (AceGPT path, AceGPT citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MMLUArabic/MMLUArabic_gen_326684.py"
    title: "OpenCompass 5-shot gen config (57 English MMLU subjects, AceGPT abbrs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/MMLUArabic.py"
    title: "MMLUArabicDataset (dev/test CSVs, six columns)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2309.12053"
    title: "AceGPT paper (arXiv:2309.12053)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2309.12053"
    title: "AceGPT paper HTML (Turbo translation of MMLU, 14k MCQs, Table 9)"
    accessed: "2026-09-08"
  - url: "https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/MMLUArabic/test"
    title: "AceGPT MMLUArabic/test (57 subject CSVs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FreedomIntelligence/AceGPT/main/eval/benchmark_eval/benchmarks/MMLUArabic/test/abstract_algebra_test.csv"
    title: "abstract_algebra_test.csv (100 Arabic rows, four options plus letter)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MMLUArabic/MMLUArabic_ppl_d2333a.py"
    title: "OpenCompass ppl config (comment still points at Hendrycks data.tar)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MMLUArabic/MMLUArabic_zero_shot_gen_3523e0.py"
    title: "OpenCompass zero-shot gen config (ZeroRetriever, 57 subjects)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-016 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-016"
---

## What it measures

OpenCompass MMLUArabic is English [MMLU](mmlu.md) translated into Arabic. A model sees a four-option question on one of 57 MMLU subjects — abstract algebra, professional law, high-school chemistry, and the rest of Hendrycks et al.'s list — with Arabic wording and Arabic subject hints in the OpenCompass templates. AceGPT produced the translation with Turbo (GPT-3.5-Turbo). The skill under test is MMLU-style academic knowledge in Arabic, including whatever the translator got wrong.

This is not [arabic_mmlu](arabic_mmlu.md) (MBZUAI ArabicMMLU), which uses native school and professional exams from Arabic-speaking countries. It is not [mmmlu](mmmlu.md), OpenAI's professionally translated MMLU.

## How it is scored

OpenCompass reports accuracy. The 5-shot generation config asks for an Arabic "إجابة:" then takes the first ABCD letter. The perplexity config ranks A–D as continuations. A zero-shot generation config exists. Few-shot examples come from each subject's `dev` split (`FixKRetriever` ids 0–4). The AceGPT paper's Table 9 is few-shot accuracy on this translation; AceGPT-13B-base scored 37.26% there. Random chance on four options is 25%.

## Dataset and licence

The AceGPT paper's table lists "14k Multiple-choice Questions" on 57 tasks. The GitHub `MMLUArabic/test` directory lists 57 `*_test.csv` files named after English MMLU subjects. The abstract-algebra test file has 100 rows, matching English MMLU's 100-item abstract algebra test. This page does not sum every CSV. OpenCompass reads headerless six-column CSVs from `./data/MMLUArabic/`. Answers are public.

No licence file was found at the AceGPT repository root. OpenCompass's gen README points at the AceGPT directory; the perplexity config comment still says to download Hendrycks' English `data.tar`. The on-disk path in that file remains `./data/MMLUArabic/`. Treat the AceGPT CSVs as the intended data, and treat that ppl comment as a copy-paste error unless a run log shows otherwise.

## Who publishes it

Huang Huang, Fei Yu, Jianqing Zhu, Juncai He and co-authors at FreedomIntelligence, the Shenzhen Research Institute of Big Data, CUHK Shenzhen, and KAUST, in "AceGPT, Localizing Large Language Models in Arabic" (arXiv:2309.12053, 21 September 2023; v5 2 April 2024). OpenCompass hosts the harness configs. Its README citation omits Juncai He; this page follows the paper author list.

## Lineage

Predecessor: English [mmlu](mmlu.md). [arabic_mmlu](arabic_mmlu.md) is a different, natively sourced exam suite. [mmmlu](mmmlu.md) is a professional translation of MMLU into 14 languages, including Arabic, not this Turbo translation. lm-eval `arabic_leaderboard_arabic_mmlu` / OALL/Arabic_MMLU is this AceGPT translation, despite some leaderboard prose calling it native.

## Saturation and contamination

The 2023 AceGPT-13B-base figure of 37.26% is a low open-model point, not a ceiling. No later top score was confirmed here. Contamination risk is high: public CSVs of a public English benchmark, on GitHub since 2023.

## How to run it

OpenCompass dataset family `MMLUArabic`: generation (`MMLUArabic_gen`), perplexity (`MMLUArabic_ppl`), or zero-shot generation. Download CSVs from the AceGPT `MMLUArabic` directory. HELM `arabic_mmlu` is MBZUAI ArabicMMLU. There is no lm-eval task named `mmluarabic`.

Name 5-shot versus zero-shot and generation versus perplexity before comparing. Do not stack this number with [arabic_mmlu](arabic_mmlu.md) or MMMLU-ar.

## Reading the numbers

A high score means the model can answer Turbo-translated MMLU items in Arabic, including English-centric subjects such as US history. It does not measure dialect, and it does not use native Arab-world exams. Translation noise is in the labels; the AceGPT paper itself contrasts this Turbo translation with Jais's in-house translation. For Arabic knowledge that was never English MMLU, read [arabic_mmlu](arabic_mmlu.md) instead.
