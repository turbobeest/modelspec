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

## Writer-pin follow-up execution evidence

Observed 2026-11-08 in the assigned `model-452-writers-read-pin` worktrees.

- Public base: `7c9282c6dc20bfb6a38e1f87ad569edb13e71a19`.
- Final public test SHA: `e6fe3d99574979b90afc502be4eda44684a26733`.
- Evidence follows those code commits. Final PR-tip SHAs are recorded after
  committing this evidence in each worktree's untracked `.pr-commit.txt` and
  in the executor completion. `git rev-parse HEAD` reproduces each final tip.

The migration described by the ticket is already present at the supplied
bases. All 19 engine checkouts across 14 workflow files read `.engine-pin`,
and every public workflow mirror is byte-identical to the private workflow.
No workflow changes or older-engine exceptions were needed.

The public test now discovers every `.yml` and `.yaml` writer, including future
files absent from the existing fixed test list. It checks the pin read, main
ancestry check, step order and checkout ref. The data companion rejects matching
mirrors that hard-code an engine ref and tests the real private inventory.

### Regression probe and green suite

From `/Users/terbeest/dev/worktrees/model-452-pin`, this temporary additional
writer proves discovery catches a new file whose engine ref is hard-coded:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import subprocess
import sys

probe = Path('.github/private-writers/model-452-probe.yaml')
assert not probe.exists()
source = Path('.github/private-writers/daily-research.yml').read_text()
try:
    probe.write_text(source.replace('ref: ${{ steps.engine_pin.outputs.sha }}', 'ref: ' + 'a' * 40, 1))
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests/test_engine_pin.py', '-k', 'every_discovered_writer', '--tb=short'])
finally:
    probe.unlink()
sys.exit(result.returncode)
PY
```

`test_every_discovered_writer_checks_out_the_verified_engine_pin[model-452-probe.yaml]`
failed at `assert checkout.get("ref") == PIN_REF` with the literal SHA instead
of `${{ steps.engine_pin.outputs.sha }}`. Result:
**1 failed, 14 passed, 60 deselected in 0.12s; exit 1**. The probe was removed
by `finally`. This was a deliberate mutation, not an existing broken workflow.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_writer_artifacts.py tests/test_research_workflow.py
```

Result: **375 passed in 12.64s; exit 0**. The tests execute pin validation
against local Git repositories, including malformed pins and off-main commits.
They ran serially after the data workflow/guard suites, which passed 173 tests.
The data evidence records its red-first guard tests and exact commands.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
```

Result: **46 passed, 1 skipped in 52.87s; exit 0**. The skip requires a built
`dist/` selected by `MODELSPEC_DIST`; no deployed site build was tested. This
ran after staging the evidence so the tracked-file scan included it.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-452-pin/.github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-452-pin/.github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-452-pin/.github/workflows
git diff --check
```

Results: `14 public writer mirror(s) match private workflows.`, exit 0;
whitespace check exit 0.

### Tools and limits

Version commands were `git --version`, `gh --version`,
`/Users/terbeest/dev/modelspec/.venv/bin/python --version`,
`/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version`, and
`/Users/terbeest/dev/modelspec/.venv/bin/python -c 'import yaml; print("PyYAML", yaml.__version__)'`.
Versions: Git 2.50.1, GitHub CLI 2.103.3, Python 3.14.4, pytest 9.1.1,
PyYAML 6.0.3.

Merge data#138 first so the pin includes public #979. Merge the paired MODEL-452
draft PRs together, public first. The data body links this companion by the
stable branch PR search because it must be created first and PR edits are
prohibited. This public PR links the exact data PR URL. Publish commands from
this worktree and `/tmp` respectively:

```sh
CI_LOCAL_SKIP=1 git push -u origin model-452-writers-read-pin
gh pr create -R turbobeest/modelspec --draft --base main --head model-452-writers-read-pin --title "MODEL-452: discover every writer in engine-pin mirror tests" --body-file /Users/terbeest/dev/worktrees/model-452-pin/.pr-body.md
```

Not observed: a currently hard-coded production checkout, live Actions
execution, the full CI run, data#138's merge state, a deployed daily-model
rebuild, or independent review. No private data was copied into this repo.
No full local suite, WSL gate, provider calls, Worker export changes,
deployments, or merges were performed.
