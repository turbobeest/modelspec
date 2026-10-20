# Coverage targets

MODEL-215. These targets define "every model is up to date and covered". A
daily report measures each target and states every breach. One GitHub issue
per breached target raises the alarm.

- **Report page:** <https://coverage.modelspec-7np.pages.dev/> (a preview branch
  of the modelspec Pages project; no page on the site links to it, and it is
  served `noindex`)
- **JSON:** <https://coverage.modelspec-7np.pages.dev/coverage.json>
- **Workflow:** [`.github/workflows/coverage-slo.yml`](../../.github/workflows/coverage-slo.yml),
  daily at 09:37 UTC, with the report also kept as a 14-day run artifact
- **Code:** [`scripts/slo/`](../../scripts/slo/). Thresholds live in
  [`scripts/slo/targets.yaml`](../../scripts/slo/targets.yaml).
  `tests/test_coverage_slo.py` fails if this table and that file disagree.

## Terms

- **Lineup:** the premier set in `premier/slice-1.yaml`, as the decision
  snapshot admits it: its active models and their metered offerings.
- **Tracked lab:** a lab whose own models.dev page the daily research seeder
  reads (`PROVIDER_MAP` in `scripts/seed_models_dev.py`).
- **Re-read:** the date of a fact's or row's winning verification in
  `verification/log.jsonl`. It is when ModelSpec last checked the value
  against its source, not the source's own date.
- **Live reading:** an evidence row with `date_type: evaluated`, which is a row
  read from a benchmark board. Its evidence date is the board's run or
  observation date, and a re-read does not move it, so its age is the re-read.

## Targets

| id | Target | Threshold | In force |
| --- | --- | --- | --- |
| `new-model-cards` | A model a tracked lab lists on its models.dev page has a card within 24 hours of release | 1 day grace, 30-day look-back | yes |
| `lab-release-feeds` | Every lab with a lineup model is a tracked lab | none | yes |
| `lineup-domain-evidence` | Every lineup model has admitted evidence in each domain its premier clauses claim | none | yes |
| `live-reading-age` | Every live board reading on a lineup model was re-read within 30 days | 30 days | yes |
| `thin-evidence` | Every lineup model has admitted evidence on at least two benchmarks | 2 benchmarks (`MIN_BENCHMARK_COUNT`) | yes |
| `unclassified-evidence` | No evidence row is kept out of the snapshot for want of a `measured_by` | none | yes |
| `lineup-facts-verified` | Every fact stated on a lineup model or offering is verified, and no guaranteed facet is missing | none | yes |
| `offering-price-age` | Every lineup offering's prices were re-read within 7 days | 7 days | yes |
| `plan-age` | Every subscription plan was re-read within 7 days, and its facts are verified | 7 days | yes |
| `premier-speed-age` | Every lineup offering has a ModelSpec speed measurement that ended within 14 days | 14 days | no: in force when the MODEL-230 pilot and baseline have run |
| `workflow-health` | The latest completed run on main of each scheduled workflow, here and in modelspec-data, succeeded, and is not overdue | 1.5 × its cron cadence | yes |
| `refresh-pr-merged` | The newest PR on each scheduled refresh branch merged within 3 days of opening | 3 days | yes |

### How each target is measured

- **`new-model-cards`.** The report reads models.dev once. For each tracked
  page, a listing released between 30 days and 1 day ago is held when the
  seeder would skip it, a card with the same file slug exists under any lab,
  or a card shares its name and release day or its Hugging Face repo. Any
  other listing is a breach. A listing still waiting in an unmerged
  daily-research PR is a breach too: the target is a card on main.
- **`lab-release-feeds`.** A lab is covered when it is tracked and models.dev
  still has its page. The Grok Bot release signals (MODEL-113) are not counted
  as a feed, because they name no lab list and are switched off.
- **`lineup-domain-evidence`.** Premier domains map to registry domains in
  `domain_map` in `targets.yaml`. Evidence in any mapped domain satisfies the
  claim. The evidence must be admitted: verified, sourced and not excluded.
- **`unclassified-evidence`.** Snapshot admission keeps out any evidence row
  with no `measured_by`, under the reason `unclassified` (MODEL-239). Who
  measured a row is never inferred, and the decision contract requires it. The
  target counts those rows over the whole catalogue, not only the lineup, and
  one finding names each model that has any. The fix is on the card.
- **`lineup-facts-verified`.** A fact stated as `unknown` is honest and is not a
  breach. Any other fact the snapshot keeps out is a breach, with the
  compiler's reason (for example `quarantined (mismatch)`), and so is a
  guaranteed facet with no fact at all.
- **`offering-price-age`, `plan-age`.** One finding per offering or plan names
  how many of its facts are overdue and the oldest re-read date.
- **`workflow-health`.** Every workflow with a `schedule:` trigger in
  `turbobeest/modelspec` and `turbobeest/modelspec-data` (MODEL-421). The list
  and each cadence come from the cron lines in the workflow files, so a new
  scheduled job is watched the day it lands; nobody keeps a list. The cadence
  is the longest gap between consecutive firings: 168 hours for a weekly job,
  6 for `41 */6 * * *`. One REST call per workflow reads its ten newest runs on
  main. It is red, with the run's URL, when:
  - its newest completed run concluded anything but `success`, `skipped` or
    `neutral`. A cancelled or timed-out run is red, never skipped over;
  - or its newest run of any kind started more than 1.5 times its cadence ago
    (`stale_factor`), or it has no run on main at all.

  A `skipped` run is a job switched off by its own `if:`, which is a
  production switch, not a failure. `deploy-sites.yml` has no schedule but is
  watched under `unscheduled`, where only a red run counts.

  This report, its log, its page and its issues are public, so
  `modelspec-data` never appears in them by workflow name, run URL, date or
  error text, and no raw `gh` stderr is kept for any repository. On GitHub the
  private repository is checked in a separate job, `private-health`. It is the
  only job holding `MODELSPEC_DATA_TOKEN` (Contents: read and Actions: read).
  It reads the private workflow files and runs through the API with no
  checkout, prints nothing, and uploads or caches nothing. It hands on only
  pass or fail, as its job result. The report job has no private access. It
  turns that word into one line: "scheduled workflow(s) red or unreadable", or
  "could not read run status" when the check was skipped or cancelled. Run
  locally with the token, the report reads the repository itself and shows
  counts only, for example "3 of 6 scheduled workflow(s) red". A missing token
  fails `private-health`, so it is never a pass.

  The detail lives in the private repository. Its own `workflow-health.yml`
  runs `python -m scripts.slo workflows --repo turbobeest/modelspec-data
  --private-detail --issue`, which names each red workflow and its run, and
  keeps one `workflow-health` issue there. That issue closes when everything is
  green. `--private-detail` is refused in any other repository's run.
  `python -m scripts.slo workflows` without it prints the public view and exits
  1 when anything is red.
- **`refresh-pr-merged`.** A refresh re-reads boards on a branch and resets
  `live-reading-age` only when its PR merges, because the report reads main.
  For each branch under `branches` in `targets.yaml` (today only
  `data/weekly-leaderboard-refresh`), one REST call reads its five newest PRs.
  The newest is a breach when it has not merged more than 3 days
  (`max_open_days`) after it opened, whether it is still open or was closed
  unmerged. A branch with no PR yet has nothing unmerged. A verified,
  score-only refresh auto-merges the day it opens, so only a blocked one waits:
  for example a quarantined row, a failed accuracy gate, or the recall ratchet
  that blocked #337. Three days gives a blocked refresh one working day before
  the alert, and the alert plus its 24-hour escalation still land before the
  next weekly run replaces the PR.

## Statuses

Each target is `met`, `breach`, `error` or `not_in_force`.

- `error` means the target could not be measured: an input could not be read,
  or the check measured nothing. A check that saw nothing never reports `met`.
- `not_in_force` targets are measured and shown, but never open an issue and
  never count as met.
- The report is `met` only when every in-force target is `met`.

## Alerts

`python -m scripts.slo alert --apply` keeps one open issue, labelled
`coverage-slo`, per target in `breach` or `error`:

- A new breach opens an issue. Later runs edit its body in place, only when the
  findings change. An edit sends no notification.
- A breach older than 24 hours gets one comment that mentions the `notify`
  handles in `targets.yaml`. That mention is the notification path.
- When the target is met again, a run comments and closes the issue.
- A marker comment in the issue body records the target, when the breach
  began, and whether it was escalated. Duplicate issues for one target are
  closed.

## Running it

```bash
PYTHONPATH=$PWD python -m scripts.slo report --out /tmp/coverage
PYTHONPATH=$PWD python -m scripts.slo alert --report /tmp/coverage/coverage.json
```

`alert` without `--apply` prints the issue changes and makes none. To prove the
alert path without a real breach, add `--stage-breach <target>` to `report`,
then run `alert --apply --only <target>`. Add `--now` with a time more than 24
hours after the first run to prove the escalation comment. A report run
without the staged breach closes the issue. The workflow's `stage_breach`
input does the first step on GitHub.

## The audit (2026-09-29)

The first report was compared with the existing workflows. These gaps were
reported to the orchestrator for tickets:

1. **Release feeds:** eight lineup labs are not tracked: bytedance, jcorners,
   kingsoft, microsoft, querit, tencent, typesafe and zhipu. Carded labs with
   no feed include nvidia, ibm, allen-ai, tii, baai and stability.
2. **Grok Bot signals are off.** `release-signals.yml` skips every hourly run
   because `SIGNALS_ENABLED` is not `true`.
3. **Nothing re-reads prices or plans on a schedule.** Offering prices were
   last verified between 2026-09-25 and 2026-09-28, by one-off collection
   tickets. `offering-price-age` breaches on 2026-10-03 unless a scheduled
   re-read exists by then.
4. **One lineup board has no scheduled re-read.** `leaderboard-refresh.yml`
   re-reads and re-verifies the registered boards weekly, through a PR. It
   has no reader for finbenchmark.ai (`finance_benchmark_v2`), which eight
   lineup models cite, so those readings breach `live-reading-age` from
   2026-10-29. A refresh PR left unmerged also stops the clock resetting,
   because the report reads main. MODEL-232 added the reader and the
   `refresh-pr-merged` target.
5. **`accuracy-nightly.yml` has failed every night from 2026-09-26 to
   2026-09-29.**
6. **Evidence gaps on the lineup:** 19 lineup models have admitted evidence on
   fewer than two benchmarks, and two claim reasoning-and-maths with no
   admitted evidence there.
7. **Subscription plan facts are quarantined:** 13 facts on 11 plans have a
   mismatched verification.
8. **The seeder's coverage stops at models.dev.** A lab not on models.dev
   cannot be tracked by the current feed at all.

### Price re-read age guard

The private weekly `scripts/price_reread.py` job uses N = 7 days, matching
`offering-price-age` and `decision.sources.DEFAULT_INTERVALS`. It attempts
**every** eligible sourced offering price and plan on each run, including
values previously verified by an LLM. There is no recent-value filter that
could omit an older source. Successful reads refresh the dated verification;
changed values require human review of the data PR.

The report records `max_read_age_days: 7` and lists facts whose last usable verification of the current value
is older than seven days or missing in `overdue`. An overdue fact that cannot
enter the read queue also appears in `alerts`, including missing claims,
quarantined values, and pages requiring rendering. It cannot silently remain
outside the job. These reads run in the private writer workflow. Public tests
replay local fixtures and make no network requests.
