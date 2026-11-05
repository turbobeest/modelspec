# MODEL-450 execution evidence

Round two is ready for review. Daily private measurement and the public
counts handoff are implemented and verified locally. Activation requires
merging the draft PRs and a pinned engine containing public PR #970.
MODEL-446/data#127 owns that pin update; this execution did not change it.
No deployed workflow or live artifact transfer is claimed.

Round-two base SHA: `5f1a7d9271bdbf70f6db37dc7cf384e13d27a632`.
Verified implementation SHA: `43d6b032` on `model-450-codex`.
The final evidence/documentation SHA is recorded exactly in `.pr-commit.txt`
and the PR handoff. Obtain it with `git rev-parse HEAD`; this file cannot
contain its own commit hash. Round-one red/green evidence and the latest-ten
release audit remain in this file at the round-two base commit.

## Integration

The new private `release-coverage.yml` runs at 09:07 UTC or by manual dispatch.
It checks out complete main history, validates `.engine-pin` against public
main, then uses that engine to generate private detail and a separate counts
file from one history read and report time. It uploads only that file under
`release-coverage-counts`, then applies private breach issues. Permissions are
`contents: read` and `issues: write`. Only two new files were added in the
private worktree; no existing data file or pin changed.

The public coverage workflow adds an isolated `release-counts` job. It reads
the dedicated artifact from the latest main scheduled/manual run, validates
it in memory, and exports a fixed counts schema. API responses, ZIP size,
JSON size and integer values are bounded. The storage redirect gets no GitHub
token. Missing, stale, malformed or failed input becomes fixed error counts.
The report job receives no private token and validates the counts again before
rendering. The existing `private-health` job remains output-free.

The guard exception accepts only the exact audited writer and output.
Regression tests still reject arbitrary outputs, command suffixes, changed
writer environment or working directory, duplicate writers, caches, artifacts
and summaries in public jobs with private access.

The REST response shapes were checked against GitHub's official
[artifact API](https://docs.github.com/en/rest/actions/artifacts) and
[workflow-run API](https://docs.github.com/en/rest/actions/workflow-runs).
Actual artifact requests were mocked during this execution.

## Red first and green

Public commands ran from `/Users/terbeest/dev/worktrees/model-450`:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo_handoff.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_workflows.py -k release_counts
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_coverage_slo.py -k public_report_waits
```

- Handoff red: 17 failed, exit 1. `--counts-out` and `release-counts` were
  unrecognized, and `scripts.slo.release_counts` was missing. Green: 17 passed,
  exit 0. `test_private_step_produces_counts_file_that_the_public_report_renders`
  exercises the producer and public CLI; transport tests cover sanitization,
  origin checks, token separation, stale dates, size limits and error fallback.
- Guard red: 1 failed, 13 passed, exit 1. The old guard rejected the exact
  audited counts writer. Green: the writer is accepted while mutated writers
  and all other publication channels remain rejected.
- Workflow red: 1 failed, exit 1, `KeyError: release-counts`. Green: the report
  waits for both isolated jobs and reads the validated counts file.

Private command, from `/Users/terbeest/dev/worktrees/data-model-450`:

```bash
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-450 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_release_coverage_workflow.py
```

Red: 4 failed, exit 1, before the workflow existed. Green: 4 passed, exit 0.
The tests verify main/full-history checkout, engine-pin validation, exact
measurement command, least privilege and single-file upload before alerting.

Final public focused suite:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo_handoff.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_coverage_slo.py tests/test_data_workflows.py tests/test_removed_sources.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/slo/release_counts.py scripts/slo/__main__.py tests/test_release_slo_handoff.py tests/test_data_workflows.py tests/test_coverage_slo.py
git diff --check
```

Pytest: `267 passed, 1 skipped in 53.68s`, exit 0. The skip requires a built
site through `MODELSPEC_DIST`. Ruff and diff checks: exit 0. Private workflow
lint and diff checks also passed. No full local suite ran.

Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, pydantic 2.13.5,
httpx 0.28.1, ruff 0.16.6, git 2.50.1. No Node toolchain was used.

## Real private step and public rendering

The scratch clone and exact private measurement command were:

```bash
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-450-scratch/r2-executor/modelspec-data
env GITHUB_REPOSITORY=turbobeest/modelspec-data PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.slo releases --data-dir /tmp/model-450-scratch/r2-executor/modelspec-data --ref origin/main --private-detail --out /tmp/model-450-scratch/r2-executor/private-detail --counts-out /tmp/model-450-scratch/r2-executor/release-counts/coverage.json > /tmp/model-450-scratch/r2-executor/private-step.log
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/r2-executor/render-public.py
```

All exited 0. The render probe compiled the real frozen public snapshot,
called `report --release-report` with the produced counts file, and rendered
JSON, Markdown and HTML. It supplied offline statuses for unrelated external
workflow/feed inputs, so no GitHub or vendor call was made. The release counts
were real, not substituted. Existing public hardware-source warnings did not
prevent rendering.

The probe asserted exact equality between producer and public stage counts,
no per-release or percentile fields in the public handoff, and only the fixed
`modelspec-data` subject in release findings. Output: 3 public report files,
4 release targets rendered, 0 private detail fields exported.

Current 28-day-window counts only:

| Stage | Measured | Completed | Pending | Unknown | Late |
| --- | ---: | ---: | ---: | ---: | ---: |
| Card | 1 | 1 | 0 | 0 | 1 |
| Price | 1 | 0 | 1 | 0 | 1 |
| Score | 1 | 0 | 1 | 0 | 1 |
| Decidable | 0 | 0 | 0 | 1 | 0 |

Historical input errors remain explicit. No discovery or snapshot history was
invented, and these counts do not establish four weeks of attained SLOs.
The private scratch clone, detailed files and redirected private log were
deleted after verification. Only the counts-only handoff remains.

## Not observed

No live schedule, private issue write, artifact upload/download, deployed
public handoff, CI result, site build or four-week SLO attainment was observed.
Both PRs remain draft. `.engine-pin`, frozen data, Worker exports and
production switches were unchanged; no Worker memory probe was needed.
No source-page retention, paid-provider call, Linear write, merge or force
push occurred.
