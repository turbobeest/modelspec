---
id: unscramble
name: "Unscramble"
aliases:
  - "Word Scrambling and Manipulation Tasks"
page_kind: benchmark
category: reasoning
subcategory: "character-level word manipulation (anagrams, letter cycling, reversal, de-noising)"
status: active
summary: >-
  A battery of 5 character-manipulation tasks from the GPT-3 paper that asks a model to recover an
  original word from a scrambled, cycled, reversed, or noise-inserted version of it.
measures: >
  Unscramble presents a distorted English word and asks the model to produce the original word.
  The distortion is one of five kinds: letters cycled within the word, all letters but the first
  and last shuffled, all letters but the first two and last two shuffled, random punctuation or
  spaces inserted between letters, or the whole word spelled backwards. Solving it requires
  character-level manipulation on top of knowing the target vocabulary word, a skill the GPT-3
  paper framed as a proxy for on-the-fly symbolic pattern recovery rather than a test of world
  knowledge.
task_format: >
  Few-shot, open-ended generation: the model is given a scrambled word and must generate the
  original word, stopping at a newline. lm-evaluation-harness implements it as 5 separate
  generate_until tasks (anagrams1, anagrams2, cycle_letters, random_insertion, reversed_words)
  grouped under the "unscramble" tag, each scored independently with exact string match against
  the target completion. The GPT-3 paper evaluated all 5 with 100 in-context examples (K=100).
metric:
  name: "Exact match (generated word equals target word, case- and punctuation-sensitive)"
  direction: higher_is_better
  unit: "accuracy"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random-chance baseline applies since the task is open-ended generation, not multiple
    choice. No human baseline figure was found in the sources read for this page.
dataset:
  size: 10000
  size_note: >
    10,000 examples per sub-task (50,000 total across the 5 tasks), drawn from the 10,000 most
    frequent English words, per the GPT-3 paper (section on synthetic and qualitative tasks). The
    lm-evaluation-harness configs load each sub-task from a distinct config of the
    EleutherAI/unscramble Hugging Face dataset (e.g. mid_word_1_anagrams, cycle_letters_in_word,
    reversed_words) and evaluate on that dataset's "validation" split.
  url: "https://huggingface.co/datasets/EleutherAI/unscramble"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Each of the 5 dataset configs exposes a single split used by the harness as its test split, named \"validation\""
  public_test_set: true
publisher:
  org: "OpenAI (original task, GPT-3 paper); EleutherAI (dataset repackaging and lm-evaluation-harness implementation)"
  authors:
    - "Tom B. Brown"
    - "Benjamin Mann"
    - "Nick Ryder"
    - "Melanie Subbiah"
  url: "https://github.com/openai/gpt-3"
paper:
  title: "Language Models are Few-Shot Learners"
  arxiv: "2005.14165"
  url: "https://arxiv.org/abs/2005.14165"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/unscramble"
released: "2020-05"
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
    The GPT-3 paper reported wide variance across the 5 sub-tasks for GPT-3 175B (roughly 0.4% on
    reversed words to 67% on random insertion), showing the sub-tasks differ hugely in difficulty
    and were far from saturated in 2020. No maintained leaderboard tracking current frontier-model
    scores on this exact task set was found for this page, so present-day saturation is not
    established.
contamination:
  risk: medium
  note: >
    The underlying word lists and generation scripts have been public since 2020 in the OpenAI
    GPT-3 repository and are re-hosted on the Hugging Face Hub, so the fixed 10,000-word-per-task
    item sets could appear in training corpora. Because items are generated deterministically from
    a fixed frequency-ranked word list rather than curated by hand, memorising the word list (not
    just the exact scrambled instances) could also inflate scores.
harness:
  lm_eval: "unscramble"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    "unscramble" is a tag in lm-evaluation-harness grouping 5 separate tasks (anagrams1, anagrams2,
    cycle_letters, random_insertion, reversed_words), each with its own generate_until config and
    exact_match metric; running the tag reports all 5 scores rather than a single averaged number.
tags:
  - character-manipulation
  - anagrams
  - gpt-3
  - synthetic
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/unscramble"
    title: "lm-evaluation-harness unscramble task directory (README and 5 task YAML files)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/unscramble/anagrams1.yaml"
    title: "anagrams1.yaml: dataset_path EleutherAI/unscramble, dataset_name mid_word_1_anagrams, generate_until, exact_match, version 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/unscramble/cycle_letters.yaml"
    title: "cycle_letters.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/unscramble/reversed_words.yaml"
    title: "reversed_words.yaml task config"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2005.14165"
    title: "Language Models are Few-Shot Learners (GPT-3 paper), Word Scrambling and Manipulation Tasks subsection: 5 task definitions, 10,000 examples per task drawn from the top 10,000 most frequent words, K=100 few-shot, GPT-3 175B per-task accuracy"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/unscramble"
    title: "EleutherAI/unscramble dataset card on Hugging Face Hub (license: other, requires dataset scripting to load)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/gpt-3/tree/master/data"
    title: "openai/gpt-3 repository data directory listing the original .jsonl.gz files for each word-scramble task"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

Unscramble gives a model a distorted English word and asks it to recover the original spelling.
The distortion takes one of five forms: letters cycled around the word, all letters but the first
and last shuffled (an anagram), all letters but the first two and last two shuffled, random
punctuation or spaces inserted between every letter, or the word spelled entirely backwards. The
GPT-3 paper introduced these tasks as a way to probe a narrow, on-the-fly symbolic manipulation
skill distinct from factual recall: the model must both recognise a target word inside noisy
character soup and apply a consistent character-level transformation rule it infers from few-shot
examples.

## How it is scored

Each of the 5 sub-tasks is scored independently with exact string match between the model's
generated completion and the target word, case- and punctuation-sensitive. There is no partial
credit for a near-miss spelling. Because the task is open-ended generation rather than multiple
choice, there is no meaningful random baseline; the GPT-3 paper evaluated with 100 in-context
examples (K=100) rather than zero-shot, and reporting under a different shot count is not directly
comparable.

## Dataset and licence

Each sub-task draws 10,000 examples from the 10,000 most frequent English words, distorted by a
fixed procedure specific to that sub-task (cycling, partial anagram, random insertion, or
reversal). The lm-evaluation-harness implementation loads each sub-task from its own config of the
EleutherAI/unscramble Hugging Face dataset (for example mid_word_1_anagrams for the anagrams1
task, cycle_letters_in_word for cycle_letters), evaluating on that dataset's single "validation"
split. The Hugging Face dataset card lists its licence as "other" without further detail; no more
specific licence text was found in the source read for this page.

## Who publishes it

The task originates from OpenAI's "Language Models are Few-Shot Learners" (GPT-3) paper (Brown et
al., 2020), which introduced it as one of several synthetic and qualitative tasks used to probe
GPT-3's few-shot abilities. The original data files were released in OpenAI's now-archived
`openai/gpt-3` GitHub repository. EleutherAI repackaged the data as the EleutherAI/unscramble
dataset on the Hugging Face Hub and implemented the 5 sub-tasks in lm-evaluation-harness, which is
the implementation most current benchmark reports use.

## Lineage

Unscramble has no tracked predecessor or successor benchmark and no page for its 5 individual
sub-tasks in this repository; they are reported here as parts of one task family rather than as
separate pages. It belongs to the same GPT-3 paper section as other synthetic few-shot probes
(such as arithmetic and word-in-context tasks), none of which are direct variants of it.

## Saturation and contamination

GPT-3 175B's own reported per-task accuracy ranged from about 0.4% on reversed words to about 67%
on random insertion, with cycle letters and the two anagram variants in between, showing the five
sub-tasks vary enormously in difficulty and were nowhere near saturated at release. No maintained
leaderboard tracking current frontier-model scores on this specific task set was found for this
page, so whether harder sub-tasks like reversed words remain difficult for today's models is not
established here. Contamination risk is medium: the source word lists and generation code have
been public since 2020 and are mirrored on the Hugging Face Hub, and because items are generated
deterministically from a fixed word-frequency list, a model could score well by having memorised
the underlying word list rather than by performing the manipulation.

## How to run it

Run via lm-evaluation-harness with `--tasks unscramble`, which executes all 5 sub-tasks
(anagrams1, anagrams2, cycle_letters, random_insertion, reversed_words) as independent
generate_until tasks and reports 5 separate exact-match scores rather than one aggregate number.
The original GPT-3 paper's own evaluation code and raw data files are in the archived
`openai/gpt-3` repository. Because the paper's own evaluation used 100-shot prompting, any
zero-shot or few-shot-with-fewer-examples report from the harness is not directly comparable to
the original GPT-3 paper numbers without matching the shot count.

## Reading the numbers

A high exact-match score on the easier sub-tasks (such as random insertion, where the original
word's letters stay in order) mainly shows a model can strip a fixed kind of noise back out of a
recognisable word. A high score on the harder sub-tasks (reversed words, or anagrams with
first/last letters preserved) is a stronger and rarer signal, since GPT-3 175B itself scored under
1% on reversed words even at K=100. Because the five sub-tasks are reported separately and differ
so much in difficulty, a single "unscramble" number without a breakdown by sub-task tells you
little; look at which sub-tasks are being reported and at what shot count before comparing models.
