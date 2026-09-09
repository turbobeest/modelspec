---
id: "aider_polyglot"
name: "Aider Polyglot Benchmark"
aliases: ["Aider's polyglot benchmark", "polyglot-benchmark"]
page_kind: "benchmark"
category: "coding"
subcategory: "multi-language code editing"
status: "active"
summary: "225 hard Exercism exercises across six languages, scoring whether a model can write and then fix its own code from failing test output."
measures: "The model is given an Exercism programming exercise description and must produce a working solution, expressed as an edit to a starting file, in one of six languages: C++, Go, Java, JavaScript, Python or Rust. Unlike a single-shot coding benchmark, it also measures whether the model can act on its own failing test output to fix a first attempt."
task_format: "Agentic code editing inside the aider CLI tool: the model receives the exercise prompt and must emit an edit in one of aider's supported edit formats, which aider applies to a real file and tests with the language's unit test suite."
metric:
  name: "pass rate (2 attempts)"
  direction: "higher_is_better"
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Pass rate 1 is the first-attempt success rate; pass rate 2, the leaderboard's headline number, allows a second attempt after the model sees its failing test output."
dataset:
  size: 225
  size_note: "225 exercises across C++ (26), Go (39), Java (47), JavaScript (49), Python (34) and Rust (30); selected as the hardest 225 of Exercism's 697 exercises in these languages, chosen so that at most 3 of 7 reference models solved them during calibration."
  url: "https://github.com/Aider-AI/polyglot-benchmark"
  license: "Exercise content is Exercism's, used under Exercism's per-track open-source licences"
  languages: ["C++", "Go", "Java", "JavaScript", "Python", "Rust"]
  modalities: ["code"]
  splits: "single fixed set, no train/test division"
  public_test_set: true
publisher:
  org: "Aider (Paul Gauthier)"
  authors: ["Paul Gauthier"]
  url: "https://aider.chat"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://aider.chat/docs/leaderboards/"
repo_url: "https://github.com/Aider-AI/polyglot-benchmark"
released: "2024-12"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: "open"
  top_score: 88.0
  as_of: "2025-08"
  note: "Aider's own leaderboard (accessed 2026-09-07) lists gpt-5 (high), a run dated 2025-08-23, at the top with an 88.0% pass rate 2, while the wider field of dozens of tested models spans from single digits into the high 80s — a wide spread that shows the benchmark still separates models by capability."
contamination:
  risk: "medium"
  note: "Exercism's exercises are public, long-standing open-source material that plausibly appears in pretraining corpora; aider's authors deliberately selected harder problems that fewer reference models could solve, which slows but does not prevent eventual saturation as new frontier models are added."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "aider CLI (Aider-AI/aider), run against the exercises in Aider-AI/polyglot-benchmark"
tags: ["coding", "multi-language", "agentic-editing", "exercism"]
sources:
  - url: "https://aider.chat/docs/leaderboards/"
    title: "Aider LLM Leaderboards"
    accessed: "2026-09-07"
  - url: "https://aider.chat/2024/12/21/polyglot.html"
    title: "o1 tops aider's new polyglot leaderboard"
    accessed: "2026-09-07"
  - url: "https://github.com/Aider-AI/polyglot-benchmark"
    title: "Aider-AI/polyglot-benchmark"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures
Aider's polyglot benchmark tests whether a model can act as a pair-programmer inside a real coding assistant, not just produce a correct snippet in isolation. Each of its 225 problems is an Exercism programming exercise; the model is given the exercise's instructions and a starting file inside the aider CLI tool and must edit the file into a working solution in one of six languages: C++, Go, Java, JavaScript, Python or Rust. The problems span 26-49 exercises per language and were deliberately picked to be hard: they are the 225, out of Exercism's 697 exercises in these languages, that at most 3 of 7 reference models solved during calibration testing.

The benchmark measures two things at once: whether the model can solve the problem at all, and whether it can act on compiler or test-runner feedback. If the first attempt fails its unit tests, aider shows the model the failing test output and lets it try again once more.

## How it is scored
Aider reports "pass rate 1" (percentage solved on the first attempt) and "pass rate 2" (percentage solved after the optional second attempt informed by test failures), the latter being the headline leaderboard number. A solution passes when the edited file compiles or runs and satisfies the exercise's unit tests; aider also separately tracks how often a model's response conforms to its requested edit format (diff, whole-file, or similar), since a malformed edit auto-fails regardless of code quality.

## Dataset and licence
225 exercises: C++ (26), Go (39), Java (47), JavaScript (49), Python (34), Rust (30). They are drawn from Exercism, an open-source, community-maintained set of per-language exercise tracks, and used under Exercism's own open-source licences; aider's harness code and the curated exercise files live in the Aider-AI/polyglot-benchmark and Aider-AI/aider repositories. Correct solutions and unit tests are public, since Exercism itself is a public teaching resource.

## Who publishes it
Aider is an open-source AI pair-programming CLI tool created and maintained by Paul Gauthier. The polyglot benchmark was introduced in a December 2024 blog post and is maintained as a continuously updated public leaderboard at aider.chat, where Gauthier adds new models as they release.

## Lineage
The polyglot benchmark replaced an earlier, easier aider coding benchmark that had saturated; the calibration step that selected these 225 problems was explicitly designed to spread scores across a wide range for the models tested at the time, rather than clustering near a ceiling. It has no family or subset variants tracked in this repository.

## Saturation and contamination
As of this research, aider's own leaderboard lists gpt-5 (high) at the top with an 88.0% pass rate 2, while the wider field of dozens of tested models spans from single digits into the high 80s — a wide spread that shows the benchmark still separates models by capability rather than sitting at a ceiling. Because Exercism's problems and reference solutions are old and public, some contamination risk exists, but the benchmark's edit-and-retry format and code-execution scoring make rote memorization less sufficient than on a plain generation benchmark.

## How to run it
The reference harness is aider itself (open source, Aider-AI/aider), run with a command like `aider --model <provider/model>` against the exercises in Aider-AI/polyglot-benchmark. Results depend on which of aider's edit formats (diff, diff-fenced, whole, architect) a model is configured to use, and scores across different edit formats or aider versions are not strictly comparable.

## Reading the numbers
A high pass rate 2 shows a model can both write working code across several languages and productively use compiler/test feedback to fix its own mistakes — a skill closer to real pair-programming than a one-shot generation score. The gap between pass rate 1 and pass rate 2 is itself informative: a model that gains a lot on the second attempt is good at self-correction, while one that gains little either nails problems immediately or cannot use error feedback effectively. Cost-per-task, which aider also reports, matters alongside the score, since higher scores often come from higher-effort, higher-cost reasoning settings.
