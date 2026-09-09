---
id: xwinograd
name: XWinograd
aliases: []
page_kind: benchmark
category: reasoning
subcategory: multilingual commonsense coreference resolution
status: active
summary: XWinograd is a multilingual Winograd Schema Challenge covering English, French, Japanese, Portuguese, Russian and Chinese.
measures: XWinograd tests commonsense pronoun/coreference resolution across six languages. Each item is a sentence with an ambiguous pronoun and two candidate referents, and the model must pick the referent that world knowledge and context make correct, resolving the same kind of ambiguity the original English Winograd Schema Challenge was built to test.
task_format: Binary choice; given a sentence with an ambiguous pronoun, pick which of two candidate referents it refers to.
metric: {name: accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 50, human_baseline: null, baseline_note: "Two-way forced choice per item, so random guessing scores 50%; per-language item counts are unequal, so a simple cross-language average weights languages unevenly."}
dataset: {size: 4449, size_note: "6 languages combined into one corpus: English 2,325, Japanese 959, Chinese 504, Russian 315, Portuguese 263, French 83 examples.", url: "https://github.com/yandex-research/crosslingual_winograd", license: "", languages: [en, fr, ja, pt, ru, zh], modalities: [text], splits: "Single evaluation set per language; no official train split", public_test_set: true}
publisher: {org: "Yandex Research", authors: ["Alexey Tikhonov", "Max Ryabinin"], url: "https://github.com/yandex-research/crosslingual_winograd"}
paper: {title: "It's All in the Heads: Using Attention Heads as a Baseline for Cross-Lingual Transfer in Commonsense Reasoning", arxiv: "2106.12066", url: "https://arxiv.org/abs/2106.12066", year: 2021}
leaderboard_url: ""
repo_url: https://github.com/yandex-research/crosslingual_winograd
released: "2021"
last_updated: ""
lineage: {family: "", predecessor: "wsc273", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: ""}
contamination: {risk: medium, note: "The English subset draws on the long-public WSC, SuperGLUE and Definite Pronoun Resolution sources; the non-English subsets (including a Chinese set expanded via CLUEWSC2020) have been publicly available since 2020-2021, so training-data overlap is plausible for models released after that."}
harness: {lm_eval: xwinograd}
tags: [benchmark, multilingual, commonsense, coreference, reasoning]
sources:
  - url: https://arxiv.org/abs/2106.12066
    title: "It's All in the Heads: Using Attention Heads as a Baseline for Cross-Lingual Transfer in Commonsense Reasoning"
    accessed: "2026-09-08"
  - url: https://github.com/yandex-research/crosslingual_winograd
    title: XWinograd (crosslingual_winograd) official repository
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Muennighoff/xwinograd
    title: XWinograd dataset card (Hugging Face)
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/xwinograd/README.md
    title: lm-evaluation-harness xwinograd task README
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-002 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-002"}
---
## What it measures

XWinograd tests commonsense pronoun and coreference resolution across six languages: English, French, Japanese, Portuguese, Russian and Chinese. Each item is a sentence containing an ambiguous pronoun and two candidate referents; the model must pick the referent that context and everyday world knowledge make correct, the same kind of disambiguation the original English Winograd Schema Challenge was designed around. Unlike Winogrande, XWinograd is not itself designed to be adversarially de-biased against surface statistical cues; it is built to test whether commonsense coreference ability generalizes across languages.

## How it is scored

Each item is a two-way forced choice between two candidate referents, so a model guessing at random scores roughly 50% accuracy per language. Scoring is typically done by comparing the model's likelihood for the sentence completed with each candidate and selecting the higher-scoring one, the same likelihood-comparison protocol used for the original English Winograd Schema Challenge, rather than free-text generation.

## Dataset and licence

XWinograd combines six per-language collections into one corpus, with unequal sizes: English 2,325 examples, Japanese 959, Chinese 504, Russian 315, Portuguese 263 and French 83. The English subset draws on the original WSC, SuperGLUE, and Definite Pronoun Resolution data; the Chinese subset was expanded from an initial 16 items to 504 using additional schemas from the CLUEWSC2020 dataset; sourcing details for the remaining languages were not confirmed beyond the paper's statement that they were "processed from several datasets from prior work within a standardized pipeline." Because the corpus aggregates data from multiple upstream sources with their own licences, and no single licence is stated for the combined release, the licence field here is left empty rather than guessed; the code repository itself is Apache-2.0.

## Who publishes it

XWinograd was introduced by Alexey Tikhonov and Max Ryabinin of Yandex Research in "It's All in the Heads: Using Attention Heads as a Baseline for Cross-Lingual Transfer in Commonsense Reasoning" (Findings of ACL-IJCNLP 2021; arXiv:2106.12066). The dataset and code are maintained at github.com/yandex-research/crosslingual_winograd, and it is commonly redistributed via Hugging Face.

## Lineage

XWinograd's English subset is built directly from the original Winograd Schema Challenge material also used by `wsc273`, plus items from SuperGLUE and Definite Pronoun Resolution; it is not a translation of Winogrande, which is a separate, later, adversarially-crowdsourced expansion of the same underlying WSC concept. No successor benchmark under a different id was established from the sources reviewed here; related multilingual coreference/commonsense sets such as XCOPA test related but distinct skills rather than being XWinograd variants.

## Saturation and contamination

No saturation study was reviewed here, so status is unknown. Contamination risk is medium: the English subset's sources (WSC, SuperGLUE, DPR) have been public for years, and the non-English subsets, including the CLUEWSC2020-expanded Chinese set, have circulated since 2020-2021, making training-data overlap plausible for models trained on broad web or benchmark-aggregation corpora since then.

## How to run it

lm-evaluation-harness implements XWinograd as an `xwinograd` group with one subtask per language: `xwinograd_en`, `xwinograd_fr`, `xwinograd_jp`, `xwinograd_pt`, `xwinograd_ru`, `xwinograd_zh`. Because per-language item counts are small and uneven (as few as 83 for French), single-language scores can be noisy; check whether a reported number is a per-language score or an item-weighted average across all six before comparing it to another report.

## Reading the numbers

A high XWinograd score indicates a model can resolve everyday pronoun ambiguity using world knowledge, in the target language, at better-than-chance rates. Because several per-language subsets are small, a single strong or weak score on French (83 items) or Portuguese (263 items) carries much less statistical weight than the same score on English (2,325 items); prefer aggregate or item-weighted comparisons over single small-language scores. Given the mixed and partly older provenance of the underlying schemas, treat very high English scores with some caution given plausible contamination.
