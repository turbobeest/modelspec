---
id: ifeval_ca
name: "IFEval_ca (Catalan IFEval)"
aliases:
  - "IFEval Catalan"
  - "Instruction-Following Eval - Catalan"
page_kind: subset
category: instruction-following
subcategory: "Catalan translation of IFEval's verifiable-instruction suite"
status: active
summary: "A 541-prompt professional Catalan translation of IFEval, checked by a separately reimplemented Catalan instruction-verification codebase rather than IFEval's English checkers."
measures: >
  ifeval_ca is Projecte AINA and the Barcelona Supercomputing Center's professional Catalan
  translation of Google's IFEval: 541 prompts, matching the 541-row English source ("train" split of
  google/IFEval) one for one. Rather than translating only the prompt text and reusing IFEval's
  English checking code, lm-evaluation-harness's multilingual implementation ships a dedicated Catalan
  instruction registry that reimplements every checker, using `langdetect` language detection and
  Unicode-aware case folding so Catalan text is judged correctly rather than by rules tuned for
  English. The registry defines 30 Catalan instruction types in code -- the original 25 English types
  (the two Latin-alphabet capitalisation checks become Catalan-alphabet versions) plus 5 new ones (two
  extra punctuation checks, three "special character" checks) -- but the 541 released prompts only
  ever invoke the original 25, confirmed by reading every prompt's instruction_id_list directly; the 5
  unused checks, on inspection, test for the Spanish letter "n with a tilde" and Spanish-only acute
  accents rather than Catalan's grave accents (a/e/o with a grave accent) or c-cedilla, reading as an
  unadapted carry-over from the Spanish sibling file.
task_format: >
  A model is given a Catalan prompt containing one or more verifiable instructions and generates a
  free-form Catalan response in a single turn, zero-shot. lm-evaluation-harness's `ifeval_ca` task
  generates greedily (do_sample: false) with a 1,280-token cap, then a Catalan-specific verification
  function checks the response against each instruction mechanically, exactly mirroring the English
  `ifeval` task's process_results structure.
metric:
  name: "instruction-following accuracy (strict and loose, at the prompt level and the instruction level)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same four-metric structure as English IFEval: prompt_level_strict_acc, inst_level_strict_acc,
    prompt_level_loose_acc and inst_level_loose_acc, computed by the Catalan checker codebase rather
    than the English one. No random or human baseline is published for this translation specifically.
dataset:
  size: 541
  size_note: >
    541 rows in a single "test" split, confirmed via the Hugging Face datasets-server size API, and
    matching the source google/IFEval dataset's "train" split, which is also exactly 541 rows (checked
    directly rather than assumed) -- this wiki's own ifeval.md page describes the English source as
    "approximately 500" prompts, following the paper's own rounded language, but the underlying dataset
    used by the harness is precisely 541 rows on both sides of the translation.
  url: "https://huggingface.co/datasets/projecte-aina/IFEval_ca"
  license: "CC BY 4.0"
  languages: [ca]
  modalities: [text]
  splits: "single \"test\" split, 541 rows; no train or validation split"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (BSC-CNS), Language Technologies Unit -- Projecte AINA"
  authors: []
  url: "https://huggingface.co/datasets/projecte-aina/IFEval_ca"
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
    No leaderboard or maintained comparison table for ifeval_ca was found during this research, and
    this repository's own model cards do not yet report it (checked via grep across models/).
contamination:
  risk: medium
  note: >
    Public on Hugging Face since December 2024 under a permissive licence, as a direct, item-aligned
    translation of a widely circulated English benchmark whose prompts and answer-checking logic have
    been public since late 2023; no held-out portion or canary string was found in the dataset card.
harness:
  lm_eval: "ifeval_ca"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Defined at lm_eval/tasks/ifeval/multilingual/ifeval_ca.yaml (metadata version 1.0), reusing the
    shared multilingual/utils.py process_results function, which dispatches to the `ca:`-prefixed
    entries of multilingual/instructions_registry.py's CA_INSTRUCTION_DICT.
tags: [instruction-following, catalan, verifiable, translation, subset, zero-shot]
sources:
  - url: "https://huggingface.co/datasets/projecte-aina/IFEval_ca"
    title: "projecte-aina/IFEval_ca dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/projecte-aina/IFEval_ca"
    title: "projecte-aina/IFEval_ca, Hugging Face Hub API (licence, dates)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=projecte-aina/IFEval_ca"
    title: "projecte-aina/IFEval_ca row count, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=google/IFEval"
    title: "google/IFEval row count, Hugging Face datasets-server (541-row \"train\" split)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/projecte-aina/IFEval_ca/resolve/main/data/test-00000-of-00001.jsonl"
    title: "projecte-aina/IFEval_ca raw test file (read directly to count instruction_id_list usage)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/ifeval_ca.yaml"
    title: "lm-evaluation-harness: ifeval_ca task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/instructions_registry.py"
    title: "lm-evaluation-harness: multilingual instructions_registry.py (CA_INSTRUCTION_DICT, 30 entries)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/multilingual/instructions/ca_instructions.py"
    title: "lm-evaluation-harness: ca_instructions.py (EnieChecker/TildesChecker/DieresisChecker source)"
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

ifeval_ca is a professional Catalan translation of IFEval by Projecte AINA and the Barcelona
Supercomputing Center: 541 prompts, matching the English source's 541-row "train" split one for one.
Rather than translating only the prompt text and running IFEval's English verification code,
lm-evaluation-harness ships a dedicated Catalan instruction registry that reimplements every checker,
using language detection and Unicode-aware case folding so Catalan responses are judged by Catalan
rules rather than English ones. The released prompts exercise the same 25 instruction types as English
IFEval, just relabelled with a `ca:` prefix; the registry's code additionally defines 5 more checks
(two punctuation checks, three "special character" checks), but none of the 541 prompts actually use
them, confirmed by reading every prompt's instruction_id_list directly. Those unused checks are also,
on inspection, not truly Catalan: they test for the Spanish letter n-with-tilde and Spanish-only acute
accents, missing Catalan's own grave accents and c-cedilla, which reads as an unadapted carry-over from
the Spanish sibling implementation rather than a Catalan-specific design choice.

## Reading the numbers

A high ifeval_ca score shows a model reliably follows explicit, checkable instructions written in
Catalan -- the same narrow claim English IFEval supports for English, not general Catalan fluency.
Because scoring runs on an independently maintained Catalan checker codebase rather than the English
one, a Catalan and an English IFEval score are comparable in spirit but not strictly the same
measurement, even though the item count and instruction taxonomy line up exactly. As with English
IFEval, check whether a reported figure is strict or loose, and prompt-level or instruction-level,
before comparing two scores.
