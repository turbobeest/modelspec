---
id: m3_duplexbench
name: M3-DuplexBench
page_kind: benchmark
category: generation
subcategory: spoken dialogue
summary: "M3-DuplexBench evaluates multilingual full-duplex spoken dialogue with turn-taking, backchannels, and user interruptions."
measures: "M3-DuplexBench tests spoken dialogue systems that listen while speaking. It covers English and Japanese, casual conversation and multi-turn question answering, and multiple context conditions for studying dialogue history."
task_format: "Multi-turn audio dialogue with full-duplex interaction and context variants."
metric:
  name: dialogue performance
  direction: higher_is_better
  unit: score
dataset:
  languages: [English, Japanese]
  modalities: [audio]
  public_test_set: null
publisher:
  org: "M3-DuplexBench authors"
  authors: [Ryo Fukuda, Atsushi Ando, Hiroki Kanagawa, Takatomo Kano, Marc Delcroix, Naohiro Tawara, Yuya Chiba]
  url: https://arxiv.org/abs/2607.29125
paper:
  title: "M3-DuplexBench: A Multi-Turn, Multilingual, Multidomain Benchmark for Full-Duplex Spoken Dialogue Models"
  arxiv: "2607.29125"
  url: https://arxiv.org/abs/2607.29125
  year: 2026
released: "2026-07"
saturation:
  status: open
  note: "The paper reports language-, domain-, and model-specific gaps."
contamination:
  risk: unknown
  note: "Training exposure is not established by the paper abstract."
harness:
  other: "The evaluation protocol described in the M3-DuplexBench paper."
tags: [speech, duplex, multilingual, turn-taking]
sources:
  - url: https://arxiv.org/abs/2607.29125
    title: "M3-DuplexBench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

M3-DuplexBench evaluates full-duplex spoken dialogue systems that can listen while speaking. It targets smooth turn-taking, backchannel handling, and user barge-in handling, capabilities that ordinary turn-based speech tests do not capture.

The benchmark supports English and Japanese, casual conversation, and multi-turn question answering. It also varies dialogue context so researchers can separate language, domain, and history effects.

## How it is scored

The paper compares recent full-duplex systems under single-turn, user-only, and teacher-forced full-context conditions. It reports model-specific turn-taking characteristics and performance gaps across languages and domains. The abstract does not specify a single metric name, maximum, or baseline, so those values remain unknown here. Context mode must accompany every score.

## Dataset and licence

The paper establishes the supported languages, dialogue types, and context conditions but does not state a total item count or licence in the abstract. Public test visibility is therefore unknown. Reproduction should use the authors’ release and record audio provenance, transcript policy, and context condition.

## Who publishes it

Ryo Fukuda, Atsushi Ando, Hiroki Kanagawa, Takatomo Kano, Marc Delcroix, Naohiro Tawara, and Yuya Chiba introduced the benchmark in a July 2026 arXiv submission to SLT 2026. No maintained public leaderboard is identified.

## Lineage

M3-DuplexBench is a standalone full-duplex spoken-dialogue benchmark. It addresses limited multilingual and multidomain coverage in earlier dialogue tests, but the paper does not name a specific predecessor or successor.

## Saturation and contamination

The paper reports clear gaps across languages and domains and mixed effects of dialogue context. This indicates an open evaluation space. The source does not establish training-data contamination, so risk is unknown.

## How to run it

Use the same audio interface and context condition described by the paper. Report language, dialogue domain, whether the user can interrupt, latency or turn-taking settings, transcript handling, and model sampling. Do not combine context conditions into one score without showing the breakdown.

## Reading the numbers

A strong score indicates better performance in the tested dialogue setup. It does not prove natural turn-taking in unseen languages or noisy real conversations. Compare language and domain slices, and inspect interruptions and backchannels. Context mode is part of the result, not an incidental implementation detail.
