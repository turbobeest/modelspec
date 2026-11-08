# MODEL-455 round-four verification

Observed 2026-11-08. Public draft PR #992; companion private draft PR #134.
Base: `79f5de8becdc17e7a58752cd2a4ad8241f31c2d2`.
Merged and scanned public main: `37a91865beba12ed5f8cf1dd505a8526d0c9278c`.
Final mirror implementation: `967cee4a0300bf9c45ffeb8ff44cbabac4788017`.
The final evidence-only commit is recorded in `.pr-commit.txt` and the PR head.
Private revisions and baseline hashes remain in the private repository.

The guard now alerts only on findings absent from the reviewed private
baseline. Existing public history is left intact. Baseline entries are SHA-256
hashes of compact JSON containing the finding kind, exact source path or PR
identity, and normalized token. No raw token or path is stored. SHA tokens
normalize case while keeping abbreviation lengths distinct. Card values use
the model ID and canonical matched value; any new value makes its row new.
Line movement and Markdown emphasis do not create new findings. Historical
matches still protect emitted paths. Missing or malformed baselines fail
closed. Baseline generation is explicit and never runs in the scheduled job.

The workflow fetches private PR-head refs before resolving commits. Its token
is passed through the Git subprocess environment, never persisted in Git
configuration or printed. Reports state "N historical, ignored". Only new
findings produce exit 1 and satisfy the existing private-alert condition.

## Red and green evidence

| Regression | Red result, exit 1 | Green result, exit 0 |
| --- | --- | --- |
| `test_baseline_ignores_known_tokens_but_new_token_in_same_file_fails` | `1 failed in 0.18s`; baseline option absent | `1 passed in 0.52s`, then included in combined suite |
| `test_baseline_matches_individual_card_values_and_preserves_new_values_in_same_row` | `1 failed in 0.23s`; baseline omitted card fingerprints | Included in combined suite |
| Workflow tests selected by `private_pull or historical_count or real_scan` | `5 failed, 13 deselected in 1.51s`; no PR fetch, no historical count, old and new tokens both counted | Full workflow file: `18 passed in 3.42s` |

The combined data suites passed `104 passed in 17.84s`. They include all prior
path-redaction regressions and new coverage for raw-token-free baselines,
path/PR identity, line/case normalization, new tokens in old files, mixed card
rows, invalid baselines, unchanged baseline on failed scan, private-only
baseline output, deterministic generation, and historical path redaction.
Existing assertions were retained.

Public suites passed `389 passed, 1 skipped in 61.46s`. The skip requires a
built dist. Pytest ran serially and each direct exit code was checked.

## Current-main observation

Fresh private and public clones were used. Private PR-head fetching imported
134 refs. All 4 open public PR bodies were captured with one gh call. Before
baselining, the scan found 187 private SHA occurrences and 0 card rows, exit 1.
Explicit generation wrote 134 unique fingerprints, exit 0. The subsequent
scan against the committed baseline returned, exit 0:

```json
{"counts":{"private_commit":0,"private_card_value":0,"total":0},"findings":[],"historical":187}
```

A structural and token audit found 134 sorted unique 64-character lowercase
hex digests and no raw candidate hex tokens from the scanned evidence or PR
bodies in the baseline. The baseline is committed only in the private repo.

The public ticket checkout and revised PR-body handoff were also scanned,
substituting the handoff for PR 992 in the captured open-PR input. That check
returned the same zero-new, 187-historical report, exit 0.

Both branches merged `origin/main` without conflicts. The existing main-to-main
mirror check passed for 14 workflows. The updated ticket branches passed for
15 workflows, including the byte-identical guard mirror. The earlier
`model-week.yml` mismatch is resolved by the main merges.

## Commands and limits

Versions: Git 2.50.1, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Node v22.22.3.
No gh version call was spent. The existing PRs remain drafts; no new PR was
created. Root `.pr-body.md` and `.pr-commit.txt` are untracked handoffs.

```sh
# In each ticket worktree. Merge messages end with the required co-author.
git fetch origin main
git merge --no-edit -m 'Merge origin/main for MODEL-455 round four

Co-Authored-By: ChatGPT Codex <noreply@openai.com>' origin/main
# Data worktree, red runs.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_public_leak_guard.py::test_baseline_ignores_known_tokens_but_new_token_in_same_file_fails
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_public_leak_guard.py::test_baseline_matches_individual_card_values_and_preserves_new_values_in_same_row
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_public_leak_guard_workflow.py -k 'private_pull or historical_count or real_scan'
# Data worktree, final focused and broader touched suites.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_public_leak_guard.py .github/scripts/tests/test_public_leak_guard_workflow.py .github/scripts/tests/test_writer_mirrors.py
# Public worktree.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_workflow_dependencies.py tests/test_removed_sources.py
# Data worktree, real clones and baseline.
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/model-455-r4-executor/private
git -C /tmp/model-449-scratch/model-455-r4-executor/private fetch --quiet origin '+refs/pull/*/head:refs/remotes/origin/pull/*'
git clone --quiet https://github.com/turbobeest/modelspec.git /tmp/model-449-scratch/model-455-r4-executor/public
# From /tmp: first of three gh calls.
gh pr list -R turbobeest/modelspec --state open --limit 1000 --json number,body > /tmp/model-449-scratch/model-455-r4-executor/public-pr-bodies.json
# Data worktree. First command exits 1; generation and baselined scan exit 0.
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/public_leak_guard.py --public-repo /tmp/model-449-scratch/model-455-r4-executor/public --private-repo /tmp/model-449-scratch/model-455-r4-executor/private --pr-bodies /tmp/model-449-scratch/model-455-r4-executor/public-pr-bodies.json --counts-only
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/public_leak_guard.py --public-repo /tmp/model-449-scratch/model-455-r4-executor/public --private-repo /tmp/model-449-scratch/model-455-r4-executor/private --pr-bodies /tmp/model-449-scratch/model-455-r4-executor/public-pr-bodies.json --write-baseline /tmp/model-449-scratch/model-455-r4-executor/private/.github/public-leak-baseline.json --counts-only
cp /tmp/model-449-scratch/model-455-r4-executor/private/.github/public-leak-baseline.json .github/public-leak-baseline.json
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/public_leak_guard.py --public-repo /tmp/model-449-scratch/model-455-r4-executor/public --private-repo /tmp/model-449-scratch/model-455-r4-executor/private --pr-bodies /tmp/model-449-scratch/model-455-r4-executor/public-pr-bodies.json --baseline .github/public-leak-baseline.json
# Public ticket checkout and local handoff-body verification, exit 0.
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/public_leak_guard.py --public-repo /Users/terbeest/dev/worktrees/model-455 --private-repo /tmp/model-449-scratch/model-455-r4-executor/private --pr-bodies /tmp/model-449-scratch/model-455-r4-executor/public-handoff-bodies.json --baseline .github/public-leak-baseline.json
# Mirror checks, all exit 0.
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /tmp/model-449-scratch/model-455-r4-executor/public/.github/private-writers --workflows /tmp/model-449-scratch/model-455-r4-executor/private/.github/workflows
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-455/.github/private-writers --workflows .github/workflows
cmp .github/workflows/public-leak-guard.yml /Users/terbeest/dev/worktrees/model-455/.github/private-writers/public-leak-guard.yml
git diff --check
# Version checks.
git --version
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/dev/modelspec/.venv/bin/python -c 'import yaml; print(yaml.__version__)'
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
# In each worktree, after focused tests.
CI_LOCAL_SKIP=1 git push -u origin model-455-public-leak-guard
# From /tmp: remaining two gh calls. Responses stay in private scratch files.
gh pr view 134 -R turbobeest/modelspec-data --json number,url,state,isDraft,baseRefName,headRefName,headRefOid,body > /tmp/model-449-scratch/model-455-r4-executor/data-pr-state.json
gh pr view 992 -R turbobeest/modelspec --json number,url,state,isDraft,baseRefName,headRefName,headRefOid,body > /tmp/model-449-scratch/model-455-r4-executor/public-pr-state.json
```

No hosted workflow, GitHub Actions token authentication, real alert delivery,
full suite, Linux/Python 3.11 execution, built site or deployed behavior was
observed. The PR-ref test uses real local Git transport; the live fetch uses
operator Git credentials. Public main and open PR bodies are a captured
observation, not a continuous watch. No retained source data or Worker export
was changed by this ticket. Only this round's own scratch directory is removed
after verification. No background process is left running.
