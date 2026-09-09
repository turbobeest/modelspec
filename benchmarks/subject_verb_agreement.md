---
id: subject_verb_agreement
name: "Subject-Verb Agreement"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "syntactic structure / linguistic probing"
status: active
summary: "Programmatic BIG-bench task that scores whether a model assigns higher probability to the grammatically correct verb form across syntactic constructions with long-distance or nested agreement."
measures: "This task probes whether a language model's internal representations capture the hierarchical (not just linear) structure of sentences, using subject-verb number agreement as the diagnostic. Given a sentence preamble such as 'The keys to the cabinet ...', the model must assign higher probability to the grammatically correct verb form (here, plural 'are') than to the form that would agree with a nearer but grammatically irrelevant noun ('cabinet', which would suggest singular 'is'). Constructions range from trivially adjacent subject-verb pairs to deeply nested relative clauses where multiple intervening nouns of conflicting grammatical number ('attractors') can mislead a model that relies on surface proximity rather than syntactic structure."
task_format: "Two-way forced choice via log-probability comparison: for each item the model's conditional log-probability on the correct verb form is compared against the incorrect form, scored 1 if the correct form is more probable, 0 otherwise, averaged per condition and then across conditions/subtasks."
metric:
  name: "accuracy (mean condition score, 'full')"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: null
  baseline_note: "Each item is a two-way forced choice (correct vs. incorrect verb form) scored via cond_log_prob argmax, so chance performance is 0.5 on any individual condition. The task's own reference implementation reports a 'full' score as the unweighted mean across all subtask-by-condition scores (range 0 to 1). The associated paper (Lakretz et al. 2021) found some current-at-the-time models scored below 0.5 chance level on the hardest nested, grammatical-number-incongruent conditions, while humans scored above chance on the same conditions -- the task's central finding."
dataset:
  size: 32116
  size_note: "32,116 multiple-choice queries total across all English and Italian subtask files in the repository (0 free-text queries), per the task README's auto-generated header. The reference task.py implementation runs a default subset of 12 English subtasks (simple, one/two adverbs, conjoined adverbs, name/noun prepositional-phrase attractors, long nested inner/outer relative clauses, the Linzen (2016) Wikipedia sentences, and two nonce-word sets); Italian and several other subtask files exist but are not run by default and must be enabled by editing task.py. Each subtask sentence has 2 to 8 'conditions' depending on how many nouns' grammatical number can vary."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/subject_verb_agreement"
  license: "Apache-2.0"
  languages: ["en", "it"]
  modalities: ["text"]
  splits: "single set, no train/test split; a '_mini' variant of two subtask files is provided for quick smoke tests"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration), with data from four earlier academic papers"
  authors: ["Marco Baroni", "Stanislas Dehaene", "Théo Desbordes", "Dan Garrette", "Dieuwke Hupkes", "German Kruszewski", "Yair Lakretz", "Tal Linzen", "Ellie Pavlick", "Jason Wei"]
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/subject_verb_agreement"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/subject_verb_agreement"
released: "2022"
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
  note: "No source consulted here gives a recent, dated leaderboard or frontier-model score. The task's motivating research (Lakretz et al. 2021, cited in the README) found that models of that era scored below chance on the hardest nested-attractor conditions, which is the opposite of saturation; whether current models have closed that gap was not established from a primary source here."
contamination:
  risk: high
  note: "All subtask JSON files, including target scores, are published in the BIG-bench GitHub repository and include a canary GUID string intended to flag the data for exclusion from training corpora; several of the underlying datasets (e.g. the Linzen 2016 sentences, drawn from Wikipedia) also predate and circulate independently of BIG-bench. Whether any given model's training pipeline honored the canary was not established here."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "subject_verb_agreement"
  other: ""
tags: ["syntax", "grammar", "linguistics", "programmatic", "probing"]
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/subject_verb_agreement"
    title: "subject_verb_agreement task directory, BIG-bench"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/subject_verb_agreement/README.md"
    title: "subject_verb_agreement README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/subject_verb_agreement/task.py"
    title: "subject_verb_agreement task.py (reference implementation)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game (BIG-bench paper)"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.1016/j.cognition.2021.104699"
    title: "Lakretz, Y., et al. (2021) Mechanisms for handling nested dependencies in neural-network language models and humans. Cognition 213."
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/blob/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

This task tests whether a causal language model's predictions reflect the hierarchical grammatical structure of a sentence, rather than just the linear order of nearby words, using subject-verb number agreement as the probe. In a sentence like "The keys to the cabinet are...", correct agreement requires linking the verb to a subject ("keys") that can be several words away, skipping over an intervening noun ("cabinet") of different grammatical number. The task presents a sentence preamble and asks whether the model assigns higher log-probability to the grammatically correct verb form than to the incorrect one that would agree with the wrong, nearer noun.

Constructions range from simple adjacent agreement up through center-embedded relative clauses with multiple "attractor" nouns of conflicting number, including a set specifically constructed by the task's contributing researchers to isolate nested dependencies where prior work found models perform below chance while humans do not.

## How it is scored

Each item is a binary forced choice: the model's conditional log-probability is computed for both the correct and incorrect verb form given the same preamble, and it scores 1 if the correct form's probability is higher, 0 otherwise (`cond_log_prob` with argmax selection, in the reference `task.py`). Items within a subtask are grouped into "conditions" corresponding to different assignments of grammatical number to the sentence's nouns (for example, a construction with three nouns that can each independently be singular or plural has up to eight conditions). Scores are averaged within each condition, and the task's preferred aggregate score, "full", is the unweighted mean across every subtask-by-condition score, giving a value in [0, 1] where 0.5 is chance on any individual two-way comparison.

The task's motivating finding, from Lakretz et al. (2021), is that on the hardest "incongruent" nested conditions (where the outer and inner nouns' grammatical numbers disagree), some contemporaneous models scored below the 0.5 chance level on the inner dependency, while human participants scored above chance on the same conditions -- evidence that those models were not resolving the sentence's hierarchical structure so much as picking up on a spurious cue.

## Dataset and licence

The task directory's own auto-generated header reports 32,116 multiple-choice queries across all English and Italian subtask JSON files it contains. The reference `task.py` implementation, however, runs a default subset of 12 English subtasks (simple adjacent agreement; one and two intervening adverbs; conjoined adverbs; name and noun prepositional-phrase attractors; long nested inner and outer relative clauses; the 500 Linzen et al. (2016) Wikipedia sentences; and two nonce-word sets), and two Italian nested-clause subtasks plus several other English variants (including "short" nested clauses) are present as files but not run unless a user edits the task's subtask list. Data comes from four earlier academic papers (Lakretz et al. 2019, Lakretz et al. 2021, Linzen et al. 2016, Gulordava et al. 2018) whose templated or nonce sentences the task's authors adapted; the repository is licensed Apache-2.0.

## Who publishes it

The task was contributed to BIG-bench by Marco Baroni, Stanislas Dehaene, Théo Desbordes, Dan Garrette, Dieuwke Hupkes, German Kruszewski, Yair Lakretz, Tal Linzen, Ellie Pavlick and Jason Wei, and appears in the BIG-bench collaboration's 2022 paper "Beyond the Imitation Game." There is no independent leaderboard beyond the auto-generated performance plots checked into the task's `results/` directory.

## Lineage

The task has no family page, predecessor or successor confirmed from a primary source in this repository. It is directly built on four earlier, separately published psycholinguistic datasets and papers (cited above), which this task's README names explicitly as its data sources rather than as related-but-distinct benchmarks.

## Saturation and contamination

No dated, current leaderboard or frontier-model score was found in the sources reviewed here, so saturation status is unknown; the task's motivating research documented sub-chance performance on its hardest conditions in 2021-era models, the opposite of a saturated benchmark, and whether that gap has since closed was not established. Contamination risk is high: every subtask file, including correct target scores, is openly hosted on GitHub with a canary string meant to flag it for training-data exclusion, and some source material (such as the Linzen et al. 2016 Wikipedia-derived sentences) is independently public as well.

## How to run it

The task runs through BIG-bench's programmatic task interface (a Python `task.py`, not a pure JSON task) as `subject_verb_agreement`, with the runnable subtask list hardcoded in `task.py`'s `__init__` and requiring a source edit to change which subtasks or languages run. This task was not found in the lm-evaluation-harness's dynamically generated BIG-bench task list (which draws from the `hails/bigbench` Hugging Face mirror of JSON-only tasks), nor was an inspect_evals, HELM or OpenCompass integration confirmed from a primary source for this page; as a programmatic, log-probability-based task it is not well suited to harnesses that only support generation or multiple-choice-from-JSON evaluation.

## Reading the numbers

A high aggregate score suggests a model reliably prefers grammatically correct verb agreement even when a nearer, conflicting-number noun is present, which the task's authors treat as evidence of hierarchical sentence processing rather than shallow linear pattern matching. Because the "full" score averages across many subtasks of very different difficulty, a respectable aggregate can mask near-chance or below-chance performance on the specific nested, incongruent-number conditions the underlying research identified as most diagnostic -- look at the per-condition breakdown, not just the aggregate, before concluding a model has "solved" hierarchical agreement. The task also requires access to token-level conditional log-probabilities, so it cannot be run as-is against models that only expose generated text.
