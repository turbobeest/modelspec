---
id: xquad
name: XQuAD
aliases: []
page_kind: benchmark
category: knowledge
subcategory: cross-lingual extractive question answering
status: active
summary: XQuAD is a cross-lingual extractive QA benchmark of 1,190 SQuAD v1.1 question-answer pairs professionally translated into 11 languages.
measures: XQuAD tests whether a model's reading-comprehension ability transfers from English to other languages. Given a short paragraph and a question in one of 11 languages, the model must extract the exact answer span from the paragraph, the same format as SQuAD but run in parallel across languages.
task_format: Extractive question answering; given a paragraph and question, output the exact answer span from the paragraph.
metric: {name: "F1 / exact match", direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "Scored per language following the SQuAD protocol and typically averaged across the 11 languages; no single official human baseline is published."}
dataset: {size: 1190, size_note: "1,190 question-answer pairs over 240 paragraphs, entirely parallel across all 11 languages.", url: "https://github.com/google-deepmind/xquad", license: "CC BY-SA 4.0", languages: [en, es, de, el, ru, tr, ar, vi, th, zh, hi], modalities: [text], splits: "Single evaluation set per language (translated from the SQuAD v1.1 dev set); no training split is provided.", public_test_set: true}
publisher: {org: "Google DeepMind", authors: ["Mikel Artetxe", "Sebastian Ruder", "Dani Yogatama"], url: "https://github.com/google-deepmind/xquad"}
paper: {title: "On the Cross-lingual Transferability of Monolingual Representations", arxiv: "1910.11856", url: "https://arxiv.org/abs/1910.11856", year: 2019}
leaderboard_url: ""
repo_url: https://github.com/google-deepmind/xquad
released: "2019-10"
last_updated: ""
lineage: {family: "", predecessor: "squad", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: medium, note: "The underlying SQuAD v1.1 paragraphs and answers, and the XQuAD translations themselves, have been publicly posted since 2019-2020, so both the English source and the translated pairs are plausible inclusions in the training data of models released since then."}
harness: {lm_eval: xquad}
tags: [benchmark, multilingual, extractive-qa, knowledge]
sources:
  - url: https://arxiv.org/abs/1910.11856
    title: "On the Cross-lingual Transferability of Monolingual Representations"
    accessed: "2026-09-08"
  - url: https://github.com/google-deepmind/xquad
    title: XQuAD official repository
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/xquad/README.md
    title: lm-evaluation-harness xquad task README
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-002"}
---
## What it measures

XQuAD (Cross-lingual Question Answering Dataset) tests whether a model's reading-comprehension ability transfers from English to other languages. Given a short paragraph and a question in one of 11 languages, the model must extract the exact answer span from the paragraph — the same extractive-QA format as SQuAD, run in parallel across languages so the same underlying question and answer pair can be compared language to language. It is a reading-comprehension transfer test, not a translation task: the model never has to produce translated text itself.

## How it is scored

Following the SQuAD protocol, XQuAD is scored with exact match and token-level F1 between the predicted span and the gold answer, computed per language and typically averaged across all 11 to report an overall number. There are no unanswerable questions in XQuAD, unlike SQuAD 2.0, so a model cannot be scored for correctly abstaining. Zero-shot cross-lingual evaluation — fine-tune only on English SQuAD, evaluate on all 11 languages — is the setting the dataset was built for, though some papers also report translate-train or translate-test variants, which are not directly comparable to zero-shot numbers.

## Dataset and licence

The dataset is a subset of 240 paragraphs and 1,190 question-answer pairs taken from the SQuAD v1.1 development set, professionally translated into Spanish, German, Greek, Russian, Turkish, Arabic, Vietnamese, Thai, Chinese and Hindi, making the set entirely parallel across all 11 languages including the English original. It ships as a single evaluation set per language with no training split, since it is meant to test transfer from English SQuAD training rather than to be trained on itself. The official repository states a CC BY-SA 4.0 licence.

## Who publishes it

XQuAD was introduced by Mikel Artetxe, Sebastian Ruder and Dani Yogatama in "On the Cross-lingual Transferability of Monolingual Representations" (arXiv:1910.11856, first posted October 2019). The dataset is maintained in the google-deepmind/xquad GitHub repository.

## Lineage

XQuAD's questions and answers are translations of the SQuAD v1.1 dev set, so `squad` is its direct predecessor. It belongs to a family of multilingual extractive-QA sets built the same way, alongside MLQA and TyDi QA (`tydiqa` in this repository), though those use different source questions and construction methods rather than being XQuAD variants. No successor benchmark under a different id was established from the sources reviewed here.

## Saturation and contamination

No saturation study was reviewed here, so status is unknown. Contamination risk is medium: the underlying SQuAD v1.1 paragraphs and answers, and the XQuAD translations themselves, have been publicly posted since 2019-2020, so both the English source and the translated pairs are plausible inclusions in the training data of models released since then.

## How to run it

lm-evaluation-harness implements XQuAD as an `xquad` group with one subtask per language: `xquad_ar`, `xquad_de`, `xquad_el`, `xquad_en`, `xquad_es`, `xquad_hi`, `xquad_ro`, `xquad_ru`, `xquad_th`, `xquad_tr`, `xquad_vi`, `xquad_zh`. Note that the harness's task list includes a Romanian subtask (`xquad_ro`) not present in the original 11-language DeepMind release, so check which language set a given report actually used before comparing averages. Also record whether a score is zero-shot, translate-train or translate-test, since these protocols are not interchangeable.

## Reading the numbers

A high average XQuAD score suggests a model's English reading-comprehension skill carries over to other languages reasonably well; a large gap between English and other languages points to weak cross-lingual transfer rather than weak reading comprehension per se. Because scores are usually averaged across very different languages, from Spanish to Thai to Arabic, look at the per-language breakdown before concluding a model is uniformly strong. F1 and exact-match can diverge, especially in languages with different tokenization, so check which metric is reported. Given the dataset's age and public availability, treat unusually high scores as a possible contamination signal rather than a pure transfer signal.
