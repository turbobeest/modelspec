# MODEL-453 review fixes

Assessment: 2026-11-08. Reviews: REV-980-cx and REV-980-cx-r2, PR #980.
Round-three base: `3ad7a4bd5acc4919212e2f32825c188d7fb0d25c`.
Round-two base: `76edfde510cb1613287bbcb4810a827fb05bda82`.
Merged main: `9e7a18eff326f5d2806b40bf6d0af1b039fd6a19`.
Merge commit: `4c6b36977a4aaedbb235604823ca60c0dbfcd178`.
Final implementation: `092aa5dbf6dee0103d7a0936dd39e5a07bca0968`.
Round three changes only this evidence file. Its final SHA is recorded in the
untracked `.pr-body.md` hand-off and executor completion marker. Resolve it with
`git rev-parse HEAD` in the PR checkout.

## Diagnosis and change

The original diagnosis found 872 failing live readings in the frozen public
image. The private comparison checked 880 live readings with zero failures.
Freshness now gates the nightly profile against current data; the public
30-day limit remains unchanged.

Round two found that `release_blog.gates.accuracy` still required freshness in
PR reports. That rejected valid reports from the three-layer PR producer and
blocked release preparation, the breakdown CLI and social draft generation.
The consumer now requires exactly `deterministic_correctness`,
`frozen_image_engine_recall` and `output_parity`. Every required layer must
pass. Missing, extra, duplicate and failing layers remain errors.

The release tests identify recall by name instead of its old list position.
They check missing and failing reports through release preparation and verify
that refusal writes no post. The social fixture now uses three layers, so its
existing generation tests exercise the updated report through the social entry
point. The requested search found no other production layer-list validator;
the release and social entry points all use the shared gate.

This evidence replaces the earlier detailed private diagnostics with aggregate
counts. It removes private repository locations, per-PR metadata, reading-age
distributions, source associations and the embedded private-data probe. A local
artifact audit failed all five checks before the rewrite. No private checkout
was needed in round two. The safe form of the earlier clone command is:

```bash
git clone --single-branch --branch main "$PRIVATE_DATA_CLONE_URL" /tmp/model-449-scratch/model-453-r2/private-data
```

In round two, the live PR body was read before editing. It contained aggregate freshness
counts and public commit identifiers, without the flagged private metadata.
The updated body describes the final implementation and review fixes.

## Original public red and green evidence

These are the measured results from 2026-11-05, restored from the public evidence
at `76edfde5`. They were not rerun in round three. The original public base was
`187117e902c266b3c63b5861af1f57189cf4f30a`; the freshness implementation was
`e1c06d985379d4369891b6bb0ba9f33e22237fc0`. The named regression cases below use
synthetic fixtures in public test files, not private catalogue observations.

| Reproduction or test | Before | After |
| --- | --- | --- |
| Full `--profile pr` on the public checkout | Exit 1; only freshness failed, 872/872 | Exit 0; deterministic correctness, frozen-image recall and parity pass |
| Explicit public freshness layer | Exit 1; 872 failures | Exit 1; still 872 failures, outside frozen PR defaults |
| `test_private_freshness_uses_current_data_and_its_registry_without_disclosure` | Four failures; private data/registry ignored | All pass; stale and undated fixture inputs still fail the gate |
| `test_private_freshness_rejects_unreadable_inputs_without_disclosure` | Three failures; no private-input validation | All pass; sanitized errors for missing, empty and malformed fixtures |
| `test_nightly_private_freshness_keeps_reference_and_recall_on_public_inputs` | Fails; nightly has no freshness layer | Passes; public reference and recall inputs preserved |
| `test_accuracy_workflows_split_pr_and_nightly_layers` | Fails against new behavioral profile assertion | Passes; freshness belongs to nightly |
| Logger sentinel assertions in the four synthetic age cases | Four failures after first fix; warnings disclosed sentinel identifiers | All pass with scoped log suppression |
| `test_pr_checks_frozen_engine_without_a_current_data_age_gate` | Fails after profile move; report lost snapshot ID | Passes; public snapshot metadata preserved |

Initial red summary: `9 failed, 71 deselected in 1.33s`.
Privacy red summary: `4 failed, 76 deselected in 0.73s`.
Final targeted regressions: 10 passed.
Final focused suites: `137 passed, 1 skipped in 53.26s`.
The skipped test requires `MODELSPEC_DIST` pointing to a built site.

The original full PR run reported `1307 passed in 45.71s` for deterministic
correctness, all 20 recall verdicts matching the approved public baseline, and
passing CLI/Worker/web parity. Only freshness failed. The final full PR run
exited 0: 1307 deterministic tests passed in 45.89s, all 20 recall verdicts
matched, 678 Python parity tests passed with one skip, and 228 web parity tests
passed. The public snapshot ID was preserved.

## Original public reproduction and rule-history commands

These commands record the original runs, not additional round-three execution.
They ran from this worktree using Python 3.14.4, pytest 9.1.1, Node v22.22.3,
npm 10.9.8 and git 2.50.1. CI's Python 3.11 and Node 24 were not reproduced
locally. Test processes ran serially, and exit codes were checked directly.
The full PR profile is a selected accuracy suite, not the repository-wide suite.

```bash
mkdir -p /tmp/model-453-scratch/executor
# Initial failing public freshness layer, before the implementation change.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --layers freshness --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-red > /tmp/model-453-scratch/executor/public-red.log 2>&1
# Install web test dependencies with the required Node version.
(cd web && env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci --ignore-scripts --no-audit --no-fund)
# The initial full-profile run used public-full-red for its directory and log;
# the final run used public-final-green as shown here.
env PYTHONPATH=$PWD PYTEST_ADDOPTS='-p no:cacheprovider' PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-final-green > /tmp/model-453-scratch/executor/public-final-green.log 2>&1
# New tests, first against unchanged implementation and then after the fix.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness or accuracy_workflows_split'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness_uses'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'pr_checks_frozen'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness or accuracy_workflows_split or pr_checks_frozen'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py tests/test_accuracy_alert.py tests/test_cite_only_accuracy.py tests/test_removed_sources.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --layers freshness --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-final-red > /tmp/model-453-scratch/executor/public-final-red.log 2>&1
# Rule history, no remote calls.
git log -S 'live_leaderboard_max_age_days' --format='%h %ad %s' --date=iso-strict -- scripts/accuracy.py accuracy.yaml
git log --format='%h %ad %s' --date=iso-strict -G 'observation|_LIVE_SOURCE_KINDS|live_rows|check_freshness' -- scripts/accuracy.py
git show 023ceaab -- scripts/accuracy.py accuracy.yaml
git show 7e3d8ba6 -- scripts/accuracy.py
git show 31263b638 -- accuracy.yaml
git blame -L 218,264 187117e9 -- scripts/accuracy.py
git blame -L 3,6 -- accuracy.yaml
```

## Round-two red-first consumer checks

All commands ran from the assigned worktree. Test processes ran serially with
pytest's cache provider disabled. Exit codes came directly from the processes.

| Check | Exit | Result |
| --- | ---: | --- |
| Original `tests/test_release_pipeline.py`, before edits | 1 | 14 failed, 12 passed in 0.95s |
| Updated release and social tests against unchanged consumer | 1 | 29 failed, 24 passed in 1.28s |
| Private-metadata artifact audit before rewrite | 1 | 5 failed checks |
| Release and social tests after the consumer change | 0 | 53 passed in 3.83s |
| Final focused verification, five test files | 0 | 226 passed, 1 skipped in 57.01s |
| Private-metadata artifact audit after rewrite | 0 | 5 passed checks |

The skipped source-exclusion test requires `MODELSPEC_DIST` to point to a built
site. No site build was requested for this change.

The rejection was `ValueError: accuracy report must contain the exact pr layers`.
`test_actual_pr_accuracy_report_is_accepted` and the existing release/social
generation cases reproduced it. `test_bad_accuracy_writes_no_post` now checks
all three required layers separately, both missing and failed.
`test_accuracy_report_with_extra_or_duplicate_layer_is_refused` additionally
checks an unexpected freshness layer and a duplicate required layer.

## Round-two commands and environment

Python 3.14.4, pytest 9.1.1, git 2.50.1. No Node commands were needed.
The first two pytest commands ran red before the consumer change; the second
also ran green after it. The third is the final focused verification command.

```bash
git fetch origin main
git merge origin/main -m 'MODEL-453: merge main before review fixes

Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_pipeline.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_pipeline.py tests/test_social_generator.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py tests/test_release_pipeline.py tests/test_social_generator.py tests/test_release_blog.py tests/test_removed_sources.py
rg -n freshness release_blog/ scripts/social/ scripts/ web/
git diff --check
```

The local artifact audit below checks for private repository locators, private
reading-age tables, individual refresh ages, PR purpose/age tables and the
removed source-association probe. It reports only pass/fail results.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import re
from pathlib import Path

text = Path("docs/evidence/g2-ios/MODEL-453-fix.md").read_text()
checks = {
    "private repository locator": not re.search(
        r"https?://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+-data\b"
        r"|\bgh[^\n]* -R [A-Za-z0-9_-]+/[A-Za-z0-9_-]+-data\b", text),
    "private reading-age distribution": "Private " + "readings |" not in text,
    "individual refresh-PR ages": "Pending age " + "in whole days" not in text,
    "private PR purpose/age table": "| Purpose | Count | " + "Age in days |" not in text,
    "private source association probe": "by_public_" + "source_id" not in text,
}
for name, passed in checks.items():
    print(f"{name}: {'pass' if passed else 'fail'}")
raise SystemExit(0 if all(checks.values()) else 1)
PY
```

The PR body and commit-message hand-offs are `.pr-body.md` and `.pr-commit.txt`
in the worktree root, both untracked. Round two used these GitHub commands for
the existing draft; round three uses git push only:

```bash
gh pr view 980 -R turbobeest/modelspec --json body,isDraft,url,headRefOid,title
CI_LOCAL_SKIP=1 git push -u origin model-453-codex
gh pr edit 980 -R turbobeest/modelspec --body-file /Users/terbeest/dev/worktrees/model-453/.pr-body.md
```

## Round-three verification

Only this evidence document changed; no code or tests changed. The required
source-exclusion check exited 0: `46 passed, 1 skipped in 49.96s`. The skipped
test still requires a built site. Python 3.14.4, pytest 9.1.1 and git 2.50.1
were used; no Node command was run in this round.

The comparison with `76edfde5` confirmed that all 16 requested public command
lines, named regressions and measured results were restored. Round-two consumer
checks remain present. The five-check privacy audit above passed, and every
hexadecimal revision token resolves in the public repository. No GitHub CLI
calls were made in this round; the existing draft PR was updated by git push.

```bash
git show 76edfde5:docs/evidence/g2-ios/MODEL-453-fix.md
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
git diff --name-only 3ad7a4bd
git diff --check
CI_LOCAL_SKIP=1 git push -u origin model-453-codex
```

## Limits

No private checkout, source pages, provider APIs or paid services were accessed
in rounds two or three, and no production configuration was changed. The full repository
suite, site build, remote CI, live nightly execution and deployment were not
verified. No Worker export changed, so the private-data memory probe does not
apply. PR #980 remains a draft for independent review. Round three restores the
public evidence without changing code, tests or the live PR body. Existing
commit history is not rewritten.
