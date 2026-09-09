---
id: perspectivegap
name: "PerspectiveGap"
aliases: []
page_kind: benchmark
category: agentic
subcategory: "multi-agent orchestration prompt composition (role-fragment assignment and free-form prompt writing)"
status: active
summary: "110 scenarios testing whether a model can write orchestration prompts that give each sub-agent in a multi-agent system exactly what it needs to know, without leaking irrelevant context."
measures: >
  Despite a name generic enough to suggest something about human perspective-taking or opinion
  polarisation, PerspectiveGap measures a narrower and more specific capability: whether a model can
  compose orchestration prompts for a multi-agent system by correctly working out what each
  sub-agent role actually needs to know, and, just as importantly, what it should not be told. Given
  a scenario describing a multi-agent workflow, the model must either assign the correct information
  fragments to each role (with distractor fragments mixed in) or write the orchestration prompt text
  itself from scratch. The 110 scenarios are organised into 10 orchestration "topologies" the authors
  say are distilled from their own real-world multi-agent engineering practice, and the benchmark is
  framed around what the paper calls the "Prompt Economy" principle: building orchestrations that
  reuse a small number of stable roles rather than proliferating roles and handoffs.
task_format: >
  Two distractor-mixed task formats scored separately and then averaged: role-fragment assignment
  (selecting which information fragments belong to which sub-agent role, out of a set that includes
  at least one injected distractor) and free-form prompt writing (generating the actual orchestration
  prompt text for a role). A separate ablation varies the injected-distractor count from 0 to 3.
metric:
  name: "Strict-pass rate (plus a separate information-leakage count)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    No random-guess baseline applies to free-form prompt writing, and none was reported for
    role-fragment assignment either. The paper's headline finding is how low scores are rather than
    where they sit relative to chance: across 33 commercial models from 10 companies, the average
    combined Strict-pass rate (the unweighted average of the two task formats) was 17.2%, and even
    the best model, GPT-5.5, reached only 62.0%. The paper separately reports an average "overall
    leakage rate" of 217.9% -- explicitly a per-scenario count of information-leak events, not a
    proportion, so it can and does exceed 100%.
dataset:
  size: 220
  size_note: >
    110 scenarios, each evaluated through both task formats, giving 220 rows total; confirmed via
    the Hugging Face datasets-server for the `sun1245/PerspectiveGap` dataset. The main results use
    one injected distractor per scenario; a separate appendix ablation reruns role-fragment
    assignment with 0 to 3 distractors to measure sensitivity to distractor count.
  url: "https://huggingface.co/datasets/sun1245/PerspectiveGap"
  license: "MIT, per the Hugging Face dataset card"
  languages:
    - en
  modalities:
    - text
  splits: "single 220-row test set (110 scenarios x 2 task formats); no train split published"
  public_test_set: true
publisher:
  org: "University of Maryland, with co-authors at the Chinese University of Hong Kong and Stanford University"
  authors:
    - "Youran Sun"
    - "Xingyu Ren"
    - "Kejia Zhang"
    - "Xinpeng Liu"
    - "Jiaxuan Guo"
  url: "https://github.com/WhymustIhaveaname/PerspectiveGap"
paper:
  title: "PerspectiveGap: A Benchmark for Multi-Agent Orchestration Prompting"
  arxiv: "2606.08878"
  url: "https://arxiv.org/abs/2606.08878"
  year: 2026
leaderboard_url: "https://huggingface.co/spaces/sun1245/PerspectiveGap-Leaderboard"
repo_url: "https://github.com/WhymustIhaveaname/PerspectiveGap"
released: "2026-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 62.0
  as_of: "2026-06"
  note: >
    Far from saturated: the paper reports an average combined Strict-pass rate of just 17.2% across
    33 evaluated commercial models, with the best model, OpenAI's GPT-5.5, reaching 62.0% (55.5% on
    role-fragment assignment, 68.6% on free-form prompt writing). The next-best company's top model,
    DeepSeek's deepseek-v4-pro, trailed at 32.0% combined, a large gap to the leader. The paper
    separately highlights that Anthropic's Opus 4.7 showed comparative weakness on this task despite
    strong coding performance elsewhere, which the authors treat as evidence orchestration-prompting
    is a distinct capability rather than one that tracks general coding or reasoning strength.
contamination:
  risk: medium
  note: >
    The dataset has been fully public on Hugging Face under an MIT licence, with no gating or
    canary string found, since its June 2026 release -- only about three months of exposure by this
    research date. The task format (writing orchestration prompts for a described multi-agent
    scenario) is also less amenable to simple memorisation than a fixed-answer question, which may
    partly offset the risk of a fully public, ungated release.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "perspectivegap (perspectivegap_role_assignment_gen, perspectivegap_prompt_writing_gen)"
  bigbench: ""
  other: >
    The benchmark's own repository states it was also merged into UKGovernmentBEIS/inspect_evals
    (two pull requests, both dated 2026-06) and into ModelScope's EvalScope (2026-07); both PRs were
    confirmed to exist on GitHub, but this page could not locate a corresponding task directory on
    inspect_evals' current main branch, so the inspect_evals field above is left empty rather than
    asserted.
tags:
  - agentic
  - multi-agent
  - prompt-engineering
  - orchestration
  - information-management
sources:
  - url: "https://arxiv.org/abs/2606.08878"
    title: "PerspectiveGap: A Benchmark for Multi-Agent Orchestration Prompting"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2606.08878"
    title: "PerspectiveGap paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/WhymustIhaveaname/PerspectiveGap"
    title: "WhymustIhaveaname/PerspectiveGap GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sun1245/PerspectiveGap"
    title: "sun1245/PerspectiveGap dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=sun1245/PerspectiveGap"
    title: "sun1245/PerspectiveGap split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/perspectivegap"
    title: "OpenCompass perspectivegap dataset configs"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/pull/1827"
    title: "inspect_evals PR #1827, Register submission: PerspectiveGap Role-Fragment Assignment"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Despite a name generic enough to suggest human perspective-taking or opinion polarisation, PerspectiveGap measures a specific, narrower capability: composing orchestration prompts for multi-agent LLM systems by correctly working out what each sub-agent role needs to know, and, just as importantly, what it should not be told. No other established benchmark carrying the exact same name was found, so the resemblance to broader perspective-taking research appears coincidental rather than a true collision -- the Hugging Face dataset card itself tags the benchmark "theory-of-mind," suggesting the authors intentionally frame information-partitioning across agent roles as an applied perspective-taking problem.

Given a scenario describing a multi-agent workflow, the model must either assign information fragments to the correct sub-agent role (role-fragment assignment, with distractors mixed in) or write the orchestration prompt text for a role from scratch (free-form prompt writing). The 110 underlying scenarios are organised into 10 orchestration "topologies" the authors describe as distilled from their own real-world engineering practice, framed around what the paper calls the "Prompt Economy" principle: orchestrations should reuse a small, stable set of roles rather than accumulate roles and handoffs without bound.

## How it is scored

Each of the 110 scenarios is scored under both task formats, and a model's headline number is the unweighted average of the two: role-fragment assignment (graded against which fragments correctly belong to which role) and free-form prompt writing (graded on whether the generated prompt correctly scopes each role's information). The paper's main results inject one distractor fragment per scenario; a separate appendix ablation varies that from 0 to 3 distractors to test sensitivity. Beyond the pass-rate metric, the paper separately reports an "overall leakage rate," an explicit per-scenario count of information-leak events rather than a proportion, meaning it can and does exceed 100% -- the average across evaluated models was 217.9%, with even GPT-5.5, the strongest model, still leaking information at a rate of 49.1%.

## Dataset and licence

PerspectiveGap totals 110 scenarios, each evaluated through both task formats for 220 rows total, confirmed directly against the Hugging Face datasets-server for `sun1245/PerspectiveGap`. There is no train split; the entire release is a single evaluation set, distributed under an MIT licence per the dataset's Hugging Face card. No dataset gating or canary string was found.

## Who publishes it

PerspectiveGap comes from Youran Sun (University of Maryland), Xingyu Ren, Kejia Zhang and Xinpeng Liu (the Chinese University of Hong Kong), and Jiaxuan Guo (Stanford University), posted to arXiv in June 2026. The authors maintain the reference implementation and scoring scripts at `github.com/WhymustIhaveaname/PerspectiveGap`, the dataset and an interactive leaderboard on Hugging Face under the `sun1245` account, and state that community result submissions are accepted through the repository.

## Lineage

This repository does not track a predecessor or successor for PerspectiveGap; it is a new benchmark with no earlier version to relate it to. Its own repository documents rapid third-party adoption (OpenCompass, inspect_evals, EvalScope, all within weeks of release); see How to run it for what this page could and could not confirm directly.

## Saturation and contamination

PerspectiveGap is far from saturated. Across 33 commercial models from 10 companies, the paper reports an average combined Strict-pass rate of just 17.2%, and even the strongest model, OpenAI's GPT-5.5, reached only 62.0% (55.5% on role-fragment assignment, 68.6% on free-form prompt writing) -- well clear of a ceiling, with a large gap to the next company's best model, DeepSeek's deepseek-v4-pro, at 32.0% combined. The paper also notes that Anthropic's Opus 4.7 performed comparatively weakly here despite strong coding results elsewhere, which the authors read as evidence that orchestration-prompting is a distinct, under-evaluated capability rather than one that simply tracks general coding or reasoning strength. Contamination risk is medium: the dataset has been fully public and ungated since its June 2026 release, but that is only around three months of exposure by this research date, and the free-form, scenario-based task format is less straightforward to answer from rote memorisation than a fixed-answer question would be.

## How to run it

OpenCompass implements both task formats as `perspectivegap-role_assignment` and `perspectivegap-prompt_writing`, reading the `sun1245/PerspectiveGap` dataset directly and scoring with dedicated evaluators for each format (`PerspectiveGapRoleAssignmentEvaluator` and `PerspectiveGapPromptWritingEvaluator`). The benchmark's own repository states it was also merged into inspect_evals and EvalScope within weeks of release, and this page confirmed the underlying pull requests exist on GitHub, but could not locate a matching task directory on inspect_evals' current main branch, so that harness field is left empty here rather than asserted from the repository's own claim alone. No lm-evaluation-harness, HELM or BIG-bench implementation was found.

## Reading the numbers

A high PerspectiveGap score indicates a model is unusually good at a specific, practical multi-agent engineering skill: scoping each sub-agent's information so it has what it needs without leaking context it does not, across a range of orchestration patterns -- not a general measure of agentic capability, coding skill, or reasoning strength, and the paper's own finding that a strong coding model (Opus 4.7) underperformed here is a direct caution against assuming those capabilities move together. Because the benchmark reports a leakage-event count alongside its pass rate, a model can post a moderate pass rate while still leaking substantially more information than a lower-scoring model, so the two numbers should be read together rather than the pass rate alone. Given how new and how far from ceiling this benchmark is, treat any single reported score as an early, likely-to-shift data point rather than a settled ranking.
