---
id: legal_support
name: LegalSupport
aliases:
  - "legal support"
  - "HELM LegalSupport"
page_kind: benchmark
category: domain
subcategory: "binary reverse entailment over US case parentheticals"
status: unknown
summary: "HELM binary legal task: choose which of two case parentheticals more strongly supports a passage mined from US opinions."
measures: >
  LegalSupport is a comparative legal-entailment task introduced in HELM.
  Each item is a passage (a legal assertion) plus two parenthetical case
  descriptions. The model must pick the parenthetical that more forcefully
  supports the assertion. Labels come from Bluebook introductory signals
  (for example see versus see also) mined with the parentheticals from US
  state and federal opinions written after 1965, using the Caselaw Access
  Project. Neel Guha designed the scenario. English legal text. Two-way
  multiple choice, not [legalbench](legalbench.md).
task_format: >
  Two references, one tagged correct. HELM default adapter: 3 in-context
  examples, instructions "Which statement best supports the passage?",
  input noun Passage, output noun Answer, method ADAPT_MULTIPLE_CHOICE_JOINT
  unless overridden. Binary A/B.
metric:
  name: "quasi_exact_match (schema); run spec also attaches exact-match metrics"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Two options. The HELM paper says the evaluation set is balanced in how
    often A or B is correct, so uniform chance is 50%. ScenarioMetadata
    names quasi_exact_match; get_legal_support_spec uses
    get_exact_match_metric_specs(). The appendix says accuracy. Report which
    HELM metric column you read. No human baseline is given.
dataset:
  size: 3047
  size_note: >
    HELM paper appendix E.3.9 (arXiv 2211.09110) states train/dev/test splits
    13,862 / 3,125 / 3,047 (20,034 total). Inputs average 137 GPT-2 tokens;
    outputs average 1 token. HELM main_split is test, so 3,047 is the scored
    headline count. The scenario downloads a zip from Google Drive
    (file id in legal_support_scenario.py) with train.jsonl, dev.jsonl and
    test.jsonl. This session did not unpack that zip; counts are from the
    paper.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_support_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "train 13,862 / dev (HELM valid) 3,125 / test 3,047"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors:
    - "Neel Guha"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_support_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/legal_support_scenario.py"
released: "2022-11"
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
    The HELM paper reports 0% for the code models it tried on LegalSupport,
    which is a 2022-era slice, not a current top. No numeric cell was read
    from the JavaScript classic leaderboard. HELM maintenance mode began
    2026-06-01.
contamination:
  risk: medium
  note: >
    Items are mined from public US opinions after 1965 (CAP / case.law) and
    the labelled JSONL has been downloadable from the URL in the scenario
    since the HELM release. Gold labels are in that file. The construction
    uses citation signals rather than a held-out exam, so leakage is
    plausible for models trained on legal web text.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "legal_support"
  opencompass: ""
  bigbench: ""
  other: "Run spec legal_support,method=<adapter>; default ADAPT_MULTIPLE_CHOICE_JOINT, max_train_instances=3. schema_classic lists legal_support under reasoning and under the multiple-choice ablation group."
tags:
  - legal
  - entailment
  - multiple-choice
  - helm
  - reasoning
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/legal_support_scenario.py"
    title: "HELM legal_support_scenario.py (binary parenthetical choice; Drive zip; metadata quasi_exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_legal_support_spec (3-shot MC joint, exact-match metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (LegalSupport group; quasi_exact_match; taxonomy language field listed as synthetic)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML appendix E.3.9 LegalSupport (splits 13862/3125/3047; CAP mining; balanced A/B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (classic leaderboard; maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code, not a dataset licence)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-011 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-011"
---

## What it measures

LegalSupport asks which of two short case descriptions better supports a legal
passage. The passage is an assertion taken from a US opinion. Each option is a
parenthetical that lawyers wrote to explain a citation. The gold label is not a
lawyer's extra annotation of "correct law"; it follows Bluebook introductory
signals that already rank strength of support (for example see ahead of see
also). When a sentence had more than two such supports, the authors sampled
two. English only. Binary choice. It is a HELM targeted reasoning scenario,
not a [legalbench](legalbench.md) task, though Neel Guha is an author of both.

## How it is scored

The default HELM run is three-shot joint multiple choice with the instruction
"Which statement best supports the passage?". schema_classic.yaml headlines
quasi_exact_match on the test split. The run spec attaches
get_exact_match_metric_specs(). The paper appendix calls the metric accuracy
and says the evaluation set is balanced across A and B, so chance is 50%.
Those three names are close but not identical; a quoted number should say
which column it came from. Changing the multiple-choice adapter method is a
documented HELM ablation and will move the score.

## Dataset and licence

Appendix E.3.9 of arXiv 2211.09110 gives 13,862 train, 3,125 development and
3,047 test items (20,034 total), with mean input length 137 GPT-2 tokens. HELM
maps the development file to its valid split and scores test. The scenario
unpacks a Google Drive zip into legal_support/{train,dev,test}.jsonl. Fields
used are context, citation_a.parenthetical, citation_b.parenthetical, and
label in {a,b}. No dataset licence string appears in the scenario, the schema,
or the appendix opened here, so license is left empty. HELM's own code is
Apache-2.0. Opinions come from CAP (case.law); CAP's terms were not opened
for this page.

## Who publishes it

Stanford CRFM released LegalSupport with HELM (arXiv 2211.09110, November
2022). Neel Guha designed and implemented the scenario, as credited in the
paper's author contributions. The classic HELM leaderboard still lists the
name. HELM entered maintenance mode on 2026-06-01. The scenario docstring
points remaining construction questions to nguha@stanford.edu and notes
related then-ongoing legal-reasoning work (later LegalBench).

## Lineage

LegalSupport has no predecessor page in this repository. It is not a
[legalbench](legalbench.md) subset: LegalBench is a 162-task collaboration
from 2023, and the LegalBench HELM scenario file does not name this id.
[legal_summarization](legal_summarization.md) is document summarization.
[lsat_qa](lsat_qa.md) is LSAT analytical reasoning. schema_classic.yaml's
taxonomy line lists language as synthetic; the appendix describes mined real
opinions, not invented prose.

## Saturation and contamination

No current top score was read from a rendered leaderboard. The paper's 0%
figure for code models is a 2022 observation, not a ceiling. Contamination
risk is medium: labels travel with a public zip, and the source opinions are
ordinary published case law. A model that memorised Bluebook signal
conventions could also score well without comparing the two parentheticals.

## How to run it

HELM: `legal_support` (optional `method=` on the multiple-choice adapter).
Default is joint multiple choice with three in-context examples because the
passages are long. Do not compare a joint-scoring run with a separate
per-choice likelihood run. lm-eval and OpenCompass names were not found.
Downloading the Drive zip is required; this page did not verify that the live
file still matches the 2022 split counts.

## Reading the numbers

A score near 50% on the 3,047-item test split is chance on a balanced binary
item. A high score means the model preferred the parenthetical whose
introductory signal was stronger in the original opinion, not that it would
win a motion. It does not measure statutory interpretation, open-ended
drafting, or multilingual law. Pair it with [legalbench](legalbench.md) for
broader legal skills, and say whether the run used joint multiple choice and
three shots.
