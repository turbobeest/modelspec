---
id: cyberseceval_2
name: "CyberSecEval 2"
aliases:
  - "CYBERSECEVAL 2"
  - "Purple Llama CyberSecEval 2"
page_kind: benchmark
category: safety
subcategory: "LLM cybersecurity risk and capability suite: prompt injection, code-interpreter abuse, insecure code generation, and offensive vulnerability-exploitation capability"
status: superseded
summary: "Meta's second-generation LLM cybersecurity suite: adds prompt-injection, code-interpreter-abuse and exploit-capability tests to the original CyberSecEval's insecure-code and attack-compliance measures."
measures: >
  CyberSecEval 2 is Meta's second release in the CyberSecEval series, following the original
  CyberSecEval (arXiv 2312.04724, not separately catalogued in this repository). It is a suite of
  separately-scored categories rather than one number. It carries forward the first version's two
  core measures -- whether a model complies with requests to help carry out cyberattacks (MITRE
  ATT&CK-based compliance tests) and whether a model's own generated code is insecure (instruct and
  autocomplete tests, scored by an automated insecure-code detector for known CWE patterns) -- and
  adds two new areas named explicitly in the paper's title scope: prompt injection (251 hand-authored
  English test cases spanning direct and indirect delivery and 15 attack-technique categories) and
  code-interpreter abuse (500 prompts across 5 categories asking a model to misuse an attached code
  interpreter, for example to read files it should not access). It also adds a False Refusal Rate
  (FRR) test set of borderline-but-benign cybersecurity requests, introduced to weigh a model's safety
  against the utility it loses by over-refusing, and expands automated vulnerability-exploitation
  tests that measure whether a model can solve string-constraint, buffer-overflow, memory-corruption
  and SQL-injection challenges end to end in C, Python and JavaScript.
task_format: >
  A per-category suite: MITRE compliance (1,000 cyberattack-assistance prompts, LLM-expanded and
  LLM-judged for attacker helpfulness), MITRE False Refusal Rate (750 borderline-benign prompts,
  judged for refusal), instruct and autocomplete insecure-code tests (1,916 prompts each, scored by
  Meta's Insecure Code Detector), textual prompt injection (251 direct/indirect cases, LLM-judged for
  whether the injected instruction was followed), code-interpreter abuse (500 prompts, LLM-judged as
  malicious or non-malicious), and vulnerability-exploitation challenges (hand-authored and, for some
  test types, randomly generated per run, scored pass/fail on whether the model's exploit works).
metric:
  name: "per-category rates -- mainly an attack/injection/insecure-code success or compliance rate (share of test cases judged unsafe); direction and headline number differ by category"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CyberSecEval 2 does not reduce to one score, so "lower is better" describes most but not all of
    it. The paper's own headline numbers: all tested models (GPT-4, Mistral, Llama 3 70B-Instruct,
    Code Llama and others) showed prompt-injection success at 13%-47% depending on model and test
    type, averaging 28% across models; most models scored 0% on the buffer-overflow and end-to-end
    memory-corruption exploitation tests, with GPT-4 a notable exception near 20% on one exploitation
    category; and one Code Llama variant reached a 70% false refusal rate on the FRR borderline set,
    well above other models. Every category above is a risk rate where lower is better, except
    vulnerability exploitation, which the paper reports as a capability score in the opposite
    direction (higher means the model solved more challenges) -- that category is this page's one
    exception to the stated direction. No single random-guess or human baseline applies suite-wide.
dataset:
  size_note: >
    A suite of separately sized test sets rather than one dataset, confirmed by counting the released
    JSON files directly: 1,000 MITRE compliance prompts (carried over from CyberSecEval 1, with
    augmentation), 750 MITRE False Refusal Rate prompts, 1,916 instruct insecure-code prompts (a later
    cleaned instruct-v2 set trims this to 1,681 by removing invalid prompts) and 1,916 autocomplete
    insecure-code prompts, 251 prompt-injection test cases, and 500 code-interpreter-abuse prompts
    (100 per category across 5 categories, matching the paper's own count). The vulnerability-
    exploitation set mixes hand-authored challenges with programs generated fresh at evaluation time,
    by design, to resist memorization, so it has no single fixed size.
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "no train/test split; each category is a single fixed evaluation set, except vulnerability exploitation, part of which is regenerated per run"
  public_test_set: true
publisher:
  org: "Meta (the Purple Llama project)"
  authors:
    - "Manish Bhatt"
    - "Sahana Chennabasappa"
    - "Yue Li"
    - "Cyrus Nikolaidis"
    - "Daniel Song"
    - "Shengye Wan"
    - "Faizan Ahmad"
    - "Cornelius Aschermann"
    - "Yaohui Chen"
    - "Dhaval Kapil"
    - "David Molnar"
    - "Spencer Whitman"
    - "Joshua Saxe"
  url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
paper:
  title: "CyberSecEval 2: A Wide-Ranging Cybersecurity Evaluation Suite for Large Language Models"
  arxiv: "2404.13161"
  url: "https://arxiv.org/abs/2404.13161"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
released: "2024-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - cyberseceval_3
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2024-04"
  note: >
    Not saturated in the paper's own results: prompt-injection success spans 13%-47% across models,
    most models score 0% on buffer-overflow exploitation while GPT-4 stands out near 20% on one
    exploitation category, and false refusal rates vary from near 0% to 70% -- wide enough spreads to
    keep separating models. No source read for this page reports a consolidated newer score on
    unmodified CyberSecEval 2 itself; subsequent work evaluated CyberSecEval 3 and 4 instead, whose
    categories are not the same tests, so a current top score for this exact suite is not established.
contamination:
  risk: medium
  note: >
    The MITRE, instruct/autocomplete, prompt-injection and interpreter-abuse sets are fixed, public,
    MIT-licensed files that have sat unchanged on GitHub since April 2024, over two years before this
    research pass, so plain exposure during later pretraining is plausible for those categories. The
    vulnerability-exploitation tests are different by design: the paper states challenges are randomly
    generated to avoid LLM memorization, and the canary-exploit generator produces fresh programs per
    run rather than reusing a fixed file, which limits (but does not by itself measure) contamination
    risk for that one category.
harness:
  lm_eval: ""
  inspect_evals: "cyse2_interpreter_abuse, cyse2_prompt_injection, cyse2_vulnerability_exploit (inspect_evals/cyberseceval_2; covers 3 of the paper's categories -- MITRE compliance, MITRE FRR, and the instruct/autocomplete insecure-code tests are not implemented in this harness)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference runner: `python3 -m CybersecurityBenchmarks.benchmark.run` in the PurpleLlama repository, which covers every category including the ones inspect_evals omits."
tags:
  - safety
  - security
  - cybersecurity
  - meta
  - llama
  - purple-llama
  - prompt-injection
  - code-interpreter
  - insecure-code
  - exploitation
sources:
  - url: "https://arxiv.org/abs/2404.13161"
    title: "CyberSecEval 2: A Wide-Ranging Cybersecurity Evaluation Suite for Large Language Models"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2404.13161"
    title: "CyberSecEval 2, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/meta-llama/PurpleLlama/tree/main/CybersecurityBenchmarks"
    title: "PurpleLlama CybersecurityBenchmarks README and reference implementation"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cyberseceval_2"
    title: "inspect_evals cyberseceval_2 task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/LICENSE"
    title: "CybersecurityBenchmarks LICENSE (MIT)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/prompt_injection/prompt_injection.json"
    title: "CyberSecEval prompt_injection.json (251 entries, counted directly)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/interpreter/interpreter.json"
    title: "CyberSecEval interpreter.json (500 entries, counted directly)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CyberSecEval 2 measures LLM cybersecurity risk and capability across several independent test categories rather than a single skill. It keeps the original CyberSecEval's two questions -- can a model be induced to help with an offensive cyberattack, and does a model's own generated code carry known security weaknesses -- and adds two categories the paper introduces by name: prompt injection (can a system prompt's rules be overridden by instructions hidden in user or third-party content) and code-interpreter abuse (will a model comply when asked to misuse an attached code interpreter, for example to read a file it should not). A fifth area, automated vulnerability exploitation, asks whether a model can solve constraint-satisfaction, buffer-overflow, memory-corruption and SQL-injection challenges end to end, treating exploit generation as a capability rather than a risk to suppress.

CyberSecEval 2 also introduces False Refusal Rate (FRR): a set of borderline-but-benign cybersecurity requests, used alongside the attack-compliance tests to show that a model conditioned to refuse unsafe requests can also learn to refuse safe ones, at a cost to utility.

## How it is scored

Each category has its own metric and its own judge. MITRE compliance prompts are first expanded by one LLM, then judged by a second as to whether the expanded response would help a real attack; FRR prompts are scored by keyword-based refusal detection. Instruct and autocomplete code prompts are scored by Meta's Insecure Code Detector (ICD) for known CWE patterns, giving a vulnerable/pass rate. Prompt-injection and interpreter-abuse cases are judged by a separate LLM as to whether the injection succeeded or the interpreter request was carried out, classified non-malicious, potentially malicious, or extremely malicious for interpreter abuse. Vulnerability-exploitation challenges are scored automatically, pass/fail, by whether the model's output actually solves the underlying program. The judge and expansion models are independent of the model under test; the paper used GPT-3.5 for judging.

## Dataset and licence

CyberSecEval 2 is not one dataset but several, released together under an MIT licence in the PurpleLlama repository: 1,000 MITRE compliance prompts, 750 MITRE FRR prompts, 1,916 instruct and 1,916 autocomplete insecure-code prompts (1,681 in a later cleaned instruct-v2 release), 251 prompt-injection test cases, and 500 code-interpreter-abuse prompts, all counted directly from the released JSON files for this page. Vulnerability-exploitation tests mix hand-authored challenges with programs synthesized at evaluation time. All text is English; content spans natural-language attack prompts and source code in C, Python and JavaScript.

## Who publishes it

CyberSecEval 2 comes from a 13-author Meta team led by Manish Bhatt and Joshua Saxe, released under the Purple Llama project and first posted to arXiv in April 2024. Meta's GitHub organisation hosts the reference implementation and continues to accept fixes, though as of mid-2025 the maintainers signalled they were reassessing the benchmark's next-version design (see Lineage).

## Lineage

CyberSecEval 2 is the second entry in Meta's CyberSecEval series. Its predecessor, the original CyberSecEval (arXiv 2312.04724, "A Secure Coding Benchmark for Language Models"), is not separately catalogued in this repository; CyberSecEval 2 carries forward that version's MITRE compliance and insecure-code tests essentially unchanged while adding prompt injection, interpreter abuse, FRR and expanded exploitation tests. Its successor, `cyberseceval_3`, keeps this version's textual prompt-injection, interpreter-abuse and exploitation tests as-is (the inspect_evals implementation of CyberSecEval 3 literally reuses this version's task code for those three categories) while adding visual prompt injection, automated social engineering and offensive-operations studies. This benchmark is unrelated to `cve_bench`, which tests live exploitation of specific real-world CVEs rather than a graded multi-category suite, and to `wmdp`, a multiple-choice hazardous-knowledge proxy; both are catalogued separately in this repository.

## Saturation and contamination

No single score exists to call saturated or not, but within categories the paper's own numbers still separate models widely: prompt-injection success ranges 13%-47%, exploitation scores are near-zero for most models with GPT-4 a clear outlier, and false refusal ranges from near 0% to 70%. No source read for this page reports a consolidated newer score against unmodified CyberSecEval 2, since later work moved to CyberSecEval 3 and 4's different category sets. Contamination risk is medium: the fixed prompt sets (MITRE, instruct/autocomplete, prompt injection, interpreter abuse) have been public and unchanged for over two years, but the exploitation tests are partly regenerated per run specifically to resist memorization.

## How to run it

inspect_evals implements three of the six categories -- `cyse2_interpreter_abuse`, `cyse2_prompt_injection`, `cyse2_vulnerability_exploit` -- leaving MITRE compliance, MITRE FRR, and the instruct/autocomplete insecure-code tests unimplemented in that harness. The PurpleLlama repository's own runner (`python3 -m CybersecurityBenchmarks.benchmark.run`) covers every category. Both require a separate judge LLM (the paper used GPT-3.5); results depend on which judge model is used, since judge choice is not standardized across reporters.

## Reading the numbers

A CyberSecEval 2 result is only meaningful per category: a "score" without naming prompt injection, interpreter abuse, MITRE compliance, insecure code, or exploitation is not comparable to another paper's number for a different category. Remember that most categories are risk rates where lower is better, but the vulnerability-exploitation category is scored as a capability where higher means more exploits solved -- the opposite direction from the rest of the suite. Because judge and expansion models are independent of the model under test and are not standardized, differences of a few points between two reported runs may reflect judge choice rather than the tested model. Scores here also predate CyberSecEval 3 and 4's harder, expanded categories, so a strong CyberSecEval 2 result does not speak to the offensive or defensive areas only later versions test.
