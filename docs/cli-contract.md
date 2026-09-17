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
```

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

### Policy fields, and the one major bump they cost (MODEL-77)

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
