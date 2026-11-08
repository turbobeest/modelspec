# MODEL-452 execution evidence

The seeder now derives video input/output and image output support flags from
its mapped modality lists. Its existing image input and audio mappings already
use those lists. `ModelCard.warnings()` reports contradictions for all six
list/flag pairs without rejecting the card.

Original public base: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Implementation commit: `b540f612c78c4a5a132133152d70b8e43f641772`.
Round-five public base: `8df96a9e53a1d0a82c1fb0ae961751fd17087a85`.
Merged public main: `37a91865beba12ed5f8cf1dd505a8526d0c9278c`.
The final SHA is recorded in the untracked `.pr-commit.txt` handoff and executor
output. PR #979 remains draft pending independent review.

## Regression evidence

The synthetic regression cases cover serialized flags for text, image, audio
and video; contradictions in both directions for each flag; consistent pairs;
and an omitted video flag that defaults to false. The tests use fixture cards.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_validate_pr.py -k 'seeded_modality_flags or modality_list_flag_consistency or listed_video_with_default' --tb=short
```

Before the implementation, this command exited 1 with **17 failed, 16 passed**.
`test_seeded_modality_flags_match_the_written_lists` failed four cases because
video input/output or image output flags were false despite their written lists.
`test_modality_list_flag_consistency` failed the 12 contradictory cases because
no warning was returned. `test_listed_video_with_default_support_flag_warns`
also returned no warning. After the implementation, the same command exited 0
with **33 passed**. These red/green results were observed during the original
implementation; round five leaves that code and those tests unchanged.

## Private-main contradiction audit

The original pre-rule audit scanned **1,385 cards** and found **114
contradictory fields across 108 cards**, with no parsing errors. All 114 flags
were explicit; defaults introduced no additional contradictions. There were
112 listed-but-false flags and two unlisted-but-true flags. The only non-card
Markdown file, `models/LICENSE.md`, was excluded.

| Field | Contradictions |
|---|---:|
| `modalities.video.input_supported` | 64 |
| `modalities.video.output_supported` | 7 |
| `modalities.audio.input_supported` | 2 |
| `modalities.audio.output_supported` | 3 |
| `modalities.vision.supported` | 21 |
| `modalities.image_generation.supported` | 17 |

The real `validate_pr --all` path then reported 1,385 valid cards, zero invalid
cards and the same 114 warnings. Each warning matched the independent audit's
card and field. This existing-data result is why the rule ships as a warning.
The public report retains aggregate counts only. The audit was not rerun in
round five, and no private card values are included here.

## Round-five validation

Tool versions: Python 3.14.4, pytest 9.1.1, Git 2.50.1.

The net PR diff contains exactly five files: `schema/card.py`,
`scripts/seed_models_dev.py`, their two test files, and this report.
A count-only scope check initially exited 1 with 85 changed files and 80 outside
that scope; after correction it exited 0 with five files and none outside it.

```bash
python3 /tmp/model-452-scratch/r5/executor/check_scope.py
python3 /tmp/model-452-scratch/r5/executor/check_scope.py --committed
git diff --stat origin/main...HEAD
```

Focused verification runs serially:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_validate_pr.py tests/test_removed_sources.py -rs
```

Exit 0: **122 passed, 1 skipped in 83.30 seconds**. The existing built-site
scan skips without `MODELSPEC_DIST`; no site was built. `git diff --check`
also exited 0.

The report and PR body are checked against a fresh private clone created with
`--filter=blob:none --no-checkout`. Private PR heads are included with:

```bash
git clone --quiet --filter=blob:none --no-checkout https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/model-452-r5/private-data
git -C /tmp/model-449-scratch/model-452-r5/private-data fetch --quiet --filter=blob:none origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
python3 /tmp/model-452-scratch/r5/executor/check_private_revisions.py --private-repo /tmp/model-449-scratch/model-452-r5/private-data docs/evidence/g2-ios/MODEL-452-fix.md .pr-body.md
```

The check compares full and abbreviated revision tokens against private and
public commit histories. Its positive controls use a private PR-head commit
absent from private main and public history. It prints counts only. No private
cards or retained source pages are checked out, and the clone is deleted before
delivery.
The clone, fetch and check exited 0. The check covered **134 private PR heads**
and found **zero private-only revision tokens** in this report and the PR body.

## Limits

No frozen cards, schema fields, Worker exports, rank rows, production switches
or legal terms changed. No provider calls, source-page retrieval, production
deployment, full local suite or CI result was observed. The conditional Worker
memory probe is not triggered by this seeder and warning-only change.
