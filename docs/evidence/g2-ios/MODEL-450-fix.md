# MODEL-450 round-five execution evidence

The conflict with public main #977 is resolved as a union. Both writer mirrors
and both sets of tests remain. The public merge is complete and tested, but the
cross-repository mirror check is blocked by an absent private lineup workflow.

Public PR: https://github.com/turbobeest/modelspec/pull/970.
Private companion: https://github.com/turbobeest/modelspec-data/pull/130.
No PR-state change or `gh` call was made.

Base: `bad0801861352e750bdbb81dd86ace0054c4165d`.
Merged main: `d55250c2e8fd5577639cd64afe2421332bc85b6e`.
Verified merge: `ab1bb931a91eb0b8403629578ba25cbec46745a7`.
Private branch after pull: `afc3a5b2fce504601af0a3537401c2edd2f231a8`.
The final evidence commit's SHA is in `.pr-commit.txt` and `.pr-body.md`;
this file cannot contain its own commit hash. Earlier evidence remains at the
base commit.

## Conflict and union verification

Commands ran from `/Users/terbeest/dev/worktrees/model-450`, except the
explicit private pull:

```bash
git fetch origin
git merge --no-edit origin/main -m 'Merge origin/main for MODEL-450 round 5' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git -C /Users/terbeest/dev/worktrees/data-model-450 pull --ff-only
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/r5-executor/verify-union.py
```

Fetch and private pull exited 0. The merge exited 1 with a content conflict in
`tests/test_writer_isolation.py`; `tests/test_engine_pin.py` merged
automatically. The union audit initially exited 1 on the conflict markers.

Resolution retained the branch's complete isolation file and inserted main's
lineup-proposer test verbatim. It preserved the shared JSON import once.
The pin registration from main and release-coverage pin cases both remain.

The same audit then exited 0. It parses both parents and the resolved files:
all 27 pin functions and 106 isolation functions, including helpers, retain
their original bodies and decorators. Both mirror files retain their parent
bytes, and lineup-proposer remains in the pin name/job registries. No new
behavioral test was needed for this merge; no existing assertion was changed.

## Tests

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_release_slo_handoff.py tests/test_coverage_slo.py tests/test_data_workflows.py tests/test_removed_sources.py > /tmp/model-450-scratch/r5-executor/focused.log 2>&1
git diff --cached --check
git commit -m 'Merge origin/main for MODEL-450 round 5 preserving both writer guards' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

All exited 0. The focused serial suite passed **598 tests, 1 skipped in
64.28s**. The skip is `test_a_built_dist_carries_no_removed_value`, which
requires `MODELSPEC_DIST`. No full local suite ran.
Tools: Python 3.14.4, pytest 9.1.1 and PyYAML 6.0.3.

After updating the evidence, the final documentation guard exited 0 with
**1 passed in 32.06s**:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > /tmp/model-450-scratch/r5-executor/final-doc-guard.log 2>&1
```

## Remaining mirror gate

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-450/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-450/.github/workflows
```

Exit 1, sole diagnostic:

```text
::error::lineup-proposer.yml: private workflow is missing
```

The requested private pull reported already up to date. The workflow is absent
from that branch and private `origin/main` at
`7409030687c87e1ed05b87b0c126ad0273b3dfb9`.
A read-only Git blob comparison confirms the incoming public mirror exactly
matches `origin/model-447-proposer` at
`db3ca54f6a6d2f1c5ce0dc28297cd9be1baf9775`.
The separate private proposal must reach the private branch before this gate
can pass. Its workflow was not fabricated, copied into MODEL-450, or omitted
from the public merge to hide the failure.

## Limits

No live workflow, CI result, deployment, artifact transfer, private issue write
or SLO attainment was observed. There were zero `gh` calls and no PR-state
changes. No private-worktree edit, pin change, Worker export change, vendor
call, source-page retention, Linear write, force push or merge to main occurred.
The approved SLO implementation is unchanged.
