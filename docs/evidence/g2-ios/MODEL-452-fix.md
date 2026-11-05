# MODEL-452 execution evidence

The seeder now derives video input/output and image output support from the
mapped models.dev lists. Existing audio and image input mappings are preserved.
Card validation reports list/flag disagreements as warnings in both directions.

Base SHA: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Final implementation SHA: `b540f612c78c4a5a132133152d70b8e43f641772`.
The subsequent evidence-only commit is the delivery revision, recorded in the
PR and executor completion line. Resolve it with
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

Audited `modelspec-data` main at
`b2f7176b13bc4c7186f9b36f66f0e644df65dcb6` before enabling the rule.
The scan found **114 contradictory fields across 108 of 1,385 cards**.
All 114 flags were explicit; no additional contradictions came from defaults.
112 disagreements were listed/false and two were unlisted/true.
There were no card parsing errors. The rule therefore ships as a **warning**.
The PR lists every affected card path and field.

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
schema defaults. `models/LICENSE.md` is the only non-card Markdown file;
an initial recursive scan reported that file as a parse error and exited 1.
The final scan uses the provider/card directory layout and exits 0.

Exact successful clone and audit commands:

```bash
mkdir -p /tmp/model-452-scratch/audit
git clone --depth 1 --single-branch --branch main --filter=blob:none --sparse https://github.com/turbobeest/modelspec-data.git /tmp/model-452-scratch/audit/modelspec-data
git -C /tmp/model-452-scratch/audit/modelspec-data sparse-checkout set models
git -C /tmp/model-452-scratch/audit/modelspec-data rev-parse HEAD
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-452-scratch/audit/audit_modalities.py /tmp/model-452-scratch/audit/modelspec-data > /tmp/model-452-scratch/audit/audit.json
git -C /tmp/model-452-scratch/audit/modelspec-data status --porcelain
```

The audit script, saved at the path above, was:

```python
"""Read-only MODEL-452 audit; run with public repo on PYTHONPATH."""
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys

import yaml
from schema.card import Modalities

root = Path(sys.argv[1])
fields = (
    ("video", "input", "video", "input_supported"),
    ("video", "output", "video", "output_supported"),
    ("audio", "input", "audio", "input_supported"),
    ("audio", "output", "audio", "output_supported"),
    ("image", "input", "vision", "supported"),
    ("image", "output", "image_generation", "supported"),
)
rows = []
errors = []
cards = sorted(root.glob("models/*/*.md"))
for path in cards:
    try:
        parts = path.read_text().split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError("card has no YAML frontmatter")
        raw = yaml.load(parts[1], Loader=yaml.CSafeLoader)
        raw_modalities = raw.get("modalities", {})
        modalities = Modalities.model_validate(raw_modalities)
        for kind, direction, detail, flag in fields:
            listed = kind in getattr(modalities, direction)
            supported = getattr(getattr(modalities, detail), flag)
            explicit = flag in raw_modalities.get(detail, {})
            if listed != supported:
                rows.append({
                    "path": str(path.relative_to(root)),
                    "model_id": raw.get("model_id"),
                    "list": f"modalities.{direction}",
                    "kind": kind,
                    "listed": listed,
                    "field": f"modalities.{detail}.{flag}",
                    "supported": supported,
                    "explicit_flag": explicit,
                })
    except Exception as exc:
        errors.append({"path": str(path.relative_to(root)), "error": str(exc)})

result = {
    "data_main_sha": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
    "card_count": len(cards),
    "contradicting_card_count": len({row["path"] for row in rows}),
    "contradiction_count": len(rows),
    "explicit_contradiction_count": sum(row["explicit_flag"] for row in rows),
    "defaulted_contradiction_count": sum(not row["explicit_flag"] for row in rows),
    "field_counts": dict(sorted(Counter(row["field"] for row in rows).items())),
    "errors": errors,
    "contradictions": rows,
}
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))
```

## Verification against private main

After implementation, the real validator processed the same checkout with
this command and exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - /tmp/model-452-scratch/audit/modelspec-data > /tmp/model-452-scratch/executor/private-validation.json <<'PY'
import sys
from pathlib import Path
from scripts import validate_pr
validate_pr.REPO_ROOT = Path(sys.argv[1])
sys.argv = ['validate_pr.py', '--all']
validate_pr.main()
PY
```

This independent comparison also exited 0:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import json
from pathlib import Path
scratch = Path('/tmp/model-452-scratch')
audit = json.loads((scratch / 'audit/audit.json').read_text())
validated = json.loads((scratch / 'executor/private-validation.json').read_text())
expected = {(row['path'], row['field']) for row in audit['contradictions']}
observed = {
    (row['file'], warning.split(' is ', 1)[0])
    for row in validated['results']
    for warning in row.get('warnings', [])
    if warning.startswith('modalities.')
}
assert validated['total'] == 1385, validated['total']
assert validated['valid'] == 1385, validated['invalid']
assert observed == expected, (observed - expected, expected - observed)
assert len(observed) == 114
assert len({path for path, _ in observed}) == 108
print('Private-data validator: 1385 valid, 0 invalid; 114 modality warnings across 108 cards.')
print('Every warning path and field matches the independent pre-rule audit; no extra or missing warnings.')
PY
```

Output:

```text
Private-data validator: 1385 valid, 0 invalid; 114 modality warnings across 108 cards.
Every warning path and field matches the independent pre-rule audit; no extra or missing warnings.
```

The private checkout remained clean. Only model cards were checked out;
source archives were not checked out. No data files were changed or committed
into this repository. The scratch clone is removed before delivery.

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
