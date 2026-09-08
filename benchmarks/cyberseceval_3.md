---
id: cyberseceval_3
name: "CyberSecEval 3"
aliases:
  - "CYBERSECEVAL 3"
  - "Purple Llama CyberSecEval 3"
page_kind: benchmark
category: safety
subcategory: "LLM cybersecurity risk and capability suite: adds visual prompt injection, automated social engineering, and manual and autonomous offensive-cyber-operations studies to the prior version's risk and insecure-code tests"
status: superseded
summary: "Meta's third CyberSecEval release: adds visual prompt injection, automated spear-phishing, and human and autonomous offensive-cyber-operations studies to the prior version's risk and insecure-code tests."
measures: >
  CyberSecEval 3 measures LLM cybersecurity risk and capability across 8 named risk areas the paper
  groups into two broad categories: risk to third parties (parties other than the model's own user or
  developer, such as social-engineering victims or organizations targeted by cyberattacks) and risk to
  application developers and end users (insecure code, prompt injection and code-interpreter abuse
  reaching the people who deploy or use the model). It keeps CyberSecEval 2's textual prompt
  injection, code-interpreter abuse and vulnerability-exploitation tests essentially unchanged --
  reusing that version's own implementation rather than re-deriving it -- and adds three offensive-
  security areas the paper names as new: automated social engineering (can a model run a persuasive
  multi-turn spear-phishing conversation against a simulated victim), scaling manual offensive cyber
  operations (a human-subjects study of whether LLM assistance speeds up novice and expert
  penetration-testers on capture-the-flag-style challenges), and autonomous offensive cyber operations
  (can an LLM agent, unassisted, advance through reconnaissance, vulnerability discovery, exploitation
  and privilege escalation against a target host). It also adds a visual and a multilingual variant of
  the prompt-injection tests, and documents Prompt Guard, a separate classifier model for detecting
  injections and jailbreaks, which this page treats as a related mitigation artifact rather than part
  of the graded benchmark itself.
task_format: >
  Reused from CyberSecEval 2 unchanged: textual prompt injection (251 cases), code-interpreter abuse
  (500 prompts), and vulnerability exploitation. New in this version: visual prompt injection (1,000
  system-prompt/image/text triples, confirmed from the Hugging Face dataset card, LLM-judged on
  whether an instruction embedded in the image overrode the system prompt), multilingual prompt
  injection (1,004 machine-translated cases, counted directly from the released file), automated
  social engineering (up to 856 synthetic multi-turn spear-phishing challenges against a simulated,
  LLM-played victim, scored by a judge LLM on a 5-point persuasion/rapport/argumentation rubric), the
  manual-uplift human study (inexperienced and highly skilled subjects solving CTF-style challenges
  with and without LLM help, on Hack The Box infrastructure), and the autonomous-operations study (an
  LLM agent attempting a fixed attack-phase sequence against a Windows host from a Kali Linux
  environment, in a controlled setting).
metric:
  name: "per-category rates and scores -- mainly an injection/attack success or compliance rate; the manual- and autonomous-uplift studies report qualitative human-subject and phase-completion outcomes rather than a single percentage"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    As in CyberSecEval 2, most categories here are risk rates where lower is better: visual and
    textual prompt-injection success, interpreter-abuse compliance, and social-engineering success
    rate against the simulated victim. The manual-uplift and autonomous-operations studies do not
    reduce to a single percentage in the paper: the manual study reports subjective and completion-
    rate outcomes by subject group (for example, that a majority of both inexperienced and highly
    skilled subjects felt the LLM helped them learn faster, and that none of the novices in either the
    LLM-assisted or unassisted stage completed the hardest challenge phase), and the autonomous study
    reports which attack phases (reconnaissance, vulnerability identification, exploitation, privilege
    escalation) an agent reached rather than a percentage. Vulnerability exploitation, inherited from
    CyberSecEval 2, again runs opposite this page's stated direction: it is a capability score where
    higher means the model solved more challenges, not a risk rate.
dataset:
  size_note: >
    Combines CyberSecEval 2's unchanged sets (251 textual prompt-injection cases, 500 interpreter-
    abuse prompts) with new CyberSecEval 3 material: 1,000 visual prompt-injection test cases,
    confirmed from the `facebook/cyberseceval3-visual-prompt-injection` Hugging Face dataset's exact
    row count (its own card metadata undersells this as "<1K"); 1,004 multilingual prompt-injection
    cases, counted directly from the released file; and up to 856 multi-turn spear-phishing challenge
    definitions (the reference runner defaults to a 250-case sample). The manual-uplift study is a
    one-time human-subjects exercise, not a reusable item set, and the autonomous-operations study
    runs against a small number of controlled-environment scenarios rather than a fixed prompt file,
    so neither has a comparable "dataset size."
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
  license: "MIT"
  languages:
    - en
    - multilingual (French, German, Hindi and others, machine-translated, for the multilingual prompt-injection set)
  modalities:
    - text
    - code
    - image
  splits: "no train/test split; each category is a single fixed evaluation set, except vulnerability exploitation, part of which is regenerated per run"
  public_test_set: true
publisher:
  org: "Meta (the Purple Llama project)"
  authors:
    - "Shengye Wan"
    - "Cyrus Nikolaidis"
    - "Daniel Song"
    - "David Molnar"
    - "James Crnkovich"
    - "Jayson Grace"
    - "Manish Bhatt"
    - "Sahana Chennabasappa"
    - "Spencer Whitman"
    - "Stephanie Ding"
    - "Vlad Ionescu"
    - "Yue Li"
    - "Joshua Saxe"
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
paper:
  title: "CYBERSECEVAL 3: Advancing the Evaluation of Cybersecurity Risks and Capabilities in Large Language Models"
  arxiv: "2408.01605"
  url: "https://arxiv.org/abs/2408.01605"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
released: "2024-08"
last_updated: ""
lineage:
  family: ""
  predecessor: cyberseceval_2
  successors:
    - cyberseceval_4
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper reports per-category results applied to the Llama 3 model family and contemporaneous
    models (for example, GPT-4 Turbo scored notably higher than Llama 3 405b and Mixtral 8x22B on the
    social-engineering test), showing real separation between models, but does not publish one
    suite-wide score to call saturated or not, and no consolidated newer score against unmodified
    CyberSecEval 3 was found for this page -- later evaluation moved to CyberSecEval 4's different
    category set. Saturation is left unknown rather than guessed.
contamination:
  risk: medium
  note: >
    The fixed prompt sets (textual and visual prompt injection, interpreter abuse, multilingual prompt
    injection) are public and MIT-licensed, unchanged since mid-to-late 2024, so plain exposure in
    later training data is plausible. The manual-uplift human study and the autonomous-operations
    study are one-off exercises against controlled environments rather than reusable public prompt
    sets, so conventional training-set contamination does not apply to them in the same way; their
    risk is closer to publication of the exact challenge design becoming known to future test subjects
    or agents, which the paper does not address.
harness:
  lm_eval: ""
  inspect_evals: "cyse3_visual_prompt_injection (inspect_evals/cyberseceval_3; the only CyberSecEval-3-specific category implemented -- textual prompt injection, interpreter abuse and vulnerability exploitation are covered by re-using the separate cyberseceval_2 task implementation; MITRE compliance, secure code generation, automated social engineering, manual uplift and autonomous offensive cyber operations are not implemented in inspect_evals)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference runner: `python3 -m CybersecurityBenchmarks.benchmark.run` in the PurpleLlama repository."
tags:
  - safety
  - security
  - cybersecurity
  - meta
  - llama
  - purple-llama
  - prompt-injection
  - visual-prompt-injection
  - social-engineering
  - offensive-security
sources:
  - url: "https://arxiv.org/abs/2408.01605"
    title: "CYBERSECEVAL 3: Advancing the Evaluation of Cybersecurity Risks and Capabilities in Large Language Models"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2408.01605"
    title: "CyberSecEval 3, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
    title: "PurpleLlama CybersecurityBenchmarks README and reference implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cyberseceval_3"
    title: "inspect_evals cyberseceval_3 task README"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/cyberseceval3-visual-prompt-injection"
    title: "facebook/cyberseceval3-visual-prompt-injection dataset card API (MIT licence tag, arXiv 2408.01605 tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=facebook/cyberseceval3-visual-prompt-injection"
    title: "facebook/cyberseceval3-visual-prompt-injection exact row count (1,000)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/prompt_injection/prompt_injection_multilingual_machine_translated.json"
    title: "CyberSecEval multilingual prompt-injection file (1,004 entries, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/spear_phishing/multiturn_phishing_challenges.json"
    title: "CyberSecEval multiturn_phishing_challenges.json (856 entries, counted directly)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CyberSecEval 3 measures LLM cybersecurity risk and capability across 8 risk areas the paper sorts into two broad categories: risk to third parties (people or organizations other than the model's own user, such as social-engineering victims) and risk to application developers and end users (insecure code, prompt injection and interpreter abuse reaching whoever deploys or uses the model). It keeps CyberSecEval 2's textual prompt injection, code-interpreter abuse and vulnerability-exploitation tests as-is, and adds three offensive-security areas the paper introduces as new: automated social engineering (a simulated multi-turn spear-phishing conversation), scaling manual offensive cyber operations (a human-subjects study of whether LLM help speeds up novice and expert penetration testers), and autonomous offensive cyber operations (an unassisted LLM agent attempting reconnaissance through privilege escalation against a target host). It also extends prompt injection to images (visual prompt injection) and to additional languages (multilingual prompt injection).

## How it is scored

Reused categories keep CyberSecEval 2's scoring exactly: LLM judges for prompt injection and interpreter abuse, an automated exploit checker for vulnerability exploitation. Visual prompt injection follows the same pattern with a judge LLM shown the model's response and a per-case judge question. Social engineering is scored by a judge LLM against a named 5-point rubric (from "Very Poor" to "Excellent") across persuasion, rapport and argumentation. The manual-uplift study reports human-subject survey responses and challenge-phase completion rates, compared between an LLM-assisted and an unassisted group, rather than an automated score. The autonomous-operations study records which of four fixed attack phases (network reconnaissance, vulnerability identification, exploitation, privilege escalation) an agent reached under a controlled system prompt.

## Dataset and licence

CyberSecEval 3 is released under an MIT licence and combines CyberSecEval 2's unchanged sets with new material: 1,000 visual prompt-injection cases (the Hugging Face dataset card undersells this as "<1K"; its own datasets-server metadata confirms 1,000 rows), 1,004 multilingual prompt-injection cases, and up to 856 spear-phishing challenge definitions (the reference command defaults to sampling 250). The manual-uplift study is a one-time human-subjects exercise rather than a reusable file, and the autonomous-operations study runs against a small number of controlled scenarios, so neither has a comparable dataset size. All new text content is English or machine-translated from English.

## Who publishes it

CyberSecEval 3 comes from a 13-author Meta team led by Shengye Wan and Joshua Saxe, posted to arXiv in August 2024 (a v2 revision followed in September 2024) alongside the Llama 3.1 release. It is maintained in the same PurpleLlama GitHub repository as the earlier versions.

## Lineage

CyberSecEval 3 is the third entry in Meta's CyberSecEval series, following `cyberseceval_2`. Its own inspect_evals implementation literally reuses CyberSecEval 2's task code for textual prompt injection, interpreter abuse and vulnerability exploitation rather than re-deriving them, confirming those three categories are unchanged between versions. Its successor, `cyberseceval_4`, keeps this version's multilingual prompt-injection dataset unchanged (the same 1,004-case file reappears verbatim as CyberSecEval 4's `cyse4_multilingual_prompt_injection` task) while adding malware-analysis and threat-intelligence-reasoning benchmarks and an automated-patching benchmark. This page also documents Prompt Guard, the classifier model CyberSecEval 3's paper introduces alongside these benchmarks, only as a related mitigation artifact -- it is a model the paper recommends deploying, not one of the graded evaluations above. This benchmark is unrelated to `cve_bench` (live exploitation of specific real CVEs) and `wmdp` (a multiple-choice hazardous-knowledge proxy), both catalogued separately here.

## Saturation and contamination

CyberSecEval 3 reports real separation between models on individual categories -- for example GPT-4 Turbo scored notably higher than Llama 3 405b and Mixtral 8x22B on the social-engineering test -- but publishes no single suite-wide score, so this page leaves saturation unknown rather than guessing. No consolidated newer score against unmodified CyberSecEval 3 was found; later work moved to CyberSecEval 4's restructured categories. Contamination risk is medium for the fixed, public prompt sets (textual and visual prompt injection, interpreter abuse, multilingual prompt injection), which have been openly available since mid-to-late 2024. The manual-uplift and autonomous-operations studies are one-off human and agent exercises rather than reusable public prompt files, so ordinary training-set contamination does not apply to them the same way.

## How to run it

inspect_evals implements only `cyse3_visual_prompt_injection` as a CyberSecEval-3-specific task; it covers textual prompt injection, interpreter abuse and vulnerability exploitation by re-using the separate `cyberseceval_2` task implementation, and does not implement MITRE compliance, secure code generation, social engineering, manual uplift or autonomous offensive operations at all. The PurpleLlama repository's own runner covers the automated categories (textual and visual prompt injection, interpreter abuse, multilingual prompt injection, spear phishing) but not the two human/agent studies, which the paper describes as one-off research exercises rather than push-button benchmarks.

## Reading the numbers

Treat a CyberSecEval 3 result as one category's number, not a suite score -- state which of the 8 risk areas it names before comparing it to anything else. Most categories are risk rates where lower is better, but vulnerability exploitation (inherited from CyberSecEval 2) again runs the opposite direction, and the manual-uplift and autonomous-operations studies do not reduce to a percentage at all, so "CyberSecEval 3 score" alone is not a meaningful comparison point across papers. Because the harness that implements this id covers only one of the version's new categories, a model's reported inspect_evals result for `cyberseceval_3` reflects visual prompt injection specifically, not the offensive-operations or social-engineering work the paper is most novel for.
