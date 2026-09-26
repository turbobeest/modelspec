# Recall baseline gate (MODEL-160)

`scripts/recall_run.py` remains a report generator. The pull request accuracy
profile compares its verdicts with `baseline.json` and gates changes. The
baseline created on 2026-09-25 is 4 pass, 6 partial, and 10 fail.

The allowed transitions only raise the recorded minimum:

- `pass` may stay `pass`.
- `partial` may stay `partial` or become `pass` after the baseline is updated.
- `fail` may stay `fail` or improve after the baseline is updated.

A regression fails the pull request accuracy profile. Its report identifies the
question, the verdict transition, and whether the current finding came from
missing data or engine behavior. An improvement also fails until the contributor
records the higher verdict. The failure prints the update command.

CI compares the proposed baseline with the baseline at the pull request's Git
merge base. Lowering `baseline.json` therefore cannot hide a current regression.
The update command also refuses to record any regression against the checked-out
baseline. For MODEL-160 itself, whose merge base predates `baseline.json`, CI
runs recall in a detached merge-base checkout and uses those verdicts as the
approved baseline.

The nightly accuracy profile runs the same comparison as a report-only layer.
Weekly leaderboard refresh pull requests wait for the `Decision accuracy`
workflow to pass before they enable auto-merge.

## Update the baseline

Generate or raise the baseline from a repository snapshot with:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline --date YYYY-MM-DD
```

MODEL-160 created `baseline.json` from commit `f6630a62` with:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline --date 2026-09-25
```

Do not edit verdicts by hand. The command runs all 20 specs, records the snapshot
ID and date, and keeps every existing verdict at the same level or higher.

## Approval guard

A pull request that changes `specs/**`, `expected.yaml`, or the approved
`README.md` must have the `recall-approved` label. CI reads the pull request's
labels and changed-file list from GitHub. Label and unlabel events rerun the
workflow, so adding `recall-approved` after a failed run checks the live label
state. Only Jamie applies that label.

Updating `baseline.json` after an engine or data improvement does not change an
approved spec or expected answer and does not require the label. This file is
also outside the protected set because it documents the gate rather than the
approved recall inputs.

## Files

`baseline.json` records the minimum accepted verdict for each question, the
snapshot ID, the date, and the command that generated it.
