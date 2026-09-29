# The feedback API (MODEL-221)

`POST https://api.modelspec.dev/v1/feedback` tells ModelSpec what you thought of
an answer or a page. It takes one rating from a fixed set, optionally tied to
the `decision_id` of a decision, and optional free text. **No key is needed.**

- Ratings: `reliable`, `unreliable`, `trustworthy`, `untrustworthy`, `confusing`.
- Clients: `agent`, `cli`, `mcp`, `page`.
- Request schema (JSON Schema 2020-12): <https://modelspec.dev/api/feedback/v1.schema.json>
- OpenAPI: operation `feedback` in <https://modelspec.dev/openapi.yaml>
- CLI: `modelspec feedback [DECISION_ID] --rating <rating> [--note …]`
- MCP: the `feedback` tool on `https://api.modelspec.dev/mcp`
- Every decision carries a `feedback` block naming this endpoint (decision
  contract 2.10).
- Source: [`api/worker/src/feedback_service.py`](../api/worker/src/feedback_service.py).
  Privacy design: [`design/feedback-privacy.md`](design/feedback-privacy.md).

## Storage is off

Storage ships **off** (`FEEDBACK_ENABLED` in `api/worker/wrangler.jsonc`). While
it is off, a valid request is answered `200` with `"status": "not_recorded"`,
and nothing is written anywhere. It is switched on only after the privacy
statement covers it. When it is on, a valid request is answered `202` with
`"status": "recorded"` and a `receipt`.

The response always says which one happened. Do not treat `200` as recorded.

## When to send it

Send it after you act on a ModelSpec answer and learn whether it held up:

- `reliable` / `unreliable` — did the answer hold when you used it?
- `trustworthy` / `untrustworthy` — did the evidence and sources look sound?
- `confusing` — you could not tell what the answer meant or what to do next.

Send one rating per answer. Put the `decision_id` in when the feedback is about
a decision, so the report can be traced to the exact spec and snapshot.

## Request

```jsonc
POST /v1/feedback
content-type: application/json

{
  "rating": "unreliable",             // required, one of the five
  "client": "agent",                  // required: agent | cli | mcp | page
  "decision_id": "dec_3f9a1c2b7d4e",  // optional
  "note": "The top pick has no pricing for my region.",  // optional, ≤ 1000 chars
  "trying_to_decide": "a coding model under $1 a task",  // optional, ≤ 300 chars
  "page": "/decide/",                 // optional site path; query and fragment dropped
  "template": "coding"                // optional decision template id
}
```

Unknown fields are refused, not ignored. **Never put a prompt, a key, or
anything that identifies a person in `note` or `trying_to_decide`.** The Worker
replaces what looks like an email address, a phone number, an IP address, a
credential or a URL query with a placeholder before anything is kept, and says
which kinds it replaced in `redacted`. That is a safety net, not permission.

The body is capped at 4096 bytes.

## Response

```jsonc
// storage off (as shipped)
{ "schema_version": "1.0", "endpoint": "feedback", "status": "not_recorded",
  "recorded": false, "receipt": null, "retention_days": null, "redacted": [],
  "message": "Thank you. Feedback storage is switched off …",
  "privacy": "https://modelspec.dev/legal/privacy/", "service_commit": "…" }

// storage on
{ "schema_version": "1.0", "endpoint": "feedback", "status": "recorded",
  "recorded": true, "receipt": "fbr_20260929_<32 hex>", "retention_days": 180,
  "redacted": ["email"], "message": "…", "privacy": "…", "service_commit": "…" }
```

## Deleting what you sent

The receipt is the only handle. The store keeps its SHA-256, never the receipt.

```bash
curl -X DELETE https://api.modelspec.dev/v1/feedback \
  -H 'content-type: application/json' -d '{"receipt": "fbr_20260929_…"}'
```

A `decision_id` cannot be a deletion handle: it is deterministic, so anyone
holding the same spec could delete everyone's feedback about it.

## Limits

Five a minute from one address, twenty a day from one address, and a global
daily cap. The address is used only as the input to an HMAC keyed by a Worker
secret and the window; it is never stored or logged by our code. See
[`design/feedback-privacy.md`](design/feedback-privacy.md).

## Errors

Every refusal has the shape
`{"schema_version": "1.0", "endpoint": "feedback", "error": {"code", "message"}}`.
A `429` also carries `error.retry_after` and a `Retry-After` header.

| code | status | what to do |
|---|---|---|
| `invalid_request` | 400 | Fix the body against the published schema and send it again. |
| `origin_not_allowed` | 403 | Send it from modelspec.dev, or from a client with no Origin header. |
| `receipt_not_found` | 404 | Nothing is stored under that receipt; it was deleted or never kept. |
| `payload_too_large` | 413 | Keep the body under 4096 bytes; shorten the note. |
| `rate_limited` | 429 | Wait retry_after seconds, then send it once. |
| `feedback_store_unavailable` | 503 | Storage is on but not configured; retry later. |
| `method_not_allowed` | 405 | Use POST to send and DELETE to withdraw. |
