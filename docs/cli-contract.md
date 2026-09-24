# The ModelSpec CLI contract

The offline commands are an interface other programs call — dpf's ticket author
first among them. This is what they can rely on.

## The interface

```
modelspec snapshot fetch [--origin URL] [--api-key KEY]
                                          download the published export (the only networked command)
modelspec snapshot status [--json]        what is cached, how old, which build
modelspec offline rank <use-case> [...]   rank models for a use case
modelspec offline fit [<hardware-id>]     what a given machine can run, or list the machines
modelspec offline class-fit [<task>]      which *class* of model a problem needs (MODEL-100)
```

`modelspec decide SPEC.yaml [--explain …] [--json]` is the decision engine's
command (MODEL-135). It speaks the **decision contract**, which is versioned on
its own (`contract_version`) and documented in
[`decision-contract.md`](decision-contract.md); nothing on this page applies to
it, and it changes nothing on this page.

Options on `rank`: `--limit/-n`, `--open-weights`, `--fits <hardware-id>`,
`--max-cost <dollars per million input tokens>`, `--price-sensitivity <0..1>`,
`--json`, `--require-fresh`, `--include-rehosts`.

`fit` also accepts `--limit/-n`, `--json`, `--require-fresh`,
`--include-rehosts`, `--host <id>`, `--host-ram <GB>` and `--include-offload`
(see "Hosts and offload" below). These options
are additive and do not change the meaning of the commands above. `--origin`
is an option on `snapshot fetch`; it defaults to `https://modelspec.dev`.
`--api-key` is an option on `snapshot fetch` too; it has no default and the
supported way to supply one is the `MODELSPEC_API_KEY` environment variable
(see "A keyed origin" below).

`class-fit` accepts a task description as its argument plus `--emits`,
`--consumes` (comma-separated), `--decides`, `--json` and `--require-fresh`.
It is a **new command under the existing envelope**: `schema_version` stays
`"1.0"`, because no field of any existing command's `result` widens.

### `class-fit`: which class, before which model (MODEL-100)

`rank` answers "which model?" once you have decided you want an LLM.
`class-fit` answers the question before that one, and it is the only command
that will tell you the catalogue has nothing for you.

`result.fit_status` is one of:

| value | meaning | exit |
| --- | --- | --- |
| `resolved` | exactly one class survives the caller's constraints | 0 |
| `partial` | **two or more survive, and they are deliberately not ordered.** ModelSpec holds no measurement that ranks one class against another, so it returns every survivor plus the question you must settle | 0 |
| `unavailable` | no class in the published taxonomy emits what was asked for | 2 |
| `refused` | the request cannot be read; `result.refusal.code` says why and what would have worked | 1 |

Two things a caller must not read into the answer. **The candidate list is
sorted by class id and carries no score** — there is no ordering hidden in it,
and `result.policy.orders_classes` is `false` beside every answer. And
`result.candidates[].catalogue.evidence_state` distinguishes `populated`,
`empty` (the catalogue holds no model of that class — a real answer) and
`unknown` (nobody supplied the counts). `empty` is not `unknown` and neither is
a recommendation against the class.

`result.composition` may name a pair of classes as a **sequence** rather than a
choice — "this one, then that one on its abstentions". That is not an
ordering: neither class is placed above the other, and no number is attached.

The whole rule, including the term list the matcher uses, is published keyless
at `https://modelspec.dev/api/rank/class-fit.json`, so a caller can run the
same match locally without calling anything.

## The JSON envelope

```json
{
  "schema_version": "1.0",
  "command": "rank",
  "freshness": {
    "fetched_at": "2026-09-09T20:53:00+00:00",
    "age_days": 0.0,
    "stale": false,
    "stale_after_days": 30,
    "origin": "https://modelspec.dev",
    "build_commit": "082e76591c545a0f...",
    "built_at": "2026-09-09T20:47:41+00:00"
  },
  "result": [ ... ],
  "ranking_status": "partial",
  "ranked_count": 122,
  "unranked_count": 1103
}
```

`freshness` is on every answer, and `build_commit` identifies the exact export a
selection was made against. Record it. A recommendation whose basis cannot be
reconstructed later is not evidence, and DPF-22's honest-broker rule requires
that it can be.

The stable envelope fields are `schema_version`, `command`, `freshness`, and
`result`. `freshness` contains `fetched_at`, `age_days`, `stale`,
`stale_after_days`, `origin`, `build_commit`, and `built_at`. `snapshot status
--json` uses the same envelope: its `result` contains `present`, `path`, and
`size_bytes` when a snapshot exists; for an absent snapshot, `freshness` is
`null` and `result` contains `present: false` and `message`.

`offline rank --json` keeps `result` as the ranked list promised by schema 1.0.
It adds `ranking_status`, `ranked_count`, and `unranked_count` at the envelope
level; the counts are before `--limit`, and `result` is still capped by it.
This is a compatible addition under schema version 1.0: fields are added to the
existing envelope and the type and shape of `result` do not change. The separate
export file `rankings.json` has schema version 2.0 because its profile value
changed from a list to a report; that version is not the CLI envelope version.

`ranking_status` is computed before `--limit` and is one of:

* `complete`: every candidate that passed the filters is rankable;
* `partial`: ranked candidates and insufficient-evidence candidates both exist;
* `unavailable`: candidates passed the filters, but none has enough evidence to
  receive a rank; or
* `empty`: no candidate passed the filters.

The CLI uses the status to avoid treating a partial shortlist as a no-match:
`complete` and `partial` exit 0; `unavailable` and `empty` exit 2. Thus an
empty ranked list with `ranking_status: unavailable` is distinguishable from an
empty catalogue match (`ranking_status: empty`) without changing the meaning of
the result list. `--limit 0` does not change the status or exit code.

### `unranked_candidates`: the models a ranking could not rank (MODEL-110)

`unranked_count` alone lets a stale shortlist look authoritative: a caller
asking for the best coding model never learns that a model released last week
exists and has no scores yet. Every rank answer therefore names them:

```json
"unranked_candidates": {
  "count": 848,
  "cap": 10,
  "models": [
    {"model_id": "anthropic/claude-opus-5-5", "display_name": "Claude Opus 5.5",
     "release_date": "2026-09-22", "reason": "no_scores",
     "missing_benchmarks": ["aider_polyglot", "arena_elo_coding", "…"]}
  ]
}
```

* **Who is named.** A model that passed every filter the request applied
  (`--open-weights`, `--fits`, `--max-cost`, rehosts), whose `model_type` or a
  subtype is one of the profile's `preferred_types`, and that is still
  unranked. The type test is what makes it "a candidate waiting for evidence"
  rather than "the rest of the catalogue": an embedding model with no coding
  scores is not a coding candidate. So `count` ≤ `unranked_count`, which is
  unchanged and still counts every unrankable model in the pool.
* **Order.** Newest `release_date` first; a model with no date, or a date that
  is not `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, sorts last; ties by `model_id`.
* **Bound.** At most `cap` (10) are named. `count` is never capped.
* **`reason`** is one of three, the ones the floors can actually tell apart:
  `no_scores` (no score on any benchmark the profile weighs),
  `below_count_floor` (fewer than `min_benchmark_count`) and
  `below_coverage_floor` (under `min_benchmark_coverage`). A model failing both
  floors is `below_count_floor`. Rehosts, type, hardware and price are
  *filters*, not reasons: a model they remove was never a candidate.
* **`missing_benchmarks`** are the profile's weighted benchmarks the model has
  no score for. `release_date` is the card's, verbatim, or `null`.

The block is always present, `{"count": 0, "cap": 10, "models": []}` when
there is nothing to name, on exit 0 and exit 2 alike. It is disclosure only:
it is computed in `pipeline.ranking.rank_report`, beside the ranking and from
the same scored rows, and nothing in `result` changes. The rank API, the MCP
`rank` tool and `rankings.json` carry the same block from the same function.

Without `--json`, `rank` prints it as one line under the table:

```
848 models are not ranked yet (not enough benchmark evidence), newest first: anthropic/claude-opus-5-5, openai/gpt-6-luna, …, and 838 more.
```

**Versioning.** A new, always-present field on the envelope and on each
`rankings.json` profile report, and a new `release_date` on each
`candidates.json` row. No existing field's range widens, so under MODEL-59
nothing bumps: the envelope stays `"1.0"`, `rankings.json` `"2.0"`,
`build.export_schema_version` `"3.0"`. A snapshot from before this field has no
`release_date`; its candidates are named, all undated, ordered by id.

When `--json` is supplied and a command fails before it can produce an answer,
it writes this machine-readable error object to stderr and writes no answer to
stdout:

```json
{
  "schema_version": "1.0",
  "command": "rank",
  "error": {"message": "..."}
}
```

The same `schema_version` rule applies to successful JSON output and JSON
errors. Without `--json`, failures use a human-readable `error:` line on
stderr. A missing snapshot from `snapshot status --json` is a status response
with exit 3 (and `freshness: null`), not a traceback.

## Exit codes

| code | meaning | what a caller should do |
| --- | --- | --- |
| 0 | an answer | use it |
| 1 | usage or runtime error | fix the call; the message is on stderr |
| 2 | no ranked answer: nothing matched the constraints (`empty`), or no matching candidate had enough evidence (`unavailable`) | inspect `ranking_status`; loosen a constraint or obtain more evidence |
| 3 | no snapshot | run `modelspec snapshot fetch` |
| 4 | stale snapshot and `--require-fresh` was given | fetch, or drop the flag |
| 5 | a keyed origin refused the credential (no key, unknown key, revoked key) | supply or replace the key; retrying the same one will not help |
| 6 | a keyed origin rate-limited the credential | wait for the window named on stderr, then retry |

**2 is not an error.** "Nothing in the catalogue fits your constraints" is a
truthful result, and conflating it with a failure makes a caller retry something
that will never succeed.

**5 and 6 belong to `snapshot fetch` against a keyed origin.** They are the
only codes MODEL-71 added, they are produced by no other command, and no
unkeyed origin produces them: against `https://modelspec.dev`, `snapshot fetch`
still exits 0 or 1 and nothing else. Every other exit code means exactly what
it meant before.

## What we promise

Within a major `schema_version`:

* Existing fields keep their names, types and meaning.
* Exit codes keep their meaning.
* New fields may be **added** to any object. Parse permissively.
* New commands and new options may appear.
* `freshness` is always present on a `--json` answer.

We may change, only with a major version bump:

* Removing or renaming a field, or changing its type or units.
* Changing what an exit code means.
* Changing the shape of `result`.

### Versioning rule (MODEL-59)

Any change that **widens** a contract field's range bumps the **major** version
of that contract. Widening means a client that handled every old value can now
receive one it does not handle. Examples:

* a number becoming nullable;
* a new enum value a client must handle;
* a field that can now be absent.

Snapshot data is versioned by `build.export_schema_version`; the CLI `--json`
envelope by `schema_version`. Purely additive changes (new optional fields, new
flags, new files) do not bump the major. The CLI already refuses a snapshot
whose export major differs from its own, so a widening fails cleanly with an
error instead of crashing a client that assumed the old range.

The MODEL-53 nullable `predicted_decode_tps` below predates this rule and was
shipped without a bump; that is the case the rule exists to prevent.

### The `decision-model` class, and two kinds of null (MODEL-97/98)

`build.export_schema_version` is **3.0**. One bump, two tickets, because
consumers should absorb one break rather than two (Jamie, 2026-09-20).

**What widened.** `model_type` gained `decision-model`:

> evaluates supplied state against caller-defined typed questions, returning
> calibrated choices, scores or probabilities; generates no text.

It is published in `/api/models/<id>.json`, `index.json`,
`/api/rank/candidates.json` and the graph nodes. A new enum value is the
textbook widening under the MODEL-59 rule above, so it bumps the major. (The
earlier non-token classes — `miscellaneous`, `time-series`, `vision-encoder`,
`text-encoder` — shipped without a bump. They predate the rule and are the
omission it exists to prevent; they are not a precedent.)

**What a pre-bump CLI does.** It refuses before reading a row:

```
error: export_schema_version 3.0 is incompatible with this CLI (expects 2.x)
```

Exit 1, or the documented `--json` error object; no traceback, and a cached
snapshot is never clobbered. A 2.x CLI therefore never sees a `decision-model`
row, never scores one and never mis-parses one. **Upgrade the CLI, then
`modelspec snapshot fetch`.** A 3.x CLI refuses a 2.0 snapshot the same way.

**The CLI `--json` envelope does not move.** `schema_version` stays `"1.0"`:
no envelope field carries `model_type`. `rank` and `fit` rows are unchanged,
as are the exit codes. `rankings.json` stays `"2.0"` and the policy export
stays `"1.0"`; they version different documents.

**Inapplicable is not unresearched.** A `null` has always meant "not yet
researched". For some fields on some classes there is nothing to research —
a model that emits no text has no `modalities.text.max_output_tokens` to find.
`/api/models/<id>.json` now carries a derived sibling block:

```json
"applicability": {
  "basis": "model_type",
  "model_type": "decision-model",
  "not_applicable": ["capabilities", "inference_performance.api_tps_output",
                     "modalities.text.max_output_tokens", "…"]
}
```

Each entry is a dotted path from the card root; a path naming a section means
every field beneath it. **This is additive, not a widening**: the `card` tree
is still the frontmatter verbatim, no field in it changes type, name, meaning
or range, and a consumer that ignores `applicability` reads exactly what it
read before. It would not have bumped the major on its own; it rides
`decision-model`'s bump.

| what you see | what it means | what to do |
| --- | --- | --- |
| `null`, path **not** in `not_applicable` | Nobody has researched it. | Treat as unknown. It is a real gap, and it can be closed. |
| `null`, path **in** `not_applicable` | This class of model cannot have it. | Do not render it as a gap, do not count it against the card, and do not ask for it. |

The block is **derived from `model_type`**, never written on a card, so it
cannot contradict the card it describes and cannot be lost in a YAML
round-trip. It says nothing at all for a card whose `model_type` is absent or
unrecognised: an unknown class is unknown, not empty. Architecture fields are
never listed — an undisclosed parameter count is *unknown*, not meaningless.
Reasoning: [`design/class-and-null-semantics.md`](design/class-and-null-semantics.md).

**Ranking is unchanged and stays safe.** A decision model carries no benchmark
scores, so it comes back `rank_status: "unranked"`, `unranked_reason:
"insufficient_benchmark_evidence"` and `score: null` — never a low score, and
never in `result`. No new `unranked_reason` value was added, deliberately:
that field rides in rows under envelope `schema_version "1.0"`, and widening
it would cost a second bump to say something a caller cannot act on. The
floors are untouched.

### Benchmark coverage gained `verified` rows without a bump

`models_covered` in `/api/benchmarks/<id>.json` used to list only the flat
`benchmarks.scores` dict on each card, so every row's `attribution` was
`unverified-legacy`. It now also lists each reviewed `benchmarks.evidence`
record, with `attribution: "verified"`. A record replaces the card's flat
score for the same benchmark, and a card with several records for one
benchmark gets one row per record. `models_covered` in `catalogue.json` counts
distinct models, not rows.

The new `attribution` value widens that field's range. Under the rule above it
would bump the major. `build.export_schema_version` stays **3.0** on the
MODEL-74 reasoning: the CLI snapshot files (`index`, `candidates`,
`profiles`, `hardware`, `hosts`) carry no coverage rows, and the CLI never
reads `/api/benchmarks/`, so a bump would make every 3.x CLI refuse new
snapshots with no consumer to protect.

Every row carries the same keys. A `verified` row fills `unit`, `date_type`,
`source_kind`, `model_id_as_evaluated`, `benchmark_version`, `configuration`
and `verified_at` from its record, and takes `as_of` and `source` from the
record's `evidence_date` and `source_url`. An `unverified-legacy` row has those
seven keys set to `null`, and its `as_of` and `source` are still the card's
one collection date and source list.

### Policy fields, and the one major bump they cost (MODEL-77)

### Graph Model property removed without a bump (MODEL-74)

Model nodes in `/api/graph/nodes.json` and the graph views no longer carry
`card_completeness` (renamed `applicable_field_coverage`, now an internal
`ModelCard` statistic only). `build.export_schema_version` stays **2.0**:
Jamie decided 2026-09-18 that this removal does not bump the export major.
The CLI snapshot files (`index`, `candidates`, `profiles`, `hardware`) never
carried the key, and the CLI does not read the graph views, so a bump would
have made every 2.x CLI refuse new snapshots with no consumer to protect.

`build.export_schema_version` is **2.0**. `/api/models/<id>.json` publishes a
card's frontmatter verbatim, so reshaping the policy fields reshapes that tree.
Two widenings ship as one bump because they are one decision:

* `licensing.commercial_use` was `true | false | null`. It is now a string:
  `allowed`, `restricted`, `prohibited`, `unspecified` or `withheld` — the same
  `UsePermission` its four siblings (`defense_use`, `government_use`,
  `medical_use`, `academic_use`) already used. A boolean could not say
  "allowed up to 700M monthly active users", which is the actual answer for the
  169 llama-community, gemma and deepseek cards in the catalogue.
* `availability.primary_provider.data_residency` was a list that defaulted to
  `[]` on every card, so "no residency guarantees" and "nobody has looked" were
  the same value. It is now `list | null`, beside
  `data_residency_disclosure` (`unresearched` | `published` | `withheld`).

Both are range-widening under the rule above, so under MODEL-59 each would bump
the major on its own. Doing them in one pass costs one bump instead of two.
A 1.x snapshot is refused by a 2.x CLI with the usual message, and a snapshot
carrying no `export_schema_version` at all is a pre-2.0 tree and is refused the
same way.

**How to treat `withheld` versus `unspecified`/`null`.** They are not
interchangeable and a consumer must not collapse them:

| value | what it means | what a caller should do |
| --- | --- | --- |
| `unspecified` (`commercial_use`), `unresearched` (`data_residency`) | Nobody has determined this. The catalogue is not asserting anything about the licence. | Treat as unknown. Do not infer permission or prohibition. Do not ask again: there is nothing to fetch. |
| `withheld` | The determination exists and is deliberately not published in this tree. | Treat as unknown **for the purposes of the public data**, but as *obtainable* — the answer exists and is not on this card. Never render it as "not researched". |
| `allowed` / `restricted` / `prohibited` | A determination, with its citation. | Use it, and carry the citation. For `restricted`, read `commercial_use_conditions` — the value alone is not actionable. |

#### The two senses of `withheld` (MODEL-79, decided 2026-09-17)

`withheld` means one thing in the contract and always has: **a determination
exists, and this card is not where it is.** It never means nobody looked. What
differs between the two fields is *what kind of thing* was determined, and a
consumer who assumes "withheld = a value is being held back for sale" will
misread most residency cards.

| field | what a `withheld` card is telling you |
| --- | --- |
| `licensing.commercial_use` | **Determined, not published to you.** A licence was identified, read and decided — allowed, restricted or prohibited. The value is held back; ask for it. |
| `availability.primary_provider.data_residency_disclosure` | **Determined — which may be that the provider publishes nothing.** Either a region list was read from the provider's own page, or the provider's documents were read and commit to no region at all. Both are findings, and both are held back; ask for it. |

So for residency, `withheld` answers "has anyone looked?" with *yes*, and
leaves "is there a region list to have?" open. That second question has a real
answer for every withheld platform, and it is sometimes "no — we read their
documents, and they name no processing location". A buyer who needs EU-only
inference is told something useful by that: not "we don't know", but "there is
nothing here to check your requirement against". Under the old shape, this
platform and one nobody had ever looked at were the same card.

**What is *not* withheld.** A platform recorded as unreachable — every
connection refused or timed out from the network the work was done on — stays
`unresearched`, because nobody successfully looked. Two of the fifty platforms
are in that state. `unresearched` is also what a local runtime carries
(`ollama`, `lm_studio`, …): a model on hardware you own has no region-shaped
answer at all, and `withheld` would advertise one that cannot exist.
`scripts/residency/platforms.py` holds that list and the reasoning;
`scripts/residency/report.py disclosure` prints what each of the fifty
publishes.

`withheld` exists because the alternative is a lie at scale. Once
determinations are made and held back, a public `commercial_use: null` would
assert "not yet researched" on roughly 1,300 cards where it is false, in the
one place this catalogue's reputation lives. The marker is carried **in the
value itself**, not in a companion "available elsewhere" flag, so that a
consumer reading only `commercial_use` cannot miss it.

**Sources are not optional.** A determination carries
`commercial_use_source` / `data_residency_source`: the document it was read
from (`kind`, `url`) and the day it was read (`read_on`, ISO), plus an optional
short `quote` of the operative clause. Licence terms are rewritten without
notice, so an undated reading is not evidence. A value without a source fails
card validation; a card that is `unspecified` or `withheld` carries no source
at all, so an empty answer can never look cited.

Eight cards carry `kind: legacy-import` with no URL and no date. Those are the
eight `commercial_use: true` values that existed before this shape, kept rather
than discarded and kept honest rather than dressed up — the same admission
`evidence_basis: unverified-legacy` makes about a benchmark score. A test
freezes that kind to exactly those eight cards.

**Not served yet.** These fields are on the cards and in
`/api/models/<id>.json`. The CLI `--json` envelope does not carry them, so its
`schema_version` stays `"1.0"`; `rank` and `fit` are unchanged. The
`policy-check` endpoint is MODEL-80.

### Two sources' data removed, without a bump (MODEL-117)

On 2026-09-24 every value from two sources whose terms do not permit this
project's use was removed from the catalogue, with the benchmarks they own.
`build.export_schema_version` stays **3.0**, `rankings.json` stays `"2.0"` and
the CLI envelope stays `"1.0"`, because no contract field's range widened:

* **Every removed value lived in a collection that was already variable.**
  Per-card `benchmarks.scores` maps and `benchmarks.evidence` lists,
  `benchmark_scores` and `verified_benchmarks` in `candidates.json`, the
  profile `benchmark_weights` and `benchmark_ranges` maps in `profiles.json`,
  `/api/benchmarks/<id>.json` files, `catalogue.json`'s `active_ids` and its
  `counts` map (keyed by the statuses present; `historical` was already
  absent), and the eligibility report's accepted results. A consumer that
  handled an empty or shorter collection before handles this one.
* **No field that was always present is now absent.** The card slot
  `sources.<name>_url` for the removed source stays, as `""`, the value every
  other card already had. Removing the slot itself would be a removal under the
  promise above and would need a bump; that is Jamie's call.
* **Nothing became nullable that was not.** `inference_performance.api_tps_output`
  (now `null` on the 139 cards whose value came from the removed source) and a
  benchmark page's `saturation.top_score` were already `null` on most cards and
  pages.
* **No enum gained a value.** The catalogue can now hold **zero** active
  benchmarks. `active` is still a disposition, and an empty active set is a
  state the eligibility gate always allowed: it fails closed.

### Deprecated: CLIs older than MODEL-53

CLIs older than #56 (MODEL-53, merge `1d8dd53`) are unsupported. They raise
`TypeError` in `offline fit` against snapshots with a null
`predicted_decode_tps`. Upgrade.

We make no promise about:

* The **ordering or content of results.** The catalogue changes daily — that is
  the point — and the ranking rules will be corrected as defects are found.
  Pin a snapshot if you need reproducibility.
* Human-readable output. Only `--json` is a contract.
* The graph commands (`stats`, `search`, `info`, `compare`, …). Those need a
  local FalkorDB and are for interactive exploration.

## Freshness, and why a stale answer still comes back

A snapshot older than 30 days is served anyway, with a warning on stderr. A
dated answer that says how dated it is beats no answer — the same continuity
rule the dpf library follows. `--require-fresh` inverts this for callers who
would rather fail.

## What the numbers are worth

Rankings are computed from the benchmark scores on the model cards. Each ranked
or unranked row reports `evidence_basis` for the inputs that contributed, not a
certification of the composite or of model quality. `_basis` in
`pipeline/ranking.py` emits one of:

* `none` — no usable weighted measurement contributed
* `unverified-legacy` — every contributing measurement is a legacy card value
* `mixed` — reviewed and legacy measurements both contribute
* `partial-verified` — every present measurement is reviewed, but the profile
  is incomplete
* `verified` — every positively weighted benchmark is present and reviewed

A live catalogue contains more than one of these. `verified` is not a quality
verdict and is not applied to incomplete evidence (see
`tests/test_ranking.py`). Older cards may still be `unverified-legacy`; that
label is no longer universal.

Hardware fit and predicted decode rates are **computed** from memory capacity
and bandwidth, not measured; no one has run these models on these devices.

Treat both as a shortlist to investigate, not a verdict. The interface says so
in every response so that a calling agent can pass the caveat on rather than
laundering it into confidence.

### `predicted_decode_tps` can be `null` (MODEL-53)

A model that fits in memory is not necessarily a model that decodes tokens.
Time-series forecasters, vision encoders (classification, segmentation,
detection), and text encoders (fill-mask, token classification) fit on a
device the same as any other set of weights, but there is no token being
decoded, so a tok/s figure would be invented. As of this change, `offline
fit`'s `predicted_decode_tps` (and the `fastest_predicted_decode_tps` behind
`--fits`) is `null` for these rows instead of an invented number.

This is a real widening of the field's range, not something the contract
already promised: `predicted_decode_tps` used to always be a number when the
row was present at all. We are making it anyway, without a major version
bump, because the field's **name and meaning stay exactly what they were** —
"the predicted decode speed for this model on this device" — and a
consumer that reads it as "a number, or absent/unknown" (the ordinary way to
treat a nullable numeric field) needs no code change. A consumer that instead
assumed every present row carries a real number will need to add a null
check; this note is that notice.

Rows with a `null` decode rate always sort after every row with a real rate,
never mixed in above a model that actually predicts a speed. The
human-readable form prints `n/a` for these rows, never a blank or a `0.0`.

Filtering `--fits <device>` still returns these models: whether the weights
fit is meaningful on its own. Only the speed is withheld.

## Rehosts (MODEL-54)

A card whose `lineage.base_model_relation` is `repackaged` re-hosts another
catalogue card's weights unchanged (a mirror such as `NousResearch/Llama-2-7b-hf`
of `meta-llama/Llama-2-7b-hf`). `lineage.base_model` names the canonical model
id. `candidates.json` rows carry an additive `rehost_of` field: the canonical id,
or `null`.

`rank` and `fit` leave rehosts out by default, and so do the precomputed
featured rankings in `rankings.json`, so one weight set has one id. Pass
`--include-rehosts` to keep them. A rehost stays reachable by id and on its own
page, and the canonical page lists it under Lineage.

Quantised copies (`quantized`) and finetunes have different weights and fit
differently, so they stay in every pool. They are related, not hidden.

## Hosts and offload (MODEL-26 phase B)

`offline fit <device> --host <id>` evaluates the device inside a host profile
(`/api/hosts.json`, from `hosts/*.yaml`; design in `docs/host-layer.md`).

* `--host <id>`: a host profile id. An unknown id, or a snapshot with no host
  profiles (an export from before this change), exits 1.
* `--host-ram <GB>`: the RAM on this machine, before the reserve. Default: the
  profile's `system_memory.capacity_max_gb`. A fixed 8 GB OS reserve is always
  subtracted. Requires `--host`.
* `--include-offload`: append an **offload tier**, which lists models that fit
  only by spilling weights to host RAM. Requires `--host`; without it, exit 1.
  A unified host (`unified: true`, for example Apple silicon) never has an
  offload tier, because its RAM already is the accelerator's memory.

With `--host`, every fit row gains four fields:

| field | values |
| --- | --- |
| `fit_state` | `accelerator` or `offload` (`does_not_fit` rows are never emitted) |
| `offload_fraction` | `0.0` for `accelerator`; `(W + A - C_acc) / W` in (0, 1] for `offload` |
| `host_id` | the `--host` id |
| `predicted_decode_tps_basis` | `accelerator-roofline`, `offload-roofline`, or `null` when `predicted_decode_tps` is null |

Offload rows also carry `quantization`, the smallest quant that fits, which
spills the least. Their `predicted_decode_tps` is
`0.70 / ((1-f)*P/B_acc + f*P/B_host)` and is `null` for models that do not
decode tokens. Candidates in `candidates.json` gain `total_parameters` and
`active_parameters`, which the CLI needs to size those models.

**Ordering.** Accelerator rows come first, in the existing order. Offload rows
follow as a separate tier, sorted by their own predicted speed. The two tiers
are never interleaved or ranked against each other. `--limit` applies to each
tier separately. The exit code is 2 only when both tiers are empty.

**Without `--host`, the output is byte-identical** to the CLI before this
change (`tests/test_host_offload.py::test_fit_without_host_is_byte_identical`).

**Versioning-rule check.** No existing field's range widens. Every new field
and value appears only when `--host` is given, which is a new flag. `hosts.json`
and the candidate parameter counts are new, optional data. So
`schema_version` stays `"1.0"` and `build.export_schema_version` stays `"1.0"`.
`fit_state` is a new field, not a widening of `fits`. A later change that emits
a new `fit_state` value (for example `cpu_only`) does widen it and needs a major
bump under the rule above.

## A keyed origin (MODEL-71)

The published export on `https://modelspec.dev` is delayed. A snapshot of it is
older than `stale_after_days` the moment it is fetched, so a caller that needs
a current answer would see `"stale": true` on day zero and could never pass
`--require-fresh`. `snapshot fetch` can therefore present a credential to an
origin that serves the current tree to keys entitled to it.

**Nothing else changes.** Same commands, same envelope, same `schema_version`,
same exit codes on every path that already existed. The one difference a keyed
fetch makes is that `freshness.fetched_at` is now and `freshness.stale` is
false. `rank` and `fit` return exactly what they returned before — no new
field, no enrichment, no marker saying a key was used
(`tests/test_cli_keyed_origin.py::test_the_rank_and_fit_envelopes_are_unchanged`).

### Supplying the key

```bash
export MODELSPEC_API_KEY='…'        # supported
modelspec snapshot fetch --origin https://api.modelspec.dev

modelspec snapshot fetch --api-key '…'   # works, and warns
```

**Use the environment variable.** `docs/agent-commerce-assessment.md` §4 is the
reason: a credential in `argv` is visible in process listings to every user on
the machine, is written to shell history, and is captured by anything that logs
a command line — CI transcripts and agent traces included. `--api-key` exists
because some callers cannot set an environment variable, and using it prints a
warning to stderr saying so. The environment is read when `--api-key` is absent;
the flag wins when it is given, because a caller who typed a key meant that key.

The key is sent as `Authorization: Bearer <key>`, which is what
[`api-access.md`](api-access.md) documents and, not incidentally, the one header
an HTTP client drops when a redirect crosses to another host. **A key is never
put in a URL**, never written into the cached snapshot, and never printed: it
is held in a `Credential` whose `repr` and `str` emit a 12-character `key_id`
(the SHA-256 prefix the origin logs) instead of the secret, and every message
`snapshot fetch` writes is passed through a redaction backstop on the way out.
`test_the_key_appears_in_no_output_no_error_and_no_cached_file` drives every
branch of the command with a known key and searches stdout, stderr, the
origin's access log and the cached snapshot for it.

### The four failures

| What happened | Exit | On stderr |
| --- | --- | --- |
| No key presented, and the origin requires one (`401 missing_api_key`) | 5 | how to set `MODELSPEC_API_KEY`, and the origin's own message |
| The key is unknown or revoked (`401 invalid_api_key`, `403 key_revoked`) | 5 | which source supplied it, its `key_id`, and the origin's message |
| A window is spent (`429 rate_limited`) | 6 | the retry delay, and the origin's message naming the limit and its reset |
| The origin did not answer (DNS, TLS, connection, timeout) | 1 | `error: could not fetch the snapshot: could not reach <origin><route>: …` |

The unreachable case keeps exit 1 and its original sentence on purpose: that
path existed before this change and callers already branch on it. The refusals
relay the origin's own `error.message` rather than paraphrasing it, because the
service already says the useful part — where to get a key, when the window
resets. None of the four prints a traceback, and none of them replaces a
snapshot that is already cached.

### Versioning

Additive under the MODEL-59 rule, so no major bump. One new option, one new
environment variable, and two exit codes that no pre-existing call can receive
— the same reasoning as the MODEL-26 host fields, which are emitted only when
`--host` is given. No existing field's range widens, `schema_version` stays
`"1.0"`, and `build.export_schema_version` is untouched.

## The live rank API (MODEL-68)

`POST https://api.modelspec.dev/v1/rank` answers the same question this CLI
answers, from the current export rather than from a local snapshot. Its rows are
**the same rows**: the endpoint runs `pipeline/ranking.py`, vendored into the
Worker verbatim, and `tests/test_rank_worker.py` holds it to bytes identical to
`modelspec offline rank --json` for the same input against the same build.

Nothing in this document changes. The CLI keeps working with no account, no
credential and no network after the first `snapshot fetch`, which is the point of
it. The endpoint is for callers that want today's export without carrying one.

Its status codes map onto the exit codes above:

| Endpoint | CLI |
|---|---|
| `200` a ranking | `0` |
| `400` refused (bad request, unknown use case, unknown device) | `1` |
| `422` no match — carries the eliminating constraint, never a bare empty list | `2` |
| `502` the published export could not be read | — |

Full contract: [`rank-api.md`](rank-api.md).

## The live policy-check API (MODEL-80)

`POST https://api.modelspec.dev/v1/policy-check` takes a policy document —
required licence terms, permitted origin countries, required processing regions,
a commercial-use requirement — and returns, per model **and per platform**, one
of three verdicts.

There is no CLI surface for it yet (`REV-6`), so nothing in the sections above
changes. It is documented here because its three-state answer is the same
discipline this contract already states for policy fields, and a consumer of one
should be able to find the other.

**`undetermined` is a verdict, not a missing `pass`.** In the response schema it
is structurally distinct: every check carries exactly one of `satisfied`,
`violated` or `undetermined` as a sibling key, and every row exactly one of
`passed`, `failed`, `undetermined`. A consumer written against `satisfied` finds
no `satisfied` key on an undetermined check, so the mistake surfaces in the
caller's code rather than in their deployment. `require_no_undetermined: true`
turns any undetermined row into a documented `422`.

That follows directly from [the policy-field rules above](#policy-fields-and-the-one-major-bump-they-cost-model-77):
`unspecified`, `withheld` and `unresearched` describe a file's contents, not the
world, and none of them is ever read as a permission. Nor is a value whose only
citation is `legacy-import`.

Its status codes map onto the exit codes above:

| Endpoint | CLI |
|---|---|
| `200` verdicts | `0` |
| `400` refused (malformed body, empty policy, unknown model or platform) | `1` |
| `422` the caller demanded no undetermined rows and there are some | `2` |
| `502` the published policy export could not be read | — |
| `503` entitled to the determinations, and they could not be read | — |

The endpoint is free; the determinations it reads are not, and the difference is
labelled on every response (`determinations.included`,
`undetermined_for_lack_of_entitlement`) rather than degraded silently.

Full contract: [`policy-check-api.md`](policy-check-api.md).
