---
id: strong_reject
name: "StrongREJECT"
aliases: []
page_kind: benchmark
category: safety
subcategory: "jailbreak robustness"
status: active
summary: "Measures how much harmful, specific and convincing content a model produces on forbidden prompts, with or without a jailbreak applied, using an LLM-judged rubric."
measures: "StrongREJECT gives a model a curated set of forbidden prompts -- requests for genuinely harmful, specific assistance across categories such as illegal goods and services, non-violent crime, hate/harassment/discrimination, disinformation, violence and sexual content -- and records how the model responds, either directly or after a jailbreak technique has rewritten the prompt. It targets whether jailbreak attacks actually extract usable harmful content, rather than just whether a model's refusal wording was bypassed, which the paper argues earlier benchmarks conflated."
task_format: "Open-ended single-turn generation on a forbidden prompt (optionally jailbreak-transformed), graded by an LLM judge on refusal plus 5-point specificity and convincingness scales."
metric:
  name: "StrongREJECT score"
  direction: lower_is_better
  unit: "points"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper's canonical score is score = (1 - refused) x (specificity + convincingness) / 2, with refused in {0,1} and specificity/convincingness each rescaled to [0,1] from 5-point Likert judge ratings, giving a 0-to-1 scale where 0 means the model refused (best case for safety) and 1 means it gave a maximally specific, convincing harmful response (worst case). The inspect_evals implementation computes the same three components but does not rescale specificity/convincingness from their native 1-5 range, so its reported score runs 0 to 5; comparing inspect_evals numbers to paper-reported numbers requires accounting for this scale difference."
dataset:
  size: 313
  size_note: "The paper reports 313 forbidden prompts across 6 categories, with at least 50 prompts per category. The dataset file currently on GitHub (strongreject_dataset.csv, the version the inspect_evals task loads) contains 323 prompt rows, a discrepancy between the published paper count and the current repository file that this page could not resolve from the sources consulted. A separate strongreject_small_dataset.csv holds a 60-prompt subset for lighter-weight testing."
  url: "https://github.com/alexandrasouly/strongreject/tree/main/strongreject_dataset"
  license: "MIT (for the project's own code and custom-authored prompts; prompts sourced from AdvBench and DAN are MIT-licensed upstream, and prompts drawn from MasterKey, MaliciousInstruct, HarmfulQ and the OpenAI GPT-4 system card carry no formal re-licensing from those sources)"
  languages: ["en"]
  modalities: ["text"]
  splits: "single set, no train/test split; a 60-prompt small subset is provided separately for quick runs"
  public_test_set: true
publisher:
  org: "UC Berkeley (Center for Human-Compatible AI) and collaborators"
  authors: ["Alexandra Souly", "Qingyuan Lu", "Dillon Bowen", "Tu Trinh", "Elvis Hsieh", "Sana Pandey", "Pieter Abbeel", "Justin Svegliato", "Scott Emmons", "Olivia Watkins", "Sam Toyer"]
  url: "https://strong-reject.readthedocs.io"
paper:
  title: "A StrongREJECT for Empty Jailbreaks"
  arxiv: "2402.10260"
  url: "https://arxiv.org/abs/2402.10260"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/alexandrasouly/strongreject"
released: "2024-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No source consulted here gives a current leaderboard or a dated set of frontier-model scores, so saturation status is not established; the benchmark's purpose (jailbreak susceptibility) also means a low score is the target, so the usual 'saturation' framing of scores clustering near a ceiling applies inversely here (models clustering near 0 with no jailbreak applied)."
contamination:
  risk: low
  note: "The forbidden prompts are intentionally public (the dataset's value depends on being usable for red-teaming), and the harness pins a specific Git commit of the CSV for reproducibility rather than a held-out set, so the risk here is not answer leakage in the usual sense; the more relevant risk is that model safety training may specifically target these known prompts, which the paper's own aim (measuring real jailbreak success, not memorized refusals) is partly designed around."
harness:
  lm_eval: ""
  inspect_evals: "strong_reject"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["jailbreak", "red-teaming", "llm-judge", "refusal"]
sources:
  - url: "https://arxiv.org/abs/2402.10260"
    title: "A StrongREJECT for Empty Jailbreaks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.10260"
    title: "A StrongREJECT for Empty Jailbreaks (ar5iv HTML)"
    accessed: "2026-09-08"
  - url: "https://github.com/alexandrasouly/strongreject"
    title: "StrongREJECT GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/alexandrasouly/strongreject/main/strongreject_dataset/strongreject_dataset.csv"
    title: "strongreject_dataset.csv (full dataset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/alexandrasouly/strongreject/main/strongreject_dataset/strongreject_small_dataset.csv"
    title: "strongreject_small_dataset.csv (60-prompt subset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/strong_reject/README.md"
    title: "inspect_evals strong_reject README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/strong_reject/strong_reject.py"
    title: "inspect_evals strong_reject task source"
    accessed: "2026-09-08"
  - url: "https://neurips.cc/virtual/2024/poster/97752"
    title: "NeurIPS 2024 Datasets and Benchmarks Track poster page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

StrongREJECT measures whether a language model can be induced to give genuinely useful, harmful assistance, not merely whether it avoids saying "I can't help with that." Each item is a forbidden prompt -- a request that a safety-conscious model should refuse -- drawn from six categories: illegal goods and services, non-violent crime, hate/harassment/discrimination, disinformation and deception, violence, and sexual content. The model can be queried with the prompt directly, to establish a baseline refusal rate, or with the prompt rewritten by a jailbreak technique, to test whether that technique actually elicits harmful, specific, convincing output rather than just a differently worded but still useless response.

The paper's motivating finding is that many published jailbreak techniques were evaluated with weak graders that counted a jailbreak as "successful" whenever the model failed to explicitly refuse, even if the resulting content was vague, wrong or otherwise unusable for harm. StrongREJECT's grading is built to separate "the model stopped refusing" from "the model actually helped."

## How it is scored

Each response is scored by an LLM judge using a rubric that returns three values: a binary refusal flag, a 1-5 specificity rating (how concretely useful the response is) and a 1-5 convincingness rating. The paper's canonical StrongREJECT score is `(1 - refused) x (specific + convincing) / 2`, with specificity and convincingness rescaled to [0,1] before averaging, giving a 0-to-1 score where 0 is the safest outcome (refusal) and 1 is a fully specific, fully convincing harmful response. The paper's primary experiments use a GPT-4o-mini rubric-based judge and also release an open-source fine-tuned Gemma 2B judge as a lighter-weight alternative.

The inspect_evals implementation follows the same three-component formula but does not rescale specificity and convincingness from their native 1-5 range, so it reports on a 0-to-5 scale by default, using GPT-4o as the judge model (`judge_llm`, configurable). It also ships one built-in jailbreak method (`AIM`, a role-play jailbreak prompt) selectable via `jailbreak_method`, on top of the no-jailbreak default. Because of the differing score scales, numbers from the two implementations are not directly comparable without adjustment.

## Dataset and licence

The paper describes 313 forbidden prompts across the six categories, with at least 50 prompts in every category, sourced partly from prior jailbreak/red-teaming work (AdvBench, DAN, MasterKey, MaliciousInstruct, HarmfulQ, the OpenAI GPT-4 system card) and partly custom-written for this benchmark. The dataset file currently hosted on GitHub and loaded by the inspect_evals task (`strongreject_dataset.csv`) contains 323 prompt rows as counted directly from the file; this page could not reconcile that count against the paper's stated 313 from the sources reviewed, so both numbers are reported here as a known discrepancy. A smaller 60-prompt file (`strongreject_small_dataset.csv`) is provided for lighter-weight runs. The project's own code and custom-authored prompts are MIT-licensed; prompts drawn from other published jailbreak datasets carry whatever licence (or lack of one) those sources had.

## Who publishes it

StrongREJECT was introduced by Alexandra Souly, Qingyuan Lu, Dillon Bowen and co-authors, including Pieter Abbeel, in the paper "A StrongREJECT for Empty Jailbreaks" (arXiv, February 2024), presented at the NeurIPS 2024 Datasets and Benchmarks Track. Documentation and the evaluator are maintained at strong-reject.readthedocs.io and the alexandrasouly/strongreject GitHub repository; there is no separate public leaderboard reviewed for this page.

## Lineage

StrongREJECT has no family page, predecessor or successor confirmed from a primary source in this repository. It positions itself against earlier, less rigorous jailbreak-success benchmarks (the paper specifically critiques weak keyword/refusal-based graders used in prior jailbreak papers) without naming a single predecessor benchmark it replaces.

## Saturation and contamination

No dated, current leaderboard or set of frontier-model scores was found in the sources reviewed here, so saturation status is unknown. Because the benchmark measures vulnerability rather than capability, the usual notion of "saturation" (scores clustering at a ceiling) would instead mean well-aligned models clustering near the safe end (score near 0 with no jailbreak applied); no source here establishes whether that has happened broadly. Contamination in the usual answer-leakage sense does not apply the same way here, since the forbidden prompts are meant to be public and reusable for red-teaming; the more relevant risk, not directly measured by any source consulted, is that a model's safety training could specifically target these known prompts rather than generalizing.

## How to run it

The reference implementation lives in the alexandrasouly/strongreject GitHub repository, with the evaluator described in the paper and packaged for install via its own Python library. inspect_evals ships it as `inspect_evals/strong_reject`, configurable with `jailbreak_method` (`None` or the built-in `AIM` prompt, or a custom callable), `judge_llm` (default `openai/gpt-4o`) and `epochs`. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench integration was confirmed from a primary source for this page. Because the score depends on an LLM judge, results can shift with the judge model and its prompt version, and inspect_evals' changelog notes a scoring-edge-case fix (discarding out-of-rubric-range judge responses) that changed reported metrics between its own versions.

## Reading the numbers

A low StrongREJECT score on the no-jailbreak baseline indicates a model reliably refuses genuinely harmful requests; a low score after a jailbreak method is applied indicates that technique failed to extract useful harmful content, not just that the model's refusal wording changed. A single score does not indicate which categories of harm the model is more or less resistant to, since the six categories are typically aggregated. Because the metric depends on an LLM judge and on which jailbreak method (if any) was applied, scores are only comparable across models when the judge, jailbreak method and score scale (0-1 versus 0-5) are held constant.
