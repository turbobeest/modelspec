---
id: ceval
name: "C-Eval"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "Chinese multi-level multi-discipline exam suite"
status: active
summary: "A 13,948-question, four-option Chinese exam benchmark across 52 subjects and four difficulty levels, whose test set was held out via a submission site until a full public release in July 2025."
measures: >
  C-Eval tests broad academic and professional knowledge and reasoning in a Chinese-language
  context. Each item is a four-option multiple-choice question drawn from one of 52 disciplines
  spanning the humanities, social sciences, STEM and other professional fields, split across four
  difficulty levels -- middle school, high school, college and professional -- mirroring how
  Chinese students and professionals actually progress through subjects. It positions itself as a
  Chinese-context counterpart to MMLU: exam-style questions authored in Chinese rather than
  translated from English content.
task_format: >
  Four-option multiple-choice question answering in Chinese, evaluated zero-shot and five-shot.
  Answers are scored either by parsing a generated answer letter or, when a model does not follow
  the instruction format well, by taking the highest-probability option among A-D.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    25% is the four-option random-guess rate. The paper reports no general human baseline. At
    release (2023) only GPT-4 exceeded 60% average accuracy on the leaderboard (66.4% zero-shot,
    68.7% five-shot), which the authors called evidence of considerable headroom over 2023-era
    models.
dataset:
  size: 13948
  size_note: >
    13,948 multiple-choice questions across 52 subjects: a 260-question dev set (5 per subject, for
    few-shot prompting), a 1,346-question validation set, and a test set making up the remainder
    (roughly 12,342 questions). Total confirmed via the Hugging Face datasets-server aggregate row
    count for ceval/ceval-exam.
  url: "https://huggingface.co/datasets/ceval/ceval-exam"
  license: "CC BY-NC-SA 4.0 (dataset, per the Hugging Face card and the repository's own Licenses section); the repository's evaluation code is separately released under MIT"
  languages:
    - zh
  modalities:
    - text
  splits: "dev (260, 5/subject) / validation (1,346) / test (~12,342; labels withheld from release in 2023 until 26 July 2025)"
  public_test_set: true
publisher:
  org: "C-Eval team (GitHub organisation hkust-nlp)"
  authors:
    - "Yuzhen Huang"
    - "Yuzhuo Bai"
    - "Zhihao Zhu"
    - "Junlei Zhang"
    - "Jinghan Zhang"
    - "Tangjun Su"
    - "Junteng Liu"
    - "Chuancheng Lv"
    - "Yikai Zhang"
    - "Jiayi Lei"
    - "Yao Fu"
    - "Maosong Sun"
    - "Junxian He"
  url: "https://github.com/hkust-nlp/ceval"
paper:
  title: "C-Eval: A Multi-Level Multi-Discipline Chinese Evaluation Suite for Foundation Models"
  arxiv: "2305.08322"
  url: "https://arxiv.org/abs/2305.08322"
  year: 2023
leaderboard_url: "https://cevalbenchmark.com/static/leaderboard.html"
repo_url: "https://github.com/hkust-nlp/ceval"
released: "2023-05"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 92.3
  as_of: "2024-10"
  note: >
    The now-frozen leaderboard's top scores are 92.3% among privately-submitted models (Hisense
    Xinghai, October 2024) and 91.8% among openly accessible models (iFlytek Spark 4.0 Max, October
    2024), both well above GPT-4's 2023 score of 68.7% and both self-submitted through the site
    rather than independently verified by the C-Eval team (only the original 2023 baseline models
    are marked as team-evaluated). No submission newer than February 2025 was observed on the
    leaderboard read for this page, consistent with the team's July 2025 announcement that they
    would stop maintaining it.
contamination:
  risk: high
  note: >
    Test-set labels were withheld specifically to prevent leakage from release in 2023 until 26
    July 2025, when the C-Eval team published the complete test set, including answers, and
    announced they would stop maintaining the leaderboard. Any model trained or fine-tuned after
    that date should be assumed to have had the opportunity to see the test answers if C-Eval was
    in its training data; the Hugging Face mirror's test split now carries real answer letters
    rather than the empty placeholders it used before the release.
harness:
  lm_eval: "ceval (documented in the harness as \"C-Eval (Validation)\"; historically exposed per-subject as Ceval-valid-<subject>)"
  inspect_evals: ""
  helm: ""
  opencompass: "ceval (multiple configs: ceval_ppl, ceval_gen, ceval_zero_shot_gen, ceval_clean_ppl, and several versioned prompt revisions)"
  bigbench: ""
  other: ""
tags:
  - knowledge
  - multiple-choice
  - chinese
  - multitask
  - exam
sources:
  - url: "https://arxiv.org/abs/2305.08322"
    title: "C-Eval: A Multi-Level Multi-Discipline Chinese Evaluation Suite for Foundation Models"
    accessed: "2026-09-08"
  - url: "https://github.com/hkust-nlp/ceval"
    title: "hkust-nlp/ceval GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ceval/ceval-exam"
    title: "ceval/ceval-exam dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://cevalbenchmark.com/static/leaderboard.html"
    title: "C-Eval leaderboard (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/ceval"
    title: "lm-evaluation-harness ceval task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/ceval"
    title: "OpenCompass ceval dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

C-Eval tests broad academic and professional knowledge and reasoning in a Chinese-language context. Each item is a four-option multiple-choice question drawn from one of 52 disciplines spanning the humanities, social sciences, STEM and other professional fields, split across four difficulty levels -- middle school, high school, college and professional -- mirroring how Chinese students and professionals actually progress through subjects. It positions itself as a Chinese-context counterpart to MMLU: exam-style questions authored in Chinese rather than translated from English sources. C-Eval Hard is a fixed 8-subject subset (advanced mathematics, discrete mathematics, probability and statistics, college chemistry, college physics, and their high-school equivalents) selected because those subjects need multi-step, often equation-heavy reasoning rather than recall alone.

## How it is scored

Every item is four-option multiple choice, so random guessing scores 25%. The authors report both zero-shot and five-shot accuracy and note that instruction-tuned models often score better zero-shot than five-shot. At release in 2023, only GPT-4 exceeded 60% average accuracy (66.4% zero-shot, 68.7% five-shot), which the authors called evidence of considerable remaining headroom. Answers are scored either by parsing a generated letter or, when a model resists the instruction format, by taking the highest-probability option among A-D -- the same constrained-decoding fallback the original MMLU evaluation script uses.

## Dataset and licence

C-Eval totals 13,948 multiple-choice questions across 52 subjects. Each subject splits into a five-question dev set for few-shot prompting (260 questions total), a 1,346-question validation set, and a test set making up the remainder (roughly 12,342 questions). From release in 2023 until 26 July 2025, test-set labels were withheld specifically "to avoid leakage," and scoring required submitting predictions to the C-Eval website -- the site's own leaderboard page states this reasoning directly. On 26 July 2025 the maintainers released the complete test set publicly (confirmed by the current Hugging Face mirror, whose test-split rows now carry real answer letters instead of the earlier placeholders) and announced they would stop updating the leaderboard. The Hugging Face dataset card gives the data licence as CC BY-NC-SA 4.0; the GitHub repository's evaluation code is separately released under MIT.

## Who publishes it

C-Eval comes from Yuzhen Huang, Yuzhuo Bai, Zhihao Zhu, Junlei Zhang, Jinghan Zhang, Tangjun Su, Junteng Liu, Chuancheng Lv, Yikai Zhang, Jiayi Lei, Yao Fu, Maosong Sun and Junxian He, published in May 2023 and accepted to NeurIPS 2023. The reference repository is hosted under hkust-nlp on GitHub, the dataset is mirrored on Hugging Face under the `ceval` organisation, and cevalbenchmark.com hosted the submission-based leaderboard.

## Lineage

C-Eval has no predecessor or successor tracked in this repository; it belongs to a cluster of contemporaneous Chinese evaluation suites, including CMMLU and GaokaoBench, that do not yet have pages here either. C-Eval Hard, the 8-subject STEM-heavy variant described above, is reported by the original authors alongside the main average but does not have a separate id in this repository.

## Saturation and contamination

Contamination avoidance was the explicit reason test labels were held out for two years, but that protection ended on 26 July 2025 when the full test set, including answers, was published and the leaderboard was frozen. Any model trained after that date should be assumed to have had the opportunity to see C-Eval's test answers directly, a materially different situation from the earlier submission-only era. Saturation looks advanced at the top of the now-static leaderboard: the highest recorded score is 92.3% (a privately-submitted model, October 2024), and 91.8% among openly accessible models (also October 2024), both well above GPT-4's 2023 score of 68.7%. Nearly every leaderboard entry besides the original 2023 baseline models is vendor-submitted through the site rather than independently reproduced by the C-Eval team, so treat any single leaderboard entry as a self-report rather than a verified score.

## How to run it

lm-evaluation-harness implements C-Eval as a validation-only task, documented as "C-Eval (Validation)" and historically exposed per subject as `Ceval-valid-<subject>` -- it scores the public validation split, not the test split. OpenCompass ships several `ceval` configuration variants, including perplexity-based and generation-based scoring plus multiple prompt-format revisions that are not directly comparable to one another. Because the test set only became public in mid-2025, older papers' numbers came from the submission portal rather than local scoring, while newer ones may score the test set directly; check which a source did before comparing numbers across papers.

## Reading the numbers

A high C-Eval score signals strong performance on Chinese-language exam-style questions across a broad range of subjects and difficulty levels, but says little about open-ended Chinese generation, dialogue, or cultural knowledge outside exam formats. Frontier scores now cluster in the low-to-mid 90s on the frozen leaderboard, so differences of a point or two are unlikely to be meaningful, and because most current entries are vendor self-reports rather than independently verified, corroborate an unusually high score against another Chinese benchmark, such as CMMLU, before trusting it. Given the July 2025 test-set release, also check whether a reported score predates or postdates that date: it changes both the contamination picture and how the number could have been produced.
