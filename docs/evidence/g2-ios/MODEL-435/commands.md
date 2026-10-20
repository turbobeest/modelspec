# MODEL-435 reproduction commands

All engine commands run from `/Users/terbeest/dev/worktrees/model-435`.
Private output paths must remain outside the public checkout. The aggregate
summary contains no fact values, source text or complete private records.

## Existing private inputs

```bash
git clone --single-branch --branch model-430-admit-haiku-5-5 \
  https://github.com/turbobeest/modelspec-data.git \
  /tmp/model-435-scratch/modelspec-data
git -C /tmp/model-435-scratch/modelspec-data rev-parse HEAD
```

The checked branch head was
`c62ce1e1b85dc3468d1e80e0b638e0cc25b3064e`. Pin that revision when repeating
the audit. The branch can move after this report.

These read-only GitHub commands looked for already retained source bytes:

```bash
gh run list -R turbobeest/modelspec-data --workflow rendered-reread.yml \
  --limit 3 --json databaseId,headSha,conclusion,createdAt
gh run download 39213106225 -R turbobeest/modelspec-data \
  --name rendered-reread-copies \
  --dir /tmp/model-435-scratch/retained-copies
gh run list -R turbobeest/modelspec-data --limit 30 \
  --json databaseId,workflowName,conclusion,createdAt
```

All three exited 0. The downloaded artifact contained 12 existing bodies,
none matching the required Anthropic sources. No additional artifact was
downloaded and no publisher page was requested.

## Offline audit

Baseline:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  docs/evidence/g2-ios/MODEL-435/audit.py \
  --data /tmp/model-435-scratch/modelspec-data \
  --copies /tmp/model-435-scratch/retained-copies \
  --out /tmp/model-435-scratch/baseline.json \
  --summary-out /tmp/model-435-scratch/baseline-summary.json
```

Exit 0 means the inventory ran. It does not mean every input was available.

After comparison and required-input check:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  docs/evidence/g2-ios/MODEL-435/audit.py \
  --data /tmp/model-435-scratch/modelspec-data \
  --copies /tmp/model-435-scratch/retained-copies \
  --compare /tmp/model-435-scratch/baseline.json \
  --out /tmp/model-435-scratch/after.json \
  --summary-out /tmp/model-435-scratch/audit-summary.json \
  --require-candidate-copies
```

Expected and observed exit: **1**. The final output is:

```text
INPUT READINESS FAILED: original mismatches lack eligible retained same-URL copies; parser regression coverage is unavailable.
```

All ten original mismatches lack eligible source bytes. This is the red
input-readiness result; no green parser-fix result is claimed.

The final aggregate output is archived as [audit-summary.json](audit-summary.json).
The detailed before and after files contain private facts and are deleted
with scratch cleanup.

## Focused baseline tests

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py tests/test_model_396_readers.py \
  > /tmp/model-435-scratch/focused-tests.log 2>&1
```

Exit 0. Output ends with `428 passed in 3.01s`.
The output is archived as [focused-tests.log](focused-tests.log).

## Helper checks and unchanged files

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check \
  docs/evidence/g2-ios/MODEL-435/audit.py
git diff --check
git diff --exit-code d9ed66aea52395b440bd72a94a109c159d4ea4c2 -- \
  decision api registry models offerings verification
git -C /tmp/model-435-scratch/modelspec-data status --short
```

Each check exited 0. Both data and implementation checks produced no changes.
Only the evidence report, audit helper, commands and aggregate outputs are
committed.

Versions were read directly with `python --version`, `python -m pytest
--version`, `python -m ruff --version`, `git --version` and `gh --version`:
Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1 and gh 2.102.0.
No Node command was needed.

The executor used six `gh` invocations in total, including the version check,
draft PR creation and one read to confirm the draft state. There was no polling
loop and no `gh api` call.
