---
id: uccb
name: "Uganda Cultural and Cognitive Benchmark"
aliases: ["UCCB", "Ugandan Cultural and Cognitive Benchmark"]
page_kind: benchmark
category: domain
subcategory: "Ugandan cultural knowledge and open-ended reasoning"
status: active
summary: "UCCB contains 1,039 open-ended questions across 24 Ugandan cultural domains, scored by model-based grading."
measures: "UCCB asks open-ended questions about Uganda's culture, history, society and daily life across 24 domains."
task_format: "Open-ended English QA with Ugandan English and multilingual elements, graded against reference answers."
metric:
  name: "model-graded accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The inspect_evals README specifies model-graded QA and accuracy, but no random or human baseline."
dataset:
  size: 1039
  size_note: "The inspect_evals README states 1,039 samples across 24 cultural domains."
  url: "https://huggingface.co/datasets/CraneAILabs/UCCB"
  license: "CC BY-NC-SA 4.0"
  languages: [en, lg, nyn, ach, teo]
  modalities: [text]
  splits: "single 1,039-sample set; no train/test split stated"
  public_test_set: true
publisher:
  org: "Crane AI Labs and UCCB authors"
  authors: ["Lwanga Caleb", "Gimei Alex", "Kavuma Lameck", "Kato Steven Mubiru", "Roland Ganafa", "Sibomana Glorry", "Atuhaire Collins", "JohnRoy Nangeso", "Bronson Bakunga"]
  url: "https://huggingface.co/datasets/CraneAILabs/UCCB"
paper: {title: "The Ugandan Cultural Context Benchmark (UCCB) Suite", arxiv: "", url: "https://huggingface.co/datasets/CraneAILabs/UCCB", year: 2025}
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals"
released: "2025"
last_updated: "2026-08"
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: "No current ceiling was established."}
contamination: {risk: high, note: "Questions and reference answers are public; no held-out or rotating policy is described."}
harness: {lm_eval: "", inspect_evals: "uccb", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [inspect-evals, uganda, cultural-knowledge, open-ended]
sources:
  - {url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/uccb/README.md", title: "inspect_evals UCCB README", accessed: "2026-09-09"}
  - {url: "https://huggingface.co/datasets/CraneAILabs/UCCB", title: "CraneAILabs UCCB dataset", accessed: "2026-09-09"}
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-new-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-003"}
---

## What it measures

UCCB evaluates open-ended answers about Ugandan cultural knowledge and reasoning. Its domains include education, herbs, media, economy, notable people, literature, architecture, folklore, language, religion, values and sports.

Questions use English with Ugandan English and multilingual elements. A strong result indicates familiarity with the represented contexts and references. It is not a general measure of reasoning or cultural competence outside the sampled domains.

## How it is scored

The inspect_evals task uses model-graded QA. Its README names GPT-4o-mini as the default scorer and says the grader considers factual accuracy, cultural understanding, key information coverage and cultural context. The reported metric is accuracy with standard error.

The README warns that its historical result table came from another pipeline, not inspect-native runs. Inspect versions matter because the changelog describes a 2026 correction to judge verdict extraction.

## Dataset and licence

The task identifies 1,039 samples across 24 domains and does not state train, validation or test splits. Questions and reference answers are public. The published licence is CC BY-NC-SA 4.0.

Domains are unequal. Use released metadata for domain analysis instead of assuming equal weighting.

The Hugging Face dataset card tags six language codes: en, ug, lg, nyn, ach, teo. lg, nyn, ach and teo match Luganda, Runyankole, Acholi and Ateso; the "ug" tag collides with the ISO code for Uyghur and its intended meaning here is not established, so it is left out of the structured language list.

## Who publishes it

The inspect_evals integration is maintained by the UK Government BEIS project. The dataset credits Lwanga Caleb, Gimei Alex, Kavuma Lameck, Kato Steven Mubiru, Roland Ganafa, Sibomana Glorry, Atuhaire Collins, JohnRoy Nangeso and Bronson Bakunga. The citation calls it the Ugandan Cultural Context Benchmark Suite and dates it 2025.

No separate leaderboard was established. Report scorer model and inspect_evals version.

## Lineage

UCCB is a standalone Uganda-focused cultural benchmark. It is not a translation subset of MMLU, BIG-bench or another general family. No predecessor or successor was established.

## Saturation and contamination

The full question set and reference answers are public, creating high contamination risk. No private test, refresh cycle or contamination study is described. Saturation is unknown.

## How to run it

Run inspect eval inspect_evals/uccb. The task supports limit, cot, max_tokens, scorer_model and shuffling parameters. Record scorer, inspect_ai version and any limit or shuffle setting.

## Reading the numbers

High model-graded accuracy means the answer matched the judge's expectations for sampled Ugandan questions. It also reflects reference answers and the judge's assumptions. It does not establish broad cultural understanding or factual reliability outside Uganda. Separate inspect-native accuracy from the README's external table.

