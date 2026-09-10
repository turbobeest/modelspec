# The ModelSpec CLI contract

The offline commands are an interface other programs call — dpf's ticket author
first among them. This is what they can rely on.

## The interface

```
modelspec snapshot fetch [--origin URL]   download the published export (the only networked command)
modelspec snapshot status [--json]        what is cached, how old, which build
modelspec offline rank <use-case> [...]   rank models for a use case
modelspec offline fit [<hardware-id>]     what a given machine can run, or list the machines
```

Options on `rank`: `--limit/-n`, `--open-weights`, `--fits <hardware-id>`,
`--max-cost <dollars per million input tokens>`, `--price-sensitivity <0..1>`,
`--json`, `--require-fresh`.

`fit` also accepts `--limit/-n`, `--json`, and `--require-fresh`. These options
are additive and do not change the meaning of the commands above. `--origin`
is an option on `snapshot fetch`; it defaults to `https://modelspec.dev`.

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

**2 is not an error.** "Nothing in the catalogue fits your constraints" is a
truthful result, and conflating it with a failure makes a caller retry something
that will never succeed.

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

Rankings are computed from the benchmark scores on the model cards. Those carry
one collection date per card and a source list rather than a source per score,
so every result reports `evidence_basis: unverified-legacy`. Hardware fit and
predicted decode rates are **computed** from memory capacity and bandwidth, not
measured; no one has run these models on these devices.

Treat both as a shortlist to investigate, not a verdict. The interface says so
in every response so that a calling agent can pass the caveat on rather than
laundering it into confidence.
