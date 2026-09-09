---
id: the_facts_grounding_leaderboard
name: "The FACTS Grounding Leaderboard"
aliases:
  - "FACTS Grounding"
  - "FACTS Grounding v1"
page_kind: benchmark
category: generation
subcategory: "long-form answers grounded in a supplied document (up to 32k tokens)"
status: active
summary: "Google FACTS Grounding scores whether long-form answers stay faithful to a supplied document, using an ensemble of LLM judges plus an eligibility filter."
measures: >
  FACTS Grounding checks scenario-one factuality: every claim in a long-form answer
  must be supported by a document in the prompt, not by parametric world knowledge.
  Each example has a system instruction ("use only this context"), a user request
  (QA, summary, rewrite) and a web-sourced document up to 32k tokens (mean about
  2.5k). The request must be non-trivial and must not need extra-document expertise,
  maths, or creative writing. This is attribution to provided context, not closed-book
  factoids and not web search.
task_format: >
  Single-turn generation: system instruction plus user request plus full document.
  Judges then run two stages, eligibility then span/response-level grounding.
metric:
  name: "final factuality score (share of responses that are eligible and fully grounded, averaged over three judges)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    v1 judges are Gemini 1.5 Pro, GPT-4o and Claude 3.5 Sonnet, each with a prompt
    picked by Macro-F1 on a 402-example private set. Unadjusted score is the mean of
    the three judges' accurate rates. A response is ineligible only if all three
    judges mark a major instruction-following failure; ineligible replies count as
    inaccurate. Paper Table 6 top row: Gemini 2.0 Flash Experimental 83.6 after that
    filter.
dataset:
  size: 1719
  size_note: >
    860 public Open examples plus 859 private Blind examples. Hugging Face
    google/FACTS-grounding-public hosts the 860-row public CSV (system_instruction,
    user_request, context_document, full_prompt) and evaluation_prompts.csv.
  url: "https://huggingface.co/datasets/google/FACTS-grounding-public"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "Open (public, n=860) / Blind (private, n=859)"
  public_test_set: false
publisher:
  org: "Google DeepMind, Google Research, Google Cloud, and Kaggle"
  authors:
    - "Alon Jacovi"
    - "Andrew Wang"
    - "Chris Alberti"
    - "Connie Tao"
    - "Jon Lipovetz"
    - "Kate Olszewska"
    - "Lukas Haas"
    - "Michelle Liu"
    - "Nate Keating"
    - "Dipanjan Das"
  url: "https://www.kaggle.com/facts-leaderboard"
paper:
  title: "The FACTS Grounding Leaderboard: Benchmarking LLMs' Ability to Ground Responses to Long-Form Input"
  arxiv: "2501.03200"
  url: "https://arxiv.org/abs/2501.03200"
  year: 2025
leaderboard_url: "https://www.kaggle.com/facts-leaderboard"
repo_url: "https://www.kaggle.com/code/andrewmingwang/facts-grounding-benchmark-starter-code"
released: "2024-12"
last_updated: "2025-01"
lineage:
  family: ""
  predecessor: ""
  successors:
    - the_facts_leaderboard
  variants: []
saturation:
  status: open
  top_score: 83.6
  as_of: "2025-01"
  note: >
    Paper Table 6 (final score after eligibility filter) lists Gemini 2.0 Flash
    Experimental at 83.6 and o1-preview at 61.7. Grounding v2 in the later FACTS
    suite uses different judges and is not this number.
contamination:
  risk: medium
  note: >
    Context documents were scraped from the web and may appear in pretraining. User
    requests and the "context-only" system instructions are new. A private split
    exists. The metric penalises using extra-document knowledge even when that
    knowledge is true.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Kaggle starter notebook (facts-grounding-benchmark-starter-code)"
tags:
  - factuality
  - grounding
  - long-context
  - llm-as-judge
sources:
  - url: "https://arxiv.org/abs/2501.03200"
    title: "FACTS Grounding paper (arXiv:2501.03200v1)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2501.03200"
    title: "FACTS Grounding HTML full text"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google/FACTS-grounding-public"
    title: "google/FACTS-grounding-public dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google/FACTS-grounding-public"
    title: "Hugging Face API metadata (license cc-by-4.0, 860 public rows)"
    accessed: "2026-09-08"
  - url: "https://www.kaggle.com/facts-leaderboard"
    title: "FACTS Grounding Kaggle leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FACTS Grounding gives the model a long document and a user request, then asks for a long answer that uses only that document. A single ungrounded claim fails the item.

Tasks include summarising, extracting facts and rewriting, across finance, technology, retail, medical and legal pages. Annotators dropped creative writing, expert-only items, maths and OCR-broken PDFs. The skill is faithfulness to provided context, not being right about the world.

## How it is scored

v1 uses three judges (Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet). Each judge first decides whether the answer actually addresses the request. If all three call a major instruction miss, the answer is ineligible and counts as inaccurate. Surviving answers are labelled accurate only if every information-bearing claim is grounded.

The published factuality score is the mean of the three judges after that filter. The paper also reports an unadjusted score and a Condorcet fused rank. Self-preference was measured at about +3.23% when a model judged itself. Eligibility filtering cut scores by roughly 1-5 points and swapped Gemini 1.5 Flash from fused rank 1 to rank 2.

## Dataset and licence

1,719 examples: 860 public, 859 private. Hugging Face `google/FACTS-grounding-public` is tagged `license: cc-by-4.0` and shows 860 public rows. The dataset card also ships judge prompt templates. The paper licence is CC BY 4.0.

There are no gold long-form answers in the public CSV. Scoring is always judge-based. The private split is how Kaggle scores unofficial submissions.

## Who publishes it

Google DeepMind, Google Research, Google Cloud and Kaggle. Equal-contribution leads on the paper include Jacovi, Wang, Alberti, Tao, Lipovetz, Olszewska, Haas, Liu, Keating and Das. Hugging Face created the public dataset on 2024-12-18. arXiv v1 is 6 January 2025.

Kaggle hosts the leaderboard and starter notebook. Live rows may move after the paper table.

## Lineage

This page is Grounding v1 (arXiv:2501.03200). [the_facts_leaderboard](the_facts_leaderboard.md) is the December 2025 FACTS suite. That suite keeps these prompts as Grounding v2 but swaps judges to Gemini 2.5 Flash and GPT-5.

Related but different: [simpleqa](simpleqa.md) is closed-book short factoids. Long-form web factuality papers (FActScore, LongFact) are not this document-grounding task.

The Hugging Face citation block titles the dataset "FACTS Leaderboard" even though this file is the grounding-only v1 eval. Use the arXiv title when you need to disambiguate.

## Saturation and contamination

Paper-era top score is 83.6, with a 22-point spread down to o1-preview. That is not saturated. Grounding v2 later reports lower absolute scores with newer judges; do not mix v1 83.6 with suite Grounding columns.

Documents may be in pretraining. The authors argue the novel requests still test grounding, and that using memorised facts against the document should hurt. Private items reduce public overfitting.

## How to run it

Public prompts: Hugging Face CSV. Starter code: the Kaggle notebook named in `repo_url`. There is no confirmed lm-eval or inspect_evals task id.

A local run that changes judge models, drops the eligibility filter, or scores only the public split will not match Kaggle. v1 numbers need the three v1 judges; v2 numbers need the suite judges.

## Reading the numbers

A high v1 score means judges found the long answer both on-task and fully supported by the supplied document. It does not mean the model is generally truthful without a document, and it does not mean it can search.

Short, empty answers can look grounded; that is why eligibility exists. When a vendor quotes "FACTS", check whether they mean this grounding leaderboard or the four-track [the_facts_leaderboard](the_facts_leaderboard.md) average.
