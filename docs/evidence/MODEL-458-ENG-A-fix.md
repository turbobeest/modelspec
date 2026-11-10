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

## Round 2

`contract_version` stays 2.19. No contract field changes type or range.
`origin/main` had moved; the branch did not conflict, so it was not merged.

### CI

Pytest shard 8/8 failed on `test_unknown_lab_subject_still_errors` (three
subjects). AUD-01-F1 rejects a fact that does not name its enclosing model
before the catalogue invariant runs. The test now expects `SnapshotBuildError`
matching `must name its actual owner`. That is the only expectation changed.
Known-lab inheritance is unchanged: the shared-lab calibration test still
expects an empty finding list.

Before the expectation change the focused command returned exit 1, `3 failed`.
After it, this command returned exit 0, `62 passed, 1 skipped in 1.56s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_trust.py::test_unknown_lab_subject_still_errors tests/test_data_trust.py::test_calibration_resolves_shared_lab_facts_without_adding_candidates tests/test_lab_jurisdiction.py tests/test_snapshot_provenance.py --tb=line
```

### AUD-01-F4

A dropped gate kept the retired-model opt-in from the condition it removed, so
a reported admission did not replay. In this round `include_retired` was
derived from the conditions still on the resolved spec. Dropping the only
opt-in admits nobody. A lifecycle opt-in that remains still admits retired
models. Round 3 stores the field again; see below.

The new regressions failed before the change (exit 1, `2 failed`). This
command then returned exit 0, `95 passed in 2.59s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_relax_single.py tests/test_decision_relax.py tests/test_decision_filter.py tests/test_decision_explain.py --tb=line
```

### AUD-01-F7

Relaxation search stays exact: the fewest relaxable gates, caps and floors
before spec order. Equivalent gates are one choice. A candidate's failing
gates name the set, and the filter confirms it. The search spends a bounded
number of filter runs. Round 3 caps that spend at 64 calls. No previously
accepted spec is refused.

The new work-budget regressions failed before the change. The cap-preference
test passed on the old search. After the change this command returned exit 0,
`48 passed in 0.90s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_relax.py tests/test_relax_single.py tests/test_decision_explain.py --tb=line
```

### AUD-01-F6

On the pre-change code, spec numbers that are not finite were accepted, and
finite weights whose products overflow produced scores that are not JSON.
Finite constraint values, including very large finite values, zero, negative
limits, and integers that do not fit in a float, already returned a valid
decision and still do. This round rejected non-finite spec numbers. Round 3
narrows that refusal to the classes the base already failed. Overflowing
finite weights still return a decision; one common scale keeps every score and
score interval finite and preserves order. When every product and sum is
already finite, the score expression is unchanged. An ordinary max of two
finite values still scores 1.0 and 0.0.

The new module failed before the change. Re-measured on the base, that run
returned exit 1, `10 failed, 8 passed`.
After the change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_numeric_bounds.py tests/test_decision_optimise.py tests/test_decision_relax.py --tb=line
```

Exit 0, `64 passed in 23.06s`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_contract.py tests/test_decision_bands.py tests/test_decision_filter.py --tb=line
```

Exit 0, `311 passed in 1.71s`. The generated decision schema was unchanged.
No OpenAPI or MCP contract-version file changed.

### Deployment-path validation, round 2

The same private checkout, throwaway key, Pyodide 0.28.3, and probe commands
as round 1. Every command returned exit 0. Both steady readings are under the
unchanged 115 MiB gate. The current-period noisy peak again exceeded 112 MiB
and produced the existing warning. No gate was raised.

| Period | Steady bytes | Steady MiB | Limit MiB | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 114273370 | 108.979578 | 115 | Pass |
| Successor | 109756866 | 104.672304 | 115 | Pass |

`vendor.py --check` restored the public bundle and returned exit 0. The
worktree was clean afterward. No production settings, ranking floors, legal
text, frozen data, prices, plans, or release tags were changed.

## Round 3

`origin/main` was merged before these fixes. `contract_version` stays 2.19.
No contract field changes type or range. `decision/engine.py`,
`decision/explain.py`, `decision/filter.py`, `decision/bands.py` and
`api/ranking/engine.py` were not edited.

### AUD-01-F6

Round 2 rejected every non-finite spec number. That refused specs the base
already answered. Measured on the base, a class is refused only when that
same request already failed. A weight that is not finite is rejected. Compact
`NaN`, `Infinity` and `-Infinity` tokens stay rejected. Compare values,
windows, set values, best margins, tolerances, memory sizes and budgets that
already decided still decide, with the same status and ranks. A non-finite
near-miss distance is omitted, so the full explanation is strict JSON and
round-trips through `Decision`. Scores that would overflow are reported on a
common power-of-two scale. Reported weights and penalties stay the caller's.
A zero shift leaves the finite score expression unchanged.

Weights `{context: 1e308, max_output: 1e308}` with `soft(0.5)` report weight
`1e308` and `soft_penalty` 0.5. Order is unchanged. The response round-trips.

Re-measured on this head and on the base, at explain none and explain full.
The classes are the rows of `tests/test_decision_numeric_bounds.py`, plus the
finite weight pair. 30 classes match. 9 differ. Every class the base answered
still returns a decision.

| Class | Base | Head |
| --- | --- | --- |
| `compare_json_nan` | decision, strict JSON | decision, strict JSON |
| `compare_json_neg_inf` | decision, strict JSON | decision, strict JSON |
| `compare_json_neg_1e400` | decision, strict JSON | decision, strict JSON |
| `compare_json_pos_inf` | explain none: decision, strict JSON; explain full: decision, JSON not strict | decision, strict JSON |
| `compare_json_1e400` | explain none: decision, strict JSON; explain full: decision, JSON not strict | decision, strict JSON |
| `compact_1e400` | explain none: decision, strict JSON; explain full: decision, JSON not strict | decision, strict JSON |
| `compact_neg_1e400` | decision, strict JSON | decision, strict JSON |
| `best_1e400` | decision, strict JSON | decision, strict JSON |
| `window_0_1e400` | decision, strict JSON | decision, strict JSON |
| `window_0_pos_inf` | decision, strict JSON | decision, strict JSON |
| `window_nan_1` | explain none: decision, strict JSON; explain full: decision, JSON not strict | decision, strict JSON |
| `window_neg_inf_1` | decision, strict JSON | decision, strict JSON |
| `in_100_1e400` | decision, strict JSON | decision, strict JSON |
| `in_nan` | decision, strict JSON | decision, strict JSON |
| `in_pos_inf` | decision, strict JSON | decision, strict JSON |
| `in_neg_inf` | decision, strict JSON | decision, strict JSON |
| `lex_within_1e400` | decision, strict JSON | decision, strict JSON |
| `lex_within_string_inf` | decision, strict JSON | decision, strict JSON |
| `lex_within_token_inf` | decision, strict JSON | decision, strict JSON |
| `memory_string_inf` | decision, strict JSON | decision, strict JSON |
| `memory_token_inf` | decision, strict JSON | decision, strict JSON |
| `budget_string_inf` | decision, strict JSON | decision, strict JSON |
| `budget_token_inf` | decision, strict JSON | decision, strict JSON |
| `compact_nan` | SpecError | SpecError |
| `compact_pos_inf` | SpecError | SpecError |
| `compact_neg_inf` | SpecError | SpecError |
| `best_nan` | SpecError | SpecError |
| `best_pos_inf` | SpecError | SpecError |
| `best_neg_inf` | SpecError | SpecError |
| `weight_pos_inf` | ValueError | SpecError |
| `weight_1e400` | ValueError | SpecError |
| `weight_nan` | SpecError | SpecError |
| `weight_neg_1e400` | SpecError | SpecError |
| `weight_neg_inf` | SpecError | SpecError |
| `preference_weight_string_inf` | ValueError | SpecError |
| `preference_weight_token_inf` | ValueError | SpecError |
| `preference_value_nan` | SpecError | SpecError |
| `preference_value_pos_inf` | SpecError | SpecError |
| `finite_weight_pair` | decision, JSON not strict | decision, strict JSON |

### AUD-01-F4

`include_retired` is a stored field again. `without()` drops gates and
recomputes it from the conditions that remain. A trial that only reorders or
rewrites a condition keeps the stored opt-in. A retired `lab/old` at context
64, asked for by `model.lifecycle = retired` and eliminated by
`model.context_window >= 128`, explains one context row: value 64, unit
tokens, record `lab/old#model.context_window`, basis `snapshot measurement`.

### AUD-01-F7

`fewest` spends at most 64 filter calls. When that budget is spent it returns
no relaxation. That empty result is deterministic. An already feasible spec
uses the old size, cap and index order and stops at the first drop that
confirms. Generated cases, 240 on each of two lineups with seed 458, matched
that search with 0 mismatches. Twelve, fourteen and sixteen caps beside one
best margin each stayed within 32 filter calls.

### Focused tests

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_numeric_bounds.py tests/test_decision_relax.py tests/test_relax_single.py tests/test_decision_filter.py tests/test_decision_explain.py tests/test_decision_optimise.py --tb=line
```

Exit 0, `206 passed in 21.22s`.

### Deployment-path validation, round 3

The same private checkout, throwaway key, Pyodide 0.28.3, and probe commands
as round 1. The private build vendored 129 files. Every command returned exit
0. Both steady readings are under the unchanged 115 MiB gate. The
current-period noisy peak was 112.527243 MiB and produced the existing 112
MiB warning. Its steady-state gate passed. No gate was raised.

| Period | Steady bytes | Steady MiB | Limit MiB | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 114281838 | 108.987654 | 115 | Pass |
| Successor | 109763062 | 104.678213 | 115 | Pass |

`vendor.py --check` restored the public bundle and returned exit 0. The
worktree was clean afterward. No production settings, ranking floors, legal
text, frozen data, prices, plans, or release tags were changed.

## Round 4

`origin/main` was merged as `c9712670680bce41c9562b8ab452aaadbbcaa1cd`, then
again at `d9e8deddeab9ce86ecce42c7fbd4e0cf76e0b6b2` and
`3f7d050deeaff49045a7898105dc52c4a9e72363`. Those two commits add tests and
their evidence only.
`contract_version` stays 2.19. `decision/engine.py`, `decision/explain.py`,
`decision/filter.py`, `decision/bands.py` and `api/ranking/engine.py` were
not edited. The round is `decision/relax.py`, its tests, and this file.

`fewest` still spends at most 64 filter calls. When that budget is spent it
returns no relaxation. That empty result is deterministic. A separate marker
on the decision for a spent budget needs `decision/engine.py` and a contract
field, so this round leaves the empty result.

### P1-A, non-relaxable best gate

A best gate in a class condition or a requested domain is scored with the
anchor. `fewest` does not raise. Commit
`0f7cbdc18d1880b81f7ef3d96fdaf5fc929b19a5`.

### P1-B, best gate under not

When a relaxable best reference sits under `not`, at any depth, `fewest`
uses the budgeted per-index search. The anchored proposal is not used for
that input. Commit `4a4f563fccf2e1ba1fbb7da51346c54e26540df0`.

### P2, confirm while building

Plain blocking sets are walked in size, cap and index order. Each proposal
is confirmed as it is built. The walk stops once no remaining set can sort
ahead of a confirmed relaxation. A lineup with at least 63 distinct plain
blocking sets, a one-gate answer, and one best gate that blocks nobody
returns that one gate in at most 8 filter calls. The same bound holds at
120 models. Twelve, fourteen and sixteen unsatisfiable caps beside one best
gate stay within 32 calls. Commit
`2aa1c1a573143fe88e962335e5161b4278f0a682`.

### P3, generated coverage

The generated comparison includes a requested domain and a 24-model lineup,
and it still includes a best reference under `not`. Compared with the
per-index search, seeds 458, 11 and 2026 had 0 mismatches. Each seed ran
3000 cases on the pair and retired lineups, 400 cases with a requested
domain, and 200 cases on the wide lineup. Commit
`74b4c3886c787081439524fe4e698ce5f6432437`.

Compared with the base search, 6900 cases produced 14 differences. All 14
are a retired lineup whose conditions include the lifecycle opt-in. Dropping
that opt-in recomputes retired admission. Seed 11 differed 8 times, seed 458
differed 3 times, and seed 2026 differed 3 times. Cases with no lifecycle
condition produced 0 differences.

### Focused tests

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_numeric_bounds.py tests/test_decision_relax.py tests/test_relax_single.py tests/test_decision_filter.py tests/test_decision_explain.py tests/test_decision_optimise.py --tb=line
```

Exit 0, `211 passed in 23.68s`.

### Deployment-path validation, round 4

The same private checkout, throwaway key, Pyodide 0.28.3, and probe commands
as round 1. The private build vendored 129 files. Every command returned exit
0. Both steady readings are under the unchanged 115 MiB gate. The
current-period noisy peak was 112.525192 MiB and produced the existing 112
MiB warning. Its steady-state gate passed. No gate was raised.

| Period | Steady bytes | Steady MiB | Limit MiB | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 114279688 | 108.985603 | 115 | Pass |
| Successor | 109766648 | 104.681633 | 115 | Pass |

`vendor.py --check` restored the public bundle and returned exit 0. The
worktree was clean of vendored private data afterward. No production
settings, ranking floors, legal text, frozen data, prices, plans, or release
tags were changed.

## Round 5

`origin/main` moved after round 4. The branch merged it at
`6721afe4990f8844d6c3b87ad74eb494862e3762`, then again at
`bc5dff4a896072a0f73181ad15ebd0b048d99a4a` so the branch contains
`origin/main`. The first merge had one conflict, in the change log of
`docs/decision-contract.md`. Both sides added a note that begins
`**MODEL-458, under 2.19 without a version change:**`. Both notes stay, word
for word. The note on band membership and the reported probability comes
first. The note on non-finite weights comes second. `contract_version` stays
2.19. The second merge had no conflict. `git diff origin/main...HEAD` names
the same 14 files as before this round. Against `origin/main`,
`docs/decision-contract.md` adds the non-finite-weight note.

Companion checks returned exit 0. Nothing was regenerated.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_harness.py::test_mcp_capture_matches_current_public_sources
```

OpenAPI reported that `api/worker/openapi.yaml` matches the implementation.
The MCP capture check returned `1 passed in 0.39s`.

Focused tests returned exit 0, `577 passed in 26.30s`:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_relax.py tests/test_decision_contract.py tests/test_data_trust.py tests/test_decision_explain.py tests/test_decision_numeric_bounds.py tests/test_decision_snapshot.py tests/test_relax_single.py tests/test_snapshot_provenance.py
```

No assertion was removed or loosened. No production settings, ranking floors,
legal text, frozen data, prices, plans, or release tags were changed.
