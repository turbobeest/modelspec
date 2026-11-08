# MODEL-453 review fixes

Assessment: 2026-11-08. Review: REV-980-cx, PR #980.
Round-two base: `76edfde510cb1613287bbcb4810a827fb05bda82`.
Merged main: `9e7a18eff326f5d2806b40bf6d0af1b039fd6a19`.
Merge commit: `4c6b36977a4aaedbb235604823ca60c0dbfcd178`.
Final implementation: `092aa5dbf6dee0103d7a0936dd39e5a07bca0968`.
The subsequent evidence-only commit is the final PR head, recorded in the PR
body and executor completion marker. Resolve it with `git rev-parse HEAD` in
the PR checkout.

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

The live PR body was read before editing. It contained aggregate freshness
counts and public commit identifiers, without the flagged private metadata.
The updated body describes the final implementation and review fixes.

## Red-first checks

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

## Commands and environment

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
in the worktree root, both untracked. The GitHub commands use the existing draft:

```bash
gh pr view 980 -R turbobeest/modelspec --json body,isDraft,url,headRefOid,title
CI_LOCAL_SKIP=1 git push -u origin model-453-codex
gh pr edit 980 -R turbobeest/modelspec --body-file /Users/terbeest/dev/worktrees/model-453/.pr-body.md
```

## Limits

No private checkout, source pages, provider APIs or paid services were accessed
in this round, and no production configuration was changed. The full repository
suite, site build, remote CI, live nightly execution and deployment were not
verified. No Worker export changed, so the private-data memory probe does not
apply. PR #980 remains a draft for independent review. This revision changes
current evidence and PR text without rewriting existing commit history.
