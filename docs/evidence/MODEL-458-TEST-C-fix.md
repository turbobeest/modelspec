# MODEL-458-TEST-C execution evidence

Base: `4c59989970e01bbb318fbd1f05c58323682053f6` (`origin/main` at start).
The audited bundle's base is `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.

Implementation SHAs:

- AUD-11-F1: `36d17fcb7e8eb3cb03c012e59fcfe883b0cea733`
- AUD-11-F12: `fbce66bea966a436ae75415d1bb0b66f734923f5`
- AUD-11-F3: `b43445359462de5418e4a080b48f5e2ac44c1531`
- AUD-11-F13: `e50c3c95b8b2021b7475b07a097ff9fee78084c8`
- AUD-11-F2: `dac511a6ab8d5602c17314ab9972295aa30c3c93`
- AUD-11-F10: `5e4e649a975fad5f4127c1d621cd14a5d5a68790`
- AUD-11-F7: `db1486ad2355bd0ec649a4f2435a8b5db4417ef2`

The evidence commit follows the F7 SHA. Resolve it with
`git log -1 --format=%H -- docs/evidence/MODEL-458-TEST-C-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-458-test-c`.
Branch: `model-458-test-c`. Commands ran from that worktree unless stated.

## Tools

Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1,
cryptography 45.0.7, Git 2.50.1, GitHub CLI 2.103.3.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`.

Pytest was serial, with `-q -p no:cacheprovider` and no `-n`. No local full
suite. No `web/` build. Exit codes were read directly.

Production files were restored after every temporary mutant. At F7
(`db1486ad2355bd0ec649a4f2435a8b5db4417ef2`) the diff against the base contains
only the eight test files below, 265 insertions. This evidence file is the
only later addition.

- `tests/test_decision_filter.py`
- `tests/test_cited_score_warnings.py`
- `tests/test_decision_bands.py`
- `tests/test_decision_optimise.py`
- `tests/test_decision_relax.py`
- `tests/test_relax_single.py`
- `tests/test_incomplete_evidence_ranking.py`
- `tests/test_rank_worker.py`

## Reproduction on current main

The bundle command asserts `HEAD` equals the audited base. On this worktree it
exited 1:

```text
AssertionError: Use the audited base SHA
```

`HEAD` was `4c59989970e01bbb318fbd1f05c58323682053f6`. `git status --porcelain`
was empty. The same command's behavior loop was then run on that HEAD, without
the SHA lock, with `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONPYCACHEPREFIX=/tmp/MODEL-458-TEST-C-scratch/pyc`. Each case used its
retained source. Twelve cases exited 0 on both phases and the two outputs
differed:

`filter02`, `filter03`, `bands03`, `bands05`, `bands06`, `optimise01`,
`optimise06`, `optimise09`, `relax06`, `rank07`, `rank09`, `rank14`.

`relax03`: the listed anchor was absent (count 0), so that hunk was not
applied. A temporary equivalent edit, restored with
`git checkout -- decision/relax.py`, still changed `relax`. The finding was
not skipped. The tree was clean afterwards. `decision/relax.py` line 186 keeps
`-_cap_count`.

No finding was skipped.

## AUD-11-F1

Commit `36d17fcb7e8eb3cb03c012e59fcfe883b0cea733`.

`test_strict_capability_ceiling_excludes_estimate_at_threshold`: the gate
`software_engineering <` lab/b's fitted value `0.585283977` recommends lab/a
and excludes lab/b. `answer.members` is `["lab/a"]` and the result models are
`["lab/a"]`.

Red, with the listed mutant applied and then restored: `1 failed in 0.57s`,
exit 1. `members` was `['lab/b']`.

## AUD-11-F12

Commit `fbce66bea966a436ae75415d1bb0b66f734923f5`.

`test_direct_reference_with_no_direct_evidence_does_not_add_citation_warning`:
the proxy-tagged reference recommends lab/plain with `warnings` `[]`. With the
benchmark tagged direct and the cited score at 60, lab/plain stays recommended
and `warnings` is `["cite_only_not_machine_verified"]`.

Red, with the listed mutant applied and then restored: `1 failed in 0.57s`,
exit 1. `warnings` gained `cite_only_not_machine_verified` on the proxy-tagged
reference.

## AUD-11-F3

Commit `b43445359462de5418e4a080b48f5e2ac44c1531`.

- `test_pairwise_probability_at_band_threshold_joins_best`:
  `p_beats["lab/challenger"]` is `0.25`, best ids are
  `["lab/leader", "lab/challenger"]`, and `rest` is `()`.
- `test_cost_blend_uses_cheapest_offering_per_model`: leaders are `["lab/a"]`,
  `value` is `1`, and order is `["lab/a", "lab/b"]`.

Red, with each listed mutant applied and then restored:

- bands03: `1 failed in 0.52s`, exit 1. Best lacked `lab/challenger`.
- bands05: `1 failed in 0.53s`, exit 1. Leaders were `['lab/b']`.

## AUD-11-F13

Commit `e50c3c95b8b2021b7475b07a097ff9fee78084c8`.

`test_band_estimate_counts_direct_and_proxy_benchmarks_separately`: each
model's `software_engineering` estimate has `benchmarks` 3 and
`direct_benchmarks` 1.

Red, with the listed mutant applied and then restored: `1 failed in 0.54s`,
exit 1. `direct_benchmarks` was 2.

## AUD-11-F2

Commit `dac511a6ab8d5602c17314ab9972295aa30c3c93`.

- `test_span_exactly_at_reference_epsilon_is_not_degenerate`: max order is
  `["b", "a"]` with scores `[1.0, 0.0]`. Min order is `["a", "b"]` with scores
  `[1.0, 0.0]`.
- `test_weight_tipping_points_exclude_zero_thresholds`: `tipping_points` is
  `()`.
- `test_multiple_soft_penalties_accumulate_and_can_change_the_winner`: order is
  `["b", "a"]`. Candidate a has score `pytest.approx(-0.2)` and `soft_penalty`
  `1.2`.

Red, with each listed mutant applied and then restored:

- optimise01: `1 failed in 0.53s`, exit 1. Max order started with `a`.
- optimise06: `1 failed in 0.53s`, exit 1. A decrease-x tipping point had
  threshold `0.0` and `new_top` `b`.
- optimise09: `1 failed in 0.51s`, exit 1. Order started with `a`.

## AUD-11-F10

Commit `5e4e649a975fad5f4127c1d621cd14a5d5a68790`.

- `test_equally_small_relaxations_prefer_a_numeric_gate`: `relax` is
  `["model.context_window >= 8000"]`.
- `test_single_gate_admissions_deduplicate_a_models_offerings`:
  `gates[0].admits` is 1 and `together_admits` is 1.

Red, mutant restored afterwards:

- relax03: `1 failed in 0.54s`, exit 1. `relax` was
  `['model.fits_hardware in {apple_m3_max}']`. See the reproduction note: the
  listed anchor was absent.
- relax06: `1 failed in 0.50s`, exit 1. `admits` was 2.

## AUD-11-F7

Commit `db1486ad2355bd0ec649a4f2435a8b5db4417ef2`.

- `test_disabled_benchmark_does_not_raise_required_measurement_count`:
  `rank_status` is `ranked`, `required_benchmark_count` and `benchmark_count`
  are 1, `benchmark_coverage` is 1.0, `score` is 20.0, and
  `missing_benchmarks` is `[]`.
- `test_unranged_benchmark_clamps_before_image_generation_ranking`: status 200,
  `score` 39.0, `benchmark_score` 24.0, `clip_score` contribution 30.0.
- `test_tier_three_capability_keeps_its_declared_coding_contribution`: status
  200, `benchmark_score` 0.0, `capability_score` 2.77, `score` 17.77.
  Arithmetic in the test: `3 * 0.30 / 0.65 * 2` rounds to 2.77, and the first
  preferred type adds 15. The tier-3 constant was not edited.

Red, with each listed mutant applied and then restored:

- rank07: `1 failed in 0.23s`, exit 1. `rank_status` was `unranked`.
- rank09: `1 failed in 0.30s`, exit 1. `score` was 45.0.
- rank14: `1 failed in 0.26s`, exit 1. `capability_score` was 5.54.

## Green

All 13 new node ids, at `db1486ad2355bd0ec649a4f2435a8b5db4417ef2`:

`13 passed in 0.79s`, exit 0.

An earlier run of the same node ids, after the F3 and F13 split and before
these commits, was `13 passed in 0.67s`, exit 0.

## Focused suites

Each command ran once, after every new test in the files it names was present.
One shell ran them in this order and exited 0 (147.95s). Pytest summaries:

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_filter.py tests/test_decision_offering_evidence.py tests/test_decision_recall_fixes.py tests/test_decision_regions.py tests/test_model_174_hardware_private.py tests/test_lab_jurisdiction.py tests/test_speed_measurement.py tests/test_cite_only_recommendation_scope.py tests/test_cite_only_warning_scope.py tests/test_cite_only_row_warnings.py tests/test_decision_estate.py tests/test_decision_offering_invariant.py tests/test_model_347.py
```

`361 passed, 1 skipped in 19.92s`, exit 0. Covers AUD-11-F1 and AUD-11-F12.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_warnings.py
```

`93 passed in 0.70s`, exit 0. Named by AUD-11-F1, F12, F3, F13, and F2.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_bands.py tests/test_cite_only_row_warnings.py tests/test_decision_plans.py tests/test_decision_capability.py tests/test_decision_refinement_estimates.py tests/test_speed_measurement.py tests/test_decision_optimise.py
```

`241 passed in 44.44s`, exit 0. Covers AUD-11-F3 and AUD-11-F13.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_optimise.py tests/test_decision_bands.py tests/test_cite_only_row_warnings.py tests/test_decision_capability.py tests/test_decision_refinement_estimates.py tests/test_decision_cost_per_task.py tests/test_decision_offering_evidence.py tests/test_model_347.py tests/test_speed_measurement.py
```

`234 passed in 40.77s`, exit 0. Covers AUD-11-F2.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_relax.py tests/test_relax_single.py tests/test_decision_cost_per_task.py tests/test_model_347.py tests/test_hardware_review.py tests/test_decide_bounded.py tests/test_decision_summary.py
```

`257 passed in 16.69s`, exit 0. Covers AUD-11-F10.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ranking.py tests/test_incomplete_evidence_ranking.py tests/test_class_and_null_semantics.py tests/test_architecture_facts.py tests/test_rank_worker.py tests/test_unranked_candidates.py tests/test_decision_compatibility.py tests/test_cite_only_exports.py tests/test_typesafe_jev_card.py tests/test_api_access.py
```

`352 passed in 23.33s`, exit 0. Covers AUD-11-F7.

## Not observed

No full local pytest suite. No site build. No Worker memory probe. No contract
edit, frozen-data edit, ranking-floor edit, legal-text edit, price edit, or
production-switch edit. No production file remains in the diff. CI was not
checked in this file; the executor checks the draft PR after push.
