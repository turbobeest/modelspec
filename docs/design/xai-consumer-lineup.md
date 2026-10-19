# xAI current subscription lineup

MODEL-408, revised by MODEL-408-cite on 2026-10-19. This design supersedes
the retained-source verification design at `581833f1`. Code PR #822 depends
on cite-only mechanism PR #840 merging first. Both it and private data PR #96
remain drafts for review.

## Citation policy

The current xAI lineup is cited, not machine-verified. The registered policy
covers `x.ai` and `docs.x.ai`, including subdomains and observed redirects.
Use the shared [retention guard](cite-only-sources.md) for every persisted
source artifact. Retain only the source URL, original fetch timestamp and
SHA-256 hash. Do not keep raw pages, normalized text, quotations, screenshots,
DOM dumps or rendered HTML.

The historical `MODEL-367/capture.mjs` command used by the original curation
is retired. It refuses before importing a browser or creating output; its
old instructions must not be reused.

The pricing citation refers to `https://x.ai/pricing`, fetched on 2026-10-18,
with SHA-256 `bdf1848f0fe27294ccc7497f2016650cb32406e7252ccf191ab5d3b21d16ab21`.
The exact fetch timestamp is preserved in private citation metadata and fact
source references. It is not a verification date. No new live retrieval is
needed for this migration.

## Identities and values

Preserve the seven distinct subscription offerings and every curated value.

| Plan | Canonical ID | Exact monthly USD price |
| --- | --- | --- |
| Free | `xai/subscription/free` | 0 |
| Plus | `xai/subscription/plus` | 8 |
| Premium | `xai/subscription/premium` | 30 |
| Super | `xai/subscription/super` | 100 |
| Ultra | `xai/subscription/ultra` | 200 |
| Teams | `xai/subscription/teams` | Unknown |
| Enterprise | `xai/subscription/enterprise` | Unknown |

The first five billing periods remain monthly. Teams' starting per-seat amount
and Enterprise's custom price do not establish exact scalar prices. Their
price and billing-period facts stay unknown. All seven model-coverage and
usage-allowance facts stay unknown. Product names cannot establish canonical
model IDs or a token quota.

The seven existing Build/Bot inclusion values stay unchanged. Free's limited
Build access remains distinct from inclusion. These values do not establish
raw API entitlement or change subscription surfaces or own-software routing.
Teams, Enterprise and the older Business offering remain separate identities.
Lite and Heavy retain their IDs and unknown or quarantined facts. No missing
column establishes retirement, a successor, availability or an alias.

## Reading and assurance

`read_matrix()` remains a pure in-memory parser. Its hashes, exact DOM paths,
header labels and glyph checks preserve the original value extraction and
reject unapproved or changed templates. Synthetic tests cover the five
prices, five billing periods, seven product values and all six mutation
cases. No provider page fixture is committed.

Production `verify()` applies #840's host policy before reading retained
regions or dispatching the exact reader. It returns `cited`, with no
`Verification`. A parser's ability to extract a value does not establish
machine verification. Parser controls isolate that logic with synthetic
fixtures; separate integration tests keep the production policy enabled.

Snapshots derive citation assurance from registered sources and valid source
references. The 17 known new facts remain admitted with `verification: null`
and `citation.status: cited`. Unknown facts remain absent from admitted values.
The existing mismatch/unreachable quarantine rules still apply. Public
consumers display "Cited, not machine-verified" through #840. No contract range,
ranking floor or production switch changes.

## Migration and validation

Private data PR #96 removes its retained xAI artifacts and obsolete capture,
replay and filing helpers. It preserves URL/hash/fetch-time metadata and the
35 new facts' values and states. Its old machine-verification records are
removed; completed queue events record citation assurance. Older history
outside this PR remains the separate MODEL-409 migration.

Do not advance `.engine-pin` during this work. The orchestrator must update it
to a merged engine SHA containing both #840 and #822 after both merge.

Validation covers offline HTTP retention, production verifier interception,
in-memory extraction and snapshot citation round-trip, private export signing
and premier completeness, generator checks, the site build and zero-finding
surface lint, web build/tests, and the full engine suite under the shared lock.
Commands and results are recorded in
[MODEL-408-cite evidence](../evidence/g2-ios/MODEL-408-cite-fix.md).
