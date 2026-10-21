# MODEL-437: count cited benchmark scores

Implementation complete; acceptance **BLOCKED** by a reproduced prerequisite
data-completeness failure. Keep this PR draft pending #857 and review. The
required candidate with #866's host policy cannot produce a deployable snapshot,
so its recommendation parity, 40-template warning count and Worker memory are
unobserved.

## Revisions and scope

- Starting prerequisite #857: `44f3bdb5cbc96afa275ee1ca836703560d10c97b`.
- Final implementation/test SHA: `7d6f5c15652c453b667f056206c540a3d2930eaf`.
- Baseline main used for private comparisons:
  `9be40994f5e884588aa21d49b2f2647e4a3fec3c`.
- Merged main after implementation:
  `9f280970f83e0530782516890e5d4345ce590053`.
- Scratch-only #866 policy: `82ebcf4627d255d7641303caff2d149e879cf359`.
- Private data: `a6f8fd798d7d6f40b35ed08320796b773f29df9a`.
- Worktree: `/Users/terbeest/dev/worktrees/model-437`; branch:
  `model-437-count-cited-scores`.

The final branch SHA follows in the PR body and executor completion marker.
Commits after the implementation SHA above contain evidence only; a file cannot
embed the hash of the commit containing itself. Machine-readable identities are
in [run-metadata.json](MODEL-437/run-metadata.json).

Cited scores now enter the snapshot with `verification: null` and citation
status `cited`. Ranking, filtering, capability fits, refinements, comparison,
explanations and browser provenance retain that distinction. Decision warnings
track scores actually used by a top or tied model, including hidden tied rows,
reference operands, unshown fit drivers and measurement tie breakers. Unused,
excluded or short-circuited scores do not add a decision warning. Mismatch,
unreachable, invalid citations, mixed refs and authored redirect restrictions
still refuse admission. An authored redirect cannot grant citation status.

No source-retention host policy, frozen data, ranking floor, legal text or
production switch was changed by this ticket. Changes inherited from #857 stay
on the branch as required. The main merge retained both PDF/rendered source
support and #857's restrictive source handling.

## Contracts

Read the decision, rank, snapshot and export contracts before changing them.

- Snapshot format **1 → 2** is a major bump. An old reader treated every evidence
  row as verified; the new format adds cited-evidence and estimate provenance
  indexes. New readers accept both format 1 and format 2.
- Decision **2.18 → 2.19**, named comparison **1.0 → 1.1**: add optional citation
  metadata, omitted for uncited evidence. No existing response field gains a
  new enum member, nullability or absence. Export record verification already
  allowed null; the snapshot reader's changed interpretation requires format 2.
- Export **3.0**, rank **1.0**, bounded decision **1.5** stay unchanged. The
  bounded response advertises its updated underlying decision version.
- Regenerated the JSON schema and OpenAPI, updated the strict browser decoder
  and MCP contract-version fallback. Tests still enforce full response bytes
  and golden hashes.

The [golden audit](MODEL-437/golden_identity_audit.json) reproduces all nine old
plan responses and three Worker hashes with snapshot format 1. Format 2 changes
only their snapshot and decision identities. The [public budget audit](MODEL-437/budget_identity_audit.json)
replays the old snapshot identity with current data and reproduces the entire old
fixture, including ten `p_best` values. Those probability changes come from the
snapshot-derived random seed; answers, order, evidence and summaries stay the
same. The saved budget fixture's identity was already older than a newly built
format-1 identity; format alone does not explain that earlier difference.

## Red first and regression results

The initial score tests ran against unchanged `44f3bdb5`. Additional edge tests
ran before their corresponding fixes. Logs below contain actual assertion
failures, not crashes.
Retained text logs have trailing whitespace and surplus final blank lines
removed; assertion text and test results are unchanged.

| Defect and test | Red result | Final green coverage |
| --- | --- | --- |
| Snapshot admission and ranking: `test_cited_score_survives_snapshot_roundtrip_without_verification`, `test_cited_score_ranks_and_warns_on_the_recommendation`, `test_tied_cited_score_outside_limit_still_warns` | [8 failed, 10 passed](MODEL-437/red.txt) | Post-merge focused suite and final fixture suite |
| Citation contracts/comparison; qualified filters, model/best references, capabilities and refinements | [22 failed, 5 passed](MODEL-437/contracts-warnings-red.txt) | Contract suite and post-merge focused suite |
| Invalid citation display URL/regions | [6 failed](MODEL-437/invalid-citation-red.txt) | Post-merge focused suite |
| Shown capability citation with a fact objective | [2 failed](MODEL-437/shown-score-red.txt) | Post-merge focused suite |
| Independent-measurement tie-break citation | [1 failed](MODEL-437/tiebreak-red.txt) | Post-merge focused suite |
| Authored redirect to excluded host | [failure](MODEL-437/edge-red.txt) | Post-merge focused suite |
| Browser decoder and displayed score provenance | [2 failed](MODEL-437/web-red.txt) | 908 web tests and production web build |
| A cited score fails a predicate while a verified score admits the model: `test_score_predicate_warning_uses_supporting_rows` | [6 failed, 8 passed](MODEL-437/predicate-red.txt) | [14 passed](MODEL-437/predicate-green.txt); 182-test warning/filter suite |

| Completed check | Result / log |
| --- | --- |
| Contracts, comparisons, MCP version | [334 passed](MODEL-437/contracts-green.txt) |
| Decision engine, capability, calibration, explanation, optimisation, vocabulary, streaming, memory-compaction, corpus | [916 passed](MODEL-437/decision-suites-green.txt) |
| Final merged code: cited scores/warnings/contracts, cite-only surfaces/verification/caller isolation, PDF/rendered sources, excluded-source guard, Worker imports | [416 passed, 31 skipped](MODEL-437/post-merge-focused.txt) |
| Refreshed golden identities, links, API docs, bounded responses, score admission | [218 passed, 2 skipped](MODEL-437/final-fixtures-green.txt) |
| Web suite | [908 passed; one test file skipped](MODEL-437/web-all-green.txt) |
| Web production build | [exit 0](MODEL-437/web-build.txt) |
| MCP suite / typecheck | [235 passed](MODEL-437/mcp-tests.txt); [typecheck exit 0](MODEL-437/mcp-typecheck.txt) |
| Regenerated MCP fixture consumers | [106 passed](MODEL-437/mcp-fixtures-green.txt) |
| Schema / OpenAPI consistency | [exit 0](MODEL-437/schema-check.txt); [exit 0](MODEL-437/openapi-check.txt) |
| Public bundle rebuilt after private memory run | [129 files, imports clean](MODEL-437/public-vendor-check.txt) |
| Data freeze | [passed](MODEL-437/data-freeze.txt) |
| Final predicate warning fix, score admission, fact warning scope and filters | [182 passed](MODEL-437/filter-warning-green.txt) |
| Excluded-source guard with all evidence artifacts staged | [46 passed, 1 skipped](MODEL-437/final-artifact-guard.txt) |

Counts overlap between suites and are not a unique test total. Intermediate
broader runs caught current-version literals, format-derived golden IDs, a
malformed-record citation guard and two test setup errors. These were corrected:
the malformed-record guard still requires a fact or benchmark record; old-format
readability uses the existing bytes returned by `canonical_json`; the shown-score
test inspects the contribution that actually carries its evidence. Golden
assertions were refreshed after the identity audits, not loosened. The hidden-tie
test explicitly puts the cited model outside the returned limit.

The final audit found and corrected an extra warning when a failing cited row
shared a benchmark with a passing verified row. Predicate provenance now selects
the rows supporting its evaluated outcome; failed predicates still retain
citations when negation or a soft penalty uses them. This changes warning
attribution only. [Exact red/green commands](MODEL-437/predicate-verification.md)
cover comparisons, windows, relative references, soft conditions and negation.

## Private deploy-equivalent proof

All private builds used the same private data revision, a throwaway signing key,
the production `vendor.export_data` path and its completeness gate. No provider
calls were made. Each state ran in its own staged tree/process. Current and
successor snapshots were evaluated at their respective `as_of` dates
(`2026-10-21`, `2027-01-01`) so the successor validity guard remained enabled.

State definitions:

- **a:** pinned main with its host policy.
- **b:** the same main plus #866's host policy, in scratch only.
- **c:** this implementation plus #866's policy, in scratch only.
- **d:** supporting check of this implementation with main's current host policy.

| Measurement | a | b | c | d, supporting only |
| --- | ---: | ---: | --- | ---: |
| Admitted benchmark records | 944 | 933 | Blocked | 944 |
| Cited benchmark records | 0 | 0 | Blocked | 0 |
| Warned templates, current / successor | 1 / 1 of 40 | 15 / 15 of 40 | Unobserved | 1 / 1 of 40 |
| Corpus expectation failures, each period | 0 | 0 | Unobserved | 0 |
| Contract-validated HTTP-200 responses, each period | 286 | 286 | Unobserved | 286 |

Each successful state exercised all 319 corpus cases, including 302 repo cases
(269 repo cases return HTTP 200; the other cases intentionally exercise errors).
State reports: [a](MODEL-437/state-a.public.json),
[b](MODEL-437/state-b.public.json), [d](MODEL-437/state-d.public.json).

| Comparison across 302 repo cases | Current | Successor |
| --- | ---: | ---: |
| b vs a: first result model changes | 66 | 66 |
| b vs a: tie member set changes | 72 | 71 |
| b vs a: answer kind or member set changes | 72 | 72 |
| c vs a | Unobserved | Unobserved |
| d vs a: first result model changes | 0 | 0 |
| d vs a: tie member set changes | 0 | 0 |
| d vs a: answer kind or member set changes | 0 | 0 |

“First result” means `results[0].model`, not a unique-winner claim. A tie member
set is sorted `answer.members` for `answer.kind == tied`, otherwise empty.
[The comparison report](MODEL-437/comparison-available.public.json) includes
case IDs and additional status/order counts. d changes the contract version in
all 302 cases; it does not establish c's required parity. a/b/d were measured
before merging main's new source readers; all ticket scoring changes were
already present. The final c gate and supporting memory probe used merged code.
The last predicate-warning correction followed the corpus runs; a/b use their
own unchanged code and d has no cited benchmark rows. The supporting memory
probe was repeated after that correction.

### Reproduced prerequisite blocker

The production c export failed before producing a deployable snapshot. A
separate build of untouched prerequisite `44f3bdb5` plus the same #866 policy
failed identically: **192 guaranteed-fact gaps across 11 models**, all
`quarantined (mixed citation)`. Exact `(subject, facet, reason)` sets match;
there are zero candidate-only or base-only gaps. This is a prerequisite/data
interaction, not a new gap introduced by score admission.

- [Base #857 gate](MODEL-437/gate-base857.public.json)
- [Candidate gate](MODEL-437/gate-c.public.json)
- [Exact set comparison](MODEL-437/gate-comparison.public.json)
- [Final post-merge c gate](MODEL-437/gate-final-c.public.json): still 192, exact match

The gate stayed enabled for every deploy/acceptance attempt. Private data and
the production gate were not changed to force a passing result.

A separate, explicitly **nondeployable score-only diagnostic** used `gate=False`
in memory solely to inspect score admission. It wrote no snapshot and fed no
corpus or memory run. It found 945 records: all 11 lost by b are restored and
labelled cited; all 944 original readings are unchanged; one additional record
is admitted. All 12 cited records have null verification, citation status cited,
and `verified == False`. This [aggregate](MODEL-437/evidence-diagnostic.public.json)
supports admission behavior, not deployment or recommendation parity.

### Memory

The required **c memory result is unobserved** because c cannot build. The
supporting probe used private data with the repository's actual host policy,
the merged implementation, deploy-style vendoring, Pyodide 0.28.3, Node 22 and a
throwaway key. It exercised decide, vocabulary, rank and policy-check requests.

| Supporting period | Steady MiB | Peak MiB | Limit | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 109.0142 | 112.5679 | 115 steady | Exit 0 |
| Successor | 104.6141 | 105.3975 | 115 steady | Exit 0 |

Raw probe results: [current](MODEL-437/memory-actual-policy-current.json),
[successor](MODEL-437/memory-actual-policy-successor.json).
The public Worker bundle was re-vendored after this private run.

## Reproduction commands and versions

Environment: macOS; Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3,
pypdf 6.19.0, cryptography 45.0.7; Node 22.22.3, Vitest 5.0.1,
Pyodide 0.28.3; git 2.50.1, gh 2.102.0. Python is the shared repo virtualenv;
Node is `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node`.

The following commands ran from the ticket worktree; `PY` below abbreviates
the exact Python executable for readability. Each pytest call was serial with
`-p no:cacheprovider`; exit codes were read directly, without a pipe.

```bash
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH

# Initial red, before production changes.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_scores.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_score_contract.py tests/test_cited_score_warnings.py
# Later red selections, before their respective fixes.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_scores.py -k invalid_cited_score
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_score_warnings.py -k shown_capability
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_score_warnings.py::test_cited_score_used_by_independent_measurement_tie_breaker_warns
(cd web && npm test -- cited-score.test.tsx)

# Green contract and broader decision suites.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_score_contract.py tests/test_decision_contract.py tests/test_compare_models_worker.py tests/test_mcp_contract_version.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_contract.py tests/test_cite_only_surfaces.py tests/test_decision_capability.py tests/test_capability_calibration.py tests/test_decision_explain.py tests/test_decision_optimise.py tests/test_decision_vocabulary.py tests/test_snapshot_streaming.py tests/test_worker_memory_compaction.py tests/test_corpus.py
# Final post-merge and fixture suites.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_warnings.py tests/test_cited_score_contract.py tests/test_cite_only_surfaces.py tests/test_cite_only_verification.py tests/test_cite_only_caller_isolation.py tests/test_pdf_sources.py tests/test_rendered_interactions.py tests/test_removed_sources.py tests/test_worker_vendor_imports.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_decision_plans.py tests/test_decision_link.py tests/test_api_docs.py tests/test_decide_bounded.py tests/test_cited_scores.py
(cd web && npm test)
(cd web && env PYTHONPATH=$PWD/.. npm run build)
(cd mcp && npm test)
(cd mcp && npm run typecheck)
(cd mcp && npm test -- decide-budget.test.ts server.test.ts)
env PYTHONPATH=$PWD "$PY" -m decision.schema --check
env PYTHONPATH=$PWD "$PY" api/worker/openapi.py --check
env PYTHONPATH=$PWD "$PY" api/worker/vendor.py --check
env PYTHONPATH=$PWD "$PY" scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-437-count-cited-scores
git diff --check
```

Private-proof scripts are committed beside this report. They keep private
records, error details and exports in scratch and emit public aggregate reports.
To reproduce, restore the pinned main and private revisions in the named scratch
paths, copy the policy from the pinned #866 commit into `hosts-866.json`, and use
fresh output directories. The private clone used HTTPS git; no source page
fetches or paid APIs were used.

Export creation used the actual UTC date `2026-10-21`; `vendor.export_data`
reads the wall clock. No export-time clock override was used. Replaying the
numeric snapshot comparison on a later date requires an environment with that
date fixed; pinned revisions alone do not reproduce calendar-dependent exports.
The explicit per-period clock in the helper applies only while evaluating the
already-built snapshots. The standalone gate and score diagnostic do accept
`--as-of`.

Scripts: [corpus comparison](MODEL-437/compare_private.py),
[completeness gate](MODEL-437/check_completeness.py),
[score-only diagnostic](MODEL-437/evidence_restore_diagnostic.py),
[supporting memory probe](MODEL-437/memory_actual_policy.sh),
[planned c memory probe](MODEL-437/memory_steps.sh),
[golden identity audit](MODEL-437/golden_identity_audit.py),
[budget identity audit](MODEL-437/budget_identity_audit.py).

```bash
PROOF=/tmp/model-437-scratch/proof-setup
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
mkdir -p "$PROOF" /tmp/model-437-scratch/contract-audit
cp docs/evidence/g2-ios/MODEL-437/{compare_private.py,check_completeness.py,evidence_restore_diagnostic.py,memory_actual_policy.sh} "$PROOF/"
"$PY" "$PROOF/compare_private.py" run \
  --main-root /tmp/model-437-scratch/main --candidate-root "$PWD" \
  --host-policy /tmp/model-437-scratch/executor/hosts-866.json \
  --data-dir /tmp/model-437-scratch/modelspec-data \
  --output "$PROOF/results" --states ab
# Same command with --states c: exit 1, production completeness failure.
# Same command with --states d: exit 0, supporting actual-policy comparison.
env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-437/compare_private.py compare \
  --output "$PROOF/results" --states abd
# Exit 0; emits comparisons for available states and explicitly marks c unobserved.

env PYTHONPATH="$PROOF/final-gated-c/code" "$PY" "$PROOF/check_completeness.py" \
  --code "$PROOF/final-gated-c/code" \
  --data-dir /tmp/model-437-scratch/modelspec-data \
  --output "$PROOF/final-gated-c/gate" \
  --compare-gaps "$PROOF/gate-base857/gaps.private.json" --as-of 2026-10-21

env MODELSPEC_SNAPSHOT_KEY=model437-private-proof-throwaway-key \
  "$PY" "$PROOF/evidence_restore_diagnostic.py" \
  --code "$PROOF/results/c/code" --data-dir /tmp/model-437-scratch/modelspec-data \
  --baseline-export "$PROOF/results/a/exports/decision/snapshot.json.gz" \
  --host-only-export "$PROOF/results/b/exports/decision/snapshot.json.gz" \
  --output "$PROOF/evidence-diagnostic-c"

bash "$PROOF/memory_actual_policy.sh"
# Actual script vendors private data into a scratch bundle, copies handwritten
# Worker modules, and runs measure_memory.cjs --limit-mib 115 for both periods.
env PYTHONPATH=$PWD "$PY" api/worker/vendor.py --check

env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-437/golden_identity_audit.py
env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-437/budget_identity_audit.py
```

The comparator was corrected during setup to evaluate in a fresh process after
vendoring: imported default paths otherwise referred to a deleted overlay.
The successor clock was then set to the snapshot period, matching the existing
memory probe. No failure from either setup mistake is counted as a corpus
result. The committed helper reflects both corrections.

## Unobserved and handoff limits

- c vs a recommendation parity, c's 40-template warning count and c's private
  Worker memory remain blocked by the prerequisite mixed-ref fact gaps.
- The extra admitted record in the score-only diagnostic means evidence-count
  restoration alone cannot establish zero recommendation changes.
- No full local pytest, full two-site pipeline build, release-chart check,
  production deploy, Cloudflare runtime measurement or remote CI result is
  claimed. CI remains the full gate.
- Optional Python Playwright cases and the `MODELSPEC_DIST` output scan were
  skipped; the two live API probes in `tests/test_api_docs.py` were disabled,
  and one web test file was skipped.
- No private score rows, fact values, snapshots or private error logs are
  committed. Private clone, overlays, exports and task scratch are removed
  before completion. All spawned processes must exit before handoff.
- This is executor evidence; independent cross-model review is still pending.
