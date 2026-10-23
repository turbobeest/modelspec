MODEL-444 private probe evidence, October 23, 2026 UTC.

Engine baseline is `7e3d8ba6c95eac6f03e438366686c5299499b6bc`. Private data main is `ba03e11651513aa108f4031e56622717cf419acf`; original data#103 is `a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7`. Both revisions were staged locally from the existing clone. No new source fetch was performed.

Baseline command, exit 0:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/probes/validate.py --engine /tmp/model-444-scratch/probes/engine-base --data /tmp/model-444-scratch/data --label main
```

The engine baseline is a `git archive` of the recorded engine commit. Before data edits, the vendor built its own temporary overlay. The separate corpus runtime was staged from an immutable archive of private data main. No corrected candidate data reaches either baseline input.

| Baseline check | Current | Successor |
| --- | ---: | ---: |
| As-of date | 2026-10-23 | 2027-01-01 |
| Production completeness gaps | 0 | 0 |
| Corpus cases passed | 319/319 | 319/319 |
| Catalogue cases | 302 | 302 |
| Fixture cases | 17 | 17 |
| Validated HTTP-200 contracts | 286 | 286 |
| Steady memory, MiB | 108.971291 | 104.646690 |
| Peak memory, MiB | 112.532913 | 107.842430 |

Baseline snapshot IDs are `snap_9cc5b5cc2f876073` and `snap_2ad658818ace907b`. The baseline public re-vendor exited 0 and its output contains no `bundled_data.py`.

Original data#103 reproduction command, exit 0 after checking the expected child failures:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/probes/red.py
```

The actual vendor child exited 2, with `CompletenessError` reported before the outer `RuntimeError`. A separate call to `snapshot.build_from_repo` used the production premier set and left the default completeness gate enabled. It exited 1 with 113 guaranteed-fact gaps: 93 `quarantined (mismatch)`, 15 `quarantined (unreachable)` and five `unknown (no fact)`. No accepted export or corpus/memory result exists for this original state. Aggregate counts are in `red/gate.public.json` and exact commands and exit codes are in `red/commands.json`.

The validation script follows `.github/workflows/rank-api.yml`: actual `api/worker/vendor.py --data-dir ... --out <scratch bundle>`, followed by `measure_memory.cjs` under Node v22.22.3 and Pyodide 0.28.3, current and `--successor`, both with `--limit-mib 115`. It copies the tracked Worker entry files into the scratch bundle, as the workflow does. The probe exercises decide, vocabulary, rank and policy-check inside the isolated runtime. Corpus evaluation extracts the actual vendored exports and invokes `docs/evidence/g2-ios/MODEL-439/r2/compare_private.py state --reuse-exports` in a fresh process.

The only signing key is `model439-private-proof-throwaway-key`. The controlled environment sets `MODELSPEC_REQUIRE_DATA_DIR=1`, `DATA_SPLIT_ENABLED=false`, `PYTHONDONTWRITEBYTECODE=1`, the selected engine as `PYTHONPATH`, scratch `TMPDIR`, and the pinned runtime as `NODE_PATH`. `MODELSPEC_SOURCE_CACHE` and `MODELSPEC_DATA_DIR` are unset. Public re-vendoring switches `MODELSPEC_REQUIRE_DATA_DIR=0` and removes the signing key.

Tools are Python 3.14.4, Node v22.22.3, Pyodide 0.28.3, pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7. Every child exit code was checked directly. These are local measurements; no production deployment or CI run was observed. This worker made no gh calls, source-page fetches, vendor-provider calls or source-file edits.

Candidate validation completed against engine implementation commit `8d380496` and the corrected private tree at `/tmp/model-444-scratch/data`. Candidate data edits were stable for the probe. The script records the input data HEAD, uncommitted status privately, and hashes of the public decision modules. Tests and evidence files could change concurrently; they are not inputs to these exports.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/probes/validate.py --engine /Users/terbeest/dev/worktrees/model-444 --data /tmp/model-444-scratch/data --label candidate
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/probes/compare.py /tmp/model-444-scratch/probes/main /tmp/model-444-scratch/probes/candidate
```

Both commands exited 0. Every vendor, memory and corpus child also exited 0.

| Candidate check | Current | Successor |
| --- | ---: | ---: |
| As-of date | 2026-10-23 | 2027-01-01 |
| Production completeness gaps | 0 | 0 |
| Corpus cases passed | 319/319 | 319/319 |
| Catalogue outcomes changed against main | 0/302 | 0/302 |
| Fixture outcomes changed against main | 0/17 | 0/17 |
| Snapshot ID identical to main | Yes | Yes |
| Steady memory, MiB | 104.646740 | 104.646290 |
| Peak memory, MiB | 107.842503 | 105.491749 |

The comparison checks HTTP status, decision status, contract version, first result, answer kind, answer leader, answer members, tie members, answer order, tie breakers, ordered results, warnings and fact assurance. Every measured field is unchanged. There are no changed outcomes to explain. Both snapshots have the same IDs as main. Each period validates all 286 HTTP-200 decision contracts. No cited benchmark evidence record carries a non-null verification.

The candidate public re-vendor exited 0 and its output contains no `bundled_data.py`. The Worker's source directory in the engine checkout was never modified by these probes. All generated bundles stayed in this worker's scratch directory. All child processes completed and were reaped.

The `public/` directory contains aggregate evidence only. The private predictions, source data, overlays and bundles are excluded. `comparison.json` contains counts and public corpus case IDs; both changed-case maps are empty. The sanitized command records omit the private Git status. No new source assertions or live accuracy checks are implied by the comparison.
