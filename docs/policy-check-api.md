# The policy-check API (MODEL-80)

`POST https://api.modelspec.dev/v1/policy-check` answers the question the paid
tier exists to answer: **is this model permitted here, and which clause says
so.**

It takes a policy document — required licence terms, permitted origin countries,
required processing regions, a commercial-use requirement — and returns, for
every model and **every platform that model is served from**, one of three
verdicts: `pass`, `fail`, `undetermined`.

The third one is the product. See [the third state](#the-third-state-is-the-product).

- Endpoint logic: [`api/worker/src/policy_service.py`](../api/worker/src/policy_service.py)
- Worker transport: [`api/worker/src/entry.py`](../api/worker/src/entry.py)
- Public export: [`pipeline/policy_export.py`](../pipeline/policy_export.py)
- KV loader: [`api/worker/load_determinations.py`](../api/worker/load_determinations.py)
- Tests: [`tests/test_policy_check.py`](../tests/test_policy_check.py)
- The rank endpoint it shares a Worker with: [`rank-api.md`](rank-api.md)
- Caller-facing reference: [`api-policy-check.md`](api-policy-check.md), and the
  generated spec [`api/worker/openapi.yaml`](../api/worker/openapi.yaml)

---

## Where the determinations live at runtime

This was the first thing to settle and it is the reason the endpoint has the
shape it has.

The answers the paid tier sells — `commercial_use` per model (MODEL-78) and
`data_residency` per platform (MODEL-79) — are **not in this repository and
never will be**. The cards here are public and the export is rebuildable in
minutes, so the determinations are the only part of the product an enrichment
split actually protects; and unlike benchmark evidence they do not age out into
git on a delay, because a compliance answer does not decay. They live in a
private store, as JSON Lines, one record per line.

A Cloudflare Worker cannot read a private git repository. So:

```
private repo (JSONL)                     public repo (this one)
        │                                        │
        │  api/worker/load_determinations.py     │  pipeline/policy_export.py
        │  run from the private checkout         │  runs in CI on every build
        ▼                                        ▼
   Workers KV                          /api/policy/catalogue.json
   determinations/commercial_use         licence, origin, commercial-use
   determinations/residency              marker, platform availability
   determinations/manifest               (public card fields, reshaped)
        │                                        │
        └──────────────► the Worker ◄────────────┘
                              │
                   POST /v1/policy-check
```

**Workers KV, not D1 and not R2.** The CI token already carries
`Workers KV Storage:Edit`, so nothing new has to be provisioned or granted. The
access pattern is two whole-catalogue reads per cold isolate, cached for the
isolate's life — that is what a key-value store is for. D1 would buy per-model
queries the endpoint does not make (a policy check reads the whole catalogue),
at the cost of a schema, a migration path and a second thing to keep in step
with `schema/enrichment.py`. R2 would be the same two objects with worse
latency and no edge cache.

`CLAUDE.md`'s "no R2/D1 on the serving path" describes the **static export**
path settled in MODEL-2 and does not bind this. A note there now says so.

### The trust boundary

| Side | Holds | Writes to KV | Reads KV |
|---|---|---|---|
| This (public) repository | the schema, the reader, the loader **code** | no | no |
| Public CI (`rank-api.yml`) | the Worker script | no | no |
| The private store's holder | the determinations | **yes**, via the loader | — |
| The Worker | nothing at rest | no | yes, for an entitled request |

Four rules, each enforced by something that fails rather than by a paragraph:

1. **A determination never enters this repository.**
   `load_determinations._refuse_repo_paths` refuses to read an input from
   inside this tree or to write its staged output into one, and
   `tests/test_policy_check.py::test_the_export_never_carries_a_determination`
   fails if the public export ever starts carrying one. `.gitignore` is not a
   control; a refusal is.
2. **Public CI never holds the determinations.** The deploy workflow publishes
   the Worker script and nothing else. It has no path to the private store and
   is not given one — a cross-repository token in a public repo's workflow
   would put the whole product one `pull_request_target` mistake away. The KV
   load is a separate, deliberate step run by whoever holds the private
   checkout.
3. **The Worker verifies what it reads.** `determinations/manifest` is written
   **last** and carries the SHA-256 of each blob's exact bytes. The Worker
   reads the manifest first and refuses a mismatch. A load that dies halfway
   leaves the manifest describing the previous pair, so the endpoint answers
   from a consistent snapshot or refuses — never from half of one.
4. **A refusal is never a downgrade.** If a request is entitled to the
   determinations and the store cannot be read, the request fails with `503`.
   It is *not* answered from the public export, because a paid caller cannot
   tell that answer from a real one and would deploy on the difference.

What KV is trusted for: only what the loader wrote. The loader validates every
record before it is staged — a `restricted` grant with no condition text, a
`legacy-import` citation, a residency record for a local runtime and a
determination with no read date are all refused at load time, not at read time.

### Loading it

From a checkout of the private store:

```bash
python api/worker/load_determinations.py \
  --commercial-use /path/to/private/enrichment/commercial_use.jsonl \
  --residency      /path/to/private/enrichment/data_residency.jsonl \
  --out            /some/scratch/dir
```

It prints the three `wrangler kv key put` commands, manifest last. `--put` runs
them. The namespace does not exist yet; see [Needs Jamie](#needs-jamie).

---

## The third state is the product

`undetermined` is not a failure mode and not a missing value. It is what a
governance buyer is paying to eliminate, and the one answer no competitor
gives. A tool that silently treats a null as a pass is worse than no tool,
because a model gets deployed on it.

So it is **structurally** distinct from `pass`, not a flag and not a null. Every
check carries exactly one of three sibling keys:

```jsonc
{ "constraint": "commercial_use", "state": "satisfied",
  "satisfied":    { "commercial_use": "allowed", "source": {…}, "read_on": "2026-09-16" } }

{ "constraint": "licence", "state": "violated",
  "violated":     { "license_type": "cc-by-nc-4.0", "because": "…", "source": {…} } }

{ "constraint": "residency", "state": "undetermined",
  "undetermined": { "why": "not_determined", "meaning": "…", "available_in_tier": null } }
```

and every row carries exactly one of `passed`, `failed`, `undetermined`:

```jsonc
{ "model_id": "meta/llama-3-70b", "platform": "groq", "verdict": "fail",
  "checks": [ … ],
  "failed": { "constraint": "residency", "eliminated_by": { … },
              "also_violated": [], "also_undetermined": ["commercial_use"] } }
```

A consumer written against `satisfied` finds **no `satisfied` key** on an
undetermined check. The failure lands in the caller's code, loudly, rather than
in their deployment, quietly. That asymmetry is the design.

A row that both violates something and leaves something unknown is a `fail` — a
violation that was actually found is decisive — but the unknowns ride along in
`failed.also_undetermined`, because they are still unknown if the caller relaxes
the constraint that eliminated it.

### Demanding certainty

`"require_no_undetermined": true` and any undetermined row produces **HTTP 422**
`undetermined_present`: a documented hard failure carrying the count, the
breakdown by constraint, and up to ten offending rows. `result` is empty. The
summary still describes the whole catalogue, so the caller learns what they are
up against rather than only that something failed.

### Why a check comes back undetermined

| `why` | Meaning | Who can fix it |
|---|---|---|
| `tier` | this request reads the public export only | the paid tier (`available_in_tier: "paid"`) |
| `not_determined` | the determination store holds nothing for this | research (MODEL-78/79 coverage) |
| `not_on_card` | the public card does not name the licence or the origin | the catalogue |
| `uncited` | a value exists whose only citation is `legacy-import` | re-read the licence |
| `unbounded` | a local runtime: residency is a property of *your* machine | you, against your own infrastructure |
| `no_platform` | the card names no platform, so no place to determine | the catalogue |

`unbounded` is not for sale and `available_in_tier` is `null` for it. No region
list can ever be true of Ollama, at any tier, for any money.

---

## No verdict is ever inferred

Standing rules 1 and 2. Each of these yields `undetermined`:

- a licence the card does not name;
- a blank `origin_country`;
- a `commercial_use` of `unspecified` or `withheld` — those describe a file, not
  a licence;
- a `commercial_use` whose only citation is `legacy-import`, which is the card
  schema's own record that no document was read. Eight cards are in this state
  and **none of them passes a commercial-use constraint**;
- any platform with no residency determination.

**Regions are matched literally**, exactly as the platform publishes them. The
endpoint will not map "Germany" onto `eu-central-1`, or a country code onto a
cloud region: that is an inference about a vendor's geography, and this is the
one product that cannot afford to infer. The published vocabulary comes back
with the verdict so a caller can see what they have to match against.

A determined **empty** region list is a `fail`, not an unknown: the platform
published its terms and commits to no processing region. That distinction is
exactly what MODEL-77 widened the field to express.

---

## Per model *and* per platform

Residency resolves through the platform, not the model (MODEL-79), so a verdict
is emitted for every (model, platform) pair a card claims availability on. The
same model passes on `aws_bedrock` and fails on `groq` when only one of them
publishes the region the policy requires, and the response says so with two
rows. Covered by
`tests/test_policy_check.py::test_a_model_passes_on_one_platform_and_fails_on_another`.

A card naming no platform gets one row with `platform: null`, whose residency
check is `undetermined` for `no_platform`. Silence is not an answer.

`summary` counts both ways, because they are different facts:

```jsonc
"summary": {
  "models_checked": 1339, "rows": 2402,
  "verdicts": { "pass": 0, "fail": 41, "undetermined": 2361 },
  "models_with_a_passing_platform": 0,
  "by_constraint": { "commercial_use": { "satisfied": 0, "violated": 0,
                                         "undetermined": 2402 }, … }
}
```

---

## The free tier

The endpoint is free. The determinations are not.

A request with no entitlement is answered from `/api/policy/catalogue.json`
alone — which is a real answer: licence and origin are public baseline facts and
are genuinely settled. What it cannot settle, it labels, on the response and on
every affected check:

```jsonc
"determinations": {
  "entitlement": "public_export",
  "included": false,
  "answered_from": "the public export only",
  "store": { "loaded": false, "generated_on": null, … },
  "undetermined_for_lack_of_entitlement": 2402,
  "why": "commercial_use and data_residency are determinations, and determinations are the paid tier. …"
}
```

One number — `undetermined_for_lack_of_entitlement` — is the whole free/paid
difference, stated on every response rather than left to be discovered by
diffing two answers. Never a silent degradation, and never a `pass` that a paid
answer would have turned into a `fail`.

### Who is entitled

`_entitlement()` in `entry.py`, and nothing else. It is a single function and it
returns the free tier for every request today, on purpose: keys, tiers and rate
limits are **MODEL-69's**, and a second opinion about who a caller is would be a
second place for the two to disagree. MODEL-69 replaces that function's body and
nothing else in the endpoint changes — `policy_service.check` already takes the
entitlement as a parameter and the paid path is fully implemented and tested.

**Saved org policies** (in the ticket's scope) are not built here for the same
reason: a saved policy belongs to an org, and org identity arrives with
MODEL-69's keys. Building it against a placeholder identity would mean
rebuilding it.

---

## Request

```jsonc
POST /v1/policy-check
{
  "policy": {
    "name": "acme-eu-2026",                              // optional label, echoed back
    "licence":  { "allowed": ["apache-2.0", "mit"],      // either or both
                  "prohibited": ["cc-by-nc-4.0"] },
    "origin":   { "permitted_countries": ["US", "GB", "DE"],
                  "prohibited_countries": [] },
    "residency": { "required_regions": ["eu-west-1"],    // as the platform spells them
                   "match": "any" },                     // or "all"
    "commercial_use": { "required": true,
                        "accept_restricted": false }     // default: a conditional
  },                                                     // grant is not a pass
  "require_no_undetermined": false,
  "models":    ["meta/llama-3-70b"],   // optional; max 500
  "platforms": ["aws_bedrock"],        // optional
  "verdicts":  ["fail", "undetermined"],  // optional row filter; counts are unaffected
  "limit": 50, "offset": 0
}
```

A policy with no constraints is **refused**. "Every model passes" against
nothing is technically true, useless, and exactly what a caller who mistyped a
field name would receive as a clean bill of health.

`commercial_use.required: false` is refused too, for the same reason: omit the
block rather than reporting a constraint that constrains nothing.

`accept_restricted` defaults to `false`, so *"allowed unless you exceed 700M
monthly active users"* is a `fail` with the condition named until the caller
says otherwise. When they do say otherwise it becomes a `pass` that still
carries the condition text, in `satisfied.conditions` and again in
`passed.conditions`. A bare `true` is never the answer.

## Response

Beyond `result` and `summary`, every response carries what it was computed from,
so an answer given today can be defended in a year:

```jsonc
"build":        { "commit": "…", "built_at": "…", "export_schema_version": "2.0" },
"service_commit": "…",           // the deployed Worker
"export_origin":  "https://modelspec.dev",
"provenance": {
  "determination_read_dates": { "commercial_use": ["2026-09-16"],
                                "residency": ["2026-09-15", "2026-09-16"] },
  "determinations_generated_on": "2026-09-17"
}
```

Every satisfied and violated check carries its own `source` (kind, url,
`read_on`, quote) as well. Licences and region lists are rewritten without
notice, so the day a document was read is as load-bearing as its URL.

`page` reports `offset`, `limit`, `returned`, `matching_rows` and `truncated`.
**`summary` always describes the whole catalogue**; only the rows are paged.

### Status codes

| Code | Meaning |
|---|---|
| `200` | verdicts (possibly including `undetermined` rows) |
| `400` | refused: malformed body, empty policy, unknown model or platform |
| `404` / `405` / `413` | as the rank endpoint |
| `422` | `undetermined_present` — the caller demanded certainty and there is none |
| `502` | the published policy export could not be read |
| `503` | `determinations_unavailable` — entitled, and the store could not be read |

### The store's state on `/v1/health`

`determinations.state` is one of four values. Only `broken` carries a
`last_error`; the other three are conditions, not faults.

| `state` | Means | `last_error` |
|---|---|---|
| `unbound` | no `DETERMINATIONS` binding on this deployment | `null` |
| `empty` | bound, and `determinations/manifest` is absent — nothing loaded yet | `null` |
| `loaded` | the manifest is present and both blobs match its SHA-256s | `null` |
| `broken` | a manifest exists and a blob is missing, mismatched, or not JSON | the reason |

Workers KV answers a missing key with JS `null`, which Pyodide hands to Python
as `pyodide.ffi.jsnull`, not `None`. Before this was handled, an empty namespace
was reported as `JSONDecodeError` — an empty store read as a corrupt one.

An entitled request is refused with `503` in every state but `loaded`, an empty
store included, and the error names the state as `store_state`.

---

## Needs Jamie

1. **Create the KV namespace.** `npx wrangler kv namespace create DETERMINATIONS`,
   then paste the id into the commented `kv_namespaces` block in
   `api/worker/wrangler.jsonc` and uncomment it. It is commented out because
   wrangler refuses a deploy naming a namespace that does not exist, and a
   broken deploy on `main` is worse than a binding that arrives a day later.
   Nothing answers differently until it lands: `_entitlement()` grants the store
   to nobody until MODEL-69.
2. **Run the first load** from the private checkout, and confirm
   `GET /v1/health` reports `determinations.state: loaded` with the expected
   `generated_on`. Health reports the bundle's version and date only — never
   counts and never content.
3. **Decide who may run the loader.** Today it is whoever holds both the private
   checkout and a Cloudflare token with `Workers KV Storage:Edit`. If that
   should become automation, it belongs in the **private** repository's CI, not
   this one.
4. **§9.4's gate.** Until the first load, every commercial-use and residency
   check answers `undetermined`, which is the correct answer and also the reason
   paid tiers are not turned on yet. The endpoint now reports that as a number
   (`summary.by_constraint`) rather than as an impression.

## Not built (deliberately)

- **Auth, keys, tiers, rate limits** — MODEL-69.
- **Saved org policies** — needs org identity, which is MODEL-69's.
- **A signed attestation of a verdict** — REV-8.
- **`modelspec offline policy-check`** — REV-6. The offline CLI is a separate
  surface with its own envelope and exit codes; this ticket is the endpoint.
  When it ships it should call `policy_service` rather than growing a second
  set of rules, the way the rank endpoint calls `pipeline.ranking`.
