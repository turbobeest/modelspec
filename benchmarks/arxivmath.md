---
id: arxivmath
name: ArXivMath
aliases:
  - ArXiv Math
  - MathArena ArXivMath
page_kind: benchmark
category: math
subcategory: research-level mathematics, final answer
status: active
summary: Monthly final-answer questions built from the previous month's arXiv mathematics papers, scored on whether a model reaches the paper's result.
measures: ArXivMath asks a model to derive a precise result from a recent arXiv mathematics paper without seeing the paper. Each monthly edition is built from papers posted in the previous month, turned into self-contained questions with a single final answer such as a number, formula or mathematical object. The model must return that answer; an LLM judge checks it for mathematical equivalence. It tests research-level problem solving and up-to-date mathematical knowledge, not proof writing.
task_format: A self-contained research-level question in English and LaTeX in; one final answer in \boxed{} out. From the August 2026 edition the model runs in its own agent harness with Python and SageMath but no internet.
metric:
  name: accuracy (mean over 4 runs per question, 95% normal-approximation CI)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No human or random baseline is published. Answers are free-form mathematical expressions, so there is no meaningful chance rate."
dataset:
  size: 145
  size_note: "Monthly editions: 12/2025 17, 01/2026 23, 02/2026 32, 03/2026 30, 04/2026 40, 05/2026 40, 06/2026 48, 08/2026 57 questions (287 in all). The site's Overall row scores the three non-deprecated editions, 05, 06 and 08/2026: 145 questions. No July 2026 edition was published."
  url: https://huggingface.co/datasets/MathArena/arxivmath-0826
  license: CC-BY-SA-4.0
  languages:
    - en
  modalities:
    - text
  splits: "one train split per monthly dataset (MathArena/arxivmath-MMYY); the split name is a distribution convention and the questions are for evaluation"
  public_test_set: true
publisher:
  org: SRI Lab, ETH Zurich, and INSAIT (MathArena)
  authors:
    - Jasper Dekoninck
    - Tim Gehrunger
    - Martin Vechev
  url: https://matharena.ai/
paper:
  title: "Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs"
  arxiv: "2605.00674"
  url: https://arxiv.org/abs/2605.00674
  year: 2026
leaderboard_url: https://matharena.ai/
repo_url: https://github.com/eth-sri/matharena
released: "2026-02"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 92.68
  as_of: "2026-09"
  note: "ArXivMath Overall on 2026-09-29: GPT-6 Astra (max) 92.68%, GPT-6 Sol (max) 91.32%, GPT-6 Astra (low) 86.07%, Claude-Opus-5.5 (high) 83.65%, then 67.59% and below across 11 ranked rows. The August 2026 edition tops out at 92.98% (GPT-6 Sol, max). MathArena wrote that GPT-6 Astra had essentially saturated the June edition and rebuilt the August edition to be harder. Top models cluster near the ceiling; the rest of the field still separates."
contamination:
  risk: low
  note: "Each edition draws on papers from the previous month and is run soon after, so fresh editions post-date most training data. Every question, answer and model output is public under CC BY-SA 4.0, so an edition ages into the public record; MathArena marks older editions deprecated and drops them from Overall. The publisher found about 30% of reviewed first-release questions answerable from prior work, and notes that papers written with LLM help may favour the models used to write them. Its CC BY 4.0 training sets draw on papers from 2010 to November 2025, before the first edition."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "MathArena configs/competitions/arxiv/<month>.yaml in eth-sri/matharena"
tags:
  - math
  - research-math
  - final-answer
  - dynamic
  - llm-judge
domains:
  - {id: maths, directness: direct}
refinements:
  - {id: research_level_maths, directness: direct}
sources:
  - url: https://matharena.ai/arxivmath/
    title: "ArXivMath: Evaluating LLMs on Mathematical Research Problems From Recent ArXiv Papers (MathArena blog, 2026-02-04)"
    accessed: "2026-09-29"
  - url: https://matharena.ai/arxiv_august/
    title: "ArXivMath and BrokenArXiv: Harder Problems and Revised Grading (MathArena blog, 2026-09-13)"
    accessed: "2026-09-29"
  - url: https://arxiv.org/abs/2605.00674
    title: "Beyond Benchmarks: MathArena as an Evaluation Platform for Mathematics with LLMs"
    accessed: "2026-09-29"
  - url: https://matharena.ai/
    title: MathArena leaderboard (edition selector, deprecation flags, run protocol, expected-performance method)
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/overall--arxivmath
    title: MathArena ArXivMath Overall table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv--august
    title: MathArena ArXivMath 08/2026 table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv--june
    title: MathArena ArXivMath 06/2026 table
    accessed: "2026-09-29"
  - url: https://matharena.ai/competition_tables/arxiv--may
    title: MathArena ArXivMath 05/2026 table
    accessed: "2026-09-29"
  - url: https://huggingface.co/datasets/MathArena/arxivmath-0826
    title: MathArena/arxivmath-0826 dataset card (57 questions, evaluation protocol, CC BY-SA 4.0)
    accessed: "2026-09-29"
  - url: https://huggingface.co/datasets/MathArena/arxivmath
    title: MathArena/arxivmath dataset card (combined 12/2025 to 03/2026 set, 103 rows)
    accessed: "2026-09-29"
  - url: https://huggingface.co/api/datasets?author=MathArena
    title: Hugging Face API listing of MathArena datasets (editions, licence tags, dates)
    accessed: "2026-09-29"
  - url: https://datasets-server.huggingface.co/size?dataset=MathArena/arxivmath-0826
    title: Hugging Face datasets-server row counts (queried for every arxivmath-MMYY edition)
    accessed: "2026-09-29"
  - url: https://matharena.ai/training/
    title: "Creating Post-Training Datasets for Research-Level Mathematics (MathArena blog, 2026-06-17)"
    accessed: "2026-09-29"
  - url: https://github.com/eth-sri/matharena
    title: eth-sri/matharena repository (MIT licence per the GitHub API)
    accessed: "2026-09-29"
  - url: https://raw.githubusercontent.com/eth-sri/matharena/main/configs/competitions/arxiv/august.yaml
    title: MathArena ArXivMath August 2026 run config
    accessed: "2026-09-29"
  - url: https://raw.githubusercontent.com/eth-sri/matharena/main/configs/competitions/arxiv/may.yaml
    title: MathArena ArXivMath May 2026 run config
    accessed: "2026-09-29"
freshness:
  researched: "2026-09-29"
  researched_by: claude-opus-5-5-model-233
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ArXivMath asks whether a model can reach the central result of a recent mathematics paper without reading it. Each question is written from one arXiv paper posted in the month before the edition, and names every definition and assumption it needs. The answer is a single number, formula or mathematical object, not a proof. The text is English with LaTeX.

The skill is research-level problem solving on material too new to have been memorised. MathArena's launch post warns that a correct final answer is much easier than a rigorous proof. It adds that the scores are not evidence that models can write the papers themselves.

## How it is scored

Accuracy is the share of questions answered correctly, averaged over four runs per question. The table reports a 95% confidence interval from the normal approximation. Before August 2026, a SymPy-based parser compared answers. At launch, a Gemini-3-Flash judge re-checked rejected answers, and humans verified its positives. From August 2026, a Gemini-3.8-Flash judge decides equivalence. MathArena reports 100% agreement between that judge and GPT-6 Astra as a second judge.

The protocol changed in August 2026. Earlier leaderboard editions ran models on a plain prompt without tools. The August edition runs each model in its own agent harness, for example Codex or Claude Code. The harness has Python and SageMath but no internet. Each attempt has a 12-hour and $100 limit. The site's Overall number is not documented in the pages read. For all 11 ranked rows, it equals the unweighted mean of the 05, 06 and 08/2026 edition scores to within 0.01 points. It therefore mixes the old and new protocols.

## Dataset and licence

There are eight editions so far, from 12/2025 (17 questions) to 08/2026 (57); there is no July edition. Each is a Hugging Face dataset, `MathArena/arxivmath-MMYY`, licensed CC BY-SA 4.0. Questions, answers and source arXiv ids are public, and so are the model outputs. A combined `MathArena/arxivmath` set holds 103 rows from December to March. It has 31 March rows where the March edition has 30.

Construction screens about 4,000 papers a month. An LLM drafts candidate questions and further LLM passes filter them. The filters check that questions are self-contained, add conditions found only in the full text, and drop answers guessable from prior work. Humans review every item. From August, GPT-6 Astra drafts from full TeX sources and conjectures refuted by the paper are preferred; 25 of the 57 August questions come from such conjectures.

## Who publishes it

MathArena publishes ArXivMath. MathArena is run by the SRI Lab at ETH Zurich with INSAIT. Jasper Dekoninck, Tim Gehrunger and Martin Vechev introduced it on 4 February 2026. It is documented in the MathArena platform paper (arXiv 2605.00674, May 2026). MathArena maintains the leaderboard at matharena.ai, and the code is in `eth-sri/matharena` under the MIT licence.

## Lineage

ArXivMath extends MathArena's contest benchmarks, including `aime_2026`, `hmmt2026` and `usamo_2026` in this repository, to research papers. The site now marks those contest groups deprecated. Siblings built by the same pipeline are `brokenarxiv` and ArXivLean, which asks for Lean 4 proofs of arXiv statements and has no page here. MathArena also built ArXivPhys and ArXivCS sets for August 2026. It dropped them because GPT-6 Astra solved almost every question.

## Saturation and contamination

On 29 September 2026 the Overall table led with GPT-6 Astra (max) at 92.68% and GPT-6 Sol (max) at 91.32%. Seven of the 11 ranked models scored below 68%. MathArena wrote that GPT-6 Astra had essentially saturated the June edition at 94%. It made the August edition harder, and there GPT-6 Sol (max) leads at 92.98%. The status is watch: the top separates little, the middle still does.

Contamination risk is low for a fresh edition, because its papers are a month old when it runs. Every ranked row in the Overall table carries the site's flag for a model released after the edition's date. Old editions are public and age out, which is why MathArena deprecates them. The publisher names two limits. About 30% of reviewed launch questions were answerable from prior work. Papers written with LLM help may favour the models used to write them.

## How to run it

Use the MathArena repository: `configs/competitions/arxiv/<month>.yaml` names the dataset, the prompt and, from August, the harness and its limits. No lm-evaluation-harness, inspect_evals, HELM or OpenCompass task was found. Vendor numbers often differ from the leaderboard. The system-card charts extracted in this repository's `benchmarks/_charts/` report single editions from internal runs, at several effort settings, with and without tools. Check the edition and tool access before comparing numbers.

## Reading the numbers

A high ArXivMath score means the model often reaches the stated result of new research papers when asked for a final answer. It does not show the model can prove those results. MathArena found correct answers backed by wrong or missing arguments. Always name the edition. The editions differ in size and difficulty, and August changed both the construction and the tools. Read it with `brokenarxiv`: a model that bluffs a correct-looking answer may also bluff a proof.
