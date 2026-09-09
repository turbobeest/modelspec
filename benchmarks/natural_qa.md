---
id: natural_qa
name: "Natural Questions (HELM)"
aliases:
  - "NaturalQA"
  - "NaturalQuestions"
  - "natural_qa_closedbook"
  - "natural_qa_openbook_longans"
  - "natural_qa_openbook_wiki"
page_kind: benchmark
category: knowledge
subcategory: "short-answer QA on real Google queries, with optional Wikipedia context"
status: active
summary: "HELM's Natural Questions wrap: short answers to real Google searches, in closed-book, long-answer-context, or full-Wikipedia-page modes."
measures: >
  This id is HELM's natural_qa scenario (Kwiatkowski et al., TACL 2019),
  not the original NQ long-answer span-selection competition and not
  lm-eval nq_open. Each example is a real anonymized Google query plus a
  Wikipedia page. HELM keeps only items with at least one short answer,
  drops yes/no, and asks the model to generate a short string. Three
  context modes exist: closedbook (question only), openbook_longans
  (annotator long answer as passage), openbook_wiki (title plus full
  page). English text.
task_format: >
  Short-answer generation. HELM Lite run spec natural_qa:mode={closedbook,
  openbook_longans, openbook_wiki}, output noun Answer, max_tokens=300.
  Closed-book uses input noun Question. Main split in the schema is valid;
  metric f1_score.
metric:
  name: "token F1 against the set of short answers (HELM f1_score)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The NQ GitHub README states a human upper bound of 87% F1 on long-
    answer selection and 76% F1 on short-answer selection for the original
    span-selection task. HELM instead generates a free-form short string
    and scores token F1, so those human figures are not copied in as this
    page's human_baseline. No HELM-specific human number was found.
dataset:
  size: 7830
  size_note: >
    Official NQ public release (TACL 2019 abstract): 307,373 train
    (single annotation), 7,830 development (5-way), 7,842 sequestered
    test (5-way). The GitHub README Data Description says 307,372 train;
    the same README's Data Statistics section says 307,373. This page
    follows the TACL figure. HELM downloads only the five official v1.0
    dev shards (nq-dev-00..04.jsonl.gz), keeps examples with at least one
    short answer, and assigns even/odd indices to HELM train/val. The
    post-filter count was not independently counted; 7,830 is the official
    dev size HELM starts from, not HELM's filtered n.
  url: "https://github.com/google-research-datasets/natural-questions"
  license: "Apache-2.0 (repository LICENSE); Wikipedia page text remains under Wikipedia's licence"
  languages:
    - en
  modalities:
    - text
  splits: "Official: train 307,373 / dev 7,830 / hidden test 7,842. HELM: filtered official dev, even/odd into train and valid"
  public_test_set: true
publisher:
  org: "Google Research; HELM scenario by Stanford CRFM"
  authors:
    - "Tom Kwiatkowski"
    - "Jennimaria Palomaki"
    - "Olivia Redfield"
    - "Michael Collins"
    - "Ankur Parikh"
    - "Chris Alberti"
    - "Danielle Epstein"
    - "Illia Polosukhin"
    - "Matthew Kelcey"
    - "Jacob Devlin"
    - "Kenton Lee"
    - "Kristina N. Toutanova"
    - "Llion Jones"
    - "Ming-Wei Chang"
    - "Andrew Dai"
    - "Jakob Uszkoreit"
    - "Quoc Le"
    - "Slav Petrov"
  url: "https://research.google/pubs/pub47761/"
paper:
  title: "Natural Questions: a Benchmark for Question Answering Research"
  arxiv: ""
  url: "https://aclanthology.org/Q19-1026/"
  year: 2019
leaderboard_url: "https://crfm.stanford.edu/helm/lite/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/natural_qa_scenario.py"
released: "2019"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - simpleqa
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    Wei et al. SimpleQA (arXiv 2411.04368, OpenAI blog 2024-10-30) name
    Natural Questions, with TriviaQA, as an older factual-recall set that
    is now saturated. HELM Lite still reports closed-book and open-book
    F1. No HELM top F1 was copied from a rendered leaderboard here, so
    top_score is empty. Status is watch rather than saturated because
    HELM's three modes are not the same number as the 2019 span-selection
    leaderboard.
contamination:
  risk: high
  note: >
    Train and development data have been public since 2019, including
    questions, Wikipedia HTML and short-answer spans. The official test
    set is sequestered behind the NQ competition Docker path; HELM does
    not use that hidden test. Closed-book HELM scores are especially
    exposed to memorization of popular queries.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "natural_qa"
  opencompass: ""
  bigbench: ""
  other: >-
    HELM Lite run spec `natural_qa:mode={closedbook,openbook_longans,openbook_wiki}`.
    Schema groups: natural_qa_closedbook, natural_qa_openbook_longans
    (openbook_wiki is implemented in the scenario but not listed in the
    Lite schema block opened here). lm-eval nq_open is a different
    closed-book protocol and has no page in this repository yet.
tags:
  - question-answering
  - wikipedia
  - helm
  - short-answer
  - google-search
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/natural_qa_scenario.py"
    title: "HELM natural_qa_scenario.py (modes, filters, official dev shards)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/lite_run_specs.py"
    title: "HELM Lite get_natural_qa_spec"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_lite.yaml"
    title: "HELM Lite schema (natural_qa_closedbook / openbook_longans, f1_score)"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research-datasets/natural-questions"
    title: "google-research-datasets/natural-questions README (counts; 76%/87% human F1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-research-datasets/natural-questions/master/LICENSE"
    title: "NQ repository Apache-2.0 LICENSE"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/Q19-1026/"
    title: "TACL 2019 Natural Questions paper (307,373 / 7,830 / 7,842)"
    accessed: "2026-09-08"
  - url: "https://research.google/pubs/pub47761/"
    title: "Google Research pub 47761 (author list)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2411.04368"
    title: "SimpleQA paper (Wei et al.; NQ named as saturated)"
    accessed: "2026-09-08"
  - url: "https://openai.com/index/introducing-simpleqa"
    title: "OpenAI Introducing SimpleQA (30 Oct 2024)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

HELM `natural_qa` is short-answer question answering on Natural Questions.
Questions are real aggregated Google searches. Annotators read a Wikipedia
page and mark a long answer (usually a paragraph) and, when possible, a
short answer (entities or a span). HELM throws away items with no short
answer and asks the model to generate a short string. Closed-book gives
only the question. Open-book long-answer gives the annotator's long
span as a passage. Open-book wiki gives the title and the whole page.

This is not the 2019 long-answer candidate-selection competition, and it
is not lm-eval `nq_open`, which is still without a page here.

## How it is scored

HELM's schema main metric is `f1_score` on the `valid` split: token F1
against the collected short answers (de-duplicated at validation time;
a single randomly chosen short answer at train time). The Lite run spec
`natural_qa:mode=...` uses the generation adapter with `max_tokens=300`
and HELM's F1 plus generative-harms metrics. It does not force
`max_train_instances=0`, so in-context count follows that helper's
default unless a run overrides it. Mode is part of the run name
(`natural_qa:mode=closedbook` and so on). Closed-book and open-book F1
are different tasks.

## Dataset and licence

Kwiatkowski et al. (TACL 2019): 307,373 train, 7,830 development, 7,842
hidden test. The GitHub README Data Description says 307,372 train; its
Data Statistics section says 307,373. HELM never downloads the hidden
test; it uses the five public v1.0 dev files from
`storage.googleapis.com/natural_questions/v1.0/dev`. The GitHub
repository licence is Apache-2.0; Wikipedia HTML still follows
Wikipedia's terms. The repository was archived on 19 April 2026 and is
read-only. HELM's even/odd split of filtered dev is not the official
NQ train/dev cut.

## Who publishes it

Natural Questions is Google Research (TACL 2019; Google pub 47761).
HELM's scenario and Lite/Classic schema entries are Stanford CRFM.
The original competition site still describes a Docker path for the
sequestered test set.

## Lineage

No predecessor in this repository. [TriviaQA](triviaqa.md) is the other
widely reported 2010s open-domain set. [SimpleQA](simpleqa.md) is a later
factual-recall benchmark that names NQ as saturated. [SQuAD](squad.md)
is Wikipedia span extraction with crowd-written questions, not Google
queries. Do not treat future `nq_open` as this HELM id.

## Saturation and contamination

SimpleQA's authors (arXiv 2411.04368) treat NQ as a saturated recall
set. HELM still separates models by mode, but no top F1 is recorded
here. Contamination is high: public questions and answers since 2019,
and HELM evaluates on a public dev slice.

## How to run it

`helm-run` with run spec `natural_qa` and `mode` in
`closedbook`, `openbook_longans`, or `openbook_wiki`. Confirm shot count
and mode before comparing to another HELM number, and do not mix with
lm-eval `nq_open` or with official NQ long-answer F1.

## Reading the numbers

Closed-book F1 is parametric recall of short facts people actually
search. Open-book F1 is reading a provided Wikipedia span or page. A
high closed-book score on a 2019 public dev set is weak evidence of
general factuality in 2026. Prefer [SimpleQA](simpleqa.md) or
[BrowseComp](browsecomp.md) when the claim is current knowledge, and
always name the HELM mode.
