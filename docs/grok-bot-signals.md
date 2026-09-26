# Grok Bot release signals

Grok Bot reports a possible model release to ModelSpec. The report starts the
research pipeline. It does not supply a fact or a piece of evidence for a card.

The Worker accepts the report, stores it in the existing `ACCESS` Workers KV
namespace, and returns `202`. An hourly GitHub Action reads one pending signal,
resolves its identity, gathers sources, and opens a pull request. Grok Bot has
no GitHub credential.

## Release signal contract

`POST https://api.modelspec.dev/v1/signals` accepts the JSON contract in
[`schemas/release-signal-v1.schema.json`](../schemas/release-signal-v1.schema.json).
The schema file is version 1. The object has exactly six fields:

```json
{
  "model_name": "Grok 5 Mini",
  "provider": "xAI",
  "first_seen_url": "https://x.com/xai/status/1234567890123456789",
  "timestamp": "2026-09-26T13:14:15Z",
  "confidence": 0.97,
  "signal_id": "grok-20260926-1234567890123456789"
}
```

`confidence` measures Grok Bot's confidence that the post announces a model
release with the stated name and lab. It does not measure the model, its
claims, or the truth of any fact in the post.

The endpoint rejects extra fields, non-X `first_seen_url` values, timestamps
outside the 24-hour intake window, and confidence values outside 0 through 1.
It stores each `signal_id` once. Reposting the same bytes is an idempotent
success. Reusing an ID for another body returns `409`.

The request carries this header:

```text
X-ModelSpec-Signature: sha256=<lowercase hex HMAC-SHA256>
```

Compute the HMAC over the exact UTF-8 request body. Do not parse and re-encode
the JSON between signing and sending it.

## Configure Grok Bot

Use this prompt as the bot's fixed instruction:

```text
Watch only the official X accounts of AI labs and model providers in the
configured account list. Report a post only when the account states that a
named model is released, available, or entering a named preview. Do not report
rumors, replies, benchmark claims without a release, model updates without a
new identity, or posts from third parties.

For a report, copy the model name and lab name stated in the post. Do not infer
architecture, context, price, licence, benchmark evidence, availability, or
another card value. Set first_seen_url to the X post. Set confidence to your
confidence that the post is a release announcement for that exact name and
lab. Create a stable signal_id from the X post ID. Send only the six fields in
the ModelSpec release-signal v1 schema.
```

Run the watch every 10 minutes. Keep Grok Bot's existing budget. Give the bot
only these two secrets:

- the endpoint URL, `https://api.modelspec.dev/v1/signals`;
- the HMAC write secret.

Do not give Grok Bot `GITHUB_TOKEN`, `RESEARCH_PR_TOKEN`, a Cloudflare API
token, or the signal read key.

## What the pipeline does

The pipeline treats `first_seen_url` as discovery input. It never writes that
URL to `models/**`, `offerings/**`, `registry/sources.yaml`, or an evidence
row.

The pipeline performs these steps:

1. It checks exact card aliases, explicit models.dev identities, the supplier
   rule in `schema/suppliers.py`, and the attribution rules in
   `scripts/attribution.py`. More than one exact match is `uncertain`; the
   workflow opens a `new-model` issue and writes no card.
2. It reads models.dev to locate pricing and source URLs. It fetches provider
   pages, API documentation, and a Hugging Face repository when the listing
   names one. Plain HTTP runs first. A run can spend at most 20 Firecrawl
   credits.
3. It rejects every excluded source named by `decision.excluded` and
   `tests/test_removed_sources.py` before fetching it. Arena evidence comes
   only from `lmarena-ai/leaderboard-dataset` at its pinned revision.
4. It drafts through `schema.card.ModelCard` and validates the round trip. New
   benchmark values can appear only as `benchmarks.evidence` rows. Missing
   facts stay empty.
5. It runs `modelspec verify`, the MODEL-111 accuracy profile, and the
   MODEL-160 recall report. The pull request runs the same required checks.
6. It classifies the diff. A new card or any identity or licence change gets
   the `new-model` label and stays a draft for a person to merge. A diff that
   passes MODEL-124's score-only guard gets an audit artifact and may enable
   auto-merge after its checks pass.
7. After the workflow acknowledges a signal, the Worker schedules re-checks
   for 1, 7, and 30 days after the first pull request.

The HTTP gatherer does not use Firecrawl today. `FirecrawlBudget` enforces the
20-credit ceiling before a rendered fetch can be added. If a source cannot be
read by plain HTTP, the pipeline leaves the signal unresolved instead of
guessing.

## Turn on the endpoint

Jamie owns these go-live steps. Do not complete them from an automated worker:

1. Generate two independent random secrets of at least 32 bytes. Use one as
   the Grok Bot HMAC write secret and one as the repository read key.
2. From `api/worker/`, run `wrangler secret put SIGNALS_HMAC_SECRET` and enter
   the write secret. Then run `wrangler secret put SIGNALS_READ_KEY` and enter
   the read key. The commands send values to Cloudflare; the values never enter
   git or shell history.
3. Add the read key as the GitHub Actions secret
   `MODELSPEC_SIGNALS_READ_KEY`. Confirm that `RESEARCH_PR_TOKEN` is present.
4. Set the GitHub Actions repository variable `SIGNALS_ENABLED` to `true`.
   Until this variable is set, the hourly workflow is skipped.
5. Change `SIGNALS_ENABLED` in `api/worker/wrangler.jsonc` from `"false"` to
   `"true"`, merge the change, and let `.github/workflows/rank-api.yml` deploy
   it. Do not hand-deploy the Worker.
6. Send one signed test signal. Confirm a `202` response, an hourly workflow
   run, and a draft pull request with the `new-model` label.
7. Put the endpoint, the write secret, the prompt above, and the 10-minute
   schedule into Grok Bot.

To stop intake, set the Worker flag to `"false"`. The endpoint then returns
`404`. Stored signals remain in KV. To stop processing without changing
intake, set the GitHub repository variable `SIGNALS_ENABLED` to `false`.

## Repository read endpoints

The hourly workflow uses two endpoints that require
`Authorization: Bearer <MODELSPEC_SIGNALS_READ_KEY>`:

- `GET /v1/signals/pending` returns pending signals and due re-checks.
- `POST /v1/signals/ack` records the pull request or issue URL, removes the
  pending item, and schedules the three re-checks.

These endpoints are for the repository workflow. Grok Bot cannot read or
acknowledge the queue.
