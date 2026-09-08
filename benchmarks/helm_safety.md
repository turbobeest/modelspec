---
id: helm_safety
name: "HELM Safety"
aliases: ["HELM-Safety"]
page_kind: benchmark
category: safety
subcategory: ""
status: active
summary: "Stanford CRFM leaderboard that scores a model by averaging its results across five existing safety benchmarks into one 0-1 number."
measures: >
  HELM Safety is a Stanford CRFM leaderboard that scores a model's refusal and bias behaviour
  across five existing safety datasets: BBQ, SimpleSafetyTests, HarmBench, AnthropicRedTeam, and
  XSTest. Together they probe six risk categories CRFM drew from AI developers' acceptable-use
  policies: violence, fraud, discrimination, sexual content, harassment, and deception. A model
  sees single-turn prompts ranging from overtly unsafe requests, through red-teamed jailbreak
  attempts meant to bypass guardrails, to sensitive-sounding but benign questions; BBQ instead asks
  multiple-choice questions testing whether the model leans on a social stereotype when context
  does not support one.
task_format: "Single-turn prompts; graded by exact-match accuracy (BBQ) or a two-model LLM-judge harmfulness/helpfulness rating (the other four scenarios)."
metric:
  name: "Mean score (unweighted average of five normalized per-scenario scores)"
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: "CRFM's write-up and leaderboard do not publish a random or human baseline for the aggregate Mean score; models are compared to each other, not to a fixed reference point."
dataset:
  size: null
  size_note: "Five separate datasets, not one: BBQ 58,492 items, AnthropicRedTeam 38,961 items, XSTest 450 items, HarmBench 321 items, SimpleSafetyTests 100 items, per CRFM's write-up."
  url: ""
  license: ""
  languages: ["en"]
  modalities: ["text"]
  splits: ""
  public_test_set: true
publisher:
  org: "Stanford Center for Research on Foundation Models (CRFM)"
  authors: ["Farzaan Kaiyom", "Ahmed Ahmed", "Yifan Mai", "Kevin Klyman", "Rishi Bommasani", "Percy Liang"]
  url: "https://crfm.stanford.edu/helm/safety/latest/"
paper:
  title: "HELM Safety: Towards Standardized Safety Evaluations of Language Models"
  arxiv: ""
  url: "https://crfm.stanford.edu/2024/11/08/helm-safety.html"
  year: 2024
leaderboard_url: "https://crfm.stanford.edu/helm/safety/latest/"
repo_url: "https://github.com/stanford-crfm/helm"
released: "2024-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 0.986
  as_of: "2026-09"
  note: "CRFM flagged 'potential saturation' among top models at the November 2024 launch. On the live leaderboard read 2026-09-07, the top ten models span only 0.974-0.986 of a 1.0 maximum, confirming that pattern has continued."
contamination:
  risk: medium
  note: "All five source datasets publish their prompts openly; the oldest, BBQ and AnthropicRedTeam, have been public for years, long enough to plausibly reach later training or safety-tuning data. HarmBench and XSTest are newer (2023-2024). No source consulted measures actual training-data overlap, but providers are known to safety-tune against red-team and refusal-style prompts like these."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "run_entries_safety.conf (scenarios: bbq, harm_bench, simple_safety_tests, anthropic_red_team, xstest)"
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["safety", "llm-judge", "jailbreak", "red-teaming", "refusal", "bias", "aggregate-benchmark", "crfm"]
sources:
  - url: "https://crfm.stanford.edu/helm/safety/latest/"
    title: "HELM Safety leaderboard"
    accessed: "2026-09-07"
  - url: "https://crfm.stanford.edu/2024/11/08/helm-safety.html"
    title: "HELM Safety: Towards Standardized Safety Evaluations of Language Models (CRFM blog)"
    accessed: "2026-09-07"
  - url: "https://crfm.stanford.edu/helm/"
    title: "Holistic Evaluation of Language Models (HELM) -- leaderboard index"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models"
    accessed: "2026-09-07"
  - url: "https://github.com/stanford-crfm/helm"
    title: "stanford-crfm/helm GitHub repository"
    accessed: "2026-09-07"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/presentation/run_entries_safety.conf"
    title: "HELM Safety run_entries configuration"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice G"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HELM Safety is a Stanford CRFM leaderboard that scores a model's refusal and bias behaviour across five existing safety datasets: BBQ, SimpleSafetyTests, HarmBench, AnthropicRedTeam, and XSTest. Together they probe six risk categories CRFM drew from AI developers' acceptable-use policies: violence, fraud, discrimination, sexual content, harassment, and deception.

A model sees single-turn prompts ranging from overtly unsafe requests, through red-teamed jailbreak attempts meant to bypass guardrails, to sensitive-sounding but benign questions. BBQ instead asks multiple-choice questions testing whether the model leans on a social stereotype when context does not support one. HELM Safety checks whether a response complies with a harmful request, refuses appropriately, or wrongly refuses a benign one.

## How it is scored

BBQ is graded by exact-match accuracy against the unbiased answer. The other four scenarios use an LLM judge: CRFM's two judges are GPT-4o (2024-05-13) and Llama 3.1 405B Instruct Turbo, and each response's harmfulness or helpfulness score is the mean of both judges' ratings. Every scenario score is normalized to 0-1, and the leaderboard's "Mean score" for a model is the unweighted average of all five; higher is better, 1.0 is the maximum.

That single number hides protocol differences. CRFM's write-up documents judges sometimes refusing to grade a harmful transcript rather than score it, at rates that vary sharply by judge -- GPT-4o graded every response in one worked example while Claude 3.5 Sonnet, tried as an alternate judge, failed on nearly 27% of them. A separate table in the same write-up shows automated jailbreak suffixes (the GCG method) cutting HarmBench scores by roughly 26% on average, a comparison that is not folded into the Mean score shown on the leaderboard.

## Dataset and licence

HELM Safety runs five separately published datasets rather than one. Per CRFM's write-up: BBQ (Parrish et al., arXiv 2110.08193) contributes 58,492 bias-probing questions; SimpleSafetyTests (Vidgen et al., arXiv 2311.08370) 100 unsafe prompts; HarmBench (Mazeika et al., arXiv 2402.04249) 321 unsafe prompts; AnthropicRedTeam, drawn from Anthropic's public hh-rlhf red-team transcripts, 38,961 attacks; and XSTest (Rottger et al., arXiv 2308.01263) 450 safe-or-unsafe prompts. All five are fully public prompt sets, browsable per-instance on the leaderboard, with no held-out split described for the composite.

CRFM does not state one unified licence for the combined suite, and each source dataset carries whatever licence its own authors published it under -- not independently verified here, so licence is not established for this page. The evaluation framework itself, stanford-crfm/helm, is published under the Apache 2.0 licence.

## Who publishes it

HELM Safety comes from Stanford's Center for Research on Foundation Models (CRFM). The write-up, "HELM Safety: Towards Standardized Safety Evaluations of Language Models," is by Farzaan Kaiyom, Ahmed Ahmed, Yifan Mai, Kevin Klyman, Rishi Bommasani, and Percy Liang, published as a CRFM blog post in November 2024 rather than as a separate arXiv paper. It sits inside the wider HELM project, which Percy Liang, Rishi Bommasani, Tony Lee and a large multi-author team introduced in "Holistic Evaluation of Language Models" (arXiv 2211.09110, November 2022); that original paper defines the HELM framework but does not itself cover Safety, which arrived two years later as a separate initiative under the same project. CRFM maintains the public leaderboard and keeps adding newly released models.

## Lineage

HELM Safety is not a revision of one earlier benchmark; it aggregates five pre-existing, independently published benchmarks -- BBQ, SimpleSafetyTests, HarmBench, AnthropicRedTeam, and XSTest -- none of which has its own page in this repository yet. CRFM says it drew its six-category risk taxonomy from prior work behind AIR-Bench, a sibling CRFM leaderboard that scores models against developers' acceptable-use policies; the two leaderboards initially shared the same 24-model evaluation cohort, but AIR-Bench is a related leaderboard under the same HELM umbrella, not a formal predecessor, and it has no page here either. No successor to HELM Safety has been announced.

## Saturation and contamination

CRFM flagged saturation risk at launch, writing in November 2024 that "the relatively high scores of the top models indicate potential saturation" and calling for harder benchmarks to keep separating strong models. Reading the live leaderboard on 2026-09-07, that pattern has continued: the top ten models -- GPT-5 nano, o3, gpt-oss-120b, two Claude 4 Sonnet configurations, GPT-5, GPT-5 mini, Kimi K2 Instruct, Claude 3.5 Sonnet, and o1 -- all sit between 0.974 and 0.986 of a 1.0 maximum, too narrow a band for the Mean score alone to separate leading models.

Contamination risk is medium. All five datasets publish their prompts openly; the oldest, BBQ and AnthropicRedTeam, have been public for years, long enough to plausibly reach later training or safety-tuning data. HarmBench and XSTest are newer, from 2023-2024. No source consulted here measures actual training-data overlap, but providers are known to safety-tune against red-team and refusal-style prompts like these, which could raise scores for reasons unrelated to general safety.

## How to run it

The reference implementation lives in the stanford-crfm/helm GitHub repository (Apache 2.0 licence). Its run configuration, run_entries_safety.conf, names the five scenarios exactly as bbq, harm_bench, simple_safety_tests, anthropic_red_team, and xstest; running all five and averaging their normalized scores reproduces the Mean score column. Matching CRFM's published numbers also requires its two judge models, GPT-4o (2024-05-13) and Llama 3.1 405B Instruct Turbo -- whether CRFM kept these same two judges for every model added to the leaderboard after the original 24 is not established, which matters when comparing older and newer rows.

No other harness checked for this page -- lm-evaluation-harness, Inspect Evals, OpenCompass, or BIG-bench -- was confirmed to carry a matching five-way "HELM Safety" aggregate task; some of the five constituent datasets may appear individually elsewhere under their own names, but that was not independently verified here.

## Reading the numbers

A high HELM Safety score means a model avoided the specific harmful completions and biased BBQ answers these five datasets sample, under two particular LLM judges, on prompts that were not adversarially perturbed. CRFM is explicit this is not a safety certification: even leading models, in its own words, are still very likely to show unsafe behaviour outside what these five benchmarks cover. A model can also score well by refusing broadly rather than by telling harmful and benign requests apart -- XSTest exists to catch exactly that failure, so check its sub-score before trusting a strong overall number. Because top scores cluster tightly, treat small Mean-score gaps between leading models as noise rather than a real ranking, and compare a model's HarmBench score against its HarmBench GCG-T score, where published, to see how much of that safety survives an adversarial prompt.
