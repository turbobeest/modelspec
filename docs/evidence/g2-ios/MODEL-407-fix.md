# MODEL-407 execution evidence

Base SHA: `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`.
Design-first commit: `008da9cc`.
Draft PR: https://github.com/turbobeest/modelspec/pull/820.
Initial implementation SHA: `9bdc7ec7a8566bba47e7a5d332fe980a1dae0598`.
Private follow-up began at `8df90ee01e6a10c08058ffef5966c16026aaae7d`.
Final executable implementation: `bb41f0f68cb90c0616263e4c4853c77ee3d916a4`.
The final evidence commit is the branch HEAD printed in the execution marker.

The private acceptance target passes: implementation `bb41f0f6` with data
`74947c3` and the successor loaded retains **104.57278 MiB**, below 115 MiB.
Warm rollover retains **104.61679 MiB**. The required historical matrix and
fresh public/private builds are complete. The original current-period public
pass alone did not establish acceptance; the follow-up fixes below were needed.
The new full-suite run is queued under the required shared lock.

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
| Only the current period is measured | New period/workflow regressions fail; the old implementation exceeds 115 MiB with `--successor` | Both candidate periods have a failing 115 MiB gate and matching main baseline |
| Whole snapshot and catalogue JSON text inflates the Wasm heap | `test_canonical_snapshot_does_not_decompress_the_whole_document` fails; the initial private successor retains 130.94 MiB | A shared bounded reader preserves values, shared keys, exact signed hashes and gzip integrity |
| Policy evaluation holds all rows before paging | Four `test_paged_policy_bounds_retained_rows_without_losing_catalogue_provenance` cases retain 200 live rows against a bound of 15 | Aggregate the entire catalogue while retaining only the page and required examples; all four pass |


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
| Initial implementation, current | 104.47210 | 59.875 | Exit 0 at 115 MiB |
| Initial implementation, successor | 115.58447 | 71.875 | Exit 1 at 115 MiB |
| Final `bb41f0f6`, current | 104.48928 | 59.875 | Exit 0 at 115 MiB |
| Final `bb41f0f6`, successor | 104.51080 | 59.875 | Exit 0 at 115 MiB |
| Final `bb41f0f6`, warm rollover | 104.53250 | 59.875 | Exit 0 at 115 MiB |

The initial current-period implementation had 10.53 MiB of public headroom,
but the successor-period check exposed a failure. The two baseline
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

| Private combination | Engine | Data | Steady bytes | Steady MiB | Wasm MiB |
| --- | --- | --- | ---: | ---: | ---: |
| Base | `7908f238` | `fd3145c` | 109,048,943 | 103.99718 | 59.875 |
| Plus data#93 | `7908f238` | `74947c3` | 121,685,659 | 116.04849 | 71.875 |
| Plus #813 successor | `b4a7074f` | `fd3145c` | 121,048,098 | 115.44046 | 71.875 |
| Both | `b4a7074f` | `74947c3` | 122,224,715 | 116.56257 | 71.875 |
| Initial implementation, current | `8df90ee0` | `74947c3` | 122,218,799 | 116.55693 | 71.875 |
| Initial implementation, successor | `8df90ee0` | `74947c3` | 137,295,447 | 130.93514 | 86.25 |
| Initial implementation, warm rollover | `8df90ee0` | `74947c3` | 137,346,492 | 130.98382 | 86.25 |
| Final implementation, current | `bb41f0f6` | `74947c3` | 109,651,736 | 104.57204 | 59.875 |
| Final implementation, successor | `bb41f0f6` | `74947c3` | 109,652,504 | 104.57278 | 59.875 |
| Final implementation, warm rollover | `bb41f0f6` | `74947c3` | 109,698,653 | 104.61679 | 59.875 |

The historical four-cell runs exit successfully at the unchanged 120 MiB
deployment gate. All three initial implementation runs fail the 115 MiB gate;
all three final implementation runs exit 0 at that same 115 MiB gate.
The successor run uses the same four requests at the current period's UTC
boundary. Warm rollover first serves the current decision, advances to the
boundary, repeats that decision request, and runs the remaining three requests.
It asserts the predecessor is released before reading the successor bytes.

Post-sample private attribution for the initial implementation measures
4,044,223 bytes for the loaded snapshot index, including 2,367,442 bytes for
general provenance and 51,644 bytes for hardware provenance. Vocabulary
accounts for 636,274 bytes. These categories overlap and are not additive
Worker allocation estimates.

Private bundles, snapshots, and probe outputs stay under the authorized
`/tmp/model-407-private` directory. No private inputs or generated private
bundles belong in this public repository. Public evidence from private
measurements contains only memory numbers and commit SHAs. The detached data
worktrees were removed and `/tmp/model-407-private` was verified empty after
exporting those permitted measurements.

The final public and private runs allocate the same 59.875 MiB Wasm heap.
Their steady totals differ by less than 0.09 MiB in each matching scenario,
providing measured calibration for the committed public recipe. The highest
final private result leaves 10.38 MiB of headroom below the 115 MiB gate.
The [private memory-only results](MODEL-407/private-memory-numbers.json) and
public [current](MODEL-407/public-final-current.json),
[successor](MODEL-407/public-final-successor.json), and
[warm rollover](MODEL-407/public-final-warm.json) artifacts record the samples.
The historical local cells do not reproduce the ticket's earlier deployment
figures; the table reports the controlled measurements observed here.

`docs/model-407-recall-private.patch` supplies the requested manual private
workflow change. It is not applied to the private repository. Workflow changes
exclude this PR from automerge, and the PR remains a draft.

## Follow-up parsing and policy verification

The bounded JSON reader delegates strings, numbers and literals to the standard
JSON decoder, shares object keys within a parse, and hashes consumed UTF-8 in
blocks. It avoids retaining a full serialized document next to its parsed tree.
The snapshot writer and format do not change. Legacy noncanonical and deeply
nested inputs preserve their existing hash/signature verification path.

New tests cover chunk boundaries, Unicode and escapes, EOF, malformed syntax,
content tampering before indexing, duplicate outer content, inner last-value
semantics, deep legacy input, and cleanup after a failed parse. Existing gzip
CRC, size, truncation and concatenated-member tests pass. The original 100 ms
load-time limit remains: final standalone samples were 71.64–75.68 ms.

The policy change retains only the requested page and the first ten required
undetermined examples. Full-catalogue verdict counts and provenance still
include off-page rows. Tests cover beyond-end offsets and dates present only
on a final off-page row. Independent local review checked policy response ordering, pagination,
provenance, and parser framing/signature behavior without a blocking finding.
This was self-review; the required cross-model review is pending.

Red/green output is retained in [streaming notes](MODEL-407/streaming-notes.md),
[streaming red](MODEL-407/streaming-red.txt),
[policy retention red](MODEL-407/policy-retention-red.txt),
[policy retention green](MODEL-407/policy-retention-green.txt), and
[catalogue integration green](MODEL-407/catalogue-stream-green.txt).
The policy host-allocation diagnostic fell from 2,985,912 to 375,248 bytes on
the public catalogue. It explains the change; it is not the acceptance probe.

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
That run preceded the private follow-up. The final focused suite passed **640 tests in 227.71 seconds**, direct exit 0,
covering snapshot loading and rollover, hardware responses, rank, policy,
workflow gates, and Worker compression. Its output is in
[focused-final.txt](MODEL-407/focused-final.txt). The new complete suite for
implementation `bb41f0f6` is queued under the shared lock; its final result
will be recorded below.

No production deployment, vendor API spending, live billing transaction,
private-workflow execution, or cross-model review has been observed in this
session. Local tests exercise synthetic billing and signature inputs. Public
CI status and the final memory figures are not inferred from these tests.
