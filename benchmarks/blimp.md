---
id: blimp
name: "BLiMP (Benchmark of Linguistic Minimal Pairs)"
aliases:
  - "Benchmark of Linguistic Minimal Pairs for English"
page_kind: benchmark
category: knowledge
subcategory: "English grammatical acceptability, minimal-pair paradigms"
status: active
summary: "67 automatically generated 1,000-pair paradigms testing whether a model's probabilities favour the grammatical member of a minimal sentence pair -- linguistic knowledge, not task-solving ability."
measures: >
  BLiMP measures what a language model implicitly knows about English grammar, not whether it can
  perform a task. Each of its 67,000 items is a minimal pair: two sentences that differ by only one
  grammatical property -- for example subject-verb agreement, or whether a negative polarity item
  like "any" appears in a context that licenses it -- where one sentence is grammatical and the
  other is not. Rather than asking the model to answer a question or classify anything, BLiMP
  simply checks whether the model's own probability distribution assigns a higher likelihood to the
  grammatical sentence than to its ungrammatical, minimally different counterpart. This makes it a
  diagnostic of linguistic competence acquired implicitly during training, closer to a
  psycholinguistic acceptability-judgment experiment than to a benchmark of task-solving ability
  like question answering; a model can score well on BLiMP while being unable to explain, in words,
  why one sentence is grammatical and the other is not. The 67 paradigms group into 12 broader
  phenomena: anaphor agreement, argument structure, binding, control/raising, determiner-noun
  agreement, ellipsis, filler-gap dependencies, irregular forms, island effects, negative polarity
  item (NPI) licensing, quantifiers, and subject-verb agreement.
task_format: "Forced-choice by probability comparison: for each of 67,000 minimal pairs, compare the log-probability the model assigns to a grammatical sentence against its minimally different ungrammatical counterpart; no explicit answer choice or generation is presented to the model."
metric:
  name: "pairwise accuracy (grammatical sentence assigned the higher probability)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 96.4
  baseline_note: "Random guessing scores 50% on this binary forced choice. The 96.4% figure is the authors' own human-validation agreement rate: 20 independent validators each rated 5 pairs from every one of the 67 paradigms (6,700 judgments total), and 96.4% of majority-vote judgments agreed with the dataset's constructed labels -- a measure of how uncontroversial the contrasts are, not a report of humans doing the same probability-comparison task a model does."
dataset:
  size: 67000
  size_note: "67 paradigms x 1,000 minimal pairs each = 67,000 sentence pairs, grouped into 12 broader linguistic phenomena (anaphor agreement, argument structure, binding, control/raising, determiner-noun agreement, ellipsis, filler-gap, irregular forms, island effects, NPI licensing, quantifiers, subject-verb agreement)."
  url: "https://github.com/alexwarstadt/blimp"
  license: "CC BY 4.0 (per the Hugging Face nyu-mll/blimp dataset card)"
  languages: ["en"]
  modalities: ["text"]
  splits: "no train/test split; all 67,000 pairs form a single evaluation set across 67 configs of 1,000 pairs each"
  public_test_set: true
publisher:
  org: "New York University"
  authors: ["Alex Warstadt", "Alicia Parrish", "Haokun Liu", "Anhad Mohananey", "Wei Peng", "Sheng-Fu Wang", "Samuel R. Bowman"]
  url: "https://github.com/alexwarstadt/blimp"
paper:
  title: "BLiMP: The Benchmark of Linguistic Minimal Pairs for English"
  arxiv: "1912.00582"
  url: "https://arxiv.org/abs/1912.00582"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/alexwarstadt/blimp"
released: "2019-12"
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
  note: "No recent top-model score or dedicated leaderboard was confirmed from a source opened during this research, and no model card currently in this repository cites it, so its standing against current frontier models is not established here. The original paper found contemporary n-gram, LSTM and Transformer models handled morphological phenomena reliably but struggled with subtler semantic and syntactic phenomena such as NPI licensing and island effects; whether that gap has closed for current frontier models was not confirmed from a source opened during this research."
contamination:
  risk: medium
  note: "The dataset's items and labels have been public since 2019, but each pair is machine-generated from a template rather than hand-authored, and correctly favouring grammatical sentences is a capability plausibly learned from broad exposure to grammatical English text generally rather than from these exact 67,000 pairs specifically, which makes contamination a weaker practical concern here than for benchmarks built from unique, hand-written items."
harness:
  lm_eval: "blimp"
  inspect_evals: ""
  helm: "blimp"
  opencompass: ""
  bigbench: ""
  other: "lm-evaluation-harness implements BLiMP as 67 separate paradigm task files (e.g. anaphor_gender_agreement, determiner_noun_agreement_1, passive_1, wh_questions_object_gap) grouped under the shared blimp tag."
tags: ["linguistics", "grammar", "minimal-pairs", "diagnostic", "probing"]
sources:
  - url: "https://arxiv.org/abs/1912.00582"
    title: "BLiMP: The Benchmark of Linguistic Minimal Pairs for English"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1912.00582"
    title: "BLiMP (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/alexwarstadt/blimp"
    title: "alexwarstadt/blimp repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/nyu-mll/blimp"
    title: "nyu-mll/blimp dataset metadata (Hugging Face API)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/blimp"
    title: "lm-evaluation-harness blimp task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/blimp/README.md"
    title: "lm-evaluation-harness blimp task README"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/blimp_scenario.py"
    title: "HELM blimp_scenario.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BLiMP measures what a language model implicitly knows about English grammar, not whether it can perform a task. Each of its 67,000 items is a minimal pair: two sentences differing by only one grammatical property -- for example subject-verb agreement, or whether a negative polarity item like "any" appears in a context that licenses it -- where one sentence is grammatical and the other is not. Rather than asking the model to answer a question or classify anything, BLiMP checks whether the model's own probability distribution assigns a higher likelihood to the grammatical sentence than to its ungrammatical, minimally different counterpart. This makes it a diagnostic of linguistic competence acquired implicitly during training, closer to a psycholinguistic acceptability-judgment experiment than a benchmark of task-solving ability like question answering; a model can score well on BLiMP while being unable to explain, in words, why one sentence is grammatical and the other is not.

The 67 paradigms group into 12 broader phenomena: anaphor agreement, argument structure, binding, control/raising, determiner-noun agreement, ellipsis, filler-gap dependencies, irregular forms, island effects, negative polarity item (NPI) licensing, quantifiers, and subject-verb agreement.

## How it is scored

For each minimal pair, the model is scored correct if it assigns a higher probability to the grammatical sentence than to the ungrammatical one; overall accuracy is the fraction of the 67,000 pairs scored this way, and per-paradigm or per-phenomenon accuracy is reported alongside the aggregate. Because each pair is a binary forced choice, random guessing scores 50%. The authors validated their own grammaticality judgments by having 20 independent human validators each rate 5 pairs from every one of the 67 paradigms (6,700 judgments total) and found 96.4% aggregate agreement, by majority vote, with the dataset's own labels -- a measure of how uncontroversial the constructed contrasts are, not a report of humans doing the same probability-comparison task a model does.

## Dataset and licence

BLiMP totals 67,000 minimal pairs: 67 paradigms of 1,000 pairs each, with all data provided as a single evaluation set rather than split into train/test. Sentences are automatically generated from linguist-crafted grammar templates that sample from a vocabulary of more than 3,000 lexical items, with each template enforcing the morphological, syntactic and semantic restrictions needed to produce a controlled, isolated contrast. The Hugging Face `nyu-mll/blimp` dataset card lists the release under a CC BY 4.0 licence.

## Who publishes it

BLiMP was published as "BLiMP: The Benchmark of Linguistic Minimal Pairs for English" by Alex Warstadt, Alicia Parrish, Haokun Liu, Anhad Mohananey, Wei Peng, Sheng-Fu Wang and Samuel R. Bowman, associated with New York University, appearing in Transactions of the Association for Computational Linguistics (TACL), volume 8. The authors maintain the reference repository and generation scripts at github.com/alexwarstadt/blimp.

## Lineage

BLiMP has no direct predecessor benchmark of its own construction, though it draws on a long tradition of hand-constructed acceptability-judgment tasks in linguistics, and on the same broad idea of automatically generated grammatical minimal pairs that CoLA (the Corpus of Linguistic Acceptability, not yet a page in this repository) applied to naturally occurring rather than templated sentences. No successor or variant id is tracked for BLiMP in this repository.

## Saturation and contamination

No recent top-model score or dedicated leaderboard was confirmed from a source opened during this research, and no model card currently in this repository cites it, so its standing against current frontier models is not established here. The original paper found contemporary n-gram, LSTM and Transformer models handled morphological phenomena reliably but struggled with subtler phenomena such as NPI licensing and island effects; whether that gap has closed for current frontier models was not confirmed here. The dataset's items and labels have been public since 2019, but each pair is machine-generated from a template rather than hand-authored, and favoring grammatical sentences is a capability plausibly learned from broad exposure to grammatical English generally rather than from these exact pairs, making contamination a weaker practical concern here than for benchmarks built from unique, hand-written items.

## How to run it

lm-evaluation-harness implements BLiMP as 67 separate task files (for example `anaphor_gender_agreement`, `determiner_noun_agreement_1`, `passive_1`, `wh_questions_object_gap`) grouped under a shared `blimp` tag, scored by comparing sentence log-likelihoods rather than by prompting the model to answer directly. HELM carries an equivalent `blimp` scenario. Because scoring is purely a likelihood comparison with no prompt or instruction involved, BLiMP is one of the few benchmarks in this repository that does not depend on prompt format, few-shot count or instruction-tuning style, which makes cross-paper comparisons unusually safe as long as both used log-likelihood scoring rather than an instruction-following variant.

## Reading the numbers

A high BLiMP score indicates a model's underlying probability distribution favors grammatical English over closely matched ungrammatical alternatives, which is evidence of linguistic knowledge absorbed during training, not evidence that the model can reason about grammar, explain a rule, or perform any downstream language task well. Look at the per-phenomenon breakdown rather than the aggregate when it is available, since the original paper found sharp unevenness across phenomena, with subtle semantic and syntactic contrasts consistently harder than morphological ones. Because BLiMP tests knowledge a model could plausibly have acquired implicitly from any large corpus of grammatical English, treat it as a check on linguistic competence specifically, not as a general capability or reasoning benchmark.
