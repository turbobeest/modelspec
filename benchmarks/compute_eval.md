---
id: compute_eval
name: ComputeEval
aliases:
  - "NVIDIA ComputeEval"
  - "compute-eval"
page_kind: benchmark
category: coding
subcategory: "CUDA / GPU kernel code generation"
status: active
summary: NVIDIA's benchmark of CUDA programming challenges - a model must write CUDA code that compiles with nvcc and passes a held-out test harness, spanning kernels, runtime APIs and GPU libraries.
measures: >
  ComputeEval tests whether a model can write correct CUDA code from a natural-language
  specification. Each problem gives the model a prompt describing a GPU programming task, plus
  visible context files (headers defining the interface to implement, optional helper utilities)
  and the exact compiler command that will be used. Problems span seven domain groups: CUDA runtime
  (memory management, streams, kernel launch), CUDA kernels (shared memory, warp intrinsics,
  reductions, tensor cores), CCCL (Thrust, CUB, libcu++), cuBLAS, math libraries (cuSPARSE, cuSOLVER,
  cuFFT, cuRAND), cuDNN, and cuTile (Python tile-based kernels). Almost all current problems are C++
  CUDA; the Python problem type exists in the schema but the shipped dataset contains none as of
  this page's research.
task_format: >
  Given a prompt, interface header(s) and a fixed build command, the model must generate a CUDA
  source file. The solution is compiled with `nvcc` and run against a held-out test harness; a
  solution is scored correct only if compilation succeeds and every test case passes (exit code 0).
  Some problems also carry a `source_references` requirement (specific API calls or symbols that
  must appear in the solution) and an optional performance-benchmarking mode that times passing
  solutions against a reference implementation.
metric:
  name: "pass@1 (compiles and all hidden test cases pass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The reference harness supports pass@k more generally via a num_epochs / epoch_reducer
    configuration (generate multiple solutions per problem at temperature > 0 and reduce with
    "pass_at_k"), but the default and most commonly reported configuration is single-sample pass@1.
    No official NVIDIA leaderboard or paper-reported score was found; the closest published numbers
    this page located are from inspect_evals' own evaluation report (not an NVIDIA-run number):
    gpt-5-nano-2025-08-07 scored 45.3% (stderr +/-2.5%) and gpt-5.2-2025-12-11 scored 60.3%
    (stderr +/-2.4%), both against the then-current dataset version. inspect_evals' own README states
    plainly "no paper or leaderboard available for comparison."
dataset:
  size: 566
  size_note: >
    The dataset is explicitly under active, versioned development. Per NVIDIA's own release table:
    version 2025.1 shipped 127 problems, 2025.2 shipped 232, and 2025.3 shipped 406. Counting the
    current default/latest problems.jsonl directly (accessed 2026-09-08) gives 566 problems,
    confirming continued growth past the 406 documented in inspect_evals' release table; individual
    problem metadata (e.g. task CUDA/146, dated 2025-10-31) tags membership in a "2026-1" release not
    yet reflected in that table. Problems are also grouped by domain: cccl, cublas, cuda-kernels,
    cuda-runtime, cudnn, cutile and mathlibs, each independently loadable as a Hugging Face config.
  url: https://huggingface.co/datasets/nvidia/compute-eval
  license: "NVIDIA Evaluation Dataset License Agreement (data, custom licence, not OSI-standard); Apache 2.0 (evaluation-harness code)"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single 'eval' split per version/group config (default, 2025-1, 2025-2, 2025-3, 2026-1, and per-group configs); no train split"
  public_test_set: true
publisher:
  org: NVIDIA (NVIDIA Research)
  authors: []
  url: https://github.com/NVIDIA/compute-eval
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: https://github.com/NVIDIA/compute-eval
released: "2025-04"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.3
  as_of: "2025-12"
  note: >
    60.3% (gpt-5.2-2025-12-11, per inspect_evals' own evaluation report) leaves clear headroom and
    is a third-party research-harness run, not an NVIDIA-published leaderboard figure -- no
    independent, maintained leaderboard was found. Because the problem set itself keeps growing
    (127 to 232 to 406 to 566-plus problems across versions), scores from different dataset versions
    are not directly comparable even for the same model.
contamination:
  risk: medium
  note: >
    Each publicly downloadable problem record bundles the prompt, the full hidden test harness, and
    a baseline (reference) solution together in the same JSON row -- confirmed by inspecting a
    sample row directly. "Hidden" in the documentation means withheld from the model's context
    during a normal evaluation run by harness convention, not withheld from anyone who downloads the
    dataset, so the reference solutions are exposed to the same web/code corpora a model's training
    data is drawn from. This is partially offset by the benchmark's continual growth: newer problems
    (dated as recently as October 2025 in the sample reviewed) have had less time to be scraped into
    any given model's training cutoff than the original 2025.1 release.
harness:
  lm_eval: ""
  inspect_evals: "compute_eval"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - coding
  - cuda
  - gpu
  - code-generation
  - nvidia
sources:
  - url: https://github.com/NVIDIA/compute-eval
    title: "NVIDIA/compute-eval GitHub repository (README, problem structure, licence)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/nvidia/compute-eval
    title: "nvidia/compute-eval dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/compute_eval
    title: "inspect_evals compute_eval task README (parameters, scoring, evaluation report)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ComputeEval tests CUDA programming ability directly: given a natural-language description of a GPU
task, visible interface headers, and the exact compiler invocation that will be used, a model must
write CUDA source code that actually compiles and works. Problems are organised into seven domain
groups covering the practical range of CUDA development -- raw kernel and runtime work (memory
management, streams, launch configuration, warp intrinsics, tensor cores), Thrust/CUB/libcu++ via
CCCL, and the major GPU libraries (cuBLAS, cuSPARSE, cuSOLVER, cuFFT, cuRAND, cuDNN), plus an
emerging Python tile-based track (cuTile) that, as of this page's research, has no problems shipped
yet despite existing in the schema. This makes ComputeEval closer in spirit to HumanEval or MBPP
than to a general reasoning benchmark, but targeting a systems-programming domain (CUDA C++, mostly)
that general code benchmarks do not exercise.

## How it is scored

A submitted solution is compiled with `nvcc` against the problem's fixed build command and then run
against a held-out test harness; it counts as correct only if compilation succeeds with no errors
and every test case exits 0. Some problems add a `source_references` check requiring specific CUDA
API calls or symbols to appear in the solution, so a solution that compiles and passes tests by using
a different approach than intended can still be marked incorrect. The default reported metric is
single-sample pass@1; the harness also supports generating multiple samples per problem at
temperature above zero and reducing with a `pass_at_k` estimator for an unbiased pass@k figure,
plus an optional mode that benchmarks the execution time of passing solutions against a reference
implementation. There is no official NVIDIA-published leaderboard or paper reporting comparative
model scores; the numbers available (noted below) come from a third-party research harness, not
NVIDIA's own reporting.

## Dataset and licence

The dataset is explicitly described as under active, frequent development rather than fixed at
release. NVIDIA's own versioned releases went from 127 problems (2025.1) to 232 (2025.2) to 406
(2025.3); counting the current default problem file directly gives 566 problems as of this page's
research date, and individual problem metadata already tags a further "2026-1" release not yet
reflected in the version table this page could confirm. Data is released under a custom "NVIDIA
Evaluation Dataset License Agreement," distinct from the Apache 2.0 licence covering the separate
evaluation-harness code; problems are additionally organised into seven Hugging-Face-loadable domain
groups (cccl, cublas, cuda-kernels, cuda-runtime, cudnn, cutile, mathlibs). Problems were authored by
NVIDIA engineers, in some cases with generative assistance from frontier models, and reviewed by
human engineers before release.

## Who publishes it

ComputeEval is published by NVIDIA (NVIDIA Corporation, credited via NVIDIA Research), created
starting April 2025. No accompanying research paper was found -- inspect_evals' own documentation
states explicitly that no paper or leaderboard exists for comparison -- so this page leaves the
`paper` fields empty rather than inferring one. NVIDIA maintains the reference repository at
`NVIDIA/compute-eval` on GitHub (147 stars, actively pushed to as recently as August 2026) and the
dataset on Hugging Face, along with periodic "Engineering Diaries" technical write-ups documenting
development decisions.

## Lineage

ComputeEval has no predecessor or successor tracked in this repository. The name is generic enough
that this page checked specifically for other benchmarks sharing it: a GitHub and Hugging Face search
found no other project of comparable adoption using "ComputeEval" or "compute-eval" as its name --
NVIDIA's repository (147 stars) is far ahead of any similarly named project found, and this
repository's own census sources (the inspect_evals task directory and the `nvidia/compute-eval`
dataset) point at it unambiguously. No genuine naming collision was confirmed, unlike `r_bench`
elsewhere in this batch.

## Saturation and contamination

ComputeEval is open, not saturated: the only scores this page could confirm -- from inspect_evals'
own evaluation report rather than an NVIDIA leaderboard -- are 45.3% (gpt-5-nano-2025-08-07) and
60.3% (gpt-5.2-2025-12-11), both well below a ceiling. Because the problem set itself grows across
versions (127 to 566-plus problems observed), scores against different dataset versions are not
directly comparable even for an unchanged model.

Contamination risk is medium: a sample problem inspected directly for this page shows that the
public dataset row bundles the prompt, the complete hidden test harness, and the reference
(baseline) solution together -- "hidden" describes what the evaluation harness withholds from the
model's context during a run, not what is withheld from the published data itself, so reference
solutions are as exposed to web/code-scraping as any other public GitHub content. This is partly
offset by the benchmark's continual growth, since newer problems have had less time to enter any
given model's pretraining window than the original 2025.1 release.

## How to run it

The reference implementation and Dockerfile live in `NVIDIA/compute-eval` on GitHub, requiring an
NVIDIA GPU, CUDA Toolkit 12.0+, and `nvcc` in `PATH`. inspect_evals packages an independent
implementation as the `compute_eval` task, explicitly built to match NVIDIA's own prompt and system-
message format for comparability, configurable via `dataset_version` (a specific dated release or
the latest default), `num_epochs`/`epoch_reducer` for pass@k, `temperature`, and an optional Docker
sandbox for isolating generated-code execution (recommended, since the harness compiles and runs
machine-generated code). No lm-evaluation-harness, HELM, OpenCompass or BIG-bench implementation was
confirmed. Because the dataset version affects both problem count and difficulty mix, a reported
ComputeEval score should always be checked against which `dataset_version` produced it.

## Reading the numbers

A high ComputeEval score means a model can produce CUDA code that actually compiles with `nvcc` and
passes a real test harness across a range of GPU programming domains -- a considerably stronger bar
than passing a general Python coding benchmark, since it requires correct memory management,
synchronization and (for library-backed problems) correct API usage in a domain with far less public
training data than mainstream languages. It says nothing about code outside CUDA/GPU programming, and
a pass@1 figure alone does not capture solution quality or performance -- the harness's separate,
opt-in performance-benchmarking mode is needed to check whether a passing solution is also fast.
Because both the dataset version and the sampling/pass@k configuration materially change the
reported number, and because no official leaderboard exists to cross-check a claimed score against,
treat any single ComputeEval figure as provisional until you know which version and configuration
produced it.
