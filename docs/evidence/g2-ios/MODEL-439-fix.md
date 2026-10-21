# MODEL-439 round 2: preserve existing verification

The repair is **BLOCKED on missing historical source attribution**. The script
now preserves verified retained support and leaves ambiguous facts unchanged.
The rebuilt data draft applies 48 rule-1 repairs and four rule-2 repairs; 150
raw mixed facts remain unchanged. This report supersedes round one's claim
that all 202 facts should use rule 2. An unavailable copy did not establish
that a retained source failed to support a value.

The main-policy control passes. State d has zero changes across all 302 repository
cases in both periods, zero fact-assurance changes and zero verified-to-cited
changes. With #866's policy, the actual deployment export fails with 144 completeness
gaps. A separate diagnostic snapshot also shows 101 verified-to-cited changes
outside the 202 mixed facts in this repair.

## Revisions and drafts

- Executor base: `77a9566822f7a23e322d2647913c755ad3cb7ed8`.
- Final implementation/test SHA: `40dbb5e290b5f4753ac23ca79abeead926850d0a`.
- Measured engine main and data `.engine-pin`: `36b2d184dcc5a67a90ceb1a9015275143c09691d`.
- Policy #866: `82ebcf4627d255d7641303caff2d149e879cf359`.
- Data merge base: `9d9de96f062ac031336ee483ae97c3b436bd3845`.
- Rebuilt data head: `0b2596afbb680e747cefb097500c91602b93d77a`.
- Replaced data head: `f722d3fcb673b28bdff9fa1b5cac06c22cc61c38`.
- [Engine PR #891](https://github.com/turbobeest/modelspec/pull/891) and
  [data PR #118](https://github.com/turbobeest/modelspec-data/pull/118) remain drafts.

The final branch SHA is in the round-two PR comment and executor completion
marker. Commits after the implementation SHA contain evidence only; this file
cannot contain the hash of its own commit. No engine source, contract, ranking
floor, legal text, production switch or frozen public data was changed.

## Why the records permit only a partial repair

The snapshot matches verification by target kind, ID and value hash, including
unordered-set handling, then selects by date and log order. Source lists are
not part of that hash. The script uses the same `_Compiler._verdicts` lookup and
confirms reduced-source admission through `_Compiler._add_facts`. Every rule-1
fact retains its exact winning verification. No verification record is created.

That admission check cannot establish source support by itself. Verification
records omit the successful source and region, and queue checks record only an
outcome. The repair reconstructs the collected source references for each check,
including temporary copy changes and their reset after a check. It groups log
records and checks by target, date, collector, outcome and bound value. It uses
only fully accounted-for groups whose records all independently verify the
claim. It never pairs different source lists merely by their position in the
logs. Current support must match the subject, facet, source ID, snapshot hash
and still-cited regions. Matching failures, including inline failures, invalidate
older support.

An earlier retained-only check can establish rule 1 when its exact references
and current value still match. Rule 2 requires the winning group's checks to
be exclusively cite-only and at least one to match the current references.
An earlier cited-only check followed by an unattributed mixed winner remains
unknown. Dated prices remain unchanged with an explicit schedule limitation;
checking a full offering schedule is outside this script's current admission
check. No dated mixed prices occurred in this repair.

The 202 winning raw-fact records comprise 196 `retained-source-proof@1`, four
`model-page-label-match@1`, and two `licence-terms@3` records. The first method's
producer searched across all cited sources and discarded which source supplied
its proof terms. The two licence checks also used mixed references, including
binding pages. Neither method name establishes the necessary source attribution.
Earlier exact-reference checks recover 48 retained facts. Forty other earlier
cited checks have newer mixed winners and remain unknown. No page was re-read,
fetched or restored to infer the missing attribution.

The four rule-2 rows are:

- `openai/gpt-5-4#origin.lab_jurisdiction`
- `openai/gpt-5-6-sol#origin.lab_jurisdiction`
- `openai/gpt-6-astra#origin.lab_jurisdiction`
- `openai/gpt-6-sol#origin.lab_jurisdiction`

The snapshot replaces these raw model rows with inherited lab facts. They cause
zero admitted verified-to-cited changes in the main-policy control. The six
other raw jurisdiction rows remain unknown and are also replaced by inheritance.

## Data audit and facet split

The [independent byte and semantic audit](MODEL-439/r2/data-audit.public.json)
passed. Exactly 52 facts across ten model files change references. Rule 1 removes
48 cite-only refs; rule 2 removes four retained refs. Values, states, other
fields and Markdown bodies are unchanged. All 150 unknown facts retain their
original references. `verification/log.jsonl` is byte-identical to the merge
base. The queue preserves its byte-exact prefix and appends only four collected
claims and four cited checks. Rule 1 appends no synthetic verification check.
No code was added under data paths. The linked-data guard passed all 14 pinned
engine paths. A repeated write makes zero repairs and still reports the 150
unknown rows, as recorded in [the second run](MODEL-439/r2/second-run.public.json).

Counts below describe raw facts, before jurisdiction inheritance.

| Facet | Rule 1 | Rule 2 | Unknown, unchanged |
| --- | ---: | ---: | ---: |
| `feature.batch` | 6 | 0 | 4 |
| `feature.effort_controls` | 6 | 0 | 4 |
| `feature.streaming` | 0 | 0 | 10 |
| `feature.structured_output` | 0 | 0 | 10 |
| `feature.tool_calling` | 0 | 0 | 10 |
| `licence.commercial_use` | 0 | 0 | 11 |
| `licence.fine_tuning` | 0 | 0 | 10 |
| `licence.output_training` | 0 | 0 | 11 |
| `licence.user_cap` | 0 | 0 | 10 |
| `model.class` | 6 | 0 | 4 |
| `model.context_window` | 6 | 0 | 4 |
| `model.input_modalities` | 0 | 0 | 10 |
| `model.lifecycle` | 6 | 0 | 4 |
| `model.max_output_tokens` | 6 | 0 | 4 |
| `model.output_modalities` | 0 | 0 | 10 |
| `model.release_date` | 0 | 0 | 10 |
| `model.weights_openness` | 0 | 0 | 10 |
| `origin.base_lineage` | 6 | 0 | 4 |
| `origin.lab_jurisdiction` | 0 | 4 | 6 |
| `origin.weights_hosting` | 6 | 0 | 4 |
| **Total** | **48** | **4** | **150** |

The 48 retained repairs cover eight facets on each of the six Anthropic models
in the original repair. All 42 licence facts remain unknown. The existing log
and queue records cannot resolve the remaining support without additional
source-specific historical evidence. Unavailability is never a rule-2 input.

## Red-first and focused checks

Captured test-log copies omit trailing whitespace.

| Behavior | Red output | Green output |
| --- | --- | --- |
| Missing retained copy with existing retained support: `test_missing_retained_copy_preserves_existing_retained_verification` | [1 failed](MODEL-439/r2/red-missing-copy.txt); old script chose rule 2 instead of rule 1 | [1 passed](MODEL-439/r2/green-missing-copy.txt); original verification retained |
| Invalidated or misfiled historical support: `test_invalidated_or_misfiled_history_cannot_prove_retained_support` | [4 failed, 1 passed](MODEL-439/r2/red-history.txt); mismatches and wrong subject/facet failed open | Final module passes all five cases |
| Repeated cite-only history: `test_repeated_cited_checks_preserve_unambiguous_winning_side` | [1 failed](MODEL-439/r2/red-cited-group.txt); older hashes hid an unambiguous cited winning side | Final module passes |
| Dated offering admission: `test_verified_dated_price_requires_complete_schedule_and_stays_unchanged` | [2 failed](MODEL-439/r2/dated-price-red.txt); actual compiler `KeyError` | [2 passed](MODEL-439/r2/dated-price-green.txt); unchanged with explicit unknown reason |

The [final script module](MODEL-439/r2/script-suite-green.txt) passes **26 tests**
in 16.21 seconds. It also exercises queue copy resets, log/check ambiguity,
stale values, historical retained support under a later mixed winner, refusal
to infer sole cited support from an older check, identifier exceptions, current
source hashes, YAML safety and idempotency. Existing tests that expected
unreachable or mismatch fallback were corrected to assert the round-two rule;
byte-preservation and snapshot-admission assertions remain.

The [broader focused run](MODEL-439/r2/focused-green.txt) passed **582 tests,
1 skipped** in 140.14 seconds. It covers the repair, cite-only admission, engine
verifier and removed-source guard. It preceded the final four script cases;
the final 26-test module covers the resulting script. Counts overlap. The skip
requires `MODELSPEC_DIST`. Ruff, diff checks and the data-freeze guard pass.
The [tracked-file source guard](MODEL-439/r2/final-tracked-guard.txt) also passed
after staging the evidence. No full local suite was run. CI's four shards
remain the full-suite authority.

## Measurements

The measurements pin engine main, the original data base, #866's policy and the
rebuilt data head. State a uses original data with main's policy; state d uses
repaired data with main's policy. Both use actual `api.worker.vendor.export_data`
exports, a throwaway signing key and the production completeness gate. Source
cache configuration is cleared. The current period is 2026-10-21; the successor
period is 2027-01-01.

| State d versus a | Current | Successor |
| --- | ---: | ---: |
| Repository cases | 302 | 302 |
| First-result changes | 0 | 0 |
| Tie-member-set changes | 0 | 0 |
| Answer-kind changes | 0 | 0 |
| Fact-assurance changes | 0 | 0 |
| Verified-to-cited changes | 0 | 0 |

Both states retain 944 benchmark records, 1,727 verified fact records and 70
cited fact records. Both run all 319 corpus cases with zero expectation failures,
286 contract-validated HTTP-200 cases and 269 repository HTTP-200 cases per
period. The [comparison](MODEL-439/r2/comparison-ad.public.json) explicitly records
all zero counters. Its older `acceptance_passed` field is null because that field
only aggregates b/c comparisons; it does not represent a failed d control.

The [actual state-b export](MODEL-439/r2/deploy-b.public.json), with repaired data
and #866's policy, exits 1 and writes no decision snapshot. Separate gate audits
measure [192 gaps before](MODEL-439/r2/gate-before.public.json) and
[144 after](MODEL-439/r2/gate-after.public.json), all mixed-citation quarantine,
across 11 models. Exactly 48 gaps disappear; no new gaps appear. The 150 raw
unknown rows include six inherited jurisdiction rows, which explains why the
remaining gate count is 144.

To measure the failing state without accepting it for deployment, a separate
`audit_build` run produces diagnostic snapshots. These are labelled
`diagnostic_only: true` and `deploy_export_accepted: false`. The actual deploy
export's gate remains enabled and failed. These diagnostics are not substitute
acceptance artifacts.

| Diagnostic b versus a | Current | Successor |
| --- | ---: | ---: |
| Repository cases | 302 | 302 |
| First-result changes | 59 | 72 |
| Tie-member-set changes | 84 | 83 |
| Answer-kind changes | 4 | 2 |
| Answer-kind or member-set changes | 84 | 84 |
| Verified-to-cited changes | 101 | 101 |
| Verified to not admitted | 154 | 154 |
| Not admitted to cited | 12 | 12 |
| Admitted benchmark records | 933 | 933 |

The diagnostic corpus has zero expectation failures over all 319 cases in both
periods. The stricter [302-case comparison](MODEL-439/r2/diagnostic-comparison-ab.public.json)
exits 1. First result is `results[0].model`; tie sets are sorted `answer.members`
for tied answers. These results include the unresolved facts as well as #866's
policy change. The expected loss of eleven benchmark records is present, but
round one's 66/66 first-result changes are not reused as a round-two measurement.

The [assurance audit](MODEL-439/r2/diagnostic-assurance.public.json) counts 1,472
verified and 183 cited fact records in each diagnostic b snapshot. All 101
verified-to-cited IDs are identical across periods and lie outside the original
202 mixed facts. Their intersection with the four raw rule-2 rows is zero,
confirmed by the [scope check](MODEL-439/r2/diagnostic-verified-to-cited-scope.public.json).
They reflect #866's wider retention-policy change. The acceptance target of only
genuine rule-2 downgrades is therefore not met in this diagnostic comparison.

The private [round-two data PR comment](https://github.com/turbobeest/modelspec-data/pull/118#issuecomment-6324618242)
lists every one of the 101 downgraded facts, all 150 unresolved facts, all four
rule-2 facts, and the retained source/region/hash plus historical log group and
queue lines for each of the 48 rule-1 facts. No private fact values or scores
are included in the public evidence.

State b's steady-memory acceptance remains unobserved. Its actual gated export
produced no snapshot to probe, so neither a <=115 MiB pass nor round one's memory
figures are claimed for this revision. This patch changes no Worker export
fields. All private exports and diagnostic snapshots stayed in scratch.

Exact measurement argv, working directories and exits are retained in
[the command record](MODEL-439/r2/measurement-commands.public.jsonl), with
[pinned revisions](MODEL-439/r2/identities.public.json) and
[tool versions](MODEL-439/r2/versions.public.json). The six adjacent helpers
reproduce preparation, gated exports, comparisons, completeness diagnostics and
assurance scope. Diagnostic evaluation requires `state --reuse-exports --diagnostic`.
Replay on another calendar day must fix the export clock to 2026-10-21.

## Reproduction

Versions used: Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3,
Ruff 0.16.6, git 2.50.1 and Node 22.22.3. Tests ran serially with cacheprovider
disabled. Exit codes were read directly, never through a pipeline.
The [additional regression command record](MODEL-439/r2/commands-and-exits.json)
includes exact arguments, versions and exits.

```bash
cd /Users/terbeest/dev/worktrees/model-439
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
DATA=/tmp/model-439-scratch/modelspec-data
RUN=/tmp/model-439-scratch/executor-r2

git fetch origin main pull/866/head:refs/remotes/origin/pr-866
git clone https://github.com/turbobeest/modelspec-data.git "$DATA"
git -C "$DATA" switch -c model-439-mixed-citation origin/model-439-mixed-citation
# This is the original branch's merge base, confirmed before resetting.
git -C "$DATA" reset --hard 9d9de96f062ac031336ee483ae97c3b436bd3845
git rev-parse origin/main > "$DATA/.engine-pin"
git show origin/pr-866:registry/source-retention.json > "$RUN/hosts-866.json"

# Each red command ran before its corresponding fix.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k missing_retained_copy
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k invalidated
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k repeated_cited
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py -k verified_dated_price
# Focused green commands.
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py tests/test_cite_only_verification.py tests/test_decision_verify.py tests/test_removed_sources.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_refile_mixed_citations.py
"$PY" -m ruff check scripts/refile_mixed_citations.py tests/test_refile_mixed_citations.py docs/evidence/g2-ios/MODEL-439/r2/audit_repair.py
"$PY" scripts/pytest_shards.py --shard-count 4 --summary

# No copy bytes are supplied or read. Omit --write to inspect the plan.
env PYTHONPATH=$PWD "$PY" scripts/refile_mixed_citations.py \
  --data-root "$DATA" --source-cache "$RUN/empty-copies" \
  --policy "$RUN/hosts-866.json" --as-of 2026-10-21 --write
# The same --write command was repeated, with zero repairs.
env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-439/r2/audit_repair.py \
  --data-root "$DATA" --base 9d9de96f062ac031336ee483ae97c3b436bd3845 \
  --engine-pin 36b2d184dcc5a67a90ceb1a9015275143c09691d \
  --policy "$RUN/hosts-866.json" --plan "$RUN/repair.private.json" \
  --output "$RUN/data-audit.public.json"
"$PY" -I "$DATA/.github/scripts/check_linked_data.py" --engine "$PWD" --data "$DATA"
env PYTHONPATH=$PWD "$PY" scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-439-mixed-citation
git diff --check
git -C "$DATA" diff --check

# Explicit round-two authorization applies only to this existing draft branch.
CI_LOCAL_SKIP=1 git -C "$DATA" push \
  --force-with-lease=refs/heads/model-439-mixed-citation:f722d3fcb673b28bdff9fa1b5cac06c22cc61c38 \
  -u origin model-439-mixed-citation
CI_LOCAL_SKIP=1 git push -u origin model-439-mixed-citation
```

## Limits and handoff

The required zero-gap acceptance and diagnostic status/answer comparison do not
pass. State d passes, but that does not establish acceptance under #866. No
successful gated state-b export, state-b memory measurement, production runtime
measurement, full local pytest, full two-site build or release-chart check is
claimed. The 115 MiB bound remains unmeasured for this revision.
The engine's support for reduced source sets is confirmed, so the spec's
reduced-set STOP condition does not apply. The unresolved blocker is source
attribution for the 150 unchanged raw facts. Their complete report is generated
by the repair command in the private checkout; only aggregate counts are stored
here. No private values, exports, predictions or raw private error logs are
committed to this public repository. No source-page reads, vendor API calls,
real signing secrets, production deploys or production switches were used.
The private clone and exports are deleted after the measurements. All processes
started for the task exit before handoff. Independent review and completed
remote CI results remain unobserved.
