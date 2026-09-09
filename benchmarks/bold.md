---
id: bold
name: "BOLD (Bias in Open-Ended Language Generation Dataset)"
aliases:
  - "Bias in Open-Ended Language Generation Dataset"
page_kind: benchmark
category: safety
subcategory: "bias in open-ended text generation, read as gaps between demographic groups rather than one score"
status: active
summary: "23,679 Wikipedia-derived prompts across five demographic domains, used to check whether a model's open-ended completions differ in sentiment, toxicity or regard depending on the group named in the prompt."
measures: >
  BOLD tests whether a model's open-ended text completions differ in tone, sentiment or toxicity
  depending on the demographic group named in the prompt, rather than testing whether it gets a
  factual answer right. Each of the 23,679 prompts is a short fragment, extracted from an English
  Wikipedia sentence and truncated to five words plus a group term, that names a profession, a
  gender, a racial or ethnic group, a religious ideology or a political ideology -- for example, a
  sentence beginning "As a nurse, she..." -- which the model is asked to continue. The five domains
  split further into 43 named sub-groups, so completions can be compared group against group within
  a domain, not just averaged overall.
task_format: >
  Open-ended text generation from short prompts (six to nine words), English; there is no reference
  answer, so completions are scored by automatic classifiers rather than matched against a key.
metric:
  name: "sentiment, toxicity, regard, gender polarity and psycholinguistic norms, compared across demographic groups"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    BOLD has no single scalar score or baseline. The paper reports group-wise proportions with
    statistical tests (for example, the share of negative-sentiment completions for female-
    versus male-associated prompts) rather than one model-level number, so no max, random or
    human baseline applies the way it would for an accuracy metric.
dataset:
  size: 23679
  size_note: >
    23,679 prompts across five domains: profession (10,195 prompts, 18 professions), race (7,657,
    4 groups), gender (3,204, 2 groups), political ideology (1,984, 12 ideologies) and religious
    ideology (639, 7 ideologies). The Hugging Face mirror (AmazonScience/bold, confirmed via the
    datasets-server size endpoint) groups these into 7,201 rows, each bundling the prompts for one
    Wikipedia-derived name or entity, which is why its row count is smaller than the prompt count.
  url: "https://huggingface.co/datasets/AmazonScience/bold"
  license: "CC BY-SA 4.0 (GitHub repository and Hugging Face dataset card agree)"
  languages:
    - en
  modalities:
    - text
  splits: "single flat prompt set; no train/dev/test split and nothing is held out"
  public_test_set: true
publisher:
  org: "Amazon Alexa AI"
  authors:
    - "Jwala Dhamala"
    - "Tony Sun"
    - "Varun Kumar"
    - "Satyapriya Krishna"
    - "Yada Pruksachatkun"
    - "Kai-Wei Chang"
    - "Rahul Gupta"
  url: "https://github.com/amazon-science/bold"
paper:
  title: "BOLD: Dataset and Metrics for Measuring Biases in Open-Ended Language Generation"
  arxiv: "2101.11718"
  url: "https://arxiv.org/abs/2101.11718"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/amazon-science/bold"
released: "2021-01"
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
    Saturation in the usual "top models near a ceiling" sense does not apply cleanly, because there
    is no single score to converge on. HELM and inspect_evals both report separate per-metric,
    per-group numbers rather than one ranked value, and neither publishes a consolidated
    leaderboard, so this page leaves saturation status unestablished rather than guess at one.
contamination:
  risk: low
  note: >
    Prompts are drawn from English Wikipedia, which almost every current model has seen in
    training, but there is no correct answer to memorise -- the model continues a sentence, it does
    not recall a fact -- so having seen the source Wikipedia text does not undermine the measurement
    the way memorising a test answer would on an accuracy benchmark.
harness:
  lm_eval: ""
  inspect_evals: "bold"
  helm: "bold"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - bias
  - safety
  - open-ended-generation
  - fairness
  - wikipedia
sources:
  - url: "https://arxiv.org/abs/2101.11718"
    title: "BOLD: Dataset and Metrics for Measuring Biases in Open-Ended Language Generation"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2101.11718"
    title: "BOLD paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/amazon-science/bold"
    title: "amazon-science/bold GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/AlexaAI/bold"
    title: "AmazonScience/bold dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=AmazonScience/bold"
    title: "AmazonScience/bold row counts, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/bold"
    title: "inspect_evals bold task"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/bold_scenario.py"
    title: "HELM bold_scenario.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
---

## What it measures

BOLD tests whether a model's open-ended text completions differ in tone, sentiment or toxicity depending on the demographic group named in the prompt, rather than testing whether it gets a factual answer right. Each of the 23,679 prompts is a short fragment, extracted from an English Wikipedia sentence and truncated to its first five words plus a group term, that names a profession, a gender, a racial or ethnic group, a religious ideology or a political ideology -- for example, a sentence beginning "As a nurse, she..." -- which the model is asked to continue. The five domains split into 43 named sub-groups (18 professions, 4 racial groups, 2 genders, 12 political ideologies, 7 religious ideologies), so completions can be compared group against group within a domain.

The point is not to mark any single completion right or wrong -- there is no reference answer -- but to see whether the distribution of completions a model produces about one group differs systematically from another, in sentiment, toxicity or how the group itself is characterised.

## How it is scored

BOLD has no single headline number. The original paper defines five metrics, each applied to completions and compared across demographic sub-groups rather than collapsed into one figure. Sentiment uses VADER to score each completion from -1 to 1 and reports the share of positive versus negative completions per group. Toxicity uses a classifier (a BERT model in the original paper; inspect_evals substitutes the openly available Detoxify "unbiased" model for lack of access to the original) and reports the fraction flagged toxic per group. Regard, a classifier trained specifically for this kind of study, scores how positively a completion characterises the named group. Gender polarity projects completions onto a male/female word-embedding axis or counts gendered unigrams. Psycholinguistic norms score completions against word lists for valence, arousal, dominance and five basic emotions.

The paper reports group-wise proportions with statistical tests -- for example, a binomial proportion test comparing the share of negative-sentiment completions between female- and male-associated prompts -- rather than a per-model score. A model with a good average toxicity number can still show a large gap between its best- and worst-treated group, which is the actual finding BOLD is built to surface, so any single number from any one metric hides most of what the benchmark measures.

## Dataset and licence

The dataset is a flat set of 23,679 prompts, with no train/dev/test split, split across profession (10,195 prompts), race (7,657), gender (3,204), political ideology (1,984) and religious ideology (639). Prompts were built by taking English Wikipedia sentences that mention a group or profession term in their first eight words, then truncating each to its first five words plus that term. The Hugging Face mirror (`AmazonScience/bold`, published under the AlexaAI organisation and confirmed by its API metadata) groups these into 7,201 rows, one per Wikipedia-derived name or entity, each holding a list of prompts -- hence its smaller row count. Both the GitHub repository and the Hugging Face dataset card give the licence as CC BY-SA 4.0.

## Who publishes it

BOLD comes from Jwala Dhamala, Tony Sun, Varun Kumar, Satyapriya Krishna, Yada Pruksachatkun, Kai-Wei Chang and Rahul Gupta, credited to Amazon Alexa AI with two authors also carrying academic affiliations (UC Santa Barbara, UCLA). It appeared at ACM FAccT 2021, submitted to arXiv in January 2021. Amazon's `amazon-science` GitHub organisation hosts the reference repository and prompt files; there is no maintained public leaderboard.

## Lineage

BOLD has no predecessor or successor tracked in this repository and does not belong to a family page here. It sits alongside BBQ (also in this repository) in the bias-evaluation space, but BBQ tests multiple-choice question answering rather than open-ended generation, so the two are not directly comparable.

## Saturation and contamination

Saturation does not apply cleanly here: there is no single score for top models to converge on, HELM and inspect_evals report separate per-metric, per-group numbers, and neither maintains a consolidated leaderboard, so this page leaves saturation status unestablished. Contamination is also a different question than for an accuracy benchmark: the source Wikipedia text is almost certainly in every current model's training data, but there is no correct completion to memorise, so prior exposure does not undermine the measurement the way memorising a held-out answer would elsewhere.

## How to run it

Both HELM (`bold` scenario) and inspect_evals (`bold` task) download the prompt files and generate one completion per prompt. inspect_evals computes toxicity (via Detoxify), sentiment (via VADER, matching the original) and regard, but omits gender polarity and psycholinguistic norms for lack of an open-source replacement. Because toxicity classifiers change over time and implementations substitute different models, toxicity numbers are not comparable across papers or tools unless they name the same classifier version.

## Reading the numbers

There is no single "BOLD score," so any report that gives one number is already simplifying more than the benchmark supports -- check which metric (sentiment, toxicity, regard) and which groups it covers before reading anything into it. A good average toxicity or sentiment number can still hide a large gap between the best- and worst-treated group in the same run, which is the finding that matters most. Results are English and Wikipedia-derived, so they say nothing about bias in other languages, and the paper itself cautions that Wikipedia's own demographic skew limits how representative the source sentences are, so a clean BOLD result should not be read as a general fairness certification. Finally, check which toxicity classifier a given report used, since HELM, inspect_evals and the original paper do not all use the same one, and scores are only comparable within the same tool.
