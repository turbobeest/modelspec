# MODEL-442 round 3: accelerate catalogue YAML parsing

**Implementation ready for independent review.** The 13-test private-serving module
fell from 643.62s to 139.39s locally (4.62× faster), with unchanged output bytes.
The broader CI completion time has not been observed after this change.

Base SHA: `5ebdc45eb474c0d09d30b1136f504fe0529d19bf`.
Final implementation SHA: `79e91d01c7893160efe6e8cf8608720f4abb481c`.
The following evidence-only commit records verification; its final branch-head
SHA is reported in the executor completion line and by `git rev-parse HEAD`.
Worktree: `/Users/terbeest/dev/worktrees/model-442`; branch:
`model-442-ci-wall-time`. [PR #897](https://github.com/turbobeest/modelspec/pull/897)
remains draft; no PR operation was performed. This section supplements the earlier
rounds below; it does not replace their observations or unsuccessful predictions.

## Observed baseline

The supplied CI log identifies three private-serving tests as the bottleneck.
The unchanged local run passed all 13 tests in **643.62 seconds**. After the fix,
the same module passed all 13 in **139.39 seconds**, a **78.3% reduction**.
Test call times and the separately charged module fixture setup are:

| Phase | Supplied CI seconds | Local before seconds | Local after seconds |
| --- | ---: | ---: | ---: |
| Public leak check, full/holding/live | 1116.66 | 171.46 | 39.40 |
| Private Worker bundle | 358.33 | 106.28 | 17.63 |
| Policy and neutrality, split off/on | 1518.94 | 339.72 | 76.80 |
| Private fixture setup | 81.22 | 24.83 | 4.36 |
| Complete 13-test module | 3078.67 | 643.62 | 139.39 |

At historical checkout `36b2d184`, the same module passed all 13 tests in
**744.67 seconds**: public call 275.83, private bundle 105.37, policy calls
337.34, and fixture setup 24.84 seconds. The private and policy phases were
already comparably slow before the recent changes named in the spec. The older
public call was slower, but cache state was uncontrolled; no causal explanation
is established for that difference. These runs do not attribute the bottleneck
to a particular recent merge.

## Profiled cause

The parent cProfile file is `/tmp/model-442-scratch/ps.prof`. The private vendor
starts a separate export process, profiled in
`/tmp/model-442-scratch/executor/export-7140.prof`. The parent spends 316.980
seconds blocked in `poll` while that child runs. Counting both would duplicate
the private export cost. Correct combined accounting is:

```text
1899.018 parent seconds - 316.980 blocking seconds + 316.697 child seconds
= 1898.736 profiled seconds
```

Across both processes, `yaml.safe_load` accounts for **1780.267 seconds,
93.761%** of that total. Its direct calls from `pipeline.load.split_front_matter`
and `schema.card.ModelCard._parse_yaml_string` account for **1758.621 seconds,
92.621%**. In the private export child alone, those two readers account for
**306.213 of 316.697 seconds, 96.690%**.

The large full-catalogue builds repeatedly use PyYAML's Python scanner and
parser. The measured alternatives are much smaller: `deterministic_probabilities`
takes 0.194 seconds in the parent and 0.094 in the child; `ref_state` takes
1.132 and 0.200 seconds. These cumulative function times can overlap with
their callers and must not be summed as independent costs.

`/tmp/model-442-scratch/review/profile-summary.txt` records the leading calls
and every direct `safe_load` caller. cProfile overhead is substantial, so
the before/after speed comparison uses unprofiled pytest runs.

## Regression and change

Before changing production code, the new tests produced **2 failed, 12 passed
in 3.23 seconds**. Both failures were
`test_large_catalogue_card_uses_less_than_half_python_parser_cpu`, parameterized
for the two real readers. The front-matter reader used 0.237 seconds against
0.241 for Python `safe_load`, ratio **0.98**. The model-card reader used 0.239
against 0.235, ratio **1.02**. Both failed the required ratio below **0.50**.
The other assertions already passed, including safe tags and diagnostics.

The fix adds `schema.yaml_loader.load_yaml` and changes only those two readers
to call it. It selects PyYAML's `CSafeLoader` when available, with `SafeLoader`
as the fallback. Both loaders use `SafeConstructor` and `Resolver`. The helper
does not cache parsed mappings, so aliases and fresh mutable results keep their
existing behavior. On a YAML error it retries with the original Python safe
loader after leaving the exception handler, preserving public diagnostics
without chaining the discarded C parser exception. Private error boundaries
remain responsible for redacting values.

The tests check dates, booleans, numeric values, nulls, aliases, repeated-read
isolation, rejection of Python-specific YAML tags, and exact public diagnostic
type, message, position, and exception context. They cover missing libyaml too.
The two timing cases use process CPU time with GC paused and repeated samples.
Their `perf` marker selects the existing serial CI timing job and excludes them
from parallel shards. The new test module passed **14 tests in 1.83 seconds**.

## Output and Worker verification

Before/after private-serving artifacts use the same build commit, timestamp,
and source data. The comparison covers every file in public, holding, live,
split-off, and split-on trees, plus decoded private Worker exports and successor
metadata. All **19,672 artifacts**, including **2,618 JSON artifacts**, were
byte-identical, comparison exit 0. Counts were bundle 6, holding 80, live 225,
split-off 8,135, split-on 5,613, and public 5,613. No files were added or removed.
These exports contain no `p_best` fields, so they cannot establish probability
precision on their own. A separate before/after replay of four engine decisions
on the synthetic banded page snapshot compared **64 non-null `p_best` and
`top3_stability` fields at four decimals**, plus serialized page-fixture response hashes.
The captures were identical, `cmp` exit 0, and the stored banded fixture matched.

The focused broader selection passed **366 tests in 29.63 seconds**, exit 0.
It includes decide-page fixtures, the decision contract, reader/schema/private
diagnostics, probability and bands tests, and the Worker import audit. Fixtures
were checked without regeneration. The same run passed the existing **100 ms
snapshot-load gate** and the fresh-snapshot Worker decision latency gate.

The changed readers and helper are build-time code absent from the Worker
vendor source list. Actual private data was nevertheless vendored with a
throwaway signing key for deployment-shaped Pyodide 0.28.3 measurements.
The complete deployment bundle matched across all **163 files**, including runtime
code and private exports. Before/after measurements were:

| Measurement | Before | After |
| --- | ---: | ---: |
| Current steady memory | 104.6480 MiB | 104.6489 MiB |
| Successor steady memory | 104.6487 MiB | 104.6486 MiB |
| Current memory-probe wall time | 2.47s | 2.50s |
| Successor memory-probe wall time | 2.52s | 2.51s |
| Worker cold imports | 1564.85ms | 1532.82ms |
| First full decision | 103.06ms | 102.68ms |
| Actual private-data vendor wall time | 163.79s | 29.15s |

Both periods passed the **115 MiB** limit. Cold imports and the first decision
were slightly lower in the after sample; these are single-run timings, not a
statistical speed claim. The first full decision is a different measurement
from the existing 100 ms snapshot-load gate, which passed unchanged. Response
hashes for `none`, `summary`, and `full` explanations also matched exactly.
The public Worker bundle was restored and its embedded private data file was
confirmed absent. The private checkout, private comparison bundle, and older
comparison worktree were deleted after verification.

## Expected CI time and limits

Applying each local phase's measured after/before ratio to its corresponding
supplied CI phase projects the private-serving pytest module at
**677.21 seconds, about 11m17s**, versus 3078.67 seconds, a **78.0% reduction**.
The calculation preserves 3.52 seconds for the remaining tests and overhead.
It excludes job setup before pytest, runner queues, and unmeasured changes to
other jobs. It is a conditional projection, not an observed CI improvement.

The saved eight-shard run has no final times for social cards, ordinary shards
6-8, or the site build. Those test shards had already exceeded 23 minutes in
the prior observation. The historical ordinary-shard replay, 1157.724,
928.438, 959.006, and 941.499 seconds before setup, did not establish the earlier
20-minute target. No private-test ratio is applied to those other jobs.
The overall new CI wall time therefore remains **unobserved**; this run measures
and projects the removal of the known private-serving bottleneck.

## Commands and environment

Environment: macOS arm64, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3
with libyaml available, pydantic 2.13.5, Ruff 0.16.6, Node 22.22.3.
The pinned probe used Pyodide 0.28.3 / Python 3.13.2, with its packaged
pydantic 2.10.6 and PyYAML 6.0.2. Local pytest used Python 3.14.4;
pytest CI uses Python 3.11. Worker build and probe runtimes are separate.
No GitHub CLI/API requests or vendor-model API calls were made in this round.
The full local suite was not run; all pytest commands below were serial.

The commands below use these path abbreviations; their expanded arguments are
the commands recorded in the session. Logs are under `$S/executor/` unless
otherwise specified. Exit codes were checked directly, without a pipe.

```bash
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
NODE=/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node
S=/tmp/model-442-scratch
I=$S/executor/instrumentation
```

Baseline and historical comparison (both exit 0):

```bash
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider \
  tests/test_private_serving.py --durations=0 > "$S/executor/private-before.log" 2>&1
git worktree add --detach "$S/older-main" 36b2d184
# The following command ran with cwd=$S/older-main.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider \
  tests/test_private_serving.py --durations=0 > "$S/executor/private-older.log" 2>&1
# All remaining commands ran in the ticket worktree.
```

The scratch `sitecustomize.py` replaces `pipeline.export.make_build` with a
`Build` using commit `5ebdc45eb474c0d09d30b1136f504fe0529d19bf`, built_at
`2026-10-23T07:00:00+00:00`, and the unchanged catalogue `as_of`. With
`MODEL442_PROFILE_CHILD=1`, it profiles only processes whose argv contains
`--export-data` and registers an `atexit` profile dump named `export-<pid>.prof`.
These are verification-only changes outside the repository.

```bash
env PYTHONPATH=$I:$PWD MODEL442_FIXED_BUILD=1 MODEL442_PROFILE_CHILD=1 \
  MODEL442_PROFILE_PARENT=1 "$PY" -m cProfile -o "$S/ps.prof" -m pytest \
  -q -p no:cacheprovider -p timing_plugin tests/test_private_serving.py \
  --durations=0 --basetemp="$S/executor/profile-before" \
  > "$S/executor/private-profile.log" 2>&1
"$PY" -c 'import pstats; pstats.Stats("/tmp/model-442-scratch/ps.prof").strip_dirs().sort_stats("cumulative").print_stats(35)'
```

The complete profile run passed 13 tests in 1900.06s, exit 0. An earlier
profiling attempt was interrupted before completing a test and is excluded
from all successful-run claims. The optional checkpoint plugin could not
retrieve cProfile through `sys.getprofile()` on Python 3.14; it made no
checkpoints. The completed parent and child profile files supplied the totals.

Red and green (same command, production code changed between runs):

```bash
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_yaml_loading.py
# yaml-red-final.log: exit 1, 2 failed / 12 passed in 3.23s.
# yaml-green.log: exit 0, 14 passed in 1.83s.
env PYTHONPATH=$I:$PWD MODEL442_FIXED_BUILD=1 "$PY" -m pytest -q \
  -p no:cacheprovider tests/test_private_serving.py --durations=0 \
  --basetemp="$S/executor/private-after" > "$S/executor/private-after.log" 2>&1
# Exit 0, 13 passed in 139.39s.
env -u MODELSPEC_WRITE_FIXTURES PYTHONPATH=$PWD "$PY" -m pytest -q \
  -p no:cacheprovider tests/test_pipeline.py tests/test_schema.py \
  tests/test_card_yaml_roundtrip.py tests/test_private_data_errors.py \
  tests/test_decide_page_fixtures.py tests/test_decision_contract.py \
  tests/test_decision_latency.py tests/test_decision_bands.py \
  tests/test_decision_snapshot.py::test_a_thirty_model_snapshot_is_small_and_loads_fast \
  tests/test_decide_worker.py::test_fresh_snapshot_load_and_first_domain_decision_stay_under_budget \
  tests/test_worker_vendor_imports.py --durations=10 \
  > "$S/executor/focused-green.log" 2>&1
# Exit 0, 366 passed in 29.63s.
```

The scratch artifact comparer inventories all files in each completed test
scenario, including decoded `BLOBS` and canonical `SNAPSHOTS` metadata. It
compares path sets, byte lengths and SHA256 hashes, and inventories probability
fields in JSON. The probability script calls the existing page test service
on `_banded_snapshot()` with the stored banded objective, coding-only,
coding-heavy and cost-heavy objectives. It records each complete page-response
hash and every non-null `p_best`/`top3_stability` at four decimals. It also
checks the stored banded fixture bytes directly.

```bash
"$PY" "$S/review/compare_artifacts.py" record \
  --basetemp "$S/executor/profile-before" --manifest "$S/review/artifacts-before.json"
"$PY" "$S/review/compare_artifacts.py" compare \
  --basetemp "$S/executor/private-after" --manifest "$S/review/artifacts-before.json"
env PYTHONPATH=$PWD "$PY" "$S/profile-context/capture_probabilities.py" \
  "$S/profile-context/probabilities-before.json"
env PYTHONPATH=$PWD "$PY" "$S/profile-context/capture_probabilities.py" \
  "$S/profile-context/probabilities-after.json"
cmp "$S/profile-context/probabilities-before.json" "$S/profile-context/probabilities-after.json"
"$PY" "$S/review/project_ci.py" --public 39.40 --private 17.63 --policy 76.80 --setup 4.36
# All exit 0. The baseline record/capture preceded the production edit.
```

Actual private-data probes used private data commit
`c26a2d7b67039dd0ed2490cd740766680c9e454d`. Only synthetic signing material was
supplied; the Ed25519 signing environment was explicitly removed. The baseline
custom output directory received the 32 tracked, hand-written top-level Worker
Python files, using `git ls-files api/worker/src` and `shutil.copyfile`. This
matches the deploy's complete runtime source tree without replacing exports.

```bash
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git "$S/executor/private-data"
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
  npm install --prefix "$S/executor/memory" --no-save pyodide@0.28.3
env -u MODELSPEC_SNAPSHOT_ED25519_KEY PYTHONPATH=$I:$PWD MODEL442_FIXED_BUILD=1 \
  MODELSPEC_SNAPSHOT_KEY=model442-memory-fixture-key /usr/bin/time -p "$PY" \
  api/worker/vendor.py --data-dir "$S/executor/private-data" \
  --out "$S/executor/private-before-bundle"
env -u MODELSPEC_SNAPSHOT_ED25519_KEY PYTHONPATH=$I:$PWD MODEL442_FIXED_BUILD=1 \
  MODELSPEC_SNAPSHOT_KEY=model442-memory-fixture-key /usr/bin/time -p "$PY" \
  api/worker/vendor.py --data-dir "$S/executor/private-data"
"$PY" "$S/executor/compare_private_bundle.py"
# All exit 0; bundle comparison: all 163 file paths and SHA256 hashes equal.
```

For each row below the command was `/usr/bin/time -p` around the indicated
Node invocation, with `NODE_PATH=$S/executor/memory/node_modules` and
`MODELSPEC_SNAPSHOT_KEY=model442-memory-fixture-key`. Memory commands included
`node --expose-gc api/worker/measure_memory.cjs`, and every one exited 0.

| Bundle | Additional arguments | Log |
| --- | --- | --- |
| `$S/executor/private-before-bundle` | `--limit-mib 115 --output $S/executor/memory-before.json` | `memory-before.log` |
| `$S/executor/private-before-bundle` | `--successor --limit-mib 115 --output $S/executor/memory-before-successor.json` | `memory-before-successor.log` |
| `api/worker/src` | `--limit-mib 115 --baseline $S/executor/memory-before.json --output $S/executor/memory-after.json` | `memory-after.log` |
| `api/worker/src` | `--successor --limit-mib 115 --baseline $S/executor/memory-before-successor.json --output $S/executor/memory-after-successor.json` | `memory-after-successor.log` |

Cold/warm timing commands used the same environment plus `PROFILE_RUNS=20`:

```bash
/usr/bin/time -p "$NODE" api/worker/profile_decide.cjs \
  "$S/executor/private-before-bundle" "$S/executor/private-timing-before.json"
/usr/bin/time -p "$NODE" api/worker/profile_decide.cjs \
  api/worker/src "$S/executor/private-timing-after.json"
# Both exit 0. SHA256 hashes match at all three explanation levels.
env -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY PYTHONPATH=$PWD \
  "$PY" api/worker/vendor.py
# Exit 0; restored public bundle, with no bundled_data.py remaining.
```

After the comparisons, `shutil.rmtree` deleted exactly
`$S/executor/private-data` and `$S/executor/private-before-bundle`; absence was
asserted. `git worktree remove $S/older-main` exited 0. Private data and bundles
were never staged. Only non-content measurement logs remain from those probes.

Final guards and delivery are recorded below.

```bash
env PYTHONPATH=$PWD \
  MODELSPEC_DIST=$S/executor/private-after/test_policy_bytes_and_neutrali0/off \
  "$PY" -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# Exit 0, 47 passed in 66.25s, including the built-artifact scan.
"$PY" -m ruff check schema/yaml_loader.py tests/test_yaml_loading.py
# Exit 0. Two new-test formatting findings were corrected before this pass.
git diff --cached --check
# Exit 0 before the implementation commit.
git commit -m 'MODEL-442: accelerate safe catalogue YAML parsing' \
  -m 'Use libyaml in the two profiled catalogue readers while preserving Python parser diagnostics, safe construction, and fresh parsed values. Add behavior and CPU regression coverage.' \
  -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
# Exit 0, implementation SHA recorded above.
```

The green implementation checks total **440 passing tests**, with no skips.
The evidence-only change is checked again by the tracked-file source guard and
`git diff --cached --check`. Delivery uses these commands, with the final head
and push outcome reported in the executor completion:

```bash
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider \
  tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
git diff --cached --check
git commit -m 'MODEL-442: record profiling and validation evidence' \
  -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
"$PY" scripts/data_freeze_guard.py --base 5ebdc45eb474c0d09d30b1136f504fe0529d19bf \
  --head HEAD --branch model-442-ci-wall-time
CI_LOCAL_SKIP=1 git push -u origin model-442-ci-wall-time
git rev-parse HEAD
git status --short
```

No post-push CI result, production deployment, or new overall CI wall time was
observed. The implementation preserves the existing private-serving assertions,
ranking logic, stored fixtures, frozen data, published contracts, and switches.

---

# MODEL-442 round 2

**BLOCKED: the approximately 20-minute CI target is still unmet.** The two
review fixes are complete and all 221 focused local tests pass. The last
permitted GitHub snapshot showed five shards still running after more than
23 minutes. Further CI timing/log retrieval would exceed the six-call cap.
The scheduling predictions below did not establish the required outcome.

Base: `52c3147d19d39876aa5900497d39030601260678`.
Final implementation: `0d82d53229e08a043ff276d2a8028d9dd81bc51a`.
The following evidence-only commit records verification. Its branch-head SHA
is reported in the executor completion line and by `git rev-parse HEAD`.
Worktree `/Users/terbeest/dev/worktrees/model-442`, branch
`model-442-ci-wall-time`. [PR #897](https://github.com/turbobeest/modelspec/pull/897)
was verified draft. Its existing executor footer already names GPT-6 Astra.

## Measured before

The round-1 implementation's [run 39887101830](https://github.com/turbobeest/modelspec/actions/runs/39887101830)
finished successfully in **59m36s**, from workflow creation at 01:59:43 UTC
to `Run pytest` completing at 02:59:19 UTC on 2026-10-23. All four downloaded
JUnit artifacts measured 339 of 342 discovered files. Unmeasured files still
receive estimated weights and remain assigned.
The creation time was observed in the first `gh run list` invocation recorded
below; the saved PR check response supplies the completion time.

| Shard | Job wall | Pytest JUnit elapsed | Before pytest starts |
| --- | ---: | ---: | ---: |
| 1/4 | 34m37s | 1801.914s | 267.953s |
| 2/4 | 59m19s | 3419.541s | 132.930s |
| 3/4 | 27m46s | 1094.477s | 561.352s |
| 4/4 | 32m02s | 1849.699s | 64.792s |

Job timestamps come from the PR checks. JUnit supplies suite timestamps and
elapsed time. The last column combines setup and collection; it does not
separate npm, pip, browser installation or imports. The separate perf and
collection job took 9m52s.

| Module | Summed testcase time | Largest testcase, including fixture setup |
| --- | ---: | --- |
| Private serving | 2484.917s | Policy comparison across two builds, 1119.891s |
| Social cards | 1659.460s | Build without the render flag, 679.094s |
| Agent readiness | 1399.913s | Full-site fixture charged to the robots test, 1327.628s |
| Blog | 956.790s | Public-root blog build, 956.273s |
| Holding | 898.141s | Full-site fixture and guide decision, 719.358s |
| Coverage | 886.937s | Snapshot/catalogue counts, 315.040s |
| Landing | 655.735s | Snapshot-derived figures, 181.271s |

Social cards' three full builds total 1297.520s. Private serving also includes
a 1005.177s public-leak build and a 357.775s private-bundle build. These remain
real full-corpus builds with their existing assertions.

The pinned xdist 3.8.0 loadfile scheduler orders modules by testcase count
unless `--no-loadscope-reorder` is passed. That delays costly modules with few
tests. Coverage and landing initialization also use filesystem locks, so
testcase times can include waiting for another worker. JUnit cannot separate
that waiting from computation.

## Changes and predictions

Eight shards replace four. Private serving, social cards, agent readiness and
landing each run serially on a dedicated runner. Four ordinary shards retain
`-n auto --dist loadfile`, preserving measured longest-first file order with
`--no-loadscope-reorder`. Module fixtures and within-file order stay intact.
Unknown, duplicate or overallocated isolation requests fail explicitly.

Six shards were considered. Two isolated files leave the measured 23.3-minute
agent-readiness module in an ordinary shard. Three isolated files plus four
ordinary shards still leave landing's app build on an ordinary shard. The
landing job previously spent 9.4 minutes before pytest. Isolating all four
costly paths preserves four ordinary shards and avoids that combination.

Only landing now runs `npm run build`. Social cards still install Node
dependencies and Chromium but render their own HTML; they do not use
`web/dist`. Python browser installation still follows the interaction module.
Cache keys and permissions are unchanged. All shards have an **80-minute**
timeout and log their 25 slowest phases. `Run pytest` and the exact comparison
of full and sharded collection remain unchanged.

The eight shards contain 1, 1, 1, 1, 85, 85, 85 and 83 files. The ordinary
shards total about 3704.785 summed testcase seconds each. Dividing that by
four is only a lower bound, not a wall-time prediction.

A replay of the pinned scheduler, including whole-file prefetch when at most
two testcases remain, predicts ordinary shard times of **1157.724s, 928.438s,
959.006s and 941.499s** before setup. With 64.8s setup, the slowest is about
20m23s. These are estimates, not observed CI improvements. The replay reuses
old testcase times, including old contention and cache waits; it excludes
setup, collection and scheduler overhead. Unmeasured files use the existing
size estimate. Isolated serial durations require separate observation.

Replay inputs, script and results remain on the operator machine. Reproduce:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-442-scratch/timing_diagnosis/replay_xdist.py --root /Users/terbeest/dev/worktrees/model-442 --junit /tmp/model-442-scratch/root-r2/junit --ordinary-shards 4 --isolate tests/test_private_serving.py --isolate tests/test_social_cards.py --isolate tests/test_agent_ready.py --isolate tests/test_landing.py
```

## Red and green

| Regression | Before implementation | After implementation |
| --- | --- | --- |
| `test_template_card_failures_name_every_broken_template` | Missing `outside-frame` in the geometry assertion; 1 failed in 0.26s, exit 1 | 1 passed in 0.37s, exit 0 |
| `test_pytest_shards_have_a_bounded_job_timeout` | `assert 100 == 80` | Passes at 80 |
| `test_shard_files_start_with_the_longest_measured_module` | Alphabetical instead of measured-duration order | Passes |
| `test_expensive_modules_get_dedicated_shards_without_losing_other_files` | No isolation argument | Passes, including reversed input order |
| `test_invalid_isolated_shards_fail_instead_of_dropping_tests` | No isolation argument | All three invalid configurations fail explicitly |
| `test_workflow_shard_selection_covers_the_suite_once` | Four mixed shards instead of dedicated modules | Executes all eight selection commands and proves exact coverage |
| Browser selection, app-build and matrix checks | No app output, app built for every Node shard, four-job matrix | All cases pass |

The workflow suite went from **15 failed, 52 passed in 2.69s**, exit 1, to
**67 passed in 1.42s**, exit 0. Existing failure-masking and required-check
tests remain active. The template regression injects a layout failure, wrong
PNG dimensions, an invalid PNG signature and a clean card. It requires every
broken template's ID and display name in the message. The real batch retains
all layout, report-count, PNG and one-renderer checks. The focused browser and
naming tests passed in 56.68s; the real browser batch itself took 56.37s.

## Local after measurements

Serial private serving passed **13 tests in 648.33s**, exit 0. Its policy
comparison took 344.37s; the public-leak call took 168.28s plus 24.97s setup;
the private bundle took 109.45s. This supports isolation but compares macOS
with local caches against Linux CI, not a controlled before/after experiment.
The app build also passed. The broader serial suite passed **161 tests in
1003.17s**, exit 0, with no skips. Local JUnit module totals were 615.373s for
social cards, 185.755s for agent readiness, 200.250s for landing and 1.305s for
workflow checks. The three social builds took 168.76s, 166.52s and 164.19s;
the real Chromium batch took 56.03s. Agent readiness's full-build fixture
took 166.75s. These are observed local after values, not Linux CI results.
The excluded-source suite then passed **47 tests in 132.38s**, exit 0, using
the just-built site through `MODELSPEC_DIST`. Its optional artifact check ran
and passed in 16.28s. Across these three focused invocations, all 221 tests
passed with no skips. The final CI snapshot is recorded below.

## Observed CI after

The sixth and final GitHub call observed implementation
`0d82d53229e08a043ff276d2a8028d9dd81bc51a` in
[run 39894184868](https://github.com/turbobeest/modelspec/actions/runs/39894184868).
The response was saved at 2026-10-23 03:40:22 UTC. PR #897 was still draft.
This was one status snapshot, not a polling loop.

| Shard | Assignment | Observed result | Completed job wall |
| --- | --- | --- | ---: |
| 1/8 | Private serving, serial | Still running after 23 minutes | Unknown |
| 2/8 | Social cards, serial | Still running after 23 minutes | Unknown |
| 3/8 | Agent readiness, serial | Success | 11m23s |
| 4/8 | Landing, serial | Success | 14m54s |
| 5/8 | Ordinary files, parallel | Success | 17m36s |
| 6/8 | Ordinary files, parallel | Still running after 23 minutes | Unknown |
| 7/8 | Ordinary files, parallel | Still running after 23 minutes | Unknown |
| 8/8 | Ordinary files, parallel | Still running after 23 minutes | Unknown |

Perf and collection passed in 10m31s; package smoke passed in 26s. The required
aggregate had not completed. These observations disprove an under-20-minute
full run at this implementation. They do not identify the remaining tests'
individual durations. The completed agent-readiness and landing jobs are
under target, but the overall performance work remains open. No further
unmeasured scheduling changes were made after this result. The evidence-only
push creates a fresh CI run at the final branch head; its outcome is unobserved.

## Commands

Commands ran in the assigned worktree unless stated otherwise. Logs and
artifacts are in `/tmp/model-442-scratch/root-r2/`; the naming worker used
`/tmp/model-442-scratch/layout_names/` for scratch work.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py::test_template_card_failures_name_every_broken_template
# Red exit 1; green exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_private_serving.py --durations=15
# 13 passed; exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py
# Red 15 failed, 52 passed, exit 1; green 67 passed, exit 0.
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/refresh_shard_durations.py /tmp/model-442-scratch/root-r2/junit
# 339 measurements from four XML files; exit 0.
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 8 --isolate tests/test_private_serving.py --isolate tests/test_social_cards.py --isolate tests/test_agent_ready.py --isolate tests/test_landing.py --summary
# All 342 discovered files assigned; exit 0.
env CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout tests/test_social_cards.py::test_template_card_failures_name_every_broken_template --durations=5
# 2 passed in 56.68s; exit 0.
actionlint -shellcheck= .github/workflows/test.yml
git diff --check
# Each checked directly; exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 52c3147d19d39876aa5900497d39030601260678 --head HEAD --branch model-442-ci-wall-time
# data freeze: ok; exit 0.

# In web/:
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-442 npm run build
# Exit 0.

# Back in the worktree:
env CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_social_cards.py tests/test_agent_ready.py tests/test_landing.py --durations=20 --junitxml=/tmp/model-442-scratch/root-r2/focused.xml --basetemp=/tmp/model-442-scratch/root-r2/focused-tmp
# 161 passed in 1003.17s; exit 0.
env CI=1 MODELSPEC_DIST=/tmp/model-442-scratch/root-r2/focused-tmp/test_build_emits_every_templat0/dist PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py --durations=10
# 47 passed in 132.38s; exit 0, including the built-artifact scan.
CI_LOCAL_SKIP=1 git push -u origin model-442-ci-wall-time
```

GitHub calls, in invocation order:

```sh
gh run list -R turbobeest/modelspec --branch model-442-ci-wall-time --workflow test.yml --limit 3 --json databaseId,headSha,status,conclusion,createdAt,url
gh run view 39887101830 -R turbobeest/modelspec --json jobs,status,conclusion,headSha
gh run download 39887101830 -R turbobeest/modelspec -p 'pytest-shard-*-junit' -D /tmp/model-442-scratch/root/junit
# Exit 1: the round-1 directory already contained the artifact files.
gh run download 39887101830 -R turbobeest/modelspec -p 'pytest-shard-*-junit' -D /tmp/model-442-scratch/root-r2/junit
# Exit 0: all four artifacts downloaded into a fresh directory.
gh pr view 897 -R turbobeest/modelspec --json number,isDraft,headRefName,baseRefName,url,body,statusCheckRollup > /tmp/model-442-scratch/root-r2/pr-before.json
gh pr view 897 -R turbobeest/modelspec --json number,isDraft,headRefOid,url,statusCheckRollup > /tmp/model-442-scratch/root-r2/pr-after.json
```

Other listed GitHub calls exited 0. No polling loop was used. Tool versions
remain Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, PyYAML 6.0.3, Node
v22.22.3, npm 10.9.8, Playwright 1.63.0, actionlint 1.7.12, Git 2.50.1 and
GitHub CLI 2.102.0. The CLI version was read from its executable path without
another invocation. CI retains Python 3.11 and the existing dependency pins.

## Limits

The full local suite was not run, as instructed. No test was removed, skipped
or marked xfail by the changes. No production code, frozen data, Worker export,
ranking floor, legal text, production switch or Linear issue changed. Private
serving uses its existing synthetic overlay of the public image. No private
repository was cloned and no vendor API was called. Exact CPU contention,
lock-wait time and cache-hit savings were not measured. The observed Linux run
exceeded the approximately 20-minute target. Its final duration and the final
evidence-commit CI result were not observed within the six-call budget.

# Round 1 record at 52c3147d

Base SHA: `7e3d8ba6c95eac6f03e438366686c5299499b6bc`.
Final implementation SHA: `d085cd8638188cebb45de72e5d90847cd949399d`.
The following commit records this evidence only. Its final branch-head SHA is
reported in the executor completion line and can be resolved with `git rev-parse HEAD`.
Worktree: `/Users/terbeest/dev/worktrees/model-442`.
Branch: `model-442-ci-wall-time`.

The base's successful Test suite run [39729025428](https://github.com/turbobeest/modelspec/actions/runs/39729025428)
took 66m 37s. Shard 1 spent 63m 37s executing pytest and 39s installing
Node dependencies, building the app and installing Chromium. The interaction
module took 69.161s of summed JUnit testcase time. Browser installation was
not the dominant cost.

The committed timing file covered 121 of 342 discovered modules. Refreshing
it from all four base-run JUnit artifacts gives 339 measured modules. The
existing deterministic file allocator now spreads approximately 5,886 seconds
of measured/estimated work to each shard. No allocator or discovery rules changed.

| Shard | Base job wall time | Base pytest step | Base summed testcase time | New predicted summed time |
| --- | ---: | ---: | ---: | ---: |
| 1/4 | 66m 21s | 63m 37s | 10,574.769s | 5,885.977s |
| 2/4 | 16m 24s | 15m 48s | 2,960.952s | 5,885.976s |
| 3/4 | 33m 05s | 32m 26s | 6,292.768s | 5,885.976s |
| 4/4 | 20m 38s | 19m 29s | 3,678.304s | 5,885.976s |

The last column is an allocator prediction, not an observed CI wall time.
Each job uses four xdist workers and keeps a module together. Large modules
therefore still bound its wall time. This PR's own CI after measurement is
**pending**. No after-CI speedup is claimed.

| Other base job | Wall time | Significant steps |
| --- | ---: | --- |
| pytest perf and collection | 8m 39s | Serial timing tests 6m 56s; collection 1m 16s |
| Package smoke test | 20s | Install/run built wheel 8s |
| Run pytest | 10s | Required result gate and full/shard collection comparison |

| Base shard setup step | 1/4 | 2/4 | 3/4 | 4/4 |
| --- | ---: | ---: | ---: | ---: |
| Checkout | 7s | 7s | 6s | 6s |
| Python setup | 2s | 1s | 2s | 2s |
| Pip install | 14s | 12s | 11s | 8s |
| File selection and collection | 94s | 10s | 13s | 9s |
| Node setup | 0s | 1s | 0s | 0s |
| Python Playwright and Chromium | 0s | 0s | 0s | 23s |
| Node packages, build and Chromium | 39s | 0s | 0s | 16s |

The largest modules were social cards at 2,844.964s, private serving at
2,384.930s, holding at 1,819.775s and agent readiness at 1,354.976s. Within
social cards, three real full-site builds consumed 2,284.039s. Those integration
tests and their full public corpus remain intact. The frozen-template layout
test was 210.836s in CI and launched a separate browser for each of 40 cards.
It now sends all cards through one renderer manifest, retains every layout
assertion and adds nonempty-input, report-count and PNG-dimension checks.

Local red/green measurements of that test were 70.48s and 57.38s respectively,
an 18.6% reduction in testcase wall time. The process count fell from 40 to 1.
These are single serial runs on macOS, not Linux CI measurements. The unchanged
snapshot/template calculation still accounts for much of this test's time.

The workflow caches npm using `web/package-lock.json`. Its browser cache key
contains the OS, architecture, Python Playwright pin, actual Node Playwright
lockfile version and the runtimes selected for the shard. Runtime selection
prevents an immutable cache populated by one runtime from remaining incomplete
if the two versions later differ. Each selected installer still uses
`--with-deps`, so a restored browser cache does not omit system libraries.
Pip caching was already present and remains enabled. Browser selection follows
the allocated filenames after every timing refresh. The matrix job has a
100-minute timeout, approximately twice the largest measured module's 47.4
minutes plus setup. The required check names and gates remain unchanged.

The history sample contains the latest ten successful/failed runs on each side
of 2026-10-21 00:00 UTC from one 100-run response. Cancelled runs are excluded
because their duration does not measure completion. Among successful runs,
the pre-cutoff median was 55.17 minutes, p90 65.82 minutes, n=9. The post-cutoff
median was 54.64 minutes, p90 78.02 minutes, n=8. P90 uses the nearest rank.
These data do not establish an onset on October 21 or attribute the slowdown
to the Playwright installation change.

| Run | Created UTC | Conclusion | Wall minutes |
| --- | --- | --- | ---: |
| 39420792556 | 2026-10-20 12:14:46 | success | 61.77 |
| 39416342541 | 2026-10-20 11:38:04 | success | 49.32 |
| 39416274536 | 2026-10-20 11:37:29 | success | 61.65 |
| 39414078198 | 2026-10-20 11:19:02 | success | 54.25 |
| 39412629912 | 2026-10-20 11:06:41 | failure | 50.67 |
| 39411794726 | 2026-10-20 10:59:36 | success | 55.93 |
| 39409516910 | 2026-10-20 10:39:50 | success | 55.17 |
| 39408928965 | 2026-10-20 10:34:45 | success | 53.57 |
| 39408058080 | 2026-10-20 10:27:23 | success | 65.82 |
| 39407237824 | 2026-10-20 10:20:26 | success | 54.53 |
| 39824706573 | 2026-10-22 17:40:06 | success | 56.57 |
| 39804070856 | 2026-10-22 15:21:31 | failure | 0.52 |
| 39729025428 | 2026-10-22 05:36:50 | success | 66.62 |
| 39721626348 | 2026-10-22 04:18:18 | success | 78.02 |
| 39713246358 | 2026-10-22 02:46:48 | failure | 57.85 |
| 39709406587 | 2026-10-22 02:05:11 | success | 51.43 |
| 39704556149 | 2026-10-22 01:14:46 | success | 38.12 |
| 39703972594 | 2026-10-22 01:08:49 | success | 56.08 |
| 39683361343 | 2026-10-21 22:01:18 | success | 53.20 |
| 39681678651 | 2026-10-21 21:48:07 | success | 49.72 |

The attempt to collect all 20 runs' job and step details failed twice with
GitHub HTTP 502, exit 1. The second request reduced connection sizes. Within
the six-call limit, the fallback retrieved the base run's complete job/step
breakdown and all four timing artifacts. The 20-run per-job/per-step comparison
was therefore **not observed**. There were no polling loops. The sixth CLI call
creates the draft PR; there is no remaining call for its CI status.
Raw responses and local test logs are in
`/tmp/model-442-scratch/root/` on the executor machine.

The GitHub calls, in order, were:

```sh
gh api 'repos/turbobeest/modelspec/actions/workflows/test.yml/runs?per_page=100&created=2026-10-18..2026-10-23' > /tmp/model-442-scratch/root/runs.json
gh api graphql --input /tmp/model-442-scratch/root/measurement-query.json > /tmp/model-442-scratch/root/jobs-and-steps.json
gh api graphql --input /tmp/model-442-scratch/root/measurement-query.json > /tmp/model-442-scratch/root/jobs-and-steps.json
gh run download 39729025428 -R turbobeest/modelspec -p 'pytest-shard-*-junit' -D /tmp/model-442-scratch/root/junit
gh api 'repos/turbobeest/modelspec/actions/runs/39729025428/jobs?per_page=100' > /tmp/model-442-scratch/root/base-jobs.json
```

The request file was generated with this Python code. The first request used
`first:30` for check runs and `first:40` for steps. The second used 8 and 25.

```python
import json
from pathlib import Path
p = Path('/tmp/model-442-scratch/root')
runs = json.loads((p / 'runs.json').read_text())['workflow_runs']
selected = []
for before in (True, False):
    selected += [r for r in runs
                 if (r['created_at'] < '2026-10-21') == before
                 and r['conclusion'] in ('success', 'failure')][:10]
query = 'query($ids:[ID!]!){nodes(ids:$ids){... on WorkflowRun{id url createdAt checkSuite{checkRuns(first:30){totalCount nodes{name detailsUrl startedAt completedAt conclusion steps(first:40){totalCount nodes{name number startedAt completedAt secondsToCompletion conclusion}}}}}}} rateLimit{cost remaining}}'
(p / 'measurement-query.json').write_text(json.dumps({
    'query': query, 'variables': {'ids': [r['node_id'] for r in selected]}
}) + '\n')
```

The REST response was inspected with:

```sh
jq -r '.jobs[] | .name as $job | ([$job,"JOB",.started_at,.completed_at] | @tsv), (.steps[] | [$job,.name,.started_at,.completed_at] | @tsv)' /tmp/model-442-scratch/root/base-jobs.json
```

Elapsed seconds are `completed_at - started_at` for jobs/steps. Run history uses
`updated_at - run_started_at`. Testcase durations come from each JUnit `time`
attribute. The existing refresh script sums those values by module.

Red-first results, before the corresponding fixes:

| Test | Red output | Green output |
| --- | --- | --- |
| `test_shard_timings_cover_the_current_suite_and_browser_modules` | `AssertionError: only 121/342 test modules have measured timings` | Passed with 339/342 measured |
| `test_pytest_shards_have_a_bounded_job_timeout` | `isinstance(None, int)` failed | Passed with 100-minute matrix timeout |
| `test_browser_dependencies_follow_the_selected_shard_files` | All five cases failed because no selection output existed | All five real shell executions passed |
| `test_every_frozen_template_card_has_clean_chromium_layout` | `assert 40 == 1`; 1 failed in 70.87s, exit 1 | 1 passed in 57.59s, exit 0 |

The five browser selector cases cover no browser, Python only, landing, social
cards, and both runtimes. They execute the workflow shell against temporary
shard-file lists and the real lockfile. The layout test wraps the real process
boundary to count launches; it does not stub browser output.

Commands were run from the worktree unless a different directory is stated:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k 'shard_timings_cover or bounded_job_timeout or browser_dependencies_follow'
# Red: 7 failed, 53 deselected in 0.48s; exit 1.

/Users/terbeest/dev/modelspec/.venv/bin/python scripts/refresh_shard_durations.py /tmp/model-442-scratch/root/junit
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
# 339 measurements; all four predicted totals 5885.978s.

env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py
# Green: 60 passed in 0.85s; exit 0.

# In web/:
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH ./node_modules/.bin/playwright install chromium

# Back in the worktree root:
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout --durations=5
# Red result above.
env CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout --durations=5
# Green result above.

actionlint -shellcheck= .github/workflows/test.yml
git diff --check
# Both exit 0.

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 7e3d8ba6c95eac6f03e438366686c5299499b6bc --head HEAD --branch model-442-ci-wall-time
# data freeze: ok; exit 0.
```

Broader focused verification ran serially and completed with exit 0:

```sh
env CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_social_cards.py tests/test_removed_sources.py --durations=10
# 133 passed, 1 skipped in 863.56s. The existing optional artifact scan
# requires MODELSPEC_DIST. Run it separately against the just-built site:
env CI=1 MODELSPEC_DIST=/private/var/folders/r6/p2knzk9x65d45dhc3x6zlyqc0000gn/T/pytest-of-terbeest/pytest-220/test_build_emits_every_templat0/dist PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_a_built_dist_carries_no_removed_value
# 1 passed in 16.30s; exit 0. No focused test remains unexecuted.
```

The artifact's two site trees and 40 template PNGs were verified to exist
before reporting the scan result. The broader run's layout test took 56.53s.
Its three unchanged full-site build tests all passed. All 342 discovered
files remain assigned exactly once across four shards. A separate read-only
review checked the final changes and reproduced the report's history and
base-run timing calculations from the saved responses.

Publication commands, with the sixth and final `gh` invocation run in `/tmp`:

```sh
CI_LOCAL_SKIP=1 git push -u origin model-442-ci-wall-time
# In /tmp:
gh pr create -R turbobeest/modelspec --draft --base main --head model-442-ci-wall-time --title 'MODEL-442: rebalance CI shards and cache Chromium' --body-file /tmp/model-442-scratch/root/pr-body.md
```

Tool versions: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, PyYAML 6.0.3,
Node v22.22.3, npm 10.9.8, Playwright 1.63.0, actionlint 1.7.12, jq 1.7.1-apple,
Git 2.50.1 and GitHub CLI 2.102.0. The CLI version was read from its resolved
Homebrew executable path without using another `gh` call. CI retains Python
3.11 and its existing dependency pins.

The full local suite was not run, as required by the ticket. No tests were
skipped, removed or marked xfail by this change. No production source, public
data image, ranking rule, Worker export, production switch, required-check
name or Linear issue was changed. Cache-hit wall-time savings, Linux runner
after timings and a causal date for the original slowdown remain unobserved.
