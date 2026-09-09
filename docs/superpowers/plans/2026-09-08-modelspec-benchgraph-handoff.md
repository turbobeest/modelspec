# ModelSpec and benchgraph session handoff — September 8, 2026

> **Superseded September 9, 2026:** use [the current ModelSpec/BenchGraph ownership handoff](2026-09-09-modelspec-benchgraph-handoff.md). This file is historical context. Its running-agent counts, census target, quota window and continuation instructions are no longer operative. Keep the legacy quality hold and Sonnet stop in place.

## Current scope override: evidence-first downselection

The operator approved a stricter approach on September 8: active benchmarks must have verifiable evaluation results or newly published results within a rolling 60-day window, covering current frontier and open models under comparable conditions. See the [accepted specification](../specs/2026-09-08-benchgraph-active-catalogue.md) and [implementation plan](2026-09-08-benchgraph-downselection.md). This overrides the historical all-candidates completion target below. Verification batches are authorized; the old generation/checkpoint queue is not authorized to resume unchanged. Keep `QUALITY_AUDIT_PAUSE.json` and `SONNET_STOP` in place. Eligibility evidence must drive the replacement queue. A recent editorial research timestamp is not recent evaluation evidence.

**Current bounded replacement:** seven independently verified profiles are assigned to seven Grok workers through `scripts/benchmarks/run_eligible.py`. Read `benchmarks/_census/cache/eligible-20260908/run-001/status.json` and per-job process metadata; the supervisor PID is in `eligible-20260908/supervisor.pid`. This run performs writing/repair, then separate source review, with fresh eligibility checks and no automatic Git operations. Do not replay it or resume the legacy queue. The accepted IDs are `aa_briefcase`, `aa_lcr`, `automationbench_aa`, `critpt`, `gdp_pdf_aa`, `gdpval_aa`, `scicode`. Source records, dispositions, exact versions and operating instructions are in [the eligibility README](../../../benchmarks/_census/eligibility/README.md). Fifteen identifiers have been assessed: seven active profiles, one alias, seven unverified. This is a limited source-led sample, not a census-wide acceptance rate or a claim that all seven articles are complete.

## Mandate and ownership

The operator first directed: “Let's Focus entirely on completing model spec and bench graph first, then we'll move into DPF tickets as soon as possible.” The subsequent session arrangement is to hand ModelSpec and benchgraph to a dedicated session in this checkout, with the original DPF session returning to DPF after the batch sessions complete. This is the handoff for that dedicated session. Do not dispatch DPF implementation from here.

Own the ModelSpec/benchgraph delivery programme and monitoring of the existing Grok Build batch runner. The runner already operates independently of the originating chat; opening this document does not require restarting it. The receiving session has not been started or contacted by the originating agent.

**Latest operator correction:** “Make no mistake, keep the batches going until they're complete.” The earlier 13-hour limit is superseded as a programme cutoff. Finish the finite queued census work, including reviews and resolution of skips/rejections, across token resets. The session handoff is not a stop instruction. Quota pauses are resumable, not completion.

## First actions

1. Read this document and the continuation controller status at `benchmarks/_census/cache/grok-continuation-20260908/status.json`. It identifies the currently owned runner. Confirm live PIDs and advancing timestamps. **Do not launch a second controller/supervisor or replay the queued assignments.**
2. Inspect current branch, working-tree changes, and worktrees. Active writers create untracked files deliberately. Never discard them, switch this checkout's branch, rebase it, or change the shared schema/validator/authoring guide while the batch runner is active.
3. Refresh MODEL-1 through MODEL-11 in Linear, including descriptions and relations. They are the delivery queue. Reading is authorized; tracker mutations follow the review-and-go convention below.
4. Use a separate worktree for site/service implementation. Keep `/Users/terbeest/dev/modelspec` on `benchgraph/census` for the runner, which stops if the branch changes. Choose the implementation base after inspecting open PRs and current main; do not assume every census change has merged.
5. Prepare the online implementation design/plan, then proceed with local implementation within the operator's ModelSpec/benchgraph scope. Bring concrete merge/deployment decisions to the operator. Do not make census completeness a prerequisite for rendering the existing corpus.

## Running batch programme — adopt, do not duplicate

The programme now has a continuation controller in `benchmarks/_census/cache/grok-continuation-20260908/`. Its `controller.py` is running detached, with PID in `controller.pid`, live state in `status.json`, and diagnostics in `controller.log`. It first monitors the original six-session runner without disturbing it, then starts successor runs in `run-001/`, `run-002/`, etc. only after the prior supervisor and its known workers have exited. A process lock prevents a duplicate continuation controller.

The successor runner has **no token-reset completion deadline**. It keeps six sessions active, reconciles accepted commits, carries partial/unreviewed drafts forward, and requires independently sourced dispositions for verified aliases or entries that are not evaluations. Quota exhaustion waits for the known reset (September 9 at approximately 05:36 EDT), or uses spaced one-session retries after that, restoring six-session concurrency once work succeeds. `dispositions.json` records approved pages, verified skips and unresolved blockers. Every target ID must be accounted for and final corpus validation must pass before the controller sets `completion: true`.

Three unsuccessful review attempts flag an ID for coordinator attention while other work continues. Such IDs, externally tracked pages without matching review evidence, failed pushes and final validation failures are **not completion**. The receiving session must resolve these when reported in controller status. Do not burn tokens repeatedly on an unchanged factual blocker. Reconcile the recorded review evidence and draft before reassigning it. The controller handles transient quota/push waits; a controller-error state needs diagnosis in the dedicated session.

To explicitly stop the entire programme, create `STOP` in the **continuation-controller directory**. Merely ending the current chat or starting the dedicated ModelSpec session does not stop it. Never delete state to restart. The controller has its own idle-sleep prevention tied to its process. At handoff preparation its reconciliation logic was smoke-checked to retain partial/new work while excluding approved pages and independently verified aliases; the successor module imported without launching workers.

The following original-window details remain useful for its logs and history; its cutoff is now a transition to continuation, not the end of the programme.

**Latest quality hold, September 8:** after the operator questioned benchmark counts and source legitimacy, the audit found duplicate identities, generic index entries promoted to benchmarks, and 52 uncommitted drafts with unsupported template prose. See [the census quality audit](2026-09-08-benchgraph-census-quality-audit.md). The primary supervisor is suspended (SIGSTOP); existing workers were not signalled and may finish their current work. `grok-continuation-20260908/QUALITY_AUDIT_PAUSE.json` blocks automatic continuation and new Luna claims. Do not blindly resume the all-candidates target. Establish eligibility, canonical identities and an evidence quality gate before restarting broad generation. This is a scope/quality hold, not a completed programme; all files are preserved.

**Sonnet override, September 8 at 22:23 EDT:** the operator called off Sonnet 5 because of its usage rate. All six assigned Sonnet workers and their supervisor were stopped and verified absent. `grok-continuation-20260908/SONNET_STOP` persistently prevents controller restarts. **Do not remove this file or restart Sonnet without new operator authorization.** Preserve completed supplemental reviews and drafts. The Sonnet configuration described below is historical capability, not authorization to run it.

**September 8 late-evening expansion:** the operator previously requested additional Grok, GPT-5.6 Luna, and Claude Sonnet 5 agents. The original six-worker supervisor was replaced at a verified idle boundary by `grok-continuation-20260908/resume-grok-runner.py`, adopting every existing Grok subprocess without restarting its context. The pool expanded to **12 Grok + 6 Claude Sonnet 5 CLI sessions**, with **three additional Luna agents** working bounded streams. Sonnet has since been stopped as directed above. Read current status rather than assuming all slots are occupied during phase transitions. The Mac itself has no four-agent ceiling; four is this Codex conversation's delegation limit, including the coordinator.

Both CLI dispatchers now share the locked registry `grok-continuation-20260908/luna-supplement/status.json` and its `status.lock`. Its directory name predates Sonnet participation: it contains both providers' assignments. Grok holds that lock through new-job registration and launch; the companion and the Luna claim helper reserve IDs under the same lock. The `resume-ready.json` marker in a run directory indicates this shared claim protocol is enabled. Do not launch independent batches outside this protocol.

Controls and logs for the expansion are in `grok-continuation-20260908/`: `grok-concurrency.txt` (currently 12, supported 1–18), `sonnet-concurrency.txt` (currently 6, supported 1–6), `sonnet-runner.py`, `sonnet-runner.pid`, `sonnet-status.json`, and `sonnet-runner.log`. The original run's current supervisor PID still lives in its original `supervisor.pid`; its replacement logs to `resumed-supervisor.log`. Historical PIDs below are obsolete. The controller was updated to restore the requested Grok concurrency after quota probes and attach the Sonnet companion to successor runs. Sonnet quota recovery waits at least 30 minutes and probes with one session. These are provider quotas, not Mac limits.

Luna streams use `/opt/homebrew/bin/python3.11 benchmarks/_census/cache/grok-continuation-20260908/luna-queue.py claim <owner>` and `finish <assignment>`. Owners `a`, `b`, and `c` are currently assigned to the three Codex-delegated Luna agents. A claim returns exact IDs, cache, and author attribution. `finish` requires a complete writer report and validates written pages before queuing independent Sonnet review. Do not take a second unfinished assignment for an owner or reuse these owners while their agents are active. Luna delegation is bounded to ten batches per stream; the CLI pools refill automatically. A stale Luna claim requires coordinator reconciliation with that agent; never infer its completion solely from elapsed time.

Supplemental pages require a separate reviewer, recorded reviewer identity, a review disposition for every assigned ID, and the existing schema validator. The continuation controller commits accepted supplemental pages only after the current Grok run and supplemental CLI workers drain, avoiding concurrent Git checkpoints. Thus `ready-to-checkpoint` is reviewed work, **not yet committed or pushed**. Finished drafts without a completed independent review return to Grok continuation. `checkpoint-needs-attention` remains reserved for coordinator inspection. No merges, deployments, or Linear writes are authorized by this expansion.

The Sonnet CLI was verified on the authenticated Claude Max account with model `claude-sonnet-5`. It launches with an empty strict MCP configuration, disabled hooks, and an explicit tool allowlist; it does not start 1Password. Grok retains the local project override described below. Verification included preserved worker PIDs across both supervisor upgrades, no overlapping active page assignments, real schema validation and isolated Git checkpoint tests preserving unrelated staged files, and registry adoption/quota-detection tests. Throughput estimates remain provisional until this larger pool has accumulated independently accepted output.

Checkout: `/Users/terbeest/dev/modelspec`.

Branch: `benchgraph/census`, open as [PR #6](https://github.com/turbobeest/modelspec/pull/6). Its title still says 296 pages and is stale.

Local run directory, ignored by Git:

`benchmarks/_census/cache/grok-window-20260908/`

| File | Purpose |
| --- | --- |
| `status.json` | Live active PIDs, job states, assignments, approved/rejected IDs, commits, push results, usage, remaining batches, and stop reason. |
| `supervisor.pid` | Supervisor PID; read the file instead of assuming the snapshot PID below is still valid. |
| `supervisor.log` | Runner diagnostics. |
| `runner.py` | One-off local supervisor; not production curation infrastructure. |
| `queue.json` | Original 414 assignments covering 2,887 candidate IDs, seven or fewer per assignment. Registry discoveries precede curated discoveries. |
| `<job>/write-prompt.md`, `write.jsonl`, `write-report.md` | Writing assignment, raw events, and extracted report. |
| `<job>/review-prompt.md`, `review.jsonl`, `review.json` | Fresh-session source review and approved/rejected disposition. |
| `<job>/*-validation.txt`, `checkpoint.txt`, `push.txt`, `accepted/` | Validation and checkpoint evidence, plus accepted-content copies. |

Snapshot at approximately 17:20 EDT September 8: supervisor PID **61987**, six active sessions, six checkpointed jobs including the pilot, **41 new approved pages committed and pushed**, no stop reason. Five writers and one reviewer were active. These counts are observations, not targets or a current guarantee; read `status.json` again.

Original pre-run baseline: commit `9d6f812`, 381 pages passing the full corpus validator. Pilot IDs: `med_concepts_qa`, `medi_qa`, `medication_qa`, `medxpertqa`, `metabench`, `minute_mysteries_qa`, `mlqa`. Pilot review committed as `125f10f`. Completion order differs from job numbering, so use Git history or recorded SHAs, not batch number, for commit order.

The operator asked to use the remaining Grok token window aggressively. This original runner maintains **six concurrent Grok Build sessions**, refilling slots and giving completed writing batches separate review sessions. Its original code stops launching new writing 30 minutes before **2026-09-09 09:36:17 UTC / 05:36:17 EDT**, and ends that run at the cutoff. A reported quota/rate limit stops replenishment; dispatch/checkpoint errors may halt it earlier. The continuation controller then reconciles and resumes remaining work, so these conditions no longer terminate the overall programme. Idle-sleep prevention (`caffeinate -i`) is tied to the supervisor process.

Creating `STOP` in an individual run directory halts that run; the continuation controller respects an explicit stop. Files are preserved. An individual `runner.py` refuses to start when `status.json` exists. Do not delete its state to force a restart. Adopt the already-running continuation controller rather than preparing a competing queue.

Writers and reviewers have unique page assignments, may use their own caches, and are instructed not to run Git, spawn nested agents, change shared files, access credentials, deploy, merge, or mutate Linear. They run through `~/.local/bin/grok`, with bounded turns. The supervisor alone validates and checkpoints approved new pages, then pushes explicitly to `origin/benchgraph/census`. It never merges or deploys.

At 21:22 EDT September 8, a local, Git-excluded `.grok/config.toml` was added to disable the `1password` MCP server in this checkout. macOS TCC logs showed repeated `SystemPolicyAppData` requests by the 1Password MCP helper attributed to `com.openai.codex`; their times matched Grok batch MCP startup timeouts. These research sessions do not need that helper. The project override includes the existing command and `enabled = false` because project MCP definitions replace entire server records. `grok mcp list --json` confirms `1password` is disabled with project scope; the global user configuration is unchanged. New batch sessions adopt it automatically, including continuation runs using this checkout. Preserve the override while batches run. Batch 059 started after the change with no 1Password warnings at the initial check; already-started sessions can still have pending prompts.

Review is a **separate Grok Build session with independently opened primary sources**, not a claim that Codex personally fact-checked every page. `freshness.reviewed_by` records the actual reviewer. Schema validation checks structure, not truth. Read review findings and spot-check accepted work; do not equate an `approved` list with infallibility. Raw events include signed usage metadata: extract numeric usage fields only when reporting cost; never dump signatures or credential material to chat.

At completion or failure: account for every dispatched ID; reconcile skips, aliases, missing/rejected/partial files; consolidate repository data findings into `benchmarks/_census/DATA-QUALITY.md` after writers finish; validate the entire corpus; inspect scope and final review evidence; confirm checkpoints are pushed; report remaining work and the exact stop reason. Do not delete rejected pages blindly or count them as accepted. The static queue does not automatically requeue unfinished assignments. New benchmark pages can reveal duplicate aliases across jobs that still require coordinator reconciliation.

## Authoring machinery

- `benchmarks/AUTHORING.md`: required prose, source and validation rules.
- `schema/benchmark.py`: `BenchmarkCard` front matter; unknown stays null/empty; `models_covered` is derived and must never be authored.
- `scripts/benchmarks/validate.py`: validate named files or, with no arguments, the entire corpus. Avoid interpreting partially written active files as completed failures.
- `scripts/benchmarks/next_batch.py`: queue slicing with written-page and alias filtering. It writes the shared `next_batch.json`; do not rerun it as an overlapping dispatch while the supervisor has claims.
- `benchmarks/_census/aliases.yaml`: aliases, renames and entries that are not evaluations.
- `benchmarks/_census/DATA-QUALITY.md`: unresolved and resolved evidence findings. Read resolution entries before reopening historical defects.

The value of the pages is the caveat: incompatible versions/protocols, source disagreements, missing scores, public test answers, and saturation. Hints and coordinator notes are leads, never citations. Avoid turning harness spelling variants into duplicate evaluations.

## Decided product and architecture

ModelSpec is the public model intelligence service; benchgraph is its benchmark project in the same repository and Linear team. ModelSpec's code stays MIT; `models/` and `benchmarks/` use CC BY-SA 4.0. Third-party sources retain their own terms.

Cards stay in GitHub, validated and human-merged. A pipeline exports versioned JSON to R2 and data to D1. One TypeScript Worker serves the model site, benchmark wiki, API, snapshot endpoint, and remote MCP. The CLI downloads a snapshot and works offline without a credential on its free path. The Mac is for editing and development previews, not a public host.

**Canonical decision:** benchmark articles are canonical at **benchgraph.dev**, with ModelSpec linking to them. MODEL-7 supersedes the older plan of canonical pages at `modelspec.dev/benchmarks/<slug>` with benchgraph redirecting. MODEL-3 routes the two hosts through the same Worker. Do not build duplicate canonical articles.

**Unresolved graph decision:** MODEL-9 requires a FalkorDB-based benchgraph, which conflicts with the prior Cloudflare-only/no-host serving plan. Decide whether FalkorDB supplies an export or serves live behind the Worker. The prior recommendation is export-based serving; it is not an accepted hosting decision or permission to provision a host. Clarify whether Git cards remain authoritative when implementing graph writes. Do not quietly introduce competing sources of truth.

The downloadable repository, CLI and snapshots remain free and unmetered. The paid recommendation service returns a model, source/provider, reasons, fallback, authoring guide and signed receipt. Prefer locally computed profiles over raw prompts; recommend and hand off, never proxy model tokens. Planned payment paths are metered keys and per-call agent payments, with a free tier; exact prices and payment-provider details remain design work. DPF's usage evidence and selection logic stay private, while ModelSpec holds the public facts and guides.

## Delivery queue (Linear snapshot; refresh before dispatch)

All eleven tickets were Backlog at the handoff read. This records their scope, not verified completion.

| Ticket | Outcome |
| --- | --- |
| [MODEL-1](https://linear.app/sparksandsawdust/issue/MODEL-1) | Repository structure for the online service, preserving the schema and corpus. |
| [MODEL-2](https://linear.app/sparksandsawdust/issue/MODEL-2) | Validated versioned exports to R2/D1; failed builds preserve the last good version. |
| [MODEL-3](https://linear.app/sparksandsawdust/issue/MODEL-3) | Shared Worker: model/provider pages, graph view, browser downselect, API, snapshot and remote MCP, host routing and discoverability. |
| [MODEL-4](https://linear.app/sparksandsawdust/issue/MODEL-4) | Credential-free offline CLI snapshot mode. |
| [MODEL-5](https://linear.app/sparksandsawdust/issue/MODEL-5) | Scheduled model research, validation and human-merged updates. |
| [MODEL-6](https://linear.app/sparksandsawdust/issue/MODEL-6) | Recommendation service, keys, metering, free tier, receipts and agent payment path. |
| [MODEL-7](https://linear.app/sparksandsawdust/issue/MODEL-7) | Benchmark wiki rendering, indexes, lineage, derived model-score links, dated sources, canonical URLs, sitemap and Search Console. |
| [MODEL-8](https://linear.app/sparksandsawdust/issue/MODEL-8) | Dated, sourced per-model authoring guides and their schema. DPF-21 is the integration counterpart. |
| [MODEL-9](https://linear.app/sparksandsawdust/issue/MODEL-9) | Graph hosting decision, lossless ingest, useful queries and backups. |
| [MODEL-10](https://linear.app/sparksandsawdust/issue/MODEL-10) | Continuous benchmark curation: Firecrawl watcher, Grok drafter, validation and human merge; seven-day evidence requirement. |
| [MODEL-11](https://linear.app/sparksandsawdust/issue/MODEL-11) | Contributor-agreement legal review before the sites drive traffic to the repository. |

Serving depends on the export/Worker work and the corpus PR being merged. Some dependencies exist only in ticket prose: MODEL-7 lists export/Worker prerequisites but its native blockedBy list was empty; MODEL-8 names restructure without a native blocker. Propose specific tracker repairs for review instead of assuming missing relations mean no dependency. MODEL-10 currently has a native dependency on MODEL-9; revisit that deliberately if planning useful file-based curation sooner.

Recommended delivery order: establish the online design and reusable code; implement exports and serving; render the existing wiki; deliver snapshot continuity and daily research; complete guides, graph and recommendation/payment features with their evidence. Census expansion continues in parallel and is not the definition of service completion. Long-duration acceptance, such as seven consecutive days of curation, must be observed rather than declared complete on deployment day.

## Open PRs, findings and operational boundaries

- [PR #5](https://github.com/turbobeest/modelspec/pull/5): `site/benchgraph-landing`, already-deployed landing source, still open at the earlier live check. Refresh before acting.
- [PR #6](https://github.com/turbobeest/modelspec/pull/6): growing census corpus, open and being pushed by the supervisor. Review a stable checkpoint; never merge a moving branch accidentally.
- `CLA.md` is a draft: governing law is unfilled and patent-grant wording needs counsel. MODEL-11 owns the remaining legal review. Code/document preparation does not substitute for that review.
- Outstanding card-data issues include ambiguous `mmlu_<category>` names on frontier cards and Artificial Analysis index naming. Pilot findings also question the existing MedXpertQA multimodal option-count/harness prose; see pilot reports and independently verify before changing that sibling.
- Pages projects: `modelspec` and `benchgraph`; domains and www aliases are already attached according to the prior handoff. Verify current infrastructure when doing deployment work.
- An automated Chrome window previously failed Cloudflare verification because of its automation flag. It is not evidence that real visitors are blocked. Check HTTP status and `cf-mitigated` with curl and an outside fetch.
- Credentials: only `~/.local/bin/op-agent`, AI-LAN vault, service-account access. Never print secrets or invoke desktop sign-in. Zone-security item: `dpf // Cloudflare // Zone security`, field `credential`; historical scope includes DNS, bot management and WAF, not zone settings/analytics. Check required permissions without exposing values.
- Use plain prose with the operator. Local implementation, reversible preparation, commits and pushes are authorized within scope. Deploying, merging, filing/editing Linear and protected manifesto changes require a concrete review copy followed by the operator's go, unless explicitly authorized later. Never send notifications to other people by implication.

## Environment and cross-repository references

Python: `/opt/homebrew/bin/python3.11`. Grok: `/Users/terbeest/.local/bin/grok`. Node recorded in prior handoff: `~/.nvm/versions/node/v22.22.3/bin/node`; verify PATH for the new session. Use `rg` rather than the local grep wrapper.

This checkout is CodeGraph-indexed. Use `codegraph explore` before locating code, and sync after edits. Root `CLAUDE.md` describes the historical FalkorDB/FastAPI stack; it is useful implementation history, not authority to override the later Worker decision. Read applicable Cloudflare/Wrangler skills and current official documentation before implementing or deploying that stack.

The original site design lives in the sibling DPF repository, not here:

- `/Users/terbeest/dev/dpf/docs/superpowers/specs/2026-09-07-modelspec-site-plan.md` — read its evening revision and then apply the later MODEL-7 canonical and MODEL-9 graph decisions. Its old prices/limits are historical estimates, not verified current costs.
- `/Users/terbeest/dev/dpf/docs/superpowers/plans/2026-09-08-claude-code-handoff.md` — wider historical handoff.
- `/Users/terbeest/dev/dpf/factory/TASKINGS.md` — dated decisions, including Grok delegation and this session split.
- `/Users/terbeest/dev/dpf/platform/CONOPS.md` — DPF integration boundaries; DPF-21/22 overlap with MODEL-8 and the service programme. Keep ModelSpec implementation here and DPF-specific integration work in the DPF session.

The original supervisor continues running, and the operator's latest instruction authorized the detached continuation controller described above. No additional Grok assignments overlap the original runner. No deployment, merge or Linear mutation was triggered by preparing this handoff.
