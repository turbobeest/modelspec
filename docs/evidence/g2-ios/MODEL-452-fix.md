# MODEL-452 execution evidence

The seeder derives video, audio and image support flags from the same mapped
input/output lists it writes to each card. Validation reports disagreements
as warnings. The implementation is unchanged by the public-text revisions.

Original public base: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Implementation commit: `b540f612c78c4a5a132133152d70b8e43f641772`.
Round-three public base: `86f651602d4ea100e1e6c45dd498f52993e1f443`.
The final delivery SHA is recorded in the untracked `.pr-commit.txt` handoff
and the executor completion line. PR #979 remains draft.

## Implementation verification

The new regression cases failed against unchanged production code:

| Test case | Red result | Green result |
|---|---|---|
| Seeded video input/output | Support flags were false instead of true | Both cases pass |
| Seeded image output and all directions | Image output flag was false instead of true | Both cases pass |
| All six contradictory flag/list pairs, both directions | Zero warnings instead of one in 12 cases | All 12 cases pass |
| Listed video with omitted support flag | Zero warnings instead of one | Pass |

These are synthetic fixtures. Consistent flags, text-only cards and the
previously correct mappings stayed covered. No assertion was weakened.
The red run exited 1 with 17 failed, 16 passed; the green run exited 0 with
33 passed. The exact command was:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_validate_pr.py -k 'seeded_modality_flags or modality_list_flag_consistency or listed_video_with_default' --tb=short
```

The original focused suites passed 76 tests. Related schema, serialization,
licence, attribution, failure-safety, guide and source-guard suites passed
233 tests with one expected built-site scan skip. REV-979-cx independently
approved the implementation and reproduced the original failures.

## Aggregate private-data audit

Before enabling the warning, a scratch clone of private data main was audited.
There were **114 contradictory fields across 108 of 1,385 cards** and zero
card parsing errors. The real validator subsequently reported 1,385 valid
cards, zero invalid cards and the same 114 warnings, with zero missing or
extra warnings. The rule therefore remains a warning.

| Field | Count |
|---|---:|
| `modalities.video.input_supported` | 64 |
| `modalities.video.output_supported` | 7 |
| `modalities.audio.input_supported` | 2 |
| `modalities.audio.output_supported` | 3 |
| `modalities.vision.supported` | 21 |
| `modalities.image_generation.supported` | 17 |

Only aggregate counts and field names are public. Detailed audit records and
scripts remain in local private scratch; this report does not contain a
reproducible private-data audit script.

## Round-three public-text correction

REV-979-cx requested removal of private revisions in older evidence and
correction of the live PR body's audit-script claim. The scan covered every
file under `docs/evidence/`, including JSON, JSONL and Python artifacts.
It extracted hexadecimal candidates of at least seven characters, resolved
them against a fresh private clone and the public repository, and selected
only identifiers resolving privately but not publicly. All selected objects
were commits. Private values were never printed in scan output.

The clone had full history, blob filtering and no checkout. Object resolution
used `GIT_NO_LAZY_FETCH=1`. The explicit scratch-directory override in the
round-three spec was followed. No data-repository files were changed.

The local check, before edits:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-452-scratch/r3/executor/check_private_revisions.py --private-repo /tmp/model-449-scratch/model-452-r3/private-data
```

Exit 1:

```text
Scanned 1155 evidence files; found 171 private-only revision references across 79 files.
```

The same command with `--apply` exited 0 and replaced **171 references across
79 evidence files** with neutral placeholders. This includes all three
references in MODEL-450. A separate read-only check independently reproduced
the count from the round-three base. Public identifiers and all other bytes
were preserved by the replacement step. A broader hexadecimal-boundary scan
found the same references.

Repeating the check exited 0:

```text
Scanned 1155 evidence files; found 0 private-only revision references across 0 files.
```

All affected JSON and JSONL files still parse. All affected Python files pass
`ast.parse`. The MODEL-452 report was shortened and updated separately.

The local `.pr-body.md` corrects the audit-script claim to describe aggregate
results. The live body is updated from that file using the explicitly
permitted command:

```bash
gh pr edit 979 -R turbobeest/modelspec --body-file .pr-body.md
```

`git fetch origin main` and `git merge-tree --write-tree HEAD origin/main`
both exited 0. No conflicts existed, so no merge was needed.

## Focused round-three checks

The source guard and both existing tests that directly read evidence artifacts
ran serially with this command:

```bash
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py tests/test_release_watch_filter.py::test_public_issue_replay_keeps_each_newly_carded_release_once tests/test_xai_capture_retired.py::test_xai_capture_helper_is_retired_before_browser_or_output -rs
```

Exit 0:

```text
..............................................s..                        [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_removed_sources.py:463: set MODELSPEC_DIST to a built dist/
48 passed, 1 skipped in 51.60s
```

The skip requires a built site through `MODELSPEC_DIST`. No site was built.
Tools checked locally: Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5,
PyYAML 6.0.3, Node v22.22.3 and Git 2.50.1. `git diff --check` exited 0.
A three-way preview of the one evidence file also changed on incoming main
found zero conflicts after sanitation.

## Limits

This round changes evidence and PR text only. No schema fields, stored cards,
Worker exports, rank rows, production switches or legal terms changed.
No new provider capability claim, deployment, live seeder ingestion, vendor
call, source-page retrieval, full local suite or CI result was observed.
The earlier implementation tests were not rerun in this text-only round.
