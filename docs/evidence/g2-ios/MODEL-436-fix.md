# MODEL-436 round-two CI repair evidence

Measured on 2026-10-22 UTC in the existing `model-436-cite-only-hosts` worktree.
This report supersedes the earlier report at base commit `7d51e57a`.
PR [#866](https://github.com/turbobeest/modelspec/pull/866) remains a draft.

## Revisions

- Round-two base: `7d51e57ae0b9e7d8d8478aa71f548d8d9ca0b06d`.
- Final implementation: `563da3fc9e90c89e4b740065a924ae23e7e9fbe1`.
- Main-policy comparison: `ae149af075e1ea1e479cd5ab3a43ebce74f7ca08`.
- Private data: `ba03e11651513aa108f4031e56622717cf419acf`.

The delivery commit adds this evidence after the implementation. Its final SHA
is in the executor receipt and is reproducible with
`git rev-parse model-436-cite-only-hosts`; a commit cannot contain its own SHA.
The approved five-host policy is unchanged. Ranking floors, legal terms,
production switches, contract field ranges and frozen public data are unchanged.

## Defects and red-first evidence

The five files named in the spec ran against unchanged production code at the
base SHA: **13 failed, 166 passed**, exit 1. Seven research failures shared the
same unavailable excerpt. New regressions then returned **15 failed, 15 passed,
279 deselected**, exit 1. The focused compact-explanation red run returned
**2 failed, 2 passed, 45 deselected**, exit 1.

| Defect | Red test and observed failure | Repair and green evidence |
| --- | --- | --- |
| Admission terms hold | `test_source_terms_hold_never_fetches_or_stores[developers.openai.com-openai]` fetched the held source; `test_cli_blocks_redirect_before_target_request[https://developers.openai.com/api/docs/model]` reached the forbidden redirect. New `test_cite_only_fetcher_still_enforces_source_terms` cases failed with `DID NOT RAISE SourceBlockedError`. | Citation eligibility and permission to fetch are separate. Held cite-only sources report `cited; source-terms hold (MODEL-409); cited, not machine-verified; not fetched`, with no cache file, hash or retrieval timestamp. Request hooks enforce exact-host terms before direct and redirected requests. The complete admission modules passed the final focused rerun. |
| Invented retrieval time | `test_successful_primary_never_uses_paid_fetch_or_ledger` first differed in body, hash and retrieval time. The new cite-only parameterized case isolated `retrieved_at`: a fabricated UTC timestamp versus upstream `None`. | Fallback sanitization preserves the upstream timestamp, including `None`, while removing restricted bytes and preserving their hash. Tests cover both retained and cite-only hosts and both timestamp states. |
| Oversized full explanation | `test_public_explain_budgets[full-80000]` reported `406676 / 4 > 80000`. `test_full_display_facts_resolve_citations_through_source_ids` found repeated inline citation payloads on display-only facts. | Display-only facts retain record IDs and source IDs; inline fact citations are populated for named facets and named-model comparison. The final response is **291,795 bytes / 4 = 72,948.75**, below 80,000. All **46** shared source entries have unique IDs. |
| Retained research inputs | Seven tests raised `no retained cited region for anthropic/claude-fable-5-1#terminal_bench_v4_0#be4c454ede6e`. New `test_frozen_evidence_store_withholds_cite_only_excerpts` exposed the historical protected excerpt. | Both case builders skip cite-only evidence, and the active frozen store withholds its excerpt. Every retained case still has hash-checked bytes and exact evidence identity. The active set is 60 blind plus 20 second-key cases. The historical 61 plus 21 study and its fingerprint remain unchanged and separately asserted. |
| Public coverage and charts | `test_coverage_is_derived_from_the_cards` failed on `[93.6, 91.04]` versus `[]`; `test_every_card_evidence_record_reaches_its_benchmark_page` reported 46 missing rows. Three new chart/strip cases failed. | Existing export rows already carried citation metadata. Tests now require exact score, source URL, evidence date, source kind and assurance. Charts and strips include cited per-score evidence with "Cited, not machine-verified". Flat legacy scores remain outside evidence charts. |
| Freshness rejects admitted citations | `test_freshness_accepts_and_labels_cited_domain_evidence` failed; stale and undated cited live-reading regressions found no checked live rows. | Freshness accepts exactly verified or cited domain evidence and reports cited counts. It retains the seven-day release grace, 30-day live-source limit, observation-date rules and rejection of unadmitted rows. |

Review found a warning dependency while compacting display facts. The new
`test_display_only_cited_fact_preserves_decision_and_summary_warnings` failed
at `assert WARNING in answer.warnings`, exit 1, in a standalone offline call.
After `_CitationUse.shown` checked the retained `record_id`, the identical call
passed, exit 0. It checks the complete warning, bounded warning, summary notice
and must-mention notice. The outside-answer case still forbids a top-level warning.

No contract shape changed. `ShownFact.citation` was already optional. Named
facets and named-model comparison retain complete citation metadata; display
facts still resolve exact sources and records. `docs/decision-contract.md`
documents this population rule. Complete 2.19 and bounded 1.5 remain unchanged.

## Validation

The first broad focused run returned **3 failed, 1,113 passed, 1 skipped**, exit 1.
The remaining failures were a transient-fetch fixture that still used forbidden
terms, a paid-fetch stub that supplied no retrieval timestamp, and an assertion
that required optional display citation payloads. Their replacements preserve
exact source identity, hash, timestamp and warning-scope checks.

The next full-module rerun returned **148 passed in 42.15s**, exit 0, covering
admission, fallback, bounded decisions and citation-warning scope.

The final complete required set returned **1,117 passed, 1 skipped in 306.95s**,
exit 0. It includes all five named CI files, `test_accuracy`, every
`test_cite_only_*` and `test_cited_score*` module, `test_class_fit`, `test_legal`,
`test_decision_explain` and `test_removed_sources`. This run includes the final
warning fix and exact-source fixture assertions. `git diff --check` and the
data-freeze guard also pass.

The exact CI PR accuracy profile passed, exit 0:

- Deterministic correctness: 1,301 tests passed across 18 suites.
- Freshness: 44 lineup models, 872 live readings and zero failures. The report
  labels 18 domain records as cited, not machine-verified; one model has only
  cited domain evidence.
- Frozen-image recall: all 20 verdicts match the approved public baseline, with
  zero regressions. The unchanged baseline contains 15 pass, four partial and
  one fail verdict; passing the gate does not mean all questions are resolved.
- Output parity: 678 Python tests passed with one optional-corpus skip, and
  all 228 web-adapter tests passed.

The required focused set skips the optional built-dist excluded-source scan
because `MODELSPEC_DIST` is unset; its tracked-file scan runs. Accuracy output
parity also skips `test_every_recall_contract_spec_has_worker_cli_parity` because
its optional `**/*.spec.yaml` corpus is absent. No local full suite is run;
CI's four pytest shards remain the authoritative full gate.

## Private deployment measurements

The same pinned private checkout feeds baseline `a`, candidate `c`, and
candidate-with-main-policy control `d`. Fresh processes invoke the real
`api.worker.vendor.export_data`, whose premier completeness gate remains enabled.
The current and successor snapshots are evaluated at their own validity dates.
The helper uses the public throwaway HMAC key
`model439-private-proof-throwaway-key`; inherited private-data, source-cache and
signing-key variables are removed. No real signing secret is used.

Both the a/c/d comparator and the strict zero-change comparator returned exit 0.
The main-policy control reproduces main. All 319 corpus expectations pass in
each state and period, and every cited benchmark record has null verification.

| Measure | Current | Successor |
| --- | ---: | ---: |
| Completeness gaps, gate enabled | 0 | 0 |
| Repository corpus cases compared | 302 | 302 |
| First-result model changes | 0 | 0 |
| Tie-member-set changes | 0 | 0 |
| Answer-kind changes | 0 | 0 |
| Ordered result-model changes | 0 | 0 |
| HTTP, status or contract changes | 0 | 0 |
| Corpus expectation failures, all 319 cases | 0 | 0 |

The final engine and explanation source bytes match both the staged candidate
used for comparison and the final private memory bundle. The requested zero-gap,
zero-outcome-change and at-most-115-MiB results still hold.

The final Worker probe re-vendors private data, loads Pyodide 0.28.3 and exercises
`/v1/decide`, `/v1/vocabulary`, `/v1/rank` and `/v1/policy-check` in both periods.
It runs with the unchanged **115 MiB** steady limit.

| Period | Steady bytes | Steady MiB | Peak MiB | Result |
| --- | ---: | ---: | ---: | --- |
| Current | 109,728,800 | 104.645538 | 105.438118 | exit 0 |
| Successor | 108,793,200 | 103.753281 | 105.728867 | exit 0 |

An earlier probe, before the warning fix, also passed both periods. The table is
from a fresh final-code probe. No rows were dropped, limits raised or retry used
to pass the memory gate. These are local Pyodide measurements, not production
Cloudflare measurements. The weekly private data-trust audit was not rerun in
this round; the private SHA is the same as in the prior report.

After private measurement, public re-vendoring with private-data and signing
variables cleared returned **129 files, clean imports**, exit 0. All generated
files match their source bytes, and `bundled_data.py` is absent.

## Reproduction commands

Run in `/Users/terbeest/dev/worktrees/model-436`. Each recorded command uses
`subprocess.run`, saves stdout/stderr and propagates the child's direct exit code.
All pytest processes run serially with cacheprovider disabled. Node is pinned.

```sh
P=/Users/terbeest/dev/modelspec/.venv/bin/python
S=/tmp/model-436-scratch/root
NODE=/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node
mkdir -p "$S/tmp"
cp docs/evidence/g2-ios/MODEL-439/r2/run_recorded.py "$S/run_recorded.py"
export PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=0
export MODELSPEC_SOURCE_CACHE="$S/empty-source-cache"

# At 7d51e57a, before production changes:
"$P" "$S/run_recorded.py" red-ci "$P" -m pytest -q -p no:cacheprovider \
  tests/test_admission_drafter.py tests/test_admission_fallback.py \
  tests/test_decide_bounded.py tests/test_jev_recommendations_research.py \
  tests/test_pipeline.py --tb=short

# With new tests but unchanged production:
"$P" "$S/run_recorded.py" red-regressions "$P" -m pytest -q -p no:cacheprovider \
  tests/test_admission_drafter.py tests/test_admission_fallback.py \
  tests/test_cite_only_caller_isolation.py tests/test_jev_recommendations_research.py \
  tests/test_accuracy.py tests/test_pipeline.py \
  -k 'source_terms or successful_primary or cite_only_draft or cite_only_fetcher or retained_research_cases_exclude or frozen_evidence_store_withholds or freshness or cited_evidence_reaches or benchmark_chart_counts or cited_flat_score' \
  --tb=short
"$P" "$S/run_recorded.py" red-compact "$P" -m pytest -q -p no:cacheprovider \
  tests/test_decide_bounded.py -k 'public_explain_budgets or full_display_facts' --tb=short

# Identical standalone red and green warning check:
"$P" -c 'from tests.test_cite_only_warning_scope import test_display_only_cited_fact_preserves_decision_and_summary_warnings; test_display_only_cited_fact_preserves_decision_and_summary_warnings()'

# Final required regression run, plus touched accuracy/explanation paths:
"$P" "$S/run_recorded.py" required-final "$P" -m pytest -q -p no:cacheprovider \
  tests/test_admission_drafter.py tests/test_admission_fallback.py \
  tests/test_decide_bounded.py tests/test_jev_recommendations_research.py \
  tests/test_pipeline.py tests/test_accuracy.py tests/test_cite_only_*.py \
  tests/test_cited_score*.py tests/test_class_fit.py tests/test_legal.py \
  tests/test_decision_explain.py tests/test_removed_sources.py --tb=short

# Exact PR accuracy profile from .github/workflows/accuracy.yml:
git show ae149af075e1ea1e479cd5ab3a43ebce74f7ca08:tests/recall/baseline.json \
  > "$S/approved-recall-baseline.json"
(cd web && env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
  "$P" "$S/run_recorded.py" npm-ci npm ci)
env -u MODELSPEC_DATA_DIR -u MODELSPEC_SNAPSHOT_KEY -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  PYTEST_ADDOPTS='-p no:cacheprovider' \
  PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
  "$P" "$S/run_recorded.py" accuracy "$P" scripts/accuracy.py --profile pr \
  --approved-recall-baseline "$S/approved-recall-baseline.json" \
  --output-dir "$S/accuracy-report"
```

The baseline archive used this command. No additional worktree or branch was
created.

```sh
"$P" - <<'ARCHIVE'
from pathlib import Path
import io, subprocess, tarfile
root = Path('/tmp/model-436-scratch/root/main-ae149af0')
root.mkdir()
raw = subprocess.run([
    'git', 'archive', 'ae149af075e1ea1e479cd5ab3a43ebce74f7ca08',
], check=True, capture_output=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    archive.extractall(root, filter='data')
ARCHIVE
```

Private measurement commands:

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git "$S/modelspec-data"
git -C "$S/modelspec-data" rev-parse HEAD
# The initial clone matched this SHA. It was explicitly pinned again before cleanup.
git -C "$S/modelspec-data" fetch --depth 1 origin ba03e11651513aa108f4031e56622717cf419acf
git -C "$S/modelspec-data" checkout --detach ba03e11651513aa108f4031e56622717cf419acf
env -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR \
  -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY TMPDIR="$S/tmp" \
  "$P" "$S/run_recorded.py" comparison "$P" \
  docs/evidence/g2-ios/MODEL-439/r3/compare_private.py \
  --main-root "$S/main-ae149af0" --candidate-root "$PWD" \
  --host-policy "$PWD/registry/source-retention.json" \
  --data-dir "$S/modelspec-data" --output "$S/results"
"$P" "$S/run_recorded.py" compare-strict "$P" \
  docs/evidence/g2-ios/MODEL-439/r2/compare_private.py compare \
  --output "$S/results" --states ac

env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
  npm install --prefix "$S/memory-runtime" --no-save pyodide@0.28.3
env -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR \
  -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY TMPDIR="$S/tmp" \
  "$P" "$S/run_recorded.py" memory-final "$P" \
  docs/evidence/g2-ios/MODEL-439/measure_private.py \
  --code "$PWD" --data-dir "$S/modelspec-data" --output "$S/memory-final" \
  --node "$NODE" --runtime "$S/memory-runtime"

env -u MODELSPEC_DATA_DIR -u MODELSPEC_SOURCE_CACHE \
  -u MODELSPEC_SNAPSHOT_KEY -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  MODELSPEC_REQUIRE_DATA_DIR=0 PYTHONPATH=$PWD \
  "$P" api/worker/vendor.py --check
"$P" - <<'BUNDLE'
from api.worker.vendor import REPO_ROOT, BUNDLE, SOURCES
assert all((REPO_ROOT / source).read_bytes() == (BUNDLE / dest).read_bytes()
           for source, dest in SOURCES.items())
assert not (BUNDLE / 'bundled_data.py').exists()
print(f'{len(SOURCES)} public-vendored files match source bytes')
BUNDLE

"$P" scripts/data_freeze_guard.py --base ae149af075e1ea1e479cd5ab3a43ebce74f7ca08 \
  --head HEAD --branch model-436-cite-only-hosts
git diff --check
CI_LOCAL_SKIP=1 git push -u origin model-436-cite-only-hosts
```

Tool versions: Python 3.14.4, pytest 9.1.1, pydantic 2.13.5, PyYAML 6.0.3,
httpx 0.28.1, cryptography 45.0.7, Node 22.22.3, Pyodide 0.28.3, Git 2.50.1,
and GitHub CLI 2.102.0.

## Limits and cleanup

No vendor API spend, live source-page fetch, external verification of cited
values, deployment, full local suite, CI-shard run, production-switch change,
Linear write or merge was performed. No private data or page bytes were added
to the public repository. No claim is made that complete response bytes are
unchanged: the purpose of the explanation fix is to remove repeated payloads.

The private checkout was clean before deletion. All test and measurement
processes completed and their direct exit codes were read. The following
command removed the private clone, overlays, exports, memory bundles, logs and
all four task-owned scratch directories. It returned exit 0.

```sh
"$P" - <<'CLEANUP'
from pathlib import Path
import shutil, subprocess
scratch = Path('/tmp/model-436-scratch/root')
status = subprocess.run([
    'git', '-C', str(scratch / 'modelspec-data'), 'status', '--porcelain',
], check=True, capture_output=True, text=True)
assert not status.stdout, 'private checkout changed'
for name in ('root', 'admission', 'research', 'pipeline'):
    path = Path('/tmp/model-436-scratch') / name
    assert path.resolve() == Path('/private/tmp/model-436-scratch') / name
    if path.exists():
        shutil.rmtree(path)
    assert not path.exists()
CLEANUP
```

The push uses `CI_LOCAL_SKIP=1` after the focused suites as required. PR #866
stays draft for independent review. No new PR, merge or Linear update is part
of this execution.
