# Verification log

Written by `decision/verify.py` (MODEL-140). See
[`docs/decision-verification.md`](../docs/decision-verification.md).

- `log.jsonl`: append-only, one `decision.model.Verification` per line. The
  latest outcome per target and checked value wins (latest `date`; on a tie,
  the later line). `decision/snapshot.py` reads this file as the log.
- `queue/events.jsonl`: the work queue (claims filed by collectors, re-queues
  from source change detection, checks done). Not read by the snapshot.

Never edit or delete a line. A correction is a new line.

## Source registry format

`registry/sources.yaml` is the one source-registry format. It has
`schema_version: 1` and a `sources` list. Each source has `id`, an HTTP(S)
`url`, and may set `fetch` (`http`, `conditional_http`, or `rendered`),
`normaliser`, and `cited_regions`. The defaults are `conditional_http`,
`html-default`, and an empty list. Each cited region has an `id` and a
`locator` with `kind` and `value`. Supported locator kinds are `css`,
`heading_anchor`, `heading`, `table`, and `page`. Registration rejects `xpath`
because the normaliser cannot resolve it. Verification and snapshot collection
both call `decision.sources.load_sources`.
