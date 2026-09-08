---
id: harm_bench
name: "HarmBench"
aliases: []
page_kind: benchmark
category: safety
subcategory: "standardized automated red-teaming framework: attack success rate across 510 harmful behaviors"
status: active
summary: "A standardized red-teaming framework of 510 curated harmful behaviors testing whether attacks make a model comply; the metric is Attack Success Rate, so a lower score is the safety-desirable outcome."
measures: >
  HarmBench is a standardized evaluation framework for automated red teaming: it lets red-teaming
  attack methods and target-model defenses be compared on equal footing, rather than each paper
  reporting numbers under its own ad hoc protocol. Its core artifact is 510 curated harmful behaviors
  -- 400 textual, 110 multimodal, confirmed by counting the released CSV files directly -- split across
  four functional categories (standard, contextual, copyright, multimodal) and semantic categories
  describing the kind of harm (cybercrime/intrusion, general illegal activity, misinformation and
  disinformation, chemical/biological, harassment/bullying, plus copyright and a residual "harmful"
  bucket). The original paper used HarmBench to run a large-scale comparison of 18 red-teaming attack
  methods (including several variants of Greedy Coordinate Gradient, GCG) against 33 target LLMs and
  defenses, and separately introduced an adversarial-training defense (RMU-adjacent but distinct;
  called R2D2) built and validated using the same framework.
task_format: >
  A red-teaming method generates a test case for each behavior (an adversarial suffix, a jailbreak
  prompt, or, for the simplest baseline, the behavior stated directly); the target model generates a
  response, standardized to up to 512 generated tokens since the paper found generation length can
  swing substring-matching ASR by up to 30 percentage points; a classifier then judges whether the
  response actually exhibits the behavior. For non-copyright behaviors this is a fine-tuned Llama 2 13B
  classifier (`cais/HarmBench-Llama-2-13b-cls`), trained and validated on separate splits so the
  classifier's own accuracy is not inflated by testing on its training data; copyright behaviors are
  instead checked by a text-overlap detector rather than the classifier. HarmBench publishes an
  official validation/test split of 100/410 behaviors across the combined textual-plus-multimodal set;
  the text-only files are separately split 80 validation / 320 test.
metric:
  name: "Attack Success Rate (ASR): share of behaviors an attack successfully elicits, per classifier judgment"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    ASR rises with how effective the attack and how vulnerable the target model are, so a lower ASR
    under a fixed, strong attack is the safety-desirable reading; a higher ASR describes a more
    effective attack, not a more capable or more useful model. No random or human baseline applies,
    since a "random" adversarial suffix and a human's own attempt to jailbreak a model are not
    comparable reference points the paper defines. Reporters are not consistent in framing: this
    repository's own reading of HELM's `harm_bench` scenario shows it reports a `safety_score` on a
    0-1 scale computed by an independent LLM judge (1 = the model fully refused, 0.5 = complied
    without an explicit refusal, 0 = the model complied) -- the mathematical near-complement of ASR,
    scaled 0-1 rather than 0-100, and produced by a different grading method (an LLM-judge prompt,
    not the paper's own fine-tuned classifier) than the original paper uses.
dataset:
  size: 510
  size_note: >
    510 total unique behaviors: 400 textual (200 standard, 100 contextual, 100 copyright, counted
    directly from harmbench_behaviors_text_all.csv) plus 110 multimodal (counted directly from
    harmbench_behaviors_multimodal_all.csv). The official validation/test split across the combined
    set is 100/410 behaviors, per the paper's own text; the separately released text-only files split
    80 validation (harmbench_behaviors_text_val.csv) / 320 test (harmbench_behaviors_text_test.csv),
    counted directly rather than assumed -- no separately released multimodal val/test file was found
    for this page, so that half of the paper's 100/410 figure could not be independently verified file
    by file.
  url: "https://github.com/centerforaisafety/HarmBench"
  license: "MIT, confirmed from the repository's own LICENSE file"
  languages: [en]
  modalities: [text, image]
  splits: "combined val/test 100/410 (paper); text-only files val 80 / test 320 (counted directly); no separate multimodal val/test file found"
  public_test_set: true
publisher:
  org: "Center for AI Safety (CAIS), with University of Illinois Urbana-Champaign, UC Berkeley, Carnegie Mellon University and Microsoft (confirmed from the paper's own author affiliation footnotes)"
  authors:
    - "Mantas Mazeika"
    - "Long Phan"
    - "Xuwang Yin"
    - "Andy Zou"
    - "Zifan Wang"
    - "Norman Mu"
    - "Elham Sakhaee"
    - "Nathaniel Li"
    - "Steven Basart"
    - "Bo Li"
    - "David Forsyth"
    - "Dan Hendrycks"
  url: "https://www.harmbench.org"
paper:
  title: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"
  arxiv: "2402.04249"
  url: "https://arxiv.org/abs/2402.04249"
  year: 2024
leaderboard_url: "https://www.harmbench.org/results"
repo_url: "https://github.com/centerforaisafety/HarmBench"
released: "2024-02"
last_updated: "2024-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - harm_bench_gcg_transfer
saturation:
  status: open
  top_score: null
  as_of: "2024-02"
  note: >
    "Top score" is not a single well-defined idea here given the inverted-desirability metric, so this
    page leaves it unset rather than pick one reading, matching how this wiki's wmdp page handles the
    same ambiguity. The paper's own Table 6 (ASR on all behaviors, by model and attack) shows very wide
    spreads: under the transfer-only GCG-T attack, ASR on Llama 2 7B Chat is 1.8% versus 19.8% on
    Vicuna 7B in the same table; under the strongest attacks (AutoDAN, PAIR, TAP), several models
    exceed 60% ASR. That spread, both across models under one attack and across attacks against one
    model, reads as real, unsaturated separation rather than ceiling clustering, though no 2025-2026
    frontier-model figures were found for this page under the paper's own classifier-based scoring.
contamination:
  risk: medium
  note: >
    The full 510-behavior set has been public and unchanged on GitHub under an MIT licence since
    February 2024, so the literal behavior strings are plausibly present in newer pretraining and
    safety-tuning data. Contamination reads differently here than on an answer-matched benchmark,
    though: there is no fixed "correct answer" to memorize, so exposure mainly matters if a developer
    safety-tunes specifically against these known behaviors or against leaked, previously
    attack-optimized suffixes -- which would lower ASR on HarmBench specifically without necessarily
    improving robustness to novel, unseen attacks. The authors' own classifier was trained on a
    manually labeled validation set with separate validation and test classifier checkpoints,
    specifically to keep the grading tool itself from being contaminated by the behaviors it scores.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "harm_bench (direct-request template only; see How to run it)"
  opencompass: ""
  bigbench: ""
  other: >
    Reference pipeline (test-case generation, completion generation, classifier-based evaluation)
    ships in centerforaisafety/HarmBench. No lm-evaluation-harness, OpenCompass or inspect_evals
    implementation was found (each checked directly at its likely path).
tags:
  - safety
  - red-teaming
  - jailbreak
  - attack-success-rate
  - adversarial-robustness
  - classifier-graded
  - multimodal
sources:
  - url: "https://arxiv.org/abs/2402.04249"
    title: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.04249"
    title: "HarmBench, full text (ar5iv) -- affiliations, behavior taxonomy, classifier design, val/test split, Table 6 results"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/README.md"
    title: "centerforaisafety/HarmBench GitHub README (classifiers, quick start, news)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/LICENSE"
    title: "centerforaisafety/HarmBench LICENSE file (MIT)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/behavior_datasets/harmbench_behaviors_text_all.csv"
    title: "harmbench_behaviors_text_all.csv (400 rows, counted directly with a CSV parser)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/behavior_datasets/harmbench_behaviors_text_val.csv"
    title: "harmbench_behaviors_text_val.csv (80 rows, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/behavior_datasets/harmbench_behaviors_text_test.csv"
    title: "harmbench_behaviors_text_test.csv (320 rows, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/centerforaisafety/HarmBench/main/data/behavior_datasets/harmbench_behaviors_multimodal_all.csv"
    title: "harmbench_behaviors_multimodal_all.csv (110 rows, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/harm_bench_scenario.py"
    title: "HELM harm_bench_scenario.py (direct-request template, safety_score metric)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/harm_bench_annotator.py"
    title: "HELM harm_bench_annotator.py (LLM-judge grading prompt, 0/0.5/1 scale)"
    accessed: "2026-09-08"
  - url: "https://www.harmbench.org/results"
    title: "harmbench.org results page (baseline charts; fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HarmBench is a standardized evaluation framework for automated red teaming: its purpose is letting
red-teaming attack methods and target-model defenses be compared on equal footing, rather than each
paper reporting numbers under its own ad hoc protocol. Its core artifact is 510 curated harmful
behaviors -- 400 textual and 110 multimodal, confirmed by counting the released files directly -- split
across four functional categories (standard, contextual, copyright, multimodal) and semantic categories
describing the kind of harm (cybercrime and intrusion, general illegal activity, misinformation and
disinformation, chemical and biological, harassment and bullying, plus copyright and a residual
"harmful" bucket). The introducing paper used HarmBench to run a large-scale comparison of 18
red-teaming attack methods, including several variants of Greedy Coordinate Gradient (GCG), against 33
target LLMs and defenses, and separately introduced its own adversarial-training defense validated
using the same framework.

## How it is scored

A red-teaming method generates a test case for each behavior -- an adversarial suffix, a jailbreak
prompt, or, for the simplest baseline (direct request), the behavior stated with no disguise at all.
The target model generates a response, standardized to up to 512 generated tokens, since the paper
found that generation length alone can swing substring-matching attack success rate (ASR) by up to 30
percentage points if left uncontrolled. A classifier then judges whether the response actually
exhibits the behavior: for non-copyright behaviors this is a fine-tuned Llama 2 13B classifier
(`cais/HarmBench-Llama-2-13b-cls`), trained and validated on separate splits so its own reported
accuracy is not inflated by evaluating on its own training data; copyright behaviors use a text-overlap
detector instead. HarmBench publishes an official validation/test split of 100/410 behaviors across
the combined set.

## Dataset and licence

510 total unique behaviors: 400 textual (200 standard, 100 contextual, 100 copyright) and 110
multimodal, both counts confirmed directly from the released CSV files rather than taken from the
paper's prose alone. The text-only files split 80 validation / 320 test, also counted directly; the
paper's combined 100/410 split implies a further 20/90 multimodal split that this page could not find
as a separately released file. The repository is MIT-licensed, and behaviors were deliberately written
to avoid operationally dangerous detail even though the set is fully public.

## Who publishes it

HarmBench comes from Mantas Mazeika, Long Phan, Xuwang Yin, Andy Zou, Zifan Wang, Norman Mu, Elham
Sakhaee, Nathaniel Li, Steven Basart, Bo Li, David Forsyth and Dan Hendrycks, posted to arXiv in
February 2024. Authors are affiliated with the Center for AI Safety (CAIS), the University of Illinois
Urbana-Champaign, UC Berkeley, Carnegie Mellon University and Microsoft. The project is maintained at
centerforaisafety/HarmBench on GitHub and at harmbench.org.

## Lineage

HarmBench positions itself against a set of smaller, less diverse prior red-teaming behavior sets it
directly compares itself to in its own Table 5, including AdvBench (58 behaviors, from the same GCG
paper, Zou et al. 2023, arXiv 2307.15043), TDC 2023 (99 behaviors) and MaliciousInstruct (100
behaviors) -- none of which are separately catalogued in this repository. Its own variant,
[harm_bench_gcg_transfer](harm_bench_gcg_transfer.md), applies suffixes from the transfer version of
GCG to the same behavior set rather than introducing new behaviors. HarmBench is the safety-red-teaming
counterpart to over-refusal calibration benchmarks like [XSTest](xstest.md): the two test opposite
failure modes (a model complying with genuinely unsafe requests versus refusing genuinely safe ones),
and are best read together rather than in isolation. It is distinct from [WMDP](wmdp.md), a
multiple-choice hazardous-knowledge proxy rather than a red-teaming attack framework, and from
[CyberSecEval 2](cyberseceval_2.md), which is scoped specifically to cybersecurity risk and code
security rather than HarmBench's broader harm taxonomy.

## Saturation and contamination

Whether HarmBench looks saturated depends entirely on which attack is used against which model, which
this page reads as evidence of real, open separation rather than picking a single top score. The
paper's own Table 6 shows very wide spreads: under the transfer-only GCG-T attack, ASR on Llama 2 7B
Chat is 1.8% versus 19.8% on Vicuna 7B; under stronger, per-target-optimized attacks such as AutoDAN,
PAIR and TAP, several models exceed 60% ASR. No 2025-2026 frontier-model figures under the paper's own
classifier-based scoring were found for this page; the project's own results page presents only
February-2024 baseline charts as static images with no newer entries. Contamination risk is medium and
reads differently here than on an answer-matched benchmark: there is no single correct answer to
memorize, so exposure mainly matters if a developer safety-tunes specifically against these known
behaviors or against previously published, attack-optimized suffixes, which would lower ASR on
HarmBench specifically without necessarily improving robustness to novel attacks the benchmark does not
cover.

## How to run it

The authors' own repository ships the full pipeline: test-case generation, completion generation, and
classifier-based evaluation, plus the three released classifier checkpoints. HELM implements a `harm_bench`
scenario, but only using HarmBench's simplest "direct request" template -- the plain behavior text with
no attack applied -- rather than running any of the paper's 18 red-teaming methods; it also scores with
its own LLM-judge prompt (`safety_score`, 0-1, judged by an independent model) rather than the paper's
fine-tuned classifier. No lm-evaluation-harness, OpenCompass or inspect_evals implementation was found.
Because "HarmBench" can mean the full 18-method academic comparison or a single reporter's choice of one
attack (or none) and one judge, always check which attack, which classifier and which behavior subset a
reported number used before comparing it to another.

## Reading the numbers

A low HarmBench ASR under a fixed, strong attack is the safety-desirable reading: it shows a model
resists that specific attack across a broad, diverse set of harmful behaviors. It is not evidence of
general safety, since ASR under a weak or absent attack (such as HELM's direct-request-only
implementation) mainly measures whether a model refuses a plainly stated harmful request, a much lower
bar than resisting an optimized jailbreak. Because ASR depends heavily on which attack, which judge and
which behavior subset were used, never compare two HarmBench numbers without confirming all three
match; a model that looks robust under GCG-Transfer may still be highly vulnerable under a stronger,
per-target attack like AutoDAN or PAIR, and the paper's own results show exactly that gap for several
models.
