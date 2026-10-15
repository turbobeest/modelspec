# MODEL-396 source readers

Only the scoped Mistral output-label rule remains in this change. PDF source
support and the model-properties output-limit reader were dropped after two
cross-model reviews, REV-760 and REV-760b. Small 4 has fifteen supported facts
and four gaps. It remains outside premier, with no API offering filed.

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

The retained tests cover text plus reasoning in each supported form, text plus
image, unknown labels, reasoning-only lists, similarly named labels, input
lists, other labs, other source hosts/paths, model identity mismatches and
conflicting output blocks. Both reviews found this rule sound.

## PDF support withdrawn

Remove the PDF recipe, extractor, offline adapter, dependency, source-locator
extension and model-properties output-limit reader. Remove their tests and
restore the shared normalizer, source fetcher, source model, CLI provenance
hash and Worker import tests to their pre-ticket versions. The Worker vendor
map and dependency locks already match that baseline. Its existing general
import-closure test remains; the PDF-specific guards are removed with the code
they guarded. PDF bytes and PDF content types remain unsupported by the
existing source pipeline.

REV-760 found resource limits missing, another model's table accepted, and
JavaScript plus embedded files accepted. The second attempt added limits and
more exclusions, but REV-760b still accepted external actions in OpenAction
arrays, an embedded filespec stream, and another model's table under a caption.
PDF support would close only `model.max_output_tokens`; the other three source
gaps already prevent admission. The orchestrator withdrew the feature rather
than extend either parser heuristic.

## Requirements for any future PDF design

A future proposal starts with an **allowlist of acceptable PDF object
structure**: permitted object types, keys, value types and relationships.
Anything outside that explicitly reviewed structure must refuse. Extending
an action-name blocklist is not an acceptable design.

Any table region needs an **exact hashed template**, bound to its claim subject,
source bytes and approved region representation. The template must account for
captions, headings, cell order and surrounding ownership context. Unrecognized
or changed templates must refuse; heading proximity cannot establish ownership.
No reusable PDF implementation or table heuristic is retained here.

The following review probes are required acceptance tests for that new design.
They are recorded as a test specification; this PR provides no PDF parser to run
against them. Unless a case is explicitly admitted by the reviewed allowlist
and exact template, it must refuse and must never verify the wrong claim.

### REV-760 probes

- Resource limits: more than the approved page/input/text limits; a Flate stream
  expanding to 1,000,000 and 80,000,000 zero bytes; and 20,000 `q`/`Q` pairs.
  A future design must own finite decoder and deterministic work budgets rather
  than inherit a library default or rely on wall-clock time.
- Table ownership: an Other Model 999k table followed by a Mistral Small 4 title
  and “See the table above”; the inverse order; two subjects with different
  tables; duplicate candidate tables, including equal values; and no heading.
  The Other Model value must never establish Small 4's output limit.
- Table meaning: input 256k/output 8k must not verify an output claim of 256k;
  reversed columns, missing/non-token units and conflicting text rows refuse.
- Active content: JavaScript actions/name trees and a retained embedded file
  must refuse even when neither payload appears in extracted text.
- Encrypted PDFs, scans with text overlays, image-only and blank pages,
  malformed PDF, HTML mislabeled or prefixed as PDF, other recipe names and
  extractor-version mismatches must not gain a text fallback.

### REV-760b probes

- Catalog OpenAction `[URI-action]`, `[page /Fit URI-action]`, and the same URI
  arrays on a page dictionary or link annotation must refuse. A GoTo action
  carrying an additional URI key must refuse. A plain `[page /Fit]` destination
  and an ordinary URI link require explicit structural admission, not an early
  return merely because the value is an array or is named GoTo.
- A filespec whose `/EF /F` points to a stream of `EMBEDDED_SECRET_BYTES` must
  refuse, including when no EmbeddedFiles name tree is present.
- A caption above a plain Model properties label must not lend the following
  table to the earlier subject, under either text or HTML normalization:

  ```text
  Mistral Small 4
  Caption: Other Model
  Model properties
  Input type | Maximum size | Output type | Maximum size
  Text | 1 token | Text | 999k tokens
  ```

- Preserve the negative action probes on catalog, page and annotation objects:
  JavaScript/JS, AA JavaScript/Launch/URI, Launch, embedded files, file
  attachments, RichMedia, annotation A JavaScript/Launch, and script names in
  decoded metadata/object streams, including escaped names such as `/#4A#53`.
- Retest both orders of separately headed subjects, repeated Model properties
  headings, same-value duplicates, foreign model declarations, foreign names
  in architecture/range metadata, captions inside the section and HTML captions.
- Exercise production resource thresholds, not only lowered test constants.
  Historical probes were 26,215,076 input bytes; 301 pages; a Flate stream of
  4,194,305 decoded bytes; thirty 1,000,000-byte decoded streams; 320,000 `q Q`
  operators; and two pages with 2,600,000 ASCII letters each. Budget exhaustion
  must refuse deterministically before an accepted or partial text result.

## Contract and admission checks

The retained rule changes source interpretation only. No public response field,
output modality, facet, ranking floor or legal term changes. Contract version
2.18 and its schemas stay unchanged.

`model.max_output_tokens` is now a reader gap: the retained PDF is a research
receipt, with no approved verification path. Closing it requires either a
qualifying non-PDF primary source or the separately reviewed design above.
The source gaps remain per-model streaming, express base lineage and the
complete first-party weights-hosting country set. Four gaps mean no premier
admission or offering, and no data engine-pin bump in this PR.
