---
id: sciknoweval
name: "SciKnowEval"
aliases: []
page_kind: benchmark
category: domain
subcategory: "multi-level scientific-knowledge evaluation across biology, chemistry, physics and materials science"
status: active
summary: "A five-level scientific-knowledge benchmark, from memorization to real-world application, across biology, chemistry, physics and materials science, with two incompatible dataset versions in current use."
measures: >
  SciKnowEval tests scientific knowledge and skill across five progressive levels, named after
  stages from the Confucian "Doctrine of the Mean": Studying Extensively (L1, memorizing facts and
  literature), Enquiring Earnestly (L2, comprehension -- summarizing, extracting relations, verifying
  hypotheses), Thinking Profoundly (L3, calculation and multi-step reasoning), Discerning Clearly
  (L4, safety judgment and harmful-request refusal) and Practicing Assiduously (L5, open-ended
  application such as designing an experimental protocol or a candidate molecule). Each level is
  instantiated separately across four scientific domains -- biology, chemistry, physics and materials
  science -- for a total of dozens of distinct tasks; for example, L1 chemistry includes molecular
  name conversion and literature QA, while L5 chemistry includes molecular generation and
  reagent-design tasks. The five-level structure is the benchmark's organising idea: rather than one
  flat accuracy number, it profiles where in this memory-to-application progression a model's
  scientific competence breaks down.
task_format: >
  A heterogeneous mix of true/false, multiple-choice, relation-extraction and free-form generation
  tasks (including molecule and protein-sequence generation), evaluated zero-shot, English only,
  filterable by domain, level or individual task.
metric:
  name: "task-dependent: exact match, model-graded fact/TF/MCQ/rating judgments, BLEU/ROUGE average, SMILES molecule similarity, Smith-Waterman protein alignment, or relation-extraction F1"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single 0-100 score exists: the paper's own headline comparison (Table 4) instead ranks 26
    evaluated models by their average rank position across all task levels and domains, where a
    smaller number is better and a perfect result would be rank 1.0 on every task. Claude 3.5 Sonnet
    placed first overall with an average rank of 3.71, ahead of GPT-4o (4.68) and GPT-4-Turbo (6.88).
    This rank-based comparison is not the same quantity as the raw per-task accuracy, F1 or
    similarity scores that inspect_evals and OpenCompass report per task, so the two are not
    interchangeable.
dataset:
  size: 28392
  size_note: >
    The currently hosted default Hugging Face configuration ("v2") contains 28,392 rows in a single
    test split, confirmed directly via the Hugging Face datasets-server and matching the paper's own
    headline "28K" figure. A separate, larger "v1" release, hosted as a raw JSONL file in the same
    repository, contains 70,196 rows, confirmed by directly downloading and counting the file.
    inspect_evals' own documentation states it deliberately pins v1 because its task-mapping code was
    written against that version, and that v2 is "a downsampled subset of v1 (~28k samples vs ~70k)
    that drops 13 tasks -- including several graded by the specialized scorers, such as protein
    design (Smith-Waterman) and molecule generation (SMILES) -- and heavily downsamples most of the
    tasks it keeps," further noting the paper itself was not updated to describe v2. In practice, v1-
    and v2-derived scores are not directly comparable, and neither is guaranteed to match whichever
    version a given paper used.
  url: "https://huggingface.co/datasets/hicai-zju/SciKnowEval"
  license: "MIT (Hugging Face dataset card); no separate licence file was found in the reference GitHub repository"
  languages:
    - en
  modalities:
    - text
  splits: "single 'test' split; v1 (70,196 rows, used by inspect_evals) and v2 (28,392 rows, the current default Hugging Face config, matching the paper's own '28K' figure) are incompatible releases with different task inventories"
  public_test_set: true
publisher:
  org: "Zhejiang University (College of Computer Science and Technology; ZJU-Hangzhou Global Scientific and Technological Innovation Center)"
  authors:
    - "Kehua Feng"
    - "Xinyi Shen"
    - "Weijie Wang"
    - "Xiang Zhuang"
    - "Yuqi Tang"
    - "Qiang Zhang"
    - "Keyan Ding"
  url: "https://github.com/HICAI-ZJU/SciKnowEval"
paper:
  title: "SciKnowEval: Evaluating Multi-level Scientific Knowledge of Large Language Models"
  arxiv: "2406.09098"
  url: "https://arxiv.org/abs/2406.09098"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/HICAI-ZJU/SciKnowEval"
released: "2024-06"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2024-06"
  note: >
    SciKnowEval is not saturated: the paper's own abstract states that even its best-performing
    proprietary models face "substantial challenges... particularly in scientific reasoning and
    real-world application," and its headline comparison shows no model near a theoretical ceiling.
    Claude 3.5 Sonnet placed first overall (average rank 3.71 across five levels and four domains)
    ahead of GPT-4o (4.68) and GPT-4-Turbo; open-source general-purpose models such as
    Qwen2-72B-Instruct and Llama3-70B-Instruct scored competitively with mid-tier proprietary models,
    while, notably, specialised "scientific" LLMs built specifically for chemistry or biology
    (ChemDFM, ChemLLM, Galactica, SciGLM, LlaSMol) ranked near the bottom of the whole field -- a
    counterintuitive finding the paper itself highlights. No 0-100 score exists to call a "top score"
    (see baseline_note), and no result newer than the original paper was found.
contamination:
  risk: medium
  note: >
    Roughly a third of the item pool is built by refactoring -- LLM-driven question rewriting and
    option reordering -- of questions drawn from existing public benchmarks: MedMCQA, SciEval, MMLU,
    XieZhi, PubMedQA and HarmfulQA, confirmed directly from the paper's own text, which states this
    was done specifically "to mitigate the risk of data contamination and leakage in these
    benchmarks." Several of those source benchmarks (MMLU and PubMedQA among them) are independently
    known to carry high contamination risk on their own after years of public exposure, and
    paraphrasing reduces rather than eliminates the risk that the underlying fact-answer pairing was
    already seen in training.
harness:
  lm_eval: ""
  inspect_evals: "sciknoweval (filterable by domain, level or task; pins the v1 dataset revision, ~70,196 rows; model-graded tasks default to gpt-4.1-2025-04-14 as grader unless a different grader role is bound)"
  helm: ""
  opencompass: "sciknoweval_biology / sciknoweval_chemistry / sciknoweval_material / sciknoweval_physics (four zero-shot configs reading the dataset's currently-hosted v2 configuration directly)"
  bigbench: ""
  other: ""
tags:
  - domain
  - science
  - multi-level
  - biology
  - chemistry
  - physics
  - materials-science
sources:
  - url: "https://arxiv.org/abs/2406.09098"
    title: "SciKnowEval: Evaluating Multi-level Scientific Knowledge of Large Language Models (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/2406.09098"
    title: "SciKnowEval (ar5iv full text, incl. Table 4 rank comparison, Appendix A4 data sources and licences, author affiliations)"
    accessed: "2026-09-08"
  - url: "https://github.com/HICAI-ZJU/SciKnowEval"
    title: "HICAI-ZJU/SciKnowEval GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sciknoweval/README.md"
    title: "inspect_evals sciknoweval task README (v1/v2 dataset note, scoring table, task mapping, changelog)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hicai-zju/SciKnowEval"
    title: "hicai-zju/SciKnowEval dataset, Hugging Face (licence, v1/v2 files)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SciKnowEval/SciKnowEval_gen_ebe47d.py"
    title: "OpenCompass SciKnowEval dataset config (per-domain sharding)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SciKnowEval tests scientific knowledge and skill across five progressive levels, named after stages from the Confucian "Doctrine of the Mean": Studying Extensively (L1, memorizing facts and literature), Enquiring Earnestly (L2, comprehension -- summarizing, extracting relations, verifying hypotheses), Thinking Profoundly (L3, calculation and multi-step reasoning), Discerning Clearly (L4, safety judgment and harmful-request refusal) and Practicing Assiduously (L5, open-ended application such as designing an experimental protocol or a candidate molecule). Each level is instantiated separately across four scientific domains -- biology, chemistry, physics and materials science -- for a total of dozens of distinct tasks; for example, L1 chemistry includes molecular name conversion and literature QA, while L5 chemistry includes molecular generation and reagent-design tasks. The five-level structure is the benchmark's organising idea: rather than one flat accuracy number, it profiles where in this memory-to-application progression a model's scientific competence breaks down.

## How it is scored

Because task types vary so widely -- true/false, multiple choice, relation extraction, free-text generation, molecule and protein-sequence generation -- SciKnowEval uses a different scorer per task rather than one metric: exact match for classification tasks, model-graded fact, true/false, multiple-choice or rating judgments for open-ended tasks (inspect_evals defaults to gpt-4.1-2025-04-14 as the grading model), an equal-weighted average of BLEU-2, BLEU-4, ROUGE-1, ROUGE-2 and ROUGE-L for summarization-style tasks, SMILES-based molecule-similarity metrics for molecule generation, normalized Smith-Waterman sequence alignment for protein design, and a batch-computed F1 for relation-extraction tasks. Rather than aggregating these into one percentage, the paper's own headline comparison ranks 26 evaluated models by their average rank position across all task levels and domains, where a smaller number is better and a perfect result would be rank 1.0 on every task -- so a "SciKnowEval score" from the original paper is a rank, not a percentage, and is not directly comparable to the raw per-task accuracy or F1 numbers inspect_evals and OpenCompass report.

## Dataset and licence

The currently hosted default Hugging Face configuration ("v2") contains 28,392 rows in a single test split, confirmed directly via the Hugging Face datasets-server and matching the paper's own headline "28K" figure. A separate, larger "v1" release, hosted as a raw JSONL file in the same repository, contains 70,196 rows, confirmed by directly downloading and counting the file; inspect_evals' own documentation states it deliberately pins v1 because its task-mapping code was written against that version, and that v2 "drops 13 tasks -- including several graded by the specialized scorers, such as protein design (Smith-Waterman) and molecule generation (SMILES) -- and heavily downsamples most of the tasks it keeps," further noting the paper itself was not updated to describe v2. In practice, v1- and v2-derived scores are not directly comparable. The dataset card states an MIT licence; no separate licence file was found in the reference GitHub repository. Roughly a third of the item pool is built by refactoring (LLM-driven question rewriting and option reordering) questions drawn from existing public benchmarks -- MedMCQA (`medmcqa`), SciEval, MMLU (`mmlu`), XieZhi, PubMedQA (`pubmedqa`) and HarmfulQA -- specifically to reduce, though not eliminate, contamination risk from those sources' own long public exposure.

## Who publishes it

SciKnowEval comes from Kehua Feng, Xinyi Shen, Weijie Wang, Xiang Zhuang, Yuqi Tang, Qiang Zhang and Keyan Ding; the paper's full text (read via ar5iv) credits Zhejiang University's College of Computer Science and Technology and its ZJU-Hangzhou Global Scientific and Technological Innovation Center, alongside additional co-authors affiliated with Tencent AI Lab in a fuller author list than the arXiv abstract's own citation metadata shows. First posted to arXiv in June 2024, no separate conference proceedings venue was confirmed for the paper in the sources checked for this page. The authors, under the organisation name HICAI-ZJU, maintain the reference GitHub repository and the Hugging Face dataset, last updated in July 2025.

## Lineage

No predecessor or successor is tracked in this repository, but SciKnowEval explicitly builds part of its item pool from several benchmarks that do or could have pages here: MedMCQA (`medmcqa`), MMLU (`mmlu`) and PubMedQA (`pubmedqa`) already have pages in this repository, while SciEval, XieZhi and HarmfulQA, also named as source benchmarks in the paper, do not yet. Within this same research batch, SciKnowEval is the broad, multi-domain counterpart to ChemBench (`chembench`), which covers chemistry alone in more depth; the two are complementary rather than one superseding the other.

## Saturation and contamination

SciKnowEval is not saturated: the paper's own abstract states that even its best-performing proprietary models face "substantial challenges... particularly in scientific reasoning and real-world application," and its headline comparison shows no model near a theoretical ceiling. Claude 3.5 Sonnet placed first overall (average rank 3.71 across five levels and four domains) ahead of GPT-4o (4.68) and GPT-4-Turbo; open-source general-purpose models such as Qwen2-72B-Instruct and Llama3-70B-Instruct scored competitively with mid-tier proprietary models, while, notably, specialised "scientific" LLMs built specifically for chemistry or biology (ChemDFM, ChemLLM, Galactica, SciGLM, LlaSMol) ranked near the bottom of the whole field -- a counterintuitive finding the paper itself highlights. inspect_evals' own changelog shows active maintenance as recently as July 2026, including a scoring bug fix for its relation-extraction tasks. Contamination risk is graded medium: roughly a third of the question pool is built from existing public benchmarks (MMLU and PubMedQA among them) independently known to carry high contamination risk on their own, and while the authors apply LLM-driven rewriting and option reordering specifically to reduce this, paraphrasing reduces rather than eliminates the risk that the underlying fact-answer pairing was already seen in training.

## How to run it

inspect_evals implements `sciknoweval`, filterable by `domain` (biology, chemistry, material, physics), `level` (l1-l5) or a specific `task` name, defaulting to the pinned v1 dataset revision (~70,196 rows) for the reasons described above; model-graded tasks default to gpt-4.1-2025-04-14 as the grading model unless a different grader role is bound. OpenCompass ships four zero-shot `sciknoweval_{biology,chemistry,material,physics}` configs that instead read the dataset's currently-hosted (v2) configuration directly. Because the two harnesses can draw from different dataset versions with different task inventories, a "SciKnowEval" score from one is not guaranteed to be comparable to a score from the other, independent of which model was evaluated.

## Reading the numbers

A strong SciKnowEval result should be read level by level rather than as one number: a model can score well on L1-L2 (recall and comprehension) while remaining weak on L4-L5 (safety judgment and open-ended application), and the paper's own results show exactly this kind of unevenness, including specialised scientific models underperforming general-purpose ones. Always check which dataset version (v1 or v2) and which harness (inspect_evals or OpenCompass) produced a given score before comparing it to another, since neither the item counts nor, for several generation tasks, the scorers themselves match between versions. Given the deliberate rewriting of borrowed questions, a high score here is somewhat more resistant to direct memorization than a raw reuse of MMLU or PubMedQA would be, but should still be corroborated against a fully original scientific-reasoning benchmark before treating it as clean evidence of scientific capability.
