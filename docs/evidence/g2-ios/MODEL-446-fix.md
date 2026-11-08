# MODEL-446 execution evidence

Local focused checks pass. Independent cross-model review and live CI remain pending. The round-2 spec authorized the additional test changes that blocked round 1.

| Revision | Public | Private |
| --- | --- | --- |
| Original base | `6815544116839f991c10904772e7357f12d5b566` | `<private revision at assessment time>` |
| Round-2 base | `f470342cd088ec9b90d092088ae5b844ac802caf` | `<private revision at assessment time>` |
| Final implementation | `a4618bc20c826a5e286c3b85d641c3ca47c0dc48` | `<private revision at assessment time>` |

Evidence-only commits follow these implementation commits. Each worktree's untracked `.pr-commit.txt` records its final PR head SHA. Draft PRs: [public #969](https://github.com/turbobeest/modelspec/pull/969), [private #127](https://github.com/turbobeest/modelspec-data/pull/127). Merge public first, then private, after human review. The private check intentionally compares with public main independently of the engine pin.

## Implementation and preserved checks

Admission reads `.engine-pin`, verifies main ancestry, and confirms the checkout HEAD. Workflow health has the same confirmation. The pin is `6815544116839f991c10904772e7357f12d5b566`; `git merge-base --is-ancestor f61c3d6a930248786a8d3303c75d38317281cfb5 6815544116839f991c10904772e7357f12d5b566` exited 0, proving it includes #914. Public tests cover all eleven writer mirrors.

The private recall PR workflow compares mirror bytes with a separate sparse checkout of public main. The checker includes every public mirror and discovers private engine writers, so missing mirrors fail. Only filenames appear in mismatch output; malformed YAML produces a generic error. No new secret names appeared in the public mirrors.

Round 2 changes only tests and evidence:

- `_canonical_link()` now selects the unchanged inline guard in price re-read. Every original executable rejection assertion remains: planted code, symlinks, required directories, empty paths, paths outside the checkout, and planted `sitecustomize`/import-path isolation.
- Daily research must identify its filename, workflow, and job, then run the exact isolated private guard immediately before the exact link step. Tests reject removing, moving, conditioning, changing, or tolerating failure of the guard, and inserting restoration between guard and link.
- The price reconfirmation exception requires its exact filename, workflow, job, step, condition, command, and data working directory. Other private script commands remain rejected.
- Rendered re-read may receive its scraper credential only in the exact existing step, under the scheduled-main-first-attempt gate, existing permissions, environment, and data working directory. Mutations of these constraints and reuse in another file fail. Existing price and curation constraints remain.
- Known-workflow mutation tests now supply their filenames. `_with_command()` first asserts the unchanged daily workflow passes, preventing unrelated private-guard errors from satisfying a mutation assertion. The positive restore-before-link test supplies the daily filename too. The generic no-Python test remains independent of workflow identity.
- `test_cli_fallback_writes_only_an_artifact_and_redacts_error_responses` monkeypatches `price_reread.datetime` with a subclass returning October 15, 2026 from `now()`. Its October fixture and all accounting/redaction/no-write assertions are unchanged; inherited datetime parsing remains available. No production clock API changed.
- Nine additional private guard cases execute the real CLI against root symlinks, missing required directories, empty/invalid path lists, and planted `sitecustomize` with data as both cwd and `PYTHONPATH`.

The original inline outside-checkout test remains against price. The private guard confines paths to its resolved `--data` argument rather than reading `GITHUB_WORKSPACE`; its tests prove that actual boundary. Daily's exact workspace-root guard/link steps bind normal Actions execution. No claim is made that the two guards handle a forged workspace environment identically.

## Red and green results

| Check | Red evidence | Green evidence |
| --- | --- | --- |
| Original public pin suite | 3 failed, 37 passed, exit 1 | 40 passed, exit 0 |
| Original private admission suite | `test_engine_pin_and_private_data_are_isolated` and `test_engine_pin_accepts_only_main_history[True]`: 2 failed, 21 passed, exit 1 | 23 passed, exit 0 |
| New private mirror checker | 9 failed before checker/CI step existed, exit 1 | All 10 mirror cases pass in private focused checks |
| Real mirror drift | daily, price, and recall mismatches, exit 1 | All 11 match, exit 0 |
| Fabricated mirror edit | Appending `# fabricated MODEL-446 mismatch` to a temporary admission mirror made the CLI exit 1 and name only `admission-drafter.yml` | Unmodified mirrors exit 0 |
| Round-2 unchanged isolation plus clock test | 17 failed, 205 passed, exit 1 | Touched files: 411 passed, exit 0 |
| Daily/rendered regression cases | 26 failed against the old guard expectations, exit 1 | Included in 583 passing public tests |
| Price reconfirmation regression cases | 10 failed against the old private-command rejection, exit 1 | Included in 583 passing public tests |
| Full focused public writer/pin set | Round 1 had 17 failures | 583 passed, exit 0 |
| Private guard and workflow set | Additional cases cover already-correct guard behavior | 130 passed, exit 0 |
| Final source-exclusion check | Round 1 also passed | 46 passed, 1 skipped, exit 0 |

Before the original pin bump, the private CI-equivalent tests had `1095 passed, 18 skipped`, exit 0. Recall had 16 pass, 4 partial, 0 fail and no regressions against the unchanged private baseline. After round-1 implementation, the same CI-equivalent suite had `1105 passed, 18 skipped`, exit 0. No data files were changed for validation.

## Reproduction commands

Tools: Python 3.14.4, pytest 9.1.1, Git 2.50.1, Bash 5.3.9. Public cwd is `/Users/terbeest/dev/worktrees/model-446`; private cwd is `/Users/terbeest/dev/worktrees/data-model-446`. Test commands ran serially. Exit statuses were captured directly, without a pipeline.

```bash
# Round-2 reproduction, before edits, public cwd: exit 1.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_price_reread_fallback.py::test_cli_fallback_writes_only_an_artifact_and_redacts_error_responses
# New regression cases before updating the guard: exit 1 for each command.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py -k 'daily_research_requires or only_daily_research or rendered_secret_requires'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py -k 'price_reconfirmation_allows'
# Touched files after fixes: 411 passed, exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_price_reread_fallback.py
# Broader focused public set after supplying known filenames: 583 passed, exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_writer_artifacts.py tests/test_prepare_data_writer.py tests/test_research_workflow.py tests/test_research_failure_safety.py tests/test_price_reread.py tests/test_price_reread_fallback.py
# After restoring the generic no-Python case's original call: 1 passed, exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py::test_a_job_that_runs_no_python_needs_no_link_step
# Final source-exclusion check after staging evidence:
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py

# Disposable private setup, each command exit 0:
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-446-scratch/private-baseline
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/prepare_data_writer.py --engine "$PWD" --data /tmp/model-446-scratch/private-baseline
# Copy only branch changes under .github/ and .engine-pin into the clone.
# Run from the composed clone: 130 passed, exit 0.
env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_linked_data_guard.py .github/scripts/tests/test_price_reread_guard.py .github/scripts/tests/test_rendered_reread_workflow.py .github/scripts/tests/test_writer_mirrors.py .github/scripts/tests/test_admission_drafter_workflow.py
# Private cwd, mirror parity:
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-446/.github/private-writers --workflows .github/workflows
```

## Limits and handoff

The full local suite, deployed Actions runs, production admission execution, and Python 3.11 runtime were not observed. No paid providers or scrape services were called. No data files, retained source copies, contracts, production switches, or Worker exports changed. No memory probe is needed for these test-only changes. Scratch private data is deleted after verification. Both PRs remain drafts. Updated, cross-linked descriptions are in `.pr-body.md`; the execution brief prohibits `gh pr edit`, so the orchestrator must apply those handoffs to the live descriptions.
