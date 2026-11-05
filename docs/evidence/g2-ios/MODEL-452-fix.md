# MODEL-452 execution evidence

The seeder now derives video input/output and image output support from the
mapped models.dev lists. Existing audio and image input mappings are preserved.
Card validation reports list/flag disagreements as warnings in both directions.

Base SHA: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Final implementation SHA: `b540f612c78c4a5a132133152d70b8e43f641772`.
Round-two base SHA: `8046a1f4f30ba18d8e0993e436bec37703bcf5e6`.
The latest evidence-only commit is the delivery revision. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-452-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-452`.
Branch: `model-452-codex`.

## Defects and regression tests

- Video input and output flags stayed false when video was listed.
  `test_seeded_modality_flags_match_the_written_lists[video-input]` and
  `[video-output]` failed with `False != True`, then passed.
- Image output support stayed false when image was listed as output.
  `test_seeded_modality_flags_match_the_written_lists[image-output]` failed
  with `False != True`, then passed. `[all-both-directions]` also failed
  before the fix. Text-only, image input and both audio directions already
  passed and remain covered.
- Validation silently accepted contradictory support flags.
  `test_modality_list_flag_consistency` failed for all six field/direction
  pairs with either list membership true and flag false, or the reverse.
  Each failure had zero warnings instead of one. All 12 cases now pass;
  the 12 consistent cases remain warning-free and valid.
- A listed video with an omitted detail block defaults to false in the schema.
  `test_listed_video_with_default_support_flag_warns` failed with zero
  warnings instead of one, then passed.

The tests inspect serialized seeded YAML and the public `validate_card()`
result. Contradictory fixtures retain `status: valid` because rollout is
warning-only. No existing assertions were weakened.

## Red and green

Both runs used this exact command from the worktree, before and after the
production changes respectively. Each shell exit code was checked directly.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_validate_pr.py -k 'seeded_modality_flags or modality_list_flag_consistency or listed_video_with_default' --tb=short
```

Red, exit 1, with production code still at the base revision:

```text
.FF.F..FFFFFFFFFFFFF............F                                        [100%]
=================================== FAILURES ===================================
_______ test_seeded_modality_flags_match_the_written_lists[video-input] ________
tests/test_seed_models_dev.py:219: in test_seeded_modality_flags_match_the_written_lists
    assert (
E   assert (True, False,... False, False) == (True, False,..., True, False)
E
E     At index 4 diff: False != True
E     Use -v to get more diff
_______ test_seeded_modality_flags_match_the_written_lists[video-output] _______
tests/test_seed_models_dev.py:219: in test_seeded_modality_flags_match_the_written_lists
    assert (
E   assert (False, False... False, False) == (False, False..., False, True)
E
E     At index 5 diff: False != True
E     Use -v to get more diff
_______ test_seeded_modality_flags_match_the_written_lists[image-output] _______
tests/test_seed_models_dev.py:219: in test_seeded_modality_flags_match_the_written_lists
    assert (
E   assert (False, False... False, False) == (False, True,... False, False)
E
E     At index 1 diff: False != True
E     Use -v to get more diff
___ test_seeded_modality_flags_match_the_written_lists[all-both-directions] ____
tests/test_seed_models_dev.py:219: in test_seeded_modality_flags_match_the_written_lists
    assert (
E   assert (True, False,... False, False) == (True, True, ...e, True, True)
E
E     At index 1 diff: False != True
E     Use -v to get more diff
_ test_modality_list_flag_consistency[listed-but-false-video-input-video-input_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[listed-but-false-video-output-video-output_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[listed-but-false-audio-input-audio-input_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[listed-but-false-audio-output-audio-output_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[listed-but-false-image-input-vision-supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[listed-but-false-image-output-image_generation-supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-video-input-video-input_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-video-output-video-output_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-audio-input-audio-input_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-audio-output-audio-output_supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-image-input-vision-supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
_ test_modality_list_flag_consistency[unlisted-but-true-image-output-image_generation-supported] _
tests/test_validate_pr.py:116: in test_modality_list_flag_consistency
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
______________ test_listed_video_with_default_support_flag_warns _______________
tests/test_validate_pr.py:137: in test_listed_video_with_default_support_flag_warns
    assert len(result["warnings"]) == 1
E   assert 0 == 1
E    +  where 0 = len([])
=========================== short test summary info ============================
FAILED tests/test_seed_models_dev.py::test_seeded_modality_flags_match_the_written_lists[video-input]
FAILED tests/test_seed_models_dev.py::test_seeded_modality_flags_match_the_written_lists[video-output]
FAILED tests/test_seed_models_dev.py::test_seeded_modality_flags_match_the_written_lists[image-output]
FAILED tests/test_seed_models_dev.py::test_seeded_modality_flags_match_the_written_lists[all-both-directions]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-video-input-video-input_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-video-output-video-output_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-audio-input-audio-input_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-audio-output-audio-output_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-image-input-vision-supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[listed-but-false-image-output-image_generation-supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-video-input-video-input_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-video-output-video-output_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-audio-input-audio-input_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-audio-output-audio-output_supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-image-input-vision-supported]
FAILED tests/test_validate_pr.py::test_modality_list_flag_consistency[unlisted-but-true-image-output-image_generation-supported]
FAILED tests/test_validate_pr.py::test_listed_video_with_default_support_flag_warns
17 failed, 16 passed, 43 deselected in 0.45s
```

Green, exit 0:

```text
.................................                                        [100%]
33 passed, 43 deselected in 0.40s
```

Focused suites, exit 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_validate_pr.py
```

```text
........................................................................ [ 94%]
....                                                                     [100%]
76 passed in 24.66s
```

Related suites, including the required source guard, exit 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_schema.py tests/test_card_yaml_roundtrip.py tests/test_license_defaults.py tests/test_typesafe_jev_card.py tests/test_research_failure_safety.py tests/test_attribution.py tests/test_guide_staleness.py tests/test_removed_sources.py
```

```text
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 92%]
.................s                                                       [100%]
233 passed, 1 skipped in 54.61s
```

The skip is `test_a_built_dist_carries_no_removed_value`, whose existing
condition requires `MODELSPEC_DIST`. No site was built for this Python change.
`tests/test_schema.py` also executes its module-level schema assertions during
collection. The full local suite was not run, as required by the ticket.

## Pre-rule private-main audit

Audited a scratch clone of private data main before enabling the rule.
The scan found **114 contradictory fields across 108 of 1,385 cards**.
There were no card parsing errors. The rule therefore ships as a **warning**.
Public audit results are limited to aggregate counts and field names.
The per-card audit records remain only in local private scratch.

| Flag | Count |
|---|---:|
| `modalities.video.input_supported` | 64 |
| `modalities.video.output_supported` | 7 |
| `modalities.audio.input_supported` | 2 |
| `modalities.audio.output_supported` | 3 |
| `modalities.vision.supported` | 21 |
| `modalities.image_generation.supported` | 17 |

Image input uses `vision.supported`; image output uses
`image_generation.supported`. These are existing schema fields.
No `modalities.image` fields were introduced. The audit includes effective
schema defaults. The initial recursive scan included one non-card document
and exited 1. The final scan uses the provider/card directory layout and
exits 0. Detailed reproduction records are held in local private scratch.

## Verification against private main

After implementation, the real validator processed the same scratch clone
and exited 0. It reported 1,385 valid cards, zero invalid cards, and 114
modality warnings across 108 cards. Comparison with the independent pre-rule
audit found zero extra or missing warnings.

The private checkout remained clean and was removed after verification.
No private card files were committed to this repository. All values in the
regression fixtures and their red/green output above are synthetic.

## Tool versions and limits

Versions were read with `python` and `importlib.metadata.version`,
`git --version`, and `gh --version`:

- Python 3.14.4, Clang 17.0.0.
- pytest 9.1.1; Pydantic 2.13.5; PyYAML 6.0.3; httpx 0.28.1.
- Git 2.50.1; GitHub CLI 2.102.0.

`git diff --check` passed. A separate read-only agent reviewed the four changed
implementation/test files and found no correctness issues. This is not the
pending cross-model PR review.

No schema fields, snapshot/export fields, rank rows, frozen cards, production
switches, or legal terms changed. `schema/card.py` is not in the Worker's
vendor source list, and pipeline/API export code does not call `warnings()`.
The conditional Worker memory probe and re-vendor step were not triggered.
No production deploy, live seeder ingestion, CI result, full local suite,
or live provider capability claim was observed. There were no paid-provider
calls or source-page downloads. The warnings identify inconsistent data;
they do not establish which side is factually correct.

## Round two: public-text correction

REV-979 passed the implementation, regression tests and private-main audit.
Its requested changes concern public text. This revision removes the private
clone URL, private revision identifier, detailed audit script and membership
breakdown from this report. The local saved PR body now contains aggregate
counts and field names only. The per-card table remains in private scratch.
No implementation or test fixture changed in this revision.

The saved body was located at
`/tmp/model-452-scratch/executor/pr-body.md`; a matching `.pr-body.md` record
is kept in that same local directory. Neither file is tracked. The live PR
body was already sanitized by the orchestrator and was not changed here.

A local privacy check reproduced the public-text defects before editing.
It checks the evidence and saved body for private revision identifiers,
clone URLs, per-card identifiers and membership/flag detail, and reviews
additions in all five committed ticket files for private audit material.
It prints only categories of findings, not the private values.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-452-scratch/r2/check_public_text.py
```

Red output, exit 1:

```text
evidence: private revision identifier
evidence: private clone URL
evidence: private membership/flag detail
pr-body.md: private revision identifier
pr-body.md: private per-card identifiers
pr-body.md: private membership/flag detail
```

Green output, exit 0:

```text
PASS: public audit text contains aggregate counts and field names only.
PASS: all 5 ticket files checked; no additional private audit detail or per-card identifiers introduced.
```

The implementation and fixtures were also inspected. The new cases use
`fixture`, `fixture/model`, and `fixture/video` with synthetic data.
Existing real-card references predate this ticket's changes.

No GitHub CLI calls, fresh private-data retrieval, live PR verification,
CI polling, deployment or full local suite were performed in this revision.
The branch remains intended for draft PR #979.

Focused source-guard suite, exit 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py -rs
```

```text
..............................................s                          [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_removed_sources.py:463: set MODELSPEC_DIST to a built dist/
46 passed, 1 skipped in 52.12s
```

Round-two versions were read locally: Python 3.14.4, pytest 9.1.1,
Pydantic 2.13.5 and PyYAML 6.0.3. No GitHub CLI version call was made.
`git diff --check` passed.

The broader tracked-tree scan found the private revision identifier in
`docs/evidence/g2-ios/MODEL-450-fix.md`. That file is byte-for-byte identical
to the original MODEL-452 base and remains outside this revision. The scan
found no copy of the private per-card audit table header in tracked files.
The privacy check passes for all five files changed by MODEL-452 and the
sanitized local PR-body records; it does not certify unrelated earlier work.
