# MODEL-368-cite execution evidence

Date: 2026-10-19. Code worktree: `/Users/terbeest/dev/worktrees/model-368`.
Code branch: `model-368-perplexity-faq`. Existing draft PR: #823.
Private worktree: `/Users/terbeest/dev/worktrees/data-model-368`.
Private branch: `model-368-perplexity-pro`. Existing draft data PR: #97.

- Initial code SHA: `fe37dad51139f96da45a93f22158babb708a2359`.
- Merged main SHA: `6568b0ebf939aca0aab05652e72eda2bda2dcdcc`.
- Red-test commit: `090f11bd`, before #840 integration.
- Merged #840 SHA: `58482dc3d50a9b8746662e8033fb14274e5a1788`.
- Final implementation SHA: `2a4e5a4ae28caa1b0ea81628df5222f1a3b29f73`.
- Initial private SHA: `d299550bc36e863a46c2d8f925ec61e41a0d9b7a`.
- The subsequent evidence commit contains this report and the standalone private
  export audit. The final code SHA is reported in the executor completion line
  and can be resolved with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-368-cite-fix.md`.

The spec's first merge instruction was malformed. Execution merged current
`origin/main`, then `origin/model-411-cite-only`, and confirmed a final
`git merge origin/main` was already up to date. No rebase or reset occurred.
The main conflict in `decision/verify.py` preserved both the FAQ reader and
main's xAI reader/whole-document helper. Its focused tests passed before the
second merge. PR #823 depends on #840 merging first.

## Result

Perplexity source retention uses #840's guard for the apex and `www` hosts.
`verify()` returns `cited` before reading page bytes or invoking an extractor.
The queue records the cited check without a verification or recrawl request.
A remaining raw-HTML accessor now checks the same policy before examining an
old copy. Snapshots retain cited fact values and provenance with null
verification, even if a historical verification record exists.

The parser preserves its model mapping and exact sentence matching. It keeps
only the sentence-ending length and SHA-256 fingerprint instead of the copied
sentence. The browser preparation no longer embeds that sentence. Tests build
small synthetic pages in memory and cover reordered lists, extra items, moved
question/answer nodes, renamed questions, changed sentence frames, incomplete
mappings, and unchanged canonical IDs. The external real-page fixture test is
removed. The design document's quoted FAQ passage is removed.

The private cleanup preserves all 24 fact values and states. Six Perplexity
source references retain their original hashes and registered URLs. One
reference gains its exact original fetch timestamp from existing tracked
provenance. Five references with no recorded exact timestamp stay undated.
The later FAQ/terms captures retain their recorded retrieval day and hashes;
no missing time is invented. `.engine-pin` is unchanged. The orchestrator must
pin a merged engine containing both #840 and #823 after they merge.

## Red-first evidence

Local logs are under `tmp/model-368-cite/root/`. Python commands below ran from
the code worktree with `PYTHONPATH=$PWD` and the shared interpreter.

| Defect / tests | Red result | Green result |
| --- | --- | --- |
| `test_perplexity_recheck_persists_only_citation_metadata`, both hosts | Retained page path existed | No page copy; URL/hash/fetch time retained |
| `test_perplexity_verify_is_cited_without_page_bytes`, both hosts | `unreachable` instead of `cited` | `cited`, no verification, original value |
| `test_perplexity_historical_html_is_not_replayed`, both hosts | Raw synthetic page returned | `None` before replay |
| `test_perplexity_queue_records_cited_without_verification_or_recrawl` | Cited count 0; unreachable count 1 | Cited count 1, no verification or pending/recrawl item |
| Synthetic sentence frame: incomplete-mapping and canonical-ID parser tests | Three `template drifted` failures with the former literal suffix | Same parsing works with synthetic suffix fingerprint |

Before integrating #840, the new citation suite exited 1 with **7 failed** at
`595c00d2`. After integrating it, the same suite exited 1 with **2 failed,
5 passed**; only the historical raw-HTML cases remained. After the accessor
fix it exited 0 with **7 passed**. Logs: `cite-red.log`,
`cite-after-merge.log`, `cite-green.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_cite_only.py --tb=short
```

The invented sentence fixture exposed **3 failed, 10 passed** before the
fingerprint change. The combined citation/parser run then passed **24 tests**.
A further changed-sentence regression passed in the final focused run. Logs:
`synthetic-frame-red.log`, `synthetic-frame-green.log`, `focused-final.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_perplexity_faq.py --tb=short
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_perplexity_faq.py tests/test_model_368_cite_only.py --tb=short
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_cite_only.py tests/test_model_368_perplexity_faq.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_cite_only_redirects.py tests/test_decision_verify.py tests/test_rendered_sources.py tests/test_model_396_readers.py tests/test_subscription_availability_reader.py
```

The final focused command exited 0: **558 passed in 3.52s**. Additional tests
cover the rendered FAQ preparation/persistence path and snapshot admission
with old verification. Their first extension run had four fixture errors:
the rendered mock expected `source_ids` instead of `prepare`, and the snapshot
check used candidate lookup instead of `subscription_offerings()`. These were
corrected without a production change and are not behavioral red evidence.

Private cleanup checks recorded **3 failed, 1 passed** before the edits and
**4 passed** after. The committed private evidence test and exact command are
in data PR #97's evidence file. Its failures concern copied prose, missing
recorded retrieval metadata, and absent citation disclosure; the unchanged
value/provenance check already passed.

## Validation

The required private vendor build exited 0. Its premier report was
`known 26, explicit null 18, gap 0`; the bundle contains 128 files and imports
with only declared dependencies. The artifact audit exited **1**, preserving
the unmet requirement rather than accepting a missing fact. Its output was:

```text
PASS: 24 fact values/states unchanged; 5 cited exports; no verification claims
PASS: original URLs/hashes/fetch metadata preserved; engine pin unchanged
FAIL: curated facts absent from snapshot: perplexity/subscription/pro#offering.subscription.models_covered
```

The existing value-hash-bound verification log has a 2026-10-14 `mismatch` for
that fact, following the older 2026-09-29 verification. The #840 design and
`decision/snapshot.py` admission rule deliberately quarantine mismatches even
for cite-only facts. Neither the append-only log nor the admission rule was
changed. This blocks the spec's requirement that all curated facts be present
and cited. A resolution must respect that quarantine policy and the instruction
not to change fact values.

```sh
env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_SNAPSHOT_KEY=model-368-cite-test-signing-key-only /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /Users/terbeest/dev/worktrees/data-model-368 --out tmp/model-368-cite/private-worker --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-368-cite/verify_private.py --data-dir /Users/terbeest/dev/worktrees/data-model-368 --bundle tmp/model-368-cite/private-worker
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-368-cite/check_reader_fingerprint.py
```

The fingerprint check exited 0 and confirms the exact original suffix length
and hash, and the absence of that quoted sentence from the current reader,
design and fixtures. It reads the old source in memory without printing it.
The audit's first attempts had script errors for optional `sources` and a
missing exported facet. The final script handles those cases explicitly and
reports the actual missing-fact failure above.

Remaining required gate results are recorded below after completion.

## Observation limits

No live Perplexity or other provider request, paid scrape, API spend, deployment,
production switch, Linear write, queue replay, merge to main, or force-push was
performed. Parser verification used synthetic HTML, not a fresh live capture.
The original source captures outside these worktrees were not opened or deleted.
Historical retained files already on data main are outside this PR cleanup.
Git history was preserved as required by the merge-only instruction.

An additional private `.github/scripts/tests` run against the new engine failed
because older private writers/tests still call `CopyStore.put()` without
`source_url`. It recorded **18 failed, 200 passed, 17 skipped, 8 errors**.
These callers require a separate migration before adopting #840's engine pin;
this task leaves that pin unchanged. The failure is distinct from the required
private export and premier-completeness checks. Details are in data PR #97's
execution evidence.

The data branch predates newer data-main work. Its two-dot diff includes
unrelated main-only MODEL-367 files and the newer main pin. The PR diff against
the merge base contains this ticket's citation cleanup, not those removals.
