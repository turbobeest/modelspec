# MODEL-396 PDF source support evidence

Base SHA: `3c8042a11aa47e8577559e01f71379119bda2cec`.
Final implementation SHA: `6e85998943eb3767e0e10cbf399a6f7f4835a719`.
The subsequent evidence-only commit is the delivery HEAD. Its final SHA is
reported in `CODEX_EXEC_DONE` and can be reproduced with `git rev-parse HEAD`.

Worktree: `/Users/terbeest/dev/worktrees/model-396`.
Branch: `model-396-pdf-sources`.

## Result and limits

Added an offline PDF recipe pinned to `pypdf==6.19.0`, an explicit object
allowlist, bounded decoding and parsing, and exact source templates for
verification. Original bytes and extracted text use separate existing hashes.
PDFs cannot reach generic or LLM readers. Retention approval is required for
the exact source URL and copy hash. Cite-only rules take precedence.

There are no approved production templates. This PR supplies the engine and
synthetic acceptance tests, not a Mistral data filing. The existing Mistral
reasoning-label implementation was already correct at the base SHA and remains
unchanged. It maps the first-party `reasoning, text` output list to `{text}`.

The accepted PDF subset, limits, template bindings and prior review probes are
documented in `docs/design/MODEL-396-readers.md`.

## Red-first evidence

All pytest commands below ran serially, with cacheprovider disabled. Exit codes
were checked directly.

Before changing production code:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py tests/test_model_396_readers.py
```

Exit `1`, `3 failed, 51 passed in 1.11s`.

| Test | Observed red output |
| --- | --- |
| `test_pdf_extracts_repeatable_text_and_hash` | `UnsupportedContentError: unsupported content: pdf` |
| `test_pdf_recipe_refuses_malformed_or_mislabeled_content[<html>Not a PDF</html>]` | `Failed: DID NOT RAISE UnsupportedContentError` |
| `test_pdf_recheck_hashes_extraction_and_retains_original_only_with_terms_approval` | `Value error, unknown normaliser 'pdf-pypdf-6.19.0-v1'` |

The same command first became green with exit `0`,
`54 passed in 1.37s`. The existing reasoning-label tests passed on both runs.

Review then found additional defects in the new implementation. Each group
below was reproduced before its fix, using:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py -k trailer_extensions
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py -k strings_in_name
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py -k text_transforms
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py -k independent_non_pdf
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py -k repairs
```

| Defect and test | Red result, each exit `1` | Correction |
| --- | --- | --- |
| `test_pdf_rejects_trailer_extensions_before_constructing_parser` | `3 failed, 63 deselected`; `unapproved trailer reached PdfReader` | Complete trailer allowlist before library construction, including escaped-name rejection. |
| `test_pdf_refuses_strings_in_name_fields` | `4 failed, 66 deselected`; `DID NOT RAISE` | Enforce PDF name and integer types rather than string or numeric equality. |
| `test_pdf_refuses_text_transforms_outside_the_subset` | `3 failed, 72 deselected`; `DID NOT RAISE` | Remove transformations and graphics-state operators from the subset. |
| `test_pdf_does_not_block_an_independent_non_pdf_source` | `1 failed, 79 deselected`; `'skipped' == 'verified'` | Allow independent non-PDF verification while retaining complete-citation requirements for jurisdiction unions. |
| `test_pdf_refuses_numeric_repairs`, `test_pdf_refuses_numeric_repairs_inside_text_arrays` | Part of `6 failed, 80 deselected`; `DID NOT RAISE`, with pypdf warning that invalid numbers were replaced with zero | Validate numeric lexemes and nesting before library parsing, including structural and content arrays. |
| `test_pdf_refuses_stream_length_repairs` | Part of the same six failures; negative and off-by-one lengths both returned text | Check raw stream dictionaries, direct lengths and exact byte boundaries before parsing. |

The Worker import-closure test also failed while the lazy operator import was
unclassified:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py tests/test_model_396_readers.py tests/test_worker_vendor_imports.py
```

Exit `1`, `1 failed, 104 passed in 1.65s`. The missing import was
`decision/normalise.py imports decision.pdf_sources`. It is now explicitly
classified as build-time only. A fresh Python process proves that importing
the Worker-shipped model and normalizer does not load pypdf or the PDF module.
The private Worker memory runs below exercise the bundled runtime.

## Final focused verification

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pdf_sources.py tests/test_model_396_readers.py tests/test_decision_sources.py tests/test_decision_verify.py tests/test_decision_model.py tests/test_cite_only_retention.py tests/test_cite_only_verification.py tests/test_worker_vendor_imports.py
```

Exit `0`, `714 passed in 30.63s`. This includes every red-first test above.

The PDF tests generate their own fixtures. They cover repeatable extraction,
both hashes, approved and unapproved retention, every template binding,
changed ownership and units, wrong recipes and versions, malformed inputs,
encrypted PDFs, blank pages, active objects, embedded files and production
resource limits. No third-party PDF is committed.

Additional commands:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check --fix decision/pdf_sources.py decision/pdf_templates.py tests/test_pdf_sources.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/pdf_sources.py decision/pdf_templates.py tests/test_pdf_sources.py
git diff --check
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py
```

Ruff fixed import formatting, then reported `All checks passed!`.
Whitespace validation passed. The shard planner assigned 82, 82, 83 and 82
files with predicted totals of 3958.133, 3958.132, 3958.132 and 3958.133 seconds.
Public vendoring exited `0` and reported `vendored 129 files`. Generated
packages remain ignored by git.

No full local pytest suite or local site build was run. CI remains the full
gate. Frozen data, ranking floors, legal terms, public response fields,
production switches and Worker dependency locks were not changed.

## Existing Small 4 copies

The private checkout was created with:

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-396-scratch/private_sources/modelspec-data
```

Its HEAD was `a6f8fd798d7d6f40b35ed08320796b773f29df9a`. From that checkout:

```sh
git ls-remote origin refs/pull/98/head
git fetch --depth 1 origin refs/pull/98/head:refs/remotes/origin/data-pr-98
git show origin/data-pr-98:research/model-409/source-terms-audit.md
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 /Users/terbeest/dev/modelspec/.venv/bin/python tools/research/model-396/replay.py
```

The audit ref was `8fb320abf57dddd63bcdd8709b686e8cb7f02080`. It classifies the
Mistral hosts as silent and says silence is not permission. The current engine
policy continues to identify x.ai, docs.x.ai and perplexity.ai as cite-only.

Replay exited `0` and reported 15 supported facts verified through
`StoredRegions` and independent deterministic readers. Output modalities read
as `["text"]` via `mistral-output-labels@1`. Four gaps remain: maximum output,
per-model streaming, express base lineage and complete first-party
weights-hosting countries.

The existing technical PDF was also checked in memory, without writing a new
retained PDF. Reproduce that check from the engine worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import gzip
from pathlib import Path
from decision.normalise import NORMALISERS, normalise_document, UnsupportedContentError
from decision.pdf_templates import retention_approved
from decision.sources import fingerprint_bytes
root = Path('/tmp/model-396-scratch/private_sources/modelspec-data')
body = gzip.decompress((root / 'research/model-396/sources/primary-research/technical-documentation.pdf.gz').read_bytes())
url = 'https://legal.mistral.ai/documents/For%20Downstream%20Providers%20only%20-%20Technical%20Documentation%20Mistral%20Small%204.pdf'
print('existing_pdf_bytes:', len(body))
print('existing_pdf_hash:', fingerprint_bytes(body))
print('retention_approved:', retention_approved(url, fingerprint_bytes(body)))
try:
    normalise_document(body, NORMALISERS['pdf-pypdf-6.19.0-v1'])
except UnsupportedContentError as exc:
    print('extraction_refused:', exc.kind)
else:
    raise SystemExit('Unexpected acceptance: a production template still needs review')
PY
```

Exit `0`. The 201,453-byte PDF matched
`sha256:9a40824543b1f0eedd0dd9db66f01e8f86f7284ec86e3063de40fa407dc6cc32`.
Approval was `False`; extraction refused with `pdf_object_limit`.
The supplied 256,000-token candidate was not independently read or verified.
The implementation does not admit Small 4 to premier or file an API offering.

## Private Worker memory

Following the deploy path in `.github/workflows/rank-api.yml`, a scratch bundle
was built from the private data checkout with a disposable signing key.
No production signing key was used. Commands ran from the engine worktree:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm install --prefix /tmp/model-396-scratch/private_sources/memory-runtime --no-save --cache /tmp/model-396-scratch/private_sources/memory-runtime/npm-cache pyodide@0.28.3
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/terbeest/dev/worktrees/model-396 TMPDIR=/tmp/model-396-scratch/private_sources/memory-tmp MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_SNAPSHOT_KEY=model396-memory-disposable-fixture-key /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/model-396-scratch/private_sources/modelspec-data --out /tmp/model-396-scratch/private_sources/memory-bundle
```

After vendoring, each `api/worker/src/*.py` was copied into the scratch bundle
using `shutil.copy2`, matching the workflow's copy step. Then:

```sh
env NODE_PATH=/tmp/model-396-scratch/private_sources/memory-runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model396-memory-disposable-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/model-396-scratch/private_sources/memory-bundle --limit-mib 115 --output /tmp/model-396-scratch/private_sources/memory-evidence/current.json
env NODE_PATH=/tmp/model-396-scratch/private_sources/memory-runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model396-memory-disposable-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/model-396-scratch/private_sources/memory-bundle --successor --limit-mib 115 --output /tmp/model-396-scratch/private_sources/memory-evidence/successor.json
```

Both probes exited `0`.

| Period | Steady bytes | Steady MiB | Peak MiB |
| --- | ---: | ---: | ---: |
| Current | 114206478 | 108.915785 | 109.738157 |
| Successor | 109677046 | 104.596182 | 105.418722 |

Each exercised decide, vocabulary, rank and policy-check. Network requests
were stubbed to fail, and no Worker network request occurred. The public
bundle was re-vendored afterward.

## Tool versions and observations

- Python 3.14.4, pytest 9.1.1, pypdf 6.19.0, Ruff 0.16.6.
- Git 2.50.1; GitHub CLI 2.102.0.
- Node 22.22.3; Pyodide 0.28.3.
- Generator dependencies matched the workflow pins: pydantic 2.13.5,
  PyYAML 6.0.3, httpx 0.28.1 and cryptography 45.0.7.
- The measured Pyodide runtime used pydantic 2.10.6, pydantic-core 2.27.2
  and PyYAML 6.0.2. The generator interpreter differs from CI's Python 3.13.

No live deployment, browser rendering, OCR, vendor API call, Firecrawl call,
new provider fetch, full CI result or cross-model review was observed.
No private dataset or source bytes were added to this repository.
The private clone and generated private bundle were deleted after the checks.
All started command sessions completed; no background process was left running.
