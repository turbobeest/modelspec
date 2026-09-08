---
id: click
name: CLIcK
aliases:
  - "CLIcK: Cultural and Linguistic Intelligence in Korean"
  - Cultural and Linguistic Intelligence in Korean
page_kind: benchmark
category: knowledge
subcategory: "Korean cultural and linguistic multiple-choice QA from exams and textbooks"
status: active
summary: "Korean multiple-choice exam of cultural and linguistic knowledge: 1,995 questions in eleven categories, drawn from official exams and textbooks."
measures: >
  click is EleutherAI lm-evaluation-harness's group for CLIcK (Cultural and
  Linguistic Intelligence in Korean). The model reads a Korean question, often
  with a short context, and picks a lettered choice. Items test Korean language
  (textual, grammatical, functional knowledge) and Korean culture (society,
  tradition, politics, economy, law, history, geography, popular culture).
  Sources are official exams plus GPT-4 questions written from the KIIP
  textbook and then validated. This is a Korean-centric knowledge test, not
  a translated English quiz and not [korbench](korbench.md) (which is English
  knowledge-orthogonal reasoning despite the similar id).
task_format: >
  Multiple choice in Korean. lm-eval output_type is multiple_choice. The Korean
  prompt in utils.get_context always lists A–D. Scoring helpers get_choices and
  get_target use A–E when the example id contains CSAT, else A–D. The Hugging
  Face split used as both test_split and fewshot_split is named train. Groups:
  click (all 11), click_lang (3), click_cul (8).
metric:
  name: "accuracy and length-normalized accuracy (acc, acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Four-option items have a 25% chance rate and CSAT items a 20% rate; the
    mixed set has no single chance figure in the paper. Claude-2 was the
    strongest of 13 models in the paper (51.72% culture, 45.39% language).
    GPT-3.5 was described as the 11th percentile of Korean test-takers on the
    relevant exams, not as a human mean on this 1,995-item mix.
dataset:
  size: 1995
  size_note: >
    Paper Table 1 and Hugging Face datasets-server agree on 1,995 examples in
    the default train split. Culture 1,345 (society 309, tradition 222, history
    280, law 219, politics 84, economy 59, geography 131, pop culture 41);
    language 650 (textual 285, functional 133, grammar 232). 1,245 textbook /
    750 exam in that table.
  url: "https://huggingface.co/datasets/EunsuKim/CLIcK"
  license: ""
  languages:
    - ko
  modalities:
    - text
  splits: "Hugging Face default config exposes only train (1,995); lm-eval uses that split for both evaluation and few-shot"
  public_test_set: true
publisher:
  org: KAIST (School of Computing and GSAI)
  authors:
    - Eunsu Kim
    - Juyoung Suk
    - Philhoon Oh
    - Haneul Yoo
    - James Thorne
    - Alice Oh
  url: "https://github.com/rladmstn1714/CLIcK"
paper:
  title: "CLIcK: A Benchmark Dataset of Cultural and Linguistic Intelligence in Korean"
  arxiv: "2403.06412"
  url: "https://arxiv.org/abs/2403.06412"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/rladmstn1714/CLIcK"
released: "2024-03"
last_updated: "2024-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 51.72
  as_of: "2024-03"
  note: >
    Paper Table of 13 models: Claude-2 51.72% average on Korean culture and
    45.39% on Korean language. Open Korean LMs clustered near 32–36% culture
    and 22–27% language. No later public ceiling was found. 51.72 is culture
    average, not a single official overall.
contamination:
  risk: medium
  note: >
    Exam items (CSAT, TOPIK, PSAT, and others) may appear in pretraining.
    1,245 textbook-derived items were generated with GPT-4 from KIIP chapters,
    which reduces exact exam overlap but can echo textbook wording. The full
    1,995 items are public on Hugging Face.
harness:
  lm_eval: click
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - korean
  - culture
  - language
  - multiple-choice
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2403.06412"
    title: "CLIcK paper (arXiv 2403.06412)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.06412"
    title: "CLIcK paper HTML"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EunsuKim/CLIcK"
    title: "Hugging Face EunsuKim/CLIcK"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EunsuKim/CLIcK/raw/main/README.md"
    title: "CLIcK dataset card README"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=EunsuKim/CLIcK"
    title: "datasets-server info: 1,995 train rows"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/click/README.md"
    title: "lm-eval click README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/click/click.yaml"
    title: "lm-eval click group YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/click/click_lang/_default_click_lang_yaml"
    title: "lm-eval click_lang default YAML (extensionless include file)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/click/click_lang/utils.py"
    title: "lm-eval click_lang utils (prompt, CSAT A-E choices)"
    accessed: "2026-09-08"
  - url: "https://github.com/rladmstn1714/CLIcK"
    title: "CLIcK GitHub repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

CLIcK asks whether a model knows Korean language and Korean cultural context well enough to pass exam-style questions. Each item is a Korean stem, optional paragraph, and lettered choices. Categories split into language (textual, grammar, function) and culture (society, tradition, politics, economy, law, history, geography, K-pop).

The authors built the set from two streams. They reclassified official exam items (CSAT, TOPIK, PSAT, Kedu, PSE, KHB). They also prompted GPT-4 on KIIP textbook chapters and kept validated questions. The skill is Korean-centric knowledge, including items that a translated MMLU clone would miss. It is not [csatqa](csatqa.md), which is a smaller HAE-RAE CSAT slice with human student rates.

## How it is scored

lm-eval reports mean `acc` and `acc_norm`, weighted by subset size, on the group `click`. Subgroups `click_lang` and `click_cul` average their tagged tasks the same way. The target is the letter whose choice string matches the dataset answer. When the example id contains `CSAT`, `get_choices` and `get_target` use A–E; otherwise they use A–D. The Korean `get_context` prompt still always prints A–D, so a fifth CSAT option is scored but not shown in that stem.

The paper evaluated 13 models. API models were scored by generated text; open models by token likelihood. Claude-2 led at 51.72% culture and 45.39% language. That is the published reference table, not an lm-eval leaderboard. There is no single random baseline for the mixed 4- and 5-choice items.

## Dataset and licence

The paper's Table 1 and Hugging Face datasets-server both give 1,995 examples. Culture sums to 1,345 and language to 650. 1,245 items are listed as textbook-origin and 750 as exam-origin. The Hub config exposes a single `train` split; lm-eval evaluates that split. Answers are public.

No licence file was present in the GitHub tree opened here, and the Hub card does not set a licence field. Leave licence empty rather than infer CC-BY. The Hub card still contains unused `your_username/CLIcK` badge links; the live dataset id is `EunsuKim/CLIcK`.

## Who publishes it

Eunsu Kim, Haneul Yoo, and Alice Oh (KAIST School of Computing) with Juyoung Suk, Philhoon Oh, and James Thorne (KAIST GSAI) released the dataset and the LREC-COLING 2024 paper (arXiv 2403.06412, 11 March 2024). The GitHub repo is `rladmstn1714/CLIcK`. Hugging Face lastModified on the API blob opened here is 7 September 2024. EleutherAI maintains the lm-eval task group.

## Lineage

CLIcK was built because translated English culture tests miss Korean context, and existing Korean culture sets were narrow (bias or hate speech). Exam overlap with [csatqa](csatqa.md) is possible on CSAT Korean items, but csatqa is a different 187-question harness group with human scores. [kormedmcqa](kormedmcqa.md) is medical. [korbench](korbench.md) is not Korean.

lm-eval filters categories in `utils.py` (for example CSAT Korean id ranges for text vs grammar). Those filters implement the eleven-way split; they are not extra hidden tests.

## Saturation and contamination

Claude-2 at about 52% culture in 2024 left clear headroom. No later official table was found in this research, so saturation stays open with that paper figure as a dated reference, not a 2026 ceiling.

Exam questions can leak. Textbook-generated items are newer but public. Treat the set as a medium contamination risk.

## How to run it

```bash
lm-eval --tasks click
```

Use `click_lang`, `click_cul`, or a single task such as `click_cul_history` for slices. Default YAMLs load `EunsuKim/CLIcK` with `output_type: multiple_choice`. The Korean prompt is hard-coded in `utils.get_context`. Few-shot, if requested, draws from the same `train` split the test uses, so in-context examples can overlap the eval pool unless you control sampling.

Paper likelihood scoring of open models is not guaranteed to match a generative lm-eval run.

## Reading the numbers

A high `click` accuracy means the model often picked the keyed letter on this 1,995-item mix. It does not mean fluency in open-ended Korean, and it does not mean medical or legal competence beyond the culture/law questions in the set. Compare `click_lang` and `click_cul` before quoting one number. Do not stack it with [csatqa](csatqa.md) as if they were the same CSAT dump. Claude-2's 51.72% is a 2024 culture average under the paper's protocol, not an lm-eval result on a 2026 model.
