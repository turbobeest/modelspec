---
id: headqa
name: HEAD-QA
aliases: ["HeadQA"]
page_kind: benchmark
category: domain
subcategory: "Spanish healthcare civil-service exam question answering, cross-lingual (Spanish/English)"
status: active
summary: "HEAD-QA scores multiple-choice questions from real Spanish healthcare civil-service exams, released in matched Spanish and English versions."
measures: >
  HEAD-QA tests whether a model can answer multiple-choice questions taken from real exams used to award
  specialized positions in the Spanish public healthcare system, set by Spain's Ministerio de Sanidad,
  Consumo y Bienestar Social. Questions cover six subjects -- medicine, nursing, psychology, chemistry,
  pharmacology and biology -- and were written for practicing or aspiring health professionals rather than
  for the benchmark, so they assume applied domain training rather than general knowledge. The dataset
  ships in two matched forms, the original Spanish and a professionally produced English translation,
  letting the same questions be evaluated monolingually or cross-lingually.
task_format: >
  Multiple-choice question with a variable number of answer options; the model reads the question text and
  returns the correct option. Most items are plain text, but a minority carry an accompanying image, and
  text-only harnesses typically evaluate only the text subset.
metric:
  name: "accuracy (and length-normalized accuracy, acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper does not quote one numeric random baseline, since the number of options is not fixed at
    four across every question, nor a physician baseline score; it states only that model results "lag
    well behind human performance."
dataset:
  size: 6765
  size_note: >
    6,765 questions per language (the Spanish original and its English translation cover the same
    questions), split 2,657 train / 1,366 validation / 2,742 test on the EleutherAI/headqa Hugging Face
    mirror that lm-evaluation-harness reads. Six subject categories: medicine, nursing, psychology,
    chemistry, pharmacology, biology, drawn from Spanish civil-service exams from the years leading up to
    the dataset's 2019 release. A separate images/PDFs archive accompanies some questions.
  url: "https://huggingface.co/datasets/dvilares/head_qa"
  license: >
    MIT, per the original aghie/head-qa GitHub repository's LICENSE file and the dvilares/head_qa dataset
    card; the separate EleutherAI/headqa mirror used by lm-evaluation-harness instead lists its own licence
    tag as "other" without further detail, so that specific mirror's terms should not be assumed to be MIT.
  languages: ["es", "en"]
  modalities: ["text", "image"]
  splits: "2,657 train / 1,366 validation / 2,742 test (per language)"
  public_test_set: true
publisher:
  org: "Universidade da Coruña"
  authors: ["David Vilares", "Carlos Gómez-Rodríguez"]
  url: "https://github.com/aghie/head-qa"
paper:
  title: "HEAD-QA: A Healthcare Dataset for Complex Reasoning"
  arxiv: "1906.04701"
  url: "https://arxiv.org/abs/1906.04701"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/aghie/head-qa"
released: "2019-06"
last_updated: ""
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
    No current leaderboard or recent model report was found during this research pass, so a present-day
    top score cannot be stated with a source behind it. HEAD-QA remains a registered task in both
    EleutherAI's lm-evaluation-harness (`headqa_en`/`headqa_es`) and Stanford HELM's scenario library,
    both actively maintained projects, but neither project's own results page was opened here.
contamination:
  risk: high
  note: >
    The question-and-answer set, including test-split answers, has been publicly downloadable without
    gating since 2019. The lm-evaluation-harness task config itself sets `should_decontaminate: true`,
    meaning its maintainers flag HEAD-QA's text as something a training-corpus decontamination check
    should look for.
harness:
  lm_eval: "headqa"
  inspect_evals: ""
  helm: "headqa"
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness registers `headqa_en` and `headqa_es` under the group tag `headqa`, reading the
    EleutherAI/headqa mirror and reporting `acc` and `acc_norm`, zero-shot by default (its task YAML sets
    no few-shot count). HELM's scenario class, `headqa_scenario.py`, reads dvilares/head_qa directly,
    defaults to the text-only subset, and restricts scoring to the test split.
tags: ["medical", "multiple-choice", "spanish", "cross-lingual", "civil-service-exam"]
sources:
  - url: "https://arxiv.org/abs/1906.04701"
    title: "HEAD-QA: A Healthcare Dataset for Complex Reasoning"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/dvilares/head_qa"
    title: "dvilares/head_qa dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/headqa"
    title: "EleutherAI/headqa dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=EleutherAI/headqa"
    title: "EleutherAI/headqa split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/aghie/head-qa"
    title: "aghie/head-qa repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/headqa/headqa_en.yaml"
    title: "lm-evaluation-harness: headqa_en task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/headqa/README.md"
    title: "lm-evaluation-harness: headqa task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/headqa_scenario.py"
    title: "HELM headqa_scenario.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HEAD-QA tests whether a model can answer multiple-choice questions taken from real exams used to award
specialized positions in the Spanish public healthcare system, set by Spain's Ministerio de Sanidad,
Consumo y Bienestar Social. Questions cover six subjects -- medicine, nursing, psychology, chemistry,
pharmacology and biology -- and were written for practicing or aspiring health professionals, not for the
benchmark, so they assume the kind of applied domain training a licensing exam expects rather than
general knowledge. The dataset ships in two matched forms: the original Spanish and a professionally
produced English translation, so the same questions can be scored monolingually or cross-lingually.

Most questions are plain text, but a minority carry an accompanying image (a diagram, chart or clinical
image); text-only harnesses typically evaluate only the text subset, so a reported score usually excludes
image-bearing items unless the reporter says otherwise.

## How it is scored

Models are graded on accuracy: the share of questions answered with the correct option. Because the
number of answer choices is not fixed at four across every question, the paper does not quote a single
random-guessing baseline. lm-evaluation-harness additionally reports `acc_norm`, an accuracy variant that
normalizes each option's log-likelihood by its length before selecting the model's answer, common practice
for multiple-choice tasks whose options vary in token length. Evaluation is zero-shot by default in
lm-evaluation-harness, whose task file sets no few-shot count; HELM's scenario implementation restricts
scoring to the test split.

## Dataset and licence

6,765 questions per language, split 2,657 train / 1,366 validation / 2,742 test on the EleutherAI/headqa
mirror that lm-evaluation-harness reads (the original dvilares/head_qa release carries the same split
sizes). The six subject categories are medicine, nursing, psychology, chemistry, pharmacology and biology,
drawn from Spanish civil-service exams from the years leading up to the dataset's 2019 release. The
authors' GitHub repository carries an MIT LICENSE file, and the dvilares Hugging Face card also tags the
dataset MIT; the separate EleutherAI/headqa mirror used by the harness instead lists its own licence as
"other" without elaborating, so that mirror's terms should not be assumed to match. Test-split answers are
included in the public files; there is no gating.

## Who publishes it

HEAD-QA was introduced by David Vilares and Carlos Gómez-Rodríguez, then at the Universidade da Coruña, in
"HEAD-QA: A Healthcare Dataset for Complex Reasoning," presented at ACL 2019. The authors maintain the
reference data and code at github.com/aghie/head-qa; the Hugging Face mirrors used by lm-evaluation-harness
and HELM are maintained by those respective projects rather than by the original authors, and no dedicated
leaderboard site was found for this page.

## Lineage

HEAD-QA has no formal predecessor, successor or variant catalogued in this repository. It sits in the same
broad space as MedQA and MedMCQA (both also in this repository) as a real-exam medical multiple-choice
benchmark, but was built independently on Spanish rather than US or Indian exam material, and ships a
built-in cross-lingual English translation that those two do not.

## Saturation and contamination

No current leaderboard or recent model report was found during this research pass, so a present-day top
score cannot be stated with a source behind it. HEAD-QA remains a registered task in both EleutherAI's
lm-evaluation-harness and Stanford HELM's scenario library, both actively maintained projects, but neither
project's own results page was opened here, and this repository's own model cards do not carry a headqa
score either. Contamination risk is high: the question-and-answer set, including test-split answers, has
been publicly downloadable without gating since 2019, and the lm-evaluation-harness task config itself
sets `should_decontaminate: true`, flagging HEAD-QA as text its maintainers consider worth checking against
training corpora.

## How to run it

lm-evaluation-harness registers `headqa_en` and `headqa_es` under the group tag `headqa`, reading the
EleutherAI/headqa mirror and reporting `acc` and `acc_norm` zero-shot. HELM's `headqa_scenario.py` reads
the dvilares/head_qa release directly, defaults to the text-only subset (skipping image-bearing questions
unless configured otherwise), and scores only the test split. Because the two harnesses read different
mirrors of the same underlying data and differ in whether they include image-bearing items, a score from
lm-evaluation-harness is not guaranteed to be computed over an identical question set to a HELM score.

## Reading the numbers

A HEAD-QA score reflects a model's grasp of Spanish (or, in translation, English) healthcare
licensing-exam content across six clinical and biomedical subjects, not general medical reasoning in some
other exam format -- compare it to MedQA or MedMCQA scores only loosely, since the source exams, languages
and option counts all differ. Because the dataset has been public for years with test answers included,
and because no fresh leaderboard reading was available for this page, treat a very high score with some
caution about training-data exposure. Check whether the reporter used the Spanish or English form and
whether image-bearing questions were included, since either choice changes what is actually being
measured.
