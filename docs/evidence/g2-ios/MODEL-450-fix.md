# MODEL-450 round-six execution evidence

Resolved the conflicts with public main #976 as a union. The release-coverage,
lineup-proposer and model-week mirrors remain, with all parent test bodies and
decorators preserved. No SLO behavior changed. All 14 mirrors match the assigned
private worktree after integrating the workflows now merged on private main.

Public PR: https://github.com/turbobeest/modelspec/pull/970.
Private companion: https://github.com/turbobeest/modelspec-data/pull/130.
Zero `gh` calls; no PR-state changes.

Public base: `9efcb5610732c1eac21a63e90bfab1beffdb8697`.
Incoming public main: `1de613b202258bf244a9427aafd722bcd71b7662`.
Verified public merge: `afc571aa23e008b85e2863146d3308114da28423`.
Private base after pull: `<private revision at assessment time>`.
Incoming private main: `<private revision at assessment time>`.
Verified private merge: `<private revision at assessment time>`.
The final public evidence commit SHA is recorded in `.pr-commit.txt` and
`.pr-body.md`; this file cannot contain its own commit hash. Earlier evidence
remains at the base commit.

## Conflict reproduction and resolution

Commands ran from `/Users/terbeest/dev/worktrees/model-450` unless `git -C`
specifies the private worktree:

```bash
git fetch origin
git merge --no-edit origin/main -m 'Merge origin/main for MODEL-450 round 6' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git -C /Users/terbeest/dev/worktrees/data-model-450 pull --ff-only
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/r6-executor/verify-union.py
```

Fetch and private pull exited 0. The public merge exited 1 with conflicts in
`tests/test_engine_pin.py` and `tests/test_writer_isolation.py`. The union audit
first exited 1 with `SyntaxError: invalid syntax` at `<<<<<<< HEAD`.

Resolution kept the branch's complete test files, added main's model-week pin
registration and copied its two new test functions with their decorators
verbatim. The same audit then exited 0. It parses both parents and the resolved
files, requires the union of function names, and compares every existing
function's AST with its parent, including decorators. All 28 pin-test/helper
functions and 107 isolation-test/helper functions passed. The three affected
mirror files retain their parent bytes. No assertion was weakened.

## Private dependency and mirror verification

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-450/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-450/.github/workflows
```

After the private pull, this exited 1 with exactly:

```text
::error::lineup-proposer.yml: private workflow is missing
::error::model-week.yml: private workflow is missing
```

Both workflows were now present on private `origin/main`. The assigned private
branch had not integrated that commit. Integrated it without conflict:

```bash
git -C /Users/terbeest/dev/worktrees/data-model-450 merge --no-edit origin/main -m 'Merge private main for MODEL-450 writer mirror verification' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

Exit 0. This adds only the seven files already merged on private main; it does
not rewrite existing data or change `.engine-pin`. Repeating the exact mirror
command exited 0 with `14 public writer mirror(s) match private workflows.`
The round-five missing-workflow blocker is resolved.

## Focused tests

Public worktree, serial run:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_release_slo_handoff.py tests/test_coverage_slo.py tests/test_data_workflows.py tests/test_removed_sources.py > /tmp/model-450-scratch/r6-executor/focused.log 2>&1
```

Exit 0: **605 passed, 1 skipped in 65.88s**. The skip is the built-site source
guard, which requires `MODELSPEC_DIST`.

Private worktree, serial run:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_writer_mirrors.py .github/scripts/tests/test_release_coverage_workflow.py .github/scripts/tests/test_model_week_workflow.py .github/scripts/tests/test_lineup_proposer.py > /tmp/model-450-scratch/r6-executor/private-focused.log 2>&1
```

Exit 0: **37 passed in 6.61s**.
`git diff --cached --check` in public and `git diff --check HEAD^ HEAD` in private
also exited 0. No unresolved paths remain.
Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Git 2.50.1.

After writing this evidence, the final documentation guard exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > /tmp/model-450-scratch/r6-executor/final-doc-guard.log 2>&1
```

Result: **1 passed in 31.94s**.

## Completion and limits

Public merge commit command:

```bash
git commit -m 'Merge origin/main for MODEL-450 round 6 preserving both writer guards' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

Exit 0. Both assigned branches are pushed with `CI_LOCAL_SKIP=1`, after their
focused tests. Final SHAs and the results are in the untracked handoffs.

No full local suite, CI result, live workflow, deployment, artifact transfer,
private issue write or SLO attainment was observed. No PR-state change, pin
change, Worker export change, vendor call, source-page retention, Linear write,
force push or merge to main occurred. The existing engine activation dependency
remains; this round verifies integration and does not activate the workflow.
