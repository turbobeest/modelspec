---
id: air_bench
name: AIR-Bench 2024
aliases:
  - AIR-Bench
  - AIRBench 2024
  - AI Risk Benchmark
page_kind: benchmark
category: safety
subcategory: regulation-grounded risk-category safety benchmark
status: active
summary: >-
  5,694 prompts judged against a 314-category safety taxonomy built from real government regulations
  and company policies; distinct from two other, unrelated benchmarks also named AIR-Bench.
measures: >
  AIR-Bench 2024 tests whether a model's responses align with safety expectations drawn directly from
  real government regulations and company usage policies, rather than from researcher intuition about
  what safety should mean. Each of its 5,694 prompts targets one of 314 fine-grained risk categories,
  organised into a four-level taxonomy built by decomposing 8 government regulations (EU, US and China)
  and 16 AI-company usage policies. A model is scored on how it responds to a risk-eliciting prompt:
  whether it refuses, redirects, or complies with a request that sits in one of these regulation-derived
  categories. This page documents AIR-Bench 2024, the AI-safety benchmark from arXiv 2407.17436 — see
  "Lineage" for the unrelated benchmarks that share its name.
task_format: >
  Single-turn text prompt drawn from one of 314 risk categories; the model's free-text response is graded
  by an LLM judge against a category-specific rubric on a three-point scale.
metric:
  name: "AIR score (judge-scored safety compliance)"
  direction: higher_is_better
  unit: "score (0-1)"
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Each response is scored on a three-point rubric by an LLM judge (GPT-4o in the original paper): 0 for
    complying with a clearly harmful request, 0.5 for an ambiguous or indirectly complying response, and
    1 for an appropriate refusal or safe redirection, then averaged per category and overall. No
    random-guess or human baseline applies to a judge-graded refusal task, and none was published by the
    authors; they instead report human/GPT-4o judge agreement (Cohen's kappa around 0.86).
dataset:
  size: 5694
  size_note: >
    5,694 prompts in the default evaluation split, each mapped to one of 314 leaf risk categories under a
    four-tier taxonomy (4 top-level, 16, 45, then 314 categories). The Hugging Face release also ships
    four overlapping jurisdiction-filtered views of the same prompt pool (china 4,420 rows;
    eu_comprehensive 4,130; eu_mandatory 3,400; us 3,920) plus a 314-row judge_prompts split holding one
    grading rubric per leaf category.
  url: https://huggingface.co/datasets/stanford-crfm/air-bench-2024
  license: CC-BY-4.0
  languages:
    - en
  modalities:
    - text
  splits: >-
    single default test split (5,694 prompts) plus 4 overlapping jurisdiction-filtered views and a
    judge_prompts split; no train/test division
  public_test_set: true
publisher:
  org: ""
  authors:
    - Yi Zeng
    - Yu Yang
    - Andy Zhou
    - Jeffrey Ziwei Tan
    - Yuheng Tu
    - Yifan Mai
    - Kevin Klyman
    - Minzhou Pan
    - Ruoxi Jia
    - Dawn Song
    - Percy Liang
    - Bo Li
  url: https://github.com/stanford-crfm/air-bench-2024
paper:
  title: "AIR-Bench 2024: A Safety Benchmark Based on Risk Categories from Regulations and Policies"
  arxiv: "2407.17436"
  url: https://arxiv.org/abs/2407.17436
  year: 2024
leaderboard_url: https://crfm.stanford.edu/helm/air-bench/v1.0.0/
repo_url: https://github.com/stanford-crfm/air-bench-2024
released: "2024-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 0.847
  as_of: "2024-07"
  note: >
    0.847 (Claude 3 Sonnet, 2024-02-29) was the top AIR score among the roughly 21 models HELM evaluated
    at the benchmark's original v1.0.0 publication; scores for that first cohort ranged narrowly, from
    0.631 to 0.847, among mostly 2024-era models rather than sitting at a hard ceiling. This research did
    not find a newer HELM AIR-Bench snapshot with current frontier models, so whether scores have since
    pushed closer to 1.0, or the public leaderboard has simply gone stale, was not established.
contamination:
  risk: medium
  note: >
    The prompt set and its full taxonomy are published openly under CC-BY-4.0, so a model trained after
    July 2024 on broadly scraped web or research data could plausibly have encountered these exact
    prompts or close paraphrases. Because scoring depends on refusal behaviour rather than a hidden
    correct answer, the more direct risk is a lab safety-tuning specifically against this or a similar
    published taxonomy, rather than passive pretraining contamination.
harness:
  lm_eval: ""
  inspect_evals: air_bench
  helm: air_bench_2024
  opencompass: ""
  bigbench: ""
  other: >
    HELM's run-spec function get_air_bench_2024_spec (registered as "air_bench_2024") takes a subset
    argument matching the dataset's default/china/eu_comprehensive/eu_mandatory/us splits and grades with
    the shipped judge_prompts. inspect_evals registers the same benchmark as inspect_evals/air_bench. Both
    of these confirmed "air_bench" harness implementations load stanford-crfm/air-bench-2024 — the
    safety-risk dataset — not the unrelated audio-language dataset that also carries the AIR-Bench name.
tags:
  - safety
  - regulation-grounded
  - risk-taxonomy
  - refusal
  - llm-judge
  - red-teaming
sources:
  - url: https://arxiv.org/abs/2407.17436
    title: "AIR-Bench 2024: A Safety Benchmark Based on Risk Categories from Regulations and Policies"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/air-bench-2024
    title: "stanford-crfm/air-bench-2024 repository (README, licences)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/stanford-crfm/air-bench-2024
    title: "stanford-crfm/air-bench-2024 dataset card"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/stanford-crfm/air-bench-2024
    title: "stanford-crfm/air-bench-2024 dataset API metadata (license, splits, tags)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/air_bench_scenario.py
    title: "HELM air_bench_scenario.py (AIRBench2024Scenario)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/air_bench_run_specs.py
    title: "HELM air_bench_run_specs.py, get_air_bench_2024_spec / run_spec_function(\"air_bench_2024\")"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/air_bench
    title: "inspect_evals air_bench task (README, registry name)"
    accessed: "2026-09-08"
  - url: https://crfm.stanford.edu/helm/air-bench/v1.0.0/
    title: "HELM AIR-Bench 2024 leaderboard v1.0.0 (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2402.07729
    title: "AIR-Bench: Benchmarking Large Audio-Language Models via Generative Comprehension (the other AIR-Bench)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2412.13102
    title: "AIR-Bench: Automated Heterogeneous Information Retrieval Benchmark (a third, unrelated AIR-Bench)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AIR-Bench 2024 tests whether a model's responses align with safety expectations drawn directly from real
government regulations and company usage policies, rather than from researcher intuition about what
safety should mean. Each of its 5,694 prompts targets one of 314 fine-grained risk categories, organised
into a four-level taxonomy (4 broad categories, then 16, then 45, then 314 leaf categories) built by
decomposing 8 government regulations from the EU, US and China and 16 AI-company usage policies. A model
is scored on how it responds to a risk-eliciting prompt: whether it refuses, redirects, or complies with a
request that sits in one of these regulation-derived risk categories.

This page documents AIR-Bench 2024, the AI-safety benchmark from arXiv 2407.17436. The name "AIR-Bench" is
also used, unrelated, for at least two other benchmarks: an audio-language-model benchmark from arXiv
2402.07729 (GitHub: OFA-Sys/AIR-Bench), and an "Automated Heterogeneous Information Retrieval Benchmark"
from arXiv 2412.13102 — neither covered here. The harness evidence for this id is unambiguous: both
HELM's and inspect_evals' "air_bench" implementations load the safety-risk dataset
(stanford-crfm/air-bench-2024), not the audio one.

## How it is scored

Every prompt is graded by an LLM judge (GPT-4o in the original paper) against a rubric specific to its
leaf risk category — the dataset ships 314 such rubrics, one per category, as a separate judge_prompts
split. Grading uses a three-point scale: 0 for a response that complies with a clearly harmful request,
0.5 for an ambiguous or indirectly complying response, and 1 for an appropriate refusal or safe
redirection. Per-category and overall scores are the mean of these per-prompt judgments, so a model's "AIR
score" is a judge-graded refusal-appropriateness rate. The authors support using GPT-4o this way with a
reported human/judge agreement study (Cohen's kappa about 0.86).

## Dataset and licence

The default evaluation split holds 5,694 prompts, each labelled with its position in the four-level
taxonomy. The Hugging Face release also ships four overlapping jurisdiction views of the same prompt pool (China,
EU-comprehensive, EU-mandatory, US), plus the 314-row judge_prompts split. The authors decomposed
regulatory and policy source text into machine-readable risk categories; the resulting prompts and
taxonomy are released under a CC-BY-4.0 licence on Hugging Face, with the surrounding evaluation code
under Apache 2.0 on GitHub. English only, text only.

## Who publishes it

AIR-Bench 2024 comes from a large multi-institution author group — Yi Zeng, Yu Yang, Andy Zhou, Jeffrey
Ziwei Tan, Yuheng Tu, Yifan Mai, Kevin Klyman, Minzhou Pan, Ruoxi Jia, Dawn Song, Percy Liang and Bo Li —
spanning Stanford, UC Berkeley, Virginia Tech, UCLA, UIUC, Harvard, Northeastern, the University of
Chicago and Lapis Labs, posted to arXiv in July 2024. Stanford CRFM hosts the reference leaderboard as
part of HELM and the dataset/code repository carries the Stanford CRFM name, though authorship spans
many institutions, not one lab.

## Lineage

AIR-Bench 2024 names no formal predecessor; the authors position it as a response to earlier safety
benchmarks that define categories from prior literature or intuition rather than regulatory text. It has
no official successor and no variant pages in this repository. It should not be confused with the other
two AIR-Benches described above — the shared name is coincidence, not lineage.

## Saturation and contamination

At its original HELM v1.0.0 publication, scores among the roughly 21 models evaluated ranged narrowly,
from 0.631 up to 0.847 (Claude 3 Sonnet, the top scorer) — a compressed spread among mostly 2024-era
models rather than a hard ceiling, which this page records as "watch" rather than "saturated" or "open."
This research did not find a newer HELM snapshot with current frontier models, so whether that gap has
since closed was not established. Contamination risk sits at medium: the prompts and full taxonomy are
published openly, so a model trained on broadly scraped data after July 2024 could plausibly have
encountered them; because grading depends on refusal behaviour rather than a single hidden correct answer,
the more direct risk is safety-tuning specifically against this or a similar published taxonomy rather
than passive pretraining memorisation.

## How to run it

HELM's reference implementation is the `air_bench_2024` run-spec (function `get_air_bench_2024_spec`),
which takes a `subset` argument matching the dataset's default/china/eu_comprehensive/eu_mandatory/us
splits and grades with the shipped judge prompts. inspect_evals registers the same benchmark as
`inspect_evals/air_bench`. Because grading runs through an LLM judge, scores depend on which judge model
is used and its snapshot date; the original paper and HELM's reference implementation both used GPT-4o,
and a score produced with a different judge is not guaranteed to be comparable.

## Reading the numbers

Before citing any "AIR-Bench" number, confirm which benchmark of that name is meant — this page covers
the regulation-grounded AI-safety version (arXiv 2407.17436), not the other two benchmarks sharing the
name. A high AIR score shows a model tends to refuse or
safely redirect prompts that map to real regulatory and policy risk categories; it does not show the
model is safe against attacks outside this specific 314-category taxonomy, and because grading runs
through an LLM judge, scores are only strictly comparable when the same judge model produced them.
