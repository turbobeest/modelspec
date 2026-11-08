# MODEL-452 execution evidence

The seeder derives video, audio and image support flags from the same mapped
input/output lists it writes to each card. Card validation reports disagreements
as warnings. This approved implementation remains unchanged in round four.

Original public base: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Implementation commit: `b540f612c78c4a5a132133152d70b8e43f641772`.
Round-four public base: `463f534d713965110ecae78f619d898075e3aca7`.
The final SHA is in the untracked `.pr-commit.txt` handoff and executor output.
PR #979 remains draft pending independent review.

## Original implementation and audit

The original synthetic regression run reproduced 17 failures before the fix;
all 33 new cases passed afterward. The focused suites passed 76 tests and
related suites passed 233, with one expected built-site scan skip.

A scratch clone of private data main contained 1,385 cards. The pre-rule audit
found **114 contradictory fields across 108 cards**, with no parsing errors.
The real validator subsequently reported the same 114 warnings, with no
missing or extra warnings and zero invalid cards. The rule remains a warning.

| Field | Count |
|---|---:|
| `modalities.video.input_supported` | 64 |
| `modalities.video.output_supported` | 7 |
| `modalities.audio.input_supported` | 2 |
| `modalities.audio.output_supported` | 3 |
| `modalities.vision.supported` | 21 |
| `modalities.image_generation.supported` | 17 |

Round three removed 171 private revision references across 79 evidence files.
It also introduced replay regressions by replacing executable revisions with
non-revision placeholders. Round four repairs those regressions while keeping
private revisions and per-card private values out of public output.

## Required replay inputs

Four helpers now require `MODELSPEC_EXPECTED_DATA_SHA` from local private
configuration: sentence seeding, repair-view auditing, acceptance setup and
staging. The sentence seeder retains its exact HEAD equality and clean-checkout
checks. The other helpers retain their Git resolution, archive, byte-comparison
and parent checks. Public metadata and Git error messages redact the supplied
revision; the staging `.sha` handoff remains local to private scratch.

The complete census found one further broken helper: `prepare_baseline.py`.
Its existing `--data-ref` argument is now required and must resolve to a commit
before archiving. Public command records, metadata and failures redact it.
Adjacent reproduction commands and generated README guidance pass the required
local inputs. Runnable snippets in seven additional reports were corrected;
archival JSON and JSONL records remain records, not executable configuration.

`tests/test_evidence_revision_inputs.py` exercises all five helpers through
their environment or CLI inputs with real Git repositories. It checks that a
supplied revision reaches the next replay operation, that omission fails,
and that invalid revisions fail without leaking the supplied value.
The parametrized tests are `test_supplied_revision_reaches_post_check`,
`test_missing_revision_is_required` and `test_wrong_revision_is_rejected`.

Before changing the four named helpers:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_evidence_revision_inputs.py -k 'not baseline' --tb=short
```

Exit 1: **8 failed, 4 passed, 3 deselected**. The four supplied-revision cases
failed at the retained equality/Git operations; the four missing-input cases
did not enforce a required input. A separate baseline-helper probe initially
passed one of five checks, then passed all five after the fix.

The error-redaction assertions separately reproduced three failures before
error handling was corrected. The final five-helper suite exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_evidence_revision_inputs.py --tb=short
```

Result: **15 passed**.

## Fresh private-HEAD proof

A fresh full-history, blob-filtered private clone was created under the explicit
scratch-directory override in the spec. Only the harmless engine-pin metadata
file was checked out. No retained source pages or model cards were checked out.

```bash
env PYTHONPATH=$PWD MODELSPEC_EVIDENCE_REPLAY_DATA=/tmp/model-449-scratch/model-452-r4/private-data /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/model-452-scratch/r4/pytest-private tests/test_evidence_revision_inputs.py --tb=short
```

Exit 0: **15 passed**. All five helpers accepted the actual private HEAD and
reached the next operation. The sentence helper reached source loading after
its HEAD and clean-checkout checks; the audit reached parent inspection;
setup reached the next fetch after resolving its baseline arguments; both archive
helpers reached tar handling. Missing and invalid-input cases also passed.

These are bounded probes. Clone, fetch and checkout effects are intercepted;
their baseline arguments are resolved with real Git. The unrelated historical
repair target is a fixture input. Git resolution uses the real clone, and the
archive probes use only its harmless engine-pin file with worktree attributes
and lazy fetching disabled. Execution stops before retained-source processing,
historical data projection, package installation or expensive acceptance work.
The first archive attempt needed attributes absent from the filtered clone;
using worktree attributes isolated the revision check without fetching them.
The clone remained clean throughout the successful proof and is deleted before
delivery. No full historical replay is claimed.

## Private-value cleanup

The audit covered all 80 files touched by the prior sweep: 95 Markdown tables
and 32 JSON/JSONL files. **Five private-detail tables and six prose disclosure
blocks** were replaced with aggregate results across six reports. No structured
per-card value records required changes. Synthetic examples, field-name-only
tables and records explicitly identical in public and private data remain.
Existing private-repository URLs and PR-number references were preserved.

The count-only disclosure check failed before editing with five tables and six
prose blocks remaining; afterward it exited 0 with zero of either remaining.
The baseline helper's complete synthetic replay passed all five checks,
including archive creation and public-output redaction. Syntax checks passed
13 shell blocks and three embedded Python blocks in the seven extra reports.

## Focused validation

Tool versions: Python 3.14.4, pytest 9.1.1, Node v22.22.3, Git 2.50.1.

```bash
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_evidence_revision_inputs.py tests/test_removed_sources.py tests/test_release_watch_filter.py::test_public_issue_replay_keeps_each_newly_carded_release_once tests/test_xai_capture_retired.py::test_xai_capture_helper_is_retired_before_browser_or_output -rs
```

Exit 0: **63 passed, 1 skipped in 53.30 seconds**. The existing built-site
scan skips without `MODELSPEC_DIST`; no site was built. This run includes the
source guard and all tests identified as readers of evidence files.

Additional count-only checks used these scratch tools:

```bash
python3 /tmp/model-452-scratch/r4/executor/check_private_revisions.py --private-repo /tmp/model-449-scratch/model-452-r4/private-data
python3 /tmp/model-452-scratch/r4/table-audit/check_disclosures.py
python3 /tmp/model-452-scratch/r4/script-review/probe_prepare_baseline.py
python3 /tmp/model-452-scratch/r4/script-review/check_replay_snippets.py
git diff --check
```

All exited 0. The full evidence-tree scan found zero private-only revision
references. Existing private PR references and repository URLs remain present.
The branch merges cleanly with the fetched public main.

## Limits

No production code, schema fields, frozen cards, Worker exports, rank rows,
production switches or legal terms changed this round. No provider calls,
source-page retrieval, production deployment, full local suite or CI result
was observed. Private data values were not rewritten. The conditional Worker
memory probe is not triggered by these evidence helpers.
