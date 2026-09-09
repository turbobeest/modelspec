---
id: harm_bench_gcg_transfer
name: "HarmBench GCG-Transfer (GCG-T)"
aliases:
  - "HarmBenchGCGTransfer"
  - "GCG-T"
  - "HarmBench GCG-T"
page_kind: benchmark
category: safety
subcategory: "HarmBench behaviors attacked with precomputed, transferred Greedy Coordinate Gradient (GCG) adversarial suffixes"
status: active
summary: "HarmBench behaviors attacked with GCG suffixes optimized once against four open models and transferred unchanged to the target; a lower Attack Success Rate is the safety-desirable outcome."
measures: >
  harm_bench_gcg_transfer evaluates the same textual behaviors as [HarmBench](harm_bench.md), but
  instead of the plain, undisguised request, each behavior is appended with an adversarial suffix
  produced by GCG-Transfer (GCG-T). HarmBench's own paper describes GCG-T as extending GCG-Multi by
  "simultaneously optimizing against multiple training models" -- specifically Llama 2 7B Chat, Llama
  2 13B Chat, Vicuna 7B and Vicuna 13B -- "to yield test cases that can be transferred to all models."
  Unlike a directly optimized GCG attack, the attacker never touches the model actually being
  evaluated: a fixed set of suffixes, computed once against those four training models, is applied
  unchanged to whichever target model is under test. This is a black-box, universal-suffix threat
  model, meaningfully weaker in general than a per-target, white-box optimized attack, and HarmBench's
  own results bear that out directly (see Saturation and contamination).
task_format: >
  Each HarmBench behavior string is paired with one precomputed GCG-T suffix; the concatenated
  (behavior + suffix) text is sent to the target model as a single-turn prompt with no further attack
  logic applied at evaluation time, the model's completion is generated, and a classifier judges
  whether the completion exhibits the harmful behavior -- structurally identical to HarmBench's own
  pipeline, just with one fixed, precomputed attack applied to every prompt instead of the unmodified
  behavior text.
metric:
  name: "Attack Success Rate (ASR) under transferred GCG suffixes"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    As with the parent HarmBench page, a lower ASR under this fixed attack is the safety-desirable
    reading. HELM's own implementation reports a `safety_score` on a 0-1 scale (1 = fully refused, 0.5
    = complied without an explicit refusal, 0 = complied), produced by an independent LLM judge -- the
    mathematical near-complement of ASR, on a different scale, from a different grading method than
    HarmBench's own fine-tuned classifier. No random or human baseline is defined for this attack
    specifically.
dataset:
  size: 401
  size_note: >
    The precomputed suffix set that HELM's `harm_bench_gcg_transfer` scenario actually reads (see How
    to run it) contains 401 (behavior, suffix) rows with 401 unique behavior names, counted directly
    with a CSV parser -- close to, but not exactly, HarmBench's 400 textual behaviors. HarmBench's own
    paper reports GCG-T results across "All Behaviors -- Standard, Contextual and Copyright" (its
    Table 6), i.e. the same ~400-behavior textual set, evaluated as a whole rather than split by the
    official validation/test partition.
  url: "https://github.com/farzaank/harmbench-gcg-ensembled"
  license: >
    Not stated. The GitHub repository hosting the precomputed suffixes HELM reads
    (farzaank/harmbench-gcg-ensembled) has no LICENSE file and essentially no README beyond its title,
    confirmed by opening both directly; the underlying HarmBench behavior strings themselves are
    MIT-licensed via the parent centerforaisafety/HarmBench project.
  languages: [en]
  modalities: [text]
  splits: "single undifferentiated set of 401 (behavior + suffix) pairs; does not follow HarmBench's own official validation/test split"
  public_test_set: true
publisher:
  org: >
    The GCG-Transfer attack method and its evaluation within HarmBench are published by the Center for
    AI Safety (CAIS) and co-authors (see harm_bench.md); the specific precomputed suffix file HELM
    reads is hosted in a separate, minimally documented GitHub repository under the account
    "farzaank," whose institutional affiliation, if any, was not stated anywhere this page checked.
  authors: []
  url: "https://github.com/farzaank/harmbench-gcg-ensembled"
paper:
  title: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"
  arxiv: "2402.04249"
  url: "https://arxiv.org/abs/2402.04249"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/centerforaisafety/HarmBench"
released: "2024-02"
last_updated: ""
lineage:
  family: harm_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2024-02"
  note: >
    Left unset for the same inverted-desirability reason as the parent HarmBench page. What is well
    established from HarmBench's own Table 6 is the shape of the effect: GCG-T produces markedly lower
    ASR than directly optimized attacks against the same models -- 1.8% on Llama 2 7B Chat and 19.8% on
    Vicuna 7B, against 21.2% and 61.5% respectively for plain (per-target) GCG on those same two models
    in the same table. That gap is the point of this variant: it isolates how much of a model's
    apparent robustness depends on the attacker never having access to the target model itself. No
    2025-2026 frontier-model figures were found for this page.
contamination:
  risk: medium
  note: >
    Beyond the risks already described for HarmBench itself, this variant carries an attack-specific
    staleness risk: its suffixes were optimized in 2023-2024 against four now-dated open models (Llama
    2 7B/13B Chat, Vicuna 7B/13B). A low ASR against a current model under this specific attack may
    partly reflect that the fixed suffixes are a poor match for newer model families and tokenizers,
    rather than evidence the target is broadly robust to transfer attacks in general -- a
    freshly-optimized transfer attack against current training models could plausibly score
    differently. No source read for this page re-ran GCG-T optimization against more recent models.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "harm_bench_gcg_transfer"
  opencompass: ""
  bigbench: ""
  other: >
    HELM's harm_bench_gcg_transfer_scenario.py downloads its test cases from
    github.com/farzaank/harmbench-gcg-ensembled (file `output.csv`), not from the official
    centerforaisafety/HarmBench repository -- confirmed by reading the scenario source directly. The
    official repository's own changelog mentions a "precomputed test cases" update (PR #19, February
    2024), but no directory of official precomputed GCG-T suffixes was located at the paths this page
    checked, so whether HELM's third-party source matches an official release could not be confirmed.
tags:
  - safety
  - red-teaming
  - jailbreak
  - gcg
  - adversarial-suffix
  - transfer-attack
  - attack-success-rate
sources:
  - url: "https://arxiv.org/abs/2402.04249"
    title: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.04249"
    title: "HarmBench, full text (ar5iv) -- GCG-Transfer method description, Table 6 (ASR by model and attack)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2307.15043"
    title: "Universal and Transferable Adversarial Attacks on Aligned Language Models (Zou et al. 2023, origin of GCG and GCG-Transfer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/harm_bench_gcg_transfer_scenario.py"
    title: "HELM harm_bench_gcg_transfer_scenario.py (data source, prompt construction)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/harm_bench_annotator.py"
    title: "HELM harm_bench_annotator.py (shared LLM-judge grading prompt, 0/0.5/1 scale)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/farzaank/harmbench-gcg-ensembled/refs/heads/main/output.csv"
    title: "farzaank/harmbench-gcg-ensembled output.csv (401 precomputed behavior+suffix pairs, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/farzaank/harmbench-gcg-ensembled/main/README.md"
    title: "farzaank/harmbench-gcg-ensembled README (title only, no further documentation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/README.md"
    title: "centerforaisafety/HarmBench GitHub README (\"precomputed test cases\" changelog entry, PR #19)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

harm_bench_gcg_transfer evaluates the same textual behaviors as [HarmBench](harm_bench.md), but instead
of the plain, undisguised request, each behavior is appended with an adversarial suffix produced by
GCG-Transfer (GCG-T). HarmBench's own paper describes GCG-T as extending GCG-Multi by "simultaneously
optimizing against multiple training models" -- specifically Llama 2 7B Chat, Llama 2 13B Chat, Vicuna
7B and Vicuna 13B -- "to yield test cases that can be transferred to all models." The crucial difference
from a directly optimized GCG attack is that the attacker never touches the model actually being
evaluated: the same fixed suffixes, computed once against those four training models, are applied
unchanged to whichever target is under test. That makes GCG-T a black-box, universal-suffix threat
model rather than a per-target, white-box one, and it is meaningfully weaker in practice, as the
original paper's own results show directly.

## How it is scored

Each behavior string is paired with one precomputed GCG-T suffix; the concatenated (behavior + suffix)
text goes to the target model as a single-turn prompt with no further attack logic applied at
evaluation time, the completion is generated, and a classifier judges whether it exhibits the harmful
behavior -- the same pipeline HarmBench itself uses, with one fixed attack baked into every prompt
rather than the bare behavior text. HELM's implementation departs from the original paper's scoring in
the same way it does for plain HarmBench: it grades with its own LLM-judge prompt (`safety_score`, 0-1,
1 meaning full refusal) rather than HarmBench's fine-tuned Llama-2-13B classifier.

## Dataset and licence

The precomputed suffix set HELM's scenario actually downloads contains 401 (behavior, suffix) rows with
401 unique behavior names, counted directly -- close to but not identical to HarmBench's 400 textual
behaviors. Notably, this file is hosted at github.com/farzaank/harmbench-gcg-ensembled, not in the
official centerforaisafety/HarmBench repository, confirmed by reading HELM's scenario source. That
repository has no LICENSE file and no documentation beyond its title, and the account's institutional
affiliation, if any, was not found; the underlying behavior strings are MIT-licensed through the parent
HarmBench project, but the specific suffixes used here come from an unattributed, minimally documented
third-party source that this page cannot independently vouch for.

## Who publishes it

GCG-Transfer as a method comes from Zou et al. 2023 (arXiv 2307.15043); its evaluation within HarmBench,
under the GCG-T abbreviation, is published by the Center for AI Safety and co-authors credited on the
parent [HarmBench](harm_bench.md) page. The precomputed suffix artifact that HELM's benchmark
implementation actually depends on is hosted separately, under the GitHub account "farzaank," with no
paper, institution or documentation attached that this page could find.

## Lineage

harm_bench_gcg_transfer is a variant of [HarmBench](harm_bench.md), reusing its behavior set and
classifier-based grading approach rather than introducing new behaviors; it applies one specific attack
method (GCG-Transfer) that HarmBench's own paper evaluates as one of 18 red-teaming methods compared
side by side. GCG-Transfer itself descends from GCG and GCG-Multi (Zou et al. 2023), the same paper
behind the smaller AdvBench dataset HarmBench's own Lineage section discusses. No further successor or
variant of this specific transfer attack is tracked in this repository.

## Saturation and contamination

Saturation here is best read as a gap, not a single ceiling. HarmBench's own Table 6 shows GCG-T
producing markedly lower ASR than directly optimized attacks against the same models: 1.8% on Llama 2
7B Chat and 19.8% on Vicuna 7B, against 21.2% and 61.5% respectively for plain, per-target GCG on those
same two models. That gap is the point of running this variant at all -- it isolates how much of a
model's apparent robustness depends on the attacker never having direct access to the target. No
2025-2026 frontier-model figures were found for this page. Contamination risk is medium, with an
attack-specific wrinkle beyond what applies to HarmBench generally: the suffixes were optimized in
2023-2024 against four now-dated open models, so a low ASR against a current model may partly reflect
that the fixed suffixes are a poor match for newer model families and tokenizers, rather than
demonstrating the target is broadly robust to transfer attacks -- a freshly re-optimized transfer attack
against current models could plausibly score differently, and no source read for this page re-ran that
optimization.

## How to run it

HELM implements this as the `harm_bench_gcg_transfer` scenario, downloading its precomputed test cases
from `github.com/farzaank/harmbench-gcg-ensembled` rather than from the official HarmBench repository --
confirmed directly from the scenario's source code. The official repository's own changelog references
a "precomputed test cases" update from February 2024 (PR #19), but no directory of official precomputed
GCG-T suffixes was found at the paths this page checked, so whether HELM's third-party source matches
an official release is not established here. No lm-evaluation-harness, OpenCompass or inspect_evals
implementation was found.

## Reading the numbers

A low ASR here shows a model resists this one specific, precomputed, black-box transfer attack -- a
real but narrow claim. It says little about robustness to attacks optimized directly against the target
model, which HarmBench's own results show can push ASR far higher on the same models; treat a strong
GCG-Transfer result as a floor on robustness, not a ceiling. Because the precomputed suffixes come from
a third-party source this page could not fully vouch for, and because they were optimized against
specific, now-dated 2023-era models, corroborate any striking GCG-Transfer result against
[HarmBench](harm_bench.md)'s own direct-request and stronger-attack numbers before drawing conclusions
about a model's general jailbreak resistance.
