---
id: xsum
name: XSum
aliases: []
page_kind: benchmark
category: generation
subcategory: single-document abstractive summarization
status: active
summary: XSum is an English single-document summarization benchmark of 226,711 BBC articles paired with a one-sentence summary each.
measures: XSum tests abstractive single-document summarization. Given a full BBC news article, the model must produce a single, fluent sentence answering "what is this article about", a format designed to discourage extractive copy-paste strategies and require genuine synthesis.
task_format: Abstractive summarization; generate a single-sentence summary of a full news article.
metric: {name: "ROUGE-1/2/L", direction: higher_is_better, unit: "F1", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "Scored against a single reference summary with ROUGE F1 in the original paper. Reference-based ROUGE is known to correlate weakly with human judgments of summary quality and faithfulness on this dataset."}
dataset: {size: 226711, size_note: "226,711 BBC articles (2010-2017) each paired with a single-sentence summary; split 204,045 train / 11,332 validation / 11,334 test.", url: "https://github.com/EdinburghNLP/XSum", license: "", languages: [en], modalities: [text], splits: "train 204,045 / validation 11,332 / test 11,334", public_test_set: true}
publisher: {org: "University of Edinburgh (EdinburghNLP)", authors: ["Shashi Narayan", "Shay B. Cohen", "Mirella Lapata"], url: "https://github.com/EdinburghNLP/XSum"}
paper: {title: "Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization", arxiv: "1808.08745", url: "https://arxiv.org/abs/1808.08745", year: 2018}
leaderboard_url: ""
repo_url: https://github.com/EdinburghNLP/XSum
released: "2018"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: watch, top_score: null, as_of: "", note: "Not saturated in the ceiling sense, but Stanford HELM and follow-up work note that reference-based ROUGE scoring on XSum and CNN/DailyMail largely fails to discriminate quality differences between strong models, which limits how much a ROUGE score alone tells you."}
contamination: {risk: high, note: "The BBC articles and reference summaries have been public since 2018 and are commonly present in web-crawl pretraining corpora, so contamination is likely for models trained on broad web data."}
harness: {opencompass: Xsum, helm: summarization_xsum}
tags: [benchmark, summarization, generation, english]
sources:
  - url: https://arxiv.org/abs/1808.08745
    title: "Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization"
    accessed: "2026-09-08"
  - url: https://github.com/EdinburghNLP/XSum
    title: XSum official repository
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/EdinburghNLP/xsum
    title: XSum dataset card (Hugging Face)
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/summarization_scenario.py
    title: "HELM summarization_scenario.py (includes XSum)"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-002"}
---
## What it measures

XSum tests abstractive single-document summarization in English: given a full BBC news article, the model must produce one fluent sentence answering "what is this article about?" The task was deliberately designed around highly abstractive, journalist-written single-sentence summaries — the kind that opens a BBC article — rather than around summaries assembled from copied sentences, so it discourages purely extractive strategies and calls for genuine synthesis of the article's content. This is a summarization benchmark, not a translation benchmark; every article and summary is in English.

## How it is scored

The original paper scores generated summaries against the single reference summary using ROUGE-1, ROUGE-2 and ROUGE-L F1. Because there is only one human reference per article and ROUGE rewards lexical overlap, it penalizes valid paraphrases that use different words and does not directly measure factual accuracy. Later work, including Stanford's HELM evaluation, has documented that reference-based ROUGE on XSum correlates weakly with human judgments of summary quality and faithfulness, and some evaluators now pair XSum with LLM-judge or dedicated factuality metrics rather than relying on ROUGE alone.

## Dataset and licence

XSum contains 226,711 BBC articles published between 2010 and 2017, covering news, politics, sport, weather, business, technology, science, health, family, education, entertainment and the arts, each paired with the one-sentence summary written by the article's own journalist. The standard split is 204,045 articles for training, 11,332 for validation and 11,334 for test. The EdinburghNLP repository's code is released under an MIT licence, but that covers the collection scripts, not necessarily the BBC article text itself; the Hugging Face dataset card does not state a licence for the underlying content, so the licence field here is left empty rather than guessed.

## Who publishes it

XSum was introduced by Shashi Narayan, Shay B. Cohen and Mirella Lapata in "Don't Give Me the Details, Just the Summary! Topic-Aware Convolutional Neural Networks for Extreme Summarization" (EMNLP 2018; arXiv:1808.08745, first posted August 2018). The dataset and preprocessing code are maintained by EdinburghNLP at the University of Edinburgh.

## Lineage

No predecessor benchmark is named by the authors; XSum was introduced specifically to contrast with the more extractive CNN/DailyMail summarization dataset. No successor benchmark under a different id, and no subset/variant pages, were established from the sources reviewed here.

## Saturation and contamination

XSum is not saturated in the sense of top models sitting at a ceiling score, but its ROUGE-based metric has a known discrimination problem: HELM and related work report that reference-based ROUGE scoring on XSum largely fails to separate strong models by quality, so status here is "watch" on the metric rather than "saturated" on the task. Contamination risk is high: the articles and summaries have been public since 2018 and are commonly present in general web-crawl pretraining data, so many recent models likely have seen this exact data during pretraining.

## How to run it

OpenCompass ships `Xsum_gen` configs (with hashed variants) under `opencompass/configs/datasets/Xsum/`. Stanford HELM implements a `summarization_xsum` scenario in `summarization_scenario.py`. No task named `xsum` was found in lm-evaluation-harness at the time of this review. Because scoring is reference-based, record which ROUGE variant (1/2/L), tokenizer, and stemming settings were used, and whether any faithfulness or LLM-judge metric was reported alongside ROUGE, since these are not standardized across reporters.

## Reading the numbers

A high ROUGE score on XSum suggests a model's one-sentence summary shares more words and phrases with the reference than a lower-scoring model's does; it is a weak proxy for whether the summary is accurate, complete, or free of hallucinated details, since ROUGE does not check factuality. Given the documented weak correlation between ROUGE and human quality judgments on this dataset, treat close ROUGE scores between strong models as uninformative and prefer results paired with a faithfulness metric or human/LLM-judge evaluation where available. Given the high contamination risk, a strong score may partly reflect memorization of the reference summary rather than genuine summarization skill.
