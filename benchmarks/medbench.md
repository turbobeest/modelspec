---
id: medbench
name: "MedBench"
aliases: ["MedBench: A Comprehensive, Standardized, and Reliable Benchmarking System for Evaluating Chinese Medical Large Language Models"]
page_kind: benchmark
category: domain
subcategory: "Chinese medical LLM, multimodal-model and clinical-agent benchmarking platform"
status: active
summary: "OpenCompass's own cloud-hosted, actively versioned Chinese medical benchmark (v1-v5), covering LLM, multimodal and clinical-agent tracks; documented here as distinct from an unrelated, same-named 2023 benchmark."
measures: >
  MedBench is a large, continuously developed Chinese medical evaluation platform, not a single fixed
  dataset. At its July 2024 launch it assembled what its authors call the largest Chinese medical LLM
  evaluation set to date (300,901 questions across 43 clinical specialties) and layered on a
  standardized, cloud-based infrastructure that physically separates questions from ground truth, plus
  a dynamic evaluation mechanism meant to resist shortcut learning and answer memorization. Later
  versions expanded scope sharply: MedBench v4 (November 2025) covers over 700,000 expert-curated
  tasks across 24 primary and 91 secondary specialties with separate tracks for LLMs, multimodal
  models and clinical agents, reviewed by clinicians from more than 500 institutions; MedBench v5
  (June 2026) adds process-oriented auditing and hallucination-propagation tracking for clinical
  multimodal and agent systems. This page documents the platform actually loaded by OpenCompass's own
  `MedBench` dataset config -- see Lineage for a naming collision with a different, unrelated Chinese
  medical benchmark that also calls itself "MedBench."
task_format: >
  A multi-track cloud evaluation covering, on the LLM side, five dimensions (medical knowledge QA,
  medical language understanding, medical language generation, complex medical reasoning, and medical
  safety/ethics) across dozens of named subsets; separate multimodal and agent-environment tracks were
  added in v4. Item formats mix multiple-choice exam questions (scored by exact-match accuracy),
  structured information-extraction tasks such as named-entity and relation extraction (scored by
  entity- or relation-level F1), and open-ended clinical-dialogue or report-generation tasks (scored
  by an LLM-as-judge the authors report is calibrated against human ratings).
metric:
  name: "task-specific: accuracy (exam/multiple-choice subsets), entity- or relation-level F1 (information-extraction subsets), or an LLM-judged 0-100 score (open-ended clinical subsets); no single published formula combines these into one number"
  direction: higher_is_better
  unit: "mixed (%, F1, and a 0-100 judged score depending on subset)"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess or human baseline is published across MedBench's mixed subset types. The
    original 2024 paper instead validates its LLM-as-judge scoring by showing it aligns with medical
    professionals' own assessments; MedBench v4 reports scores on a 0-100 composite scale per track
    (for example base LLMs averaging 54.1/100 overall) without stating a fixed human-expert anchor on
    that same scale.
dataset:
  size: 700000
  size_note: >
    Scale has grown across versions rather than stayed fixed: 300,901 questions across 43 clinical
    specialties at the July 2024 launch (2407.10990's own count), growing to "over 700,000
    expert-curated tasks" across 24 primary and 91 secondary specialties by MedBench v4 (November
    2025); neither paper gives an exact current count more precise than "over 700,000." Separately,
    the OpenCompass GitHub config this page's harness section documents implements a much smaller,
    apparently older roster of 19 named subsets (Med-Exam, DDx-basic, DDx-advanced, MedSafety, MedHC,
    MedMC, MedDG, MedSpeQA, MedTreat, CMB-Clin, MedHG, DrugCA, DBMHG, CMeEE, CMeIE, CHIP-CDEE,
    CHIP-CDN, CHIP-CTC, SMDoc, IMCS-V2-MRG) -- eight of these names (MedHC, MedMC, MedSpeQA, MedHG,
    DDx-advanced, MedTreat, SMDoc, and a "CMB-Clin-extended" variant) also appear on the live
    medbench.opencompass.org.cn homepage fetched for this research, confirming the same lineage, but
    the live site lists several dozen further subset names (MedLitQA, MedRehab, MedRxPlan,
    MedPsychCare, MedRecordGen, MedInsureCheck and many more) that the checked-in OpenCompass config
    does not yet implement.
  url: "https://medbench.opencompass.org.cn"
  license: ""
  languages: ["zh"]
  modalities: ["text", "image"]
  splits: "no public train/test split; the introducing paper describes ground truth as held behind a cloud evaluation service with physical separation from questions, though OpenCompass's own integration downloads a local ./data/MedBench/<subset> copy per subset for offline scoring -- these two descriptions of access are not fully reconciled by any source read for this page"
  public_test_set: false
publisher:
  org: "Shanghai Artificial Intelligence Laboratory (OpenCompass), with co-authors across multiple Chinese hospitals, medical schools and universities"
  authors: ["Mianxin Liu", "Jinru Ding", "Jie Xu", "Weiguo Hu", "Xiaoyang Li", "Lifeng Zhu", "Zhian Bai", "Xiaoming Shi", "Benyou Wang", "Haitao Song", "Pengfei Liu", "Xiaofan Zhang", "Shanshan Wang", "Kang Li", "Haofen Wang", "Tong Ruan", "Xuanjing Huang", "Xin Sun", "Shaoting Zhang"]
  url: "https://medbench.opencompass.org.cn"
paper:
  title: "MedBench: A Comprehensive, Standardized, and Reliable Benchmarking System for Evaluating Chinese Medical Large Language Models"
  arxiv: "2407.10990"
  url: "https://arxiv.org/abs/2407.10990"
  year: 2024
leaderboard_url: "https://medbench.opencompass.org.cn"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/datasets/medbench"
released: "2024-07"
last_updated: "2026-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 62.5
  as_of: "2025-11"
  note: >
    Wide open, and unevenly so across tracks. MedBench v4 (November 2025) reports base LLMs reaching
    a mean overall score of 54.1/100 (best: Claude Sonnet 4.5 at 62.5/100), with safety-and-ethics
    performance far behind at a mean of just 18.4/100. Multimodal models score lower still overall
    (mean 47.5/100; best: GPT-5 at 54.9/100), with the authors noting solid perception but weaker
    cross-modal reasoning. Agents built on the same model backbones do much better end-to-end (mean
    79.8/100), with Claude Sonnet 4.5-based agents reaching 85.3/100 overall and 88.9/100 on safety
    tasks specifically -- a large jump attributed to governance-aware agentic orchestration rather
    than base-model capability alone. No single top_score summarizes this well given how differently
    the base-LLM, multimodal and agent tracks score; 62.5 (best base LLM, the track most comparable to
    how other pages in this repository report a single number) is recorded here with that caveat.
contamination:
  risk: low
  note: >
    The introducing paper states MedBench's cloud infrastructure physically separates questions from
    ground truth and applies "dynamic evaluation mechanisms to prevent shortcut learning and answer
    remembering," which if accurate as described would make direct test-answer memorization
    difficult. This page could not fully verify that description against OpenCompass's own
    integration, however, which downloads a local, subset-named data folder rather than calling a
    held-out cloud service -- a discrepancy between the platform's stated design and at least one
    public integration of it that this research could not resolve from the sources read.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MedBench (opencompass/configs/datasets/MedBench/medbench_gen.py, resolving to medbench_gen_0b4fff.py; 19 subsets grouped into multiple-choice, open-ended QA, cloze and information-extraction evaluator types)"
  bigbench: ""
  other: >
    The live medbench.opencompass.org.cn platform, run by the OpenCompass project at Shanghai
    Artificial Intelligence Laboratory, is the authoritative and actively developed reference
    implementation; its current subset roster is substantially larger than what OpenCompass's
    checked-in GitHub config implements, and it now also serves standalone MedBench v4/v5 papers
    describing multimodal and agent tracks not present in the GitHub config at all.
tags: ["domain", "medical", "chinese", "clinical-reasoning", "information-extraction", "multimodal", "agentic", "safety"]
sources:
  - url: "https://arxiv.org/abs/2407.10990"
    title: "MedBench: A Comprehensive, Standardized, and Reliable Benchmarking System for Evaluating Chinese Medical Large Language Models (Liu et al., arXiv:2407.10990)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2312.12806"
    title: "MedBench: A Large-Scale Chinese Benchmark for Evaluating Medical Large Language Models (Cai et al., arXiv:2312.12806) -- a different, unrelated benchmark sharing this exact name; not the one this page documents"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2511.14439"
    title: "MedBench v4: A Robust and Scalable Benchmark for Evaluating Chinese Medical Language Models, Multimodal Models, and Intelligent Agents (Ding et al., arXiv:2511.14439)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2606.24155"
    title: "MedBench v5: A Dynamic, Process-Oriented, and Hallucination-Aware Benchmark for Clinical Multimodal Models (Ding et al., arXiv:2606.24155)"
    accessed: "2026-09-08"
  - url: "https://medbench.opencompass.org.cn"
    title: "MedBench platform homepage (subset roster, track descriptions; fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: "https://opencompass.org.cn/policy"
    title: "OpenCompass open platform service agreement (Shanghai Artificial Intelligence Innovation Center; general platform ToS, no dataset-specific licence)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/MedBench"
    title: "OpenCompass MedBench dataset configs (medbench_gen.py, medbench_gen_0b4fff.py)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/medbench/medbench.py"
    title: "OpenCompass medbench dataset loader and evaluators (subset lists, scoring logic, local data path)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MedBench is a large, continuously developed Chinese medical evaluation platform rather than a single
fixed dataset. At its July 2024 launch it assembled what its authors describe as the largest Chinese
medical LLM evaluation set to date -- 300,901 questions across 43 clinical specialties -- on a
standardized, cloud-based infrastructure meant to physically separate questions from ground truth and
resist shortcut learning through dynamic evaluation. Coverage has since grown substantially: MedBench
v4 (November 2025) spans over 700,000 expert-curated tasks across 24 primary and 91 secondary
specialties, with separate tracks for base LLMs, multimodal models and clinical agents, reviewed by
clinicians from more than 500 institutions; MedBench v5 (June 2026) adds process-level auditing and
hallucination-propagation tracking specifically for clinical multimodal and agent systems.

On the LLM track, items span five dimensions: medical knowledge QA, medical language understanding,
medical language generation, complex medical reasoning, and medical safety and ethics, drawn from
exam questions, structured information-extraction tasks and open-ended clinical dialogue.

## How it is scored

Scoring is task-specific rather than uniform: multiple-choice exam-style subsets are graded by
exact-match accuracy; structured information-extraction subsets (Chinese medical named-entity and
relation extraction, drawing on shared tasks such as CMeEE, CMeIE and the CHIP series) are graded by
entity- or relation-level F1; and open-ended clinical-dialogue or report-writing subsets are graded
by an LLM-as-judge the original paper reports is calibrated to align with human professional ratings.
No single published formula combines these into one score; MedBench v4 instead reports separate
0-100 composite scores per track (base LLM, multimodal, agent) rather than one number spanning the
whole platform.

## Dataset and licence

Scale has grown across versions: 300,901 questions at the 2024 launch, growing to "over 700,000"
by MedBench v4, with no source read for this page giving a more precise current count. No SPDX-style
licence is published for the dataset itself; the platform operates under a general OpenCompass
open-platform service agreement (from the Shanghai Artificial Intelligence Innovation Center) that
prohibits commercial use of platform resources but does not specify a data licence. Access is
described inconsistently across sources this page could not reconcile: the introducing paper states
ground truth is held behind a cloud service with "physical separations for question and ground
truth," while OpenCompass's own integration downloads a local, subset-named data folder
(`./data/MedBench/<subset>`) for offline scoring.

## Who publishes it

Mianxin Liu, Jinru Ding, Jie Xu and 16 further co-authors published the introducing MedBench paper in
July 2024, with the platform hosted at medbench.opencompass.org.cn by the Shanghai Artificial
Intelligence Laboratory's OpenCompass project. Co-authors span multiple Chinese hospitals, medical
schools and universities. Jie Xu appears as a consistent lead across the later MedBench v4 (November
2025) and v5 (June 2026) papers, both by substantially overlapping author teams, indicating ongoing,
active development of the platform rather than a one-off release.

## Lineage

This page documents the MedBench that OpenCompass's own `MedBench` dataset config actually loads.
That identification is based on direct evidence: OpenCompass's checked-in subset names (MedHC,
MedMC, MedSpeQA, MedHG, DDx-advanced, MedTreat, SMDoc, CMB-Clin, among others) match subset names
found on the live medbench.opencompass.org.cn platform, and that platform is explicitly named as
MedBench's home in the introducing paper's own abstract. One of the OpenCompass subsets, CMB-Clin, is
a direct reuse of the clinical-case component from this repository's own `cmb` benchmark (CMB: A
Comprehensive Medical Benchmark in Chinese), making CMB a component MedBench borrows from rather than
a predecessor or successor benchmark in its own right.

"MedBench" is not a unique name: a different, unrelated benchmark, "MedBench: A Large-Scale Chinese
Benchmark for Evaluating Medical Large Language Models" (Cai et al., arXiv:2312.12806, December
2023), also Chinese and medical, predates this one by seven months and comes from a different author
team (no overlap identified with the authors documented on this page). Its 40,041 questions are built
from four components -- the Chinese Medical Licensing Examination, the Resident Standardization
Training Examination, the Doctor In-Charge Qualification Examination, and real-world clinic cases --
and it is not hosted on the opencompass.org.cn domain. This page does not document that benchmark;
readers who encounter a "MedBench" score should confirm which of the two produced it before treating
it as comparable to either page.

## Saturation and contamination

Wide open, and unevenly so by track. MedBench v4 reports base LLMs reaching a mean overall score of
54.1/100 (best: Claude Sonnet 4.5 at 62.5/100), with safety-and-ethics performance far behind at a
mean of 18.4/100. Multimodal models score lower overall (mean 47.5/100; best: GPT-5 at 54.9/100),
with solid perception but weaker cross-modal reasoning noted by the authors. Agents built on the same
backbones do substantially better end to end (mean 79.8/100; Claude Sonnet 4.5-based agents reaching
85.3/100 overall and 88.9/100 on safety specifically), which the authors attribute to governance-aware
orchestration rather than base-model capability alone. Contamination risk is assessed as low: the
platform's stated design -- physical separation of questions from ground truth, plus dynamic
evaluation meant to resist shortcut learning -- would limit direct memorization if implemented as
described, though this page could not fully reconcile that description against OpenCompass's own
integration, which downloads a local data copy per subset rather than calling a held-out service.

## How to run it

OpenCompass ships MedBench as the `MedBench` dataset config (`medbench_gen.py`, resolving to
`medbench_gen_0b4fff.py`), covering 19 named subsets split across multiple-choice accuracy, open-ended
QA, cloze and per-task information-extraction evaluators (separate F1-style evaluators exist for
CMeEE, CMeIE, CHIP-CDEE, CHIP-CDN, CHIP-CTC, DBMHG, SMDoc and IMCS-V2-MRG specifically). No
lm-evaluation-harness, inspect_evals or HELM implementation was found during this research. The live
medbench.opencompass.org.cn platform is the authoritative, actively developed reference and now
covers a substantially larger subset roster and additional multimodal and agent tracks that the
checked-in OpenCompass config does not yet implement, so a score obtained through the OpenCompass
config is not necessarily comparable to one obtained through the live platform or quoted from the v4
or v5 papers.

## Reading the numbers

A MedBench score is only informative once you know which version, which track (base LLM, multimodal
or agent) and which of the platform's dozens of subsets produced it, given how much broader and
differently structured the platform has become since its 2024 launch. The gap the v4 paper reports
between base-model and agent-orchestrated scores is itself a useful signal distinct from raw model
capability: a governance-aware agent scaffold can substantially close gaps a base model alone cannot,
particularly on safety-and-ethics tasks. Before citing a "MedBench" number from any source, confirm it
is this OpenCompass-hosted, versioned platform and not the differently constructed, unrelated 2023
benchmark of the same name.
