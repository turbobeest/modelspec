---
id: tydiqa
name: TyDi QA
aliases:
  - TyDiQA
  - TyDiQA-GoldP
page_kind: benchmark
category: knowledge
subcategory: multilingual extractive question answering
status: active
summary: 204,000 information-seeking question-answer pairs across 11 typologically diverse languages, collected without translation, testing extractive QA beyond English.
measures: >
  TyDi QA gives a model a real information-seeking question in one of 11 typologically diverse
  languages and asks it to find the answer in Wikipedia text in that same language. Questions were
  written by people who wanted to know the answer and did not already know it, and the data was
  collected directly in each language rather than by translating English questions, which the
  authors built in specifically to avoid the priming and translation artefacts that shape datasets
  like SQuAD, XQuAD or MLQA. "Typologically diverse" means the 11 languages were chosen to span a
  wide range of grammatical and orthographic features - among them Arabic, Bengali, Finnish,
  Indonesian, Japanese, Swahili, Korean, Russian, Telugu and Thai alongside English - so that
  strong performance is harder to achieve by a system tuned only to English-like structure. It is
  a question-answering and information-retrieval task rather than a machine-translation task - no
  language pair is translated, and each question is answered from text in its own language.
task_format: "Two primary tasks over a full Wikipedia article - Passage selection (SelectP): return the index of the passage that answers the question, or NULL if none does; Minimal answer span (MinSpan): return the start/end byte span of the minimal answering text, YES/NO for yes-no questions, or NULL if unanswerable. A secondary Gold passage task (GoldP) hands the model a single passage guaranteed to contain the answer and asks for the extractive span, matching the SQuAD 1.1 format; GoldP drops unanswerable questions and excludes Japanese and Thai."
metric:
  name: "F1 and exact match, averaged across languages"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The official evaluation script computes language-wise F1 and averages across languages, excluding English from the macro average; primary-task spans are compared by byte position with partial credit for overlap, while the Gold Passage task reuses the SQuAD 1.1 F1/exact-match code directly. No source read for this page gave a human-performance baseline figure."
dataset:
  size: 204000
  size_note: "204K question-answer pairs across 11 languages for the primary tasks (166,916 train / 18,670 validation rows in the Hugging Face primary_task config, confirmed via the datasets-server API); the secondary Gold Passage task subsets this to 49,881 train / 5,077 validation rows across 9 of the 11 languages, dropping Japanese and Thai for tokenisation and SQuAD-format compatibility."
  url: https://github.com/google-research-datasets/tydiqa
  license: Apache-2.0
  languages:
    - en
    - ar
    - bn
    - fi
    - id
    - ja
    - sw
    - ko
    - ru
    - te
    - th
  modalities:
    - text
  splits: "public train and validation (dev) files for both the primary and Gold Passage tasks; the repository also runs a submission-based public leaderboard for held-out comparison."
  public_test_set: true
publisher:
  org: Google Research
  authors:
    - Jonathan H. Clark
    - Eunsol Choi
    - Michael Collins
    - Dan Garrette
    - Tom Kwiatkowski
    - Vitaly Nikolaev
    - Jennimaria Palomaki
  url: https://ai.google.com/research/tydiqa
paper:
  title: "TyDi QA: A Benchmark for Information-Seeking Question Answering in Typologically Diverse Languages"
  arxiv: "2003.05002"
  url: https://arxiv.org/abs/2003.05002
  year: 2020
leaderboard_url: https://ai.google.com/research/tydiqa
repo_url: https://github.com/google-research-datasets/tydiqa
released: "2020-02"
last_updated: "2020-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current, model-by-model leaderboard snapshot was read for this page, so a present-day top score is not established. The dataset's own public leaderboard page was reachable at research time, but its live standings were not captured here."
contamination:
  risk: medium
  note: "The dataset (Wikipedia passages plus questions and answers) has been public since February 2020, and most reported harness scores run against the public dev/validation split rather than any held-out set, so overlap with later pretraining crawls is plausible. Risk is kept at medium rather than high because no source read during this research documented actual demonstrated memorisation, and the source Wikipedia snapshots are individually dated and identifiable rather than freshly scraped."
harness:
  lm_eval: tydiqa_goldp
  inspect_evals: ""
  helm: ""
  opencompass: tydiqa
  bigbench: ""
  other: ""
tags:
  - multilingual
  - question-answering
  - extractive-qa
  - typological-diversity
  - knowledge
sources:
  - url: https://arxiv.org/abs/2003.05002
    title: "TyDi QA: A Benchmark for Information-Seeking Question Answering in Typologically Diverse Languages (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/google-research-datasets/tydiqa/master/README.md
    title: google-research-datasets/tydiqa README (raw)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/google-research-datasets/tydiqa/master/tydi_eval.py
    title: google-research-datasets/tydiqa evaluation script (raw, language list and scoring logic)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/google-research-datasets/tydiqa/master/CHANGELOG.md
    title: google-research-datasets/tydiqa CHANGELOG
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/google-research-datasets/tydiqa
    title: google-research-datasets/tydiqa dataset card (Hugging Face)
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=google-research-datasets/tydiqa&config=primary_task
    title: datasets-server info endpoint for tydiqa primary_task (split sizes)
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/tydiqa/README.md
    title: lm-evaluation-harness tydiqa (Gold Passage) task README
    accessed: "2026-09-08"
  - url: https://github.com/google-research/xtreme
    title: google-research/xtreme GitHub repository
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

TyDi QA tests whether a model can find the answer to a genuine information-seeking question in Wikipedia text written in the question's own language, across 11 typologically diverse languages: English, Arabic, Bengali, Finnish, Indonesian, Japanese, Swahili, Korean, Russian, Telugu and Thai (the exact list the official evaluation script scores over). "Typologically diverse" means the languages were deliberately chosen to differ widely in grammar, morphology and script, so a system cannot do well by relying on structural regularities that happen to hold for English. Two design choices distinguish it from earlier multilingual QA sets: questions were written by people who wanted to know the answer and did not already know it, avoiding the artificial phrasing that comes from writing a question to match a known passage, and the data was collected natively in each language rather than by translating English questions or answers.

This is a question-answering and retrieval task, not a translation task: nothing in the benchmark asks a model to render text from one language into another, and each question is answered using source text in that same language. That is why this repository categorises it under knowledge rather than translation, despite the multilingual framing.

## How it is scored

The two primary tasks - passage selection and minimal answer span - are scored with the official `tydi_eval.py` script, which computes F1 per language (byte-position span overlap for minimal answers) and then macro-averages across languages, explicitly excluding English from that average. The secondary Gold Passage (GoldP) task simplifies the setting to a single guaranteed-relevant passage per question, discards unanswerable questions, and reuses the SQuAD 1.1 F1/exact-match evaluation code directly, which is why GoldP is the version most often plugged into existing reading-comprehension pipelines and harnesses. GoldP drops Japanese and Thai because, per the authors, the lack of whitespace word boundaries in those languages breaks some of the SQuAD-era tooling, leaving 9 languages in that variant.

## Dataset and licence

The primary-task release contains 204,000 question-answer pairs across the 11 languages, split into 166,916 training and 18,670 validation rows. The Gold Passage variant subsets this to 49,881 training and 5,077 validation rows across the 9 languages it keeps. Source articles come from single, dated Wikipedia snapshots (per-language dumps from around February 2019) fetched via the Internet Archive, which keeps the underlying text traceable to a specific point in time. Both the GitHub repository and its Hugging Face mirror state an Apache-2.0 licence.

## Who publishes it

TyDi QA was created by Jonathan H. Clark, Eunsol Choi, Michael Collins, Dan Garrette, Tom Kwiatkowski, Vitaly Nikolaev and Jennimaria Palomaki at Google Research, published in Transactions of the Association for Computational Linguistics (TACL) in 2020. Google maintains the reference repository, evaluation code and a public leaderboard for the primary tasks at the project's own site; the GitHub repository asks leaderboard submitters to disclose their training data and methodology alongside a score.

## Lineage

TyDi QA does not have a numbered successor in this repository, but its Gold Passage task is one of the constituent question-answering tasks in the XTREME cross-lingual benchmark suite, alongside XQuAD and MLQA - XTREME reuses TyDiQA-GoldP rather than replacing it. Within TyDi QA itself, SelectP, MinSpan and GoldP are three task variants over the same underlying question set rather than separate benchmarks, and the authors ask that reports name the specific variant (TyDiQA-SelectP, TyDiQA-MinSpan or TyDiQA-GoldP) rather than citing "TyDi QA" alone, since the three differ substantially in difficulty and format. No distinct successor benchmark by a different name was identified in the sources reviewed for this page.

## Saturation and contamination

No current, dated leaderboard snapshot was captured for this page, so a present-day top score across models is not established here; the project's own leaderboard page was reachable at research time but its live standings were not read. Contamination risk sits at medium: the dataset has been public since February 2020, most reported scores run against the open validation split rather than a blind set, and the source Wikipedia text is easy to find in later web crawls, but no source read during this research demonstrated specific memorisation.

## How to run it

lm-evaluation-harness implements the Gold Passage task as `tydiqa_goldp`, with one YAML config per language (for example `tydiqa_goldp_ar.yaml`) built on a shared common config, covering the same 9 languages GoldP defines. OpenCompass ships its own `tydiqa` dataset configuration. Because GoldP, SelectP and MinSpan are graded differently and cover different language subsets, and because harnesses vary in prompt format and few-shot count, always confirm which task variant and how many languages a reported TyDi QA number actually covers before comparing it to another source's figure.

## Reading the numbers

A strong TyDi QA score, especially on the harder primary tasks, is reasonable evidence a model can do extractive question answering in typologically varied languages rather than only in English or closely related ones. Because most reports use the Gold Passage simplification - a single guaranteed-relevant passage - a high GoldP score says less about retrieval or ranking ability than the full primary tasks would; check which variant and how many of the 11 languages a report covers, since a "TyDi QA" number quoted without that context is not comparable across papers.
