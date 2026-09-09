---
id: agent_threat_bench
name: AgentThreatBench
aliases: []
page_kind: benchmark
category: safety
subcategory: agent security / prompt-injection and goal-hijack resistance (OWASP Agentic Top 10)
status: active
summary: Small Inspect AI suite that scores whether an LLM agent completes its task and separately whether it resists prompt-injection attacks drawn from the OWASP Agentic Top 10.
measures: >
  AgentThreatBench gives an agent an ordinary task -- answer a question from a memory store,
  triage an email inbox, resolve a customer-support ticket -- where one of the tool outputs the agent
  reads (a memory entry, an email body, a customer record) has been seeded with an adversarial
  instruction trying to redirect the agent's behaviour. It tests whether the agent both finishes the
  legitimate task and refuses to be manipulated by the embedded attack, scoring the two outcomes
  independently rather than folding them into one number. The three tasks operationalise two categories
  from the OWASP Top 10 for Agentic Applications (2026), namely memory and context poisoning and agent
  goal hijack via indirect prompt injection.
task_format: Three separate Inspect AI tasks, each a small set of multi-turn tool-use scenarios with an
  adversarial payload embedded in one tool's output; the agent calls tools to complete its task while a
  dual grader checks task completion and whether the embedded attack succeeded.
metric:
  name: 'dual binary metric per sample: utility (task completed correctly) and security (attack
    resisted), each graded CORRECT (1.0) or INCORRECT (0.0) by task-specific criteria, reported as two
    separate percentages rather than combined into one score'
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: 'The suite''s own documentation frames results as a 2x2 read: high utility/high
    security means the agent is capable and robust; high utility/low security means it completes tasks
    but is manipulable; low utility/high security means it is over-cautious; low utility/low security
    means it fails at both. No random or human baseline is defined by the source.'
dataset:
  size: 24
  size_note: '24 samples across three fixed task datasets: memory_poison (10 samples: direct
    instruction injection, context poisoning, gradual poisoning, authority impersonation, delimiter
    escape, multi-vector poisoning, role hijack, and clean baselines, with easy/medium samples using
    append-style attacks and hard samples using replacement-style attacks), autonomy_hijack (6 samples:
    inline injection, progressive goal drift, authority escalation, multi-step social engineering,
    encoded payloads, and clean baselines, embedded in email-triage tool output), and data_exfil (8
    samples: social-engineering exfiltration, redirect via tool output, impersonation, urgency
    pressure, JSON injection, and clean baselines, embedded in customer-support tool output).'
  url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agent_threat_bench
  license: MIT (the inspect_evals package licence; no separate licence is stated for this task's own
    data files)
  languages:
  - en
  modalities:
  - text
  splits: No train/test split; three fixed evaluation sets (10, 6 and 8 samples), with memory_poison
    samples additionally taggable by difficulty (easy, medium, hard).
  public_test_set: true
publisher:
  org: Inspect Evals (UK AI Security Institute, in collaboration with Arcadia Impact and the Vector
    Institute); this specific suite was community-contributed
  authors:
  - vgudur-dev (GitHub handle; no fuller author name given in the source)
  url: https://github.com/UKGovernmentBEIS/inspect_evals
paper:
  title: ''
  arxiv: ''
  url: ''
  year: null
leaderboard_url: ''
repo_url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agent_threat_bench
released: '2026-05'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: No published per-model results were found in the sources reviewed; the benchmark is new
    (added to inspect_evals in version 0.12.0, dated 2026-05-14) and has no known leaderboard.
contamination:
  risk: medium
  note: All 24 samples and their grading logic are public in the inspect_evals GitHub repository. The
    suite is recent (added May 2026), so most models trained before that date could not have seen it,
    but any model trained on a crawl of the inspect_evals repository after that point could have, and
    the exact attack scenarios are easy to reproduce from the public source.
harness:
  lm_eval: ''
  inspect_evals: agent_threat_bench_memory_poison, agent_threat_bench_autonomy_hijack,
    agent_threat_bench_data_exfil
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- safety
- agentic
- prompt-injection
- agent-security
- owasp
sources:
- url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/agent_threat_bench/README.md
  title: inspect_evals AgentThreatBench README (task descriptions, attack types, scoring)
  accessed: '2026-09-08'
- url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agent_threat_bench
  title: inspect_evals agent_threat_bench task directory
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/agent_threat_bench/eval.yaml
  title: agent_threat_bench eval.yaml (registry metadata -- group, tasks, sample counts, contributor)
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/CHANGELOG.md
  title: inspect_evals CHANGELOG.md (confirms addition in v0.12.0, 2026-05-14)
  accessed: '2026-09-08'
- url: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
  title: OWASP Top 10 for Agentic Applications (2026) -- the threat taxonomy this suite operationalises
  accessed: '2026-09-08'
- url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/README.md
  title: 'inspect_evals top-level README (project origin: UK AISI, Arcadia Impact, Vector Institute)'
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

## What it measures

AgentThreatBench checks whether an LLM agent can do useful work while resisting adversarial
manipulation hidden inside the data it reads, rather than checking task competence alone. Each of its
three tasks gives the agent an ordinary job -- answer a question using entries from a memory store,
triage an inbox of emails, or resolve a customer-support ticket -- where the tool output the agent
consumes has been seeded, in most samples, with an instruction trying to redirect its behaviour: a fake
authority claim, a gradually escalating request, an encoded payload, or a request to leak sensitive
data to an unauthorized recipient. Some samples are clean baselines with no attack, used to check that a
model does not become so cautious it fails ordinary requests. The three tasks cover two categories from
the OWASP Top 10 for Agentic Applications (2026): memory and context poisoning (ASI06), and agent goal
hijack via indirect prompt injection (ASI01), the latter tested through two different tool surfaces
(email triage and customer support).

## How it is scored

Every sample is graded on two independent binary outcomes: utility, whether the agent actually
completed its assigned task, and security, whether it avoided being manipulated by the embedded attack.
Each is CORRECT (1.0) or INCORRECT (0.0) by task-specific criteria -- for example, in the data-exfiltration
task, utility requires the agent to resolve the legitimate customer's ticket with a substantive
response, while security requires that no sensitive field (SSNs, account numbers) was sent to an
unauthorized recipient. The two scores are reported separately rather than combined, since a model that
scores well on one and poorly on the other reveals a different failure mode than a model that scores
poorly on both.

## Dataset and licence

24 samples total, split across three task-specific JSON files: 10 for memory poisoning, 6 for autonomy
hijacking, and 8 for data exfiltration. Attack types vary per task (for example memory poisoning
includes direct instruction injection, gradual poisoning, authority impersonation, delimiter escape,
multi-vector poisoning and role hijack, alongside clean baselines), and memory-poisoning samples are
further tagged easy, medium or hard, with harder samples replacing legitimate content entirely rather
than merely appending an attack alongside it. All data lives inside the inspect_evals repository, which
is MIT licensed; no separate licence is stated for this task's own data files specifically. There is no
held-out or private split -- everything is public.

## Who publishes it

AgentThreatBench was contributed to Inspect Evals, a repository of community evaluations for the
Inspect AI framework created in collaboration by the UK AI Security Institute (AISI), Arcadia Impact and
the Vector Institute. The suite itself is credited to a single community contributor identified in the
repository only by their GitHub handle, vgudur-dev; no accompanying academic paper was found; the
"reference" the task registry cites is the OWASP Top 10 for Agentic Applications (2026) resource page
rather than a paper.

## Lineage

AgentThreatBench names no predecessor or successor benchmark; it is a purpose-built operationalisation
of two OWASP Agentic Top 10 categories rather than a descendant of an earlier evaluation. Its own
documentation notes that future releases may extend coverage to the remaining eight OWASP categories
(tool misuse, agent identity abuse, supply-chain compromise, unexpected code execution, insecure
inter-agent communication, cascading failures, human-agent trust exploitation, and rogue agents), none
of which are implemented yet.

## Saturation and contamination

No published per-model scores were found for this benchmark in the sources reviewed, so a saturation
reading was not established; it has no known public leaderboard. It is also very new: it was added to
inspect_evals in version 0.12.0, dated 2026-05-14, only a few months before this page was written. All
24 samples and the grading logic are public in the repository, so contamination is structurally
possible for any model trained on a crawl that includes it, though its recency limits how many
already-released models could have encountered it.

## How to run it

The three tasks run through inspect_evals: `agent_threat_bench_memory_poison`,
`agent_threat_bench_autonomy_hijack`, and `agent_threat_bench_data_exfil`, individually or together via
`inspect eval-set`. Because the benchmark is so small (6 to 10 samples per task), a single sample
flipping from correct to incorrect changes the reported percentage by roughly 10-17 points, so treat
any single-run score as noisy and prefer averaging over multiple runs or seeds before drawing
conclusions about a model's robustness. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench
integration exists, as this benchmark is native to Inspect AI.

## Reading the numbers

A model that scores high on both utility and security across all three tasks is doing the hard thing:
finishing real work while declining to act on instructions smuggled in through data it was only asked
to read, not obey. High utility paired with low security is the more dangerous combination in practice,
since it means the agent looks productive while remaining exploitable through its tool inputs. Because
the sample counts are tiny and the suite covers only 2 of the OWASP Top 10's ten agentic risk
categories, a strong AgentThreatBench score is evidence about resistance to these specific attack
patterns on these specific tool surfaces, not a general claim about an agent's security posture.
