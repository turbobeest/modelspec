---
id: cyberseceval_4
name: "CyberSecEval 4"
aliases:
  - "CYBERSECEVAL 4"
  - "Purple Llama CyberSecEval 4"
page_kind: benchmark
category: safety
subcategory: "LLM cybersecurity risk and capability suite: adds CrowdStrike-built defensive benchmarks (malware analysis, threat-intelligence reasoning, as CyberSOCEval) and an automated-vulnerability-patching benchmark (AutoPatchBench) to the prior version's risk and insecure-code tests"
status: active
summary: "Meta's fourth CyberSecEval release, adding CrowdStrike-built defensive benchmarks (malware analysis, threat-intel reasoning) and an automated-patching benchmark to the prior risk and insecure-code tests."
measures: >
  CyberSecEval 4 builds on CyberSecEval 3's risk categories and adds three new benchmarks the
  repository documents as its headline additions: two developed with CrowdStrike under the name
  CyberSOCEval -- Malware Analysis (can a model correctly answer multi-answer questions about a piece
  of malware from its detonation report) and Threat Intelligence Reasoning (can a model extract
  correct answers from unstructured threat-intelligence reports, as text or as report images) -- and
  AutoPatchBench, which measures whether an LLM agent can generate a security patch for a real,
  fuzzer-discovered crash in native (C/C++) code that a verification pipeline confirms actually fixes
  the bug. Unlike most of the suite, the CyberSOCEval benchmarks measure a defensive capability that
  is good to have more of, not a risk to minimize -- the first point in the CyberSecEval series where
  a higher score is unambiguously the desirable direction for part of the suite. CyberSecEval 4 also
  carries forward CyberSecEval 3's MITRE compliance, MITRE False Refusal Rate, instruct and
  autocomplete insecure-code tests, and multilingual prompt injection and multi-turn phishing tests,
  largely unchanged.
task_format: >
  Continuing categories (largely unchanged from CyberSecEval 3, confirmed by exact sample counts):
  MITRE compliance (1,000 prompts), MITRE FRR (750 prompts), instruct and autocomplete insecure-code
  tests (1,916 prompts each), multilingual prompt injection (1,004 cases, the same file as CyberSecEval
  3), and multi-turn phishing (a subset of the CyberSecEval 3 challenge set). New: Malware Analysis
  (609 multiple-answer questions built from detonation reports of public malware samples targeting
  Windows-operated businesses, with up to 10 possible correct options per question), Threat
  Intelligence Reasoning (588 question-answer pairs drawn from 45 distinct threat-intelligence
  reports, answerable from report text, report images, or both), and AutoPatchBench (an LLM agent is
  given a fuzzer-discovered crash from 178 bugs across 11 crash types, drawn from the ARVO dataset of
  reproducible open-source vulnerabilities, and must produce a patch that a fuzzing-and-differential-
  testing pipeline verifies actually resolves the crash without breaking the target).
metric:
  name: "per-category rates and scores -- risk/insecurity rates for most inherited categories; multi-answer accuracy plus Jaccard similarity for the new CyberSOCEval tasks; patch-verification success rate for AutoPatchBench"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Direction still varies by category, and CyberSecEval 4 is the first version where that variation
    runs in an explicitly positive direction for part of the suite: Malware Analysis and Threat
    Intelligence Reasoning score a defensive capability where higher is better (an inspect_evals
    reference run on a small subset, not a full-dataset reproduction, put five contemporary frontier
    models at roughly 21%-29% exact-match accuracy on Malware Analysis and 46%-69% on Threat
    Intelligence Reasoning, with Jaccard similarity noticeably higher than exact-match on both,
    showing partial credit matters). AutoPatchBench is also a capability score (higher = more
    verified-correct patches). The inherited MITRE, FRR, prompt-injection and insecure-code categories
    remain risk rates where lower is better, and vulnerability exploitation (still present via the
    inherited categories) again runs opposite that. No single random or human baseline applies
    suite-wide; treat any one number as belonging to a single named category.
dataset:
  size_note: >
    Combines CyberSecEval 3's largely unchanged sets (1,000 MITRE, 750 MITRE FRR, 1,916 instruct,
    1,916 autocomplete, 1,004 multilingual prompt injection -- all confirmed by exact sample counts in
    the inspect_evals reference implementation) with new material: 609 Malware Analysis question-
    answer pairs and 588 Threat Intelligence Reasoning question-answer pairs (both figures confirmed
    directly from the CyberSOCEval paper's own dataset-construction section), and 178 AutoPatchBench
    bugs across 11 fuzzer-discovered crash types, drawn from the larger ARVO dataset (which the
    AutoPatchBench announcement describes as over 5,000 reproducible vulnerabilities across 250+
    projects) but not itself a fixed-size prompt file in the same sense as the other categories.
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
  license: ""
  languages:
    - en
  modalities:
    - text
    - code
    - image
  splits: "no train/test split; each inherited category is a single fixed evaluation set; Malware Analysis and Threat Intelligence Reasoning are each a single fixed set; AutoPatchBench draws from a fixed set of 178 bugs"
  public_test_set: true
publisher:
  org: "Meta (the Purple Llama project), with CyberSOCEval developed in partnership with CrowdStrike"
  authors: []
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
released: "2025-04"
last_updated: ""
lineage:
  family: ""
  predecessor: cyberseceval_3
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2026-04"
  note: >
    No full-dataset, cross-model reproduction of CyberSecEval 4 as a whole was found for this page.
    The closest available evidence is inspect_evals' own implementation-validation report (dated
    2026-04-11, on a small deterministic subset with newer frontier models than the original release,
    explicitly not a comparison to the original paper): scores there are well short of ceiling on most
    tasks (for example 21%-29% accuracy on Malware Analysis, 9%-22% on multilingual prompt injection
    success), indicating the suite is not saturated, though this evidence is thin and non-canonical
    enough that "open" is a description of what was observed rather than a confident claim about the
    full suite.
contamination:
  risk: medium
  note: >
    The inherited MITRE, FRR, insecure-code and multilingual-prompt-injection sets are the same
    public, MIT-licensed files carried from earlier CyberSecEval versions, now over a year old at this
    research date. The CyberSOCEval malware and threat-intelligence data is distributed differently --
    inspect_evals describes fetching it from a pinned CrowdStrike snapshot and pinned web.archive.org
    report-PDF captures verified by checksum, rather than a plain public GitHub file -- which may
    narrow exposure somewhat but was not established either way for this page. AutoPatchBench draws
    from ARVO, an existing public OSS-Fuzz-derived vulnerability corpus assembled before CyberSecEval
    4, so its individual bugs and patches may already be circulating in other training data.
harness:
  lm_eval: ""
  inspect_evals: "cyse4_mitre, cyse4_mitre_frr, cyse4_instruct, cyse4_autocomplete, cyse4_multilingual_prompt_injection, cyse4_multiturn_phishing, cyse4_malware_analysis, cyse4_threat_intelligence (inspect_evals/cyberseceval_4; the AutoPatchBench-derived cyse4_autopatching task and the cyse4_autonomous_uplift prototype exist in the source tree but are intentionally excluded from the public/supported task list, so the harness that carries this id does not currently run AutoPatchBench, one of the version's three headline additions)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Malware Analysis and Threat Intelligence Reasoning are also documented as their own open-source suite, CyberSOCEval (arXiv 2509.20166), separate from the PurpleLlama runner."
tags:
  - safety
  - security
  - cybersecurity
  - meta
  - llama
  - purple-llama
  - crowdstrike
  - malware-analysis
  - threat-intelligence
  - automated-patching
sources:
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/README.md"
    title: "PurpleLlama CybersecurityBenchmarks README (introduces CyberSecEval 4, its 9 benchmark types)"
    accessed: "2026-09-08"
  - url: "https://github.com/meta-llama/PurpleLlama/commit/cd9fe65792343c285730c967f888a7373d7e6c17"
    title: "PurpleLlama commit: \"New Release of Llama Guard 4, LlamaFirewall, Llama Prompt Guard 2, CyberSecEval 4, and Sensitive Doc Classification\" (2025-04-29, dates the release)"
    accessed: "2026-09-08"
  - url: "https://meta-llama.github.io/PurpleLlama/CyberSecEval/"
    title: "CyberSecEval 4 documentation landing page (names AutoPatchBench and Prompt Guard)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2509.20166"
    title: "CyberSOCEval: Benchmarking LLMs Capabilities for Malware Analysis and Threat Intelligence Reasoning (states it is part of CyberSecEval 4; 609 and 588 dataset sizes)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2509.20166"
    title: "CyberSOCEval, full text (ar5iv) -- dataset construction, 609/588 counts, CrowdStrike partnership"
    accessed: "2026-09-08"
  - url: "https://engineering.fb.com/2025/04/29/ai-research/autopatchbench-benchmark-ai-powered-security-fixes/"
    title: "Introducing AutoPatchBench: A Benchmark for AI-Powered Security Fixes (Meta Engineering blog, 2025-04-29; 178 bugs, 11 crash types, ARVO dataset)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cyberseceval_4"
    title: "inspect_evals cyberseceval_4 task README (8 public tasks, omitted autopatching/uplift, sample counts, reference report)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CyberSecEval 4 builds on CyberSecEval 3's risk categories -- MITRE compliance, false refusal, insecure code generation, and multilingual prompt injection and phishing tests, all continued with largely the same prompt sets -- and adds three new benchmarks the project documents as its headline contributions. Two, developed with CrowdStrike under the name CyberSOCEval, measure defensive rather than offensive capability: Malware Analysis asks whether a model can correctly answer multi-answer questions about a piece of malware from its detonation report, and Threat Intelligence Reasoning asks whether a model can extract correct answers from unstructured threat-intelligence reports, given as text, images, or both. The third, AutoPatchBench, measures whether an LLM agent can generate a security patch for a real, fuzzer-discovered crash in native C/C++ code and have a verification pipeline confirm the patch actually fixes the bug. CyberSecEval 4 is the first version in the series where part of the suite explicitly rewards more capability rather than less: a higher CyberSOCEval or AutoPatchBench score reflects a stronger defender or patcher, not a riskier model.

## How it is scored

Inherited categories keep their earlier scoring: LLM-judged compliance and injection-success rates, and an automated insecure-code detector for the coding tests. Malware Analysis and Threat Intelligence Reasoning are scored with exact-match accuracy on multi-answer multiple-choice questions plus Jaccard similarity between the model's selected options and the correct set, so a model that gets some but not all correct options still earns partial credit. AutoPatchBench scores automatically: a candidate patch passes only if it compiles, the original crash no longer reproduces under fuzzing, and differential testing shows the fix does not change the program's intended behavior elsewhere.

## Dataset and licence

Inherited categories are the same MIT-licensed files used in CyberSecEval 3 (1,000 MITRE, 750 MITRE FRR, 1,916 instruct, 1,916 autocomplete, 1,004 multilingual prompt-injection prompts, all confirmed by exact counts in the inspect_evals reference implementation). Malware Analysis (609 question-answer pairs) and Threat Intelligence Reasoning (588 pairs from 45 distinct reports) are confirmed from the CyberSOCEval paper's own dataset-construction section; their underlying report data is distributed through a pinned CrowdStrike snapshot and checksummed web-archive captures rather than a plain public repository file, and this page could not establish a single licence covering that material, so the licence field is left blank rather than assumed. AutoPatchBench draws 178 bugs across 11 crash types from ARVO, a public corpus the project describes as over 5,000 reproducible OSS-Fuzz-derived vulnerabilities across more than 250 projects.

## Who publishes it

CyberSecEval 4 is a Meta (Purple Llama project) release; unlike the first three versions, this page found no dedicated arXiv paper for CyberSecEval 4 itself. It was released on GitHub on 29 April 2025 alongside Llama Guard 4, LlamaFirewall, Llama Prompt Guard 2 and a sensitive-document classifier, confirmed from the PurpleLlama repository's own commit history. Its CyberSOCEval component has its own separate paper (arXiv 2509.20166, September 2025, led by Lauren Deason with Meta and CrowdStrike co-authors); AutoPatchBench is documented through a Meta Engineering blog post from the same release date rather than a paper. Because authorship is split across these sources rather than unified in one publication, this page leaves the front matter's `paper` and `publisher.authors` fields empty.

## Lineage

CyberSecEval 4 is the fourth entry in Meta's CyberSecEval series, following `cyberseceval_3`, whose multilingual prompt-injection dataset it reuses unchanged (the same 1,004-case file backs both versions' tasks). As of this research date, no fifth version was found; the PurpleLlama repository's own README states that, as of June 2025, "our team is exploring options for the next version of our project, which may result in significant changes to our current benchmarking infrastructure and all benchmark source code," so no successor id is recorded. This benchmark is unrelated to `cve_bench` (live exploitation of specific real CVEs) and `wmdp` (a multiple-choice hazardous-knowledge proxy), both catalogued separately here; AutoPatchBench itself does not yet have a separate page in this repository.

## Saturation and contamination

No full-suite, cross-model reproduction of CyberSecEval 4 was found; the best available evidence is inspect_evals' own small-subset implementation-validation report (2026-04-11), which the harness's own documentation explicitly says is not a reproduction of the original paper's results. On that subset, scores for contemporary frontier models were well short of ceiling on most tasks, so this page records saturation as open rather than reached, while flagging that the evidence is thin. Contamination risk is medium: the inherited public prompt sets are now over a year old, the CyberSOCEval report data is distributed through pinned, checksummed snapshots rather than a plain public file (which may narrow but does not eliminate exposure), and AutoPatchBench's underlying ARVO bugs are drawn from an existing public vulnerability corpus that could already appear in other training data.

## How to run it

inspect_evals implements 8 of CyberSecEval 4's task entry points -- MITRE, MITRE FRR, instruct, autocomplete, multilingual prompt injection, multi-turn phishing, Malware Analysis and Threat Intelligence Reasoning -- but intentionally excludes `cyse4_autopatching` and a `cyse4_autonomous_uplift` prototype from its supported public suite, stating the current prototypes simulate command feedback or lack a real build/test/validate loop rather than running against a grounded target. That means the harness carrying this id does not currently run AutoPatchBench at all, despite it being one of the version's three headline additions; running AutoPatchBench requires the separate reference materials Meta published alongside the ARVO dataset. `cyse4_malware_analysis` and `cyse4_threat_intelligence` additionally require locally available CyberSOCEval report data, and the image-based Threat Intelligence mode needs `pdf2image`, `pypdf` and a system Poppler installation.

## Reading the numbers

A CyberSecEval 4 number is only meaningful per named category, and direction is not uniform: most inherited categories are risk rates where lower is better, but Malware Analysis, Threat Intelligence Reasoning and AutoPatchBench are capability scores where higher is better, since they measure defensive and remediation skill rather than a harm to suppress. A strong CyberSOCEval score reflects performance on synthetic interview-style questions over specific detonation reports and threat-intel documents, not general SOC-analyst competence. Because the currently supported harness omits AutoPatchBench entirely, any inspect_evals-reported `cyberseceval_4` result should be read as covering the other 8 tasks only, not the automated-patching benchmark the version is named for in Meta's own announcement.
