# MODEL-458-ENG-B execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`. A fresh `git fetch origin main`
confirmed that this was `origin/main` before any change.

Final implementation and regression-test SHA:
`de65002ee3c6f794d3bee2a2c208f8923724a90a`.
The evidence-only commit follows this SHA. The final PR head SHA is recorded in
the PR body and executor completion line. Resolve the evidence revision with
`git log -1 --format=%H -- docs/evidence/MODEL-458-ENG-B-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-458-eng-b`.
Branch: `model-458-eng-b`. All commands below ran from that worktree unless stated.

## Tools and constraints

Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1,
cryptography 45.0.7, Git 2.50.1, GitHub CLI 2.103.3, Node v22.22.3, npm 10.9.8,
Pyodide 0.28.3.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`; Node and npm are from
`/Users/terbeest/.nvm/versions/node/v22.22.3/bin`.

Read the executor brief, ModelSpec overrides, bundle spec, repository instructions,
`docs/handoff/README.md`, and the relevant decision and ranking contract sections.
Existing nullable tie-breakers and response fields cover these changes. No contract
range widens. No production setting, frozen data, price, plan, legal text, or
ranking floor changed.

All pytest runs were serial with `-p no:cacheprovider`. No full suite ran locally.
The original synthetic reproduction blocks were copied from the supplied spec to
`/tmp/MODEL-458-ENG-B-scratch/executor/test_f{2,3,5,8,9}_repro.py`, then each ran
before its finding's fix. Commands used this exact prefix:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider
```

Each command's direct exit status was checked. Red runs exited 1; green runs exited 0.

## AUD-01-F2

Commit: `b9cdb7faa66233d626466b40fb8ea6a6109d42ac`.
Exclusion reasons use the original filter's evidence and relative thresholds.
Remove-one-gate probes retain the original access reach.

Original reproduction command added `-s --tb=short` and the scratch
`test_f2_repro.py` path to the pytest prefix. Output: `2 failed in 0.37s`.
The synthetic ranked row also appeared in exclusions; the access counterfactual
reported 2 admissions where the rerun reported 1.

Permanent regressions in `tests/test_decision_explain.py`:

- `test_full_explanation_uses_the_same_best_anchor_as_filtering`, four cases
  covering a simple floor, a nested floor, and both orders of multiple floors.
- `test_constraint_costs_keep_the_requested_access_reach`, two cases covering
  admissions and objective gain against a fresh request.

Red command suffix:
`--tb=short tests/test_decision_explain.py -k 'same_best_anchor or requested_access_reach'`.
Output: `6 failed, 21 deselected in 0.53s`. The extra ranked model was present in
exclusions; the access-restricted gain was 99 instead of 9.

Green command suffix:
`tests/test_decision_explain.py tests/test_decision_plans.py tests/test_decision_estate.py tests/test_decision_filter.py tests/test_relax_single.py`.
Output: `170 passed in 2.34s`.

## AUD-01-F3

Commit: `1b0315c6ab519407234df3bc9408d0f96869a7b2`.
A unique price or speed extreme requires known values for every tied representative.

Original reproduction command suffix: `--tb=short /tmp/MODEL-458-ENG-B-scratch/executor/test_f3_repro.py`.
Output: `1 failed in 0.46s`, with `('lab/a', 'lab/a')` instead of `(None, None)`.

Permanent regression: `tests/test_decision_capability.py::test_tie_extrema_require_known_values_for_every_member`.
Its 20 cases cover unknown price and speed independently and together, known
unique extrema, and equal values. Routes cover omitted access, own software,
provider estate and chat plans. Chat assertions use monthly plan prices and
retain null per-task costs. Existing measurement-count assertions remain unchanged.

Red command suffix: `--tb=short tests/test_decision_capability.py -k tie_extrema_require_known`.
Output: `12 failed, 8 passed, 35 deselected in 0.82s`.

Green command suffix:
`tests/test_decision_capability.py tests/test_decision_bands.py tests/test_decision_estate.py tests/test_decision_plans.py tests/test_decision_summary.py`.
Output: `214 passed in 22.63s`.

## AUD-01-F5

Commit: `b6abc1b3e9f4173dbc62b876f9323927299ab1e8`.
Unknown-facet attribution traverses the truth values presented by nested operands,
including explicit policies, consistently with Boolean evaluation.

Original reproduction command suffix: `--tb=short /tmp/MODEL-458-ENG-B-scratch/executor/test_f5_repro.py`.
Output: `1 failed in 0.42s`, with nested may-qualify count 0 instead of 1.

Permanent regressions in `tests/test_decision_filter.py`:

- `test_nested_unknown_overrides_preserve_boolean_participation`, ten cases for
  `all`, `any`, `not`, compound-node policies, and explicit pass/fail policies.
  May-qualify cases assert that only context remains unresolved.
- `test_nested_missing_governance_remains_fail_closed`, three cases for missing
  licence, retention and region information.

Red command suffix: `--tb=short tests/test_decision_filter.py -k 'nested_unknown_overrides or nested_missing_governance'`.
Output: `4 failed, 9 passed, 51 deselected in 0.52s`.
An earlier fixture draft used an invalid retention enum; it was corrected to
numeric retention before the recorded red run and before changing production code.

Green command suffix:
`tests/test_decision_filter.py tests/test_decision_regions.py tests/test_licence_rules.py tests/test_cite_only_retention.py`.
Output: `121 passed in 1.88s`.

## AUD-01-F8

Commit: `241a5e7f9903bbce0dc438a3f689f3c58635289b`.
Band membership compares the unrounded pairwise probability. Presentation keeps
four decimal places. Both band and blend use the same width predicate.

Original reproduction command suffix: `--tb=short /tmp/MODEL-458-ENG-B-scratch/executor/test_f8_repro.py`.
Output: `2 failed in 0.26s`. Raw probability `0.24996496649784594` was displayed
as `0.25` and admitted; endpoints `-0.1` and `2.7` were classified as thin.

Permanent regressions in `tests/test_decision_bands.py`:

- `test_best_band_membership_precedes_probability_rounding`, real distributions
  immediately below and above the probability threshold, all displayed as 0.25.
- `test_best_band_includes_probability_exactly_at_threshold`, exact equality with
  a controlled numerical result, independent of platform libm rounding.
- `test_band_and_blend_width_boundaries_ignore_interval_offset`, translated
  intervals and widths one stored decimal unit above/below 2.8.

Red command suffix: `--tb=short tests/test_decision_bands.py -k 'membership_precedes or boundaries_ignore'`.
Output: `3 failed, 8 passed, 11 deselected in 0.27s`.

Green command suffix:
`tests/test_decision_bands.py tests/test_decision_optimise.py tests/test_decision_capability.py`.
Output: `113 passed in 32.99s`.
After replacing the approximate equality fixture with the controlled exact case,
`tests/test_decision_bands.py` gave `22 passed in 0.56s`.

Snapshot endpoint serialization rounds to nine decimal places in
`decision/capability.py::to_payload` and `_round`. The shared comparison uses an
absolute tolerance of `1e-12`, with zero relative tolerance, below the stored
precision. Existing `2.8 + 1e-9` coverage still passes. `BAND_PROBABILITY` and
`THIN_INTERVAL_WIDTH` are unchanged.

## AUD-01-F9

Commit: `de65002ee3c6f794d3bee2a2c208f8923724a90a`.
The graph ranker sorts by descending score, ELO and parameter count, then ascending
model ID. Its serving dependencies are unchanged.

Original reproduction command suffix: `--tb=short /tmp/MODEL-458-ENG-B-scratch/executor/test_f9_repro.py`.
Output: `1 failed in 0.23s`, with different limit-one shortlists after reversal.

Permanent regressions in `tests/test_incomplete_evidence_ranking.py`:

- `test_graph_rank_exact_ties_are_independent_of_candidate_order`, all six
  permutations of three equal candidates, at limits one and three.
- `test_graph_rank_preserves_score_elo_and_parameter_priorities`, real scoring
  with distinct score, ELO, parameter and ID priorities, including missing values.

Red command suffix: `--tb=short tests/test_incomplete_evidence_ranking.py -k 'graph_rank_exact or graph_rank_preserves'`.
Output: `3 failed, 27 deselected in 0.21s`.

Green command suffix:
`tests/test_incomplete_evidence_ranking.py tests/test_ranking.py tests/test_class_fit.py`.
Output: `122 passed in 16.48s`.

## Combined verification

The complete union of the requested focused suites passed on the final
implementation, `546 passed in 55.68s`, exit 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_explain.py tests/test_decision_plans.py tests/test_decision_estate.py tests/test_decision_filter.py tests/test_relax_single.py tests/test_decision_capability.py tests/test_decision_bands.py tests/test_decision_summary.py tests/test_decision_regions.py tests/test_licence_rules.py tests/test_cite_only_retention.py tests/test_decision_optimise.py tests/test_incomplete_evidence_ranking.py tests/test_ranking.py tests/test_class_fit.py
```

The five original reproduction files also passed together after the fixes.
Output: `7 passed in 0.61s`, exit 0. Their exact command was the same pytest prefix followed by all five paths:
`/tmp/MODEL-458-ENG-B-scratch/executor/test_f2_repro.py /tmp/MODEL-458-ENG-B-scratch/executor/test_f3_repro.py /tmp/MODEL-458-ENG-B-scratch/executor/test_f5_repro.py /tmp/MODEL-458-ENG-B-scratch/executor/test_f8_repro.py /tmp/MODEL-458-ENG-B-scratch/executor/test_f9_repro.py`.

The source-policy suite ran after staging the evidence file:
`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py`.
It reported `46 passed, 1 skipped in 56.48s`. The optional built-site scan was
skipped because no site build was supplied.

`git diff --check` passed. An AST comparison against the base, excluding only
`RankingEngine.rank_report`, found `api/ranking/engine.py` otherwise identical.
This verifies that ranking floors and `neutrality_commitment()` did not change.
Read-only parallel reviews found no implementation defects. They prompted the
exact-probability test portability correction recorded above.

## Worker bundle verification

The data source was `https://github.com/turbobeest/modelspec-data.git`.
The private data clone lived only under
`/tmp/MODEL-458-ENG-B-scratch/memory/modelspec-data`. The probe followed the deploy
vendoring path in `.github/workflows/rank-api.yml`, with a fresh throwaway HMAC
key generated by `secrets.token_hex(32)`. Inherited Ed25519 and source-cache
overrides were removed from the child environment. No real credential was used
for signing. A generated private bundle remained in scratch.

The exact runner invocation was:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-ENG-B-scratch/memory/run_memory.py
```

The runner set `PYTHONPATH` to this worktree, prepended the pinned Node bin
directory to `PATH`, set `TMPDIR` to the memory scratch directory,
`MODELSPEC_REQUIRE_DATA_DIR=1`, and `NODE_PATH` to
`/tmp/MODEL-458-ENG-B-scratch/memory/runtime/node_modules`. It executed these
commands with the throwaway `MODELSPEC_SNAPSHOT_KEY` in the environment:

```sh
/Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm install --prefix /tmp/MODEL-458-ENG-B-scratch/memory/runtime --no-save pyodide@0.28.3
/Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/MODEL-458-ENG-B-scratch/memory/modelspec-data --out /tmp/MODEL-458-ENG-B-scratch/memory/bundle
/Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-ENG-B-scratch/memory/bundle --limit-mib 115 --output /tmp/MODEL-458-ENG-B-scratch/memory/current.json
/Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-ENG-B-scratch/memory/bundle --limit-mib 115 --output /tmp/MODEL-458-ENG-B-scratch/memory/successor.json --successor
```

Between vendoring and probing, the runner copied handwritten `api/worker/src/*.py`
into the scratch bundle with `shutil.copy2`, excluding `bundled_data.py` and
`tier_policy.py` so the private generated versions remained intact. Each command
exited 0. The probe invoked the real local Worker handlers for decide, vocabulary,
rank and policy-check. Its fetch stub refuses network requests.

| Period | Steady bytes | Steady MiB | Peak MiB | Steady limit MiB | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Current | 114340281 | 109.043389 | 112.558816 | 115 | pass |
| Successor | 109736209 | 104.652604 | 107.798631 | 115 | pass |

The current-period peak crossed the probe's informational 112 MiB warning level.
Both retained-memory checks passed. The 115 MiB gate and all other gates remain
unchanged. No comparison to a main-branch memory baseline was performed.

Public bundle regeneration and dependency validation also exited 0:

```sh
/Users/terbeest/.codex-g2/heavy.sh env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=0 MODELSPEC_SNAPSHOT_KEY=model458-public-verification-key /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
```

Output: `vendored 129 files` and `bundle imports cleanly with only declared dependencies`.
The generated bundle is ignored by Git; no frozen public data changed.

## Limits of observation

The defects were reproduced with synthetic inputs. No production request or
private-catalogue defect sweep was performed. Private data was used only to build
and measure the Worker bundle. No private values or private commit IDs are included
here. The local memory probe exercises the deployed modules in pinned Pyodide;
it is not a production isolate measurement.

No vendor API calls, device tests, deployments, Linear writes or merges were
performed. Full CI and independent review remain pending on the draft PR.
