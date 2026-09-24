# API access: keys, tiers, limits and the sandbox

MODEL-69. How a call to the ranking origin is identified, what it is allowed to
do, and what it is told when it is refused.

**Status: wired, enforcement off, key store bound, no keys issued.** Both POST
endpoints (`/v1/rank`, `/v1/policy-check`) pass through the gate. A request
without a key is served exactly as before; a request that presents a key is
checked. See [The switch](#the-switch-access_enforced) and
[Morning steps](#turning-it-on). No key has been issued yet (issuance is
MODEL-73).

The modules are in `api/worker/src/`:

| Module | What it is |
| --- | --- |
| `access.py` | `serve()` — the one path from a presented key to an answer |
| `access_config.py` | the tier table, loaded and validated |
| `access_keys.py` | key format, fingerprinting, issue / lookup / revoke |
| `access_limits.py` | the daily and burst counters, and their windows |
| `access_sandbox.py` | the `test_` answer |
| `access_kv.py` | the key-value interface, a Workers KV adapter, a test double, and `UnboundKV` for a Worker with no store |
| `kv_value.py` | what "no such key" looks like from Workers KV under Pyodide, shared with the determination store |

None of them import the Workers runtime, so `tests/test_api_access.py` exercises
all of it under CPython. Only `access_kv.CloudflareKV` knows what a binding is,
and it is handed one rather than looking one up by name.

## Presenting a key

```
Authorization: Bearer <key>
X-API-Key: <key>
```

`Authorization` wins if both are sent. **A key is never read from the query
string.** URLs are written into access logs, proxy caches, browser history and
referrer headers by everything they pass through; a key in one is a key in
somebody else's logs.

`POST /v1/billing/checkout` uses the same headers. A valid live key binds the
purchase to that key (pack credits ADD, a plan attaches). An unknown or
revoked key is `401`, never treated as anonymous. See [`billing.md`](billing.md).

## Tiers

The table is `api/worker/tiers.json`. It is data: changing a limit is an edit
to that file (or to the `TIER_POLICY` variable), never to a module.
`tests/test_api_access.py::test_a_limit_changes_with_no_code_change` proves it
by tightening a limit in JSON and watching the refusal arrive earlier, and
`test_no_access_module_hard_codes_a_limit` parses every module and fails on a
numeric literal bound to a name that reads like a limit.

| Tier | Daily | Burst | Live data |
| --- | --- | --- | --- |
| `sandbox` (`test_…`) | unlimited | unlimited | no |
| `free` | 10 | 5/min | yes |
| `paid` | none (funded keys) | 60/min | yes |
| `dpf` | unlimited | unlimited | yes |

`null` is how unlimited is written, and it is a comparison that never refuses —
not a branch that skips the meter. Every live call is counted, including the
ones no limit will ever refuse, because usage is worth knowing for a key that
pays nothing and for the key that is exempt. That is also why the exempt key is
on the same handler as a paying one:
`test_an_exempt_key_takes_the_same_steps_as_a_paying_key` asserts the two
requests record an identical sequence of steps, and
`test_no_module_branches_on_the_exempt_tier_by_name` parses the package's syntax
tree and fails if the tier is named anywhere outside a comment or a docstring.

MODEL-93 meters paid access in credits, not a daily quota. `billing.prices`
maps each Stripe Price id to `{kind: plan|pack, credits, name}`. A funded key
(balance > 0) gets the paid answer, including determinations. A key with zero
credits gets the free-tier answer plus `credits.exhausted`. See
[`billing.md`](billing.md).

## Windows and the reset boundary

**The daily window is a UTC calendar day.** It opens at `00:00:00Z` and resets
at the next `00:00:00Z`. UTC is the only boundary that is the same for every
caller, needs no timezone database in the isolate, and does not move under
anybody twice a year; the cost is that the reset lands mid-afternoon for part of
the world. Every refusal carries the exact `resets_at`, so nobody has to work it
out. A tier table that asks for another timezone is refused at load time rather
than metered in UTC anyway.

**The burst window is a wall-clock UTC minute** — seconds 00 to 59.

Both windows are fixed, not sliding. A fixed window costs one counter and no
history, and admits at most twice the burst limit across a boundary; for a
5/minute guard over a 10/day quota, a sliding window is not worth its storage.

A refused call is not counted. Being told "no" must not spend quota, or a
mis-looping client would never get its window back.

Counters live in KV under `count:<key-fingerprint>:<scope>:<bucket>`. KV is
eventually consistent and has no atomic increment, so a caller racing itself
across several Cloudflare locations can overshoot a quota slightly. That is a
good-faith meter, and an acceptable trade for a free tier; a Durable Object is
the answer if it ever has to be exact, and `access_kv.AsyncKV` is the seam it
would be swapped behind.

## Statuses

| Status | `error.code` | When |
| --- | --- | --- |
| 401 | `missing_api_key` | no key presented. The message names where to get one and that `test_` keys are unlimited |
| 401 | `invalid_api_key` | a key we do not know. Retrying with credentials may work, which is what 401 means |
| 403 | `key_revoked` | a key we know and will not serve. Retrying will not help |
| 429 | `rate_limited` | a window is spent |
| 500 | `tier_not_configured` | the key names a tier the table does not carry. Ours, not the caller's |
| 500 | `access_not_configured` | a key was presented and the deployment has no tier table (`TIER_POLICY` unset). Ours |
| 503 | `access_store_not_configured` | a live key was presented and no `ACCESS` KV namespace is bound, so it cannot be checked. Refused, never served as anonymous |
| 400 | `sandbox_not_available` | a `test_` key on `/v1/policy-check`. The sandbox holds no synthetic policy data and touches no live data |

`missing_api_key` only occurs with enforcement on. The table is
`access.REFUSALS`; the OpenAPI spec is generated from it by running the gate.

A 429 states the limit, the window, and when it resets:

```json
{
  "error": {
    "code": "rate_limited",
    "message": "rate limit reached: 10 request(s) per 1 day, fixed, resetting at 00:00:00 UTC. This window resets at 2026-09-18T00:00:00Z (34200s). The sandbox is unlimited.",
    "scope": "daily",
    "limit": 10,
    "used": 10,
    "remaining": 0,
    "window": "1 day, fixed, resetting at 00:00:00 UTC",
    "window_seconds": 86400,
    "resets_at": "2026-09-18T00:00:00Z",
    "retry_after_seconds": 34200,
    "tier": "free",
    "windows": [{"scope": "daily", "...": "..."}, {"scope": "burst", "...": "..."}],
    "how_to_get_a_key": "https://modelspec.dev/pricing"
  },
  "result": []
}
```

Both windows are reported, not only the one that refused: a caller stopped by
the burst limiter wants to know whether the day is nearly gone as well. The
response also carries `Retry-After` and `RateLimit-Limit` / `RateLimit-Remaining`
/ `RateLimit-Reset`.

## The sandbox

Any key beginning `test_` is answered from `access_sandbox.py`. No signup, no
limit, no key store, no published export, no network. The short-circuit is in
`access.serve` before the key is looked up and before the live handler is
called, and the test that proves it hands the gateway a key store and a data
path that raise if they are touched.

The rows are not a hand-written fixture. They come out of
`pipeline.ranking.rank_report` — the function the live endpoint and
`modelspec offline rank --json` both call — run over five synthetic candidates
defined in the module. Every field a live row has, a sandbox row has, with the
same types, because the same code produced both; a field added to the scorer
appears in the sandbox on the next deploy with nobody remembering to update
anything.

The values are unmistakable: models are `sandbox/fixture-…`, the provider is
`ModelSpec Sandbox`, `scores_as_of` is fixed, and `"sandbox": true` rides on the
response. Two of the five have thin evidence, so an integrator sees a real
`unranked` count, named `unranked_candidates` and a real `evidence_basis` before
paying for any of them.

## Keys are never written down

A key is looked up by the SHA-256 of its own bytes. What KV holds — both the
name and the value — is survivable in a leak: a tier, an owner, a timestamp and
a 12-character fingerprint, and nothing that can be replayed.

There is no field anywhere that holds a secret, which is what makes "no key
value is ever logged" a property of the shape rather than a rule to remember.
`test_no_key_value_is_ever_logged_returned_or_stored` issues a known key, drives
every branch of the gateway with it, and searches the log events, captured
logging, stdout, response bodies, headers, object reprs and both the names and
the values in the store for it.

Logs identify a key by `key_id`: the first 12 hex characters of the
fingerprint. It identifies, it does not authenticate.

## Wiring: the gate in `entry.py`

`Default.fetch` reads and parses the body, then hands both POST endpoints to
`access.gate` **before either export is fetched**:

```python
outcome = await access.gate(
    api_key=access_keys.extract(lambda name: request.headers.get(name)),
    enforced=access.enforcement(getattr(self.env, "ACCESS_ENFORCED", None)),
    kv=_access_store(self.env),            # CloudflareKV(env.ACCESS), or UnboundKV
    load_policy=lambda: access_config.load_policy(self.env),
    anonymous=anonymous, live=live, sandbox=sandbox, envelope=envelope,
)
return _json_response(outcome.status, outcome.body, outcome.headers)
```

`gate` is `serve` behind the switch. `live(record, tier)` answers for a known,
metered key; for policy-check it passes `_entitlement(tier, funded=…)`, which
grants the determinations when the key has remaining credits, or when the tier
is paid and unlimited (the exempt row — the flags, never the name).
`anonymous()` is the pre-MODEL-69 answer, the free tier. `sandbox()` is the
`test_` answer for rank, and `sandbox_not_available` for policy-check.

The body is parsed with the live parser before the sandbox answers, so a body
the live endpoint would refuse is refused in the sandbox too. The one exception
is `environment.hardware`: the sandbox reads no hardware vocabulary, so it
accepts any id and filters nothing by it.

The gate is handed no part of the body — only the key, read off the headers.
`tests/test_legal.py` checks that from the syntax tree.

## The switch: `ACCESS_ENFORCED`

A `vars` entry in `api/worker/wrangler.jsonc`, shipped as `"false"`.

| | no key | `test_…` key | known live key | unknown or revoked key |
| --- | --- | --- | --- | --- |
| **off** (shipped) | served as before: free tier, unmetered, nothing written | sandbox | metered, served per tier | 401 / 403 |
| **on** | 401 `missing_api_key` | sandbox | metered, served per tier | 401 / 403 |

Presenting a bad key is an error in both modes. Silently treating it as
anonymous would let a caller who believes they hold a paid key run for weeks on
the free answer without being told.

`"false"`, `"0"`, `"no"`, `"off"` and `""` (and unset) read as off; **anything
else reads as on**, so a typo made while switching it on cannot leave it off.

It ships off because self-serve issuance (Stripe Checkout, MODEL-73) ships
behind its own flag, `BILLING_ENABLED`, also off. Enforcing now would refuse
every anonymous caller. **Flip `ACCESS_ENFORCED` once keys can be obtained.**

## The key store: the `ACCESS` binding

Key records and counters live in their own KV namespace, bound as `ACCESS` —
never in `DETERMINATIONS`, which holds our research and is only ever read. The
namespace was created 2026-09-18 and is bound in `wrangler.jsonc`. Enforcement
stays off; no key has been issued (issuance is MODEL-73). A presented live key
is checked against the store; none are issued, so it is unknown.

With no `ACCESS` binding the Worker would hand the gate `access_kv.UnboundKV`,
which refuses every read. A presented live key is then refused 503
`access_store_not_configured`; anonymous and `test_` requests are unaffected,
because neither reads the store. No crash, and no silent pass.

What the store holds, and what it does not, is disclosed in
`docs/legal/privacy.md`; `tests/test_legal.py` fails if the binding is live or
staged without that disclosure, or if an access module writes anything but a
named record kind (key, counter, Stripe event id, subscription, session
pointer, keyref).

### Missing keys and Pyodide's `jsnull`

Workers KV answers a missing key with JS `null`, which Pyodide hands to Python
as `pyodide.ffi.jsnull` — **not** `None`. `CloudflareKV.get` used to test
`is None`, so a mistyped key came back as the string `"jsnull"` and was parsed
as a key record: a crash, not a 401. `CloudflareKV.get` now normalises through
`kv_value.absent` (the rule #104 wrote for the determination store, moved to a
shared module), so every caller — lookup, revoke, both counters — sees `None`.
`tests/test_api_access.py` and `tests/test_access_wiring.py` drive a stub
binding that returns a `jsnull` stand-in, `""` and `None`, and assert an unknown
key is a clean 401 under each.

## The tier table in the isolate: `TIER_POLICY`

The deploy (`.github/workflows/rank-api.yml`) passes the table:

```
wrangler deploy --var "BUILD_COMMIT:$GITHUB_SHA" --var "TIER_POLICY:$(jq -c . tiers.json)"
```

The disk fallback in `load_policy` is for this repository's tests; the isolate
has no copy of `tiers.json`. A Worker without the variable refuses a presented
key with `access_not_configured` rather than metering it against numbers
invented in code. Anonymous requests never load the table.

## Turning it on

1. **Done 2026-09-18.** The `ACCESS` namespace
   (`ef86b7ce138d4891b3eb630cdd2ba4e5`) is bound in
   `api/worker/wrangler.jsonc`. Enforcement stays off.
2. Issue keys: Stripe Checkout (`docs/billing.md`, MODEL-73) records the
   entitlement from the webhook. `GET`/`POST /v1/billing/claim` calls
   `access_keys.issue` once. Rotation is `POST /v1/billing/rotate`.
3. Then, and only then, set `"ACCESS_ENFORCED": "true"`, regenerate the spec
   (`python api/worker/openapi.py`) and update `docs/api.md`; the doc tests
   fail until both say a key is required.
