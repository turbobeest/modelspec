---
id: lambada
name: "LAMBADA"
aliases: ["LAMBADA dataset", "Word prediction requiring a broad discourse context"]
page_kind: benchmark
category: reasoning
subcategory: "broad-context word prediction"
status: active
summary: "A last-word-prediction test built from narrative passages that humans can only complete correctly after reading the whole passage, not just the final sentence."
measures: >
  LAMBADA gives a model a narrative passage -- several sentences of context plus one final "target"
  sentence with its last word removed -- and asks it to predict that missing word. Passages were
  filtered so human readers shown only the final sentence could not guess the word, while readers
  shown the whole passage could. Succeeding therefore requires tracking information across the
  broader discourse -- who is speaking, what was named earlier, what the scene is -- rather than
  relying on local, sentence-level statistics, which is why the original paper frames it as testing
  "genuine understanding of broad context."
task_format: "Language modelling / cloze: passage with its final word withheld in, a single predicted word out, scored as next-token prediction under a causal language model rather than multiple choice."
metric:
  name: "accuracy (next-word exact match); perplexity also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No fixed random baseline applies to open-vocabulary next-word prediction. The original 2016 paper
    reports that none of several contemporary language models exceeded 1% accuracy on the task at
    publication; no controlled human-accuracy figure is given beyond the two-stage filtering
    criterion used to build the dataset (full-passage guessable, final-sentence-only not guessable).
dataset:
  size: 5153
  size_note: >
    10,022 narrative passages total, split into 4,869 development and 5,153 test passages (the count
    recorded here), drawn from 1,331 and 1,332 disjoint novels respectively. Passages were filtered
    from an initial 200,000 candidates down to items every annotator answered correctly given the
    full passage and incorrectly given only the final sentence. A separate 2,662-novel, 203-million-
    word release provides full book text -- not further passages -- as background training corpus for
    language models under test, disjoint from the dev/test novels; the Hugging Face mirror's `train`
    split of 2,662 rows corresponds to these full novels. A reformatted `lambada_openai` variant (see
    How to run it) keeps the same 5,153-passage test count.
  url: "https://huggingface.co/datasets/cimec/lambada"
  license: "CC BY 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (2,662 rows, full novels used as background corpus, not eval passages), validation (4,869), test (5,153)"
  public_test_set: true
publisher:
  org: "University of Trento (CIMeC); University of Amsterdam"
  authors: ["Denis Paperno", "Germán Kruszewski", "Angeliki Lazaridou", "Quan Ngoc Pham", "Raffaella Bernardi", "Sandro Pezzelle", "Marco Baroni", "Gemma Boleda", "Raquel Fernández"]
  url: "https://zenodo.org/records/2630551"
paper:
  title: "The LAMBADA dataset: Word prediction requiring a broad discourse context"
  arxiv: "1606.06031"
  url: "https://arxiv.org/abs/1606.06031"
  year: 2016
leaderboard_url: ""
repo_url: "https://zenodo.org/records/2630551"
released: "2016-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 86.4
  as_of: "2020-05"
  note: >
    The GPT-3 paper (Brown et al., 2020) reports 86.4% few-shot accuracy, calling it "a gain of 8%
    over the previous state of the art" (68.0%, zero-shot); GPT-3's own zero-shot and one-shot
    settings scored 76.2% and 72.5%. No model card in this repository's corpus carries a lambada
    score, and no more recent large-scale published number was found during this research, consistent
    with the benchmark having fallen out of frontier system-card reporting after around 2020 -- treat
    this as the most recent sourced reading rather than a current one.
contamination:
  risk: high
  note: >
    Passages and their target words have been openly downloadable since 2016, and GPT-3's own paper
    explicitly states "the LAMBADA dataset appears to be present in our training data," while arguing
    its own contamination analysis suggests limited score inflation from that overlap. Given the
    dataset's age and its ubiquity as a standard eval set mirrored across many corpora, assume any
    model trained on a broad web or books crawl after 2016 has likely seen these exact passages.
harness:
  lm_eval: "lambada_standard, lambada_openai (grouped under a lambada tag)"
  inspect_evals: ""
  helm: ""
  opencompass: "lambada"
  bigbench: ""
  other: ""
tags: ["language-modelling", "cloze", "long-range-dependency", "zero-shot", "narrative"]
sources:
  - url: "https://arxiv.org/abs/1606.06031"
    title: "The LAMBADA dataset: Word prediction requiring a broad discourse context (Paperno et al., 2016)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1606.06031"
    title: "LAMBADA paper, full text (ar5iv HTML)"
    accessed: "2026-09-08"
  - url: "https://zenodo.org/records/2630551"
    title: "The LAMBADA dataset, Zenodo record (original release)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cimec/lambada"
    title: "cimec/lambada dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/lambada_openai"
    title: "EleutherAI/lambada_openai dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/lambada"
    title: "lm-evaluation-harness lambada task (lambada_standard, lambada_openai)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/lambada"
    title: "OpenCompass lambada dataset config"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2005.14165"
    title: "Language Models are Few-Shot Learners (GPT-3 paper, Brown et al., 2020) -- LAMBADA results and contamination note"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LAMBADA gives a model a narrative passage -- several sentences of context followed by a final
sentence with its last word removed -- and asks it to predict that missing word. The passages, drawn
from a large collection of unpublished novels, were filtered by a two-stage human test: an annotator
shown only the final sentence had to fail to guess the missing word, while an annotator shown the
whole passage had to succeed. That construction is deliberate: local, sentence-level statistics are
not enough, so a model has to track who is speaking, what was named earlier, and what situation the
scene describes across the broader discourse to get the word right. It is English narrative text
only, evaluated as free next-word prediction rather than a multiple-choice task.

## How it is scored

Models are scored as next-token predictors: given the context up to the missing word, accuracy is
the fraction of passages where the model's highest-probability next token exactly matches the true
word (perplexity over that same prediction is also commonly reported). There is no partial credit
and no answer-choice list. The task has two harness variants that are not directly comparable:
`lambada_standard` loads the original passages verbatim, while `lambada_openai` uses OpenAI's
reformatted version of the same passages (introduced for the GPT-2 and GPT-3 papers, with light
detokenization differences); both keep the same 5,153-passage test count, but a model's accuracy can
differ by a few points between them depending on tokenization sensitivity, so two reported LAMBADA
numbers are only comparable once you know which variant produced them.

## Dataset and licence

The dataset consists of 10,022 narrative passages -- 4,869 for development and 5,153 for test --
drawn from 1,331 and 1,332 disjoint novels respectively, filtered down from an initial 200,000
candidate passages judged by Amazon Mechanical Turk workers under the two-stage criterion above. A
separate "training data" release supplies the full text of 2,662 further novels (203 million words),
disjoint from the dev/test novels, intended as background corpus for language models under test
rather than additional eval passages; the Hugging Face mirror's `train` split of 2,662 rows
corresponds to these full novels, not further cloze items. Hugging Face lists the dataset under a CC
BY 4.0 licence; the original Zenodo archive (published 2016-08-07, coinciding with the paper's ACL
2016 presentation) did not display a licence in the page content this research could read, so that
reading is not independently confirmed against the primary host.

## Who publishes it

LAMBADA was introduced by Denis Paperno, Germán Kruszewski, Angeliki Lazaridou, Quan Ngoc Pham,
Raffaella Bernardi, Sandro Pezzelle, Marco Baroni and Gemma Boleda at the University of Trento's
Center for Mind/Brain Sciences, with Raquel Fernández at the University of Amsterdam, presented at
ACL 2016. The dataset is archived on Zenodo under the original authors' account rather than a
maintained leaderboard; no organisation currently runs a live LAMBADA leaderboard. It is kept usable
today mainly through inclusion in general-purpose evaluation harnesses.

## Lineage

LAMBADA has no named predecessor or formal successor benchmark. It predates the modern
instruction-following and reasoning benchmark families by several years and belongs to an earlier
generation of pure language-modelling evals, built to probe a specific linguistic phenomenon --
long-range discourse dependency -- rather than general task-solving ability. No variant or
descendant benchmark carrying the LAMBADA name has its own page in this repository.

## Saturation and contamination

LAMBADA saturated early relative to today's models. GPT-3's paper (Brown et al., May 2020) reported
86.4% few-shot accuracy, an 8-point jump over the prior published state of the art (68.0%), with
GPT-3's own zero-shot and one-shot settings at 76.2% and 72.5%. No later, larger-scale published
number was found during this research: the benchmark has largely fallen out of frontier system-card
reporting since around 2020, and no model card in this repository's own corpus currently carries a
lambada score. Contamination risk is high: the passages and answers have been public since 2016, are
widely mirrored, and GPT-3's own paper explicitly notes the dataset "appears to be present" in its
training data, so any model trained on a broad web or books crawl since then should be assumed to
have seen these exact passages.

## How to run it

lm-evaluation-harness ships both variants under its `lambada` tag: `lambada_standard` (loading
`cimec/lambada`) and `lambada_openai` (loading `EleutherAI/lambada_openai`, which also ships
translated `de`/`es`/`fr`/`it` configs for a multilingual variant OpenAI produced). OpenCompass
carries its own `lambada` config. Both harness tasks score loglikelihood-based accuracy and
perplexity rather than free generation, so results depend on exact tokenization and are sensitive to
whether a model's tokenizer splits the target word the same way the reference implementation
expects.

## Reading the numbers

A high LAMBADA score shows a model can maintain discourse-level context -- tracking a referent or
scene across several sentences -- well enough to predict a final word that local statistics alone
would not give away; a model scoring near zero is failing at basic long-range coherence. Given the
dataset's age, public availability since 2016, and near-universal presence in pretraining corpora, a
strong score today says very little about a model's current capability relative to its
contemporaries, and next to nothing about contamination-free understanding. Prefer a newer, actively
curated long-context or discourse-comprehension benchmark for any claim about a current model, and
check whether a reported number used the `standard` or `openai` passage variant before comparing it
to another.
