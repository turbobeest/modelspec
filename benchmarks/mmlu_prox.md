---
id: mmlu_prox
name: "MMLU-ProX"
aliases: ["MMLU-ProX: A Multilingual Benchmark for Advanced Large Language Model Evaluation"]
page_kind: benchmark
category: knowledge
subcategory: "multilingual multitask academic and professional knowledge (translated MMLU-Pro, 29 languages)"
status: active
summary: "A 29-language, expert-verified translation of MMLU-Pro with 11,829 identical questions per language, built to compare cross-linguistic reasoning rather than just English knowledge."
measures: >
  MMLU-ProX takes MMLU-Pro's ten-option, reasoning-heavy multiple-choice questions across 14
  categories and translates every question into 29 typologically diverse languages, keeping the same
  11,829 questions identical (parallel) across every language version so scores are directly
  comparable across languages rather than only within one. Translation runs through multiple large
  language models followed by expert human review: over 30 professional translators, native in the
  target language and proficient in English, rated accuracy, fluency and completeness on a 1-5 scale
  for a stratified sample, triggering full retranslation of any subject-language pair that scored
  below 3 on any dimension (only Yoruba law needed this). A separate lite version keeps 658 questions
  per language (a fixed 47-question-per-category-ish, difficulty-consistent subsample) for cheaper
  evaluation runs.
task_format: >
  Ten-option (occasionally fewer) multiple-choice questions across the same 14 MMLU-Pro categories
  (Biology, Business, Chemistry, Computer Science, Economics, Engineering, Health, History, Law,
  Math, Philosophy, Physics, Psychology, Other), graded on the single option selected, in each of 29
  languages. Following MMLU-Pro's own protocol, the paper's primary reported setting is 5-shot
  chain-of-thought prompting, though the authors also evaluate 0-shot for comparison across their
  36-model sweep.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 10
  human_baseline: null
  baseline_note: >
    10% is the ten-option random-guess rate, inherited from MMLU-Pro (a few questions carry fewer
    options after review, as in the parent benchmark). No human baseline has been published for
    MMLU-ProX; the paper's central comparison is between languages and models rather than against a
    human anchor.
dataset:
  size: 342441
  size_note: >
    29 languages x 11,829 questions each = 342,441 rows in the full release (confirmed per-language
    via the Hugging Face datasets-server: 70 validation + 11,759 test = 11,829 for the English
    config, matching every other language's config). A separate lite release
    (`li-lab/MMLU-ProX-Lite`) holds 658 questions per language (70 validation + 588 test, confirmed
    the same way) x 29 languages = 19,082 rows, for cheaper evaluation. Both releases are built from
    the same underlying MMLU-Pro test questions translated in parallel, so counts are identical
    across languages by construction.
  url: "https://huggingface.co/datasets/li-lab/MMLU-ProX"
  license: MIT
  languages: ["af", "ar", "bn", "cs", "de", "en", "es", "fr", "hi", "hu", "id", "it", "ja", "ko", "mr", "ne", "pt", "ru", "sr", "sw", "te", "th", "uk", "ur", "vi", "wo", "yo", "zh", "zu"]
  modalities: ["text"]
  splits: "validation (70/language, few-shot source) and test (11,759/language, scored); lite release mirrors this with 70/588 per language"
  public_test_set: true
publisher:
  org: "The University of Tokyo, with co-authors across 16 further institutions including Duke-NUS Medical School, Waseda University, Carnegie Mellon University and Yale University"
  authors: ["Weihao Xuan", "Rui Yang", "Heli Qi", "Qingcheng Zeng", "Yunze Xiao", "Aosong Feng", "Dairui Liu", "Yun Xing", "Junjue Wang", "Fan Gao", "Jinghui Lu", "Yuang Jiang", "Huitao Li", "Xin Li", "Kunyu Yu", "Ruihai Dong", "Shangding Gu", "Yuekang Li", "Xiaofei Xie", "Felix Juefei-Xu", "Foutse Khomh", "Osamu Yoshie", "Qingyu Chen", "Douglas Teodoro", "Nan Liu", "Randy Goebel", "Lei Ma", "Edison Marrese-Taylor", "Shijian Lu", "Yusuke Iwasawa", "Yutaka Matsuo", "Irene Li"]
  url: "https://github.com/weihao1115/MMLU-ProX"
paper:
  title: "MMLU-ProX: A Multilingual Benchmark for Advanced Large Language Model Evaluation"
  arxiv: "2503.10497"
  url: "https://arxiv.org/abs/2503.10497"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/weihao1115/MMLU-ProX"
released: "2025-03"
last_updated: "2025-08"
lineage:
  family: mmlu
  predecessor: mmlu_pro
  successors: []
  variants: []
saturation:
  status: open
  top_score: 75.5
  as_of: "2025-05"
  note: >
    Not saturated, and far from it in most languages. Among the 15 representative models the paper
    highlights (largest or best of each family, of 36 tested), DeepSeek-R1 leads with a 75.5% overall
    average across all 29 languages per the paper's own results table -- though the accompanying
    prose states "an average of 75.2%" for the same model, a minor table-versus-text discrepancy in
    the source that this page reports rather than resolves. Performance is highly uneven by language:
    the paper reports "gaps of up to 24.3%" between high- and low-resource languages in aggregate, and
    separately notes some models scoring as low as 0.6% accuracy on certain African languages while
    exceeding 75% on Western European ones. The project's own leaderboard page was marked "Coming
    Soon" as of the homepage fetched for this research, so no independently tracked current standing
    beyond the paper's May 2025 (v2) results could be confirmed.
contamination:
  risk: medium
  note: >
    MMLU-ProX's English config is built directly from MMLU-Pro's public test questions, which in turn
    carry over about 57% of the original MMLU test set (public since 2020, assessed as high
    contamination risk on the `mmlu` family page). The translated versions are newer (first released
    March 2025) and less likely to have been seen verbatim in older training corpora, but the full
    dataset and its answers, in all 29 languages, have been public on Hugging Face without gating
    since release, with no held-out portion.
harness:
  lm_eval: "mmlu_prox (groups mmlu_prox_{lang} and mmlu_prox_lite_{lang} for each of the 29 language codes, each expanding to 14 per-category tasks, following mmlu_pro's own evaluation methodology)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "The authors' own repository (weihao1115/MMLU-ProX) provides the translation pipeline and evaluation code; the project was accepted at EMNLP 2025 (Main Conference)."
tags: ["knowledge", "multiple-choice", "multitask", "multilingual", "chain-of-thought", "ten-option", "five-shot", "translation"]
sources:
  - url: "https://arxiv.org/abs/2503.10497"
    title: "MMLU-ProX: A Multilingual Benchmark for Advanced Large Language Model Evaluation (Xuan et al., arXiv:2503.10497)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.10497"
    title: "MMLU-ProX, full text (ar5iv, reflecting the May 2025 v2 revision)"
    accessed: "2026-09-08"
  - url: "https://github.com/weihao1115/MMLU-ProX"
    title: "weihao1115/MMLU-ProX GitHub repository"
    accessed: "2026-09-08"
  - url: "https://mmluprox.github.io/"
    title: "MMLU-ProX project homepage (author list, affiliations, links)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/li-lab/MMLU-ProX"
    title: "li-lab/MMLU-ProX dataset card and API metadata, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/li-lab/MMLU-ProX-Lite"
    title: "li-lab/MMLU-ProX-Lite dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=li-lab/MMLU-ProX&config=en"
    title: "li-lab/MMLU-ProX datasets-server size API (English config split counts)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu_prox/README.md"
    title: "lm-evaluation-harness mmlu_prox task README (groups, tasks, 29 language codes)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MMLU-ProX takes MMLU-Pro's ten-option, reasoning-heavy multiple-choice questions, spanning the same
14 categories from Biology to Psychology, and translates every question into 29 typologically
diverse languages while keeping the question set identical (parallel) across languages. That
parallelism is the point: because every language version asks the same 11,829 questions, a drop in
score when moving from English to another language is attributable to the language itself rather
than to different underlying content, which prior multilingual benchmarks assembled from
per-language sources could not isolate as cleanly.

Translation runs through multiple large language models, then expert human review: over 30
professional translators native in the target language rated accuracy, fluency and completeness on
a 1-5 scale for a stratified sample, triggering full retranslation of any subject-language pair that
scored below 3 on any dimension. Only Yoruba's law category needed this; every other
language-category pair averaged 4 or above. A lite version (658 questions per language) supports
cheaper evaluation runs at the cost of coverage.

## How it is scored

Accuracy against a 10% random-guess floor for ten-option questions, inherited unchanged from
MMLU-Pro. No human baseline has been published. Following MMLU-Pro's own evaluation methodology, the
paper's primary reported condition is 5-shot chain-of-thought prompting, though the authors also run
0-shot across their full 36-model sweep to check protocol sensitivity. All experiments used vLLM on
an H100 cluster, consuming an estimated 10,000-plus GPU hours for the unified evaluation the paper
reports.

## Dataset and licence

The full release holds 342,441 rows: 29 languages, each with the identical 11,829 questions (70
validation, 11,759 test, confirmed per-language via the Hugging Face datasets-server). The lite
release mirrors this at 658 questions per language (70 validation, 588 test) for 19,082 rows total.
Both are hosted on Hugging Face (`li-lab/MMLU-ProX` and `li-lab/MMLU-ProX-Lite`) under an MIT
licence, matching MMLU-Pro's own. Because the question pool is translated rather than newly written,
its content inherits MMLU-Pro's provenance (partly difficulty-filtered original MMLU questions,
partly newly authored ones) in every language version.

## Who publishes it

Weihao Xuan, Rui Yang, Heli Qi, Qingcheng Zeng and 28 further co-authors published MMLU-ProX in
March 2025 (arXiv:2503.10497, revised May 2025), with the paper accepted at EMNLP 2025's Main
Conference. The 32-author list spans at least 17 institutions; the project homepage lists first
author Weihao Xuan and corresponding-position author Irene Li both at the University of Tokyo, with
other co-authors at Duke-NUS Medical School, Waseda University, Carnegie Mellon University, Yale
University and elsewhere. The authors maintain the GitHub repository, both Hugging Face dataset
releases, and a project homepage that lists a leaderboard as forthcoming.

## Lineage

MMLU-ProX's direct predecessor is MMLU-Pro (`mmlu_pro`), from which it inherits its 14-category,
ten-option question format and its full English question set verbatim; MMLU-Pro's own predecessor,
the original MMLU (`mmlu`), sits one level further back in the same lineage as the ultimate source of
roughly 57% of MMLU-Pro's (and so MMLU-ProX's) questions. No successor to MMLU-ProX was identified in
this research; the paper states an intention to keep expanding language coverage in future releases,
which would extend this same benchmark rather than replace it.

## Saturation and contamination

Not saturated in aggregate, and unevenly so by language. Among the paper's 15 representative models
(largest or strongest per family, of 36 tested), DeepSeek-R1 leads with a 75.5% overall average
across all 29 languages per the results table, a few tenths above GPT-4.1 (72.7%) and
Qwen3-235B-Think (74.9%); the accompanying text states "75.2%" for the same model, a small
table-versus-prose discrepancy in the source. The real story is the spread: the paper reports gaps of
up to 24.3% between high- and low-resource languages, and specific cases of models scoring near
random (as low as 0.6%) on some African languages while exceeding 75% on Western European ones. This
repository could not confirm a current leaderboard beyond the paper's own May 2025 table, since the
project's own leaderboard page reads "Coming Soon." Contamination risk is medium: the underlying
English questions carry MMLU-Pro's own exposure (including MMLU's high-risk original test set), while
the translations are newer and less likely memorized verbatim, but the full multilingual dataset has
been public without gating since March 2025.

## How to run it

lm-evaluation-harness implements the benchmark as `mmlu_prox_{lang}` and `mmlu_prox_lite_{lang}`
groups for each of the 29 language codes, each expanding into 14 per-category tasks evaluated
"following the methodology in mmlu_pro's original implementation," for 812 total tasks across both
releases. No OpenCompass, inspect_evals or HELM implementation was found during this research. Given
the paper evaluates both 0-shot and 5-shot CoT and finds these produce different results, and that
the harness README does not fix one setting as canonical, always check which shot count and prompting
condition produced a reported score before comparing it to another.

## Reading the numbers

A high MMLU-ProX score in one language is only informative about that language; because the question
set is held parallel across languages, the more informative comparison is a model's score spread
across languages, which shows how much its apparent knowledge and reasoning ability depends on the
language it is tested in rather than on the underlying content. A model strong in English or other
high-resource languages can still perform close to random on low-resource ones, so an aggregate
across-language average can mask exactly the disparity the benchmark was built to expose -- check the
per-language breakdown, and treat an MMLU-ProX score in a specific language as more informative than
one overall number.
