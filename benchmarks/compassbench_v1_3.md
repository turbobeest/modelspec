---
id: compassbench_v1_3
name: "CompassBench v1.3"
aliases:
  - "compassbench_v1_3"
page_kind: benchmark
category: composite
subcategory: "OpenCompass's own composite evaluation aggregating four category groups -- knowledge, mathematics, code, and agent/tool-use -- restructured from, and not a superset of, CompassBench v1.1"
status: unknown
summary: "OpenCompass's next dated CompassBench release: a narrower, restructured composite of knowledge, math, code and agent scores, not a superset of CompassBench v1.1."
measures: >
  CompassBench v1.3 is OpenCompass's next dated release in the CompassBench line after
  `compassbench_20_v1_1`, established directly from its dataset and summarizer configuration files in
  the opencompass repository, but the evidence shows it is a restructured, genuinely different
  composite rather than an extended version of v1.1: it aggregates only four category groups --
  knowledge (English and Chinese Wikipedia-derived single-choice questions split by domain: humanities,
  social science, and natural science in both an engineering and a science variant; a fifth domain,
  life common sense, is defined in the dataset configuration but is not included in the shipped
  aggregation), mathematics (college-level single choice in English and Chinese, plus an English
  arithmetic cloze set -- narrower than v1.1's MathBench, which spans arithmetic through college in
  both languages), code (a HumanEval-style code-completion pair, an LCBench-style code-interview task
  at three difficulties in both languages, and TACO-based code-competition at five difficulties), and
  agent (T-Eval / plugin_eval tool-planning only; a CIBench code-interpreter group is defined in the
  same configuration file but is commented out of the active aggregation). v1.1's language and
  reasoning (ReasonBench) categories have no counterpart in v1.3 at all. OpenCompass's own release
  notes separately reference a "CompassBench Checklist Evaluation" and a "Compassbench v1_3 subjective
  evaluation" landing in the same development window; this page documents only the objective composite
  under `configs/datasets/compassbench_v1_3`, and does not claim those other, differently-scoped
  CompassBench-branded evaluations are the same thing.
task_format: >
  Predominantly multiple choice, scored with OpenCompass's circular evaluation (every answer-order
  permutation must be answered correctly to credit the item, `perf_4`), the same technique v1.1 uses.
  The knowledge and math categories use this circular multiple-choice format with a step-by-step
  reasoning instruction in the prompt; the arithmetic-cloze math task and the code tasks are graded by
  final-answer extraction or functional test execution (pass@1) instead. Unlike v1.1's published
  summarizer, v1.3's shipped configuration defines no single top-level blended score across all four
  categories -- the corresponding line in its summarizer file is commented out -- so it is reported as
  four separate category averages rather than one number.
metric:
  name: "four separate category-level naive averages (knowledge, math, code, agent) -- no single blended top-level score is defined in the shipped configuration, unlike compassbench_20_v1_1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No official leaderboard table for this exact configuration could be read for this page (the
    CompassRank site's results load through client-side scripts this page's tools could not execute),
    so no headline top_score is recorded. Because the shipped summarizer defines no combined score
    across knowledge, math, code and agent, there is no single number to baseline in the first place;
    each category's naive average tops out at 100% on its own accuracy-type components, but the code
    category's pass@1 figures and the arithmetic-cloze accuracy are not guaranteed to sit on the same
    practical scale as the circular-MCQ knowledge and math scores.
dataset:
  size_note: >
    Not established as a single number; this page did not download and count every constituent file.
    What the configuration files confirm directly: the knowledge category's file names embed "500" in
    each of ten domain-language splits (`wiki_en_sub_500_<domain>`, `wiki_zh_sub_500_<domain>`),
    suggesting roughly 500 items per split, though this page did not independently verify that count by
    inspecting the underlying data files, so it is reported here as what the naming implies rather than
    a confirmed figure. The math category spans two college-level single-choice splits (English,
    Chinese) plus one arithmetic-cloze split. The code category spans two code-completion splits, six
    code-interview splits (three difficulties, two languages), and five TACO code-competition
    difficulty splits.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_v1_3"
  license: ""
  languages:
    - en
    - zh
  modalities:
    - text
    - code
  splits: "single evaluation set per constituent dataset; no train/validation split documented in the configs read for this page"
  public_test_set: null
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://rank.opencompass.org.cn/home"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_v1_3"
released: "2024-08"
last_updated: ""
lineage:
  family: ""
  predecessor: compassbench_20_v1_1
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    OpenCompass's own CompassRank leaderboard would be the natural source for current standing, but
    its results table loads through client-side scripts this page's tools could not render, so no top
    score or saturation reading could be confirmed. Recorded as unknown rather than guessed.
contamination:
  risk: medium
  note: >
    The code category reuses HumanEval-, LCBench- and TACO-style tasks whose underlying problem styles
    are widely known and, for HumanEval and TACO specifically, long public; the knowledge category
    draws from Wikipedia, a training-data staple. This page found no held-back "public" versus
    full-item split for compassbench_v1_3 comparable to the one confirmed for the v1.1 line (no
    `compassbench_v1_3_public` sibling id or directory was found in the repository), so, unlike
    compassbench_20_v1_1, there is no evidence here that OpenCompass withholds part of this id's item
    set from open distribution.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "compassbench_v1_3 (opencompass/configs/datasets/compassbench_v1_3/*.py; aggregated by opencompass/configs/summarizers/compassbench_v1_3_objective.py)"
  bigbench: ""
  other: ""
tags:
  - composite
  - opencompass
  - compassbench
  - chinese
  - bilingual
  - code
  - agent
  - circular-evaluation
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_v1_3"
    title: "opencompass configs/datasets/compassbench_v1_3 (code_gen, knowledge, math, objective_gen, prompt configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/summarizers/compassbench_v1_3_objective.py"
    title: "compassbench_v1_3_objective.py summarizer (defines knowledge/math/code/agent groups; no top-level average; CIBench commented out of agent groups)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_v1_3/compassbench_v1_3_knowledge.py"
    title: "compassbench_v1_3_knowledge.py (ten wiki_en_sub_500 / wiki_zh_sub_500 domain splits)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_v1_3/compassbench_v1_3_math.py"
    title: "compassbench_v1_3_math.py (college-level single choice EN/CN, arithmetic cloze EN)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_v1_3/compassbench_v1_3_code_gen_c8c3aa.py"
    title: "compassbench_v1_3_code_gen_c8c3aa.py (code completion, code interview, TACO code competition)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/releases/tag/v0.3.1"
    title: "opencompass v0.3.1 release notes (\"Updated Compassbench to v1.3\", published 2024-08-23)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/releases/tag/v0.3.0"
    title: "opencompass v0.3.0 release notes (\"Add compassbench wiki&math part\" PR #1342; separate \"CompassBench Checklist Evaluation\" and \"Compassbench v1_3 subjective evaluation\" entries)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CompassBench v1.3 is OpenCompass's next dated release in the CompassBench line, but comparing its configuration files directly against `compassbench_20_v1_1` shows it is a restructured, genuinely different composite rather than an extension of it. It aggregates four category groups -- knowledge (English and Chinese Wikipedia-derived single-choice questions across four domains each; a fifth defined domain, life common sense, is not included in the shipped aggregation), mathematics (college-level single choice plus English arithmetic, narrower than v1.1's full arithmetic-through-college MathBench sweep), code (HumanEval-style completion, LCBench-style interview questions, and TACO-based competition problems), and agent (tool-planning only; a defined CIBench code-interpreter group is commented out of the active build). v1.1's language and reasoning categories have no counterpart here.

OpenCompass's release history separately references a "CompassBench Checklist Evaluation" and a "Compassbench v1_3 subjective evaluation" from the same development period; this page documents only the objective composite this id's configuration directory defines, not those other CompassBench-branded tracks, to avoid conflating differently-scoped evaluations that happen to share a name.

## How it is scored

Knowledge and the two college-level math splits are scored with OpenCompass's circular evaluation: the model must answer every permutation of a multiple-choice item's options correctly to be credited (`perf_4`), the same stricter, position-bias-resistant technique v1.1 uses. The arithmetic-cloze math split is graded by extracting a final boxed answer and checking it for correctness. The code category is scored by functional test execution: code-completion and code-interview items report pass@1 or pass@k across difficulty tiers, and the TACO-based code-competition split reports pass@1 per difficulty level (easy through very hard). The agent category is scored by T-Eval / plugin_eval's own tool-planning grading. Unlike v1.1's summarizer, v1.3's shipped configuration defines no combined score across all four categories -- the corresponding line is commented out of its summarizer file -- so results are four separate category averages, each itself a naive average across that category's constituent splits.

## Dataset and licence

No single item count is published for the composite, and this page did not download and count every constituent file. The configuration files confirm the shape directly: ten knowledge splits (four domains times English and Chinese, plus a fifth domain defined but not aggregated), whose file names embed "500" (`wiki_en_sub_500_<domain>`), suggesting roughly 500 items per split without this page independently verifying that count; three math splits (English college, Chinese college, English arithmetic); and thirteen code splits (two completion, six interview across three difficulties and two languages, five TACO competition difficulties). As with v1.1, the opencompass repository itself is Apache-2.0, but the composite draws in datasets with their own separate provenance (Wikipedia-derived knowledge items, TACO competitive-programming problems, HumanEval-style completion tasks), and no single licence covering the composite's data content specifically was found, so this page leaves `dataset.license` empty. Content is bilingual, English and Chinese, text and code.

## Who publishes it

CompassBench v1.3 is published by OpenCompass, maintained principally by Shanghai AI Laboratory, as part of the same CompassRank leaderboard project as `compassbench_20_v1_1`. No dedicated academic paper documents this composite; OpenCompass's GitHub release notes show its wiki-and-math portion landing around PR #1342 and a further update in PR #1396, both bundled into the opencompass v0.3.0 (2024-08-06) and v0.3.1 (2024-08-23, "Updated Compassbench to v1.3") releases, which this page uses to date the release rather than a paper.

## Lineage

CompassBench v1.3 follows `compassbench_20_v1_1` as the next dated release in the same OpenCompass project, and this page records that as `lineage.predecessor`, but the two are not score-comparable: v1.3 drops v1.1's language and reasoning categories outright, narrows math to college-level and arithmetic only, and rebuilds knowledge around a different per-domain wiki split rather than v1.1's WikiBench-plus-TriviaQA construction. No `compassbench_v1_2` was found in the repository, so the version numbering itself skips from 1.1 to 1.3. No further CompassBench version was found after v1.3 as of this research date, so no successor id is recorded. As noted above, OpenCompass's own release notes reference a separately-scoped "CompassBench Checklist Evaluation" and "subjective evaluation" from the same period that this page does not document.

## Saturation and contamination

OpenCompass's own CompassRank leaderboard would be the natural source for current standing, but its results table loads through client-side scripts this page's tools could not render, so no top score or saturation reading could be confirmed; this page records both as unknown rather than guessed. Contamination risk is medium: the code category reuses HumanEval-, LCBench- and TACO-style tasks whose problem styles are widely known and, for HumanEval and TACO specifically, long public, and the knowledge category draws from Wikipedia, a training-data staple. Unlike `compassbench_20_v1_1`, this page found no held-back "public" versus full-item split for v1.3 -- no `compassbench_v1_3_public` sibling id or data directory was found in the repository -- so there is no evidence OpenCompass withholds part of this id's item set from open distribution the way it appears to for the v1.1 line.

## How to run it

The reference implementation is the opencompass repository's own configuration files under `configs/datasets/compassbench_v1_3/` (`compassbench_v1_3_knowledge.py`, `compassbench_v1_3_math.py`, `compassbench_v1_3_code_gen_c8c3aa.py`, plus an `objective_gen` variant and shared agent-prompt templates), run through the OpenCompass evaluation framework and aggregated by `configs/summarizers/compassbench_v1_3_objective.py`. No other harness (lm-evaluation-harness, HELM, BIG-bench, inspect_evals) was confirmed to implement this composite. Because the knowledge and math prompts instruct the model to reason step by step before giving a final answer -- a different prompting style from v1.1's more direct question format -- a score obtained with a different prompt template is not guaranteed to match a published v1.3 number.

## Reading the numbers

Because the shipped summarizer defines no single blended score across all four categories, read knowledge, math, code and agent as four separate figures rather than hunting for one "CompassBench v1.3" number -- the top-level average line in its own configuration file is commented out. Do not compare a v1.3 score against a `compassbench_20_v1_1` score for the same category name expecting equivalence: v1.3's math category, for instance, covers only college-level and arithmetic problems, while v1.1's covers primary through college, so a higher v1.3 math score does not necessarily mean stronger overall math ability, only stronger performance on the narrower slice v1.3 tests. As with the v1.1 line, most items are graded by circular multiple choice, a stricter, position-bias-resistant accuracy measure than a single-pass score, so figures from a source using plain accuracy are not directly comparable to this page's `perf_4`-style numbers.
