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
  "result": [ ... ]
}
```

`freshness` is on every answer, and `build_commit` identifies the exact export a
selection was made against. Record it. A recommendation whose basis cannot be
reconstructed later is not evidence, and DPF-22's honest-broker rule requires
that it can be.

## Exit codes

| code | meaning | what a caller should do |
| --- | --- | --- |
| 0 | an answer | use it |
| 1 | usage or runtime error | fix the call; the message is on stderr |
| 2 | nothing matched the constraints | a real answer — loosen a constraint |
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
