---
id: score
name: "SCORE (Systematic COnsistency and Robustness Evaluation)"
aliases:
  - "SCORE"
  - "Systematic COnsistency and Robustness Evaluation"
  - "score_robustness"
page_kind: family
category: composite
subcategory: "non-adversarial prompt, choice-order, and seed robustness on MMLU-Pro, AGIEval MCQ, and MATH"
status: active
summary: "NVIDIA's non-adversarial robustness suite: re-run MMLU-Pro, AGIEval MCQ, and MATH under prompt, choice-order, and seed changes, reporting accuracy plus consistency rate."
measures: >
  SCORE does not introduce new questions. It re-asks public items from MMLU-Pro, seven English
  AGIEval multiple-choice exams, and Hendrycks MATH while changing the prompt, the option order,
  or the sampling seed. Prompt robustness uses ten semantically similar templates. Choice-order
  robustness swaps the gold option through every listed slot (MMLU-Pro letters A–J; AGIEval only).
  Non-greedy robustness holds the prompt fixed and samples at temperature 0.7 with seeds 1–5.
  The skill is whether an instruct model keeps the same answer under those non-adversarial edits,
  not whether it withstands PromptBench-style attacks.
task_format: >
  Zero-shot generative evaluation of instruct models. MMLU-Pro and AGIEval items are multiple-choice
  completions parsed for an answer letter. MATH items are free-form solutions. The paper generates
  up to 1024 tokens per call. lm-eval recommends --apply_chat_template. Non-greedy runs need five
  seeded jobs plus non_greedy_summarizer.py.
metric:
  name: "accuracy and consistency rate (CR)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Every robustness arm reports accuracy (often per prompt, per option slot, or per seed) and
    pairwise consistency rate CR from Yukun et al. 2024 (arXiv:2403.14221). CR averages a
    similarity over all answer pairs for the same question. The paper writes both as percents;
    the CR formula is a 0–1 mean of pairwise matches. Chance accuracy is not one number:
    MMLU-Pro is ten-way, AGIEval subsets mix option counts, and MATH is open-ended. No human
    CR baseline is published.
dataset:
  size: 19372
  size_note: >
    Unique source items in the paper's tables: MMLU-Pro 12,032 (Apache-2.0), AGIEval English MCQ
    subset 2,340 (MIT; aqua_rat 254, logiqa_en 651, lsat_ar 230, lsat_lr 510, lsat_rc 269,
    sat_en 206, sat_math 220), MATH 5,000 (MIT, levels 1–5). Prompt robustness multiplies each
    item by 10 templates; option-order multiplies by the option count. lm-eval MMLU-Pro YAML
    loads TIGER-Lab/MMLU-Pro validation and test.
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/score"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "source-dataset splits; MMLU-Pro YAML uses validation and test; MATH and AGIEval follow those datasets"
  public_test_set: true
publisher:
  org: "NVIDIA"
  authors:
    - "Grigor Nalbandyan"
    - "Rima Shahbazyan"
    - "Evelina Bakhturina"
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/score"
paper:
  title: "SCORE: Systematic COnsistency and Robustness Evaluation for Large Language Models"
  arxiv: "2503.00137"
  url: "https://arxiv.org/abs/2503.00137"
  year: 2025
leaderboard_url: "https://huggingface.co/spaces/nvidia/llm-robustness-leaderboard"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/score"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The 2025 paper's point is that a single accuracy hides large swings (up to 10% on MMLU-Pro
    prompts and 6.1% on AGIEval option order in the abstract). The Hugging Face Space
    nvidia/llm-robustness-leaderboard was opened on 2026-09-08 and returned a runtime error
    (403 on space restart), so no current numeric table was read. Higher mean accuracy did
    not always mean higher CR in the paper.
contamination:
  risk: high
  note: >
    SCORE reuses public MMLU-Pro, AGIEval, and MATH items that are old enough to appear in
    pretraining. The protocol measures consistency under edits, so memorised gold labels can
    inflate accuracy while CR still moves. It is not a held-out item set.
harness:
  lm_eval: "score_robustness"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Groups: score_robustness_mmlu_pro, score_robustness_agieval, score_robustness_math.
    Named tasks include score_prompt_robustness_*, score_option_order_robustness_* (MCQ only),
    and score_non_greedy_robustness_*. MATH YAML groups split by subject
    (prompt_robustness_math_algebra, …). Non-greedy needs NON_GREEDY.md / non_greedy.sh.
tags:
  - robustness
  - consistency
  - mmlu-pro
  - agieval
  - math
  - family
  - nvidia
sources:
  - url: "https://arxiv.org/abs/2503.00137"
    title: "SCORE paper (arXiv:2503.00137, CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.00137"
    title: "SCORE HTML (tables: MATH 5000, MMLU-Pro 12032, AGIEval 2340; CR; temperature 0.7)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/score"
    title: "lm-eval SCORE task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/score/README.md"
    title: "lm-eval SCORE README (groups, CR formula, instruct-model note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/score/score_robustness.yaml"
    title: "Parent group score_robustness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/score/NON_GREEDY.md"
    title: "Non-greedy protocol (seeds 1–5, temperature 0.7)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/score/mmlu_pro/score_prompt_robustness_mmlu_pro.yaml"
    title: "score_prompt_robustness_mmlu_pro YAML (TIGER-Lab/MMLU-Pro, 10 prompt accuracies + CR)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/score/mmlu_pro/prompt_templates.json"
    title: "MMLU-Pro SCORE prompt templates (10 prompt_robustness entries)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/nvidia/llm-robustness-leaderboard"
    title: "NVIDIA SCORE robustness Space (runtime error on 2026-09-08; no table read)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-071 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-071"
---

## What it measures

SCORE (Systematic COnsistency and Robustness Evaluation) asks whether an instruct model still picks the same answer when the question is unchanged but the wrapper is not. NVIDIA authors Grigor Nalbandyan, Rima Shahbazyan, and Evelina Bakhturina reuse [MMLU-Pro](mmlu_pro.md), seven English [AGIEval](agieval.md) multiple-choice exams, and [MATH](math.md). They change ten non-adversarial prompts, permute where the gold option sits, or sample five seeds at temperature 0.7. English text only. It is not [PromptBench](promptbench.md), which attacks the instruction.

## How it is scored

The paper and lm-eval both report accuracy and consistency rate. CR averages pairwise answer similarity for each question, following Yukun et al. 2024. Prompt robustness yields ten per-template accuracies plus one CR. Option-order robustness reports per-slot accuracy (A–J on MMLU-Pro) plus CR. Non-greedy robustness reports per-seed accuracy plus CR after a separate summariser. The abstract cites up to 10% MMLU-Pro swing under paraphrases and 6.1% AGIEval swing under reordering. There is no single chance baseline across the three sources.

## Dataset and licence

No new labelled items. Paper Table 2 lists 12,032 MMLU-Pro questions (Apache-2.0). Table 3 lists 2,340 AGIEval items (MIT). Table 1 lists 5,000 MATH problems (MIT). The harness code is Apache-2.0, copyright NVIDIA 2024. The paper is CC BY 4.0. Answers for those public sets are public. Prompt templates live under each dataset folder, not at the SCORE root (the README path `./prompt_templates.json` 404s).

## Who publishes it

NVIDIA. The paper (arXiv:2503.00137, 28 February 2025) is the reference. Code ships in EleutherAI lm-evaluation-harness under `lm_eval/tasks/score`. The authors point to a Hugging Face Space `nvidia/llm-robustness-leaderboard`; on 2026-09-08 that Space returned a runtime error and no numeric table. The harness README still leaves the citation block empty and says the paper will be referenced when published, which disagrees with the 2025 paper.

## Lineage

SCORE is a protocol over [mmlu_pro](mmlu_pro.md), [agieval](agieval.md), and [math](math.md), not a successor that replaces them. [PromptBench](promptbench.md) is the adversarial-prompt counterpart. No SCORE subset pages exist in this repository. ZeroSCROLLS and SEA-HELM are unrelated “score” collisions; this id is the NVIDIA robustness family.

## Saturation and contamination

Current standing is not established: the paper’s 2025 tables still show wide CR and accuracy ranges, but the named Space did not render a 2026 table. Underlying items are public and widely copied, so contamination risk is high for raw accuracy. A stable CR on memorised MMLU-Pro is still a robustness signal, not a new knowledge probe.

## How to run it

`lm_eval --tasks score_robustness` (or a child group) with `--apply_chat_template`. Non-greedy tasks need `--seed` 1 through 5, `--log_samples`, and `non_greedy_summarizer.py` as in `NON_GREEDY.md`. MATH has no option-order arm. Compare only matching arms, datasets, and whether chat templates were applied.

## Reading the numbers

A high SCORE accuracy is the same skill as the source bench, measured under a stated prompt or seed. A high CR means the model’s letter or MATH string stayed aligned across those edits. A wide accuracy range with decent mean means the published “best prompt” number is fragile. Do not mix a SCORE CR with PromptBench attack drop, and do not treat a SCORE MMLU-Pro cell as a standard 5-shot CoT MMLU-Pro result.
