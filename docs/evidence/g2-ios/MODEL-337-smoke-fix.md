# MODEL-337-smoke execution evidence

The installed 1.0.0 wheel worked as designed. The package smoke mock still
expected the original Spec, so it rejected the bounded `fields` that MODEL-337
adds when the caller omits them. `CliRunner` captured that assertion and returned
exit 1 with empty output. The outer smoke assertion then failed at
`scripts/package_smoke.py:47`.

Observed on 2026-10-13 in `/Users/terbeest/dev/worktrees/model-337`, on
`sparksandsawdust/model-337-bounded-cli`. PR #717 remains a draft.

- Base SHA: `515bb0bbebaa477245a6b4a280bb2930dd26818a`.
- Merged `origin/main`: `faed1e6a9d5cb6461c214c2d195e650b2fe1c486`.
- Merge SHA: `86d4bbe584f0459878f94cb35d5f924ee4588ad3`.
- Final tested code SHA: `80fde7a77967eafdd114b94763cc518b5e1111f2`.
- The final branch SHA includes this evidence-only commit. Resolve it with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-337-smoke-fix.md`;
  the PR comment records that SHA literally.

The merge conflicted only in `cli/modelspec/agent-bundle.json`. Regenerating
the bundle retained package version 1.0.0 and incorporated main's source
hashes. No other generated artifact changed. An early validation ran before
the generator finished and reported 3 failures and 13 passes from conflict
markers. After generation completed, the same suite passed all 16 tests.

The fix changes the smoke script and adds
`test_package_smoke_runs_against_the_current_cli` to the source suite. The
mock checks exact request bodies for the bounded default, explicit null, and
an explicit field list. It still checks the host, Authorization, endpoint,
offline guidance, missing-key refusal, request count, and unchanged response
bytes. Smoke failures now include the captured exception and request case.
The source regression restores the transport, environment, and working
directory through pytest's monkeypatch fixture.

The red-first test ran before the smoke script changed:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pypi_packaging.py::test_package_smoke_runs_against_the_current_cli
```

It exited 1 with this output:

```text
scripts/package_smoke.py:47: AssertionError
FAILED tests/test_pypi_packaging.py::test_package_smoke_runs_against_the_current_cli
1 failed in 0.40s
```

After the fix, the same command exited 0:

```text
1 passed in 0.16s
```

The independent log reader fetched the full original job log with:

```sh
gh run view --job 115458252791 -R turbobeest/modelspec --log
gh pr view 717 -R turbobeest/modelspec --json number,title,isDraft,state,headRefName,headRefOid,mergeStateStatus,statusCheckRollup,url
```

CI built and installed `modelspec_dev-1.0.0-py3-none-any.whl`, passed its wheel
content assertions, and passed the direct help and guidance commands before
the mocked `decide --spec ... --json` invocation failed.

These local commands built the sdist and then the wheel from that sdist,
inspected its contents, and installed it in a fresh Python 3.11 environment:

```sh
git fetch origin main
git merge origin/main -m 'Merge origin/main for MODEL-337-smoke

Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py

mkdir -p .scratch/model-337-smoke/executor
/Users/terbeest/.local/bin/python3.11 -m venv .scratch/model-337-smoke/executor/build-venv
.scratch/model-337-smoke/executor/build-venv/bin/python -m pip install build
.scratch/model-337-smoke/executor/build-venv/bin/python -m build --outdir .scratch/model-337-smoke/executor/dist
.scratch/model-337-smoke/executor/build-venv/bin/python - <<'PY'
from pathlib import Path
import zipfile
wheel = next(Path('.scratch/model-337-smoke/executor/dist').glob('*.whl'))
names = zipfile.ZipFile(wheel).namelist()
roots = {name.split('/', 1)[0] for name in names}
assert 'cli' in roots
assert not ({'api', 'decision', 'pipeline', 'registry', 'schema', 'models', 'tests', 'web'} & roots)
assert 'cli/modelspec/agent-bundle.json' in names
assert not any(name.endswith(('/offline.py', '/snapshot.py', '/legacy.py')) for name in names)
print('Workflow wheel-content assertions passed.')
PY
/Users/terbeest/.local/bin/python3.11 -m venv .scratch/model-337-smoke/executor/wheel-venv
.scratch/model-337-smoke/executor/wheel-venv/bin/python -m pip install .scratch/model-337-smoke/executor/dist/modelspec_dev-1.0.0-py3-none-any.whl
```

Build, inspection, and installation each exited 0. CI uses an unrelated
temporary directory. The local runtime directory was isolated beneath the
authorized worktree, with `PYTHONPATH` unset. The imported package path contained
`wheel-venv/lib/python3.11/site-packages/cli/modelspec/__init__.py`, and the
repository root was absent from `sys.path`. No editable package was installed
in that environment.

The workflow's runtime commands ran with these settings, both before and
after the smoke fix:

```sh
set -e
repo_root="$PWD"
venv="$PWD/.scratch/model-337-smoke/executor/wheel-venv"
mkdir -p .scratch/model-337-smoke/executor/isolated-cwd
cd .scratch/model-337-smoke/executor/isolated-cwd
unset PYTHONPATH
export PATH="$venv/bin:$PATH"
export XDG_CONFIG_HOME="$repo_root/.scratch/model-337-smoke/executor/isolated-config"
export MODELSPEC_API_KEY=""
modelspec --help > modelspec-help.txt
modelspec decide --help > modelspec-decide-help.txt
modelspec help agent --json > modelspec-agent.json
modelspec key --json > modelspec-key.json
"$venv/bin/python" "$repo_root/scripts/package_smoke.py"
```

This probe ran from that isolated runtime directory and exited 0:

```sh
"$venv/bin/python" - <<'PY'
import importlib.metadata
import sys
import cli.modelspec
from pathlib import Path
root = Path('/Users/terbeest/dev/worktrees/model-337')
module = Path(cli.modelspec.__file__).resolve()
assert 'site-packages' in module.parts
assert str(root) not in sys.path
assert importlib.metadata.version('modelspec-dev') == '1.0.0'
print('Installed imports verified:', module)
for name in ('httpx', 'typer', 'click', 'jsonschema', 'rich'):
    print(name, importlib.metadata.version(name))
PY
```

Every direct command exited 0. The unchanged smoke script exited 1 at line
47. This diagnostic command also replayed the pre-fix smoke script against
the same installed wheel. It exited 1 and exposed the captured assertion:

```sh
git show 86d4bbe5:scripts/package_smoke.py > .scratch/model-337-smoke/executor/red-package-smoke.py
cd .scratch/model-337-smoke/executor/isolated-cwd
env -u PYTHONPATH /Users/terbeest/dev/worktrees/model-337/.scratch/model-337-smoke/executor/wheel-venv/bin/python - ../red-package-smoke.py <<'PY'
import json
import runpy
import sys
from typer.testing import CliRunner

invoke = CliRunner.invoke

def report_failure(self, *args, **kwargs):
    result = invoke(self, *args, **kwargs)
    if result.exit_code == 1:
        print('Failing args:', args[1])
        print('Exit:', result.exit_code, 'exception:', repr(result.exception))
        tb = result.exception.__traceback__
        while tb:
            if tb.tb_frame.f_code.co_name == 'hosted':
                print('Expected request:', tb.tb_frame.f_locals['spec'])
                print('Actual request:', json.loads(tb.tb_frame.f_locals['request'].content))
            tb = tb.tb_next
    return result

CliRunner.invoke = report_failure
runpy.run_path(sys.argv[1], run_name='__main__')
PY
```

The diagnostic reported these bodies:

```json
{"expected":{"spec_version":1,"optimize":{"min":"offering.cost_per_task"}},"actual":{"spec_version":1,"optimize":{"min":"offering.cost_per_task"},"fields":["model_rank","cost_per_task","estimates","p_best","contributions","evidence"]}}
```

The same installed wheel passed with the corrected script, which exited 0:

```text
Installed wheel: offline guidance, key gate, bounded default, explicit fields and hosted response verified.
```

Validation commands ran from the worktree unless shown otherwise. Commands
that captured logs saved the command's `$?` immediately and returned that
code after printing the log. No test status came from a pipe.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pypi_packaging.py tests/test_cli_concierge.py tests/test_cli_wheel.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/package_smoke.py tests/test_pypi_packaging.py
git diff --check
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci)
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-337 npm run build)
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile -m 'not perf'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:xdist -m perf
```

| Validation | Result | Exit |
| --- | --- | --- |
| Generated guidance after merge | 16 passed | 0 |
| Focused packaging and CLI suites | 166 passed | 0 |
| Ruff on touched files | All checks passed | 0 |
| Diff whitespace | Passed | 0 |
| Web dependency installation | Completed | 0 |
| Web build | Completed | 0 |
| Web unit tests | 813 passed, 1 test file skipped | 0 |
| Full non-performance Python suite | 10,356 passed, 8 skipped, 11 warnings in 1118.73 s | 0 |
| Serial performance Python suite | 2 passed, 10,364 deselected in 54.12 s | 0 |

Ruff initially reported one existing 101-character line in the touched
packaging test file. Wrapping that line made the file pass without changing
its behavior. Independent review of the fix found no actionable issues.

Tool versions were Python 3.11.15 for the wheel build and installation,
Python 3.14.4 for source tests, build 1.6.1, hatchling 1.32.4, pytest 9.1.1,
pytest-xdist 3.8.0, ruff 0.16.6, Node 22.22.3, npm 10.9.8, Git 2.50.1, and
GitHub CLI 2.102.0. The installed wheel used HTTPX 0.28.1, Typer 0.27.3,
Click 8.5.0, jsonschema 4.26.0, and Rich 15.0.0. Original CI used Python
3.11.17; the local Python patch version differs.

No live hosted API response or paid provider call was observed. Hosted HTTP
was mocked with a synthetic key. The observation covers package installation,
offline guidance, local key refusal, request bodies, and response passthrough.
It does not establish live service behavior. The smoke fix changes no production
switch. No package was published, and no PR merge or Linear write was performed.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
