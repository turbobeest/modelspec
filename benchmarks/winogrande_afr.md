---
id: winogrande_afr
name: Winogrande African Languages
aliases: []
page_kind: benchmark
category: knowledge
subcategory: reasoning
status: active
summary: HELM's winogrande_afr scenario evaluates commonsense pronoun resolution using Winogrande items translated into 11 low-resource African languages.
measures: HELM's winogrande_afr scenario evaluates commonsense pronoun resolution using Winogrande-style multiple-choice items translated into 11 low-resource African languages, not English.
task_format: Multiple-choice pronoun resolution; each item is a sentence with an ambiguous pronoun and two candidate referents, scored by exact match on the correct choice.
metric: {name: exact match, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 50, human_baseline: null, baseline_note: "Random baseline of 50% follows from the two-way choice format; not separately confirmed by the source."}
dataset: {size: null, size_note: "Winogrande items translated into 11 languages; the HELM scenario file does not state a per-language or total item count.", url: https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages, license: "", languages: [Afrikaans, Amharic, Bambara, Igbo, Sepedi, Shona, Sesotho, Setswana, Tsonga, Xhosa, Zulu], modalities: [text], splits: "train (dev), validation, test, loaded per language from CSV files", public_test_set: null}
publisher: {org: "Stanford CRFM (HELM integration); translations from the Bridging the Gap project", authors: [Tuka Alhanai, Adam Kasumovic, Mohammad Ghassemi, Aven Zitzelberger, Jessica Lundin, Guillaume Chabot-Couture], url: https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages}
paper: {title: "Bridging the Gap: Enhancing LLM Performance for Low-Resource African Languages with New Benchmarks, Fine-Tuning, and Cultural Adjustments", arxiv: "2412.12417", url: https://arxiv.org/abs/2412.12417, year: 2024}
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/winogrande_afr_scenario.py
released: "2024"
last_updated: ""
lineage: {family: "", predecessor: winogrande, successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: unknown, note: "The underlying Winogrande items are public and predate most model training cutoffs, but the 11-language translations are newer (2024) and their training-data exposure has not been studied."}
harness: {helm: winogrande_afr, lm_eval: "", inspect_evals: "", opencompass: "", bigbench: "", other: ""}
tags: [benchmark, multilingual, low-resource]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/winogrande_afr_scenario.py
    title: "Winogrande_Afr_Scenario source (HELM)"
    accessed: "2026-09-08"
  - url: https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages
    title: "Bridging the Gap: Low-Resource African Languages project repository"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2412.12417
    title: "Bridging the Gap: Enhancing LLM Performance for Low-Resource African Languages with New Benchmarks, Fine-Tuning, and Cultural Adjustments"
    accessed: "2026-09-08"
  - url: https://github.com/allenai/winogrande
    title: "WinoGrande source repository (original English benchmark)"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-001 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-001"}
---
## What it measures

`winogrande_afr` is a HELM scenario (`Winogrande_Afr_Scenario`, source name `winogrande_afr`) that translates items from Winogrande — a Winograd-schema-style, two-way pronoun-resolution task — into 11 low-resource African languages: Afrikaans, Amharic, Bambara, Igbo, Sepedi, Shona, Sesotho, Setswana, Tsonga, Xhosa and Zulu. Despite the page name inherited from earlier drafts, the task is not about English; each language is evaluated separately, and HELM registers a distinct scenario name per language (`winogrande_afr_af`, `winogrande_afr_am`, and so on).

Each item presents a sentence containing an ambiguous pronoun and two candidate referents that differ by one or two words; the model must pick the referent that world knowledge supports, the same task structure as the original English Winogrande.

## How it is scored

The scenario's own docstring identifies the primary metric as exact match, evaluated on the test split. Because each item is a two-way choice, chance performance is nominally 50%, though the source does not restate this baseline explicitly.

## Dataset and licence

Items originate from Winogrande (Sakaguchi et al., 2021) and were translated into the 11 listed languages by the Bridging the Gap project (Alhanai et al., 2024, arXiv:2412.12417), maintained in a GitHub repository by the Institute for Disease Modeling alongside translated MMLU-Clinical and Belebele sets. The HELM scenario loads three CSV splits per language: dev (used as train), val and test. The source repository ships a separate `LICENSE-Winogrande` file referencing the original Winogrande dataset's licence terms; the exact licence text was not read for this page, so it is left unstated. Total item counts per language are not given in the scenario file or its docstring.

## Who publishes it

Stanford CRFM's HELM project maintains the harness integration and scenario code. The translated dataset itself is a product of the Bridging the Gap project, authored by Tuka Alhanai, Adam Kasumovic, Mohammad Ghassemi, Aven Zitzelberger, Jessica Lundin and Guillaume Chabot-Couture (2024). No separate public leaderboard specific to `winogrande_afr` was found.

## Lineage

This is a translated variant of [WinoGrande](winogrande.md) (Sakaguchi et al., 2021), which is itself built on the original Winograd Schema Challenge format. It sits alongside sibling translations of MMLU-Clinical and Belebele produced by the same project, which are not benchmark pages in this repository. No successor to `winogrande_afr` was found.

## Saturation and contamination

No saturation data was found for this scenario. The original English Winogrande items are old enough to plausibly appear in training data, but the 11-language translations were only published in 2024, so their presence in any given model's training set has not been established and likely varies by language and by model.

## How to run it

Run the `winogrande_afr` scenario in HELM, specifying the `lang` parameter for one of the 11 supported language codes (e.g. `af`, `am`, `bm`, `ig`, `nso`, `sn`, `st`, `tn`, `ts`, `xh`, `zu` — exact codes should be confirmed against the scenario source before use). Scores are reported per language, not as a single aggregate, so comparisons should specify which language was run.

## Reading the numbers

A strong per-language score shows a model can resolve translated Winogrande-style pronoun ambiguities in that specific language, using items derived from human or machine translation rather than native-language authorship. It says little about the model's broader fluency or reasoning in that language, and scores across the 11 languages are not directly comparable to each other or to the original English WinoGrande without checking translation quality and item overlap. Because per-language item counts are unpublished here, small samples could make scores noisy; check the exact split sizes before treating a gap between models as meaningful.
