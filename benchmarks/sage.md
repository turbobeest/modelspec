---
id: sage
name: SAGE
aliases:
  - Sage
  - "Scientific AGentic retrieval Evaluation"
page_kind: benchmark
category: agentic
subcategory: "scientific literature retrieval for deep-research agents"
status: active
summary: >
  1,200 scientific-literature queries over a closed paper corpus that tests whether
  deep-research agents retrieve the right papers, not just browse the open web.
measures: >
  SAGE (Scientific AGentic retrieval Evaluation) scores a deep-research agent on
  finding papers, not on writing a report. Each item is an English research query
  over a domain-specific corpus of open-access PDFs. Short-form items have one
  target paper and mix venue metadata, figure or table details, and citation overlap.
  Open-ended items mimic a literature-review request and have a ranked set of relevant
  papers. The skill under test is multi-step retrieval with sub-queries, not single-shot
  RAG. The authors contrast native web search with a controlled corpus-search tool.
task_format: >
  English query in; the agent may think, issue search sub-queries, and answer with
  text plus citations. Short-form items ask for one paper. Open-ended items ask for
  a set of related papers.
metric:
  name: "exact match (short-form); weighted recall (open-ended)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Short-form exact match checks whether the unique target paper appears in the
    answer text or citations. Open-ended weighted recall uses gains 2 / 1 / 0 for
    the seed pair, their shared references, and everything else. No human baseline
    was reported. Web-search and corpus-search numbers are not interchangeable.
dataset:
  size: 1200
  size_note: >
    1,200 queries: 600 short-form and 600 open-ended, 150 of each in computer science,
    natural science, healthcare, and humanities. The abstract describes a 200,000-paper
    corpus (about 50,000 open-access PDFs per domain). Table 1 lists smaller per-split
    database sizes; humanities short-form is 39,032 papers and humanities open-ended
    is 37,506, because older literature was excluded. GitHub ships the queries, not
    the PDF corpus.
  url: "https://github.com/HughieHu/Sage"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "600 short-form + 600 open-ended; four domains; no separate hidden test split"
  public_test_set: true
publisher:
  org: "NYU Shanghai, Yale University, and New York University Center for Data Science"
  authors:
    - Tiansheng Hu
    - Yilun Zhao
    - Canyu Zhang
    - Arman Cohan
    - Chen Zhao
  url: "https://github.com/HughieHu/Sage"
paper:
  title: "SAGE: Benchmarking and Improving Retrieval for Deep Research Agents"
  arxiv: "2602.05975"
  url: "https://arxiv.org/abs/2602.05975"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/HughieHu/Sage"
released: "2026-02"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 71.7
  as_of: "2026-02"
  note: >
    Under native web search, GPT-5 reached 71.7% mean short-form exact match and
    26.3% mean open-ended weighted recall (paper Table 2, 2026-02). With DR Tulu
    restricted to the authors' corpus, BM25 at k=10 reached 81.2% short-form exact
    match; gte-Qwen2-7B-instruct at k=10 reached 33.0% open-ended weighted recall.
    Open-ended scores remain far from 100.
contamination:
  risk: medium
  note: >
    Queries, paper titles, and Semantic Scholar-style ids are public on GitHub.
    The paper says seed papers were published after 2024 to limit pretraining
    leakage. The released computer-science short-form file includes 2023 venue
    papers such as ReConcile (ACL 2023), so that date filter is not a complete
    description of the public set.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No lm-evaluation-harness, inspect_evals, HELM, OpenCompass, or BIG-bench task
    was found. The paper evaluates proprietary deep-research APIs and a modified
    DR Tulu MCP tool that can only search the authors' corpus.
tags:
  - agentic
  - retrieval
  - scientific-literature
  - deep-research
  - english
sources:
  - url: "https://arxiv.org/abs/2602.05975"
    title: "SAGE: Benchmarking and Improving Retrieval for Deep Research Agents (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2602.05975v2"
    title: "SAGE HTML full text, arXiv 2602.05975v2"
    accessed: "2026-09-08"
  - url: "https://github.com/HughieHu/Sage"
    title: "HughieHu/Sage GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/HughieHu/Sage/main/README.md"
    title: "Sage Benchmark README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/HughieHu/Sage/main/Sage_Short_Form_Questions/computer_science.json"
    title: "Sage short-form computer-science queries (public JSON)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/HughieHu/Sage"
    title: "HughieHu/Sage GitHub API (created date; license field empty)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-080 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SAGE asks a deep-research agent to find scientific papers from an English query. Short-form items give venue, figure or table clues, and citation overlap, and there is one correct paper. Open-ended items look like a related-work search and have many relevant papers. The agent may search several times, then answer with text and citations.

The test is retrieval, not report quality. Native web search and a closed PDF corpus are separate protocols. The corpus uses open-access PDFs so retrievers can be swapped.

## How it is scored

Short-form scoring is exact match: the target paper must appear in the output or citations. Open-ended scoring is weighted recall. The two seed papers score 2, papers cited by both score 1, and other papers score 0. The paper uses a linear gain. Maximum on both metrics is 100. No random or human baseline was given.

Table 2 (2026-02) is the main comparison. With web search, GPT-5 averaged 71.7% short-form exact match and 26.3% open-ended weighted recall. DR Tulu scored 42.0% and 17.4%. Gemini-2.5-Pro scored 38.5% and 11.0%. Those web-search runs are not the same as corpus search. On the authors' corpus, DR Tulu plus BM25 at k=10 reached 81.2% short-form exact match. gte-Qwen2-7B-instruct at k=10 reached 33.0% open-ended weighted recall, slightly above BM25's 30.7%. ReasonIR lagged both.

## Dataset and licence

There are 1,200 queries, 150 short-form and 150 open-ended in each of four domains. The paper describes a 200,000-paper corpus of open-access PDFs, about 50,000 per domain. Table 1 is more precise: humanities short-form has 39,032 papers and humanities open-ended has 37,506. Ground-truth count is one paper for every short-form item. Open-ended items average between 9.94 and 17.62 gold papers by domain.

Questions were built with GPT-5-mini from metadata, figures, tables, and papers that share at least four references. The GitHub README calls the queries expert-curated; the paper describes LLM generation. The public JSON includes 2023 papers, against the paper's after-2024 wording. The arXiv HTML is CC BY 4.0. The GitHub API listed no repository licence. The PDF corpus is not in the repo.

## Who publishes it

Tiansheng Hu, Yilun Zhao, Canyu Zhang, Arman Cohan, and Chen Zhao released the work in February 2026. Affiliations are NYU Shanghai, Yale, and NYU's Center for Data Science. Queries live at HughieHu/Sage. No public leaderboard was found.

## Lineage

SAGE is a closed-corpus retrieval test for deep-research agents. It is not Princeton SAgE (Science of Agent Evaluation), not the service-agent SAGE in arXiv 2604.09285, and not SageMath. [BrowseComp](browsecomp.md) and [DeepSearchQA](deepsearchqa.md) also stress multi-step search, but they use the live web and grade short answers, not paper ids. The paper cites BrowseComp-Plus as related short-form work; that name has no page here.

## Saturation and contamination

Short-form web-search scores still spread from 38% to 72%. Open-ended scores sit in the teens to low thirties. The ceiling is not reached. Queries and titles are public, so a later model could memorize the GitHub files. The paper tried to use recent papers to cut pretraining leakage. The released computer-science file still contains 2023 ACL and similar papers, so treat that claim as incomplete.

## How to run it

Clone HughieHu/Sage for the JSON queries. Short-form fields are `complete_query` and `ground_truth`. Open-ended fields include `most_relevant` and `relevant` paper lists. There is no lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task. The paper's corpus-search setup converts PDFs to markdown, embeds the first 32,000 tokens, and lets DR Tulu search only that index. The PDFs themselves are not in the GitHub tree. A web-search number and a BM25 corpus number are different experiments. Say which protocol you used, and whether documents were keyword-augmented.

## Reading the numbers

A high short-form exact match means the agent named the intended paper, not that it understood the science. Open-ended weighted recall can look decent while missing one of the two seed papers. BM25 beating ReasonIR here tracks keyword-like sub-queries, not a general ranking of retrievers. Compare SAGE with [BrowseComp](browsecomp.md) or [DeepSearchQA](deepsearchqa.md) only if you also report search backend, iteration cap, and whether the corpus was rewritten at test time.
