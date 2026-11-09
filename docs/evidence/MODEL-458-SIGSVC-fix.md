# MODEL-458-SIGSVC verification

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
The PR body and executor completion line record the final head SHA. Resolve it
from this checkout with `git rev-parse HEAD`.

## AUD-14-F6

Signal IDs retain their canonical payload after acknowledgement. Identical
payloads remain duplicates within the intake window; conflicting payloads
retain the existing conflict response. Acknowledgement also retains the
canonical payload for previously queued rows. Response shapes are unchanged.

The permanent regression is `test_replay_after_ack_is_still_duplicate` in
`tests/test_release_signals.py`, with four cases. Before the implementation
change, pytest reported `4 failed, 57 deselected`, exit 1. Afterward, it
reported `4 passed, 57 deselected`, exit 0. The isolated specification check
also changed from `1 failed, 27 deselected`, exit 1, to
`1 passed, 27 deselected`, exit 0. Detailed local fixtures and output are
excluded from this public evidence.

Commands, run from the assigned worktree:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_replay_after_ack_is_still_duplicate
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_watch.py
git diff --check
```

The focused suites reported `92 passed in 24.61s`, exit 0. Existing assertions
were preserved. The documentation clarification is in `docs/grok-bot-signals.md`.
The OpenAPI description remains unchanged because its generator is outside
the specified edit paths.

## Environment and limits

Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3,
cryptography 45.0.7, Node v22.22.3, git 2.50.1.

Verification used local service calls with an in-memory KV. Production HTTP,
distributed KV consistency and concurrent requests were not observed. No
production switch, secret, frozen data, ranking policy or legal text changed.
No deployment, paid-provider call or local full-suite run was performed.
