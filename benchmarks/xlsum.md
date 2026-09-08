---
id: xlsum
name: "XL-Sum"
aliases:
  - "XLSum"
  - "XL-Sum"
  - "csebuetnlp/xlsum"
page_kind: benchmark
category: generation
subcategory: "multilingual abstractive summarization of BBC articles"
status: active
summary: "BBC article-summary pairs across 45 language configs; OpenCompass concatenates validation splits and scores ROUGE."
measures: >
  XL-Sum asks a model to write a short abstractive summary of a BBC article. Articles and
  bullet-style summaries were extracted from BBC language sites with heuristics, not written
  by the authors. The v2 public release has about 1.35 million pairs. The ACL 2021 paper
  described an earlier cut of about 1 million pairs in 44 languages. OpenCompass loads every
  Hugging Face language config it lists and concatenates the validation splits, then scores
  ROUGE, so an OpenCompass "XLSum" number is a multilingual validation mix, not the English
  test split from the paper.
task_format: >
  OpenCompass prompt: "Document：{text}\\nBased on the previous text, provide a brief single
  summary:". GenInferencer, ZeroRetriever (zero-shot). Predictions pass through
  Xsum_postprocess and RougeEvaluator. Hugging Face configs are named in full
  (english, chinese_simplified, …), not ISO codes.
metric:
  name: "ROUGE (OpenCompass RougeEvaluator)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports ROUGE-1/2/L for an mT5 model fine-tuned on XL-Sum, including English
    test ROUGE-2 around 15.2 in the repository benchmark table. Those are fine-tuned
    encoder-decoder numbers, not zero-shot LLM numbers. OpenCompass does not name which
    ROUGE variant is the headline in the dataset config. There is no random baseline for
    free-form summaries. No human summary-quality baseline was read from the paper extract.
dataset:
  size: 1351253
  size_note: >
    Sum of the v2 per-language totals in the csebuetnlp/xl-sum README table (45 rows):
    train 1,122,857, validation 114,198, test 114,198, total 1,351,253. OpenCompass
    XLSUMDataset concatenates load_dataset(path, lan)['validation'] over 45 language names,
    so a default OpenCompass run scores 114,198 validation items, not the 114,198 test items
    and not the 1.35M pool. The ACL paper's "1 million / 44 languages" figure is the older
    cut; v2 adds Traditional Chinese and more rows. English alone is 329,592 pairs
    (306,522/11,535/11,535).
  url: "https://huggingface.co/datasets/csebuetnlp/xlsum"
  license: "CC-BY-NC-SA-4.0 (dataset contents remain BBC copyright; repo README restricts use to non-commercial research)"
  languages:
    - am
    - ar
    - az
    - bn
    - my
    - zh
    - en
    - fr
    - gu
    - ha
    - hi
    - ig
    - id
    - ja
    - rn
    - ko
    - ky
    - mr
    - ne
    - om
    - ps
    - fa
    - pcm
    - pt
    - pa
    - ru
    - gd
    - sr
    - si
    - so
    - es
    - sw
    - ta
    - te
    - th
    - ti
    - tr
    - uk
    - ur
    - uz
    - vi
    - cy
    - yo
  modalities:
    - text
  splits: "per-language train/validation/test (mostly 80/10/10; English 93/3.5/3.5; some low-resource eval sets expanded to 500). OpenCompass uses validation only."
  public_test_set: true
publisher:
  org: "Bangladesh University of Engineering and Technology (BUET) CSE NLP, with University of Rochester, Monash University, and Swinburne University"
  authors:
    - "Tahmid Hasan"
    - "Abhik Bhattacharjee"
    - "Md. Saiful Islam"
    - "Kazi Mubasshir"
    - "Yuan-Fang Li"
    - "Yong-Bin Kang"
    - "M. Sohel Rahman"
    - "Rifat Shahriyar"
  url: "https://github.com/csebuetnlp/xl-sum"
paper:
  title: "XL-Sum: Large-Scale Multilingual Abstractive Summarization for 44 Languages"
  arxiv: "2106.13822"
  url: "https://aclanthology.org/2021.findings-acl.413/"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/csebuetnlp/xl-sum"
released: "2021-08"
last_updated: "2023-04"
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
    Fine-tuned mT5 numbers in the repo benchmark table are not a current LLM ceiling.
    ExplainaBoard hosted an XL-Sum leaderboard; this page did not scrape it. Zero-shot
    OpenCompass ROUGE is a different protocol from the paper's fine-tune.
contamination:
  risk: high
  note: >
    BBC articles and summaries have been public since 2021 on GitHub and Hugging Face.
    Many models train on news crawls. The test summaries are not held out from the web.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "XLSum"
  bigbench: ""
  other: >
    OpenCompass config directory XLSum; XLSum_gen.py imports XLSum_gen_2bb71c.
    Dataset class XLSUMDataset, path csebuetnlp/xlsum. Japanese evaluation on this
    corpus also appears as ja_leaderboard_xlsum inside [japanese_leaderboard](japanese_leaderboard.md),
    which is Japanese-only ROUGE-2, not the 45-language concat.
tags:
  - summarization
  - multilingual
  - bbc
  - rouge
  - generation
sources:
  - url: "https://arxiv.org/abs/2106.13822"
    title: "XL-Sum arXiv abs (44 languages, ~1 million pairs in the paper cut)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2021.findings-acl.413/"
    title: "ACL Anthology Findings 2021 page for XL-Sum"
    accessed: "2026-09-08"
  - url: "https://github.com/csebuetnlp/xl-sum"
    title: "csebuetnlp/xl-sum README (v2 1.35M / 45 configs, split table, CC BY-NC-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/csebuetnlp/xlsum/raw/main/README.md"
    title: "Hugging Face csebuetnlp/xlsum card (CC-BY-NC-SA-4.0, language list)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/xlsum.py"
    title: "XLSUMDataset: concatenates 45 language validation splits"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/XLSum/XLSum_gen_2bb71c.py"
    title: "OpenCompass XLSum gen config (RougeEvaluator, Xsum_postprocess)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/ja_leaderboard_xlsum.yaml"
    title: "ja_leaderboard_xlsum: Japanese-only ROUGE-2 on mkshing/xlsum_ja, 1-shot"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

XL-Sum is multilingual summarization. The model reads a BBC article in one of the supported languages and writes a short summary, matching the style of the site's own bolded lead. The authors did not hire annotators to write those leads; they recovered them from BBC pages. Coverage runs from English and Arabic to Kirundi, Tigrinya and Welsh. OpenCompass, the harness that registered this id, does not pick one language. It concatenates 45 validation configs, including both simplified and traditional Chinese and both Serbian scripts.

## How it is scored

The paper and the official repo report ROUGE-1, ROUGE-2 and ROUGE-L on per-language test sets, mostly from mT5 fine-tunes. OpenCompass uses `RougeEvaluator` plus the XSum postprocessor on a zero-shot English instruction wrapped around possibly non-English articles. That mix is not the paper protocol. Do not compare an OpenCompass XLSum figure to a Japanese-only `ja_leaderboard_xlsum` ROUGE-2 or to a fine-tuned mT5 English test score.

## Dataset and licence

v2 totals 1,351,253 pairs (README table summed for this page). Licence is CC BY-NC-SA 4.0; the README adds that BBC still holds copyright and use is for non-commercial research. Splits are public. English was split like CNN/DailyMail and XSum (larger train, ~11.5k eval). A few low-resource languages enlarge eval to 500 rows. Same articles are used in both Chinese scripts and both Serbian scripts so multilingual training does not leak across those pairs.

## Who publishes it

Tahmid Hasan, Abhik Bhattacharjee and co-authors at BUET, with collaborators at Rochester, Monash and Swinburne. The paper appeared in Findings of ACL-IJCNLP 2021 (arXiv 2106.13822, June 2021; anthology 2021.findings-acl.413). Code and data: `csebuetnlp/xl-sum`. Hugging Face last-modified April 2023.

## Lineage

The English design follows BBC lead-summary work such as XSum; this repository has no `xsum` page. CrossSum (ACL 2023, same group) is a cross-lingual extension and does not yet have a page here. [japanese_leaderboard](japanese_leaderboard.md) includes a Japanese XL-Sum task that is not OpenCompass's 45-way concat. The paper title says 44 languages; v2's table has 45 language rows because Traditional Chinese was added.

## Saturation and contamination

No current LLM ceiling was transcribed. Fine-tuned mT5 English ROUGE-2 in the repo table sits near 15, which is a 2021 seq2seq point, not a 2026 chat-model point. Contamination risk is high: the text is BBC news on the open web and in a widely downloaded Hub dataset.

## How to run it

OpenCompass: import `XLSum_datasets` from `opencompass.configs.datasets.XLSum.XLSum_gen`. Official fine-tune/eval scripts are in `csebuetnlp/xl-sum` and use the project's multilingual ROUGE. If you need one language, load that Hub config's test split yourself; the OpenCompass loader will not.

## Reading the numbers

A high OpenCompass XLSum ROUGE means the model's zero-shot English-instruction summaries overlap BBC leads on a 45-language validation stew. It does not mean the model summarises every language equally well, and it is not a test-set number from the 2021 paper. Check language, split (validation vs test), and whether the model was fine-tuned. For Japanese-only news summaries, use the Japanese leaderboard task instead of this concat.
