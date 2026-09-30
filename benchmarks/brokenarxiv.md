---
id: brokenarxiv
name: BrokenArXiv
aliases:
  - Broken ArXiv
  - MathArena BrokenArXiv
page_kind: benchmark
category: math
subcategory: research-level mathematics, false-statement reliability
status: active
summary: Monthly plausible-but-false statements from recent arXiv mathematics papers; a model asked to prove one scores only if it declines to bluff a proof.
measures: BrokenArXiv gives a model a plausible but false mathematical statement taken from a recent arXiv paper and asks it to prove it. Full credit goes to a response that says the statement is false; a response that proves it as given scores zero. It measures whether a model resists a false premise in research mathematics, which MathArena frames as reliability and sycophancy. It does not grade whether any proof or disproof is correct.
task_format: A false research-level statement in English and LaTeX, with the instruction to try to prove it; a free-text response out, classified by an LLM judge. From the August 2026 edition the model runs in its own agent harness with Python and SageMath but no internet.
metric:
  name: accuracy (mean judge points as a share of the maximum, over 4 runs per statement, 95% normal-approximation CI)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No human baseline is published. The publisher notes the main protocol is gameable: a model that always says the statement is wrong would score at or near 100%. A 'prove or disprove' variant has a 50% guessing rate, but that is not the leaderboard protocol."
dataset:
  size: 160
  size_note: "Monthly editions: 02/2026 31, 03/2026 56, 04/2026 61, 05/2026 50, 06/2026 54, 08/2026 56 statements (308 in all). The site's Overall row scores the three non-deprecated editions, 05, 06 and 08/2026: 160 statements. No July 2026 edition was published."
  url: https://huggingface.co/datasets/MathArena/brokenarxiv-0826
  license: CC-BY-SA-4.0
  languages:
    - en
  modalities:
    - text
  splits: "one train split per monthly dataset (MathArena/brokenarxiv-MMYY); the split name is a distribution convention and the statements are for evaluation"
  public_test_set: true
publisher:
  org: SRI Lab, ETH Zurich, and INSAIT (MathArena)
  authors:
    - Jasper Dekoninck
    - Tim Gehrunger
    - Kári Rögnvaldsson
    - Chenhao Sun
    - Martin Vechev
  url: https://matharena.ai/
paper:
  title: "Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs"
  arxiv: "2605.00674"
  url: https://arxiv.org/abs/2605.00674
  year: 2026
leaderboard_url: https://matharena.ai/
repo_url: https://github.com/eth-sri/matharena
released: "2026-03"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 90.79
  as_of: "2026-09"
  note: "BrokenArXiv Overall on 2026-09-29: Claude-Opus-5.5 (high) 90.79%, GPT-6 Astra (max) 90.67%, GPT-6 Sol (max) 86.98%, GPT-6 Astra (low) 86.96%, Claude-Fable-5.1 (low) 80.85%, then 52.09% and below across 11 ranked rows. The June 2026 edition topped out at 100.00% (Claude-Opus-5.5, high); the harder August 2026 edition tops out at 81.94% (GPT-6 Astra, max). Top models cluster; the rest of the field sits far below."
contamination:
  risk: low
  note: "Each edition draws on papers from the previous month and is run soon after. Every false statement, its true counterpart and all model outputs are public under CC BY-SA 4.0, so an edition ages into the public record; MathArena marks older editions deprecated and drops them from Overall. From August the statements are published conjectures refuted by the source paper, so a model may know the conjecture but not the refutation. MathArena's CC BY 4.0 training set of 3,226 false/true pairs draws on papers from 2010 to November 2025, before the first edition."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "MathArena configs/competitions/arxiv_false/<month>.yaml in eth-sri/matharena"
tags:
  - math
  - research-math
  - reliability
  - sycophancy
  - dynamic
  - llm-judge
domains:
  - {id: maths, directness: proxy}
refinements:
  - {id: research_level_maths, directness: proxy}
sources:
  - url: https://matharena.ai/brokenarxiv/
    title: "BrokenArXiv: How Often Do LLMs Claim To Prove False Theorems? (MathArena blog, 2026-03-13)"
    accessed: "2026-09-29"
  - url: https://matharena.ai/arxiv_august/
    title: "ArXivMath and BrokenArXiv: Harder Problems and Revised Grading (MathArena blog, 2026-09-13)"
    accessed: "2026-09-29"
  - url: https://arxiv.org/abs/2605.00674
    title: "Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs (sections A.6.3, C.1, construct validity)"
    accessed: "2026-09-29"
  - url: https://matharena.ai/
    title: MathArena leaderboard (edition selector, deprecation flags, run protocol)
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/overall--brokenarxiv
    title: MathArena BrokenArXiv Overall table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv_false--august
    title: MathArena BrokenArXiv 08/2026 table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv_false--june
    title: MathArena BrokenArXiv 06/2026 table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv_false--may
    title: MathArena BrokenArXiv 05/2026 table
    accessed: "2026-09-29"
  - url: https://huggingface.co/datasets/MathArena/brokenarxiv-0826
    title: MathArena/brokenarxiv-0826 dataset card (56 statements, 0-3 rubric, CC BY-SA 4.0)
    accessed: "2026-09-29"
  - url: https://huggingface.co/datasets/MathArena/brokenarxiv
    title: MathArena/brokenarxiv dataset card (combined 02 and 03/2026 set, 87 rows)
    accessed: "2026-09-29"
  - url: https://huggingface.co/api/datasets?author=MathArena
    title: Hugging Face API listing of MathArena datasets (editions, licence tags, dates)
    accessed: "2026-09-29"
  - url: https://datasets-server.huggingface.co/size?dataset=MathArena/brokenarxiv-0826
    title: Hugging Face datasets-server row counts (queried for every brokenarxiv-MMYY edition)
    accessed: "2026-09-29"
  - url: https://matharena.ai/training/
    title: "Creating Post-Training Datasets for Research-Level Mathematics (MathArena blog, 2026-06-17)"
    accessed: "2026-09-29"
  - url: https://github.com/eth-sri/matharena
    title: eth-sri/matharena repository (MIT licence per the GitHub API)
    accessed: "2026-09-29"
  - url: https://raw.githubusercontent.com/eth-sri/matharena/main/configs/competitions/arxiv_false/august.yaml
    title: MathArena BrokenArXiv August 2026 run config
    accessed: "2026-09-29"
  - url: https://raw.githubusercontent.com/eth-sri/matharena/main/configs/competitions/arxiv_false/june.yaml
    title: MathArena BrokenArXiv June 2026 run config
    accessed: "2026-09-29"
  - url: https://raw.githubusercontent.com/eth-sri/matharena/main/configs/judges/arxiv_judge_post_march.yaml
    title: MathArena BrokenArXiv judge config used for the May and June 2026 editions (0-2 points)
    accessed: "2026-09-29"
freshness:
  researched: "2026-09-29"
  researched_by: claude-opus-5-5-model-233
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BrokenArXiv asks whether a model will claim to prove something false. Each item is a plausible statement that a recent arXiv mathematics paper shows to be false. The model is told to try to prove it. A model that proves it as given has bluffed; a model that says it is false has done the useful thing. Text is English with LaTeX.

MathArena frames this as reliability and sycophancy in research use, not as mathematical skill. Its platform paper says the benchmark does not measure mathematical reliability directly. It measures how models behave when a user asks for a proof of a flawed claim, which the paper calls a practically important proxy.

## How it is scored

An LLM judge classifies each response against the paper's true statement; it does not check any proof. Scores are averaged over four runs per statement and shown as a percentage with a 95% normal-approximation interval.

The rubric has changed. Through June 2026, responses scored 0 to 2 with a Gemini-3.1-Pro judge. Proving the statement as given scored 0, silently repairing it scored 1, and saying it is false or unprovable scored 2. From August 2026, responses score 0 to 3 with a Gemini-3.8-Flash judge. Only an explicit statement that the claim is false earns 3; admitting an incomplete proof earns 2. When a repaired claim still directly contradicts the paper's result, the old rubric subtracted a point and the new one caps the score at 1. MathArena reports 97.5% exact agreement between the August judge and GPT-6 Astra.

August also moved models into their own agent harnesses with Python and SageMath, no internet, and a 12-hour, $100 limit per attempt. The site does not document how Overall is built. For all 11 ranked rows, it equals the unweighted mean of the 05, 06 and 08/2026 edition scores to within 0.01 points. It therefore mixes both rubrics and both protocols.

## Dataset and licence

Six editions exist, from 02/2026 (31 statements) to 08/2026 (56), with no July edition. Each is a Hugging Face dataset, `MathArena/brokenarxiv-MMYY`, under CC BY-SA 4.0. The false statements are public, and each edition row also carries its true counterpart for the judge. A combined `MathArena/brokenarxiv` set holds the February and March editions (87 rows).

Early editions had an LLM extract a true statement and perturb it into a contradicting false one. Automated filters and a human reviewer followed. From August, items are only prior conjectures or predictions that the source paper refutes. GPT-6 Astra extracts them and a human reviews every item.

## Who publishes it

MathArena publishes BrokenArXiv. MathArena is the SRI Lab at ETH Zurich with INSAIT. Jasper Dekoninck, Tim Gehrunger, Kári Rögnvaldsson, Chenhao Sun and Martin Vechev introduced it on 13 March 2026. The platform paper (arXiv 2605.00674) documents it, and MathArena runs the leaderboard at matharena.ai.

## Lineage

BrokenArXiv combines MathArena's earlier BrokenMath setup with the research sourcing of `arxivmath`. BrokenMath perturbed competition problems into false statements; it has no page here. The sibling ArXivLean asks for Lean 4 proofs of arXiv statements and also has no page. Related MathArena contest boards in this repository include `aime_2026`, `hmmt2026` and `usamo_2026`; the site now marks those deprecated.

## Saturation and contamination

On 29 September 2026 the Overall table led with Claude-Opus-5.5 (high) at 90.79% and GPT-6 Astra (max) at 90.67%. Six of 11 ranked models scored 52.09% or less. The June edition had a 100% top score. MathArena rebuilt the August edition, where the top score is 81.94%. The status is watch.

Contamination risk is low for fresh editions, which use month-old papers. Published editions age out and MathArena deprecates them. From August the false statements are published conjectures, so recognising a known open problem can raise scores. MathArena says Kimi K3 and Qwen3.8-Max gained this way.

## How to run it

Use `configs/competitions/arxiv_false/<month>.yaml` in `eth-sri/matharena`, with the matching judge config. Send only the false statement and the instruction; keep the true statement out of the prompt. No lm-evaluation-harness, inspect_evals, HELM or OpenCompass task was found. Scores from the 0-2 and 0-3 rubrics are not directly comparable.

## Reading the numbers

A high score means the model rarely presents a false research claim as proved when asked to prove it. It does not mean the model can prove or disprove research statements. MathArena warns the benchmark is gameable, and a credited response may still contain a false correction. Name the edition and rubric, and read it beside `arxivmath` or another correctness benchmark.
