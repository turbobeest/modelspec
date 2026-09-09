---
id: xstorycloze
name: XStoryCloze
aliases: []
page_kind: benchmark
category: reasoning
subcategory: commonsense story-ending selection
status: active
summary: XStoryCloze translates the English StoryCloze validation set into 10 languages, testing commonsense selection of a story's correct ending.
measures: XStoryCloze tests commonsense narrative understanding across languages. Given a four-sentence story, the model must pick which of two possible one-sentence endings is the coherent continuation, using the same stories translated into 11 languages so results can be compared across them.
task_format: Binary choice; given a four-sentence story context, pick which of two candidate final sentences is the coherent ending.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 50, human_baseline: null, baseline_note: "Two-way forced choice, so random guessing scores 50%."}
dataset: {size: 20581, size_note: "11 languages (English plus 10 translations), each with 360 examples reserved for few-shot exemplars and 1,510 for evaluation, aligned line-by-line across languages; ~20,581 rows total.", url: "https://huggingface.co/datasets/juletxara/xstory_cloze", license: "CC BY-SA 4.0", languages: [en, ru, zh, es, ar, hi, id, te, sw, eu, my], modalities: [text], splits: "360 few-shot exemplars + 1,510 evaluation examples per language", public_test_set: true}
publisher: {org: "Meta AI (FAIR)", authors: ["Xi Victoria Lin", "and co-authors"], url: "https://github.com/facebookresearch/fairseq/blob/main/examples/xglm/README.md"}
paper: {title: "Few-shot Learning with Multilingual Language Models", arxiv: "2112.10668", url: "https://arxiv.org/abs/2112.10668", year: 2022}
leaderboard_url: ""
repo_url: https://github.com/facebookresearch/fairseq/tree/main/examples/xglm
released: "2022"
last_updated: ""
lineage: {family: "", predecessor: "storycloze", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "Given the two-way forced-choice format and the known ease of the original English StoryCloze task for strong models, scores are likely to sit well above the 50% random baseline for current frontier models, but this was not confirmed against a leaderboard here."}
contamination: {risk: medium, note: "The English StoryCloze validation set has circulated publicly since 2016 and the XStoryCloze translations since 2021-2022, so both are plausible training-data inclusions for models released after those dates."}
harness: {lm_eval: xstorycloze}
tags: [benchmark, multilingual, commonsense, reasoning]
sources:
  - url: https://arxiv.org/abs/2112.10668
    title: "Few-shot Learning with Multilingual Language Models"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/juletxara/xstory_cloze
    title: XStoryCloze dataset card
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/xstorycloze/README.md
    title: lm-evaluation-harness xstorycloze task README
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-002"}
---
## What it measures

XStoryCloze tests commonsense narrative understanding across languages: given a four-sentence story, the model must pick which of two possible one-sentence endings is the coherent continuation. It is a professional translation of the English StoryCloze validation set (Spring 2016 version) into 10 additional languages, so the same underlying stories and endings can be compared language to language rather than testing different content per language.

## How it is scored

Each item is a two-way forced choice, so a model that always guesses scores 50% accuracy. Models are typically scored zero- or few-shot by comparing the log-likelihood assigned to the story followed by each candidate ending and picking the higher-scoring one, rather than by free generation. Scores are reported per language and often averaged across all 11 (English plus 10 translations).

## Dataset and licence

XStoryCloze covers 11 languages: English, Russian, Simplified Chinese, Latin American Spanish, Arabic, Hindi, Indonesian, Telugu, Swahili, Basque and Burmese. Each language has 360 examples reserved for few-shot exemplars and 1,510 for evaluation, aligned line-by-line across languages, for roughly 20,581 rows in total across all languages and splits. It is released under CC BY-SA 4.0, matching the licence of the original English StoryCloze dataset it translates.

## Who publishes it

XStoryCloze was released by Meta AI's FAIR team alongside "Few-shot Learning with Multilingual Language Models" (Xi Victoria Lin et al., EMNLP 2022; arXiv:2112.10668, first posted December 2021), the paper introducing the XGLM model. It is distributed through the fairseq XGLM examples and mirrored on Hugging Face.

## Lineage

XStoryCloze is a direct multilingual translation of `storycloze` (the English Story Cloze Test), so that page is its predecessor. It belongs to a family of translated-benchmark suites released for multilingual evaluation, alongside sets such as XNLI and XCOPA, but is not itself a family page for other subset ids in this repository. No successor benchmark under a different id was established from the sources reviewed here.

## Saturation and contamination

No saturation study was reviewed here, so status is unknown; given the two-way forced-choice format and the well-known ease of the original English StoryCloze task for strong models, scores are likely to sit well above the 50% random baseline for current frontier models, but this was not directly confirmed from a leaderboard. Contamination risk is medium: the English StoryCloze validation set has circulated publicly since 2016 and the XStoryCloze translations since 2021-2022, so both are plausible training-data inclusions for models released after those dates.

## How to run it

lm-evaluation-harness implements XStoryCloze as an `xstorycloze` group with one subtask per language: `xstorycloze_ar`, `xstorycloze_en`, `xstorycloze_es`, `xstorycloze_eu`, `xstorycloze_hi`, `xstorycloze_id`, `xstorycloze_my`, `xstorycloze_ru`, `xstorycloze_sw`, `xstorycloze_te`, `xstorycloze_zh`, matching all 11 released languages. Report the shot count and whether scoring used likelihood comparison versus generation, since the two approaches are not directly comparable.

## Reading the numbers

A high XStoryCloze score indicates a model can track simple everyday narrative causality and pick the more plausible ending, in the target language, from a two-way choice — a fairly easy task for strong models, so ceiling effects are plausible even though this was not confirmed against a leaderboard here. Because it is binary choice, small score differences can reflect noise more than in tasks with lower random baselines. Compare only same-language, same-shot-count scores, and treat very high uniform scores across all 11 languages with some caution given the age and public availability of the source data.
