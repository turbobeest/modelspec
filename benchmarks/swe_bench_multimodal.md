---
id: swe_bench_multimodal
name: SWE-bench Multimodal
aliases: ["SWE-bench M", "SWE-bench MM"]
page_kind: benchmark
category: coding
subcategory: "GitHub issue resolution / patch generation with visual inputs"
status: active
summary: "SWE-bench Multimodal tests GitHub-issue patching on JavaScript/TypeScript repositories where the issue includes an image, such as a bug screenshot or design mockup."
measures: >
  SWE-bench Multimodal measures the same underlying skill as SWE-bench — resolving a real GitHub issue
  with a patch a project's own tests accept — but restricted to issues that include a visual element: a
  screenshot of a bug, a design mockup or wireframe, a diagram of the desired behaviour, or an error
  message with visual context. Repositories are JavaScript/TypeScript projects for web interface design,
  diagramming, data visualisation, syntax highlighting and interactive mapping, so a model must read and
  act on both text and images to succeed, not just text.
task_format: >
  Given an issue description that includes at least one image, plus repository access, the system outputs
  a patch. The patch is applied inside a container and graded against FAIL_TO_PASS and PASS_TO_PASS tests
  recovered from the pull request that originally fixed the issue, the same protocol as the rest of the
  SWE-bench family.
metric:
  name: "% resolved (FAIL_TO_PASS and PASS_TO_PASS tests both pass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline published. At the original 2024 release, SWE-agent resolved 12% of task instances, the best of the systems tested; the next-best system reached 6%."
dataset:
  size: 480
  size_note: >
    The original 2024 release held 517 task instances containing at least one image in the issue text or
    its tests, drawn from JavaScript/TypeScript repositories. A "v2" refresh released 2026-09-01 retains
    480 of those instances chosen for reproducible evaluation, dropping ones with flaky or ungradeable
    tests, rebuilding the Docker environments to fix dependency and browser drift, and hardening
    JavaScript grading and visual test-asset handling.
  url: "https://huggingface.co/datasets/SWE-bench/SWE-bench_Multimodal"
  license: "CC BY 4.0"
  languages: [JavaScript, TypeScript]
  modalities: [code, text, image]
  splits: "single test split; 517 instances at original release, 480 in the v2 refresh"
  public_test_set: true
publisher:
  org: "Originally Princeton NLP / Stanford, with the SWE-bench team; maintained today by the SWE-bench Team at swebench.com"
  authors: ["John Yang", "Carlos E. Jimenez", "Alex L. Zhang", "Kilian Lieret", "Joyce Yang", "Xindi Wu", "Ori Press", "Niklas Muennighoff", "Gabriel Synnaeve", "Karthik R. Narasimhan", "Diyi Yang", "Sida I. Wang", "Ofir Press"]
  url: "https://www.swebench.com/multimodal.html"
paper:
  title: "SWE-bench Multimodal: Do AI Systems Generalize to Visual Software Domains?"
  arxiv: "2410.03859"
  url: "https://arxiv.org/abs/2410.03859"
  year: 2024
leaderboard_url: "https://www.swebench.com/multimodal.html"
repo_url: "https://github.com/SWE-bench/SWE-bench"
released: "2024-10"
last_updated: "2026-09"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    At the original October 2024 release, the best system tested (SWE-agent) resolved 12% of instances,
    with the next-best system at 6% — far from any ceiling, but that figure is now nearly two years old
    and describes the superseded 517-instance set. The v2 refresh (480 instances) went live 2026-09-01,
    one week before this page was researched; no post-refresh leaderboard or top score could be confirmed
    in this research pass, so current standing is not established.
contamination:
  risk: high
  note: >
    Same structural risk as the rest of the family: every instance is a real, publicly merged pull
    request, so a model trained after an instance's fix date may have seen it. Visual assets (screenshots,
    mockups) add a second, less-studied exposure path distinct from the family's usual text-only concern.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Uses the SWE-bench Docker evaluation harness and `swebench` CLI, extended for image-bearing issues and
    JavaScript/TypeScript test grading. Not confirmed in the lm-evaluation-harness, HELM, OpenCompass or
    BIG-bench task lists.
tags: [coding, multimodal, agentic, github-issues, patch-generation, docker, javascript]
sources:
  - url: "https://arxiv.org/abs/2410.03859"
    title: "SWE-bench Multimodal: Do AI Systems Generalize to Visual Software Domains?"
    accessed: "2026-09-08"
  - url: "https://www.swebench.com/multimodal.html"
    title: "SWE-bench Multimodal overview"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-bench Multimodal asks whether a model's ability to resolve real GitHub issues, as measured by
SWE-bench, holds up when the issue itself is partly visual. Every task instance's problem statement or
tests include at least one image — a screenshot of a bug, a design mockup or wireframe, a diagram of
intended behaviour, or an error message shown in context — drawn from JavaScript/TypeScript repositories
covering web interface design, diagramming, data visualisation, syntax highlighting and interactive
mapping. A model must read and act on both the text and the image to produce a patch, not just the text.

## How it is scored

Scoring follows the rest of the SWE-bench family exactly: a candidate patch is applied inside a container
and must make the instance's FAIL_TO_PASS tests pass while leaving its PASS_TO_PASS tests passing, with no
partial credit for a partially correct fix. What differs is the input and the target codebase, not the
grading mechanics.

## Dataset and licence

Released under CC BY 4.0, hosted on Hugging Face. The original October 2024 release held 517 task
instances containing at least one image, mined from JavaScript/TypeScript projects using SWE-bench's usual
GitHub issue/PR collection pipeline. A "v2" refresh, dated 2026-09-01 on the project's own page, narrows
this to 480 instances chosen for reproducible evaluation: instances with flaky or ungradeable tests were
dropped, Docker environments were rebuilt to address dependency and browser drift, and JavaScript grading
and visual test-asset handling were made more robust.

## Who publishes it

SWE-bench Multimodal comes from John Yang and Carlos E. Jimenez with Alex L. Zhang, Kilian Lieret, Joyce
Yang, Xindi Wu, Ori Press, Niklas Muennighoff, Gabriel Synnaeve, Karthik Narasimhan, Diyi Yang, Sida Wang
and Ofir Press, submitted to arXiv in October 2024 and accepted to ICLR 2025. It is maintained today
alongside the rest of the family on swebench.com, which issued the v2 dataset refresh in September 2026.

## Lineage

Multimodal is a sibling extension of the base SWE-bench (`swe_bench`) methodology, applying the same
collection and grading approach to a visual, JavaScript/TypeScript task set rather than to Python. It sits
alongside SWE-bench Verified (`swe_bench_verified`), SWE-bench Multilingual (`swe_bench_multilingual`) and
SWE-bench Pro as siblings rather than descendants of one another; no successor to Multimodal itself was
found.

## Saturation and contamination

At the original release, the best system tested (SWE-agent) resolved only 12% of instances, with the
next-best system at 6% — a wide-open benchmark at the time, but that figure is now nearly two years old
and describes the superseded 517-instance set rather than the current 480-instance v2. Because v2 went
live only a week before this page was researched, no post-refresh leaderboard or current top score could
be confirmed here; saturation is accordingly unknown rather than assumed low. Contamination risk is high
for the usual structural reason (every instance is a real, dated, merged pull request), with the added and
less-studied wrinkle that a training corpus could also have absorbed the screenshots and mockups
themselves.

## How to run it

Multimodal runs on the SWE-bench Docker evaluation harness and `swebench` CLI, extended to serve
image-bearing issues and to grade JavaScript/TypeScript test output. It was not found in the
lm-evaluation-harness, HELM, OpenCompass or BIG-bench task lists. Because the harness must additionally
hand a model any embedded images, comparing scores across publishers also means checking whether the
system under test actually has vision input at all, not just whether it has repository and shell access.

## Reading the numbers

A high Multimodal score would show a system can act on visual information embedded in a real software
task, not only read it — a capability plain-text SWE-bench cannot probe at all. Given how low the only
published baseline is (12%) and how recent the v2 refresh is, a reader should treat any current Multimodal
number as preliminary and check whether it was run against the original 517-instance set or the September
2026 480-instance v2, since the two are not the same benchmark despite the shared name.
