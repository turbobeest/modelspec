---
id: cmb
name: "CMB (Comprehensive Medical Benchmark in Chinese)"
aliases:
  - "Comprehensive Medical Benchmark in Chinese"
page_kind: benchmark
category: domain
subcategory: "Chinese medical licensing exams and clinical-case diagnosis"
status: active
summary: "A two-part Chinese medical benchmark: 280,839 licensing-exam questions across 28 subcategories (CMB-Exam) plus 74 multi-turn clinical cases graded on four qualitative dimensions (CMB-Clin)."
measures: >
  CMB tests medical knowledge and clinical reasoning in a Chinese-language, China-specific medical
  context, deliberately built rather than translated because the authors argue medical practice,
  licensing structure and terminology differ by region -- the benchmark also covers traditional
  Chinese medicine alongside modern biomedicine. It has two parts. CMB-Exam is multiple-choice and
  multiple-answer questions drawn from real Chinese medical licensing and qualification exams,
  covering six major categories (physician, nursing, pharmacist, medical technician, professional
  knowledge and postgraduate-entrance exams) split into 28 subcategories. CMB-Clin is 74 complex
  clinical cases, each a multi-turn conversation simulating a doctor working through a patient's
  history, examinations and diagnosis, testing free-form clinical reasoning rather than recall.
task_format: >
  CMB-Exam: multiple-choice and multiple-answer questions, Chinese, evaluated zero-shot and
  few-shot with and without chain-of-thought. CMB-Clin: multi-turn free-form clinical dialogue,
  graded rather than scored against a fixed key.
metric:
  name: "accuracy (CMB-Exam); four-dimension 1-5 rating (CMB-Clin)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CMB-Exam is scored as plain accuracy against the exam's answer key; the paper does not report a
    general random-guess baseline because question types mix single- and multi-answer formats.
    CMB-Clin is scored on four dimensions (fluency, relevance, completeness, medical proficiency),
    each rated 1-5, originally by human experts and, in the paper, also by a GPT-4 judge whose
    ratings the authors report correlate with human judgment at a Spearman coefficient of 0.93.
dataset:
  size: 280839
  size_note: >
    CMB-Exam totals 280,839 multiple-choice/multiple-answer questions across 28 subcategories:
    269,359 for training, 280 for validation (with explanations), and 11,200 for test (confirmed via
    the project GitHub repository's data breakdown). CMB-Clin is separate: 74 expert-curated clinical
    cases comprising 208 questions in total, sourced from official medical textbooks and screened to
    remove image-dependent cases.
  url: "https://huggingface.co/datasets/FreedomIntelligence/CMB"
  license: "Apache-2.0 (GitHub repository and Hugging Face dataset card both state this)"
  languages:
    - zh
  modalities:
    - text
  splits: "CMB-Exam: train (269,359) / val (280) / test (11,200). CMB-Clin: 74 cases, 208 questions, no split."
  public_test_set: true
publisher:
  org: "The Chinese University of Hong Kong, Shenzhen; Shenzhen Research Institute of Big Data"
  authors:
    - "Xidong Wang"
    - "Guiming Hardy Chen"
    - "Dingjie Song"
    - "Zhiyi Zhang"
    - "Zhihong Chen"
    - "Qingying Xiao"
    - "Feng Jiang"
    - "Jianquan Li"
    - "Xiang Wan"
    - "Benyou Wang"
    - "Haizhou Li"
  url: "https://github.com/FreedomIntelligence/CMB"
paper:
  title: "CMB: A Comprehensive Medical Benchmark in Chinese"
  arxiv: "2308.08833"
  url: "https://arxiv.org/abs/2308.08833"
  year: 2023
leaderboard_url: "https://cmedbenchmark.llmzoo.com/static/leaderboard.html"
repo_url: "https://github.com/FreedomIntelligence/CMB"
released: "2023-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    The public CMB-Exam leaderboard (fetched for this page) shows a very wide spread rather than a
    single ceiling: general frontier models sit far from the top (GPT-4 scored in the high 50s to
    low 60s in the leaderboard's own averaged columns), while the highest-ranked entries are
    vendor-submitted, vertical medical-LLM products from Chinese healthcare companies scoring above
    99%. Because those top entries are self-reported by their vendors rather than independently
    reproduced by the CMB team -- the same caveat this repository applies to C-Eval's leaderboard --
    and because the table's column headers did not render unambiguously through this page's
    fetch, no single top_score is recorded here. The gap between general-purpose and
    domain-tuned entries suggests CMB still separates models meaningfully rather than being
    saturated for the models most readers will care about.
contamination:
  risk: medium
  note: >
    CMB-Exam's test-set questions and answers have been public since the August 2023 release, with
    no held-out or refreshed portion noted by the authors, so any model trained afterward could have
    seen them; CMB-Clin's 74 cases are similarly public. No publisher statement about contamination
    mitigation or test-set refresh was found during this research.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "cmb"
  bigbench: ""
  other: ""
tags:
  - domain
  - medical
  - chinese
  - clinical-reasoning
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2308.08833"
    title: "CMB: A Comprehensive Medical Benchmark in Chinese"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2308.08833"
    title: "CMB paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/FreedomIntelligence/CMB"
    title: "FreedomIntelligence/CMB GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/FreedomIntelligence/CMB"
    title: "FreedomIntelligence/CMB dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://cmedbenchmark.llmzoo.com/static/leaderboard.html"
    title: "CMB leaderboard (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmb"
    title: "OpenCompass cmb dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
---

## What it measures

CMB tests medical knowledge and clinical reasoning in a Chinese-language, China-specific medical context, built natively rather than translated because the authors argue medical practice, licensing structure and terminology differ meaningfully by region -- the benchmark also covers traditional Chinese medicine alongside modern biomedicine, which most English-first medical benchmarks omit entirely. It has two parts. CMB-Exam is multiple-choice and multiple-answer questions drawn from real Chinese medical licensing and qualification exams, spanning six major categories (physician, nursing, pharmacist, medical technician, professional-knowledge and postgraduate-entrance exams) split into 28 subcategories. CMB-Clin is a much smaller set of 74 complex clinical cases, each a multi-turn conversation simulating a doctor working through a patient's history, physical examination and diagnosis, testing free-form clinical reasoning rather than multiple-choice recall.

## How it is scored

CMB-Exam is scored as plain accuracy against the exam's own answer key, extracted from generated text with regular expressions; questions mix single-answer and multiple-answer formats, so the paper does not quote one general random-guess baseline. CMB-Clin cannot be scored against a fixed key because answers are free-form clinical dialogue, so the authors grade responses on four dimensions -- fluency, relevance, completeness and medical proficiency -- each rated 1 to 5. The paper reports these ratings both from human experts and from a GPT-4 judge, and states the two correlate at a Spearman coefficient of 0.93, which the authors use to justify GPT-4 as a scalable proxy grader for CMB-Clin in later evaluations.

## Dataset and licence

CMB-Exam totals 280,839 questions across 28 subcategories, split into 269,359 training questions, 280 validation questions (each with an explanation), and 11,200 test questions, sourced from publicly available exam and coursework questions with expert solutions, obtained primarily from Medtiku with permission. CMB-Clin adds 74 clinical cases (208 questions total) extracted from official medical textbooks and screened to remove cases that depend on images the model cannot see. Both the GitHub repository and the Hugging Face dataset card give the licence as Apache-2.0.

## Who publishes it

CMB comes from Xidong Wang, Guiming Hardy Chen, Dingjie Song, Zhiyi Zhang, Zhihong Chen, Qingying Xiao, Feng Jiang, Jianquan Li, Xiang Wan, Benyou Wang and Haizhou Li, based at The Chinese University of Hong Kong, Shenzhen and the Shenzhen Research Institute of Big Data, with Benyou Wang as corresponding author. It appeared on arXiv in August 2023 and at NAACL 2024. The `FreedomIntelligence` GitHub organisation, which also maintains the related HuatuoGPT medical model line, hosts the repository and data, and `cmedbenchmark.llmzoo.com` hosts the public leaderboard.

## Lineage

CMB has no predecessor or successor tracked in this repository. It belongs to the same cluster of 2023-era Chinese evaluation suites as C-Eval and CMMLU, both also in this repository, though CMB is domain-specific to medicine while C-Eval and CMMLU are general knowledge suites; C-Eval's own page notes CMMLU and Gaokao-based benchmarks as related but does not track CMB. FreedomIntelligence's own HuatuoGPT-II model line, evaluated on the public leaderboard, does not have a page here.

## Saturation and contamination

The public leaderboard shows a wide spread rather than a clear ceiling for general-purpose models: GPT-4 sits well down the table (in the high 50s to low 60s in the leaderboard's own average columns), while the top-ranked entries are vendor-submitted, vertical medical-LLM products from Chinese healthcare and AI companies, several scoring above 99% on CMB-Exam. Those top scores are vendor self-reports rather than independently reproduced by the CMB team, the same caveat this repository applies to C-Eval's leaderboard, so they should be read as a ceiling for benchmark-tuned specialist systems rather than for general models. Contamination risk sits at medium: CMB-Exam's test questions and answers have been fully public since the August 2023 release with no stated refresh, so any model trained since then could have seen them, though no publisher statement or independent study of actual leakage was found.

## How to run it

OpenCompass ships CMB as the `cmb` dataset (its generation config resolves to a versioned `cmb_gen_dfb5c4` implementation). No lm-evaluation-harness, HELM or inspect_evals implementation was found during this research. Because CMB-Clin requires a judge model rather than exact-match scoring, numbers depend on which judge a reporter used -- the original paper used GPT-4 -- and are not directly comparable to a run graded by a different judge or by different human raters.

## Reading the numbers

A high CMB-Exam score shows a model can pass Chinese medical licensing-style multiple-choice questions, which is a meaningfully different skill from the free-form clinical reasoning CMB-Clin is designed to test -- check which half of CMB a reported number covers before comparing models. Because the top of the public CMB-Exam leaderboard is dominated by vendor-submitted, domain-tuned systems scoring near-perfect and unverified by the benchmark's own team, an unusually high self-reported score is worth more scepticism than a general frontier model's more modest, but independently observable, result. A CMB-Clin score depends heavily on which judge graded it, so treat scores from different papers as comparable only when they name the same judge model and grading rubric.
