---
id: xiezhi
name: Xiezhi
aliases: []
page_kind: benchmark
category: knowledge
subcategory: multi-disciplinary domain knowledge (multiple-choice)
status: active
summary: Xiezhi is a Chinese-and-English multiple-choice benchmark covering holistic knowledge across 516 academic disciplines in 13 subjects.
measures: Xiezhi tests how much domain knowledge a model holds across a very wide span of academic and professional fields, in both Chinese and English, using multiple-choice questions adapted from exam and textbook material.
task_format: Multiple-choice question answering; each item gives a discipline-specific question and a candidate label pool, and the model selects the correct label.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The paper reports average human performance per discipline group rather than one fixed baseline figure."}
dataset: {size: 249587, size_note: "249,587 questions across 516 disciplines grouped into 13 subjects, plus two curated subsets (Xiezhi-Specialty and Xiezhi-Interdiscipline) of 15,000 questions each.", url: "https://github.com/MikeGu721/XiezhiBenchmark", license: "CC BY-NC-SA 4.0 (dataset); MIT (code)", languages: [en, zh], modalities: [text], splits: "Full benchmark plus Specialty and Interdiscipline evaluation subsets (15k questions each)", public_test_set: true}
publisher: {org: "Fudan University and collaborators", authors: ["Zhouhong Gu", "and 18 co-authors"], url: "https://github.com/MikeGu721/XiezhiBenchmark"}
paper: {title: "Xiezhi: An Ever-Updating Benchmark for Holistic Domain Knowledge Evaluation", arxiv: "2306.05783", url: "https://arxiv.org/abs/2306.05783", year: 2024}
leaderboard_url: ""
repo_url: https://github.com/MikeGu721/XiezhiBenchmark
released: "2023-06"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "The paper's own 2023 evaluation of 47 LLMs found models beat average human performance in science, engineering, agronomy, medicine and art, but trailed humans in economics, law, education, literature, history and management. No later saturation study was reviewed here."}
contamination: {risk: medium, note: "Items are adapted from public Chinese and English exam and textbook material. The benchmark is explicitly designed to be periodically refreshed to counter staleness, but any single released split can still enter training corpora once public."}
harness: {opencompass: xiezhi}
tags: [benchmark, multilingual, multiple-choice, knowledge]
sources:
  - url: https://arxiv.org/abs/2306.05783
    title: "Xiezhi: An Ever-Updating Benchmark for Holistic Domain Knowledge Evaluation"
    accessed: "2026-09-08"
  - url: https://github.com/MikeGu721/XiezhiBenchmark
    title: Xiezhi official repository
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/xiezhi
    title: OpenCompass xiezhi dataset configs
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/xiezhi
    title: "lm-evaluation-harness tasks directory (no xiezhi task present)"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-002"}
---
## What it measures

Xiezhi tests how much domain knowledge a language model holds across a very wide span of academic and professional fields, in both Chinese and English. Each item is a multiple-choice question drawn from an academic discipline — engineering, medicine, law, the humanities and more — and the model must pick the correct label from a candidate set rather than generate a free-text answer. The benchmark spans 516 disciplines organized into 13 top-level subjects, aiming for the kind of broad, encyclopedic coverage a general knowledge or professional-licensing exam would need, rather than depth in one field.

## How it is scored

Items are scored as exact-match multiple-choice accuracy: the model picks one label from the candidate pool and is marked correct if it matches the gold discipline label. OpenCompass runs Xiezhi both as a generative task (`xiezhi_gen`) and as a perplexity/log-likelihood ranking task over the candidate options (`xiezhi_ppl`); the two protocols can produce different scores for the same model, since the generative variant depends on output parsing while the perplexity variant compares candidate likelihoods directly. The paper additionally reports per-discipline scores against average human performance drawn from the exams the questions were adapted from, rather than a single fixed baseline number.

## Dataset and licence

The full Xiezhi set contains 249,587 questions. Two smaller curated evaluation subsets, Xiezhi-Specialty and Xiezhi-Interdiscipline, each hold 15,000 questions for cheaper, faster runs. Items are adapted from Chinese and English professional and academic exam material spanning the 516 disciplines. The official repository states the dataset is released under CC BY-NC-SA 4.0 (non-commercial, share-alike), while the accompanying code is MIT-licensed; the two licences cover different parts of the release and should not be conflated. Which exact split OpenCompass consumes by default was not established from the files inspected here.

## Who publishes it

Xiezhi comes from Zhouhong Gu and 18 co-authors, published as "Xiezhi: An Ever-Updating Benchmark for Holistic Domain Knowledge Evaluation" and accepted at AAAI 2024 (arXiv:2306.05783, first posted June 2023). The authors maintain the benchmark and code at github.com/MikeGu721/XiezhiBenchmark.

## Lineage

This page documents the `xiezhi` identifier as integrated into OpenCompass. No predecessor benchmark is named in the paper; "ever-updating" refers to the authors' stated intent to keep refreshing the item pool over time, not to a distinct successor benchmark. No successor or variant under a different id was established from the sources reviewed here.

## Saturation and contamination

No saturation study specific to current frontier models was found, so status is unknown. In the paper's own 2023 evaluation of 47 LLMs, models exceeded average human performance in science, engineering, agronomy, medicine and art, but fell short of humans in economics, law, education, literature, history and management — so the benchmark was not saturated at release. Contamination risk is medium: items are drawn from publicly available exam and textbook sources, and while the authors designed Xiezhi to be periodically refreshed specifically to fight staleness, any single released split can still leak into training corpora once public.

## How to run it

OpenCompass ships two variants under `opencompass/configs/datasets/xiezhi/`: `xiezhi_gen` (generative) and `xiezhi_ppl` (perplexity-ranked), each with a hashed config variant. No task named `xiezhi` was found in lm-evaluation-harness at the time of this review, so scores reported through other harnesses should not be assumed comparable to OpenCompass numbers. Record which of the two OpenCompass protocols, and which config hash, produced a given score.

## Reading the numbers

A strong Xiezhi score suggests broad, encyclopedic recall across many academic disciplines in Chinese and English, not depth in any one field or the ability to apply that knowledge. Because it is a large label-selection task, generative and perplexity-based scoring can diverge for the same model, so compare only same-protocol numbers. The Specialty and Interdiscipline subsets are cheaper proxies, not full replacements, for the 249k-question benchmark. Given the medium contamination risk from public exam-sourced items, treat very high scores with some caution and prefer numbers reported against a stated release or config revision.
