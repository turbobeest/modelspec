MODEL-444 execution evidence, October 22 local time / October 23, 2026 UTC.

The weekly rendered re-read now separates re-check attempts from verification decisions. A failed read, missing value, reader error or cite-only result cannot replace an accepted verification. A value mismatch remains a recrawl request for curation. Eligibility uses the pinned snapshot compiler's actual verdict selection, including date/line precedence, counting records, dated-price envelopes and unordered sets. The completeness gate is unchanged.

The public engine change replays verification queue events by their timestamps. Legacy naive timestamps mean UTC; equal instants retain append order. Reading the queue does not rewrite its history. The private workflow restores completed checks only, diverts historical failed verifications to the attempt stream, and never restores unfinished failed-copy changes. The live writer also avoids an intermediate changed event, so an interrupted write cannot leave a failed copy pending for generic verification.

The engine base is `7e3d8ba6c95eac6f03e438366686c5299499b6bc`; the final engine implementation is `8d380496de7f1acad555485b896083879b7a6f32`. Subsequent public commits contain only this evidence. The final public HEAD is recorded in the PR body and executor completion line. Private data main is `ba03e11651513aa108f4031e56622717cf419acf`, and the captured data#103 head is `a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7`. The replacement data head is `be7c5acd4e866cb1e95eb39372ea5739d6161183`, published as draft [data#120](https://github.com/turbobeest/modelspec-data/pull/120). Its `.engine-pin` is the existing main commit `7e3d8ba6c95eac6f03e438366686c5299499b6bc`; the private job also passes against that pin.

The replacement starts from data main. Offline replay uses only the captured report, Git records and current source policies. Of 287 captured results, 223 concern derived copies and 35 require interaction recipes, so 258 are recorded as not reread. The other 29 are cite-only under the current retention policy and source-terms hold. None supplies a new verification. The private receipt maps every one of the 269 captured verification additions and 554 queue events to its captured report row and SHA256. All eight existing main JSONL streams remain byte-identical; the new attempt stream has 287 rows. Eight stale queue events affect four newer claim states. The old restore path also left 16 unfinished checks pending; the new checked-only restore closes that path.

The captured mismatches contain no confirmed changed values: 192 report no observed value, and eight report a source-kind mismatch. The replay does not invent replacement facts. The original 12-credit ledger, rotation state and source hashes remain metadata. The report removes captured diffs and carries the original report hash. The detailed mapping is private at `research/model-444/replay.json`.

The replacement also inherits MODEL-443's reviewed source-terms cleanup. Hash-checked removal deletes 81 artifacts totaling 4,667,409 stored bytes and two preview fields totaling 843 UTF-8 bytes. It preserves 45 unrelated empty artifacts. A second application changes nothing. No source page was fetched or newly retained for this task.

| Regression | Red output against the prior behavior | Green validation |
| --- | --- | --- |
| `test_failed_recheck_is_an_attempt_and_preserves_verified_value`, five variants | Five failures: failed reads append verdicts, or an attempt record is absent | All variants pass, including unreachable, genuine mismatch, reader error, missing value and cite-only |
| `test_reread_eligibility_uses_snapshot_value_and_verdict` | Three failures and two passes: newer mismatch, dated-price hash and unordered-set binding were wrong | All five variants pass |
| `test_pending_failed_verification_restores_as_attempt_only` and allowlist check | Two failures: historical failure restored to the verdict log and attempts path absent | Both pass in the full private workflow suite |
| `test_skipped_recheck_does_not_queue_its_failed_copy` and reader-error pending assertion | Two failures: failed copy remains pending | Both pass |
| `test_interrupted_recheck_does_not_queue_a_failed_copy` and `test_pending_incomplete_recheck_never_restores_failed_copy` | Two failures: live interruption and old pending state restore leave changed events | Both pass |
| Four chronological queue regressions | Four failures and one existing same-time pass | All pass |
| `test_queue_treats_legacy_naive_event_times_as_utc` | `TypeError: can't compare offset-naive and offset-aware datetimes` | Passes with UTC normalization |

Raw red output and focused green output are in [MODEL-444](MODEL-444/). Where pytest emits trailing whitespace, a `.log.gz` archive preserves its exact bytes and the adjacent `.txt` copy removes only that whitespace for review. No existing assertion was deleted to hide a failure. Tests that explicitly expected the superseded behavior now assert preservation of accepted verifications and curation requests. The existing seeded engine fixture now uses its fixed timestamp for checks as well as collection, rather than mixing fixed September events with wall-clock checks.

| Production-path acceptance | Current, 2026-10-23 | Successor, 2027-01-01 |
| --- | ---: | ---: |
| Original data#103 completeness gaps | 113 | No accepted export |
| Corrected completeness gaps | 0 | 0 |
| Catalogue cases passed | 302/302 | 302/302 |
| Additional fixture cases passed | 17/17 | 17/17 |
| Changed catalogue outcomes against main | 0 | 0 |
| Changed fixture outcomes against main | 0 | 0 |
| Steady memory, MiB | 104.646740 | 104.646290 |
| Peak memory, MiB | 107.842503 | 105.491749 |

The original actual vendor exited 2; the separate gated snapshot build exited 1 with exactly 93 mismatch gaps, 15 unreachable-price gaps and five missing facts. The corrected actual vendor, both memory probes and both corpus runs exit 0. The 115 MiB steady limit stays enabled. Snapshot IDs equal main in both periods. HTTP and decision status, contracts, first results, answer kinds, leaders, tie members, result ordering, warnings and fact assurance are all unchanged. There are no changed cases to explain. The [aggregate comparison](MODEL-444/probes/comparison.json) and [probe evidence](MODEL-444/probes/probe-evidence.md) contain the measured detail and exact child commands.

Private vendoring follows `.github/workflows/rank-api.yml`, with the actual `api/worker/vendor.py --data-dir`, the pinned Pyodide runtime, and a throwaway signing key. Public re-vendoring then passes and contains no `bundled_data.py`. All private bundles and exports stay in scratch; no private data enters the public repository.

Tools: Python 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.102.0, Node v22.22.3, Pyodide 0.28.3, pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7. Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`. Every test process exit code was checked directly.

Commands used from the engine worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k test_queue_
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k test_queue_treats_legacy_naive_event_times_as_utc
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_refile_mixed_citations.py
env PYTHONPATH=$PWD MODEL444_DATA_DIR=/tmp/model-444-scratch/data /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider docs/evidence/g2-ios/MODEL-444/replay_checks.py docs/evidence/g2-ios/MODEL-444/retention_checks.py
```

The final queue suite passes 427 tests. All 73 private job and workflow tests also pass against the unmodified main engine pin. The portable replay and retention checks pass seven tests. The final private job, workflow and retention suite passes 84 tests. An earlier run with the replay checks passes 86 tests; the final two interrupted-read regressions also pass in the 84-test run. The public source guard passes 46 tests with one expected skip for the built site because `MODELSPEC_DIST` is unset. Its exact command is `env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py --tb=short`. After adding the raw regression output as tracked text files, `env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source --tb=short` also passes. No full local suite ran.

Commands used from the private scratch clone:

```sh
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py -k failed_recheck --tb=short
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py -k reread_eligibility --tb=short
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread_workflow.py -k 'pending_failed or state_restore_reads_only_allowlisted_data' --tb=short
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py -k 'skipped_recheck or reader_error' --tb=short
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py .github/scripts/tests/test_rendered_reread_workflow.py -k 'interrupted_recheck or incomplete_recheck' --tb=short
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py .github/scripts/tests/test_rendered_reread_workflow.py .github/scripts/tests/test_source_retention_guard.py --tb=short
env PYTHONPATH=/tmp/model-444-scratch/probes/engine-base /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py .github/scripts/tests/test_rendered_reread_workflow.py --tb=short
/Users/terbeest/dev/modelspec/.venv/bin/python .github/scripts/check_linked_data.py --data /tmp/model-444-scratch/data --engine /Users/terbeest/dev/worktrees/model-444
```

Replay and cleanup commands used the scripts preserved beside this report:

```sh
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-444 /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/review/replay_rendered.py --repo /tmp/model-444-scratch/data --target /tmp/model-444-scratch/data --job-script /tmp/model-444-scratch/data/.github/scripts/rendered_reread.py --receipt /tmp/model-444-scratch/review/replay-applied.json --apply
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/review/inherit_retention_cleanup.py --repo /tmp/model-444-scratch/data --target /tmp/model-444-scratch/data --apply
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-444-scratch/review/inherit_retention_cleanup.py --repo /tmp/model-444-scratch/data --target /tmp/model-444-scratch/data --check
```

These results establish local behavior and compatibility with the captured private data. No fresh source accuracy, production deployment, CI result or independent cross-model approval was observed. No provider API call, Firecrawl call, Linear write, main push, force push or merge occurred. Draft PRs require review. The old data#103 branch remains historical and must be replaced by the corrected draft; this task does not approve it for merge.

The replacement data commit was pushed with `CI_LOCAL_SKIP=1 git push -u origin model-444-reread-supersede` from its scratch clone. Its draft was opened from `/tmp` with `gh pr create -R turbobeest/modelspec-data --draft --base main --head model-444-reread-supersede --title 'MODEL-444: preserve accepted verification outcomes during rendered rechecks' --body-file /tmp/model-444-scratch/executor/data-pr.md`. The public branch uses the same push command and an explicit `--draft` PR creation. Both final heads and draft flags are checked with `gh pr view --json number,isDraft,headRefOid,url`. GitHub CLI use totals five calls, including one local version query, below the six-call limit; no polling.

Private scratch clones, replay metadata, generated exports, bundles, predictions and the temporary runtime have been deleted. No matching private replay fixtures remain in pytest temporary directories. Every started test, probe and child process completed. Aggregate evidence and reproduction scripts remain beside this report.

Executed by ChatGPT Codex (GPT-6 Astra); cross-model review by Claude pending.
