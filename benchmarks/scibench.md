---
id: scibench
name: "SciBench"
aliases:
  - "SciBench: Evaluating College-Level Scientific Problem-Solving Abilities of Large Language Models"
page_kind: benchmark
category: reasoning
subcategory: "college textbook scientific problems (chemistry, physics, mathematics) with numeric answers"
status: active
summary: "College-level chemistry, physics and math word problems from textbooks; OpenCompass scores ten text subsets by numeric exact match after a boxed-answer parse."
measures: >
  SciBench asks a model to solve a collegiate chemistry, physics or mathematics exercise
  and return a number. Items come from named textbooks (Atkins physical chemistry, Halliday
  fundamentals of physics, Stewart calculus, and others). Many solutions need multi-step
  calculation and domain formulae, not high-school arithmetic. The paper also studies
  multimodal (figure) items and an error-attribution protocol over ten skills. OpenCompass
  implements only the text subsets: ten JSON files, four prompt styles (zero-shot,
  zero-shot CoT, few-shot, few-shot CoT), no figures and no Wolfram/Python tool loop.
task_format: >
  Free-text generation. OpenCompass asks for a three-decimal number and a
  `\\boxed[ANSWER]` close (note the square-bracket instruction in the zero-shot template).
  Postprocess looks for `answer is`, then `\\boxed{...}`, then the last number in the
  completion. AccEvaluator does string equality with the `answer_number` field.
metric:
  name: "accuracy (exact match on parsed numeric answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human exam baseline was taken from the paper HTML. The paper's best overall score
    on the textual set is 43.22% (with tools/prompting). The project website, checked
    2026-09-08, states a best overall of 48.96% and notes GPT numbers from 15 March 2024
    that differ slightly from the paper. OpenCompass accuracy is exact match after
    scibench_postprocess, not the paper's tool-using protocol.
dataset:
  size: 580
  size_note: >
    Counted from the ten current xw27/scibench original JSON files (no *_sol.json):
    atkins 105, calculus 42, chemmc 38, class 56, diff 50, fund 71, matter 47, quan 33,
    stat 72, thermo 66 (580). The paper's textbook table sums to 869 (fund 142, calc 161,
    atkins 122, and so on). Hugging Face datasets-server default config reports 692
    train rows because it concatenates original and *_sol.json files. GitHub README says
    the dataset was updated and the previous version lives on the old branch. OpenCompass
    loads `{name}.json` only, so a default OpenCompass run is the 580-item current text set,
    not 869 and not the visual split.
  url: "https://huggingface.co/datasets/xw27/scibench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass: ten named files as separate eval sets; no train/test split in the JSON"
  public_test_set: true
publisher:
  org: "University of California, Los Angeles, Caltech, and University of Washington"
  authors:
    - "Xiaoxuan Wang"
    - "Ziniu Hu"
    - "Pan Lu"
    - "Yanqiao Zhu"
    - "Jieyu Zhang"
    - "Satyen Subramaniam"
    - "Arjun R. Loomba"
    - "Shichang Zhang"
    - "Yizhou Sun"
    - "Wei Wang"
  url: "https://github.com/mandyyyyii/scibench"
paper:
  title: "SciBench: Evaluating College-Level Scientific Problem-Solving Abilities of Large Language Models"
  arxiv: "2307.10635"
  url: "https://arxiv.org/abs/2307.10635"
  year: 2024
leaderboard_url: "https://scibench-ucla.github.io"
repo_url: "https://github.com/mandyyyyii/scibench"
released: "2023-07"
last_updated: "2024-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 43.22
  as_of: "2024-06"
  note: >
    Paper (arXiv v3, 28 June 2024, "To appear at ICML 2024"): best textual overall 43.22%,
    multimodal 13.8%, closed-ended 51.57%. The project website (checked 2026-09-08)
    headlines 48.96% under a zero-shot table dated 15 March 2024 and cites ICML 2024
    in its BibTeX. Scores remain far from 100. top_score records the paper's 43.22
    textual overall.
contamination:
  risk: high
  note: >
    Problems are taken from widely used textbooks whose solutions circulate online.
    The current JSON, including `answer_number` and worked `solution` fields, is public
    on Hugging Face (MIT, created 21 July 2023, last updated 6 May 2024). No held-out
    test split. Textbook leakage into pretraining is likely.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    scibench-{atkins,calculus,chemmc,class,diff,fund,matter,quan,stat,thermo} plus
    _{zs-cot,fs,fs-cot} suffixes; dataset class ScibenchDataset; AccEvaluator with
    scibench_postprocess
  bigbench: ""
  other: "Official eval/ scripts in mandyyyyii/scibench (zero, CoT, few-shot, python, wolfram). No lm-eval or inspect_evals task was found."
tags:
  - science
  - chemistry
  - physics
  - mathematics
  - college
  - numeric
sources:
  - url: "https://arxiv.org/abs/2307.10635"
    title: "SciBench abs: submitted 20 Jul 2023, v3 28 Jun 2024, ICML 2024 comment"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.10635"
    title: "SciBench paper HTML: 869 textbook problems, 43.22% best textual"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/mandyyyyii/scibench/main/README.md"
    title: "SciBench GitHub README: ICML 2024, Hub dataset, old branch"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/mandyyyyii/scibench/main/LICENSE"
    title: "MIT License, copyright 2023 Xiaoxuan Wang"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/xw27/scibench/raw/main/README.md"
    title: "xw27/scibench card: MIT"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/xw27/scibench"
    title: "Hub API: ten original JSON plus ten *_sol.json, created 2023-07-21"
    accessed: "2026-09-08"
  - url: "https://scibench-ucla.github.io/"
    title: "Project site: 48.96% zero-shot headline; ICML 2024 BibTeX"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/scibench/scibench_gen_2b21f3.py"
    title: "OpenCompass ten subsets and four prompt types"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/scibench.py"
    title: "ScibenchDataset + scibench_postprocess"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

SciBench is college scientific problem solving in English text. Each item is a textbook exercise whose official answer is a number, often with a unit that the model must not copy into the boxed value. Subjects mix physical chemistry, quantum chemistry, classical mechanics, thermodynamics, calculus, statistics and differential equations. OpenCompass evaluates ten files (`atkins`, `chemmc`, `quan`, `matter`, `fund`, `class`, `thermo`, `diff`, `stat`, `calculus`). The paper's visual split and its Python/Wolfram tool settings are not in that config.

This is not [ScienceQA](scienceqa.md) (K–12 multimodal MCQ), not [SciCode](scicode.md) (research coding), and not [scBench](scbench.md) (single-cell agents).

## How it is scored

OpenCompass uses exact match on a parsed number. The zero-shot template asks for three decimal places and `\\boxed[ANSWER]` with square brackets; the parser also accepts `\\boxed{...}` and otherwise takes the last number after "answer is". Units are stripped by construction. The paper instead varies zero-shot, CoT, few-shot, Python and Wolfram and reports an overall mean; that 43.22% is not an OpenCompass `AccEvaluator` run. Few-shot prompts are read from `lib_prompt/{name}_prompt.txt` or `{name}_sol.txt`. `max_out_len` is 512.

## Dataset and licence

MIT (GitHub LICENSE and Hub card). Current original JSON files hold 580 problems; the paper table lists 869; datasets-server's 692 concatenates solution-prompt files. GitHub says the set was updated and the old files sit on branch `old`. Answers and worked solutions are in the JSON. OpenCompass does not shuffle a hidden test split.

## Who publishes it

Wang, Hu, Lu, Zhu and colleagues at UCLA, Caltech and the University of Washington. arXiv:2307.10635, 20 July 2023; v3 28 June 2024 comments "To appear at ICML 2024." The GitHub README and the project-site BibTeX both cite ICML 2024. The live site (2026-09-08) headlines 48.96%, not the paper's 43.22%.

## Lineage

Standalone. It sits in the same science-eval neighbourhood as [SciCode](scicode.md), [SciKnowEval](sciknoweval.md) and [OlympiadBench](olympiadbench.md), none of which reuse these textbook ids. No family page.

## Saturation and contamination

Paper-best 43.22% textual (few-shot plus Python in Table 3), website 48.96% (zero-shot table, GPT runs dated 15 March 2024), multimodal 13.8%. The ceiling is open. Contamination risk is high: public numbered answers from standard textbooks. A rising score may be recall of Atkins or Halliday, not new scientific reasoning.

## How to run it

Hub: `xw27/scibench`. OpenCompass: `scibench_datasets` from `configs/datasets/scibench/scibench_gen.py`, local `./data/scibench/{name}.json`. Name the prompt type (`zs` vs `fs-cot`) and whether tools were allowed. Official `eval/` scripts also run Python and Wolfram settings that OpenCompass does not. No lm-eval or inspect_evals task was found.

## Reading the numbers

A high OpenCompass SciBench accuracy means the parsed number matched `answer_number` on these 580 (or 869, if an older dump) text problems. It does not mean the model can read the paper's figures, write research code, or pass a closed-book college exam in a proctored setting. Always state the item dump (580 vs 869), the prompt style, and tool access. Compare with [GPQA](gpqa.md) or [OlympiadBench](olympiadbench.md) only as a rough scientific-reasoning panel, not as the same test.
