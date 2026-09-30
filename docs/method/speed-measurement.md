# Speed measurement, method speed-v1

This is the published method behind every speed number ModelSpec measures
itself. It implements step 2 of [ADR 0004](../adr/0004-first-party-measurement.md):
active speed probes on premier offerings, each step approved by Jamie before
any spend. The code is [`scripts/speed/`](../../scripts/speed/). The
source review that found no reusable public reading is
[`docs/research/speed-measurement.md`](../research/speed-measurement.md).

Every speed fact ModelSpec publishes carries `measured_by: ModelSpec`, this
method's ID and URL, its sample size, the workload, the median, the
interquartile range and a 95% interval of the median. A number without all of
them is not published.

## Why the 2026-09 latency programme was cancelled, and what is different

On 2026-09-16 Jamie cancelled the agentic-latency programme (MODEL-60, 66 and
67) and discarded its results. It could not be tested thoroughly enough to
trust. Four reasons were recorded. This method answers each one in structure,
not in intent.

| The 2026-09 problem | What speed-v1 does |
|---|---|
| A solo operator cannot produce trustworthy **hardware-dependent** latency without a wide variety of hardware, networks and components. | speed-v1 measures only **hosted provider offerings**, where the programme itself found that about 96.6% of wall-clock time is the provider's infrastructure. It measures no hardware of ours. The TLS handshake is timed separately and left out of time to first token. Each run records where its traffic enters the internet (the Cloudflare location from `cdn-cgi/trace`), and runs from any other vantage are dropped before aggregation. |
| Publishing numbers that cannot be trusted costs the catalogue its credibility. | **The instrument is tested against a known truth.** `tests/test_speed_harness.py` streams responses of known timing over a real local socket, with HTTP/1.1 chunked transfer, in all three wire formats (Anthropic, OpenAI-compatible, Gemini), through the transport and parsers a live run uses. Measured throughput must be within 5% of the truth, which the test sets, not the code under test. **The second key re-measures.** Every run file keeps each request's raw stream events. A deterministic verifier with its own parser re-times every counted sample from those events, re-derives the run set, vantage and every gate, and recomputes the statistics by a separate implementation. It trusts no number the collector wrote. A fact it cannot re-derive gets a `mismatch` record and stays out of the snapshot. A full dry run replays streams in each provider's wire format through the whole pipeline with no network. Until the pilot records real streams, those fixtures are synthetic, and they are labelled so. |
| Thin or noisy results read as findings. | **Publication gates on independent slots.** Requests in one slot share provider load, so at most 2 count from each slot. A number is published only with at least 20 counted good samples from at least 8 slots that cover all four scheduled hours, on at least 2 days within 7, with at most 20% failed requests. A run file or sample given twice is refused. Anything short of the gates stays `unknown`, because a null beats a guess. The pilot is one slot, so it cannot pass. |
| Latency without a pass rate ranks models backwards. | **Speed never outweighs quality.** Every template that prefers speed weighs capability at least three times all its other terms together (0.75 against 0.25), and a test enforces this. Terms are normalised over the feasible set, so a model that is fastest (and, for High volume, cheapest) still needs two thirds of the lineup's capability range to beat the strongest model. This is a weighting, not a floor: a relative capability floor, "within a margin of the leader", needs a new contract operator and is a follow-up. speed-v1 measures single streamed requests on fixed prompts, not agentic wall-clock. Its interval enters the answer bands, so two offerings whose speeds cannot be told apart are not separated by speed. |

## What is measured

Two facets per offering, defined in `registry/facets.yaml`:

- `offering.speed.time_to_first_token`, in milliseconds. The time from the
  moment the request is written to an open connection until the first
  **visible** content token arrives. Reasoning or thinking deltas are not
  content.
- `offering.speed.throughput`, in tokens per second. The visible output
  tokens after the first content event, divided by the time from the first to
  the last content event: `N × (e − 1) / e / (t_last − t_first)`, where `N` is
  the visible tokens and `e` the content events. The first event's share of the
  tokens arrived before the clock started. Counting `N − 1` instead would read a
  provider that sends 32 tokens an event about 14% fast. A stream with fewer
  than 16 content events is `not_streamed` and does not count. Visible tokens
  are the provider-reported output tokens minus provider-reported reasoning
  tokens.

Both are medians of the **headline workload**, `short_chat`. The other two
workloads are measured and published in the measurement file beside it. Only
the headline workload becomes a fact in speed-v1, because a facet holds one
number per offering and a short prompt separates serving speed from
prompt-processing cost.

## Workloads

Each workload has a fixed, published prompt. Its SHA-256 is pinned in
`tests/test_speed_harness.py`, so a changed prompt fails the tests. A changed
prompt is a new method version, never an edit to speed-v1.

| Workload | Input | `max_tokens` | Prompt |
|---|---|---|---|
| `short_chat` | about 150 tokens | 256 | [`prompts/short_chat.txt`](../../scripts/speed/prompts/short_chat.txt) |
| `coding` | about 1,800 tokens | 512 | [`prompts/coding.txt`](../../scripts/speed/prompts/coding.txt) |
| `long_context` | about 30,000 tokens | 256 | `long_context_prompt()` in [`method.py`](../../scripts/speed/method.py), a ledger generated from seed 212 |

Every prompt asks for more output than `max_tokens` allows, so streams run to
about the same length. A stream under 32 visible tokens does not count. Every request starts with a line holding a random
16-hex nonce. The nonce defeats provider prompt caches. A sample that still
reports cached input tokens is marked `cache_hit` and never aggregated.

Temperature is 0 where the API accepts it. Effort is the lowest the offering
accepts, pinned per offering in [`pilot.yaml`](../../scripts/speed/pilot.yaml),
recorded with every run and published in every fact with the median reasoning
tokens. An offering whose effort claims no reasoning (`reasoning_off`) is held,
never published, if any counted request reasoned: reported reasoning tokens,
or thinking or reasoning deltas in the stream (Anthropic reports thinking only
that way). An offering's model ID, effort and parameters must be the same in
every run of a window; a window that mixes configurations is refused. Default effort varies by prompt and by provider,
and hidden reasoning before the first visible token would make time to first
token a measure of reasoning length, not of the offering.

## Sampling

- **Direct provider APIs only.** The hosts are listed in
  `scripts/speed/providers.py`, and a test fails if one is not a first-party
  provider host. No router is ever called.
- **One slot is one run.** Slots are scheduled at 00:00, 06:00, 12:00 and 18:00
  UTC, so every offering is sampled across the day.
- **Within a slot**, each offering first gets one warm-up request, which is
  recorded and never aggregated. Then the lineup, shuffled with the slot as the
  seed, is called round-robin: every offering, then every workload, for each
  repetition. A burst of load on one provider therefore does not land on one
  offering's whole sample.
- **Repetitions.** The baseline takes 2 measured requests per offering,
  workload and slot, and only the first 2 of any slot count. Twelve slots over
  three days give 24 samples each.
- **Every request is new.** Each request opens a new TLS connection and is
  never retried. A failure is recorded with its cause (`http_error`,
  `stream_error`, `transport_error`, `no_content`, `not_streamed`,
  `short_output`, `cache_hit`) and counts against the failure gate. A reply the
  harness cannot parse is a failed sample; it never ends a paid run early.
- **Every stream is kept.** Each sample stores its raw events with their
  times, so every number can be re-derived from what the provider sent.

## Statistics

For each offering, workload and metric, over the good samples:

- the **median**, the published value;
- the **interquartile range** (`statistics.quantiles`, inclusive method), the
  spread one request sees;
- the **95% interval of the median**, from order statistics and the exact
  binomial distribution. It needs no distribution assumption. With 20 samples
  it runs from the 6th to the 15th value. It is the uncertainty a ranking must
  respect, so it is the interval that enters the answer bands.

A single number is never published alone.

## Publication

A window is a directory: `measurements/speed/<window>/runs/` holds one gzipped
run file per slot, and a rerun of a slot replaces that slot's file.

1. `python -m scripts.speed aggregate <window>` merges every run file in the
   window and applies the gates.
   It writes one result row for every offering and workload, published or not,
   with the reasons a row was held.
2. `python -m scripts.speed verify <window>` is the second key. It reads every
   run file in the window, refuses a measurement that names a different set,
   and re-times every counted sample from its raw
   events with its own parser, re-derives the vantage, the gates and the
   statistics, checks the run files' hash and the prompt hashes, and writes
   one verification record per fact. A fact it cannot re-derive gets a
   `mismatch` record, which keeps it out of the snapshot.
3. Promotion puts the verified facts into `offerings/`, their verification
   records into `verification/log.jsonl`, and registers the source
   `modelspec-speed-v1`. That source's snapshot reference is the SHA-256 of the
   run files, and the run files are committed beside the measurement, so anyone
   can recompute every number.

## Staleness

A measurement stops deciding anything 30 days after its sampling window
closes (`MEASUREMENT_STALE_AFTER_DAYS` in `decision/model.py`). The snapshot
build drops it as `stale_measurement`, and the offering's speed reads as
unknown until a new window is promoted.

## Fixture numbers never reach the published snapshot

A dry run marks every fact `provenance: fixture`. The snapshot compiler raises
on a fixture measurement unless a test passes `allow_fixture_measurements`, and
`build_from_repo`, the published build, never does. A test also fails if any
offering file holds a fixture measurement.

## Limits

- **Single vantage point.** Every number is from one network location. A user
  elsewhere may see different time to first token. Throughput depends much
  less on location. The vantage is recorded on every fact.
- **Provider routing varies.** A provider may serve one model from different
  regions or hardware between requests, and it may change that without notice.
  The time-slot spread and the interval capture this variance, but they do not
  remove it.
- **Global offerings only.** Region-specific offerings need a probe in the
  named region. They stay unknown under speed-v1.
- **Generation only.** Embedding and rerank models produce no streamed output,
  so their Fastest tier (`retrieval-fastest`) stays unavailable under
  speed-v1.
- **One workload decides.** The facts come from `short_chat`. The Long
  documents Fastest tier (`documents-fastest`) therefore ranks million-token
  work by short-prompt speed. The `long_context` numbers are measured and
  published in the measurement file, but a facet per workload is a later
  method version.
- **Lowest effort.** The numbers describe the offering at its lowest accepted
  effort. Speed at a higher effort is a different measurement.
- **Token counts are the provider's.** Throughput uses provider-reported
  tokens, and each provider tokenises differently. A provider that sends many
  tokens per content event makes the interval between first and last events
  shorter by up to one event.
- **The cloud runner's location is not pinned.** GitHub-hosted runners run in
  several Azure regions. Runs from a vantage other than the window's most
  common one are dropped, and the drop is reported.

## Request shapes and smoke mode (MODEL-243)

The pilot's first slot failed on request shape, not on speed. Shapes are
pinned per provider in `scripts/speed/providers.py` and `pilot.yaml`, each with
the doc URL it was checked against, and none of it changes the speed-v1 rules
above: no retry, no workload change, the same gates.

`mode=smoke` in the speed-probe workflow sends one short_chat request per
offering under a fixed $0.25 cap (the cap is a constant, not an input) and
prints each status, usage and the first 1 KB of any non-2xx body with keys and
auth values redacted. A shape that no doc settles is settled by that output,
not by a guess. Every non-2xx sample in a pilot or baseline run carries the
same redacted `error_body`.

Two speed-v1 rules the pilot showed to be awkward, left as they are until a
method version changes them: a provider-injected cached prefix (xAI, 1152
tokens on every request) collides with the `cache_hit` rule, and a provider that
streams under 16 chunks for 256 tokens (Gemini) ends `not_streamed`.

## Spend control

No request is sent without an explicit `--live` and `--cap-usd`. Before the
first call, the run computes its worst case from the offerings' own verified
prices:

```
bound per call = (prompt_bytes + nonce_bytes + 64) × input_price
               + (max_tokens + output_bound_extra) × output_price
```

Prices are in US dollars per million tokens. Every input token is at least one
UTF-8 byte, and output is capped by `max_tokens`. The bound holds as long as
the catalogue's prices are current and each provider honours `max_tokens` and
any thinking budget; Google describes `thinkingBudget` as guidance. If the
slot's total bound is over the cap, the run refuses and sends nothing. Before
each call, the run also checks that spend so far, from provider-reported
usage, plus that call's bound still fits under the cap, and stops if it does
not. A provider that bills past its bound can therefore overshoot the cap by at
most that one call's excess. The provider-side spend limits on each key are
the last line. Keys come only from
environment variables, are sent only in request headers, and never appear in a
run file.

## Pilot plan (awaiting Jamie's approval)

The pilot checks authentication, stream parsing, token accounting and the run
file format against the real APIs. It publishes nothing: one slot cannot pass
the gates.

**Offerings.** Ten premier offerings on six direct provider APIs:

| Offering | API | Price in / out ($/M) |
|---|---|---|
| Claude Opus 5.5, Anthropic API | `anthropic` | 4.00 / 20.00 |
| Claude Sonnet 5.5, Anthropic API | `anthropic` | 2.00 / 10.00 |
| GPT-6 Sol, OpenAI API | `openai` | 2.00 / 10.00 |
| GPT-5.6 Sol, OpenAI API | `openai` | 4.00 / 20.00 |
| Gemini 3.8 Flash, Gemini API | `gemini` | 0.75 / 3.75 |
| Gemini 3.1 Pro Preview, Gemini API | `gemini` | 2.00 / 12.00 |
| Grok 4.7, xAI API | `xai` | 2.00 / 6.00 |
| DeepSeek V4 Pro, DeepSeek API | `deepseek` | 1.32 / 3.96 |
| DeepSeek Flash, DeepSeek API | `deepseek` | 0.30 / 1.20 |
| GLM 5.3, Z.ai API | `zai` | 1.40 / 4.40 |

Bedrock, Vertex and Azure offerings need cloud credentials rather than an API
key, so they are not in the pilot.

**Repetitions.** One slot: 1 warm-up and 5 measured requests per offering and
workload, 160 requests in all. Five, not two, so the pilot shows within-slot
spread; only two of them would count toward a published number.

**Cost.** From `python -m scripts.speed plan`:

```
expected per call = ((prompt_bytes + nonce_bytes) / 4 + 64) × input_price
                  + max_tokens × output_price
```

| Run | Requests | Expected | Worst case |
|---|---|---|---|
| Pilot, one slot | 160 | $3.65 | $13.11 |
| Baseline slot (2 measured) | 70 | $1.48 | $5.27 |
| Baseline window, 12 slots over 3 days | 840 | $17.74 | $63.21 |
| Refresh: one baseline window every 3 weeks | 840 a window | about $25 a month | about $90 a month |

The long-context workload is about 85% of the input cost. The approval cap for
the pilot should be **$15**. It is above the $13.11 worst case, so the run
starts, and the expected spend is about $3.65.

**Keys Jamie sets.** Six repository secrets, one per API. Each should be a
dedicated key with a spend limit set at the provider:
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`,
`DEEPSEEK_API_KEY`, `ZAI_API_KEY`.

**Vantage first, free.** Before the pilot, dispatch the free `preflight`
three or more times on GitHub-hosted runners. It prints each runner's
Cloudflare location. If the location changes between runs, a baseline window
loses the minority runs to the vantage rule and may fail its gates, so that
must be settled before any baseline spend.

**Where and how often.** The pilot runs once, by hand, from a
`workflow_dispatch` job on a GitHub-hosted `ubuntu-latest` runner:
[`.github/workflows/speed-probe.yml`](../../.github/workflows/speed-probe.yml),
mode `preflight` (free) or `pilot` (paid, capped by `SPEED_CAP_USD` in the
file, not by an input). The pilot's run file, measurement and verification
records go to a `data/` pull request, never to `main`. After the
pilot is reviewed, the baseline runs a three-day window (12 slots at the four
slot hours) every three weeks, which keeps every fact inside the 30-day
staleness limit. The workflow has no schedule; the baseline needs a separate
approval and a reviewed change to that file. Runner time is measured, not guessed, where possible:

- Job setup is **about 14 seconds**, measured on this repository's scheduled
  Python job (`leaderboard-refresh.yml`, run 36476089270): checkout 6 s,
  `setup-python` with the pip cache 3 s, and installing `pydantic` and
  `pyyaml` 4 s.
- The probe itself is sequential, one stream at a time. At 3 to 7 seconds a
  stream, a pilot slot takes about 10 to 20 minutes and a baseline slot about
  5 to 9 minutes. The pilot measures the real figure.
- A baseline window is 12 jobs of about 6 to 10 minutes, so about 70 to 120
  runner minutes every three weeks. The repository is public, so standard
  GitHub-hosted runner minutes bill $0.

**The one command.** After the free preflight (`python -m scripts.speed
preflight`, which lists each provider's models and checks every pinned model
ID without a paid call):

```bash
python -m scripts.speed run --live --cap-usd 15
```

The run file keeps every raw stream with its timing. Those streams become the
recorded fixtures that replace the synthetic ones in `scripts/speed/fixtures/`.
