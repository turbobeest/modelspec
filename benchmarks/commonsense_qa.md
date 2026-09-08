---
id: commonsense_qa
name: "CommonsenseQA"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "commonsense multiple-choice question answering"
status: saturated
summary: "A 5-way multiple-choice commonsense test built from ConceptNet relations, designed so questions need world knowledge beyond the immediate text."
measures: >
  CommonsenseQA tests whether a model can answer questions that require general world knowledge
  rather than information available in a supplied passage. Questions were constructed by extracting
  sets of target concepts from ConceptNet that share the same semantic relation to one source
  concept, then having crowd-workers write a question that mentions the source concept and
  discriminates between the target concepts as candidate answers -- a process meant to force
  questions with complex semantics rather than simple keyword association.
task_format: >
  Five-way multiple-choice question answering: one correct answer plus four distractor concepts
  drawn from the same ConceptNet neighborhood, evaluated zero-shot or few-shot with no supporting
  passage. The dataset ships a main "Random split" (train/validation/test) used for most reported
  results, plus a secondary "Question token split" described in the paper for testing
  generalization to unseen question wording.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20.0
  human_baseline: 89.0
  baseline_note: >
    20% is the five-way random-guess rate. The paper reports human performance at 89% and its
    strongest baseline at the time, BERT-large, at 56% accuracy -- a roughly 33-point gap the
    authors used to argue the task required genuine commonsense knowledge rather than surface
    pattern matching.
dataset:
  size: 12102
  size_note: >
    The paper states 12,247 questions were created through the ConceptNet-driven authoring
    process. The current Hugging Face mirror (tau/commonsense_qa), which is the main "Random
    split," totals 12,102 rows: 9,741 train, 1,221 validation and 1,140 test, confirmed via the
    Hugging Face datasets-server. Test-split rows carry an empty answerKey field, confirming labels
    are withheld; the leaderboard historically scored test-set submissions.
  url: "https://huggingface.co/datasets/tau/commonsense_qa"
  license: "MIT, per the Hugging Face dataset card; the reference GitHub repository (jonathanherzig/commonsenseqa) carries no separate LICENSE file"
  languages:
    - en
  modalities:
    - text
  splits: "train (9,741) / validation (1,221) / test (1,140, labels withheld)"
  public_test_set: false
publisher:
  org: "Tel Aviv University; Allen Institute for Artificial Intelligence"
  authors:
    - "Alon Talmor"
    - "Jonathan Herzig"
    - "Nicholas Lourie"
    - "Jonathan Berant"
  url: "https://github.com/jonathanherzig/commonsenseqa"
paper:
  title: "CommonsenseQA: A Question Answering Challenge Targeting Commonsense Knowledge"
  arxiv: "1811.00937"
  url: "https://arxiv.org/abs/1811.00937"
  year: 2019
leaderboard_url: "https://www.tau-nlp.org/commonsenseqa"
repo_url: "https://github.com/jonathanherzig/commonsenseqa"
released: "2018-11"
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
    No current top score was confirmed from a source opened for this page. The official project
    homepage (tau-nlp.org/commonsenseqa), which historically hosted the submission-based test-set
    leaderboard, returned a 404 when checked on 2026-09-08, suggesting the original leaderboard is
    no longer actively maintained. Combined with the benchmark's age (2018), its 89% human ceiling,
    and continued but no longer headline-making use in eval harnesses, this page treats the spread
    among current frontier models as likely collapsed even though no specific figure confirms it.
contamination:
  risk: medium
  note: >
    The train and validation splits, including answers, have been public since 2018 and are
    mirrored widely, so exposure through web-scale pretraining is plausible. The official test
    split's labels are withheld (confirmed empty in the current Hugging Face mirror), but the
    underlying ConceptNet relations and question-authoring method are themselves public, so a model
    could plausibly learn the task's patterns without ever seeing the held-out labels directly. No
    dedicated contamination study was found in the sources read for this page.
harness:
  lm_eval: "commonsense_qa"
  inspect_evals: "commonsense_qa"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - commonsense
  - multiple-choice
  - conceptnet
  - reasoning
sources:
  - url: "https://arxiv.org/abs/1811.00937"
    title: "CommonsenseQA: A Question Answering Challenge Targeting Commonsense Knowledge"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tau/commonsense_qa"
    title: "tau/commonsense_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/jonathanherzig/commonsenseqa"
    title: "jonathanherzig/commonsenseqa GitHub repository"
    accessed: "2026-09-08"
  - url: "https://www.tau-nlp.org/commonsenseqa"
    title: "CommonsenseQA project homepage (returned HTTP 404 on 2026-09-08)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/commonsense_qa"
    title: "lm-evaluation-harness commonsense_qa task"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/commonsense_qa"
    title: "inspect_evals commonsense_qa task"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

CommonsenseQA tests whether a model can answer questions that need general world knowledge rather than information available in a supplied passage -- there is no context paragraph to read, only the question itself. Questions were built by extracting sets of target concepts from ConceptNet that share one semantic relation to a common source concept, then having crowd-workers write a question mentioning the source concept that discriminates between the targets as answer options. The intent was to force complex semantics rather than simple keyword or association shortcuts, since a naive model cannot rely on lexical overlap between the question and the correct option alone.

## How it is scored

Each item is five-way multiple choice -- one correct answer and four ConceptNet-derived distractors -- so random guessing scores 20%. The paper reports human performance at 89% against 56% for its strongest baseline at the time, BERT-large, a roughly 33-point gap the authors used to argue the task demands genuine commonsense knowledge rather than pattern matching. The dataset's main evaluation split is the "Random split" (the one almost all reported scores use); a second "Question token split," which holds out specific question wordings to test generalization, is described in the paper but far less commonly reported.

## Dataset and licence

The paper states 12,247 questions were created through the ConceptNet-driven authoring process. The current Hugging Face mirror of the Random split totals 12,102 rows: 9,741 for training, 1,221 for validation and 1,140 for test. Test-split rows carry an empty answer field in the current mirror, confirming that labels remain withheld; the original leaderboard scored submissions against those hidden labels. The Hugging Face dataset card gives the licence as MIT; the reference GitHub repository carries no separate LICENSE file of its own.

## Who publishes it

CommonsenseQA comes from Alon Talmor, Jonathan Herzig, Nicholas Lourie and Jonathan Berant, associated with Tel Aviv University and the Allen Institute for Artificial Intelligence, published in November 2018 and presented at NAACL 2019. The reference implementation and data live in Jonathan Herzig's GitHub repository; the project's own homepage historically hosted a submission-based leaderboard for the held-out test split.

## Lineage

CommonsenseQA has no predecessor or successor tracked in this repository. It predates and is frequently bundled alongside later commonsense benchmarks such as HellaSwag, PIQA and Social IQa in eval suites, none of which are direct descendants of it, and none of which are covered by a `lineage` link on this page.

## Saturation and contamination

No current top score for CommonsenseQA was confirmed from a source opened for this page. The project's own homepage, which historically hosted the test-set leaderboard, returned a 404 when checked on 2026-09-08, suggesting the original leaderboard is no longer actively maintained -- a similar signal to other benchmarks from this era whose dedicated leaderboards have gone quiet. Combined with the benchmark's age, its 89% human ceiling, and its continued but no longer headline use in eval harnesses, this page treats the spread among current frontier models as likely collapsed even without a specific recent figure to confirm it. Contamination risk sits at medium: the train and validation splits, including answers, have been public since 2018 and are widely mirrored, though the official test labels remain withheld from the public mirror.

## How to run it

lm-evaluation-harness and inspect_evals both implement it as the `commonsense_qa` task; because official test labels are not public, harness runs typically score the validation split rather than reproducing the original leaderboard's hidden-test-set numbers. Scoring can be done either by comparing the log-likelihood of each answer option or by parsing a generated answer letter, and reporters do not always state which they used, which limits exact comparability between papers.

## Reading the numbers

A high CommonsenseQA score indicates a model handles everyday relational commonsense -- the kind of "what usually goes with what" knowledge ConceptNet encodes -- reasonably well, but by 2026 this is true of most competent models, so it mainly separates weak or very small models from everything else rather than distinguishing frontier models from each other. Because the benchmark predates modern instruction-tuned models by several years and its main public split (validation) has been available since 2018, treat an unusually low score from an otherwise capable model as a possible formatting or answer-parsing issue before concluding it lacks commonsense knowledge.
