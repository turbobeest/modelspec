# MODEL-275-LINUX-P execution evidence

Base SHA: `d38f02f02067af4be58004d9956f0b89269c1d97`.
The head SHA is the commit that adds this file. The same SHA is in the draft PR body and the executor completion line.

Tool versions in this worktree: Python 3.14.4, pytest 9.1.1, git 2.50.1. `bash -n` used GNU bash 5.3.9. The offline run used `/bin/bash` 3.2.57 because the test PATH was `/usr/bin:/bin`. `/bin/zsh` is zsh 5.9. Commands: `/Users/terbeest/dev/modelspec/.venv/bin/python --version`, `/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version`, `git --version`, `/usr/bin/env bash --version`, `/bin/bash --version`, `/bin/zsh --version`.

## What changed

`qa/run-subscription-job.sh` had `#!/bin/zsh`. A Linux host that executes the file could not start it. The shebang is now `#!/usr/bin/env bash`. The body is unchanged: `set -euo pipefail`, the EXIT trap, `mktemp`, and `export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"`. Those Homebrew directories stay first. `/usr/bin` and `/bin` stay after them, so a host without Homebrew still resolves `git` and `mktemp`. `"$@"` is still passed to `python -m qa.subscription_jobs`.

`qa/README.md` says the wrapper runs under bash on macOS and Linux.

The launchd plists still start the file with `/bin/zsh`. That is the Mac schedule. The script body has no zsh-only syntax. Docker and login code were not changed.

No other `qa/*.sh` is referenced by the wrapper or by `qa/launchd/*.plist`.

## Red first

Command, exit 1:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subscription_report_out.py::test_subscription_job_shells_have_no_zsh_shebang tests/test_subscription_report_out.py::test_readme_says_the_subscription_wrapper_runs_under_bash tests/test_subscription_report_out.py::test_subscription_job_wrapper_forwards_args_offline tests/test_subscription_report_out.py::test_subscription_job_wrapper_under_zsh_forwards_the_same_args
```

`3 failed, 1 passed in 0.40s`.

- `test_subscription_job_shells_have_no_zsh_shebang` failed on `#!/bin/zsh`.
- `test_readme_says_the_subscription_wrapper_runs_under_bash` failed because the README did not say the wrapper runs under bash on macOS and Linux.
- `test_subscription_job_wrapper_forwards_args_offline` executed the file through its shebang. zsh ignored `BASH_ENV`, so the real `git` ran against a temporary directory that is not a repository. Exit 128. stderr: `fatal: not a git repository (or any of the parent directories): .git`. No fetch left the machine.
- `test_subscription_job_wrapper_under_zsh_forwards_the_same_args` passed. `/bin/zsh` with a git function and a fake `.venv/bin/python` already forwarded `--no-publish` and `--report-out` with a path that contains a space.

## Green

Same four selectors, exit 0: `4 passed in 0.30s`.

`bash -n qa/run-subscription-job.sh` exit 0. `zsh -n qa/run-subscription-job.sh` exit 0.

Focused file, exit 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subscription_report_out.py
```

`16 passed in 0.48s`. The same command on the final tree, after the test docstring, exited 0: `16 passed in 0.49s`. No `-n`. Exit codes were read directly.

The offline test runs a symlink of `qa/run-subscription-job.sh` from a temporary tree, with a fake `git` and a fake `.venv/bin/python`. It records three git calls, in order: `fetch -q origin main`, `worktree add -q --detach <job>/engine origin/main`, and the EXIT trap's `worktree remove --force <job>/engine`. The python argv is `-m qa.subscription_jobs --no-publish --report-out <dir with spaces>`. `PYTHONPATH` is the detached engine directory. The inherited `PATH` at the python call is `/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin`.

## Not observed

No live Linux run. No Ubuntu 24.04 host executed the wrapper. No vendor call, login, network fetch, or Docker run. No Linear write. No full local pytest suite. CI is the full gate. No workflow, legal text, ranking floor, price, or production switch was changed.
