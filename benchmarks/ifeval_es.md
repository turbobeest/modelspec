---
id: ifeval_es
name: "IFEval_es (Spanish IFEval)"
aliases:
  - "IFEval Spanish"
  - "Instruction-Following Eval - Spanish"
page_kind: subset
category: instruction-following
subcategory: "Spanish translation of IFEval's verifiable-instruction suite"
status: active
summary: "A 541-prompt professional Spanish translation of IFEval, checked by a separately reimplemented Spanish instruction-verification codebase rather than IFEval's English checkers."
measures: >
  ifeval_es is the Barcelona Supercomputing Center's professional Spanish translation of Google's
  IFEval: 541 prompts, matching the 541-row English source ("train" split of google/IFEval) one for
  one. As with the sibling Catalan translation, lm-evaluation-harness does not run the translated
  prompts through IFEval's English checking code; it ships a dedicated Spanish instruction registry
  that reimplements every checker, using `langdetect` language detection and Unicode-aware case
  folding so Spanish text is judged by Spanish-appropriate rules. The registry defines 30 Spanish
  instruction types in code -- the original 25 English types (the two Latin-alphabet capitalisation
  checks become Spanish-alphabet versions) plus 5 new ones (two extra punctuation checks, three
  "special character" checks for the letter n-with-tilde and accented vowels) -- but the 541 released
  prompts only ever invoke the original 25, confirmed by reading every prompt's instruction_id_list
  directly. Unlike the Catalan sibling file, where the equivalent unused checks test for the wrong
  language's diacritics, the Spanish special-character checks do target genuine Spanish orthography;
  they are simply dormant, exercised by no released prompt.
task_format: >
  A model is given a Spanish prompt containing one or more verifiable instructions and generates a
  free-form Spanish response in a single turn, zero-shot. lm-evaluation-harness's `ifeval_es` task
  generates greedily (do_sample: false) with a 1,280-token cap, then a Spanish-specific verification
  function checks the response against each instruction mechanically, mirroring the English `ifeval`
  task's process_results structure.
metric:
  name: "instruction-following accuracy (strict and loose, at the prompt level and the instruction level)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same four-metric structure as English IFEval: prompt_level_strict_acc, inst_level_strict_acc,
    prompt_level_loose_acc and inst_level_loose_acc, computed by the Spanish checker codebase rather
    than the English one. No random or human baseline is published for this translation specifically.
dataset:
  size: 541
  size_note: >
    541 rows in a single "test" split, confirmed via the Hugging Face datasets-server size API, and
    matching the source google/IFEval dataset's "train" split, which is also exactly 541 rows (checked
    directly rather than assumed) -- this wiki's own ifeval.md page describes the English source as
    "approximately 500" prompts, following the paper's own rounded language, but the underlying dataset
    used by the harness is precisely 541 rows on both sides of the translation.
  url: "https://huggingface.co/datasets/BSC-LT/IFEval_es"
  license: "CC BY 4.0"
  languages: [es]
  modalities: [text]
  splits: "single \"test\" split, 541 rows; no train or validation split"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (BSC-CNS), Language Technologies Unit"
  authors: []
  url: "https://huggingface.co/datasets/BSC-LT/IFEval_es"
paper:
  title: "Instruction-Following Evaluation for Large Language Models"
  arxiv: "2311.07911"
  url: "https://arxiv.org/abs/2311.07911"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/ifeval/multilingual"
released: "2024-12"
last_updated: "2025-11"
lineage:
  family: ifeval
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No leaderboard or maintained comparison table for ifeval_es was found during this research, and
    this repository's own model cards do not yet report it (checked via grep across models/).
contamination:
  risk: medium
  note: >
    Public on Hugging Face since December 2024 under a permissive licence, as a direct, item-aligned
    translation of a widely circulated English benchmark whose prompts and answer-checking logic have
    been public since late 2023; no held-out portion or canary string was found in the dataset card.
harness:
  lm_eval: "ifeval_es"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Defined at lm_eval/tasks/ifeval/multilingual/ifeval_es.yaml (metadata version 1.0), reusing the
    shared multilingual/utils.py process_results function, which dispatches to the `es:`-prefixed
    entries of multilingual/instructions_registry.py's ES_INSTRUCTION_DICT.
tags: [instruction-following, spanish, verifiable, translation, subset, zero-shot]
sources:
  - url: "https://huggingface.co/datasets/BSC-LT/IFEval_es"
    title: "BSC-LT/IFEval_es dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/BSC-LT/IFEval_es"
    title: "BSC-LT/IFEval_es, Hugging Face Hub API (licence, dates)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=BSC-LT/IFEval_es"
    title: "BSC-LT/IFEval_es row count, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=google/IFEval"
    title: "google/IFEval row count, Hugging Face datasets-server (541-row \"train\" split)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/BSC-LT/IFEval_es/resolve/main/data/test-00000-of-00001.jsonl"
    title: "BSC-LT/IFEval_es raw test file (read directly to count instruction_id_list usage)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/ifeval_es.yaml"
    title: "lm-evaluation-harness: ifeval_es task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/instructions_registry.py"
    title: "lm-evaluation-harness: multilingual instructions_registry.py (ES_INSTRUCTION_DICT, 30 entries)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/instructions/es_instructions.py"
    title: "lm-evaluation-harness: es_instructions.py (EnieChecker/TildesChecker/DieresisChecker source)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/instructions_registry.py"
    title: "lm-evaluation-harness: original English ifeval instructions_registry.py (25-entry INSTRUCTION_DICT, for comparison)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2311.07911"
    title: "Instruction-Following Evaluation for Large Language Models"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice C"
  reviewed: ""
  reviewed_by: ""
---

Part of the [IFEval](ifeval.md) family.

## What it measures

ifeval_es is the Barcelona Supercomputing Center's professional Spanish translation of IFEval: 541
prompts, matching the English source's 541-row "train" split one for one. As with the sibling Catalan
translation, lm-evaluation-harness does not run the translated prompts through IFEval's English
checking code; it ships a dedicated Spanish instruction registry that reimplements every checker, using
language detection and Unicode-aware case folding so responses are judged by Spanish rules. The
released prompts exercise the same 25 instruction types as English IFEval, just relabelled `es:`; the
registry's code also defines 5 more checks (two punctuation, three "special character" checks for
n-with-tilde and accented vowels), but none of the 541 prompts use them -- confirmed by reading every
instruction_id_list directly. Unlike the sibling Catalan file, where the equivalent unused checks test
for the wrong language's diacritics, these Spanish versions do target genuine Spanish orthography; they
are simply unexercised here.

## Reading the numbers

A high ifeval_es score shows a model reliably follows explicit, checkable instructions written in
Spanish -- the same narrow claim English IFEval supports for English, not general Spanish fluency.
Because scoring runs on an independently maintained Spanish checker codebase rather than the English
one, a Spanish and an English IFEval score are comparable in spirit but not strictly the same
measurement, even though the item count and instruction taxonomy line up exactly. As with English
IFEval, check whether a reported figure is strict or loose, and prompt-level or instruction-level,
before comparing two scores.
