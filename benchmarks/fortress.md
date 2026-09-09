---
id: fortress
name: FORTRESS
aliases:
  - "Frontier Risk Evaluation for National Security and Public Safety"
  - "ScaleAI/fortress_public"
page_kind: benchmark
category: safety
subcategory: "national security and public safety (NSPS) adversarial prompts with paired over-refusal checks"
status: active
summary: "500 public NSPS adversarial prompts with instance rubrics, scored as average risk (ARS) plus over-refusal (ORS) on 500 paired benign prompts."
measures: >
  FORTRESS tests whether a model's refusal layer holds up on unclassified national-security
  and public-safety requests, and whether that layer also refuses harmless twins of the
  same topics. The public set has 500 expert-written single-turn adversarial prompts across
  three domains — Chemical, Biological, Radiological, Nuclear and Explosive (CBRNE);
  Political Violence and Terrorism; and Criminal and Financial Illicit Activities — and ten
  subcategories. Each adversarial prompt has a 4–7 question binary rubric and a benign
  counterpart. English text only. Inspect Evals loads the Hugging Face public split
  (ScaleAI/fortress_public, 500 train rows) and does not ship the authors' private hold-out.
task_format: >
  Single-turn generation. fortress_adversarial feeds the adversarial prompt and grades the
  reply with a three-model rubric panel. fortress_benign feeds the paired benign prompt and
  asks one judge whether the model refused. Domain and subdomain filters are optional.
metric:
  name: "average risk score (ARS) on adversarial prompts; over-refusal score (ORS) on benign prompts"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower ARS and lower ORS are both better. ARS is the dataset mean of per-prompt harm
    scores: for each adversarial reply, three judges (paper and Inspect default: o3,
    Claude 3.7 Sonnet, Gemini 2.5 Pro) answer the rubric's 4–7 yes/no questions, a
    majority vote is taken per question, and the share of yes votes is the harm score.
    ORS is the share of benign prompts refused, judged by GPT-4o-mini in both the paper
    and Inspect. Among 26 models on the public set (paper, May 2024–April 2025 releases),
    Claude 3.5 Sonnet had the lowest ARS at 14.09 and the highest ORS at 21.80; DeepSeek-R1
    had the highest ARS at 78.05 and the lowest ORS at 0.06. Mean ARS was 42.35 and mean
    ORS 4.32. No random-guess baseline applies.
dataset:
  size: 500
  size_note: >
    Hugging Face train split has 500 examples (confirmed from the dataset card and
    dataset_info). Each row holds one adversarial prompt, one benign prompt, one rubric,
    and domain labels, so the public evaluation is 500 adversarial plus 500 benign
    judgements. Inspect README domain counts: CBRNE 180, Political Violence & Terrorism
    132, Criminal & Financial Illicit Activities 188. Subdomain counts: Chemical 37,
    Biological 30, Radiological and Nuclear (WMD) 47, Explosives 65, Terrorism 87,
    Political Violence 31, Illegal Weapons 9, Coordination of Illicit Activities 80,
    Fraud 67, Privacy/Scams 30. Some rows mix domain and subdomain labels relative to
    the paper table; Inspect documents that mismatch. The authors also keep a private
    set, not in this release. Inspect pins revision 0c096becbc75bb12065c8059a53960c7f0d4d35c.
  url: "https://huggingface.co/datasets/ScaleAI/fortress_public"
  license: "CC-BY-4.0 (Hugging Face card); Inspect Evals harness MIT"
  languages:
    - en
  modalities:
    - text
  splits: "public train split of 500 rows (adversarial + benign + rubric per row); private hold-out not released"
  public_test_set: true
publisher:
  org: "Scale AI (SEAL Research Team and Scale Red Team)"
  authors:
    - "Christina Q. Knight"
    - "Kaustubh Deshpande"
    - "Ved Sirdeshmukh"
    - "Meher Mankikar"
    - "Scale Red Team"
    - "SEAL Research Team"
    - "Julian Michael"
  url: "https://huggingface.co/datasets/ScaleAI/fortress_public"
paper:
  title: "FORTRESS: Frontier Risk Evaluation for National Security and Public Safety"
  arxiv: "2506.14922"
  url: "https://arxiv.org/abs/2506.14922"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/fortress"
released: "2025-06"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 14.09
  as_of: "2025-06"
  note: >
    Best public-set ARS in the paper is Claude 3.5 Sonnet at 14.09 (lower is better),
    still well above zero. DeepSeek-R1 sits at 78.05 ARS. Inspect's own gpt-4.1-mini
    check on Political Violence & Terrorism (2025-09-14) reported ARS 58.5 ± 3.6 versus
    the paper's 59.40 on that domain. No 2026 full-set leaderboard was found.
contamination:
  risk: medium
  note: >
    The 500-row public set has been on Hugging Face since 17 June 2025 under CC-BY-4.0.
    The card forbids using it for adversarial training. The paper keeps a private set
    for later evaluation. Single-turn prompts are easy to scrape once public.
harness:
  lm_eval: ""
  inspect_evals: "fortress_adversarial, fortress_benign"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Extra inspect-evals[fortress]. There is no task named inspect_evals/fortress.
    Default adversarial judges: openai/o3, anthropic/claude-3-7-sonnet-20250219,
    google/gemini-2.5-pro. Default benign judge: openai/gpt-4o-mini. Inspect version 3-A
    (2026-08-21) fixed lower-case GRADE strings being counted as all-no, and changed
    unparseable benign grades from INCORRECT to unscored.
tags:
  - safety
  - nsps
  - cbrne
  - over-refusal
  - rubric
  - inspect-evals
sources:
  - url: "https://arxiv.org/abs/2506.14922"
    title: "FORTRESS: Frontier Risk Evaluation for National Security and Public Safety (arXiv:2506.14922)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.14922"
    title: "FORTRESS paper HTML (ARS/ORS definitions, 500 public prompts, 26-model table)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ScaleAI/fortress_public"
    title: "ScaleAI/fortress_public dataset card (CC-BY-4.0, 500 train rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ScaleAI/fortress_public"
    title: "Hugging Face dataset API (created 2025-06-17, revision 0c096bec, license cc-by-4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/fortress/README.md"
    title: "Inspect Evals FORTRESS README (task names, domain counts, changelog 3-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/fortress/eval.yaml"
    title: "Inspect eval.yaml (fortress_adversarial and fortress_benign, 500 samples each)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/fortress/data.py"
    title: "Inspect data.py (HF path and pinned revision)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-044 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-044"
---

## What it measures

FORTRESS asks whether a chat model will give useful help on a harmful national-security request, and whether the same model refuses a nearby benign request. Prompts are English, single-turn, and written by Scale red teamers. They cover CBRNE, political violence and terrorism, and criminal or financial crime, with ten subcategories. Each adversarial item ships a short rubric of binary questions rather than a single "did it jailbreak" label.

The public Hugging Face split is the set Inspect runs. Scale also keeps a private set that this page does not treat as scored. The card says the data is for safety evaluation only.

## How it is scored

ARS averages per-prompt harm. Three judges vote yes or no on each rubric line; majority yes counts as harmful; ties in Inspect default to yes. The paper reports ARS on a 0–100 scale, lower better. ORS is the fraction of benign prompts refused, judged by GPT-4o-mini, also lower better. Inspect task `fortress_adversarial` emits ARS; `fortress_benign` emits ORS. If all three adversarial judges abstain, Inspect drops the sample as INVALID.

Judge prompts are not in the paper. Inspect implements them in `scorer.py`. Version 3-A (2026-08-21) stopped treating lower-case `GRADE: yny` as all-no. Compare numbers only after that pin if you use Inspect.

## Dataset and licence

Five hundred public rows, one adversarial prompt, one benign prompt, and one rubric each. Hugging Face licence is CC-BY-4.0. Inspect's code is MIT. Illegal Weapons has only nine prompts, so a single judge failure moves ORS a lot. Domain/subdomain labels sometimes disagree with the paper's mapping table.

## Who publishes it

Scale AI, first author Christina Q. Knight, with the Scale Red Team and SEAL Research Team. arXiv v1 17 June 2025, v2 24 June 2025, submitted to NeurIPS. Hugging Face dataset created 17 June 2025. Inspect port by contributor jeqcho; current metadata version 3-A.

## Lineage

FORTRESS is not [harm_bench](harm_bench.md). It pairs each attack with a benign twin and uses instance rubrics instead of a fixed harm taxonomy. The paper positions it against AIR-Bench, HarmBench, and over-refusal sets such as XSTest and OR-Bench. No successor id is in this repository.

## Saturation and contamination

Claude 3.5 Sonnet's 14.09 ARS is the best public-set figure in the paper, not a floor of zero, so the suite still separates models. The public prompts have been easy to scrape since June 2025. Treat public-set scores as contaminated for any model trained after that date unless the publisher's private set is used.

## How to run it

`uv sync --extra fortress`, then `uv run inspect eval inspect_evals/fortress_adversarial` and `inspect_evals/fortress_benign`. Optional `-T risk_domain=...` or `-T risk_subdomain=...`. Paper decoding used temperature 0.7 (1.0 for reasoning models). Do not compare an Inspect ARS to a paper ARS until judge models, temperature, and the 3-A grade-case fix match.

## Reading the numbers

A low ARS means the model stayed inside the rubric on these 500 attacks, not that it is safe in multi-turn or tool-using settings. A low ORS means it answered the benign twins; Claude 3.5 Sonnet shows the trade-off (lowest ARS, highest ORS). Report ARS and ORS together. Private-set scores, when Scale publishes them, are the contamination check.
