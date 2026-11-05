# MODEL-450 round-three execution evidence

Round three addresses REV-970's discovery-identity divergence. The SLO reader
calls the unchanged release pipeline resolver using the selected main revision's
cards and known-identities registry. Ambiguous discoveries stay individually
unknown without adding errors to other releases' measurements. Missing milestone
history and an empty measured cohort still cannot establish success.

Base: `6c156659d9c0690bb29ff0582babb378bd3ccc5e`.
Merged main: `468dd44ceb8600f661479f2f595dac617aff312b`, including #969.
Merge commit: `fa453d86fee3d19282471e84cff749304d0fcbc6`.
Verified implementation: `86577a0fcac3acfe314335926c300d21fbcdd212`.
The final evidence commit's exact SHA is in the untracked `.pr-commit.txt` and
`.pr-body.md` handoffs. This file cannot contain its own commit hash.
Earlier rounds' evidence remains in this file at the base commit.

Public draft: https://github.com/turbobeest/modelspec/pull/970.
Private companion: https://github.com/turbobeest/modelspec-data/pull/130.
No private worktree changes were needed in round three. Activation still requires
the pinned engine to include public #970; this execution did not change the pin.

## Red first

Commands ran from `/Users/terbeest/dev/worktrees/model-450`:

```bash
git fetch origin main
git merge --no-edit origin/main -m 'Merge origin/main for MODEL-450 round 3' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo.py > /tmp/model-450-scratch/r3-resolver-review/report-red.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo_history.py > /tmp/model-450-scratch/r3-executor/history-red.log 2>&1
```

Fetch and merge exited 0 without conflicts. Report red exited 1 with 5 failed,
14 passed. History red exited 1 with 6 failed, 8 passed against the unchanged
reader. The report change had been made before the separate history red run.

| Red-first test | Observed failure | Green behavior |
| --- | --- | --- |
| `test_discovery_identity_matches_release_pipeline` with Llama | One unmatched-discovery history error | `meta/llama-3-1-8b`, matching the pipeline |
| Same test with DeepSeek | `qwen/deepseek-v4-flash-0731` | `deepseek/deepseek-v4-flash-0731` |
| Same test with a slash name | `meta/org-new-model-2-0` | `meta/new-model-2-0` |
| `test_discovery_uses_known_identity_registry_at_selected_main_revision` | `lab/listed-name` | `lab/example`; an unmerged card and registry edit cannot change the historical result |
| `test_unknown_provider_and_ambiguous_aliases_stay_per_release_unknown` | Three unmatched-discovery errors | Three separate unknown discoveries; existing release clocks unchanged |
| `test_ambiguous_discovery_does_not_error_unrelated_release_stages` | One history error | All measured stages stay met, with one unknown discovery per stage |
| `test_public_counts_preserve_ambiguity_without_changing_measured_stage_status` | All four statuses were `error` | Producer error counts and measured statuses survive public import |

The report tests `test_ambiguous_identity_is_unknown_without_poisoning_other_release_measurements`,
`test_only_ambiguous_identities_never_establish_success` in both output modes,
and `test_ambiguity_does_not_hide_other_releases_missing_stage_history` first
failed with an unexpected `identity_unknown` argument. They now pass and verify
that unresolved identities contribute no timestamps or lag findings, an entirely
unresolved cohort cannot succeed, and real history errors remain visible.

## Green and broader verification

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo.py > /tmp/model-450-scratch/r3-resolver-review/report-green.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo_history.py tests/test_release_slo.py > /tmp/model-450-scratch/r3-executor/history-green.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_slo_handoff.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_coverage_slo.py tests/test_data_workflows.py tests/test_release_signals.py tests/test_release_pipeline.py tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py tests/test_engine_pin.py tests/test_removed_sources.py > /tmp/model-450-scratch/r3-executor/focused.log 2>&1
/Users/terbeest/dev/modelspec/.venv/bin/ruff check scripts/slo/releases.py scripts/slo/report.py tests/test_release_slo_history.py tests/test_release_slo.py
git diff --check
```

All exited 0. Report green: 19 passed in 0.47s. Combined history/report green:
33 passed in 2.72s. Broader serial suite: **555 passed, 1 skipped in 65.55s**.
The skip is `test_a_built_dist_carries_no_removed_value`, which needs
`MODELSPEC_DIST`. Existing release pipeline, watcher and engine-pin tests pass.
No pipeline implementation changed. Ruff first reported formatting issues;
after line wrapping, its final check passed. No full local suite ran.

After updating this evidence, the documentation guard also passed:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > /tmp/model-450-scratch/r3-executor/final-doc-guard.log 2>&1
```

Exit 0, 1 passed in 32.94s.

Tools: Python 3.14.4, pytest 9.1.1, ruff 0.16.6, git 2.50.1, gh 2.102.0.
An independent read-only review found no blockers. The resolver import adds no
network calls, filesystem writes or subprocesses at import time.

## Real-data before and after

The comparison uses private main `8ce0b5b56a2cdbbc84449bf6150c436124203dc1`,
104 first-parent commits and 1,385 current cards, at `2026-11-05T03:30:55Z`.
The normal scheduled mode supplies no discovery artifact. A separate probe adds
only the review's three examples, each explicitly dated `2026-11-01T00:00:00Z`.
Those are synthetic discoveries against real data, not observed discovery times.

The before probe uses reader/report modules saved from merge commit `fa453d86`
and its unchanged target configuration. Both probes call the real `releases`
CLI entry point with `--private-detail` and `--counts-out`.

Scheduled mode was identical before and after. Tuples below are
(measured, completed, pending, unknown, late, errors).

| Stage | Scheduled, both runs | With discoveries, before | With discoveries, after |
| --- | --- | --- | --- |
| Card | (1, 1, 0, 0, 1, 1) | (2, 1, 1, 1, 2, 3) | (3, 1, 2, 1, 3, 2) |
| Price | (1, 0, 1, 0, 1, 1) | (3, 0, 3, 0, 3, 2) | (4, 0, 4, 0, 4, 1) |
| Score | (1, 0, 1, 0, 1, 1) | (2, 0, 2, 1, 2, 3) | (4, 0, 4, 0, 4, 1) |
| Decidable | (0, 0, 0, 1, 0, 2) | (0, 0, 0, 3, 0, 3) | (0, 0, 0, 4, 0, 2) |

The three after-discovery IDs match the pipeline's literal expected IDs in the
regression table. The original reader dropped Llama, chose the hosted DeepSeek
card, and retained the organisation prefix in the slash-name slug. The corrected
reader retains all three discoveries. Existing 33 undated cards and missing
import/snapshot history still produce errors; this fix does not invent history.

Exact real-data commands, from the public worktree:

```bash
mkdir -p /tmp/model-450-scratch/r3-real-data
git clone --quiet https://github.com/turbobeest/modelspec-data.git /tmp/model-450-scratch/r3-real-data/modelspec-data
git show fa453d86:scripts/slo/releases.py > /tmp/model-450-scratch/r3-real-data/before_releases.py
git show fa453d86:scripts/slo/report.py > /tmp/model-450-scratch/r3-real-data/before_report.py
git show fa453d86:scripts/slo/targets.yaml > /tmp/model-450-scratch/r3-real-data/targets.yaml
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/r3-real-data/measure.py before
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/r3-real-data/measure.py after
```

Final commands exited 0. The first baseline attempt, before copying
`targets.yaml`, exited 1 before measurement because the copied report module
could not find that adjacent file. The corrected runner and public baseline
modules remain in scratch for review.

The runner sets `GITHUB_REPOSITORY=turbobeest/modelspec-data` and calls
`scripts.slo.__main__.main` with the following arguments for each phase and mode.
Standard output and error were redirected to private logs.

```text
releases --data-dir /tmp/model-450-scratch/r3-real-data/modelspec-data --ref origin/main --private-detail --out /tmp/model-450-scratch/r3-real-data/PHASE-MODE-detail --counts-out /tmp/model-450-scratch/r3-real-data/PHASE-MODE-counts.json --now 2026-11-05T03:30:55Z
```

`PHASE` is `before` or `after`. `MODE` is `scheduled` or
`review-discoveries`; the latter adds
`--discovery /tmp/model-450-scratch/r3-real-data/review-discoveries.json`.
The runner creates that input from the three provider/name examples above,
using `meta` for Llama and the slash name, `deepseek` for DeepSeek, and the
fixed synthetic `first_seen_at` timestamp.

Assertions confirmed identical scheduled counts and exact agreement with all
three pipeline IDs. Exact-path-checked `shutil.rmtree` and `Path.unlink`
removed the clone, four private report directories, four logs and discovery
input. Absence checks passed. Only the runner, public baseline source/config
and sanitized count files/summaries remain. No background command remains.

## Not observed

No live workflow, artifact upload/download, private issue write, deployed handoff,
CI result, site build or four-week SLO attainment was observed. Existing missing
dates and snapshot history remain errors; this fix supplies neither.
The private worktree, `.engine-pin`, frozen data, workflows, Worker exports and
production switches were unchanged. No Worker memory probe was required.
No source-page fetch or retention, vendor spend, Linear write, merge to main,
force push or PR readiness change occurred.
