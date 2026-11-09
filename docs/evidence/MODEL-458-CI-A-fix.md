# MODEL-458-CI-A verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Branch: `model-458-ci-a`.
The final commit SHA is recorded in the draft PR body after committing this file.

Environment: macOS 27.2 arm64, Python 3.14.4, pytest 9.1.1, Git 2.50.1,
PyYAML 6.0.3, pydantic 2.13.5. Commands ran from the assigned worktree.

## AUD-08-F1

Both required checks preserve filenames from NUL-delimited Git output.
Frozen-path classification and chart reader requirements apply consistently
to added, modified, deleted and renamed paths.

Regression tests: `test_collect_preserves_frozen_paths`,
`test_fixture_changes_preserve_paths`, and `test_card_changes_preserve_paths`.
Before the change, the new cases reported 24 failed and 12 passed, exit 1.
An additional filename preservation check reported 8 failed and 1 passed,
exit 1, before explicit output decoding was added.
After the change, the affected suites reported 80 passed in 16.50 seconds,
exit 0. Detailed local probe output is excluded from this public record.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_freeze_guard.py tests/test_chart_check_pr.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/f1-green-final
git diff --check
```

## Scope of observation

Tests use local fixtures and temporary repositories. No production request,
deployment, paid provider call, private data change or workflow edit was made.
The local full suite was not run; CI remains the full gate. No CI wall-time
improvement has been measured.
