---
id: lm_syneval
name: "LM-SynEval (Targeted Syntactic Evaluation of Language Models)"
aliases:
  - "Targeted Syntactic Evaluation of Language Models"
  - "Marvin and Linzen 2018"
page_kind: benchmark
category: knowledge
subcategory: "targeted syntactic minimal pairs (agreement, reflexives, negative polarity items)"
status: active
summary: >-
  72 auto-generated minimal-pair test sets probing whether a model's probabilities favour the
  grammatical sentence for subject-verb agreement, reflexive anaphora and negative polarity items.
measures: >
  LM-SynEval measures what a language model implicitly knows about specific points of English
  syntax, not whether it can perform a task or explain a rule. Each item is a minimal pair of
  sentences differing in one grammatical property -- for example "The author laughs" versus "The
  author laugh" -- and the model is scored by whether it assigns a higher probability to the
  grammatical member of the pair. The pairs are organised into three phenomena: subject-verb
  agreement (tested across many constructions -- across a prepositional phrase, a sentential
  complement, subject and object relative clauses with and without an overt "that", and verb-phrase
  coordination), reflexive anaphora (does the reflexive pronoun's number match its antecedent, again
  tested within simple sentences and across relative clauses), and negative polarity item licensing
  (does "ever" or a similar NPI appear only where a licensing context such as "no" makes it
  grammatical). A model can score well on every construction here while being unable to state, in
  words, the agreement or licensing rule it is implicitly satisfying -- this is a probe of linguistic
  competence, closer to a psycholinguistic acceptability experiment than to a benchmark of
  task-solving ability like question answering.
task_format: >
  Forced-choice by probability comparison: for each minimal pair, compare the model's log-probability
  on the grammatical sentence against its ungrammatical, minimally different counterpart; the harness
  presents exactly two choices per item and no explicit answer or generation is requested.
metric:
  name: "pairwise accuracy (grammatical sentence assigned the higher probability)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Random guessing scores 50% on this binary forced choice (every lm-evaluation-harness item offers
    exactly the grammatical and ungrammatical sentence as its two choices). The original paper
    recruited human participants online and reports that "a large gap remained" between the best
    LSTM model's accuracy and human accuracy, but does not state one single overall human-accuracy
    percentage in the text read for this page, so no human_baseline figure is recorded here.
dataset:
  size: 158084
  size_note: >
    158,084 sentence pairs across 72 leaf task configs (confirmed via the Hugging Face
    datasets-server for the jmichaelov/lm_syneval mirror used by lm-evaluation-harness), grouped
    into 3 phenomena: agreement (the largest group, itself split across roughly 14 construction
    types such as simple agreement, agreement across a prepositional phrase, across a sentential
    complement, across subject/object relative clauses with and without "that", and verb-phrase
    coordination), reflexives (3 construction types) and negative polarity items (4 construction
    types, split by animacy and tense). Per-construction size varies widely, from 200 pairs (e.g.
    long verb-phrase coordination) to over 2,800 (e.g. agreement across an object relative clause).
  url: "https://huggingface.co/datasets/jmichaelov/lm_syneval"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "single 'test' split per construction; no train/validation split"
  public_test_set: true
publisher:
  org: ""
  authors: ["Rebecca Marvin", "Tal Linzen"]
  url: "https://github.com/BeckyMarvin/LM_syneval"
paper:
  title: "Targeted Syntactic Evaluation of Language Models"
  arxiv: "1808.09031"
  url: "https://arxiv.org/abs/1808.09031"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/BeckyMarvin/LM_syneval"
released: "2018-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: ["blimp"]
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The original 2018 paper found that an LSTM language model handled simple constructions well but
    performed poorly on several harder ones (notably agreement across an object relative clause and
    NPI licensing), with multi-task training on CCG supertagging improving but not closing the gap to
    human accuracy. No source opened for this page reported a current transformer-era or frontier-LLM
    score on this specific benchmark, and no model card in this repository was found to cite it, so
    its standing against current models is not established here.
contamination:
  risk: medium
  note: >
    The dataset and its labels have been public since 2018, but every pair is generated automatically
    from linguist-built templates and a fixed vocabulary rather than hand-written or sourced from a
    single external corpus, so favouring grammatical sentences is a capability plausibly learned from
    broad exposure to grammatical English generally rather than from memorising these exact 158,084
    pairs. This mirrors the reasoning this repository applies to the related `blimp` benchmark.
harness:
  lm_eval: "lm_syneval"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The original authors' own repository (BeckyMarvin/LM_syneval) provides the reference generation
    and analysis code, built for evaluating RNN-family models; lm-evaluation-harness's own checklist
    for this task notes explicitly that it has not been checked against that reference implementation
    because the original pipeline targets a different (RNN) model architecture.
tags:
  - linguistics
  - grammar
  - minimal-pairs
  - agreement
  - reflexives
  - negative-polarity-items
  - diagnostic
  - probing
sources:
  - url: "https://arxiv.org/abs/1808.09031"
    title: "Targeted Syntactic Evaluation of Language Models"
    accessed: "2026-09-08"
  - url: "https://github.com/BeckyMarvin/LM_syneval"
    title: "BeckyMarvin/LM_syneval repository (MIT licence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lm_syneval/README.md"
    title: "lm-evaluation-harness lm_syneval README (phenomenon/construction breakdown with examples, citation, checklist)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lm_syneval/_template_yaml"
    title: "lm-evaluation-harness lm_syneval task template (multiple_choice format, doc_to_choice/doc_to_target)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jmichaelov/lm_syneval"
    title: "jmichaelov/lm_syneval dataset metadata (Hugging Face API) -- MIT licence"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=jmichaelov/lm_syneval"
    title: "jmichaelov/lm_syneval datasets-server size endpoint (158,084 rows across 72 configs)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1912.00582"
    title: "BLiMP (Warstadt et al. 2020, full text, ar5iv) -- related-work table citing Marvin and Linzen 2018 for the same three phenomena"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LM-SynEval measures what a language model implicitly knows about specific points of English syntax,
not whether it can perform a task or explain a rule. Each item is a minimal pair of sentences
differing in exactly one grammatical property -- for example "The author laughs" versus "The author
laugh" -- and the model is scored by whether it assigns a higher probability to the grammatical
member. The pairs cover three phenomena: subject-verb agreement, tested across many constructions
(across a prepositional phrase, a sentential complement, subject and object relative clauses with and
without an overt "that", and verb-phrase coordination); reflexive anaphora, testing whether a
reflexive pronoun's number matches its antecedent, within simple sentences and across a relative
clause; and negative polarity item licensing, testing whether a word like "ever" appears only in a
context, such as one introduced by "no", that licenses it. A model can score well on every
construction here while being unable to state, in words, the agreement or licensing rule it is
implicitly satisfying -- this is a probe of linguistic competence, closer to a psycholinguistic
acceptability-judgment experiment than to a benchmark of task-solving ability such as question
answering.

## How it is scored

For each minimal pair, the model is scored correct if it assigns a higher probability to the
grammatical sentence than to the ungrammatical one; lm-evaluation-harness implements this as a
`multiple_choice` task with exactly two options per item, so random guessing scores 50%. Accuracy is
reported per construction (72 in total) and can be aggregated up through each phenomenon (agreement,
reflexives, NPI) to an overall mean. The original paper additionally recruited human participants
online to validate the task and reports that "a large gap remained" between its best LSTM model and
human accuracy, though no single overall human-accuracy percentage was found in the source read for
this page.

## Dataset and licence

The Hugging Face mirror used by lm-evaluation-harness (`jmichaelov/lm_syneval`) totals 158,084
sentence pairs across the 72 individual construction configs, confirmed via the Hugging Face
datasets-server. Per-construction size varies substantially, from 200 pairs for the smallest
construction (long verb-phrase coordination) to over 2,800 for the largest (agreement across an
object relative clause). Sentences are automatically generated from linguist-built templates over a
fixed vocabulary rather than drawn from a naturally occurring corpus. Both the original GitHub
repository and its Hugging Face mirror carry an MIT licence, and all pairs and their correct-answer
labels are public.

## Who publishes it

LM-SynEval was introduced by Rebecca Marvin and Tal Linzen in a paper presented at EMNLP 2018. The
original reference implementation is hosted at github.com/BeckyMarvin/LM_syneval; no organisation
runs an active public leaderboard for it, and lm-evaluation-harness maintains the version most
commonly used to evaluate current models.

## Lineage

LM-SynEval names no predecessor of its own. This repository's `blimp` page (Warstadt et al., 2020,
NYU) is the clearest downstream relative: BLiMP's own related-work table cites Marvin and Linzen 2018
by name specifically for its coverage of subject-verb agreement, anaphor/binding phenomena and
negative polarity items -- the same three phenomena this benchmark tests -- while BLiMP itself scales
the same minimal-pair methodology to 67 paradigms and 12 broader phenomena using fully automatic,
larger-scale generation. The two are separate benchmarks with separate datasets and code, not a
family and a subset of it, but they measure the same underlying kind of thing: probability-based
grammaticality judgment on constructed minimal pairs.

## Saturation and contamination

The original 2018 paper found an LSTM language model handled simple constructions well but performed
poorly on several harder ones, particularly agreement across an object relative clause and NPI
licensing, and that multi-task training with a CCG-supertagging objective improved but did not close
the gap to human accuracy. No source opened for this page reported a current transformer-era or
frontier-model score on this specific benchmark, and no model card in this repository was found
citing it, so its standing against current models is not established here. Contamination risk is
medium: the dataset has been public since 2018, but because every pair is generated from a template
over a shared vocabulary rather than hand-written or drawn from one external source, correctly
favouring grammatical sentences is plausibly a capability learned from broad exposure to grammatical
English generally, not from memorising these specific 158,084 pairs.

## How to run it

lm-evaluation-harness implements the task as `lm_syneval`, made up of 72 individual construction
tasks (for example `lm_syneval__agreement__simple_agrmt__sing_MS_MV`) grouped under three
sub-groups -- `lm_syneval__agreement`, `lm_syneval__reflexives`, `lm_syneval__npi` -- and an overall
`lm_syneval` group, each using unweighted mean aggregation. The harness's own checklist notes that
this implementation has not been checked against the original authors' reference code, because that
code was built to evaluate RNN-family models rather than the prompted, tokenizer-based evaluation
used for current LLMs. No HELM, OpenCompass, inspect_evals or BIG-bench registration was confirmed
during this research.

## Reading the numbers

A high LM-SynEval score says a model's output probabilities are well calibrated to specific,
narrowly defined grammatical contrasts -- not that it can reason about, explain, or apply the
underlying rule in a downstream task, and not that it is broadly grammatical in open-ended
generation. Because scores are reported per construction and phenomenon, an aggregate number can
hide real unevenness: the original paper's own findings show some constructions (simple agreement)
solved far more easily than others (agreement across an object relative clause, NPI licensing), and
that pattern is exactly what the per-construction breakdown is for. Read this benchmark alongside
`blimp` rather than in place of it: the two overlap in what they probe but differ in scale and
construction set, so a strong score on one does not guarantee a strong score on the other.
