# Frozen-image engine recall gate

Jamie decided on 2026-10-01, Q04 option b, that recall's approved answers are
judged against the private data production serves. Private CI has its own
baseline at `reports/recall/baseline.json`. The public accuracy profile runs
recall as an engine regression test against the frozen public image.
`tests/recall/baseline.json` records that image's verdicts. It does not amend
`expected.yaml`, whose approved answers remain Jamie's decision.

## Comparison and baseline changes

The current run must match every proposed baseline verdict. A regression fails
until the contributor fixes it or records a justified frozen-image change.
An improvement also fails until the contributor records the higher verdict.
Missing questions fail. The nightly accuracy profile reports the same
comparison without gating its run.

CI also compares the proposed baseline with the pull request's Git merge-base
baseline. Lowering a verdict requires a non-empty `frozen_image_reason` for
that question, newly added or changed from the merge base. An existing reason
cannot excuse another decrease. The reason documents why the frozen image
causes the change, and should cite a private recall run when available. It
never excuses a current verdict below the proposed baseline. Reviewers must
check the explanation and reject engine regressions disguised as image gaps.

Every public baseline verdict below `pass` must have a `frozen_image_reason`,
including existing partials caused by missing verified objective evidence.
The reasons are a JSON map alongside `verdicts`, keyed by question id. Old
merge-base baselines without this field remain readable.

For example, MODEL-266 correctly eliminates a model with no offering and no
verified open weights. Q04 then fails on the frozen public image, which has
no GPT-6 Luna offering. Current private data has its offering and Q04 passes there.
Record that image limitation; do not weaken the approved answer.

## Update the public baseline

Generate or raise the baseline with:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline --date YYYY-MM-DD
```

For a frozen-image change, put the new explanations in a JSON file:

```json
{
  "Q04": "no GPT-6 Luna offering in the frozen public image; passes on current private data, see the private recall run"
}
```

Then run:

```bash
PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline \
  --date YYYY-MM-DD --frozen-image-reasons /path/to/reasons.json
```

The command runs all 20 specs and records the snapshot and date. It retains
existing reasons, removes reasons for questions that now pass, and refuses a
lower verdict without a new or changed explanation. Do not edit verdicts by
hand. Keep the generated JSON and Markdown report at
`docs/recall/<date>-<snapshot>.*` so the baseline remains traceable.

## Approval guard

A PR changing `specs/**`, `expected.yaml`, or the approved `README.md` must
have the `recall-approved` label. CI checks the live PR labels and changed
files. Only Jamie applies that label. Label events rerun the workflow.

Baseline updates and this gate's documentation do not change approved inputs.
They need no label. This split changes the README's operational explanation,
so its PR still needs Jamie's label under the existing guard.

## Private baseline

The private gate scores the same approved answers using a pinned engine
composed with the private data. It fails any verdict below either its checked-in
baseline or the baseline at the PR merge base. Public `frozen_image_reason`
exceptions do not apply. Seed it from the first private run and review any
existing partial or failing answers as data coverage work. Private reports,
model values and finding messages stay out of public CI and public PRs.
