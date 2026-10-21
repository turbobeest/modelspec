# MODEL-396 review fixes

Resumed on 2026-10-20 in `/Users/terbeest/dev/worktrees/model-396`, branch
`model-396-pdf-sources`, with a clean worktree.

- Resume base: `f18aee2e23ee46e582bc22251b482223e1117176`.
- Reviewed implementation: `3a2a59c02843e784e448730bceb2c9682fb8949b`.
- Merged `origin/main`: `d9ed66aea52395b440bd72a94a109c159d4ea4c2`.
- Merge commit: `4bef88dc40330598065fc85e6de2d2b423b5ed17`.
- Final implementation SHA: `49532524ee48a631f28de58343c37bfc229b9d35`.

The delivery commit adds this evidence. Its SHA is reported in
`CODEX_EXEC_DONE`; use `git rev-parse HEAD` on the delivered branch to reproduce
it. No rebase or force push was used.

## Changes

The resumed commit already contained the optional `verify` dependency group,
the missing-dependency message, drift reporting and the per-copy PDF detection
cache. Those changes were preserved. The remaining install defect was the
stale generated CLI bundle.

`pypdf==6.19.0` belongs only to `modelspec-dev[verify]`. Both pytest installation
steps in `.github/workflows/test.yml` request `[dev,verify]`, including the job
that collects the complete suite. The thin CLI's normal dependencies and the
Worker's dependencies do not include pypdf. Importing the PDF reader without
pypdf produces an error explaining how to install the extra.

An unapproved revision of a previously retained PDF reports every cited region
as `CHANGED`, requeues affected claims and raises the governance change alert
with the new bytes' hash. The old approved snapshot remains available; the
unapproved bytes are not retained. Both a valid changed PDF and a malformed
revision are covered.

PDF detection caches both positive and negative results by copy reference for
each `StoredRegions` instance. A new instance starts a fresh cache. Each copy
gets one `has`/`get` pair for detection in a run, shared across source IDs;
a declared PDF recipe needs neither call.

The parser's safety limits and production retention templates are unchanged.
Real-world PDFs, including Small 4's technical PDF, are still refused by the
structure limits. Its maximum-output fact needs a later engine PR and remains
unverified here.

## Red and green evidence

The resume started after the regression tests and their fixes had been
committed. The six regression cases were therefore replayed against the
reviewed pre-fix files, not claimed as newly written tests. The replay saved
the current bytes of four files, substituted their versions from `3a2a59c0`,
ran pytest, and restored every saved file in `finally`. No test was changed.

| Defect and test | Observed red output |
| --- | --- |
| Missing dependency: `test_pdf_missing_optional_dependency_explains_how_to_install` | Expected `install modelspec-dev[verify]`; got `unsupported content: pdf_invalid`. |
| Operator extra: `test_pdf_dependency_is_only_in_operator_extra` | `KeyError: 'verify'`. |
| Drift: `test_pdf_unapproved_revision_reports_drift_without_retaining_bytes`, two cases | `assert 0 == 2`, no region results for the revised PDF. |
| Repeated reads: `test_pdf_detection_reads_each_copy_once_per_run`, two cases | `assert 6 == 1`, six `get` calls in the first run. |
| Generated bundle: `test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources` | `AssertionError: pyproject.toml`; committed hash `aacf011b...` differed from actual `e55919d8...`. |

Replay command:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import os
from pathlib import Path
import subprocess
import sys

paths = [Path(p) for p in ('pyproject.toml', 'decision/pdf_sources.py', 'decision/sources.py', 'decision/verify.py')]
originals = {p: p.read_bytes() for p in paths}
try:
    for path in paths:
        path.write_bytes(subprocess.check_output(['git', 'show', f'3a2a59c0:{path}']))
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
         'tests/test_pdf_sources.py', '-k',
         'missing_optional_dependency or dependency_is_only or unapproved_revision or detection_reads'],
        env={**os.environ, 'PYTHONPATH': str(Path.cwd()), 'PYTHONDONTWRITEBYTECODE': '1'},
        capture_output=True, text=True,
    )
    print(result.stdout)
    print(result.stderr)
    print(f'REPLAY_RED_EXIT={result.returncode}')
finally:
    for path, content in originals.items():
        path.write_bytes(content)
assert result.returncode == 1
PY
```

Pytest exited `1`: `6 failed, 86 deselected in 2.50s`. The wrapper exited `0`
after asserting the expected failure and restoring the files.

The bundle test ran on the merged implementation before regeneration:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_copy.py::test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
```

The test exited `1`: `1 failed in 0.19s`. The generator check exited `1` with
`cli/modelspec/agent-bundle.json is stale`.

The fresh-venv install also reproduced the blocker before regeneration:

```sh
task_venv=$(mktemp -d /tmp/model-396-r2-venv.XXXXXX)
/Users/terbeest/dev/modelspec/.venv/bin/python -m venv "$task_venv"
"$task_venv/bin/python" -m pip install -e .
```

Venv creation exited `0`; installation exited `1`. The build hook raised
`ValueError: CLI guidance is stale. Run python -m pipeline.agent_copy write.`
The allocated path was `/tmp/model-396-r2-venv.D7lCSr`.

## Final verification

All pytest commands ran serially. Command exit codes were checked directly.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py tests/test_model_396_readers.py tests/test_worker_vendor_imports.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_sources.py tests/test_decision_verify.py tests/test_decision_model.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_kimi_plan_reader.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_copy.py tests/test_cli_wheel.py
/tmp/model-396-r2-venv.D7lCSr/bin/python -m pip install -e .
```

- Regeneration exited `0`. Only the `pyproject.toml` source hash changed in
  `cli/modelspec/agent-bundle.json`; all other generated artifacts were identical.
- Focused suite exited `0`: `126 passed in 6.23s`.
- Broader source, verification, model, retention and merged Kimi reader suite
  exited `0`: `651 passed in 45.35s`.
- Fresh-venv installation exited `0`: `Successfully built modelspec-dev`,
  `Successfully installed ... modelspec-dev-1.0.0`.
- Generator check exited `0` with no stale artifacts.
- Guidance and wheel-packaging suite exited `0`: `18 passed in 47.60s`.
  This includes the formerly failing source-hash test.

The three suites total 795 passing tests. Each of the six replayed regression
cases is included in the 126-test focused suite.

The installed client was then exercised without the optional PDF dependency:

```sh
/tmp/model-396-r2-venv.D7lCSr/bin/python - <<'PY'
from importlib.metadata import requires
from importlib.util import find_spec
import subprocess

assert find_spec('pypdf') is None
requirements = [item for item in requires('modelspec-dev') if item.startswith('pypdf')]
assert requirements == ["pypdf==6.19.0; extra == 'verify'"], requirements
result = subprocess.run(['/tmp/model-396-r2-venv.D7lCSr/bin/modelspec', '--help'], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert 'Usage:' in result.stdout
print('Thin CLI help passed without pypdf; wheel metadata restricts pypdf to the verify extra.')
PY
```

Exited `0` with the printed success message.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/pdf_sources.py decision/pdf_templates.py tests/test_pdf_sources.py
git diff --check
```

Both exited `0`; Ruff reported `All checks passed!`.

## Delivery commands

```sh
git fetch origin main
git merge --no-edit -m 'Merge origin/main into model-396-pdf-sources

Co-Authored-By: ChatGPT Codex <noreply@openai.com>' origin/main
git add cli/modelspec/agent-bundle.json
git commit -m 'MODEL-396: regenerate CLI bundle for optional PDF tooling' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git add docs/evidence/g2-ios/MODEL-396-r2-fix.md docs/evidence/g2-ios/MODEL-396-r2-pr-body.md
git commit -m 'MODEL-396: record review-fix regression and installation evidence' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin model-396-pdf-sources
```

The first GitHub CLI call read PR 862's title, body, draft status, branch and
URL: `gh pr view 862 --json title,body,isDraft,headRefName,url`.

The connected GitHub tool rejected the PR body update with HTTP `403`,
`Resource not accessible by integration`. The execution brief forbids
`gh pr edit`, so that command was not used. The existing body already states
that the Small 4 PDF exceeds the subset's object limit and maximum output
remains unverified. Updating the body with the new validation results and
explicit later-PR requirement remains blocked by the integration's permissions.
The prepared replacement is saved in
[`MODEL-396-r2-pr-body.md`](MODEL-396-r2-pr-body.md).

## Tools and limits of observation

Python 3.14.4, pytest 9.1.1, pypdf 6.19.0, Ruff 0.16.6, build 1.6.1,
pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7.
Git 2.50.1 and GitHub CLI 2.102.0. The shared Python environment has pip
26.2.1; the new venv started with pip 26.1.

No full local pytest run, site build, live deployment, vendor API call, new
provider fetch, real-world PDF acceptance, or private Worker memory rerun was
performed in this round. The previous evidence report contains the earlier
private memory measurements. This round's Worker import tests passed; that
does not establish a new memory measurement. CI and independent review remain
separate gates.
