---
id: ruler
name: "RULER"
aliases: ["RULER: What's the Real Context Size of Your Long-Context Language Models?"]
page_kind: benchmark
category: long-context
subcategory: "synthetic long-context retrieval, tracing and aggregation"
status: active
summary: "A synthetic long-context suite of 13 tasks across four categories, built to show a model's effective context length is usually shorter than its claimed maximum."
measures: >
  RULER procedurally generates long documents at a chosen sequence length and asks a model to
  complete one of 13 synthetic tasks over them, grouped into four categories: retrieval
  (needle-in-a-haystack variants with different needle/haystack types and multiple needles or
  queries at once), multi-hop tracing (following chains of variable-binding across the document),
  aggregation (extracting the most or least frequent words from a long list), and question answering
  (real SQuAD or HotpotQA questions embedded in a padded-out long context). It goes beyond a plain
  needle-in-a-haystack test specifically because that simpler test can be solved with a single
  read-through; RULER's multi-hop and aggregation tasks require combining information scattered
  across the whole context, which single-pass retrieval cannot do.
task_format: "Long synthetic or padded-real-text document plus an instruction in; a short answer (a value, a word list, or an entity name) out, at a chosen target sequence length from 4K to 1M+ tokens."
metric:
  name: "accuracy, per task and averaged across all 13"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No fixed random or human baseline is established; RULER instead defines an "effective length"
    threshold per model, using a weaker reference model's (Llama-2-7B-chat) 4K-context accuracy
    (85.6%) as the bar a model must clear at a given length to count as reliably handling that
    length.
dataset:
  size: null
  size_note: >
    RULER has no fixed item count: it is a synthetic task generator (Paul Graham essays for the
    retrieval haystack, SQuAD and HotpotQA for the QA task, procedurally generated text for the
    rest) that produces new instances at whatever sequence length and task-complexity settings are
    requested. Community members have uploaded fixed, pre-generated instance sets to Hugging Face
    for convenience (for example simonjegou/ruler, over 7,500 downloads at last check), but none of
    these is the official released dataset.
  url: "https://github.com/NVIDIA/RULER"
  license: "Apache-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "generated on demand per task/length combination; no fixed train/test split"
  public_test_set: true
publisher:
  org: "NVIDIA"
  authors: ["Cheng-Ping Hsieh", "Simeng Sun", "Samuel Kriman", "Shantanu Acharya", "Dima Rekesh", "Fei Jia", "Yang Zhang", "Boris Ginsburg"]
  url: "https://github.com/NVIDIA/RULER"
paper:
  title: "RULER: What's the Real Context Size of Your Long-Context Language Models?"
  arxiv: "2404.06654"
  url: "https://arxiv.org/abs/2404.06654"
  year: 2024
leaderboard_url: "https://github.com/NVIDIA/RULER"
repo_url: "https://github.com/NVIDIA/RULER"
released: "2024-04"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 96.0
  as_of: "2024-08"
  note: >
    On the maintainers' own leaderboard table (accessed 2026-09), Jamba-1.5-Large leads with a 96.0%
    average across six tested lengths (4K-128K), a score reported by its own authors in an August
    2024 technical report rather than measured by the RULER team directly; Gemini-1.5-Pro follows at
    95.8%. Below the top handful of models the spread is wide -- the lowest-ranked model on the same
    table averages 36.3% -- and the benchmark's central finding holds broadly: many models with a
    claimed context length of 128K or more only maintain the paper's quality threshold up to
    32K-64K of actual context, well short of their claimed maximum.
contamination:
  risk: low
  note: >
    Tasks are generated synthetically at evaluation time from a fixed recipe (with real Paul Graham
    essays and SQuAD/HotpotQA questions as source material for two of the 13 tasks), so a specific
    graded instance is unlikely to already exist verbatim in training data, though a model could
    still have seen the underlying essays or QA source datasets.
harness:
  lm_eval: "ruler (group of 13 tasks: niah_single_1/2/3, niah_multikey_1/2/3, niah_multiquery, niah_multivalue, ruler_vt, ruler_cwe, ruler_fwe, ruler_qa_hotpot, ruler_qa_squad)"
  inspect_evals: ""
  helm: ""
  opencompass: "ruler (separate config per context length: ruler_4k_gen.py through ruler_1m_gen.py, plus per-task ruler_niah_gen.py, ruler_vt_gen.py, ruler_cwe_gen.py, ruler_fwe_gen.py, ruler_qa_gen.py)"
  bigbench: ""
  other: "NVIDIA/RULER is the reference implementation; Docker images and TensorRT-LLM integration are provided for large-scale evaluation."
tags: ["long-context", "synthetic", "needle-in-a-haystack", "multi-hop", "retrieval", "aggregation"]
sources:
  - url: "https://arxiv.org/abs/2404.06654"
    title: "RULER: What's the Real Context Size of Your Long-Context Language Models? (Hsieh et al., 2024)"
    accessed: "2026-09-08"
  - url: "https://github.com/NVIDIA/RULER"
    title: "NVIDIA/RULER GitHub repository (Apache-2.0, task categories, current leaderboard table)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/ruler"
    title: "lm-evaluation-harness ruler task (13 tasks under a longcxt tag)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/ruler"
    title: "OpenCompass ruler dataset configs (per-length and per-task)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/simonjegou/ruler"
    title: "simonjegou/ruler dataset card (unofficial pre-generated mirror)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RULER procedurally generates long documents at a chosen target length and tests a model with one of
13 synthetic tasks across four categories. Retrieval tasks extend the familiar "needle in a haystack"
test with multiple needle types, multiple needles, and multiple simultaneous queries. Multi-hop
tracing asks a model to follow chains of variable-name bindings scattered through the document.
Aggregation asks it to find the most or least frequent words across a long list. Question answering
embeds real SQuAD or HotpotQA questions inside a padded-out long context. The design goal is
explicit: a plain needle-in-a-haystack test can in principle be solved by one read-through of the
prompt, so RULER's multi-hop and aggregation tasks specifically require combining information from
scattered positions, which a single pass cannot do.

## How it is scored

Each of the 13 tasks is scored on accuracy at a chosen sequence length; the paper's headline metric
averages across six standard lengths (4K, 8K, 16K, 32K, 64K, 128K) and all 13 tasks. Because
"long-context" claims are otherwise hard to compare across models, RULER defines an "effective
length": the longest length at which a model's score still exceeds a fixed quality threshold, set to
Llama-2-7B-chat's own 4K performance (85.6%) as a floor any genuinely capable model should clear. A
model's claimed maximum context length and its effective length, by this measure, are reported side
by side, and the gap between them is the paper's central finding. Weighted averages that up- or
down-weight longer contexts (`wAvg (inc)`/`wAvg (dec)`) are also reported on the maintainers' table
for a subset of models.

## Dataset and licence

RULER ships no fixed set of graded items; it is a generator (Apache-2.0 licensed) that produces new
synthetic instances at whatever length and task-complexity configuration is requested. Two of the 13
tasks draw on existing real text rather than pure synthesis: the needle-in-a-haystack retrieval
variants can use Paul Graham's essays as haystack filler, and the question-answering task embeds real
questions from SQuAD and HotpotQA. Because there is no canonical fixed dataset, community members
have uploaded their own pre-generated instance sets to Hugging Face for convenience (for example
`simonjegou/ruler`), but none of these is the official release, and results from a different random
seed or template are not guaranteed to match another report exactly.

## Who publishes it

RULER was introduced by Cheng-Ping Hsieh, Simeng Sun, Samuel Kriman, Shantanu Acharya, Dima Rekesh,
Fei Jia, Yang Zhang and Boris Ginsburg at NVIDIA in April 2024. NVIDIA continues to maintain the
reference repository directly -- it was last pushed to in July 2026, more than two years after the
original paper, with newer branches (`rulerv1-ns`, `rulerv2-ns`) for updated evaluation pipelines and
a running results table extended well past the paper's original 17 models to include 2025-era
releases such as Qwen3 and EXAONE 4.0.

## Lineage

RULER has no formal predecessor benchmark of its own; it explicitly positions itself as an upgrade
over the plain needle-in-a-haystack test that earlier long-context evaluations relied on, arguing
that test alone indicates only "a superficial form of long-context understanding." No RULER-specific
successor benchmark was identified during this research, though the same claimed-versus-effective-
length framing has been adopted informally by later long-context evaluations, including this
repository's own `graphwalks` family, which was built for a related reason: to require multi-hop
combination rather than single-pass retrieval.

## Saturation and contamination

RULER is not saturated in aggregate: on the maintainers' own results table (accessed 2026-09), scores
range from Jamba-1.5-Large's 96.0% average down to 36.3% for the lowest-ranked model shown, and the
paper's central finding still holds broadly across newer entries -- many models claiming 128K context
or more only sustain the quality threshold up to 32K-64K of actual context. Because RULER generates
fresh instances from a fixed recipe rather than reusing a static public test set, contamination risk
is low: a specific graded document is unlikely to already sit in training data verbatim, though the
essays and QA datasets it draws on for two of its 13 tasks are themselves old and public.

## How to run it

NVIDIA/RULER is the reference implementation, distributed with Docker images and TensorRT-LLM
integration for large-scale runs; `bash run.sh` drives the full 13-task, six-length sweep.
lm-evaluation-harness ships all 13 tasks individually (for example `niah_single_1`, `ruler_vt`,
`ruler_qa_squad`) grouped under a `ruler` group and a `longcxt` tag, and requires a tokenizer so it
can size the generated documents correctly; its default maximum sequence length is 4096 unless a
longer list is passed explicitly. OpenCompass instead ships a separate config file per context length
(`ruler_4k_gen.py` through `ruler_1m_gen.py`), so a reported OpenCompass RULER score is tied to one
specific length rather than the paper's six-length average. Because both the documents and task
templates are regenerated rather than fixed, exact numbers can vary slightly by implementation even
at the same nominal length.

## Reading the numbers

A high RULER score at a given length is good evidence a model can actually use that much context for
retrieval, tracing and aggregation, not just accept that many tokens without erroring -- which is
exactly the gap RULER was built to expose between a vendor's claimed context window and what a model
can reliably use. Because scores are reported per length, a single aggregate RULER number hides where
a model's real ceiling sits; look at the length-by-length breakdown, and specifically at the reported
"effective length," before trusting a headline context-window claim. Given the benchmark averages
across 13 fairly different tasks, a model can also be strong at retrieval-style tasks while notably
weaker at multi-hop tracing or aggregation, so check the task-level breakdown if the use case leans
on one skill in particular.
