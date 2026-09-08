---
id: eus_exams
name: EusExams
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "Basque and Spanish public-service exam multiple-choice QA (civil-service admission tests)"
status: active
summary: "35,727 multiple-choice questions from real Basque public-service admission exams, parallel in Basque (16,774) and Spanish (18,953), from the Latxa evaluation suite."
measures: >
  EusExams tests whether a model can answer the kind of multiple-choice question used in real
  admission exams for Basque public-sector jobs -- civil-service tests set by the Basque Government,
  the public health system Osakidetza, the City Councils of Bilbao and Gasteiz (Vitoria), and the
  University of the Basque Country (UPV/EHU), across roles from administrative assistant to technician
  and nurse. Each question has 2 to 4 answer options (3.90 on average) and one correct answer. Because
  the questions were written for real civil-service candidates rather than for language-model
  evaluation, they draw on general knowledge, procedural and legal/administrative material rather than
  any single narrow skill.
task_format: >
  Multiple-choice question with up to four labelled options (A-D), single correct answer, offered in
  parallel Basque-language and Spanish-language versions of largely the same underlying exams; scored
  by loglikelihood ranking over the (up to four) candidate options.
metric:
  name: accuracy (acc and acc_norm, length-normalised)
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    lm-evaluation-harness always scores each item against four fixed candidate slots (A-D); for the
    minority of items whose underlying exam question offered fewer than four options, the harness fills
    the remaining slot(s) with empty-string candidates rather than dropping them, so a naive four-way
    guess is a reasonable approximation of chance performance even though the true average option count
    is 3.90, not exactly 4. No human baseline is published for this task specifically.
dataset:
  size: 35727
  size_note: >
    35,727 questions across 62 per-institution/per-role configs on the current `HiTZ/EusExams` Hugging
    Face dataset that the harness loads: 18,953 in Spanish (33 configs) and 16,774 in Basque (29
    configs), counted directly from the dataset's own split sizes. The Latxa paper's own headline
    figure for EusExams is 16,774 questions -- which matches this page's Basque-only count exactly, not
    the combined bilingual total -- so the paper's cited size describes the Basque portion specifically;
    the roughly equal-sized Spanish parallel set is present in the released dataset but not separately
    counted in the paper's own text. The dataset's Hugging Face card also carries a notice that a newer
    "EusExams-v2" release exists, with deduplication, regrouping and additional data, which the harness
    task as currently written does not point to.
  url: "https://huggingface.co/datasets/HiTZ/EusExams"
  license: "CC BY-SA 4.0, per the Hugging Face dataset card's licence tag"
  languages:
    - eu
    - es
  modalities:
    - text
  splits: "single `test` split per config; the harness draws its few-shot exemplars from that same test split (excluding the item under evaluation) since no separate train or dev split is released"
  public_test_set: true
publisher:
  org: "HiTZ Center - Ixa, University of the Basque Country (UPV/EHU)"
  authors:
    - "Julen Etxaniz"
    - "Oscar Sainz"
    - "Naiara Perez"
    - "Itziar Aldabe"
    - "German Rigau"
    - "Eneko Agirre"
    - "Aitor Ormazabal"
    - "Mikel Artetxe"
    - "Aitor Soroa"
  url: "https://github.com/hitz-zentroa/latxa"
paper:
  title: "Latxa: An Open Language Model and Evaluation Suite for Basque"
  arxiv: "2403.20266"
  url: "https://arxiv.org/abs/2403.20266"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/hitz-zentroa/latxa"
released: "2024-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 70.22
  as_of: "2024-03"
  note: >
    The Latxa paper's own Table 13 (detailed EusExams results across 14 tested models) gives GPT-4
    Turbo the highest average accuracy at 70.22%, ahead of every open model tested, including the
    paper's own largest model, Latxa 70B, at 50.07%; GPT-3.5 Turbo scored 42.42%. The text notes "Latxa
    13B outperforms GPT-3.5 Turbo in most categories, but Latxa 70B is far from GPT-4 Turbo." This is
    the paper's own one-time comparison rather than a maintained leaderboard, and no more recent,
    independent top score was found, but the roughly 20-point gap between the best open model and GPT-4
    Turbo indicates the benchmark still separates models rather than sitting at a ceiling.
contamination:
  risk: low
  note: >
    The Latxa paper ran a dedicated n-gram contamination analysis (its Table 8) comparing EusExams
    against its own pretraining corpus and reports, at a 1-word overlap threshold, 96.6% of items show
    some overlap, but this collapses to 13.6% at 6-gram, 7.1% at 9-gram, and just 0.1% at 15-gram
    overlap -- on this basis the authors state "we did not observe annotation contamination" for
    EusExams specifically. Against that, the underlying material (public-sector exam questions
    referencing real laws, directives and administrative bodies) is information also findable elsewhere
    on the public web, and the exact released question set has been downloadable since 2024, so
    contamination is not impossible for models trained since then even though this specific measured
    check found no strong signal of it.
harness:
  lm_eval: "eus_exams_es, eus_exams_eu (tag-level groups aggregating 33 and 29 per-institution/per-role tasks respectively, e.g. eus_exams_es_ejadministrativo, eus_exams_eu_osakidetza1e; the shared `eus_exams` yaml every task-specific file includes is a base config, not itself a runnable task or tag, and there is no single group spanning both languages)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - basque
  - spanish
  - knowledge
  - multiple-choice
  - exam-qa
  - civil-service
  - bilingual
  - low-resource
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_exams/README.md"
    title: "lm-evaluation-harness eus_exams task README (task description, citation, tag structure)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_exams/eus_exams"
    title: "lm-evaluation-harness eus_exams base yaml (dataset_path, scoring config, 4-way multiple_choice)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_exams/eus_exams_eu"
    title: "lm-evaluation-harness eus_exams_eu tag file (Basque prompt template)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_exams/eus_exams_es"
    title: "lm-evaluation-harness eus_exams_es tag file (Spanish prompt template)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/eus_exams/utils.py"
    title: "lm-evaluation-harness eus_exams utils.py (process_docs filtering logic)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/EusExams"
    title: "HiTZ/EusExams dataset metadata, Hugging Face API (licence tag, EusExams-v2 notice)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HiTZ/EusExams"
    title: "HiTZ/EusExams per-config row counts, Hugging Face datasets-server (62 configs, 35,727 rows total)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.20266"
    title: "Latxa: An Open Language Model and Evaluation Suite for Basque (arXiv abstract page; venue and submission history)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.20266"
    title: "Latxa full text (ar5iv) -- EusExams size statement, Table 8 contamination analysis, Table 12/13 per-model results"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

EusExams tests whether a model can answer the kind of question used in real admission exams for Basque
public-sector jobs: civil-service tests set by the Basque Government, the public health system
Osakidetza, the City Councils of Bilbao and Gasteiz, and the University of the Basque Country (UPV/EHU),
spanning roles from administrative assistant to technician and nurse. Each question offers 2 to 4
options (3.90 on average) with one correct answer. Because the material was written for real exam
candidates, correctly answering it draws on general knowledge and administrative/legal familiarity
rather than any one narrow skill, and the questions exist in parallel Basque and Spanish versions of
largely the same underlying exams.

EusExams is one of four multiple-choice benchmarks introduced together by the Latxa project (2024) to
evaluate Basque-language models: EusExams (public examinations), EusProficiency (language-proficiency
exams), EusReading (reading comprehension) and EusTrivia (general trivia). None of the other three has
its own page in this repository yet.

## How it is scored

Each item is scored by loglikelihood ranking over four fixed answer slots (A-D), reported as both raw
accuracy and length-normalised accuracy (acc_norm). Because a genuine minority of underlying exam
questions offer fewer than four options, the harness fills unused slots with empty-string candidates
rather than removing them, so scoring always ranks four continuations even when only two or three carry
real text. With no separate training or development split released, few-shot exemplars for a given item
are drawn from the same test split, excluding the item itself.

## Dataset and licence

35,727 questions across 62 per-institution/per-role configurations on the `HiTZ/EusExams` Hugging Face
dataset the harness loads: 18,953 in Spanish across 33 configs and 16,774 in Basque across 29 configs,
both counted directly from the dataset's own split metadata. The Latxa paper's own stated size for
EusExams, 16,774 questions, matches this page's Basque-only count exactly rather than the combined
bilingual total, so the paper's headline figure describes the Basque portion of what is now a larger,
parallel bilingual release. The dataset card also flags that a newer "EusExams-v2" exists, with
deduplication, regrouping and additional data, which the current lm-evaluation-harness task does not
point to. The data is released under CC BY-SA 4.0, with a single public `test` split per configuration
and no held-out answers.

## Who publishes it

EusExams was introduced alongside the Latxa open Basque language model by Julen Etxaniz, Oscar Sainz,
Naiara Perez, Itziar Aldabe, German Rigau, Eneko Agirre, Aitor Ormazabal, Mikel Artetxe and Aitor Soroa
at the HiTZ Center (University of the Basque Country, UPV/EHU), in "Latxa: An Open Language Model and
Evaluation Suite for Basque," accepted to ACL 2024 (posted to arXiv in March 2024). The HiTZ group
maintains the dataset on Hugging Face and the evaluation code as part of the Latxa project repository.

## Lineage

EusExams has no predecessor or successor benchmark of its own in this repository, but it is closely tied
to two sibling pages here. It is one of the "Latxa evaluation suite" datasets (EusExams, EusProficiency,
EusReading, EusTrivia) that [BasqueBench](basque_bench.md) -- a broader, 18-task IberoBench composite
suite for Basque -- reuses unmodified as one of its own components; a BasqueBench score therefore
partly reflects EusExams performance, blended with many other tasks, rather than being a separate
measurement. EusExams is also easy to confuse with [BertaQA](bertaqa.md), a different HiTZ-affiliated
Basque trivia benchmark built from an overlapping set of authors: BasqueBench's own task list includes
a trivia dataset called EusTrivia (also from the Latxa paper) but not BertaQA, and EusExams itself is
about public-examination material, not general trivia. All three pages -- EusExams, BasqueBench and
BertaQA -- should be read as related but distinct HiTZ-affiliated Basque benchmarks rather than
variants of one another.

## Saturation and contamination

The Latxa paper's own detailed results (Table 13, 14 models compared) give GPT-4 Turbo the highest
average EusExams accuracy at 70.22%, roughly 20 points ahead of the paper's own best open model, Latxa
70B, at 50.07%, and well ahead of GPT-3.5 Turbo's 42.42%. This is the paper's one-time comparison, not a
continuously maintained leaderboard, and no more recent top score was found, but the wide spread between
models indicates the benchmark still separates them rather than sitting at a ceiling. Contamination risk
is assessed as low: the paper ran a dedicated n-gram overlap analysis against its own training corpus
(Table 8) and found overlap collapses from 96.6% at 1-gram to just 0.1% at 15-gram, concluding "we did
not observe annotation contamination" for EusExams specifically -- a stronger, more direct check than
most benchmarks in this repository can cite, though the underlying material (public administrative and
legal content) remains findable elsewhere on the web in principle.

## How to run it

lm-evaluation-harness implements EusExams as 62 per-institution/per-role tasks (for example
`eus_exams_es_ejadministrativo`, `eus_exams_eu_osakidetza1e`), each including a shared base
configuration and tagged into one of two language-level groups, `eus_exams_es` (33 tasks) and
`eus_exams_eu` (29 tasks); there is no single group spanning both languages together, and the bare
`eus_exams` file the individual task files include is a shared configuration, not a runnable task
itself. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was found. Because EusExams is
also bundled inside [BasqueBench](basque_bench.md)'s own 18-task suite, a "BasqueBench" score is not the
same measurement as an `eus_exams_eu` or `eus_exams_es` score reported on its own.

## Reading the numbers

A high EusExams score indicates a model can handle the kind of factual, procedural and administrative
material a real Basque public-sector job candidate is tested on, in either Basque or Spanish -- useful
evidence of practical, domain-grounded knowledge rather than abstract reasoning. Because the benchmark
spans 62 separate institution/role configurations bundled into two language groups, an aggregate score
can mask uneven performance across specific exam types; the Latxa paper's own per-category detail (its
Appendix E) shows meaningful variation by category and exam year. Given GPT-4 Turbo's roughly 20-point
lead over the best open model tested, and given EusExams' role as one component inside the broader
BasqueBench suite, always check whether a reported score is from EusExams alone or from BasqueBench's
blended aggregate before comparing it to another.
