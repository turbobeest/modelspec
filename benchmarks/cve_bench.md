---
id: cve_bench
name: "CVE-Bench"
aliases:
  - "CVE-Bench"
page_kind: benchmark
category: agentic
subcategory: "autonomous exploitation of real-world web-application CVEs in a live sandbox"
status: active
summary: "Tests whether an autonomous LLM agent can actually exploit 40 real, critical-severity web application CVEs inside a live sandbox, not whether it can answer security questions."
measures: >
  CVE-Bench measures whether an autonomous LLM agent can exploit real, critical-severity web
  application vulnerabilities inside a live sandbox, rather than whether a model can answer
  questions about security. Each of its 40 tasks corresponds to one real CVE from the National
  Vulnerability Database, hosted as a running, vulnerable web application in a set of Docker
  containers alongside a reference exploit the authors built to confirm the vulnerability is
  genuinely reachable. The agent must plan, issue tool calls, and observe results across multiple
  steps to achieve one of eight standardized attack goals -- this is why this page categorizes it
  as agentic rather than domain: scoring depends on live, multi-step interaction with a real
  system, not on a static answer.
task_format: >
  An LLM agent is placed against a live, vulnerable target container and must achieve one of eight
  standardized attack goals (denial of service, file access, file creation, database modification,
  database access, unauthorized administrator login, privilege escalation, or an outbound-service
  request), graded automatically. Each CVE is run under two settings: zero-day (the agent gets only
  a task description and must find the vulnerability itself) and one-day (the agent additionally
  gets a high-level description of the known vulnerability). The paper reports success@1 and
  success@5 across five independent attempts.
metric:
  name: "attack success rate (fraction of the 40 CVEs where an agent achieves any one of the eight standard attack goals)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's headline results put its best agent-and-tooling combination at up to 13% success
    under the harder zero-day setting and up to 25% under the one-day setting, both at five
    attempts. A bare, cybersecurity-specialized agent (Cy-Agent, adapted from Cybench) reached only
    2.5% success in the easier one-day setting; equipping a team-based agent with the sqlmap tool
    substantially improved results. No random-guess or human baseline applies to this task, and none
    is reported.
dataset:
  size: 40
  size_note: >
    40 CVEs selected from the National Vulnerability Database: web-application vulnerabilities
    only, in free and open-source software, published in a six-week window from 1 May to 14 June
    2024, excluding platform-dependent (for example Windows-only) and non-reproducible CVEs. Every
    included CVE carries a CVSS v3.1 base severity score of at least 9.0 ("critical"), with 21 of
    the 40 rated between 9.6 and 9.8; 24 of the 40 have login interfaces backed by separate
    databases. Application types: content management 12 (e.g. WordPress), AI or machine learning 7
    (e.g. LoLLMs), business management 6, operational monitoring 4, web infrastructure 3, library
    or package 3, e-commerce 2, and one each of computing management, mail server and web portal.
  url: "https://github.com/uiuc-kang-lab/cve-bench"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "no train/test split; all 40 CVE tasks form a single fixed evaluation set, each run under both the zero-day and one-day settings"
  public_test_set: true
publisher:
  org: "University of Illinois Urbana-Champaign (Kang Lab)"
  authors:
    - "Yuxuan Zhu"
    - "Antony Kellermann"
    - "Dylan Bowman"
    - "Philip Li"
    - "Akul Gupta"
    - "Adarsh Danda"
    - "Richard Fang"
    - "Conner Jensen"
    - "Eric Ihli"
    - "Jason Benn"
    - "Jet Geronimo"
    - "Avi Dhir"
    - "Sudhit Rao"
    - "Kaicheng Yu"
    - "Twm Stone"
    - "Daniel Kang"
  url: "https://github.com/uiuc-kang-lab/cve-bench"
paper:
  title: "CVE-Bench: A Benchmark for AI Agents' Ability to Exploit Real-World Web Application Vulnerabilities"
  arxiv: "2503.17332"
  url: "https://arxiv.org/abs/2503.17332"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/uiuc-kang-lab/cve-bench"
released: "2025-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 25.0
  as_of: "2025-03"
  note: >
    The paper's own headline numbers, up to 13% success under the zero-day setting and 25% under
    the one-day setting at five attempts, leave most of the 40 vulnerabilities unexploited by every
    agent configuration tested, and the authors frame this as evidence of a real but still limited
    threat rather than a solved task. Because scores depend heavily on which agent scaffold and
    tools wrap the underlying model, a higher score does not necessarily mean a stronger base LLM;
    it can just as easily mean better tooling or orchestration. No score newer than the original
    paper's own evaluation was found in the sources read for this page.
contamination:
  risk: medium
  note: >
    Exploiting a live sandbox cannot be done by regurgitating memorized text alone, unlike a static
    question-answering benchmark. But all 40 CVEs are public NVD entries from a specific, narrow
    disclosure window, and critical-severity CVEs commonly attract public proof-of-concept exploits
    and writeups soon after disclosure. An agent that has memorized a public PoC for one of these
    specific CVEs could succeed without doing the discovery or exploitation reasoning the benchmark
    is meant to test, which matters most in the one-day setting, where the agent is explicitly told
    which vulnerability to target.
harness:
  lm_eval: ""
  inspect_evals: "cve_bench (ships as an isolated package with its own dependencies; supports Docker and Kubernetes sandbox backends; the Kubernetes backend currently supports only a subset of the 40 CVEs)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - agentic
  - security
  - cybersecurity
  - cve
  - sandbox
  - exploitation
sources:
  - url: "https://arxiv.org/abs/2503.17332"
    title: "CVE-Bench: A Benchmark for AI Agents' Ability to Exploit Real-World Web Application Vulnerabilities"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.17332"
    title: "CVE-Bench (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/uiuc-kang-lab/cve-bench"
    title: "uiuc-kang-lab/cve-bench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cve_bench"
    title: "inspect_evals cve_bench task"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

CVE-Bench measures whether an autonomous LLM agent can exploit real, critical-severity web application vulnerabilities inside a live sandbox, rather than whether a model can answer questions about security. Each of its 40 tasks corresponds to one real CVE from the National Vulnerability Database, hosted as a running, vulnerable web application in Docker containers alongside a reference exploit confirming the vulnerability is genuinely reachable. The agent must plan, issue tool calls, and observe results across multiple steps to achieve one of eight standardized attack goals, which is why this page categorizes CVE-Bench as agentic rather than domain: scoring depends on live, multi-step interaction with a real system, not a static answer.

CVE-Bench also simulates two points in a vulnerability's disclosure lifecycle. Under the zero-day setting, the agent gets only a task description and must discover the vulnerability itself; under the one-day setting, it additionally gets a high-level description of the known vulnerability, closer to how a real attacker would work once a CVE is public.

## How it is scored

Success is measured against eight standardized attack goals, each independently graded by an automated checker: denial of service, file access, file creation, database modification, database access, unauthorized administrator login, privilege escalation, and an outbound-service request that makes the target server call an attacker-controlled endpoint. An agent succeeds if it achieves any one goal; the paper reports success@1 and success@5 over five attempts. The headline numbers -- up to 13% success under zero-day and 25% under one-day -- came from the strongest agent-and-tooling combination tried. A bare, cybersecurity-specialized agent (Cy-Agent, adapted from Cybench) reached only 2.5% in the easier one-day setting, while giving a team-based agent the sqlmap tool substantially improved results -- the paper's central methodological point: the score measures a whole agent system, not the underlying LLM alone.

## Dataset and licence

The 40 CVEs come from the National Vulnerability Database: web-application vulnerabilities only, in free and open-source software, published in a six-week window from 1 May to 14 June 2024, excluding platform-dependent and non-reproducible CVEs. Every one carries a CVSS v3.1 base severity of at least 9.0 ("critical"), with 21 of the 40 rated 9.6-9.8. Application types skew toward content management systems such as WordPress (12 CVEs) and AI or machine-learning tools such as LoLLMs (7), with the rest spread across business management, monitoring, infrastructure, libraries and e-commerce. Data and code are released on GitHub under the Apache 2.0 licence.

## Who publishes it

CVE-Bench comes from a 16-author team led by Yuxuan Zhu and Daniel Kang at the University of Illinois Urbana-Champaign (the full author list is in this page's front matter), first posted to arXiv in March 2025. The uiuc-kang-lab GitHub organisation hosts the reference implementation and sandbox definitions.

## Lineage

CVE-Bench has no predecessor or successor tracked in this repository. The authors built it explicitly to match the scale of Cybench, an earlier capture-the-flag-style cybersecurity benchmark for LLM agents that CVE-Bench also reuses as one of its own baseline agents (Cy-Agent). CVE-Bench itself is built around real, unabstracted web-application CVEs rather than CTF-style puzzles; Cybench does not have its own page here.

## Saturation and contamination

CVE-Bench is far from saturated: the headline numbers, up to 13% success under zero-day and 25% under one-day, leave most vulnerabilities unexploited by every agent configuration tested, and the authors frame this as a real but still limited threat rather than a solved task. Because scores depend heavily on the agent scaffold and tools wrapping the model, a higher score does not necessarily mean a stronger base LLM -- it can just as easily mean better tooling. Contamination works differently here than for static benchmarks: exploiting a live sandbox cannot be done by regurgitating memorized text alone, but all 40 CVEs are public NVD entries from a narrow disclosure window, and critical-severity CVEs commonly attract public proof-of-concept exploits soon after disclosure. An agent that memorized a public PoC for one of these CVEs could succeed without the discovery or exploitation reasoning the benchmark is meant to test -- which matters most in the one-day setting, where the agent is told which vulnerability to target.

## How to run it

The reference implementation runs each CVE as a set of Docker containers -- typically the web application, its database, and auxiliary services -- alongside a reference exploit confirming reproducibility. inspect_evals packages CVE-Bench as an isolated task with its own dependencies, supporting Docker and Kubernetes sandbox backends; Kubernetes currently covers only a subset of the 40 CVEs. Standing up live, exploitable infrastructure rather than calling an API makes CVE-Bench far more demanding to reproduce than a typical text benchmark, which is itself a reason to expect fewer independent replications of any published score.

## Reading the numbers

A CVE-Bench score describes an entire agent system attacking real infrastructure, not a pure measure of a language model's knowledge -- check which agent scaffold and which tools, such as sqlmap, were available before comparing two numbers. Reading the score also means reading its threat model: it reflects offensive capability against 40 already-disclosed, mid-2024 vulnerabilities under sandboxed conditions, not a general estimate of what an agent could do against unpatched or novel vulnerabilities in the wild. A low score is reassuring only within that scope -- it says little about zero-day discovery against vulnerability classes the 40 CVEs do not represent, or attacks outside the eight standardized goals. Prefer the harder zero-day setting when the real question is whether an agent can find vulnerabilities on its own, since the one-day setting hands it most of the discovery work already done.
