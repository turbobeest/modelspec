# MODEL-436 final execution evidence

Measured on 2026-10-22 UTC. This report supersedes the earlier measurements in
this file. The five approved hosts are `www.anthropic.com`,
`developers.openai.com`, `help.openai.com`, `chatgpt.com`, and `cursor.com`.
PR #866 remains a draft.

## Revisions and scope

- Starting branch SHA: `82ebcf4627d255d7641303caff2d149e879cf359`.
- Main and production comparison: `ae149af075e1ea1e479cd5ab3a43ebce74f7ca08`.
- Merge commit: `6705e9174f8536593dccda327c2f5fb54abc12bf`, with the starting
  branch and main as its parents.
- Final implementation SHA: `f6bc6520b5fbe72b7afe99ea6bb878f602b8c523`.
- Private data main: `ba03e11651513aa108f4031e56622717cf419acf`.

The delivery commit adds this evidence after the implementation commit. Its SHA
is recorded in the executor receipt and can be reproduced with
`git rev-parse model-436-cite-only-hosts`; a commit cannot contain its own SHA.

Main merged without textual conflicts. Focused tests then caught a semantic
merge issue: the branch's host-boundary tests still imported `is_cite_only`,
which main removed. They now use `cite_only_status(url) is False`, preserving
the boundary assertion and rejecting an indeterminate result. No production
Python code changed relative to main. The production change remains the five
registry hosts. Ranking floors, legal text, contracts and production switches
are unchanged.

## Deploy-style private comparison

All states used the same pinned private checkout. State `a` used main's code and
policy; `c` used this branch's code and policy; `d` used this branch's code with
main's policy as a control. Separate processes built real
`api.worker.vendor.export_data` exports, then evaluated them without stale
registry caches. The exporter calls `snapshot.build_from_repo` with the private
`premier/slice-1.yaml` and the default `gate=True` in both periods. It used the
helper's public throwaway HMAC key, `model439-private-proof-throwaway-key`.
Inherited source-cache, private-data and Ed25519-key variables were removed.

The current export is dated 2026-10-22 and expires on 2027-01-01. The successor
starts on 2027-01-01. Evaluation advances the snapshot validity clock to each
export's date. Every tracked file in staged candidate `c` matched implementation
commit `f6bc6520` byte for byte before this evidence update.

| Measure | Current | Successor |
|---|---:|---:|
| Completeness gaps, gate enabled | 0 | 0 |
| Repository corpus cases compared | 302 | 302 |
| First-result model changes | 0 | 0 |
| Tie-member-set changes | 0 | 0 |
| Answer-kind changes | 0 | 0 |
| Ordered result-model changes | 0 | 0 |
| HTTP, status or contract changes | 0 | 0 |
| Corpus expectation failures, all 319 cases | 0 | 0 |

First result means `results[0].model`, or null when no results. A tie set means
sorted `answer.members` for a tied answer, otherwise an empty set. Answer kind
means `answer.kind`. There are no changed cases to explain. This does not claim
byte-identical responses: snapshot identifiers, assurance and citation warnings
change.

The main-policy control reproduced main with zero outcome or assurance
changes in both periods. The stricter candidate comparator passed its explicit
zero-change gate. The export audit found zero unexplained cases.

| Cause of verified-to-cited transition | Current | Successor |
|---|---:|---:|
| Authored facts with mixed retained/cite-only references | 144 | 144 |
| Facts whose references are all cite-only | 101 | 101 |
| Derived mixed `model.fits_hardware` facts | 10 | 10 |
| Other | 0 | 0 |
| Total | 255 | 255 |

There are 150 authored mixed guaranteed facts in the input. Of those, 144 are
admitted directly as cited and six use their shared cited lab-jurisdiction
records. The audit found zero unexplained absences, zero missing mixed citation
references and zero non-null verification fields on admitted mixed citations.
The 10 derived hardware-fit records also remain admitted as cited.

In each period, 12 additional facts enter as cited, no facts leave, and no fact
becomes newly verified. Fact totals change from 1,797 to 1,809: verified facts
from 1,727 to 1,472, and cited facts from 70 to 337. Benchmark evidence records
change from 944 to 945, including 12 cited records in the candidate. The added row is for `hle_tools`.
Every cited
benchmark record has null verification.

Top-level citation warnings change from 3 to 140 corpus cases in the current
period and from 3 to 134 in the successor. Among the 40 summary-template cases,
the counts change from 1 to 18 and from 1 to 16 respectively. These provenance
changes leave the requested outcome measures unchanged.

## Private Worker memory and data trust

The memory helper invoked `vendor.py --data-dir` with the branch's actual policy
and private checkout, then exercised decide, vocabulary, rank and policy-check
through Pyodide 0.28.3. Both first attempts passed `--limit-mib 115`.

| Period | Steady bytes | Steady MiB | Peak MiB | Limit MiB |
|---|---:|---:|---:|---:|
| Current | 114,334,827 | 109.038188 | 112.577151 | 115 |
| Successor | 109,729,539 | 104.646243 | 107.842151 | 115 |

The current peak exceeds the separate 112 MiB warning threshold. The enforced
steady limit is 120,586,240 bytes. No retry, data reduction or limit change was
needed. These are local Pyodide measurements, not live Cloudflare measurements.

The weekly audit ran `scripts.data_trust data`, which performs load, calibrate
and invariants without sampling. It made no source requests and wrote no defect
ledger. Both dates returned exit 0 and zero invariant errors. Warnings were
3,258 current and 7,118 successor, with the following rule counts.

| Warning rule | Current | Successor |
|---|---:|---:|
| `benchmark_range_unbounded` | 715 | 715 |
| `benchmark_unit` | 690 | 690 |
| `citation_undated` | 164 | 164 |
| `field_slo` | 405 | 4,265 |
| `offering_or_verified_open_weights` | 1,284 | 1,284 |

## Public artifacts

The four documented generators ran successfully. Page fixtures, the QA MCP
contract fixture, the MCP hardware-fit fixture, agent prose, and the remaining
schemas stayed unchanged. Only `cli/modelspec/agent-bundle.json` changed:

- Engineering/STEM coverage increased from 26 to 28 models.
- Maths coverage increased from 31 to 32 models.
- The public coverage snapshot changed from `snap_52cd9d32350ce919` to
  `snap_fe8ddebc7e3d6dff`.

Regenerating the same bundle from the main archive reproduced main's committed
counts and snapshot exactly, isolating this difference to the host policy.
The frozen source data did not change. The first baseline generator invocation
failed because macOS exposed `/tmp` as `/private/tmp` while the generator used
`Path(__file__).relative_to(ROOT)`. Invoking the resolved absolute path passed;
no repository code changed for that scratch-path issue.

After private measurement, the public Worker was re-vendored with private-data
and signing variables cleared. `vendor.py --check` reported 129 files and clean
imports using declared dependencies. All 129 generated files matched their
source bytes, including the retention registry. `bundled_data.py` was absent.
The data-freeze guard passed.

## Red-first and focused tests

Before the merge or any new edits, the branch's existing host tests ran with
main's three-host retention policy injected through `retention.POLICY_PATH`.
They returned `41 failed, 79 passed in 1.06s`, exit 1.

| Test | Observed red output |
|---|---|
| `test_cite_only_policy_contains_exactly_the_approved_hosts` | Five expected hosts missing from the policy |
| `test_copy_store_cite_only_keeps_only_citation` | Ten host/subdomain cases failed `assert not store.has(ref)` |
| `test_cite_facts_satisfy_premier_completeness_without_verification` | Five cases raised `CompletenessError`; five retained non-null verification |
| `test_grok_warning_stays_on_its_row_unless_the_answer_recommends_it` | Twenty cases lacked `cite_only_not_machine_verified` |

The first merged run then returned exit 2 at collection with
`ImportError: cannot import name 'is_cite_only' from 'decision.retention'`.
After the test API migration, those three modules plus page fixtures returned
`228 passed in 1.16s`, exit 0. The larger count includes main's added tests.
Page fixture regeneration separately returned `13 passed in 0.53s`.

The final focused run returned `1106 passed, 1 skipped in 144.00s`, exit 0.
It included all cite-only modules, curation, pricing rereads and fallbacks,
fetchers, lab jurisdiction, generated page and agent artifacts, Worker imports
and successor bundling, `tests/test_class_fit.py` and `tests/test_legal.py`.
The skip is the optional existing-source-cache test; an empty scratch cache was
selected so the operator's retained cache was not read.

The final excluded-source guard returned `46 passed, 1 skipped in 118.62s (0:01:58)`, exit 0.
It scanned the tracked evidence and test changes. Its skip requires a built
`MODELSPEC_DIST`, which this focused run did not supply. `git diff --check` also
passed.

All tests ran serially with `-p no:cacheprovider`. CI's four pytest shards remain
the authoritative full run. No local full suite was run.

## Reproduction commands

Commands ran in `/Users/terbeest/dev/worktrees/model-436`. The shorthand below
expands to the paths used. The copied command recorder checks the direct child
exit code, saves its output under scratch, and exits with that same code.

```sh
P=/Users/terbeest/dev/modelspec/.venv/bin/python
S=/tmp/model-436-scratch/final-executor
NODE=/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node
mkdir -p "$S/tmp"
cp docs/evidence/g2-ios/MODEL-439/r2/run_recorded.py "$S/run_recorded.py"

git fetch origin main
git show origin/main:registry/source-retention.json > "$S/main-policy.json"
# At the starting SHA, before merging:
env PYTHONPATH=$PWD "$P" - <<'RED'
from pathlib import Path
from decision import retention
import pytest
retention.POLICY_PATH = Path('/tmp/model-436-scratch/final-executor/main-policy.json')
retention.cite_only_hosts.cache_clear()
raise SystemExit(pytest.main([
    '-q', '-p', 'no:cacheprovider',
    'tests/test_cite_only_retention.py', 'tests/test_cite_only_verification.py',
    'tests/test_cite_only_row_warnings.py', '--tb=short',
]))
RED

git merge --no-ff --no-commit origin/main
git commit -m 'Merge origin/main into model-436-cite-only-hosts' \
  -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git "$S/modelspec-data"
git -C "$S/modelspec-data" rev-parse HEAD
```

For a later reproduction, use the recorded private SHA rather than a newer main.
The deploy exporter uses the actual UTC date. A later run measures its own
current period; pinning code and data alone does not reproduce the original
2026-10-22 snapshot identifier or date-sensitive warnings.
The public baseline archive was created without another worktree:

```sh
"$P" - <<'ARCHIVE'
from pathlib import Path
import io, subprocess, tarfile
root = Path('/tmp/model-436-scratch/final-executor/main-ae149af0')
root.mkdir()
raw = subprocess.run([
    'git', 'archive', 'ae149af075e1ea1e479cd5ab3a43ebce74f7ca08',
], check=True, capture_output=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    archive.extractall(root, filter='data')
ARCHIVE

# Export and evaluate a/c/d with the enabled production gate.
"$P" "$S/run_recorded.py" comparison env \
  -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  TMPDIR="$S/tmp" "$P" docs/evidence/g2-ios/MODEL-439/r3/compare_private.py \
  --main-root "$S/main-ae149af0" --candidate-root "$PWD" \
  --host-policy "$PWD/registry/source-retention.json" \
  --data-dir "$S/modelspec-data" --output "$S/results"

# This stricter comparison also enforces the zero-outcome-change target.
"$P" "$S/run_recorded.py" compare-candidate "$P" \
  docs/evidence/g2-ios/MODEL-439/r2/compare_private.py compare \
  --output "$S/results" --states ac

# Restore the report containing the control, after the strict target check.
"$P" "$S/run_recorded.py" compare-control "$P" \
  docs/evidence/g2-ios/MODEL-439/r3/compare_private.py \
  --compare-only --output "$S/results"

"$P" "$S/run_recorded.py" assurance env \
  -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR \
  -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY \
  TMPDIR="$S/tmp" "$P" docs/evidence/g2-ios/MODEL-439/r3/audit_exports.py \
  --results "$S/results" --output "$S/assurance"

"$P" "$S/run_recorded.py" install-pyodide \
  env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
  npm install --prefix "$S/memory-runtime" --no-save pyodide@0.28.3
"$P" "$S/run_recorded.py" memory env \
  -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  TMPDIR="$S/tmp" "$P" docs/evidence/g2-ios/MODEL-439/measure_private.py \
  --code "$PWD" --data-dir "$S/modelspec-data" --output "$S/memory" \
  --node "$NODE" --runtime "$S/memory-runtime"

# Run once for each date, with distinct trust-current/trust-successor log names.
"$P" "$S/run_recorded.py" trust-current env \
  -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR \
  -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY \
  TMPDIR="$S/tmp" PYTHONPATH=$PWD "$P" -m scripts.data_trust data \
  --data-dir "$S/modelspec-data" --date 2026-10-22 --json
"$P" "$S/run_recorded.py" trust-successor env \
  -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_DATA_DIR \
  -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_SNAPSHOT_KEY \
  TMPDIR="$S/tmp" PYTHONPATH=$PWD "$P" -m scripts.data_trust data \
  --data-dir "$S/modelspec-data" --date 2027-01-01 --json
```

Public generation and tests used `PYTHONPATH=$PWD`, no private-data or signing
variables, and `MODELSPEC_REQUIRE_DATA_DIR=0`:

```sh
unset MODELSPEC_DATA_DIR MODELSPEC_SOURCE_CACHE MODELSPEC_SNAPSHOT_KEY MODELSPEC_SNAPSHOT_ED25519_KEY
export PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=0
env PYTHONPATH=$PWD MODELSPEC_WRITE_FIXTURES=1 "$P" -m pytest -q \
  -p no:cacheprovider tests/test_decide_page_fixtures.py
"$P" -m qa.contracts
"$P" -m pipeline.agent_copy write
"$P" mcp/test/fixtures/generate-hardware-fit.py

# Baseline public generator; resolved macOS path avoids the scratch-path error.
env -u MODELSPEC_DATA_DIR -u MODELSPEC_SOURCE_CACHE \
  -u MODELSPEC_SNAPSHOT_KEY -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  MODELSPEC_REQUIRE_DATA_DIR=0 \
  PYTHONPATH=/private/tmp/model-436-scratch/final-executor/main-ae149af0 \
  "$P" /private/tmp/model-436-scratch/final-executor/main-ae149af0/pipeline/agent_copy.py write

env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE="$S/empty-source-cache" \
  "$P" -m pytest -q -p no:cacheprovider \
  tests/test_cite_only*.py tests/test_curation_cite_only.py \
  tests/test_price_reread.py tests/test_price_reread_fallback.py \
  tests/test_fetch.py tests/test_fetch_pricing.py tests/test_lab_jurisdiction.py \
  tests/test_decide_page_fixtures.py tests/test_agent_copy.py \
  tests/test_worker_bundle.py tests/test_worker_vendor_imports.py \
  tests/test_snapshot_successor_vendor.py tests/test_class_fit.py tests/test_legal.py

env -u MODELSPEC_DATA_DIR -u MODELSPEC_SOURCE_CACHE \
  -u MODELSPEC_SNAPSHOT_KEY -u MODELSPEC_SNAPSHOT_ED25519_KEY \
  MODELSPEC_REQUIRE_DATA_DIR=0 PYTHONPATH=$PWD "$P" api/worker/vendor.py --check
"$P" - <<'BUNDLE'
from api.worker.vendor import REPO_ROOT, BUNDLE, SOURCES
assert all((REPO_ROOT / source).read_bytes() == (BUNDLE / dest).read_bytes()
           for source, dest in SOURCES.items())
assert not (BUNDLE / 'bundled_data.py').exists()
print(f'{len(SOURCES)} vendored files byte-identical; bundled_data.py absent')
BUNDLE

"$P" scripts/data_freeze_guard.py \
  --base ae149af075e1ea1e479cd5ab3a43ebce74f7ca08 --head HEAD \
  --branch model-436-cite-only-hosts
env PYTHONPATH=$PWD "$P" -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
git diff --check
```

Tool versions were Python 3.14.4, pytest 9.1.1, pydantic 2.13.5, PyYAML 6.0.3,
httpx 0.28.1, cryptography 45.0.7, Node 22.22.3, Pyodide 0.28.3, Git 2.50.1 and
GitHub CLI 2.102.0.

## Limits and cleanup

No live deployment, vendor API call, paid probe, source-page fetch, external
verification of cited values, browser run or full local test suite was performed.
No claim is made that citation warnings or whole response bodies are unchanged.
The private checkout and its generated exports, overlays, logs and bundle stayed
under the ticket's scratch directory. No private data or source-page bytes were
added to the public repository.

Before deletion, `git status --porcelain` confirmed the private checkout was
unchanged. All measurement and test processes completed and their direct exit
codes were read. The following command deleted this run's scratch tree,
including the private clone, overlays, exports, logs and memory bundle:

```sh
"$P" - <<'CLEANUP'
from pathlib import Path
import shutil, subprocess
scratch = Path('/tmp/model-436-scratch/final-executor')
assert scratch.resolve() == Path('/private/tmp/model-436-scratch/final-executor')
status = subprocess.run([
    'git', '-C', str(scratch / 'modelspec-data'), 'status', '--porcelain',
], check=True, capture_output=True, text=True)
assert not status.stdout, 'private data checkout changed'
shutil.rmtree(scratch)
assert not scratch.exists()
CLEANUP
```

The final push uses `CI_LOCAL_SKIP=1` after the focused suites, as the executor
brief requires. PR #866 stays draft for the independent review. No new PR,
merge, production deployment or Linear update is part of this execution.
