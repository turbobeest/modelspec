# MODEL-396 source readers

The scoped Mistral output-label rule remains unchanged. PDF extraction now has
an explicit structural allowlist and a verifier route bound to reviewed source
templates. There are no approved production PDF templates. Small 4 still has
fifteen supported facts and four gaps. It remains outside premier, with no API
offering filed.

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

## Restricted PDF support

`pdf-pypdf-6.19.0-v1` uses exactly `pypdf==6.19.0`. The parser runs offline in
the operator process and rejects a different installed version. The Worker
does not import or vendor the parser or its dependency.

`decision/pdf_sources.py` admits this structure:

- One classic cross-reference section, with consecutive generation-zero
  objects in file order. The trailer has integer `Size`, a `Root` reference,
  and an optional `Info` reference. No incremental updates, cross-reference
  streams or object streams are admitted.
- A catalog containing only `Type` and `Pages`. The page tree is flat, has
  unique page references, and its `Count` matches its children.
- Each page has `Type`, the matching `Parent`, a numeric `MediaBox`,
  `Resources` and one `Contents` stream.
- Resources contain only a font map. Fonts are the standard Helvetica,
  Courier or Times Type1 variants, with optional Standard or WinAnsi encoding.
  PDF names must have the PDF name type, not a string with matching text.
- Content streams are unfiltered or use one Flate filter without decode
  parameters. Operators are `BT`, `ET`, `Tf`, `Td`, `TL`, `T*`, `Tj` and `TJ`.
  Their operands and text-state transitions are checked before extraction.
- Optional document information contains only a string `Producer`.

Every indexed object must belong to that structure. Unused objects, unknown
keys, actions, links, annotations, embedded files, images, scanned pages,
forms, font programs and metadata streams refuse. Encrypted, malformed and
blank documents refuse. There is no partial output or alternative text recipe.

The limits are 1 MiB of input, 16 pages, 256 indirect objects, 256 KiB decoded
per stream, 1 MiB decoded in total, 10,000 content operations and 64 KiB of
extracted UTF-8 text. Parser I/O has a separate budget of 16 MiB read and
262,144 read calls. Token nesting is limited to 32. The cross-reference
section, complete trailer, numeric lexemes and exact stream lengths are
checked before the library can repair them. Flate decoding uses bounded
output; operations are counted during token parsing.

PDF sources require a whole-document page locator with an empty value. The
existing `copy_ref` hashes original bytes. The existing `page_fingerprint`
and region fingerprint hash extracted text.

`decision/pdf_templates.py` holds reviewed templates. Each template binds
the source URL, original hash, complete extraction hash, subject, source kind
and facet. It names a fixed line and a full-match expression whose `value`
group reads the value from that line. It also records the affirmative
retention-terms decision's URL. Templates are executable review policy, not
collector-supplied assertions.

Source rechecks and stored-region reads require approval for the exact URL
and original bytes. The existing cite-only policy takes precedence. PDF
verification runs before ordinary readers, with no generic or LLM fallback.
Changed captions, duplicate tables or ownership context change the hashes
and require review. An independent non-PDF citation can still verify a claim.
A jurisdiction union cannot omit its PDF citation.

No production template is included because the data#98 audit classifies the
Mistral hosts as silent and expressly distinguishes silence from permission.
Existing-copy replay is a diagnostic, not an affirmative retention decision.
The current Small 4 PDF also exceeds the 256-object limit. Its 256,000-token
maximum-output candidate remains unverified.

## Prior withdrawn implementations

The earlier PDF recipe and model-properties output-limit heuristic were
withdrawn after REV-760 and REV-760b. The current implementation does not
restore that heuristic, page-number locators or a broad PDF object walker.

REV-760 found resource limits missing, another model's table accepted, and
JavaScript plus embedded files accepted. The second attempt added limits and
more exclusions, but REV-760b still accepted external actions in OpenAction
arrays, an embedded filespec stream, and another model's table under a caption.
PDF support would close only `model.max_output_tokens`; the other three source
gaps already prevent admission. The orchestrator withdrew the feature rather
than extend either parser heuristic.

## Requirements when extending PDF support

A future proposal starts with an **allowlist of acceptable PDF object
structure**: permitted object types, keys, value types and relationships.
Anything outside that explicitly reviewed structure must refuse. Extending
an action-name blocklist is not an acceptable design.

Any table region needs an **exact hashed template**, bound to its claim subject,
source bytes and approved region representation. The template must account for
captions, headings, cell order and surrounding ownership context. Unrecognized
or changed templates must refuse; heading proximity cannot establish ownership.
The restricted implementation above starts from a structural allowlist and
exact source templates. Extensions require the same review.

The following historical review probes remain acceptance requirements.
`tests/test_pdf_sources.py` exercises synthetic extraction, template bindings,
resource limits and refusals. The current limits are smaller than the former
implementation's limits. A case outside the structural allowlist and exact
template must refuse and must never verify the wrong claim.

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

`model.max_output_tokens` remains a gap. The retained PDF is a research receipt,
with no approved retention decision or supported verification template.
Closing it requires a qualifying non-PDF primary source, or both an affirmative
retention decision and a reviewed extension that admits the actual PDF.
The source gaps remain per-model streaming, express base lineage and the
complete first-party weights-hosting country set. Four gaps mean no premier
admission or offering, and no data engine-pin bump in this PR.
