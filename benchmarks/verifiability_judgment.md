---
id: verifiability_judgment
name: "Verifiability Judgment"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "citation verification (statement-to-source support classification)"
status: active
summary: >-
  A HELM scenario that gives a model a generated statement and its cited source and asks it to
  judge whether the source fully, partially, or does not support the statement.
measures: >
  Verifiability Judgment presents a statement, taken from a real generative search engine's
  response, together with the source document it cited, and asks the model to classify the
  citation relationship as "fully supports", "partially supports", or "does not support" the
  statement. It tests whether a model can perform the citation-verification step that underlies
  retrieval-augmented and search-grounded systems: reading a passage and judging whether it
  actually substantiates a specific claim, rather than merely appearing topically related.
task_format: >
  Zero-shot (or few-shot, per HELM's default adapter configuration) text generation: HELM prompts
  the model with the statement and source under instructions to judge support as "fully supports",
  "partially supports" or "does not support", generating up to 10 tokens, and scores the output
  against the human-annotated label with exact match and quasi-exact match.
metric:
  name: "Exact match / quasi-exact match against the human-annotated 3-way label"
  direction: higher_is_better
  unit: "accuracy"
  max_score: 1.0
  random_baseline: 0.333
  human_baseline: null
  baseline_note: >
    Three roughly-defined label categories give a naive uniform-guess baseline near 1/3, though the
    label distribution is imbalanced toward "complete support" (about 73% of the source dataset's
    examples), so a model that always answers "fully supports" would score close to that
    proportion rather than 0.333. No human baseline accuracy figure was found in the sources read
    for this page; the source dataset's labels are themselves derived from human crowdworker
    annotation, which HELM treats as ground truth.
dataset:
  size: 11037
  size_note: >
    11,037 human-annotated statement-source pairs total across an 80/10/10 split: 8,834 train,
    1,106 dev, 1,097 test, per the source GitHub repository's data files. Label counts: train
    6,415 complete / 1,552 partial / 867 no support; dev 830 / 165 / 111; test 797 / 183 / 117.
    HELM's scenario downloads and uses these same train/dev/test splits.
  url: "https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "train (8,834), dev (1,106), test (1,097), as released by the source repository"
  public_test_set: true
publisher:
  org: "Stanford NLP Group (source dataset); Stanford CRFM (HELM implementation)"
  authors:
    - "Nelson F. Liu"
    - "Tianyi Zhang"
    - "Percy Liang"
  url: "https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines"
paper:
  title: "Evaluating Verifiability in Generative Search Engines"
  arxiv: "2304.09848"
  url: "https://arxiv.org/abs/2304.09848"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/verifiability_judgment_scenario.py"
released: "2023-04"
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
    No maintained leaderboard or published per-model score table specifically for this HELM
    scenario was found in the sources read for this page, so saturation status is not established.
    The source paper's own headline finding, that four commercial generative search engines fully
    supported only 51.5% of their sentences on average, describes citation quality of those
    systems' outputs, not model performance at the classification task this benchmark measures.
contamination:
  risk: medium
  note: >
    The full dataset, with gold labels for all three splits, has been publicly available under an
    MIT licence on GitHub since 2023, including the test split HELM evaluates on, so exact
    statement-source-label triples could appear in training data for models trained on broad web
    or GitHub scrapes.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "verifiability_judgment"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - fact-verification
  - citation
  - retrieval-augmented-generation
  - helm
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/verifiability_judgment_scenario.py"
    title: "HELM VerifiabilityJudgementScenario source: label mapping (complete_support/partial_support/no_support), prompt construction, train/dev/test download from source GitHub repo"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM classic_run_specs.py get_verifiability_judgment_spec(): generation adapter, instructions text, max_tokens=10, exact_match and quasi_exact_match metrics"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2304.09848"
    title: "Evaluating Verifiability in Generative Search Engines (Liu, Zhang, Liang, 2023, Findings of EMNLP 2023): defines verifiability via citation recall/precision, evaluates Bing Chat, NeevaAI, Perplexity.ai, YouChat; average 51.5% of sentences fully supported by citations"
    accessed: "2026-09-08"
  - url: "https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines"
    title: "Source repository README and data files: MIT licence, 80/10/10 train/dev/test split (8,834/1,106/1,097), per-split label counts, JSONL data format with query, statement, source text, and judgment fields"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

Verifiability Judgment gives a model a statement, originally produced by a real generative search
engine, together with the source document that engine cited for it, and asks the model to classify
whether the source "fully supports", "partially supports", or "does not support" the statement.
The task isolates the citation-verification step underlying retrieval-augmented generation and
search-grounded answering: it tests reading comprehension for entailment between a specific claim
and a candidate source passage, not whether the model can generate a well-cited answer itself.

## How it is scored

HELM prompts the model with the statement and source text under an instruction to answer with one
of the three support levels, generating up to 10 tokens, and scores the output against the
human-annotated gold label using exact match and quasi-exact match. The three label categories are
unevenly distributed in the source data (complete support makes up roughly 70 to 75% of examples
in each split), so a naive baseline that always predicts "fully supports" would score well above
the 1-in-3 chance level a uniform guess would imply. No human accuracy baseline for this
classification task was found in the sources read for this page.

## Dataset and licence

The underlying dataset holds 11,037 human-annotated statement-source pairs split 8,834 train,
1,106 dev, and 1,097 test, released under an MIT licence in Nelson Liu's GitHub repository
accompanying the paper. Each JSONL record includes the original user query, the generative search
engine's statement, the cited source's metadata (title, author, date, URL) and text, the
crowdworker-assigned support label, and annotator-identified evidence excerpts. HELM downloads and
uses these same splits directly rather than a resampled subset.

## Who publishes it

The source dataset and study come from Nelson F. Liu, Tianyi Zhang and Percy Liang of Stanford,
published as "Evaluating Verifiability in Generative Search Engines" at Findings of EMNLP 2023. The
paper's main contribution was auditing four commercial generative search engines (Bing Chat,
NeevaAI, Perplexity.ai and YouChat) for citation quality; the human judgments collected for that
audit were repurposed by Stanford CRFM as a standalone classification scenario in the HELM
benchmark suite, which is what this page documents.

## Lineage

Verifiability Judgment has no predecessor or successor benchmark tracked in this repository. It is
a HELM-specific repackaging of human annotations originally collected to audit real generative
search engines rather than to train or evaluate general-purpose fact-verification models, so its
label distribution and source-passage style reflect real search-engine outputs from 2023 rather
than a benchmark purpose-built for balanced classification.

## Saturation and contamination

No maintained leaderboard or per-model score table specific to this HELM scenario was found in the
sources read for this page, so whether current models have saturated it is not established. The
source paper's own finding, that the audited search engines fully supported only about half their
sentences with citations, describes those systems' citation behavior rather than a model's accuracy
at this classification task, so it should not be read as a saturation signal for this benchmark.
Contamination risk is medium: the complete dataset with gold labels, including the test split HELM
uses, has been openly available on GitHub since 2023.

## How to run it

Run via HELM's `verifiability_judgment` run spec, which uses `VerifiabilityJudgementScenario` to
build prompts from the source repository's train/dev/test files and a generation adapter that asks
for one of the three support levels in up to 10 tokens, scored with exact match and quasi-exact
match. There is no equivalent task in lm-evaluation-harness, inspect_evals, OpenCompass or
BIG-bench as of the source read for this page; comparing a score to any other citation-verification
benchmark requires checking that the label set and prompting instructions match.

## Reading the numbers

A high score means a model reliably distinguishes whether a source passage actually backs up a
specific claim, a useful proxy for how well a model could self-check citations in a
retrieval-augmented pipeline. Because the label distribution skews heavily toward "complete
support," a raw accuracy number can be inflated by a model that defaults to that answer; comparing
per-class performance or checking against the majority-class baseline gives a more honest read.
The benchmark does not test whether a model can generate accurate citations itself, only whether it
can judge citations that already exist.
