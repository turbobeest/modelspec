# MODEL-448 public mirror evidence

## Round 2: union merge after the lineup mirror landed

Requested base: `f5f44f9a24aab0980bcea70c2fb639d97f3aa679`.
The remote ticket branch had already advanced to
`8c4c5824efbba379ebc22aade41d62b40b07508d`; fast-forwarding preserved those
intervening changes. Merged public main
`d55250c2e8fd5577639cd64afe2421332bc85b6e`, including the lineup mirror.
Final merge implementation SHA: `aefaeb1c5e456a26507f7e5ec9bae6769413964a`.
The final pushed SHA including this evidence update is in `.pr-commit.txt`.

Read `REV-976.verdict.md`: APPROVE, no defects, reviewing the original public
and private heads. This round changes only the integration with newer main.

Commands from `/Users/terbeest/dev/worktrees/model-448`, unless noted:

```sh
git fetch origin
git merge --ff-only origin/model-448-mirror
git -C /Users/terbeest/dev/worktrees/data-model-448 pull --ff-only
git merge --no-commit origin/main
```

The first three exited 0; private pull reported `Already up to date.`
The merge exited 1 with conflicts in `tests/test_engine_pin.py` and
`tests/test_writer_isolation.py`.

Before resolving the conflicts:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_model_week.py
```

Exit 2: `2 errors in 0.17s`. Both conflicting files failed pytest collection
with `SyntaxError` from the conflict markers. No new behavior was introduced,
so the regression check is the existing suite across the actual union merge.

Resolution retains both `model-week` and `lineup-proposer` in `NAMES` and
`ENGINE_JOBS`, and both complete isolation test functions. All functions and
classes in the three requested test files were compared as Python ASTs with
both parents: the resulting name set is their union, and every parent node
is unchanged. Both workflow files match their corresponding parent bytes.
The same pytest command then exited 0: `358 passed in 16.58s`.

Source guard after staging this evidence:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: `46 passed, 1 skipped in 51.50s`. The skipped built-site check
requires `MODELSPEC_DIST`; this merge does not build or change a site export.

Actual private-worktree mirror check:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -I /Users/terbeest/dev/worktrees/data-model-448/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-448/.github/workflows
```

Exit 1: `::error::lineup-proposer.yml: private workflow is missing`.
The pulled private ticket branch is still
`82a2a61ee05c01870e46e807ccbc16173ce350b9`; its fetched main is
`7409030687c87e1ed05b87b0c126ad0273b3dfb9`. Neither contains the lineup
workflow. The incoming public lineup mirror matches
`origin/model-447-proposer:.github/workflows/lineup-proposer.yml` in the
private repository byte-for-byte. That separate workflow has not reached the
designated private worktree. No private workflow was added, removed or edited
in this round. This dependency blocks a successful all-writer mirror check.

`git diff --check` and `git diff --cached --check` exited 0. The merge was
committed with the required co-author trailer. Push uses
`CI_LOCAL_SKIP=1 git push -u origin model-448-mirror` after focused checks.
Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Git 2.50.1, Bash 5.3.9.
Zero `gh` calls. No PR state change, hosted CI check, live dispatch, full suite,
site build, provider call or Worker export was performed. Temporary logs were
removed; no background processes remain.

## Round 1 evidence

Public base: `468dd44ceb8600f661479f2f595dac617aff312b`.
Final implementation SHA: `2926cd377dc98fc1b36ed75002c8828c946290b3`.
The final pushed SHA, including this evidence-only commit, is in the untracked
`.pr-commit.txt` hand-off and can be read with `git rev-parse HEAD`.

This adds the byte-identical Model Week workflow under `.github/private-writers/`
and extends engine-pin and isolation checks. It does not change the generator
or add a public Actions workflow. The private companion PR owns execution.

Before copying the mirror, this command exited 1 with `2 failed in 0.15s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider 'tests/test_engine_pin.py::test_the_pin_is_verified_before_the_engine_checkout[model-week]' tests/test_writer_isolation.py::test_model_week_imports_only_the_engine_with_private_history_as_input
```

Both tests failed because `model-week.yml` was absent. Both pass in the final
focused run. Additional tests execute the history-completion shell against
shallow, full and unreachable fixture repositories and verify pinned HEAD stays
unchanged. The isolation test executes the generator command with hostile
private code and `PYTHONPATH` and proves only the engine module is imported.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Git 2.50.1,
Bash 5.3.9, actionlint 1.7.12, ShellCheck 0.11.0, GitHub CLI 2.102.0.
All pytest runs used the specified interpreter, ran serially, and had their
exit codes checked directly. No full local suite was run.

From the data worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_model_week_workflow.py .github/scripts/tests/test_writer_mirrors.py
```

Exit 0: `27 passed in 0.94s`. Covers Monday/manual scheduling, one fixed draft
branch, no merge command, exact generator flags, error propagation, ISO year
boundaries, invalid inputs, repeated staging and working appendix links.

From the public mirror worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_model_week.py tests/test_removed_sources.py
```

Exit 0: `400 passed, 1 skipped in 70.95s`. Covers main ancestry, canonical
pin checks, complete history without moving engine HEAD, import isolation
against hostile private files, and the unchanged generator's privacy checks.

After staging the new public mirror:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: `46 passed, 1 skipped in 52.93s`. The skip needs `MODELSPEC_DIST`;
this workflow change does not build or change a site export.

From the data worktree:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-448/.github/private-writers --workflows .github/workflows
actionlint .github/workflows/model-week.yml
git diff --check
```

Each exits 0. Mirror check: `12 public writer mirror(s) match private workflows.`
The public mirror is byte-identical, including the canonical pin verification,
checkout and confirmation steps. The checker identifies this workflow as a
writer because it checks out `turbobeest/modelspec` into `engine`.

The private scratch run for `2026-W44` produced the digest and preserved its
appendices using engine pin `6815544116839f991c10904772e7357f12d5b566`.
Detailed reproduction is in the private companion PR's evidence file. No
private report content is included here. Scratch checkouts were deleted.

No live dispatch, hosted CI or scheduled PR update was observed. No full local
suite, site build, provider call, source fetch or Worker export was run.
Human merges must coordinate this mirror with the private workflow because
private recall compares against public main. Both PRs remain drafts.


## Round 3: install the pinned engine dependencies

Public base: `1de613b202258bf244a9427aafd722bcd71b7662`.
Final public implementation SHA: `d2570968e7b0259001086746b7fdc9617ddcd134`.
Private base: `b2f7176b13bc4c7186f9b36f66f0e644df65dcb6`.
Final private implementation SHA: `27625a7dbb8e4ea152f5bf712aa828ff0ed69c4b`.
The final pushed revisions including evidence are recorded in each worktree's
untracked `.pr-commit.txt` hand-off.

The first live run reported an import failure because Model Week installed
only PyYAML. Importing `decision.excluded` executes `decision/__init__.py`,
which imports `decision.contract` and requires pydantic. The existing developer
venv already contained it. The fix copies admission-drafter's exact
`Install the pinned engine` step, `python -I -m pip install -e
"$GITHUB_WORKSPACE/engine[dev]"`. Both use Python 3.11 without a shared cache.
The pin verification, checkout, confirmation and generator commands stay intact.

### Regression results

From the public worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py -k 'dependencies or dependency_guard'
```

Before changing the workflow, exit 1: `1 failed, 20 passed, 264 deselected in
0.21s`. `test_model_week_installs_the_same_engine_dependencies_as_admission`
failed with `AssertionError: Model Week must install the pinned engine's
dependencies`. After the two-line workflow change, exit 0: `21 passed, 264
deselected in 0.20s`.

The all-writer guard checks each job separately and rejects a missing, late,
conditional, comment-only, failure-tolerant, other-job or superseded install.
The Model Week parity test also checks dependency completeness against the
admission step; ordering alone would accept the old PyYAML-only install.

Three inline-import cases were added before tightening the guard. The command
below initially exited 1, `3 failed in 0.13s`, because the guard returned `[]`
instead of `draft: Inline engine runs before dependencies`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py::test_dependency_guard_requires_installs_for_inline_engine_imports
```

The guard now checks engine references in stdin programs and `-c` commands.
The final targeted command above using `-k` exited 0: `24 passed, 264 deselected
in 0.20s`.

Focused public checks, exit 0, `382 passed in 17.57s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_model_week.py
```

Focused private checks from the data worktree, exit 0, `50 passed in 6.96s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_model_week_workflow.py .github/scripts/tests/test_writer_mirrors.py .github/scripts/tests/test_admission_drafter_workflow.py
```

Source guard after staging this evidence:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: `46 passed, 1 skipped in 51.76s`. The skip requires a built site
export through `MODELSPEC_DIST`; no export changed in this round.

From the public worktree, both commands exited 0:

```sh
cmp .github/private-writers/model-week.yml /Users/terbeest/dev/worktrees/data-model-448-deps/.github/workflows/model-week.yml
/Users/terbeest/dev/modelspec/.venv/bin/python -I /Users/terbeest/dev/worktrees/data-model-448-deps/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-448-deps/.github/workflows
```

Output: `13 public writer mirror(s) match private workflows.`
From the data worktree, `actionlint .github/workflows/model-week.yml` exited 0.
`git diff --check` exited 0 in both worktrees.

### Clean Python 3.11 reproduction

Setup commands, all exit 0:

```sh
/Users/terbeest/.local/bin/python3.11 -m venv /tmp/m448venv
/tmp/m448venv/bin/python -I -m pip install 'PyYAML>=6.0'
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-448-scratch/r3-repro/data
git clone --quiet https://github.com/turbobeest/modelspec.git /tmp/model-448-scratch/r3-repro/engine
git -C /tmp/model-448-scratch/r3-repro/data checkout --quiet --detach b2f7176b13bc4c7186f9b36f66f0e644df65dcb6
git -C /tmp/model-448-scratch/r3-repro/engine checkout --quiet --detach d7d5082b9ead230782f58533224ac901b55d4e81
```

The same driver ran before and after the dependency fix:
`/tmp/m448venv/bin/python -I /tmp/model-448-scratch/r3-repro/run_step.py`.
To reproduce that driver:

```python
import os
from pathlib import Path
import subprocess
import sys
import yaml

root = Path('/tmp/model-448-scratch/r3-repro')
data = root / 'data'
workflow = yaml.load((data / '.github/workflows/model-week.yml').read_text(), Loader=yaml.BaseLoader)
step = next(step for step in workflow['jobs']['draft']['steps'] if step.get('name') == 'Draft Model Week')
env = {**os.environ, 'PATH': '/tmp/m448venv/bin:' + os.environ['PATH'],
       'GITHUB_WORKSPACE': str(root), 'RUNNER_TEMP': str(root / 'runner'),
       'MONDAY': '2026-10-26'}
result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', step['run']], cwd=data, env=env)
print(f'Draft Model Week: exit {result.returncode}', flush=True)
sys.exit(result.returncode)
```

Red: exit 1, `ModuleNotFoundError: No module named 'pydantic'`, through
`scripts/model_week.py:19`, `decision/__init__.py:7`, `decision/contract.py:27`.
From the scratch data directory, installed the exact admission command:

```sh
env GITHUB_WORKSPACE=/tmp/model-448-scratch/r3-repro PATH="/tmp/m448venv/bin:$PATH" bash -e -o pipefail -c 'python -I -m pip install -e "$GITHUB_WORKSPACE/engine[dev]"'
```

Install exit 0. The unchanged driver then exited 0. Verified all four generated
files, their date bounds and section labels, then executed the actual
`Stage the weekly digest` block with `ISO_WEEK=2026-W44`. Staging exited 0 and
produced a 5,632-byte digest with valid links and byte-identical appendices.
The engine remained clean at the pin. No private report content entered either
branch. The private scratch clone and clean venv were removed after verification.

Tools: reproduction Python 3.11.15, pip 24.0, PyYAML 6.0.3, pydantic 2.14.2,
modelspec-dev 1.0.0; tests Python 3.14.4, pytest 9.1.1; Git 2.50.1,
Bash 5.3.9, actionlint 1.7.12.

Both PRs are drafts. Merge the public mirror/test PR first, then the private
workflow PR. No live dispatch, hosted CI, full local suite, site build, source
fetch or provider call was performed in this round. No Worker export changed.
