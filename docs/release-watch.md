# Release watch: primary-source discovery (MODEL-216)

Grok Bot ([`grok-bot-signals.md`](grok-bot-signals.md)) hears about a release
on X. That makes one person's X feed a single point of failure. The release
watcher reads the primary sources directly: the labs' own model pages,
Hugging Face org feeds for open-weights labs, and OpenRouter's public model
list. It files what is new into the same pending queue Grok Bot uses. The
hourly `release-signals.yml` then resolves, drafts, re-checks and opens pull
requests exactly as it does for Grok Bot.

While that queue is off (`SIGNALS_ENABLED`), Grok Bot is off with it and the
watcher is the only release feed. It then files each discovery as one GitHub
issue instead. See [Two sinks](#two-sinks).

Every carded lab is watched. The labs with their own model page are read
there first. Every other lab is read from the Hugging Face org its cards
cite, and OpenRouter backs up the hosted labs. That is 74 sources.
`models/cerebras/` is the one exception: its cards are other labs' models as
Cerebras serves them.

A discovery is a trigger, never evidence. The watcher writes nothing to a
card. The pipeline downstream re-reads primary sources under its own
two-key rules.

## How a run works

`.github/workflows/release-watch.yml` runs `scripts/release_watch.py` every
6 hours, at minute 41.

1. It loads [`registry/release-watch.yaml`](../registry/release-watch.yaml) and
   refuses any source on a host `decision/excluded.py` excludes, or on X.
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
5. Each new model becomes one `release-discovery` v1 and is filed to one of
   the [two sinks](#two-sinks). The signal ID is
   `watch:<lab>:<model>`, normalised the way catalogue aliases are. A model
   listed by the lab's page, Hugging Face and OpenRouter is therefore filed
   once, from the first source in registry order. The labs' pages come first.

The watcher re-files every uncatalogued discovery on every run. Each sink
keeps its own permanent record of what it has seen, so every repeat is a
no-op. The committed baseline plus that record are all the state there is.

A model a watched lab lists is filed on the next run, at most 6 hours later.
`tests/test_release_watch.py` proves this on replayed fixtures
(`tests/fixtures/release_watch/`).

## Two sinks

| `vars.SIGNALS_ENABLED` | Sink | Dedup |
| --- | --- | --- |
| `true` | `POST https://api.modelspec.dev/v1/signals/discovered`, into the MODEL-113 queue. The next hourly `release-signals.yml` run drafts the card, re-checks it at 1, 7 and 30 days, and opens the PR. | A permanent Workers KV marker per discovery ID. A repeat is `200 duplicate`, even after the pending row is acknowledged. |
| anything else | One GitHub issue per discovery, labelled `release-discovery` and `new-model`, carrying the discovery JSON. A person or the research flow drafts the card. | One listing per run of every `release-discovery` issue, open or closed. A closed issue is never filed again. |

The issue sink uses the workflow's own `GITHUB_TOKEN` (`issues: write`). If
the listing fails, nothing is created and the run alerts. A failed listing
must not turn into a flood of duplicates.

## Outages raise an alert

A source is never skipped quietly. The run reports each source as one of:

| Status | Meaning |
| --- | --- |
| `ok` | The source answered, and at least half its baseline count of IDs came back. |
| `unreachable` | A network error, a timeout, or a status other than 200. |
| `robots_disallowed` | `robots.txt` forbids the URL, or answered 5xx. Any 4xx allows (RFC 9309 §2.3.1). |
| `parse_failed` | Fewer IDs than half the baseline. The page moved or became script-only. |
| `burst` | More new IDs than `max_new` (10, or 15 for OpenRouter). The source probably changed shape. Nothing from it is filed. |

A refused POST to the Worker, or a refused issue listing or create, is
reported too. On any of these, and on any failed step (a crash before the
report included), the workflow comments on the one open issue labelled
`release-watch`, or opens it, and the run fails. Sources that did answer still
file their discoveries on the same run. A transport error or 5xx is retried
once before it counts.

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

There is nothing to configure. On merge the workflow runs every 6 hours and
files issues. It moves to the queue when Jamie turns the queue on per
[`grok-bot-signals.md`](grok-bot-signals.md#turn-on-the-endpoint): the
Worker's `SIGNALS_ENABLED`, the `MODELSPEC_SIGNALS_READ_KEY` secret, and the
repository variable `SIGNALS_ENABLED=true`, which also starts
`release-signals.yml`.

`python scripts/release_watch.py` with neither `--post` nor `--issues` is a
dry run that prints what it would file.

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

The baseline was first taken on 2026-09-29 from live sources. The dry run
right after it found 74 of 74 sources answering and 0 discoveries.

## Sources and their terms

On 2026-09-29 every watched host's `robots.txt` allowed the watched path.
The watcher reads each host's `robots.txt` again on every run, once per host.
It sends `ModelSpec-Release-Watch/1.0 (+https://modelspec.dev)` and makes
about 85 requests every 6 hours in all.

| Source | What it is |
| --- | --- |
| Anthropic, Google Gemini, OpenAI, Mistral, xAI, DeepSeek, Cohere, Voyage model pages | Public documentation pages. `docs.x.ai` also sends `Content-Signal: ai-input=yes, ai-train=no`. The watcher trains nothing. |
| Hugging Face `/api/models` for 65 org accounts | The public Hub API, anonymous. |
| OpenRouter `/api/v1/models` | A documented public endpoint that needs no key. |

The publishers `decision/excluded.py` excludes are never sources. X belongs
to Grok Bot.

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
| `api.typesafe.ai/v1/models` | `403` without a key, checked 2026-09-29. TypeSafe is watched through OpenRouter. |
| Cohere, DeepSeek, Groq, Fireworks model lists | keyed by design (not probed) |
