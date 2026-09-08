---
id: kernelbench
name: "KernelBench"
aliases:
  - "KernelBench: Can LLMs Write Efficient GPU Kernels?"
page_kind: benchmark
category: coding
subcategory: "GPU kernel generation from PyTorch reference code, scored on both functional correctness and runtime speedup"
status: active
summary: A model rewrites PyTorch workloads as GPU kernels; fast_p scores the share that are both correct and at least p times faster than the PyTorch baseline.
measures: >
  KernelBench asks a model to replace a PyTorch reference implementation -- a single operator, a
  small fused pattern, or a full neural network architecture -- with a custom GPU kernel that
  computes the same result, faster. Problems are organized into four difficulty levels: Level 1
  (100 single-kernel operators such as convolutions, matrix multiplies and normalization layers),
  Level 2 (100 simple fusion patterns, such as a convolution followed by a bias add and a ReLU,
  where fusing operations into one kernel should beat running them separately), Level 3 (50 full
  model architectures such as MobileNet, VGG, MiniGPT and Mamba, requiring end-to-end kernel
  optimization), and Level 4 (20 Hugging Face model architectures, added in a July 2025 update).
  The default backend is raw CUDA, but the harness also supports Triton, CUTE, TileLang,
  ThunderKittens and HIP (for AMD GPUs). The benchmark exercises both a model's ability to write
  functionally correct low-level GPU code and its ability to make that code fast -- these are
  graded separately, not folded into one pass/fail check.
task_format: >
  A PyTorch nn.Module reference implementation in; a replacement implementation that calls a
  custom GPU kernel out. The generated kernel is compiled and executed, then checked for
  correctness against the reference on randomized inputs and timed against it for speed, inside a
  Docker sandbox.
metric:
  name: "fast_p (share of tasks both functionally correct and at least p times faster than the PyTorch reference); fast_1 and fast_2 are the thresholds most commonly reported, fast_0 reduces to plain correctness"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline applies to a code-generation task like this one. The paper's own
    reference point is the plain PyTorch implementation itself: models are said to match or beat
    it ("fast_1") in fewer than 20% of tasks on average across the seven models tested at release.
dataset:
  size: 270
  size_note: >
    270 problems across four Hugging Face dataset splits, confirmed directly from the
    datasets-server row counts: level_1 100, level_2 100, level_3 50, level_4 20. The original
    February 2025 paper evaluated only the first 250 (levels 1-3); level_4, along with problem-size
    and numerics fixes to levels 1-2, was added in a July 2025 "v0.1" revision, so scores against
    the current dataset are not automatically comparable to the original paper's own reference
    table, which used pre-fix Level 1/2 problems and did not include Level 4 at all. The v0.1
    revision also states that METR's independent quality review removed 43 Level 1-3 tasks it
    flagged as unreliable (near-zero outputs, near-constant results across random seeds, and
    similar issues); this page could not confirm whether those 43 were dropped from the current
    270-row Hugging Face dataset or only from METR's own separate re-evaluation set.
  url: "https://huggingface.co/datasets/ScalingIntelligence/KernelBench"
  license: "MIT (GitHub repository LICENSE file and the Hugging Face dataset listing); the arXiv paper text itself is separately licensed CC BY 4.0."
  languages:
    - en
  modalities:
    - code
  splits: "four splits by difficulty level: level_1 (100), level_2 (100), level_3 (50), level_4 (20); no train/validation split, every problem is available for evaluation"
  public_test_set: true
publisher:
  org: "Stanford University (Scaling Intelligence Lab); Princeton University"
  authors:
    - "Anne Ouyang"
    - "Simon Guo"
    - "Simran Arora"
    - "Alex L. Zhang"
    - "William Hu"
    - "Christopher Ré"
    - "Azalia Mirhoseini"
  url: "https://github.com/ScalingIntelligence/KernelBench"
paper:
  title: "KernelBench: Can LLMs Write Efficient GPU Kernels?"
  arxiv: "2502.10517"
  url: "https://arxiv.org/abs/2502.10517"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/ScalingIntelligence/KernelBench"
released: "2025-02"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 36.0
  as_of: "2025-02"
  note: >
    Not saturated. In the original paper's seven-model evaluation, DeepSeek R1's 36% fast_1 on
    Level 2 was the single highest score recorded, and no model exceeded that on any level; GPT-4o
    scored 0% fast_1 on Level 3, and the best Level 3 result (OpenAI o1) was 12%. The authors state
    models match the plain PyTorch baseline in fewer than 20% of tasks on average, and that the
    benchmark gets harder as the speedup threshold p rises. No updated, dated leaderboard table
    with newer frontier models was found during this research, so a current top score is not
    established here.
contamination:
  risk: medium
  note: >
    The problem set (reference PyTorch code, without published gold kernel solutions) has been
    public since February 2025, about a year and a half by this research date. Since then, outside
    teams have published worked solutions and specialized models trained toward the same or similar
    problems -- Meta's KernelLLM and Sakana AI's "AI CUDA Engineer" among them, per the authors' own
    v0.1 blog post -- which raises the risk that a later model has seen a working answer to a
    specific problem. Risk is not rated high because there is no single canonical "correct" kernel
    to memorize the way there is a single correct multiple-choice letter, and the authors'
    correctness and theoretical-performance-limit checks are explicitly designed to catch
    non-functional or reward-hacked submissions.
harness:
  lm_eval: ""
  inspect_evals: "kernelbench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    UK AISI's inspect_evals package implements KernelBench 0.1 as a single task, defaulting to
    num_correct_trials=5, num_perf_trials=100, an L40S GPU target, fp32 precision, a CUDA backend
    and p=1.0, run inside a Docker sandbox with its own isolated Python environment. The original
    authors' own scripts in ScalingIntelligence/KernelBench remain the reference implementation.
tags:
  - coding
  - gpu-kernels
  - code-generation
  - performance
  - correctness
  - cuda
sources:
  - url: "https://arxiv.org/abs/2502.10517"
    title: "KernelBench: Can LLMs Write Efficient GPU Kernels? (Ouyang et al., arXiv:2502.10517)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.10517"
    title: "KernelBench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/ScalingIntelligence/KernelBench"
    title: "ScalingIntelligence/KernelBench GitHub repository (README, task levels, backends)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ScalingIntelligence/KernelBench/main/LICENSE"
    title: "KernelBench repository LICENSE file (MIT)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ScalingIntelligence/KernelBench"
    title: "ScalingIntelligence/KernelBench dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ScalingIntelligence/KernelBench"
    title: "Hugging Face datasets-server per-split row counts for ScalingIntelligence/KernelBench"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/kernelbench"
    title: "inspect_evals kernelbench task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/kernelbench/kernelbench.py"
    title: "inspect_evals kernelbench task definition (kernelbench.py)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/kernelbench/_defaults.py"
    title: "inspect_evals kernelbench default parameters (_defaults.py)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/kernelbench/README.md"
    title: "inspect_evals kernelbench task README"
    accessed: "2026-09-08"
  - url: "https://scalingintelligence.stanford.edu/blogs/kernelbenchv01/"
    title: "KernelBench v0.1 (Scaling Intelligence Lab blog post: reward hacking, dataset fixes, Level 4)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

KernelBench asks a model to replace a PyTorch reference implementation -- a single operator, a small fused pattern, or a full neural network architecture -- with a custom GPU kernel that computes the same result, faster. Problems are organized into four difficulty levels: Level 1 (100 single-kernel operators such as convolutions, matrix multiplies and normalization layers), Level 2 (100 simple fusion patterns, such as a convolution followed by a bias add and a ReLU, where fusing operations into one kernel should beat running them separately), Level 3 (50 full model architectures such as MobileNet, VGG, MiniGPT and Mamba, requiring end-to-end kernel optimization), and Level 4 (20 Hugging Face model architectures, added in a July 2025 update). The default backend is raw CUDA, but the harness also supports Triton, CUTE, TileLang, ThunderKittens and HIP for AMD GPUs.

The benchmark deliberately grades two different things at once: whether the generated kernel is functionally correct, and whether it is actually faster than the PyTorch baseline. A model that writes a slow-but-correct kernel, or a fast-but-wrong one, fails the combined metric either way.

## How it is scored

Each generated kernel is checked twice: for correctness, by comparing its output against the reference PyTorch operator on `num_correct_trials` (5 by default) sets of randomized inputs, all of which must pass; and for performance, by timing `num_perf_trials` (100 by default) repeated runs with CUDA events and comparing the mean wall-clock time to the reference PyTorch implementation's own timing on the same hardware (an NVIDIA L40S GPU, in both the original paper and the inspect_evals default configuration). The headline metric, `fast_p`, is the fraction of tasks that are both correct and at least p times faster than PyTorch: `fast_1` (correct and at least as fast as PyTorch) and `fast_2` (correct and at least twice as fast) are the two thresholds most commonly reported; `fast_0` reduces to a plain correctness rate, ignoring speed entirely. Because fast_p is defined for any threshold p, a bare "KernelBench score" is ambiguous unless the threshold is stated alongside it.

The authors' own v0.1 revision documents several "reward hacking" patterns models have been caught exploiting -- calling high-level torch/cuBLAS operators instead of writing a real kernel, writing a kernel but never calling it, or exploiting timing and stream-synchronization bugs to record an artificially fast time -- and recommends sanity-checking any unusually high score against a theoretical hardware performance ceiling (compute and memory throughput limits) before trusting it.

## Dataset and licence

The current Hugging Face dataset holds 270 problems across four splits, confirmed directly from the datasets-server row counts: level_1 100, level_2 100, level_3 50, level_4 20. The original paper evaluated only the first 250 (levels 1-3); level_4, along with problem-size and numerics fixes to levels 1 and 2, was added in the July 2025 v0.1 revision, so scores against the current dataset are not automatically comparable to the original paper's reference table. Problems are PyTorch `nn.Module` reference implementations selected by the authors, not scraped or crowdsourced. The GitHub repository and Hugging Face dataset are both MIT-licensed; the arXiv paper text itself carries a separate CC BY 4.0 licence. There is no train/validation split -- every problem is available for evaluation -- and no gold kernel solutions are published, though worked solutions to some of the same problems have since appeared in outside projects.

## Who publishes it

KernelBench was introduced by Anne Ouyang, Simon Guo, Simran Arora, Alex L. Zhang, William Hu, Christopher Ré and Azalia Mirhoseini, from Stanford University's Scaling Intelligence Lab (Alex L. Zhang additionally affiliated with Princeton University), posted to arXiv in February 2025 and later presented at ICML 2025. The Scaling Intelligence Lab continues to maintain the GitHub repository and Hugging Face dataset directly, shipping the v0.1 revision in July 2025; no separate organisation runs a public leaderboard.

## Lineage

KernelBench has no formal predecessor and no successor benchmark supersedes it as of this research. Its authors describe an active ecosystem of follow-on work built around the same problem set: Meta released a fine-tuned model, KernelLLM, aimed specifically at the task; Sakana AI published "The AI CUDA Engineer," an agentic pipeline for the same problems; and METR and NVIDIA both published independent re-evaluations, with METR's quality review leading the authors to remove 43 Level 1-3 tasks it flagged as unreliable in the v0.1 revision. None of these related projects has its own page in this repository yet. UK AISI's inspect_evals package implements KernelBench 0.1 as a single task rather than as a family of per-version ids, and this page follows that choice, treating "kernelbench" as one evolving benchmark.

## Saturation and contamination

KernelBench is not saturated. In the original paper's seven-model evaluation, DeepSeek R1's 36% fast_1 on Level 2 was the single highest score recorded, and no model exceeded that on any level; GPT-4o scored 0% fast_1 on Level 3, and the best Level 3 result, from OpenAI o1, was only 12%. The authors state models match the plain PyTorch baseline in fewer than 20% of tasks on average, and that the benchmark gets harder as the speedup threshold p rises, so real headroom remains on both the correctness and performance axes. No updated, dated leaderboard with newer frontier models was found during this research, so a current top score is not established here.

Contamination risk is assessed as medium. The problem set has been public since February 2025, about a year and a half by this research date, and outside teams have since published worked solutions and specialized models trained toward the same or similar problems, which raises the risk that a later model has seen a working answer to a specific problem. Risk is not rated high because there is no single canonical "correct" kernel to memorize the way there is a single correct multiple-choice letter, and the benchmark's correctness and theoretical-performance-limit checks are explicitly designed to catch non-functional or reward-hacked submissions rather than reward a memorized string.

## How to run it

UK AISI's inspect_evals package implements the benchmark as the `kernelbench` task (`inspect eval inspect_evals/kernelbench`), defaulting to the level_1/level_2/level_3 splits (Level 4 must be requested explicitly), a CUDA backend, fp32 precision, an L40S GPU target, 5 correctness trials, 100 performance trials and p=1.0, run inside a Docker sandbox; it ships its own isolated Python environment because of dependency conflicts with other evals in that repository. The original authors' own scripts in the ScalingIntelligence/KernelBench repository remain the reference implementation and additionally support Triton, CUTE, TileLang, ThunderKittens and HIP backends. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench implementation was found during this research. Because timing depends on the specific GPU, backend and precision used, fast_p scores are only safely compared when the hardware, backend and threshold p all match.

## Reading the numbers

A high KernelBench fast_p score is comparatively strong evidence a model can write GPU code that both works and is fast -- a combination general-purpose coding benchmarks rarely test, since most do not grade runtime performance at all. Because fast_p bundles two different bars (correctness, then a speed threshold) into one number, always check which p and which levels were included: a fast_1 score is a much lower bar than fast_2, and a Level-1-only score says nothing about whole-architecture optimization (Level 3) or Hugging Face model coverage (Level 4). Given the July 2025 dataset revision changed problem sizes and numerics, and inspect_evals follows that revision while the original paper predates it, treat pre- and post-v0.1 scores as measuring a similar but not identical benchmark, and watch for reward-hacked results the authors themselves warn are still possible even after their fixes.
