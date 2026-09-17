# API access: keys, tiers, limits and the sandbox

MODEL-69. How a call to the ranking origin is identified, what it is allowed to
do, and what it is told when it is refused.

The modules are in `api/worker/src/`:

| Module | What it is |
| --- | --- |
| `access.py` | `serve()` — the one path from a presented key to an answer |
| `access_config.py` | the tier table, loaded and validated |
| `access_keys.py` | key format, fingerprinting, issue / lookup / revoke |
| `access_limits.py` | the daily and burst counters, and their windows |
| `access_sandbox.py` | the `test_` answer |
| `access_kv.py` | the key-value interface, a Workers KV adapter, a test double |

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
| `paid` | placeholder, per plan | placeholder | yes |
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

MODEL-73 provisions paid plans by adding rows to this table.

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
`modelspec offline rank --json` both call — run over four synthetic candidates
defined in the module. Every field a live row has, a sandbox row has, with the
same types, because the same code produced both; a field added to the scorer
appears in the sandbox on the next deploy with nobody remembering to update
anything.

The values are unmistakable: models are `sandbox/fixture-…`, the provider is
`ModelSpec Sandbox`, `scores_as_of` is fixed, and `"sandbox": true` rides on the
response. One of the four has thin evidence, so an integrator sees a real
`unranked` count and a real `evidence_basis` before paying for either.

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

## Wiring this into the Worker

`serve()` takes the two things it deliberately does not know — how to build a
live answer and how to build a sandbox one:

```python
policy = access_config.load_policy(self.env)
envelope = service._envelope({}, service_commit, origin)
parsed = service.parse_request(payload, frozenset())

outcome = await access.serve(
    api_key=access_keys.extract(lambda name: request.headers.get(name)),
    kv=access_kv.CloudflareKV(self.env.API_KEYS),
    policy=policy,
    envelope=envelope,
    live=lambda record: self._rank(payload, service_commit, origin),
    sandbox=lambda: access_sandbox.rank_response(parsed, envelope=envelope),
)
return _json_response(outcome.status, outcome.body, extra_headers=outcome.headers)
```

Parsing the request before the split is deliberate: a body the live endpoint
would refuse is refused in the sandbox too, so an integrator's error handling is
exercised against the same validation. `access_sandbox.request_from_payload` is
the tolerant fallback for callers that have not parsed anything.

The Worker needs a KV namespace bound (any name — the adapter is handed the
binding) and, for a limit change without a deploy, a `TIER_POLICY` variable
carrying `tiers.json`:

```
wrangler deploy --var TIER_POLICY:"$(jq -c . api/worker/tiers.json)"
```

`TIER_POLICY` is how the isolate gets the table: the disk fallback in
`load_policy` is for this repository's tests and for local use, and the Worker
is not expected to reach it. A Worker deployed without the variable refuses to
serve rather than metering callers against numbers invented in code — a missing
configuration is an outage, and an outage that announces itself beats a Worker
quietly serving somebody else's limits.
