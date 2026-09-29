# Release watch: primary-source discovery (MODEL-216)

Grok Bot ([`grok-bot-signals.md`](grok-bot-signals.md)) hears about a release
on X. That makes one person's X feed a single point of failure. The release
watcher reads the primary sources directly: the labs' own model pages,
Hugging Face org feeds for open-weights labs, and OpenRouter's public model
list. It files what is new into the same pending queue Grok Bot uses. The
hourly `release-signals.yml` then resolves, drafts, re-checks and opens pull
requests exactly as it does for Grok Bot.

A discovery is a trigger, never evidence. The watcher writes nothing to a
card. The pipeline downstream re-reads primary sources under its own
two-key rules.

## How a run works

`.github/workflows/release-watch.yml` runs `scripts/release_watch.py --post`
every 6 hours, at minute 41.

1. It loads [`registry/release-watch.yaml`](../registry/release-watch.yaml) and
   refuses any source on an excluded host (Artificial Analysis, Zapier) or on
   X.
2. For each source it reads `robots.txt` and then fetches the source with
   plain HTTPS. It uses no key, no account, no browser and no Firecrawl.
3. It extracts the model IDs the source lists:
   - **Lab pages.** The page is read as text and matched against the
     source's `pattern`. A match needs a digit, so doc slugs like
     `claude-code` never count. `exclude` removes the rest.
   - **Hugging Face.** `/api/models?author=<org>`, newest 100. Quantised and
     repackaged repos (GGUF, AWQ, FP8, MLX, …) are skipped.
   - **OpenRouter.** `/api/v1/models`. Only prefixes mapped to a catalogue
     lab are read. `~…-latest` aliases and `:free`/`:batch` variants are
     skipped.
4. A model is new when all three are true: it is not in
   [`registry/release-watch-baseline.json`](../registry/release-watch-baseline.json),
   it was created in the last 30 days (Hugging Face and OpenRouter only;
   pages carry no date), and it matches no exact catalogue alias.
5. Each new model becomes one `release-discovery` v1 and is posted to
   `POST https://api.modelspec.dev/v1/signals/discovered`. The signal ID is
   `watch:<lab>:<model>`, normalised the way catalogue aliases are. A model
   listed by the lab's page, Hugging Face and OpenRouter is therefore filed
   once, from the first source in registry order. The labs' pages come first.

The Worker keeps a permanent marker for every discovery ID it has accepted.
The watcher re-posts every uncatalogued discovery on every run, and every
repeat is a `200 duplicate`, including after the pending row has been
acknowledged. The committed baseline plus these markers are all the state
there is.

A model a watched lab lists reaches the queue on the next run, at most
6 hours later. The next hourly `release-signals.yml` run processes it.
`tests/test_release_watch.py` proves this on replayed fixtures
(`tests/fixtures/release_watch/`).

## Outages raise an alert

A source is never skipped quietly. The run reports each source as one of:

| Status | Meaning |
| --- | --- |
| `ok` | The source answered, and at least half its baseline count of IDs came back. |
| `unreachable` | A network error, a timeout, or a status other than 200. |
| `robots_disallowed` | `robots.txt` forbids the URL, or answered 401, 403 or 5xx (RFC 9309). |
| `parse_failed` | Fewer IDs than half the baseline. The page moved or became script-only. |
| `burst` | More new IDs than `max_new` (10, or 15 for OpenRouter). The source probably changed shape. Nothing from it is filed. |

A refused POST to the Worker is reported too. On any of these, the workflow
comments on the one open issue labelled `release-watch`, or opens it, and the
run fails. Sources that did answer still file their discoveries on the same
run.

## Contracts

Two senders share one queue, and the signal ID prefix says which contract a
row belongs to:

- **`release-signal` v1** ([schema](../schemas/release-signal-v1.schema.json)).
  Grok Bot, HMAC-signed, `first_seen_url` on X. Its IDs may not start with
  `watch:`. Grok Bot's IDs are `grok-…`, so this changes nothing it sends.
- **`release-discovery` v1** ([schema](../schemas/release-discovery-v1.schema.json)).
  The watcher. Same six fields, a `watch:` ID, and an https `first_seen_url`
  that is not X and not an excluded source. It is authenticated with the
  repository read key, `MODELSPEC_SIGNALS_READ_KEY`, which the workflows
  already hold.

`GET /v1/signals/pending` answers `schema_version` **2** because a queued row
can now be a discovery, whose `first_seen_url` is not on X. That widens the
rows' range, so under MODEL-59 the queue took a major version. Its only
consumer is `release-signals.yml`, which parses rows with
`ReleaseSignal.from_queue` and is updated in the same change. Grok Bot's
intake response stays at `1`.

## Turning it on

There is nothing new to configure. The watcher runs when the queue it feeds
is drained, behind the same switches as Grok Bot:

1. The Worker's `SIGNALS_ENABLED` and the `MODELSPEC_SIGNALS_READ_KEY`
   secret, per [`grok-bot-signals.md`](grok-bot-signals.md#turn-on-the-endpoint).
2. The repository variable `SIGNALS_ENABLED=true`. It gates both
   `release-signals.yml` and `release-watch.yml`.

Until then the workflow is skipped. `python scripts/release_watch.py` without
`--post` is a dry run that prints what it would file.

## Maintaining the sources

- **Add a source.** Add it to `registry/release-watch.yaml`, then run
  `python scripts/release_watch.py --rebaseline --source <id>` and commit the
  baseline. A source without a baseline fails the run.
- **A source changed shape** (`parse_failed` or `burst`). Look at the page,
  fix `pattern` or `exclude` if the IDs moved, then rebaseline that one
  source.
- **Noise.** A doc slug that looks like a model ID becomes a discovery. The
  pipeline resolves it as `uncertain` and opens an identity-review issue.
  Add it to the source's `exclude`.

The baseline was first taken on 2026-09-29 from live sources. That run found
29 of 29 sources answering and 0 discoveries.

## Sources and their terms

On 2026-09-29 every watched host's `robots.txt` allowed the watched path.
The watcher reads each host's `robots.txt` again on every run, once per host.
It sends `ModelSpec-Release-Watch/1.0 (+https://modelspec.dev)` and makes
about 40 requests every 6 hours in all.

| Source | What it is |
| --- | --- |
| Anthropic, Google Gemini, OpenAI, Mistral, xAI, DeepSeek, Cohere model pages | Public documentation pages. `docs.x.ai` also sends `Content-Signal: ai-input=yes, ai-train=no`. The watcher trains nothing. |
| Hugging Face `/api/models` for 21 org accounts | The public Hub API, anonymous. |
| OpenRouter `/api/v1/models` | A documented public endpoint that needs no key. |

Artificial Analysis and Zapier are never sources. X belongs to Grok Bot.

### Provider model lists that need a key (not used)

These list a provider's models authoritatively, but only with an API key. The
watcher does not use them. An agent never creates accounts or handles
credentials, so adding any of them is Jamie's call. The lab pages above cover
the same labs without a key.

| Endpoint | Status |
| --- | --- |
| `api.mistral.ai/v1/models` | `401` without a key, checked 2026-09-29 |
| `api.together.xyz/v1/models` | `401` without a key, checked 2026-09-29 |
| OpenAI `GET /v1/models` | keyed by design (not probed) |
| Anthropic `GET /v1/models` | keyed by design (not probed) |
| Google Gemini `models.list` | keyed by design (not probed) |
| xAI `GET /v1/models` | keyed by design (not probed) |
| Cohere, DeepSeek, Groq, Fireworks model lists | keyed by design (not probed) |
