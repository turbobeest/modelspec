# MODEL-407 execution evidence

Base SHA: `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`.
Design-first commit: `008da9cc`.
Draft PR: https://github.com/turbobeest/modelspec/pull/820.
Initial implementation SHA: `9bdc7ec7a8566bba47e7a5d332fe980a1dae0598`.
Private follow-up began at `8df90ee01e6a10c08058ffef5966c16026aaae7d`.
Round 2 executable implementation: `bb41f0f68cb90c0616263e4c4853c77ee3d916a4`.
Round 3 executable implementation: `f6dbbcd86845e614a00d3bd7ce8dfa4d55c2f618`.
The final evidence commit is the branch HEAD printed in the execution marker.

The private acceptance target passes for `f6dbbcd8` with data `74947c3`:
**104.57322 MiB** with the successor loaded and **103.69368 MiB** after warm
rollover. The unchanged 100 ms load gate measures **13.30 ms** locally, best
of five with GC disabled. The 648 focused tests, both serial performance
tests and non-performance collection pass. The Round 3 full suite passed
under the shared lock: **11,654 passed, 9 skipped, 11 warnings**, direct exit 0.
CI `pytest perf and collection` passes at `8a0009d4`;
the separate Decision accuracy check also passes (1,301 deterministic tests).

The deployment limit remains 120 MiB. The new public PR gate enforces 115 MiB
and warns when retained memory increases by more than 1 MiB against the same
fixture on main. No ranking, Decision 2.18, bounded 1.5, hardware-fit 2.0,
legal text, or production switches changed.

## Round 3: restore snapshot load time

REV-820 found that the complete Python token loop passed locally near 73 ms
but failed the unchanged MODEL-138 gate in Decision accuracy at **149.30 ms**
best of five. The [original CI failure](MODEL-407/round3/ci-accuracy-before.txt)
records run `39112262794`. The [separate perf-job log](MODEL-407/round3/ci-perf-before.txt)
from run `39112262785`, job `117630715894`, reports the same sole failure at
**208.75 ms** best of five. Its serial command produced one failed and one
passed test; collection was skipped. That log became available after the
superseded workflow was cancelled. There was no additional perf failure.

Profiling located roughly 2.95 million calls in per-value parsing. The change
asks the standard C decoder to parse an array only when the complete array is
already in the existing buffer. Larger arrays keep the incremental path.
The buffer limit, exact-source hashing, gzip verification, signed envelope,
public response bytes and both performance/memory limits are unchanged.

| Measured option | Local best-of-five load | Public successor steady | Decision |
| --- | ---: | ---: | --- |
| Previous Python token loop | 69.98 ms | 104.51080 MiB in Round 2 | CI fails the 100 ms gate |
| Whole-document C decode, text released before indexing | 5.62 ms | 116.48983 MiB | Reject: fails 115 MiB |
| Complete buffered arrays decoded in C | 13.30 ms | 104.51238 MiB | Passes both local limits |

The decoder shares dictionary keys across streamed objects and separate C
calls. A version without that sharing fails all three new
`test_streamed_arrays_share_keys_with_surrounding_objects` cases. The final
reader passes them and the failed-array lifetime case with GC disabled.
The two legacy-depth cases now use nested objects, so buffered-array decoding
does not bypass the fallback those cases exercise. The final reader rerun
passed all 42 tests, direct exit 0.
See [the red result](MODEL-407/round3/key-sharing-red.txt) and
[the focused result](MODEL-407/round3/focused-final.txt).

Fresh public and private bundles were built from committed `f6dbbcd8` by
`vendor.py --data-dir`, with no generated-source patches. All three scenarios
pass 115 MiB using Node 22.22.3 and Pyodide 0.28.3. The private detached
worktree was removed and the authorized private scratch directory is empty.
Only memory values and engine/data commit SHAs were exported.

Local validation: **648 passed in 224.30 seconds**, serial performance
**2 passed, 11,661 deselected in 37.24 seconds**, and non-performance
collection **11,661 of 11,663 tests collected, 2 deselected**, all direct exit 0.
The first collection attempt overlapped a temporary public vendor overlay
and encountered duplicate plugin registrations. After that build exited and
removed its overlay, the exact collection command passed. No collection
configuration or test limit was changed. [CI `pytest perf and collection`](MODEL-407/round3/ci-perf-final.txt)
passes at `8a0009d4` (run `39114952450`, job `117638819060`): **2 passed,
11,788 deselected in 100.54 seconds** on CPython 3.11.17, followed by successful
collection. All four CI pytest shards also pass. The locked local full suite
passed with **11,654 passed, 9 skipped, 11 warnings in 1,306.36 seconds
(21 minutes 46 seconds)**, direct exit 0. The [complete terminal output](MODEL-407/round3/full-suite-final.txt)
records branch HEAD `00a03dbbd837615d90cefee7d32d47e64c266da1`; its runtime
source is identical to measured `f6dbbcd8`, and its tests match the green CI
head `8a0009d4`. Subsequent changes record evidence only. [Decision accuracy also passes](MODEL-407/round3/ci-accuracy-final.txt)
at that PR head (run `39114952430`, job `117638749339`): 1,301 deterministic
tests, 678 parity tests with one skip, and 227 web-adapter tests. The successful
CI output confirms the unchanged assertion without printing its five samples.
[Worker memory headroom also passes](MODEL-407/round3/ci-memory-final.txt):
104.74959 MiB current and 104.74835 MiB successor, each with 59.875 MiB Wasm
and the unchanged 115 MiB bound. That public CI run uses Pyodide 0.28.3 and
Node 22.23.3; the local public/private measurements use Node 22.22.3.

The [timing/profile recipe and samples](MODEL-407/round3/profiling.md),
[public memory commands and artifacts](MODEL-407/round3/memory-commands.md),
and [Round 3 validation commands](MODEL-407/round3/validation-commands.md)
make these measurements reproducible. The differential reader check passed
16,040 acceptance/value/exact-hash comparisons plus the key-sharing and
GC-disabled lifetime cases. Final ruff, data-freeze and chart checks pass;
the chart check has nothing to check. Source equality with the measured
implementation and the empty private scratch directory were verified again.
The full-suite process has exited.

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
| Only the current period is measured | New period/workflow regressions fail; the old implementation exceeds 115 MiB with `--successor` | Both candidate periods have a failing 115 MiB gate; each uses its main baseline when available |
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
| Round 2 `bb41f0f6`, current | 104.48928 | 59.875 | Exit 0 at 115 MiB |
| Round 2 `bb41f0f6`, successor | 104.51080 | 59.875 | Exit 0 at 115 MiB |
| Round 2 `bb41f0f6`, warm rollover | 104.53250 | 59.875 | Exit 0 at 115 MiB |
| Round 3 `f6dbbcd8`, current | 104.48933 | 59.875 | Exit 0 at 115 MiB |
| Round 3 `f6dbbcd8`, successor | 104.51238 | 59.875 | Exit 0 at 115 MiB |
| Round 3 `f6dbbcd8`, warm rollover | 104.53329 | 59.875 | Exit 0 at 115 MiB |

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
| Round 2 implementation, current | `bb41f0f6` | `74947c3` | 109,651,736 | 104.57204 | 59.875 |
| Round 2 implementation, successor | `bb41f0f6` | `74947c3` | 109,652,504 | 104.57278 | 59.875 |
| Round 2 implementation, warm rollover | `bb41f0f6` | `74947c3` | 109,698,653 | 104.61679 | 59.875 |
| Round 3 implementation, current | `f6dbbcd8` | `74947c3` | 109,652,912 | 104.57317 | 59.875 |
| Round 3 implementation, successor | `f6dbbcd8` | `74947c3` | 109,652,968 | 104.57322 | 59.875 |
| Round 3 implementation, warm rollover | `f6dbbcd8` | `74947c3` | 108,730,708 | 103.69368 | 59.875 |

The historical four-cell runs exit successfully at the unchanged 120 MiB
deployment gate. All three initial implementation runs fail the 115 MiB gate;
all Round 2 and Round 3 implementation runs exit 0 at that same 115 MiB gate.
The successor run uses the same four requests at the current period's UTC
boundary. Warm rollover first serves the current decision, advances to the
boundary, repeats that decision request, and runs the remaining three requests.
It asserts the predecessor is released before reading the successor bytes.

Post-sample private attribution for the Round 2 implementation's current period measures
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

The public and private runs allocate the same 59.875 MiB Wasm heap.
Round 2 steady totals differ by less than 0.09 MiB in each matching scenario.
Round 3 current and successor totals also differ by less than 0.09 MiB;
the public warm result is 0.84 MiB higher than the private sample. This is
within the observed V8 variation and conservatively represents private warm
memory. The highest Round 3 private result leaves 10.43 MiB below 115 MiB.
The [Round 3 private memory-only results](MODEL-407/round3/private-memory-numbers.json)
record the latest samples.
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
blocks. It avoids a full decoded text copy alongside the parsed tree; catalogue
loading still retains the decompressed UTF-8 bytes while parsing.
The snapshot writer and format do not change. Legacy noncanonical and deeply
nested inputs preserve their existing hash/signature verification path.

New tests cover chunk boundaries, Unicode and escapes, EOF, malformed syntax,
content tampering before indexing, duplicate outer content, inner last-value
semantics, deep legacy input, and cleanup after a failed parse. Existing gzip
CRC, size, truncation and concatenated-member tests pass. The original 100 ms
load-time limit remains. Round 2 standalone best-of-five samples were 71.64–75.68 ms;
REV-820 exposed the CI failure, corrected in Round 3 above.

The policy change retains only the requested page and the first ten required
undetermined examples. Full-catalogue verdict counts and provenance still
include off-page rows. Tests cover beyond-end offsets and dates present only
on a final off-page row. Independent local review checked policy response ordering, pagination,
provenance, and parser framing/signature behavior without a blocking finding.
Those were local executor checks. REV-820 subsequently reviewed Round 2 and
identified the load-time blocker above. Cross-model review of Round 3 remains pending.

Red/green output is retained in [streaming notes](MODEL-407/streaming-notes.md),
[streaming red](MODEL-407/streaming-red.txt),
[policy retention red](MODEL-407/policy-retention-red.txt),
[policy retention green](MODEL-407/policy-retention-green.txt), and
[catalogue integration green](MODEL-407/catalogue-stream-green.txt).
The policy host-allocation diagnostic fell from 2,985,912 to 375,248 bytes on
the public catalogue. It explains the change; it is not the acceptance probe.

## Main reconciliation

Main advanced to `34c6dbef95371cff728a7a28aba33dcffe3e50e3`, reverting #813
until a lazy successor could meet the memory budget. Merge commit
`3cf60629630d225e486f0726cf5001450fb738ca` restores the tested successor
implementation and regressions, while retaining main's removal of obsolete
MODEL-402 evidence. `git diff --exit-code bb41f0f6 3cf60629 -- api decision
pipeline schema` confirms that merge's executable source is identical to the
Round 2 measured build. Round 3 changes only the reader as described above.

The public workflow also handles main versions without a successor bundle:
main's current baseline remains required; an explicit notice replaces only
the unavailable successor comparison. Both candidate 115 MiB gates remain
mandatory. Process-level workflow tests exercise both available-period cases
and both incomplete-pair failures. The detector was additionally run against
real public baseline and final bundles. The focused workflow rerun passed
10 tests with the already-tested fixture-build case deselected, exit 0.
The data-freeze guard and chart check were rerun against `34c6dbef`, both
with direct exit 0; the chart check had nothing to check.

## Integration commands and limits

The integration commands and results in this section were completed in the
earlier rounds. Round 3 commands and results are linked above; its required
full-suite rerun uses the same locked command shown below.

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

The initial complete suite finished with direct process exit code **0**:
**11,595 passed, 9 skipped, 11 warnings in 1,410.99 seconds (23 minutes 30
seconds)**. The [complete terminal output](MODEL-407/full-suite.txt) is retained.
That run preceded the private follow-up. The final focused suite passed **640 tests in 227.71 seconds**, direct exit 0,
covering snapshot loading and rollover, hardware responses, rank, policy,
workflow gates, and Worker compression. Its output is in
[focused-final.txt](MODEL-407/focused-final.txt).

The Round 2 complete suite at merge commit
`3cf60629630d225e486f0726cf5001450fb738ca` passed under the required shared
lock with direct process exit code **0**: **11,650 passed, 9 skipped,
11 warnings in 1,286.78 seconds (21 minutes 26 seconds)**. The executable
source remains identical to the measured `bb41f0f6` implementation. The
[final terminal output](MODEL-407/full-suite-final.txt) is retained. That
verification process exited before the Round 3 changes.

The executor performed no production deployment, vendor API spending, live
billing transaction, or private-workflow execution. Round 3 cross-model review
remains pending. Local tests exercise synthetic billing and signature inputs. Public
CI status and the final memory figures are not inferred from these tests.
