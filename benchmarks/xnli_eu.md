---
id: xnli_eu
name: "XNLIeu"
aliases:
  - "xnli-eu"
  - "HiTZ/xnli-eu"
  - "XNLIeu"
page_kind: benchmark
category: reasoning
subcategory: "Basque three-way NLI (postedited MT, raw MT, and native test)"
status: active
summary: "Basque XNLI: postedited and machine-translated English XNLI plus a 621-item native Basque test set, scored as three-way NLI accuracy."
measures: >
  XNLIeu extends [XNLI](xnli.md) to Basque. The model still classifies a
  premise–hypothesis pair as entailment, contradiction or neutral, but the
  text is Basque. The authors first machine-translated English XNLI, then
  professionally post-edited that MT, and also built a smaller native Basque
  test set from scratch so they could check whether MT artefacts change which
  transfer recipe looks best.
task_format: >
  Three-way classification. lm-evaluation-harness uses the same cloze as XNLI:
  premise + ", ezta? {Bai|Gainera|Ez}, " + hypothesis, scored by multiple-choice
  log-likelihood. Three runnable tasks: `xnli_eu` (postedited, Hugging Face
  config `eu`), `xnli_eu_mt` (raw MT, `eu_mt`), `xnli_eu_native` (native test
  only, `eu_native`).
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three labels, so uniform chance is 33.3%. No pooled human-accuracy ceiling
    was confirmed from the sources opened here. The paper's claim is that
    post-edition changes measured transfer, not a human scoreboard.
dataset:
  size: 5010
  size_note: >
    Hugging Face `HiTZ/xnli-eu` and the dataset card: postedited `eu` and raw
    `eu_mt` each have 392,702 train / 2,490 validation / 5,010 test (the train
    file is the MT train in both configs). Native `eu_native` is test-only,
    621 pairs. The headline `xnli_eu` harness task evaluates the postedited
    5,010-item test split. The paper scraped 5,000 Basque news sentences, kept
    207 as premises, and wrote three hypotheses each (621 pairs). 621 is the
    released native test count, not 5,000. The card's pretty_name is
    "EuskañolDS"; the paper name is XNLIeu.
  url: "https://huggingface.co/datasets/HiTZ/xnli-eu"
  license: "CC BY-NC 4.0"
  languages:
    - eu
  modalities:
    - text
  splits: "eu and eu_mt: train / validation / test; eu_native: test only (621)"
  public_test_set: true
publisher:
  org: "HiTZ Center - IXA, University of the Basque Country (UPV/EHU)"
  authors:
    - "Maite Heredia"
    - "Julen Etxaniz"
    - "Muitze Zulaika"
    - "Xabier Saralegi"
    - "Jeremy Barnes"
    - "Aitor Soroa"
  url: "https://github.com/hitz-zentroa/xnli-eu"
paper:
  title: "XNLIeu: a dataset for cross-lingual NLI in Basque"
  arxiv: "2404.06996"
  url: "https://arxiv.org/abs/2404.06996"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/hitz-zentroa/xnli-eu"
released: "2024-04"
last_updated: ""
lineage:
  family: ""
  predecessor: xnli
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dedicated current leaderboard top score was confirmed. The paper
    compares post-edition versus raw MT and translate-train versus zero-shot
    on mono- and multilingual models rather than ranking frontier LLMs.
contamination:
  risk: high
  note: >
    Postedited and MT test labels are public on Hugging Face and GitHub. The
    postedited set is a translation of public [XNLI](xnli.md). The native 621
    is also released with labels. No private hold-out is described.
harness:
  lm_eval: "xnli_eu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Also `xnli_eu_mt` and `xnli_eu_native`. Dataset `HiTZ/xnli-eu`. Unlike
    the original `xnli` group, `xnli_eu.yaml` sets test_split: test (5,010
    rows). BasqueBench in this repository includes XNLIeu as one constituent
    of a larger Basque suite; that aggregate is not this page.
tags:
  - nli
  - basque
  - cross-lingual
  - entailment
  - classification
sources:
  - url: "https://arxiv.org/abs/2404.06996"
    title: "XNLIeu: a dataset for cross-lingual NLI in Basque (arXiv:2404.06996)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2404.06996"
    title: "XNLIeu paper HTML (post-edition, native test, 5,000 news-sentence pool)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2024.naacl-long.234/"
    title: "NAACL 2024 XNLIeu anthology page"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hitz-zentroa/xnli-eu/main/README.md"
    title: "hitz-zentroa/xnli-eu README (licence follows XNLI, three splits)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/xnli-eu/raw/main/README.md"
    title: "HiTZ/xnli-eu card (CC BY-NC 4.0, split table 5010 / 621)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HiTZ/xnli-eu"
    title: "HiTZ/xnli-eu datasets-server sizes"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli_eu/README.md"
    title: "lm-eval xnli_eu README (three tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/xnli_eu/xnli_eu.yaml"
    title: "lm-eval xnli_eu.yaml (HiTZ/xnli-eu, test split, Basque cloze)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-016 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-016"
---

## What it measures

XNLIeu is three-way natural language inference in Basque. The model reads a Basque premise and hypothesis and chooses entailment, contradiction or neutral. The authors started from English [XNLI](xnli.md), machine-translated it, then had professionals post-edit the MT. They also wrote a native Basque test set from Basque news premises and speaker-written hypotheses, so they could see whether translation artefacts change which transfer method looks best.

The Hugging Face card's `pretty_name` field says "EuskañolDS"; that is not the paper's name. This page documents XNLIeu.

## How it is scored

Each pair is a three-way class, so chance is 33.3%. lm-evaluation-harness uses a Basque cloze — premise + ", ezta? Bai/Gainera/Ez, " + hypothesis — and scores accuracy from sequence likelihood, matching the original XNLI harness recipe. Three task ids exist. `xnli_eu` is the postedited test (5,010 items). `xnli_eu_mt` is the raw MT test. `xnli_eu_native` is the 621-item native test. Unlike the original `xnli` group, these YAMLs set `test_split: test`.

The paper's own tables compare fine-tuned translate-train, zero-shot and typology setups as well as decoder prompting. Those protocols are not interchangeable with the harness cloze.

## Dataset and licence

Postedited `eu` and raw `eu_mt` each list 392,702 train, 2,490 validation and 5,010 test on Hugging Face; both configs reuse the MT train file. Native `eu_native` is 621 test pairs only. The paper scraped 5,000 Basque news sentences, kept 207 premises, and wrote three hypotheses per premise. Labels are public.

The GitHub README says the data follows the same licence as XNLI. The Hugging Face card tags CC BY-NC 4.0, matching the XNLI GitHub LICENSE.

## Who publishes it

Maite Heredia, Julen Etxaniz, Muitze Zulaika, Xabier Saralegi, Jeremy Barnes and Aitor Soroa, at the HiTZ Center / IXA, University of the Basque Country. Posted as arXiv:2404.06996 on 10 April 2024 and published at NAACL 2024 (long papers). Code and data: github.com/hitz-zentroa/xnli-eu.

## Lineage

Predecessor: [xnli](xnli.md), the 15-language 2018 eval this work extends. [basque_bench](basque_bench.md) includes XNLIeu as one Basque NLU constituent; a BasqueBench average is not an XNLIeu score. Do not treat `xnli_eu` as a sixteenth language inside the original `xnli` group.

## Saturation and contamination

No current leaderboard ceiling was confirmed. The paper's result is that post-edition matters and that translate-train usually beats zero-shot, with a smaller gap on the native test. Contamination risk is high: postedited, MT and native labels are public, and the postedited set is a translation of already-public XNLI.

## How to run it

lm-eval: `xnli_eu`, `xnli_eu_mt`, or `xnli_eu_native` on `HiTZ/xnli-eu`. Default postedited eval is the 5,010-item test split. OpenCompass, inspect_evals, HELM and BIG-bench implementations were not found at the paths checked.

Name which of the three configs was used. Postedited and raw-MT accuracy are not the same number.

## Reading the numbers

A high postedited `xnli_eu` score means the model can do three-way Basque NLI on professionally cleaned translations of English XNLI. It does not by itself prove the model handles natively written Basque news inference; that is the 621-item native split, where the paper found smaller gains from translate-train. Do not mix this id with original `xnli` language tasks or with the [basque_bench](basque_bench.md) aggregate.
