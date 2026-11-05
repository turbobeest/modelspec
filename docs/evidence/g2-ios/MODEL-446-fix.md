# MODEL-446 execution evidence

Status: blocked pending scope approval for the public isolation-test compatibility update.

Public base: `6815544116839f991c10904772e7357f12d5b566`.
Private base: `c26a2d7b67039dd0ed2490cd740766680c9e454d`.
Public implementation: `c81f05cc46930d443cb7b87fcd4869016aed61e0`.
Private implementation: `09c3af2e241b782bfc0a7dcd8d1a401e6e7b9754`.
Final PR head SHAs are recorded in each worktree's untracked `.pr-commit.txt` after the evidence-only commits.

## Changes

Admission now reads `.engine-pin`, uses the same main-ancestry verification as the other writers, and confirms its checkout HEAD. Workflow health gains the same confirmation. The private pin is `6815544116839f991c10904772e7357f12d5b566`. Public pin tests cover eleven writers, including two newly published mirrors. Rendered re-read retains its existing restoration-before-pin order; assertions for the original eight writers are unchanged.

The private recall PR workflow separately clones public `main` with a sparse checkout of `.github/private-writers`. Its checker compares bytes inside private CI and prints filenames only. It discovers expected mirrors from private engine checkouts and includes every public mirror, so deletions and extra mirrors cannot silently disappear from comparison. Malformed inputs fail without printing YAML contents. Comparing public main separately keeps the check independent of historical mirrors at the engine pin. Merge the public PR before the private PR. Both require human review and merge.

No new secret names were found against the mirrors at the public base. No data files, retained source copies, published contracts, production switches, or Worker exports were changed.

## Red-first evidence

- Public `test_the_engine_pin_step_is_identical_in_every_writer` and `test_the_pin_is_verified_before_the_engine_checkout[admission-drafter]` / `[workflow-health]`: `3 failed, 37 passed`, exit 1, before the workflow changes. The failures exposed different pin blocks, admission's checkout confirmation path, and workflow health's missing confirmation.
- Private `test_engine_pin_and_private_data_are_isolated` and `test_engine_pin_accepts_only_main_history[True]`: `2 failed, 21 passed`, exit 1. A valid `.engine-pin` with an unrelated `ENGINE_SHA` failed under the original workflow. After the change: `23 passed`, exit 0.
- New private `.github/scripts/tests/test_writer_mirrors.py`: `9 failed`, exit 1 before the checker and CI step existed; `9 passed`, exit 0 afterward. The final private run includes all ten mirror tests, including malformed YAML privacy coverage.
- The new checker against the unsynchronized working trees exited 1 and named `daily-research.yml`, `price-reread.yml`, and `recall-private.yml` as mismatches. After synchronization: `11 public writer mirror(s) match private workflows.`, exit 0.
- A temporary copy of the synchronized public mirrors had `# fabricated MODEL-446 mismatch` appended to `admission-drafter.yml`. The same CLI exited 1 with `::error::admission-drafter.yml: public mirror differs from private workflow`.

## Commands and results

Tools: Python 3.14.4, pytest 9.1.1, Git 2.50.1, Bash 5.3.9, GitHub CLI 2.102.0. Tests ran serially using the existing Python environment. The workflow uses Python 3.11; that interpreter was not exercised locally.

Public working directory: `/Users/terbeest/dev/worktrees/model-446`.
Private working directory: `/Users/terbeest/dev/worktrees/data-model-446`.
Scratch clone: `/tmp/model-446-scratch/private-baseline`.

```bash
git ls-remote origin refs/heads/main
git log --all --format='%H %s' --grep='#914' -n 3
git merge-base --is-ancestor f61c3d6a930248786a8d3303c75d38317281cfb5 6815544116839f991c10904772e7357f12d5b566
```

All exited 0. Public main was the requested pin. Commit `f61c3d6a930248786a8d3303c75d38317281cfb5` is #914 and is an ancestor of the new pin.

```bash
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-446-scratch/private-baseline
# From the private worktree:
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_linked_data.py --engine /Users/terbeest/dev/worktrees/model-446 --data /tmp/model-446-scratch/private-baseline
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/model-446/scripts/prepare_data_writer.py --engine /Users/terbeest/dev/worktrees/model-446 --data /tmp/model-446-scratch/private-baseline
# From the scratch clone, before bumping .engine-pin:
env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests tests/test_decision_sources.py tests/test_decision_verify.py tests/test_decision_model.py tests/test_decision_snapshot.py tests/test_subscription_availability.py tests/test_subscription_availability_reader.py tests/test_slice1_offerings.py
env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/recall_run.py --root "$PWD" --output-dir /tmp/model-446-scratch/root/private-recall
/Users/terbeest/dev/modelspec/.venv/bin/python reports/recall/check.py --report-dir /tmp/model-446-scratch/root/private-recall --baseline reports/recall/baseline.json --approved-baseline reports/recall/baseline.json --summary /tmp/model-446-scratch/root/recall-summary.txt
```

All exited 0. The linked-data guard covered 14 paths. Pre-bump tests: `1095 passed, 18 skipped`. Recall: 16 pass, 4 partial, 0 fail, no regression question IDs. The private clone had the unchanged data at the private base and engine code from the requested public pin. After implementation, only the changed workflow, checker, test, and pin files were copied into that clone for the final repeat of the same CI-equivalent test command.

```bash
# Public red-first and final pin checks:
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py
# Private red-first and focused green checks:
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_admission_drafter_workflow.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_writer_mirrors.py
# Private drift check, run before and after mirror synchronization:
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-446/.github/private-writers --workflows .github/workflows
# Fabricated mismatch, from public worktree:
/Users/terbeest/dev/modelspec/.venv/bin/python -I /Users/terbeest/dev/worktrees/data-model-446/.github/scripts/check_writer_mirrors.py --mirrors /tmp/model-446-scratch/root/mutated-mirrors --workflows /Users/terbeest/dev/worktrees/data-model-446/.github/workflows
# Broader public focused run:
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_writer_artifacts.py tests/test_prepare_data_writer.py tests/test_research_workflow.py tests/test_research_failure_safety.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_removed_sources.py
```

Final public pin suite: `40 passed`, exit 0. The final `tests/test_removed_sources.py` run, after staging both new mirrors and this evidence, passed with `46 passed, 1 skipped`, exit 0. Final private CI-equivalent suite: `1105 passed, 18 skipped`, exit 0.

The broader public run exited 1: `17 failed, 575 passed, 1 skipped`. Sixteen failures are in unchanged `tests/test_writer_isolation.py`. Synchronizing daily research replaces its inline validation with a separately tested private guard, while this public suite uses daily's link step as its shared executable validation fixture. Adding the existing rendered workflow also exposes its bounded scraper step to the public secret allowlist. These tests require a focused compatibility update that retains their executable code/symlink rejection coverage and constrains the existing rendered step. Scope approval for that additional test file was requested and has not arrived.

The remaining failure is unchanged `tests/test_price_reread_fallback.py::test_cli_fallback_writes_only_an_artifact_and_redacts_error_responses`: expected prior known spend 7, observed 0. Its fixture fixes the ledger month at `2026-10`; the CLI uses the current month, November, and rejects that historical ledger. No relevant source or test changed:

```bash
git diff --exit-code 6815544116839f991c10904772e7357f12d5b566 -- tests/test_price_reread_fallback.py scripts/price_reread.py scripts/price_reread_fallback.py
```

Exit 0. No existing tests were skipped, weakened, or removed to hide these failures.

## Limits

The full local suite, deployed Actions runs, production admission execution, and Python 3.11 runtime were not observed. No paid providers or scrape services were called. The Worker memory probe does not apply because no export fields or serving bundle changed. Independent cross-model review remains pending. Scratch private data is deleted after verification. Final draft links and push results are recorded in the worktree handoffs and executor report.
