# MODEL-408-cite: citation-only xAI consumer lineup

2026-10-19. Reworks code PR #822 and private data PR #96. Both remain drafts.
The code PR depends on #840 merging first. The orchestrator must advance the
private `.engine-pin` only after #840 and #822 have merged.

## Revisions and scope

- Initial code: `f8e78f4b8d0e56b9a2696b9e6a3110381a97bb8c`.
- Merged #840 at `58482dc3d50a9b8746662e8033fb14274e5a1788`, then main at
  `6568b0ebf939aca0aab05652e72eda2bda2dcdcc`. No rebase or reset.
- Integration HEAD: `ffd4e74a017b96c60f7450fd2cffcad3e63bc3d8`.
- Initial private data: `9cb9260f394e8d6b0c0300c5c5091c502ee482bb`.
- Final private data: `c11e335c0f9d5a36a990920963ccdf748aadae77`.
- Final tested code revision: `95944ce7248e07aebaf5b93a2b4d9a27fe0f1191`.
  Full-suite result is pending below. The final
  evidence-only commit is discoverable with `git log -1 --format=%H --
  docs/evidence/g2-ios/MODEL-408-cite-fix.md`.

#840 supplies the shared host policy, metadata-only CopyStore behavior,
verification interception and citation serialization. MODEL-408 now exercises
those paths with synthetic fixtures for both `x.ai` and `docs.x.ai`.
`read_matrix()` still parses transient input without changing the extracted
prices, billing periods or product inclusion values. Its parser controls
disable the host policy only inside their test fixture; separate integration
tests use the production policy and assert `cited` with no verification.

Merge conflicts were limited to billing test isolation in
`tests/replay_billing_launch.py` and `tests/test_billing_launch.py`. The runtime
stub restoration and both sets of assertions survive. The focused billing
and first citation regressions passed together (42 tests).

The historical capture command referenced by the original MODEL-408 evidence,
`docs/evidence/g2-ios/MODEL-367/capture.mjs`, bypassed retention by writing HTML,
text, screenshots and DOM bindings. It now refuses before browser imports or
file writes. The old MODEL-408 evidence is explicitly marked superseded.

## Red-first checks

| Defect / behavior | Red result | Green result |
| --- | --- | --- |
| `test_current_plan_recheck_persists_citation_without_page_bytes`, both hosts | Raw CopyStore objects existed, 2 failures | Metadata retains URL, original fetch time and hash; no page file |
| `test_current_plan_verification_is_cited_without_a_retained_copy`, seven plans and both hosts | 14 failures: outcome was not `cited` | All six facets return `cited`, no verification, no store writes |
| Private `audit_cite_only.py` | 38 assertion failures in 6 tests: missing citation metadata, retained artifacts and machine-verification records | 6 tests pass; every existing value/state unchanged |
| `test_xai_capture_helper_is_retired_before_browser_or_output` | Offline browser stub reached: `launch attempted` | Helper exits 1 with cite-only retirement message; no browser import or output directory |
| Collect `test_cite_only_collector_writers.py` with only `.[dev]` installed | CI and isolated Python 3.11 collection exit 2: `ModuleNotFoundError: No module named 'pypdf'` | 35 collector tests pass; full isolated collection finds 12,528 tests with no errors |

The first 16 citation failures ran against the initial code before the #840
merge. See [red output](MODEL-408-cite/citations-red.log.gz). The expanded
integration suite checks all seven plans, two hosts and six verifier facets,
plus a snapshot round-trip of the unchanged values.

The snapshot test initially used the model-fact lookup for subscription facts,
then expected a `+00:00` timestamp instead of the serializer's equivalent `Z`.
Those were test setup/assertion errors, corrected to use
`subscription_offerings()` and the actual wire timestamp. The private proof
initially tried to build verification claims for unknown facts; it now checks
their unknown state and absence from admitted snapshot values instead.
Existing assertions were not relaxed.

The capture regression uses a Node loader that replaces Playwright with an
offline synthetic stub and rejects unexpected imports. Its exact red/green
commands and exit codes are in
[capture evidence](MODEL-408-cite/capture-retired-evidence.json).

After the first push, CI [pytest shard 1](https://github.com/turbobeest/modelspec/actions/runs/39289751948/job/118186999108)
and [performance/collection](https://github.com/turbobeest/modelspec/actions/runs/39289751948/job/118186999699)
failed before test execution. The merged #840 collector test imports a PDF
collector whose `pypdf` dependency was absent from `.[dev]`. The shared local
environment already had pypdf 6.19.0 and had concealed this packaging gap.

An isolated Python 3.11.15 environment installed from `.[dev]` reproduced the
missing import. Adding `pypdf>=6.19` to the development extra and regenerating
the CLI bundle's input fingerprint fixed it. The first reinstall correctly
rejected that stale fingerprint; the reinstall after regeneration passed.
The clean environment resolved pypdf 6.21.1, passed all 35 synthetic collector
tests, and collected all 12,528 tests without import errors. The runtime CLI
dependency set is unchanged. Commands, direct exits, versions and timings are
in [isolated environment evidence](MODEL-408-cite/py311-ci.json).

## Private migration and export proof

Private data PR #96 removes 45 retained-copy and obsolete helper files from
its added capture/reuse/data-plan directories. Six source records retain only
status, URL, original retrieval timestamp and SHA-256. All 77 facts across
the 12 xAI offerings preserve their semantic fields; the 35 new facts gain
their original retrieval timestamp. The 17 new machine-verification records
are removed, and 17 completed queue outcomes become `cited`. Earlier queue
and verification history is byte-preserved. Registry entries and `.engine-pin`
remain unchanged. The pin stays `a22355bf9c3d9511ff563494791dd99282411898`.

The private audit compares the final tree to the original PR head without
copying source bodies. The final PR diff against private `origin/main` has no
retained-copy files. Its audit script and migration report are in private
`docs/evidence/g2-ios/MODEL-408/` and `MODEL-408-fix.md`; original red/green logs
remain in the private worktree's `tmp/model-408-cite/data-agent/` scratch.

The updated engine built the private Worker exports with a test signing key.
The premier gate reported **known 26, explicit null 18, gap 0** for both
snapshot formats; outside-premier gaps were `codefuse` and `infgrad`.
The bundle imported using only declared dependencies. The executable
[private proof](MODEL-408-cite/verify_private.py) validated all 35 facts,
called production `verify()` for all 17 known facts with page reads forbidden,
and checked both signed snapshots: 17 known values cited with null
verification, 18 unknown values absent. URL, original timestamps and hashes
survive in both formats. Outputs contain counts, not private page content.
See the [vendor output](MODEL-408-cite/private-vendor.log.gz),
[private proof output](MODEL-408-cite/private-proof-final.json), and
[final audit output](MODEL-408-cite/private-audit.log.gz).

Private CI [Approved answers on private data](https://github.com/turbobeest/modelspec-data/actions/runs/39289298641/job/118185436862)
stops in `Verify the engine pin is on modelspec main`, before data validation:
`.engine-pin a22355bf9c3d9511ff563494791dd99282411898 is not a commit on modelspec main`.
The pre-existing pin was deliberately preserved as required by the spec.
The local updated-engine checks above pass, but they do not satisfy this
separate ancestry check. The orchestrator must update the pin to merged main
after #840 and #822 merge before the data PR can pass that check.

## Commands and results

Run from `/Users/terbeest/dev/worktrees/model-408` unless stated. Python is
`/Users/terbeest/dev/modelspec/.venv/bin/python` (3.14.4), pytest 9.1.1,
Node 22.22.3, npm 10.9.8, Git 2.50.1, gh 2.102.0. Node PATH prefix:
`/Users/terbeest/.nvm/versions/node/v22.22.3/bin`.

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export PYTHONPATH=$PWD
py=/Users/terbeest/dev/modelspec/.venv/bin/python

# Initial red; exit 1, 16 failed.
"$py" -m pytest -q tests/test_xai_consumer_citations.py

# Final focused; exit 0, 804 passed.
"$py" -m pytest -q tests/test_xai_consumer_citations.py tests/test_xai_consumer_lineup.py tests/test_xai_matrix_reader.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_decision_verify.py tests/test_decision_snapshot.py

# Capture guard plus consumer/citation suites; exit 0, 203 passed.
"$py" -m pytest -q -p no:cacheprovider --basetemp=tmp/model-408-cite/review/retired-green tests/test_xai_capture_retired.py tests/test_xai_consumer_citations.py tests/test_xai_consumer_lineup.py

# Private data checks; exit 0, 6 tests passed.
PYTHONDONTWRITEBYTECODE=1 "$py" /Users/terbeest/dev/worktrees/data-model-408/docs/evidence/g2-ios/MODEL-408/audit_cite_only.py 9cb9260f394e8d6b0c0300c5c5091c502ee482bb

# Private export and signature/citation proof; both exit 0.
MODELSPEC_SNAPSHOT_KEY=model-408-cite-test-key "$py" api/worker/vendor.py --data-dir /Users/terbeest/dev/worktrees/data-model-408 --out tmp/model-408-cite/root/private-worker --check
PYTHONDONTWRITEBYTECODE=1 MODELSPEC_SNAPSHOT_KEY=model-408-cite-test-key "$py" docs/evidence/g2-ios/MODEL-408-cite/verify_private.py --data-dir /Users/terbeest/dev/worktrees/data-model-408 --bundle tmp/model-408-cite/root/private-worker

# Generators and sites; each exit 0.
"$py" -m pipeline.agent_copy check
"$py" -m api.worker.openapi --check
"$py" -m qa.contracts
git diff --exit-code -- qa/fixtures
"$py" -m pipeline.build --out dist
"$py" -m pipeline.surface_lint --tree dist/modelspec
(cd web && npm ci && npm run build && npm test)

# Release/data guards; both exit 0.
"$py" scripts/chart_check_pr.py --base origin/main
"$py" scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-408-xai-consumer

# Full suite under the shared lock; result recorded below when complete.
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Direct subprocess/tool exit codes were checked; no test status was inferred
from a pipe. Focused engine tests: **804 passed**. Consumer parser/matrix/
citation tests: **263 passed**. Site surface lint: **0 findings, 5,366 files**.
Web: **902 tests passed, 57 files passed, 1 file skipped**. Initial generator
checks needed no artifact changes. After the CI dependency correction,
`pipeline.agent_copy write` refreshed only the CLI bundle's pyproject hash;
`pipeline.agent_copy check` then passed again (exit 0). The release-chart guard had no evidence
changes to check. The data-freeze guard passed.

Exact public-check arguments, working directories, timings, versions and exit
codes are in [public-checks.json](MODEL-408-cite/public-checks.json). Compressed
logs and private aggregate proof are alongside this report.

## Limits

No live xAI/docs.x.ai request, paid-provider call, deployment or production
switch change was made. This migration does not re-establish the truth of
the curated facts; it preserves their values and lowers their assurance to
citation-only. No legal terms, ranking floors or contract ranges changed.

Deletion removes retained artifacts from this PR's final tree/diff. It does
not erase historical Git objects or perform the separate MODEL-409 cleanup
of older retained material. Both PRs require review and stay drafts. No merge
was attempted. Site hardware source-registration warnings and web runtime
font URL notices remain; the corresponding build commands passed.
