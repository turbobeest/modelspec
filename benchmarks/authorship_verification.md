---
id: authorship_verification
name: "Authorship Verification (BIG-bench)"
aliases:
  - "Authorship Verification in a Swapping Scenario"
page_kind: subset
category: reasoning
subcategory: "style-based same-author identification with genre swap"
status: unknown
summary: "BIG-bench two-choice task: match a ~500-word Gutenberg passage to its author, in same-genre and genre-swapped pairings."
measures: >
  The model sees one reference passage of about 500 words and two candidate passages of similar
  length. It must pick the candidate written by the same author as the reference. One subtask
  keeps genre aligned (adult vs children's literature). The swapped subtask pairs same-author
  texts across genre and same-genre texts across authors, so topic cues point the wrong way.
task_format: >
  Two-option multiple choice. Preferred metric multiple_choice_grade. Dummy-model header counts
  880 queries. Canary GUID embedded.
metric:
  name: multiple_choice_grade
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Two choices, so chance is 50%. BIG-bench score files set low_score 0.5 and high_score 1.0.
    No human-rater figure is in the task README. Google BIG-G 128B at temperature 0 scored 0.5136
    on non-swapped, 0.4932 on swapped, and 0.5034 aggregate — essentially chance.
dataset:
  size: 880
  size_note: >
    README: 440 samples in each of the two subtasks, sharing the same texts in different pairings.
    Auto-generated header: 880 multiple-choice dummy-model queries. The task.json currently on
    GitHub is a 504-byte metadata stub without an examples array; the dummy-model transcript and
    per-model score files are the evidence that the 880-item pool was evaluated.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/authorship_verification"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "two subtasks (non_swapped, swapped); no separate train/test split"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); task authors at HU Berlin, Uni Weimar, Uni Halle, Uni Leipzig"
  authors:
    - "Niklas Deckers"
    - "Sebastian Bischoff"
    - "Benno Stein"
    - "Matthias Hagen"
    - "Martin Potthast"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/authorship_verification"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/authorship_verification"
released: "2022-06"
last_updated: ""
lineage:
  family: big_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    BIG-G 128B is at chance on the 2022 score files. No later public leaderboard cell was read.
    Chance-level 2022 numbers do not establish a current ceiling.
contamination:
  risk: high
  note: >
    Passages are long excerpts from named Project Gutenberg books (Alcott, Milne, Scott, Twain,
    Kipling and others). Those books are public-domain and widely mirrored. The BIG-bench canary
    GUID is present. Memorising the novels is a more plausible failure mode than memorising a
    private test key.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "authorship_verification"
  other: ""
tags:
  - big-bench
  - subset
  - authorship
  - multiple-choice
  - style
  - long-input
sources:
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/authorship_verification/README.md"
    title: "BIG-bench authorship_verification README (440+440 samples, Gutenberg list, authors)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/authorship_verification/task.json"
    title: "task.json metadata stub (name, preferred_score multiple_choice_grade; no examples array)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/authorship_verification/results/dummy_model.transcript.md"
    title: "Dummy-model transcript (two-choice Gutenberg passages; truncated)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/authorship_verification/results/scores_BIG-G_128b_T=0.json"
    title: "BIG-G 128B T=0 scores (aggregate multiple_choice_grade 0.5034)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/LICENSE"
    title: "google/BIG-bench Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "BIG-bench paper (arXiv:2206.04615)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-027 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-027"
---

Part of the [BIG-bench](big_bench.md) family.

## What it measures

authorship_verification asks which of two long English passages shares an author with a reference passage. Texts are about 500 words, drawn from Project Gutenberg pairs of adult and children's books by the same writer. The non-swapped subtask keeps genre matched. The swapped subtask crosses genre on purpose, so a model that keys on "children's adventure" instead of style should fail. The skill is authorship style, not plot trivia. It is not a PAN shared-task dump and is not [bbh](bbh.md).

## Reading the numbers

With two choices, 50% is chance. Google's 128B BIG-G model sat at 50.3% aggregate in the 2022 score file, so a mid-50s number is not a result. A real gain has to show up on the swapped slice, not only on same-genre pairs. The current GitHub `task.json` has no examples; reproduce from the original BIG-bench release artifacts, not from that stub. Long public-domain novels in the prompt also mean a memorisation story is always on the table.
