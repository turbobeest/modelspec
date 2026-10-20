# MODEL-432 executor evidence

## Round 2, October 20, 2026

The changes requested by `MODEL-432-r2.spec.md` and `REV-860.verdict.md`
are implemented. This section supersedes the implementation status below;
the original execution record remains as history. The future live recall
measurement has not occurred.

- Starting SHA: `3b560b28666f18d38e13ab1ce02f5285e55d64a2`.
- Final implementation SHA: `3a33d9a3c140de70a6140d3eb71ef7d63916b5ac`.
- Delivery adds only this evidence update after the implementation commit.
  Resolve its final SHA with `git rev-parse model-432-release-watch-filter`;
  the executor receipt records the exact delivery SHA. This file cannot
  contain the hash of its own commit.
- Worktree and branch remain `/Users/terbeest/dev/worktrees/model-432` and
  `model-432-release-watch-filter`.
- `git fetch origin main` followed by `git merge --no-edit origin/main`
  returned `Already up to date.`, exit 0, before implementation.
  `git merge-base --is-ancestor origin/main HEAD` also returned 0.
- Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3, Ruff 0.16.6,
  Git 2.50.1. No Node tooling was used.

### Corrections and red-first evidence

| Defect | Test | Red output against unchanged production code | Green output |
| --- | --- | --- | --- |
| Artifact tokens inside model names are dropped | `test_huggingface_model_names_with_artifact_tokens_stay_discoveries`, seven cases | Each name was absent from discoveries, for example `assert 'ERNIE-5-Docs' in {'lfm-2'}` | All seven pass |
| Rejected observations are absent from summaries | `test_summary_lists_every_rejected_item_with_reason_and_source` | `AssertionError: assert '### Rejected (not filed)' in text` | Pass; all four observations include name, reason, source ID and URL |
| No scripted comparison of retained inputs with card-added dates | `test_recall_compares_30_days_of_retained_inputs_with_card_additions` and `test_recall_reports_artifact_gaps_and_outages_instead_of_claiming_full_coverage` | `SystemExit: 2`, `unrecognized arguments: --recall-end 2026-11-20 --catalogue-root ...` | Both pass |

The filter red run produced **8 failed, 16 deselected**, exit 1. It covered
`ERNIE-5-Docs`, `Pixtral-Docs`, `ocr-doc`, `client-embed-1`, `guide-7b`,
`Example-LM` and `agent-sdk-model-7b`. An earlier attempt accidentally gave
OpenRouter an empty feed and failed the existing outage guard. The fixture
was corrected and the eight intended assertions failed before production
code changed.

The rule now rejects only whole artifact tokens, tokens paired with the
provider name, and the existing exact IBM example rule. The 222 ambiguous
synthetic negatives remain in the per-source fixture as positive candidates.
Another 222 whole-token negatives preserve rejection coverage across all
74 sources. All 542 observations have explicit expected identities or
rejection labels. No assertions were deleted to hide the old behavior.
The triage regression likewise retains `acme-sdk-2` as a possible model
and checks that `acme-sdk` is noise. Its dry-run-only implementation did
not change.

The recall red run produced **2 failed, 24 deselected**, exit 1. Its Git
fixture and retained JSON reports verify:

- The UTC window includes October 21 and excludes November 20.
- Reports outside the window do not rescue an otherwise missing card.
- Repeating an artifact does not inflate counts.
- Two of four in-window card additions match accepted signals, recall 0.5.
  One missing card has a rejected observation; the other has no observation.
- A packaging alias matches its card. A feature-branch card is counted at
  its first-parent merge date, even with an older author-branch commit.
- Later card edits do not alter the addition's identity.
- Sparse inputs expose 29 missing days and retain a source outage.
- The standalone CLI reports null recall when no cards were added.
- Shallow catalogue history and output paths inside the catalogue are refused.
- Private card bodies do not appear in JSON or Markdown output.

The command is documented in [release-watch.md](../../release-watch.md).
It runs on local retained artifacts and local catalogue Git history, has
no filing mode, and is not scheduled. Run it on or after November 20 with
`--recall-end 2026-11-20`, or choose a later 30-day window. Backfills and
seed imports remain in the denominator for explicit review.

### Verification commands and results

All pytest invocations were serial. Exit codes came directly from the
process, with no output pipe.

```bash
git fetch origin main
git merge --no-edit origin/main
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_release_watch_filter.py -k 'artifact_tokens or every_rejected'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_release_watch_filter.py -k 'recall_compares or recall_reports'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py tests/test_release_signals.py tests/test_release_pipeline.py tests/test_cite_only_retention.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/release_watch.py scripts/release_watch_filter.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
git diff --check
git merge-base --is-ancestor origin/main HEAD
git --version
/Users/terbeest/dev/modelspec/.venv/bin/python -c 'import sys, pytest, httpx, yaml; from importlib.metadata import version; print(sys.version); print("pytest", pytest.__version__, "httpx", httpx.__version__, "PyYAML", yaml.__version__, "Ruff", version("ruff"))'
gh pr view 860 --repo turbobeest/modelspec --json number,url,isDraft,headRefName,headRefOid,baseRefName
```

After the filter correction, the filter/precision/triage run passed
**120 tests in 2.01s**, exit 0. The four focused suites passed **155 tests
in 9.27s**, exit 0. The final broader run passed **256 tests in 18.02s**,
exit 0, including the MODEL-421 outage and dry-run triage regressions.
Ruff and `git diff --check` passed, exit 0.

Intermediate validation also caught an incorrect bulk fixture replacement
and a test assertion that compared equivalent `Z` and `+00:00` timestamp
spellings as strings. Both were corrected; the final run above includes
the corrected fixture and a comparison of parsed timestamps.

PR inspection confirmed #860 is DRAFT on the assigned branch, based on
main. Delivery uses `CI_LOCAL_SKIP=1 git push -u origin
model-432-release-watch-filter` after the checks above. There is no new
PR, ready action, merge, force-push or Linear write.

### Not observed in round 2

- A real 30-day future artifact corpus, live precision or live recall.
- Private catalogue contents or live publisher requests. The new comparison
  was verified against synthetic retained artifacts and a local Git fixture.
- The full repository suite, both site builds, or final remote CI results.
- Live issue filing, deployment, production switch changes or provider spend.

The retained JSON contains normalized post-baseline observations, not raw
source responses. A complete set of daily artifacts cannot establish that
all scheduled runs or every source extraction were captured. The command
reports these limits rather than claiming complete release recall.

## Original execution record

The filter, grouping, offline replay and dry-run triage are implemented.
Acceptance remains blocked on the complete historical replay: the watcher
did not retain its original inputs, and it did not exist for the first nine
days of the requested window. The committed archive is explicitly a replay
of previously emitted discovery outputs, not all source inputs.

## Revision and environment

- Base SHA: `3c8042a11aa47e8577559e01f71379119bda2cec`.
- Final tested implementation SHA: `6100a2f18447cbc0f630ecdd56a7e13001769c00`.
- Final delivery SHA: resolve `git rev-parse model-432-release-watch-filter`
  after the evidence-only commit. The exact hash is also printed in the
  executor's `CODEX_EXEC_DONE` receipt. A commit cannot contain its own hash.
- Worktree: `/Users/terbeest/dev/worktrees/model-432`.
- Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3, Ruff 0.16.6.
- Git 2.50.1, GitHub CLI 2.102.0. No Node tooling was used.

The implementation is confined to watcher scripts, its workflow, tests and
documentation. No Worker exports, snapshot fields, production switches,
ranking, legal text, frozen model cards or signal contracts changed.

## Observed behavior

- The CLI filters explicit non-model names before either sink.
- Release identities group known spellings, mirrors, precision packaging
  and training endpoints of the same recipe. Sizes, base/tuned distinctions,
  unknown dated revisions and different experiment recipes remain distinct.
- A new issue includes every grouped source reference and a draft stub.
  Dates, type and parameter count stay null.
- Historical open and closed issue IDs use the same canonicalization as new
  signals. Repeated candidates in one filing call are also deduplicated.
- Reports retain accepted and rejected normalized observations. The workflow
  uploads its JSON and Markdown for 45 days, including failed runs.
- Replay has no filing mode. Triage has no network or apply operation.
  Malformed signals stay visible for manual review; output paths cannot
  overwrite the input export.

Queue payloads retain their existing six fields. Their group evidence and
drafts are in the workflow artifact, joined by `signal_id`; they are not
additional KV fields. Historical queue markers are not migrated. Existing
issue bodies are not rewritten when a later source joins the group.

## Red-first results

Production code was unchanged during the initial red run. The filter and
triage suites produced **27 failed in 0.56s**, exit 1.

| Defect | Red-first test | Observed red output | Green |
| --- | --- | --- | --- |
| One release emitted as three spellings/packages | `test_cli_groups_sources_and_packaging_with_evidence_and_a_draft` | Expected one signal; received three, including `lfm2-5-24b-a2b-bf16` | Pass |
| SDK, blog and docs candidates emitted | `test_cli_drops_non_model_items_but_keeps_distinct_releases` | Eight discoveries instead of four release identities | Pass |
| Legacy alias creates another issue | `test_existing_legacy_alias_issue_prevents_a_second_issue` | Expected GET only; attempted POST | Pass |
| Aliases and mirrors lack shared identity | `test_release_aliases_share_an_identity`, `test_mirrors_share_the_upstream_release_without_merging_other_labs` | `ModuleNotFoundError: scripts.release_watch_filter` | Pass |
| Real minor versions need separate identities | `test_named_minor_versions_sizes_and_tuning_are_distinct` | Filter module absent | Pass |
| New issue lacks a draft | `test_issue_contains_draft_even_when_called_without_a_report` | `### Draft card` absent from created body | Pass |
| No retained replay archive | `test_workflow_keeps_normalized_reports_for_a_30_day_replay` | Expected one artifact step; found zero | Pass |
| No offline classification command | All initial `test_release_watch_triage.py` cases | Module absent; executable CLI returned 2 | Pass |

Review then exposed two overly broad rules in the initial implementation.
New counterexamples failed before the corrections:

| Defect | Test | Observed red output | Green |
| --- | --- | --- | --- |
| Different dated models merged | `test_separately_released_dated_models_are_not_aliases` | June and October Claude 3.5 Sonnet returned the same identity | Pass |
| No offline replay CLI | `test_offline_replay_reproduces_groups_without_fetch_or_post` | `unrecognized arguments: --replay`, exit 2 | Pass |
| Different experiment recipes merged | `test_experiment_recipes_and_unverified_exports_remain_distinct` | Dense and MoE recipes both returned `loopedlm-p1` | Pass |
| Same-recipe endpoints lacked the intended narrow identity | `test_release_aliases_share_an_identity[ifm-names3-expected3]` | Returned `loopedlm-p1` instead of `loopedlm-p1-dense-d112` | Pass |
| Standalone triage imports failed | `test_triage_standalone_cli_does_not_need_pythonpath` | Import failure without repository path injection | Pass |
| Malformed URL aborted triage | `test_malformed_signal_url_stays_real_for_manual_review` | Unhandled URL `ValueError` | Pass |
| Triage overwrote source/output files | `test_triage_refuses_output_collisions_without_changing_files`, three cases | `DID NOT RAISE SystemExit` | Pass |

These later red runs produced 2, 2 and 5 failures respectively, each exit 1.
The early broad experiment expectations were corrected after reviewing the
publisher's model descriptions; no pre-existing repository test was weakened.

The final broader focused run produced **244 passed in 11.22s**, exit 0.
After the final replay-summary wording change, the watcher and filter suites
produced **47 passed in 5.52s**, exit 0. Ruff and `git diff --check` passed.
The four predicted pytest shard durations remained balanced at about
3,961.7 seconds each. The full local suite was not run, per the ticket.

## Historical replay and card comparison

The window is September 20 through October 20, 2026. The single authorized
issue listing returned 177 open discovery issues, created September 30
through October 20. Their source split is 158 Hugging Face, six OpenRouter
and 13 lab-page discoveries.

[Normalized public inputs](MODEL-432-discovery-inputs.json) contain only
public GitHub discovery metadata, including original IDs, issue numbers,
timestamps and source references. No publisher response bodies or private
card contents are present. SHA-256:
`57f36f0acf7541bf3839c3365b8f9c215afbdee4abb08f4639aa2a58b4d6f114`.

Replay produces **157 signals**, with **176 retained observations** and
**one rejected item**. Nineteen observations join another release group.
Every retained input belongs to exactly one group. The full signal list is
in [the replay report](MODEL-432-replay.md).

The independent local-history audit found:

- The watcher landed September 29 in `c9948f3b6`; its baseline was taken at
  `2026-09-29T20:16:40Z`. Earlier runs cannot be replayed.
- All 34 public card additions in the window preceded that baseline.
- The private repository added 13 cards after its seed. Eight were
  backfills for older releases. Five described releases in the window.
- One of those five was already in the September 29 baseline. The other
  four were present in the issue archive and remain exactly once after
  filtering.

| Public discovery | Retained signal | Count |
| --- | --- | ---: |
| [#722](https://github.com/turbobeest/modelspec/issues/722) | `watch:google:gemini-4-argon` | 1 |
| [#624](https://github.com/turbobeest/modelspec/issues/624) | `watch:anthropic:claude-haiku-5-5` | 1 |
| [#468](https://github.com/turbobeest/modelspec/issues/468) | `watch:xai:grok-imagine-video-1-5-lite` | 1 |
| [#616](https://github.com/turbobeest/modelspec/issues/616) | `watch:mistral:mistral-large-4` | 1 |

This proves retention for **4/4 applicable carded releases represented in
the archive**. It cannot prove that a source input never emitted by the old
watcher was retained, or that every untriaged candidate is a real release.

The per-source fixture covers 74 sources and 320 labelled observations:
98 positive candidates and 222 explicit negative items. Every source has
fixture precision and recall of 1.0. Sixty-six source fixtures are entirely
synthetic; eight mix synthetic cases with public issue metadata. These
numbers are regression measurements, not estimates of live precision.

## Triage dry run

The classifier read the single cached issue export and the scratch private
catalogue. It produced:

| Classification | Count |
| --- | ---: |
| duplicate | 19 |
| superseded, already carded | 6 |
| real, candidate retained for review | 151 |
| noise | 1 |

[The dry-run report](MODEL-432-triage.md) has samples and the complete proposed
classification of all 177 issues. No issue was closed, labelled or edited.
Reconstructing the issue export from the committed normalized inputs
reproduced the complete JSON triage report exactly.

The sole rejected historical item is IBM's
[ensemble-forecasting repository](https://huggingface.co/ibm-granite/ensemble-forecasting-with-ibm-granite-time-series/tree/main).
Its public API listing contained only `.gitattributes` and two SVG diagrams.
The filter uses an exact rule for that repository. `Trident-Train` was
retained because its public metadata could not be verified.

The [IFM model description](https://huggingface.co/IFM/LoopedLM-P1-dense-d112-336b)
identifies 336B and 500B as training-token endpoints of one recipe.
The filter groups only those endpoints, preserving different recipes.
[NVIDIA's description](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16)
identifies the BF16 listing as the full-precision form of Nemotron 3.5 Super
VL, supporting its explicit short-name alias.

## Commands and reproduction

All repository commands ran in the assigned worktree. Test exit codes were
captured directly, with no pipe. The following were the test invocations;
the output files lived under `/tmp/model-432-scratch/executor/`.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py tests/test_release_watch_triage.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py -k 'separately_released or offline_replay'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py -k 'experiment_recipes or ifm'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_triage.py -k 'standalone or malformed_signal_url or output_collisions'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py tests/test_release_signals.py tests/test_release_pipeline.py tests/test_cite_only_retention.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py tests/test_release_watch_filter.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/release_watch.py scripts/release_watch_filter.py scripts/triage_release_discoveries.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

The actual test-output capture pattern was:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py tests/test_release_watch_filter.py > /tmp/model-432-scratch/executor/watch-final-green.txt 2>&1
test_exit=$?
cat /tmp/model-432-scratch/executor/watch-final-green.txt
exit "$test_exit"
```

External data acquisition, once each:

```bash
gh issue list -R turbobeest/modelspec --label release-discovery --state open --limit 300 --json number,title,body,createdAt,url > /tmp/model-432-scratch/executor/open-discoveries.json
git clone https://github.com/turbobeest/modelspec-data.git /tmp/model-432-scratch/modelspec-data
```

The private audit used these local-history commands for each repository:

```bash
git -C "$repo" log --since=2026-09-20T00:00:00Z --until=2026-10-21T00:00:00Z --diff-filter=A --format=%H -- models
git -C "$repo" show -s --format=%s "$sha"
git -C "$repo" diff-tree --no-commit-id --name-only --diff-filter=A -r "$sha" -- models
git -C "$repo" show "$sha:$path"
```

The public revision was the base SHA above. The private revision was
`a6f8fd798d7d6f40b35ed08320796b773f29df9a`. Subjects starting with `Seed:`
were excluded, removing the private initial import
`df5c7e3da3da488e36418b4f3571c1c1df9f53ed`. Each added card's YAML
frontmatter supplied its release date. The audit compared in-window
identities with the issue archive and committed baseline. Private data was
used only in scratch and deleted before delivery.

Replay and triage:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/release_watch.py --replay docs/evidence/g2-ios/MODEL-432-discovery-inputs.json --report /tmp/model-432-scratch/executor/replay.json --summary /tmp/model-432-scratch/executor/replay.md
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/triage_release_discoveries.py --issues /tmp/model-432-scratch/executor/open-discoveries.json --catalogue-root /tmp/model-432-scratch/modelspec-data --report /tmp/model-432-scratch/executor/triage.json --summary /tmp/model-432-scratch/executor/triage.md
```

The public issue input can be reconstructed without another GitHub call:

```python
import json
from pathlib import Path

archive = json.loads(Path(
    "docs/evidence/g2-ios/MODEL-432-discovery-inputs.json"
).read_text())
issues = []
for row in archive["observations"]:
    signal = {
        "model_name": row["model_name"], "provider": row["provider"],
        "first_seen_url": row["url"], "timestamp": row["signal_timestamp"],
        "confidence": row["confidence"], "signal_id": row["source_key"],
    }
    issues.append({
        "number": row["issue_number"],
        "title": f"release discovery: {row['model_name']} ({row['provider']}) `{row['source_key']}`",
        "url": row["issue_url"], "createdAt": row["issue_created_at"],
        "body": "```json\n" + json.dumps(signal) + "\n```",
    })
Path("/tmp/model-432-scratch/executor/reconstructed-issues.json").write_text(
    json.dumps(issues, indent=2) + "\n"
)
```

## What was not observed

- A complete 30-day historical input corpus or real-world precision/recall.
- Successful CI for the final draft PR; CI remains the authoritative full gate.
- Live watcher filing, queue migration, deployment, or a production switch change.
- Any vendor API spend, Firecrawl use, forbidden-host page retention or issue mutation.
- Private model facts in the public diff.

The remaining acceptance work is to replay a retained source-observation
window and compare it with the complete independently curated release set.
This PR supplies future retention and replay tooling; it cannot recreate
missing historical inputs.
