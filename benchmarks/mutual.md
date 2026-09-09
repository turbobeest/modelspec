---
id: mutual
name: "MuTual"
aliases:
  - "MuTual"
page_kind: benchmark
category: reasoning
subcategory: "multi-turn English dialogue response selection with four candidates"
status: unknown
summary: "8,860 four-way response-selection dialogues rewritten from Chinese high-school English listening tests, scored with R@1, R@2 and MRR."
measures: >
  MuTual gives a short multi-turn English conversation and four candidate next turns. All four
  replies are on-topic; only one is logically consistent with the speakers, the setting and what
  was already said. The model must rank the correct reply first. Dialogues were rewritten by
  annotators from Chinese senior-high-school English listening exams, so the English is exam
  English, not spontaneous chat. A harder variant, MuTual-plus (lm-eval task `mutual_plus`),
  replaces one candidate with a safe fallback such as “Could you repeat that?”. This is retrieval-
  style response selection, not open-ended chatting and not [coqa](coqa.md).
task_format: >
  Multiple choice over four responses. lm-eval uses output_type multiple_choice, doc_to_text the
  detokenised article, doc_to_choice the four options, gold letter A–D. Metrics r@1, r@2 and mrr
  via utils.process_results. Default YAML scores the validation split (no test_split key).
  should_decontaminate true.
metric:
  name: "R@1 (recall at 1 among 4 candidates); also R@2 and MRR"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: 94
  baseline_note: >
    Four candidates, so uniform R@1 is 25%. The ACL 2020 paper reports human performance 94% and
    then-SOTA methods 71% in the abstract; those headlines sit next to the R@1 / R@2 / MRR
    protocol in section 4. R@2 chance is 50%. lm-eval r@1 is argmax accuracy; r@2 is 1 if the gold
    is in the top two log-prob ranks. Do not treat 71% as a current ceiling.
dataset:
  size: 8860
  size_note: >
    Paper and GitHub README: 8,860 context-response pairs from 6,371 original dialogues and
    11,323 original questions; 4.73 turns per dialogue on average; four candidates. Split 80% /
    10% / 10% by packing items from the same conversation together. GitHub listing on 2026-09-08:
    886 .txt files in data/mutual/dev and 886 .txt files in data/mutual/test (plus a .DS_Store).
    The train directory listing is truncated by the GitHub API at 1,000 entries; 80% of 8,860 is
    7,088, which was not re-counted file-by-file. Test answers are withheld on the authors'
    GitHub (README). Hugging Face EleutherAI/mutual rebuilds from the GitHub zip.
  url: "https://github.com/Nealcly/MuTual"
  license: "other (EleutherAI/mutual card); the loader comments 'No license found'"
  languages:
    - en
  modalities:
    - text
  splits: "train / validation (dev) / test at 80/10/10; lm-eval scores validation"
  public_test_set: false
publisher:
  org: "Westlake University and Microsoft Research Asia"
  authors:
    - "Leyang Cui"
    - "Yu Wu"
    - "Shujie Liu"
    - "Yue Zhang"
    - "Ming Zhou"
  url: "https://github.com/Nealcly/MuTual"
paper:
  title: "MuTual: A Dataset for Multi-Turn Dialogue Reasoning"
  arxiv: "2004.04494"
  url: "https://aclanthology.org/2020.acl-main.130/"
  year: 2020
leaderboard_url: "https://nealcly.github.io/MuTual-leaderboard/"
repo_url: "https://github.com/Nealcly/MuTual"
released: "2020-04"
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
    Paper headline in 2020: methods 71%, humans 94%. No current leaderboard cell was read from
    nealcly.github.io/MuTual-leaderboard (the README points there). lm-eval scores the
    development split, not the hidden-answer test files, so a harness number is not the official
    test ranking.
contamination:
  risk: high
  note: >
    Train and development items, including gold letters, have been public on GitHub since 2020.
    The authors withheld test labels and ask for emailed predictions. Listening-exam source
    material is also widely copied. lm-eval sets should_decontaminate true with the article as
    the query. Treat a near-perfect R@1 on the public YAML as possibly leaked.
harness:
  lm_eval: "mutual"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "lm-eval also ships mutual_plus (include: mutual.yaml, dataset_name mutual_plus)."
tags:
  - dialogue
  - response-selection
  - reasoning
  - multiple-choice
  - english
sources:
  - url: "https://arxiv.org/abs/2004.04494"
    title: "MuTual arXiv abstract (8,860 dialogues, human 94%, methods 71%)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2004.04494"
    title: "MuTual HTML (80/10/10 split, R@1 R@2 MRR, MuTual-plus safe responses)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.acl-main.130/"
    title: "ACL 2020 anthology page (July 2020, anthology id 2020.acl-main.130)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/Nealcly/MuTual/master/README.md"
    title: "Nealcly/MuTual README (8,860 pairs, data template, test answers withheld, leaderboard)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/mutual"
    title: "EleutherAI/mutual API (license: other)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/mutual/raw/main/mutual.py"
    title: "EleutherAI/mutual loader (mutual and mutual_plus configs; licence comment)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mutual/README.md"
    title: "lm-eval mutual README (tasks mutual and mutual_plus)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mutual/mutual.yaml"
    title: "lm-eval mutual.yaml (validation split, r@1 r@2 mrr)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mutual/multual_plus.yaml"
    title: "lm-eval mutual_plus YAML (filename multual_plus.yaml)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mutual/utils.py"
    title: "lm-eval mutual utils.py (detokenise, R@1/R@2/MRR)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-061 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-061"
---

## What it measures

MuTual is a four-way next-turn test. The model reads a short English dialogue (speakers marked `m` and `f`) and four candidate replies. Every candidate is about the same scene. Only one reply respects the facts, the relationship and the last question. Annotators rewrote Chinese high-school listening items so that the original question-and-answer became four responses instead of a separate comprehension question. The English is classroom listening English. Average dialogue length in the README is 4.73 turns. The skill is multi-turn consistency, not fluency and not trivia.

MuTual-plus, run in lm-eval as `mutual_plus`, swaps one of the four replies for a canned “I didn’t catch that” line. If the gold reply was replaced, the safe line is now correct; if a distractor was replaced, the original gold remains correct. That variant checks whether the model still picks a real answer when a vague apology is on the list.

## How it is scored

The paper treats the task as response selection and reports recall at 1 among 4 (R@1), recall at 2 (R@2) and mean reciprocal rank. Chance R@1 is 25%. Humans in the paper are 94%; contemporaneous models are 71% on that same headline. lm-evaluation-harness maps the four options to log-probabilities, then computes `r@1` as whether the gold is argmax, `r@2` as whether it is in the top two, and `mrr` as 1/rank. The YAML names the training and validation splits and does not set `test_split`, so a default `mutual` run is the development set. The authors’ test files omit gold labels and ask for emailed ranked predictions. Those two protocols are not the same leaderboard.

## Dataset and licence

8,860 pairs, split 80/10/10 with whole source conversations kept together. Development and test directories on GitHub each held 886 `.txt` files when listed. Each file is one JSON object with `article`, `options`, `answers` and `id`. Hugging Face `EleutherAI/mutual` downloads the GitHub zip and exposes configs `mutual` and `mutual_plus`. The card licence is `other`; the loader comments that no licence was found. Do not assume Apache or CC-BY.

## Who publishes it

Leyang Cui, Yue Zhang (Westlake / Zhejiang), Yu Wu, Shujie Liu and Ming Zhou (Microsoft Research Asia). ACL 2020 (anthology 2020.acl-main.130), arXiv:2004.04494, 9 April 2020. Repository github.com/Nealcly/MuTual. The README points at a leaderboard at nealcly.github.io/MuTual-leaderboard/; that page was not scored for this write-up.

## Lineage

MuTual sits in the retrieval-dialogue line (Lowe et al. Ubuntu, Wu et al. Douban) but swaps crawled next-utterance matching for exam-style reasoning distractors. It is not CoQA and not an open generation benchmark. `mutual_plus` is a difficulty variant of the same files, not a separate dataset family in this repository.

## Saturation and contamination

A 94% human ceiling with a 2020 model score of 71% left room then. Whether current chat models sit on that ceiling on the hidden test set was not read from the authors’ board. Train and dev labels have been public for years, so contamination risk is high for any lm-eval `mutual` number. The original test keys remain off GitHub.

## How to run it

```text
lm_eval --model hf --model_args pretrained=... --tasks mutual
```

`mutual_plus` is a second task with the same metrics. Detokenisation lives in `utils.process_docs`. Compare R@1 only to other R@1 numbers, not to generation BLEU. HELM, inspect_evals and OpenCompass names were not found.

## Reading the numbers

A high `mutual` R@1 means the model ranked the logically consistent reply first on the public development dialogues. It does not mean the model can chat, and it does not mean the hidden test set. Quote `mutual` versus `mutual_plus` explicitly. Treat scores near 94% on the YAML as possibly contaminated. Pair with a more recent dialogue or long-context reasoning set if the claim is about current assistants.
