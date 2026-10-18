# MODEL-394 execution evidence

Engine base: `b51985205621aba2e231a8914b5d4f0be9d4db6d`.
Data base: `502683e2aee6c6ddb3f8e5fd4998f89007388ae9`.
Final source commit: `93854ca73f34106d60eec9c838a6d82e604030e9`.
The executor handoff records the final branch SHA after the evidence commit.

## Design and delivered behavior

[Draft engine PR 809](https://github.com/turbobeest/modelspec/pull/809) contained
its design before implementation. Design-only commit `40a2dc96` preceded code.
Dated facts were chosen over a nested schedule because each entry reuses the
existing fact ID, source references, queue, and verification log.

Each price entry is a scalar `Fact` with inclusive `effective_from` and
`effective_until` bounds. Its verification hash binds the price and both dates.
Undated facts keep their existing hashes. The schema and raw builder reject
ambiguous schedules, gaps, overlaps, mixed dated and undated facts, and dated
facts that do not belong to their actual metered offering.

The builder requires `as_of` and selects one entry per price facet. Signed
`valid_from` and exclusive `valid_until` bounds cover every kept candidate,
including the archive. Retired models can enter a current decision when its
conditions explicitly request them, so their prices must also expire.
Out-of-lineup offerings do not shorten validity. The engine and every hosted
snapshot-holder return path enforce the bounds, including cached, bundled,
304, failed-refresh, and concurrent-load paths. Historical comparison bypasses
the current-date check for its old snapshot.

Dated claims use a dedicated deterministic reader. It checks the exact model,
source URL, cited DOM table, tier, region, price kind, and dated row. Undated
readers cannot rescue a dated claim. Weekly re-read verifies future entries
and preserves their dates when it proposes an amount change.

The public response still presents one scalar value per price facet. Complete
contract 2.18, bounded 1.5, and model comparison 1.0 remain unchanged under
MODEL-59. No existing field widens or becomes optional. Ranking floors,
class ordering, legal terms, and `rank_score` are untouched. The guaranteed-facet
invariant still requires exactly one active fact at today and every explicit
schedule boundary.

## Final Gemini ownership check

The Gemini reader hashes the complete original HTML before any DOM parsing or
normalization. It decodes strict UTF-8 and masks only lexical dated-price
phrases inside the paid price cells of exact three-cell price rows. Their
labels are `Input price`, `Output price (including thinking tokens)`, and
`Context caching price`. Every byte outside those phrases remains literal,
including attributes, captions, hidden text, row markup, and surrounding page
content. The hash is SHA-256 over `gemini-price-context@1`, a NUL byte, and the
masked UTF-8 source. Numeric values and dates must still verify separately.

The production hash for the canonical Argon offering and Gemini pricing URL is
`326badec64e22fac17023b30796ba78ab8b6ea546b52aac4933f4341e2544866`.
It comes from retained primary response
`sha256:dfbd1d4d4ff9dfd7d740fd15b1269b84d4e9f04570457ce6454db0013ff05025`.
The test-only fixture hash is
`42905b0da1bb81cecf23ab46c82c435a55e9bb11ef2ccfeccd5d375f8783ada3`.
The fixture injects its hash. Production does not accept it.

Any page change outside the declared price phrases refuses verification until
a reviewed template update. This supersedes the earlier DOM template, which
lost `aside` and hidden text and could collapse duplicate attributes or miss a
caption before the owner wrapper. Exact amount changes remain supported.

## Red-first and final focused results

Every red run preceded the source correction for its reported behavior.
Paths below are relative to `.scratch/model-394/`.

| Behavior | Red result, exit 1 | Final verification, exit 0 |
| --- | --- | --- |
| Date resolution and expiry: `test_snapshot_resolves_exactly_one_price_on_its_as_of`, `test_snapshot_refuses_to_cross_the_price_boundary_while_stale`, and related cases | `snapshot-design/red.log`: 38 failed, 1 passed | Snapshot file: 44 passed, including the later archive and actual-owner regressions |
| Primary rows, missing/mismatched dates, and weekly future rows: `test_dated_argon_rows_verify_and_bind_the_dates`, `test_dated_argon_never_borrows_an_undated_or_foreign_price`, `test_vertex_exact_model_date_region_and_continuation_row`, `test_weekly_reread_checks_future_row_and_preserves_schedule_on_rewrite` | `root/readers-red.log`: 13 failed | Reader file: 36 passed |
| Cached and bundled expiry and refresh/concurrency fallbacks | `reread-design/serving-red.log`: 12 failed | Serving file: 13 passed, including historical comparison |
| YAML dates: `test_native_yaml_dates_build_the_same_snapshot_as_iso_strings` | `snapshot-design/red-native-dates.log`: `TypeError: Object of type date is not JSON serializable` | Included in the snapshot file, with caller input unchanged |
| Discarded ownership context: `test_ownership_hash_keeps_elements_the_text_normalizer_drops` | `root/raw-context-red.log`: 2 failed, 1 passed, 24 deselected | Final source hash retains the original bytes |
| Canonical Vertex identity: `test_vertex_canonical_model_cannot_borrow_another_catalogue_name` | `root/vertex-identity-red.log`: 3 failed, 33 deselected, including claims persisted and reloaded from the queue | Included in the 36 passing reader cases |
| Duplicate attributes and preceding captions: `test_duplicate_attributes_cannot_hide_foreign_ownership`, `test_ownership_caption_before_the_model_section_is_bound` | `root/raw-source-red.log`: 5 failed, 28 deselected | Included in the 36 passing reader cases and independent source probes |
| Archive expiry and forged owners: `test_an_expired_archived_price_cannot_answer_a_current_retired_model_request`, `test_dated_price_facts_must_belong_to_their_actual_snapshot_owner` | `snapshot-design/red-archive-owner.log`: 3 failed, including `DID NOT RAISE SnapshotError` from the actual engine request | `snapshot-design/green-archive-owner.log`: 44 passed in 0.46s |

Earlier ownership reds also preceded their fixes: `test_argon_rejects_conflicting_or_nested_table_ownership` failed three assertions (`root/ownership-red.log`); `test_quoted_table_text_does_not_cite_the_actual_table` failed one (`root/citation-red.log`); and `test_foreign_paragraph_caption_cannot_assign_argons_sibling_table` failed one (`root/template-red.log`). All are included in the 36 passing reader cases.

Final dated and offering-invariant run: **110 passed in 1.33s**, exit 0,
`root/dated-canonical-final.log`. This covers 44 snapshot, 36 reader, 13 serving, and 17
slice-1 cases.

Final source, verification, and weekly-reader focused run: **667 passed in
9.83s**, exit 0, `root/vertex-final-focused.log`.

Independent original-source probes: **8 passed in 1.08s**, exit 0,
`reread-design/review-raw-bytes-green.log`. They cover the actual primary
capture, three duplicate-attribute mutations, a caption before the owner,
two ownership-markup changes inside paid cells, and the positive $4-to-$5
amount-change control.

The final canonical-identity confirmation passes **4 tests, 7 deselected in
0.26s**, exit 0 (`reread-design/review-final-confirmation.log`). Correct Vertex
3.7 and the retained Gemini capture verify. A canonical Vertex 3.8 or unknown
model cannot borrow 3.7's row by supplying its name, even after queue reload.
The reader now maps each supported canonical Vertex model ID to its exact
published row name; an alias list cannot widen that binding.

Schema equality, Ruff on the new reader and test files, and `git diff --check`
all exited 0. Existing files retain unrelated pre-existing lint findings.

## Required full run

Final source run: **11353 passed, 9 skipped, 11 warnings in 1175.65s**, exit **0**.
Its log is `.scratch/model-394/root/engine-full-canonical.log`.
The foreground process completed with exit 0 on source `93854ca7`.

The first completed full run exited 1: **2 failed, 11333 passed, 24 skipped,
11 warnings in 1238.60s** (`root/engine-full-complete.log`). Both failures were
`tests/test_social_cards.py::test_build_emits_every_template_preview_and_card`
and `::test_every_frozen_template_card_has_clean_chromium_layout`: the renderer
could not import `@playwright/test`. A direct import reproduced
`ERR_MODULE_NOT_FOUND`, exit 1. Installing the locked `web/` dependencies with
Node 22.22.3 and `npm ci` fixed that import, exit 0. No source or lockfile changed.
A real Chromium launch also exits 0. The same two previously failing tests
then pass: **2 passed in 189.19s**, exit 0 (`root/social-cards-final.log`).
The next run exposed the landing fixture's separate requirement for
`web/dist/decide.html`. It was interrupted with **10120 passed, 7 skipped,
11 warnings, 12 fixture errors in 455.94s**, exit 2
(`root/engine-full-green.log`). Every fixture error was the missing built page.
`npm run build` then exited 0; it changed no tracked source. The exact full
command is repeated with dependencies installed and the web assets built.

Four source-obsolete full runs were deliberately interrupted when new corrections
made their source obsolete. All exited 2. None is a full passing result.

| Log under `.scratch/model-394/root/` | Interrupted output | Exit |
| --- | --- | --- |
| `engine-full.log` | 8497 passed, 5 skipped, 4 warnings in 256.40s | 2 |
| `engine-full-final.log` | 10082 passed, 21 skipped, 11 warnings in 552.85s | 2 |
| `engine-full-reviewed.log` | 7363 passed, 4 skipped, 4 warnings in 277.36s | 2 |
| `engine-full-final-green.log` | 7257 passed, 4 skipped, 4 warnings in 165.48s | 2 |

## Exact commands and versions

Engine working directory: `/Users/terbeest/dev/worktrees/model-394`.
Each pytest command ran directly, with output redirected to its log. The
execution session returned the actual process exit code. Log tails were read
separately; no exit code came from a pipe.

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff --version
git --version
gh --version
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
# Dependency preparation ran with web/ as its working directory:
npm ci
PYTHONPATH=/Users/terbeest/dev/worktrees/model-394 npm run build
# The remaining commands ran from the engine worktree root:

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_snapshot.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_serving.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_snapshot.py::test_an_expired_archived_price_cannot_answer_a_current_retired_model_request tests/test_dated_price_snapshot.py::test_dated_price_facts_must_belong_to_their_actual_snapshot_owner
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_snapshot.py tests/test_dated_price_serving.py tests/test_dated_price_readers.py tests/test_slice1_offerings.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_readers.py tests/test_dated_price_snapshot.py tests/test_dated_price_serving.py tests/test_decision_sources.py tests/test_decision_verify.py tests/test_price_reread.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_dated_price_readers.py -k 'duplicate_attributes or caption_before'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q .scratch/model-394/reread-design/review_raw_dom.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -x --tb=short tests/test_landing.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/dated_prices.py tests/test_dated_price_snapshot.py tests/test_dated_price_serving.py tests/test_dated_price_readers.py --output-format concise
git diff --check
```

Versions: Python 3.14.4, pydantic 2.13.5, pytest 9.1.1, pytest-xdist 3.8.0,
Ruff 0.16.6, Git 2.50.1, and GitHub CLI 2.102.0. No Node suite is part of
the implementation; the full Python suite invokes the existing Node/Chromium
social-card renderer. Final browser validation uses Node 22.22.3 and npm 10.9.8.

Log archive manifest: [MODEL-394-engine/logs.json](MODEL-394-engine/logs.json).
The manifest covers 36 compressed logs. Every decompressed log matches
its recorded SHA-256 and byte count, including the completed full run. Earlier
archived green logs do not replace the final results listed here.

## Retained-source data proof and admission limits

The private data tool `tools/research/model-394/replay.py --proof` verifies
30 dated price records against retained Google primary responses and records
six boundary observations in `research/model-394/verification.json`.

| Offering and snapshot date | Input | Output | Cache input | Snapshot expires at |
| --- | --- | --- | --- | --- |
| Argon candidate, 2026-11-30, `snap_b7c9b50f48e1072b` | 2.00 | 10.00 | 0.10 | 2026-12-01 |
| Argon candidate, 2026-12-01, `snap_d5663f6012e2cf2e` | 4.00 | 20.00 | 0.20 | 2027-01-01 |
| Vertex 3.7 and 3.8 Flash, 2026-12-31, `snap_635e25199012d2ab` | 0.75 | 3.75 | 0.075 | 2027-01-01 |
| Vertex 3.7 and 3.8 Flash, 2027-01-01, `snap_c55213daf71f8b46` | 1.50 | 7.50 | 0.15 | No later filed boundary |

Prices are USD per million tokens. Batch input and output also switch.
The December Argon proof includes the Vertex schedules, so its snapshot expires
on January 1 despite Argon's later entry having no filed end date.

Argon is an injected research candidate with the premier gate disabled. It is
not a production offering. The private findings report 20 missing guaranteed
model facts, five missing offering governance facts, and absent premier
admission. This follows the spec's explicit missing-facts alternative.

The final private broader run against source `93854ca7` passed **966 tests,
17 skipped in 155.05s**, exit 0. The preceding `a9fdcebb` run passed the same
966 tests with 17 skipped in 189.64s, exit 0.
The linked-data guard passed all 14 paths, exit 0. The run used Python 3.11 and
the exact `recall-private.yml` test list, including `.github/scripts/tests`.
The private evidence records its command and engine-code fingerprints.
The final private replay verifies all 30 records and records six observations
from four snapshot builds. Its runnable `tools/research/model-394/audit_context.py`
passes 11 actual-source controls, and repeated successful writes leave the
production queue and log unchanged. The data PR evidence retains those receipts.

The data draft pins the final engine evidence commit. The hosted gate requires
that commit to be on engine `main`, so the data draft remains dependent on
engine review and merge. No ancestry check is weakened for the unmerged pin.

## What was not observed

No real December 1 or January 1 production request was observed. Boundary
behavior comes from `as_of` builds, injected UTC dates, and local engine calls.
There was no production deployment, configuration switch, new retained source
fetch, Firecrawl credit use, vendor API spend, device use, or Linear write.
Read-only browsing of Argon model and governance documentation did not file
or verify admission facts. No merge action was taken. Cross-model review is
pending.
