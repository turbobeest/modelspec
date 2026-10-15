> Current status, round three: PDF support and the table-scope reader were
> withdrawn after REV-760 and REV-760b. Earlier PDF and sixteen-fact results
> below describe rejected prototypes. The retained change is the Mistral label
> rule; current filing has fifteen facts and four gaps. See round three below.

# MODEL-396 execution evidence

The two reader gaps are closed. A genuine retained-source replay verifies
sixteen of nineteen guaranteed Small 4 facts. Per-model streaming, express base
lineage and the complete first-party weights-hosting country set still lack
qualifying primary statements. Small 4 remains outside premier and no La
Plateforme offering was filed.

## Revisions and design order

- Engine worktree: `/Users/terbeest/dev/worktrees/model-396`, branch
  `model-396-readers`, base `c9b625605750f29ede73ade4d7020eb2714b1513`.
- Engine final code SHA: `8b9bff5b9124e04b349414d984845a5c79a1a3a0`.
  The delivery commit adds only this evidence and logs. Resolve its final SHA
  with `git rev-parse model-396-readers`; that SHA is also in the executor's
  final output and the draft PR head.
- Data worktree: `/Users/terbeest/dev/worktrees/data-model-396`, branch
  `model-396-mistral-small`, base `cf93edc381b4699fb251c1f06f206237b77ea727`.
  Final data SHA: `df86c419ed26701a9d73e16452e56c8f18dd44c5`, delivered in
  draft [data PR 90](https://github.com/turbobeest/modelspec-data/pull/90).
- The engine design note was committed as `2fba54ba` and posted as the body of
  draft [engine PR 760](https://github.com/turbobeest/modelspec/pull/760) before
  any reader or test code. The [current design](../../design/MODEL-396-readers.md)
  records the exact normalization, supported source forms, conservative raster
  limits and adversarial cases.

Packaging support was completed in `8b9bff5b`. The first PDF implementation was committed as `66227354`, then the scoped
readers as `84ec2e7d`. Independent raster-container probes exposed additional
scan paths. Their red-first fixes are in the final code commit above. Two
preliminary full-suite starts were deliberately interrupted with exit 130 to
test the final artifact after those changes. They are not successful gates.

## Red before green

All initial tests ran before production reader changes. Original red output
and final green output are retained in the compressed logs alongside this file.

| Defect | Red-first behavior tests | Observed red | Observed green |
|---|---|---|---|
| No opt-in PDF normalization, source recheck or retained verification path | `test_pdf_normalization_has_literal_reproducible_text`, `test_pdf_recheck_and_verifier_use_original_hashed_bytes`, `test_pdf_recheck_detects_changed_text` | Unknown `pdf-pypdf-6.19.0-v1` recipe, `KeyError` or source validation error. Initial module: 19 failed, 3 passed, exit 1. | Original bytes, exact text and changed/unchanged regions pass. Final PDF module: 27 passed, exit 0. |
| Mistral's documented reasoning label prevented exact text output verification | `test_mistral_reasoning_output_label_verifies_exact_text_set`, `test_mistral_rule_keeps_real_output_labels`, `test_mistral_rule_refuses_conflicting_output_blocks_even_with_claim_label` | Initial reader module: 10 failed, 36 passed, exit 1. Valid labels mismatched; a conflicting block was incorrectly accepted by a generic fallback. | Reader module: 47 passed, exit 0. Only exact reasoning is removed in the scoped primary output forms. Unknown and real extra labels remain. |
| The four-column PDF table did not yield a text output maximum | `test_model_properties_reads_output_maximum_not_input_maximum` | Expected 256000 was not verified. Included in the initial reader module's 10 failures. | Output cell verifies 256000; differing 128000 input limit fails the output claim. |
| A raster scan in a pattern escaped the ordinary image walk | `test_scan_painted_through_pattern_cannot_supply_text_overlay` | `DID NOT RAISE UnsupportedContentError`, 1 failed, exit 1. | Pattern resources are unsupported. |
| A raster scan in annotation appearances or graphics-state masks escaped the ordinary image walk | `test_scan_in_unsupported_rendering_container_fails_closed` | Both cases: `DID NOT RAISE UnsupportedContentError`, 2 failed, exit 1. | Both containers are unsupported. Plain primary-document link annotations still work. |
| A full-page raster inside a Type 3 glyph escaped the ordinary image walk | `test_type3_font_cannot_paint_scan_behind_extractable_text` | `DID NOT RAISE UnsupportedContentError`, 1 failed, 1 passed, exit 1. | Glyph image dimensions include font, text and page transforms. The oversized glyph fails; `test_small_type3_bitmap_glyph_is_supported` passes. |
| The dependency pin invalidated the generated CLI source hash; the PDF helper was missing from the Worker bundle | `test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources`, `test_wheel_contains_only_the_thin_client_and_its_guidance`, `test_every_imported_repository_module_is_vendored` | Focused packaging replay: 3 failed, exit 1. | Regenerated one existing CLI hash and added one Worker source entry. Expanded packaging suites: 24 passed, exit 0. |

The final new reader modules together passed 74 tests. The regression command
covering existing verifier, licence, source and MODEL-235 readers passed 829
tests. The first source/model/PDF regression command passed 177 tests. After
the rendering-container changes, source/model/new-reader coverage passed 227
tests; the two final Type 3 tests also passed in the final new-module run.

## Commands and versions

Commands below ran from the engine worktree unless a different directory is
stated. Exit codes were read from the process, without a pipeline.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_sources.py tests/test_decision_model.py tests/test_model_396_pdf.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_verify.py tests/test_model_235_readers.py tests/test_model_390_licence_readers.py tests/test_decision_sources.py tests/test_model_396_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py::test_scan_painted_through_pattern_cannot_supply_text_overlay
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py::test_scan_in_unsupported_rendering_container_fails_closed
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py::test_type3_font_cannot_paint_scan_behind_extractable_text tests/test_model_396_pdf.py::test_small_type3_bitmap_glyph_is_supported
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py tests/test_model_396_readers.py tests/test_decision_sources.py tests/test_decision_model.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_396_pdf.py tests/test_model_396_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/pdf_text.py tests/test_model_396_pdf.py tests/test_model_396_readers.py
git diff --check
```

Final full engine suite: **11249 passed, 9 skipped, 11 existing warnings in 1162.35 seconds**, exit 0. The locked web dependencies made fifteen previously skipped tests runnable.
The additional static site build, `PYTHONPATH=$PWD
/Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist`,
exited 0 against reader commit `858f1fe0` and frozen public data. Subsequent changes only repair packaging. Its manifest keeps
`export_schema_version` at `3.0`; output stayed in ignored `dist/`.
New-file Ruff and `git diff --check` passed. A broader exploratory Ruff check
also reported existing violations elsewhere in `normalise.py` and `verify.py`;
those unrelated lines were not changed to suppress that result.

Engine tools: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, pypdf 6.19.0,
Pydantic 2.13.5, PyYAML 6.0.3, HTTPX 0.28.1, Ruff 0.16.6, Git 2.50.1,
GitHub CLI 2.102.0. The recipe and development dependency pin pypdf 6.19.0
exactly and an installed-version mismatch fails closed.

The first completed full run exited 1 with **5 failed, 11229 passed, 24 skipped
in 1210.34 seconds**. Three failures were the packaging omissions above. Two
social-card failures reported `ERR_MODULE_NOT_FOUND` for `@playwright/test`.
The rendering script and locked web dependencies are byte-identical to the
assigned base. `npm ci` installed those locked packages; it changed no tracked
web files. The initial run inherited Node 22.23.1 from the shell. Subsequent
Node commands and the final full Python run explicitly use the brief's Node
22.22.3, with npm 10.9.8 and Playwright 1.63.0. The final full run is the gate,
with those local setup omissions repaired. Its exact invocation was:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py::test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources tests/test_cli_wheel.py::test_wheel_contains_only_the_thin_client_and_its_guidance tests/test_worker_vendor_imports.py::test_every_imported_repository_module_is_vendored
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_cli_wheel.py tests/test_worker_vendor_imports.py tests/test_worker_bundle.py
```

From `web/`, with `PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH`
and `PYTHONPATH=/Users/terbeest/dev/worktrees/model-396`:

```sh
npm ci
npm run build
npm test
```

All exited 0. Web tests: **52 files passed, one skipped; 843 tests passed**.
The Worker bundle change retains lazy pypdf loading. Importing `decision.pdf_text`
and normalizing plain text leaves pypdf unloaded. Worker lockfiles and production
variables are unchanged. The generated CLI diff is a single provenance hash;
no prose, schema or public field range changed.

The new modules also passed **74 tests under Python 3.11.15**, exit 0, after
installing that same extractor in the isolated private validation environment.
These commands ran from the data worktree and write only its ignored scratch:

```sh
research/model-396/validation/venv/bin/python -m pip install pypdf==6.19.0
PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 research/model-396/validation/venv/bin/python -m pytest -q /Users/terbeest/dev/worktrees/model-396/tests/test_model_396_pdf.py /Users/terbeest/dev/worktrees/model-396/tests/test_model_396_readers.py
```

The source collector used Python `urllib.request` with public GET requests and
a thirty-second timeout. Poppler 26.09.0 rendered PDF page 2 for visual review;
the Poppler text derivative was never used as a verifier source. Fetch commands,
URLs, byte hashes and failed HTTP probes are in the private research bundle.

## Private-data results and reproduction

From the data worktree:

```sh
PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 /Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/replay.py
/Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/sources/primary-research/check-sources.py
```

Both exited 0. Replay preserves the fourteen previous fact records and adds
two research candidates with real independent verifications:

- `model.output_modalities = [text]`, method `mistral-output-labels@1`.
- `model.max_output_tokens = 256000`, method `model-properties-output-limit@1`.

The original PDF source hash is
`sha256:9a40824543b1f0eedd0dd9db66f01e8f86f7284ec86e3063de40fa407dc6cc32`.
`StoredRegions` normalizes those original bytes, not a fabricated text copy.
The source checker validates twenty-nine retained observations and records four
failed HTTP probes. Unsupported facts are research `not_attempted` results,
excluded from both candidate facts and verification records.

The broader data suite ran in an isolated composition of private data and its
unchanged main engine pin, `d29d1c6cf7c3671e51f9191f3f2594afe4afbb6b`.
The pin matches `git show origin/main:.engine-pin`. No production data changed.
Python 3.11.15 was used, matching the workflow's minor version; pip 24.0
installed the pinned engine with `python -m pip install -e '.[dev]'`.
From `research/model-396/validation/data` the exact workflow test command was:

```sh
MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR=$PWD PYTHONPATH=$PWD ../venv/bin/python -m pytest -q .github/scripts/tests tests/test_decision_sources.py tests/test_decision_verify.py tests/test_decision_model.py tests/test_decision_snapshot.py tests/test_subscription_availability.py tests/test_subscription_availability_reader.py tests/test_slice1_offerings.py
```

The final run exited 0: **938 passed, 17 skipped in 151.19 seconds**. The
private recall run and baseline comparison each exited 0: sixteen pass, four
existing partials, zero fail, no regressions. Exact setup commands, exit codes,
versions and logs are in the private `research/model-396/validation` bundle.

Independent PDF probes in that bundle rejected nested Form, pattern,
annotation appearance, graphics-state mask and Type 3 glyph scans. The tested
`decision/pdf_text.py` hash is
`510ce69eb7d466ee99d2d2908b30789c4b87055114f2c734b93af109992d151f`, identical
to the final committed reader. This check exited 0.

The local private-data premier decision for
`origin.lab_jurisdiction in {FR}` used `optimize.max=model.context_window` and
`access.kind=own_software`. Before and after, its full JSON bytes were identical,
SHA-256 `fd99c2c5158ee476e1f4933927b59287e76b0bf74565226cde617aae96b8423c`.
Both used `snap_1318fd523c982c07`, returned `no_feasible`, had no API routes,
and excluded Small 4 from premier and results.

## Remaining source gaps and contract check

| Gap | Observed limitation | What would close it |
|---|---|---|
| `feature.streaming` | Model pages omit it. The generic chat API parameter is not a per-model guarantee; observed streaming examples use other models. | A first-party Small 4 streaming statement or explicitly model-bound capability/example. |
| `origin.base_lineage` | `Model dependencies NA` and a base lifecycle label do not state random initialization or enumerate ancestors. | An express first-party random-initialization statement, or a complete ancestor chain with the required jurisdiction evidence. |
| `origin.weights_hosting` | EU/EFTA/US inference scopes and customer-data location do not enumerate this model's first-party weight-storage and serving countries. | An explicit complete country set for Small 4's first-party stored and served weights. |

The data `.engine-pin` stays at main's value. Adoption of these readers in
production data needs a pin bump to the merged engine commit after review and
merge. Research candidates do not currently require the pinned production
engine to understand the new PDF recipe.

The actual MODEL-59 rules in `docs/decision-contract.md` and
`docs/cli-contract.md` were read. No public response field range, enum, nullability,
optional presence, unit or envelope changes. The output-modality vocabulary
and generic exact-set comparison remain unchanged. Source normalizer names
are internal open text fields. No public contract version bump is required.
Frozen cards, facts, offerings and premier files in the public engine are
unchanged.

## Observation limits

No live production decision or model response was observed. The before/after
decision is a local snapshot execution. The source audit establishes what the
inspected documents say; it does not prove absence from every possible private
agreement or future publication. Raster checks conservatively reject some
legitimate PDFs; they do not determine the historical origin of visible text.

No vendor API spend, Firecrawl credits, machine or device calls, workflow
dispatch, production switch, legal text change, Linear write or merge occurred.
No WSL gate, SSH, SCP or forbidden download command ran. No Node or Swift
files changed. All spawned validation, fetch, build and test processes completed before delivery. Hosted CI and the orchestrator's
gate are not claimed as observed here.

## REV-760 round two (MODEL-396-r2)

Review base: engine `a8cfd787f6d315d8ad9a0e328a87b14effb6e49f`, data
`df86c419ed26701a9d73e16452e56c8f18dd44c5`. Read the full REV-760 verdict.
Updated the design note and draft PR #760 body before implementation.

The extractor owns limits of 25 MiB original input, 300 pages, 4 MiB per
decoded stream, 25 MiB aggregate decoded streams, 5 MiB total UTF-8 extracted
text (including page separators), and 50 million Python line events in pypdf
and the extractor. The last budget bounds parser, decoding and layout loops
without a clock-dependent verdict. The actual Mistral document uses about
14 million pypdf events; its largest decoded stream is 181,044 bytes.
Configuration is explicit, context-local and restored. A private BaseException
signal prevents parser recovery from swallowing the operation limit.

The active-content preflight rejects JavaScript/JS, Launch, embedded files,
file attachments and RichMedia names, including escaped names and names in
decoded object streams. OpenAction/AA chains support internal navigation only.
The retained PDF has duplicate named-destination keys: a failed strict Dests
parse may bypass resolution only for a bounded, uncompressed dictionary of
named internal destination arrays. Streams and action dictionaries cannot use
that exception. An independently discovered compressed-Dests bypass was
reproduced red, then closed and checked independently.

Output limits come from exactly one table owned by the subject's own heading
or title. Two separately headed subjects may each own a table. Another
subject's table before or after the title cannot establish the claim. Multiple
own tables, foreign model names, headingless tables and ambiguous normalized
heading text refuse. The four-column matrix permits explicit modality labels
and token quantities; unrelated text does not extend its scope.

PDF extraction is supplied by the offline `decision.source_document` adapter.
The shared normalizer takes an explicit PDF extractor; the Worker has none.
The actual generated Worker bundle contains neither pdf_text.py nor any pypdf
import path, and an isolated bundle rejects the PDF recipe without importing
an offline reader. Existing verifier document-cache tests remain unchanged.

Red-first observations (each command exited 1):

- `tests/test_model_396_pdf.py`: 17 failed, 27 passed against unchanged code.
  The failures cover input/page/stream/text/work limits and eleven distinct
  active-content fixtures. Bomb and 301-page fixtures are generated in memory.
- Reader probes: 10 failed, 49 passed; a normalized HTML foreign-heading probe
  failed separately. Additional subject-ownership probes failed 3 cases, then
  the foreign-column and bare-posttable probes failed 5 cases before their fixes.
- Actual Worker bundle exclusion test failed, reporting bundled pdf_text.py,
  the normalizer's import of it, and its pypdf imports.
- `test_pdf_destination_metadata_cannot_hide_compressed_active_names` failed
  before narrowing the destination exception.

Final focused command:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q \
  tests/test_model_396_pdf.py tests/test_model_396_readers.py \
  tests/test_worker_vendor_imports.py tests/test_worker_bundle.py \
  tests/test_decision_regions.py tests/test_decision_sources.py \
  tests/test_decision_verify.py
```

Result: **628 passed in 2.54 s**, exit **0**. The PDF module has 51 passing
tests; the reader module has 70. Independent broader reader/source regression:
853 passed, exit 0. Changed PDF/adapter/reader test lint and diff whitespace
checks pass. Tools: Python 3.14.4, pypdf 6.19.0, Node 22.22.3.

The first focused invocation used a nonexistent normalizer test filename and
exited 4 before collecting anything; corrected to test_decision_regions.py.
A restoration test initially compared an apply_configuration copy by identity
with its input; corrected it to compare the active context returned by the
public API. No existing test was weakened.

Full engine suite and fresh data replay results will be recorded below once
the implementation commit is clean. No Worker deployment, production switch,
contract change, data pin bump, lineup admission or offering was performed.

### Final subject-ownership hardening

An independent probe found unknown model names accepted as architecture or
parameter-range metadata values. Six cases failed red, then explicit supported
architecture descriptions and anchored numerical parameter ranges closed them.
Two further red cases showed an unknown numbered model heading could be
followed by Model properties and regain ownership. Only General information
and Model properties are now permitted numbered sections before the table.

The first full run was intentionally interrupted (exit 130) after 8566 passed,
5 skipped, 4 warnings in 237.15 s because these additional source changes
required a fresh run. That partial run is not a completed validation gate.

The final combined focused command above now passes **637 tests**, exit **0**;
the reader module has **79** passing tests and the PDF module **51**. The actual
original Mistral PDF still verifies 256000 through the stricter reader.

### Completed round-two gates

Final implementation SHA: `75aa2df3b0d94975637c11771c2fa2c0e3da2e61`.
This evidence commit adds only the completed gate record and compressed log.
The source implementation remained clean throughout the final full run.

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Result: **11307 passed, 9 skipped, 11 warnings in 1543.18 s (25:43)**,
exit **0**, checked directly from the process. Warnings are the existing
unsigned decision-vocabulary warnings in CLI snapshot/keyed-origin tests.
There are no failed or errored tests. Full stdout/stderr is retained in
MODEL-396-r2-full-engine.log.gz.

The private-data worktree replay against this clean implementation passed
with Python 3.11.15 and 3.14.4: the same **16** facts verify, every field of
the **14** baseline fact dictionaries remains identical, and the same three
unfiled gaps remain unknown. Python 3.11's focused PDF/reader suite passed
**130 tests in 1.18 s**, exit **0**. Source-byte integrity and the five
independent scan probes also pass. The canonical replay is refreshed once
more against the evidence head before the data commit, and its exact head,
clean status, runtime and exit codes live in data PR #90's
research/model-396/candidate-results.json and validation/r2-replay-results.json.

Data replay command (cwd /Users/terbeest/dev/worktrees/data-model-396):

```bash
PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 /Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/replay.py
```

The data .engine-pin stays `d29d1c6cf7c3671e51f9191f3f2594afe4afbb6b`.
Contract version remains 2.18; decision/contract.py, the decision JSON schema,
Worker OpenAPI, ranking floors, legal terms, production variables, premier
and frozen public data are unchanged. Source and verification records remain
research-only. No Worker isolate deployment or paid provider request was
observed or performed. Both PRs remain drafts; no merge was performed.

## Round three: withdraw PDF support

Base engine `b10f80d66b31220f499b4e7f1c91c3314aa367ab`; base data
`f59692b443ee223a8bf61d6975387d4c31d4bcc1`. Read REV-760b fully. The
orchestrator explicitly withdrew PDF support instead of extending its action
blocklist or table-heading heuristic.

Removed the PDF recipe, extractor, offline adapter, dependency, PDF locator
change, model-properties reader and their tests. The shared normalizer, source
fetcher/model, CLI provenance and Worker import tests match pre-ticket commit
`c9b62560` byte for byte. Worker vendor code and locks also match that baseline;
there were no remaining lock changes to revert. PDF-specific Worker guards
were removed with their dead path; the existing general import-closure test
remains. The Mistral reasoning-label rule and its 33 behavioral cases remain.

Red-first removal audit: exit 1, listing eleven remnants of the withdrawn
feature. The same audit now exits 0. Its rerunnable source is
MODEL-396-r3-removal-audit.py; run from the engine with:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-396-r3-removal-audit.py
```

Focused command, exit 0: **524 passed in 9.56 s**.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q \
  tests/test_model_396_readers.py tests/test_decision_verify.py \
  tests/test_decision_sources.py tests/test_worker_vendor_imports.py \
  tests/test_worker_bundle.py
```

The source-pipeline tests retain the pre-existing PDF-is-unsupported behavior.
No new parser replacement or PDF tests were introduced. The design note and
PR body record both reviews' probes as acceptance requirements for a future
structural allowlist and exact hashed region templates. Current code provides
neither PDF extraction nor a heading-based output-limit reader.

Python 3.14.4; Node 22.22.3. Playwright's locked package was present before the
full run. The completed full-engine and broader-data results are recorded below; no
partial run is counted as a completed gate.


### Completed round-three gates

Implementation SHA: `9b620332de18c12c54fbd1ef54ab445893c8205b`. The full run
used this clean implementation. This final engine commit changes only evidence;
the canonical data replay records its exact final evidence-head SHA after commit.

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Result: **11208 passed, 9 skipped, 11 warnings in 1167.86 s (19:27)**,
exit **0**, captured directly from the process. The eleven warnings concern the
existing unsigned decision vocabulary in CLI snapshot/keyed-origin tests.
There are no failed or errored tests. Full stdout/stderr is retained in
MODEL-396-r3-full-engine.log.gz. The focused gate remains **524 passed**, exit 0.

Data replay, cwd `/Users/terbeest/dev/worktrees/data-model-396`:

```bash
PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 /Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/replay.py
/Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/validation/r3/audit.py
/Users/terbeest/dev/modelspec/.venv/bin/python research/model-396/sources/primary-research/check-sources.py
```

All three exit **0**. The genuine verifier produces **15** independent,
schema-valid facts, with all **14** baseline fact dictionaries unchanged. The
candidate bundle contains no PDF source registrations or citations. The raw
receipt integrity check covers 29 retained responses and four recorded HTTP
failures; it does not parse PDFs. A second red/green audit exposed and removed
a redundant PDF citation from the new output-modalities claim, which still
verifies from the model page alone.

The exact broader private-data suite from recall-private.yml ran on archived
data `f9eb36f96a68a1222b2afd5f77b04804a35f69f8` with main's unchanged engine
pin `d29d1c6cf7c3671e51f9191f3f2594afe4afbb6b`: **938 passed, 17 skipped,
zero failures in 161.86 s**, exit **0**. Python 3.11.15; pytest 9.1.1; Git
2.50.1. Its three candidate bundle files match the tested revision byte for byte.
The exact commands, environments, versions, exit codes and hashes are retained
in data PR #90 under research/model-396/validation/r3/. Subsequent data changes
record validation evidence and the final engine-head replay binding only.

Four gaps remain unfiled: reader gap `model.max_output_tokens`, and source gaps
`feature.streaming`, `origin.base_lineage`, `origin.weights_hosting`. No premier
admission, API offering, production fact or data-pin change was made. Public
contract version 2.18, schema/OpenAPI, ranking floors, legal terms and production
switches still match the pre-ticket baseline. The original unsupported-PDF
source-pipeline test remains green; there is no replacement PDF parser.

Both review probe sets are documented as future acceptance requirements, not
claims that the retired implementation was safe. Historical round-one and
round-two PDF/16-fact results above are superseded. No paid provider call,
Worker isolate deployment, live production query, workflow dispatch, Linear
write or merge was performed. The hosted workflow and production behavior were
not independently observed in this round. Both PRs remain drafts.
