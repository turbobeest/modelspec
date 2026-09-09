---
id: assistant_bench
name: "AssistantBench"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "realistic, time-consuming web tasks scored by automatic answer matching"
status: active
summary: "214 realistic web tasks such as monitoring listings or comparing prices, scored by an automatic answer-matching function; no system has cleared half credit on the public leaderboard."
measures: >
  AssistantBench gives a model or agent a natural-language request that a person might actually want
  handled on the open web -- monitoring a real-estate listing, comparing ticket prices across dates,
  locating a nearby business that meets several criteria -- and checks whether it can produce the
  correct answer. The authors built it specifically because prior web-agent benchmarks tended to use
  short, artificial tasks; AssistantBench's 214 tasks are instead designed to be realistic and, in
  many cases, genuinely time-consuming for a human to complete by hand, spanning many sites and
  domains rather than one sandboxed environment. Answers take several forms -- a number, a short
  string, a list, or a small JSON object -- rather than always being a single fact, so scoring has to
  handle partial credit rather than plain exact match.
task_format: >
  A natural-language task description in, a free-form answer out. The reference implementation
  (inspect_evals) runs five variants of the same 214-task set: closed-book zero-shot, closed-book
  one-shot, web-search zero-shot, web-search one-shot, and a web-browser-plus-search agent variant
  the authors did not run themselves. The original paper also evaluated a SeeAct web-navigation agent
  and the authors' own SeePlanAct (SPA) agent, neither of which inspect_evals reproduces, since both
  need scaffolding the framework does not support.
metric:
  name: "accuracy (custom partial-credit scorer) and answer rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's own headline result is that no model or agent evaluated at release exceeded 26
    accuracy points out of 100; closed-book language models answered confidently but with low
    precision (frequent hallucination), while contemporary web agents scored close to zero. As of
    this page's research date, the project's own self-hosted leaderboard (read 2026-09-08) shows the
    top two entries tied at 50.70, roughly double the paper's release-time ceiling. There is no
    meaningful random baseline, since answers are free-form rather than drawn from fixed options.
dataset:
  size: 214
  size_note: >
    214 tasks total, confirmed by downloading and counting both released files directly: 33 in
    `assistant_bench_v1.0_dev.jsonl`, which ships with public answers and is loaded by
    inspect_evals as the "validation" split, and 181 in `assistant_bench_v1.0_test.jsonl`, whose
    `answer` field is present in the schema but empty for every row -- the test answers are
    withheld and scored only through the project's own submission-based leaderboard.
  url: "https://huggingface.co/datasets/AssistantBench/AssistantBench"
  license: "Apache-2.0, per the Hugging Face dataset card"
  languages:
    - en
  modalities:
    - text
  splits: "validation (33 tasks, answers public) / test (181 tasks, answers withheld)"
  public_test_set: false
publisher:
  org: "Tel Aviv University, with Allen Institute for AI, University of Pennsylvania, University of Washington and Princeton University"
  authors:
    - "Ori Yoran"
    - "Samuel Joseph Amouyal"
    - "Chaitanya Malaviya"
    - "Ben Bogin"
    - "Ofir Press"
    - "Jonathan Berant"
  url: "https://assistantbench.github.io"
paper:
  title: "AssistantBench: Can Web Agents Solve Realistic and Time-Consuming Tasks?"
  arxiv: "2407.15711"
  url: "https://arxiv.org/abs/2407.15711"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/AssistantBench/leaderboard"
repo_url: "https://github.com/oriyor/assistantbench"
released: "2024-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 50.70
  as_of: "2026-09-08"
  note: >
    Read live from the project's own Hugging Face Space leaderboard on the research date: the top
    two entries (LossLessRAG, from the University of Central Florida, and AutoAssist ChatGPT-HQ +
    GPT-5.6 Sol Ultra) are tied at 50.70 accuracy on the held-out test set, with a fourth-place entry
    at 37.60 -- a real spread, and still roughly half of the 100-point ceiling. That is a large jump
    from the paper's own release-time finding that no system exceeded 26 points, but the benchmark is
    not close to saturated: even the best current systems answer under 99% of tasks and get roughly
    half of what they answer wrong.
contamination:
  risk: medium
  note: >
    The two splits carry different risk. The 181-question test set's answers have never been
    published -- scoring happens only through the project's own leaderboard, which accepts
    predictions rather than answers -- so it resists simple memorization. The 33-question validation
    set, by contrast, has shipped with public answers since July 2024 (over two years by this page's
    research date) and is the split inspect_evals actually scores against, "so that we can score the
    results of the tasks" in the harness maintainers' own words; a score quoted from inspect_evals
    should be read as coming from the more contamination-exposed half of the benchmark, not the
    harder-to-game leaderboard half.
harness:
  lm_eval: ""
  inspect_evals: "assistant_bench (assistant_bench_closed_book_zero_shot, assistant_bench_closed_book_one_shot, assistant_bench_web_search_zero_shot, assistant_bench_web_search_one_shot, assistant_bench_web_browser)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - agentic
  - web-agent
  - tool-use
  - open-ended-qa
  - realistic-tasks
sources:
  - url: "https://arxiv.org/abs/2407.15711"
    title: "AssistantBench: Can Web Agents Solve Realistic and Time-Consuming Tasks?"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.15711"
    title: "AssistantBench paper, full text (ar5iv), for author affiliations"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AssistantBench/AssistantBench"
    title: "AssistantBench/AssistantBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/AssistantBench/AssistantBench"
    title: "AssistantBench/AssistantBench dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AssistantBench/AssistantBench/resolve/main/assistant_bench_v1.0_dev.jsonl"
    title: "AssistantBench v1.0 dev/validation file (33 rows, counted directly)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AssistantBench/AssistantBench/resolve/main/assistant_bench_v1.0_test.jsonl"
    title: "AssistantBench v1.0 test file (181 rows, answers empty, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/assistant_bench/README.md"
    title: "inspect_evals assistant_bench task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/assistant_bench/dataset.py"
    title: "inspect_evals assistant_bench dataset.py (confirms HF dataset id and revision)"
    accessed: "2026-09-08"
  - url: "https://assistantbench.github.io"
    title: "AssistantBench project page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/AssistantBench/leaderboard"
    title: "AssistantBench live leaderboard (Hugging Face Space)"
    accessed: "2026-09-08"
  - url: "https://github.com/oriyor/assistantbench"
    title: "oriyor/assistantbench reference repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AssistantBench gives a model or agent a natural-language request that a person might actually want handled on the open web -- monitoring a real-estate listing, comparing ticket prices across a set of dates, locating a nearby business that satisfies several criteria at once -- and checks whether it produces the correct answer. The authors built it because earlier web-agent benchmarks leaned on short, artificial tasks confined to one sandboxed site; AssistantBench's 214 tasks are instead meant to be realistic and, for a human doing them by hand, often genuinely time-consuming, spanning many real sites and domains rather than a single simulated environment.

Answers are not always a single fact: a task's target can be a number, a short string, a list of strings, or a small JSON object, so the benchmark's scoring has to handle partial credit rather than plain exact match. Because the harness scores whatever the model outputs, it also tracks how often the model produces an answer at all (answer rate) alongside how often that answer is correct.

## How it is scored

The paper defines a custom scoring function, reimplemented as closely as possible in inspect_evals: string answers are scored by token-level F1 against the target; numeric answers by a ratio-based penalty, `max{0, 1 - log(max(A, A')/min(A, A'))}`, so an answer that is off by a small multiplicative factor still earns partial credit; list answers extend the string logic across every item; and JSON answers are scored key by key, with a missing key scoring zero. Every task is also marked as answered or not, giving a secondary answer-rate metric. inspect_evals runs five task variants -- closed-book zero-shot, closed-book one-shot, web-search zero-shot, web-search one-shot, and a web-browser-plus-search variant that has no direct counterpart in the paper -- and the paper additionally reports two agent setups, SeeAct and the authors' own SeePlanAct, that inspect_evals does not reproduce because they need scaffolding the framework does not support.

## Dataset and licence

The full item pool is 214 tasks, confirmed here by downloading both release files and counting rows directly rather than trusting a stated total: 33 in the dev file, which carries public answers and is loaded by inspect_evals as the "validation" split, and 181 in the test file, whose `answer` field exists in the schema but is empty for every row. The Hugging Face dataset card states an Apache-2.0 licence. All tasks are in English and are text-only at the task-definition level, though solving them typically requires an agent to browse or search the live web, which is outside the dataset's own content.

## Who publishes it

AssistantBench comes from Ori Yoran, Samuel Joseph Amouyal and Jonathan Berant at Tel Aviv University, together with Chaitanya Malaviya (University of Pennsylvania), Ben Bogin (Allen Institute for AI), Ofir Press (University of Washington, at the time of the v1 preprint) and Jonathan Berant's co-authors at Princeton, posted to arXiv in July 2024 and revised in October 2024. The authors maintain the reference repository, the Hugging Face dataset, and a self-hosted leaderboard built on the same template the GAIA benchmark's leaderboard uses; the UK AI Security Institute's inspect_evals project maintains an independent harness implementation.

## Lineage

AssistantBench has no predecessor or successor tracked in this repository. It sits in the same family of realistic-agentic-task benchmarks as GAIA, whose leaderboard template its own leaderboard explicitly reuses, though GAIA does not yet have a page here. Within inspect_evals it is one of several web-agent and tool-use tasks, distinguished by its emphasis on tasks that are open-ended and genuinely time-consuming rather than puzzle-like.

## Saturation and contamination

AssistantBench is not saturated. At release, no evaluated system exceeded 26 accuracy points; reading the project's own live leaderboard on this page's research date shows the top two entries tied at 50.70, with real separation further down the board (a fourth-place entry at 37.60) and still roughly half the available credit unclaimed. Contamination risk differs sharply by split: the 181-task test set's answers have never been published and are scored only by the project's own prediction-submission leaderboard, while the 33-task validation set has carried public answers since July 2024 and is the split inspect_evals actually scores against -- a number quoted from inspect_evals reflects the more exposed half of the benchmark, not the harder-to-game leaderboard half.

## How to run it

inspect_evals implements all five task variants under the `assistant_bench` namespace (for example `inspect_evals/assistant_bench_web_search_zero_shot`), loading the Hugging Face dataset at a pinned revision and scoring with the reimplemented custom function described above. Reported numbers depend heavily on which of the five variants was run, since closed-book and web-search-augmented setups produce very different accuracy and answer-rate profiles for the same model, and on whether the score came from inspect_evals' public validation split or the project's own held-out leaderboard.

## Reading the numbers

A high AssistantBench score signals that a system can chain together multi-step, realistic information-gathering work on the open web and land on a specific, checkable answer -- not just retrieve a fact, but combine several of them the way a task like "how much would I have saved with a season pass" requires. Because closed-book language models can score deceptively well on accuracy while hallucinating (the paper's own finding), always read accuracy alongside answer rate and, where available, precision, rather than accuracy alone. Confirm which of the five task variants and which split (public validation versus held-out test) produced a given number before comparing it to another reported score.
