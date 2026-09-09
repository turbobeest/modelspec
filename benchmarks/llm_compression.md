---
id: llm_compression
name: "LLM Compression"
aliases:
  - "llm-compression"
  - "Compression Represents Intelligence Linearly"
  - "BPC compression corpora"
page_kind: benchmark
category: generation
subcategory: "unsupervised bits-per-character on Common Crawl, GitHub Python, and arXiv-math"
status: active
summary: "Bits-per-character compression of three raw corpora, used as an unsupervised linear proxy for knowledge, coding, and math benchmarks."
measures: >
  LLM Compression does not ask questions. It scores how many bits a base
  language model needs, on average, to encode held-out raw text. Huang,
  Zhang, Shan, and He collect three external corpora aimed at three
  abilities: Common Crawl snapshots for knowledge and commonsense, GitHub
  Python for coding, and arXiv mathematics papers for math. They report
  bits per character (BPC) rather than bits per token so tokenizers can be
  compared. The claim in the COLM 2024 paper is that average BPC is almost
  linearly correlated with average scores on 12 downstream benchmarks.
  The HTML body says 30 public LLMs; the arXiv v2 abstract says 31.
task_format: >
  No prompt and no target string. OpenCompass feeds the content field
  through SWCELossInferencer with a sliding window (paper reproduction:
  block_size 1900, stride 512), sums cross-entropy, and converts to BPC.
  ZeroRetriever; no in-context examples. Intended for base models, not
  chat-tuned models.
metric:
  name: "bits per character (BPC), also averaged across the three corpora"
  direction: lower_is_better
  unit: "BPC"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower BPC is better. There is no chance baseline. The GitHub README
    leaderboard's best listed average is Llama-3-70b at 0.359 (Common Crawl
    0.496, Python 0.204, Arxiv-Math 0.376). OpenCompass's bundled table
    tops out at qwen1.5-32b-hf 0.4191 average among the 13 models it
    prints. Those tables are author-run, not a live board.
dataset:
  size: 32344
  size_note: >
    Hugging Face datasets-server for hkust-nlp/llm-compression reports
    32,344 test rows: cc 20,159, python 10,977, arxiv_math 1,208. The paper
    Table 1 instead quotes character counts and crawl windows: Common Crawl
    131M characters (September–October 2023), GitHub 98M (June–September
    2023), ArXiv 101M (September–October 2023). The Hub card's
    size_categories field is the coarse bucket 10K<n<100K. OpenCompass
    loads local jsonl files named arxiv_math, commoncraw, and python under
    ./data/llm-compression (the commoncraw filename is the crawl subset,
    Hub config name cc).
  url: "https://huggingface.co/datasets/hkust-nlp/llm-compression"
  license: "CC-BY-NC-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "single public test split per config (cc, python, arxiv_math); no train split"
  public_test_set: true
publisher:
  org: "Hong Kong University of Science and Technology, with Tencent"
  authors:
    - "Yuzhen Huang"
    - "Jinghan Zhang"
    - "Zifei Shan"
    - "Junxian He"
  url: "https://github.com/hkust-nlp/llm-compression-intelligence"
paper:
  title: "Compression Represents Intelligence Linearly"
  arxiv: "2404.09937"
  url: "https://arxiv.org/abs/2404.09937"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/hkust-nlp/llm-compression-intelligence"
released: "2024-04"
last_updated: "2024-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.359
  as_of: "2024-09"
  note: >
    Best average BPC on the GitHub README table is Llama-3-70b at 0.359.
    That table is a static author list, not a continuously updated board,
    and later models are not established here. Lower is better, so the
    number is a floor among listed models rather than a percentage ceiling.
contamination:
  risk: medium
  note: >
    Corpora are public raw text from Common Crawl, GitHub, and arXiv,
    collected in mid-to-late 2023 to reduce overlap with older pretraining
    dumps. The paper argues the metric can be refreshed with new crawls.
    No source opened here measured leakage of these exact jsonl files into
    a named model.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "llm_compression"
  bigbench: ""
  other: "OpenCompass dataset abbrs llm_compression-arxiv_math, llm_compression-commoncraw, llm_compression-python. Example: python run.py --datasets llm_compression"
tags:
  - compression
  - perplexity
  - unsupervised
  - language-modeling
sources:
  - url: "https://arxiv.org/abs/2404.09937"
    title: "Compression Represents Intelligence Linearly abs (arXiv:2404.09937v2, COLM 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2404.09937"
    title: "Paper HTML (BPC formula, Table 1 character counts and crawl dates, context 1900)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hkust-nlp/llm-compression-intelligence/main/README.md"
    title: "Official GitHub README (leaderboard, OpenCompass, MIT code / CC BY-NC-SA 4.0 data)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hkust-nlp/llm-compression/raw/main/README.md"
    title: "Hugging Face dataset card (license cc-by-nc-sa-4.0, three test configs)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hkust-nlp/llm-compression"
    title: "Hugging Face dataset API (license cc-by-nc-sa-4.0; lastModified 2024-04-16)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hkust-nlp/llm-compression"
    title: "datasets-server size (32,344 rows: cc 20,159 / python 10,977 / arxiv_math 1,208)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/llm_compression/README.md"
    title: "OpenCompass llm_compression README (BPC formula, example scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/llm_compression/llm_compression.py"
    title: "OpenCompass llm_compression.py (block_size 1900, stride 512, BPCEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_bpc_evaluator.py"
    title: "OpenCompass BPCEvaluator (CE / (chars * log 2))"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-054 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-054"
---

## What it measures

LLM Compression scores a base language model as a lossless compressor of raw text. The model is not asked to answer questions. OpenCompass and the authors' script concatenate corpus documents, run a sliding window of 1,900 tokens with stride 512, and convert total cross-entropy into bits per character. Three corpora stand in for three abilities: Common Crawl for knowledge and commonsense, GitHub Python for coding, and arXiv math papers for mathematical reasoning. The COLM 2024 paper reports that this unsupervised BPC tracks average scores on 12 downstream benchmarks almost linearly for the base models they tested.

## How it is scored

BPC is total cross-entropy divided by (character count × ln 2), matching PyTorch's natural-log loss. Lower is better. The authors unify the context window at 1,900 tokens so a long-context model cannot buy a better compressor score than the short-context downstream tasks would reflect. They average the three corpora for a headline figure and also report each domain. The GitHub README table lists Llama-3-70b at 0.359 average BPC as the best of the printed models. OpenCompass's config README prints a shorter table headed by qwen1.5-32b-hf at 0.4191. Those are different model sets, not a disagreement about the same run. Fine-tuned chat models are out of scope in the paper's main claim, because they no longer model arbitrary next tokens.

## Dataset and licence

Hugging Face `hkust-nlp/llm-compression` has 32,344 public test rows (cc 20,159, python 10,977, arxiv_math 1,208) under CC BY-NC-SA 4.0. The Hub API lastModified stamp is 16 April 2024. The GitHub repository's code is MIT; the README says stricter upstream terms are honoured when a source requires them. The paper quotes character totals (131M / 98M / 101M) and crawl windows in 2023 rather than row counts. OpenCompass expects local jsonl files under `./data/llm-compression`, with the crawl file named `commoncraw.jsonl` even though the Hub config is `cc`. There is no hidden test split.

## Who publishes it

Yuzhen Huang, Jinghan Zhang, and Junxian He at HKUST, with Zifei Shan at Tencent. The paper was posted on arXiv on 15 April 2024 (2404.09937). The GitHub README records OpenCompass support on 1 May 2024 and COLM 2024 acceptance on 20 September 2024, and its citation block points at OpenReview forum SHMj84U5SH. There is no separate live leaderboard URL beyond the static GitHub table.

## Lineage

This page is the compression corpora and BPC protocol from that paper, as wired in OpenCompass under `llm_compression`. It is not [Inference-PPL](inference_ppl.md), which averages token NLL on labeled spans of a local reasoning jsonl. It is also not WikiText perplexity ([wikitext](wikitext.md)). The authors present BPC as a refreshable unsupervised stand-in for MMLU-style, HumanEval-style, and GSM8K/MATH-style averages, not as a replacement for those pages. No successor id is recorded here.

## Saturation and contamination

BPC has no 100% ceiling. Among models printed on the GitHub table, Llama-3-70b is best at 0.359 average, but later models were not read here. Because the metric is just language-model loss on public crawls, a model trained on those crawls can look strong without being a better reasoner. The authors chose 2023 windows to limit overlap with older dumps and argue that new crawls can be swapped in. Treat a low BPC as compression skill on these files, then check the matching downstream suite before claiming knowledge, code, or math gains.

## How to run it

In OpenCompass, `--datasets llm_compression` builds three dataset abbrs with `SWCELossInferencer` (block_size 1900, stride 512) and `BPCEvaluator`. Download the Hub configs into `./data/llm-compression` first; the loader reads local json/jsonl only. The authors' `code/evaluation/main.py` is the reference outside OpenCompass. Keep flash-attention and GPU settings explicit. Do not score chat checkpoints with this protocol if you want numbers comparable to the paper: the paper's main plots are base models.

## Reading the numbers

A lower average BPC means the model assigned higher probability to these three crawls under a 1,900-token window. It does not mean the model is better at GSM8K or HumanEval on its own, only that the authors saw a near-linear fit for their 2024 base-model pool. Always name the subset (cc vs python vs arxiv_math): a code specialist can look strong on python and weak on crawl. Do not mix OpenCompass's short example table with the GitHub leaderboard, and do not compare BPC to [Inference-PPL](inference_ppl.md) NLL. If two models use very different tokenizers, BPC is the quantity that is supposed to remain comparable; bits-per-token is not.
