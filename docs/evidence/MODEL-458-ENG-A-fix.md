# MODEL-458-ENG-A execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Branch: `model-458-eng-a`.
Final commit and PR are recorded in the executor's final report.

Environment: Python 3.14.4, pytest 9.1.1, Node v22.22.3, git 2.50.1.
Commands run from the assigned worktree. Tests are serial and use no cache provider.

## AUD-01-F1

Snapshot admission checks inline verification target kind and ID. Authored model,
offering and subscription facts must name their enclosing owner before lab
jurisdiction inheritance. Valid targeted log records remain eligible.

The supplied synthetic reproduction returned exit 1 with eight failed cases.
The permanent regression adds subscription ownership and log fallback through
both loaders. Before the fix this command returned exit 1, `16 failed`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_snapshot_provenance.py --tb=short
```

Red test groups and output:

- `test_snapshot_rejects_inline_verification_for_another_target`: `known` differed from `unknown`.
- `test_snapshot_rejects_evidence_inline_verification_for_another_target`: expected no admitted evidence.
- `test_snapshot_rejects_verified_fact_owned_by_another_subject`: `DID NOT RAISE SnapshotBuildError`.
- `test_repository_build_rejects_misattributed_authored_fact`: expected unknown or an owner error.
- `test_matching_log_can_admit_record_with_unrelated_inline_verification`: expected a known fact or admitted evidence.

The green command returned exit 0, `806 passed, 1 skipped in 25.17s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_snapshot_provenance.py tests/test_decision_snapshot.py tests/test_decision_model.py tests/test_decision_independence.py tests/test_dated_price_snapshot.py tests/test_decision_verify.py tests/test_lab_jurisdiction.py tests/test_set_value_hashes.py --tb=short
```

The region and invalid-identity tests now omit irrelevant price facts, so they
exercise their existing assertions with no mismatched fact owner. No assertions
were removed. Existing coverage verifies lab inheritance, set binding, dated
prices, newer failed-verification precedence, and repository snapshot builds.

No production deployment or external provider calls were observed or attempted.

## AUD-01-F6 and execution scope

The supplied synthetic numeric reproduction ran against unchanged numeric code:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short /tmp/MODEL-458-ENG-A-scratch/test_f6_repro.py
```

Exit 1, `5 failed in 0.44s`. The three cases of
`test_condition_must_reject_nonfinite_json_numbers` and
`test_weight_overflow_json_is_invalid_spec` reported `DID NOT RAISE SpecError`.
`test_finite_weighted_decision_roundtrips_json` reported three required-number
validation errors at `bands.best.0.score` and the two `score_interval` bounds.
There is no green result for this finding because its implementation is blocked.

The contract's Versioning section requires 3.0 for newly refused inputs. The
required version artifacts include `api/worker/openapi.yaml`,
`mcp/src/contract-version.ts`, and `mcp/test/contract-version.test.ts`, outside
the spec's named paths. The executor brief says to stop and report when another
file is required. Scope confirmation was requested and has not been received.
No numeric contract change was made.

AUD-01-F7 bounded relaxation work and AUD-01-F4 lifecycle recomputation remain
pending. Neither reproduction nor implementation was run, preserving the
specified finding order. No claim of completion is made for either finding.

## Deployment-path validation

The private data checkout was used only for local validation. No private values
or private revision identifiers are recorded here. The key below is a throwaway
fixture key, not a deployed credential.

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/MODEL-458-ENG-A-scratch/modelspec-data
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm install --prefix /tmp/MODEL-458-ENG-A-scratch/memory --no-save pyodide@0.28.3
env PYTHONPATH=$PWD MODELSPEC_SNAPSHOT_KEY=model-458-eng-a-memory-only TMPDIR=/tmp/MODEL-458-ENG-A-scratch /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/MODEL-458-ENG-A-scratch/modelspec-data
env NODE_PATH=/tmp/MODEL-458-ENG-A-scratch/memory/node_modules MODELSPEC_SNAPSHOT_KEY=model-458-eng-a-memory-only /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs api/worker/src --limit-mib 115 --output /tmp/MODEL-458-ENG-A-scratch/memory-current.json
env NODE_PATH=/tmp/MODEL-458-ENG-A-scratch/memory/node_modules MODELSPEC_SNAPSHOT_KEY=model-458-eng-a-memory-only /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs api/worker/src --successor --limit-mib 115 --output /tmp/MODEL-458-ENG-A-scratch/memory-successor.json
```

Every command returned exit 0. The private build vendored 129 files. The probe
runs Pyodide 0.28.3 with its Pydantic 2.10.6 and exercises decide, vocabulary,
rank, and policy-check requests locally with networking disabled for the Worker.

| Period | Steady bytes | Steady MiB | Limit MiB | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 114272581 | 108.978826 | 115 | Pass |
| Successor | 109769701 | 104.684545 | 115 | Pass |

The current-period noisy peak was 112.494504 MiB, producing the existing
112 MiB warning. Its steady-state gate passed. No gate was raised.

The public bundle was restored and import-checked after the private probe:

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
```

A separate read-only review of the snapshot change found no actionable defects.
This does not replace the pending independent review. No full local suite,
production deployment, paid-provider request, or later finding implementation
was performed. No production settings, ranking floors, legal text, frozen data,
prices, plans or release tags were changed.

The public-bundle import check returned exit 0. The source-exclusion check also
returned exit 0, `46 passed, 1 skipped in 87.58s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py --tb=short
```
