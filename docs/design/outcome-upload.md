# Outcome upload: design only (MODEL-211)

*Design, written 2026-09-29. **Not built, not enabled.** Building it needs
Jamie's approval and a change to the published privacy statement
([`../legal/privacy.md`](../legal/privacy.md)) before any code ships.*

MODEL-211 built local outcome records: `modelspec outcome record` appends to
`~/.modelspec/outcomes.jsonl` after an explicit opt-in, and nothing leaves the
machine ([`../outcome-privacy.md`](../outcome-privacy.md)). ADR 0004 step 1
also needs those records to reach ModelSpec, because an outcome ModelSpec never
sees cannot become first-party evidence. REV-9 requires that path to be
separately consented and documented. This document is that path, with every
decision that needs Jamie marked as such.

Outcome data is the "never publish" row in the business data policy. Uploaded
records are raw material for aggregates. They are never published row by row,
never exported from the store, and never shown to another customer.

## 1. Consent

Uploading needs its own consent, separate from recording:

```bash
modelspec outcome upload enable     # prints what is sent, where, how long it is kept
modelspec outcome upload            # sends records not yet sent; never runs by itself
modelspec outcome upload disable    # stops; with --delete-remote, asks the store to delete
```

- Turning recording on never turns upload on. The two consents are stored in
  separate files with separate version numbers (`outcomes-upload-consent.json`,
  `{"upload_consent_version": 1}`).
- An upload happens only when a person or their agent runs
  `modelspec outcome upload`. No other command uploads, and nothing uploads in
  the background. A future opt-in for automatic upload after each `record`
  would be a third consent with its own text.
- Before sending anything, `upload` prints the number of records and the exact
  JSON body, and needs `--yes` to proceed without a terminal.
- The consent text names the retention period and the privacy statement version
  it relies on. If the statement changes, the consent version changes, and
  upload stops until the person consents again.

## 2. Schema: the same record, minus what the store does not need

The upload body is a list of records validated against `OutcomeRecord`
(`cli/modelspec/outcome.py`) on the client, and again against a copy of that
schema in the Worker with `extra="forbid"`. The Worker refuses the whole batch if
any record fails. It does not drop the bad fields and keep the rest, because a
batch that fails is a client that is sending something it should not.

Three fields change on the way out:

| field | locally | uploaded | why |
| --- | --- | --- | --- |
| `recorded_at` | to the minute | to the **day** (`YYYY-MM-DD`) | a minute plus a decision ID can be joined to a caller's own logs |
| `cost_usd` | 3 significant figures | 2 significant figures | an exact cost can fingerprint one account's pricing |
| `latency_ms` | 3 significant figures | 2 significant figures | the same, for latency |

Nothing is added on the way out. There is no install ID, machine ID, user ID,
IP-derived field or API key ID in the body. See section 4 for how the Worker
limits abuse without them.

A batch is capped at 500 records and 256 KB. The request carries no field
besides `records`.

## 3. Retention

- **Raw records: 180 days, then deleted.** That is long enough to detect a
  silent model change (a shift in success rate with no announced change) across
  two model release cycles, and short enough that the store never becomes an
  archive of any one caller's work. *Jamie decides the number.*
- **Aggregates: kept.** These are counts and rates per
  `(adopted_model, adopted_offering, task_kind, result)` and per week. An
  aggregate is computed only for a cell with at least 20 records from at least
  5 distinct upload batches. A cell below that threshold is not computed, not
  stored and not published. The thresholds are *Jamie's call*.
- **Deletion on request.** A decision ID cannot be the deletion handle. It is
  deterministic, so anyone with a public or template spec could delete every
  caller's records for it. Instead, each accepted batch gets a random 128-bit
  receipt. The Worker stores the receipt's SHA-256 beside the batch's rows, and
  the client keeps the receipts locally (`outcomes-uploaded.jsonl`, receipts
  only). `upload disable --delete-remote` sends the receipts, and the Worker
  deletes those batches.

## 4. Anonymisation, and what it cannot do

What is removed:

- **The caller.** The Worker does not store the request's IP, `Authorization`
  header, key hash or Cloudflare request metadata alongside records. Cloudflare's
  own platform logs still exist under Cloudflare's retention, and the privacy
  statement already says so.
- **Timing.** Day precision (section 2), and records are written in shuffled
  order so that storage order does not reveal upload order.
- **Rare cells.** The minimum-count rule (section 3) applies before anything
  derived from the store is published or used as evidence.

What this cannot remove, stated plainly so that nobody overclaims:

- `decision_id` and `spec_hash` are deterministic. Anyone who holds the same spec
  and snapshot can compute them, so two callers with identical specs produce
  identical IDs. The store can therefore tell "these records came from the same
  spec", but not who wrote it. A caller who wants even that hidden should not
  upload.
- **The spec hash is a guessable fingerprint.** It is unsalted SHA-256 over the
  canonical spec (`decision/contract.py`), and a spec can carry an `estate`:
  the providers, plans and devices the caller holds. Whoever holds the store
  can confirm a guessed spec, including a guessed estate, by hashing it.
  Knowing which providers someone holds is close to REV-9's "whether keys are
  present". Before this is built, Jamie decides between two options. One is to
  upload no `spec_hash` and a peppered `decision_id`, which loses the join to
  published specs. The other is to upload both and state this risk in the
  consent text and the privacy statement. The recommendation is the first.
  Deletion by receipt (section 3) does not depend on the ID, so peppering it
  costs nothing there.
- A caller with a very unusual `(model, offering, task_kind)` combination may
  be the only contributor to a cell. The minimum-count rule keeps that cell out
  of anything published, but the raw rows exist for up to 180 days.

**Abuse without identity.** The store keeps no caller identity, so rate limits
and poisoning defence cannot use one:

- Rate-limit by IP in memory at the edge, and never persist the IP.
- Accept an upload only for a `decision_id` whose `snapshot` is one ModelSpec
  published, and whose `spec_hash` matches a decision the Worker can recompute
  or has seen. *Open question for Jamie:* this needs the Worker to keep a set of
  issued decision IDs. The Worker keeps no such set today, and adding one is a
  second store.
- Treat outcome evidence as a labelled first-party source (ADR 0004) with its
  sample size published beside it, so one poisoned batch moves a published
  number by at most its share of that sample.

## 5. The Worker store

A new binding on the keyed Worker (`api.modelspec.dev`), beside `ACCESS` and
`DETERMINATIONS`:

- **Endpoint:** `POST /v1/outcomes`, with the body `{"records": [...]}`.
  It answers with the batch's receipt. `DELETE /v1/outcomes` takes
  `{"receipts": [...]}`. There is no GET, so
  the store cannot be read over the API.
- **Storage:** a D1 database, `OUTCOMES`, not KV, because retention deletion
  and aggregation are range queries over dates. It has one table whose columns
  are exactly the uploaded fields, plus nothing. A nightly Cron Trigger deletes
  rows older than the retention period and recomputes the thresholded
  aggregates into a second table.
- **Serving path:** unchanged. The static export stays free of D1 and R2
  (MODEL-2's rule binds that path). The outcome store is on the keyed Worker,
  the same way the `DETERMINATIONS` KV store is, and nothing in it is exported
  to `modelspec.dev`.
- **Flag:** `OUTCOME_UPLOAD_ENABLED` in `api/worker/wrangler.jsonc`, shipping
  `"false"`, like `ACCESS_ENFORCED`, `BILLING_ENABLED` and `X402_ENABLED`.
  Turning it on is Jamie's call.
- **Access:** only the aggregation job reads the raw table. No admin endpoint
  lists records.

## 6. What must change before it ships

1. Jamie approves this design, including the retention and threshold numbers.
2. The privacy statement's "Not yet live, Outcome logging" entry is rewritten
   to describe this store, and a new version is adopted, **before** the flag is
   turned on. That statement currently says the service will record "the
   profile, the recommendation and the outcome". This design records less than
   that: no profile, only its hash. The new text should say so.
3. `tests/test_legal.py` gains a check that the statement's list of uploaded
   fields matches the upload schema, the same way it already guards the
   neutrality commitment.

## Not in this design

- Uploading anything besides outcome records, such as specs, decisions or logs.
- Harness, effort or failure-mode fields (decision-engine design §9). Adding any
  of them is a new record version and a new local consent first.
- Any view of another caller's outcomes.
