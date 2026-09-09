# ModelSpec and BenchGraph — ownership handoff, September 9, 2026

## Start here

The operator is moving **all ModelSpec and BenchGraph work into a new session in `/Users/terbeest/dev/modelspec`**. The originating `/Users/terbeest/dev/dpf` session will work only on DPF. This document supersedes the September 8 handoff's operational instructions. The new session owns curated benchmark batches **and the remaining ModelSpec service delivery**, not just article generation.

The operator authorized continued Grok Build and GPT-5.6 Luna batch work, then replaced the broad census target with strict evidence-based downselection. **Keep Sonnet disabled** following the explicit cost instruction. No new research agents were dispatched during this transfer. The two remaining research agents finished their ledgers; agent IDs and conversation memory do not transfer.

Use this existing checkout: much of the new work is still untracked or modified locally. A fresh clone will not contain it. Branch is `benchgraph/census`; observed HEAD is `20b0491` (`benchmarks: batch-068, 6 source-reviewed census pages`). Preserve the entire working tree, old drafts and run evidence. Do not reset, clean, stage everything, switch branches blindly, or treat older census commits as approved under the new policy.

### First actions, in order

1. Read applicable repository instructions, this handoff, [the active-catalogue policy](../specs/2026-09-08-benchgraph-active-catalogue.md), and [eligibility operating notes](../../../benchmarks/_census/eligibility/README.md). This checkout is CodeGraph-indexed: use `codegraph explore` before locating code and `codegraph sync .` after edits. Root `CLAUDE.md` describes an older FalkorDB/FastAPI/React implementation; later decisions below govern the target architecture.
2. Inspect Git status and the operational hold files below. Reconfirm process identities before acting on a PID. Preserve legacy holds; start no competing census controller. Refresh PR and Linear state read-only before planning changes; their statuses below are historical snapshots.
3. Recompute today's eligibility, verify the seven article hashes against the durable review bundle, and inspect the reconciled review decisions. Integrate this reviewed work with selective commits and truthful provenance. Review the whole existing PR before choosing how to merge or replace its older census content.
4. Independently review research batches 003 and 004 before adding evidence records or assigning more pages. Expand source coverage through bounded research, using current model references by domain. Continue authoring or repairing only eligible, explicitly assigned profiles with a separate source reviewer.
5. Advance exports and site rendering alongside curation. Serving a useful reviewed catalogue does not depend on exhausting every census lead. Follow the MODEL delivery queue below; keep DPF implementation in its own session.

Local implementation, reversible preparation, scoped commits and pushes were authorized. For a merge, deployment, or Linear mutation, prepare the concrete reviewable change and obtain the operator's go unless the new session receives explicit authorization. No merge, deployment, or Linear write was performed for this handoff. Do not send messages to others by implication.

## What is complete, and what is not

**Seven profiles have reviewed articles ready for integration:** `aa_briefcase`, `aa_lcr`, `automationbench_aa`, `critpt`, `gdp_pdf_aa`, `gdpval_aa`, `scicode`. They are not yet committed as the curated batch, published, or proof that the sites are complete. Three are new pages; the other four repair or replace existing drafts/pages.

The current mechanical report, assessed September 9, contains **7 active, 1 alias and 7 unverified records**. This is a small reviewed evidence set, not a census-wide acceptance rate. The reference set is a limited seed covering GPT-6 Astra (max) and GLM-5.3 (max) in relevant domains; it is not a comprehensive frontier-model registry.

| Artifact | Meaning |
| --- | --- |
| [Durable review bundle](../../../benchmarks/_census/eligibility/handoff/2026-09-09/review-bundle.json) | Seven article SHA-256 values, reconciled coordinator status, and ten original/correction review records copied out of ignored cache. |
| `benchmarks/_census/cache/eligible-20260908/coordinator-status.json` | Reconciled `curated-batch-reviewed` status; all seven ready for integration, `published: false`. |
| `benchmarks/_census/cache/eligible-20260908/run-001/` | Original writer/reviewer logs and immutable earlier status. Its `needs-attention` state predates corrections; do not blindly retry it. |
| `benchmarks/_census/cache/eligible-20260908/corrections-001/` | Subsequent independent reviews resolving three rejections and the AA-LCR reviewer startup failure. |
| [Chart erratum](../../../benchmarks/_census/eligibility/2026-09-09-chart-correction.md) | SciCode GLM-5.3 value corrected from 56% to 59% in the evidence and article. |
| [Batch 003 ledger](../../../benchmarks/_census/eligibility/batch-003-research.md) | Completed research proposing HLE and AA-Omniscience pairs; **not independently approved or admitted**. Reopen primary sources and inspect chart labels and identity/methodology claims. |
| [Batch 004 ledger](../../../benchmarks/_census/eligibility/batch-004-research.md) | Completed research on LiveBench and SWE-bench Pro; both proposed `unverified` because attributable recent result dates were not established. This is not proof they are stale or invalid. |

Original Grok reviews approved three pages immediately and rejected three subsequently corrected. AA-LCR's reviewer produced no events during a prolonged MCP startup stall; that specific process was terminated and a full independent Luna source review replaced it. The other Luna reviews covered focused corrections. Preserve these distinctions in attribution; do not label every page personally checked by the coordinator or every correction a new full review. Front-matter attribution still needs integration. Any content or metadata change alters the reviewed hash; record the delta and obtain appropriate review.

The current seven use AA's dated September 4 v4.2 component chart and September 7 v4.3 AutomationBench results. Result publication dates are established; execution dates are undisclosed. AA-Briefcase and GDPval-AA values are rounded normalized Elo percentages, not raw Elo. GDP.pdf is AA's specific implementation. An aggregate index update cannot qualify every component without actual component results. Never copy later live scores into an older dated snapshot.

## The accepted eligibility policy

The old approximately 2,894-page completion target and old completion estimates are withdrawn. Census entries are discovery leads: many are aliases, subsets, generic names or weakly sourced proposals. Structural validation does not establish factual legitimacy.

Admission to the default active catalogue requires:

- A distinct canonical benchmark identity with a described task, metric, version and evaluation protocol. Aliases, harness variants and extra metrics must not inflate the benchmark count.
- At least one current frontier model and one current open model from different organizations, with compatible results for the same benchmark version/configuration and units. Distinguish open weights from open source; preserve exact published model/configuration labels and unknown API pins.
- An actual evaluation event or newly published result within a **rolling 60-day window**. Record whether the date is `evaluated` or `published`. Retrieval dates, paper dates, question-set releases, maintenance commits and announcements without attributable result values do not qualify.
- Primary evidence URLs, scores, units, dates, source context, and an independent review distinct from the researcher. Missing or uncertain requirements fail closed. Assess usefulness, remaining headroom and saturation rather than counting reruns automatically.
- Current model membership by domain. The implemented reference-set guard is 30 days; this differs from the 60-day result window.

Keep active, historical, unverified and alias dispositions distinct. A failure to establish freshness does not prove illegitimacy. Public articles may explain historical benchmarks, but serving must not silently classify all existing Markdown as active. Preserve useful old work while explicitly excluding held or unverified material from automatic publication.

## Implementation and verification

| File | Responsibility |
| --- | --- |
| `schema/benchmark_eligibility.py` | Strict evidence/reference schemas and admission evaluation: identity, dates, paired coverage, independent review, usefulness and compatibility. |
| `scripts/benchmarks/downselect.py` | Recomputes dispositions; fails closed on missing/malformed inputs, conflicting identities and duplicate records; writes reports atomically. |
| `scripts/benchmarks/next_batch.py` | Recomputes today's eligibility, excludes existing pages, writes `next_batch_eligible.json`; no fallback to the raw census. |
| `scripts/benchmarks/run_eligible.py` | Bounded opt-in Grok writer/reviewer runner with per-page ownership, gates before writing/before review/after review, shared lock, validation and hash-bound review. No automatic Git operations. |
| `benchmarks/_census/eligibility/` | Reviewed evidence, reference models, reports, source fingerprints and research ledgers. Retrieval hashes are provenance, not evidence dates. |
| `benchmarks/AUTHORING.md`, `schema/benchmark.py`, `scripts/benchmarks/validate.py` | Article prose and schema rules. `models_covered` is derived, never authored. |

Last implementation checks passed **35 focused tests**, Ruff on changed code/tests, validation of the seven articles, and `git diff --check`. This handoff adds documentation/evidence copies, not new runtime behavior. Repeat appropriate checks when integrating changes:

```sh
cd /Users/terbeest/dev/modelspec
/opt/homebrew/bin/python3.11 scripts/benchmarks/downselect.py \
  --evidence benchmarks/_census/eligibility/evidence \
  --reference-set benchmarks/_census/eligibility/reference-models.json \
  --as-of "$(date +%F)" \
  --output benchmarks/_census/eligibility/current-report.json
/opt/homebrew/bin/python3.11 -m pytest \
  tests/test_benchmark_eligibility.py tests/test_eligible_batch.py \
  tests/test_eligible_runner.py -q
/opt/homebrew/bin/python3.11 scripts/benchmarks/validate.py \
  benchmarks/aa_briefcase.md benchmarks/aa_lcr.md benchmarks/automationbench_aa.md \
  benchmarks/critpt.md benchmarks/gdp_pdf_aa.md benchmarks/gdpval_aa.md benchmarks/scicode.md
```

For a new run, inspect `run_eligible.py --help`, explicitly choose independently admitted IDs, and supply a **new, nonexistent** run directory under the current date's cache directory. The seven reviewed IDs do not need another authoring run. The runner uses `/Users/terbeest/.local/bin/grok`, bounded turns, unique job caches and `benchmarks/_census/cache/eligible-run.lock`. The legacy quality-pause marker must remain present. A soft signal to the verified new supervisor PID lets current work finish without assigning further work; do not signal an entire process group casually. Reconcile every assigned ID and review before a selective checkpoint. Serving admission and coordinator checkpoint integration are still unfinished.

## Paused infrastructure and cost controls

No curated writer/reviewer jobs remain running at this transfer. The old infrastructure is deliberately quiescent, not deleted:

| State at transfer | Durable locator |
| --- | --- |
| Legacy controller PID 26229 alive, `paused-for-quality-audit` | `benchmarks/_census/cache/grok-continuation-20260908/controller.pid` and `status.json` |
| Legacy supervisor PID 54381 suspended (`Ts`) | `benchmarks/_census/cache/grok-window-20260908/supervisor.pid` |
| Broad generation persistently held | `benchmarks/_census/cache/grok-continuation-20260908/QUALITY_AUDIT_PAUSE.json` |
| Sonnet stopped following operator cost instruction | `benchmarks/_census/cache/grok-continuation-20260908/SONNET_STOP` |
| 52 generic drafts held for quality audit | `benchmarks/_census/cache/grok-continuation-20260908/quality-hold-generic-drafts.json` |

Verify process command and state before termination or adoption; PIDs can be reused. Keep both hold files. Do not resume the suspended legacy queue or its automatic checkpointing. The new session may carefully retire this idle infrastructure after reconciliation, preserving evidence and avoiding restart/checkpoint side effects. Historical quota-reset timestamps and concurrency settings are not current capacity guarantees. No Sonnet restart is authorized.

Preserve the Git-excluded `.grok/config.toml` project override disabling the `1password` MCP server. It retains the existing command and sets `enabled = false`; benchmark research does not need secrets. Repeated helper startup previously caused macOS file-access Allow prompts attributed to Codex. Do not change global MCP configuration or OS permissions to run these batches. Other global MCP startup can still stall a worker; diagnose the specific job before restarting it.

The full cache is ignored by Git. The durable review bundle is not ignored, but remains local until selectively committed with the handoff and related work. Neither this bundle nor a Git push transfers live processes or agent conversations.

## ModelSpec product scope and remaining MODEL work

ModelSpec supplies public model intelligence; BenchGraph is its benchmark project in this repository and Linear's MODEL team. Git cards remain authoritative, validated and human-merged. Code is MIT; the model/benchmark corpus is CC BY-SA 4.0; third-party sources retain their own terms.

The target is versioned exports to R2/D1 and one TypeScript Cloudflare Worker for model/provider pages, benchmark wiki, graph view, browser downselection, API, snapshots and remote MCP. The Mac is for editing and development previews, not public hosting. Benchmark articles are **canonical at `benchgraph.dev`**, with ModelSpec linking to them; `modelspec.dev/benchmarks` may provide discovery. MODEL-7 supersedes the older dual-domain/redirect proposal. Do not create duplicate canonical articles.

**Graph hosting remains unresolved:** MODEL-9 asks for FalkorDB, conflicting with the earlier Cloudflare-only serving design. Decide explicitly whether it feeds exports or serves live behind the Worker; export-based FalkorDB was a recommendation, not an accepted provisioning decision. Do not silently replace Git as the source of truth.

Repository, CLI and snapshots stay free and unmetered. The paid recommender returns a model/provider, reasons, fallback, authoring guide and signed receipt, then hands off; it does not proxy model tokens. Prefer locally derived profiles to raw prompts. Metered keys, free-tier allowances and per-call agent payments remain design/implementation work, including exact prices.

These eleven issues were Backlog at the earlier read; **refresh their actual scope, status and dependencies before dispatch**:

| Ticket | Remaining delivery scope |
| --- | --- |
| [MODEL-1](https://linear.app/sparksandsawdust/issue/MODEL-1) | Organize the online-service repository while preserving schema and corpus. |
| [MODEL-2](https://linear.app/sparksandsawdust/issue/MODEL-2) | Validated, versioned R2/D1 exports; failures preserve the last good snapshot. |
| [MODEL-3](https://linear.app/sparksandsawdust/issue/MODEL-3) | Shared Worker, model/provider pages, graph, downselect, API, snapshots, remote MCP, host routing and discoverability. |
| [MODEL-4](https://linear.app/sparksandsawdust/issue/MODEL-4) | Credential-free CLI with cached snapshots and offline continuity. |
| [MODEL-5](https://linear.app/sparksandsawdust/issue/MODEL-5) | Scheduled model research, validation and human-merged updates. |
| [MODEL-6](https://linear.app/sparksandsawdust/issue/MODEL-6) | Recommendations, keys, metering, free tier, receipts and agent payments. |
| [MODEL-7](https://linear.app/sparksandsawdust/issue/MODEL-7) | Benchmark wiki and indexes, lineage, derived model-score links, dated sources, canonical URLs, sitemap and Search Console. Default active listings must consume current eligibility. |
| [MODEL-8](https://linear.app/sparksandsawdust/issue/MODEL-8) | Sourced, dated model authoring guides and schema; DPF-21 owns the DPF counterpart. |
| [MODEL-9](https://linear.app/sparksandsawdust/issue/MODEL-9) | Explicit graph hosting decision, lossless ingest, useful queries and backups. |
| [MODEL-10](https://linear.app/sparksandsawdust/issue/MODEL-10) | Continuous benchmark curation: watcher, drafter, independent validation and human merge. Observe seven consecutive days of acceptance evidence; this is separate from the 60-day freshness rule. |
| [MODEL-11](https://linear.app/sparksandsawdust/issue/MODEL-11) | Contributor-agreement legal review before driving contribution traffic. `CLA.md` has unresolved governing-law/patent language. |

Prioritize stable reviewed data, exports and rendering, then offline continuity and scheduled research, guides and the remaining graph/recommendation/payment work. Some prerequisites were only in ticket prose; native blockers were incomplete. MODEL-10 had a native MODEL-9 dependency: revisit deliberately if file-based curation can ship earlier, without silently changing the tracker.

[PR #6](https://github.com/turbobeest/modelspec/pull/6) is the census branch; its old title/count is stale and its older content predates the eligibility policy. [PR #5](https://github.com/turbobeest/modelspec/pull/5) contains the already-deployed landing source and was still open at the earlier check. Landing deployment is not wiki/service completion. Historical Pages projects are `modelspec` and `benchgraph`, with domains/www aliases attached; recheck infrastructure before deployment. Use current official Cloudflare documentation and applicable skills; old pricing/limits are not current estimates.

Completion means a reviewed and truthfully classified catalogue, tested export/serving and CLI behavior, deliberate resolution of remaining MODEL scope, and observed long-duration acceptance. It does not mean generating every lead or merely passing YAML validation. Report remaining work and deployment/merge status explicitly.

## References and the DPF boundary

- [Original site plan, copied into this repository](../references/2026-09-07-modelspec-site-plan.md): byte-for-byte copy from DPF's same-named specification on September 9. Historical context only; apply the canonical-host and unresolved graph decisions above. Machine observations, costs and early architecture proposals are dated.
- [Downselection implementation plan](2026-09-08-benchgraph-downselection.md) and [census quality audit](2026-09-08-benchgraph-census-quality-audit.md): implementation rationale and held-work findings. Read their dated status as history.
- [September 8 handoff](2026-09-08-modelspec-benchgraph-handoff.md): archived operating history only. Its queue, running-agent, continuation and quota instructions are superseded here.

DPF retains private usage evidence, selection logic and runtime integration. ModelSpec owns public facts, guides, exports and service interfaces. DPF-21/22 are cross-project interfaces, not permission for this new session to take over DPF tickets. Prepare any required interface contract in ModelSpec and report the DPF dependency for the operator to coordinate. The originating session will handle DPF separately.

For future credential-dependent implementation, use the established `~/.local/bin/op-agent` service-account path and AI-LAN vault, never desktop sign-in or printed secret values. The historical Cloudflare zone-security credential's scopes must be checked against the concrete operation; do not assume it can deploy the service. Source research requires no credentials.
