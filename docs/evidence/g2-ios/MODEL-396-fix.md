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
