# MODEL-447 verification

Public base: `6815544116839f991c10904772e7357f12d5b566`.
Verified public implementation: `a10e3a7a9e084e2f2405063549b7e0bd4919bb1d`.
Data base: `c26a2d7b67039dd0ed2490cd740766680c9e454d`.
Verified data implementation: `183927ac8617b8ca894ca85cf29b1137545cfc79`.
The final PR heads, including evidence-only commits, are recorded in each
worktree's untracked `.pr-commit.txt` handoff.

Python 3.14.4; pytest 9.1.1; Ruff 0.16.6; Git 2.50.1; GitHub CLI 2.102.0.
The data workflow installs Python 3.11. No Node tooling was used.

## Observed failures and fixes

All pytest commands used the repository virtualenv, `env PYTHONPATH=$PWD`,
`-q -p no:cacheprovider`, and serial execution. Logs are under
`/tmp/model-447-scratch/executor/` or `data-workflow/`.

| Test | Red output, exit 1 | Green behavior |
| --- | --- | --- |
| `test_live_cli_proposes_recent_lab_release_with_clause_2_and_noop` | CLI returned 2, unrecognized `--data-dir`, `--as-of`, `--output`, `--diff` | Recent lab release enters through clause 2; repeating against computed baseline has no membership change |
| `test_recent_release_qualifies_through_a_retired_labs_past_year_leader` | `[] != ['lab/new-release']` | Retired models leave the set but their past-year results still qualify the lab |
| `test_live_cli_cannot_overwrite_the_reviewed_input[--diff]` | CLI returned 0 instead of 2 | Both output destinations reject the reviewed baseline path |
| `test_unregistered_offering_tier_cannot_block_other_admission_clauses` | `SnapshotBuildError`, unregistered `Tier0` | Invalid offering identities are excluded from provider and price clauses; other model clauses still compute |
| `test_budget_clause_does_not_add_the_frontier_one_year_cutoff` | `[] != ['lab/budget-model']` | Clause 5 retains the existing admitted-evidence rule without adding clause 1's age cutoff |
| `test_live_vision_domain_keeps_the_existing_vision_quota` | `frontier-generation != vision` | Current `vision_documents` evidence uses the existing vision balance |
| Data workflow/helper tests | Initially 2 failed, 4 errors, absent files | Fixed branch, clause body, verified engine pin, draft creation and updates |
| Data no-op reconciliation tests | 2 failed, 4 passed | No-op leaves YAML untouched and lets the PR action retire a stale proposal |

The first CLI fixture used an unregistered model type. Changing it to the
registered `llm-chat` type corrected the fixture; the expected admission did
not change. No existing tests were weakened.

## Commands and results

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_premier_live.py tests/test_premier_slice1.py tests/test_premier_missing_cards.py tests/test_removed_sources.py
/Users/terbeest/dev/modelspec/.venv/bin/ruff check scripts/premier_slice1.py scripts/premier_live.py tests/test_premier_live.py
git diff --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 6815544116839f991c10904772e7357f12d5b566 --head HEAD --branch model-447-codex
```

119 passed, 1 skipped in 113.63s, exit 0. The skipped test needs a built
`dist/`. Ruff and `git diff --check` exited 0; the freeze guard printed
`data freeze: ok`, exit 0. The new live suite alone passed all 17 tests.

From the data worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_lineup_proposer.py .github/scripts/tests/test_admission_drafter_workflow.py .github/scripts/tests/test_data_test_workflow.py .github/scripts/tests/test_linked_data_guard.py
```

51 passed in 3.69s, exit 0. `git diff --check` exited 0. The data repository has
no automerge workflow at its base. The new workflow contains no merge action,
uses `data/lineup-proposal`, and keeps creation and updates in draft.
No diff creates no PR; the PR action also reconciles an existing proposal whose
diff disappeared. See the action's
[documented behavior](https://github.com/peter-evans/create-pull-request/blob/v7/README.md#action-behaviour).

Frozen output was serialized before editing with `_dump(build())` and compared
byte-for-byte after editing, using Python assertions. Exit 0; 50,534 bytes;
SHA-256 `bb2106ce061775d75eb529b16c8e054fc40a301abae9573259f576c0bac72c1e`.
The checked-in frozen YAML and all frozen data paths remain unchanged.

## Historical replay

The private clone was created with:

```sh
git clone https://github.com/turbobeest/modelspec-data.git /tmp/model-447-scratch/private
```

The runner `/tmp/model-447-scratch/executor/replay.py` invoked the live CLI at
both parents and both merge commits, then invoked the data helper. Exact
revision/date pairs:

| Run | Private revision | Evaluation date |
| --- | --- | --- |
| Admission parent | `e562ba68cdc6306e25f4c010b2ec727c6cb189a7` | 2026-10-04 |
| Admission merge | `7aa56b8f198f0043c8fb806c0fd2def35ccc562a` | 2026-10-04 |
| No-op parent | `081c6bcb5546e13308754bf5f6ff2bf29f8e447e` | 2026-10-10 |
| No-op merge | `603f06abe7c124eb0320924ede400d81b6ae6c91` | 2026-10-10 |

For each row the runner executed `git -C /tmp/model-447-scratch/private
checkout --detach REVISION`, followed by:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/premier_slice1.py --data-dir /tmp/model-447-scratch/private --as-of DATE --output /tmp/model-447-scratch/executor/LABEL.yaml --diff /tmp/model-447-scratch/executor/LABEL.json
```

The CLI JSON compares against the historical reviewed `premier/slice-1.yaml`.
To isolate each merge, the runner also called `membership_diff(after, before)`
on its two computed YAML documents. It wrote that JSON to `LABEL-delta.json`
and a copy of the computed parent YAML to `LABEL-target.yaml`, outside the
clone. It then invoked the same helper used in the workflow:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-447/.github/scripts/lineup_proposal.py --proposal /tmp/model-447-scratch/executor/LABEL.yaml --diff /tmp/model-447-scratch/executor/LABEL-delta.json --target /tmp/model-447-scratch/executor/LABEL-target.yaml --body /tmp/model-447-scratch/executor/LABEL-body.md
```

All four CLI invocations and both helper invocations exited 0. The admission
merge adds exactly `openai/gpt-6-1-sol` relative to its computed parent, removes
nothing, and emits clause 2 with release date 2026-09-29 and lab `openai`.
The helper prints `changed=true` and its body names the model and clause 2.
The direct comparison against the historical reviewed YAML also proposes Sol;
it contains 1 addition and 7 removals from recomputing the older frozen list.

`git diff --name-only 603f06a^ 603f06a` prints only `.engine-pin`.
The no-op replay emits `{"added": [], "removed": [], "changed": false}`.
The helper prints `changed=false`, writes the no-op body, and leaves the
scratch baseline bytes unchanged. This establishes local proposal/no-proposal
behavior; the action's GitHub lifecycle was not executed.

A final current-main smoke run at private commit
`c26a2d7b67039dd0ed2490cd740766680c9e454d` used the same CLI with
`--as-of 2026-11-04 --output /tmp/model-447-scratch/executor/current.yaml
--diff /tmp/model-447-scratch/executor/current.json`. It exited 0 and selected
36 models. The excluded-source tracked-file guard was rerun after staging
this evidence and passed, exit 0.

## Limits

No Actions run, actual automated proposal creation/update/closure, full pytest
suite, or site build was observed. CI supplies the full gate. No production
switches, ranking floors, legal terms, public exports, rank rows or snapshot
fields changed, so the private Worker memory-probe condition did not apply.
No source fetch, paid provider call, Linear write, merge, force-push, or real
signing key was used. The temporary private clone is removed after replay.
Only code, synthetic tests and this verification record enter the public PR.
