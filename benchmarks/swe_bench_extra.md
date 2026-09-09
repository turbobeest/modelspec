---
id: swe_bench_extra
name: SWE-bench Extra
aliases: []
page_kind: benchmark
category: coding
subcategory: GitHub issue resolution / patch generation
status: active
summary: SWE-bench Extra is a 6,415-instance dataset of real GitHub issue-and-fix pairs, built with the SWE-bench methodology to extend beyond the original benchmark's repositories.
measures: >
  SWE-bench Extra follows the SWE-bench task design: given a real GitHub issue and a snapshot of the
  repository at the commit before the fix, a model or agent must produce a patch that resolves the
  issue, verified by the project's own tests. It extends the pool of such tasks well beyond the
  original SWE-bench's 12 repositories, drawing issue-and-pull-request pairs from 1,988 Python
  repositories, and is positioned for training and evaluating agentic systems that resolve GitHub
  issues rather than as a fixed leaderboard benchmark.
task_format: >
  Given an issue description and a repository checkout, the system produces a patch/diff, applied to
  a container and graded against tests recovered from the pull request that originally closed the
  issue, following the SWE-bench protocol.
metric: {name: "% resolved (FAIL_TO_PASS and PASS_TO_PASS tests pass)", direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "No baseline or leaderboard was found in the sources reviewed; the dataset card presents it as a training/evaluation resource rather than a scored competition."}
dataset: {size: 6415, size_note: "6,415 issue-and-pull-request pairs across 1,988 Python repositories; the published Hugging Face split totals 6,376 examples (~88MB uncompressed, ~25MB download).", url: "https://huggingface.co/datasets/nebius/SWE-bench-extra", license: CC-BY-4.0, languages: [Python], modalities: [code, text], splits: "single 'train' split", public_test_set: null}
publisher: {org: Nebius, authors: [], url: "https://huggingface.co/datasets/nebius/SWE-bench-extra"}
paper: {title: "", arxiv: "", url: "", year: null}
leaderboard_url: ""
repo_url: https://huggingface.co/datasets/nebius/SWE-bench-extra
released: ""
last_updated: ""
lineage: {family: swe_bench, predecessor: swe_bench, successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "No scored leaderboard or reported model results were found in the sources reviewed."}
contamination: {risk: unknown, note: "Built from real, public GitHub issues and pull requests in the SWE-bench style; the dataset card does not state a decontamination or training-data exclusion process."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: "Uses the SWE-bench task/container evaluation methodology per the dataset card; no specific harness task name was found."}
tags: [benchmark, coding, agentic, github-issues]
sources:
  - url: https://huggingface.co/datasets/nebius/SWE-bench-extra
    title: "nebius/SWE-bench-extra dataset card"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/nebius/SWE-bench-extra
    title: "nebius/SWE-bench-extra dataset metadata (API)"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-003"}
---
## What it measures

SWE-bench Extra follows the same task design as SWE-bench: a system is given a real GitHub issue and
a snapshot of the repository at the commit before the fix, and must produce a patch that resolves the
issue, checked against the project's own tests. Rather than adding a new task format, it extends the
pool of such tasks beyond SWE-bench's original 12 repositories, drawing issue-and-pull-request pairs
from 1,988 distinct Python repositories.

The dataset card describes it as intended "to train or evaluate agentic systems specializing in
resolving GitHub issues," which positions it as a larger and more diverse pool of SWE-bench-style
tasks for training or broad evaluation rather than a fixed, leaderboard-graded benchmark release.

## How it is scored

Scoring follows the SWE-bench convention when used for evaluation: a patch is applied to a
containerised checkout and the instance counts as resolved only if the FAIL_TO_PASS tests recovered
from the original pull request now pass and the PASS_TO_PASS tests continue to pass. No random or
human baseline, and no published leaderboard score, was found in the sources reviewed.

## Dataset and licence

The dataset contains 6,415 issue-and-pull-request pairs collected across 1,988 Python repositories,
published under the CC-BY-4.0 licence. The Hugging Face release lists a single "train" split of 6,376
examples, roughly 88MB uncompressed. Each example includes fields such as instance ID, base commit,
patch, repository name, and problem statement, matching the SWE-bench instance schema.

## Who publishes it

SWE-bench Extra is published by Nebius on Hugging Face. No accompanying paper or named author list was
found in the sources reviewed, and the dataset card does not identify a maintained leaderboard.

## Lineage

SWE-bench Extra is built using the SWE-bench methodology and instance schema, so it is recorded here
in the SWE-bench family with SWE-bench itself as its predecessor. It is not a subset of SWE-bench's
own repositories: it collects pairs from a much larger and different pool of 1,988 repositories, so it
should be treated as an independent, larger dataset in the same style rather than a sample of the
original benchmark.

## Saturation and contamination

No leaderboard or reported model scores were found in the sources reviewed, so saturation status is
unknown. Contamination risk is also unknown: the underlying issues and pull requests are public
GitHub content in the same style as SWE-bench, which has a documented risk of appearing in training
data, but the dataset card does not state a decontamination process for this specific collection.

## How to run it

No lm-evaluation-harness, HELM, or OpenCompass task name was found in the sources reviewed. The
dataset card indicates it follows the SWE-bench evaluation methodology (patch application inside a
container, graded by the project's recovered tests), so the reference SWE-bench harness is the
practical way to run it, though this was not explicitly confirmed as a packaged task in that harness.

## Reading the numbers

Because SWE-bench Extra has no established leaderboard in the sources reviewed, a reported score
should be read as a self-reported result on this specific 6,415-instance pool rather than a comparison
against other models' scores. A high resolve rate indicates the system can locate and fix real issues
across a wide variety of unfamiliar Python repositories, which is a broader test of generalisation than
SWE-bench's original 12 repositories. Results are not directly comparable to SWE-bench or SWE-bench
Verified scores, since the task pool, and therefore task difficulty distribution, differs. Treat the
dataset primarily as a training and evaluation resource rather than a standardized benchmark until a
leaderboard or comparative study is published.
