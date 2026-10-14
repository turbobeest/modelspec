# MODEL-396 source readers

This note precedes the reader code and is the initial engine draft PR body.
Small 4 remains outside premier unless all nineteen guaranteed facts verify.

## PDF normalization

Register an opt-in `pdf-pypdf-6.19.0-v1` recipe. Neither HTML nor plain-text
recipes begin accepting PDFs. Pin `pypdf==6.19.0` in the engine's development
dependencies and check the installed version before extraction. There is no
PDF extractor in the existing lockfiles. pypdf is an established, pure-Python
library already installed in the operator environment and used by the existing
research scripts. It avoids depending on the host's Poppler version.

The retained, SHA-256-addressed source is the original PDF bytes. Text is a
derived normalization identified by the recipe name. Parse with strict PDF
handling, without passwords, network calls or OCR. Extract pages in document
order with pypdf's layout mode, fixed options and no blank-line padding. Apply
the existing Unicode and whitespace rules, converting internal layout gaps of
two or more spaces into table-cell separators. Source locators remain the
existing whole-page and exact-excerpt forms. PDF sources cannot use HTML
selectors or headings. Changes to the extractor, its options or this recipe
require a new recipe name.

Reject encrypted, malformed, empty and image-only documents. Reject a document
if any page has no machine-readable text. Permit only small raster decorations
whose drawn edge lengths are at most 16 points and whose aggregate area is less
than one percent of the page. Larger images, inline images and invisible text
rendering modes are unsupported, including a scan with an existing text overlay.
Calculate image coverage from PDF placement transforms, including nested form
objects, rather than pixel dimensions. This conservative rule can reject a
legitimate image-heavy technical report. Small checkbox images in Mistral's
technical document do not qualify as scans. Do not recover a rejected PDF by
decoding its bytes as plain text.

The output-limit reader recognizes the documented four-column model-properties
table: `Input type | Maximum size | Output type | Maximum size`. It reads only
the text output's maximum-size cell, requires a token unit and model identity,
and refuses missing, conflicting or malformed rows. An input limit must never
stand in for the output limit.

Adversarial checks cover repeated extraction with literal expected text,
original-byte copy hashes, recheck changes, incorrect extractor versions,
encrypted PDFs, blank pages, image-only pages, scans with text overlays,
malformed PDFs, HTML mislabeled as PDF, non-PDF recipes, selector misuse and
different input/output limits.

## Mistral output labels

Treat the exact documented `reasoning` label as a feature description only
when reading an explicit output-label block from a first-party Mistral model
page. Bind the rule to a Mistral model identity and the exact primary
`docs.mistral.ai/models/` host/path. Supported source forms are native Markdown
`Output: reasoning, text`, its HTML-normalized label block, and an explicit
two-cell output-label row. Match whole labels, case-insensitively, and require
at least one actual output label. Retain every other label so an unknown label
or additional real output causes the ordinary exact-set comparison to fail.
Do not change generic set comparison or input-label handling.

The registry has no separate reasoning feature facet. It already has
`feature.effort_controls` for request-controlled reasoning, and Small 4's
verified effort-control fact remains on that facet. Add no facet or output enum.

Adversarial checks cover text plus reasoning in each supported form, text plus
image, unknown labels, reasoning-only lists, similarly named labels, input
lists, other labs, other source hosts/paths, model identity mismatches and
conflicting output blocks.

## Contract and admission checks

Read the actual decision contract and check MODEL-59 against the final diff.
These changes affect source normalization and independent readers. They do not
add output modalities, widen public response fields or alter the decision
envelope. No contract version change is planned.

Research must separately establish per-model streaming, an express base-lineage
statement and the complete first-party weights-hosting country set. Generic
platform streaming, `Model dependencies NA`, inference-region scopes and the
lab's incorporation country do not establish those facts. If any remains
unsupported, file the exact gaps and leave premier and the API offering alone.
