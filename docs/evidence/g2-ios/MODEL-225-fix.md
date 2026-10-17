# MODEL-225 execution evidence

Status: **BLOCKED for fresh production releases.** The public-bundle executor,
gates and draft transport are implemented. The private merge to approved public
snapshot handoff is not implemented or activated. This evidence does not claim
that a private card merge produced a live blog PR.

## Revision and environment

- Base: `2b2e9a38f19012658f2b390cbb3f00eb8a00ae75`.
- Final implementation SHA: `f92495ba4710023235364833bb16c54074a46bf2`.
- The evidence-only delivery commit follows that implementation. Its exact SHA
  is recorded in the draft PR and executor completion line. Resolve it with
  `git rev-parse model-225-release-pipeline`.
- Worktree: `/Users/terbeest/dev/worktrees/model-225-release-pipeline`.
- Python 3.14.4, pytest 9.1.1, pydantic 2.13.5, cryptography 45.0.7.
- Node v22.22.3, npm 10.9.8, Playwright 1.63.0, Git 2.50.1, gh 2.102.0.
- actionlint 1.7.12, installed by Homebrew, built with Go 1.27.1.

The executor brief, spec, CLAUDE.md and AGENTS.md were read before changes.
Two read-only design candidates and a third read-only design judge compared
polling and dispatch. They agreed that a full fresh private snapshot cannot be
committed as a public blog input under the current data split. A later review
found the retry and publication-date defects below; each received a failing
behavioral test before its fix.

## Red-first defects and results

The first command ran before changing implementation code and exited **1**:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py > docs/evidence/g2-ios/MODEL-225-red.txt 2>&1
```

Observed: `19 failed in 21.03s`. Full output is in
[`MODEL-225-red.txt`](MODEL-225-red.txt).

| Defect | Red-first test | Observed red output | Final green evidence |
| --- | --- | --- | --- |
| Current accuracy output is refused by the blog gate | `test_actual_pr_accuracy_report_is_accepted` | `ValueError: accuracy report must contain the exact pr layers` | Accepted the actual `PROFILES['pr']` report; final focused suite passed |
| No release executor or draft PR workflow | `test_replayed_release_produces_gated_draft_pr_within_one_day`, `test_workflow_gates_before_draft_and_uses_only_public_inputs` | `ModuleNotFoundError: No module named 'release_blog.pipeline'`; `release pipeline workflow is missing` | Launch replay calls a recording draft transport after corpus/page gates, with a one-hour fixture delay and explicit pending evidence |
| No scheduled revision executor | `test_replayed_seven_day_check_appends_dated_update_pr`, `test_recheck_schedule_uses_first_publication` | `ModuleNotFoundError: No module named 'release_blog.pipeline'` | +7 replay creates unpublished r2, includes a dated update, and retains r1 bytes; +1/+7/+30 boundaries pass |
| No pipeline refusals or optional platform adapter | `test_failed_quality_gate_opens_no_pr`, `test_bad_accuracy_writes_no_post`, `test_unsigned_snapshot_writes_no_post`, `test_release_inputs_cannot_reach_private_or_unrelated_paths`, `test_optional_platform_import_failure_is_stated` | `ModuleNotFoundError: No module named 'release_blog.pipeline'` | Bad gates create no draft request; bad accuracy, unsigned input and path escapes create no post; missing platforms are stated |
| Replays after midnight select a second branch | `test_signal_identity_is_stable_across_midnight` | `2026-09-26-lab-alpha` differs from `2026-09-27-lab-alpha` | Branch identity and breakdown bytes match across fresh checkouts on different UTC dates |
| A successful push followed by failed PR creation cannot retry | `test_transport_recovers_push_success_before_pr_failure` | Retrying `git push ... blog/2026-09-26-lab-alpha-r1` exits 1 | Actual workflow script recovers the same commit in a local bare remote, then the offline gh fixture records `--draft`; no second push |
| A symlinked signal bypasses the public input guard | `test_public_bundle_rejects_symlinks[signal]` | `Failed: DID NOT RAISE ValueError` | Signal, snapshot and accuracy symlinks are refused; changed committed input is also refused |
| A delayed first publication exposes the provisional schedule | `test_delayed_publication_requires_the_readers_actual_schedule` | `Failed: DID NOT RAISE ValueError` | Page gate refuses stale dates; regenerated unpublished draft displays the actual publication date and matching +7 due date |

The unsigned-input test was corrected during the first green attempt to remove
the envelope's Ed25519 `signatures` list as well as its legacy HMAC `signature`.
Removing only the HMAC field had left the test snapshot validly signed. The
metadata writer also preserves YAML date types when appending a revision.
No existing behavior assertion was weakened. The social-generator fixture's
accuracy layer name changed to the current authoritative profile name.

The retry, input-boundary and delayed-publication reds were separate commands,
each with exit **1**:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py -k 'signal_identity or transport_recovers' --tb=short > docs/evidence/g2-ios/MODEL-225-retry-red.txt 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py -k 'symlinks or uncommitted' --tb=short > docs/evidence/g2-ios/MODEL-225-boundary-red.txt 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py -k delayed_publication --tb=short > docs/evidence/g2-ios/MODEL-225-publication-red.txt 2>&1
```

Their outputs are retained beside this file. The first two retry tests failed;
the boundary command had one failure and three passes; the delayed-publication
command had one failure.

## Focused verification

Initial implementation, exit **0**, `221 passed in 377.77s`:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py tests/test_release_blog.py tests/test_blog.py tests/test_blog_append_only.py tests/test_social_generator.py tests/test_data_workflows.py --tb=short > docs/evidence/g2-ios/MODEL-225-focused.txt 2>&1
```

The expanded pipeline suite passed 25 tests before the final delayed-publication
test was added. Its output is in `MODEL-225-retry-green.txt`.

Final implementation, exit **0**, `176 passed in 5.65s`:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_release_pipeline.py tests/test_release_blog.py tests/test_social_generator.py tests/test_data_workflows.py --tb=short > docs/evidence/g2-ios/MODEL-225-final-focused.txt 2>&1
```

That final focused command includes all 26 pipeline tests, the existing generator
and social suites, and the private-data workflow leak guard. Publication and
append-only suites are also included in the full run below.

## Broader verification

The final full suite on implementation SHA `f92495ba` exited **0**:
**11,260 passed, nine skipped, 11 warnings in 1670.53 seconds**.
`CI=true` and installed Chromium made the Python landing/social-card browser
checks run. The nine skips concern live API opt-ins, absent source cache,
optional `litellm`, an optional dist scan and two existing placeholder cases.
None is a missing browser prerequisite. The warnings concern unsigned fixture
vocabulary in existing CLI tests. Full details are retained in
[`MODEL-225-final-full.txt`](MODEL-225-final-full.txt).

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD CI=true /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile -ra > docs/evidence/g2-ios/MODEL-225-final-full.txt 2>&1
```

An earlier full run was started before the final review fixes and is retained
as `MODEL-225-full.txt`. It was superseded by the final-code run and explicitly
terminated with `kill -TERM -- -28003` to avoid duplicate CPU use. Its observed
exit was **143**. It is not a passing validation claim.

Both sites built, exit **0**. The resulting tree contains 8,090 modelspec files
and the one-file benchgraph redirect. Social cards rendered in Chromium:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD MODELSPEC_RENDER_SOCIAL_CARDS=1 /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist > docs/evidence/g2-ios/MODEL-225-build.txt 2>&1
```

Web installation and Chromium installation both exited **0**:

```bash
# Working directory: web/
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npx playwright install chromium
```

Corpus generation exited **0**, writing 319 decisions and five vocabularies:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD CI=true /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__ > docs/evidence/g2-ios/MODEL-225-corpus.txt 2>&1
```

From `web/`, each of these exited **0**. Build output is retained in
`MODEL-225-web-build.txt`. Vitest reported **53 files and 1,242 tests passed**.
Chromium reported **104 passed, six skipped** in 16.6 seconds. The six skipped
cases require the disabled human/visit gate build variants:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-225-release-pipeline CI=true MODELSPEC_CORPUS_REQUIRED=1 npm run build > ../docs/evidence/g2-ios/MODEL-225-web-build.txt 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH CI=true MODELSPEC_CORPUS_REQUIRED=1 npm test > ../docs/evidence/g2-ios/MODEL-225-web-test.txt 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH CI=true MODELSPEC_CORPUS_REQUIRED=1 npx playwright test --config=playwright.corpus.config.ts > ../docs/evidence/g2-ios/MODEL-225-browser.txt 2>&1
```

Workflow and whitespace checks exited **0**:

```bash
actionlint -version
actionlint .github/workflows/release-breakdown.yml
git diff --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 2b2e9a38f19012658f2b390cbb3f00eb8a00ae75 --head HEAD --branch model-225-release-pipeline
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
```

The shard planner assigns 69 files to each shard with predicted durations
within 0.003 seconds. No shard weights were changed.
Data freeze reported `ok`. Surface lint checked 5,279 HTML/Markdown files with
zero findings.

## What was not observed or activated

- No real private card merge, live keyed release export, production dispatch,
  live blog PR, or measured private-merge-to-PR latency was observed.
- Replay PR receipts are an offline recording transport, including an actual
  local bare-remote push/retry with a fake gh executable. They are not GitHub
  blog publication events.
- The existing corpus uses synthetic and frozen-image snapshots. It was not
  substituted with the release S1. S1 has its matching accuracy-report gate;
  page validation uses the actual generated S1 breakdown and retained signatures.
- MODEL-226's module is absent on this branch. The skip path is tested, and
  its callable interface is documented. Platform generation/posting was not
  observed and `release_blog/platforms.py` was not created or edited.
- No secret or repository variable was created. The proposed private-repository
  secret `MODELSPEC_RELEASE_DISPATCH_TOKEN` and the public editorial export
  contract remain activation blockers, documented in
  [`docs/release-blog-pipeline.md`](../../release-blog-pipeline.md).
- No private data checkout, raw card/log export, vendor API spend, wsl gate,
  SSH/SCP, device operation, tmux operation, workflow dispatch, merge, social
  posting, production switch change, or Linear write was performed.

The executor draft PR is the code/evidence delivery artifact only. Jamie must
resolve the editorial snapshot scope and authenticated private handoff before
MODEL-225 can be considered production-complete.
