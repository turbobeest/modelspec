---
id: legalbench
name: LegalBench
aliases:
  - "LEGALBENCH"
page_kind: benchmark
category: domain
subcategory: legal reasoning
status: active
summary: A collaboratively built suite of 162 tasks, contributed by lawyers and computer scientists, testing six categories of legal reasoning in language models.
measures: >
  LegalBench tests whether a model can perform the kinds of reasoning lawyers actually use, rather
  than treating "legal reasoning" as one undifferentiated skill. Its 162 tasks are organised into
  six categories drawn from how the legal profession itself frames reasoning: issue-spotting (does
  a fact pattern raise a given legal question), rule-recall (state or identify the applicable rule),
  rule-application (explain how a rule applies to facts, with reasoning graded for correctness and
  analysis), rule-conclusion (state the resulting legal outcome), interpretation (parse a contract,
  privacy policy or statute), and rhetorical-understanding (reason about legal argument and judicial
  writing). Inputs are short clauses, fact patterns, questions or case excerpts; most tasks are
  single-turn, English-only, and text-only.
task_format: >
  Varies by task: multiple-choice (35 tasks), open-ended generation (7), binary classification
  (112), and multi-class or multi-label classification (8). Few-shot prompting is standard, using
  0 to 8 in-context demonstrations drawn from each task's own small training split.
metric:
  name: "accuracy, balanced accuracy, F1, or human-graded correctness/analysis (varies by task)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Classification tasks are scored by exact-match, using balanced accuracy because many tasks are
    class-imbalanced. Multi-answer extraction tasks (e.g. identifying several defendants) use F1.
    A handful of generation tasks use custom rules (e.g. sara_numeric counts a prediction correct if
    within 10% of the true tax amount). The 12 rule-application tasks are graded manually by a
    law-trained annotator against a published answer guide, on two separate axes: whether the
    explanation is factually and legally correct, and whether it actually contains analysis rather
    than just restating the rule and the outcome. There is no official random or human baseline; the
    original paper's own study evaluated 20 LLMs from 11 families and reports per-category averages,
    not one combined "LegalBench score."
dataset:
  size: 162
  size_note: >
    162 tasks drawn from 36 distinct source corpora, totalling 91,750 examples (82.5 MB on Hugging
    Face); task size ranges from the minimum of 50 examples up to several thousand, averaging about
    563. Each task ships a small train split (2-8 examples, sized for genuine few-shot prompting)
    and a larger evaluation split, not a conventional large train/test partition.
  url: https://huggingface.co/datasets/nguha/legalbench
  license: >
    Mixed, task by task: most tasks are CC BY 4.0; a smaller number are CC BY-NC 4.0 (e.g. Canada
    Tax Court Outcomes, Consumer Contracts QA), CC BY-SA 4.0 (Definition tasks), CC BY-NC-SA 4.0
    (Learned Hands tasks), MIT (NY Judicial Ethics, Privacy Policy QA, SARA), CC BY-NC (OPP-115) or
    CC BY-NC 3.0 (Privacy Policy Entailment), inherited from each task's original source dataset.
  languages:
    - en
  modalities:
    - text
  splits: "per task: a small few-shot train split (2-8 examples) plus a larger evaluation split"
  public_test_set: true
publisher:
  org: Stanford University, with an interdisciplinary, 40-author collaboration spanning law schools,
    computer science departments and legal practice at institutions including the University of
    Chicago, Harvard Law School, Georgetown University Law Center and others
  authors:
    - Neel Guha
    - Julian Nyarko
    - Daniel E. Ho
    - Christopher Ré
  url: https://github.com/HazyResearch/legalbench/
paper:
  title: "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models"
  arxiv: "2308.11462"
  url: https://arxiv.org/abs/2308.11462
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/HazyResearch/legalbench/
released: "2023-08"
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
    At the paper's August 2023 release, GPT-4 led every category (59.2-89.9% depending on category)
    but was far from a ceiling, especially on rule-application analysis and on harder interpretation
    tasks (e.g. GPT-4 scored 47.8% on the MAUD merger-agreement questions). HELM Lite continues to
    track a 5-task sample of LegalBench (abercrombie, corporate_lobbying,
    function_of_decision_section, international_citizenship_questions, proa) against current models,
    but this repository found no source that aggregates current scores across the full 162-task
    suite, so a present-day, whole-suite saturation call is not established here.
contamination:
  risk: medium
  note: >
    LegalBench is fully public with public labels, and the authors' own datasheet flags the risk
    directly: many tasks are adapted from datasets (CUAD, MAUD, OPP-115, SARA, and others) that were
    already public before LegalBench existed, and the paper itself notes it is "possible that some
    LEGALBENCH tasks leaked into pretraining data" for the commercial models it tested. The
    appendix's "public availability status" table sorts tasks into previously-published, original
    but available, and original-and-unavailable categories specifically so readers can judge this
    per task rather than for the suite as a whole.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "legalbench:subset=<task> (HELM Lite core scenario; HELM Lite runs a 5-task sample —
    abercrombie, corporate_lobbying, function_of_decision_section,
    international_citizenship_questions, proa — not the full 162-task suite)"
  opencompass: ""
  bigbench: ""
  other: >
    The authors' own repository (HazyResearch/legalbench) is the reference harness: it ships a base
    prompt (instructions plus demonstrations) for every task, plus the answer guide used for manual
    grading of rule-application tasks. Anthropic-format prompts (<example> tags) were required to
    get usable output from Claude-1 in the original study, which is itself a reminder that prompt
    format is not neutral across model families on this benchmark.
tags:
  - legal
  - reasoning
  - multiple-choice
  - classification
  - few-shot
  - collaborative-benchmark
sources:
  - url: https://arxiv.org/abs/2308.11462
    title: "LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models"
    accessed: "2026-09-08"
  - url: https://github.com/HazyResearch/legalbench/
    title: "HazyResearch/legalbench (GitHub repository, README)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/nguha/legalbench
    title: "nguha/legalbench dataset card (Hugging Face)"
    accessed: "2026-09-08"
  - url: https://crfm.stanford.edu/helm/lite/latest/
    title: "HELM Lite leaderboard (Stanford CRFM) — core scenarios including LegalBench"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice P"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LegalBench tests whether a model can perform the specific kinds of reasoning lawyers use, rather
than treating "legal reasoning" as one skill. Its 162 tasks are organised into six categories drawn
directly from how the legal profession frames reasoning, following the IRAC framework taught in
American law schools: issue-spotting (does a fact pattern raise a given legal question),
rule-recall (state or identify the applicable rule), rule-application (explain how a rule applies to
a set of facts), rule-conclusion (state the resulting legal outcome), plus two categories outside
IRAC — interpretation (parse a contract, privacy policy or statute) and rhetorical-understanding
(reason about legal argument and judicial writing). Inputs are short clauses, fact patterns,
questions or case excerpts, drawn from areas including contracts, privacy policy, evidence and
corporate and tax law; the benchmark is English-only and skews toward U.S. federal law.

## How it is scored

Most of the 162 tasks are automatically scored: classification tasks use balanced accuracy (many
are class-imbalanced), and multi-answer extraction tasks use F1. A handful of generation tasks use
custom rules, such as accepting a tax-amount prediction within 10% of the true value. The 12
rule-application tasks are the exception: a law-trained annotator manually grades each model
explanation against a published answer guide, on two separate axes — whether it is factually and
legally correct, and whether it actually contains analysis rather than merely restating the rule
and the predicted outcome — because the authors found models often produce conclusory explanations
that are technically correct but analytically empty. There is no single official "LegalBench score"
combining all 162 tasks; the original paper reports per-category averages across 20 models.

## Dataset and licence

The 162 tasks are drawn from 36 distinct source corpora — some pre-existing datasets restructured
for few-shot prompting (e.g. CUAD, MAUD, OPP-115), some previously unpublished data hand-coded by
legal scholars, and some built specifically for LegalBench by its author-contributors. In total the
dataset holds 91,750 examples (82.5 MB), averaging 563 per task with a floor of 50. Every task
carries a small few-shot train split (2-8 examples) rather than a conventional large training set,
by design, since the benchmark targets in-context learning rather than fine-tuning. Licensing is set
per task by its original source: most are CC BY 4.0, with several others under CC BY-NC 4.0,
CC BY-SA 4.0, CC BY-NC-SA 4.0, MIT, CC BY-NC or CC BY-NC 3.0, documented task-by-task in the paper.

## Who publishes it

LegalBench was introduced by a 40-author collaboration led by Neel Guha, Julian Nyarko, Daniel E.
Ho and Christopher Ré (credited as equal contributors), together with Adam Chilton and 35 further
co-authors spanning Stanford, the University of Chicago, Dartmouth, Harvard Law School, the
University of Toronto, Georgetown University Law Center and other law schools and computer science
departments, plus practicing lawyers. The paper, posted to arXiv in August 2023, describes an
August 2022 open call for task contributions, publicised through legal-computing mailing lists and
conferences, with submissions vetted for legal correctness before inclusion. Neel Guha maintains the
dataset and the GitHub repository, and the project states it intends to keep incorporating new
tasks contributed by the legal community.

## Lineage

LegalBench names no single predecessor; the paper positions itself against narrower prior legal NLP
benchmarks such as LexGLUE and against fine-tuning-era efforts, while explicitly citing GLUE,
BIG-bench and HELM's task organisation as inspirations for its own fine-grained, typed structure.
The clearest downstream relationship is with HELM: Stanford's HELM Lite folds LegalBench in as one
of ten core scenarios, running a 5-task sample of it (abercrombie, corporate_lobbying,
function_of_decision_section, international_citizenship_questions, proa) against the models on its
leaderboard — a genuine but partial reuse, not full-suite coverage. Neither LexGLUE nor a
LegalBench-specific successor benchmark has a page in this repository yet.

## Saturation and contamination

At release, GPT-4 led every category the paper measured (59.2% on rule-recall up to 89.9% on
rule-conclusion) but sat well short of a ceiling, especially on rule-application analysis and on the
hardest interpretation tasks — for example, GPT-4 scored only 47.8% on the MAUD merger-agreement
multiple-choice questions. HELM Lite continues to score current models against its 5-task
LegalBench sample, but this repository found no source tracking current scores across the full
162-task suite, so a present-day saturation call is not established here. Contamination risk is
medium: the benchmark is fully public with public labels, several component tasks were already
public before LegalBench existed, and the paper itself flags that commercial models it tested may
already have seen some tasks during pretraining — which is why its own appendix classifies every
task by public-availability status, to let readers weigh this per task.

## How to run it

The authors' own repository (HazyResearch/legalbench) is the reference implementation, shipping a
base prompt per task and, for the 12 rule-application tasks, the manual-grading answer guide used
in the paper. HELM Lite runs a 5-task sample under the scenario name `legalbench`, with individual
tasks addressed as `legalbench:subset=<task>` (for example `legalbench:subset=abercrombie`). No
lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench task list was confirmed to carry
LegalBench. Because prompt format materially changed results in the original study — Claude-1
needed Anthropic-specific `<example>` tag formatting to produce usable output — and because
few-shot demonstration counts vary by task (0 to 8), scores from different harnesses or prompting
setups are not guaranteed to be comparable even on the same task.

## Reading the numbers

A high LegalBench score on a given category says a model is good at that specific kind of legal
reasoning — say, spotting which area of law a fact pattern implicates — not that it is a competent
lawyer across the board; the paper's own point is that "legal reasoning" fractures into distinguishable
skills with different difficulty profiles. A single combined score across the 162 tasks is
uninformative on its own, since it blends categories as different as multiple-choice merger-agreement
interpretation and multi-label privacy-policy classification; look at the category breakdown, or the
individual task, that matches the use case in question. Treat any rule-application "analysis" score
with particular caution unless the grading method (the original manual, answer-guide-based grading,
or some automated substitute) is stated, since that dimension does not reduce to exact-match scoring.
