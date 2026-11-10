# MODEL-458-TEST-A verification

Base SHA: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca` (`origin/main` at start).
The audit bundle's base is `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`. This
worktree stayed on current `origin/main`. The supplied reproduction stops
there with `Use the audited base SHA` before it runs a case. Replaying the
same retained sources on this HEAD, then restoring each file, still changes
the observable output for datedprices01, datedprices02, datedprices03,
datedprices05, capability06, bounded02, bounded03, and bounded05. Each phase
exited 0. `git status` was clean afterward.

Python 3.14.4, pytest 9.1.1, ruff 0.16.6, Git 2.50.1. Tests use
`/Users/terbeest/dev/modelspec/.venv/bin/python` with `PYTHONPATH=$PWD`,
serially, `-p no:cacheprovider`, no `-n`. Multi-file suites went through
`~/.codex-g2/heavy.sh`. No production file remains changed. No full local
suite, fetch, paid call, deployment, or Worker memory probe ran. CI is
checked after the push.

## AUD-11-F4

A non-global Vertex row, a malformed row before a blank-owner output row, and
a second eligible table each yield no dated price. The comparator stays the
only priced result. The price clock in these tests is 2026-11-09 UTC.

With each ownership guard temporarily set to the audited alternative, the new
test failed before any later assertion:

- `test_vertex_rejects_non_global_price_rows_for_global_offering`: readings
  were one `DatedPrice` value `0.75`, not `[]`. 1 failed in 0.31s, exit 1.
- `test_vertex_clears_owner_after_malformed_intervening_row`: one
  `DatedPrice` value `3.75`. 1 failed in 0.29s, exit 1.
- `test_vertex_rejects_multiple_eligible_pricing_tables`: one `DatedPrice`
  value `0.75`. 1 failed in 0.36s, exit 1.

Restored production code:

```text
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_dated_price_readers.py tests/test_dated_price_serving.py tests/test_dated_price_snapshot.py
```

96 passed in 0.75s, exit 0. Commit `3b2f8b4d4f480f9d0c5bc140481d563070697818`.

## AUD-11-F5

When the short and long context columns differ, the input reading is `0.75`
and the 1000/1000 task cost is 0.00175. The cached-input reading is `0.075`.
The same clock pin applies.

With the column choice temporarily set to the audited alternative,
`test_vertex_reads_short_context_input_when_columns_differ` got `0.99` and
`test_vertex_reads_short_context_cached_input_when_columns_differ` got
`0.099`. 2 failed in 0.31s, exit 1.

The same three-file command then reported 98 passed in 0.79s, exit 0.
Commit `5e6110a5e301deb901ab77324685c0c7bd5ee07f`.

## AUD-11-F6

One fresh direct benchmark that is both software-engineering and Rust
evidence is the refinement observation once. The public means and standard
deviations match the posterior with parent mean 0, widened prior variance
4.15, and one observation of variance 0.75. The disclosed interval for lab/b
is [-0.422516492, 1.620268795]; lab/a is the negation.

With the parent-row exclusion temporarily removed,
`test_refinement_evidence_does_not_enter_its_own_parent_prior` obtained
0.652433576455629 against 0.5988761514130964. 1 failed in 0.24s, exit 1.
Unmodified, that test passed in 0.39s.

```text
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_capability.py tests/test_decision_refinement_estimates.py tests/test_capability_calibration.py tests/test_decision_latency.py tests/test_decision_summary.py tests/test_decision_bands.py tests/test_decision_optimise.py tests/test_cite_only_recommendation_scope.py tests/test_cite_only_scope.py
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_warnings.py
```

254 passed in 35.18s, exit 0. 92 passed in 0.66s, exit 0.
Commit `cb67a8d6f8e83aced34a476c8ba0166bd5432b07`.

## AUD-11-F14

Equal weights keep the direct record `lab/a#z` and omit `lab/a#c`. At equal
item counts, one trim at the real response budget keeps both of lab/a's items
and only `lab/b#1`. Omission counts are one item.

With directness temporarily left out of the order,
`test_member_evidence_keeps_direct_before_proxy_on_equal_weight` retained
`lab/a#a`, `lab/a#b`, `lab/a#c`. Exit 1.
With the later-member tie temporarily reversed,
`test_one_budget_trim_prefers_later_member_on_equal_counts` retained only
`lab/a#1`. Exit 1.
Unmodified, both passed in 1.01s.

```text
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decide_bounded.py tests/test_decide_agent_budget.py tests/test_bounded_pick.py tests/test_decision_summary.py tests/test_decision_link.py tests/test_decision_contract.py tests/test_relax_single.py tests/test_subscription_availability.py tests/test_cite_only_supersession.py tests/test_cite_only_surfaces.py tests/test_cite_only_warning_scope.py tests/test_cite_only_recommendation_scope.py tests/test_ablation_proxy.py tests/test_next_move.py tests/test_cli_concierge.py tests/test_keyed_router_worker.py
```

1012 passed in 38.26s, exit 0.
Commit `641d51827e65e2f6c7e08daee79ce6154c5a8287`.

## AUD-11-F15

A drill-down whose compact body is exactly `DRILL_DOWN_BYTES` keeps
`lab/a#1` and does not count a `model_evidence.evidence.items` omission.

With the inclusive limit temporarily made exclusive,
`test_drill_down_exact_byte_budget_retains_evidence` saw 2870 bytes against
6731. Exit 1. Unmodified, the test passed in 0.71s. The same bounded suite
then reported 1013 passed in 48.24s, exit 0. This file is in that commit.
