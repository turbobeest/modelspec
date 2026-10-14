# MODEL-390 CI source-kind expectation correction

CI shard 3 at PR #747's `8bd8f1e0346770e9facc9d516580cab55c77cc07`
failed three MODEL-380 metadata tests. They expected the old user-cap source-kind
list, while the reviewed MODEL-390 registry deliberately permits both
`licence_text` and `provider_terms`.

## Revisions and change

Starting SHA: `8bd8f1e0346770e9facc9d516580cab55c77cc07`.
Fetched main SHA: `44f56ec635a88bbba6bcd97123d64ed9f63e5251`.
Merge SHA: `d71c1219f9fccab826ac91ca3a647dcb1d9085fa`.
Verified test correction SHA: `e3baecce8971cde30fea7be176a3e1e200fc5a03`.
Final delivery SHA is reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-390-engine-ci-fix.md`.

The merge of `origin/main` completed without conflicts. The only functional
follow-up edits are two literal expected lists in
`tests/test_model380_licence_metadata.py`, now
`["licence_text", "provider_terms"]`. One assertion covers unknown source kinds;
the other is parametrized over two unread reasons for a known disallowed kind.
All outcome, found-kind, queue and verification-log assertions are unchanged.
Unknown source kinds are still refused; `weights_repository` is still a
mismatch. No implementation or registry edit was made for this follow-up.

## Red-first and final verification

The existing tests reproduced the three CI failures on the merged branch before
editing expectations: **3 failed, 3 passed**, exit **1**, in **0.65 seconds**.
The failing names were:

- `test_core_verification_refuses_licence_absence_without_source_kind`
- `test_known_disallowed_licence_source_kind_remains_mismatch[source_changed]`
- `test_known_disallowed_licence_source_kind_remains_mismatch[mismatch]`

All three had the same expected-list difference. The observed list was
`["licence_text", "provider_terms"]`; the stale expected list was
`["licence_text"]`. The mismatch outcomes and found kinds were already correct.

After updating only those expected lists:

- Metadata module: **6 passed**, exit **0**, in **10.80 seconds**.
- Licence clause module: **285 passed**, exit **0**, in **0.99 seconds**.
- Full UTC suite: **11,027 passed, 9 skipped, 11 warnings**, exit **0**, in
  **1249.65 seconds (20 minutes 49 seconds)**. The warnings are from the CLI's
  unsigned-vocabulary test fixtures.

The local web bundle was rebuilt because the main merge brought frontend and
contract changes. `npm run build` exited **0**. No generated asset was committed.
Ruff reports the same single inherited `I001` import-order finding before and
after the change. No new finding was introduced. Diff whitespace checks passed.

## Reproduction commands

Commands ran in `/Users/terbeest/dev/worktrees/model-390-engine` on
`sparksandsawdust/model-390-licence-readers`. Test process exits were checked
directly; outputs were redirected to logs without a pipe.

```bash
git fetch origin
git merge origin/main -m 'Merge origin/main for MODEL-390 CI compatibility' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_licence_metadata.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The web build used `PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
npm run build` from `web/`. CI inspection used
`gh pr checks 747 -R turbobeest/modelspec --json name,bucket,state,workflow,link`
and `gh run view 38552676886 -R turbobeest/modelspec --job 115814165374 --log-failed`.
The failed check was `pytest shard 3/4`; the aggregate `Run pytest` check also
failed. The logs identified exactly the three reproduced failures.

Tools: Python **3.14.4**, pytest **9.1.1**, repo-environment Ruff **0.16.6**,
Node **v22.22.3**. The Ruff comparison used
`ruff check --output-format json --stdin-filename tests/test_model380_licence_metadata.py -`
on the merge SHA's source and the updated source, comparing rule and stripped
source line. The inherited finding is anchored at `from dataclasses import replace`.

## Scope limits

The PR's observed draft/ready state is preserved. The local main merge was
explicitly requested; no PR merge or ready-state transition was performed.
No Linear action, data-repo edit, private engine-pin edit, production switch,
paid-provider call or WSL gate was attempted. The data #80 offline recheck was
not repeated because this follow-up changes only test expectations.
