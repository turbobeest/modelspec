# MODEL-456 verification

Base SHA: `37a91865beba12ed5f8cf1dd505a8526d0c9278c`.
Final implementation SHA: `84488b95b628c23f591baf2042798d3d4f38dede`.
The subsequent commit adds only this evidence. The final PR head SHA is recorded
in the untracked `.pr-commit.txt` hand-off and the executor's completion output.

The required test no longer compares wall-clock durations. It retains the
forbidden `decision.explain.explain` monkeypatch and `actual() == baseline()`.
The guard now accepts keyword arguments, matching the engine's `comparison=`
call and producing its intended assertion if that call regresses.

Commands ran from `/Users/terbeest/dev/worktrees/model-456` on 2026-11-08.
Versions: Python 3.14.4, pytest 9.1.1, Git 2.50.1, GitHub CLI 2.103.3.
Python, pytest and Git versions came from `--version`; the GitHub CLI version
came from `/opt/homebrew/bin/gh` pointing to `../Cellar/gh/2.103.3/bin/gh`.

## Red before editing

The existing test was the regression case. This command injected the ticket's
reported timings into its measurement boundary while leaving the engine and
test unchanged. It reproduced the timing failure deterministically; it was not
an observation of natural scheduler noise on this machine.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from unittest.mock import patch
import pytest

with patch('timeit.timeit', side_effect=[0.0324, 0.0379] * 15):
    code = pytest.main([
        '-q', '-p', 'no:cacheprovider',
        'tests/test_decision_explain.py::test_none_latency_is_within_noise_of_bypassed_explanation',
    ])
raise SystemExit(code)
PY
```

Exit 1, `1 failed in 0.53s`:

```text
E       assert 0.0379 <= (0.0324 * 1.15)
```

After editing, the same command with the node ID changed to
`test_none_bypasses_explanation_without_changing_decision` exited 0:
`1 passed in 0.81s`.

## Mutation rejected and reverted

The temporary `else` branch called the real explanation entry point for
`explain="none"`. Keeping the original guard text let the test compile its
bypassed baseline, so the failure came from the forbidden call assertion.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
import sys

path = Path('decision/engine.py')
original = path.read_bytes()
anchor = b'        if spec.explain == "full":\n            decision.by_model = build_by_model(decision, cost_of)\n'
mutation = b'''    else:
        from decision.explain import explain

        explain(
            decision, resolved, snapshot, filtered, ordered, selectors, domains,
            comparison=comparison,
        )
'''
assert original.count(anchor) == 1
try:
    path.write_bytes(original.replace(anchor, anchor + mutation, 1))
    result = subprocess.run([
        sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
        'tests/test_decision_explain.py::test_none_bypasses_explanation_without_changing_decision',
    ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, end='')
    assert result.returncode == 1, result.returncode
    assert 'AssertionError: none entered explanation code' in result.stdout
finally:
    path.write_bytes(original)
    assert path.read_bytes() == original
    print('Engine restored byte-for-byte.')
raise SystemExit(result.returncode)
PY
```

Exit 1, `1 failed in 0.71s`:

```text
E       AssertionError: none entered explanation code
Engine restored byte-for-byte.
```

`git diff --exit-code -- decision/engine.py` then exited 0.

## Repeated and serial checks

Each loop iteration launched a separate serial pytest process and checked its
return code directly. The subprocess pipes captured output; they did not mask
the test's exit code.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import subprocess
import sys

command = [
    sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
    'tests/test_decision_explain.py::test_none_bypasses_explanation_without_changing_decision',
]
passed = 0
failed = 0
for run in range(1, 51):
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode == 0:
        passed += 1
    else:
        failed += 1
        print(f'Run {run}: exit {result.returncode}\n{result.stdout}', flush=True)
    if run % 10 == 0:
        print(f'{run}/50 complete: {passed} passed, {failed} failed', flush=True)
print(f'PASS COUNT: {passed}/50; FAIL COUNT: {failed}/50', flush=True)
raise SystemExit(1 if failed else 0)
PY

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_explain.py

git add docs/evidence/g2-ios/MODEL-456-fix.md
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py

git diff --cached --check
git diff --exit-code -- decision/engine.py
```

Loop exit 0: `PASS COUNT: 50/50; FAIL COUNT: 0/50`.
Explanation file exit 0: `21 passed in 0.70s`.
Source guard exit 0: `46 passed, 1 skipped in 53.46s`. The skipped check
requires a built site via `MODELSPEC_DIST`; no site build was requested.
Both diff checks exited 0. The evidence was staged before the source guard so
its tracked-file scan included the new document.

## Limits

No latency claim is made. Natural shared-runner noise, remote CI results, the
full local suite, and site builds were not verified. The ticket reserves the
full suite for CI. No production code or data changed, and no provider calls
were made. No background service was started; every test subprocess completed.
