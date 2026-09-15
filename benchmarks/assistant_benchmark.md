---
id: assistant_benchmark
name: "Assistant Benchmark"
aliases:
  - "AssistantBenchmark.com"
page_kind: benchmark
category: agentic
subcategory: "real-use, task-by-task scoring of consumer AI assistant products against written anchors"
status: active
summary: "A public scorecard that scores 71 consumer AI assistant products on the same 15 real-use dimensions (v0.2), 1-10 against written anchors after a logged run, alongside a separate public-opinion read from quotes."
measures: >
  Assistant Benchmark scores assistant products a person can text or otherwise talk to -- Instinct,
  Muse, Poke, Grok Bot and 67 others at the time of research -- rather than the underlying language
  models that power them. Each of 71 listed assistants is run through the same 15 dimensions:
  carrying out an online task, travel booking, recommendation quality, purchasing a product,
  responding to emails, proactive behavior, running a routine, third-party integrations,
  permissions and privacy, memory, phone calls, multiplayer/groups, chained tasks, proactive
  restraint, and content creation/games. A sixteenth listed dimension, personality, is explicitly
  "public opinion only" and is read from public quotes rather than scored 1-10, so it sits outside
  the 15 tested dimensions the site's own scorecard counts. Each dimension publishes one named task
  on the site itself -- for example "book a hotel stay" for the online-task dimension, or "reply to
  a scheduling email" for the email dimension -- so, unlike a hidden test set, the exact task an
  assistant will face is public.
task_format: >
  For each of the 15 tested dimensions, a tester actually uses the live product to attempt the
  dimension's one published task (for example, calling a business and getting an answer, for the
  phone-calls dimension) and records what happened as a logged run, with a short written note, a
  pass/partial/fail-style read, and a link to the underlying thread or quotes where the site shows
  one. A dimension can also be marked N/A when it does not apply to a given product (for example, a
  text-only assistant against the phone-calls dimension), or left untested (shown as "--").
metric:
  name: "per-dimension score against written anchors, 1-10, after real use"
  direction: higher_is_better
  unit: "points"
  max_score: 10
  random_baseline: null
  human_baseline: null
  baseline_note: >
    An assistant's "Overall" figure is the mean of only the dimensions scored so far for that
    product, not of all 15 -- the site states this explicitly ("Overall is a running mean until an
    assistant is fully tested"). At the research date no assistant had every applicable dimension
    scored: within the site's own default "General" category view (44 of the 71 listed assistants),
    0 were shown as fully completed, 21 as in progress and 23 as pending, out of 15 tasks and 180
    logged runs sitewide. Because "Overall" scores are compared across products with different
    numbers of dimensions tested (for example 9.1 from 7 of 15 dimensions versus 7.6 from 13 of 15),
    the current top "Overall" figures are not a settled ranking and are not recorded here as a
    saturation ceiling.
dataset:
  size: 15
  size_note: >
    Not a fixed item bank: 15 published tasks, one per tested dimension, each rerun against every
    assistant that reaches that dimension in the testing queue. The site reports 180 logged runs
    and 5,194 public quotes sitewide as of the research date, both figures that grow as more
    assistants and dimensions are tested.
  url: "https://assistantbenchmark.com/dimensions"
  license: ""
  languages:
    - en
  modalities:
    - text
    - image
    - audio
    - video
  splits: ""
  public_test_set: null
publisher:
  org: "Assistant Benchmark"
  authors: []
  url: "https://assistantbenchmark.com/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://assistantbenchmark.com/"
repo_url: ""
released: ""
last_updated: "2026-09-14"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Not saturated: at the research date zero assistants were fully tested across all 15 dimensions
    (within the default General-category view, 0 of 44 complete, 21 in progress, 23 pending), and
    reported per-dimension scores among tested assistants span the full 1-10 scale. Because
    "Overall" is a partial running mean over however many dimensions have been scored so far, and
    that count differs assistant to assistant, no single top score is comparable enough to record
    as a ceiling.
contamination:
  risk: medium
  note: >
    Classic train/test leakage does not apply -- this evaluates live products by using them, not a
    model against a held-out answer key. But each dimension's one task is published on the site
    itself (for example "book a hotel stay," "reply to a scheduling email"), so a vendor knows in
    advance exactly what will be tested for its product, even though the specific instance details
    of a given logged run (dates, cities, exact wording) are not published in advance.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - agentic
  - product-benchmark
  - consumer-assistant
  - human-scored
  - public-opinion
  - live-leaderboard
sources:
  - url: "https://assistantbenchmark.com/"
    title: "Assistant Benchmark -- Scorecard (home page)"
    accessed: "2026-09-14"
  - url: "https://assistantbenchmark.com/dimensions"
    title: "Assistant Benchmark -- Dimensions and How scoring works"
    accessed: "2026-09-14"
  - url: "https://assistantbenchmark.com/compare"
    title: "Assistant Benchmark -- Head to head"
    accessed: "2026-09-14"
  - url: "https://assistantbenchmark.com/request"
    title: "Assistant Benchmark -- Request a test"
    accessed: "2026-09-14"
  - url: "https://assistantbenchmark.com/use-cases"
    title: "Assistant Benchmark -- Trending use cases"
    accessed: "2026-09-14"
  - url: "https://assistantbenchmark.com/agents/instinct"
    title: "Assistant Benchmark -- Instinct assistant page (example per-dimension detail)"
    accessed: "2026-09-14"
freshness:
  researched: "2026-09-14"
  researched_by: "sonnet-5 agent, MODEL-55"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Assistant Benchmark scores assistant products, not base models: things like Instinct, Muse, Poke and Grok Bot, which a person texts or otherwise talks to, rather than the language model underneath any of them. At the research date it listed 71 assistants, grouped into kinds such as general, travel, email, finance, shopping, health and food, work and teams, and infra and hardware. Every assistant is measured against the same 15 dimensions: carrying out an online task, travel booking, recommendation quality, purchasing a product, responding to emails, proactive behavior, running a routine, third-party integrations, permissions and privacy, memory, phone calls, multiplayer/groups, chained tasks, proactive restraint, and content creation/games.

A sixteenth listed item, personality, is called out on the site as "public opinion only": it is read from public quotes about an assistant rather than scored 1-10, so it sits outside the 15 dimensions the scorecard actually tests. Each of the 15 tested dimensions publishes exactly one named task on the site -- "book a hotel stay" for the online-task dimension, "reply to a scheduling email" for the email dimension, and so on -- so the task an assistant will face is known in advance rather than hidden.

## How it is scored

For each dimension, a tester uses the live product on its one published task and records a logged run: a short written note on what happened, a pass/partial/fail-style read, and, where the site links one, a quote thread. The site states its rule plainly: "One published task per dimension, scored 1-10 against written anchors after real use. No score without a logged run." A dimension can also come back N/A, when it does not apply to that product, or untested, shown as a dash. An assistant's "Overall" number is the mean of only the dimensions scored so far, not of all 15, so it is a running mean that changes shape as more dimensions land -- comparing two assistants' Overall scores means comparing means taken over different numbers of dimensions.

Separately, most assistant pages also carry a "public opinion" figure (a percentage, for example 82% on one assistant's page) built from public quotes about that product, and the site toggles between a "Benchmark" view and a "Public opinion" view of the scorecard. The two are not the same measurement: the benchmark score is a tester's logged, anchor-scored real use; public opinion is a read of what people say about the product elsewhere, chiefly on X.

## Dataset and licence

There is no downloadable item bank. The "dataset" is 15 published tasks, one per tested dimension, rerun against whichever assistants have reached that dimension in the testing queue; the site reports 180 logged runs and 5,194 public quotes sitewide as of the research date. No licence for the site's own scores or quotes was stated on the pages read. Evaluated modalities span text, phone-call audio, and image, video or game output, since the content-creation/games dimension covers making images, video or games on request and the phone-calls dimension covers placing real calls.

## Who publishes it

The site identifies itself only as "Assistant Benchmark," at assistantbenchmark.com; no operating company, named author or contact beyond an in-page test-request form was found on the home page, the dimensions page, the compare page or the request page. The benchmark is versioned ("Benchmark v0.2") and both "last test" and "updated" were stamped September 14, 2026 -- the research date -- indicating the roster and scores are actively maintained rather than a one-time snapshot.

## Lineage

A version history was not established beyond the current "v0.2" label read from the site; no predecessor, successor or variant benchmark is named on the pages read, and this benchmark has no tracked family or subset pages in this repository.

## Saturation and contamination

The benchmark is not saturated: at the research date, within the site's own default "General" category view (44 of the 71 listed assistants), 0 were shown fully completed across all 15 dimensions, 21 were in progress and 23 were pending, and per-dimension scores among tested assistants ranged across the full 1-10 scale. Because "Overall" is a partial running mean computed over however many dimensions a given assistant has had scored, the current top Overall figures are not a settled, comparable ranking, and this page does not record one as a saturation ceiling. Contamination in the classic train/test sense does not apply, since this evaluates live products by using them rather than scoring a model against a held-out answer key. The closer risk is that each dimension's single task is published on the site itself, so a vendor knows in advance what will be tested, even though a given logged run's exact details are not pre-announced.

## How to run it

There is no offline harness, reference implementation or downloadable eval script: scores come only from the site's own testers using each live assistant product and logging the result. A vendor or reader cannot reproduce a score outside the site's own process. A "request a test" form lets anyone suggest an assistant or ask that specific dimensions be tested first, after which the site checks the assistant is real and publicly available and queues it.

## Reading the numbers

A high per-dimension score means a tester's own use of the product cleared that dimension's specific published task against written anchors, on the date logged -- it is a real, if small-sample, result, not a statistical average over many trials. Always check how many of the 15 dimensions are actually scored (shown as "N of 15 tested") before comparing two assistants' "Overall" figures, since a 9.1 built from 7 dimensions and a 7.6 built from 13 are not measuring the same amount of the product. Treat the benchmark score and the public-opinion figure as answering different questions -- one tester's logged, anchor-scored real use versus a read of public sentiment -- and do not average them together.
