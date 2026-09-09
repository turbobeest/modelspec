---
id: financebench
name: FinanceBench
aliases: []
page_kind: benchmark
category: domain
subcategory: "open-book financial question answering (SEC filings)"
status: active
summary: Patronus AI's open-book financial QA test of 10,231 questions over 40 companies' public filings; only a 150-question human-graded sample is publicly released with answers.
measures: >
  FinanceBench tests whether a model can answer a financial-analyst-style question about a publicly
  traded company when given the relevant excerpt from that company's own SEC filing or earnings
  report as context. Questions range from simple extraction ("what was Boeing's FY2022 cost of
  goods sold?") to questions requiring a short calculation over reported figures. It is single-turn,
  open-book (evidence is supplied, not retrieved from scratch, in the paper's own "oracle" setting;
  other tested configurations force the model to retrieve the right passage itself from a vector
  store or a long context window), text-only, and English-language.
task_format: >
  Given a question and either a directly supplied evidence excerpt, a retrieved passage, or a full
  document (depending on configuration), the model must produce a short free-text answer, typically
  a figure, a yes/no judgement, or a brief explanation, which is then graded against a human-written
  gold answer.
metric:
  name: "human-graded correct / incorrect / failed-to-answer rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper does not use one automatic metric; two trained human raters classify each of a
    model's answers as "correct answer," "incorrect answer," or "failed to answer" (declined,
    hedged, or clearly wrong reasoning), and reports the percentage in each bucket per model
    configuration. Outside the unrealistic "Oracle" setting (evidence handed to the model directly),
    the paper's own best configuration -- GPT-4-Turbo with a long-context window -- was correct on
    79% of the 150 human-reviewed cases; GPT-4-Turbo with a retrieval system was incorrect or
    refused on 81% of questions. No single official pass/fail threshold or automatic scorer is
    defined, so a "FinanceBench score" from a third party should be checked for which grading method
    it used.
dataset:
  size: 150
  size_note: >
    The full benchmark described in the paper totals 10,231 question/answer/evidence triplets over
    40 US publicly traded companies and 361 filings (10-Ks, 10-Qs, 8-Ks and earnings reports)
    released between 2015 and 2023, split by construction method into 925 domain-relevant questions
    (25 templates, e.g. "did the company pay a dividend"), 1,323 novel-generated questions, and
    7,983 metrics-generated questions computed from 18 base financial-statement metrics. Only a
    150-question sample -- stratified 50/50/50 across those three question types, spanning 32 of the
    40 companies -- is publicly released with gold answers and evidence; the remaining roughly
    10,081 questions and their answers are not public. The open-source sample is what this page's
    size and size_note describe as released; the 10,231 figure is the paper's stated full-benchmark
    size.
  url: https://github.com/patronus-ai/financebench
  license: not established
  languages:
    - en
  modalities:
    - text
  splits: "single 150-question open-source release (all labelled OPEN_SOURCE); no train/validation split; the closed-source majority of the 10,231-question set is not distributed"
  public_test_set: false
publisher:
  org: "Patronus AI, with Contextual AI and Stanford University"
  authors:
    - Pranab Islam
    - Anand Kannappan
    - Douwe Kiela
    - Rebecca Qian
    - Nino Scherrer
    - Bertie Vidgen
  url: https://github.com/patronus-ai/financebench
paper:
  title: "FinanceBench: A New Benchmark for Financial Question Answering"
  arxiv: "2311.11944"
  url: https://arxiv.org/abs/2311.11944
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/patronus-ai/financebench
released: "2023-11"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 79.0
  as_of: "2023-11"
  note: >
    79% correct (GPT-4-Turbo, long-context, non-oracle) is the paper's own best realistic result
    across the 16 model configurations it tested; the fully-oracle setting scores higher but is
    described by the authors as unrealistic for production use. This is a single paper's internal
    comparison, not an independently maintained leaderboard, and this page found no updated public
    tracking of frontier-model scores on FinanceBench since November 2023.
contamination:
  risk: medium
  note: >
    The source filings are all public SEC documents, and the 150-question open-source sample --
    including its gold answers and evidence excerpts -- has been public on GitHub since November
    2023, so that sample specifically is plausible to memorise. The much larger closed-source
    portion (roughly 10,081 of the 10,231 questions) is not publicly distributed, which limits
    contamination for the benchmark as a whole even though the released sample is fully exposed.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: financebench
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - finance
  - question-answering
  - open-book
  - sec-filings
  - domain
sources:
  - url: https://arxiv.org/abs/2311.11944
    title: "FinanceBench: A New Benchmark for Financial Question Answering (Islam et al., arXiv:2311.11944)"
    accessed: "2026-09-08"
  - url: https://github.com/patronus-ai/financebench
    title: "patronus-ai/financebench GitHub repository (README and open-source data)"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/financebench_scenario.py
    title: "HELM financebench_scenario.py (FinanceBenchScenario, HELM benchmark)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/embedding-benchmark/FinanceBench
    title: "embedding-benchmark/FinanceBench dataset card, Hugging Face (repackaged retrieval variant)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FinanceBench asks a model to answer the kind of question a financial analyst poses about a specific
public company: what a reported metric was for a given period, whether a trend held across filings,
or a short derived calculation from figures in a 10-K, 10-Q, 8-K or earnings report. Every question
is paired with a company, a source document, and an evidence excerpt an annotator identified as
sufficient to answer it. The paper frames this deliberately as a "minimum performance standard" --
the questions are meant to be clear-cut for a human analyst with the right document in hand, not
adversarial or ambiguous.

The benchmark is evaluated under several context configurations: an unrealistic "Oracle" setting
that hands the model the exact evidence text, a shared or per-document vector-store retrieval
setting, and a long-context setting that feeds a large portion of the filing directly. Only the
150-question open-source sample -- not the full 10,231-question set the paper describes -- is
publicly distributed with answers.

## How it is scored

FinanceBench has no single official automatic metric. The paper's own evaluation has two trained
human annotators independently classify each model answer as a correct answer, an incorrect answer,
or a failure to answer (a refusal, a hedge, or reasoning that never reaches a usable answer), then
reports the percentage in each bucket, computed over 2,400 manually reviewed answers across 16
model configurations. Results vary sharply by configuration: GPT-4-Turbo used closed-book (no
evidence at all) was correct on only 9% of cases, while the same model with a long-context window
reached 79%, and a retrieval-augmented setup was incorrect or refused on 81% of questions. Because
no standardised automatic scorer is defined, a third-party "FinanceBench accuracy" figure should be
checked for how it grades free-text answers -- HELM's implementation, for instance, is a generation
task without a documented exact-match or LLM-judge scorer stated in its scenario file.

## Dataset and licence

The full benchmark, as described in the paper, comprises 10,231 question/answer/evidence triplets
over 40 US public companies and 361 filings released between 2015 and 2023: 925 domain-relevant
questions from 25 general templates, 1,323 novel-generated questions, and 7,983 metrics-generated
questions built from 18 base financial-statement metrics with variations. Only a 150-question
sample -- stratified evenly across the three question types and covering 32 of the 40 companies --
is released publicly, in `patronus-ai/financebench` on GitHub, alongside the source PDFs and the
paper's own model completions. No LICENSE file or explicit licence statement for the data was found
in the repository or the paper text reviewed for this page, so licence is not established.

## Who publishes it

FinanceBench was published in November 2023 by Pranab Islam, Anand Kannappan, Rebecca Qian, Nino
Scherrer and Bertie Vidgen at Patronus AI, with Douwe Kiela (also affiliated with Contextual AI and
Stanford University). Patronus AI maintains the reference repository and offers to evaluate models
against the full, non-public dataset on request. The repository was last updated in December 2024
and remains unarchived.

## Lineage

FinanceBench has no predecessor or successor benchmark in this repository. Its name is easily
confused with `finbench` (documented separately in this repository at `benchmarks/finbench.md`),
which is an unrelated ten-dataset Kaggle-sourced credit-risk and fraud classification benchmark from
FinPT (Yin et al., 2023) -- a name collision, not a shared lineage. A reader encountering either
"FinanceBench" or "FinBench" in a model card should confirm which of the two is meant: this page
covers Patronus AI's open-book filings QA set; `finbench` covers tabular financial-risk
classification. FinanceBench is also distinct from FinBen, a larger 36-dataset holistic financial
benchmark referenced in `finbench.md`'s own lineage discussion.

## Saturation and contamination

The paper's own results leave real headroom: outside the unrealistic Oracle setting, the best
configuration tested (GPT-4-Turbo, long context) was correct on 79% of the 150-case sample, and the
authors conclude no model examined is reliable enough for unsupervised enterprise use. This is the
paper's own internal comparison rather than a maintained leaderboard, and no independent, current
tracking of frontier-model FinanceBench scores was found, so a present-day saturation read beyond
"open" is not established.

Contamination risk is medium: the source SEC filings are public by law, and the 150-question
open-source sample -- including gold answers and evidence text -- has been downloadable since
November 2023, so that specific sample is plausible to memorise. The much larger held-back portion
of the full 10,231-question set (roughly 10,081 questions) is not publicly distributed, which caps
contamination risk for the benchmark's full intended scope even though the released sample itself is
fully exposed.

## How to run it

The reference data and evaluation notebook live in `patronus-ai/financebench` on GitHub. HELM
implements it as the `financebench` scenario, feeding each question with its evidence's full source
page as context and evaluating as free-text generation; no lm-evaluation-harness, inspect_evals or
OpenCompass implementation was confirmed. Because the paper itself tested closed-book, retrieval,
and long-context conditions with large score swings between them, a reported FinanceBench number is
only comparable to another if both used the same context-supply method.

## Reading the numbers

A high FinanceBench score means a model can extract or compute a specific figure from the right
excerpt of a real financial filing -- useful evidence for retrieval-grounded financial QA, but not a
general test of financial reasoning, since the questions are deliberately designed to be
straightforward once the right evidence is in hand. Because scoring is human-graded rather than
automatic, and the released sample is a 150-question fraction of a much larger private set, treat
any single reported score as approximate and check whether it came from the public sample or from a
vendor's access to the full non-public benchmark. The large gap the paper found between closed-book,
retrieval and long-context configurations for the same underlying model means the context-supply
method matters as much as the model itself -- always check which condition a reported number used
before comparing it to another.
