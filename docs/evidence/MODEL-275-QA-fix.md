# MODEL-275-QA execution evidence

Base SHA: `1584e31aa54c6de77fc545ba8cd109e1b047014c` (`origin/main` at the start of this branch).
The submitted head SHA is the commit that adds this file. It is also in the PR body and the executor completion line.

Tool versions, checked in this worktree: Python 3.14.4, pytest 9.1.1, git 2.50.1, GitHub CLI 2.103.3.
Commands: `/Users/terbeest/dev/modelspec/.venv/bin/python --version`, `/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version`, `git --version`, `gh --version`.

## What changed

`qa.subscription_jobs` accepts `--no-publish` and `--report-out DIR` only as a pair. A live run still builds the fresh report worktree, runs the same `execute(tree)` path, copies the job report to `DIR/report.md` and the pull-request body to `DIR/body.md`, then removes the worktree. It does not run git add, commit, push, or `gh`. Directory mode is 0700 and the two files are 0600. A symlink or an existing non-empty directory is refused. A failure still retains the worktree and prints its path.

With neither flag, `main` still calls `publish`. `--dry-run` cannot be combined with the pair, so a dry run stays on its existing path.

AEO behavior was already: the engine file must name Gemini, and a run that does not select Gemini records `skipped (retired)`, marks the run partial, and writes no new `BASELINE`. `qa/README.md` had said the job refuses until the engine set changes. The README now matches the code. `qa/run-subscription-job.sh` already forwards `"$@"` and was not edited.

## Red first

Command, exit 1:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subscription_report_out.py
```

`9 failed, 2 passed in 0.51s`. The two passes were the shell-forward pin and the existing engine-file requirement. The flag tests exited via `SystemExit: 2` with `unrecognized arguments: --no-publish`. The README test failed while the file still contained `refuses until its engine set changes`.

## Green

Same command, exit 0: `12 passed in 0.35s` on the final tree.

Focused regression, exit 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subscription_jobs.py tests/test_subscription_report_out.py tests/test_aeo_visibility.py
```

`204 passed in 12.84s` before the report-path assertion was added. The final report-out run above includes that assertion. No `-n`. Exit codes were read directly.

`scripts/pytest_shards.py --summary` placed the new file in the ordinary estimated shards. Shards 5 to 8 stayed within one file of each other. `tests/shard_durations.json` was not edited.

## Not observed

No vendor call, login, network fetch, or `gh` call other than opening this draft PR. No Linear write. No full local pytest suite. CI is the full gate. No workflow, legal text, ranking floor, price, or production switch was changed. The private host was not run.
