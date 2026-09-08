---
id: xcopa
name: "XCOPA"
aliases: ["Cross-lingual Choice of Plausible Alternatives"]
page_kind: benchmark
category: reasoning
subcategory: "cross-lingual causal commonsense reasoning (COPA-style)"
status: active
summary: "XCOPA translates and re-annotates the English COPA causal-reasoning test into 11 typologically diverse languages, to measure zero-shot cross-lingual transfer of commonsense reasoning."
measures: >
  XCOPA tests causal commonsense reasoning in the COPA format: a model reads a one-sentence premise, is
  told whether it needs the cause or the result, and must pick which of two alternative sentences is more
  plausible. What XCOPA adds to plain COPA is language coverage -- the same premise-and-alternatives
  format, translated and re-annotated by native speakers into 11 typologically diverse languages
  (Estonian, Haitian Creole, Indonesian, Italian, Eastern Apurímac Quechua, Swahili, Tamil, Thai, Turkish,
  Vietnamese and Mandarin Chinese), spanning 11 language families and several world regions. Because
  XCOPA ships no training data of its own, it is designed to be used as a zero-shot cross-lingual transfer
  test: a system is typically trained or fine-tuned on English resources (the original English COPA,
  sometimes alongside Social IQa) and then evaluated directly on each of the 11 target languages, so a
  score reflects both commonsense-reasoning ability and how well that ability transfers out of English.
task_format: >
  Two-choice, single-turn: given a premise sentence and a prompt indicating cause or result, the model
  selects the more plausible of two alternative sentences, in the target language. No free-text
  generation or explanation is required.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 97.6
  baseline_note: >
    Binary choice gives a 50% random baseline. The original paper's own human evaluation, reported on
    the maintainers' GitHub leaderboard, averaged 97.60% across all 11 languages (individual languages
    ranging from 94.8% on Quechua to 100.0% on Indonesian), which is the benchmark's practical ceiling.
    Scores are usually reported per language and as a cross-language average; a single blended average
    can hide large per-language gaps, particularly for the least-resourced languages in the set (see
    Reading the numbers).
dataset:
  size: 6600
  size_note: >
    6,600 instances: 11 languages x 600 items each (100 validation, 500 test), confirmed directly from
    the Hugging Face datasets-server split sizes for cambridgeltl/xcopa. XCOPA provides no training
    split of its own -- it is built by translating and re-annotating only the validation and test
    portions of the original English COPA, specifically so it can be used to test zero-shot transfer
    from a model trained on English (or another) data rather than trained on XCOPA itself. A separate
    set of "translate-test" configs (machine-translated English versions of 10 of the 11 languages,
    excluding Quechua) is also distributed, for translate-then-classify baselines rather than as part
    of the core cross-lingual test.
  url: "https://huggingface.co/datasets/cambridgeltl/xcopa"
  license: "CC BY 4.0"
  languages: ["et", "ht", "id", "it", "qu", "sw", "ta", "th", "tr", "vi", "zh"]
  modalities: ["text"]
  splits: "validation (100/language) and test (500/language); no training split"
  public_test_set: true
publisher:
  org: "Language Technology Lab, University of Cambridge, with University of Mannheim"
  authors: ["Edoardo M. Ponti", "Goran Glavaš", "Olga Majewska", "Qianchu Liu", "Ivan Vulić", "Anna Korhonen"]
  url: "https://github.com/cambridgeltl/xcopa"
paper:
  title: "XCOPA: A Multilingual Dataset for Causal Commonsense Reasoning"
  arxiv: "2005.00333"
  url: "https://arxiv.org/abs/2005.00333"
  year: 2020
leaderboard_url: "https://github.com/cambridgeltl/xcopa#leaderboard"
repo_url: "https://github.com/cambridgeltl/xcopa"
released: "2020-05"
last_updated: "2021-02"
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
    No current, actively maintained leaderboard reflecting modern LLMs was found -- the maintainers'
    own GitHub leaderboard has not been updated since February 2021 and points to a Papers with Code
    page that no longer serves an independent XCOPA leaderboard, so top_score is left unset rather than
    guessed. What that stale leaderboard does show, from the original paper's own baselines, is a wide
    gap between human performance (97.60% average) and the strongest model it tested, XLM-R Large, at
    68.69% average zero-shot (with a translate-test RoBERTa Large baseline at 76.05% and a MAD-X Base
    baseline at 60.94%) -- a roughly 20-30 point gap to humans that was clearly open, not saturated, as
    of 2020. No source read during this research gave a 2025-2026 frontier-model score.
contamination:
  risk: high
  note: >
    The full validation and test sets, in all 11 languages, have been public under CC BY 4.0 since 2020
    and are widely mirrored (Hugging Face, lm-evaluation-harness, OpenCompass, and the maintainers' own
    GitHub repository), with no private held-out portion. Over five years of public exposure by the time
    of this research pass makes it plausible that current pretraining corpora, especially for the
    higher-resource languages in the set (Italian, Chinese, Vietnamese, Indonesian, Turkish), include
    this exact test data.
harness:
  lm_eval: "xcopa (per-language default_<lang>.yaml configs grouped under the xcopa tag)"
  inspect_evals: ""
  helm: ""
  opencompass: "XCOPA"
  bigbench: ""
  other: "Reference data and the original leaderboard live at github.com/cambridgeltl/xcopa; loadable via Hugging Face Datasets as cambridgeltl/xcopa."
tags: ["reasoning", "commonsense", "cross-lingual", "multilingual", "copa", "multiple-choice", "zero-shot-transfer"]
sources:
  - url: "https://arxiv.org/abs/2005.00333"
    title: "XCOPA: A Multilingual Dataset for Causal Commonsense Reasoning (Ponti et al., 2020)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2005.00333"
    title: "XCOPA paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/cambridgeltl/xcopa"
    title: "cambridgeltl/xcopa repository -- languages table, examples, leaderboard, licence"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cambridgeltl/xcopa"
    title: "cambridgeltl/xcopa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=cambridgeltl/xcopa"
    title: "cambridgeltl/xcopa split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/xcopa"
    title: "lm-evaluation-harness xcopa task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

XCOPA tests causal commonsense reasoning in 11 languages at once, using the same task English-only COPA
set: given a one-sentence premise and a prompt asking for its cause or result, pick the more plausible of
two alternative sentences ("The girl found a bug in her cereal" -> result: "She poured milk in the bowl"
versus "She lost her appetite"). XCOPA's contribution is translating and re-annotating COPA's validation
and test items, by a native speaker per language, into Estonian, Haitian Creole, Indonesian, Italian,
Eastern Apurímac Quechua, Swahili, Tamil, Thai, Turkish, Vietnamese and Mandarin Chinese -- 11 languages
chosen for typological diversity rather than for being the world's most widely spoken. Because it ships
no training data of its own, it is meant to be run zero-shot: a system trained on English commonsense
data is evaluated directly against each target language, so the score mixes whether the model can reason
about cause and effect at all, and whether that reasoning survives being applied in an untrained-for
language.

## How it is scored

Plain two-way accuracy: each item has exactly one correct alternative, with no partial credit. Binary
choice gives a 50% random baseline. The paper's own human evaluation reached 97.60% averaged across the
11 languages, ranging from 94.8% (Quechua) to a perfect 100.0% (Indonesian), and is the closest thing this
benchmark has to a ceiling. Two evaluation protocols are common: "zero-shot transfer," where a
multilingual model is fine-tuned only on English data (COPA, sometimes with Social IQa added) and
evaluated directly in each target language, and "translate-test," where the target-language input is
machine-translated into English first and scored with an English-only model. The two are not directly
comparable, since translate-test performance is bounded by machine-translation quality rather than purely
by the model's own multilingual reasoning.

## Dataset and licence

6,600 items total: 11 languages, each with 100 validation and 500 test instances and no training split,
confirmed from the Hugging Face datasets-server's per-config split sizes. The dataset is released under a
CC BY 4.0 licence. Inter-translator agreement (Fleiss' kappa) was 0.921 on validation and 0.911 on test,
which the authors report as evidence the translations preserved the intended causal relationship rather
than drifting during adaptation. A separate machine-translated "translate-test" version of 10 of the 11
languages (all but Quechua) is also distributed, for the translate-then-classify baseline above.

## Who publishes it

XCOPA comes from Edoardo M. Ponti, Goran Glavaš, Olga Majewska, Qianchu Liu, Ivan Vulić and Anna Korhonen,
based at the University of Cambridge's Language Technology Lab (with a Mannheim contribution from Glavaš),
and was published at EMNLP 2020. The authors continue to host the reference dataset, examples and a
community leaderboard at github.com/cambridgeltl/xcopa, though that leaderboard has not been updated
since February 2021.

## Lineage

XCOPA is a direct multilingual extension of the original English COPA (Choice of Plausible Alternatives,
Roemmele et al. 2011), which is not separately catalogued in this repository; XCOPA reuses COPA's exact
task format and simply translates and re-annotates COPA's validation and test items rather than
introducing a new task design. It has no successor benchmark catalogued here, though it sits alongside a
broader wave of "X"-prefixed cross-lingual transfer benchmarks built the same way (translating an English
task into many languages) that this repository does not yet catalogue under this id's family.

## Saturation and contamination

No actively maintained leaderboard reflecting current models was found -- the authors' own leaderboard on
GitHub is unchanged since February 2021. The historical record shows a substantial, clearly unsaturated
gap as of 2020: human performance averaged 97.60%, while the paper's strongest tested model, XLM-R Large,
reached 68.69% zero-shot (translate-test RoBERTa Large scored 76.05%, MAD-X Base 60.94%). No 2025-2026
frontier-model score was confirmed for this page, so a current saturation state is not established.
Contamination risk is high: the full test set, in all 11 languages, has been public and unchanged for
more than five years and is widely mirrored across major evaluation harnesses.

## How to run it

lm-evaluation-harness implements per-language configs (`default_et.yaml` through `default_zh.yaml`)
grouped under the `xcopa` tag, so a run can target one language or the full set. OpenCompass registers it
as `XCOPA`. The reference data and original baseline implementations are in the authors'
github.com/cambridgeltl/xcopa repository, and the dataset loads directly through Hugging Face Datasets.
No HELM, Inspect Evals or BIG-bench implementation was confirmed during this research. Because zero-shot
transfer and translate-test are different protocols with different ceilings, check which one a reported
score used, and check whether a result is a single-language or an 11-language-average figure, before
comparing across sources.

## Reading the numbers

A high XCOPA average shows a model's commonsense-reasoning ability transfers well beyond English into
typologically distant languages -- a meaningfully harder claim than doing well on English COPA alone,
since the model must handle both the reasoning task and the language shift together. Because performance
varies substantially by language (the paper's own baselines show much lower scores on Quechua, the
benchmark's lowest-resource language, than on higher-resource languages like Chinese or Italian), a strong
overall average can still hide weak performance on specific, typically lower-resource languages, so check
the per-language breakdown rather than relying on the blended figure alone. XCOPA measures reasoning
transfer specifically -- it does not test generation, dialogue, or any skill beyond picking between two
short alternatives.
