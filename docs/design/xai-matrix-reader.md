# xAI exact-template matrix reader

MODEL-367. Design-first commit against engine base
`34c6dbef95371cff728a7a28aba33dcffe3e50e3`.

## Current evidence and scope

Full Chromium 153.0.8010.12, headed with its standard user agent, retrieved
https://x.ai/pricing and https://x.ai/grok/business on 2026-10-18. Headless
Chromium received HTTP 403. Waiting indefinitely for network idle also failed;
the successful capture used DOMContentLoaded and a bounded idle wait.
Rendered HTML, screenshots, retrieval metadata and SHA-256 hashes stay in
private `modelspec-data/research/model-367/`. No page bytes enter the public
engine or Worker snapshot.

The pricing matrix now has seven columns: Free, Plus, Premium, Super, Ultra,
Teams and Enterprise. Neither SuperGrok Lite nor SuperGrok Heavy occurs in that
matrix. Do not reinterpret a new plan as an old plan, infer retirement from
absence, or approve the ticket's historical matrix from its description.
There is no approved current consumer template. Consumer extraction must
report `template drifted`, including for a claimed null. The eight consumer
facts cannot be positively curated from this page. Record that limitation in
the data PR and leave unsupported facts unadmitted.

The Business pricing section names Business and Enterprise and has Models rows
Imagine, Voice and Grok 4.7. Both Grok 4.6 and Grok 4.7 exist in the canonical
catalogue. Only the exact Grok 4.7 label may map to `xai/grok-4-7`; Imagine and
Voice are product names without exact versioned model IDs. Business curation
is conditional on inspecting the retained glyphs and proving their ownership.
If that check fails, defer Business too.

## Reader contract

Use a narrow engine module and exclusive verification dispatch for the four
consumer subscription facets and Business model coverage and coverage quote. The parser takes only a
registered first-party source, a retained copy, a canonical offering subject
and a facet. The registry contains no executable parser instructions.

A reviewed template records:

- The exact source URL, cited region and canonical offering IDs.
- The raw retained copy SHA-256, a hash of its complete normalized document
  representation, and a hash of the
  selected DOM region including tags, attributes, text, cell order and SVG
  path data. The full-document binding also covers surrounding ownership
  context. This intentionally permits false refusals after unrelated page
  changes. Re-review is preferable to a silent change in interpretation.
- Explicit paths to the ordered plan headers, ordered row labels and every
  corresponding cell. These are paths in one reviewed DOM, never searches for
  nearby words or similarly named plans.
- The exact header strings and row strings, and the hash of each approved SVG
  glyph. Every glyph in the recorded matrix must be recognized before any
  claim can produce a reading.
- Literal model-label-to-canonical-ID mappings. No fuzzy catalogue lookup,
  aliases or model-version substitution establishes a reading.

Preserve HTML through the existing `text-default` source recipe with a whole
page citation. This keeps SVG markup and avoids changing shared HTML
normalization. Hash the exact representation that `StoredRegions` gives the
verifier, with the same recipe and version. Register new private source IDs;
do not change normalizers for historical citations. Normalized fingerprints
retain SVG and layout markup; the raw copy hash detects every byte change. The raw retained copy has a separate hash
in the retrieval manifest and CopyStore verifies it before use. The template
must also match that raw copy hash: Unicode normalization can otherwise turn
a changed or invalid SVG command into the approved normalized path. A citation
must use the actual whole-page locator, not a same-named excerpt region.

An unregistered page hash, different source URL, missing/duplicate region,
reordered/extra header, changed row, moved cell, unexpected glyph or unresolved
model must fail closed. The result must say `template drifted`. A failed exact
reader may not fall through to table, prose, neighbouring-cell or LLM readers,
and may not verify `not_disclosed` merely because it found no reading. A
consumer template allowlist remains empty until current first-party evidence
actually names those two plans.

## Facets and data filing

`offering.subscription.programmatic_or_agent_use` is already a string whose
registry definition includes agent products. A future approved matrix may
therefore say `Grok Build included; Grok Bot not included` without asserting
raw API permission. Do not add `api` to `surfaces` or change own-software routing.
Today there is no qualifying Lite/Heavy matrix, so do not file these strings.

Usage allowances require current explicit text attached to the named plan.
Coverage quotes require exact current wording. The old consumer allowance and
quote values are already quarantined in the private baseline; retain their
history and record why they cannot be re-admitted. Retrieval failure, template
drift and missing plan identity are not evidence of `not_disclosed`. Use the
existing unknown/quarantine representation when current support is absent.

Business models may be updated only by the approved exact region. The old
Business quote names 4.6; it must not remain admitted while its source now
names 4.7. Recheck or replace it with a properly sourced unknown state, without
inventing a new quote from the matrix.

No schema, public contract, ranking floor, legal text or production switch
changes. The private engine pin must descend from its current pin. The data
PR remains draft and depends on the engine commit reaching main.

## Reuse and storage

The retrieved robots file permits public paths and declares search/AI content
signals. That is not a redistribution licence. Review the current consumer and
enterprise terms and record their URLs, dates and hashes privately. Retain
source copies privately for review; publish only parser code, hashes, necessary
short labels and synthetic fixtures. Do not claim permission for bulk reuse.
No paid provider calls or Firecrawl credits are needed.

## Verification

Tests run through retained CopyStore and the public verification boundary.
Use an explicitly synthetic reviewed matrix for consumer positive controls;
never present it as a current xAI page. Test both glyph meanings and exact
model ID mapping. The six required mutations are reordered columns, an extra
column, a swapped glyph, a renamed plan, a changed row label and a cell moved
one column. Each must fail closed with a drift reason, even when a fallback
reader could otherwise verify the value. Include unknown glyphs, wrong
source/subject, duplicate regions, corrupt copies and null claims.

Replay the approved Business template against retained private bytes. Public
fixtures must be synthetic. Run focused reader suites, `cd web && npm ci`, the
full engine suite under `/tmp/modelspec-fullsuite.lock` with four workers, and
the private data suites. Record exit codes, red/green output, tool versions,
base/final commits and unobserved outcomes. Consumer positive curation remains
blocked by the changed live page even if parser tests pass.
