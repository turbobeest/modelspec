# MODEL-439: re-file mixed guaranteed citations

The script and data repair are complete. Deployment acceptance is **BLOCKED**:
main with #866 still changes recommendations when it excludes newly cite-only
benchmark records. #889 does not merge cleanly with this main, so the conditional
combined-state measurements are unobserved. Both PRs remain draft for review.

The repair reduces the production completeness gate from **192 gaps to zero**.
It changes source references and filing metadata only. The engine's verifier,
mixed-citation rule, completeness gate, ranking floors, contracts, legal text,
frozen public data and production switches are unchanged.

## Revisions

- Engine base/main: `a03c4d077acc03c2bc5dba526ff635fb708ccb94`.
- Final implementation/test SHA: `d46c70a06c9c30d150c4a48f1908ba50e1a9cbe6`.
- Private data base: `9d9de96f062ac031336ee483ae97c3b436bd3845`.
- Private data final SHA: `f722d3fcb673b28bdff9fa1b5cac06c22cc61c38`.
- Data PR: [modelspec-data#118](https://github.com/turbobeest/modelspec-data/pull/118).
- Data `.engine-pin`: main `a03c4d077acc03c2bc5dba526ff635fb708ccb94`.
- #866 policy: `82ebcf4627d255d7641303caff2d149e879cf359`.
- #889 candidate: `25b29cbab0f0f8751b1ed6968bd3370562e13acd`.

The final branch SHA is recorded in the PR body and executor completion marker.
Commits after the implementation SHA contain evidence only; a file cannot contain
the hash of its own commit. [Pinned identities](MODEL-439/identities.public.json)
and the [merge conflict output](MODEL-439/combined-merge.txt) preserve the inputs.

## Repair and data audit

`scripts/refile_mixed_citations.py` requires an explicit data root, retention
policy, retained-copy directory and date. It prints a deterministic plan by
default. `--write` applies it. It validates all original citation refs, uses
`decision.verify.verify` with `StoredRegions` and the engine's deterministic
extractors for rule 1, and preserves existing cite-only refs for rule 2.
The snapshot derives cited assurance from those refs, using the existing filing
convention. No retrieval date, source hash or fact value is invented.

A retained-only verification must return `verified` with a verification record.
Only that successful record is appended to the verification log. An unsuccessful
retained-only check never adds a mismatch or unreachable record to the repaired
fact. Filing/check events reflect the chosen sources. Current card values take
precedence over stale queue values. Identifier exceptions are reported unchanged.
The writer validates the complete parsed document before writing, preserves
surviving YAML and line endings, and refuses edited documents with YAML aliases.

There are **202 raw mixed guaranteed facts across 11 models**, all repaired by
rule 2. Ten `origin.lab_jurisdiction` rows are replaced by inherited lab facts
before snapshot admission, explaining the 192 gate gaps. Four queue claims for
those jurisdiction rows had stale values; new filing events use current card
values. Zero mixed `offering.api_model_id` or `offering.router_slug` facts were found.

All 202 retained-only checks returned `unreachable` in this run. The script used
an explicit empty scratch cache, not the operator's cache outside the allowed
paths. Inventory of the private clone found only one retained hash among the
needed eleven, on a host covered by the source-terms hold. No page bytes were
opened or copied. These results show unavailable retained verification, not a
contradiction of the stated values. Synthetic tests exercise rule 1 with a real
retained fixture and the engine verifier.

The [independent data audit](MODEL-439/data-audit.public.json) confirms:

- 202 facts changed across 11 model files; 490 retained refs removed and 394
  cite-only refs preserved. Every final list is exactly the original cited subset.
- All values, states, other fact fields, model metadata and Markdown bodies match.
- The verification log is byte-identical. Queue history retains its exact byte
  prefix, including line endings, followed by 202 collected and 202 cited checks.
- Appended claims match current cards and references. `.engine-pin` is a main
  commit. The linked-data guard passes and no code was added under data paths.
- The final script reproduces the private patch byte-for-byte over all 14 replay
  inputs. A [second write run](MODEL-439/repair-second-run.public.json) reports
  zero changes and leaves the files unchanged.

Counts per rule: rule 1 keeps independently verified retained refs; rule 2 keeps
only cited refs; rule 3 leaves identifiers unchanged. These counts describe the
raw data rows, including the ten inherited jurisdiction rows.

| Facet | Rule 1 | Rule 2 | Rule 3 |
| --- | ---: | ---: | ---: |
| `feature.batch` | 0 | 10 | 0 |
| `feature.effort_controls` | 0 | 10 | 0 |
| `feature.streaming` | 0 | 10 | 0 |
| `feature.structured_output` | 0 | 10 | 0 |
| `feature.tool_calling` | 0 | 10 | 0 |
| `licence.commercial_use` | 0 | 11 | 0 |
| `licence.fine_tuning` | 0 | 10 | 0 |
| `licence.output_training` | 0 | 11 | 0 |
| `licence.user_cap` | 0 | 10 | 0 |
| `model.class` | 0 | 10 | 0 |
| `model.context_window` | 0 | 10 | 0 |
| `model.input_modalities` | 0 | 10 | 0 |
| `model.lifecycle` | 0 | 10 | 0 |
| `model.max_output_tokens` | 0 | 10 | 0 |
| `model.output_modalities` | 0 | 10 | 0 |
| `model.release_date` | 0 | 10 | 0 |
| `model.weights_openness` | 0 | 10 | 0 |
| `origin.base_lineage` | 0 | 10 | 0 |
| `origin.lab_jurisdiction` | 0 | 10 | 0 |
| `origin.weights_hosting` | 0 | 10 | 0 |

| Model | Rule 1 | Rule 2 | Rule 3 |
| --- | ---: | ---: | ---: |
| `anthropic/claude-fable-5` | 0 | 20 | 0 |
| `anthropic/claude-fable-5-1` | 0 | 20 | 0 |
| `anthropic/claude-opus-4-6` | 0 | 20 | 0 |
| `anthropic/claude-opus-4-7` | 0 | 20 | 0 |
| `anthropic/claude-opus-5` | 0 | 20 | 0 |
| `anthropic/claude-opus-5-5` | 0 | 20 | 0 |
| `openai/gpt-5-4` | 0 | 20 | 0 |
| `openai/gpt-5-6-sol` | 0 | 20 | 0 |
| `openai/gpt-6-astra` | 0 | 20 | 0 |
| `openai/gpt-6-luna` | 0 | 2 | 0 |
| `openai/gpt-6-sol` | 0 | 20 | 0 |

## Red-first and focused verification

| Behavior | Red evidence | Green evidence |
| --- | --- | --- |
| Dry-run retained-only verification: `test_dry_run_verifies_retained_refs_without_writing` | [1 failure: missing script](MODEL-439/red-dry-run.txt) against unchanged base | [1 passed](MODEL-439/green-dry-run.txt) |
| Opt-in writes, both repair rules, admitted values, byte preservation and idempotency: `test_write_preserves_values_bytes_and_admission_and_is_idempotent` | [2 failures: unsupported `--write`](MODEL-439/red-write.txt) | [3 passed](MODEL-439/green-write.txt) |
| Inline source mappings and alias safety: `test_inline_source_mappings_are_removed_and_second_run_is_empty`, `test_aliased_sources_are_refused_without_changing_other_records` | [2 assertion failures](MODEL-439/red-yaml.txt) | [11 passed](MODEL-439/green-yaml.txt) |
| Unresolved original references: `test_invalid_input_prevents_all_writes[unresolved_source]` | [1 assertion failure](MODEL-439/red-unresolved.txt) | [12 passed](MODEL-439/final-script-green.txt) |

The final script suite also covers stale filed values, both identifier exceptions,
unavailable copies, undated citations, malformed citation metadata and refusal to
append to an unterminated log. The first fixture was corrected to use registered
source/normalizer names and the existing table label before recording the missing
script failure. Those setup failures are not counted as product defects.

The broader focused run of script, cite-only admission, engine verifier and
removed-source guard suites passed **571 tests, 1 skipped** in 149.41 seconds.
[Full output](MODEL-439/focused-green.txt). It preceded the final unresolved-ref
validation; the subsequent final script suite passed all 12 tests. Counts overlap.
Ruff and `git diff --check` pass. The four predicted CI shards remain balanced at
about 4097 seconds each. No full local suite was run. After staging the evidence, the
[tracked-file publisher guard](MODEL-439/final-tracked-guard.txt) passed again.

## Deploy-style acceptance

Every private export used `api.worker.vendor.export_data`, a throwaway signing
key and the production completeness gate. No gate was disabled. Source-cache
configuration was cleared for deploy equivalence. The actual export date was
2026-10-21; snapshot evaluation used 2026-10-21 and successor 2027-01-01.
Replaying calendar-dependent exports on another day requires fixing that date.

State a uses original private data and main's actual policy. Required state b
uses repaired private data, the same main and #866's scratch-only policy.
Supporting state d uses repaired private data with main's actual policy.
Each state evaluates all 319 corpus cases, including the required 302 repo cases.

| Measurement | Current b versus a | Successor b versus a |
| --- | ---: | ---: |
| Repo cases | 302 | 302 |
| First-result model changes | 66 | 66 |
| Tie-member-set changes | 72 | 71 |
| Answer-kind changes | 4 | 2 |
| Answer-kind or member-set changes | 72 | 72 |
| Admitted benchmark records, a to b | 944 to 933 | 944 to 933 |

Both a and b have zero corpus expectation failures, 286 contract-validated
HTTP-200 cases and 269 repo HTTP-200 cases per period. Passing expectations does
not satisfy the stricter recommendation comparison. The comparison command
returns **exit 1** for the measured changes. First result means
`results[0].model`; tie sets are sorted `answer.members` for tied answers.

The separate [original gate](MODEL-439/gate-original.public.json) reports 192
mixed-citation gaps across 11 models, exactly reproducing MODEL-437's facet
counts. The [repaired gate](MODEL-439/gate-repaired.public.json) reports zero.
The required private export also succeeds with the same gate enabled.

Supporting d versus a has **zero first-result, tie-set and answer-kind changes**
in both periods over all 302 repo cases. It retains all 944 benchmark records.
This isolates the refiling itself as neutral under main's actual policy; the
required state b still fails after #866 removes eleven benchmark records.
[State a](MODEL-439/state-a.public.json), [state b](MODEL-439/state-b.public.json),
[state d](MODEL-439/state-d.public.json), and the
[full comparison](MODEL-439/comparison.public.json) contain the measurements.

The required b memory probe passed both periods using deploy-style private
vendoring, Pyodide 0.28.3, Node 22.22.3 and a throwaway signing key. It exercised
decide, vocabulary, rank and policy-check.

| Period | Steady MiB | Peak MiB | Steady limit | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 109.0001 | 109.8225 | 115 | Exit 0 |
| Successor | 104.6017 | 105.4237 | 115 | Exit 0 |

[Current memory](MODEL-439/memory-current.public.json) and
[successor memory](MODEL-439/memory-successor.public.json) retain the raw probe
reports. The [public Worker bundle check](MODEL-439/public-vendor-check.txt) rebuilt
129 files after the private run and verified imports. The
[data-freeze guard](MODEL-439/data-freeze.txt) passed.

#889 conflicts in `decision/citation.py`, `decision/snapshot.py`,
`scripts/price_reread.py`, `tests/test_cite_only_caller_isolation.py` and
`tests/test_cite_only_verification.py`. The scratch merge check uses isolated git
objects and changes no branch. Per the spec's clean-merge condition, combined
completeness, corpus parity and memory remain unobserved. Resolving that engine
branch and restoring its cited benchmark behavior are outside this data repair.

## Reproduction commands

Versions: Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3,
pypdf 6.19.0, cryptography 45.0.7, Ruff 0.16.6, Node 22.22.3, npm 10.9.8,
Pyodide 0.28.3, git 2.50.1 and gh 2.102.0. Tests ran serially with cacheprovider
disabled; exit codes were read directly. Scratch `/tmp` resolves to
`/private/tmp` on this Mac. The helpers contain the complete subprocess commands. Captured argv and exit
codes are in [initial commands](MODEL-439/initial-commands.public.json),
[measurements](MODEL-439/measurement-commands.jsonl),
[supporting d](MODEL-439/supporting-d.commands.public.json), and
[exit summary](MODEL-439/measurement-exits.public.json).

```bash
cd /Users/terbeest/dev/worktrees/model-439
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
DATA=/tmp/model-439-scratch/modelspec-data
PROOF=/tmp/model-439-scratch/acceptance-review
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH

# Repository preparation, using the pinned revisions above.
git fetch origin main pull/866/head:refs/remotes/origin/pr-866 pull/889/head:refs/remotes/origin/pr-889
git clone https://github.com/turbobeest/modelspec-data.git "$DATA"
# Before refiling, DATA was at 9d9de96f062ac031336ee483ae97c3b436bd3845.
# Copy the four acceptance helpers from this evidence directory to PROOF.
"$PY" "$PROOF/prepare.py" --repo "$PWD" --data-dir "$DATA" \
  --output "$PROOF/prepared" --main-ref origin/main \
  --policy-ref origin/pr-866 --combined-ref origin/pr-889
"$PY" "$PROOF/compare_private.py" run \
  --main-root "$PROOF/prepared/main" --candidate-root "$PROOF/prepared/main" \
  --host-policy "$PROOF/prepared/hosts-866.json" \
  --baseline-data-dir "$PROOF/prepared/baseline-data" --data-dir "$DATA" \
  --output "$PROOF/results" --states a

# Red commands ran before their corresponding implementations.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k write
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k 'inline_source or aliased'
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k unresolved_source
# Green focused checks.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py tests/test_cite_only_verification.py tests/test_decision_verify.py tests/test_removed_sources.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
"$PY" -m ruff check scripts/refile_mixed_citations.py tests/test_refile_mixed_citations.py
"$PY" scripts/pytest_shards.py --shard-count 4 --summary

# Policy is scratch-only. The cache is explicit and empty.
git show origin/pr-866:registry/source-retention.json > /tmp/model-439-scratch/executor/hosts-866.json
mkdir -p /tmp/model-439-scratch/executor/empty-copies
git -C "$DATA" switch -c model-439-mixed-citation
git rev-parse origin/main > "$DATA/.engine-pin"
env PYTHONPATH=$PWD "$PY" scripts/refile_mixed_citations.py \
  --data-root "$DATA" --source-cache /tmp/model-439-scratch/executor/empty-copies \
  --policy /tmp/model-439-scratch/executor/hosts-866.json --as-of 2026-10-21
# Same command with --write applied the patch, then a repeated --write was empty.
env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-439/audit_data.py \
  --data-root "$DATA" --engine-root "$PWD" --base 9d9de96f \
  --output /tmp/model-439-scratch/filing-review/data-audit.public.json
"$PY" -I "$DATA/.github/scripts/check_linked_data.py" --engine "$PWD" --data "$DATA"

# Repaired deploy exports and exact 302-case comparisons.
"$PY" "$PROOF/compare_private.py" run \
  --main-root "$PROOF/prepared/main" --candidate-root "$PROOF/prepared/main" \
  --host-policy "$PROOF/prepared/hosts-866.json" \
  --baseline-data-dir "$PROOF/prepared/baseline-data" --data-dir "$DATA" \
  --output "$PROOF/results" --states b
# Same run command with --states d for the supporting main-policy control.
"$PY" "$PROOF/compare_private.py" compare --output "$PROOF/results" --states abd
"$PY" "$PROOF/check_completeness.py" --code "$PROOF/results/b/code" \
  --data-dir "$PROOF/prepared/baseline-data" --output "$PROOF/gate-original" --as-of 2026-10-21
"$PY" "$PROOF/check_completeness.py" --code "$PROOF/results/b/code" \
  --data-dir "$DATA" --output "$PROOF/gate-repaired" --as-of 2026-10-21
npm install --prefix "$PROOF/memory-runtime" --no-save pyodide@0.28.3
"$PY" "$PROOF/measure_private.py" --code "$PROOF/results/b/code" \
  --data-dir "$DATA" --output "$PROOF/memory-b" \
  --node /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node \
  --runtime "$PROOF/memory-runtime"
# After private memory measurement, restore and check the public Worker bundle.
env PYTHONPATH=$PWD "$PY" api/worker/vendor.py --check

env PYTHONPATH=$PWD "$PY" scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-439-mixed-citation
git diff --check
git -C "$DATA" diff --check
CI_LOCAL_SKIP=1 git push -u origin model-439-mixed-citation
CI_LOCAL_SKIP=1 git -C "$DATA" push -u origin model-439-mixed-citation
# Both PRs were created with gh pr create --draft; neither was readied or merged.
```

## Unobserved and handoff limits

No production deployment, Cloudflare runtime memory measurement, full local
pytest, full two-site build, release-chart check or completed remote CI result is
claimed. The skipped removed-source test requires `MODELSPEC_DIST`. Local memory
is the deploy-style Pyodide probe, not a production runtime observation.
The private repair read no source-page bytes. Synthetic verifier tests used local
fixtures. No source-page fetches, provider API calls or real signing secrets were used. No private facts, scores, exports or private error logs are committed
to the engine repository. The private clone and scratch exports are removed at
handoff, and every process started for this task exits before completion.
Independent cross-model review remains pending.
