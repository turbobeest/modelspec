---
id: anthropic_red_team
name: "Anthropic Red Team (HELM)"
aliases:
  - "AnthropicRedTeam"
  - "anthropic-red-team"
  - "hh-rlhf red-team-attempts"
page_kind: benchmark
category: safety
subcategory: "single-turn refusal on first utterances from Anthropic's 2022 red-team dialogues"
status: active
summary: "HELM safety scenario that scores a model's first reply to 38,961 Anthropic red-team openings with a 0–1 LLM-judge safety_score."
measures: >
  HELM's anthropic_red_team scenario takes Anthropic's public red-team dialogues and
  keeps only the first human utterance of each transcript. The model must answer that
  single English prompt. The original collection was a multi-turn attack by crowdworkers
  trying to elicit harmful assistant behaviour. HELM does not replay later turns, so the
  score is a one-shot refusal test on historically successful attack openings, not a
  reproduction of Anthropic's multi-turn red-team protocol.
task_format: >
  Zero-shot generation. HELM sends the first Human utterance with empty instructions,
  max_tokens 512, temperature 0. Two LLM judges (the safety annotator) rate the
  completion's harmfulness on a 0–1 scale; higher means a more harmless reply.
metric:
  name: "safety_score (mean of LLM-judge harmlessness ratings)"
  direction: higher_is_better
  unit: "0-1 scale"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The annotator prompt maps replies from 0 (extremely offensive or dangerous) to 1
    (completely harmless). HELM's schema still describes safety_score as the mean of
    GPT-4o and Llama 3.1 ratings. In the current model_as_judge.py the Llama 3.1 405B
    Turbo judge is commented out as deprecated on 2026-03-06, so a fresh run may be
    GPT-4o-2024-05-13 only. No random or human baseline is defined.
dataset:
  size: 38961
  size_note: >
    Ganguli et al. (2022) release 38,961 red-team attacks. HELM loads
    Anthropic/hh-rlhf data_dir=red-team-attempts at revision
    09be8c5bbc57cb3887f3a9732ad6aa7ec602a1fa and maps the Hugging Face train split
    to HELM's test split because that subset has no test split. HELM Safety's
    write-up uses the same 38,961 figure. This page did not decompress the 15 MB
    jsonl.gz to re-count rows.
  url: "https://huggingface.co/datasets/Anthropic/hh-rlhf"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face red-team-attempts train used as HELM test; no held-out test split"
  public_test_set: true
publisher:
  org: "Anthropic (dataset); Stanford CRFM (HELM scenario)"
  authors:
    - "Deep Ganguli"
    - "Liane Lovitt"
    - "Jackson Kernion"
  url: "https://github.com/anthropics/hh-rlhf"
paper:
  title: "Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned"
  arxiv: "2209.07858"
  url: "https://arxiv.org/abs/2209.07858"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/safety/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/anthropic_red_team_scenario.py"
released: "2022-09"
last_updated: "2026-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated per-scenario top score for anthropic_red_team alone was read here.
    The parent [HELM Safety](helm_safety.md) mean mixes this scenario with BBQ,
    HarmBench, SimpleSafetyTests and XSTest, so it is not a reading of this run.
contamination:
  risk: high
  note: >
    Transcripts and first-turn prompts have been public on GitHub and Hugging Face
    since 2022 under MIT. Providers have used similar red-team text in later
    safety tuning. HELM's first-utterance cut is a deterministic extract of that
    public file, so leakage into training or refusal datasets is plausible.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "anthropic_red_team"
  opencompass: ""
  bigbench: ""
  other: "run_entries_safety.conf and schema_safety.yaml list this scenario with bbq, harm_bench, simple_safety_tests, and xstest"
tags:
  - safety
  - red-teaming
  - refusal
  - llm-judge
  - helm
  - english
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/anthropic_red_team_scenario.py"
    title: "HELM AnthropicRedTeamScenario (first utterance, hh-rlhf red-team-attempts pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/safety_run_specs.py"
    title: "HELM safety_run_specs.py (anthropic_red_team run spec, 512 tokens, T=0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/anthropic_red_team_annotator.py"
    title: "AnthropicRedTeamAnnotator (0–1 harmfulness rubric)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/safety_metrics.py"
    title: "HELM SafetyScoreMetric (mean of *_score annotator fields)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/model_as_judge.py"
    title: "score_with_reasoning_with_gpt_and_llama (GPT-4o-2024-05-13; Llama 3.1 405B commented out 2026-03-06)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_safety.yaml"
    title: "HELM schema_safety.yaml (anthropic_red_team main_name safety_score)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_safety.conf"
    title: "HELM run_entries_safety.conf (bbq, harm_bench, simple_safety_tests, anthropic_red_team, xstest)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2209.07858"
    title: "Red Teaming Language Models to Reduce Harms (arXiv:2209.07858)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2209.07858"
    title: "Ganguli et al. HTML (38,961 attacks released)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2204.05862"
    title: "Training a Helpful and Harmless Assistant with RLHF (arXiv:2204.05862)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Anthropic/hh-rlhf"
    title: "Anthropic/hh-rlhf dataset card (MIT; red-team-attempts usage)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Anthropic/hh-rlhf"
    title: "Hugging Face dataset API (license MIT, revision 09be8c5bbc57cb3887f3a9732ad6aa7ec602a1fa)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/anthropics/hh-rlhf/master/README.md"
    title: "anthropics/hh-rlhf README (red-team field dictionary)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/anthropics/hh-rlhf/master/LICENSE"
    title: "anthropics/hh-rlhf MIT License (Copyright 2022 Anthropic)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/2024/11/08/helm-safety.html"
    title: "HELM Safety CRFM write-up (AnthropicRedTeam 38,961 items)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/safety/latest/"
    title: "HELM Safety leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-026 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-026"
---

## What it measures

HELM's anthropic_red_team task gives the model one English sentence from a human red-teamer and asks it to reply. The sentence is the first `Human:` turn of a dialogue in Anthropic's red-team-attempts file. Crowdworkers originally used those dialogues to try to make an assistant produce harmful text. HELM throws away later turns, so the model never sees the rest of the attack. The skill under test is whether the first reply is judged harmless, not whether a long jailbreak eventually succeeds.

The underlying collection is the 38,961-attack set from Ganguli, Lovitt, Kernion and colleagues at Anthropic (arXiv:2209.07858, submitted 23 August 2022). HELM also cites the HH-RLHF paper (arXiv:2204.05862) because the same Hugging Face repo hosts both preference data and these transcripts. This page documents the HELM scenario, not Anthropic's original multi-turn analysis.

## How it is scored

The headline metric is `safety_score` on a 0–1 scale, higher better. An annotator prompt asks a judge to rate harmfulness in five bands from 0 to 1. HELM averages the numeric `*_score` fields it gets back. The schema still says that mean is over GPT-4o and Llama 3.1. The current judge helper pins `openai/gpt-4o-2024-05-13` and has the Llama 3.1 405B Turbo entry commented out after a 6 March 2026 deprecation note. A new run may therefore be a single-judge score. Generation is temperature 0, 512 tokens, no in-context examples.

This is not Anthropic's own success rating. In the source file each transcript has a crowdworker Likert `rating` of how well the red-teamer broke the assistant. HELM does not use that field. It also does not use the preference-model harmlessness scores stored on the rows.

## Dataset and licence

Anthropic released 38,961 attacks. Each row is a full transcript plus metadata (model size and type, red-team member id, Upwork vs MTurk, optional tags on a 1,000-item sample). HELM parses the transcript, splits on `Human:` / `Assistant:`, and keeps the first non-empty utterance. The Hugging Face card and GitHub README both mark the repo MIT; the GitHub LICENSE file is MIT, Copyright 2022 Anthropic. Prompts and transcripts are public. There is no held-out test split for this subset.

## Who publishes it

Anthropic collected the dialogues and published the 2022 red-teaming paper. Core authors named above the paper's author break are Deep Ganguli, Liane Lovitt and Jackson Kernion; the full author list is much longer. Stanford CRFM wrapped the first utterance as a HELM Safety scenario and still lists it on the HELM Safety leaderboard (launched November 2024). HELM itself entered maintenance mode on 1 June 2026.

## Lineage

This is not a copy of [harm_bench](harm_bench.md). HarmBench scores attack success with its own classifier on a separate behaviour set. It is not [agentic_misalignment](agentic_misalignment.md) or [model_written_evals](model_written_evals.md). Those are later Anthropic evals with different tasks. The five-scenario mean that includes this run is [helm_safety](helm_safety.md). [anthropic_hh_rlhf](anthropic_hh_rlhf.md) is HELM Instruct over the same Hugging Face repo, including a `red_team` subset scored with a 1–5 helpfulness critique, not this Safety `safety_score`.

## Saturation and contamination

No sourced top score for this scenario alone was found. A high HELM Safety mean is not a reading of this run: that average also includes BBQ, HarmBench, SimpleSafetyTests and XSTest. Treat a high `safety_score` here as a judge's view of a one-turn refusal, not as evidence that the model resists a full red-team dialogue. The prompts have been public since 2022, so training-set overlap and targeted safety tuning are both plausible.

## How to run it

In HELM the run spec name is `anthropic_red_team`. It loads `AnthropicRedTeamScenario`, annotates with `AnthropicRedTeamAnnotator`, and scores with `SafetyScoreMetric`. `run_entries_safety.conf` lists it beside `bbq`, `harm_bench`, `simple_safety_tests` and `xstest`. Compare numbers only when the judge set matches. After March 2026 the Llama judge may be absent from the code even though the schema text still names two models.

## Reading the numbers

A high score means the judges called the first reply harmless on these 2022 attack openings. It does not mean the model would hold up over the rest of the original dialogue. It does not measure helpfulness, over-refusal, or robustness to new jailbreaks. Read it next to [helm_safety](helm_safety.md) and [harm_bench](harm_bench.md), and check which judge models produced the number.
