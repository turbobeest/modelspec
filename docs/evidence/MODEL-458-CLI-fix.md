# MODEL-458-CLI execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Final implementation SHA: recorded below after the last implementation commit.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, Typer 0.27.2,
Git 2.50.1. Commands run from the assigned `model-458-cli` worktree.
All pytest runs use `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider`
as the prefix. Tests run serially with synthetic credentials and local origins.

## AUD-04-F6

The CLI redacts presented credentials in decoded response content and copied
header values. Unchanged successful JSON retains its original bytes.
The focused response-boundary regression selection recorded 9 failed and
1 passed before the change. The full `tests/test_cli_concierge.py` run recorded
169 passed after the change, exit 0. Detailed reproduction material is private.

## Limits of observation

No production request, provider call, deployment, package publication, release
tag or full local suite was run. No production switch, price, ranking floor,
legal text, frozen data or contract field range was changed. CI and independent
review are pending.

## AUD-04-F10

Setup review diffs show the parsed selected entry with credentials masked.
Native config content and exact original backups retain their intended bytes.
The focused setup-boundary regression selection recorded 14 failed and 2 passed
before the change. `tests/test_cli_concierge.py` recorded 185 passed after the
change, exit 0. Detailed reproduction material is private.

An additional AUD-04-F10 review check covers masking existing argument values.
It recorded 2 failed and 10 passed before the adjustment; the full concierge
file then recorded 188 passed, exit 0.

## AUD-04-F7

Saved credential files open without blocking before descriptor validation.
The existing no-follow, regular-file and permission checks remain in place.
The supplied subprocess reproduction exceeded its 3-second deadline before the
change, and its child was killed and reaped. The permanent
`test_fifo_credential_fails_promptly` test failed for the same deadline.

With the pytest prefix above, `tests/test_cli_concierge.py -k fifo_credential`
recorded `1 failed, 185 deselected`, exit 1. After the change,
`tests/test_cli_concierge.py` recorded `186 passed`, exit 0, including the
subprocess assertion for `auth_unreadable`, exit 5, and recovery steps.
Windows was not executed locally.
