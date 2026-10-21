# MODEL-439 round 3: mixed records enter as cited

The implementation and measured acceptance checks pass. Handoff remains
**BLOCKED on the requested #889 merge to main**. PR #889 was still open at
its last API check, with head `33c705e125545400b3af6b0d2aab9b74da5ad2fc`.
The advertised engine main remains
`36b2d184dcc5a67a90ceb1a9015275143c09691d`. This branch merges both that main
and #889's fetched head, so the requested precedence is implemented and tested.
No PR was merged or marked ready. Engine #891 is confirmed draft; data #118
was updated without changing its draft status.

This report supersedes round two's attribution blocker and the older counts
in the existing PR description. The executor brief forbids `gh pr edit`, so
that description remains historical. Its link to this report remains valid.
Round two's report is available at executor base `75e248a2`; its artifacts
remain under [r2](MODEL-439/r2/).

## Result and provenance

Mixed facts and benchmark scores now enter as cited with every reference in
the citation payload. Retained verification is null. Loaded score rows expose
`verified == False`. Malformed metadata, failed verification outcomes and
cited operational identifiers remain excluded. #889's verified-sibling
precedence remains unchanged and covers mixed model and offering scores.

The change removes the two mixed-record quarantine branches in
`decision/snapshot.py`. Citation construction already validated and preserved
all refs. Tests and the independent subscription expectation helper now follow
the new admission rule. The design and decision-contract explanations were
updated. No ranking floor, legal term, production switch, host policy or
frozen public data was edited.

No contract field widens. `FactCitation.sources` already accepts a nonempty
list of `CitationSource` objects with HTTP(S) URLs, hashes and nullable
retrieval times. Mixed references use that existing range. #889 supplies its
own contract changes; MODEL-439 adds no further version change.

## Revisions

- Executor base: `75e248a28fe704b37f128d192f5d7c462b2b40d6`.
- Runtime implementation SHA: `a8ea6d0e`.
- Advertised main: `36b2d184dcc5a67a90ceb1a9015275143c09691d`.
- Integrated #889 head: `33c705e125545400b3af6b0d2aab9b74da5ad2fc`.
- Prospective main+#889 tree: `e27848539593d156507ae9fccb6fe52a324e1b66`.
- #866 policy: `82ebcf4627d255d7641303caff2d149e879cf359`.
- Data #117 merge fetched by SHA: `4ac4f273bebf25ac796e67441d7381d618394a26`.
- Data #118 head pushed: `44fc4e4`; `.engine-pin` remains the main commit above.

[Identities and 101 runtime source hashes](MODEL-439/r3/identities.public.json)
confirm that the measured candidate code matches the final runtime source.
Later changes concern evidence and test formatting. The final branch SHA is
in the executor completion marker; this file cannot contain its own commit's
hash.

GitHub reported data #117 merged while Git still advertised the older data
main `9d9de96f`. The reported merge commit was fetched directly and merged.
Three add/add conflicts were older copies of the same guard/test files;
resolution takes #117's split cite-only API and rendering tests. The final
data diff against that merge contains only the original ten repaired model
files and eight queue events.

## Red-first checks

| Behavior | Before admission change | After admission change |
| --- | --- | --- |
| `test_mixed_citation_fact_is_cited_with_every_ref` and associated identifier, failed-outcome and helper checks | [15 failed, 5 passed](MODEL-439/r3/red-facts.txt) | [20 passed](MODEL-439/r3/green-facts.txt) |
| `test_mixed_cited_and_open_score_sources_are_cited_with_every_ref`, both absent and historical verification | [2 failed, 8 passed](MODEL-439/r3/red-scores-confirmed.txt) | [10 passed](MODEL-439/r3/green-scores.txt) |

The score red confirmation uses #889's original quarantine branch and the
final tests. The first exploratory score run also included an invalid test
assertion that tried to retrieve a discarded sibling record; that assertion
was removed before confirming the two admission failures. No production
behavior depends on that exploratory assertion.

Mixed malformed refs remain excluded. Both cited identifier facets remain
excluded. Model and offering tests exercise verified-sibling precedence in
both input orders. The labeling checks cover mixed facts and scores in
complete and bounded decisions, named comparisons, CLI output and rendered
model pages. Existing web and MCP citation tests also pass.

Focused serial checks:

- [Engine and snapshot tests](MODEL-439/r3/focused-engine.txt): 343 passed.
- [Fact admission, round-two repair and source exclusion](MODEL-439/r3/focused-facts.txt):
  193 passed, one distribution-dependent skip. This run preceded #889 integration;
  the final tracked-file guard covers the resulting artifacts separately.
- [Mixed citation labeling modules](MODEL-439/r3/surfaces-green.txt): 28 passed.
- [Final tracked-file source guard](MODEL-439/r3/final-tracked-guard.txt):
  46 passed, one distribution-dependent skip.
- [Merged private data guards](MODEL-439/r3/data-guard-tests-corrected.txt): 112 passed.
- [Web cited-score](MODEL-439/r3/web-cited-score.txt) and
  [MCP cite-only](MODEL-439/r3/mcp-cite-only.txt): two tests each passed.
- [Restoration verification](MODEL-439/r3/restoration-check.txt): six synthetic
  snapshot roundtrips passed, covering both directions of assurance restoration.

Counts overlap; they are not a combined test total. An initial private-guard
command named a nonexistent test file and exited 4 before running tests; the
corrected command above passed. New evidence helpers pass Ruff. The
[lint comparison](MODEL-439/r3/lint-comparison.public.json) reports no new
findings in edited existing files; those files retain 22 pre-existing
findings. The [data-freeze guard](MODEL-439/r3/data-freeze.txt) passes.

## Private deployment acceptance

Every state uses the merged data #118 checkout, actual
`api.worker.vendor.export_data` exports, the production completeness gate and
a throwaway signing key. Source-cache configuration is cleared. State c uses
#866's policy in scratch only; state d uses main's unchanged policy.

Two baselines were measured separately: the advertised main commit, and the
prospective merge of main with #889. Their fact-assurance maps and all 319
corpus predictions are identical except for contract versions, as checked in
[baseline equivalence](MODEL-439/r3/baseline-equivalence.public.json).

| Check | 2026-10-21 | 2027-01-01 |
| --- | ---: | ---: |
| Production completeness gaps | 0 | 0 |
| Repository comparison cases | 302 | 302 |
| #866 first-result changes | 0 | 0 |
| #866 tie-member-set changes | 0 | 0 |
| #866 answer-kind changes | 0 | 0 |
| Main-policy first-result / tie-set / answer-kind changes | 0 / 0 / 0 | 0 / 0 / 0 |
| Main-policy fact-assurance changes | 0 | 0 |
| Worker steady memory, MiB | 109.0359 | 103.7544 |
| Worker peak memory, MiB | 109.8191 | 105.7163 |

The [actual-main comparison](MODEL-439/r3/comparison-main.public.json) records
302 contract-version changes per period from #889's contract bump. The
[integrated-baseline comparison](MODEL-439/r3/comparison-integrated.public.json)
has zero such changes. There are no changed first results, tie sets or answer
kinds to explain under either baseline. Neither comparison substitutes a
successful merge of #889 into main.

All three integrated states run 319 corpus cases with zero expectation
failures per period, including 286 contract-validated HTTP-200 responses and
269 repository HTTP-200 responses. The #866 candidate retains 945 benchmark
records, 12 cited; compared with the baseline, one `hle_tools` row becomes
operative. No decision outcome changes. Candidate facts comprise 1,472
verified and 337 cited records. Main-policy facts remain 1,727 verified and
70 cited.

The separate production gate runs report zero gaps for
[current](MODEL-439/r3/gate-current.public.json) and
[successor](MODEL-439/r3/gate-successor.public.json) periods. The deploy-style
Worker probe uses Pyodide 0.28.3, the real vendored bundle and the 115 MiB limit:
[current memory](MODEL-439/r3/memory-current.public.json),
[successor memory](MODEL-439/r3/memory-successor.public.json).
It exercises decide, vocabulary, rank and policy-check. The
[public bundle was re-vendored](MODEL-439/r3/public-vendor.txt) after the private
probe, with private data and signing credentials absent from that command.

## Assurance and preserved data repair

The [accepted-export audit](MODEL-439/r3/audit.public.json) accounts for the
same 255 verified-to-cited transitions in both periods:

| Group | Transitions |
| --- | ---: |
| Authored mixed facts admitted directly | 144 |
| Fully cite-only records, including shared inherited provenance | 101 |
| Derived mixed `model.fits_hardware` facts | 10 |
| Other | 0 |

The original 150 authored mixed facts comprise 144 directly admitted records
and six jurisdiction rows replaced through lab inheritance. Those six inherit
cited assurance from the actual shared lab record. They are not six additional
transitions, and their shared provenance is already included in the fully
cite-only count. The ten generated hardware-fit facts are counted separately
using their explicit derivation metadata.

All 255 transitions preserve their values, states and original source lists,
confirmed by [the value/reference comparison](MODEL-439/r3/transition-values.public.json).
No mixed citation loses a reference or retains nonnull verification. Twelve
additional previously unadmitted facts become cited under the wider policy.
No unresolved missing authored mixed fact remains.

The first assurance audit incorrectly counted generated facts as authored and
assumed inherited jurisdiction facts would be verified. It failed. The final
audit uses actual derivation metadata, retained source states and the public
snapshot lookup to verify inheritance against the lab record's ID, values and
sources. These corrections change measurement classification, not production
admission. Independent review found no acceptance masking. The restoration
helper's earlier record-type bug was also corrected and checked through six
real snapshot roundtrips. With zero changed outcomes, no diagnostic restoration
is needed to claim an explained decision change.

The [independent data audit](MODEL-439/r3/data-audit.public.json) proves that
round two's 48 rule-1 and four rule-2 repairs remain intact. All 150 unknown raw
facts retain their original references. Values, states, other fields and
Markdown bodies are unchanged; the verification log is byte-identical to data
main. The queue preserves its byte prefix and appends only four collected
claims and four cited checks. The linked-data guard passed all 14 pinned paths.

## Commands, reproduction and limits

[Recorded commands and direct exit codes](MODEL-439/r3/commands.public.jsonl),
[tool versions](MODEL-439/r3/versions.public.json),
[the final audit command](MODEL-439/r3/audit-command.public.json) and
[the surface command](MODEL-439/r3/surface-command.public.json) retain the
measurement and test invocations. Python was 3.14.4, pytest 9.1.1, Pydantic
2.13.5, PyYAML 6.0.3, Ruff 0.16.6, git 2.50.1 and Node 22.22.3.

For replay, clone private data into `/tmp/model-439-scratch/`, check out
`44fc4e4`, and archive the pinned public engine refs into scratch. The
[r2 preparation helper](MODEL-439/r2/prepare_baseline.py) archives refs without
changing the active checkout. `git merge-tree --write-tree 36b2d184 33c705e1`
produces the prospective baseline tree above. Use the exact pinned main commit
for the actual-main baseline. Extract #866's retention registry into scratch.
Then run the [r3 state runner](MODEL-439/r3/compare_private.py) with
`--main-root`, `--candidate-root`, `--host-policy`, `--data-dir` and `--output`;
all states share the repaired data. Run [the export audit](MODEL-439/r3/audit_exports.py)
against those results. The original [memory helper](MODEL-439/measure_private.py)
vendors and probes both periods with `--limit-mib 115`. Replays on another date
must fix the export clock to 2026-10-21. Delete the private clone and exports
when finished.

Both branches are pushed normally with `CI_LOCAL_SKIP=1`; no force push is
used. Exactly six `gh` calls were used for read-only PR inspection. No Linear
writes, source-page retrievals, paid provider calls, real signing credentials,
production deploys, production switches or full local suite were used.
The full CI shards, independent cross-model review, production runtime memory,
and #889's completed merge remain unobserved. The private clone and scratch
exports are removed before handoff, and all task processes are reaped;
[the cleanup receipt](MODEL-439/r3/cleanup.public.json) records the removed paths.
