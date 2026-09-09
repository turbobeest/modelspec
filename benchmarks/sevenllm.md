---
id: sevenllm
name: "SEvenLLM (SEvenLLM-Bench)"
aliases:
  - "SEvenLLM"
  - "SEVENLLM"
  - "SEvenLLM-Bench"
  - "SEVENLLM-Dataset"
page_kind: benchmark
category: domain
subcategory: "bilingual English/Chinese cyber threat intelligence: incident understanding MCQ and generation QA"
status: active
summary: "Bilingual English/Chinese cyber-threat-intelligence bench of 1,300 test items: 100 four-way MCQs and 1,200 free-form QA items on incident analysis."
measures: >
  SEvenLLM-Bench tests whether a model can analyse cybersecurity incidents in English and
  Simplified Chinese. Understanding items are four-way multiple choice. Generation items ask for
  free-form answers such as key-entity lists, malware features, or attack-strategy writeups.
  The paper’s instruction corpus covers 28 expert-vetted CTI tasks over crawled incident text.
  Inspect Evals splits the public test dump into four runs: MCQ and QA, each in zh and en.
task_format: >
  Inspect tasks wrap Hugging Face test.jsonl at revision 1de23ce. MCQ uses a fixed instruction
  template and Inspect multiple_choice with choice() scoring. QA uses generate() plus ROUGE-L
  (0.2 sentence threshold, jieba for Chinese) and cosine similarity from
  paraphrase-multilingual-MiniLM-L12-v2. The authors’ own code also reports GPT-4 scores and
  human ratings, which Inspect does not implement.
metric:
  name: "MCQ accuracy (choice); QA ROUGE-L (0–100) and semantic cosine similarity"
  direction: higher_is_better
  unit: ""
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    MCQ is four options (A–D), so chance is 25% on those 100 items if options are balanced; that
    was not separately tabulated in the sources opened here. QA ROUGE-L in Inspect is the share of
    reference sentences whose best generated match has rouge-l F ≥ 0.2, scaled to 100. Semantic
    similarity is cosine on MiniLM embeddings, not a percentage accuracy. Paper Table 3 reports
    author-stack Rouge-L, not the Inspect thresholded scorer.
dataset:
  size: 1300
  size_note: >
    Paper Table 1 and the HF card: SEvenLLM-Bench test is 1,300 items (MCQ zh 50, MCQ en 50, QA zh
    600, QA en 600). Inspect eval.yaml repeats those four counts. SEvenLLM-Instruct train.jsonl is
    91,401 rows on the HF card; the paper says nearly 90K. The card filename column says test.json
    while the repo sibling is test.jsonl; Inspect fetches test.jsonl via the raw HF URL.
  url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/SEVENLLM-Dataset"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "train.jsonl (Instruct, 91401) / test.jsonl (Bench, 1300); Inspect uses only the filtered test split"
  public_test_set: true
publisher:
  org: "Beihang University and collaborators (Multilingual-Multimodal-NLP)"
  authors:
    - "Hangyuan Ji"
    - "Jian Yang"
    - "Linzheng Chai"
    - "Chaoren Wei"
    - "Liqun Yang"
    - "Yunlong Duan"
    - "Yunli Wang"
    - "Tianzhen Sun"
    - "Hongcheng Guo"
    - "Tongliang Li"
    - "Changyu Ren"
    - "Zhoujun Li"
  url: "https://github.com/CSJianYang/SEevenLLM"
paper:
  title: "SEvenLLM: Benchmarking, Eliciting, and Enhancing Abilities of Large Language Models in Cyber Threat Intelligence"
  arxiv: "2405.03446"
  url: "https://arxiv.org/abs/2405.03446"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/CSJianYang/SEevenLLM"
released: "2024-05"
last_updated: "2024-05"
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
    Paper tables compare the authors' fine-tuned models with Llama-2-Chat and Qwen1.5-Chat under
    their Rouge-L stack. Those 2024 numbers are not a current Inspect leaderboard. No Inspect-eval
    top cell was read here.
contamination:
  risk: medium
  note: >
    The 1,300 test rows are public on Hugging Face (Apache-2.0) since May 2024, with chain-of-thought
    fields in the JSON. Source incident pages were already on the web. No study opened here showed
    verbatim memorisation of the test split.
harness:
  lm_eval: ""
  inspect_evals: "sevenllm"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable Inspect tasks: sevenllm_mcq_zh, sevenllm_mcq_en, sevenllm_qa_zh, sevenllm_qa_en
    (inspect_evals v2-A). Extra: pip install inspect-evals[sevenllm]. Prompt adapted from
    CSJianYang/SEevenLLM infer.py.
tags:
  - cybersecurity
  - cti
  - bilingual
  - chinese
  - english
  - inspect-evals
sources:
  - url: "https://arxiv.org/abs/2405.03446"
    title: "SEvenLLM paper (arXiv:2405.03446)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.03446"
    title: "SEvenLLM HTML (Table 1 1300-test split; 28 tasks; Rouge-L tables)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/SEVENLLM-Dataset"
    title: "HF SEVENLLM-Dataset (Apache-2.0, train 91401, test 1300)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Multilingual-Multimodal-NLP/SEVENLLM-Dataset"
    title: "HF API (sha 1de23ce; files train.jsonl and test.jsonl; license apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Multilingual-Multimodal-NLP/SEVENLLM-Dataset/raw/main/README.md"
    title: "HF dataset card README"
    accessed: "2026-09-08"
  - url: "https://github.com/CSJianYang/SEevenLLM"
    title: "Authors' SEevenLLM GitHub (note extra e in the path)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CSJianYang/SEevenLLM/main/README.md"
    title: "Authors' README (GPT-4 / Rouge-L / semantic / MCQ / human scoring)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/sevenllm"
    title: "inspect_evals sevenllm directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sevenllm/README.md"
    title: "inspect_evals sevenllm README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sevenllm/sevenllm.py"
    title: "sevenllm.py (four tasks, HF revision, prompt template)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sevenllm/scorers.py"
    title: "Inspect ROUGE-L and MiniLM semantic scorers"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sevenllm/eval.yaml"
    title: "eval.yaml (50/50/600/600 counts, version 2-A)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-071 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-071"
---

## What it measures

SEvenLLM-Bench asks a model to work a cybersecurity incident in English or Simplified Chinese. Multiple-choice items test understanding. Generation items ask for structured CTI outputs such as entities, malware traits, or response text. Hangyuan Ji, Jian Yang, and co-authors built the tasks from crawled reports, GPT-4 drafts, and expert edits against MITRE and OASIS-style foci. It is incident analysis, not a live CTF like [Cybench](cybench.md).

## How it is scored

Inspect grades MCQ with `choice()` over A–D. QA uses two scorers: a thresholded ROUGE-L (sentence-level LCS, jieba on Chinese, 0.2 cutoff, scaled to 100) and MiniLM cosine similarity. The authors’ repository also lists GPT-4 scores and human expert scores; those are not what `inspect eval inspect_evals/sevenllm_qa_en` prints. Paper Table 3 Rouge-L is their stack, not the Inspect 0.2 rule. Do not mix them.

## Dataset and licence

Hugging Face `Multilingual-Multimodal-NLP/SEVENLLM-Dataset` is Apache-2.0. Bench test size is 1,300 (50+50 MCQ, 600+600 QA), matching Table 1 and Inspect `eval.yaml`. Instruct train.jsonl is 91,401 rows on the card versus “nearly 90K” in the paper. The card table says `test.json`; the file is `test.jsonl`. The JSON includes `thought` chain-of-thought. Inspect pins revision `1de23ce55cadc984d3f3a7b52c4035a68c6cd5b0`.

## Who publishes it

Beihang-affiliated authors, dataset org Multilingual-Multimodal-NLP. arXiv:2405.03446 (6 May 2024; v2 3 June 2024). Author code is https://github.com/CSJianYang/SEevenLLM (the path has an extra “e”). Inspect Evals packages the public test split as `sevenllm`. No live public leaderboard URL was confirmed.

## Lineage

Standalone CTI bench plus a training corpus. It is not [cti_realm](cti_realm.md) or [cti_to_mitre](cti_to_mitre.md), and it is not CyberSecEval. v1 abstract text in some indexes said 27 tasks; the v2 HTML and Inspect README say 28. No successor page here.

## Saturation and contamination

Frontier standing under Inspect scorers is not established here. Test answers are public, so leakage is possible. The card warns that security jargon may trip safety filters, which can look like a low score for the wrong reason.

## How to run it

`pip install inspect-evals[sevenllm]` then `inspect eval inspect_evals/sevenllm_mcq_en` (and `_zh`, `_qa_en`, `_qa_zh`). Language is detected from CJK characters, not from a metadata field. Compare MCQ accuracy only with MCQ accuracy, and ROUGE-L only with the same thresholded scorer.

## Reading the numbers

A high MCQ score means the model picked the labelled letter on 50 English or 50 Chinese items. A high Inspect QA ROUGE-L means enough reference sentences found a generated sentence above 0.2 LCS F, not that a SOC analyst would file the writeup. Semantic cosine can be high when wording diverges. Check language, MCQ versus QA, and whether GPT-4 judging was used instead of Inspect.
