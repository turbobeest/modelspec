# MODEL-437 round 2: verified score precedence and citation labels

All three review findings are fixed. Private exports pass completeness in both
periods under main's policy and under #866's policy plus the MODEL-439 data
repair. All four private Worker memory measurements are below 115 MiB steady.
The repaired configuration changes one of the 302 repository corpus cases per
period. The diagnostic below proves that hardware-fit facts cause that change.

PR #889 remains a draft for independent review. This report replaces the
round-1 blocker assessment. The earlier report and measurements remain in
[the starting revision](https://github.com/turbobeest/modelspec/blob/25b29cbab0f0f8751b1ed6968bd3370562e13acd/docs/evidence/g2-ios/MODEL-437-fix.md).

## Revisions

| Input | Revision |
| --- | --- |
| Starting branch | `25b29cbab0f0f8751b1ed6968bd3370562e13acd` |
| Main, including #857's final code | `a03c4d077acc03c2bc5dba526ff635fb708ccb94` |
| Main merge commit | `a65a4997692d20abcccc848abf6a8c48448ed727` |
| Final implementation and tests | `6b9695fc75748bf31d8f07955bbf8fea89fc57f0` |
| Scratch-only #866 policy | `82ebcf4627d255d7641303caff2d149e879cf359` |
| MODEL-439 repair script, engine #891 | `77a9566822f7a23e322d2647913c755ad3cb7ed8` |
| Baseline private data | `9d9de96f062ac031336ee483ae97c3b436bd3845` |
| Repaired private data, data #118 | `f722d3fcb673b28bdff9fa1b5cac06c22cc61c38` |

Worktree `/Users/terbeest/dev/worktrees/model-437`, branch
`model-437-count-cited-scores`. Commits after the implementation SHA contain
evidence only. The final branch SHA is in the executor completion marker.

The merge retained main's final record-origin validation and the granting
versus restrictive cite-only APIs. `scripts/price_reread.py` and
`tests/test_cite_only_caller_isolation.py` match main exactly. The other conflict
resolutions retained #889's cited-score additions.

## Changes and red-first proof

The snapshot compiler removes cited rows when an admitted verified row exists
for the same canonical model and benchmark. This runs before capabilities,
objective lookups and predicate indexes are built. Offering records use their
canonical model. Rejected records from copy-permitted sources cannot suppress
a cited score, and multiple verified measurements remain intact. The legacy ranker's score
admission applies the same precedence regardless of input order.

The CLI comparison table appends `[Cited, not machine-verified]` to cited
benchmark values. Answer sentences distinguish cited facts, benchmark scores,
and both. Citation-kind tracking stays internal to the decision object and
does not alter the JSON contract or schema. A deserialized decision without
that internal context uses generic wording instead of guessing.

| Finding | Red-first regression tests | Red result | Green evidence |
| --- | --- | --- | --- |
| P1, objectives and predicate admission/veto | `test_verified_score_remains_the_benchmark_objective_winner`, `test_cited_score_neither_admits_nor_vetoes_verified_candidate`, rewritten `test_score_predicate_uses_verified_value` | Initial [14 failed, 51 passed](MODEL-437/round2/precedence-red.txt) | [99 passed](MODEL-437/round2/precedence-green.txt) |
| P1, capability estimate and legacy ranker | `test_cited_sibling_does_not_change_capability_estimate`, `test_legacy_ranker_prefers_verified_score_to_cited_sibling` | Included in the same initial red run | Included in the same 99-test green run |
| P2, human comparison table | `test_human_named_comparison_labels_cited_benchmark_score` | Combined P2/P3 [7 failed, 3 passed](MODEL-437/round2/labels-red.txt) | [154 passed](MODEL-437/round2/labels-green.txt) |
| P3, actual cited categories | `test_cited_answer_sentence_covers_facts_scores_and_both` | Included in the P2/P3 red run | Included in the 154-test green run; [17 selected tests passed](MODEL-437/round2/labels-final-green.txt) |

Additional regressions cover offering inheritance, rejected verified siblings,
multiple verified measurements, soft penalties, hidden reference operands,
measurement tie breakers, shown estimates and omitted private metadata. The
hidden ninth-driver fixture now uses a different benchmark so its cited driver
is not superseded by a verified sibling.

The final P1 test files also ran against an untouched archive of merge commit
`a65a4997`. Only the tests were copied into that archive. They produced
[18 assertion failures and 81 passes](MODEL-437/round2/precedence-confirmation-red.txt).
This replay includes corrected test fixtures. Earlier green attempts exposed
three fixture mistakes: comparing a normalized contribution with a raw score,
assuming an empty answer was populated, and choosing a context threshold that
did not exclude the default competitor. The final assertions use the raw
contribution, the absent answer and a threshold above that competitor's context.

## Completed checks

| Check | Result |
| --- | --- |
| Merged cite-only verification and caller isolation | [211 passed](MODEL-437/round2/merge-green.txt) |
| Final touched test files plus class-fit, legal and removed-source guards | [367 passed, 1 skipped](MODEL-437/round2/focused-green.txt), exit 0 |
| Decision schema and OpenAPI checks | Exit 0; no generated contract changes |
| Data freeze guard against main | Exit 0 |
| CI shard planner | Exit 0; predicted 4,111.592 to 4,111.594 seconds per shard |
| Tracked-file guard with acceptance artifacts staged | [1 passed](MODEL-437/round2/final-artifact-guard.txt), exit 0 |
| Public Worker bundle restored after all private probes | [129 files; clean imports](MODEL-437/round2/public-vendor-check.txt), exit 0 |

The optional built-site scan was the only final-suite skip because
`MODELSPEC_DIST` was unset. Suite counts overlap. Retained test logs only remove
trailing whitespace and surplus final blank lines; assertions and results are
unchanged. Exact commands and versions are in
[commands.md](MODEL-437/round2/commands.md).

## Private acceptance

Both candidate builds used final implementation `6b9695fc`. The staged-source
audit compared 205 files in each candidate against that commit, permitting only
the intended scratch policy override. Each state ran in a separate staged tree
and process.

The [acceptance README](MODEL-437/round2/acceptance/README.md) gives the replay
steps. The [comparison](MODEL-437/round2/acceptance/comparison.public.json),
[aggregate results](MODEL-437/round2/acceptance/summary.public.json),
[source audit](MODEL-437/round2/acceptance/staged-code.public.json) and
[repair audit](MODEL-437/round2/acceptance/repair-view.public.json) retain the
measured results. Command records include the failed setup attempt.

| State | Engine | Policy | Private data |
| --- | --- | --- | --- |
| a, baseline | Main `a03c4d07` | Main | `9d9de96f` |
| d | Candidate `6b9695fc` | Main | `9d9de96f` |
| c | Candidate `6b9695fc` | #866 | Data #118 repair on `9d9de96f` |

Data #118 directly descends from the baseline data revision. Its 13 changed
files were applied byte-for-byte in scratch. Unchanged leaf files were linked
to the original clone, with real containing directories. The #891 repair
script ran in dry-run mode against the repaired view with an explicit empty
CopyStore. All three rule counts and remaining changes were zero. No retained
research page bytes were read or copied to prepare or audit the view.

The first c setup used directory symlinks, which recursive model discovery
skipped. It exited 1 before corpus evaluation. Replacing only the scratch view
with real directories and leaf symlinks corrected the setup. No engine change
or completeness-gate bypass was involved.

Current exports were built on `2026-10-21`; successor exports start
`2027-01-01`. Corpus evaluation uses each snapshot's own date and keeps validity
checks enabled. Export creation uses the wall clock, so replaying calendar-
dependent identities later also requires the same build date.

Every state ran 319 total corpus cases, including 302 repository cases, in each
period. Every run had zero expectation failures and 286 contract-validated
HTTP-200 responses, including 269 repository cases. These responses came from
the local Worker service path, with no live API requests.

| Comparison against a, across 302 repository cases | Current | Successor |
| --- | ---: | ---: |
| d first-result model changes | 0 | 0 |
| d tie-member-set changes | 0 | 0 |
| d answer-kind changes | 0 | 0 |
| c first-result model changes | 1 | 1 |
| c tie-member-set changes | 1 | 1 |
| c answer-kind changes | 0 | 0 |

Both candidates' standalone completeness checks passed with `gap_count: 0` for
both periods. The deploy-style exports also kept the gate enabled.

| Additional measurement | a | d | c |
| --- | ---: | ---: | ---: |
| Admitted benchmark records, each period | 944 | 944 | 945 |
| Cited benchmark records, each period | 0 | 0 | 12 |
| Cited records with non-null verification | 0 | 0 | 0 |
| Warned templates, current, of 40 | 1 | 1 | 18 |
| Warned templates, successor, of 40 | 1 | 1 | 16 |

First result means `results[0].model`, not a unique-winner claim. A tie set is
sorted `answer.members` only when the answer is tied. Candidate contract
versions differ from main in all 302 cases as expected from #889's original
contract update. No HTTP or response status changed.

The strict comparator retains exit 1 and `acceptance_passed: false` because
it requires zero differences. Round 2 explicitly permits each remaining change
to be explained. The comparator was not weakened to hide the difference.

### The one changed case

The case is `facet-must-model.fits_hardware` in both periods. Its generated
spec requires a known `model.fits_hardware` value and maximizes
`software_engineering`, with `explain: summary` and `limit: 5`.

Under #866's policy, 10 unchanged hardware-fit facts are quarantined as mixed
citations. These are best-effort facts, outside MODEL-439's guaranteed-fact
repair. They are identical in the original and repaired data. Feeding each
identical admitted baseline record through the compiler under main's policy
admits all 10; changing only the policy to #866 rejects all 10. Their inherited
offering facts account for 32 subjects changing from known to unknown.

No software-engineering estimate changes. All 944 baseline benchmark readings
remain present and unchanged, with one additional admitted record. The
candidate subject set is unchanged.

An in-memory diagnostic replaced only the candidate's hardware-fit fact and
bitset columns with the baseline columns. That restored the exact baseline
first result, answer kind and member set in both periods while retaining the
candidate snapshot seed. Replacing only the seed or capability estimates did
not restore the answer. This isolates the remaining case change to #866's
policy treatment of best-effort hardware facts, rather than score precedence
or the data repair. The unmodified candidate snapshots and enabled production
gate were used for every acceptance and memory run.

The [public causal report](MODEL-437/round2/acceptance/residual.public.json)
and [replay script](MODEL-437/round2/acceptance/explain_difference.py) record
that diagnostic without publishing model identities or fact values.

### Worker memory

Each probe used deploy-style private vendoring, a throwaway signing key,
Node 22.22.3 and Pyodide 0.28.3. It exercised decide, vocabulary, rank and
policy-check with a 115 MiB steady limit. Source-cache and real signing-key
environment variables were absent.

| Configuration | Period | Steady MiB | Peak MiB | Result |
| --- | --- | ---: | ---: | --- |
| d, main policy | Current | 109.0079 | 109.7911 | Exit 0 |
| d, main policy | Successor | 104.6112 | 107.7897 | Exit 0 |
| c, #866 plus repair | Current | 104.6295 | 105.4141 | Exit 0 |
| c, #866 plus repair | Successor | 103.7415 | 105.7109 | Exit 0 |

Probe outputs: [d current](MODEL-437/round2/acceptance/memory-d-current.public.json),
[d successor](MODEL-437/round2/acceptance/memory-d-successor.public.json),
[c current](MODEL-437/round2/acceptance/memory-c-current.public.json),
[c successor](MODEL-437/round2/acceptance/memory-c-successor.public.json).

The public Worker bundle was rebuilt after all private memory runs, without a
private-data argument or signing key. It passed the import check and left no
tracked bundle changes.

## Reproduction and limits

Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3,
cryptography 45.0.7, pypdf 6.19.0, Node 22.22.3, Pyodide 0.28.3,
Git 2.50.1 and gh 2.102.0 were used. Pytest ran serially with
`-p no:cacheprovider`; exit codes were checked directly.

Private acceptance helpers and public aggregates accompany this report.
They record revisions, exact arguments, timestamps, exit codes and aggregate
results. Private records, response bodies, snapshots, exports and error logs
were removed with all task scratch before handoff. The
[cleanup record](MODEL-437/round2/cleanup.public.json) confirms removal and
zero remaining owned processes. The acceptance package is an immutable copy
from before cleanup, so its historical pending-cleanup fields remain intact.

No source-retention policy, frozen data, ranking floor, legal text or production
switch changed in the repository. No provider calls or API spend occurred.
No full local pytest run, full two-site build, release-chart check, remote CI
result, production deployment or Cloudflare runtime memory measurement is
claimed. CI remains the full gate, and independent cross-model review is pending.
