---
id: arabic_leaderboard_light
name: "Open Arabic LLM Leaderboard — Light configuration"
aliases:
  - "OALL Light"
page_kind: subset
category: composite
subcategory: "10%-sample version of arabic_leaderboard_complete's 14 task groups"
status: superseded
summary: "A 10%-random-sample version of arabic_leaderboard_complete's same 14 Arabic task groups, run for lower cost; ACVA's 10-item Yemen subset is kept at full size rather than sampled further."
measures: >
  arabic_leaderboard_light runs the same 14 component task groups as arabic_leaderboard_complete --
  AlGhafa, ACVA, Arabic EXAMS, and ten machine-translated groups (ARC-Challenge, ARC-Easy, BoolQ,
  COPA, HellaSwag, MMLU, OpenBookQA, PIQA, RACE, SciQ, ToxiGen) -- but scores each one against a
  random 10% sample of its test set rather than the full set, to cut evaluation cost. The harness's
  own README for this task documents one explicit exception: ACVA's Yemen subset has only 10 test
  items to begin with, so it is evaluated at full size rather than reduced to a single item.
task_format: >
  Identical task formats to arabic_leaderboard_complete's 14 components, each applied to a smaller,
  randomly sampled item set.
metric:
  name: "accuracy (acc and acc_norm, size-weighted mean across 14 sampled task groups)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Same as arabic_leaderboard_complete: arity varies by component, so no single random baseline applies to the aggregate."
dataset:
  size: null
  size_note: >
    Each of the 14 component test sets is randomly sampled down to 10% of its full size, per the
    harness's own README for this task, with ACVA's Yemen subset (10 items) kept at full size rather
    than reduced further. No aggregate item count across the 14 sampled groups was established from
    a source read for this page.
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arabic_leaderboard_light"
  license: "Varies by component dataset; see arabic_leaderboard_complete."
  languages:
    - ar
  modalities:
    - text
  splits: "10% random sample of each of the 14 component groups' test sets (ACVA's Yemen subset excepted, kept at its full 10 items)"
  public_test_set: true
publisher:
  org: "Open Arabic LLM Leaderboard (OALL) project: Technology Innovation Institute (TII) and 2A2I, with Hugging Face"
  authors: []
  url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard"
paper:
  title: "Introducing the Open Arabic LLM Leaderboard"
  arxiv: ""
  url: "https://huggingface.co/blog/leaderboard-arabic"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arabic_leaderboard_light"
released: "2024-05"
last_updated: ""
lineage:
  family: "arabic_leaderboard_complete"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No current top score specific to this sampled composition was established from a source read for this page; see arabic_leaderboard_complete for the same limitation on the full configuration, including the live leaderboard's move to an unrelated v2 composition."
contamination:
  risk: high
  note: >
    Draws from the same public, unrefreshed test sets as arabic_leaderboard_complete, merely
    sub-sampled at random; sampling does not lower contamination risk, since the full pool each
    sample is drawn from remains public and a model cannot know in advance which 10% will be used.
harness:
  lm_eval: "arabic_leaderboard_light"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Same LightEval-vs-lm-evaluation-harness distinction as arabic_leaderboard_complete: the live OALL space does not run this harness task."
tags:
  - composite
  - arabic
  - leaderboard
  - multiple-choice
  - machine-translated
  - native-sourced
  - subset
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arabic_leaderboard_light"
    title: "arabic_leaderboard_light tasks directory, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arabic_leaderboard_light/README.md"
    title: "arabic_leaderboard_light README (10% sampling rule, ACVA Yemen exception)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arabic_leaderboard_light/arabic_leaderboard_light.yaml"
    title: "arabic_leaderboard_light.yaml aggregation config (14-task list, weighting)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice A"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Open Arabic LLM Leaderboard — Complete configuration](arabic_leaderboard_complete.md) family.

## What it measures

arabic_leaderboard_light runs the same 14 component task groups as [arabic_leaderboard_complete](arabic_leaderboard_complete.md) -- AlGhafa, ACVA, Arabic EXAMS, and ten machine-translated groups covering ARC, BoolQ, COPA, HellaSwag, MMLU, OpenBookQA, PIQA, RACE, SciQ and ToxiGen -- but scores each against a random 10% sample of its test set instead of the full set, to make evaluation cheaper. The harness's own README for this task documents one exception directly: ACVA's Yemen subset has only 10 test items in total, so it is kept at full size rather than reduced to a single item, which would make its score unreliable.

## Reading the numbers

A light score approximates, but is not identical to, the same model's complete-configuration score: it is computed from a different, smaller, randomly sampled set of items per component, so small differences between a light score and a complete score should not be over-read. Because sampling draws from the same public test pools as the complete configuration, it carries the same high contamination risk and the same disconnect from the live OALL leaderboard, which has since moved to an unrelated v2 task composition run through a different framework. Use this configuration for a cheaper, approximate read when the full configuration's cost is prohibitive, not as an independently meaningful score.
