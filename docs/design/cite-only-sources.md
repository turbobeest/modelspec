# Cite-only sources

MODEL-411, 2026-10-19. Design references below refer to base
`bbfa93be5eed392878a2af0d709ca6e774302c5c`.

## Policy and storage

The initial host policy lives in `registry/source-retention.json`, a public
build configuration, with `schema_version: 1` and `cite_only_hosts` containing
`x.ai`, `docs.x.ai`, and `perplexity.ai`. It is not curated model data and is
not one of the frozen paths in `pipeline/data_source.py:30`. Private overlays
retain this configuration. No private data PR or edits to the 718 existing
premier facts are part of this change.

A shared, standard-library retention module loads this file. Hosts are
case-insensitive, ignore a terminal dot and port, and match the named host or
its subdomains on a label boundary. Redirect destinations count too. Unknown
or missing configuration must not silently disable a configured policy.

A source citation retains the URL, fetch timestamp and SHA-256 `snapshot_ref`.
The timestamp belongs to the retrieval, not to verification. `SourceRef`
currently carries source ID, hash and regions (`decision/model.py:49`);
`SourceSnapshot` already carries retrieval date and hash (`:493`). Add an
optional retrieval timestamp to source references for new readers. Existing
references lacking that timestamp remain explicitly undated; never invent a
fetch date from the verification date.

`CopyStore.put` currently writes every byte sequence without source context
(`decision/sources.py:438`). Require a source URL on writes and enforce the
host policy there. For cite-only content, return its hash and retain only
citation metadata. Do not retain page bytes, normalized text, quotes, browser
HTML, scraper responses, or derived page caches. Historical copies are not
deleted by this ticket; readers refuse to use them for cite-only sources.

All writer paths must use the guard, including ordinary rechecks
(`decision/sources.py:687`), rendered price rechecks
(`scripts/price_reread.py:289,405`), rendered fallback artifacts
(`scripts/price_reread_fallback.py:273`), pricing scrape caches
(`scripts/fetch_pricing.py:595,611`), and benchmark fetch caches
(`scripts/benchmarks/fetch.py:308,490`). Local fixture tests cover these
boundaries. Collection scripts that cannot safely provide a transient reader
must refuse before invoking a disk-writing scraper.

## Assurance and admission

The new assurance state is `cited`, displayed as "Cited, not machine-verified".
It is separate from `Fact.state`, whose existing values describe knowledge of
a value (`decision/model.py:396`). A cited known price is still a known price.

`verify()` returns `Result.outcome == "cited"`, `verification is None`, and a
reason naming the retention policy. The early policy check runs before every
specialized dispatch (`decision/verify.py:6321`) and before `regions.text()`.
No extractor or quotation cache runs. Queue checked events and run counts
record cited separately; they do not append a `Verification` or endlessly
request recrawls (`decision/verify.py:6585,6610,6651`). The `Verification`
outcome enum and two-key rule stay unchanged (`decision/model.py:98,117`).

The snapshot derives assurance from registered source URLs and policy, not
from a caller-supplied claim of verification. A cited fact retains
`verification: null` and an additive `citation` object with `status: "cited"`
and source references including URL, source ID, snapshot hash, and available
retrieval timestamps. It cannot masquerade as verified even when an old
verification record remains in frozen data. Missing dates remain null.
Source references must resolve and carry valid hashes. Existing latest
mismatch or unreachable results still quarantine the associated value;
excluded publishers remain excluded. Non-cite-only facts keep the existing
value-hash-bound, independent verification gate (`decision/snapshot.py:750,804`).

Cite-only facts are admitted to the premier lineup, snapshot, and fact-based
decision ranking through this explicit exception. The guaranteed-facet gate
currently checks admitted presence (`decision/snapshot.py:1430`), so a cited
fact can provide completeness but cannot provide machine verification. This
follows Jamie's "cite only then merge" decision. Two independent keys are
still required to claim verified; citation admission makes no such claim.
Unknown facts remain unknown. A cite-only host is not a reason to manufacture
an absent value or bypass registry/schema validation.

This exception is for facts. Benchmark evidence in decision responses still
requires independent verification. The legacy card/ranking path must stop
counting evidence from a cite-only host as verified, retain its ordinary
ranking policy, and disclose citation status separately. Ranking floors,
class boundaries, and cost-to-correct policy do not change.

## Public representations

The design reads the current decision, API, rank, policy-check and CLI
contracts. MODEL-59 permits additive fields and open warning codes. It does
not permit adding to closed enums without a major bump.

Keep all existing closed states and verification outcomes. Add citation
metadata to exports and shown facts as needed, and use
`cite_only_not_machine_verified` in decision and result warnings. Full,
bounded, and explain-none decisions must retain the warning. Source dates
continue to mean verification dates (`decision/contract.py:1775` and
`docs/decision-contract.md:1640`); a cite-only source's verification date is
null. Fetch dates and hashes belong to citation metadata. Verified-only API
model identifiers must not be promoted from cite-only facts.

The explanation guard currently accepts verified records only
(`decision/explain.py:130`); add a narrow branch for validated cited fact
records, never for benchmark evidence. Model pages show a citation notice
beside affected facts. Both decide interfaces show the notice. The MCP
forwards decision and result warnings (`mcp/src/server.ts:563,574`), so it uses
the same assurance disclosure. CLI JSON preserves the response body.

For legacy rank results, add citation metadata/warnings while preserving the
closed `evidence_basis` vocabulary in `docs/api.md:45`. A cited record is
excluded from verified counts. Export additions leave
`export_schema_version: 3.0` unchanged (`pipeline/export.py:28,218`). No public
contract field widens, so this design requires no major version bump.

## Later reads and verification

Weekly rendered reads and price rereads fetch live content transiently,
compute its hash, and persist only URL/date/hash metadata for cite-only
hosts. Browser and HTTP caches cannot retain that content. Changed hashes
can request a new human citation assessment; an unchanged hash does not turn
a citation into an independently verified fact. No copied region or price
quotation appears in a manifest, diff, report, or extractor cache.

Red-first tests exercise the agreed boundaries from the ticket: CopyStore and
reader persistence, verifier and queue, premier snapshot admission and
round-trip, export/rank/decide propagation, and model/decide rendering.
Existing tests continue to cover ordinary hosts and independent verification.
Validation includes the site build and zero-finding surface lint, web build
and tests if touched, all three generators, and the complete pytest suite
under `/tmp/modelspec-fullsuite.lock`. All fetch tests use local fixtures;
there are no paid-provider calls or production switch changes.
