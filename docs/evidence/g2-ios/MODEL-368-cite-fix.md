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
- Final private SHA: `6fb6bea4c5de82843493f7cb461a96ec19297d14`.
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

Execution status: **BLOCKED**. The code checks pass, including the required full
suite. The private export admits five cited facts but quarantines the Pro model
list because of its existing mismatch. The all-facts-present requirement fails.

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
not to change fact values. An independent read-only check found no supported
retraction/supersession outcome that could retire this mismatch under those
constraints. The current Verification schema rejects `cited`, `retracted`, and
`superseded`; cited queue checks intentionally do not append verification rows.
The unchanged value hash is
`sha256:d8f1c80fb0bbf3ce12db7154fe18f281f96c8325d28609aad7272f5e21d1a685`.
The winning historical row is private `verification/log.jsonl:21269`;
its older verified row is at line 16114.

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

| Check | Exit | Observed result |
| --- | ---: | --- |
| Final focused Python suite | 0 | 558 passed in 3.52s |
| Agent-copy generator check | 0 | Generated bundle current |
| OpenAPI generator check | 0 | Schema matches implementation |
| QA contract generation and in-memory comparison | 0 | Checked-in fixture unchanged and matches capture |
| Site build | 0 | Build completed; `site-build.log` |
| Surface lint | 0 | 0 findings; 5,366 files checked |
| Web install / build / test | 0 | 902 tests passed; 57 files passed, one skipped |
| MCP install / typecheck / test | 0 | 235 tests passed across 12 files |
| Evidence/release-chart guard | 0 | Nothing to check |
| Data freeze | 0 | Data freeze: ok |
| Private Worker export and import check | 0 | 128 vendored files; premier gap 0 |
| Private authored-data cleanup checks | 0 | 4 passed |
| Private exported-fact audit | 1 | Five cited facts present; Pro models covered quarantined |
| Additional private script suite | 1 | 18 failed, 200 passed, 17 skipped, 8 errors; old CopyStore call signatures |
| Full pytest under the shared lock | 0 | 12,340 passed, 9 skipped, 11 warnings in 1,805.50s (30:05) |

The full run waited for the shared lock, completed in this executor session,
and returned exit 0 directly. Its log is `tmp/model-368-cite/root/full-pytest.log`.
No test process from this run remains active.

Tool versions: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
git 2.50.1, gh 2.102.0. Checked with the corresponding `--version` commands.
Node commands used `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` first on
PATH. Process exit codes were read directly, never from a log-display pipe.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
git diff --exit-code -- api/worker/openapi.yaml cli/modelspec/agent-bundle.json qa/fixtures/mcp-tools.json
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base origin/main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-368-perplexity-faq
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Web commands, working directory `web`, each with the pinned Node PATH:

```sh
npm ci
npm run build
npm test
```

MCP commands, working directory `mcp`, each with the pinned Node PATH:

```sh
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run typecheck
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test
```

Private cleanup check, working directory `data-model-368`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --assert=plain --tb=short -p no:cacheprovider docs/evidence/g2-ios/MODEL-368-cite/test_cite_cleanup.py
```

The exact requested `git -C /Users/terbeest/dev/worktrees/data-model-368 diff
origin/main --stat` was inspected. It contains no retained Perplexity page-copy
files. The merge-base PR diff contains three files: the subscription YAML,
the data evidence document, and its offline cleanup test.

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

## PR state and description restriction

Both branches were pushed with `CI_LOCAL_SKIP=1 git push -u origin <branch>`.
GitHub confirmed PR #823 and data PR #97 remain drafts at `43082b20` and
`6fb6bea`, respectively, before this final evidence-only code commit. The final
code SHA is the report's last commit, resolved by the command above and recorded
in the executor completion line. No ready transition or merge was attempted.

The spec requires PR description edits, but `CODEX-EXEC.md` explicitly forbids
`gh pr edit` and `gh api`. An asynchronous question requested a narrow exception
for these two description bodies. No answer arrived during execution, so
the prepared [code description](MODEL-368-cite/code-pr-body.md) and
[data description](MODEL-368-cite/data-pr-body.md) remain for the orchestrator.
They name the #840 dependency, the deferred data pin, and the actual export
blocker. No alternative API was used to bypass the command restriction.

## Round 3: models_covered

Date: 2026-10-19. Executor: Claude Opus 5.5 (fallback lane). Goal: file a new
cite-only `perplexity/subscription/pro#offering.subscription.models_covered`
value from the expanded Pro FAQ, so that it leaves quarantine as a new value.

Result: **BLOCKED**. The correctly curated value is the same set as the filed
value, so its value hash is the same and the 2026-10-14 `mismatch` still
quarantines it. Nothing was filed in the data worktree.

### Transient read

| Step | Result |
| --- | --- |
| Plain HTTP GET `https://www.perplexity.ai/pro`, 2026-10-19T17:50:00Z | 200, 15,592 bytes, SHA-256 `1eab55e7e9c839c42422146a7f0a7604906279b1e30785823980f4e1819bc62d`. Application shell only; no `#faq` element in the server HTML |
| Rendered read, local headless Chromium (Playwright 1.63.0 from `web/node_modules`), same user agent and viewport as `RenderedFetcher`, models question expanded as `prepare_pro_faq` does | 200, final URL unchanged |
| Fetch time of the rendered read | `2026-10-19T17:51:11.546Z` |
| SHA-256 of the rendered HTML (`page.content()`, UTF-8, 461,908 bytes) | `sha256:8b56772b959dae9c2e610fb59e342ee5871f74e2b269451e2682928e2ca9faac` |
| `decision/perplexity_faq.py` structure walk on those bytes | Structural hash `sha256:5bbb70cd…f2a0e2` equals the reviewed `FAQ_STRUCTURAL_HASH`; 47 tokens; one five-item list; order equals the reviewed `LIVE_ITEMS` |
| Firecrawl | Not used; 0 credits |

The page bytes existed only under `/tmp/m368/` and were deleted after the
parse. No page text, quote or HTML was written to either repository.

### Mapping

Model names only; the answer sentence is not reproduced. Catalogue: `models/`
in the data worktree at `6fb6bea4`.

| FAQ model name | Canonical ID | Reason |
| --- | --- | --- |
| GPT-5.6 Terra | `openai/gpt-5-6-terra` | Card `display_name` is exactly this name |
| Claude Sonnet 5 | `anthropic/claude-sonnet-5` | Card `display_name` is exactly this name; `claude-sonnet-5-5` is a different model |
| Gemini 3.1 Pro Thinking | unmapped | No card. `google/gemini-3-1-pro-preview` and `…-preview-customtools` are different, Preview-labelled models |
| Grok 4.1 | unmapped | No card. `xai/grok-4-1-fast` and `xai/grok-4-1-fast-non-reasoning` are the Fast variants |
| Sonar 2 | unmapped | No card. `models/perplexity/` holds only `sonar`, `sonar-pro`, `sonar-reasoning-pro` and `sonar-deep-research` |

Mapped 2, unmapped 3. This matches the reviewed `MAPPING` in the reader.

### Why this blocks

The curated value is `["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"]`,
the same as the filed value.
`value_hash` = `sha256:d8f1c80fb0bbf3ce12db7154fe18f281f96c8325d28609aad7272f5e21d1a685`,
unchanged. The latest log row for that hash is the 2026-10-14 `mismatch`
(private `verification/log.jsonl:21269`). That row compared the value with the
`#pricing` region of `model-235-data-perplexity-html` and found no models
there. The FAQ read today confirms the value. But
`decision/snapshot.py` `_admit` quarantines a cited fact on its latest
`mismatch`, keyed only on the value hash. The append-only log and the admission
rule were not changed.

Not done: `value_hash` is order-sensitive for set facets. The same two IDs in
FAQ order hash to `sha256:810a5ed5dbcd7201d1bdfcbdd20e95357875cf80e3782eb076336e2bcf8b7ac5`.
Refiling the same set in another order would leave quarantine without new
information. That would weaken the quarantine rule, so it was not done. The
order sensitivity is a separate gap: a set-valued fact can leave a
mismatch quarantine by reordering alone.

The source reference was also left unchanged. It still cites
`model-235-data-perplexity-html#pricing`. Moving it to the FAQ (`#faq`, the hash
and fetch time above) does not change the value hash, so the fact would stay
quarantined. It would also break the round-2 checks that pin the original
provenance (`test_cite_cleanup.py`, `verify_private.py`). The URL, fetch time
and hash above are available for that re-file once the block is resolved.

Ways out, each needing a decision outside this executor:

1. The value changes legitimately. Perplexity changes the FAQ list, or the
   catalogue gains cards for Gemini 3.1 Pro Thinking, Grok 4.1 or Sonar 2, so
   that more names map. The set then grows and its hash differs.
2. A supported way to retire a mismatch recorded against a source region that
   the fact no longer cites. This changes verification-log semantics.
3. Leave the fact quarantined. The five other Perplexity facts stay cited.

### Commands and exit codes

| Command | Exit | Result |
| --- | ---: | --- |
| `vendor.py --data-dir …/data-model-368 --out /tmp/m368/private-worker --check`, `MODELSPEC_SNAPSHOT_KEY=model-368-test-key-only` | 0 | 128 files; premier known 26, explicit null 18, gap 0 |
| `verify_private.py --data-dir … --bundle /tmp/m368/private-worker --key model-368-test-key-only` | 1 | 24 values unchanged; 5 cited exports; `models_covered` absent from snapshot |
| Focused tests (`test_model_368_cite_only`, `test_model_368_perplexity_faq`, `test_cite_only_retention`, `test_cite_only_verification`, `test_cite_only_redirects`, `test_rendered_sources`) | 0 | 83 passed |
| `git -C …/data-model-368 diff origin/main --stat` | 0 | No perplexity.ai page copy added. The branch's own diff against the merge base is still `perplexity.yaml`, `MODEL-368-data.md` and `test_cite_cleanup.py`. The two-dot entries under `research/model-367/` are main-only files that the older branch lacks |
| Full suite under `/tmp/modelspec-fullsuite.lock` | 0 | 12,340 passed, 9 skipped, 11 warnings in 1,595.75s (26:35) |

`verify_private.py` gained a `--key` option, default unchanged, so the audit
can read a bundle signed with any test key. It still checks for all six
facts. No other code, test, reader or data changed in round 3. The data
branch has no round-3 commit. `.engine-pin` is unchanged.

```sh
env PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_SNAPSHOT_KEY=model-368-test-key-only /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /Users/terbeest/dev/worktrees/data-model-368 --out /tmp/m368/private-worker --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-368-cite/verify_private.py --data-dir /Users/terbeest/dev/worktrees/data-model-368 --bundle /tmp/m368/private-worker --key model-368-test-key-only
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_368_cite_only.py tests/test_model_368_perplexity_faq.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_cite_only_redirects.py tests/test_rendered_sources.py
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

## Main sync after #840

#840 (MODEL-411) was squash-merged to main as `2bdc4eb3`. This branch had
merged #840's branch at `58482dc3`, so `git merge origin/main` conflicted on
ten files. In each one this branch had no change of its own relative to
main `6568b0eb` plus `58482dc3`, so main's version (#840 as merged) was
taken whole: `api/worker/openapi.yaml`, `cli/modelspec/agent-bundle.json`,
`decision/engine.py`, `decision/filter.py`, `docs/decision-contract.md`,
`docs/design/cite-only-sources.md`, `docs/evidence/g2-ios/MODEL-411-fix.md`,
`qa/fixtures/mcp-tools.json`, `tests/test_cite_only_surfaces.py` and
`tests/test_cite_only_warning_scope.py`. Each of the branch's own 12 files has
the same diff against main as before the merge. The reader, the cite-only
integration, the tests, the evidence and the `verify_private.py --key` option
are unchanged. `pipeline.agent_copy write`/`check`,
`api.worker.openapi`/`--check` and `qa.contracts` regenerated no change, and
`openapi.yaml` is 232,783 bytes, the same as main. The focused tests gave
605 passed. The full suite under the shared lock gave exit 0, with 12,410
passed and 9 skipped in 1,982.77s.

## Merge prep after #843

`check_reader_fingerprint.py` no longer reads commit `fe37dad5`, which will not
exist on main after the squash merge. It pins the original suffix length (70),
its SHA-256 and the FAQ template hash, checks them against the reader's
constants, and checks absence by hashing every 70-character window of the
reader, design doc and tests. It stores no page text. It exits 0 on this branch
and exits 1 when the old suffix-bearing reader is used as the reader or is
appended to the test file.

`git merge origin/main` (#843, `e64f9f20`) had no conflicts.
`pipeline.agent_copy write`/`check`, `api.worker.openapi`/`--check` and
`qa.contracts` all exit 0 and changed no file; `openapi.yaml` is 232,783 bytes.

Worker memory, Pyodide 0.28.3, Node v22.23.2, exit codes 0. Steady MiB / Wasm MiB:

| Check | main `e64f9f20` | this branch | Delta |
| --- | ---: | ---: | ---: |
| PR job fixture, current period | 104.571 / 59.875 | 104.571 / 59.875 | 0.000 |
| PR job fixture, successor period | 103.669 / 59.875 | 103.660 / 59.875 | -0.009 |
| Private data (`modelspec-data` `5d797a6`, test key), steady | 104.582 / 59.875 | 104.561 / 59.875 | -0.021 |

The PR job ran as `rank-api.yml` defines it, with the #843 fixture recipe and
`--limit-mib 115` against main baselines. The first main measurement downloaded
the Pyodide wheels and read 109.02 MiB; repeats with cached wheels read the
values above. The private check ran `vendor.py --data-dir` with
`MODELSPEC_REQUIRE_DATA_DIR=1`, then `measure_memory.cjs api/worker/src`; the
premier report was `known 26, explicit null 18, gap 0`. The vendored private
files and the scratch worktrees were removed afterwards.

Focused tests (the nine files above plus `test_worker_memory.py` and
`test_worker_memory_compaction.py`) gave 591 passed. Web `npm ci` and
`npm run build` exited 0.
The full suite under the shared lock (`-n 4 --dist loadfile`) exited 0:
12,432 passed, 9 skipped, 11 warnings in 1,939.67s.
