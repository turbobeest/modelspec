# Curation loop (MODEL-10)

The curation loop keeps `benchmarks/*.md` current. It watches every source a page cites.
When a source changes, a drafter proposes an edit, the validator gates it, and the edit
reaches `main` only through a human-merged pull request. The loop edits Markdown, never
the graph. Nothing auto-merges.

Part 1 (this change) builds the watcher, the classifier, the drafter interface and the
PR gate. It runs the watcher weekly in CI, with no secrets, no drafter call and no PRs.

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
- The default cap is **0**, and CI part 1 pins it at 0. With cap 0 the Firecrawl module is
  never called, and no key is resolved. JS-host sources are then listed under
  `needs_js_not_rendered`, and their plain-HTTP reading is still watched.
- When the guard raises `CreditBudgetExceeded`, the run stops using Firecrawl, finishes the
  rest on plain HTTP and records `firecrawl.stopped: true`.
- The watcher never prints or logs a key.

## Drafter contract

`scripts/curation/draft.py`. The drafter is tool-agnostic. Any drafter is a callable
`(prompt, page_text) -> revised full page`, which must include front matter.

- `ClaudeDrafter` runs `claude -p --output-format text`, with the prompt on stdin. It
  extracts the page between `<<<BEGIN PAGE>>>` and `<<<END PAGE>>>`. Part 1 runs it locally
  only.
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
`benchmarks/_curation/reports/pr_bodies.md`. `--open-prs` is for human-run local use only.

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
  newly released benchmark enters the census queues: a human or census agent adds it to
  `benchmarks/_census`. Part 1 does not write the queue files.

## Scheduler

`.github/workflows/curation-benchmarks.yml`. It triggers on a weekly `schedule` (Monday
06:17 UTC) and on `workflow_dispatch` with three inputs: `axis` (benchmarks), `pages`
(pilot | all | ids) and `immediate_brief`. It has `permissions: contents: read`, no
secrets and a Firecrawl cap of 0. It restores the state cache, runs the watcher, writes the
summary and uploads `benchmarks/_curation/reports/` as an artifact. Inputs reach the
shell through `env`, never interpolated into `run`.

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

## Part 2 checklist for Jamie

1. **Drafter credential for CI.** Choose one:
   - a Claude Code OAuth token: run `claude setup-token` locally and store it as the repo
     secret `CLAUDE_CODE_OAUTH_TOKEN`
   - an `ANTHROPIC_API_KEY` repo secret

   Scope it to this workflow's environment.
2. **Turn on drafting and PRs.**
   - Add a job after `watch` that runs `draft.py` for each change, then `propose.py --open-prs`.
   - Grant that job only `contents: write` and `pull-requests: write`.
   - Required checks will not run on PRs opened with `GITHUB_TOKEN`, as with MODEL-5. Install
     a PAT or GitHub App token for the PR step.
3. **Firecrawl cap value.** Pick a per-run cap. For example, 10 covers the 8 JS-host pilot
   sources. Credits are 1000 per month, shared with the census. Store `FIRECRAWL_API_KEY` as
   a secret and pass `--firecrawl-credit-cap N`.
4. **7-day run plan.**
   - Day 0: dispatch `pages=pilot` to baseline.
   - Days 1 to 7: run daily by temporarily adding a daily cron (or dispatching by hand).
   - Pass: 7 consecutive green runs, no-change pages produce no PR, and at least one real
     change goes end to end to a merged PR with a dated source.
   - Then revert to weekly and widen to `pages=all`.
5. **Decisions still open.** Where census leads should be written, and whether a
   `leaderboard_dead` should open an issue instead of a draft.

## What is not built

- Drafter and PR steps in CI (no credential).
- Firecrawl use in CI (cap 0).
- Automatic `saturation_crossing` and `dataset_change` detection.
- Writing census queue files from leads.
- Rendering `freshness.researched` on benchmark pages.
- The `models` axis.
- Any auto-merge, which is out of scope permanently.
