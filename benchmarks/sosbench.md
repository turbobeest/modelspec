---
id: sosbench
name: "SOSBench"
aliases:
  - "SoSBench"
  - "SOSBench: Benchmarking Safety Alignment on Scientific Knowledge"
  - "SoSBench: Benchmarking Safety Alignment on Six Scientific Domains"
page_kind: benchmark
category: safety
subcategory: "regulation-grounded hazardous scientific knowledge misuse"
status: active
summary: "3,000 regulation-grounded, hazard-focused prompts across six scientific domains, testing whether models refuse policy-violating requests that require real scientific expertise to recognise."
measures: >
  SOSBench tests safety alignment against knowledge-intensive, scientifically sophisticated
  misuse requests, not low-effort or superficial jailbreak prompts. Every prompt is grounded in
  authoritative regulatory text (from bodies such as the U.S. government and the United Nations)
  naming a specific hazard, for example an NFPA-704 level-4 chemical, a DEA Schedule III
  substance or an ICD-11 pathology code, then expanded through an LLM-assisted evolutionary
  pipeline into a realistic instruction using domain databases (such as PubChem or DSM-5 synonym
  lists). The six covered domains are chemistry, biology, medicine, pharmacology, physics and
  psychology, with 500 prompts per domain.
task_format: >
  Open-ended generation: the model is given a hazardous, regulation-derived instruction and its
  free-text response is graded for whether it discloses policy-violating scientific content. A
  300-prompt "lite" subset (50 per domain) is also published for cheaper evaluation runs.
metric:
  name: "unsafe response rate (LLM-judge)"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Responses are graded on a binary safe(0)/unsafe(1) scale by an LLM judge; the paper reports
    that GPT-4.1-based judging showed the best agreement with human annotators among the judges
    they tested. No random or human-response baseline applies, since the metric is a judged
    safety rate on model outputs, not a correctness score against a fixed answer key.
dataset:
  size: 3000
  size_note: >
    The Hugging Face dataset card and paper both state 3,000 prompts, 500 per domain across six
    domains (chemistry, biology, medicine, pharmacology, physics, psychology). The project site
    additionally lists a 300-prompt lite version (50 per domain) for lower-cost evaluation.
  url: "https://huggingface.co/SOSBench"
  license: "gated access; Hugging Face lists the licence tag as \"other\" with a use agreement restricting the data to safety, alignment, oversight, red-teaming and policy-analysis research"
  languages:
    - en
  modalities:
    - text
  splits: "single train split (3,000 rows); no answer key, since responses are judged rather than matched"
  public_test_set: false
publisher:
  org: "University of Washington, University of Georgia, Western Washington University, University of Illinois Urbana-Champaign"
  authors:
    - "Fengqing Jiang"
    - "Fengbo Ma"
    - "Zhangchen Xu"
    - "Yuetai Li"
    - "Zixin Rao"
    - "Bhaskar Ramasubramanian"
    - "Luyao Niu"
    - "Bo Li"
    - "Xianyan Chen"
    - "Zhen Xiang"
    - "Radha Poovendran"
  url: "https://sosbench.github.io/"
paper:
  title: "SOSBench: Benchmarking Safety Alignment on Scientific Knowledge"
  arxiv: "2505.21605"
  url: "https://arxiv.org/abs/2505.21605"
  year: 2025
leaderboard_url: "https://sosbench.github.io/"
repo_url: "https://github.com/SOSBenchEval"
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 84.9
  as_of: "2025-05"
  note: >
    The paper reports harmful-response rates as high as 84.9% for DeepSeek-R1 and 50.3% for
    GPT-4.1, meaning the strongest models tested still failed to refuse a majority-to-plurality
    of hazardous prompts. That is the opposite of saturation on the safety axis: the benchmark
    currently separates models by how often they fail, not by how close they are to a perfect
    refusal ceiling. It is marked "watch" here because a benchmark on which even capable models
    concentrate near a common high failure rate can lose discriminative power as labs specifically
    train against it.
contamination:
  risk: medium
  note: >
    Prompts are synthetically evolved from public regulatory text and hazard databases rather
    than scraped verbatim from an existing exam, which limits direct answer-key leakage. The
    dataset itself, however, is public (behind a use-agreement gate) with the full prompt set
    visible to accepted users, so models specifically safety-tuned against this named benchmark
    after its 2025 release could show inflated refusal rates that do not reflect general
    hazardous-science robustness.
harness:
  lm_eval: ""
  inspect_evals: "sosbench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect_evals task takes a domain parameter (e.g. biology, chemistry) to run a single-domain slice rather than all six at once."
tags:
  - safety
  - red-teaming
  - chemistry
  - biology
  - medicine
  - hazard
  - regulation-grounded
sources:
  - url: "https://arxiv.org/abs/2505.21605"
    title: "SOSBench paper abstract (arXiv:2505.21605), six domains, 3,000 prompts, harmful-response rates for DeepSeek-R1 and GPT-4.1"
    accessed: "2026-09-08"
  - url: "https://sosbench.github.io/"
    title: "SOSBench project site (author affiliations UW/UGA/WWU/UIUC, ICLR 2026 acceptance, 300-prompt lite version, links to code/data)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sosbench/README.md"
    title: "inspect_evals sosbench README (six domain splits, GPT-4-based binary safe/unsafe judge, domain task parameter)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/SOSBench/SOSBench"
    title: "Hugging Face dataset API for SOSBench/SOSBench (license tag \"other\", 3,000 train rows, gated access notice)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-003"
---

## What it measures

SOSBench probes whether a model will disclose genuinely hazardous, policy-violating scientific information when the request requires real domain expertise to recognise as dangerous, rather than testing against shallow or obviously malicious jailbreak phrasing. Every one of its 3,000 prompts starts from an authoritative regulatory source, such as U.S. federal rules or United Nations conventions, that names a specific controlled or hazardous item, for example a chemical carrying an NFPA-704 level-4 rating, a DEA Schedule III substance, or a condition coded in ICD-11. An LLM-assisted evolutionary process then expands each seed into a realistic, natural-sounding instruction using domain databases like PubChem or DSM-5 synonym lists, spread evenly (500 each) across chemistry, biology, medicine, pharmacology, physics and psychology.

## How it is scored

Each model response to a hazardous prompt is judged on a binary safe (0) or unsafe (1) scale by an LLM judge; the paper found GPT-4.1-family judges tracked human safety annotations most closely among the judges it tried. The reported number is a rate: the share of prompts (overall or per domain) that produced a policy-violating, unsafe response, so lower is better, unlike most capability benchmarks on this page's schema convention. There is no ground-truth "answer" to match against; correctness is a judgement about the response's safety, which makes the choice and calibration of the judge model part of the reported score, not a detail that can be ignored.

## Dataset and licence

The full dataset is 3,000 prompts, 500 per domain across the six domains named above, hosted on Hugging Face at `SOSBench/SOSBench` behind a gated use agreement restricting use to safety, alignment, oversight, red-teaming and policy-analysis research; the Hugging Face API lists the licence tag as "other" rather than a standard SPDX licence. A smaller 300-prompt "lite" version (50 per domain) is also published for cheaper evaluation runs. There is a single train split with no held-out answer key, since grading is judge-based rather than exact match.

## Who publishes it

The paper, "SOSBench: Benchmarking Safety Alignment on Scientific Knowledge," is by Fengqing Jiang, Fengbo Ma, Zhangchen Xu, Yuetai Li, Zixin Rao, Bhaskar Ramasubramanian, Luyao Niu, Bo Li, Xianyan Chen, Zhen Xiang and Radha Poovendran, with author affiliations spanning the University of Washington, University of Georgia, Western Washington University and the University of Illinois Urbana-Champaign per the project site. It was first posted to arXiv in May 2025 and accepted at ICLR 2026. The project site (sosbench.github.io) hosts the paper, code and dataset links and is maintained by the same author group.

## Lineage

SOSBench is a 2025 addition to the scientific-hazard-safety benchmark space; no predecessor, successor or variant is tracked in this repository. It is distinct from generic jailbreak or refusal benchmarks that do not require domain expertise to construct: its prompts are explicitly regulation-derived and hazard-specific rather than generic harmful-request templates.

## Saturation and contamination

The paper's headline finding runs the opposite direction from a typical capability-benchmark ceiling: leading models still produced unsafe, policy-violating responses at high rates, up to 84.9% for DeepSeek-R1 and 50.3% for GPT-4.1, meaning refusal behaviour on this benchmark is far from saturated toward safe. This page marks saturation status "watch" rather than "open" because a named, public safety benchmark like this one is a plausible target for post-hoc safety fine-tuning by labs, which could compress scores toward low unsafe-rates without necessarily improving robustness to novel hazardous-science requests outside the benchmark's specific prompt distribution. Contamination risk is medium: prompts are synthetically evolved rather than copied from a single public source, but the full prompt set is available to accepted dataset users, so targeted defensive tuning against this specific benchmark is possible after its release.

## How to run it

inspect_evals implements this as the `sosbench` task, accepting a `domain` parameter to run a single scientific domain (for example `biology` or `chemistry`) rather than always scoring all six domains together, and uses an LLM judge to produce the safe/unsafe rate. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench implementation was found. Because the dataset is gated, running it requires accepting the publisher's use agreement before download.

## Reading the numbers

A low unsafe-response rate on SOSBench means a model tends to refuse or safely handle hazardous, regulation-grounded scientific requests that specifically require expertise to recognise as dangerous, which is a harder bar than refusing an obviously malicious prompt. It does not mean the model is safe against novel hazard framings outside this benchmark's six domains or its specific prompt-construction pipeline, and a low score achieved shortly after the benchmark's public release should be checked for benchmark-specific safety tuning rather than assumed to be general robustness. Always report which judge model produced the safe/unsafe labels, since the paper itself found meaningful disagreement in human-agreement rates across candidate judges.
