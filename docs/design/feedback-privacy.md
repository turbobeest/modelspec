# Feedback: privacy design and the wording for Jamie (MODEL-221)

*Written 2026-09-29. **Built, storage off.** `FEEDBACK_ENABLED` ships `"false"`
and no `FEEDBACK` namespace is bound. Turning storage on needs Jamie's approval
of this design and adoption of the privacy statement wording in
[section 7](#7-the-privacy-statement-wording-for-jamie) first.
`tests/test_legal.py::test_feedback_storage_is_unreachable_until_the_statement_covers_it`
fails CI if the flag is turned on or the namespace is bound while the statement
does not disclose the store.*

People and agents can tell ModelSpec whether an answer was reliable,
unreliable, trustworthy, untrustworthy or confusing. The endpoint is
[`feedback-api.md`](../feedback-api.md). This document says what is received,
what would be kept, and why each choice was made. It follows the outcome-upload
design ([`outcome-upload.md`](outcome-upload.md)) where the two meet.

## 1. What is received

`POST https://api.modelspec.dev/v1/feedback`, no key:

| field | required | limit | why it exists |
|---|---|---|---|
| `rating` | yes | one of five | the signal itself |
| `client` | yes | `agent`, `cli`, `mcp`, `page` | to tell agent from human feedback in the digest; self-reported |
| `decision_id` | no | `dec_` + 8–64 alphanumerics | to reproduce the answer being rated |
| `note` | no | 1000 characters | what went wrong, in the sender's words |
| `trying_to_decide` | no | 300 characters | the task, so a cluster can be read |
| `page` | no | a site path, query and fragment dropped | which page, for page feedback |
| `template` | no | a template id | which template, for the digest |

Anything else is refused (`400`), not ignored, so a client that sends an email
field or a prompt field learns that it should not. The body is capped at 4096
bytes. The Worker reads no `Authorization` header, no `X-API-Key` and no
`User-Agent` on this path; `tests/test_feedback.py` reads the handler's source
and fails if it starts to.

## 2. What would be kept, when storage is on

One KV value per piece of feedback, in its own namespace `FEEDBACK`, holding
exactly `feedback_service.STORED_FIELDS`:

`received_on` (the UTC **day**, never the time), `rating`, `client`,
`decision_id`, `page`, `template`, `note`, `trying_to_decide`, and `redacted`
(which kinds of text the scrubber replaced).

- **No address, key, user agent, origin or time of day.** The record's name is
  `feedback/v1/record/<day>/<sha256 of the receipt>`: a day and a hash.
- **Free text is scrubbed before it is stored.** What looks like an email
  address, a phone number, an IP address, a credential (known vendor key
  prefixes, ModelSpec `live_`/`test_` keys, bearer tokens, long mixed
  letter-and-digit runs) or a URL query is replaced by a placeholder, and the
  response says which kinds were replaced. This is **best effort**. It catches
  shapes, not meaning: a name, an employer or a pasted prompt is not caught.
  The form and the API say not to send those, and the field is optional.
- **Retention: 180 days**, enforced by Workers KV itself (`expirationTtl`), so
  no job has to remember to delete. *Jamie decides the number.* 180 matches the
  outcome-upload design.
- **Deletion on request, by receipt.** A recorded response carries a random
  128-bit receipt; the store keeps only its SHA-256. `DELETE /v1/feedback`
  with the receipt removes the record. A `decision_id` is not a deletion
  handle: it is deterministic, so anyone with the same spec could delete
  everyone's feedback about it.
- **No read endpoint.** Nothing on the API lists or returns feedback. The
  digest reads the namespace with the account's own Cloudflare credentials.

## 3. Abuse limits without identity

The tension: the ticket requires rate limits, and forbids keeping IP addresses
"beyond short-lived abuse limits".

- **Per minute (5 per address): isolate memory only.** Keyed by an HMAC of the
  address under a random salt generated when the isolate starts. Nothing is
  written. Lost when the isolate ends.
- **Per day (20 per address): a KV counter** named
  `feedback/v1/limit/day/<day>/<HMAC-SHA256(pepper, day|address)[:32]>`,
  expiring after two days. The pepper is a Worker secret
  (`FEEDBACK_LIMIT_PEPPER`) that is never in this repository. Without the
  pepper, an unkeyed hash of an IPv4 address could be reversed by trying all
  four billion; with it, a reader of the namespace cannot. Because the day is
  inside the MAC, one address's counters on two days cannot be linked.
- **Global (1000 a day)**, so a flood from many addresses is bounded, and so
  are KV writes.
- **Storage on without a namespace or without a pepper answers `503`**, never
  stores unkeyed.
- **The MCP server** reaches the Worker through a service binding, where no
  `CF-Connecting-IP` is set. It forwards its own caller's address in
  `x-modelspec-client-ip`, used by the Worker only when `CF-Connecting-IP` is
  absent. A caller on the public route cannot choose its bucket: Cloudflare
  sets `CF-Connecting-IP` on every request that reaches the route and
  overwrites any the client sent.
- **Browsers**: a request with an `Origin` other than modelspec.dev, its `www`
  host and the internal preview is refused (`403`), so another site cannot
  make its visitors post feedback. Clients with no `Origin` (agents, the CLI)
  are not browsers and are accepted.

What this cannot stop: a determined sender rotating addresses can send more,
up to the global cap. Poisoning is limited by the digest (section 5), which
reads clusters, not single reports, and by a person reading every draft.

## 4. While storage is off (as shipped)

A valid body is validated, rate-limited in memory and answered
`200 {"status": "not_recorded"}`. Nothing is written to any store; the KV
binding is not even present. The page and the CLI both say "nothing was kept".

**This still receives free text.** The statement in force (1.2) says "We do not
receive your prompts, because the API has no field for them." After this
ships, `note` is a free-text field that someone could paste a prompt into,
even though nothing keeps it. **Recommendation: adopt the 1.3 wording in
section 7 before or with the merge that deploys the endpoint**, the same way
1.2 disclosed the release-signal queue before it was enabled. If Jamie prefers
to wait, the alternative is to hold the merge. Both are Jamie's call; this
worker did not decide it.

Cloudflare's platform logs and Workers observability record request metadata
for this endpoint as for every other (the statement already says so). Our code
writes no log line with the body.

## 5. Closing the loop

- **Export** (`scripts/feedback/export.py`) and **digest**
  (`scripts/feedback/digest.py`) run on the operator's machine with the
  account's Cloudflare credentials. **Never in a GitHub workflow**: this
  repository is public and so are its workflow logs.
  `tests/test_feedback_digest.py` fails if a workflow names either script, and
  both refuse an output path inside the repository.
- The digest counts by rating, page and template for the week, and turns each
  cluster of at least two `unreliable`, `untrustworthy` or `confusing` reports
  that share a rating and a surface (template, else page, else client) into an
  issue draft with its decision IDs. A cluster already drafted becomes an
  update to that issue, never a second issue (`--ledger`).
- **Drafts quote scrubbed notes into Linear**, a private third-party tool.
  That is a disclosure the statement has to make (it does, in section 7).
  *Jamie decides* whether drafts quote notes or only paraphrase.
- "What you told us / what we changed" on `/feedback/` is written by hand from
  `docs/feedback/changes.yaml`: aggregate, paraphrased, never a quotation and
  never anything that identifies a sender.

## 6. Launch checklist (Jamie)

1. Approve this design, including 180 days, 5/min, 20/day, 1000/day, and
   whether drafts may quote notes.
2. Adopt the section 7 wording as privacy statement 1.3 (`docs/legal/privacy.md`,
   bump `IN_FORCE` in `tests/test_legal.py`).
3. Create the KV namespace and a pepper:
   ```bash
   cd api/worker
   npx wrangler kv namespace create FEEDBACK
   openssl rand -hex 32 | npx wrangler secret put FEEDBACK_LIMIT_PEPPER
   ```
4. In one PR: bind `FEEDBACK` in `wrangler.jsonc` with that id, set
   `FEEDBACK_ENABLED` to `"true"`, add `FEEDBACK` to the allowed set in
   `tests/test_legal.py::test_the_privacy_statement_matches_what_the_worker_binds`,
   and flip `test_feedback.py::test_the_shipped_configuration_is_off`. The legal
   test refuses this PR unless step 2 is merged.
5. Schedule the weekly export and digest on the operator's machine (not CI).

## 7. The privacy statement wording, for Jamie

Proposed as **version 1.3**. Each block names where it goes in
`docs/legal/privacy.md`. The wording describes storage as **not yet live**, so
it can be adopted before the flag is turned on; the one sentence to change on
the day storage goes live is marked.

**The short version** — replace its first sentence:

> We do not ask for your prompts: no field of the decision API takes one. The
> feedback endpoint has an optional free-text note, and asks you not to put a
> prompt, a key or personal details in it.

and add, after "The separate release-signal automation … processes them.":

> Feedback you choose to send about an answer is described below; storing it
> is not yet switched on.

**What a request contains** — add after the policy-check paragraph:

> `POST https://api.modelspec.dev/v1/feedback` accepts **feedback on an
> answer**: a `rating` (reliable, unreliable, trustworthy, untrustworthy or
> confusing), a `client` (agent, cli, mcp or page), and, optionally, the
> `decision_id` of the answer, a `note` of up to 1,000 characters, what you
> were `trying_to_decide` in up to 300 characters, the site `page` and the
> `template` you used (`api/worker/src/feedback_service.py`). No key is needed
> and none is read. Any other field is refused. Its body is capped at 4 KB.
> Before anything is kept, text that looks like an email address, a phone
> number, an IP address, a credential or a URL query is replaced by a
> placeholder; this catches the shape of such text, not its meaning, so please
> do not send a prompt, a key or personal details in the note.

**What we store** — change "The Worker binds two KV namespaces" to "three", and
add a section after *The release-signal queue*:

> ### The feedback store
>
> A third KV namespace, `FEEDBACK`, holds feedback on answers (MODEL-221). It
> is **not yet live**: `FEEDBACK_ENABLED` is `"false"` and the namespace is
> not bound, so feedback is checked, answered and not kept. *[On the day
> storage goes live, replace the previous sentence with: "It is live."]*
>
> When it is live, each piece of feedback is one record holding exactly: the
> day it was received (`received_on`, never the time), the `rating`, the
> `client`, and whichever of `decision_id`, `page`, `template`, `note` and
> `trying_to_decide` you sent, after the replacement described above, plus
> which kinds of text were replaced (`redacted`). It holds no IP address, no
> key, no user-agent, no origin and no time of day. Records are deleted
> automatically 180 days after they are received.
>
> A recorded response gives you a random receipt; we keep only its SHA-256
> hash. Sending the receipt to `DELETE /v1/feedback` deletes that record at
> once.
>
> To limit abuse without keeping addresses, the Worker counts feedback per
> address per day under a name derived from the address with a keyed hash
> (HMAC-SHA256 with a secret that is not published) and the day, so the count
> cannot be turned back into the address or linked across days. The count
> expires after two days. The per-minute limit is kept only in the running
> Worker's memory. The ModelSpec MCP server passes its caller's address to the
> Worker for these limits only.
>
> Once a week we read the feedback, count it by rating, page and template, and
> group repeated negative feedback into issues in our private issue tracker
> (Linear), with the decision IDs and short excerpts of the scrubbed notes.
> What we change because of feedback is listed, in our own words and never
> quoting anyone, at https://modelspec.dev/feedback/.

**The websites** — add a bullet:

> - The **Feedback** button, on every page, and the "Was this answer
>   reliable?" prompt on the decide page send what you enter to
>   `/v1/feedback` only when you press Send. They set no cookie and store
>   nothing in your browser.

**Your requests about your data** — add:

> Feedback is not linked to you. To delete a piece of feedback, send its
> receipt to `DELETE /v1/feedback`, or write to us with it.

**Changes** — add:

> - **1.3, 2026-MM-DD.** Disclosed the feedback endpoint and the feedback store
>   before storage is switched on: the fields it accepts, what a record holds,
>   the 180-day retention, deletion by receipt, the keyed per-day abuse
>   counter, and the weekly digest into our issue tracker (MODEL-221).

`tests/test_legal.py` checks, once `FEEDBACK` is disclosed, that the statement
names every stored field in backticks, which the wording above does.
