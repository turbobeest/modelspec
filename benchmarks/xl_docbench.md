---
id: xl_docbench
name: XL-DocBench
aliases: []
page_kind: benchmark
category: long-context
subcategory: evidence-grounded extra-long document question answering
status: active
summary: "XL-DocBench tests evidence-grounded QA on extra-long professional documents, with page-level evidence, typed rules, and unanswerable cases."
measures: >
  XL-DocBench gives a system one or more long professional PDFs and a question that
  usually cannot be answered from a single local snippet. The model must find supporting
  pages, read text together with tables, charts, or figures, apply a typed verification
  rule, and abstain when the documents do not contain the required support. Twelve
  reasoning labels separate comparison, reference chains, ranking, coverage, set
  difference, compliance, counterfactuals, and related failures from a single accuracy
  number.
task_format: >
  Extra-long document QA: page-image or OCR context (or a PDF agent), a free-form or
  typed answer, scored by a deterministic rule; gold evidence pages are withheld at
  inference.
metric:
  name: rule-based accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Primary metric is accuracy under the item's typed rule (exact match, numeric
    tolerance, percentage match, alias/string rules, or abstention for None). Token
    F1 and ANLS are secondary. Failed, missing, or unparsable outputs count as wrong.
    The paper's strongest pipeline is SimpleDoc+GPT-5.4 at 44.0% on the 1,519-item
    set. The Hugging Face strict release reports GPT-5.4 OCR at 38.36% on 1,345 items.
dataset:
  size: 1345
  size_note: >
    The paper's fully verified evaluation set has 1,519 questions over 331 documents
    (98,342 pages; mean 297.1 pages; median 211; max document 2,062 pages; longest
    multi-document context 2,303 pages). Construction started from 3,550 candidates;
    2,104 passed expert verification before difficulty filtering. Hugging Face ships
    a conservative subset: 1,345 questions (1,191 single-document, 154 cross-document)
    over 292 documents after dropping 174 questions whose source URLs were marked
    RAG Not Approved. Paper slices: 1,103 multi-page (72.6%), 556 multimodal (36.6%),
    165 cross-document (10.9%), 218 None answers (14.4%). Domain counts in the paper:
    311 legal, 333 finance, 274 technical, 294 medical, 218 scientific, 89 narrative.
  url: https://huggingface.co/datasets/microsoft/XL-DocBench
  license: other
  languages:
    - en
  modalities:
    - text
    - image
  splits: test-only public release (single_doc and cross_doc configs); PDFs are linked, not redistributed
  public_test_set: true
publisher:
  org: "Microsoft Research Asia and Wuhan University"
  authors:
    - Hongchen Wei
    - Yuanzhe Wang
    - Bei Liu
    - Yifan Yang
    - Qi Dai
    - Ruichun Ma
    - Kai Qiu
    - Yunsheng Li
    - Dongdong Chen
    - Chong Luo
    - Zhenzhong Chen
    - Baining Guo
  url: https://officeintelligence.github.io/xl-docbench/
paper:
  title: "XL-DocBench: Benchmarking Evidence-Grounded Extra-Long Document Understanding"
  arxiv: "2608.00036"
  url: https://arxiv.org/abs/2608.00036
  year: 2026
leaderboard_url: https://officeintelligence.github.io/xl-docbench/#leaderboard
repo_url: https://huggingface.co/datasets/microsoft/XL-DocBench
released: "2026-07"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: docvqa
  successors: []
  variants: []
saturation:
  status: open
  top_score: 44.0
  as_of: "2026-07"
  note: >
    SimpleDoc+GPT-5.4 reached 44.0% on the paper's 1,519-item set. Claude Opus 4.6
    OCR reached 39.8% as the strongest one-shot reader. Ranking, coverage, and
    set-difference stayed at or below 36.4% even for the best systems. The public
    strict subset's top score is 38.36% (GPT-5.4 OCR).
contamination:
  risk: medium
  note: >
    Source documents are public professional files, so page text may appear in
    pretraining. Questions were model-proposed then verified by 194 experts, and a
    no-context filter drops items answerable without the documents. The Hugging Face
    release further drops RAG-restricted URLs. Gold evidence pages are not given
    to the model at test time.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "microsoft/XL-DocBench bundled evaluate.py"
tags:
  - long-context
  - document-understanding
  - multimodal
  - retrieval
  - abstention
sources:
  - url: https://arxiv.org/abs/2608.00036
    title: "XL-DocBench paper (arXiv abs, 2608.00036)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2608.00036v1
    title: "XL-DocBench HTML full text (arXiv html)"
    accessed: "2026-09-08"
  - url: https://officeintelligence.github.io/xl-docbench/
    title: "XL-DocBench project homepage and leaderboard"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/microsoft/XL-DocBench
    title: "microsoft/XL-DocBench dataset card (strict 1,345-item release)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-084 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

XL-DocBench asks a document system to answer a professional question from contexts that can run to hundreds or thousands of pages. Typical sources are reports, regulations, clinical guidelines, and manuals. Most items need more than one evidence page. Some need tables, charts, or figures. A smaller slice needs related PDFs. Two hundred-odd items are unanswerable from the given files, so a correct output is to abstain.

The model does not see the expert evidence pages at test time. It must search, read, combine, and apply the typed rule. Twelve reasoning labels sit in three tiers: core (comparison, reference chain), structural (ranking, coverage, reconciliation), and advanced (set difference, unanswerable, temporal, compliance, counterfactual, aggregation, consistency).

## How it is scored

Headline accuracy is deterministic. Integer answers need a normalised exact match. Floats use units, rounding, and a stated tolerance. Strings use aliases. None answers require an abstention. Token F1 and ANLS are extras. Paper runs compare full page images, OCR truncated to 80% of the context window, and PDF agents (MDocAgent, SimpleDoc, DeepRead). Missing or unparsable predictions are wrong.

On the 1,519-item paper set, SimpleDoc+GPT-5.4 reached 44.0%. Claude Opus 4.6 OCR reached 39.8%. The Hugging Face strict subset of 1,345 items reports GPT-5.4 OCR at 38.36% as the top of 13 fully scored systems.

## Dataset and licence

The paper keeps 1,519 of 3,550 synthetic candidates after 194 experts re-answer, mark pages and quotes, and check rules. Hugging Face `microsoft/XL-DocBench` is a later conservative dump: 1,345 questions, 292 documents, licence `other`. PDFs are not shipped; rows point at public URLs and inherit those documents' terms. The card says the filter removed RAG Not Approved sources (174 questions, 39 documents). Some released questions are not English-only even though the paper frames the task in English. The comparison table in the paper dates the benchmark 2026-04; arXiv v1 is 21 July 2026; the Hub dump is dated 2 September 2026.

## Who publishes it

Hongchen Wei and Zhenzhong Chen (Wuhan University) with Yuanzhe Wang, Bei Liu, Yifan Yang, Qi Dai, Ruichun Ma, Kai Qiu, Yunsheng Li, Dongdong Chen, Chong Luo, and Baining Guo (Microsoft). Wei and Wang are equal contributors; Liu is project leader. The homepage is officeintelligence.github.io/xl-docbench/.

## Lineage

XL-DocBench extends page-level document QA toward extra-long, evidence-audited professional files. This repository already has [DocVQA](docvqa.md), [ChartQA](chartqa.md), [InfiniteBench](infinitebench.md), and [Dr. DocBench](dr_docbench.md). Cited neighbours without pages here include MP-DocVQA, DUDE, SlideVQA, MMLongBench-Doc, LongDocURL, and DocBench. It is not an alias of Dr. DocBench, which is an expert parsing test, not extra-long QA.

## Saturation and contamination

The best paper pipeline still fails more than half the items. Set-tracking types stay under 37%. Agents help only when retrieval returns compact evidence; some agents hurt abstention. Public source PDFs make document-text contamination plausible. The no-context filter and human evidence checks reduce question-only shortcuts.

## How to run it

Load `microsoft/XL-DocBench` and score with the bundled `code/evaluate.py`. Do not feed gold evidence pages to the model. State whether you used the paper's 1,519-item set or the 1,345-item Hub subset, and whether input was images, OCR, or an agent. No lm-eval task name was found.

## Reading the numbers

44% is the paper's best on the full verified set, not the Hub subset. A long context window is not the whole story: two 1M-token readers still differ, and retrieval can beat or lose to OCR. High unanswerable accuracy with low ranking accuracy means the system knows when to stop more than it can track a set. Always report reasoning type, input mode, and which release you scored.
