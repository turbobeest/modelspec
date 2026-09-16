# Curation loop (MODEL-10)

The curation loop keeps `benchmarks/*.md` current. It watches every source a page cites.
When a source changes, a drafter proposes an edit, the validator gates it, and the edit
reaches `main` only through a human-merged pull request. The loop edits Markdown, never
the graph. Nothing auto-merges.

Part 1 built the watcher, the classifier, the drafter interface and the PR gate in dry
run. Part 2 (live) runs the drafter, opens draft PRs and files dead-leaderboard issues in
CI, and runs a 7-day daily trial. See "Part 2 (live)" below.

## Architecture

```
benchmarks/<id>.md ──sources──▶ scripts/curation/watch.py ── plain HTTP (Firecrawl only if JS + cap > 0)
                                   │ state: benchmarks/_curation/state/<sha>.json|.txt
                                   ▼
                                scripts/curation/classify.py ──▶ change_report.json / .md
                                   ▼  (part 2 in CI; local now)
                                scripts/curation/draft.py ── claude -p | fake ──▶ validate.py + curation checks
                                   ▼  accepted drafts only
                                scripts/curation/propose.py ──▶ one branch + one DRAFT PR per page
                                   ▼
                                human review and merge
```

- **Watcher** (`scripts/curation/watch.py`). It collects the sources of each page
  (`leaderboard_url`, `paper.url`, `dataset.url`, `repo_url`, every `sources[].url`),
  deduplicates them across pages and skips images and archives. Each is read once with a
  plain GET: backoff on 429 and 5xx, and an 8 MB truncation guard. The text is normalised:
  scripts, styles, comments, `data-*` attributes (embedded JSON counters), timestamps,
  nonces, long hex ids and relative times ("about 15 hours ago") are dropped. The state
  file per source records hash, fetched_at, status, etag, last_modified and fetcher, plus
  the last good normalised text for diffing. A failed or truncated fetch records
  `last_error` and `last_status` only; it never replaces the last good hash or text. A
  first sighting is a baseline, not a change.
- **State location.** `benchmarks/_curation/state/` is gitignored. CI persists it between
  weekly runs with `actions/cache` (each run saves a new key, restoring the latest). Losing
  the cache costs one baseline run, not a false PR.
- **Report.** `benchmarks/_curation/reports/change_report.{json,md}`: changes, failures,
  JS-host sources not rendered, census leads and Firecrawl calls.

## Pilot pages

`benchmarks/_curation/pilot.txt`, computed by `watch.py --write-pilot`: pages with
`status: active` and an http(s) `leaderboard_url`, sorted by id, first 25 (63 qualified on
2026-09-15). It is deterministic, and a test asserts the recorded file matches the rule.

aa_briefcase, aa_lcr, aclue, adv_glue, agent_bench, agentdojo, agieval, aider_polyglot,
aime, aime_2025, aime_2026, air_bench, alghafa, alpaca_eval, alrage, anima,
anthropic_red_team, arabic_exams, arc_agi_2, arena_elo, arena_elo_coding,
arena_elo_hard_prompts, arena_elo_math, arena_elo_overall, arena_elo_style_control.

The list leans alphabetically toward AA, AIME and Arena pages. That is accepted for a pilot
because it is reproducible. Widen it with `--pages all` after the 7-day run.

## Change kinds and heuristics

`scripts/curation/classify.py`. A kind needs evidence that is new in this reading: present
in the added lines and absent from the old text. Otherwise the change is
`changed_unclassified`.

| Kind | Evidence required |
|---|---|
| `leaderboard_dead` | HTTP 404/410 on the page's `leaderboard_url` |
| `source_gone` | HTTP 404/410 on any other source |
| `fetch_failed` | other non-2xx, network error or truncation (state kept) |
| `new_version` | a `vN[.N]` / `version N` string not in the old text, or new successor wording ("superseded by", "successor") |
| `deprecation` | "deprecated", "retired", "no longer maintained", "sunset", "archived" newly appearing |
| `licence_change` | the set of licence tokens (MIT, Apache-2.0, CC-BY-*, GPL, …) differs |
| `test_set_release` | "private/held-out/new test set", "test set released", "test split now public" newly appearing |
| `paper_revision` | arXiv version number increased (`arXiv:….vN`, `[vN]`) |
| `leaderboard_movement` | a leaderboard source changed and no other kind matched |
| `changed_unclassified` | anything else |

The watcher does not detect two ticket kinds, `saturation_crossing` and `dataset_change`.
Both need reading scores and splits, which is the drafter's job. They surface as
`leaderboard_movement` or `changed_unclassified`.

## Firecrawl cap policy

- Plain HTTP first, always. It costs zero credits.
- Firecrawl is considered only for sources whose host is listed in
  `benchmarks/_curation/js_hosts.yaml` **and** on the census `scrape_allow` list.
- It goes only through `scripts/benchmarks/fetch.py` `scrape()` with a `CreditGuard` whose
  budget is `--firecrawl-credit-cap`, and with `max_pages=1`. That reuses the MODEL-43
  truncation and cost guards.
- The default cap is **0**. CI passes **10** with `--firecrawl-key-from-env` (see Part 2). With cap 0 the Firecrawl module is
  never called, and no key is resolved. JS-host sources are then listed under
  `needs_js_not_rendered`, and their plain-HTTP reading is still watched.
- When the guard raises `CreditBudgetExceeded`, the run stops using Firecrawl, finishes the
  rest on plain HTTP and records `firecrawl.stopped: true`.
- The watcher never prints or logs a key.

## Drafter contract

The drafter treats all fetched content as untrusted and runs with no tools:
`claude -p --output-format text --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence`,
in an empty temp directory, with only PATH, HOME, USER, LOGNAME and the Claude auth variables passed
through. The source text is wrapped in random `<<<UNTRUSTED_SOURCE_…>>>` delimiters, and a draft that
adds a URL outside the page's existing sources and the watched URL is rejected.

`scripts/curation/draft.py`. The drafter is tool-agnostic. Any drafter is a callable
`(prompt, page_text) -> revised full page`, which must include front matter.

- `ClaudeDrafter` runs `claude -p --output-format text`, with the prompt on stdin. It
  extracts the page between `<<<BEGIN PAGE>>>` and `<<<END PAGE>>>`. CI job 2 runs it with
  `CLAUDE_CODE_OAUTH_TOKEN`.
- `FakeDrafter`, selected by `--dry-run`, is deterministic. It adds or refreshes the watched
  source in `sources` with today's accessed date. Tests inject broken drafts through
  `transform`.

The prompt embeds `benchmarks/AUTHORING.md` verbatim, then these binding rules:

1. Change only what the source text supports; otherwise return the page unchanged.
2. Every added or changed fact cites the watched URL in `sources` with `accessed: today`.
   Nothing else may be cited.
3. Unknown stays empty; nothing comes from memory and no number is rounded.
4. When sources disagree, record both readings in the prose with sources and dates, and
   leave the field empty unless the source is authoritative.
5. Keep `id`, the headings and their order. Do not author `models_covered`.
6. Do not edit `freshness`; the pipeline stamps it.
7. Output the full file between the markers, and nothing else.

Gate, in order:

1. Stamp `freshness.researched = today` and `researched_by = <drafter label>`.
2. Write the draft to a scratch file.
3. Run `scripts/benchmarks/validate.py` `check()`.
4. Run the curation checks: the id is unchanged, the watched URL is cited with today's
   date, and no existing source was dropped.
5. If any check fails, discard the draft. Nothing is written and the page is untouched.
6. If all pass, write the draft to `benchmarks/_curation/drafts/<id>.md`. Only `--apply`
   overwrites the page.

Freshness is therefore updated only on accepted drafts.

## PR gate

`scripts/curation/propose.py`. The default is a dry run, which writes
`benchmarks/_curation/reports/pr_bodies.md`. `--open-prs` is used by CI job 2 (or a human).

**Batching: one branch and one draft PR per changed page**, named
`curation/benchmarks/<id>-<date>`. Reviewers check a page against its sources, so per-page
PRs keep reviews small. One bad page can be closed without blocking the others, and a
revert touches one file.

Each PR body lists:

- the detected change kinds with their evidence
- every source cited in the edit, with its accessed date
- the validator result

Rejected drafts and no-change drafts produce no PR and appear only under "Skipped".

## Freshness on the site

Every page already carries `freshness.researched` and `freshness.researched_by`, and the
validator requires them. **The site does not render them on benchmark pages yet.**
`pipeline/render.py` shows only a catalogue-level freshness notice for models. Rendering is
left to a follow-up, because this ticket does not touch `pipeline/render.py`.

## Immediate brief

Run `watch.py --immediate-brief <page-id|URL>`, or dispatch the workflow with
`immediate_brief`.

- **A page id** watches that page now.
- **A URL** watches every page that cites it, either exactly or as a URL prefix.
- **A URL no page cites** is recorded under `census_leads` in the report. That is how a
  newly released benchmark enters the census queues. CI job 2 appends it to
  `benchmarks/_census/` in the curation PR (see Part 2, decision E).

## Scheduler

`.github/workflows/curation-benchmarks.yml`. Triggers: `schedule` (weekly Monday 06:17 UTC,
plus the temporary daily 06:47 UTC trial cron) and `workflow_dispatch` with `axis`, `pages`
and `immediate_brief`. There is no `pull_request` trigger, so no secret reaches a PR or fork
run. Workflow permissions are `contents: read`; concurrency is one run at a time with no
cancel in progress. Inputs reach the shell through `env`, never interpolated into `run`.

| Job | Runs when | Permissions | Secret (one step only) |
| --- | --- | --- | --- |
| `gate` | always | contents: read | none |
| `watch` | gate says run | contents: read | `FIRECRAWL_API_KEY` in the watcher step |
| `draft` | schedule or dispatch, and watch found draftable changes or census leads | contents: read | `CLAUDE_CODE_OAUTH_TOKEN` in the drafter step; `RESEARCH_PR_TOKEN` in the open-PRs step |
| `issues` | watch found `leaderboard_dead` | contents: read, issues: write | `GITHUB_TOKEN` |

`watch` uploads `benchmarks/_curation/reports/` (the change report plus each changed
source's text under `sources/`). `draft` and `issues` download it.

### How MODEL-5 moves in later

This is one shared scheduler, parameterised by axis:

1. Add `models` to the `axis` choice.
2. Give `watch.py --axis models` a page loader over `models/*.md`. It returns
   `(url, role)` from card sources, and the model axis gets its own cache key through
   `curation-state-${AXIS}`.
3. Move the research step of `daily-research.yml` into this workflow behind
   `axis == 'models'`, then delete the old workflow. That has to wait until MODEL-65's edit
   lands, so part 1 does not touch it.
4. The drafter and the PR gate are already axis-neutral. Each needs the model validator in
   place of `scripts/benchmarks/validate.py`.

## Part 2 (live)

Part 2 turns on drafting, PRs and issues in CI. Jamie's decisions of 2026-09-15:

- **A. Drafter credential.** Repo secret `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`),
  exposed only in the drafter step's env. Claude Code is installed with
  `npm install -g @anthropic-ai/claude-code@2.1.267` (pinned; npm's `stable` tag on 2026-09-15).
  The call is unchanged: no tools, strict MCP config, no setting sources, no session
  persistence, empty temp cwd. The env allowlist (`DRAFTER_ENV_KEYS`) is PATH, HOME, USER,
  LOGNAME, `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_API_KEY`. It never carries
  `FIRECRAWL_API_KEY`, `RESEARCH_PR_TOKEN` or `GH_TOKEN`. An empty token fails the step.
- **B. PRs.** Repo secret `RESEARCH_PR_TOKEN`, only in the open-PRs step, so required checks
  run. Checkout uses `persist-credentials: false`; the step sets a masked git
  `http.extraheader` from the token after drafting and removes it at the end. One **draft**
  PR per changed page, branch `curation/benchmarks/<id>-<date>`. A page that already has an
  open `curation/benchmarks/<id>-*` PR, or a branch that already exists, is skipped, so daily
  runs do not stack PRs. Nothing auto-merges: `automerge.yml` skips draft PRs, and
  `propose.py` never marks a PR ready or merges. Marking a curation PR ready is a human act;
  `automerge.yml` would then queue it like any agent PR, because MODEL-44 forbids prefix
  rules in its `if` (a curation exclusion needs Jamie's call).
- **C. Firecrawl.** Cap **10 credits per run** from repo secret `FIRECRAWL_API_KEY`, only for
  `js_hosts.yaml` hosts on the census allowlist, through the `CreditGuard` path.
  `--firecrawl-key-from-env` makes an empty secret fall back to plain HTTP only (effective
  cap 0). The run does not fail; the report records `requested_cap`, `cap: 0` and the note
  "FIRECRAWL_API_KEY is empty: plain HTTP only".
- **D. 7-day run.** See below.
- **E. Census leads.** `scripts/curation/ci.py append_census_leads` writes census.py's own
  formats: one `candidates.jsonl` line (`name, slug, source, url, evidence, category_hint,
  kind, priority`, source `curation:immediate_brief`, kind `lead`, priority 3) and one
  `queue_p3.json` entry (`slug, name, aliases, sources, source_count, urls, harness,
  category_hint, priority, downloads, score`). A URL already in `candidates.jsonl` or any
  `queue_p*.json`, or whose slug is already queued, is skipped. The files ride in the first
  page PR of the run, or in a `curation/benchmarks/census-leads-<date>` draft PR if no page
  changed.
- **F. Dead leaderboards.** `leaderboard_dead` never drafts. The `issues` job (GITHUB_TOKEN,
  `issues: write`) opens one issue per page titled `curation: leaderboard dead for <id>`, with
  a hidden `<!-- curation-leaderboard-dead:<id> -->` marker. If an open issue carries that
  marker, the job comments on it instead.

### 7-day trial and revert

- Day 0: dispatch `pages=pilot` to baseline (or let 2026-09-16 be the baseline).
- The daily cron `47 6 * * *` runs 2026-09-16..2026-09-23 inclusive: 8 runs, baseline plus 7.
  During the window the weekly cron is skipped, so Monday 09-21 does not run twice.
- **Guard: a date window in `scripts/curation/ci.py gate`**, not a run counter. An Actions
  cache counter can be evicted (7 days unused, 10 GB limit) or raced, and a failed run would
  shift the end. The window is deterministic, needs no state, and is unit-tested. After
  09-23 the daily cron fires but the gate job skips everything in seconds.
- **2026-09-16 was lost.** Run 35066344154 reported `Trial gate=success` and skipped every
  downstream job: the gate job installed no dependencies, so `ci.py` died on `import pydantic`,
  and `| tee -a "$GITHUB_OUTPUT"` returned tee's status instead of the gate's. Both are fixed
  (the gate now installs the same deps as the other jobs, every `$GITHUB_OUTPUT` pipe sets
  `pipefail`, and a gate with no `run=` fails with `::error::`). The baseline therefore moves
  to 2026-09-17, which leaves only 6 comparison runs before 09-23: **Jamie decides whether to
  push `TRIAL_END` to 2026-09-24** to keep baseline plus 7.
- **Revert to weekly after 7 runs:** delete the `47 6 * * *` cron line and the
  `DAILY_CRON`/`TRIAL_*` window in `ci.py` (and its test), then widen to `pages=all`.
- Pass: 7 consecutive green runs, no-change pages produce no PR, and at least one real change
  goes end to end to a merged PR with a dated source.

## What is not built

- Automatic `saturation_crossing` and `dataset_change` detection.
- Rendering `freshness.researched` on benchmark pages.
- The `models` axis.
- Any auto-merge, which is out of scope permanently.
