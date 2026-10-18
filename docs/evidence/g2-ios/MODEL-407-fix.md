# MODEL-407 execution evidence

Base SHA: `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`.
Design-first commit: `008da9cc`.
Draft PR: https://github.com/turbobeest/modelspec/pull/820.
Final implementation SHA: `9bdc7ec7a8566bba47e7a5d332fe980a1dae0598`.
Subsequent commits contain execution evidence only. The final evidence commit
is the branch HEAD printed in the execution marker.

Private measurement is authorized under `/tmp/model-407-private`. The required
matrix and final private target remain pending. The public memory gate passes;
it is not a substitute for the private target.

The deployment limit remains 120 MiB. The new public PR gate enforces 115 MiB
and warns when retained memory increases by more than 1 MiB against the same
fixture on main. No ranking, Decision 2.18, bounded 1.5, hardware-fit 2.0,
legal text, or production switches changed.

## Red-first defects and corrections

| Defect | Regression and red result | Correction and green result |
| --- | --- | --- |
| Hardware-specific provenance fields pad every general record | `test_hardware_fit_fields_do_not_pad_every_other_provenance_record` fails because the general table changes | Workload and numeric-input records have a separate signed packed table; 208 focused tests pass |
| Duplicate eager hardware workloads | `test_hardware_fit_snapshot_retains_source_ids_and_one_copy_of_each_record` finds the duplicate; `test_hardware_fit_loads_records_once_on_first_assessment` observes no lazy decode | Workload IDs select records on the first assessment; all four captured response cases match their original bytes |
| Eager successor snapshot and vocabulary | `test_successor_is_not_read_parsed_or_verified_at_isolate_start` and `test_successor_stays_unparsed_through_the_utc_preload_window` fail | Successor payload and vocabulary remain unread until the boundary |
| Old snapshot survives promotion | `test_rollover_releases_current_snapshot_and_vocabulary_before_loading_successor` fails | Weak-reference assertions prove old objects are collectible before successor parsing |
| Deferred load failures lose deliberate refusal behavior | `test_successor_load_failure_stays_a_refusal_on_following_requests` gets 502 instead of 503 | Cache only the error string and consistently refuse the immutable failed bundle |
| Vocabulary request holds old objects across billing await | Both variants of `test_vocabulary_metering_does_not_retain_old_snapshot_or_parsed_vocabulary` find the old snapshot, dictionary and nested facet alive | Release parsed references before metering; 63 focused tests pass and the suspended response retains its original bytes |
| Public memory failures cannot block PRs | The immutable old probe ignores `--limit-mib 1` and exits 0 at 104.35 MiB | The new probe exits 1 for that same valid bundle with the 1 MiB limit; exact threshold and warning tests pass |
| A synthetic workload can be excluded by production selection | The first generated bundle retained zero synthetic hardware rows | Use a model in the production premier slice and test that slice; both generated periods retain all 15 rows |

Hardware red run: 3 failed and 5 passed, exit 1. Successor initial red run:
6 failed, exit 1. Broad successor verification before the concurrency
correction: 250 passed and 1 skipped, exit 0. Existing REV-813 price,
signature, expired-period, comparison, and billing/header assertions remain.
Full logs and exact commands are in [hardware notes](MODEL-407/hardware-notes.md)
and [successor notes](MODEL-407/successor-notes.md).

Hardware golden responses cover measured, full estimate, lower-bound estimate,
and undetermined results through the keyed Worker route. Only the
content-addressed snapshot ID is normalized. Its value necessarily changes
when the signed storage representation changes. The generator
`mcp/test/fixtures/generate-hardware-fit.py` updated exactly two corresponding
snapshot IDs.

The small public fixture's old shared provenance table had 41 fields and
287 slots. The separate tables have 201 slots in total. Each general record
avoids 14 empty hardware columns. These are structural counts, not measured
Worker memory savings; see [the attribution](MODEL-407/hardware-storage.json).

## Measured public memory

Both bundles use the frozen public image plus the committed recipe, the same
synthetic key and four CI requests, Node 22.22.3, and Pyodide 0.28.3. The
runtime reports Python 3.13.2 and Pydantic 2.10.6.

| Public synthetic bundle | Steady MiB | Wasm MiB | Result |
| --- | ---: | ---: | --- |
| Starting `b4a7074f`, first sample | 115.41149 | 71.875 | Measurement-only exit 0 |
| Starting `b4a7074f`, enforcing 115 MiB | 116.47690 | 71.875 | Exit 1 |
| MODEL-407 implementation | 104.47210 | 59.875 | Exit 0 at 115 MiB |

The implementation has 10.53 MiB of measured public headroom. The two baseline
runs show about 1.07 MiB of V8 variation despite identical Wasm allocation.
The regression warning is deliberately sensitive to increases above 1 MiB;
repeat measurements can distinguish runtime noise from retained growth.

Post-sample object attribution shows one parsed snapshot instead of two and
633,718 bytes of vocabulary objects instead of 1,267,226. The general
provenance table has 134,028 slots plus 1,350 in the hardware table, versus
171,072 shared slots per original snapshot. The candidate provenance table
accounts for 1,997,118 Python object bytes, its separate packed hardware table
for 133,259 bytes, and packed verification values for 319,671 bytes. These
categories overlap and do not sum to the measured Worker allocation.

Exact commands and caveats are in [memory commands](MODEL-407/memory-commands.md).
The [public measurements](MODEL-407/public-memory.json),
[baseline measurements](MODEL-407/public-baseline-memory.json),
[failing gate run](MODEL-407/public-baseline-gate-red.json), and
[bundle admission counts](MODEL-407/public-bundle-metadata.json) are retained.
The original unit-test red output also records missing new helpers and the
uninstalled Pyodide dependency; the separate actual-process runs above prove
the limit behavior without relying on that environment failure.

## Private measurement scope

The private checkout is read-only. The matrix uses engine commits `7908f238`
and `b4a7074f` against private data commits `fd3145c` and `74947c3`. The final
target uses `74947c3` with this implementation.

| Required private combination | Engine | Data | Local measured result |
| --- | --- | --- | --- |
| Base | `7908f238` | `fd3145c` | Pending measurement |
| Plus data#93 | `7908f238` | `74947c3` | Pending measurement |
| Plus #813 successor | `b4a7074f` | `fd3145c` | Pending measurement |
| Both | `b4a7074f` | `74947c3` | Pending measurement |
| Final target with lazy successor | `9bdc7ec7` | `74947c3` | Pending measurement; must be at most 115 MiB |

Private bundles, snapshots, and probe outputs stay under the authorized
`/tmp/model-407-private` directory. No private inputs or generated private
bundles belong in this public repository. Public evidence from private
measurements contains only memory numbers and commit SHAs. The matrix,
measured memory calibration, and final private 115 MiB target remain
unverified until their measurements are recorded above.

`docs/model-407-recall-private.patch` supplies the requested manual private
workflow change. It is not applied to the private repository. Workflow changes
exclude this PR from automerge, and the PR remains a draft.

## Integration commands and limits

Commands run from `/Users/terbeest/dev/worktrees/model-407`, unless noted.
Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` on `PATH`.
Observed versions: Python 3.14.4, pytest 9.1.1, Node 22.22.3, ruff 0.16.6,
gh 2.102.0, npm 10.9.8, and actionlint 1.7.12. Pyodide is pinned to 0.28.3
in the probe and workflows.

```sh
# In web; exit 0.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build

# In mcp; both exit 0.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- test/hardware-fit.test.ts

# At the worktree root; all exit 0.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH actionlint -shellcheck= .github/workflows/rank-api.yml
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --out tmp/model-407/root/import-bundle --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base b4a7074f
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base b4a7074f --head HEAD --branch model-407-worker-memory

# In web after corpus generation; exit 0, 1242 tests pass.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH MODELSPEC_CORPUS_REQUIRED=1 npm test

# At the worktree root; exit 0, 76 tests pass.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_memory.py tests/test_ci_workflows.py tests/test_hardware_fit_memory.py tests/test_snapshot_successor_memory.py

# Required complete suite, after web npm ci. Direct result recorded below.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The site surface check reported zero findings across 5,321 files. Corpus
generation wrote 319 decisions and five vocabularies. The web suite passed
1,242 tests, MCP hardware-fit passed 37, and final focused Python checks passed
76. New-file ruff and actionlint pass. The chart check reported nothing to
check; data freeze passed. The private workflow patch passed `git apply --check`
against a scratch copy of its existing workflow, without changing the private
checkout. Preserved terminal logs have trailing whitespace removed.

The required complete suite finished with direct process exit code **0**:
**11,595 passed, 9 skipped, 11 warnings in 1,410.99 seconds (23 minutes 30
seconds)**. The [complete terminal output](MODEL-407/full-suite.txt) is retained.
Only evidence files changed after implementation commit `9bdc7ec7`; the final
focused run also covered the nonsemantic test-import formatting applied while
the complete suite was running. All started validation processes finished.

No production deployment, vendor API spending, live billing transaction,
private-workflow execution, or cross-model review has been observed in this
session. Local tests exercise synthetic billing and signature inputs. Public
CI status and the final memory figures are not inferred from these tests.
