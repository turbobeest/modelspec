# MODEL-458-TEST-B execution evidence

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca` (`origin/main` at start).
The audited bundle's base is `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.

Implementation SHAs:

- AUD-11-F8: `4f532e7a52a4fd82c062bf9a519a663bd57fcf34`
- AUD-11-F9: `e78dfc9b5d2c6cb995e1647a98f9b52c82b10972`
- AUD-11-F11: `0a7a6f5ee135fd5e497600f67f79d08299c14d18`

The evidence commit follows the F11 SHA. Resolve it with
`git log -1 --format=%H -- docs/evidence/MODEL-458-TEST-B-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-458-test-b`.
Branch: `model-458-test-b`. Commands ran from that worktree unless stated.

## Tools

Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1,
cryptography 45.0.7, Git 2.50.1, GitHub CLI 2.103.3.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`.

Pytest was serial, with `-q -p no:cacheprovider` and no `-n`. No local full
suite. No `web/` build. Exit codes were read directly.

Production files were restored after every temporary mutant. The diff against
the base contains only `tests/test_decision_compare.py` and
`tests/test_decision_by_model.py`, plus this evidence file.

## Reproduction on current main

The bundle command asserts `HEAD` equals the audited base. On this worktree it
exited 1:

```text
AssertionError: Use the audited base SHA
```

`HEAD` was `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`. `git status --porcelain`
was empty. The same command's behavior loop was then run on that HEAD, with
each case's retained source and its one mutant, restoring the file afterwards.
All seven cases exited 0 on both phases, the two outputs differed, and the tree
was clean at the end. `compare01`, `compare02`, `compare03`, `compare05`,
`whynot01` and `whynot04` matched the recorded original stdout.
`whynot03` still distinguished the mutant. Its current original reports
`admits` 0. The recorded proof, from before `46c3ee08` passed the requested
reach into the remove-one-gate probe, reports `admits` 1. The regression pins
the current cost, including `admits` 0. The mutant still drops that cost.

## AUD-11-F8

Commit `4f532e7a52a4fd82c062bf9a519a663bd57fcf34`.

- `test_compare_uses_best_offering_rank_when_another_offering_moves`: lab/a
  offering ranks are `[1, 3]` then `[1, 4]`, and lab/a is absent from
  `comparison.models`.
- `test_compare_does_not_pair_multiple_replacement_offerings`: providers
  `p1`/`p2` replaced by `p3`/`p4` leave `changed` false and `models` empty.

Red, with the listed mutant applied and then restored:

- compare01: `1 failed in 0.42s`, exit 1. The failure is
  `rank_changed` `{'old': 3, 'new': 4}` for lab/a.
- compare03: `1 failed in 0.37s`, exit 1. `changed` was true.

Green new tests: `2 passed in 0.40s`, exit 0.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_compare.py tests/test_cli_compare.py tests/test_lab_jurisdiction.py
```

`95 passed, 1 skipped in 0.87s`, exit 0.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decide_worker.py::test_worker_compare_returns_an_http_comparison_from_two_snapshots tests/test_api_docs.py::test_comparison_schema_accepts_every_facet_value_and_sparse_offering tests/test_api_docs.py::test_comparison_result_schema_rejects_missing_and_malformed_fields
```

`3 passed in 0.92s`, exit 0.

## AUD-11-F9

Commit `e78dfc9b5d2c6cb995e1647a98f9b52c82b10972`.

- `test_compare_ignores_rotated_records_for_unchanged_values`: both task costs
  are `0.044` on provider `p1`. Record ids gain the `@reread` suffix.
  `changed` is false and `models` is empty.
- `test_compare_tracks_changed_collection_must_values`: the lab/a row is the
  only model change. `model.input_modalities` moves from `["text"]` to
  `["image"]`, each side keeps `lab/a#model.input_modalities`, `entered` is
  false, `left` is null, and `rank_changed` is null.

Red, with the listed mutant applied and then restored:

- compare02: `1 failed in 0.40s`, exit 1. `changed` was true.
- compare05: `1 failed in 0.54s`, exit 1. `models` was `[]`.

Green new tests: `2 passed in 0.50s`, exit 0.

The two focused commands above, rerun after these tests:

`97 passed, 1 skipped in 1.25s`, exit 0.
`3 passed in 1.13s`, exit 0.

## AUD-11-F11

Commit `0a7a6f5ee135fd5e497600f67f79d08299c14d18`.

- `test_why_not_counts_only_ranked_models`: lab/b has `ranked_models` 2 and
  summary `lab/b ranked #2 of 2 model(s). No single weight change puts it first.`
  The decision also contains eliminated lab/c and may-qualify lab/d.
- `test_why_not_keeps_relaxation_cost_for_unverified_governance_must`: the
  failed condition is `origin.lab_jurisdiction in {US}: eliminated: Lab jurisdiction not verified; unknown(list)`.
  `constraint_costs` is `(origin.lab_jurisdiction in {US}, admits 0)`.
- `test_why_not_does_not_extend_tie_to_outside_model`: `answer.members` is
  `["lab/a", "lab/b"]`. lab/c is rank 3 of 3. Its summary is
  `lab/c ranked #3 of 3 model(s). No single weight change puts it first.`

Red, with the listed mutant applied and then restored:

- whynot01: `1 failed in 0.47s`, exit 1. `ranked_models` was 4.
- whynot03: `1 failed in 0.47s`, exit 1. `constraint_costs` was empty.
- whynot04: `1 failed in 0.52s`, exit 1. The summary contained
  `tied for the answer`.

Green new tests: `3 passed in 0.54s`, exit 0.

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_by_model.py tests/test_decision_regions.py tests/test_lab_jurisdiction.py tests/test_decision_cli.py
```

`112 passed, 1 skipped in 5.44s`, exit 0.

## Not observed

No full local pytest suite. No site build. No Worker memory probe. No contract
edit, frozen-data edit, ranking-floor edit, legal-text edit, price edit, or
production-switch edit. CI was not checked in this file; the executor checks
the draft PR after push.
